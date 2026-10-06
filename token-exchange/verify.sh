#!/usr/bin/env bash
# The gateway holds alice's token (aud: gateway) and swaps it for one addressed to orders-api (RFC 8693).
set -euo pipefail
TOKEN_URL=http://localhost:8080/realms/orders/protocol/openid-connect/token

claims() {  # decode the JWT payload from a token response on stdin
  python3 -c 'import sys,json,base64; b=json.load(sys.stdin)["access_token"].split(".")[1]; print(json.dumps(json.loads(base64.urlsafe_b64decode(b+"="*(-len(b)%4)))))'
}

# 1. alice logs in to the gateway (password grant is enabled for this client only to keep the script short)
subject=$(curl -sf -u gateway:lab-secret -d grant_type=password -d username=alice -d password=alice-pass "$TOKEN_URL" \
  | python3 -c 'import sys,json; print(json.load(sys.stdin)["access_token"])')

# 2. the gateway exchanges it for a token whose audience is orders-api
exchanged=$(curl -sf -u gateway:lab-secret "$TOKEN_URL" \
  -d grant_type=urn:ietf:params:oauth:grant-type:token-exchange \
  -d subject_token="$subject" \
  -d subject_token_type=urn:ietf:params:oauth:token-type:access_token \
  -d requested_token_type=urn:ietf:params:oauth:token-type:access_token \
  -d audience=orders-api)

echo "$exchanged" | claims | python3 -c '
import sys, json
c = json.load(sys.stdin)
aud = c["aud"] if isinstance(c["aud"], list) else [c["aud"]]
assert "orders-api" in aud, c
assert c["preferred_username"] == "alice", c
print("exchanged token: sub kept for", c["preferred_username"], "aud:", aud)'

# 3. an unknown audience is refused
code=$(curl -s -o /dev/null -w '%{http_code}' -u gateway:lab-secret "$TOKEN_URL" \
  -d grant_type=urn:ietf:params:oauth:grant-type:token-exchange -d subject_token="$subject" \
  -d subject_token_type=urn:ietf:params:oauth:token-type:access_token -d audience=does-not-exist)
[ "$code" = 400 ] || { echo "unknown audience should be 400, got $code"; exit 1; }
echo "unknown audience rejected (400)"
echo ok
