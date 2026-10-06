# sec-identity-oauth

OAuth 2.0 and OpenID Connect flows wired up with Keycloak (realm as code), Spring Security and Spring Authorization Server, so you can see how tokens are issued, exchanged and validated for a small Orders API.

## What is inside

| Folder | What it shows | Run |
| --- | --- | --- |
| [`keycloak-oidc-pkce`](./keycloak-oidc-pkce) | Authorization code flow with PKCE (S256) against a Keycloak realm imported from JSON | `docker compose up -d && python3 pkce.py` |
| [`client-credentials`](./client-credentials) | Machine-to-machine token, default versus optional scopes, wrong secret rejected | `docker compose up -d && ./verify.sh` |
| [`token-exchange`](./token-exchange) | RFC 8693 exchange of a user token for one addressed to a downstream API | `docker compose up -d && ./verify.sh` |
| [`spring-security-resource-server`](./spring-security-resource-server) | JWT resource server with scope rules and method security | `mvn -B test` |
| [`spring-authorization-server`](./spring-authorization-server) | Minimal authorization server configured only in `application.yml` | `mvn -B test` |
| [`cognito-auth0`](./cognito-auth0) | Spring profiles for Cognito and Auth0 and an offline claims mapper | `python3 claims_map.py` |

## Prerequisites

- Java 21 and Maven 3.8+ (the two Spring folders, Spring Boot 3.3.5)
- Docker with Compose (the three Keycloak folders, Keycloak 26.2.5)
- Python 3 (standard library only) and curl

## How to read it

Start with `keycloak-oidc-pkce`, whose realm and ports the other Keycloak folders reuse, then `spring-security-resource-server` to see how an API consumes the tokens. The folders share the small Orders domain (`orders.read`, `orders.write`). The Keycloak folders use port 8080, so run one at a time.
