"""
Functions related to manipulating users in the database
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

USERNAMES_QUERY = """
SELECT username FROM user
"""

DEPARTMENTS_QUERY = """
SELECT DISTINCT dept_name FROM submitter
"""

def get_usernames():
    usernames = []
    with Transaction() as cursor:
        cursor.execute(USERNAMES_QUERY)
        usernames = [d[0] for d in cursor.fetchall()]
    return usernames

def get_departments():
    departments = []
    with Transaction() as cursor:
        cursor.execute(DEPARTMENTS_QUERY)
        departments = [d[0] for d in cursor.fetchall()]
    return departments

def edit_user(query, current_user):
    if 'user' not in query:
        raise Error400("Missing 'user' parameter!")

    with Transaction() as cursor:
        cursor.execute(
            "SELECT username FROM user WHERE username = %s",
            (query['user'][0],)
        )
        result = cursor.fetchone()
        if result is None:
            raise Error400(f"User {query['user'][0]} does not exist!")
        username = result[0]

        if 'button' not in query:
            raise Error400("Missing 'button' parameter!")
        choice = query['button'][0]

        if choice == 'password':
            if 'password' not in query or 'passwordconfirm' not in query:
                raise Error400("Missing 'password' or 'passwordconfirm' parameter!")
            password = query['password'][0]
            confirm = query['passwordconfirm'][0]
            if password == "":
                raise Error400("'password' cannot be empty!")
            if password != confirm:
                raise Error400("'password' and 'passwordconfirm' must match!")
            
            password_hash = hash_password(password)
            cursor.execute(
                "UPDATE user SET usr_password = %s WHERE username = %s",
                (password_hash, username))

        elif choice == 'delete':
            if username == current_user.username:
                raise Error400("You cannot delete yourself!")
            cursor.execute("DELETE FROM user WHERE username = %s", (username,))

        else:
            raise Error400("'button' value must be either 'password' or 'delete'!")


def add_user(query):
    fields = ['username', 'password', 'passwordconfirm', 'banner_id', 'role']
    if not all(k in query for k in fields):
        raise Error400("Missing parameters! Must have: "+str(fields))

    with Transaction() as cursor:
        username = query['username'][0]

        cursor.execute(
            "SELECT username FROM user WHERE username = %s", (username,))
        result = cursor.fetchone()
        if result is not None:
            raise Error400(f"User {username} already exists!")

        password = query['password'][0]
        confirm = query['passwordconfirm'][0]
        if password == "":
            raise Error400("'password' cannot be empty!")
        if password != confirm:
            raise Error400("'password' and 'passwordconfirm' must match!")
        password_hash = hash_password(password)

        try:
            banner_id = int(query['banner_id'][0])
        except ValueError:
            raise Error400("'banner_id' must be an integer!")

        role = query['role'][0]
        if role not in ['submitter', 'approver','admin']:
            raise Error400("'role' must be 'submitter','approver' or 'admin'!")

        insert_data = (username, password_hash, banner_id, role)
        cursor.execute(ADD_USER_QUERY, insert_data)

        if role == 'submitter' and 'dept_name' not in query:
            raise Error400("submitters must have a 'dept_name' parameter")
        dept_name = query['dept_name'][0]

        cursor.execute(
            "INSERT INTO submitter VALUES (%s, %s)",
            (username, dept_name)
        )






