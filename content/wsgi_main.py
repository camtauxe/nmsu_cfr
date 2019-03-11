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
from utils import home_page
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

    ###########################################
    # RESPONSE HANDLERS
    #   Each function should respond to a particular request and return
    #   a byte seqence to return. (Each one should also call respond() at
    #   some point)
    ############################################

    # If no path was provided, check if the user is logged in
    # (with a cookie) and send back a home page if they are.
    # If not, send back the login page
    def handle_root():
        logged_in = False
        if 'HTTP_COOKIE' in environ:
            user = authentication.authenticate_from_cookie(environ['HTTP_COOKIE'])
            if user is not None:
                logged_in = True
                page = home_page.build_home_page(user)
                respond()
                return page_builder.soup_to_bytes(page)
        if not logged_in:
            page = page_builder.build_page_from_file("login.html")
            respond()
            return page_builder.soup_to_bytes(page)

    # For 'login' use the provided URL parameters to authenticate the
    # user. If successful send back a home page with a set-cookie
    # header to log the user in. If unsuccessful, send back the
    # login page
    def handle_login():
        logged_in = False
        if 'QUERY_STRING' in environ:
            query = parse_qs(environ['QUERY_STRING'])
            if 'username' in query:
                user = authentication.authenticate(query['username'][0])
                if user is not None:
                    respond(
                        additional_headers = [('Set-Cookie',authentication.create_cookie(user))]
                    )
                    page = home_page.build_home_page(user)
                    logged_in = True
                    return page_builder.soup_to_bytes(page)
        if not logged_in:
            respond(
                additional_headers = [('Set-Cookie',authentication.clear_cookie())]
            )
            page = page_builder.build_page_from_file("login.html")
            return page_builder.soup_to_bytes(page)

    def handle_cfr():
        page = page_builder.build_page_from_file("cfr.html")
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_salary_saving():
        page = page_builder.build_page_from_file("salary_saving.html")
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_previous_semesters():
        page = page_builder.build_page_from_file("previous_semesters.html")
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_revisions():
        page = page_builder.build_page_from_file("revisions.html")
        respond()
        return page_builder.soup_to_bytes(page)

    # For 'db_info' return a JSON describing the database
    def handle_db_info():
        respond(mime = "text/json; charset=utf-8")
        info = sql_utils.get_database_info()
        return json.dumps(info, indent=4).encode('utf-8')

    # For 'error' throw an error to test the the error-catching system.
    def handle_error():
        raise RuntimeError(
            "This was supposed to happen because you selected 'error'"
        )

    # Register handlers into a dictionary
    handlers = {
        '/':                    handle_root,
        'login':                handle_login,
        'cfr':                  handle_cfr,
        'salary_saving':        handle_salary_saving,
        'previous_semesters':   handle_previous_semesters,
        'revisions':            handle_revisions,
        'db_info':              handle_db_info,
        'error':                handle_error
    }

    # Initialize the CFR environment
    cfrenv.init_environ(environ)
    # If the environment is not configured correctly. Respond
    # with an error page immediately.
    if not cfrenv.verify_environ():
        respond(status="500 Internal Server Error")
        error_page = page_builder.build_page_from_file('config_error.html')
        return page_builder.soup_to_bytes(error_page)

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

        if top in handlers:
            yield handlers[top]()
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
