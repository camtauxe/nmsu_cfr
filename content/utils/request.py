"""
Functions related to submitting a request
"""
import json
from enum import Enum, auto
from .sql_connection import Transaction
from .authentication import User
from . import db_utils

REQ_FIELDS = [
    'priority',
    'course',
    'sec',
    'mini_session',
    'online_course',
    'num_students',
    'instructor',
    'banner_id',
    'inst_rank',
    'cost',
    'reason'
]

SELECT_COURSES = (
    "SELECT "+(", ".join(REQ_FIELDS))+" "
    "FROM request "
    "WHERE "
    "dept_name = %s AND "
    "semester = %s AND "
    "cal_year = %s AND "
    "revision_num = %s"
)

SAL_FIELDS = [
    'leave_type',
    'inst_name',
    'savings',
    'notes'
]

INSERT_COURSE = """
INSERT INTO request
VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)
"""

INSERT_SAL = """
INSERT INTO sal_savings
VALUES (%s, %s, %s, NULL, %s, %s, %s, %s, %s, NULL)
"""

def new_cfr_from_courses(user: User, course_list):
    """
    Add a new cfr revision for the department represented
    by the given user using the given course data.

    course_list is a list of dicts with all the fields
    for a course (defined in REQ_FIELDS)
    """

    rows_inserted = 0
    with Transaction() as cursor:
        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.current_cfr(cursor, user)

        cfr_data = (new_cfr[0], new_cfr[1], new_cfr[2], new_cfr[5])
        data_ls = []

        for course in course_list:
            course_data = ()
            for field in REQ_FIELDS:
                course_data = course_data + (course[field],)
            data_ls.append(course_data + cfr_data)

        
        for row in data_ls:
            cursor.execute(INSERT_COURSE, row)
            rows_inserted += cursor.rowcount

    return rows_inserted

def new_cfr_from_sal_savings(user: User, sal_list):
    """
    Add a new cfr revision for the department represented
    by the given user using the given salary savings data.

    sal_list is a list of dicts with all the fields
    for salary savings (defined in SAL_FIELDS)
    """

    rows_inserted = 0
    with Transaction() as cursor:
        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.current_cfr(cursor, user)

        cfr_data = (new_cfr[0], new_cfr[1], new_cfr[2], new_cfr[5])
        data_ls = []

        for sal in sal_list:
            sal_data = ()
            for field in SAL_FIELDS:
                sal_data = sal_data + (sal[field],)
            data_ls.append(sal_data + cfr_data)

        
        for row in data_ls:
            cursor.execute(INSERT_SAL, row)
            rows_inserted += cursor.rowcount

    return rows_inserted

def get_current_courses(user: User):
    """
    Get a list of the courses in the latest cfr for the
    department represented by the given user as a list
    of tuples
    """
    courses = []
    with Transaction() as cursor:
        cfr = db_utils.current_cfr(cursor, user)

        if cfr is not None:
            cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
            cursor.execute(SELECT_COURSES, cfr_data)
            courses = cursor.fetchall()

    return courses


