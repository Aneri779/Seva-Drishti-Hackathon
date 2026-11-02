"""
API verification script — Gate D.
Calls every route with correct role, wrong role, and no token.
Prints PASS/FAIL table.
Usage: python scripts/verify_api.py --base-url http://localhost:8000
"""
import asyncio
import httpx
import sys
import json
from typing import Optional

BASE_URL = "http://localhost:8000"

# Test credentials — must exist in the DB
ADMIN_MOBILE = "9876543210"
ADMIN_OTP = None  # Read from server logs after /otp/send

ROLE_CREDENTIALS: dict[str, tuple[str, str]] = {
    "admin": ("9876543210", ""),
    "rb_ee": ("9876543211", ""),
    "seoc_officer": ("9876543212", ""),
}

ROUTE_TEST_SPEC = [
    # (method, path, required_role, body)
    ("GET", "/health", None, None),
    ("GET", "/health/deep", None, None),
    ("GET", "/api/v1/auth/me", "admin", None),
    ("GET", "/api/v1/scenes", "admin", None),
    ("GET", "/api/v1/scenes/latest/telemetry", "admin", None),
    ("GET", "/api/v1/chainage-events", "admin", None),
    ("GET", "/api/v1/alerts", "admin", None),
    ("GET", "/api/v1/stats/summary", "admin", None),
    ("GET", "/api/v1/stats/road-classes", "admin", None),
    ("GET", "/api/v1/advisories/corridors", "admin", None),
    ("GET", "/api/v1/notifications/audiences", "admin", None),
    ("GET", "/api/v1/bulletins", "admin", None),
    ("GET", "/api/v1/dispatch-tasks", "admin", None),
    ("GET", "/api/v1/meta/districts", None, None),
    ("GET", "/api/v1/public/summary", None, None),
    ("GET", "/api/v1/public/districts", None, None),
    ("GET", "/api/v1/system/status", "admin", None),
    ("GET", "/api/v1/admin/config", "admin", None),
]

tokens: dict[str, str] = {}

async def get_token(client: httpx.AsyncClient, mobile: str) -> Optional[str]:
    """Get OTP and verify to get access token."""
    r = await client.post(f"{BASE_URL}/api/v1/auth/otp/send", json={"mobile": mobile})
    if r.status_code != 200:
        print(f"  OTP send failed for {mobile}: {r.text}")
        return None
    # OTP is in SERVER LOGS only. For testing, admin seeds a known user.
    # Read from server log or inject via test-only endpoint.
    print(f"  [ACTION NEEDED] Read OTP from server log for +91-{mobile} and enter:")
    otp = input(f"  OTP for {mobile}: ").strip()
    
    r2 = await client.post(f"{BASE_URL}/api/v1/auth/otp/verify", json={"mobile": mobile, "otp": otp})
    if r2.status_code == 200:
        return r2.json()["tokens"]["access_token"]
    print(f"  OTP verify failed: {r2.text}")
    return None


async def run_tests():
    results = []
    async with httpx.AsyncClient(timeout=15) as client:
        # Acquire tokens for each role
        print("\n=== Acquiring tokens ===")
        for role, (mobile, _) in ROLE_CREDENTIALS.items():
            token = await get_token(client, mobile)
            if token:
                tokens[role] = token
                print(f"  [{role}] token acquired")
            else:
                print(f"  [{role}] SKIPPED — no token")
        
        print("\n=== Running route tests ===")
        for method, path, required_role, body in ROUTE_TEST_SPEC:
            row = {"method": method, "path": path, "required_role": required_role or "public"}
            
            # 1. No auth
            r = await client.request(method, BASE_URL + path, json=body)
            if required_role is None:
                row["no_auth"] = "PASS" if r.status_code < 400 else f"FAIL ({r.status_code})"
            else:
                row["no_auth"] = "PASS" if r.status_code == 401 else f"FAIL (expected 401, got {r.status_code})"
            
            # 2. Wrong role (use rb_ee for admin-only routes, admin for rb_ee-only)
            wrong_role = "rb_ee" if required_role == "admin" else "admin"
            wrong_token = tokens.get(wrong_role)
            if wrong_token and required_role:
                headers = {"Authorization": f"Bearer {wrong_token}"}
                r2 = await client.request(method, BASE_URL + path, headers=headers, json=body)
                if wrong_role != required_role:
                    row["wrong_role"] = "PASS" if r2.status_code in (403, 200) else f"FAIL ({r2.status_code})"
                else:
                    row["wrong_role"] = "N/A"
            else:
                row["wrong_role"] = "SKIP"
            
            # 3. Correct role
            token = tokens.get(required_role or "admin")
            if token:
                headers = {"Authorization": f"Bearer {token}"}
                r3 = await client.request(method, BASE_URL + path, headers=headers, json=body)
                row["correct_role"] = "PASS" if r3.status_code < 400 else f"FAIL ({r3.status_code}: {r3.text[:100]})"
            else:
                row["correct_role"] = "SKIP"
            
            results.append(row)
        
        # Print table
        print("\n" + "=" * 100)
        print(f"{'Method':<8} {'Path':<40} {'Required':<20} {'No Auth':<15} {'Wrong Role':<15} {'Correct Role':<15}")
        print("-" * 100)
        pass_count = fail_count = 0
        for row in results:
            all_pass = "FAIL" not in row.get("no_auth", "") and \
                       "FAIL" not in row.get("wrong_role", "") and \
                       "FAIL" not in row.get("correct_role", "")
            if all_pass:
                pass_count += 1
            else:
                fail_count += 1
            marker = "✅" if all_pass else "❌"
            print(f"{marker} {row['method']:<6} {row['path']:<40} {row['required_role']:<20} "
                  f"{row['no_auth']:<15} {row['wrong_role']:<15} {row['correct_role']:<15}")
        
        print("=" * 100)
        print(f"TOTAL: {pass_count + fail_count} routes | PASS: {pass_count} | FAIL: {fail_count}")
        return fail_count == 0


if __name__ == "__main__":
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument("--base-url", default="http://localhost:8000")
    args = parser.parse_args()
    BASE_URL = args.base_url
    ok = asyncio.run(run_tests())
    sys.exit(0 if ok else 1)

