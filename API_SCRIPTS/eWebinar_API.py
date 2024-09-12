import csv
import datetime
import glob
import os
import shutil
import unidecode

from aiohttp import ClientSession

from Database.database import ewebinar_db, db
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
                    ewebinar_db.query("INSERT INTO tokens (api_token, service) VALUES (%s, %s)", values=(token, 'eWebinar'),
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
    tokens = db.query("SELECT api_token FROM tokens WHERE service = 'eWebinar'", fetch='fetchall')
    url = 'https://api.ewebinar.com/v2/registrants'
    for token in tokens:
        header = {
            'Authorization': f'Bearer {token[0]}'
        }
        params = {}
        if cursor:
            params['nextCursor'] = cursor
        try:
            async with session.get(url, headers=header, params=params) as response:
                return await response.json()
        except response.raise_for_status() as _ex:
            ewebinar_logger.error(msg=f"Error fetching data: {_ex}")


async def get_all_registrants(user_id):
    next_cursor = None
    item = 0
    async with ClientSession() as session:
        while True:
            data = await fetch_registrants(session, next_cursor)
            registrants = (data.get('registrants', []))
            next_cursor = data.get('nextCursor')

            if not next_cursor:
                break

            for registrant in registrants:
                try:
                    os.mkdir(os.path.abspath(f'../API_SCRIPTS/temp/{user_id}'))
                    os.mkdir(os.path.abspath(f'../temp/{user_id}'))
                except:
                    pass
                ewebinar_db.query("""INSERT INTO ewebinar (id, firstName, lastName, name, email, subscribed, registrationLink, replayLink, 
                joinLink, addToCalendarLink, timezone, sessionType, registeredTime, sessionTime, joinedTime, leftTime, attended, 
                likes, watchedPercent, watchedScheduledPercent, watchedReplayPercent, purchaseAmount, converted, tags, referrer, 
                origin, utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid, ip, city, country, source) 
                VALUES 
                (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,  
                %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING""",
                         values=(
                             registrant.get('id', ''),
                             unidecode.unidecode(registrant.get('firstName', '')),
                             unidecode.unidecode(registrant.get('lastName', '')),
                             unidecode.unidecode(registrant.get('name', '')),
                             registrant.get('email', ''),
                             registrant.get('subscribed', ''),
                             registrant.get('registrationLink', ''),
                             registrant.get('replayLink', ''),
                             registrant.get('joinLink', ''),
                             registrant.get('addToCalendarLink', ''),
                             registrant.get('timezone', ''),
                             registrant.get('sessionType', ''),
                             registrant.get('registeredTime', None),
                             registrant.get('sessionTime', None),
                             registrant.get('joinedTime', None),
                             registrant.get('leftTime', None),
                             registrant.get('attended', None),
                             registrant.get('likes', 0),
                             registrant.get('watchedPercent', 0.0),
                             registrant.get('watchedScheduledPercent', 0.0),
                             registrant.get('watchedReplayPercent', 0.0),
                             registrant.get('purchaseAmount', 0.0),
                             registrant.get('converted', False),
                             registrant.get('tags', []),
                             registrant.get('referrer', ''),
                             registrant.get('origin', ''),
                             registrant.get('utm_source', ''),
                             registrant.get('utm_medium', ''),
                             registrant.get('utm_campaign', ''),
                             registrant.get('utm_term', ''),
                             registrant.get('utm_content', ''),
                             registrant.get('gclid', ''),
                             registrant.get('ip', ''),
                             registrant.get('city', ''),
                             registrant.get('country', ''),
                             registrant.get('source', '')
                         ))

                ewebinar_db.query(query="""DELETE FROM ewebinar
                            WHERE ctid NOT IN (
                                SELECT MIN(ctid)
                                FROM ewebinar
                                GROUP BY id, firstName, lastName, name, email, subscribed, registrationLink, replayLink, 
                joinLink, addToCalendarLink, timezone, sessionType, registeredTime, sessionTime, joinedTime, leftTime, attended, 
                likes, watchedPercent, watchedScheduledPercent, watchedReplayPercent, purchaseAmount, converted, tags, 
                referrer, origin, utm_source, utm_medium, utm_campaign, utm_term, utm_content, gclid, ip, city, country, source
                            );""")

                file_pattern = f'../API_SCRIPTS/temp/{user_id}/ewebinar_report_{datetime.datetime.today().strftime('%Y-%m-%d')}_*.csv'
                filename = os.path.abspath(
                    f'../API_SCRIPTS/temp/{user_id}/ewebinar_report_{datetime.datetime.today().strftime('%Y-%m-%d')}_{item}.csv')
                filename_2 = os.path.abspath(
                    f'../temp/{user_id}/ewebinar_report_{datetime.datetime.today().strftime('%Y-%m-%d')}.csv')

                with open(filename, mode='w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = [
                        'id', 'firstName', 'lastName', 'name', 'email',
                        'subscribed', 'registrationLink', 'replayLink', 'joinLink',
                        'addToCalendarLink', 'timezone', 'sessionType',
                        'registeredTime', 'sessionTime', 'joinedTime',
                        'leftTime', 'attended', 'likes', 'watchedPercent',
                        'watchedScheduledPercent', 'watchedReplayPercent',
                        'purchaseAmount', 'converted', 'tags',
                        'referrer', 'origin', 'utm_source',
                        'utm_medium', 'utm_campaign', 'utm_term',
                        'utm_content', 'gclid', 'ip', 'city',
                        'country', 'source'
                    ]

                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                    writer.writeheader()

                    writer.writerow({
                        'id': registrant.get('id', ''),
                        'firstName': unidecode.unidecode(registrant.get('firstName', '')),
                        'lastName': unidecode.unidecode(registrant.get('lastName', '')),
                        'name': unidecode.unidecode(registrant.get('name', '')),
                        'email': registrant.get('email', ''),
                        'subscribed': registrant.get('subscribed', ''),
                        'registrationLink': registrant.get('registrationLink', ''),
                        'replayLink': registrant.get('replayLink', ''),
                        'joinLink': registrant.get('joinLink', ''),
                        'addToCalendarLink': registrant.get('addToCalendarLink', ''),
                        'timezone': registrant.get('timezone', ''),
                        'sessionType': registrant.get('sessionType', ''),
                        'registeredTime': registrant.get('registeredTime', None),
                        'sessionTime': registrant.get('sessionTime', None),
                        'joinedTime': registrant.get('joinedTime', None),
                        'leftTime': registrant.get('leftTime', None),
                        'attended': registrant.get('attended', None),
                        'likes': registrant.get('likes', 0),
                        'watchedPercent': registrant.get('watchedPercent', 0.0),
                        'watchedScheduledPercent': registrant.get('watchedScheduledPercent', 0.0),
                        'watchedReplayPercent': registrant.get('watchedReplayPercent', 0.0),
                        'purchaseAmount': registrant.get('purchaseAmount', 0.0),
                        'converted': registrant.get('converted', False),
                        'tags': registrant.get('tags', []),
                        'referrer': registrant.get('referrer', ''),
                        'origin': registrant.get('origin', ''),
                        'utm_source': registrant.get('utm_source', ''),
                        'utm_medium': registrant.get('utm_medium', ''),
                        'utm_campaign': registrant.get('utm_campaign', ''),
                        'utm_term': registrant.get('utm_term', ''),
                        'utm_content': registrant.get('utm_content', ''),
                        'gclid': registrant.get('gclid', ''),
                        'ip': registrant.get('ip', ''),
                        'city': registrant.get('city', ''),
                        'country': registrant.get('country', ''),
                        'source': registrant.get('source', '')
                    })

                item += 1

    try:
        file_list = glob.glob(file_pattern)
        with open(filename_2, 'w', encoding='utf-8') as out:
            for file_name in file_list:
                with open(file_name, 'r', encoding='utf-8') as infile:
                    out.write(infile.read())
        shutil.rmtree(os.path.abspath(f'../API_SCRIPTS/temp/{user_id}'))
    except Exception as _ex:
        ewebinar_logger.error(msg=f'CSV write canceled with error: {_ex}')

