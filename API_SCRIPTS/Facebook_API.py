import csv
import datetime
import json
import os.path
import shutil
import ssl
from decimal import Decimal
import glob

import certifi
import requests
from aiohttp import ClientSession

from Database.database import db


ssl_context = ssl.create_default_context(cafile=certifi.where())


def check_adacc_facebook(token):
    url = ('https://graph.facebook.com/v20.0/me?'
           'fields=adaccounts{name, id}'
           f'&access_token={token}')
    try:
        req = requests.get(url=url)
        if req.status_code == 200:
            json_req = req.json()['adaccounts']['data']
            for i in range(len(json_req)):
                res = json_req[i]
                name = res['name']
                acc_id = res['id']
                db.query(query="INSERT INTO adaccounts (acc_name, acc_id, api_token) VALUES (%s, %s, %s)",
                         values=(name, acc_id, token))
            return 200
        if req.status_code == 401:
            return 401
        if req.status_code != (200 or 401):
            return 'BAD'
    except:
        return 'BAD'


async def reports_which_is_active(user_id='reserved'):
    adacc_ids = db.query(query="SELECT acc_id, api_token, date_preset, increment, level FROM adaccounts "
                               "WHERE is_active = TRUE",
                         fetch='fetchall')
    params_list = []
    campaign_ids = []

    for items in adacc_ids:
        adacc_id, token, date_preset, time_increment, level = items

        fields_list = ['account_name', 'account_id', 'campaign_name', 'campaign_id', 'adset_name', 'adset_id',
                       'ad_name', 'ad_id', 'impressions', 'frequency', 'clicks', 'unique_clicks', 'spend', 'reach',
                       'cpp', 'cpm', 'unique_link_clicks_ctr', 'ctr', 'unique_ctr', 'cpc', 'cost_per_unique_click',
                       'objective', 'buying_type', 'created_time']

        fields = ''
        fields_db = db.query(
            query="SELECT account_name, account_id, campaign_name, campaign_id, adset_name, adset_id,"
                  "ad_name, ad_id, impressions, frequency, clicks, unique_clicks, spend, reach, cpp, cpm, "
                  "unique_link_clicks_ctr, ctr, unique_ctr, cpc, cost_per_unique_click, objective, buying_type, "
                  "created_time FROM adaccounts WHERE acc_id=%s", values=(adacc_id,), fetch='fetchall')[0]

        for i in range(len(fields_db)):
            if str(fields_db[i]).lower() == 'true':
                fields += f'{fields_list[i]},'
            else:
                pass

        url_step_1 = f'https://graph.facebook.com/v20.0/{adacc_id}/insights'

        params_step_1 = {
            'access_token': token,

            'fields': 'campaign_id',

            'date_preset': 'maximum',

            'level': 'campaign',

            'limit': '1000',

            'time_increment': str(time_increment),
        }

        params_step_2 = {
            'access_token': token,

            'fields': fields.rstrip(','),

            'date_preset': date_preset,

            'level': level,

            'time_increment': str(time_increment),

            'limit': '1000'

        }

        params_step_1 = {k: (float(v) if isinstance(v, Decimal) else str(v)) for k, v in params_step_1.items()}

        while True:
            async with ClientSession() as client:
                async with client.get(url=url_step_1, params=params_step_1, ssl=ssl_context) as response_step_1:
                    response_step_1.raise_for_status()
                    data_step_1 = await response_step_1.json()

                    for record in data_step_1.get('data', []):
                        campaign_ids.append(record['campaign_id'])
                        params_list.append(params_step_2)

                        # Проверяем наличие следующей страницы с кампаниями
                    if 'paging' in data_step_1 and 'next' in data_step_1['paging']:
                        url_step_1 = data_step_1['paging']['next']  # Обновляем URL на следующий
                        params_step_1 = {}  # Параметры не нужны для следующей страницы
                    else:
                        break  # Выход из цикла, если следующей страницы нет
    campaign_ids_res = list(dict.fromkeys(campaign_ids))
    item = 0
    try:
        os.mkdir(os.path.abspath(f'../API_SCRIPTS/temp/{user_id}'))
        os.mkdir(os.path.abspath(f'../temp/{user_id}'))
    except:
        pass
    for camp_id in campaign_ids_res:
        url = f'https://graph.facebook.com/v20.0/{camp_id}/insights'
        params = params_list[item]

        while True:
            async with ClientSession() as client:
                async with client.get(url=url, params=params, ssl=ssl_context) as response:
                    response.raise_for_status()
                    data = await response.json()

                    try:
                        file_pattern = f'../API_SCRIPTS/temp/{user_id}/report_{datetime.datetime.today().strftime('%Y-%m-%d')}_*.csv'
                        filename = os.path.abspath(
                            f'../API_SCRIPTS/temp/{user_id}/report_{datetime.datetime.today().strftime('%Y-%m-%d')}_{item}.csv')
                        filename_2 = os.path.abspath(
                            f'../temp/{user_id}/report_{datetime.datetime.today().strftime('%Y-%m-%d')}.csv')
                        for record in data.get('data', []):
                            db.query(
                                query="INSERT INTO reports (account_name, account_id, campaign_name, campaign_id, adset_name, "
                                      "adset_id, ad_name, ad_id, impressions, frequency, clicks, unique_clicks, spend, reach, cpp, "
                                      "cpm, unique_link_clicks_ctr, ctr, unique_ctr, cpc, cost_per_unique_click, objective, "
                                      "buying_type, created_time, date_start, date_stop) "
                                      "VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, "
                                      "%s, %s, %s, %s, %s)",
                                values=(
                                    record.get('account_name', None),
                                    record.get('account_id', None),
                                    record.get('campaign_name', None),
                                    record.get('campaign_id', None),
                                    record.get('adset_name', None),
                                    record.get('adset_id', None),
                                    record.get('ad_name', None),
                                    record.get('ad_id', None),
                                    float(record.get('impressions', 0)),
                                    float(record.get('frequency', 0)),
                                    float(record.get('clicks', 0)),
                                    float(record.get('unique_clicks', 0)),
                                    float(record.get('spend', 0)),
                                    float(record.get('reach', 0)),
                                    float(record.get('cpp', 0)),
                                    float(record.get('cpm', 0)),
                                    float(record.get('unique_link_clicks_ctr', 0)),
                                    float(record.get('ctr', 0)),
                                    float(record.get('unique_ctr', 0)),
                                    float(record.get('cpc', 0)),
                                    float(record.get('cost_per_unique_click', 0)),
                                    record.get('objective', None),
                                    record.get('buying_type', None),
                                    record.get('created_time', None),
                                    record.get('date_start', None),
                                    record.get('date_stop', None),
                                )
                            )
                        try:
                            with open(filename, mode='a', newline='', encoding='utf-8') as csvfile:
                                writer = csv.writer(csvfile)
                                # Заголовки
                                writer.writerow([
                                    'account_name', 'account_id', 'campaign_name', 'campaign_id',
                                    'adset_name', 'adset_id', 'ad_name', 'ad_id',
                                    'impressions', 'frequency', 'clicks', 'unique_clicks',
                                    'spend', 'reach', 'cpp', 'cpm',
                                    'unique_link_clicks_ctr', 'ctr', 'unique_ctr',
                                    'cpc', 'cost_per_unique_click', 'objective',
                                    'buying_type', 'created_time', 'date_start', 'date_stop'
                                ])
                                for record in data.get('data', []):
                                    writer.writerow([
                                        record.get('account_name', ''),
                                        record.get('account_id', ''),
                                        record.get('campaign_name', ''),
                                        record.get('campaign_id', ''),
                                        record.get('adset_name', ''),
                                        record.get('adset_id', ''),
                                        record.get('ad_name', ''),
                                        record.get('ad_id', ''),
                                        float(record.get('impressions', 0)),
                                        float(record.get('frequency', 0)),
                                        float(record.get('clicks', 0)),
                                        float(record.get('unique_clicks', 0)),
                                        float(record.get('spend', 0)),
                                        float(record.get('reach', 0)),
                                        float(record.get('cpp', 0)),
                                        float(record.get('cpm', 0)),
                                        float(record.get('unique_link_clicks_ctr', 0)),
                                        float(record.get('ctr', 0)),
                                        float(record.get('unique_ctr', 0)),
                                        float(record.get('cpc', 0)),
                                        float(record.get('cost_per_unique_click', 0)),
                                        record.get('objective', ''),
                                        record.get('buying_type', ''),
                                        record.get('created_time', ''),
                                        record.get('date_start', ''),
                                        record.get('date_stop', ''),
                                    ])
                        except:
                            pass


                    except:
                        pass
                    if 'paging' in data and 'next' in data['paging']:
                        url = data['paging']['next']
                        params = {}
                    else:
                        item += 1
                        break

    db.query(query="""DELETE FROM reports
            WHERE ctid NOT IN (
                SELECT MIN(ctid)
                FROM reports
                GROUP BY account_name, account_id, campaign_name, campaign_id, adset_name, adset_id, ad_name, ad_id,
                impressions, frequency, clicks, unique_clicks, spend, reach, cpp, cpm, unique_link_clicks_ctr, ctr,
                unique_ctr, cpc, cost_per_unique_click, objective, buying_type, created_time, date_start, date_stop
            );""")
    try:
        file_list = glob.glob(file_pattern)
        with open(filename_2, 'w') as out:
            for file_name in file_list:
                with open(file_name, 'r') as infile:
                    out.write(infile.read())
        shutil.rmtree(os.path.abspath(f'../API_SCRIPTS/temp/{user_id}'))
    except:
        pass





