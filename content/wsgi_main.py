#!/usr/bin/python3
import os
import traceback
import mysql.connector
import json
from urllib.parse import parse_qs
from pathlib import PurePath

from utils import page_builder
from utils import sql_connection
from utils import authentication
from utils import home_page
from utils import cfrenv
from utils import create_user
from utils import request
from utils import dummy

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

    def dict_from_POST():
        """
        Returns a dictionary obtained by parsing the body of the HTTP request,
        assumes that this is a POST request and that the body is in the
        application/x-www-form-urlencoded format.

        If the request has no body, then this will still return a dict, but
        it will be empty. Each value in the dictionary will be list containing
        the values for that entry.
        """
        body_text = environ['wsgi.input'].read()
        query_raw = parse_qs(body_text) # This will be empty if there is no body

        # Convert the query keys and values from bytes to strings
        query = {}
        for key in query_raw.keys():
            new_key = key
            if isinstance(key, bytes):
                new_key = key.decode('utf-8')
            query[new_key] = []
            for item in query_raw[key]:
                if isinstance(item, bytes):
                    query[new_key].append(item.decode('utf-8'))
                else:
                    query[new_key].append(item)

        return query

    ###########################################
    # RESPONSE HANDLERS
    #   Each function should respond to a particular request and return
    #   a byte seqence to return. (Each one should also call respond
    #   or start_response at some point)
    #
    #   Each handler must take in a dictionary of keyword arguments.
    #   They will be called with the following fields in the arguments,
    #   but not every handler has to use them:
    #
    #       'user':     An instance of authentication.User representing
    #                   the logged in user. For any handler except
    #                   the ones in login_exempt_handlers,
    #                   this is gaurenteed to not be None.
    ############################################

    def handle_root(**kwargs):
        """
        Return the home page for the logged-in user
        """
        page = home_page.build_home_page(kwargs['user'])
        respond()
        return page_builder.soup_to_bytes(page)

    
    def handle_login(**kwargs):
        """
        'login' can do one of two things depending on if a request
        body is included or not.

        If there is a body:
        The body will be read as HTML form data with
        a 'username' and 'password' field. These values will be used
        to authenticate the user and, if successful, the response
        will set cookies for the user and redirect them to the home page.
        If unsuccessful, the login page will be returned.

        If there is no body:
        The standard login page will be returned.
        If the body exists but does not contain the username
        or password parameters, it will be treated as if there was no body
        """

        query = dict_from_POST()
        if 'username' in query and 'password' in query:
            username = query['username'][0]
            password = query['password'][0]
            user = authentication.authenticate(username,password)

            # If the user was authenticated, redirect to the home page
            if user is not None:
                cookies = [('Set-Cookie',c) for c in authentication.create_cookies(user)]
                start_response('303 See Other',[('Location','/')]+cookies)
                return "REDIRECT".encode('utf-8')
            # If the user was not authenticated, send back the login page
            else:
                cookies = [('Set-Cookie', c) for c in authentication.clear_cookies()]
                respond(additional_headers = cookies)
                page = page_builder.build_login_page(message="The provided username or password is incorrect!")
                return page_builder.soup_to_bytes(page)

        # If there is no body (or username and password are otherwise not present)
        # then return the login page
        else:
            cookies = [('Set-Cookie', c) for c in authentication.clear_cookies()]
            respond(additional_headers = cookies)
            page = page_builder.build_login_page()
            return page_builder.soup_to_bytes(page)

    def handle_cfr(**kwargs):
        page = page_builder.build_page_from_file("cfr.html")
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_salary_saving(**kwargs):
        page = page_builder.build_page_from_file("salary_saving.html")
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_previous_semesters(**kwargs):
        page = page_builder.build_page_from_file("previous_semesters.html")
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_revisions(**kwargs):
        page = page_builder.build_page_from_file("revisions.html")
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_add_dummy(**kwargs):
        text = environ['wsgi.input'].read()
        dummy.insert_dummy_data(text)
        respond(mime = "text/plain")
        return "OK".encode('utf-8')

    # For 'echo' send the request body back as plain text
    def handle_echo(**kwargs):
        respond(mime = "text/plain; charset=utf-8")
        text = environ['wsgi.input'].read()
        if isinstance(text, str):
            return text.encode('utf-8')
        else:
            return text

    # For 'error' throw an error to test the the error-catching system.
    def handle_error(**kwargs):
        raise RuntimeError(
            "This was supposed to happen because you selected 'error'"
        )


    #For 'create_cfr' create a new cfr for a department
    def handle_create_cfr():
        if 'QUERY_STRING' in environ:
            query = parse_qs(environ['QUERY_STRING'])
            if 'dept' in query and 'sem' in query and 'year' in query and 'sub' in query:
                dept = query['dept'][0]
                sem = query['sem'][0]
                year = query['year'][0]
                sub = query['sub'][0]
                rows_inserted = request.create_cfr(dept, sem, year, sub)
                respond(mime = 'text/plain')
                return f"{rows_inserted} CFR(s) created.".encode('utf-8')


    #For 'add_course' add a course to a cfr
    def handle_add_course():
        data = environ['wsgi.input'].read()
        rows_inserted = request.add_course(data)
        respond(mime = 'text/plain')
        return f"{rows_inserted} course(s) inserted.".encode('utf-8')

    #For 'add_sal_savings' add salary savings to a cfr
    def handle_add_sal_savings():
        data = environ['wsgi.input'].read()
        rows_inserted = request.add_sal_savings(data)
        respond(mime = 'text/plain')
        return f"{rows_inserted} salary savings inserted.".encode('utf-8')

    # Register handlers into a dictionary
    def handle_new_user(**kwargs):
        if kwargs['user'].role != authentication.UserRole.ADMIN:
            raise RuntimeError("Only admins can do this!")
        rows_inserted = create_user.create_user(dict_from_POST())
        respond(mime = 'text/plain')
        return f"{rows_inserted} user(s) inserted.".encode('utf-8')

    # Register handlers into a dictionary.
    # The login-exempt handlers can be called
    # without the user needing to be logged in
    login_exempt_handlers = {
        'login':    handle_login,
        'echo':     handle_echo,
        'error':    handle_error
    }
    # These handlers require the user to be logged in.
    # Attempting to access them without being logged in
    # will cause a redirect to the login page.
    handlers = {
        '/':                    handle_root,
        'cfr':                  handle_cfr,
        'salary_saving':        handle_salary_saving,
        'previous_semesters':   handle_previous_semesters,
        'revisions':            handle_revisions,
        'echo':                 handle_echo,
        'error':                handle_error,
        'create_cfr':           handle_create_cfr,
        'add_course':           handle_add_course,
        'add_sal_savings':      handle_add_sal_savings,
        'new_user':             handle_new_user,
        'add_dummy':            handle_add_dummy
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

        # Check if the request is in login_exempt_handlers and call
        # it if it is. Otherwise, log in
        if top in login_exempt_handlers:
            yield login_exempt_handlers[top]()
            return

        if top in handlers:
            # Attempt to log the user in using the cookies from their browser.
            # If unsuccessful, redirect to the login page
            user = None
            if 'HTTP_COOKIE' in environ:
                user = authentication.authenticate_from_cookie(environ['HTTP_COOKIE'])
            if user is None:
                start_response('303 See Other',[('Location','/login')])
                yield "REDIRECT".encode('utf-8')
                return

            yield handlers[top](user = user)
            return

        # If the top part of the path was not recognized, send back
        # a 404 page.
        respond(status="404 Not Found")
        error_page = page_builder.build_page_from_file("404.html", includeNavbar=False)
        yield page_builder.soup_to_bytes(error_page)

    except Exception as err:
        respond(status="500 Internal Server Error")
        error_page = page_builder.build_500_error_page(err)
        yield page_builder.soup_to_bytes(error_page)
