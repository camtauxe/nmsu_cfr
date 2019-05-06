# Developer's Guide
If you are going to continue development on the system, please readthrough this guide for an overview of the system architecture,development tools and code. For more detail on parts of the system,please read the comments in the relevant files.

## Architecture

The system runs inside a Docker container that runs an Apache HTTP
server. The Apache server can serve static content from the [static](../content/static) directory, and uses Python for back-end code
for responding to POST requests and building dynamic content (using [wsgi_main.py](../content/wsgi_main.py) as the main entry point). Apache communicates with Python using WSGI (**W**eb **S**erver **G**ateway **I**nterface). For more information on WSIG, read its specification in [PEP 333](https://www.python.org/dev/peps/pep-0333/).

The docker image copies all of the contents of the [content](../content) directory into its own /srv directory and copies [apache_config.conf](../apache_config.conf) to configure a virtual host for Apache.

Using the provided docker-compose files provided, the running container will be bound to port 80, but you can change this if you use ```docker run``` directly or write your own docker-compose file.

## Using the Interactive Debugger

[debug.py](../debug.py) can be used to run the back-end code locally and can be attached to a debugger to inspect variables, insert breakpoints etc. If you are using VS Code (reccommended) then a debug profile has already been set up for you in [launch.json](../.vscode/launch.json). If you're using your own debugging setup, don't forget to import the environment variables from cfr.env (or another configuration).

When running the debugger, you will be prompted to enter a URL (relative to the server's root) to simulate a request for. You will be able to see the HTTP response code, body and headers that the server returned. If the server returns some "Set-Cookie" headers then the debugger will automatically save and remember them for future sessions. These cookies will be automatically sent with each new request.

When entering a URL, you can add the path to file (just put a space between it and the URL). The contents of this file will be sent as the body of the request. You can use this to test the server against different pieces of data. If you're looking for examples of data, check out the [testdata](../travis/testdata) that Travis CI uses.

## Travis CI

We include configuration for the continious integration system, Travis CI. The scripts and files used by Travis can be found in the [travis](../travis) directory. The script will set up and initialize a database, then build and run the docker container. For testing, it uses cURL to hit the server with various requests and check that the response code for each is what it expected.

## The Code

[wsgi_main.py](../content/wsgi_main.py) is the main entry point for the backend code. It contains the *application()* function that WSGI
will call. It performs the high-level functionality of the back-end,
i.e. parsing the incoming request, passing the buck to one of many "handler" functions, then returning the response. It makes use of the
[utils module](../content/utils) for most operations. Below is a description of each part of utils.

- [authentication.py](../content/utils/authentication.py) manages the authentication of users. It defines the *User* class which represents an authenticated user.

- [cfrenv.py](../content/utils/cfrenv.py) manages the environment variables normally defined in *cfr.env* If other modules need to access these variables, they should do so through this module.

- [component_builder.py](../content/utils/component_builder.py) builds individual HTML elements (such as tables, inputs and modals) to be inserted into pages. (Uses the BeautifulSoup library)

- [db_utils.py](../content/utils/db_utils.py) performs queries and other operations on the database. Most functions are designed to be "low-level" operations where, oftentimes, multiple of them will be used together as a part of one atomic transaction.

- [email_notification.py](../content/utils/email_notification.py) manages writing and sending email notifications to users.

- [errors.py](../content/utils/errors.py) defines custom exceptions.

- [page_builder.py](../content/utils/page_builder.py) constructs web pages in response to requests. Works closely with *component_builder.py*. (Uses the BeautifulSoup library).

- [request.py](../content/utils/request.py) defines functions for manipulating CFRs (Course Funding Requests) in the database. Makes heavy use of *db_utils.py*.

- [semesters.py](../content/utils/semesters.py) defines functions for manipulating semesters in the database. Makes heavy use of *db_utils.py*.

- [sql_connection.py](../content/utils/sql_connection.py) defines the *Transaction* context manager for connecting to the database.

- [users.py](../content/utils/users.py) defines functions for manipulating users in the database. Makes heavy use of *db_utils.py*