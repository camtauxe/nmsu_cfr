"""
Create json files with the needed fields for to add a course or salary savings
to a cfr. Used to test the add_course and add_sal_savings functions.

-currently, it will only add the information for one course in a file called
 req_data.json and one the information for one salary savings in a file called
 sal_data.json. Eventually it will create jsons with the information for several
 courses and salary savings to test the functionality of more than one entry being
 made at a time.
"""
import json

def course_req_json(fields):
    data = {
        "request" : {
            "priority" : fields[0],
            "course" : fields[1],
            "sec" : fields[2],
            "mini_session" : fields[3],
            "online_course" : fields[4],
            "num_students" : fields[5],
            "instructor" : fields[6],
            "banner_id" : fields[7],
            "inst_rank" : fields[8],
            "cost" : fields[9],
            "reason" : fields[10],
            "dept_name" : fields[11],
            "semester" : fields[12],
            "cal_year" : fields[13],
            "revision_num" : fields[14]
        }
    }
    
    with open("req_data.json", "w") as write_file:
        json.dump(data,write_file)

def sav_req_json(fields):
    data = {
        "savings" : {
            "leave_type" : fields[0],
            "inst_name" : fields[1],
            "savings" : fields[2],
            "notes" : fields[3],
            "dept_name" : fields[4],
            "semester" : fields[5],
            "cal_year" : fields[6],
            "revision_num" : fields[7]
        }
    }
    
    with open("sav_data.json", "w") as write_file:
        json.dump(data,write_file)
    

req_data = ["1","CS253","M01","No","No","25","Cooper","800152344","NULL","1234.33", "NULL","Computer Science","Spring","2019","0"]
sav_data = ["sabbatical", "Zhang", "40124.23", "NULL", "Sociology", "Spring", "2019", "0"]
sav_req_json(sav_data)
course_req_json(req_data)


