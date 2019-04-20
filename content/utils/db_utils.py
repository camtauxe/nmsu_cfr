"""
Functions to perform various operations and queries on the database.

These functions are considerd "low-level" and are meant to be used
as parts of a larger, atomic transaction. So they take a mySQL cursor
as an argument which they use to execute queries.

These functions are written assuming the cursor that is passed in is
the default kind. They may behave unpredictably if different kinds of
cursors are passed in.
"""
from .authentication import User
from mysql.connector.cursor import CursorBase
from .sql_connection import Transaction

# Definition of all the fields in a course request.
# These should correspond to the field names in the database
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

# Query to select the courses associated with a cfr
# Returned columns match what is defined in REQ_FIELDS
# Parameters are: dept_name, semester, cal_year and revision_num
SELECT_COURSES = (
    "SELECT "+(", ".join(REQ_FIELDS))+" "
    "FROM request r, cfr_request c "
    "WHERE r.id = c.course_id AND "
    "c.dept_name = %s AND "
    "c.semester = %s AND "
    "c.cal_year = %s AND "
    "c.revision_num = %s "
    "ORDER BY r.id"
)

SELECT_TOTAL_COST = """
SELECT SUM(r.cost)
FROM request r, cfr_request c
WHERE r.id = c.course_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
"""

SELECT_COURSE_APPROVALS = """
SELECT r.approver, r.commitment_code
FROM request r, cfr_request c
WHERE r.id = c.course_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
ORDER BY r.id
"""

# Definition of all the fields in a salary savings entry.
# These should correspond to the field names in the database
SAL_FIELDS = [
    'leave_type',
    'inst_name',
    'savings',
    'notes'
]

# Query to select the salary savings associated with a cfr
# Returned columns match what is defined in SAL_FIELDS
# Parameters are: dept_name, semester, cal_year and revision_num
SELECT_SAVINGS = (
    "SELECT "+(", ".join(SAL_FIELDS))+" "
    "FROM sal_savings r, cfr_savings c "
    "WHERE r.id = c.savings_id AND "
    "c.dept_name = %s AND "
    "c.semester = %s AND "
    "c.cal_year = %s AND "
    "c.revision_num = %s "
    "ORDER BY r.id"
)

SELECT_TOTAL_SAVINGS = """
SELECT SUM(s.savings), SUM(s.confirmed_amt)
FROM sal_savings s, cfr_request c
WHERE s.id = c.course_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
"""

SELECT_SAVINGS_APPROVALS = """
SELECT s.approver, s.confirmed_amt
FROM sal_savings s, cfr_request c
WHERE s.id = c.course_id AND
    c.dept_name = %s AND
    c.semester = %s AND
    c.cal_year = %s AND
    c.revision_num = %s
ORDER BY s.id
"""

# Query to select the most recent cfr revision
# for a department in a semester
# Returned columns are: dept_name, semester, cal_year, date_initial,
#   date_revised, revision_num and cfr_submitter
# Parameters are: dept_name, semester, cal_year
SELECT_CFR_DEPT = """
SELECT dept_name,
    semester,
    cal_year,
    date_initial,
    date_revised,
    revision_num,
    cfr_submitter
FROM cfr_department
WHERE dept_name = %s AND 
semester = %s AND
cal_year = %s
ORDER BY revision_num DESC
LIMIT 1
"""

# Query to select all of the cfr revisions for
# a department in a semester
# Returned columns are: dept_name, semester, cal_year, date_initial,
#   date_revised, revision_num and cfr_submitter
# Parameters are: dept_name, semester, and cal_year
SELECT_REVISIONS = """
    SELECT dept_name,
        semester,
        cal_year,
        date_initial,
        date_revised,
        revision_num,
        cfr_submitter
    FROM cfr_department
    WHERE
        dept_name = %s AND
        semester = %s AND
        cal_year = %s
    GROUP BY dept_name, semester, cal_year, revision_num
    ORDER BY revision_num DESC
"""

# Query to insert a new entry into the cfr_department table.
# This is meant to be used for the first revision of a semester.
# If you're adding a new revision to a previous cfr, use the NEW_REVISION query.
# Parameters are: semester, cal_year, date_initial and cfr_submitter
NEW_CFR_DEPT = """
INSERT INTO cfr_department
VALUES (%s, %s, %s, NOW(), NULL, 0, %s)
"""

# Query to insert a new entry into the cfr_department table
# as a new revision to a previous cfr
# Parameters are: semester, cal_year, date_initial, revision_num and cfr_submitter
NEW_REVISION = """
INSERT INTO cfr_department
VALUES (%s, %s, %s, %s, NOW(), %s, %s)
"""

