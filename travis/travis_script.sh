#!/usr/bin/bash

TEST=$TRAVIS_BUILD_DIR/travis/test_response_code.sh
bash $TEST / 303
bash $TEST /nope 404
bash $TEST /error 500
bash $TEST /login 200

bash $TEST /login 303 $TRAVIS_BUILD_DIR/travis/submitter1_login.data application/x-www-form-urlencoded
bash $TEST /cfr 200
bash $TEST /login 200