# cognito-auth0

Two Spring profile files (`application-cognito.yml`, `application-auth0.yml`) and `claims_map.py`, an offline mapper that normalises Keycloak, Cognito and Auth0 token claims.

## Goal

Show how the Orders resource server would point at Cognito or Auth0 instead of Keycloak, and how differently the three providers shape their access-token claims.

## Run it

```bash
python3 claims_map.py       # offline, standard library only
```

Expected (this was run):

    keycloak  sub=k-1        scopes=['openid', 'orders.read']
    cognito   sub=c-1        scopes=['orders/read']
    auth0     sub=auth0|a-1  scopes=['read:orders', 'write:orders']
    untrusted issuer rejected
    ok

Not run end to end: the two YAML files need a real Cognito user pool or Auth0 tenant, which this folder does not create. Activate them with `--spring.profiles.active=cognito` or `auth0`. Cost if you try: Cognito's free tier covers the first 10,000 monthly active users and Auth0 has a free plan; destroy by deleting the user pool, or the Auth0 API and application.

## What it proves

- Groups and scopes live in different claims: Keycloak `realm_access.roles`, Cognito `cognito:groups` with scopes such as `orders/read`, Auth0 `permissions` and a namespaced roles claim.
- One `principal()` function maps all three into the same shape and raises an error for an unknown issuer.
- `application-auth0.yml` sets `audiences` because Auth0 puts the API identifier in `aud`, while Cognito access tokens carry `client_id` instead.

## Trade-offs

- The fixtures in `claims_map.py` are written by hand from the providers' documented formats, not captured from live tenants.
- Signatures are not verified; only the claim shape is checked.
- Provider limits differ, for example Cognito custom scopes need a resource server and Cognito offers limited token exchange.

## When not to use it

- When you run one identity provider and do not plan to switch.
- When you need behaviour verified against a live tenant; check the provider documentation with a real token first.
