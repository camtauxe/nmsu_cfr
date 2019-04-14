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
cal_year = %s AND
revision_num = (SELECT MAX(revision_num)
                FROM cfr_department c
                WHERE c.dept_name = %s)
"""

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

NEW_CFR_DEPT = """
INSERT INTO cfr_department
VALUES (%s, %s, %s, NOW(), NULL, 0, %s)
"""

NEW_REVISION = """
INSERT INTO cfr_department
VALUES (%s, %s, %s, %s, NOW(), %s, %s)
"""

ACTIVE_SEMESTER_QUERY = """
SELECT semester, cal_year
FROM semester
WHERE active = 'yes'
LIMIT 1
"""

SEMESTERS_QUERY = """
SELECT semester, cal_year
FROM semester
"""

USERNAMES_QUERY = """
SELECT username FROM user
"""

DEPARTMENTS_QUERY = """
SELECT DISTINCT dept_name FROM submitter
"""

def quick_exec(function: callable, *args):
    with Transaction() as cursor:
        return function(cursor, *args)

def get_usernames(cursor: CursorBase):
    cursor.execute(USERNAMES_QUERY)
    return [d[0] for d in cursor.fetchall()]

def get_departments(cursor: CursorBase):
    cursor.execute(DEPARTMENTS_QUERY)
    return [d[0] for d in cursor.fetchall()]

def get_semesters(cursor: CursorBase):
    cursor.execute(SEMESTERS_QUERY)
    return cursor.fetchall()

def get_active_semester(cursor: CursorBase):
    cursor.execute(ACTIVE_SEMESTER_QUERY)
    return cursor.fetchone()

def get_current_cfr(cursor: CursorBase, dept_name: str):
    """
    Get the latest cfr for the deparment that the given
    user represents, using the given cursor.
    
    The information returned depends on the kind of cursor
    passed in but dy default it is a tuple with the following
    fields (in this order):
    dept_name, semester, cal_year, data_initial, date_revised,
    revision_num, cfr_submitter

    This will return None if there are no CFRs for the department
    """
    semester = get_active_semester(cursor)
    query = (dept_name, semester[0], semester[1], dept_name)
    cursor.execute(SELECT_CFR_DEPT, query)
    result = cursor.fetchone()
    
    return result

def create_cfr(cursor: CursorBase, user: User):
    """
    Insert a new cfr into cfr_department table
    for the department represented by the given user,
    using the given cursor.

    Right now, all new cfrs are created with "Spring"
    as the semester.

    Returns true on success, otherwise returns false
    """
    semester = get_active_semester(cursor)
    query = (user.dept_name, semester[0], semester[1], user.username)
    cursor.execute(NEW_CFR_DEPT, query)

def create_new_revision(cursor: CursorBase, user: User):
    """
    Creates a new revision (a new cfr) for the department
    represented by the given user, using the given cursor.

    If no cfrs exist yet for the department, one will
    be created
    """

    current = get_current_cfr(cursor, user.dept_name)
    if current is None:
        create_cfr(cursor, user)
    else:
        revision = current[5] + 1
        data = (current[0], current[1], current[2], current[3], revision, user.username)
        cursor.execute(NEW_REVISION, data)

def get_all_revisions_for_semester(cursor: CursorBase, dept_name: str, semester: tuple):
    query = (dept_name, semester[0], semester[1])
    cursor.execute(SELECT_REVISIONS, query)
    return cursor.fetchall()

def get_all_revisions_for_active_semester(cursor: CursorBase, dept_name: str):
    semester = get_active_semester(cursor)
    return get_all_revisions_for_semester(cursor, dept_name, semester)

def get_courses(cursor: CursorBase, cfr: tuple):
    cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
    cursor.execute(SELECT_COURSES, cfr_data)
    return cursor.fetchall()

def get_current_courses(cursor: CursorBase, dept_name: str):
    cfr = get_current_cfr(cursor, dept_name)
    if cfr is not None:
        return get_courses(cursor, cfr)
    else:
        return []

def get_savings(cursor: CursorBase, cfr: tuple):
    cfr_data = (cfr[0], cfr[1], cfr[2], cfr[5])
    cursor.execute(SELECT_SAVINGS, cfr_data)
    return cursor.fetchall()

def get_current_savings(cursor: CursorBase, dept_name: str):
    cfr = get_current_cfr(cursor, dept_name)
    if cfr is not None:
        return get_savings(cursor, cfr)
    else:
        return []

