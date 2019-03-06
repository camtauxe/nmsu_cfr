#!/usr/bin/python3
import os
import traceback
import mysql.connector
import json
from urllib.parse import parse_qs
from pathlib import PurePath
from utils import page_builder
from utils import sql_connection
from utils import error_handling
from utils import sql_utils
from utils import authentication

def application(environ, start_response):
    """
    This is the main entry point for the web server.

    This function must be named 'application' because that is what the web
    server will look to call when it calls the file.
    environ contains information regarding the HTTP request that was
    received.
    start_response is a function to be called with an HTTP status and
    response headers when sending a response.
    This function will yield a byte array containing the body of the
    HTTP response.

    Please see the WSGI standard for more information:
    https://www.python.org/dev/peps/pep-3333/
    """

    def respond(
        status: str     = "200 OK",
        mime: str       = "text/html; charset=utf-8",
        additional_headers: list = []
    ):
        """
        Call start_response with the given status, and content-type
        header for the given MIME Type and any additonal headers provided.

        Provided headers should be tuples with the variable name as the first
        part and the value as the second part.
        Example: ('Content-Length', 500)

        If no status or MIME Type is provided, they will default to
        '200 OK' and 'text/html' respectively.
        """
        start_response(status, [('Content-Type',mime)]+additional_headers)

    # Most of the execution is wrapped in a try/catch. If an exception
    # is thrown, it will be caught and passed to the error handler
    # which will generate a nicely-formatted 500 Internal Server Error page
    try:
        # Get the top part of the path supplied in the request's URL.
        # If no path was given, this will simply be '/'.
        # This will be used to determine what function the server does
        path = PurePath(environ.get('PATH_INFO').split('?')[0])
        if len(path.parts) < 2:
            top = '/'
        else:
            top = path.parts[1]

        # If no path was provided, check if the user is logged in
        # (with a cookie) and send back a home page if they are.
        # If not, send back the login page
        if top == '/':
            page = page_builder.build_page_from_file("login.html")
            respond()
            yield page_builder.soup_to_bytes(page)

        # For 'login' use the provided URL parameters to authenticate the
        # user. If successful send back a home page with a set-cookie
        # header to log the user in. If unsuccessful, send back the
        # login page
        elif top == 'login':
            logged_in = False
            if 'QUERY_STRING' in environ:
                query = parse_qs(environ['QUERY_STRING'])
                if 'username' in query:
                    user = authentication.authenticate(query['username'][0])
                    if user is not None:
                        respond(
                            additional_headers = [('Set-Cookie','username='+user['username'])]
                        )
                        page = page_builder.build_page_from_file("cfr.html")
                        logged_in = True
                        yield page_builder.soup_to_bytes(page)
            if not logged_in:
                raise RuntimeError("Could not log in!!")

        elif top == 'cfr' or top == '/cfr':
            page = page_builder.build_page_from_file("cfr.html")
            respond()
            yield page_builder.soup_to_bytes(page)

        elif top == 'salary_saving' or top == '/salary_saving':
            page = page_builder.build_page_from_file("salary_saving.html")
            respond()
            yield page_builder.soup_to_bytes(page)

        # For 'db_info' return a JSON describing the database
        elif top == 'db_info':
            respond(mime = "text/json; charset=utf-8")
            info = sql_utils.get_database_info()
            yield json.dumps(info, indent=4).encode('utf-8')

        # For 'error' throw an error to test the the error-catching system.
        elif top == 'error':
            raise RuntimeError(
                "This was supposed to happen because you selected 'error'"
            )

        # If the top part of the path was not recognized, send back
        # a 404 page.
        else:
            respond(status="404 Not Found")
            error_page = error_handling.build_404_error_page()
            yield page_builder.soup_to_bytes(error_page)

    except Exception as err:
        respond(status="500 Internal Server Error")
        error_page = error_handling.build_500_error_page(err)
        yield page_builder.soup_to_bytes(error_page)
