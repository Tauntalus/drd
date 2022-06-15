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
# TODO: harden against SQL injection
def try_create_table(conn, table, schema):
    # From table info, build SQL string
    table_format = str(table) + " ("
    for field in schema:
        table_format += str(field) + ", "
    table_format = table_format[:-2]  # Cut away redundant extra ", "
    table_format += ")"

    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS %(sql)s;" % {"sql": table_format})
            print("DB: Created table %(table)s." % {"table":table_format})
        except Error as e:
            print(e)
        finally:
            cursor.close()
            return conn


# try_basic_select: given a connection, table name, fields, and optional WHERE clause,
# attempts to process a SELECT query to get <fields> from <table> which satisfies <cond>
# Returns connection, and query result.
def try_basic_select(conn, table, fields, cond=None):
    ret = None
    inserts = (table,) + fields
    if conn:
        cursor = conn.cursor()
        try:
            if cond:
                inserts += cond
                cursor.execute("SELECT ? FROM ? WHERE ?;", inserts)
                print("DB: SELECT processed.")
                print("DB: %(fields)s, %(table)s, %(cond)s" % {"fields": fields, "table": table, "cond": cond})
            else:
                cursor.execute("SELECT ? FROM ?;", inserts)
                print("DB: SELECT processed.")
                print("DB: %(fields)s, %(table)s" % {"fields": fields, "table": table})
        except Error as e:
            print(e)
        finally:
            cursor.close()
            return conn, ret
    return


# try_execute: given a connection, SQL query, and insertion list,
# attempts to execute the SQL query as written.
# Returns connection, and query result.
def try_execute(conn, sql, inserts=None):
    ret = None
    if conn:
        cursor = conn.cursor()
        try:
            ret = cursor.execute(sql, inserts)
        except Error as e:
            print(e)
        finally:
            cursor.close()
            return conn, ret


# close: closes the DB connection.
# returns the closed connection.
def close(conn):
    conn.close()
    return conn


# DBInfo: A class for storing SQLite DB information
# members:
#   :name   :type                   :description
#   file    - string,               the SQLite DB file location
#   tables  - tuple/string,         the names of the tables in the SQLite DB
#   schemas - tuple/tuple/string,   the schema for each table in the SQLite DB
class DBInfo:
    def __init__(self, file, tables, schemas):
        self.file = file
        self.tables = tables
        self.schemas = schemas
