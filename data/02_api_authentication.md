# API Authentication

## Bearer tokens
Northstar API requests use `Authorization: Bearer <token>`. A `401 invalid_token` response indicates a missing, expired, malformed, or revoked token. Confirm there is exactly one `Bearer` prefix and no quotation marks around the token. Tokens are environment-specific: sandbox tokens do not work against `api.northstar.example`.

## Permissions
A `403 insufficient_scope` response means the token is valid but lacks the required scope. Compare the endpoint documentation with the scopes visible in Settings > Developer > API tokens. Create a replacement token with the required scope; existing token scopes cannot be edited.

## Safe diagnostics
Record the request ID, endpoint, HTTP status, and timestamp. Never paste a full token into logs or support messages. Tokens should be stored in a secret manager and rotated immediately if exposed.

