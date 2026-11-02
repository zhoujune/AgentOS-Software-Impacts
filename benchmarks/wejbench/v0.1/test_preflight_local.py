"""Loopback API and model-name propagation tests; no real inference required."""
from __future__ import annotations

from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
import json
import os
from pathlib import Path
import sys
import tempfile
import threading
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parent))
from preflight_local import local_endpoint, preflight
from prepare_local_checkout import check_or_apply, TARGET, INSERTED, LOOP


class MockLLM(BaseHTTPRequestHandler):
    requests = []

    def do_GET(self):
        if self.path != "/v1/models":
            self.send_error(404)
            return
        self.reply({"object": "list", "data": [{"id": "llama3-8b-local"}]})

    def do_POST(self):
        if self.path != "/v1/chat/completions":
            self.send_error(404)
            return
        body = json.loads(self.rfile.read(int(self.headers["Content-Length"])))
        self.__class__.requests.append(body)
        self.reply({"id": "chat-1", "choices": [
            {"message": {"role": "assistant", "content": "Hello."},
             "finish_reason": "stop"}]})

    def reply(self, body):
        data = json.dumps(body).encode()
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def log_message(self, *args):
        pass


class LocalInferencePreflightTests(unittest.TestCase):
    def test_local_only_paths(self):
        for url in ("https://api.openai.com/v1/chat/completions",
                    "http://192.168.1.10:8017/v1/chat/completions",
                    "http://localhost:8017/v1/models",
                    "http://user:password@127.0.0.1/v1/chat/completions",
                    "http://localhost:8017/v1/chat/completions?api_key=leak"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                local_endpoint(url)
        completion, models = local_endpoint("http://127.0.0.1:8017/v1/chat/completions")
        self.assertEqual(models, "http://127.0.0.1:8017/v1/models")

    def test_mock_local_response_and_model_alias(self):
        MockLLM.requests = []
        server = ThreadingHTTPServer(("127.0.0.1", 0), MockLLM)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            model = {"profile_id": "llama3-8b", "model_id": "meta-llama/Meta-Llama-3-8B-Instruct",
                     "endpoint_env": "AGENTOS_BENCH_TEST_ENDPOINT",
                     "token_env": "AGENTOS_BENCH_TEST_TOKEN",
                     "served_model_env": "AGENTOS_BENCH_TEST_SERVED_ID"}
            values = {
                "AGENTOS_BENCH_TEST_ENDPOINT":
                    f"http://127.0.0.1:{server.server_address[1]}/v1/chat/completions",
                "AGENTOS_BENCH_TEST_TOKEN": "dummy-local",
                "AGENTOS_BENCH_TEST_SERVED_ID": "llama3-8b-local",
            }
            with patch.dict(os.environ, values):
                result = preflight(model)
                self.assertTrue(result["real_local_chat_completion_verified"])
                self.assertEqual(result["served_model_id"], "llama3-8b-local")
                self.assertEqual(MockLLM.requests[-1]["model"], "llama3-8b-local")
                self.assertNotIn("dummy-local", json.dumps(result))
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=5)

    def test_missing_server_fails_closed(self):
        model = {"profile_id": "test", "model_id": "test",
                 "endpoint_env": "AGENTOS_BENCH_UNSET_ENDPOINT",
                 "token_env": "AGENTOS_BENCH_UNSET_TOKEN"}
        with patch.dict(os.environ, {"AGENTOS_BENCH_UNSET_ENDPOINT": "",
                                     "AGENTOS_BENCH_UNSET_TOKEN": ""}):
            with self.assertRaisesRegex(ValueError, "missing local"):
                preflight(model)

    def test_guest_model_name_patch_is_idempotent(self):
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "run_vtrm_eval.py"
            path.write_text("    command = (\n" + TARGET + "\n" + LOOP + "\n    )\n")
            with self.assertRaisesRegex(ValueError, "NOT propagated"):
                check_or_apply(path, False)
            self.assertEqual(check_or_apply(path, True), "PATCHED")
            self.assertEqual(check_or_apply(path, False), "ALREADY_PRESENT")
            self.assertEqual(check_or_apply(path, True), "ALREADY_PRESENT")
            self.assertEqual(path.read_text().count(INSERTED), 1)


if __name__ == "__main__":
    unittest.main()
