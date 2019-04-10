from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from .authentication import User
from . import request

def add_cell_to_row(table: Soup, row: Tag, content: str = ""):
    cell = table.new_tag('td')
    cell['contenteditable'] = "true"
    cell['class'] = "editable"
    cell.string = str(content)
    row.append(cell)

def add_checkbox_to_row(table: Soup, row: Tag):
    add_cell_to_row(table, row)
    last_cell = row.find_all('td')[-1]

    checkbox = table.new_tag('input')
    checkbox['type'] = 'checkbox'
    checkbox['id'] = 'checkCFR'
    last_cell.append(checkbox)
    row.append(last_cell)

def add_row_to_table(table: Soup, tup: tuple):
    row = table.new_tag('tr')
    for val in tup:
        add_cell_to_row(table, row, val)
    add_checkbox_to_row(table, row)
    table.append(row)

def add_empty_row_to_table(table: Soup, num_cells: int):
    row = table.new_tag('tr')
    for _ in range(num_cells):
        add_cell_to_row(table, row)
    add_checkbox_to_row(table, row)
    table.append(row)
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