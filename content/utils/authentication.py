"""
Functions related to authenticating a user
"""
import http.cookies as cookies
from . import sql_connection as sql
from enum import Enum, auto

# Number of seconds in a day. Used for specifying the Max-Age of cookies
SECONDS_PER_DAY = 86400

class UserRole(Enum):
    """
    Enum representation of user roles
    """
    SUBMITTER   = auto()
    APPROVER    = auto()
    ADMIN       = auto()

class User:
    """
    Class representing an authenticated user
    """
    def __init__(self, user_dict: dict):
        """
        Initialize a User. user_dict is a dictionary 
        returned by a query to the user table in the database
        """
        self.username   = user_dict['username']
        self.role       = UserRole[user_dict['role']]

def authenticate(username) -> User:
    """
    Authenticate with the given credintials and returns an instance
    of User if successful, otherwise returns None

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
    """
    Authenticate with the credintials defined in a http cookie.
    cookies_header is the content of the "Cookie" header given
    in the request. Returns an instance of user if successful,
    otherwise returns None
    """
    cookie = cookies.SimpleCookie()
    cookie.load(cookies_header)
    username = cookie['username'].value
    return authenticate(username)

def create_cookie(user: User) -> str:
    """
    Create a cookie that will set the logged-in user to the given user.
    Cookie is set to expire in one day. The returned string is the
    content of the "Set-Cookie" header in the response.
    """
    return "username={}; Max-Age={}".format(user.username, SECONDS_PER_DAY)

def clear_cookie() -> str:
    """
    Create a cookie that will clear the logged in user (By setting to a blank
    value with an max-age of zero seconds). The returned string is the
    content of the "Set-Cookie" header in the response.
    """
    return "username=; Max-Age=0"