#!/usr/bin/env python3
"""Preflight real loopback OpenAI-compatible LLM services (no external APIs).

This script sends one harmless chat-completions request to the actual local
server and verifies the requested served model ID. Raw model output, tokens,
and endpoint URLs are never written into the provenance report.
"""
from __future__ import annotations
import argparse
from datetime import datetime, timezone
import json
import os
from pathlib import Path
from urllib.parse import urlsplit, urlunsplit
from urllib.request import Request, urlopen

from prepare import ROOT, read_json


def local_endpoint(value: str) -> tuple[str, str]:
    u = urlsplit(value)
    if (u.scheme not in ("http", "https")
        or (u.hostname or "").lower() not in ("127.0.0.1", "localhost", "::1")
        or u.username is not None or u.password is not None
        or u.path != "/v1/chat/completions" or u.query or u.fragment):
        raise ValueError("model endpoint must be a loopback /v1/chat/completions URL without credentials or query")
    return value, urlunsplit((u.scheme, u.netloc, "/v1/models", "", ""))


def server_request(url: str, token: str, payload: dict | None, timeout: int) -> dict:
    headers = {"Authorization": f"Bearer {token}", "Accept": "application/json"}
    if payload is not None:
        headers["Content-Type"] = "application/json"
    request = Request(url, headers=headers,
                      data=json.dumps(payload).encode() if payload is not None else None,
                      method="POST" if payload is not None else "GET")
    with urlopen(request, timeout=timeout) as response:
        if response.status != 200:
            raise ValueError(f"unexpected local endpoint HTTP status {response.status}")
        body = response.read(512 * 1024)
    result = json.loads(body)
    if not isinstance(result, dict):
        raise ValueError("local endpoint did not return a JSON object")
    return result


def preflight(model: dict, request_generation: bool = True, timeout: int = 120) -> dict:
    endpoint_value = os.environ.get(model["endpoint_env"], "")
    token = os.environ.get(model["token_env"], "")
    served_id = os.environ.get(model.get("served_model_env", ""), "") or model["model_id"]
    if not endpoint_value or not token or not served_id:
        raise ValueError("missing local model endpoint, key or served model ID")
    completions_url, models_url = local_endpoint(endpoint_value)
    listing = server_request(models_url, token, None, min(timeout, 20))
    available = [x.get("id") for x in listing.get("data", [])
                 if isinstance(x, dict) and isinstance(x.get("id"), str)]
    if served_id not in available:
        raise ValueError(f"selected served model not in local /v1/models IDs: {served_id!r}; available={available!r}")
    answer_checked = False
    if request_generation:
        response = server_request(completions_url, token, {
            "model": served_id,
            "messages": [{"role": "user", "content": "Reply with a brief greeting."}],
            "temperature": 0, "max_tokens": 32, "stream": False,
        }, timeout)
        choices = response.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise ValueError("local chat-completions response missing choices")
        choice = choices[0]
        message = choice.get("message") or {}
        if not isinstance(message, dict) or not isinstance(message.get("content"), str):
            raise ValueError("local chat completion did not return textual content")
        answer_checked = True
    return {
        "profile_id": model["profile_id"],
        "checkpoint_candidate": model["model_id"],
        "checkpoint_revision": model.get("model_revision"),
        "model_revision_pinned": bool(model.get("model_revision")),
        "served_model_id": served_id,
        "loopback": True,
        "model_list_verified": True,
        "real_local_chat_completion_verified": answer_checked,
        "timestamp_utc": datetime.now(timezone.utc).isoformat(),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--models", nargs="+", required=True, help="profile IDs to verify")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--list-only", action="store_true", help="GET /v1/models only; no inference")
    parser.add_argument("--timeout", type=int, default=120)
    args = parser.parse_args()
    profiles = read_json(ROOT / "model-profiles.json")["models"]
    allowed = {p["profile_id"]: p for p in profiles}
    if any(x not in allowed for x in args.models):
        parser.error("unknown model profile")
    if args.output.exists():
        parser.error("refusing to overwrite preflight report")
    results = [preflight(allowed[p], not args.list_only, args.timeout) for p in args.models]
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps({
        "status": "PASS", "classification": "LOCAL_LLM_ENDPOINT_PREFLIGHT_NOT_AGENTOS_TASK",
        "models": results}, indent=2) + "\n", encoding="utf-8")
    print(f"Verified {len(results)} local model endpoints; real generation={not args.list_only}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
