import psycopg2
from getpass import getpass


def connect(*, dbname="agm_ht", user="noah", password=None):
    if password is None:
        password = getpass()
    conn = psycopg2.connect(dbname=dbname,
                            user=user,
                            password=password)
    return conn.cursor()