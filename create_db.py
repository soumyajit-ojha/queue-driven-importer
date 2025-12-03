"""
This module used to check and create database
"""


import traceback
from datetime import datetime
import pymysql
from decouple import config

VARS={
    "host":config("DB_HOST"),
    "db_name":config("DB_NAME"),
    "user":config("DB_USER"),
    "password":config("DB_PASS"),
    "port":config("DB_PORT"),
}

def create_database(db_name:str):
    """
    It check database exitance then create.
    - parameters:
        - db_name : str (name of the database)
    - returns:
        - message : str (message of database create or existance.)
    - errors:
        - message : str (error message.)
    """
    try:
        mysql_conn = pymysql.connect(
            host=VARS["host"],
            user=VARS["user"],
            password=VARS["password"],
            port=int(VARS["port"]),
        )
        cur = mysql_conn.cursor()
        cur.execute("SHOW DATABASES")
        dbs = []
        for i in cur.fetchall():
            dbs += i
        if db_name not in dbs:
            cur.execute(f"CREATE DATABASE IF NOT EXISTS {db_name}")
            print(f"INFO : {datetime.now()} {db_name} database successfully created...")
        else:
            print(f"ERROR : {datetime.now()} {db_name} database already existed...")
        mysql_conn.close()
    except Exception:
        print(traceback.format_exc())


name = VARS["db_name"]
create_database(db_name=name)
