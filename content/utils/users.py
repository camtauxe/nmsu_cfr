"""
Functions related to manipulating users in the database
"""
from .sql_connection import Transaction
from .authentication import hash_password, User
from .errors import Error400
from . import db_utils

# Query to insert a new user into the database
# Parameters are username, usr_password, banner_id and type (role)
ADD_USER = """
INSERT INTO user VALUES (
    %s, %s, %s, %s
)
"""

# Query to insert a new entry into the submitter table
# Parameters are: username, dept_name
ADD_SUBMITTER = """
INSERT INTO submitter VALUES (%s, %s)
"""

# Query to update a user's password
# Parameters: usr_password (hashed), username
UPDATE_PASSWORD = """
UPDATE user SET usr_password = %s WHERE username = %s
"""

# Query to delete a user
# Parameters are: username
DELETE_USER = """
DELETE FROM user WHERE username = %s
"""

def edit_user(query, current_user: User):
    """
    Delete a user or change their password

    query is a dict parsed from the form data in a POST request.
    It should contain the following fields:
        'button': A string; either 'delete' or 'password' specifying
        what action to take
        'user': The username of the user to update or delete
    The following fields are only needed if 'button' is 'password'
        'password': The new password to set
        'passwordconfirm': Must match 'password'

    current_user is 

    Any problems with the data will result in a Error400 being thrown.
    """
    if 'user' not in query:
        raise Error400("Missing 'user' parameter!")

    with Transaction() as cursor:
        # Check that the specified user exists
        username = query['user'][0]
        if not db_utils.does_user_exist(cursor, username):
            raise Error400(f"User {query['user'][0]} does not exist!")

        if 'button' not in query:
            raise Error400("Missing 'button' parameter!")
        choice = query['button'][0]

        # Update the user's password
        if choice == 'password':
            # Validate
            if 'password' not in query or 'passwordconfirm' not in query:
                raise Error400("Missing 'password' or 'passwordconfirm' parameter!")
            password = query['password'][0]
            confirm = query['passwordconfirm'][0]
            if password == "":
                raise Error400("'password' cannot be empty!")
            if password != confirm:
                raise Error400("'password' and 'passwordconfirm' must match!")
            
            # Hash and update password
            password_hash = hash_password(password)
            cursor.execute(UPDATE_PASSWORD, (password_hash, username))

        # Delete the user
        elif choice == 'delete':
            if username == current_user.username:
                raise Error400("You cannot delete yourself!")
            cursor.execute(DELETE_USER, (username,))

        else:
            raise Error400("'button' value must be either 'password' or 'delete'!")

def add_user(query):
    """
    Add a new user to the database.

    query is a dict parsed from the form data in a POST request.
    It should contain the following fields:
        'username': A string
        'password': A string
        'passwordconfirm': Should match 'password'
        'banner_id': An integer
        'role': A string; either 'submitter', 'approver' or 'admin'
    If 'role' is 'submitter', there must be an additional field: 'dept_name'
    """
    fields = ['username', 'password', 'passwordconfirm', 'banner_id', 'role']
    if not all(k in query for k in fields):
        raise Error400("Missing parameters! Must have: "+str(fields))

    with Transaction() as cursor:
        # Check that the specified user does not already exist
        username = query['username'][0]
        if db_utils.does_user_exist(cursor, username):
            raise Error400(f"User {username} already exists!")

        # Validate password
        password = query['password'][0]
        confirm = query['passwordconfirm'][0]
        if password == "":
            raise Error400("'password' cannot be empty!")
        if password != confirm:
            raise Error400("'password' and 'passwordconfirm' must match!")
        password_hash = hash_password(password)

        # Validate banner_id
        try:
            banner_id = int(query['banner_id'][0])
        except ValueError:
            raise Error400("'banner_id' must be an integer!")

        # Validate role
        role = query['role'][0]
        if role not in ['submitter', 'approver','admin']:
            raise Error400("'role' must be 'submitter','approver' or 'admin'!")

        # Insert user
        insert_data = (username, password_hash, banner_id, role)
        cursor.execute(ADD_USER, insert_data)

        # If the user is a submitter, insert them and their department
        # into the submitter table
        if role == 'submitter':
            if 'dept_name' not in query:
                raise Error400("submitters must have a 'dept_name' parameter")
            dept_name = query['dept_name'][0]
            cursor.execute(ADD_SUBMITTER, (username, dept_name))






