"""
Functions related to authenticating a user
"""
import hashlib
import http.cookies as cookies
from .sql_connection import Transaction
from enum import Enum, auto

# Number of seconds in a day. Used for specifying the Max-Age of cookies
SECONDS_PER_DAY = 86400

# Query used to select a user from the database.
# Returns username, type and usr_password
# Parameters are username and usr_password
SELECT_USER_QUERY = """
SELECT username, type, usr_password
FROM user 
WHERE 
    username = %s AND
    usr_password = %s
"""

# Query to get the department name out of the submitter table
# Parameters are: username
SELECT_DEPT_QUERY = """
SELECT dept_name
FROM submitter 
WHERE username = %s
"""

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
    def __init__(self, user_tup: tuple, password):
        """
        Initialize a User. user_tup is the tuple
        (OF RAW BYTES) returned by the MySQL cursor.
        """
        self.username       = user_tup[0].decode('utf-8')
        self.role           = UserRole[user_tup[1].decode('utf-8').upper()]
        self.password_hash  = user_tup[2]
        self.password       = password
        # By default, dept_name is None
        # But this may be set if the user is a submitter
        self.dept_name      = None

def authenticate(username, password) -> User:
    """
    Authenticate with the given credintials and returns an instance
    of User if successful, otherwise returns None

    Passwords are currently compared with hash values in the
    database. Passwords are hashed using SHA3 (512-bit output)
    which is FIPS PUB 202 certified.
    """

    hashed = hash_password(password)

    with Transaction(raw=True, buffered=True) as cursor:
        cursor.execute(SELECT_USER_QUERY, (username, hashed))
        result = cursor.fetchone()

        if result is not None:
            user = User(result, password)
            if user.role == UserRole.SUBMITTER:
                cursor.execute(SELECT_DEPT_QUERY, (user.username,))
                user.dept_name = cursor.fetchone()[0].decode('utf-8')
        else:
            user = None

    return user

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

def hash_password(plaintext: str) -> bytes:
    """
    Hash the given plaintext password and return
    the digest as bytes
    """
    hash = hashlib.sha3_512(plaintext.encode('utf-8'))
    return hash.digest()

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