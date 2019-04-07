from .sql_connection import Transaction

def get_dept(username):
    #query used to get department name of current user form database
    #returns a tuple containing the department name
    SELECT_DEPT_QUERY = """
    SELECT dept_name
    FROM submitter 
    WHERE username = %s
    """

    with Transaction(buffered=True) as cursor:
        cursor.execute(SELECT_DEPT_QUERY, (username,))
        dept_name = cursor.fetchone()
    
    return dept_name

def current_cfr(username):
    """
    Retrieve the information from the most current CFR for a department
    """
    SELECT_CFR_DEPT = """
    SELECT *
    FROM cfr_department
    WHERE dept_name = %s AND 
    revision_num = (SELECT MAX(revision_num)
                    FROM cfr_department c
                    WHERE c.dept_name = %s)
    """
    dept_name = get_dept(username)
    dept_name = dept_name + dept_name

    with Transaction() as cursor:
        cursor.execute(SELECT_CFR_DEPT, dept_name)
        result = cursor.fetchone()
    
    return result

def get_requests(cfr):
    """
    get a list of current course request for a cfr
    """
    SELECT_REQ = """
    SELECT *
    FROM request
    WHERE dept_name = %s AND semester = %s AND year = %s AND revision_num = %s
    """
    with Transaction() as cursor:
        cursor.execute(SELECT_REQ, cfr)
        result = cursor.fetchall()

    return result


    
