#!/usr/bin/bash

set -e

TEST=$TRAVIS_BUILD_DIR/travis/test_response_code.sh
DATADIR=$TRAVIS_BUILD_DIR/testdata

FORM=application/x-www-form-urlencoded
JSON=text/json

# Basic tests without logging in
bash $TEST / 303
bash $TEST /nope 404
bash $TEST /login 200

# Login as admin, change password, then log in again
bash $TEST /login 303 $DATADIR/admin_login.data $FORM
bash $TEST /edit_user 303 $DATADIR/change_admin_password.data $FORM
bash $TEST /login 303 $DATADIR/admin_new_login.data $FORM
grep admin .curl_cookies

# Create user accounts (2 submitters and an approver)
bash $TEST /add_user 303 $DATADIR/create_submit1.data $FORM
bash $TEST /add_user 303 $DATADIR/create_submit2.data $FORM
bash $TEST /add_user 303 $DATADIR/create_approve.data $FORM

# Add a new semester and make it active
bash $TEST /add_semester 303 $DATADIR/add_semester.data $FORM
bash $TEST /change_semester 303 $DATADIR/change_semester.data $FORM

set +e