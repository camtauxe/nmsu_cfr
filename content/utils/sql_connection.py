"""
Functions to manage the connection to the MySQL server
"""
import os
import mysql.connector as conn
from typing import List

# Global variable for the MySQL Connection.
_connection: conn.MySQLConnection = None
# Global variable listing the names of all the tables in the database
# Empty before a connection is made
_tablenames: List[str] = []

def connect():
    """
    Form a connection to the MySQL server.
    If a connection is already made, this does nothing.
    """
    global _connection, _tablenames
    if _connection is None:
        _connection = conn.connect(
            user        = os.getenv('DB_USER'),
            passwd      = os.getenv('DB_PASS'),
            host        = os.getenv('DB_HOST'),
            database    = os.getenv('DB_DATABASE')
        )
        # Get tablenames
        cursor = _connection.cursor()
        cursor.execute("SHOW tables")
        _tablenames = [d[0] for d in cursor.fetchall()]

def disconnect():
    """
    Disconnect from the MySQL server. If the connection is already
    disconnected. This does nothing.
    """
    global _connection
    if _connection is not None:
        _connection.close()
        _connection = None

def new_cursor(**kwargs) -> conn.cursor.CursorBase:
    """
    Create and return a new cursor for the MySQL connection.
    If a connection has not been made yet, the connection will
    be made automatically.

    Any keyword-arguments passed to this will be passed to the
    MySQL cursor constructor. Please close the cursor when you
    are done with it
    """
    global _connection
    if _connection is None:
        connect()
    return _connection.cursor(**kwargs)

def get_connection() -> conn.MySQLConnection:
    global _connection
    return _connection

def is_connected() -> bool:
    global _connection
    return bool(_connection is not None)

def get_table_names() -> List[str]:
    """
    Get a list of the names of tables in the database.

    If a connection has not been made yet, the connection will
    be made automatically. 
    """
    global _connection, _tablenames
    if _connection is None:
        connect()
    return _tablenames.copy()
