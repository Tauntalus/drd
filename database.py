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


# try_create_table: given a connection, table name, and fields,
# attempts to create a table that matches the schema.
# returns connection on success, None on fail
def try_create_table(conn, table, schema):
    # From table info, build SQL string
    table_format = str(table) + "("
    for field in schema:
        table_format += str(field) + ", "
    table_format += ")"

    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("IF NOT EXISTS CREATE TABLE ?", table_format)
            cursor.close()
            return conn
        except Error as e:
            print(e)
            return None


# close: closes the DB connection.
def close(conn):
    conn.close()


class DBInfo:
    def __init__(self, file, tables, schemas):
        self.file = file
        self.tables = tables
        self.schemas = schemas
