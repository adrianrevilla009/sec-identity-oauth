# token-exchange

Keycloak 26.2.5 in Docker Compose with an `orders` realm in `realm.json` (clients `gateway` and `orders-api`) and `verify.sh`, which performs an RFC 8693 exchange with curl.

## Goal

Show a gateway swapping the user's token for one whose audience is a downstream API, using Keycloak's standard token exchange.

## Run it

```bash
docker compose up -d        # Keycloak on :8080 (wait about 30 s)
./verify.sh
docker compose down -v      # destroy
```

Expected: `exchanged token: sub kept for alice aud: ['orders-api', ...]`, `unknown audience rejected (400)` and `ok`. Lab-only credentials (`lab-secret`, alice/alice-pass); no cost.

Not run end to end: the compose file, realm and script were not executed against a running Keycloak, so the expected output comes from the script's `print` and `echo` lines.

## What it proves

- `verify.sh` logs alice in to `gateway`, exchanges her token with `audience=orders-api`, and asserts the new token lists `orders-api` in `aud` and still names alice.
- Exchange is opt-in per client: `gateway` has `standard.token.exchange.enabled` set in `realm.json`.
- Asking for an audience that does not exist (`does-not-exist`) is expected to return HTTP 400.

## Trade-offs

- It uses the standard internal-to-internal exchange from Keycloak 26.2; impersonation and external-token exchange are not covered.
- The password grant on `gateway` only keeps the script short; a real gateway receives the token from a login flow.
- The audience must be a known client, and downscoping rules are specific to Keycloak.

## When not to use it

- When the downstream API can accept the incoming token because its audience already fits.
- For service-to-service calls with no user; use client credentials.