# Query to get the currently active semester
# Returned columns are: semester and cal_year
ACTIVE_SEMESTER_QUERY = """
SELECT semester, cal_year
FROM semester
WHERE active = 'yes'
LIMIT 1
"""

# Query to get all semesters
# Returned columns are: semester and cal_year
SEMESTERS_QUERY = """
SELECT semester, cal_year
FROM semester
"""

# Query to get usernames for all users
# Returned columns are: username
USERNAMES_QUERY = """
SELECT username FROM user
"""

# Get the username of the user with the given username
# (It looks stupid, but it's used to test if a user exists)
# Parameters are: username
SELECT_USER = """
SELECT username FROM user WHERE username = %s
"""

# Query to get the names of all departments
# Returned columns are: dept_name
DEPARTMENTS_QUERY = """
SELECT DISTINCT dept_name FROM submitter
"""

def quick_exec(function: callable, *args):
    """
    Execute another db_utils function as an atomic transaction
    and return its result. *args are passed to the other function.
    (not including the cursor)

    This is useful when you only need to perform one db_utils function
    and don't want to bother creating a Transaction/cursor yourself.
    """
    with Transaction() as cursor:
        return function(cursor, *args)

def get_usernames(cursor: CursorBase) -> list:
    """
    Get a list of the usernames of all users in the database, using
    the given cursor.
    """
    cursor.execute(USERNAMES_QUERY)
    return [d[0] for d in cursor.fetchall()]

def does_user_exist(cursor: CursorBase, username: str) -> bool:
    """
    Return whether or not a user with the given username exists
    in the database, using the given cursor
    """
    cursor.execute(SELECT_USER, (username,))
    cursor.fetchall()
    return cursor.rowcount > 0

def get_departments(cursor: CursorBase) -> list:
    """
    Get a list of the names of all departments in the database, using
    the given cursor.
    """
    cursor.execute(DEPARTMENTS_QUERY)
    return [d[0] for d in cursor.fetchall()]

def get_semesters(cursor: CursorBase) -> list:
    """
    Get a list of all the semesters in the database, using the
    given cursor.

    The returned list is a list of tuples representing the 
    season and cal_year of a semester (in that order).
    """
    cursor.execute(SEMESTERS_QUERY)
    return cursor.fetchall()

def get_active_semester(cursor: CursorBase) -> tuple:
    """
    Get the currently active semester, using the given cursor.

    The returned value is a tuple representing the season
    and cal_year of the semester (in that order)
    """
    cursor.execute(ACTIVE_SEMESTER_QUERY)
    return cursor.fetchone()

def get_current_cfr(cursor: CursorBase, dept_name: str) -> tuple:
    """
    Get the latest cfr for the given department in the currently
    active semester, using the given cursor.
    
    The returned value is a tuple with the following fields (in this order):
    dept_name, semester, cal_year, date_initial, date_revised,
    revision_num, cfr_submitter

    This will return None if there are no CFRs for the department
    """
    semester = get_active_semester(cursor)
    query = (dept_name, semester[0], semester[1])
    cursor.execute(SELECT_CFR_DEPT, query)
    result = cursor.fetchone()
    
    return result

def create_cfr(cursor: CursorBase, user: User):
    """
    Insert a new cfr into cfr_department table
    for the department represented by the given user in the
    currently active semester, using the given cursor.
    """
    semester = get_active_semester(cursor)
    query = (user.dept_name, semester[0], semester[1], user.username)
    cursor.execute(NEW_CFR_DEPT, query)

def create_new_revision(cursor: CursorBase, user: User):
    """
    Creates a new revision (a new cfr) for the department
    represented by the given user in the currently
    active semester, using the given cursor.

    If no cfrs exist yet for the department, one will
    be created.
    """

    current = get_current_cfr(cursor, user.dept_name)
    if current is None:
        create_cfr(cursor, user)
    else:
        revision = current[5] + 1
        data = (current[0], current[1], current[2], current[3], revision, user.username)
        cursor.execute(NEW_REVISION, data)

def get_all_revisions_for_semester(cursor: CursorBase, dept_name: str, semester: tuple) -> list:
    """
    Get all the cfr revisions for the given department in the given semester,
    using the given cursor.

    semester should be a tuple containing the season and
    cal_year of the semester (in that order).

    The returned value is a list of tuples with the following fields (in this order):
    dept_name, semester, cal_year, date_initial, date_revised,
    revision_num, cfr_submitter
    """
    query = (dept_name, semester[0], semester[1])
    cursor.execute(SELECT_REVISIONS, query)
    return cursor.fetchall()

