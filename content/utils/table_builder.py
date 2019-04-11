from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from .authentication import User
from . import request

TABLE_HEADERS = [
    "Dept. Priority",
    "Course",
    "Sec",
    "Mini Session?",
    "Online Class?",
    "Number of Students",
    "Instructor",
    "Banner ID",
    "Instructor Rank",
    "Course Cost",
    "Reason"
]

LEAVE_TYPE_SELECT = """
<select class="form-control" id="leaveType" name="leaveType">
    <option value="Sabbatical">Approved Amounts from Sabbatical Leaves</option>
    <option value="RBO">Research Buy Out (Provide Index Number)</option>
    <option value="LWOP">Leave Without Pay</option>
    <option value="Other">Other Funded Leave</option>
</select>
"""

def add_cell_to_row(table: Soup, row: Tag, content: str = "", editable = True):
    cell = table.new_tag('td')
    if editable:
        cell['contenteditable'] = "true"
        cell['class'] = "editable"
    cell.string = str(content)
    row.append(cell)

def add_checkbox_to_row(table: Soup, row: Tag):
    add_cell_to_row(table, row, editable=False)
    last_cell = row.find_all('td')[-1]

    checkbox = table.new_tag('input')
    checkbox['type'] = 'checkbox'
    checkbox['id'] = 'checkCFR'
    last_cell.append(checkbox)
    row.append(last_cell)

def add_leave_type_select_to_row(row: Tag):
    first_cell = row.find('td')
    del first_cell['class']
    del first_cell['contenteditable']
    leave_type = first_cell.string
    select = Soup(LEAVE_TYPE_SELECT, 'html.parser')
    option = select.find('option', value=leave_type)
    if option is not None:
        option['selected'] = 'selected'
    first_cell.string = ''
    first_cell.append(select)

def add_row_to_table(table: Soup, tup: tuple, editable = True):
    row = table.new_tag('tr')
    for val in tup:
        add_cell_to_row(table, row, val, editable = editable)
    if editable:
        add_checkbox_to_row(table, row)
    table.tbody.append(row)

def add_empty_row_to_table(table: Soup, num_cells: int):
    row = table.new_tag('tr')
    for _ in range(num_cells):
        add_cell_to_row(table, row)
    add_checkbox_to_row(table, row)
    table.tbody.append(row)
    return row

def build_table_body(list_of_tups: list) -> Soup:
    soup = Soup("<tbody></tbody>", 'html.parser')
    for tup in list_of_tups:
        add_row_to_table(soup, tup)
    return soup

def build_course_table_body(user: User):
    course_list = request.get_current_courses(user)
    body = build_table_body(course_list)
    if len(course_list) == 0:
        add_empty_row_to_table(body, len(request.REQ_FIELDS))
    return body

def build_savings_table_body(user: User):
    savings_list = request.get_current_savings(user)
    body = build_table_body(savings_list)
    if len(savings_list) == 0:
        add_empty_row_to_table(body, 3)
    for row in body.find_all('tr'):
        add_leave_type_select_to_row(row)
    return body


def build_course_table_full(cfr: tuple):
    soup = Soup("<table></table>", 'html.parser')
    soup.table['class'] = "table table-bordered table-striped"
    soup.table['style'] = "padding-bottom: 50px"
    
    head = soup.new_tag('thead')
    row = soup.new_tag('tr')
    head.append(row)
    for header in TABLE_HEADERS:
        cell = soup.new_tag('th')
        cell.string = header
        row.append(cell)
    soup.table.append(head)

    body = soup.new_tag('tbody')
    soup.table.append(body)

    courses = request.get_courses(cfr)
    for course in courses:
        add_row_to_table(soup, course, editable=False)

    return soup