"""
Functions related to authenticating a user
"""
from . import sql_connection as sql


def authenticate(username):
    """
    Authenticate with the given credintials and returns a dictionary
    of user information if successful, otherwise returns None

    Right now, this literally only checks that the given username is
    in the users table. This is just for testing purposes and will later
    have to be imlpemented with passwords and actual security stuff
    """

    cursor = sql.new_cursor()
    cursor.execute('SELECT username, role FROM user WHERE username = %s', (username,))

    result = cursor.fetchone()

    if result is None:
        return None
    else:
        return {'username': result[0], 'role': result[1]}

