#!/usr/bin/env python3
"""Normalise the claims of Keycloak, Cognito and Auth0 access tokens into one principal.

The same Orders API sees three different token shapes. Run `python3 claims_map.py` to check the mapping
against the fixtures below (payloads copied from the providers' documented formats, no signatures).
"""

ISSUERS = {
    "keycloak": "http://localhost:8080/realms/orders",
    "cognito": "https://cognito-idp.eu-west-1.amazonaws.com/eu-west-1_EXAMPLE",
    "auth0": "https://example.eu.auth0.com/",
}


def principal(claims):
    """Return {provider, subject, scopes, groups} for a decoded access-token payload."""
    iss = claims["iss"]
    if iss == ISSUERS["cognito"]:
        # Cognito access tokens: space-delimited `scope`, groups in `cognito:groups`, no `aud` (uses client_id)
        return {"provider": "cognito", "subject": claims["sub"],
                "scopes": set(claims.get("scope", "").split()), "groups": set(claims.get("cognito:groups", []))}
    if iss == ISSUERS["auth0"]:
        # Auth0: scopes in `scope` (or `permissions` when RBAC is on), roles via a namespaced custom claim
        scopes = set(claims.get("scope", "").split()) | set(claims.get("permissions", []))
        return {"provider": "auth0", "subject": claims["sub"], "scopes": scopes,
                "groups": set(claims.get("https://orders.example/roles", []))}
    if iss == ISSUERS["keycloak"]:
        return {"provider": "keycloak", "subject": claims["sub"],
                "scopes": set(claims.get("scope", "").split()),
                "groups": set(claims.get("realm_access", {}).get("roles", []))}
    raise ValueError(f"untrusted issuer {iss}")


FIXTURES = [
    ({"iss": ISSUERS["keycloak"], "sub": "k-1", "scope": "openid orders.read",
      "realm_access": {"roles": ["staff"]}}, "keycloak", {"openid", "orders.read"}, {"staff"}),
    ({"iss": ISSUERS["cognito"], "sub": "c-1", "client_id": "abc", "scope": "orders/read",
      "cognito:groups": ["staff"]}, "cognito", {"orders/read"}, {"staff"}),
    ({"iss": ISSUERS["auth0"], "sub": "auth0|a-1", "aud": "https://orders.example/api", "scope": "read:orders",
      "permissions": ["read:orders", "write:orders"], "https://orders.example/roles": ["staff"]},
     "auth0", {"read:orders", "write:orders"}, {"staff"}),
]

if __name__ == "__main__":
    for claims, provider, scopes, groups in FIXTURES:
        p = principal(claims)
        assert (p["provider"], p["scopes"], p["groups"]) == (provider, scopes, groups), p
        print(f"{provider:9} sub={p['subject']:10} scopes={sorted(p['scopes'])}")
    try:
        principal({"iss": "https://evil.example", "sub": "x"})
        raise SystemExit("FAIL: untrusted issuer accepted")
    except ValueError:
        print("untrusted issuer rejected")
    print("ok")
