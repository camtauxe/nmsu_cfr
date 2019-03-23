"""
Functions related to creating a new user
"""
from .sql_connection import Transaction
from .authentication import hash_password

# Query to insert a new user into the database
# Parameters are username, usr_password, banner_id and type (role)
ADD_USER_QUERY = """
INSERT INTO user VALUES (
    %s, %s, %s, %s
)
"""

def create_user(username, usr_password, banner_id, usr_role):
    """
    Insert a new user into the user table.
    If successful, returns the number of rows (users) that were inserted
    (really should just be one, but we might change this function to allow
    inserting more than one user at a time in the future)
    """
    with Transaction() as cursor:
        data_user = (username, hash_password(usr_password), banner_id, usr_role)
        cursor.execute(ADD_USER_QUERY, data_user)
        rows_inserted = cursor.rowcount

    return rows_inserted





