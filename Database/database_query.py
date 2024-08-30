from Bot.logging_settings import database_query_logger
from .database import db
from Bot.dialogs import RU_ru


def white_list():
    white = db.query("SELECT user_id FROM white_list", fetch='fetchall')
    developer_id_1 = db.query(query="SELECT user_id FROM white_list WHERE super_admin=true", fetch='fetchall')
    developer_id = [item for tup in developer_id_1 for item in tup]
    admins_list_1 = db.query(query="SELECT user_id FROM white_list WHERE admin=true", fetch='fetchall')
    admins_list = [item for tup in admins_list_1 for item in tup]
    step_3 = {}

    for ids in white:
        try:
            user = db.query("SELECT (user_name, user_surname, username) FROM users WHERE user_id=%s",
                            values=ids,
                            fetch='fetchone')[0]
            if ids[0] in developer_id:
                pass
            elif ids[0] in admins_list:
                translator_user = str.maketrans('', '', '()')
                step_1 = user.translate(translator_user)
                step_2 = step_1.replace(',', ' ')
                step_3[f'white_{ids[0]}'] = '[ADM] ' + step_2
            else:
                translator_user = str.maketrans('', '', '()')
                step_1 = user.translate(translator_user)
                step_2 = step_1.replace(',', ' ')
                step_3[f'white_{ids[0]}'] = step_2
        except:
            pass
    return step_3


def admins_lists():
    developer_id_1 = db.query(query="SELECT user_id FROM white_list WHERE super_admin=true", fetch='fetchall')
    developer_id = [item for tup in developer_id_1 for item in tup]
    admins_list_1 = db.query(query="SELECT user_id FROM white_list WHERE admin=true", fetch='fetchall')
    admins_list = [item for tup in admins_list_1 for item in tup]
    admins_list.extend(developer_id)
    admins_list = [int(d) for d in admins_list]
    return admins_list


def token_list():
    tokens_lists = db.query(query='SELECT api_token, service, id FROM tokens', fetch='fetchall')
    step = {}
    keys = ['token', 'service', 'id']

    for i in range(len(tokens_lists)):
        step_1 = tokens_lists[i]

        step[f'token_{step_1[2]}'] = {}

        for v in range(len(step_1)):
            step[f'token_{step_1[2]}'][keys[v]] = step_1[v]

    return step
