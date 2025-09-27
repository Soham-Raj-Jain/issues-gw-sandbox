### Coded by - Soham Jain - SJSUID- 019139796 ###

# -----------------------------------------------------------------------------
# scripts/check_github_token.py
# -----------------------------------------------------------------------------
# Purpose:
#   - Verify that the GitHub Personal Access Token (PAT) or fine-grained token
#     stored in `.env` works correctly for accessing the Issues API.
#   - Provide helpful diagnostics if something is misconfigured.
#
# How it works:
#   1. Loads environment variables from `.env`
#   2. Checks that GITHUB_TOKEN, GITHUB_OWNER, and GITHUB_REPO are present
#   3. Makes a request to GitHub's Issues API
#   4. Reports success or detailed error info depending on the response
# -----------------------------------------------------------------------------

import os, sys
import httpx
from dotenv import load_dotenv

# Load variables from a .env file in the project root
load_dotenv()

# Read required variables from environment
token = os.getenv("GITHUB_TOKEN")
owner = os.getenv("GITHUB_OWNER")
repo = os.getenv("GITHUB_REPO")

# -----------------------------------------------------------------------------
# Helper function: exit with an error message
# -----------------------------------------------------------------------------
def fail(msg: str, code: int = 1):
    print(f"[ERROR] {msg}")
    sys.exit(code)

# Ensure required environment variables are present
if not token:
    fail("GITHUB_TOKEN is missing in .env")
if not owner:
    fail("GITHUB_OWNER is missing in .env")
if not repo:
    fail("GITHUB_REPO is missing in .env")

# -----------------------------------------------------------------------------
# Build GitHub Issues API request
# -----------------------------------------------------------------------------
url = f"https://api.github.com/repos/{owner}/{repo}/issues"
headers = {
    "Authorization": f"Bearer {token}",            # Token authentication
    "Accept": "application/vnd.github+json",       # Standard GitHub API media type
    "User-Agent": "issues-gw/check",               # Custom UA string (required by GitHub)
}
params = {"state": "open", "per_page": 1}          # Only request 1 open issue

print(f"[INFO] Checking GitHub Issues API for {owner}/{repo} ...")

# -----------------------------------------------------------------------------
# Perform the request
# -----------------------------------------------------------------------------
with httpx.Client(timeout=20) as client:
    r = client.get(url, headers=headers, params=params)
    print(f"[INFO] Status: {r.status_code}")

    # Print GitHub rate-limit headers if available
    for k in ["X-RateLimit-Limit", "X-RateLimit-Remaining", "X-RateLimit-Reset"]:
        if k in r.headers:
            print(f"[INFO] {k}: {r.headers[k]}")

    # -----------------------------------------------------------------------------
    # Case 1: Success
    # -----------------------------------------------------------------------------
    if r.status_code == 200:
        print("[SUCCESS] Token works! Issues endpoint is accessible.")
        if isinstance(r.json(), list):
            print(f"[INFO] Returned {len(r.json())} issue(s) (showing up to 1).")
        sys.exit(0)

    # -----------------------------------------------------------------------------
    # Case 2: Error → Provide detailed diagnostics
    # -----------------------------------------------------------------------------
    try:
        body = r.json()   # Try parsing JSON error response
    except Exception:
        body = {"raw": r.text[:200]}  # Fallback: first 200 chars of raw text

    if r.status_code in (401, 403):
        # Unauthorized or Forbidden errors
        print("[ERROR] Unauthorized/Forbidden. Common causes:")
        print("  - Token is wrong or expired")
        print("  - Token lacks 'Issues: Read and write' permission for THIS repo")
        print("  - Repo not selected when creating the fine-grained token")
    elif r.status_code == 404:
        # Repo not found errors
        print("[ERROR] Not found. Common causes:")
        print("  - GITHUB_OWNER or GITHUB_REPO is misspelled")
        print("  - The token does not have access to this private repo")
    else:
        # Any other unexpected status
        print("[ERROR] Unexpected status. Response body shown below.")

    # Always print debug info to help with troubleshooting
    print("[DEBUG] Response JSON (truncated):", str(body)[:500])
    sys.exit(2)
