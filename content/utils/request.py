"""
Functions related to submitting a request
"""
import json
import decimal
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
    "FROM request r, cfr_request c "
    "WHERE r.id = c.course_id AND "
    "c.dept_name = %s AND "
    "c.semester = %s AND "
    "c.cal_year = %s AND "
    "c.revision_num = %s"
)

SELECT_REVISIONS = """
    SELECT c.dept_name, c.semester, c.cal_year, c.revision_num
    FROM request r, cfr_request c
    WHERE r.id = c.course_id AND
        c.dept_name = %s AND
        c.semester = %s AND
        c.cal_year = %s
    GROUP BY c.dept_name, c.semester, c.cal_year, c.revision_num
    ORDER BY c.revision_num DESC
"""

SAL_FIELDS = [
    'leave_type',
    'inst_name',
    'savings',
    'notes'
]

SELECT_SAVINGS = (
    "SELECT "+(", ".join(SAL_FIELDS))+" "
    "FROM sal_savings r, cfr_savings c "
    "WHERE r.id = c.savings_id AND "
    "c.dept_name = %s AND "
    "c.semester = %s AND "
    "c.cal_year = %s AND "
    "c.revision_num = %s"
)

INSERT_COURSE = """
INSERT INTO request(
                    priority, 
                    course, 
                    sec, 
                    mini_session, 
                    online_course, 
                    num_students,
                    instructor,
                    banner_id,
                    inst_rank,
                    cost,
                    reason
                    )
VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
"""

COMPARE_COURSE = """
SELECT COUNT(r.id), r.id
FROM request r, cfr_request c
WHERE r.id = c.course_id AND
    r.priority = %s AND
    r.course = %s AND
    r.sec = %s AND 
    r.mini_session = %s AND
    r.online_course = %s AND
    r.num_students = %s AND
    r.instructor = %s AND
    r.banner_id = %s AND
    r.inst_rank = %s AND
    r.cost = %s AND
    r.reason = %s AND 
    c.revision_num = %s
"""

       
GET_ID = """
SELECT LAST_INSERT_ID()
"""

INSERT_CFR_COURSE = """
INSERT INTO cfr_request
VALUES (%s, %s, %s, %s, %s)
"""

INSERT_SAL = """
INSERT INTO sal_savings(leave_type, inst_name, savings, notes)
VALUES (%s, %s, %s, %s)
"""

COMPARE_SAL = """
SELECT COUNT(s.id), s.id
FROM sal_savings s, cfr_savings c
WHERE s.id = c.savings_id AND
    s.leave_type = %s AND
    s.inst_name = %s AND
    s.savings = %s AND
    s.notes = %s AND
    c.revision_num = %s
"""

INSERT_CFR_SAVINGS = """
INSERT INTO cfr_savings
VALUES (%s, %s, %s, %s, %s)
"""

def new_cfr_from_courses(user: User, course_list):
    """
    Add a new cfr revision for the department represented
    by the given user using the given course data.

    course_list is a list of dicts with all the fields
    for a course (defined in REQ_FIELDS)
    """

    num_courses = 0
    num_new_courses = 0
    ret_string = ""
    with Transaction() as cursor:
        if db_utils.current_cfr(cursor, user) != None:
            revision = True
            prev_cfr = db_utils.current_cfr(cursor, user)
            prev_cfr_data = (prev_cfr[0], prev_cfr[1], prev_cfr[2], prev_cfr[5])
        else:
            revision = False

        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.current_cfr(cursor, user)

        cfr_data = (new_cfr[0], new_cfr[1], new_cfr[2], new_cfr[5])
        data_ls = []

        for course in course_list:
            course_data = ()
            for field in REQ_FIELDS:
                course_data = course_data + (course[field],)
            data_ls.append(course_data)

        
        new_courses = []
        for row in data_ls:
            exists = False
            if revision == True:
                cursor.execute(COMPARE_COURSE, row + (prev_cfr_data[3], ))
                dup_course = cursor.fetchone()
                if dup_course[0] > 0:
                    exists = True
                    course_id = (dup_course[1], )
                            

            if exists == False:
                cursor.execute(INSERT_COURSE, row)
                num_new_courses += cursor.rowcount
                new_courses.append(row)
                cursor.execute(GET_ID, params=None)
                course_id = cursor.fetchone()
            
            cfr_course = course_id + cfr_data
            cursor.execute(INSERT_CFR_COURSE, cfr_course)
            num_courses += cursor.rowcount
            #courses_inserted.append(cfr_course)

    if num_new_courses > 0:
        ret_string += f"{num_new_courses} courses added or modified:\n"
        for row in new_courses:
            ret_string += f"{row[1]}\t{row[2]}\n"
    else:
        ret_string += "No courses added or modified."

    return ret_string
    



def new_cfr_from_sal_savings(user: User, sal_list):
    """
    Add a new cfr revision for the department represented
    by the given user using the given salary savings data.

    sal_list is a list of dicts with all the fields
    for salary savings (defined in SAL_FIELDS)
    """

    num_new_sal_savings = 0
    ret_string = ""
    with Transaction() as cursor:
        if db_utils.current_cfr(cursor, user) != None:
            revision = True
            prev_cfr = db_utils.current_cfr(cursor, user)
            prev_cfr_data = (prev_cfr[0], prev_cfr[1], prev_cfr[2], prev_cfr[5])
        else:
            revision = False

        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.current_cfr(cursor, user)

        cfr_data = (new_cfr[0], new_cfr[1], new_cfr[2], new_cfr[5])
        data_ls = []

        for sal in sal_list:
            sal_data = ()
            for field in SAL_FIELDS:
                sal_data = sal_data + (sal[field],)
            data_ls.append(sal_data)

        new_sal_savings = []
        for row in data_ls:
            exists = False
            if revision == True:
                cursor.execute(COMPARE_SAL, row + (prev_cfr_data[3], ))
                dup_savings = cursor.fetchone()
                if dup_savings[0] > 0:
                    exists = True
                    savings_id = (dup_savings[1], )
            
            if exists == False:
                cursor.execute(INSERT_SAL, row)
                num_new_sal_savings += cursor.rowcount
                new_sal_savings.append(row)
                cursor.execute(GET_ID, params=None)
                savings_id = cursor.fetchone()

            cfr_savings = savings_id + cfr_data
            cursor.execute(INSERT_CFR_SAVINGS, cfr_savings)

    if num_new_sal_savings > 0:
        ret_string += f"{num_new_sal_savings} savings added or modified."

    else:
        ret_string += "No salaray savings added or modified."

    return ret_string

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

def get_courses(cfr: tuple):
    courses = []
    with Transaction() as cursor:
        cursor.execute(SELECT_COURSES, cfr)
        courses = cursor.fetchall()
    return courses

def get_current_savings(user: User):
    savings = []
    with Transaction() as cursor:
        cfr = db_utils.current_cfr(cursor, user)

        if cfr is not None:
            cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
            cursor.execute(SELECT_SAVINGS, cfr_data)
            savings = cursor.fetchall()

    return savings

def get_all_revisions(user: User):
    cfrs = []
    with Transaction() as cursor:
        # Semester and year are placeholder values
        # later to be replaced with a reference to
        # the current semester
        query = (user.dept_name, 'Spring', '2019')
        cursor.execute(SELECT_REVISIONS, query)
        cfrs = cursor.fetchall()
    return cfrs
