from typing import Any

import psycopg2

from config import host, user, password, db_name, port, db_name_ewebinar, russia_host, russia_port, \
    russia_db_name, russia_user, russia_password
from Bot.utils.logging_settings import database_logger


class Database:
    def __init__(self, host, port, db_name, user, password):
        try:
            self.connect = psycopg2.connect(host=host,
                                            port=port,
                                            database=db_name,
                                            user=user,
                                            password=password,
                                            options="-c client_encoding=UTF8")
            self.cursor = self.connect.cursor()
            database_logger.debug(f'DataBase - *{db_name}* connection...')
            with self.connect.cursor() as cursor:
                cursor.execute(
                    "SELECT version();"
                )
                database_logger.debug(f'Server version: {cursor.fetchone()[0]}')
        except Exception as _ex:
            database_logger.critical(f'Can`t establish connection to DataBase with error: {_ex}')

    def close(self):
        self.cursor.close()
        self.connect.close()

    msg = f'The sql query failed with an error'

    def query(self, query: str, values: tuple = None, execute_many = False, fetch: str = None, size: int = None, log_level: int = 40,
              msg: str = msg, debug: bool = False) -> Any:
        """
        :param query: takes sql query, for example: "SELECT * FROM table"
        :param values: takes tuple of values
        :param execute_many: if True - change cursor *execute* to *execute_many*
        :param fetch: choose of one upper this list
        :param size: count of fetching info from database. Default 10, JUST FOR fetchmany
        :param log_level: choose of logging level if needed. Default 40[ERROR]
        :param msg: message for logger
        :param debug: make Exception error message

        - fetch:
            1. fetchone
            2. fetchall
            3. fetchmany - size required(default 10)
            4. None - using for UPDATE, DELETE etc.

        - log_level:
            1. 10 (Debug) - the lowest logging level, intended for debugging messages, for displaying diagnostic information about the application.
            2. 20 (Info) - this level is intended for displaying data about code fragments that work as expected.
            3. 30 (Warning) - this logging level provides for the display of warnings, it is used to record information about events that a programmer usually pays attention to. Such events may well lead to problems during the operation of the application. If you do not explicitly set the logging level, the warning is used by default.
            4. 40 (Error)(default) - this logging level provides for the display of information about errors - that part of the application does not work as expected, that the program could not execute correctly.
            5. 50 (Critical) - this level is used to display information about very serious errors, the presence of which threatens the normal functioning of the entire application. If you do not fix such an error, this may lead to the application ceasing to work.
        """
        try:
            self.cursor.execute('SAVEPOINT point1')
            if fetch == 'fetchone':
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                        return cursor.fetchone()
                    else:
                        cursor.execute(query, values)
                        return cursor.fetchone()
            elif fetch == 'fetchall':
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                        return cursor.fetchall()
                    else:
                        cursor.execute(query, values)
                        return cursor.fetchall()
            elif fetch == 'fetchmany':
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                        return cursor.fetchmany(size=size)
                    else:
                        cursor.execute(query, values)
                        return cursor.fetchmany(size=size)
            else:
                with self.connect.cursor() as cursor:
                    if values is None:
                        cursor.execute(query)
                    else:
                        if execute_many:
                            cursor.executemany(query, values)
                        else:
                            cursor.execute(query, values)
            self.cursor.execute('RELEASE point1')
            self.connect.commit()
            return 'Success'
        except Exception as _ex:
            if debug:
                database_logger.log(msg=_ex, level=log_level)
                self.cursor.execute('ROLLBACK TO point1')
                return 'Error'
            else:
                database_logger.log(msg=msg, level=log_level)
                self.cursor.execute('ROLLBACK TO point1')
                return 'Error'


db = Database(host=host, port=port, db_name=db_name, user=user, password=password)

ewebinar_db = Database(host=host, port=port, db_name=db_name_ewebinar, user=user, password=password)

getcourse_db = Database(host=russia_host, port=russia_port, db_name=russia_db_name, user=russia_user, password=russia_password)

