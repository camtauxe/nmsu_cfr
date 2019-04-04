"""
Functions related to submitting a request
"""
import json
from enum import Enum, auto
from .sql_connection import Transaction as Transaction

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
    dept_name = auto()
    semester = auto()
    cal_year = auto()
    revision_num = auto()

class sav_fields(Enum):
    """
    Enum representation of salary savings fields
    """
    leave_type = auto()
    inst_name = auto()
    savings = auto()
    notes = auto()
    dept_name = auto()
    semester = auto()
    cal_year = auto()
    revision_num = auto()

def create_cfr(dept_name, semester, cal_year, submitter):
    """
    Insert a new cfr into the cfr_department table
    """
    create_cfr = ("INSERT INTO cfr_department "
                  "VALUES (%s, %s, %s, NOW(), NULL, 0, %s)")
    data_cfr = (dept_name, semester, cal_year, submitter)

    # execute insert statement to create new cfr
    with Transaction() as cursor:
        cursor.execute(create_cfr, data_cfr)
        cursor.commit()
        rows_inserted = cursor.rowcount
    return rows_inserted


def add_course(data):
    """
    Add a course to a cfr
    -parameter should be a json string containing a list of dictionaries 
     containing the input information for the course requests

    -can now insert multiple records at a time
    """

    #load the string to a json string containing data in a list of dictionaries 
    json_data = json.loads(data)
    data_ls = []

    #loop through each dictionary and extract the values and insert them into tuples
    for i in range(len(json_data)):
        data_req = ()
        request = json_data[i]
        for j in range(len(request)):
            data_req = data_req + (request[req_fields(j+1).name], )

        #apend each tuple to a list of tuples
        data_ls.append(data_req) 


    add_req = ("INSERT INTO request "
               "VALUES (NULL, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s)")
      

    with Transaction() as cursor:
        cursor.executemany(add_req, data_req)
        cursor.commit()
        rows_inserted = cursor.rowcount
    return rows_inserted


def add_sal_savings(data):
    """
    Add salary savings to a cfr

    -Parameter is a json string containing a list of dictionaries containing 
     the input data for the salary savings record.

    -can now insert multiple records at a time
    """

    #load the string into a json string and parse the dictionary called 'savings'
    json_data = json.loads(data)
    data_ls = []

    #loop through list of dictionaries, extract values and put them into tuples
    for i in range(len(json_data)):
        data_sav = ()
        savings = json_data[i]
        for j in range(len(savings)):
            data_sav = data_sav + (savings[sav_fields(j+1).name], )

        #create a list of tuples
        data_ls.append(data_sav)
    

    add_sav = ("INSERT INTO sal_savings "
               "VALUES (%s, %s, %s, NULL, %s, %s, %s, %s, %s)")
   
    with Transaction() as cursor:
        cursor.executemany(add_sav, data_ls)
        cursor.commit()
        rows_inserted = cursor.rowcount
    return rows_inserted

    

