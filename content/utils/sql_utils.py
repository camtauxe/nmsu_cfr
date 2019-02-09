"""
Miscellaneous functions for operations on the database.
"""
from . import sql_connection as sql
import mysql.connector as conn
from typing import List

def get_table_description(tablename) -> List[dict]:
    """
    Get a description of the given table. This is a
    dict equivalent to the result of executing
    DESCRIBE [table]

    Raises a ValueError if the given name is not the
    name of a table in the database.
    """
    if tablename not in sql.get_table_names():
        raise ValueError("Invalid table name!")
    cursor = sql.new_cursor(dictionary=True)
    cursor.execute("DESCRIBE "+tablename)
    desc = cursor.fetchall()
    cursor.close()
    return desc

def get_database_info() -> dict:
    """
    Get a dict with the description for each table in the database
    """
    info = {}
    for table in sql.get_table_names():
        info[table] = get_table_description(table)
    return info
