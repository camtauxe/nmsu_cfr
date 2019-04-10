"""
Functions related to creating a new user

In the future, this should probably be moved to another file
so that we don't have a whole file with basically only one function
"""
from .sql_connection import Transaction
from .authentication import hash_password
from .errors import Error400

# Query to insert a new user into the database
# Parameters are username, usr_password, banner_id and type (role)
ADD_USER_QUERY = """
INSERT INTO user VALUES (
    %s, %s, %s, %s
)
"""

def create_user(query):
    """
    Insert a new user into the user table.
    If successful, returns the number of rows (users) that were inserted
    (really should just be one, but we might change this function to allow
    inserting more than one user at a time in the future)
    """
    if all(k in query for k in ['username', 'password', 'id', 'usr_role']):
        data = (
            query['username'][0],
            hash_password(query['password'][0]),
            query['id'][0],
            query['usr_role'][0]
        )
        with Transaction() as cursor:
            cursor.execute(ADD_USER_QUERY, data)
            rows_inserted = cursor.rowcount
    else:
        raise Error400("Form data for new_user request is missing parameters!")

    return rows_inserted





