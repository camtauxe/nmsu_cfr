"""
Maintains a set of variables for the CFR server's environment.

These variables are gotten either from the WSGI environ or the OS
environ and stored in a dictionary here. This module should be the
authortative source on the listed variables and other modules should
get their values from here rather than the WSGI or OS environ.

init_environ() MUST be called with the WSGI environ as an argument
to initialize the values in here. After initialization, every value
is gaurenteed to exist but may have a value of None. The initialized
values will look first to the OS environ for variables and use
the WSGI environ if a variable is not defined there. If a variable
is not defined in either, it will have a value of None.

Required:
    DB_HOST         The hostname used when connecting to the database
    DB_USER         MySQL username when connecting to the database
    DB_PASS         MySQL password when connecting to the database
    DB_DATABASE     The name of the MySQL database to connect to

Optional:
    DEBUG           Enable showing additonal debug information if set
                    to 'yes.' Does nothing if set to anything else
                    or nonexistant
"""

import os

environ = {}

def _init_var(varname: str, wsgi_environ: dict):
    environ[varname] = os.getenv(varname)
    if environ[varname] is None and varname in wsgi_environ:
        environ[varname] = wsgi_environ[varname]

def init_environ(wsgi_environ: dict):
    _init_var('DB_HOST',        wsgi_environ)
    _init_var('DB_USER',        wsgi_environ)
    _init_var('DB_PASS',        wsgi_environ)
    _init_var('DB_DATABASE',    wsgi_environ)

    _init_var('DEBUG',          wsgi_environ)

def getenv(varname):
    if varname in environ:
        return environ[varname]
    else:
        return None