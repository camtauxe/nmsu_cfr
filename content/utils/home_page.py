"""
Functions for building the site's home page.

The content of the home page can change depending on
the currently logged in user.
"""
from . import page_builder
from . import authentication
from bs4 import BeautifulSoup


def build_home_page(user: authentication.User) -> BeautifulSoup:
    """
    Builds the home page for a given user and returns it
    as a BeautifulSoup.
    The provided user is the same dictionary that is returned
    by the authentication.authenticate function.
    If the provided user is None, then this function returns
    a generic "You are not logged in" home page.
    """
    if user is None:
        content = "You are not logged in."
    else:
        content = "Hello, {}! You are logged in as a {}".format(
            user.username, user.role.name
        )
    return page_builder.build_page_around_content(content)
