import os
import mysql.connector

connection = None

def connect():
    global connection
    if connection is None:
        connection = mysql.connector.connect(
            user        = os.getenv('DB_USER'),
            passwd      = os.getenv('DB_PASS'),
            host        = os.getenv('DB_HOST'),
            database    = os.getenv('DB_DATABASE')
        )

def disconnect():
    global connection
    if connection is not None:
        connection.close()
        connection = None