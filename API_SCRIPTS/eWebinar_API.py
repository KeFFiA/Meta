from aiohttp import ClientSession

from Database.database import ewebinar_db, db
from Bot.utils.logging_settings import ewebinar_logger


async def check_acc_ewebinar(token):
    url = 'https://api.ewebinar.com/v2/webinars'

    headers = {
        'Authorization': f'Bearer {token}'
    }
    try:
        async with ClientSession() as session:
            async with session.get(url, headers=headers) as resp:
                if resp.status == 200:
                    return 200
                if resp.status == 401:
                    return 401
                if resp.status != (200 or 401):
                    ewebinar_logger.error(msg=f'Check_acc failed with error: [{resp.status}] - {resp.reason}')
                    return 'BAD'
    except Exception as _ex:
        ewebinar_logger.error(msg=f'Check_acc failed with error: {_ex}')
        return 'BAD'


async def get_all_registrants():
    count = 1
    tokens = db.query("SELECT api_token FROM tokens WHERE service = 'eWebinar'", fetch='fetchall')
    url = 'https://api.ewebinar.com/v2/registrants'
    registrants_list = []
    for token in tokens:
        header = {
            'Authorization': f'Bearer {token[0]}'
        }
        params = {}
        try:
            while True:
                async with ClientSession() as session:
                    async with session.get(url, headers=header, params=params) as response:
                        try:
                            data = await response.json()
                            for registrant in data['registrants']:
                                registrants_list.append([registrant.get('actions', None),
                                                        registrant.get('addToCalendarLink', None),
                                                        registrant.get('allWebinarsLink', None),
                                                        registrant.get('attended', None),
                                                        registrant.get('chatsSent', None),
                                                        registrant.get('city', None),
                                                        registrant.get('country', None),
                                                        registrant.get('deviceTypeWhenRegistered', None),
                                                        registrant.get('deviceTypeWhenWatching', None),
                                                        registrant.get('email', None),
                                                        registrant.get('emailVerified', None),
                                                        registrant.get('firstName', None),
                                                        registrant.get('firstOrigin', None),
                                                        registrant.get('firstReferrer', None),
                                                        registrant.get(str(registrant.keys()).startswith('httpsdrivegoogle'), None),
                                                        registrant.get('id', None),
                                                        registrant.get('ip', None),
                                                        registrant.get('joinedTime', None),
                                                        registrant.get('joinLink', None),
                                                        registrant.get('lastName', None),
                                                        registrant.get('leftTime', None),
                                                        registrant.get('likes', None),
                                                        registrant.get('name', None),
                                                        registrant.get('neurographicsCourse', None),
                                                        registrant.get('origin', None),
                                                        registrant.get('referrer', None),
                                                        registrant.get('registeredTime', None),
                                                        registrant.get('registrationLink', None),
                                                        registrant.get('replayLink', None),
                                                        registrant.get('sessionTime', None),
                                                        registrant.get('sessionType', None),
                                                        registrant.get('source', None),
                                                        registrant.get('state', None),
                                                        registrant.get('subscribed', None),
                                                        registrant.get('timezone', None),
                                                        registrant.get('totalWatchedPercent', None),
                                                        registrant.get('utm_campaign', None),
                                                        registrant.get('utm_content', None),
                                                        registrant.get('utm_medium', None),
                                                        registrant.get('utm_source', None),
                                                        registrant.get('utm_term', None),
                                                        registrant.get('watchedScheduledPercent', None),
                                                        registrant.get('webinarId', None),
                                                        registrant.get('webinarTitle', None)])
                                count += 1
                            if data['nextCursor']:
                                params['nextCursor'] = data['nextCursor']
                            else:
                                break

                        except Exception as _ex:
                            ewebinar_logger.error(msg=f'Fetch registrants failed with error: {_ex} | status: {response.status}')
                            break

            new_registrants_list = [tuple([None if elem == '' else str(elem).encode('utf-8').decode('utf-8')
                                           for elem in item]) for item in registrants_list]

            ewebinar_db.query("""INSERT INTO ewebinar 
            (actions, addToCalendarLink, allWebinarsLink, attended, chatsSent, city, country, deviceTypeWhenRegistered, 
            deviceTypeWhenWatching, email, emailVerified, firstName, firstOrigin, firstReferrer, httpsdrivegoogle, id, ip, 
            joinedTime, joinLink, lastName, leftTime, likes, name, neurographicsCourse, origin, referrer, registeredTime, 
            registrationLink, replayLink, sessionTime, sessionType, source, state, subscribed, timezone, 
            totalWatchedPercent, utm_campaign, utm_content, utm_medium, utm_source, utm_term, watchedScheduledPercent, 
            webinarId, webinarTitle)
            VALUES 
            (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) 
            ON CONFLICT DO NOTHING""",
                     values=new_registrants_list, execute_many=True)

            ewebinar_db.query(query="""DELETE FROM ewebinar
                        WHERE ctid NOT IN (
                            SELECT MIN(ctid)
                            FROM ewebinar
                            GROUP BY actions, addToCalendarLink, allWebinarsLink, attended, chatsSent, city, country, 
                            deviceTypeWhenRegistered, deviceTypeWhenWatching, email, emailVerified, firstName, 
                            firstOrigin, firstReferrer, httpsdrivegoogle, id, ip, joinedTime, joinLink, lastName, 
                            leftTime, likes, name, neurographicsCourse, origin, referrer, registeredTime, registrationLink, 
                            replayLink, sessionTime, sessionType, source, state, subscribed, timezone, 
                            totalWatchedPercent, utm_campaign, utm_content, utm_medium, utm_source, utm_term, 
                            watchedScheduledPercent, webinarId, webinarTitle
                        );""")

            ewebinar_logger.info(msg=f'Fetch registrants query successfully ended with ~{count*50} registrants')
            return True
        except Exception as _ex:
            ewebinar_logger.error(msg=f'Registrants failed with error: {_ex}')


