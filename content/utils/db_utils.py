from .authentication import User
from mysql.connector.cursor import CursorBase

# Query to the get latest CFR of a department
# Parameters are: dept_name and dept_name (yes, it is used twice)
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
revision_num = (SELECT MAX(revision_num)
                FROM cfr_department c
                WHERE c.dept_name = %s)
"""

# Query to insert a new cfr into the cfr_department table
# Parameters are: dept_name and submitter
NEW_CFR_DEPT = """
INSERT INTO cfr_department
VALUES (%s, 'Spring', YEAR(NOW()), NOW(), NULL, 0, %s)
"""

# Query to insert a new cfr into the cfr_department table
# Parameters are: dept_name, semester, revision_num and submitter
NEW_REVISION = """
INSERT INTO cfr_department
VALUES (%s, %s, YEAR(NOW()), %s, NOW(), %s, %s)
"""

def current_cfr(cursor: CursorBase, user: User):
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
    
    dept_name = user.dept_name
    cursor.execute(SELECT_CFR_DEPT, (dept_name, dept_name))
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
    cursor.execute(NEW_CFR_DEPT, (user.dept_name, user.username))

def create_new_revision(cursor: CursorBase, user: User):
    """
    Creates a new revision (a new cfr) for the department
    represented by the given user, using the given cursor.

    If no cfrs exist yet for the department, one will
    be created
    """

    current = current_cfr(cursor, user)
    if current is None:
        create_cfr(cursor, user)
    else:
        revision = current[5] + 1
        data = (current[0], current[1], current[3], revision, user.username)
        cursor.execute(NEW_REVISION, data)


    
