#!/usr/bin/bash

set -e
set -x

mysql -u root -e "SET PASSWORD FOR 'root'@'localhost' = PASSWORD('TR@V1S');"
mysql -u root -pTR@V1S -e "create database cfr; use cfr; source sql/cfr-schema.sql; source sql/db-test-init.sql;"

sleep 5

cp travis/travis_cfr.env cfr.env
docker build -q -t nmsu_cfr:latest .
docker run -d --env-file cfr.env --name cfr --network="host" nmsu_cfr:latest

sleep 5

set +x
set +e