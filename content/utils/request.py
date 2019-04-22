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

# Query to select just the coure ids of all of the courses
# associated with a cr
# Returned columns are: course_id
# Parameters are: dept_name, semester, cal_year, revision_num
SELECT_COURSE_IDS = """
    SELECT c.course_id
    FROM request r, cfr_request c
    WHERE r.id = c.course_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
"""

# Query to select just the savings ids of all of the savings
# associated with a cr
# Returned columns are: savings_id
# Parameters are: dept_name, semester, cal_year, revision_num
SELECT_SAVINGS_IDS = """
    SELECT c.savings_id
    FROM request r, cfr_savings c
    WHERE r.id = c.savings_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
"""

# Query to insert a new course request into the request table
# Parameters are: priority, course, sec, mini_session, online_course,
#   num_students, instructor, banner_id, inst_rank, cost, reason
# TODO: Should this be auto-generated based on REQ_FIELDS?
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

# Query to count the number of courses matching the given
# definition of a course.
# Returned columns: COUNT(id)
# Parameters are: priority, course, sec, mini_session, online_course,
#   num_students, instructor, banner_id, inst_rank, cost, reason
# TODO: Should this be auto-generated based on REQ_FIELDS?
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

# Query to get the id of the last inserted item
# Returned coloumns: LAST_INSERT_ID()
GET_ID = """
SELECT LAST_INSERT_ID()
"""

# Query to insert a new entry into the cfr_request table
# Parameters are: course_id, dept_name, semester, cal_year, revision_num
INSERT_CFR_COURSE = """
INSERT INTO cfr_request
VALUES (%s, %s, %s, %s, %s)
"""

# Query to insert a new entry into the sal_savings table
# Parameters are: leave_type, inst_name, savings, notes
# TODO: Should this be auto-generated based on SAL_FIELDS?
INSERT_SAL = """
INSERT INTO sal_savings(leave_type, inst_name, savings, notes)
VALUES (%s, %s, %s, %s)
"""

# Query to count the number of sal_savings matching the given
# definition.
# Returned columns: COUNT(id)
# Parameters are: leave_type, inst_name, savings, notes
# TODO: Should this be auto-generated based on SAL_FIELDS?
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

# Query to insert a new entry into the cfr_savings table
# Parameters are: savings_id, dept_name, semester, cal_year, revision_num
INSERT_CFR_SAVINGS = """
INSERT INTO cfr_savings
VALUES (%s, %s, %s, %s, %s)
"""

# Update statement to update commitment_code and cost of a course
# when a course is approved 
APPROVE_COURSES = """
UPDATE request r
SET commitment_code = %s, cost = %s, approver = %s
WHERE EXISTS (SELECT *
              FROM cfr_request c
              WHERE r.id = c.course_id AND
                    r.course = %s AND
                    r.sec = %s AND
                    c.dept_name = %s AND
                    c.semester = %s AND
                    c.cal_year = %s AND
                    c.revision_num = %s)
                
"""

APPROVE_SAVINGS = """
UPDATE sal_savings s
SET confirmed_amt = %s, approver = %s
WHERE EXISTS (SELECT *
              FROM cfr_savings c
              WHERE s.id = c.savings_id AND
                    s.inst_name = %s AND
                    c.dept_name = %s AND
                    c.semester = %s AND
                    c.cal_year = %s AND
                    c.revision_num = %s)
"""

