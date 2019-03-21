"""
Functions for dealing with dummy data.

These are simplified units of data used for testing
before implementing entire course funding requests
"""

import json
from . import sql_connection as sql

def insert_dummy_data(json_str: str):
    """
    Insert the rows of dummy data defined in the
    given JSON string into the database
    """

    data = json.loads(json_str)

    cursor = sql.new_cursor()

    for row in data:
        cursor.execute(
            "INSERT INTO dummy_data VALUES (%s, %s, %s, %s)",
            (row['name1'], row['num1'], row['num2'], row['num3'])
        )

    sql.get_connection().commit()
    cursor.close()
    sql.disconnect()
