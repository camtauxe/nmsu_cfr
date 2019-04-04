"""
Functions for dealing with dummy data.

These are simplified units of data used for testing
before implementing entire course funding requests
"""
import json
from .sql_connection import Transaction

# Query to insert a row of dummy data into the database
# Parameters are name, value1, value2 and value3
INSERT_DUMMY_QUERY = """
INSERT INTO dummy_data VALUES 
    (%s, %s, %s, %s)
"""

def insert_dummy_data(json_str: str):
    """
    Insert the rows of dummy data defined in the
    given JSON string into the database
    """

    data = json.loads(json_str)

    with Transaction() as cursor:
        for row in data:
            params = (row['name1'], row['num1'], row['num2'], row['num3'])
            cursor.execute(INSERT_DUMMY_QUERY, params)
