import datetime
from asyncio import sleep

from aiohttp import ClientSession

from Database.database import db, getcourse_db
from Bot.utils.logging_settings import ewebinar_logger, getcourse_logger


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


async def getcourse_report():
    account_names = db.query(query="SELECT api_token, account_name FROM tokens WHERE service = 'GetCourse'", fetch='fetchall')

    for token, account_name in account_names:
        params = {
            'key': token,
            'created_at[from]': (datetime.datetime.today() - datetime.timedelta(days=1)).strftime('%Y-%m-%d'),
        }
        urls = {
            'users': f'https://{account_name}.getcourse.ru/pl/api/account/users',
            'deals': f'https://{account_name}.getcourse.ru/pl/api/account/deals',
            'payments': f'https://{account_name}.getcourse.ru/pl/api/account/payments',
        }
        for key, url in urls.items():
            if key == 'users':
                async with ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        data = await response.json()
                        await getcourse_users_report(account_name=account_name, params=params, data=data)
            elif key == 'deals':
                async with ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        data = await response.json()
                        await getcourse_deals_report(account_name=account_name, params=params, data=data)
            elif key == 'payments':
                async with ClientSession() as session:
                    async with session.get(url, params=params) as response:
                        data = await response.json()
                        await getcourse_payments_report(account_name=account_name, params=params, data=data)

        return True


async def getcourse_users_report(account_name, params, data):
    time = 1200
    while time > 0:
        try:
            if data.get('success'):
                export = data.get('info', {})
                if 'export_id' in export:
                    export_id = export['export_id']
                    url = f'https://{account_name}.getcourse.ru/pl/api/account/exports/{export_id}'
                    await sleep(300)
                    async with ClientSession() as session:
                        async with session.get(url, params=params) as resp:
                            data_2 = await resp.json()
                            items = data_2['info']['items']
                            new_item = [tuple([None if elem == '' else str(elem).encode('utf-8').decode('utf-8')
                                               for elem in item]) for item in items]

                            getcourse_db.query(f"""INSERT INTO getcourse_users (id, email, registration_type, 
                            created, last_activity, first_name, last_name, phone, date_of_birth, age, country, 
                            city, from_partner, client_portrait, comments, bil_minut, dosmotrel_do_kontsa, 
                            button_click, web_room, data_webinara, vremya_start, vremya_end, bil_na_webe, 
                            banner_click, city_2, pay_at, sb_id, partner_id, partner_email, partner_full_name, 
                            utm_source, utm_medium, utm_campaign, utm_term, utm_content, bil_minut_2, utm_group, 
                            btn_1, btn_2, btn_3, lm_utm_source, lm_utm_medium, lm_utm_term, lm_utm_content, 
                            lm_utm_campaign, btn_4, btn_5, btn_6, instagram_telegram_nick, income_money, btn_7, 
                            btn_8, web_time, webhook_time_web, btn_9, from_where, utm_source_2, utm_medium_2, 
                            utm_campaign_2, utm_term_2, utm_content_2, utm_group_2, partner_id_2, partner_email_2, 
                            partner_fullname, manager_fullname, vk_id) 
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                                    %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s,
                                    %s, %s, %s) ON CONFLICT DO NOTHING;""",
                                               values=new_item, execute_many=True, debug=True)
                break
            else:
                await sleep(60)
                time -= 60
        except Exception as _ex:
            getcourse_logger.error(msg=f'GetCourse users_report failed with error: {_ex}')
            await sleep(60)
            time -= 60

    getcourse_db.query(query="""DELETE FROM getcourse_users
                WHERE ctid NOT IN (
                    SELECT MIN(ctid)
                    FROM getcourse_users
                    GROUP BY id, email, registration_type, 
                        created, last_activity, first_name, last_name, phone, date_of_birth, age, country, 
                        city, from_partner, client_portrait, comments, bil_minut, dosmotrel_do_kontsa, 
                        button_click, web_room, data_webinara, vremya_start, vremya_end, bil_na_webe, 
                        banner_click, city_2, pay_at, sb_id, partner_id, partner_email, partner_full_name, 
                        utm_source, utm_medium, utm_campaign, utm_term, utm_content, bil_minut_2, utm_group, 
                        btn_1, btn_2, btn_3, lm_utm_source, lm_utm_medium, lm_utm_term, lm_utm_content, 
                        lm_utm_campaign, btn_4, btn_5, btn_6, instagram_telegram_nick, income_money, btn_7, 
                        btn_8, web_time, webhook_time_web, btn_9, from_where, utm_source_2, utm_medium_2, 
                        utm_campaign_2, utm_term_2, utm_content_2, utm_group_2, partner_id_2, partner_email_2, 
                        partner_fullname, manager_fullname, vk_id
                );""", debug=True)


