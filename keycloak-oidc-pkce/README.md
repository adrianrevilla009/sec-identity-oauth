# keycloak-oidc-pkce

Keycloak 26.2.5 in Docker Compose with an `orders` realm in `realm.json`, and `pkce.py`, a standard-library script that completes an authorization code flow with PKCE.

## Goal

Show an authorization code flow with PKCE (S256) for a public client, with the realm defined as code so nothing is configured by hand in the console.

## Run it

```bash
docker compose up -d        # Keycloak on :8080, realm imported on boot (wait about 30 s)
python3 pkce.py
docker compose down -v      # destroy
```

Expected: `wrong code_verifier rejected (400)` followed by `ok: token for alice scope: ...` including `orders.read`. Dev-only credentials: admin/admin for the console, alice/alice-pass for the user. Everything is local, so there is no cost.

Not run end to end: the compose file, realm and script were written against Keycloak's documented behaviour but not executed against a running container, so the expected output above comes from the script's `print` statements, not from a captured run.

## What it proves

- `orders-web` is a public client (no secret); the script first redeems a code with a random `code_verifier` and expects HTTP 400, then redeems it with the matching one.
- `pkce.py` acts as the browser: it loads the login form, posts alice's credentials, reads the code from the 302 `Location`, and checks that `state` comes back unchanged.
- The access token's `preferred_username` is `alice` and its `scope` contains `orders.read`; the realm, client, scope and user all come from `realm.json`.

## Trade-offs

- The script scrapes the login form with a regex, which can break with other Keycloak themes; a real app uses a redirect and a client library.
- `start-dev` uses an embedded database and plain HTTP (`sslRequired: none`).
- The realm import only runs when the realm does not exist, so edits to `realm.json` need `docker compose down -v`.

## When not to use it

- For production: you would need a real database, TLS, a fixed hostname and a managed realm pipeline.
- For a confidential server-side client the secret still matters; PKCE is added on top, not instead.
