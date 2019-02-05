#!/usr/bin/python3
import os
import traceback
import mysql.connector
from utils import page_builder as builder
from utils import sql_connection as db

def application(environ, start_response):
    try:
        test_soup = builder.soup_from_file("test.html")
        dynamic_text = builder.soup_from_text("This text is <b>𝒹𝓎𝓃𝒶𝓂𝒾𝒸</b>")
        test_soup.find(id='dynamictext').append(dynamic_text)

        db.connect()
        cursor = db.new_cursor()
        cursor.execute("SHOW TABLES")
        tables = [d[0] for d in cursor.fetchall()]

        ul = builder.soup_from_text("<ul></ul>")
        for table in tables:
            ul.append(builder.soup_from_text("<li>"+table+"</li>"))
        test_soup.find(id='tablelist').append(ul)

        start_response('200 OK', [('Content-Type', 'text/html; charset=utf-8')])
        yield builder.soup_to_bytes(test_soup)

    except Exception as err:
        start_response(
            '500 Internal Server Error',
            [('Content-Type', 'text/html; charset=utf-8')]
        )
        error_soup = builder.soup_from_file("500.html")
        error_message = builder.soup_from_text(create_error_message(err))
        error_soup.find(id="message").append(error_message)
        yield builder.soup_to_bytes(error_soup)
        exit(1)

def create_error_message(error):
    if os.getenv('MODE') != 'debug':
        message = (
            "<p>Something went wrong :(<br>"+
            "Error information below:<br>"+
            str(type(error))+": "+str(error)+"<br>"+
            traceback.format_exc().replace('\n','<br>')+"</p>"
        )

        if isinstance(error, mysql.connector.Error):
            message += (
                "<p>MySQL Error!<br>"+
                "Pyton MySQL Error code: "+str(error.errno)+"<br>"+
                error.msg+"</p>"
            )
    else:
        message = (
            "<p>Something went wrong :(<br>"+
            "Please contact a system administrator.</p>"
        )
    return message