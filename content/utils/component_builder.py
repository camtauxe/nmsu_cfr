from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from .authentication import User
from . import request
from . import page_builder

COURSE_TABLE_HEADERS = [
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

LEAVE_TYPE_VALUES = ['Sabbatical', 'RBO', 'LWOP', 'Other']
LEAVE_TYPE_NAMES = [
    "Approved Amounts from Sabbatical Leaves",
    "Research Buy-Out (Provide Index Number)",
    "Leave Without Pay",
    "Other Funded Leave"
]

def build_option_list(
    names: list,
    value_accessor = (lambda n, i: n),
    selector = (lambda n, i, v: False)
) -> Soup:
    soup = page_builder.soup_from_text("")
    for i in range(len(names)):
        option = soup.new_tag('option')
        option.string = names[i]
        value = value_accessor(names[i], i)
        option['value'] = value
        if selector(names[i], i, value):
            option['selected'] = 'selected'
        soup.append(option)
    return soup

def replace_cell_with_select(cell: Tag, names: list, values: list, attrs = {}):
    soup = page_builder.soup_from_text("<select></select>")
    select = soup.find('select') # Soup.select is already a function, so we access the select element this way
    for key in attrs.keys():
        select[key] = attrs[key]
    string = cell.string
    options = build_option_list(
        names,
        value_accessor= (lambda n, i: values[i]),
        selector= (lambda n, i, v: v == string))
    cell.string = ''
    select.append(options)
    cell.append(select)

def add_cell_to_row(row: Tag, content: str = "", editable = False) -> Tag:
    cell = page_builder.soup_from_text("<td></td>")
    if editable:
        cell.td['contenteditable'] = "true"
        cell.td['class'] = "editable"
    cell.td.string = str(content)
    row.append(cell.td)
    return row('td')[-1]

def replace_cell_with_checkbox(cell: Tag, attrs = {}):
    checkbox = page_builder.soup_from_text("<input type='checkbox'>")
    for key in attrs.keys():
        checkbox.input[key] = attrs[key]
    cell.string = ''
    cell.append(checkbox.input)

def add_row_from_tuple(table: Tag, tup: tuple, editable = False):
    row = page_builder.soup_from_text("<tr></tr>")
    for val in tup:
        add_cell_to_row(row.tr, val, editable = editable)
    table.append(row.tr)
    return table('tr')[-1]

def add_empty_row(table: Tag, num_cells: int, editable = False) -> Tag:
    row = page_builder.soup_from_text("<tr></tr>")
    for _ in range(num_cells):
        add_cell_to_row(row.tr, editable=editable)
    table.append(row.tr)
    return table('tr')[-1]

def build_tbody_from_tups(tups: list, editable = False) -> Tag:
    soup = page_builder.soup_from_text("<tbody></tbody>")
    for tup in tups:
        add_row_from_tuple(soup.tbody, tup, editable=editable)
    return soup.tbody

def build_edit_course_table_body(user: User) -> Tag:
    course_list = request.get_current_courses(user)
    body = build_tbody_from_tups(course_list, editable=True)
    if len(course_list) == 0:
        add_empty_row(body, len(request.REQ_FIELDS), editable=True)
    for row in body.find_all('tr', recursive=False):
        new_cell = add_cell_to_row(row)
        replace_cell_with_checkbox(new_cell, attrs={'id': 'checkCFR'})

    return body

def build_view_courses_table(cfr: tuple) -> Tag:
    soup = page_builder.soup_from_text("<table></table>")
    soup.table['class'] = "table table-bordered table-striped"
    soup.table['style'] = "padding-bottom: 50px"
    
    head = soup.new_tag('thead')
    row = soup.new_tag('tr')
    head.append(row)
    for header in COURSE_TABLE_HEADERS:
        cell = soup.new_tag('th')
        cell.string = header
        row.append(cell)
    soup.table.append(head)

    body = soup.new_tag('tbody')
    soup.table.append(body)

    courses = request.get_courses(cfr)
    for course in courses:
        add_row_from_tuple(soup.tbody, course)

    return soup.table

def build_edit_savings_table_body(user: User) -> Tag:
    savings_list = request.get_current_savings(user)
    body = build_tbody_from_tups(savings_list)
    if len(savings_list) == 0:
        add_empty_row(body, len(request.SAL_FIELDS), editable=True)
    for row in body.find_all('tr', recursive=False):
        new_cell = add_cell_to_row(row)
        replace_cell_with_checkbox(new_cell)

        replace_cell_with_select(
            row.find('td'),
            LEAVE_TYPE_NAMES,
            LEAVE_TYPE_VALUES,
            attrs= {'class': 'form-control'}
        )

    return body