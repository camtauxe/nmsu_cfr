import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__),'content'))
import wsgi_main #pylint: disable=import-error

class ResponseSummary():
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

def simulate_request(url):
    response_started = False
    status = None
    headers = []
    output_begun = False

    def handle_response(_status, _headers):
        nonlocal response_started, status, headers, output_begun
        if (output_begun):
            raise RuntimeError("start_response was called after some of the response body was already sent!")
        response_started = True
        status = _status
        headers = _headers

    environ = {
        'PATH_INFO': url
    }

    response_bytes = bytes()
    for response in wsgi_main.application(environ, handle_response):
        if not response_started:
            raise RuntimeError("Some of the response body was sent before start_response was called!")
        if not output_begun:
            output_begun = True
        response_bytes += response

    body = response_bytes.decode('utf-8')
    return ResponseSummary(status, headers, body)

if __name__ == "__main__":
    if len(sys.argv) > 1:
        url = sys.argv[1]
        print(simulate_request(url))