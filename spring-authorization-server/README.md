# spring-authorization-server

A minimal Spring Authorization Server (Spring Boot 3.3.5, Java 21) whose only client is registered in `application.yml`, with `TokenEndpointTest.java` covering three cases.

## Goal

Show that Boot's auto-configuration alone can issue client credentials tokens and publish discovery and JWKS endpoints, with no `@Configuration` class.

## Run it

```bash
mvn -B test                 # MockMvc tests, no Docker
mvn spring-boot:run         # optional: server on :9000
```

Expected: `Tests run: 3, Failures: 0, Errors: 0` and `BUILD SUCCESS` (this was run). `spring-boot:run` was not started during this check.

## What it proves

- The client `orders-service` (secret stored with the `{noop}` encoder) gets a Bearer token from `POST /oauth2/token` with `client_credentials` and scope `orders.read`; a wrong secret gets 401.
- `/.well-known/openid-configuration` reports the issuer `http://localhost:9000` and `/oauth2/jwks` returns 200, so a resource server can use that issuer.
- `App.java` is only a `main` method; everything else is the `application.yml` client registration.

## Trade-offs

- Signing keys are generated in memory at startup, so tokens do not survive a restart; clients are in memory too.
- `{noop}` secrets are for the lab only; real use needs bcrypt and a persistent client repository such as JDBC.
- Interactive flows (authorization code with login and consent) need extra configuration and a user store, and are not covered.

## When not to use it

- When you want a ready-made identity provider with an admin UI, user federation and MFA; use Keycloak or a managed service.
