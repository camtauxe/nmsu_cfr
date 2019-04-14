"""
Functions related to manipulating semesters in the database
"""
from .sql_connection import Transaction
from . import db_utils
from .errors import Error400

# Query to deactivate the currently active semester
DEACTIVATE_ACTIVE_SEMESTER = """
UPDATE semester SET active = 'no'
WHERE active = 'yes'
"""

# Query to activate the given semester
# Parameters are: semester, cal_year
ACTIVATE_SEMESTER = """
UPDATE semester SET active = 'yes'
WHERE semester = %s AND cal_year = %s
"""

# Query to insert a new semester into the database
# Parameters are: semester, cal_year
# (The new semester will not be active)
INSERT_SEMESTER = """
INSERT INTO semester VALUES (%s, %s, 'no')
"""

def change_semester(query):
    """
    Change the currently active semester

    query is a dict parsed from the form data in a POST request.
    It should contain the single field 'semester' which contains
    two, space-separated fields: 
    The first one should specify the season and be either 
    'Spring', 'Summer' or 'Fall'.
    The second one should be an integer specifying the year

    Any problems with the data will result in a Error400 being thrown.
    """
    if 'semester' not in query:
        raise Error400("'semester' parameter missing!")

    # Parse the 'semester' value into a tuple
    semester_tup = tuple(query['semester'][0].split())
    if len(semester_tup) != 2:
        raise Error400("'semester' must have two space-separated fields!")
    if semester_tup[0] not in ['Spring', 'Summer', 'Fall']:
        raise Error400("First field must be 'Spring', 'Summer' or 'Fall'")
    try:
        _ = int(semester_tup[1])
    except ValueError:
        raise Error400("Second field must be an integer!")

    # Change active semester in the database
    with Transaction() as cursor:
        cursor.execute(DEACTIVATE_ACTIVE_SEMESTER)
        cursor.execute(ACTIVATE_SEMESTER, semester_tup)

def add_semester(query):
    """
    Add a new semester to the database

    query is a dict parsed from the form data in a POST request.
    It should contain the following fields:
        'season': A string; either 'Spring', 'Summer' or 'Fall'
        'year': An integer

    Any problems with the data will result in a Error400 being thrown.
    """
    if 'season' not in query or 'year' not in query:
        raise Error400("Missing parameters 'season' or 'year'!")

    # Validate
    season = query['season'][0]
    if season not in ['Spring', 'Summer', 'Fall']:
        raise Error400("'season' must be 'Spring', 'Summer' or 'Fall'")
    try:
        year = int(query['year'][0])
    except ValueError:
        raise Error400("Second field must be an integer!")

    # Insert semester into database
    with Transaction() as cursor:
        cursor.execute(INSERT_SEMESTER, (season, year))