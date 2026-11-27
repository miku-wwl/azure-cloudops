from __future__ import annotations

import argparse
import json
import sys
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

def observe(url: str, timeout: float = 10.0) -> tuple[int, dict[str, Any]]:
    request = urllib.request.Request(
        url,
        headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        method="GET",
    )
    try:
        response = urllib.request.urlopen(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        return response.code, json.loads(response.read().decode("utf-8"))

def main() -> int:
    parser = argparse.ArgumentParser(description="Check an isolated IR-11 App Service release.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--expected-status", type=int, required=True)
    parser.add_argument("--expected-release", required=True)
    args = parser.parse_args()
    parsed = urllib.parse.urlparse(args.url)
    if parsed.scheme != "https" or not parsed.hostname or not parsed.hostname.endswith(".azurewebsites.net"):
        parser.error("URL must be the approved HTTPS azurewebsites.net endpoint")
    try:
        status, body = observe(args.url)
    except (OSError, ValueError, json.JSONDecodeError) as error:
        print(f"probe=FAIL error={type(error).__name__}", file=sys.stderr)
        return 2
    passed = status == args.expected_status and body.get("release") == args.expected_release
    print(f"probe={'PASS' if passed else 'FAIL'} status={status} release={body.get('release')}")
    return 0 if passed else 1

if __name__ == "__main__":
    raise SystemExit(main())
