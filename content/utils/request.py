"""
Functions related to submitting a request
"""
import json
from enum import Enum, auto
from .sql_connection import Transaction
from . import db_utils

class req_fields(Enum):
    """
    Enum representation of course request fields
    """
    priority = auto()
    course = auto()
    sec = auto()
    mini_session = auto()
    online_course = auto()
    num_students = auto()
    instructor = auto()
    banner_id = auto()
    inst_rank = auto()
    cost = auto()
    reason = auto()

class sav_fields(Enum):
    """
    Enum representation of salary savings fields
    """
    leave_type = auto()
    inst_name = auto()
    savings = auto()
    notes = auto()



#create a new cfr
#gets the username of user that is currently signed in from wsgi_main
#gets the semester from the POST request body
def create_cfr(username, semester):
    """
    Insert a new cfr into the cfr_department table
    """
    if all(k in semester for k in ['semester']):
        semester = semester['semester'][0]
    submitter = username
    dept_name = db_utils.get_dept(username)

    create_cfr = ("INSERT INTO cfr_department "
                  "VALUES (%s, %s, YEAR(NOW()), NOW(), NULL, 0, %s)")
    data_cfr = dept_name + (semester, submitter)

    # execute insert statement to create new cfr
    with Transaction() as cursor:
        cursor.execute(create_cfr, data_cfr)
        rows_inserted = cursor.rowcount
    return rows_inserted


def add_course(username, data):
    """
    Add a course to a cfr
    -parameter should be a json string containing a list of dictionaries 
     containing the input information for the course requests

    -can now insert multiple records at a time
    """
    #get the data from the current cfr
    current_cfr = db_utils.current_cfr(username)
    cfr_data = (current_cfr[0], current_cfr[1], current_cfr[2], current_cfr[5])

    #load the string to a json string containing data in a list of dictionaries 
    json_data = json.loads(data)
    data_ls = []

    #loop through each dictionary and parse the values and insert them into tuples
    for i in range(len(json_data)):
        data_req = ()
        request = json_data[i]
        for j in range(len(request)):
            data_req = data_req + (request[req_fields(j+1).name], )

        data_req = data_req + cfr_data

        #apend each tuple to a list of tuples
        data_ls.append(data_req) 


    add_req = ("INSERT INTO request "
               "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, NULL)")
      

    with Transaction() as cursor:
        rows_inserted = 0
        for row in data_ls:
            cursor.execute(add_req, row)
            rows_inserted += cursor.rowcount
    return rows_inserted


def add_sal_savings(username, data):
    """
    Add salary savings to a cfr

    -Parameter is a json string containing a list of dictionaries containing 
     the input data for the salary savings record.

    -can now insert multiple records at a time
    """
    current_cfr = db_utils.current_cfr(username)
    cfr_data = (current_cfr[0], current_cfr[1], current_cfr[2], current_cfr[5])


    #load the string into a json string and parse the dictionary called 'savings'
    json_data = json.loads(data)
    data_ls = []

    #loop through list of dictionaries, extract values and put them into tuples
    for i in range(len(json_data)):
        data_sav = ()
        savings = json_data[i]
        for j in range(len(savings)):
            data_sav = data_sav + (savings[sav_fields(j+1).name], )

        data_sav = data_sav + cfr_data

        #create a list of tuples
        data_ls.append(data_sav)
    

    add_sav = ("INSERT INTO sal_savings "
               "VALUES (%s, %s, %s, NULL, %s, %s, %s, %s, %s, NULL)")
   
    with Transaction() as cursor:
        rows_inserted = 0
        for row in data_ls:
            cursor.execute(add_sav, row)
            rows_inserted += cursor.rowcount
    return rows_inserted

    

