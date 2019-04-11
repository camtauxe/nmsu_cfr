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

def add_header_to_table(table_soup: Soup):
    head = table_soup.new_tag('thead')
    row = table_soup.new_tag('tr')
    head.append(row)
    for header in TABLE_HEADERS:
        cell = table_soup.new_tag('th')
        cell.string = header
        row.append(cell)
    table_soup.table.append(head)

def build_course_table_body(user: User):
    course_list = request.get_current_courses(user)
    body = build_table_body(course_list)
    if len(course_list) == 0:
        add_empty_row_to_table(body, len(request.REQ_FIELDS))
    return body

def build_course_table_full(cfr: tuple):
    soup = Soup("<table></table>", 'html.parser')
    soup.table['class'] = "table table-bordered table-striped"
    soup.table['style'] = "padding-bottom: 50px"
    add_header_to_table(soup)

    body = soup.new_tag('tbody')
    soup.table.append(body)

    courses = request.get_courses(cfr)
    for course in courses:
        add_row_to_table(soup, course, editable=False)

    return soup