set -e

[[ $(curl -s -o /dev/null -w '%{http_code}' localhost) == 303 ]]
[[ $(curl -s -o /dev/null -w '%{http_code}' localhost/login) == 200 ]
# [[ $(curl -s -o /dev/null -w '%{http_code}' localhost/nope) == 404 ]]
# [[ $(curl -s -o /dev/null -w '%{http_code}' localhost/error) == 500 ]]