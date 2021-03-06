"""
Functions for constructing various HTML elements and components
for use in pages
"""
from bs4 import BeautifulSoup as Soup
from bs4 import Tag
from .authentication import User
from . import request
from . import page_builder
from . import db_utils

# User-readable headers for the read-only version of a course table
# These should map to the fields of db_utils.REQ_FIELDS
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

# User-readable headers for the course approval table that the
# approvers will see, with columns for approving individual courses
COURSE_APPROVAL_HEADERS = [
    "Priority",
    "Course",
    "Sec",
    "Mini Session?",
    "Online Class?",
    "Students",
    "Instructor",
    "Banner ID",
    "Instructor Rank",
    "Cost",
    "Reason",
    "Commitment Code",
    "Approve"
]

# User-readable headers for the read-only version of a salary savings table
# These should map to the fields of db_utils.SAL_FIELDS
SAVINGS_HEADERS = [
    "Type",
    "Instructor",
    "Savings",
    "Notes"
]

# The values and user-readable names for different kinds of paid leave.
# Used in the options for a leave type select element
LEAVE_TYPE_VALUES = ['Sabbatical', 'RBO', 'LWOP', 'Other']
LEAVE_TYPE_NAMES = [
    "Approved Amounts from Sabbatical Leaves",
    "Research Buy-Out (Provide Index Number)",
    "Leave Without Pay",
    "Other Funded Leave"
]

# The possible values for a course commitment code (used as options in
# the selector)
COMMITMENT_CODES = [
    "EM", "SS", "CO", "DE"
]

# Template for a button appearing within a table
TABLE_BUTTON = """
<button class="btn btn-primary" style="margin:3px"></button>
"""

def build_option_list(
    names: list,
    value_accessor = (lambda n, i: n),
    selector = (lambda n, i, v: False)
) -> Soup:
    """
    Construct a list of option elements (for use inside a select)
    and return it as a BeautifulSoup.

    names is a list of the user-readable names that will be displayed
    in the select (that is, the innerText of each option).

    value_accessor is a function that takes, as arguments, the name
    and index of an option and returns what the internal value for
    the option should be (the 'value' attribute). By default, it
    just uses the name.

    selector is a function that takes, as arguments, the name,
    index and value of an option and returns a boolean indicating
    whether or not that option should be marked as selected.
    """
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
    """
    Replaces the contents of a table cell with a select element with options
    using the given list of names and values.

    If the string contents already in the cell, match one of the values given,
    then that option will be marked as selected.
    attrs is a dictionary of additional attributes that will be applied to the
    select element.
    If the cell is marked as 'contenteditable' or has a class 'editable',
    those attributes will be removed.
    """
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

def replace_cell_with_checkbox(cell: Tag, attrs = {}):
    """
    Replaces the contents of a table cell with a checkbox input

    attrs is a dictionary of additonal attributes to apply to the
    input element
    If the cell is marked as 'contenteditable' or has a class 'editable',
    those attributes will be removed.
    """
    checkbox = page_builder.soup_from_text("<input type='checkbox'>")
    for key in attrs.keys():
        checkbox.input[key] = attrs[key]

    cell.string = ''
    if 'contenteditable' in cell.attrs:
        del cell.attrs['contenteditable']
    if 'class' in cell.attrs and cell.attrs['class'] == "editable":
        del cell.attrs['class']
    cell.attrs['class'] = "noprint"

    cell.append(checkbox.input)

def add_cell_to_row(row: Tag, content: str = "", editable = False) -> Tag:
    """
    Append a table cell to the given table row and return the new cell
    as a tag.

    content determines the string content to place inside the new cell
    (empty by default)
    editable determines whether or not the user will be able to edit the
    contents of the cell (false by default)
    """
    cell = page_builder.soup_from_text("<td></td>")
    if editable:
        cell.td['contenteditable'] = "true"
        cell.td['class'] = "editable"
    cell.td.string = str(content)
    row.append(cell.td)
    return row('td')[-1]

def add_row_from_tuple(table: Tag, tup: tuple, editable = False) -> Tag:
    """
    Add a table row to the given tuple using values from the given
    tuple as the cell contents, and return the new row as a tag

    editable determines whether or not the user will be able to edit
    the contents of the cells (false by default)
    """
    row = page_builder.soup_from_text("<tr></tr>")
    for val in tup:
        add_cell_to_row(row.tr, val, editable = editable)
    table.append(row.tr)
    return table('tr')[-1]

def add_empty_row(table: Tag, num_cells: int, editable = False) -> Tag:
    """
    Add a row of num_cells empty cells to the given table and return
    the new row as a tag.

    editable determines whether or not the user will be able to edit
    the contents of the cells (false by default)
    """
    row = page_builder.soup_from_text("<tr></tr>")
    for _ in range(num_cells):
        add_cell_to_row(row.tr, editable=editable)
    table.append(row.tr)
    return table('tr')[-1]

