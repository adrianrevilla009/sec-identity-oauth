# client-credentials

Keycloak 26.2.5 in Docker Compose with an `orders` realm in `realm.json` and `verify.sh`, which requests tokens for the `billing-job` client with curl.

## Goal

Get a machine-to-machine access token with the client credentials grant and see how default and optional scopes behave.

## Run it

```bash
docker compose up -d        # Keycloak on :8080 (wait about 30 s)
./verify.sh
docker compose down -v      # destroy
```

Expected: `default scope: ...` with `orders.read`, `optional scope on request: ...` with `orders.write`, `wrong secret rejected (401)` and `ok`. The client secret `lab-secret` is for this lab only; there is no cost.

Not run end to end: the compose file, realm and script were not executed against a running Keycloak, so the expected output comes from the script's `echo` lines.

## What it proves

- `billing-job` is a confidential client with a service account and no standard flow, so no user takes part.
- The default token has `orders.read` and not `orders.write`; adding `-d scope=orders.write` puts the optional scope into the token.
- The service-account token's `preferred_username` starts with `service-account`, and a wrong secret returns 401.

## Trade-offs

- The client secret is a long-lived shared credential; only the token is short-lived.
- Optional scopes keep least privilege, but the caller has to know to ask for them.
- The subject is the service-account user, not a business identity.

## When not to use it

- When a user is on the other side of the call; use authorization code with PKCE.
- When workloads can use signed client assertions or mTLS instead of a shared secret.