create_users_table = """
CREATE TABLE IF NOT EXISTS users (
    user_id BIGINT UNIQUE NOT NULL,
    user_name TEXT CHECK (char_length(user_name) <= 500),
    username TEXT CHECK (char_length(username) <= 500),
    user_surname TEXT CHECK (char_length(user_surname) <= 500),
    id SERIAL PRIMARY KEY
);
"""

create_white_list_table = """
    CREATE TABLE IF NOT EXISTS white_list (
        id SERIAL PRIMARY KEY,
        user_id NUMERIC(50) UNIQUE,
        admin BOOLEAN DEFAULT FALSE,
        super_admin BOOLEAN DEFAULT FALSE
    )
    """

create_tokens_table = """
    CREATE TABLE IF NOT EXISTS tokens (
        id SERIAL PRIMARY KEY,
        api_token TEXT UNIQUE NOT NULL,
        service TEXT NOT NULL,
        account_name TEXT DEFAULT NULL
    )
    """

create_adaccounts_table = """
    CREATE TABLE IF NOT EXISTS adaccounts (
        id SERIAL PRIMARY KEY,
        api_token TEXT NOT NULL,
        acc_name TEXT NOT NULL,
        acc_id TEXT NOT NULL,
        is_active BOOLEAN DEFAULT FALSE,
        account_name BOOLEAN DEFAULT FALSE,
        account_id BOOLEAN DEFAULT FALSE,
        campaign_name BOOLEAN DEFAULT FALSE,
        campaign_id BOOLEAN DEFAULT FALSE,
        adset_name BOOLEAN DEFAULT FALSE,
        adset_id BOOLEAN DEFAULT FALSE,
        ad_name BOOLEAN DEFAULT FALSE,
        ad_id BOOLEAN DEFAULT FALSE,
        impressions BOOLEAN DEFAULT FALSE,
        frequency BOOLEAN DEFAULT FALSE,
        clicks BOOLEAN DEFAULT FALSE,
        unique_clicks BOOLEAN DEFAULT FALSE,
        spend BOOLEAN DEFAULT FALSE,
        reach BOOLEAN DEFAULT FALSE,
        cpp BOOLEAN DEFAULT FALSE,
        cpm BOOLEAN DEFAULT FALSE,
        unique_link_clicks_ctr BOOLEAN DEFAULT FALSE,
        ctr BOOLEAN DEFAULT FALSE,
        unique_ctr BOOLEAN DEFAULT FALSE,
        cpc BOOLEAN DEFAULT FALSE,
        cost_per_unique_click BOOLEAN DEFAULT FALSE,
        objective BOOLEAN DEFAULT FALSE,
        buying_type BOOLEAN DEFAULT FALSE,
        created_time BOOLEAN DEFAULT FALSE,
        level TEXT DEFAULT 'ad',
        date_preset TEXT DEFAULT 'maximum',
        increment NUMERIC DEFAULT 1
    )
    """

create_reports_table_query = """
    CREATE TABLE IF NOT EXISTS reports (
        account_name TEXT,
        account_id TEXT,
        campaign_name TEXT,
        campaign_id TEXT,
        adset_name TEXT,
        adset_id TEXT,
        ad_name TEXT,
        ad_id TEXT,
        impressions TEXT,
        frequency TEXT,
        clicks TEXT,
        unique_clicks TEXT,
        spend TEXT,
        reach TEXT,
        cpp TEXT,
        cpm TEXT,
        unique_link_clicks_ctr TEXT,
        ctr TEXT,
        unique_ctr TEXT,
        cpc TEXT,
        cost_per_unique_click TEXT,
        objective TEXT,
        buying_type TEXT,
        created_time TEXT,
        date_start TEXT,
        date_stop TEXT
    );
    """

create_scheduler_table = """CREATE TABLE IF NOT EXISTS scheduled_jobs (
                    job_id VARCHAR(255) UNIQUE NOT NULL,
                    time VARCHAR
                );
"""

