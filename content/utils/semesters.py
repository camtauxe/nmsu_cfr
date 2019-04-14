"""
Functions related to manipulating semesters in the database
"""
from .sql_connection import Transaction
from . import db_utils
from .errors import Error400

def change_semester(query):
    if 'semester' not in query:
        raise Error400("'semester' parameter missing!")

    semester_tup = tuple(query['semester'][0].split(' '))
    if len(semester_tup) != 2:
        raise Error400("'semester' must have two space-separted fields!")
    if semester_tup[0] not in ['Spring', 'Summer', 'Fall']:
        raise Error400("First field must be 'Spring', 'Summer' or 'Fall'")
    try:
        _ = int(semester_tup[1])
    except ValueError:
        raise Error400("Second field must be an integer!")

    with Transaction() as cursor:
        active_semester = db_utils.get_active_semester(cursor)

        if active_semester is not None:
            cursor.execute(
                "UPDATE semester SET active = 'no' WHERE semester = %s AND cal_year = %s",
                active_semester
            )

        cursor.execute(
            "UPDATE semester SET active = 'yes' WHERE semester = %s AND cal_year = %s",
            semester_tup
        )

def add_semester(query):
    if 'season' not in query or 'year' not in query:
        raise Error400("Missing parameters 'season' or 'year'!")

    season = query['season'][0]
    if season not in ['Spring', 'Summer', 'Fall']:
        raise Error400("'season' must be 'Spring', 'Summer' or 'Fall'")
    try:
        year = int(query['year'][0])
    except ValueError:
        raise Error400("Second field must be an integer!")

    with Transaction() as cursor:
        cursor.execute("INSERT INTO semester VALUES (%s, %s, 'no')", (season, year))