import ssl
from decimal import Decimal

import certifi
import requests
from aiohttp import ClientSession

from Database.database import db
from Bot.utils.logging_settings import facebook_logger

ssl_context = ssl.create_default_context(cafile=certifi.where())


def check_adacc_facebook(token):
    app_id = '1050769943235820'
    app_secret = 'da6bf3e17b662edb311aaecd81ab0f90'
    url = ("https://graph.facebook.com/v20.0/oauth/access_token?grant_type=fb_exchange_token&"
           f"client_id={app_id}&client_secret={app_secret}&fb_exchange_token={token}")
    try:
        response = requests.get(url)
        if response.status_code == 200:
            long_token = response.json()['access_token']

            url = ('https://graph.facebook.com/v20.0/me?'
                   'fields=adaccounts{name, id}'
                   f'&access_token={long_token}')

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
        if response.status_code == 401:
            return 401
        if response.status_code != (200 or 401):
            return 'BAD'
    except:
        return 'BAD'


async def reports_which_is_active():
    facebook_logger.info('Start Facebook reports function')
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
        try:
            while True:
                async with ClientSession() as client:
                    async with client.get(url=url_step_1, params=params_step_1, ssl=ssl_context) as response_step_1:
                        response_step_1.raise_for_status()
                        data_step_1 = await response_step_1.json()

                        for record in data_step_1.get('data', []):
                            campaign_ids.append(record['campaign_id'])
                            params_list.append(params_step_2)


                        if 'paging' in data_step_1 and 'next' in data_step_1['paging']:
                            url_step_1 = data_step_1['paging']['next']
                            params_step_1 = {}
                        else:
                            break
        except Exception as _ex:
            facebook_logger.error(f'Report failed with error: {_ex}')
            return False
    campaign_ids_res = list(dict.fromkeys(campaign_ids))
    item = 0
    for camp_id in campaign_ids_res:
        url = f'https://graph.facebook.com/v20.0/{camp_id}/insights'
        params = params_list[item]

        while True:
            async with ClientSession() as client:
                async with client.get(url=url, params=params, ssl=ssl_context) as response:
                    response.raise_for_status()
                    data = await response.json()

                    try:
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
                                ))

                    except Exception as _ex:
                        facebook_logger.error(f'Report failed with error: {_ex}')
                        return False
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
            );""", debug=True)
    facebook_logger.info(f'Facebook report complete with {item} records')
    return True





