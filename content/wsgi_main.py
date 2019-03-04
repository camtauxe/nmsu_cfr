#!/usr/bin/python3
import os
import traceback
import mysql.connector
import json
from pathlib import PurePath
from utils import page_builder
from utils import sql_connection
from utils import error_handling
from utils import sql_utils
from utils import cfrenv

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
        *additional_headers
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
        start_response(status, [('Content-Type',mime)]+list(additional_headers))

    # Initialize the CFR environment
    cfrenv.init_environ(environ)
    # If the environment is not configured correctly. Respond
    # with an error page immediately.
    if not cfrenv.verify_environ():
        respond(status="500 Internal Server Error")
        error_page = page_builder.build_page_from_file('config_error.html')
        yield page_builder.soup_to_bytes(error_page)

    # Most of the execution is wrapped in a try/catch. If an exception
    # is thrown, it will be caught and passed to the error handler
    # which will generate a nicely-formatted 500 Internal Server Error page
    try:
        # Get the top part of the path supplied in the request's URL.
        # If no path was given, this will simply be '/'.
        # This will be used to determine what function the server does
        path = PurePath(environ.get('PATH_INFO'))
        if len(path.parts) < 2:
            top = '/'
        else:
            top = path.parts[1]

        # For 'lorem' (or if no path was provided), build and send back
        # a lorem ipsum page
        if top == '/' or top == 'lorem':
            page = page_builder.build_page_from_file("lorem_ipsum.html")
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
