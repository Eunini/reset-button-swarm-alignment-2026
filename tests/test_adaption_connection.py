"""Credential boundary checks. All upstream responses are mocked; no real API calls."""
import importlib.util
import json
from pathlib import Path
import threading
import unittest
from unittest.mock import patch
from urllib import request, error

spec = importlib.util.spec_from_file_location("adaption_connection", Path(__file__).resolve().parents[1] / "scripts/adaption_connection.py")
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


class ConnectionTests(unittest.TestCase):
    def setUp(self):
        self.server = module.ConnectionServer(("127.0.0.1", 0), 120)
        self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
        self.thread.start()
        self.base = "http://127.0.0.1:" + str(self.server.server_port)

    def tearDown(self):
        self.server.shutdown()
        self.server.server_close()
        self.thread.join(timeout=2)

    def post(self, path, data, csrf=True):
        headers = {"Content-Type": "application/json"}
        if csrf:
            headers["X-Connection-CSRF"] = self.server.csrf
        req = request.Request(self.base + path, data=json.dumps(data).encode(), headers=headers, method="POST")
        return request.urlopen(req, timeout=2)

    def test_cross_origin_request_cannot_connect(self):
        with patch.object(module, "api_get") as upstream:
            with self.assertRaises(error.HTTPError) as raised:
                self.post("/connect", {"api_key": "unit-test-placeholder"}, csrf=False)
            self.assertEqual(raised.exception.code, 403)
            upstream.assert_not_called()

    def test_response_does_not_return_credential_and_does_not_cache(self):
        with patch.object(module, "api_get", return_value={"data": [{"id": "test-model"}]}):
            with self.post("/connect", {"api_key": "unit-test-placeholder"}) as response:
                body = response.read().decode()
                self.assertNotIn("unit-test-placeholder", body)
                self.assertEqual(response.headers["Cache-Control"], "no-store")
                self.assertTrue(json.loads(body)["connected"])
        with request.urlopen(self.base + "/status") as response:
            value = json.load(response)
            self.assertFalse(value["credential_persisted"])
            self.assertNotIn("key", value)

    def test_paid_operations_are_not_supported(self):
        with patch.object(module, "api_get") as upstream:
            for op in ("responses", "create_autoscientist_run", "invent"):
                with self.assertRaises(error.HTTPError) as raised:
                    self.post("/read", {"operation": op})
                self.assertEqual(raised.exception.code, 400)
            upstream.assert_not_called()

    def test_upstream_failure_body_is_not_echoed(self):
        failure = error.HTTPError("https://example.invalid", 401, "private diagnostic", {}, None)
        with patch.object(module, "api_get", side_effect=failure):
            with self.assertRaises(error.HTTPError) as raised:
                self.post("/connect", {"api_key": "unit-test-placeholder"})
            body = raised.exception.read().decode()
            self.assertNotIn("unit-test-placeholder", body)
            self.assertNotIn("private diagnostic", body)
            self.assertIsNone(self.server.key)

    def test_expired_session_will_not_accept_a_key(self):
        self.server.deadline = 0
        with patch.object(module, "api_get") as upstream:
            with self.assertRaises(error.HTTPError) as raised:
                self.post("/connect", {"api_key": "unit-test-placeholder"})
            self.assertEqual(raised.exception.code, 410)
            upstream.assert_not_called()


if __name__ == "__main__":
    unittest.main()
