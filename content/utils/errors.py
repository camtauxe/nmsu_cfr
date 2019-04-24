"""
Definitions for custom Exceptions

TODO: Right now, permission errors simply raise a generic RuntimeError
(which the server catches and returns a HTTP 500 error), but ideally, we
should have a custom exception for the appropriate response (403 Forbidden)
"""

class Error400(Exception):
    pass