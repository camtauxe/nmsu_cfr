#!/usr/bin/bash

set -e
set -x

mysql -u root -e "create database cfr; use cfr; source sql/cfr-schema.sql; source sql/db-test-init.sql;"

cp travis/travis_cfr.env cfr.env
docker build -q -t nmsu_cfr:latest .
docker run -d --env-file cfr.env --name cfr --network="host" nmsu_cfr:latest