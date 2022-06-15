import sqlite3
from sqlite3 import Error


# try_create_db: Creates a DB file if none exists at <target>
# If successful, returns the connection. Otherwise, returns None.
def try_connect_db(target):
    conn = None
    try:
        conn = sqlite3.connect(target)
    except Error as e:
        print(e)
    finally:
        if conn:
            return conn
        else:
            return None
