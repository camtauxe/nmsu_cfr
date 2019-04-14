"""
Functions related to manipulating requests, salary savings and cfrs in the database
"""
import json
import decimal
from enum import Enum, auto
from .sql_connection import Transaction
from .authentication import User
from . import db_utils
from .db_utils import REQ_FIELDS
from .db_utils import SAL_FIELDS
from .errors import Error400

SELECT_COURSE_IDS = """
    SELECT c.course_id
    FROM request r, cfr_request c
    WHERE r.id = c.course_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
"""

SELECT_SAVINGS_IDS = """
    SELECT c.savings_id
    FROM request r, cfr_savings c
    WHERE r.id = c.savings_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
"""

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
        if db_utils.get_current_cfr(cursor, user.dept_name) != None:
            revision = True
            prev_cfr = db_utils.get_current_cfr(cursor, user.dept_name)
            prev_cfr_data = (prev_cfr[0], prev_cfr[1], prev_cfr[2], prev_cfr[5])
        else:
            revision = False

        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.get_current_cfr(cursor, user.dept_name)

        cfr_data = (new_cfr[0], new_cfr[1], new_cfr[2], new_cfr[5])
        data_ls = []

        for course in course_list:
            course_data = ()
            for field in REQ_FIELDS:
                course_data = course_data + (course[field],)
            data_ls.append(course_data)

        new_courses = []
        for row in data_ls:
            validate_course(row)
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

        if revision:
            cursor.execute(SELECT_SAVINGS_IDS, prev_cfr_data)
            last_savings_ids = cursor.fetchall()
            for savings_id in last_savings_ids:
                cursor.execute(INSERT_CFR_SAVINGS, (savings_id + cfr_data))

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
        if db_utils.get_current_cfr(cursor, user.dept_name) != None:
            revision = True
            prev_cfr = db_utils.get_current_cfr(cursor, user.dept_name)
            prev_cfr_data = (prev_cfr[0], prev_cfr[1], prev_cfr[2], prev_cfr[5])
        else:
            revision = False

        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.get_current_cfr(cursor, user.dept_name)

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

        if revision:
            cursor.execute(SELECT_COURSE_IDS, prev_cfr_data)
            last_course_ids = cursor.fetchall()
            for course_id in last_course_ids:
                cursor.execute(INSERT_CFR_COURSE, (course_id + cfr_data))

    if num_new_sal_savings > 0:
        ret_string += f"{num_new_sal_savings} savings added or modified."

    else:
        ret_string += "No salaray savings added or modified."

    return ret_string

def validate_course(row):
    """
    Field validation for cfr submission requests

    row is a list of tuples containing all fields
    (defined in REQ_FIELDS) of a single course in
    the cfr request

    NOTE: There is no validation in place for
    instructor, inst_rank, or reason
    """

    priority = row[0]
    if not priority:
        priority = 0
    else:
        try:
            priority = int(row[0])
        except ValueError:
            raise Error400('The ' + REQ_FIELDS[0] + ' field must be an integer')
    if priority < 0:
        raise Error400('The ' + REQ_FIELDS[0] + ' field must be a positive integer')

    course = row[1]
    sec = row[2]
    if not course or not sec:
        raise Error400('The ' + REQ_FIELDS[1] + ' and ' + REQ_FIELDS[2] + ' fields are required')
    else:
        course = course.upper()
        sec = sec.upper()
    
    mini_session = row[3].lower()
    if mini_session not in ('yes', 'no'):
        raise Error400('The ' + REQ_FIELDS[3] + ' field must be a \"yes\" or \"no\"')

    online_course = row[4].lower()
    if online_course not in ('yes', 'no'):
        raise Error400('The ' + REQ_FIELDS[4] + ' field must be a \"yes\" or \"no\"')

    try:
        num_students = int(row[5])
    except ValueError:
        raise Error400('The ' + REQ_FIELDS[5] + ' field must be an integer')
    if num_students < 0:
        raise Error400('The ' + REQ_FIELDS[5] + ' field must be a positive integer')

    banner_id = row[7]
    if len(banner_id) != 9:
        raise Error400('The ' + REQ_FIELDS[7] + ' field must be a 9-digit number')
    else:
        try:
            banner_id = int(banner_id)
        except ValueError:
            raise Error400('The ' + REQ_FIELDS[7] + ' field must be an integer')

    cost = row[9].replace("$", "").replace(",", "")
    try:
        float(cost)
    except ValueError:
        raise Error400('The ' + REQ_FIELDS[9] + ' field must be a valid float')
