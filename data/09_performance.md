# Performance and Timeouts

## Browser performance
Northstar supports the current and previous major versions of Chrome, Edge, Firefox, and Safari. First test in a private window with extensions disabled. Clear site data only after saving unsent work. Capture the browser version, region, affected page, timestamp, and a sanitized network trace.

## API latency
API clients should use a 30-second request timeout and exponential backoff with jitter for `429`, `502`, `503`, and `504` responses. Do not retry other 4xx responses automatically. The standard API limit is 600 requests per minute per organization; limit headers report the remaining quota and reset time.

## Large queries
Use pagination and request only required fields. Export jobs are better suited to large datasets than synchronous list requests. Persistent latency with request IDs should be escalated for service review.

