"""
Functions for using BeatifulSoup to construct web pages
"""
import traceback
from datetime import datetime
from pathlib import Path
from bs4 import BeautifulSoup as Soup
from bs4 import Comment
from . import cfrenv

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


def build_page_around_content(content, raw_text = False) -> Soup:
    """
    Build a full page with the given content as the page's content
    and return it as a BeautifulSoup.

    content can be either a BeautifulSoup or a string. If it is a string,
    it will first be parsed into a BeautifulSoup before being inserted.
    Unless raw_text is True in which case it will be inserted directly.
    """
    page = soup_from_file("page_wrapper.html")
    if not isinstance(content, Soup) and not raw_text:
        content = soup_from_text(content)
    page.find(id='pagecontent').append(content)
    return page

def build_page_from_file(path, absolute_path = False) -> Soup:
    """
    Build a full page with the contents of the given html file as the
    page's content and return it as a BeautifulSoup.

    By default, this will look for the given filename inside
    the RESOURCE_DIR, but if absolute_path is True, then the path
    will be interpreted as an absolute path for a file anywhere on
    the machine.
    """
    content = soup_from_file(path, absolute_path = absolute_path)
    return build_page_around_content(content)

def build_500_error_page(exception) -> Soup:
    """
    Build a webpage displaying information for 500 Internal Server Error
    regarding the given exception and return it as a BeautifulSoup

    If the environment variable 'DEBUG' is 'yes', then debug information
    such as the current time and date and a stack trace of the exception
    will be displayed on the page.
    """
    page = build_page_from_file("500.html")

    if cfrenv.getenv('DEBUG') != 'yes':
        page.find(id="debugonly").extract()
    else:
        insert_at_id(page, "datetime", str(datetime.now()), raw_text=True)
        insert_at_id(page, "errortype", str(type(exception)), raw_text=True)
        insert_at_id(page, "stacktrace", traceback.format_exc(), raw_text=True)

    return page

def build_404_error_page() -> Soup:
    """
    Build a webpage displaying a 404 Not Found Error and return
    it as a BeautifulSoup
    """
    return build_page_from_file("404.html")

def soup_to_bytes(soup: Soup) -> bytes:
    """
    Encode a BeautifulSoup into an array of bytes encoded in UTF-8.
    This is what will be sent back to the web server.

    This process will also remove all html comments.
    """
    for comment in soup.find_all(text=lambda text:isinstance(text, Comment)):
        comment.extract()
    return str(soup).encode('UTF-8')