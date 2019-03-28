set -e

echo ""

mysql -u root -e "source sql/cfr-schema.sql; source sql/db-test-init.sql;"

cp travis/travis_cfr.env cfr.env
docker build -q -t nmsu_cfr:latest .
docker run -d --env-file cfr.env --name cfr -p 80:80 --network="host" nmsu_cfr:latest