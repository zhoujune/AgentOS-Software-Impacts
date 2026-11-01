#!/usr/bin/env python3
"""Loopback-only OpenAI-compatible Qwen3 chat template adapter.

For vLLM Qwen3 models whose default chat template emits <think> blocks,
AgentOS's typed JSON-only tool protocol requires the official per-request
enable_thinking=False setting. This adapter supplies that setting to the local
vLLM server, without editing AgentOS guest/runtime or WEJ/VTRM rules.

No credentials, prompts, model text or responses are logged. The upstream
server MUST be loopback and the model ID MUST match the intended checkpoint.
"""
from __future__ import annotations

import argparse
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
from urllib.parse import urlsplit
from urllib.request import Request, urlopen
from urllib.error import HTTPError


def loopback_origin(value: str) -> str:
    parsed = urlsplit(value)
    if (parsed.scheme != "http"
        or parsed.hostname not in {"localhost", "127.0.0.1", "::1"}
        or parsed.path not in {"", "/"} or parsed.query or parsed.fragment
        or parsed.username or parsed.password):
        raise ValueError("upstream must be a plain loopback HTTP origin")
    return value.rstrip("/")


def create_handler(origin: str, model: str):
    origin = loopback_origin(origin)
    if not model or len(model) > 128:
        raise ValueError("explicit served model required")

    class Handler(BaseHTTPRequestHandler):
        def respond(self, status: int, payload: bytes, mime: str = "application/json"):
            self.send_response(status)
            self.send_header("Content-Type", mime)
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)

        def forward(self, method: str, data: bytes | None = None):
            upstream_url = origin + self.path
            headers = {"Accept": "application/json"}
            if data is not None:
                headers["Content-Type"] = "application/json"
            req = Request(upstream_url, data=data, headers=headers, method=method)
            try:
                with urlopen(req, timeout=120) as response:
                    return response.status, response.read(2 * 1024 * 1024)
            except HTTPError as exc:
                return exc.code, exc.read(512 * 1024)

        def do_GET(self):
            if self.path != "/v1/models":
                self.respond(404, b'{"error":"unknown route"}')
                return
            try:
                status, data = self.forward("GET")
                self.respond(status, data)
            except OSError:
                self.respond(502, b'{"error":"local upstream unavailable"}')

        def do_POST(self):
            if self.path != "/v1/chat/completions":
                self.respond(404, b'{"error":"unknown route"}')
                return
            size = int(self.headers.get("Content-Length", "0"))
            if size <= 0 or size > 1024 * 1024:
                self.respond(413, b'{"error":"invalid request size"}')
                return
            try:
                request = json.loads(self.rfile.read(size))
                if (not isinstance(request, dict)
                    or request.get("model") != model
                    or not isinstance(request.get("messages"), list)
                    or request.get("stream") is True):
                    self.respond(400, b'{"error":"model mismatch or unsupported request"}')
                    return
                # Only change the model's serialization of its reasoning.
                # The original user/task messages, policy and model outputs
                # are otherwise transported unchanged.
                request["chat_template_kwargs"] = {"enable_thinking": False}
                data = json.dumps(request).encode("utf-8")
                status, response = self.forward("POST", data)
                self.respond(status, response)
            except (ValueError, TypeError, KeyError, OSError):
                self.respond(502, b'{"error":"invalid request or local upstream unavailable"}')

        def log_message(self, fmt, *args):
            # Metadata only; never log prompt, request, response or token.
            print("adapter access: " + fmt % args, flush=True)

    return Handler


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--upstream", required=True, help="http://127.0.0.1:8018")
    parser.add_argument("--model", required=True, help="qwen3-14b-local")
    parser.add_argument("--port", type=int, default=8028)
    args = parser.parse_args()
    if not 1024 <= args.port <= 65535:
        parser.error("adapter port must be 1024..65535")
    Handler = create_handler(args.upstream, args.model)
    server = ThreadingHTTPServer(("127.0.0.1", args.port), Handler)
    print("Qwen3 adapter listening on 127.0.0.1:" + str(args.port)
          + " for served model " + args.model + " (thinking disabled)", flush=True)
    server.serve_forever()


if __name__ == "__main__":
    main()
