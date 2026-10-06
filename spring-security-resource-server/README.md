# spring-security-resource-server

A Spring Boot 3.3.5 (Java 21) Orders API in `App.java` that validates JWT bearer tokens, plus `OrdersTest.java` with four MockMvc tests.

## Goal

Show how a resource server turns token scopes into authorities and enforces them with both URL rules and method security.

## Run it

```bash
mvn -B test                 # no Docker or identity provider needed
mvn spring-boot:run         # optional: fetches keys from the keycloak-oidc-pkce realm on :8080
```

Expected: `Tests run: 4, Failures: 0, Errors: 0` and `BUILD SUCCESS` (this was run). `spring-boot:run` was not started here; it needs the `keycloak-oidc-pkce` realm running, which was not run end to end.

## What it proves

- With no token, `GET /orders` returns 401; with a token that lacks `SCOPE_orders.read` it returns 403.
- `SCOPE_orders.read` is enough to list orders; `POST /orders` needs `SCOPE_orders.write` through `@PreAuthorize`.
- Signature validation is configured by `jwk-set-uri` alone in `application.yml`, and the tests use the `jwt()` post-processor, so they check authorization rules, not token parsing.

## Trade-offs

- Only the JWKS URI is set, so the `iss` and `aud` claims are not checked; add an issuer and an audience validator for real use.
- JWTs stay valid until they expire; opaque tokens, introspection and revocation are not covered.
- The tests never contact Keycloak; pair them with `keycloak-oidc-pkce` to get real tokens.

## When not to use it

- When tokens are opaque or you need instant revocation; use introspection.
- When a gateway already validates tokens and the services simply trust it.
