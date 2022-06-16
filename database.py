import sqlite3
from sqlite3 import Error


# TODO: Write this to prevent SQL Injection
def process_condition(cond):
    return cond


# try_create_db: Creates a DB file if none exists at <target>
# If successful, returns the connection. Otherwise, returns None.
def try_connect_db(target):
    conn = None
    try:
        conn = sqlite3.connect(target)
        print("DB: Connected to database file \"%(file)s\"." % {"file": target})
    except Error as e:
        print("DB: Error")
        print("DB: " + str(e))
    finally:
        return conn


# try_create_table: given a connection, table name, and fields, and bijective flag,
# attempts to create a table that matches the schema.
# returns connection on success, None on fail
# TODO: harden against SQL injection
def try_create_table(conn, table, schema, biject=False):
    # From table info, build SQL string
    table_format = "'" + str(table) + "'" + " ("
    for field in schema:
        table_format += str(field)
        if biject:
            table_format += " NOT NULL UNIQUE"
        table_format += ", "
    table_format = table_format[:-2]  # Cut away redundant extra ", "
    table_format += ")"

    if conn:
        cursor = conn.cursor()
        try:
            cursor.execute("CREATE TABLE IF NOT EXISTS %(sql)s" % {"sql": table_format})  # TODO: SQL Injection Hazard!
            print("DB: Created table %(table)s." % {"table":table_format})
        except Error as e:
            print("DB: Error")
            print("DB: " + str(e))
        finally:
            cursor.close()
            return conn


# try_execute: given a connection, SQL query, and insertion list,
# attempts to execute the SQL query as written.
# Returns connection, and query result.
def try_execute(conn, sql, values=None):
    ret = None
    if conn:
        cursor = conn.cursor()
        try:
            if values:
                if not isinstance(values, tuple):
                    values = (values,)
                cursor.execute(sql, values)
            else:
                cursor.execute(sql)

            ret = cursor.fetchall()
            print("DB: Executed SQL Statement.")
            print("DB: Query \"%(sql)s\"; Result \"%(ret)s\"." % {"sql": sql, "ret": ret})
        except Error as e:
            print("DB: Error")
            print("DB: " + str(e))
        finally:
            cursor.close()
            return conn, ret


# try_basic_select: given a connection, table name, fields, and optional WHERE clause,
# attempts to process a SELECT query to get <fields> from <table> which satisfies <cond>
# Returns connection, and query result.
# TODO: SQL Injection Hardening
# TODO: Problem areas: conds
def try_select(conn, table, fields, conds=None):
    ret = None

    sql = "SELECT '" + fields + "' FROM '" + table + "';"
    if conn:
        cursor = conn.cursor()
        try:
            if conds:
                sql += " WHERE " + conds  # TODO: SQL Injection Hazard!

                cursor.execute(sql)
                print("DB: SELECT processed.")
                print("DB: Fields %(fields)s; Table %(table)s; Condition %(cond)s." % {"fields": fields, "table": table, "conds": conds})
            else:
                cursor.execute(sql)
                print("DB: SELECT processed.")
                print("DB: Fields %(fields)s; Table %(table)s." % {"fields": fields, "table": table})
        except Error as e:
            print("DB: Error")
            print("DB: " + str(e))
        finally:
            cursor.close()
            return conn, ret


# try_insert: given a connection, table name, and value tuple,
# attempts to insert <values> into <table>
# Returns connection.
def try_insert(conn, table, values):
    sql = "INSERT INTO '" + table + "' VALUES (?, ?)"
    if conn:
        cursor = conn.cursor()
        try:
            ret = cursor.execute(sql, values)
            print("DB: INSERT processed.")
            print("DB: Table %(table)s; Values %(val)s." % {"table": table, "val": values})
        except Error as e:
            print("DB: Error")
            print("DB: " + str(e))
        finally:
            cursor.close()
            return conn, ret


# try_delete: given a connection, table name, and conditions,
# attempts to remove rows from <table> that match <conds>
# Returns connection.
# TODO: SQL Injection Hardening
# TODO: Problem areas: conds
def try_delete(conn, table, conds):
    sql = "DELETE FROM '" + table + "' WHERE " + conds  # TODO: SQL Injection Hazard!
    if conn:
        cursor = conn.cursor()
        try:
            ret = cursor.execute(sql)
            print("DB: DELETE Processed.")
            print("DB: Table %(table)s; Conditions %(conds)s." % {"table": table, "conds": conds})
        except Error as e:
            print("DB: Error")
            print("DB: " + str(e))
        finally:
            cursor.close()
            return conn, ret


# TODO: SQL Injection Hardening
# TODO: Problem areas: values, conds
def try_update(conn, table, values, conds):
    sql = "UPDATE '" + table + "' SET " + values + " WHERE " + conds  # TODO: SQL Injection Hazard!
    if conn:
        cursor = conn.cursor()
        try:
            ret = cursor.execute(sql)
            print("DB: UPDATE Processed.")
            print("DB: Table %(table)s; Values %(val)s; Conditions %(conds)s." % {"table": table, "val": values, "conds": conds})
        except Error as e:
            print("DB: Error")
            print("DB: " + str(e))
        finally:
            cursor.close()
            return conn, ret


# close: commits operations and closes the DB connection.
# returns the closed connection.
def close(conn):
    conn.commit()
    conn.close()
    print("DB: Changes committed.")
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
