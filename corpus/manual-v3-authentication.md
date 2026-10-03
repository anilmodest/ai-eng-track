---
product: Kestrel Data Runner
version: v3
section: Security
---

# Authentication (Kestrel v3)

Every call to the Kestrel API must identify the caller.

## How to authenticate

Exchange your client credentials for a bearer token, then send the token in the `Authorization` header on every request.

```
curl -X POST https://api.example-kestrel.test/v3/oauth/token \
  -d grant_type=client_credentials -d client_id=... -d client_secret=...
curl -H 'Authorization: Bearer <token>' https://api.example-kestrel.test/v3/runs
```

A token **expires after 3600 seconds** and must be requested again. Client credentials are created in the console under Settings, Access. An account may hold up to 10 credential pairs.

## Failures

The `X-Kestrel-Key` header is no longer accepted. A request carrying it is rejected with `401` and the body `{"error":"scheme_removed"}`, which is the error to look for after an upgrade. A missing or expired token returns `401` with `{"error":"bad_token"}`.

## Rotating credentials

Create the new pair, move your callers to it, then revoke the old one. Both pairs work while you do this.
