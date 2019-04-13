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

def build_cfr_page(user: User):
    page = build_page_from_file("cfr.html")
    body = component_builder.build_edit_course_table_body(user)
    body['id'] = 'cfrTable'
    table_head = page.find('table',id='cfrTable_full').find('thead')
    table_head.insert_after(body)
    return page

def build_savings_page(user: User):
    page = build_page_from_file("salary_saving.html")
    body = component_builder.build_edit_savings_table_body(user)
    body['id'] = 'salaryTable'
    table_head = page.find('table',id='salaryTable_full').find('thead')
    table_head.insert_after(body)
    return page

def build_revisions_page(user: User):
    content = soup_from_text(f"<h1>Revision History ({user.dept_name})</h1>")

    revisions = request.get_all_revisions(user)
    for revision in revisions:
        table_title = content.new_tag('h3')
        table_title.string = f"Revision {revision[3]}"
        content.append(table_title)
        table = component_builder.build_view_courses_table(revision)
        content.append(table)
    page = build_page_around_content(content)
    return page

def build_admin_page():
    page = build_page_from_file("admin.html", includeNavbar=False)

    usernames = users.get_usernames()
    user_options = component_builder.build_option_list(usernames)
    insert_at_id(page, 'userselect', user_options)

    depts = users.get_departments()
    dept_options = component_builder.build_option_list(depts)
    insert_at_id(page, 'dept_list', dept_options)
    if len(depts) > 0:
        page.find('input', attrs={'name':'dept_name'})['value'] = depts[0]

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