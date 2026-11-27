#!/usr/bin/env python3
"""Inspect JWT audience and selected claims without logging or validating a token.

This is a local claim-inspection aid, not a signature validator, identity proof,
or Azure login tool. Supply a token through hidden interactive input or stdin;
never place it on a command line or in a transcript.
"""
from __future__ import annotations

import argparse
import base64
import binascii
import getpass
import json
import sys
import time
from datetime import datetime, timezone
from typing import Any, Sequence


class TokenFormatError(ValueError):
    pass


def _unique_object(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    result: dict[str, Any] = {}
    for key, value in pairs:
        if key in result:
            raise TokenFormatError("duplicate claim")
        result[key] = value
    return result


def _decode_claims(token: str) -> dict[str, Any]:
    if not isinstance(token, str) or not token or len(token) > 32768:
        raise TokenFormatError("token is empty or exceeds the input limit")
    parts = token.strip().split(".")
    if len(parts) != 3 or not parts[1]:
        raise TokenFormatError("input is not a three-part JWT")
    encoded = parts[1]
    try:
        padding = "=" * (-len(encoded) % 4)
        payload = base64.b64decode(encoded + padding, altchars=b"-_", validate=True)
        claims = json.loads(payload.decode("utf-8"), object_pairs_hook=_unique_object)
    except (ValueError, UnicodeDecodeError, binascii.Error, json.JSONDecodeError) as exc:
        raise TokenFormatError("JWT payload is not valid base64url JSON") from exc
    if not isinstance(claims, dict):
        raise TokenFormatError("JWT payload must be a JSON object")
    return claims


def inspect_token(token: str, expected_audience: str | None = None, now: int | None = None) -> dict[str, Any]:
    claims = _decode_claims(token)
    aud = claims.get("aud")
    if isinstance(aud, str):
        audiences = [aud]
    elif isinstance(aud, list) and all(isinstance(value, str) for value in aud):
        audiences = aud
    elif aud is None:
        audiences = []
    else:
        raise TokenFormatError("aud claim has an unsupported type")

    result: dict[str, Any] = {
        "input_kind": "JWT access token",
        "signature_verified": False,
        "warning": "Claims are untrusted until signature, issuer, tenant, lifetime and expected token type are verified by an approved validator.",
        "aud": audiences,
    }
    if expected_audience is not None:
        result["expected_audience"] = expected_audience
        result["audience_match"] = expected_audience in audiences

    for key in ("iss", "tid", "appid", "azp", "ver"):
        value = claims.get(key)
        if value is not None:
            if not isinstance(value, str):
                raise TokenFormatError(f"{key} claim has an unsupported type")
            result[key] = value
    scope = claims.get("scp")
    if scope is not None:
        if not isinstance(scope, str):
            raise TokenFormatError("scp claim has an unsupported type")
        result["scopes"] = sorted(set(scope.split()))
    roles = claims.get("roles")
    if roles is not None:
        if not isinstance(roles, list) or not all(isinstance(item, str) for item in roles):
            raise TokenFormatError("roles claim has an unsupported type")
        result["roles"] = sorted(set(roles))

    current = int(time.time()) if now is None else now
    for key in ("exp", "nbf"):
        value = claims.get(key)
        if value is not None:
            if isinstance(value, bool) or not isinstance(value, int):
                raise TokenFormatError(f"{key} claim has an unsupported type")
            result[f"{key}_utc"] = datetime.fromtimestamp(value, timezone.utc).isoformat(timespec="seconds")
    if isinstance(claims.get("exp"), int) and not isinstance(claims.get("exp"), bool):
        result["expired_at_inspection_time"] = claims["exp"] <= current
    if isinstance(claims.get("nbf"), int) and not isinstance(claims.get("nbf"), bool):
        result["not_yet_valid_at_inspection_time"] = claims["nbf"] > current
    return result


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Inspect selected JWT claims locally; no token is sent or verified.")
    parser.add_argument("--expected-audience", help="Optional audience value to compare with the token's aud claim.")
    args = parser.parse_args(argv)
    token = getpass.getpass("JWT (hidden input; signature is not verified): ", stream=sys.stderr) if sys.stdin.isatty() else sys.stdin.read(32769)
    try:
        result = inspect_token(token, args.expected_audience)
    except TokenFormatError:
        print(json.dumps({"ok": False, "error": "INVALID_JWT_INPUT", "message": "Input was not a supported JWT; token content was suppressed."}))
        return 2
    print(json.dumps({"ok": True, "claims": result}, ensure_ascii=False, sort_keys=True, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