async def getcourse_deals_report(account_name, params, data):
    time = 1800
    while time > 0:
        try:
            if data.get('success'):
                export = data.get('info', {})
                if 'export_id' in export:
                    export_id = export['export_id']
                    url = f'https://{account_name}.getcourse.ru/pl/api/account/exports/{export_id}'
                    await sleep(300)
                    async with ClientSession() as session:
                        async with session.get(url, params=params) as resp:
                            data_2 = await resp.json()
                            items = data_2['info']['items']
                            new_item = [tuple([None if elem == '' else str(elem).encode('utf-8').decode('utf-8')
                                               for elem in item]) for item in items]

                            getcourse_db.query(f"""INSERT INTO getcourse_deals
                            (Order_ID, Number, User_ID, Username, Email, Phone, Creation_Date, Payment_Date, Title, 
                            Status, Cost_RUB, Paid, Payment_System_Fee, Received, Tax, 
                            Remaining_After_Deducting_Payment_System_Fee_and_Tax, Other_Fees, Earned, Currency, Manager, 
                            City, Payment_System, Partner_ID, Used_Promo_Code, Promotion, Partner_Evgeny_Schneider, 
                            Code_Word, Club_Opening_Date, Payment_Date_1st_Payment, second_payment_date, third_Payment_Date, 
                            utm_source, utm_medium, utm_campaign, utm_content, utm_term, Active_Messenger, sb_id, gcpc, 
                            fun, gcmlg, Order_Creation_Page, number_manager, time_web, date_web, time_left, replay_web, 
                            Order_Partner_ID, Order_Partner_Email, Order_Partner_Full_Name, User_Partner_ID, User_Partner_Email, 
                            User_Partner_Full_Name, utm_source_2, utm_medium_2, utm_campaign_2, utm_content_2, utm_term_2, 
                            utm_group, Affiliate_Source, Affiliate_Code, Affiliate_Session, user_utm_source, user_utm_medium, 
                            user_utm_campaign, user_utm_content, user_utm_term, user_utm_group, user_gcpc, Tags, Offer_Tags) 
                            VALUES (
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, 
                            %s, %s) ON CONFLICT DO NOTHING;""",
                                               values=new_item, execute_many=True, debug=True)
                break
            else:
                await sleep(120)
                time -= 120
        except Exception as _ex:
            getcourse_logger.error(msg=f'GetCourse deals_report failed with error: {_ex}')
            await sleep(120)
            time -= 120

    getcourse_db.query(query="""DELETE FROM getcourse_deals
                        WHERE ctid NOT IN (
                            SELECT MIN(ctid)
                            FROM getcourse_deals
                            GROUP BY Order_ID, Number, User_ID, Username, Email, Phone, Creation_Date, Payment_Date, Title, 
                            Status, Cost_RUB, Paid, Payment_System_Fee, Received, Tax, 
                            Remaining_After_Deducting_Payment_System_Fee_and_Tax, Other_Fees, Earned, Currency, Manager, 
                            City, Payment_System, Partner_ID, Used_Promo_Code, Promotion, Partner_Evgeny_Schneider, 
                            Code_Word, Club_Opening_Date, Payment_Date_1st_Payment, second_payment_date, third_Payment_Date, 
                            utm_source, utm_medium, utm_campaign, utm_content, utm_term, Active_Messenger, sb_id, gcpc, 
                            fun, gcmlg, Order_Creation_Page, number_manager, time_web, date_web, time_left, replay_web, 
                            Order_Partner_ID, Order_Partner_Email, Order_Partner_Full_Name, User_Partner_ID, User_Partner_Email, 
                            User_Partner_Full_Name, utm_source_2, utm_medium_2, utm_campaign_2, utm_content_2, utm_term_2, 
                            utm_group, Affiliate_Source, Affiliate_Code, Affiliate_Session, user_utm_source, user_utm_medium, 
                            user_utm_campaign, user_utm_content, user_utm_term, user_utm_group, user_gcpc, Tags, Offer_Tags
                        );""", debug=True)


async def getcourse_payments_report(account_name, params, data):
    time = 1200
    while time > 0:
        try:
            if data.get('success'):
                export = data.get('info', {})
                if 'export_id' in export:
                    export_id = export['export_id']
                    url = f'https://{account_name}.getcourse.ru/pl/api/account/exports/{export_id}'
                    await sleep(300)
                    async with ClientSession() as session:
                        async with session.get(url, params=params) as resp:
                            data_2 = await resp.json()
                            items = data_2['info']['items']
                            new_item = [tuple([None if elem == '' else str(elem).encode('utf-8').decode('utf-8')
                                               for elem in item]) for item in items]

                            getcourse_db.query(f"""INSERT INTO getcourse_payments (Number, Username, Email, Orders, 
                            Creation_Date, Type, Status, Amount, Fees, Received, Payment_Code, Title)
                            VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s) ON CONFLICT DO NOTHING;""",
                                               values=new_item, execute_many=True, debug=True)
                break
            else:
                await sleep(120)
                time -= 120
        except Exception as _ex:
            getcourse_logger.error(msg=f'GetCourse payments_report failed with error: {_ex}')
            await sleep(120)
            time -= 120

    getcourse_db.query(query="""DELETE FROM getcourse_payments
                            WHERE ctid NOT IN (
                                SELECT MIN(ctid)
                                FROM getcourse_payments
                                GROUP BY Number, Username, Email, Orders, 
                                         Creation_Date, Type, Status, Amount, Fees, Received, Payment_Code, Title
                            );""", debug=True)


