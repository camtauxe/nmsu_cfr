"""
Utilities for calling wsgi_main directly so that a debugger can be
attached or tests can be performed
"""
import sys
import os
import re
from io import StringIO
import http.cookies as cookies

# Import wsgi_main from the content directory
sys.path.append(os.path.join(os.path.dirname(__file__),'content'))
import wsgi_main #pylint: disable=import-error

COOKIE_FILE = os.path.join(os.path.dirname(__file__),'.debug_cookies')
cookie_regex = re.compile(r'Set-Cookie:\s+(?P<key>\w+)\s*=\s*"?(?P<value>\w*)"?\s*;?')
cookie = cookies.SimpleCookie()

def load_cookie():
    """
    Load the cookie from the cookie file if it exists.
    If the file does not exist, this does nothing
    """
    global cookie
    cookie = cookies.SimpleCookie()
    try:
        with open(COOKIE_FILE,'r') as f:
            for line in f:
                match = cookie_regex.match(line)
                if match is None:
                    print("Error parsing cookie file!")
                    print(line)
                else:
                    cookie[match.group('key')] = match.group('value')
        print("Loaded cookie!")
        print(cookie.output())

    except IOError as e:
        print("Error loading cookie!")
        print(e)

def save_cookie():
    """
    Save the cookie to the cookie file. If the file does not exist,
    this will create it
    """
    global cookie
    try:
        with open(COOKIE_FILE,'w') as f:
            f.write(cookie.output())
    except IOError as e:
        print("Error saving cookie!")
        print(e)


class ResponseSummary():
    """
    Represents the information received in a response from the server
    as a string for its status code, a list of tuples for its headers
    and a string for its body.
    """
    def __init__(self, status: str, headers: list, body: str):
        self.status: str    = status
        self.headers: list  = headers
        self.body: str      = body

        self.is_ok: bool = (self.status.lower == '200 ok')

    def __str__(self):
        string = "Status:\t"+self.status+"\n"
        for header in self.headers:
            string += (header[0]+":\t"+header[1]+"\n")
        string += "\n"
        string += self.body
        return string

def simulate_request(url, body_file = None) -> ResponseSummary:
    """
    Send the given url to the wsgi application and return its response
    in a ResponseSummary
    Optionally takes body_file which is the name of a file to be used
    as the body of the sent request
    """
    global cookie

    response_started = False
    status = None
    headers = []
    output_begun = False

    # This is the 'start_response' callable that is passed to application
    def handle_response(_status, _headers):
        nonlocal response_started, status, headers, output_begun
        if (output_begun):
            raise RuntimeError("start_response was called after some of the response body was already sent!")
        response_started = True
        status = _status
        headers = _headers

    # Prepare the environ
    environ = dict(os.environ.items())
    if body_file is not None:
        try:
            environ['wsgi.input']       = open(body_file)
        except (IOError):
            print("Could not open {}!!".format(body_file))
            environ['wsgi.input']       = StringIO("")
    else:
        environ['wsgi.input']       = StringIO("")
    environ['wsgi.errors']          = sys.stderr
    environ['wsgi.version']         = (1, 0)
    environ['wsgi.multithread']     = False
    environ['wsgi.multiprocess']    = True
    environ['wsgi.run_once']        = True
    environ['wsgi.url_scheme']      = 'http'

    environ['PATH_INFO']        = url
    environ['REQUEST_METHOD']   = 'GET'
    environ['SCRIPT_NAME']      = wsgi_main.__file__
    query_index = url.find('?')
    if query_index != -1:
        environ['QUERY_STRING']     = url[query_index+1:]
    environ['SERVER_NAME']      = 'localhost'
    environ['SERVER_PORT']      = 80
    environ['SERVER_PROTOCOL']  = 'HTTP/1.0'

    environ['HTTP_COOKIE'] = cookie.output(attrs = [], header="", sep="; ")

    # Call application and assemble its response (which comes as bytes)
    # into a string
    response_bytes = bytes()
    for next_response in wsgi_main.application(environ, handle_response):
        if not response_started:
            raise RuntimeError("Some of the response body was sent before start_response was called!")
        if not output_begun:
            output_begun = True
        response_bytes += next_response

    body = response_bytes.decode('utf-8')

    # Check headers for Set-Cookie headers
    cookies_found = False
    for header in headers:
        if header[0] == 'Set-Cookie':
            match = cookie_regex.match(header[0]+": "+header[1])
            if match is not None:
                if not cookies_found:
                    cookies_found = True
                    print("Found cookies!")
                cookie[match.group('key')] = match.group('value')
    if cookies_found:
        save_cookie()
        print(cookie)

    return ResponseSummary(status, headers, body)

def interactive_mode():
    """
    An interactive mode for operating the debugger.
    
    Prompts the user to enter URLs to try sending the server
    and reports back with their status's and allows the user
    to view the headers or body. Repeats until the user
    chooses to exit
    """
    last_response: ResponseSummary = None
    should_exit = False

    load_cookie()

    # Send a request wrapped in a try/catch to catch any exceptions
    # that the server code failed to catch itself
    def request(url, body_file = None):
        try:
            return simulate_request(url, body_file)
        except Exception as e:
            print("The server code threw an exception and didn't catch it!")
            print(e)
            return ResponseSummary('500 Internal Server Error', [], 'ERROR')

    # If an argument was provided on the command line, forgo
    # the introduction and immediately try sending the argument
    # as if the user had entered that as a URL to try
    if len(sys.argv) > 1:
        last_response = request(sys.argv[1])
    else:
        print("="*80)
        print("{:^80}".format("Welcome to the interactive debugger!"))
        print("="*80)
        print("")
        print("Enter a URL:")
        print("(Enter a filename after the URL to use a file for the request body)")
        answer = input("> ").split()
        if len(answer) < 2:
            last_response = request(answer[0])
        else:
            last_response = request(answer[0], answer[1])

    # Main loop
    while not should_exit:
        print("\n")
        print("Status: "+last_response.status)
        print(
            "Please enter a URL or select the number for an option below:\n"
            "1) See response body\n"
            "2) See response headers\n"
            "3) Exit"
        )
        answer = input("> ").split()
        choice = answer[0]

        if choice == '1':
            print("="*80)
            print(last_response.body)
            print("="*80)
            continue

        if choice == '2':
            for header in last_response.headers:
                print(header[0]+":\t"+header[1])
            print("")
            continue

        if choice == '3':
            should_exit = True
            continue

        # If the user's answer doesn't match any choice, 
        # interpret it as a URL (with possibly a filename
        # for the request body)
        if len(answer) < 2:
            last_response = request(answer[0])
        else:
            last_response = request(answer[0], answer[1])

# Run in interactive mode if the file was run on the command line
if __name__ == "__main__":
    interactive_mode()