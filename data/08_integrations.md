# OAuth Integrations

## Connecting an integration
An Administrator must approve requested scopes during OAuth authorization. A `redirect_uri_mismatch` error means the callback URL differs from the exact value registered for the integration, including scheme, port, path, and trailing slash.

## Refresh failures
An `invalid_grant` response can mean the refresh token was revoked, already rotated, or issued for a different client. Reconnect the integration from Settings > Integrations to issue a new authorization. Do not retry an invalid refresh token indefinitely.

## Operational guidance
Use a dedicated integration identity rather than a departing employee's account. Record the integration name, workspace, approximate failure time, request ID, and returned OAuth error without including client secrets.

