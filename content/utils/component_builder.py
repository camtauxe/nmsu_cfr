from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from .authentication import User
from . import request
from . import page_builder
from . import db_utils

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
    if 'contenteditable' in cell.attrs:
        del cell.attrs['contenteditable']
    if 'class' in cell.attrs and cell.attrs['class'] == "editable":
        del cell.attrs['class']
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

def build_edit_course_table_body(course_list) -> Tag:
    body = build_tbody_from_tups(course_list, editable=True)
    if len(course_list) == 0:
        add_empty_row(body, len(request.REQ_FIELDS), editable=True)
    for row in body.find_all('tr', recursive=False):
        new_cell = add_cell_to_row(row)
        replace_cell_with_checkbox(new_cell, attrs={'id': 'checkCFR'})

    return body

def build_view_courses_table(courses_list) -> Tag:
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

    for course in courses_list:
        add_row_from_tuple(soup.tbody, course)

    return soup.table

def build_edit_savings_table_body(savings_list) -> Tag:
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

def build_revision_history(course_lists: list) -> Soup:
    soup = page_builder.soup_from_text("")

    for i in range(len(course_lists)):
        header = soup.new_tag('h3')
        header.string = f"Revision {len(course_lists) - i}"
        soup.append(header)

        table = build_view_courses_table(course_lists[i])
        soup.append(table)

    return soup

def build_tabs(content_list: list, tab_names: list, tab_ids: list) -> Tag:
    soup = page_builder.soup_from_text('<div id="tabs"></div>')

    tabnav = soup.new_tag('div')
    tabnav['id'] = 'tabbed-nav'
    tabnav['class'] = 'noprint'

    tablist = soup.new_tag('ul')
    tablist['class'] = 'nav nav-tabs'
    tablist['role'] = 'tablist'

    tabcontent = soup.new_tag('div')
    tabcontent['class'] = 'tab-content padded-15'

    for i in range(min([len(content_list), len(tab_names), len(tab_ids)])):
        tab = soup.new_tag('li')
        tab['role'] = 'presentation'

        tablink = soup.new_tag('a')
        tablink['href'] = '#'+tab_ids[i]
        tablink['aria-controls'] = tab_ids[i]
        tablink['role'] = 'tab'
        tablink['data-toggle'] = 'tab'
        tablink.string = tab_names[i]

        content = soup.new_tag('div')
        content['role'] = 'tabpanel'
        content['class'] = 'tab-pane fade'
        content['id'] = tab_ids[i]

        if i == 0:
            content['class'] = 'tab-pane fade in active'
            tablink['class'] = 'active'

        content.append(content_list[i])
        tabcontent.append(content)
        tab.append(tablink)
        tablist.append(tab)

    tabnav.append(tablist)
    soup.append(tabnav)
    soup.append(tabcontent)

    return soup