def get_all_revisions_for_active_semester(cursor: CursorBase, dept_name: str) -> list:
    """
    Get all of the cfr revisions for the given department in the currently
    active semester.

    The returned value is a list of tuples with the following fields (in this order):
    dept_name, semester, cal_year, date_initial, date_revised,
    revision_num, cfr_submitter
    """
    semester = get_active_semester(cursor)
    return get_all_revisions_for_semester(cursor, dept_name, semester)

def get_courses(cursor: CursorBase, cfr: tuple) -> list:
    """
    Get a list of courses associated with the given cfr, using the given
    cursor.

    The returned value is a list of tuples with fields corresponding
    to REQ_FIELDS

    cfr should be a tuple with the following fields (in this order):
    dept_name, semester, cal_year, [date_initial], [date_revised],
    revision_num, [cfr_submitter]
    (fields in brackets are not used, but this order is still expected)
    """
    cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
    cursor.execute(SELECT_COURSES, cfr_data)
    return cursor.fetchall()

def get_course_approvals(cursor: CursorBase, cfr: tuple) -> list:
    cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
    cursor.execute(SELECT_COURSE_APPROVALS, cfr_data)
    return cursor.fetchall()

def get_current_courses(cursor: CursorBase, dept_name: str) -> list:
    """
    Get a list of courses associated with the current cfr (latest revision
    in active semester) for the given department, using the given cursor.

    The returned value is a list of tuples with fields corresponding
    to REQ_FIELDS

    If there are no cfrs for this department in the active semester, the
    returned list will be empty.
    """
    cfr = get_current_cfr(cursor, dept_name)
    if cfr is not None:
        return get_courses(cursor, cfr)
    else:
        return []

def get_savings(cursor: CursorBase, cfr: tuple) -> list:
    """
    Get a list of the salary savings entries associated with the given cfr,
    using the given cursor.

    The returned value is a list of tuples with fields corresponding
    to SAL_FIELDS

    cfr should be a tuple with the following fields (in this order):
    dept_name, semester, cal_year, [date_initial], [date_revised],
    revision_num, [cfr_submitter]
    (fields in brackets are not used, but this order is still expected)
    """
    cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
    cursor.execute(SELECT_SAVINGS, cfr_data)
    return cursor.fetchall()

def get_savings_approvals(cursor: CursorBase, cfr: tuple) -> list:
    cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
    cursor.execute(SELECT_SAVINGS_APPROVALS, cfr_data)
    return cursor.fetchall()

def get_current_savings(cursor: CursorBase, dept_name: str) -> list:
    """
    Get a list of the salary savings entries associated with the current cfr (latest revision
    in active semester) for the given department, using the given cursor.

    The returned value is a list of tuples with fields corresponding
    to SAL_FIELDS

    If there are no cfrs for this department in the active semester, the
    returned list will be empty.
    """
    cfr = get_current_cfr(cursor, dept_name)
    if cfr is not None:
        return get_savings(cursor, cfr)
    else:
        return []

def get_approver_data(cursor: CursorBase) -> dict:
    data = {
        'summary': [],
        'dept_names': [],
        'course_lists': [],
        'course_approvals_lists': [],
        'savings_lists': [],
        'savings_approvals_lists': []
    }

    depts = get_departments(cursor)
    for dept in depts:
        cfr = get_current_cfr(cursor, dept)
        if cfr is None:
            continue

        courses = get_courses(cursor, cfr)
        if len(courses) == 0:
            continue
        course_approvals = get_course_approvals(cursor, cfr)

        savings = get_savings(cursor, cfr)
        savings_approvals = get_savings_approvals(cursor, cfr)

        all_approved = True
        total_cost = 0
        for i in range(len(courses)):
            total_cost += courses[i][9]
            all_approved = all_approved and (course_approvals[i][0] is not None)

        total_savings = 0
        total_committed = 0
        for i in range(len(savings)):
            total_savings += savings[i][2]
            if savings_approvals[i][0] is not None:
                total_committed += savings_approvals[i][1]
            else:
                all_approved = False

        funds_needed = total_cost - total_savings - total_committed
        if funds_needed < 0:
            funds_needed = 0
        
        data['dept_names'].append(dept)
        data['summary'].append((dept, total_cost, total_savings, total_committed, funds_needed, all_approved))
        data['course_lists'].append(courses)
        data['course_approvals_lists'].append(course_approvals)
        data['savings_lists'].append(savings)
        data['savings_approvals_lists'].append(savings_approvals)

    return data