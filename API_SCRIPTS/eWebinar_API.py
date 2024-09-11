from aiohttp import ClientSession

from Database.database import db
from utils.logging_settings import ewebinar_logger


async def check_acc_ewebinar(token):
    url = 'https://api.ewebinar.com/v2/webinars'

    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    db.query("INSERT INTO tokens (api_token, service) VALUES (%s, %s)", values=(token, 'eWebinar'),
                             msg='Token eWebinar already exists',
                             log_level=10)
                    return 200
                if resp.status == 401:
                    return 401
                if resp.status != (200 or 401):
                    return 'BAD'
    except Exception as _ex:
        ewebinar_logger.error(msg=f'Check_acc failed with error: {_ex}')
        return 'BAD'


async def fetch_registrants(session, cursor=None):
    tokens = db.query("SELECT * FROM tokens WHERE service = 'eWebinar'")
    url = 'https://api.ewebinar.com/v2/registrants'
    for token in tokens:
        header = {
            'Authorization': f'Bearer {token}'
        }
        params = {}
        if cursor:
            params['nextCursor'] = cursor
        try:
            async with session.get(url, headers=header, params=params) as response:
                return await response.json()
        except Exception as _ex:
            ewebinar_logger.error(msg=f"Error fetching data: {_ex}")


async def get_all_registrants():
    registrants = []
    next_cursor = None

    async with ClientSession() as session:
        while True:
            data = await fetch_registrants(session, next_cursor)
            registrants.extend(data.get('registrants', []))
            next_cursor = data.get('nextCursor')

            if not next_cursor:
                break

    for registrant in registrants:
        await insert_into_database(registrant)

async def insert_into_database(registrant):
    db.query("""INSERT INTO ewebinar (id, firstName, lastName, name, email, subscribed, registrationLink, replayLink, 
    joinLink, addToCalendarLink, timezone, sessionType, registeredTime, sessionTime, joinedTime, leftTime, attended, 
    likes, watchedPercent, watchedScheduledPercent, watchedReplayPercent, purchaseAmount, converted, tags, source, 
    referrer, origin, utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid, ip, city, country)
    VALUES ($1, $2, $3, $4, $5, $6, $7, $8, $9, $10, $11, $12, $13, $14, $15, $16, $17, $18, $19, $20, $21, $22, $23, 
    $24, $25, $26, $27, $28, $29, $30, $31, $32, $33, $34, $35, $36)""",
             values=(registrant['id'],
                     registrant['firstName'],
                     registrant['lastName'],
                     registrant['name'],
                     registrant['email'],
                     registrant['subscribed'],
                     registrant['registrationLink'],
                     registrant['replayLink'],
                     registrant['joinLink'],
                     registrant['addToCalendarLink'],
                     registrant['timezone'],
                     registrant['sessionType'],
                     registrant['registeredTime'],
                     registrant['sessionTime'],
                     registrant['joinedTime'],
                     registrant['leftTime'],
                     registrant['attended'],
                     registrant.get('likes', 0),
                     registrant.get('watchedPercent', 0.0),
                     registrant.get('watchedScheduledPercent', 0.0),
                     registrant.get('watchedReplayPercent', 0.0),
                     registrant.get('purchaseAmount', 0.0),
                     registrant.get('converted', False),
                     registrant['source'],
                     registrant.get('utm_term', ''),
                     registrant.get('utm_content', ''),
                     registrant.get('gclid', ''),
                     registrant['ip'],
                     registrant['city'],
                     registrant['country']))

    db.query(query="""DELETE FROM ewebinar
                WHERE ctid NOT IN (
                    SELECT MIN(ctid)
                    FROM ewebinar
                    GROUP BY id, firstName, lastName, name, email, subscribed, registrationLink, replayLink, 
    joinLink, addToCalendarLink, timezone, sessionType, registeredTime, sessionTime, joinedTime, leftTime, attended, 
    likes, watchedPercent, watchedScheduledPercent, watchedReplayPercent, purchaseAmount, converted, tags, source, 
    referrer, origin, utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid, ip, city, country
                );""")
