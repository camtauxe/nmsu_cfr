"""
Functions related to authenticating a user
"""
import http.cookies as cookies
from . import sql_connection as sql
from enum import Enum, auto

SECONDS_PER_DAY = 86400

class UserRole(Enum):
    SUBMITTER   = auto()
    APPROVER    = auto()
    ADMIN       = auto()

class User:

    def __init__(self, user_dict: dict):
        self.username   = user_dict['username']
        self.role       = UserRole[user_dict['role']]

def authenticate(username) -> User:
    """
    Authenticate with the given credintials and returns a dictionary
    of user information if successful, otherwise returns None

    Right now, this literally only checks that the given username is
    in the users table. This is just for testing purposes and will later
    have to be imlpemented with passwords and actual security stuff
    """

    cursor = sql.new_cursor(dictionary=True)
    cursor.execute('SELECT username, role FROM user WHERE username = %s', (username,))

    result = cursor.fetchone()

    if result is None:
        return None
    else:
        return User(result)

def authenticate_from_cookie(cookies_header: str) -> User:
    cookie = cookies.SimpleCookie()
    cookie.load(cookies_header)
    username = cookie['username'].value
    return authenticate(username)

def create_cookie(user: User) -> str:
    return "username={}; Max-Age={}".format(user.username, SECONDS_PER_DAY)

def clear_cookie() -> str:
    return "username=; Max-Age=0"