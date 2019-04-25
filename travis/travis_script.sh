#!/usr/bin/bash

set -e

TEST=$TRAVIS_BUILD_DIR/travis/test_response_code.sh
DATADIR=$TRAVIS_BUILD_DIR/travis/testdata

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

# Log in as submit1 and test 4 main pages
bash $TEST /login 303 $DATADIR/submit1_login.data $FORM
grep submit1 .curl_cookies
bash $TEST /cfr 200
bash $TEST /salary_saving 200
bash $TEST /revisions 200
bash $TEST /previous_semesters 200

# Submit stuff
bash $TEST /add_course 200 $DATADIR/art_courses1.json $JSON
bash $TEST /add_sal_savings 200 $DATADIR/art_savings1.json $JSON
bash $TEST /add_course 200 $DATADIR/art_courses2.json $JSON

# Log in as submit2 and test 4 main pages
bash $TEST /login 303 $DATADIR/submit2_login.data $FORM
grep submit2 .curl_cookies
bash $TEST /cfr 200
bash $TEST /salary_saving 200
bash $TEST /revisions 200
bash $TEST /previous_semesters 200

# Submit stuff
bash $TEST /add_sal_savings 200 $DATADIR/history_savings1.json $JSON
bash $TEST /add_course 200 $DATADIR/history_courses1.json $JSON
bash $TEST /add_sal_savings 200 $DATADIR/history_savings2.json $JSON

# Log in as approve and test 4 main pages (wth queries)
bash $TEST /login 303 $DATADIR/approve_login.data $FORM
grep approve .curl_cookies
bash $TEST /cfr 200
bash $TEST /salary_saving 200
bash $TEST "/salary_saving?dept=art" 200
bash $TEST /revisions 200
bash $TEST "/revisions?dept=history" 200
bash $TEST /previous_semesters 200
bash $TEST "/previous_semesters?dept=art" 200

#Approve stuff
bash $TEST /approve_courses 200 $DATADIR/approve_courses.json $JSON
bash $TEST /add_commitments 200 $DATA_DIR/add_commitments.json $JSON

set +e