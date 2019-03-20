"""
Functions related to submitting a request
"""
import json
from . import sql_connection as sql 


def create_cfr(dept_name, semester, cal_year, submitter):
    """
    Insert a new cfr into the cfr_department table
    """
    cursor = sql.new_cursor()
    create_cfr = ("INSERT INTO cfr_department "
                  "VALUES (%s, %s, %s, NOW(), NULL, 0, %s)")
    data_cfr = (dept_name, semester, cal_year, submitter)

    # execute insert statement to create new cfr
    cursor.execute(create_cfr, data_cfr)
    sql.get_connection().commit()
    rows_inserted = cursor.rowcount
    cursor.close()
    sql.disconnect()
    return rows_inserted


def add_course(data):
    """
    Add a course to a cfr
    -parameter should be a json string containing a list of dictionaries 
     containing the input information for the course request

    -at the moment it only reads in one dictionary in the list called 'request'
     but it will eventually read in more than one dictionary and add a course 
     for each.
    """

    #load the string to a json string and parse the dictionary called 'request'
    json_data = json.loads(data)
    request = json_data['request']

    cursor = sql.new_cursor()
    add_req = ("INSERT INTO request "
               "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
    data_req = (request['priority'], request['course'], request['sec'], request['mini_session'], 
                request['online_course'], request['num_students'], request['instructor'], request['banner_id'], 
                request['inst_rank'], request['cost'], request['reason'], request['dept_name'], 
                request['semester'], request['cal_year'], request['revision_num'])
    
    cursor.execute(add_req, data_req)

    sql.get_connection().commit()
    rows_inserted = cursor.rowcount
    cursor.close()
    sql.disconnect()
    return rows_inserted


def add_sal_savings(data):
    """
    Add salary savings to a cfr

    -Parameter is a json string containing a list of dictionaries containing 
     the input data for the salary savings record.

    -At the moment it only reads in one dictionary called 'savings'
    """

    #load the string into a json string and parse the dictionary called 'savings'
    json_data = json.loads(data)
    savings = json_data['savings']

    cursor = sql.new_cursor()
    add_sav = ("INSERT INTO sal_savings "
               "VALUES (%s, %s, %s, NULL, %s, %s, %s, %s, %s)")
    data_sav = (savings['leave_type'], savings['inst_name'], savings['savings'], savings['notes'],
                savings['dept_name'], savings['semester'], savings['cal_year'], savings['revision_num'])

    cursor.execute(add_sav, data_sav)
    
    sql.get_connection().commit()
    rows_inserted = cursor.rowcount
    cursor.close()
    sql.disconnect()
    return rows_inserted

    

