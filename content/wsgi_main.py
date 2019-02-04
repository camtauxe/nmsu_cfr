#!/usr/bin/python3

from utils import souputils

def application(environ, start_response):
    start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
    
    test_soup = souputils.soup_from_file("test.html")
    dynamic_text = souputils.soup_from_text("This text is <b>𝒹𝓎𝓃𝒶𝓂𝒾𝒸</b>")
    test_soup.find(id='dynamictext').append(dynamic_text)

    yield souputils.soup_to_bytes(test_soup)