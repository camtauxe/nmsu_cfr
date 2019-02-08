"""
Utilities for calling wsgi_main directly so that a debugger can be
attached or tests can be performed
"""
import sys
import os

# Import wsgi_main from the content directory
sys.path.append(os.path.join(os.path.dirname(__file__),'content'))
import wsgi_main #pylint: disable=import-error

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

def simulate_request(url) -> ResponseSummary:
    """
    Send the given url to the wsgi application and return its response
    in a ResponseSummary
    """
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
    environ['wsgi.input']           = sys.stdin
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
        environ['QUERY_STRING']     = url[query_index:]
    environ['SERVER_NAME']      = 'localhost'
    environ['SERVER_PORT']      = 80
    environ['SERVER_PROTOCOL']  = 'HTTP/1.0'

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

    # Send a request wrapped in a try/catch to catch any exceptions
    # that the server code failed to catch itself
    def request(url):
        try:
            return simulate_request(url)
        except Exception as e:
            print("The server code threw an exception and didn't catch it!")
            print(e)
            return None

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

    # Main loop
    while not should_exit:
        if last_response is None:
            url = input("Enter a URL: ")
            last_response = request(url)
            continue

        print("Status: "+last_response.status)
        print(
            "Please enter a URL or select the number for an option below:\n"
            "1) See response body\n"
            "2) See response headers\n"
            "3) Exit"
        )
        choice = input("> ")

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

        last_response = request(choice)

# Run in interactive mode if the file was run on the command line
if __name__ == "__main__":
    interactive_mode()