import datetime
from asyncio import sleep

from aiohttp import ClientSession

from Database.database import db, getcourse_db
from utils.logging_settings import ewebinar_logger, getcourse_logger


async def check_acc_getcourse(token, account_name):
    url = f'https://{account_name}.getcourse.ru/pl/api/account/users'

    params = {
        'key': token,

        'created_at[from]': datetime.datetime.today().strftime('%Y-%m-%d'),
    }
    try:
        async with ClientSession() as session:
            async with session.get(url, params=params) as resp:
                if resp.status == 200:
                    db.query("INSERT INTO tokens (api_token, service, account_name) VALUES (%s, %s, %s)",
                             values=(token, 'GetCourse', account_name),
                             msg='Token GetCourse already exists',
                             log_level=10)
                    return 200
                if resp.status == 401:
                    return 401
                if resp.status != (200 or 401):
                    return 'BAD'
    except Exception as _ex:
        ewebinar_logger.error(msg=f'Check_acc failed with error: {_ex}')
        return 'BAD'


async def getcourse_users_report():
    account_names = db.query(query="SELECT api_token, account_name FROM tokens WHERE service = 'GetCourse'", fetch='fetchall')

    for token, account_name in account_names:
        url = f'https://{account_name}.getcourse.ru/pl/api/account/users'
        params = {
            'key': token,
            'created_at[from]': (datetime.datetime.today() - datetime.timedelta(days=30)).strftime('%Y-%m-%d'),
        }
        time = 600
        async with ClientSession() as session:
            async with session.get(url, params=params) as resp:
                try:
                    data = await resp.json()
                except Exception as _ex:
                    getcourse_logger.error(msg=f'GetCourse users report failed with error: {_ex}')
                    return
                while time > 0:
                    try:
                        if data.get('success'):
                            export = data.get('info', {})
                            if 'export_id' in export:
                                export_id = export['export_id']
                                print(export_id)
                                url = f'https://{account_name}.getcourse.ru/pl/api/account/exports/{export_id}'
                                await sleep(180)
                            async with ClientSession() as session:
                                async with session.get(url, params=params) as resp:
                                    data_2 = await resp.json()
                                    for item in data_2['info']['items']:
                                        new_item = [None if x == '' else str(x).encode('utf-8').decode('utf-8') for x in
                                                    item]
                                        print(new_item)
                                        getcourse_db.query(f"""INSERT INTO GetCourse (id, email, registration_type, created, 
                                        last_activity, first_name, last_name, phone, date_of_birth, age, country, city, 
                                        from_partner, client_portrait, comments, bil_minut, dosmotrel_do_kontsa, button_click, 
                                        web_room, data_webinara, vremya_start, vremya_end, bil_na_webe, banner_click, sb_id, 
                                        partner_id, partner_email, partner_full_name, utm_source, utm_medium, utm_campaign, 
                                        utm_term, utm_content, bil_minut_2, utm_group, btn_1, btn_2, btn_3, lm_utm_source, 
                                        lm_utm_medium, lm_utm_term, lm_utm_content, lm_utm_campaign, btn_4, btn_5, btn_6, 
                                        instagram_telegram_nick, income_money, btn_7, btn_8, web_time, webhook_time_web, 
                                        btn_9, from_where, utm_source_2, utm_medium_2, utm_campaign_2, utm_term_2, utm_content_2, 
                                        utm_group_2, partner_id_2, partner_email_2, partner_fullname, manager_fullname, vk_id) 
                                        VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                                %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                                %s);""",
                                                           values=tuple(new_item), debug=True)
                            break
                        else:
                            await sleep(20)
                            time -= 20
                    except Exception as _ex:
                        getcourse_logger.error(msg=f'GetCourse users_report failed with error: {_ex}')
                        await sleep(20)
                        time -= 20