def build_tbody_from_tups(tups: list, editable = False) -> Tag:
    """
    Build a new tbody element with contents defined by the given list
    of tuples, where each tuple defines one row of the table, and
    return the tbody as a tag.

    editable determines whether or not the user will be able to edit
    the contents of the cells in the table (false by default)
    """
    soup = page_builder.soup_from_text("<tbody></tbody>")
    for tup in tups:
        add_row_from_tuple(soup.tbody, tup, editable=editable)
    return soup.tbody

def build_edit_course_table_body(course_list: list) -> Tag:
    """
    Build the tbody for an editable table of courses defined
    in course_list and return the tbody as a tag.

    Each tuple in course_list should have values corresponding to the
    fields described in db_utils.REQ_FIELDS. The returned table will
    have editable cells and include an additional column with checboxes
    for for the "delete course" option.

    If course_list is empty, there will be a single, empty row in the table
    """
    body = build_tbody_from_tups(course_list, editable=True)
    if len(course_list) == 0:
        add_empty_row(body, len(request.REQ_FIELDS), editable=True)
    # Add a new cell with a checkbox to each row
    for row in body.find_all('tr', recursive=False):
        new_cell = add_cell_to_row(row)
        replace_cell_with_checkbox(new_cell, attrs={'id': 'checkCFR'})

    return body

def build_view_courses_table(courses_list: list) -> Tag:
    """
    Build the table element for a read-only table of courses defined
    in course_list and return the table as a tag

    Each tuple in course_list should have values corresponding to the
    fields described in db_utils.REQ_FIELDS. The returned table will
    have headers corresponding to COURSE_TABLE_HEADERS
    """

    # Build table
    soup = page_builder.soup_from_text("<table></table>")
    soup.table['class'] = "table table-bordered table-striped"
    soup.table['style'] = "padding-bottom: 50px"
    
    # Build thead
    head = soup.new_tag('thead')
    row = soup.new_tag('tr')
    head.append(row)
    for header in COURSE_TABLE_HEADERS:
        cell = soup.new_tag('th')
        cell.string = header
        row.append(cell)
    soup.table.append(head)

    # Build tbody
    body = soup.new_tag('tbody')
    soup.table.append(body)

    # Add courses to tbody
    for course in courses_list:
        add_row_from_tuple(soup.tbody, course)

    return soup.table

def build_view_savings_table(savings_list: list) -> Tag:
    """
    Build the table element for a read-only table of savings defined
    in savings_list and return the table as a tag

    Each tuple in savings_list should have values corresponding to the
    fields described in db_utils.SAL_FIELDS. The returned table will
    have headers corresponding to SAVINGS_HEADERS
    """

    # Build table
    soup = page_builder.soup_from_text("<table></table>")
    soup.table['class'] = "table table-bordered table-striped"
    soup.table['style'] = "padding-bottom: 50px"
    
    # Build thead
    head = soup.new_tag('thead')
    row = soup.new_tag('tr')
    head.append(row)
    for header in SAVINGS_HEADERS:
        cell = soup.new_tag('th')
        cell.string = header
        row.append(cell)
    soup.table.append(head)

    # Build tbody
    body = soup.new_tag('tbody')
    soup.table.append(body)

    # Add courses to tbody
    for entry in savings_list:
        add_row_from_tuple(soup.tbody, entry)

    return soup.table

def build_edit_savings_table_body(savings_list: list) -> Tag:
    """
    Build the tbody for an editable table of salary savings defined
    in savings_list and return the tbody as a tag.

    Each tuple in savings_list should have values corresponding to the
    fields described in db_utils.SAL_FIELDS. The returned table will
    have editable cells and include an additional column with checboxes
    for for the "delete entry" option.

    If savings_list is empty, there will be a single, empty row in the table
    """
    body = build_tbody_from_tups(savings_list)
    if len(savings_list) == 0:
        add_empty_row(body, len(request.SAL_FIELDS), editable=True)
    # Add a new cell with a checkbox to each row
    for row in body.find_all('tr', recursive=False):
        new_cell = add_cell_to_row(row)
        replace_cell_with_checkbox(new_cell)

        # Replace the first cell with a leave-type selector in each row
        replace_cell_with_select(
            row.find('td'),
            LEAVE_TYPE_NAMES,
            LEAVE_TYPE_VALUES,
            attrs= {'class': 'form-control'}
        )

    return body

def build_approve_table_body(summary: list):
    """
    Build the tbody of the main table for the approver course funding request page.

    summary is a list with one element for each department's latest cfr
    where each element is a tuple with the following fields:
        department name, total course costs, total savings, dean commitment,
        funds needed and finally a boolean value indicating whether or not
        each course has been approved.
    This summary can be gotten as the 'summary' element of the dict returned
    by db_utils.get_approver_data()
    """

    # Create the table rows from the summary
    body = build_tbody_from_tups(summary)

    index = 0
    # Iterate through each row
    for row in body.find_all('tr', recursive=False):

        # Make just the dean_commitment cell editable
        commitment_cell = row('td')[3]
        commitment_cell['contenteditable'] = "true"
        commitment_cell['class'] = "editable"

        # Replace the last cell with an image depending on whether or
        # not all the courses in the cfr have been approved
        img = page_builder.soup_from_text('<img height="30px"></img>')
        last_cell = row('td')[-1]
        approved = summary[index][5]
        if approved:
            src = "/static/images/check.png"
        else:
            src = "/static/images/x.png"
        img.img['src'] = src
        last_cell.string = ''
        last_cell.append(img)

        # Add a new column to each row which will contain to open the
        # respective modal if not all courses have been approved
        new_cell = add_cell_to_row(row)
        if approved:
            new_cell.string = "Already approved"
        else:
            course_button = page_builder.soup_from_text(TABLE_BUTTON)
            course_button.button['onclick'] = f"summonModal(\"modal_cfr_{index}\")"
            course_button.button.string = "Approve Courses"
            new_cell.append(course_button)

        index += 1

    return body

