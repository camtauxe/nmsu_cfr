#!/usr/bin/python3

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/json')])
    yield str(environ).encode('UTF-8')