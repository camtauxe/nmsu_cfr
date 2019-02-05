import os
import mysql.connector as con

_connection: con.MySQLConnection = None

def connect():
    if _connection is None:
        _connection = con.connect(
            user        = os.getenv('DB_USER'),
            passwd      = os.getenv('DB_PASS'),
            host        = os.getenv('DB_HOST'),
            database    = os.getenv('DB_DATABASE')
        )

def disconnect():
    if _connection is not None:
        _connection.close()
        _connection = None

def new_cursor() -> con.cursor.MySQLCursor:
    if _connection is None:
        connect()
    return _connection.cursor()

def get_connection() -> con.MySQLConnection:
    return _connection

def is_connected() -> bool:
    return bool(_connection is not None)
