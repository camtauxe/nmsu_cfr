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
        self.role       = UserRole[user_dict['type'].upper()]
        self.password   = user_dict['usr_password']

def authenticate(username, password) -> User:
    """
    Authenticate with the given credintials and returns an instance
    of User if successful, otherwise returns None

    Right now, this uses plaintext passwords in the database, and
    will be expanded to be more secure later.
    """

    cursor = sql.new_cursor(dictionary=True)
    cursor.execute(
        'SELECT username, type, usr_password FROM user WHERE username = %s AND usr_password = %s',
        (username, password)
    )

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
    password = cookie['password'].value
    return authenticate(username, password)

def create_cookies(user: User) -> str:
    """
    Returns a list of cookies used to store the user's login credintials.
    The cookies are set to expire in one day.

    The returned cookies are in the form of a list where each element
    is the content of a 'Set-Cookie' header in the response.
    """
    return [
        "username={}; Max-Age={}".format(user.username, SECONDS_PER_DAY),
        "password={}; Max-Age={}".format(user.password, SECONDS_PER_DAY)
    ]

def clear_cookies() -> str:
    """
    Creates a set of cookies to clear the user's creditinals. This is done
    by creating cookies with an empty value and a maximum age of 0.

    The returned cookies are in the form of a list where each element
    is the content of a 'Set-Cookie' header in the response.
    """
    return [
        "username=; Max-Age=0",
        "password=; Max-Age=0"
    ]