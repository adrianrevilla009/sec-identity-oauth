#!/usr/bin/env bash
# Machine-to-machine token via client_credentials, then proof of what the token does and does not carry.
set -euo pipefail
TOKEN_URL=http://localhost:8080/realms/orders/protocol/openid-connect/token

token() {  # $@ = extra curl -d args
  curl -sf -u billing-job:lab-secret -d grant_type=client_credentials "$@" "$TOKEN_URL"
}
claims() {  # decode the JWT payload
  python3 -c 'import sys,json,base64; b=json.load(sys.stdin)["access_token"].split(".")[1]; print(json.dumps(json.loads(base64.urlsafe_b64decode(b+"="*(-len(b)%4))))) '
}

default=$(token | claims)
echo "$default" | python3 -c 'import sys,json; c=json.load(sys.stdin); assert "orders.read" in c["scope"] and "orders.write" not in c["scope"], c; assert c["preferred_username"].startswith("service-account"), c; print("default scope:", c["scope"])'

elevated=$(token -d scope=orders.write | claims)
echo "$elevated" | python3 -c 'import sys,json; c=json.load(sys.stdin); assert "orders.write" in c["scope"], c; print("optional scope on request:", c["scope"])'

code=$(curl -s -o /dev/null -w '%{http_code}' -u billing-job:wrong -d grant_type=client_credentials "$TOKEN_URL")
[ "$code" = 401 ] || { echo "wrong secret should be 401, got $code"; exit 1; }
echo "wrong secret rejected (401)"
echo ok
