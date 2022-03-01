import psycopg2
from getpass import getpass


def connect():
    conn = psycopg2.connect(dbname="agm_ht",
                            user="noah",
                            password=getpass())
    return conn.cursor()
