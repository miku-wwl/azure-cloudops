from __future__ import annotations

import argparse
import json
import re
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from typing import Any

HOST_PATTERN = re.compile(r"azcoir11aue261126(?:-[a-z0-9-]+)?(?:\.[a-z0-9-]+)*\.azurewebsites\.net")
EXPECTED_HEALTH = {"known-good-v1": (200, True), "intentional-failure-v2": (500, False)}


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def observe(url: str, timeout: float = 10.0) -> tuple[int, dict[str, Any] | None]:
    request = urllib.request.Request(
        url,
        headers={"Cache-Control": "no-cache", "Pragma": "no-cache"},
        method="GET",
    )
    try:
        response = urllib.request.build_opener(NoRedirect()).open(request, timeout=timeout)
    except urllib.error.HTTPError as error:
        response = error
    with response:
        raw = response.read(4097)
        try:
            body = json.loads(raw) if len(raw) <= 4096 else None
        except (ValueError, UnicodeError):
            body = None
        return response.code, body if isinstance(body, dict) else None


def matches_expected(status: int, body: dict[str, Any] | None, release: str) -> bool:
    expected_status, expected_healthy = EXPECTED_HEALTH[release]
    return (
        status == expected_status
        and body is not None
        and set(body) == {"release", "healthy"}
        and body["release"] == release
        and body["healthy"] is expected_healthy
    )

def main() -> int:
    parser = argparse.ArgumentParser(description="Check an isolated IR-11 App Service release.")
    parser.add_argument("--url", required=True)
    parser.add_argument("--expected-status", type=int, required=True)
    parser.add_argument("--expected-release", required=True, choices=EXPECTED_HEALTH)
    parser.add_argument("--wait-seconds", type=int, default=90)
    args = parser.parse_args()
    parsed = urllib.parse.urlparse(args.url)
    if (
        parsed.scheme != "https" or not HOST_PATTERN.fullmatch(parsed.netloc)
        or parsed.path != "/health" or parsed.query or parsed.fragment
    ):
        parser.error("URL must be the approved HTTPS azurewebsites.net endpoint")
    if not 1 <= args.wait_seconds <= 120 or EXPECTED_HEALTH[args.expected_release][0] != args.expected_status:
        parser.error("invalid probe window or expected status for this release")

    start = time.monotonic()
    deadline = start + args.wait_seconds
    attempts = 0
    last = "no_response"
    while (remaining := deadline - time.monotonic()) > 0:
        attempts += 1
        try:
            status, body = observe(args.url, timeout=min(8, remaining))
        except OSError as exc:
            last = f"transport={type(exc).__name__}"
        else:
            if matches_expected(status, body, args.expected_release):
                safe_body = json.dumps(body, separators=(",", ":"))
                print(f"probe=PASS status={status} body={safe_body} attempts={attempts} elapsed_s={time.monotonic() - start:.2f}")
                return 0
            last = f"status={status} body_match=false"
        time.sleep(max(0, min(4, deadline - time.monotonic())))
    print(f"probe=FAIL {last} attempts={attempts} elapsed_s={time.monotonic() - start:.2f}", file=sys.stderr)
    return 1

if __name__ == "__main__":
    raise SystemExit(main())
