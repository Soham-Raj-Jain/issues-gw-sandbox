### Coded by - Soham Jain - SJSUID- 019139796 ###
import hmac, hashlib, json
import pytest

# ----------------------------------------------------------------------------
# Utility function: Generates a valid GitHub-style HMAC SHA-256 signature
# ----------------------------------------------------------------------------
# - GitHub signs each webhook payload with a secret (known only to GitHub + server).
# - The server re-computes the HMAC signature using the secret + payload,
#   then compares it with the one sent in "X-Hub-Signature-256".
# - This ensures the request actually came from GitHub and was not tampered with.
def sign(secret: str, payload: bytes) -> str:
    return "sha256=" + hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()


# ----------------------------------------------------------------------------
# Test 1: Valid webhook signature
# ----------------------------------------------------------------------------
# Scenario:
# - Simulates GitHub sending a "ping" webhook event.
# - The payload is correctly signed with the shared webhook secret.
# Expectation:
# - The server should verify the signature successfully.
# - Response should be HTTP 204 (No Content) since "ping" is just a test event.
@pytest.mark.asyncio
async def test_webhook_valid_signature(client, webhook_secret):
    # Construct a small JSON payload (GitHub sends JSON bodies)
    body = json.dumps({"zen": "ok"}).encode()

    # Build headers as GitHub would send them
    headers = {
        "X-GitHub-Event": "ping",                       # Event type (ping = test event)
        "X-GitHub-Delivery": "local-1",                 # Unique delivery identifier
        "X-Hub-Signature-256": sign(webhook_secret, body),  # Correct signature
        "Content-Type": "application/json",             # Payload format
    }

    # Send request to our webhook endpoint with valid signature
    resp = await client.post("/webhook", content=body, headers=headers)

    # ✅ Expect success: 204 means "processed but no content returned"
    assert resp.status_code == 204


# ----------------------------------------------------------------------------
# Test 2: Invalid webhook signature
# ----------------------------------------------------------------------------
# Scenario:
# - Simulates a malicious or tampered request.
# - The payload is signed incorrectly (wrong HMAC).
# Expectation:
# - The server should reject the request.
# - Response should be HTTP 401 (Unauthorized).
@pytest.mark.asyncio
async def test_webhook_invalid_signature(client):
    # Create a fake/tampered payload
    body = b'{"zen":"tampered"}'

    # Build headers with WRONG signature
    headers = {
        "X-GitHub-Event": "ping",                   # Still a "ping" event
        "X-GitHub-Delivery": "local-2",             # Different unique delivery ID
        "X-Hub-Signature-256": "sha256=" + "00"*32, # ❌ Fake signature (all zeros)
        "Content-Type": "application/json",
    }

    # Send request to webhook endpoint with invalid signature
    resp = await client.post("/webhook", content=body, headers=headers)

    # ❌ Expect failure: 401 Unauthorized (signature verification failed)
    assert resp.status_code == 401
