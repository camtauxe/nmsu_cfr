"""
Functions for using BeatifulSoup to construct web pages
"""
import traceback
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup as Soup
from bs4 import Comment
from . import cfrenv
from . import component_builder
from . import request
from . import users
from . import semesters
from . import db_utils
from .sql_connection import Transaction
from .authentication import User, UserRole

# The RESOURCE_DIR refers to directory containing resource files
# loaded by the page builder. Usually, these are html files that
# the page builder assembles together.
#
# Right now, this is pointing to the directory 'resource' in the web root
RESOURCE_DIR = Path(__file__).parent.parent.joinpath("resource")

def soup_from_file(path, absolute_path = False) -> Soup:
    """
    Parse an html file into a BeautifulSoup and return it.

    By default, this will look for the given filename inside
    the RESOURCE_DIR, but if absolute_path is True, then the path
    will be interpreted as an absolute path for a file anywhere on
    the machine.
    """
    if (absolute_path):
        url = path
    else:
        url = RESOURCE_DIR.joinpath(path)

    with open(url) as f:
        soup = Soup(f, "html.parser")
    return soup

def soup_from_text(text) -> Soup:
    """
    Parse the given html string into a BeautifulSoup and return it
    """
    return Soup(text, "html.parser")

def insert_at_id(containing_soup: Soup, tag_id, content, raw_text = False):
    """
    Insert some content into another soup at the tag with the given id.

    content can be either a BeautifulSoup or a string. If it is a string,
    it will first be parsed into a BeautifulSoup before being inserted.
    Unless raw_text is True in which case it will be inserted directly.
    """
    if not isinstance(content, Soup) and not raw_text:
        content = soup_from_text(content)
    containing_soup.find(id=tag_id).append(content)


def build_page_around_content(content, raw_text = False, includeNavbar = True) -> Soup:
    """
    Build a full page with the given content as the page's content
    and return it as a BeautifulSoup.

    If includeNavbar is False, then the navbar will not be present
    on the built page.

    content can be either a BeautifulSoup or a string. If it is a string,
    it will first be parsed into a BeautifulSoup before being inserted.
    Unless raw_text is True in which case it will be inserted directly.
    """
    page = soup_from_file("page_wrapper.html")
    if not includeNavbar:
        navbar = page.find(id='main-navigation')
        navbar.extract()
    if not isinstance(content, Soup) and not raw_text:
        content = soup_from_text(content)
    page.find(id='pagecontent').append(content)
    return page

def build_page_from_file(path, absolute_path = False, includeNavbar = True) -> Soup:
    """
    Build a full page with the contents of the given html file as the
    page's content and return it as a BeautifulSoup.

    If includeNavbar is False, then the navbar will not be present
    on the built page.

    By default, this will look for the given filename inside
    the RESOURCE_DIR, but if absolute_path is True, then the path
    will be interpreted as an absolute path for a file anywhere on
    the machine.
    """
    content = soup_from_file(path, absolute_path = absolute_path)
    return build_page_around_content(content, includeNavbar = includeNavbar)

def build_login_page(message = None):
    """
    Build a login page.

    If a string, message, is provided then the message will be
    displayed as an error below the login form.
    """
    page = build_page_from_file("login.html", includeNavbar=False)
    if message is not None:
        error_message = f'<p class="error" style="padding: 5px;">{message}</p>'
        insert_at_id(page, 'loginp', error_message)
    return page

def build_home_page(user: User) -> Soup:
    """
    Builds the home page for a given user and returns it
    as a BeautifulSoup.
    If the provided user is None, then this function returns
    a generic "You are not logged in" home page.
    """
    if user is None:
        content = "You are not logged in."
        return build_page_around_content(content)

    if user.role == UserRole.ADMIN:
        return build_admin_page()
    else:
        content = f"Hello, {user.username}!"
        return build_page_around_content(content)

def build_cfr_page(user: User) -> Soup:
    """
    Build the course funding request page for the given user and
    return it as a BeautifulSoup
    """

    page = build_page_from_file("cfr.html")
    # Build table body from current courses list
    courses = db_utils.quick_exec(db_utils.get_current_courses, user.dept_name)
    body = component_builder.build_edit_course_table_body(courses)
    body['id'] = 'cfrTable'

    # Insert table body after table head
    table_head = page.find('table',id='cfrTable_full').find('thead')
    table_head.insert_after(body)
    return page

def build_savings_page(user: User) -> Soup:
    """
    Build the sources of salary savings page for the given user and
    return it as a BeautifulSoup
    """
    page = build_page_from_file("salary_saving.html")
    # Build table body from current salary list
    savings = db_utils.quick_exec(db_utils.get_current_savings, user.dept_name)
    body = component_builder.build_edit_savings_table_body(savings)
    body['id'] = 'salaryTable'

    # Insert table body after table head
    table_head = page.find('table',id='salaryTable_full').find('thead')
    table_head.insert_after(body)
    return page

def build_department_selector(current_dept: str = None):
    """
    Create a select element for selecting departments and return it as
    a BeautifulSoup. This is used for the approver side of the 
    revisions and previous semesters pages.

    When changed, the select element will cause the page to refresh with
    the newly selected department as a query in the URL.

    If a current_dept is provided, that department will be marked as selected.
    """

    soup = soup_from_text('<select></select>')
    select = soup.find('select')
    select['class'] = 'form-control'
    # Add Javascript to refresh the page on change
    select['onchange'] = """
window.location.href = window.location.pathname + "?dept="+encodeURIComponent(this.value)
    """
    
    # Create options from list of departments
    departments = db_utils.quick_exec(db_utils.get_departments)
    options = component_builder.build_option_list(
        departments,
        selector= (lambda n, i, v: n == current_dept)
    )
    select.append(options)

    return soup