create_ewebinar_table = """
    CREATE TABLE IF NOT EXISTS EWEBINAR (
    actions TEXT,
    addToCalendarLink TEXT,
    allWebinarsLink TEXT,
    attended TEXT,
    chatsSent TEXT,
    city TEXT,
    country TEXT,
    deviceTypeWhenRegistered TEXT,
    deviceTypeWhenWatching TEXT,
    email TEXT,
    emailVerified TEXT,
    firstName TEXT,
    firstOrigin TEXT,
    firstReferrer TEXT,
    httpsdrivegoogle TEXT,
    id TEXT,
    ip TEXT,
    joinedTime TEXT,
    joinLink TEXT,
    lastName TEXT,
    leftTime TEXT,
    likes TEXT,
    name TEXT,
    neurographicsCourse TEXT,
    origin TEXT,
    referrer TEXT,
    registeredTime TEXT,
    registrationLink TEXT,
    replayLink TEXT,
    sessionTime TEXT,
    sessionType TEXT,
    source TEXT,
    state TEXT,
    subscribed TEXT,
    timezone TEXT,
    totalWatchedPercent TEXT,
    utm_campaign TEXT,
    utm_content TEXT,
    utm_medium TEXT,
    utm_source TEXT,
    utm_term TEXT,
    watchedScheduledPercent TEXT,
    webinarId TEXT,
    webinarTitle TEXT
        );
    """


create_getcourse_users_table =  """
    CREATE TABLE IF NOT EXISTS GetCourse_users (
        id TEXT UNIQUE,
        Email TEXT,
        Registration_Type TEXT,
        Created TEXT,
        Last_Activity TEXT,
        First_Name TEXT,
        Last_Name TEXT,
        Phone TEXT,
        Date_of_Birth TEXT,
        Age TEXT,
        Country TEXT,
        City TEXT,
        From_Partner TEXT,
        Client_Portrait TEXT,
        Comments TEXT,
        Bil_minut TEXT,
        Dosmotrel_do_kontsa TEXT,
        Button_Click TEXT,
        Web_Room TEXT,
        Data_Webinara TEXT,
        Vremya_Start TEXT,
        Vremya_End TEXT,
        Bil_na_Webe TEXT,
        Banner_Click TEXT,
        City_2 TEXT,
        Pay_At TEXT,
        SB_ID TEXT,
        Partner_ID TEXT,
        Partner_Email TEXT,
        Partner_Full_Name TEXT,
        utm_source TEXT,
        utm_medium TEXT,
        utm_campaign TEXT,
        utm_term TEXT,
        utm_content TEXT,
        Bil_minut_2 TEXT,
        utm_group TEXT,
        btn_1 TEXT,
        btn_2 TEXT,
        btn_3 TEXT,
        LM_utm_source TEXT,
        LM_utm_medium TEXT,
        LM_utm_term TEXT,
        LM_utm_content TEXT,
        LM_utm_campaign TEXT,
        btn_4 TEXT,
        btn_5 TEXT,
        btn_6 TEXT,
        Instagram_Telegram_Nick TEXT,
        Income_Money TEXT,
        btn_7 TEXT,
        btn_8 TEXT,
        web_time TEXT,
        webhook_time_web TEXT,
        btn_9 TEXT,
        From_Where TEXT,
        utm_source_2 TEXT,
        utm_medium_2 TEXT,
        utm_campaign_2 TEXT,
        utm_term_2 TEXT,
        utm_content_2 TEXT,
        utm_group_2 TEXT,
        Partner_ID_2 TEXT,
        Partner_Email_2 TEXT,
        Partner_FullName TEXT,
        Manager_FullName TEXT,
        VK_ID TEXT
    );
    """


db.query(query=create_users_table)
db.query(query=create_white_list_table)
db.query(query=create_tokens_table)
db.query(query=create_adaccounts_table)
db.query(query=create_reports_table_query)
db.query(query=create_scheduler_table)
ewebinar_db.query(query=create_ewebinar_table)
getcourse_db.query(query=create_getcourse_users_table)
