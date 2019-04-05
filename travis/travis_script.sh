#!/usr/bin/bash

set -e

TEST=$TRAVIS_BUILD_DIR/travis/test_response_code.sh

# Basic tests without logging in
bash $TEST / 303
bash $TEST /nope 404
bash $TEST /error 500
bash $TEST /login 200

# Login as submitter1, try visiting /cfr, then log out
bash $TEST /login 303 $TRAVIS_BUILD_DIR/travis/submitter1_login.data application/x-www-form-urlencoded
bash $TEST /cfr 200
bash $TEST /login 200

# Login as admin and try to create a user
bash $TEST /login 303 $TRAVIS_BUILD_DIR/travis/admin_login.data application/x-www-form-urlencoded
bash $TEST /new_user 200 $TRAVIS_BUILD_DIR/travis/new_user.data application/x-www-form-urlencoded

# Login as the newly-created user
bash $TEST /login 303 $TRAVIS_BUILD_DIR/travis/new_user_login.data application/x-www-form-urlencoded
# Test that login worked by checking cookies
grep newguy .curl_cookies

set +e