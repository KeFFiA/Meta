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

    def query(self, query: str, values: tuple = None, fetch: str = None, size: int = None, log_level: int = 40,
              msg: str = msg, debug: bool = False) -> Any:
        """
        :param query: takes sql query, for example: "SELECT * FROM table"
        :param values: takes tuple of values
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

create_ewebinar_table = '''
    CREATE TABLE IF NOT EXISTS ewebinar (
        id VARCHAR,
        firstName VARCHAR,
        lastName VARCHAR,
        name VARCHAR,
        email VARCHAR,
        subscribed VARCHAR,
        registrationLink VARCHAR,
        replayLink VARCHAR,
        joinLink VARCHAR,
        addToCalendarLink VARCHAR,
        timezone VARCHAR,
        sessionType VARCHAR,
        registeredTime TIMESTAMPTZ,
        sessionTime VARCHAR,
        joinedTime TIMESTAMPTZ,
        leftTime TIMESTAMPTZ,
        attended VARCHAR,
        likes INTEGER,
        watchedPercent DECIMAL,
        watchedScheduledPercent DECIMAL,
        watchedReplayPercent DECIMAL,
        purchaseAmount DECIMAL,
        converted BOOLEAN,
        tags TEXT[],  -- массив строк
        source VARCHAR,
        referrer VARCHAR,
        origin VARCHAR,
        utm_source VARCHAR,
        utm_medium VARCHAR,
        utm_campaign VARCHAR,
        utm_term VARCHAR,
        utm_content VARCHAR,
        gclid VARCHAR,
        ip VARCHAR,
        city VARCHAR,
        country VARCHAR
    );
    '''


create_getcourse_table = """
    CREATE TABLE IF NOT EXISTS GetCourse (
        id VARCHAR(250),
        Email VARCHAR(250),
        Registration_Type VARCHAR(250),
        Created VARCHAR(250),
        Last_Activity VARCHAR(250),
        First_Name VARCHAR(250),
        Last_Name VARCHAR(250),
        Phone VARCHAR(250),
        Date_of_Birth VARCHAR(250),
        Age VARCHAR(250),
        Country VARCHAR(250),
        City VARCHAR(250),
        From_Partner VARCHAR(250),
        Client_Portrait VARCHAR(250),
        Comments VARCHAR(250),
        Bil_minut VARCHAR(250),
        Dosmotrel_do_kontsa VARCHAR(250),
        Button_Click VARCHAR(250),
        Web_Room VARCHAR(250),
        Data_Webinara VARCHAR(250),
        Vremya_Start VARCHAR(250),
        Vremya_End VARCHAR(250),
        Bil_na_Webe VARCHAR(250),
        Banner_Click VARCHAR(250),
        SB_ID VARCHAR(250),
        Partner_ID VARCHAR(250),
        Partner_Email VARCHAR(250),
        Partner_Full_Name VARCHAR(250),
        utm_source VARCHAR(250),
        utm_medium VARCHAR(250),
        utm_campaign VARCHAR(250),
        utm_term VARCHAR(250),
        utm_content VARCHAR(250),
        Bil_minut_2 VARCHAR(250),
        utm_group VARCHAR(250),
        btn_1 VARCHAR(250),
        btn_2 VARCHAR(250),
        btn_3 VARCHAR(250),
        LM_utm_source VARCHAR(250),
        LM_utm_medium VARCHAR(250),
        LM_utm_term VARCHAR(250),
        LM_utm_content VARCHAR(250),
        LM_utm_campaign VARCHAR(250),
        btn_4 VARCHAR(250),
        btn_5 VARCHAR(250),
        btn_6 VARCHAR(250),
        Instagram_Telegram_Nick VARCHAR(250),
        Income_Money VARCHAR(250),
        btn_7 VARCHAR(250),
        btn_8 VARCHAR(250),
        web_time VARCHAR(250),
        webhook_time_web VARCHAR(250),
        btn_9 VARCHAR(250),
        From_Where VARCHAR(250),
        utm_source_2 VARCHAR(250),
        utm_medium_2 VARCHAR(250),
        utm_campaign_2 VARCHAR(250),
        utm_term_2 VARCHAR(250),
        utm_content_2 VARCHAR(250),
        utm_group_2 VARCHAR(250),
        Partner_ID_2 VARCHAR(250),
        Partner_Email_2 VARCHAR(250),
        Partner_FullName VARCHAR(250),
        Manager_FullName VARCHAR(250),
        VK_ID VARCHAR(250)
    );
    """


db.query(query=create_users_table)
db.query(query=create_white_list_table)
db.query(query=create_tokens_table)
db.query(query=create_adaccounts_table)
db.query(query=create_reports_table_query)
db.query(query=create_scheduler_table)
ewebinar_db.query(query=create_ewebinar_table)
getcourse_db.query(query=create_getcourse_table)
