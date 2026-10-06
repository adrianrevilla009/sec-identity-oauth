#!/usr/bin/env python3
"""Authorization code + PKCE (S256) against the local Keycloak, scripted end to end with the stdlib only.

Plays the browser: loads the login form, posts alice's credentials, catches the redirect that carries the
code (nothing listens on the redirect URI), then redeems the code with the code_verifier.
"""
import base64, hashlib, html, json, re, secrets, urllib.error, urllib.parse, urllib.request
from http.cookiejar import CookieJar

BASE = "http://localhost:8080/realms/orders/protocol/openid-connect"
CLIENT, REDIRECT = "orders-web", "http://localhost:8081/callback"


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, *a, **k):
        return None


opener = urllib.request.build_opener(NoRedirect, urllib.request.HTTPCookieProcessor(CookieJar()))


def b64(raw):
    return base64.urlsafe_b64encode(raw).rstrip(b"=").decode()


def redirect_params(call):
    """Run a request that must answer 302 and return the query params of its Location."""
    try:
        call()
    except urllib.error.HTTPError as e:
        assert e.code == 302, e.code
        return urllib.parse.parse_qs(urllib.parse.urlparse(e.headers["Location"]).query)
    raise AssertionError("expected a redirect")


def get_code(challenge, state):
    """Browser leg: the first call shows the login form, later calls ride on the SSO cookie."""
    query = urllib.parse.urlencode({
        "client_id": CLIENT, "redirect_uri": REDIRECT, "response_type": "code", "scope": "openid",
        "state": state, "code_challenge": challenge, "code_challenge_method": "S256"})
    url = f"{BASE}/auth?{query}"
    try:
        page = opener.open(url).read().decode()
    except urllib.error.HTTPError as e:  # already logged in
        return urllib.parse.parse_qs(urllib.parse.urlparse(e.headers["Location"]).query)["code"][0]
    action = html.unescape(re.search(r'action="([^"]+)"', page).group(1))
    form = urllib.parse.urlencode({"username": "alice", "password": "alice-pass"}).encode()
    params = redirect_params(lambda: opener.open(action, form))
    assert params["state"] == [state], "state mismatch"
    return params["code"][0]


def redeem(code, verifier):
    data = urllib.parse.urlencode({
        "grant_type": "authorization_code", "client_id": CLIENT, "redirect_uri": REDIRECT,
        "code": code, "code_verifier": verifier}).encode()
    return json.load(opener.open(f"{BASE}/token", data))


def main():
    verifier = b64(secrets.token_bytes(48))
    challenge = b64(hashlib.sha256(verifier.encode()).digest())

    try:
        redeem(get_code(challenge, "s1"), b64(secrets.token_bytes(48)))
        raise SystemExit("FAIL: wrong verifier was accepted")
    except urllib.error.HTTPError as e:
        assert e.code == 400, e.code
    print("wrong code_verifier rejected (400)")

    token = redeem(get_code(challenge, "s2"), verifier)
    body = token["access_token"].split(".")[1]
    claims = json.loads(base64.urlsafe_b64decode(body + "=" * (-len(body) % 4)))
    assert claims["preferred_username"] == "alice" and "orders.read" in claims["scope"], claims
    print("ok: token for", claims["preferred_username"], "scope:", claims["scope"])


if __name__ == "__main__":
    main()
