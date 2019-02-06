"""
Functions to manage the connection to the MySQL server
"""
import os
import mysql.connector as con

# Global variable for the MySQL Connection.
_connection: con.MySQLConnection = None

def connect():
    """
    Form a connection to the MySQL server.
    If a connection is already made, this does nothing.
    """
    if _connection is None:
        _connection = con.connect(
            user        = os.getenv('DB_USER'),
            passwd      = os.getenv('DB_PASS'),
            host        = os.getenv('DB_HOST'),
            database    = os.getenv('DB_DATABASE')
        )

def disconnect():
    """
    Disconnect from the MySQL server. If the connection is already
    disconnected. This does nothing.
    """
    if _connection is not None:
        _connection.close()
        _connection = None

def new_cursor() -> con.cursor.MySQLCursor:
    """
    Create and return a new cursor for the MySQL connection.
    If a connection has not been made yet, the connection will
    be made automatically.
    """
    if _connection is None:
        connect()
    return _connection.cursor()

def get_connection() -> con.MySQLConnection:
    return _connection

def is_connected() -> bool:
    return bool(_connection is not None)
