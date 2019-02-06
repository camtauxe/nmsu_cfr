"""
Functions for responding to various errors that may occur during execution.
Can build pages to display information about HTTP errors.
"""

import os
import traceback
from datetime import datetime
from . import page_builder as builder
from bs4 import BeautifulSoup

def build_500_error_page(exception) -> BeautifulSoup:
    """
    Build a webpage displaying information for 500 Internal Server Error
    regarding the given exception and return it as a BeautifulSoup

    If the environment variable 'DEBUG' is 'yes', then debug information
    such as the current time and date and a stack trace of the exception
    will be displayed on the page.
    """
    page = builder.build_page_from_file("500.html")

    if os.environ.get('DEBUG') != 'yes':
        page.find(id="debugonly").extract()
    else:
        builder.insert_at_id(page, "datetime", str(datetime.now()), raw_text=True)
        builder.insert_at_id(page, "errortype", str(type(exception)), raw_text=True)
        builder.insert_at_id(page, "stacktrace", traceback.format_exc(), raw_text=True)

    return page

def build_404_error_page() -> BeautifulSoup:
    """
    Build a webpage displaying a 404 Not Found Error and return
    it as a BeautifulSoup
    """
    return builder.build_page_from_file("404.html")