# Webhook Delivery and Signatures

## Delivery behavior
Webhook endpoints must return a 2xx response within 10 seconds. Northstar retries failed delivery after 1, 5, 30, and 120 minutes. After the final retry, the event remains visible in Developer > Webhook deliveries for seven days and can be replayed manually.

## Signature verification
The `X-Northstar-Signature` header contains an HMAC-SHA256 signature of the raw request body. Compute the HMAC with the endpoint signing secret and compare it using a constant-time function. Parsing or re-serializing JSON before verification changes the body and causes a signature mismatch.

## Troubleshooting
For timeouts, acknowledge the webhook before starting slow downstream work. For repeated 5xx responses, inspect the delivery request ID and application logs. Rotate the signing secret if it was exposed; both old and new secrets remain valid for a five-minute transition window.