def build_revisions_page(user: User, dept_override: str = None):
    """
    Build the revisions page for the given user and return it as 
    a BeautifulSoup.

    If the user is an approver or admin, a dept_override can be added
    to change which department's revisions are displayed. dept_override
    is ignored if the user is a submitter. For submitters, only their
    own department's revisions will be shown.
    """
    content = soup_from_text("")

    # Set dept_name depending on the user's role and dept_override
    if user.role == UserRole.SUBMITTER:
        dept_name = user.dept_name
    else:
        selector = build_department_selector(dept_override)
        if dept_override:
            dept_name = dept_override
        else:
            dept_name = str(selector.find('option').string)
        content.append(selector)

    content.append(soup_from_text(f"<h1>Revision History ({dept_name})</h1>"))

    # course_lists is a list of lists of courses representing the revision
    # history of the department
    course_lists = []
    with Transaction() as cursor:
        revisions = db_utils.get_all_revisions_for_active_semester(cursor, dept_name)
        for revision in revisions:
            courses = db_utils.get_courses(cursor, revision)
            course_lists.append(courses)

    # Build the revision history and add it to the page
    history = component_builder.build_revision_history(course_lists)
    content.append(history)

    page = build_page_around_content(content)
    return page

def build_previous_semesters_page(user: User, dept_override: str = None):
    """
    Build the prevision semesters page for the given user and return it as 
    a BeautifulSoup.

    If the user is an approver or admin, a dept_override can be added
    to change which department's history is displayed. dept_override
    is ignored if the user is a submitter. For submitters, only their
    own department's history will be shown.
    """
    content = soup_from_text("")

    # Set dept_name depending on the user's role and dept_override
    if user.role == UserRole.SUBMITTER:
        dept_name = user.dept_name
    else:
        selector = build_department_selector(dept_override)
        if dept_override:
            dept_name = dept_override
        else:
            dept_name = str(selector.find('option').string)
        content.append(selector)

    content.append(soup_from_text(f"<h1>Full Revision History ({dept_name})</h1>"))

    # histories is a list of lists of lists of courses (yes, really)
    # Representing the revision histories for each semester in the department
    histories = []
    tab_names = []
    tab_ids = []
    with Transaction() as cursor:
        for s in db_utils.get_semesters(cursor):
            revisions = []
            for r in db_utils.get_all_revisions_for_semester(cursor, dept_name, s):
                revisions.append(db_utils.get_courses(cursor, r))

            # Build a revision history for this semester and create a tab for it
            histories.append(component_builder.build_revision_history(revisions))
            tab_names.append(f"{s[0]}, {s[1]}")
            tab_ids.append(f"{s[0]}{s[1]}")

    # Build tab pane and add it to page
    tabs = component_builder.build_tabs(histories, tab_names, tab_ids)
    content.append(tabs)

    page = build_page_around_content(content)
    return page

def build_admin_page():
    """
    Build the admin controls page and return it as a BeautifulSoup
    """
    page = build_page_from_file("admin.html", includeNavbar=False)

    # Get all necessary information from the database in one transaction
    with Transaction() as cursor:
        usernames = db_utils.get_usernames(cursor)
        depts = db_utils.get_departments(cursor)
        semester_list = db_utils.get_semesters(cursor)
        active_semester = db_utils.get_active_semester(cursor)

    # Populate user select with options
    user_options = component_builder.build_option_list(usernames)
    insert_at_id(page, 'userselect', user_options)

    # Populate department list with options
    dept_options = component_builder.build_option_list(depts)
    insert_at_id(page, 'dept_list', dept_options)
    # The department text box will start with the name
    # of the first department
    if len(depts) > 0:
        page.find('input', attrs={'name':'dept_name'})['value'] = depts[0]

    # Populate semester select with options
    semester_names = [f"{d[0]}, {d[1]}" for d in semester_list]
    semester_options = component_builder.build_option_list(
        semester_names,
        value_accessor= 
            (lambda n, i: str(semester_list[i][0])+" "+str(semester_list[i][1])),
        selector=
            (lambda n, i, v: semester_list[i] == active_semester)
    )
    insert_at_id(page, 'semesterselect', semester_options)

    return page

def build_500_error_page(exception) -> Soup:
    """
    Build a webpage displaying information for 500 Internal Server Error
    regarding the given exception and return it as a BeautifulSoup

    If the environment variable 'DEBUG' is 'yes', then debug information
    such as the current time and date and a stack trace of the exception
    will be displayed on the page.
    """
    page = build_page_from_file("500.html", includeNavbar=False)

    if cfrenv.getenv('DEBUG') != 'yes':
        page.find(id="debugonly").extract()
    else:
        insert_at_id(page, "datetime", str(datetime.now()), raw_text=True)
        insert_at_id(page, "errortype", str(type(exception)), raw_text=True)
        insert_at_id(page, "stacktrace", traceback.format_exc(), raw_text=True)

    return page

def soup_to_bytes(soup: Soup) -> bytes:
    """
    Encode a BeautifulSoup into an array of bytes encoded in UTF-8.
    This is what will be sent back to the web server.

    This process will also remove all html comments.
    """
    for comment in soup.find_all(text=lambda text:isinstance(text, Comment)):
        comment.extract()
    return str(soup).encode('UTF-8')