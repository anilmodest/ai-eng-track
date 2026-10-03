---
product: Kestrel Data Runner
version: v2
section: Security
---

# Authentication (Kestrel v2)

Every call to the Kestrel API must identify the caller.

## How to authenticate

Send your API key in the `X-Kestrel-Key` header on every request.

```
curl -H 'X-Kestrel-Key: <your key>' https://api.example-kestrel.test/v2/runs
```

Keys are created in the console under Settings, Access. A key **does not expire** and remains valid until it is revoked by hand. An account may hold up to 10 keys.

## Failures

A missing or unknown key returns `401` with the body `{"error":"bad_key"}`.

## Rotating a key

Create the new key, move your callers to it, then revoke the old one. Both keys work while you do this.
