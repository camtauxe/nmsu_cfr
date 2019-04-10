"""
Create json files with the needed fields for to add a course or salary savings
to a cfr. Used to test the add_course and add_sal_savings functions.
 
-now creates json files formatted as a list of dictionaries. Each dictionary
 corresponds the data to be inserted into a row in the database. There are some 
 usage examples at the bottom of the file
"""
import json
from enum import Enum, auto


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


def course_req_json(val):
    
    data = dict_list(val, req_fields)

    with open("mul_req_data.json", "w") as write_file:
        json.dump(data,write_file)

def sal_sav_json(val):

    data = dict_list(val, sav_fields)

    with open("mul_sav_data.json", "w") as write_file:
        json.dump(data, write_file)

def dict_list(val, dict_type):
    data = []
    for i in range(len(val)):
        dict_data = {}
        for j in range(len(val[0])):
            dict_data[dict_type(j + 1).name] = val[i][j]
        data.append(dict_data)
    
    return data


req_data = [["1","ART253","M03","No","No","25","Cooper","80015234","NULL","1234.33", "NULL"],
            ["2", "ART105", "D11", "No", "No", "22", "Miller", "80011223", "NULL", "2000.12", "NULL"]]

#accepts a list of lists with data corresponding to a course request insertion
course_req_json(req_data)

"""

sav_data = [["Sabbatical", "Leung", "30123.11", "NULL"],
            ["Other", "Wilson", "100000.22", "NULL"],
            ["Sabbatical", "Marquez", "30223.11", "NULL"]]

#single_sav = [["Other", "Miller", "10023", "NULL", "Computer Science", "Spring", "2019", "0"]]

#accepts a list of lists with data corresponding to a salary savings insertion
sal_sav_json(sav_data)
"""
