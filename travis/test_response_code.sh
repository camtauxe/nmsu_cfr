#!/usr/bin/bash

# A shell script that uses curl to send a request to localhost
# and test that for a certain response code.
#
# Exits with 0 if the response code matches, otherwise exits with 1.
# An exit code of 2 means there was a mistake with the supplied arguments.
#
# Usage:
#   sh test_response_code.sh URL RESPONSE_CODE [REQUEST_BODY_FILE CONTENT_TYPE]
#   sh test_response_code.sh /login 200
#   (This will send a request to localhost/login and check that it returns
#   with status 200)

if [ $# -lt 2 ]; then
    echo "Usage: test_response_code.sh URL RESPONSE_CODE [REQUEST_BODY_FILE]"
    exit 2
fi

if [ "$4" != "" ]; then
    echo "Testing request to localhost$1 (expecting $2, data from $3 as $4) ..." 
    CODE=$(curl -s -o /dev/null -w '%{http_code}\n' --cookie-jar .curl_cookies --cookie .curl_cookies -H "Content-Type: $4" --data-binary @$3 localhost$1)
    if [[ $CODE == "$2" ]]; then
        echo "OK!"
        exit 0
    else
        echo "Oh no! (got $CODE)"
        exit 1
    fi
else
    echo "Testing request to localhost$1 (expecting $2) ..."
    CODE=$(curl -s -o /dev/null -w '%{http_code}\n' --cookie-jar .curl_cookies --cookie .curl_cookies localhost$1)
    if [[ $CODE == "$2" ]]; then
        echo "OK!"
        exit 0
    else
        echo "Oh no! (got $CODE)"
        exit 1
    fi
fi