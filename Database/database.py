from typing import Any

import psycopg2

from config import host, user, password, db_name, port
from Bot.utils.logging_settings import database_logger


class Database:
    def __init__(self, host=host, port=port, db_name=db_name, user=user, password=password):
        try:
            self.connect = psycopg2.connect(host=host,
                                            port=port,
                                            database=db_name,
                                            user=user,
                                            password=password)
            self.cursor = self.connect.cursor()
            database_logger.debug('DataBase connection...')
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
              msg: str = msg) -> Any:
        """
        :param query: takes sql query, for example: "SELECT * FROM table"
        :param values: takes tuple of values
        :param fetch: choose of one upper this list
        :param size: count of fetching info from database. Default 10, JUST FOR fetchmany
        :param log_level: choose of logging level if needed. Default 40[ERROR]
        :param msg: message for logger

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
            database_logger.log(msg=msg, level=log_level)
            self.cursor.execute('ROLLBACK TO point1')
            return 'Error'


db = Database()

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
        service TEXT NOT NULL
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
                    hour INTEGER NOT NULL,
                    minute INTEGER NOT NULL
                );
"""


db.query(query=create_users_table)
db.query(query=create_white_list_table)
db.query(query=create_tokens_table)
db.query(query=create_adaccounts_table)
db.query(query=create_reports_table_query)
db.query(query=create_scheduler_table)
