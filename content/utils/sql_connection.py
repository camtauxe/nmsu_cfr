"""
Manages the connection to the MySQL server
"""
import os
import mysql.connector as conn
from typing import List
from . import cfrenv

class Transaction:
    """
    Transaction is the primary means of interacting with the MySQL server.

    It is a context manager designed to be used with the 'with' statement.
    Using the with statement, Transaction returns a new cursor in a new connection
    to the database. After exiting the code block, the database connection
    and cursor are automatically closed (if an exception occurs in the
    middle of the code block, the database connection will still automatically
    be closed).

    Any keyword arguments passed to Transaction will be passed along to the
    cursor.

    Example:

    with Transaction(buffered = True) as cursor:
        cursor.execute(...)
        ...
        ...

    """
    def __init__(self, **kwargs):
        self._cursor_kwargs = kwargs

    def __enter__(self):
        self._connection = conn.connect(
            user        = cfrenv.getenv('DB_USER'),
            passwd      = cfrenv.getenv('DB_PASS'),
            host        = cfrenv.getenv('DB_HOST'),
            database    = cfrenv.getenv('DB_DATABASE')
        )
        self._cursor = self._connection.cursor(**self._cursor_kwargs)
        return self._cursor

    def __exit__(self, type, value, traceback):
        if traceback is None:
            self._connection.commit()
        else:
            self._connection.rollback()
        self._cursor.close()
        self._connection.close()