def new_cfr_from_courses(user: User, course_list):
    """
    Add a new cfr revision for the department represented
    by the given user using the given course data. The new
    revision will be in the currently active semester and
    based on the current latest revision (or created from
    scratch if there are no previous revisions).

    course_list is a list of dicts with all the fields
    for a course (defined in REQ_FIELDS)
    """

    num_courses = 0
    num_new_courses = 0
    ret_string = ""

    with Transaction() as cursor:
        # If there is a current cfr, mark that this new one is a revision
        # and remember the old one
        if db_utils.get_current_cfr(cursor, user.dept_name) != None:
            revision = True
            # prev_cfr is the full tuple of the previous cfr
            prev_cfr = db_utils.get_current_cfr(cursor, user.dept_name)
            # prev_cfr_data contains only the primary key
            prev_cfr_data = (prev_cfr[0], prev_cfr[1], prev_cfr[2], prev_cfr[5])
        else:
            revision = False

        # Create the new cfr
        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.get_current_cfr(cursor, user.dept_name)
        # cfr_data is just the primary key of the new cfr
        cfr_data = (new_cfr[0], new_cfr[1], new_cfr[2], new_cfr[5])

        # Parse the dicts in course_list into tuples
        data_ls = []
        for course in course_list:
            course_data = ()
            for field in REQ_FIELDS:
                course_data = course_data + (course[field],)
            data_ls.append(course_data)

        new_courses = []
        # Iterate through courses to add
        for row in data_ls:
            # Validation will raise an exception if there are
            # errors, so if execution continues, we can assume
            # we validated successfully
            validate_course(row)

            exists = False
            # If this is a revision, we first check that an equivalent
            # course does not already exist
            # (if one does, remember its id)
            if revision == True:
                cursor.execute(COMPARE_COURSE, row + (prev_cfr_data[3], ))
                dup_course = cursor.fetchone()
                if dup_course[0] > 0:
                    exists = True
                    course_id = (dup_course[1], )

            # If an equivalent course does not already exist,
            # insert this one into the database and remember its id
            if exists == False:
                cursor.execute(INSERT_COURSE, row)
                num_new_courses += cursor.rowcount
                new_courses.append(row)
                cursor.execute(GET_ID, params=None)
                course_id = cursor.fetchone()
        
            # Insert a new entry into cfr_request to link
            # this course with the new cfr
            cfr_course = course_id + cfr_data
            cursor.execute(INSERT_CFR_COURSE, cfr_course)
            num_courses += cursor.rowcount

        # End: for row in data_ls:

        # If this is a revision, get the savings associated with
        # the previous cfr and create entries in cfr_savings
        # to associate them with the new cfr as well
        if revision:
            cursor.execute(SELECT_SAVINGS_IDS, prev_cfr_data)
            last_savings_ids = cursor.fetchall()
            for savings_id in last_savings_ids:
                cursor.execute(INSERT_CFR_SAVINGS, (savings_id + cfr_data))

    # Create and return a string specifying the number of
    # courses that were added
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
    by the given user using the given salary savings data. The new
    revision will be in the currently active semester and
    based on the current latest revision (or created from
    scratch if there are no previous revisions).

    sal_list is a list of dicts with all the fields
    for salary savings (defined in SAL_FIELDS)

    TODO: There is a decent amount of code re-use between this and
    new_cfr_from_courses. Can it be refactored?
    """

    num_new_sal_savings = 0
    ret_string = ""

    with Transaction() as cursor:
        # If there is a current cfr, mark that this new one is a revision
        # and remember the old one
        if db_utils.get_current_cfr(cursor, user.dept_name) != None:
            revision = True
            # prev_cfr is the full tuple of the previous cfr
            prev_cfr = db_utils.get_current_cfr(cursor, user.dept_name)
            # prev_cfr_data contains only the primary key
            prev_cfr_data = (prev_cfr[0], prev_cfr[1], prev_cfr[2], prev_cfr[5])
        else:
            revision = False

        # Create the new cfr
        db_utils.create_new_revision(cursor, user)
        new_cfr = db_utils.get_current_cfr(cursor, user.dept_name)
        # cfr_data is just the primary key of the new cfr
        cfr_data = (new_cfr[0], new_cfr[1], new_cfr[2], new_cfr[5])

        # Parse the dicts in sal_list into tuples
        data_ls = []
        for sal in sal_list:
            sal_data = ()
            for field in SAL_FIELDS:
                sal_data = sal_data + (sal[field],)
            data_ls.append(sal_data)

        new_sal_savings = []
        # Iterate through savings to add
        for row in data_ls:
            # Validation will raise an exception if there are
            # errors, so if execution continues, we can assume
            # we validated successfully
            validate_sal_saving(row)

            exists = False
            # If this is a revision, we first check that an equivalent
            # entry does not already exist
            # (if one does, remember its id)
            if revision == True:
                cursor.execute(COMPARE_SAL, row + (prev_cfr_data[3], ))
                dup_savings = cursor.fetchone()
                if dup_savings[0] > 0:
                    exists = True
                    savings_id = (dup_savings[1], )

            # If an equivalent entry does not already exist,
            # insert this one into the database and remember its id
            if exists == False:
                cursor.execute(INSERT_SAL, row)
                num_new_sal_savings += cursor.rowcount
                new_sal_savings.append(row)
                cursor.execute(GET_ID, params=None)
                savings_id = cursor.fetchone()

            # Insert a new entry into cfr_savings to link
            # this entry with the new cfr
            cfr_savings = savings_id + cfr_data
            cursor.execute(INSERT_CFR_SAVINGS, cfr_savings)

        # If this is a revision, get the courses associated with
        # the previous cfr and create entries in cfr_request
        # to associate them with the new cfr as well
        if revision:
            cursor.execute(SELECT_COURSE_IDS, prev_cfr_data)
            last_course_ids = cursor.fetchall()
            for course_id in last_course_ids:
                cursor.execute(INSERT_CFR_COURSE, (course_id + cfr_data))

    # Create and return a string specifying the number of
    # entries that were added
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

def validate_sal_saving(row):
    """
    Field validation for Sources of Salary Savings

    row is a list of tuples containing all fields
    (defined in SAL_FIELDS) of a salary saving
    request

    NOTE: There is no validation in place for
    inst_name or notes
    """

    leave_type = row[0]
    if leave_type not in ('Sabbatical', 'RBO', 'LWOP', 'Other'):
        raise Error400('The ' + SAL_FIELDS[0] + ' field must be \"Sabbatical,\" \"RBO,\" \"LWOP,\" or \"Other\"')

    savings = row[2].replace("$", "").replace(",", "")
    try:
        float(savings)
    except ValueError:
        raise Error400('The ' + SAL_FIELDS[2] + ' field must be a valid float')

def approve_courses(current_user: User, approved_courses):
    """
    Approve courses within the current cfr for the selected
    department. Approved courses must have a commitment code 
    selected. Cost of courses can be edited by approver and
    is updated when course is approved.

    approved courses is an object contataining the department
    name and a list of courses that have been approved. 
    Approved courses are identified by course and sec.
    """
    ret_string = "Courses approved:\n"
    username = current_user.username
    dept_name = approved_courses['dept_name']
    with Transaction() as cursor:
        current_cfr = db_utils.get_current_cfr(cursor, dept_name)
        #current_cfr is the full tuple of the current cfr 
        #for the department selected
        cfr_key = (current_cfr[0], current_cfr[1], current_cfr[2], current_cfr[5])
        #cfr_key is the primary key for the cfr

        for course in approved_courses['courses']:
            #if course has a commitment code, it is approved
            if course['commitment_code'] != None:
                update_course = (course['commitment_code'], course['cost'], username, course["course"], course["sec"])
                #update_course is a tuple that contains the commitment code,
                #cost, course, section and approver's username
                cursor.execute(APPROVE_COURSES, update_course + cfr_key)
                ret_string += f"{course['course']} {course['sec']} \n"
            else: 
                print(f"{course['course']} {course['sec']} not approved, no commitment code found")
    
    return ret_string

def approve_sal_savings(current_user: User, approved_savings):
    """
    Approve salary savings in the current cfr for the
    selected department. Approved salaray savings must 
    have a confirmed amount. 

    approved savings is a object containing the 
    department name selected and a list of the salary 
    savings that have been approved. Salary savings
    are identified by the instructor name.
    """
    ret_string = "Salary savings approved:\n"
    username = current_user.username
    dept_name = approved_savings['dept_name']
    with Transaction() as cursor:
        current_cfr = db_utils.get_current_cfr(cursor, dept_name)
        #current_cfr is the full tuple of the current cfr
        cfr_key = (current_cfr[0], current_cfr[1], current_cfr[2], current_cfr[5])
        #cfr_key is the primary key for the cfr

        for savings in approved_savings['savings']:
            if savings['confirmed_amt'] != None:
            #if savings has a confirmed amount it is approved
                update_savings = (savings['confirmed_amt'], username, savings['inst_name'])
                #update_savings is a tuple that contains the values 
                #from the json: confirmed_amt, username, inst_name
                cursor.execute(APPROVE_SAVINGS, update_savings + cfr_key)
                ret_string += f"Savings for {savings['inst_name']} confirmed for {savings['confirmed_amt']}\n"
            else:
                print(f"Savings for {savings['inst_name']} has no confirmed amount")

    return ret_string