def build_approve_course_table(course_list: list) -> Tag:
    """
    Build the "Approve Courses" table that the approver uses to 
    approve and set commitment codes for courses.

    NOTE: The elements of course_list here are a little different
    than in other parts of the code. Each element is a tuple with
    all the fields of db_utils.REQ_FIELDS PLUS two more fields
    for the request approver and commitment code.
    Tuples like these can be gotten as the elements of the 'course_lists'
    elements in the dict returned by db_utils.get_approver_data()
    """

    # Build table
    soup = page_builder.soup_from_text("<table></table>")
    soup.table['class'] = 'table table-bordered table-striped'
    soup.table['style'] = 'padding-bottom: 50px'

    # Add thead
    head = soup.new_tag('thead')
    row = soup.new_tag('tr')
    head.append(row)
    for header in COURSE_APPROVAL_HEADERS:
        cell = soup.new_tag('th')
        cell.string = header
        row.append(cell)
    soup.table.append(head)

    # Add tbody
    body = soup.new_tag('tbody')
    soup.table.append(body)

    # Iterate through courses
    for i in range(len(course_list)):
        data = course_list[i][:11] + (course_list[i][12], course_list[i][11])
        new_row = add_row_from_tuple(body, data)

        # Make cell for course cost editable
        cells = new_row.find_all('td')
        cost_cell = cells[9]
        cost_cell['contenteditable'] = "true",
        cost_cell['class'] = "editable"

        # Replace the cell with the commitment code with a select element
        commitment_cell = cells[-2]
        replace_cell_with_select(
            commitment_cell,
            names=COMMITMENT_CODES,
            values=COMMITMENT_CODES,
             attrs= {'class': 'form-control'},
        )

        # Replace the cell with the approval status with a checkbox
        approve_cell = cells[-1]
        replace_cell_with_checkbox(approve_cell)

    return soup.table

def build_revision_history(course_lists: list) -> Soup:
    """
    Build a series of tables representing the revisions defined
    in course_lists and return it as a Soup.

    Each element in course_lists represents one table as a list of 
    courses where each course is a tuple with values corresponding to
    the fields in db_utils.REQ_FIELDS. That is, course_lists
    is a list of lists of tuples

    The returned soup contains headers labeling the tables as revisions
    in reverse-chronologial order.
    """
    soup = page_builder.soup_from_text("")

    if len(course_lists) == 0:
        soup.append("No revisions available.")
    else:
        for i in range(len(course_lists)):
            header = soup.new_tag('h3')
            header.string = f"Revision {len(course_lists) - i}"
            soup.append(header)

            table = build_view_courses_table(course_lists[i])
            soup.append(table)

    return soup

def build_modal(title: str, modal_id: str, content) -> Tag:
    """
    Build a modal and return it as a tag.

    title is the text to display in the modal header
    modal_id will the id of the modal element
    and content will be appended to the modal's body.

    Every modal contains a "Close" button in its footer
    """

    # Build modal div
    soup = page_builder.soup_from_text("<div class=\"modal\"></div>")
    soup.div['id'] = modal_id

    content_div = soup.new_tag('div')
    content_div['class'] = 'modal-content'

    # Add header
    header_container = soup.new_tag('div')
    header_container['class'] = 'modal-header'
    header = soup.new_tag('h1')
    header.string = title
    header_container.append(header)

    # Add body and append content
    body = soup.new_tag('div')
    body['class'] = 'modal-body'
    body.append(content)

    # Add footer with close button
    footer = soup.new_tag('div')
    footer['class'] = 'modal-footer'
    close_button = soup.new_tag('button')
    close_button['class'] = 'btn btn-default'
    close_button['onclick'] = f"dismissModal(\"{modal_id}\")"
    close_button.string = 'Close'
    footer.append(close_button)

    # Assemble
    content_div.append(header_container)
    content_div.append(body)
    content_div.append(footer)

    soup.div.append(content_div)
    return soup.div

def build_tabs(content_list: list, tab_names: list, tab_ids: list) -> Tag:
    """
    Build a tab pane element from the given content with the given names
    and return it as a tag.

    content_list is a list of the contents for each tab (anything that
    can be appended to a BeautifulSoup Tag will work).
    tab_names is the user-readable names that will label each tab.
    tab_ids are the internal names used to identify each tab.
    """
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
