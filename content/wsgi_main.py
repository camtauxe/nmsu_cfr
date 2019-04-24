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
from utils import cfrenv
from utils import users
from utils import semesters
from utils import request
from utils import errors

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

    ###########################################
    # LOGIN-EXEMPT HANDLERS
    #   These can be called with the user being logged in
    ###########################################
    
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

    ###########################################
    # PAGE HANDLERS
    #   These handlers all return web pages
    ###########################################

    def handle_root(**kwargs):
        """
        Return the home page for the logged-in user
        """
        page = page_builder.build_home_page(kwargs['user'])
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_cfr(**kwargs):
        """
        Return the course funding request submission page
        """
        if kwargs['user'].role == authentication.UserRole.ADMIN:
            raise RuntimeError("Only submitters or approvers can do this!")
        page = page_builder.build_cfr_page(kwargs['user'])
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_salary_saving(**kwargs):
        """
        Return the salary savings submission page.
        If the user is an approver or admin,
        they can also supply a 'dept' value in the query string.
        """
        dept = None
        if 'QUERY_STRING' in environ:
            query = parse_qs(environ['QUERY_STRING'])
            if 'dept' in query:
                dept= query['dept'][0]

        page = page_builder.build_savings_page(kwargs['user'], dept_override=dept)
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_revisions(**kwargs):
        """
        Return the revisions page. If the user is an approver or admin,
        they can also supply a 'dept' value in the query string to view
        the revisions of a particular department. Otherwise, the page
        will only have the revisions for the user's department
        """
        dept = None
        if 'QUERY_STRING' in environ:
            query = parse_qs(environ['QUERY_STRING'])
            if 'dept' in query:
                dept= query['dept'][0]
        
        page = page_builder.build_revisions_page(kwargs['user'], dept_override=dept)
        respond()
        return page_builder.soup_to_bytes(page)

    def handle_previous_semesters(**kwargs):
        """
        Return the previous semesters page. If the user is an approver or admin,
        they can also supply a 'dept' value in the query string to view
        the history of a particular department. Otherwise, the page
        will only have the history for the user's department
        """
        dept = None
        if 'QUERY_STRING' in environ:
            query = parse_qs(environ['QUERY_STRING'])
            if 'dept' in query:
                dept= query['dept'][0]

        page = page_builder.build_previous_semesters_page(kwargs['user'], dept_override=dept)
        respond()
        return page_builder.soup_to_bytes(page)

    ###########################################
    # POST HANDLERS
    #   These are responses to POST requests
    ###########################################

    def handle_cfr_from_courses(**kwargs):
        """
        Handle POST request to create a new cfr from a list
        of courses specified in JSON in the request body.
        """
        if kwargs['user'].role != authentication.UserRole.SUBMITTER:
            if kwargs['user'].role != authentication.UserRole.APPROVER:
                raise RuntimeError("Only submitters can do this!")
        body_text = environ['wsgi.input'].read()
        data = json.loads(body_text)
        courses_inserted = request.new_cfr_from_courses(kwargs['user'], data)
        respond(mime = 'text/plain')
        return f"{courses_inserted}".encode('utf-8')

    def handle_cfr_from_sal_savings(**kwargs):
        """
        Handle POST request to create a new cfr from a list
        of salary savings specified in JSON in the request body.
        """
        if kwargs ['user'].role != authentication.UserRole.SUBMITTER:
            raise RuntimeError("Only submitters can do this!")
        body_text = environ['wsgi.input'].read()
        data = json.loads(body_text)
        savings_inserted = request.new_cfr_from_sal_savings(kwargs['user'], data)
        respond(mime = 'text/plain')
        return f"{savings_inserted}".encode('utf-8')

    def handle_approve_courses(**kwargs):
        """
        Handle POST request to approve courses from a list 
        specified in JSON in the request body.
        """
        if kwargs ['user'].role != authentication.UserRole.APPROVER:
            raise RuntimeError("Only approvers can do this!")
        body_text = environ['wsgi.input'].read()
        data = json.loads(body_text)
        courses_approved = request.approve_courses(kwargs['user'], data)
        respond(mime = 'text/plain')
        return f"{courses_approved}".encode('utf-8')

    def handle_add_commitments(**kwargs):
        """
        Handle POST request to add dean commitments to cfrs specified
        in JSON in the request body
        """
        if kwargs ['user'].role != authentication.UserRole.APPROVER:
            raise RuntimeError("Only approvers can do this!")
        body_text = environ['wsgi.input'].read()
        data = json.loads(body_text)
        request.commit_cfr(data)
        respond(mime = 'text/plain')
        return "OK".encode('utf-8')

    ###########################################
    # ADMIN ACTIONS
    ###########################################

    def handle_edit_user(**kwargs):
        """
        Handle POST request to edit or delete a user using form
        data in the request body. If successful, redirects to the
        home page.
        """
        if kwargs['user'].role != authentication.UserRole.ADMIN:
            raise RuntimeError("Only admins can do this!")
        users.edit_user(dict_from_POST(), kwargs['user'])
        start_response('303 See Other',[('Location','/')])
        return "OK".encode('utf-8')

    def handle_add_user(**kwargs):
        """
        Handle POST request to add a user using form
        data in the request body. If successful, redirects to the
        home page.
        """
        if kwargs['user'].role != authentication.UserRole.ADMIN:
            raise RuntimeError("Only admins can do this!")
        users.add_user(dict_from_POST())
        start_response('303 See Other',[('Location','/')])
        return "OK".encode('utf-8')

    def handle_change_semester(**kwargs):
        """
        Handle POST request to change the active semester using form
        data in the request body. If successful, redirects to the
        home page.
        """
        if kwargs['user'].role != authentication.UserRole.ADMIN:
            raise RuntimeError("Only admins can do this!")
        semesters.change_semester(dict_from_POST())
        start_response('303 See Other',[('Location','/')])
        return "OK".encode('utf-8')

    def handle_add_semester(**kwargs):
        """
        Handle POST request to add a semester using form
        data in the request body. If successful, redirects to the
        home page.
        """
        if kwargs['user'].role != authentication.UserRole.ADMIN:
            raise RuntimeError("Only admins can do this!")
        semesters.add_semester(dict_from_POST())
        start_response('303 See Other',[('Location','/')])
        return "OK".encode('utf-8')

    # Register handlers into a dictionary.
    # The login-exempt handlers can be called
    # without the user needing to be logged in
    login_exempt_handlers = {
        'login':    handle_login
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
        'add_course':           handle_cfr_from_courses,
        'add_sal_savings':      handle_cfr_from_sal_savings,
        'approve_courses' :     handle_approve_courses,
        'add_commitments':      handle_add_commitments,
        'add_user':             handle_add_user,
        'edit_user':            handle_edit_user,
        'change_semester':      handle_change_semester,
        'add_semester':         handle_add_semester,
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

    except errors.Error400 as err400:
        respond(status="400 Bad Request", mime="text/plain")
        yield str(err400).encode('utf-8')
    except Exception as err:
        respond(status="500 Internal Server Error")
        error_page = page_builder.build_500_error_page(err)
        yield page_builder.soup_to_bytes(error_page)
