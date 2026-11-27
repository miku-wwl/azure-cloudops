from __future__ import annotations

import json
import socket
import sys
import threading
import unittest
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from unittest import mock

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import network_probe  # noqa: E402


class NetworkProbeTests(unittest.TestCase):
    def test_dns_wait_is_bounded_even_if_os_resolver_is_still_running(self) -> None:
        entered = threading.Event()
        release = threading.Event()

        def slow_lookup(*_args: object, **_kwargs: object) -> list[object]:
            entered.set()
            release.wait(timeout=1)
            return []

        with mock.patch.object(network_probe.socket, "getaddrinfo", side_effect=slow_lookup):
            try:
                with self.assertRaises(network_probe.ProbeError) as raised:
                    network_probe.resolve("resolver-test.invalid", 443, timeout=0.02)
                self.assertEqual(str(raised.exception), "DNS_TIMEOUT")
                self.assertTrue(entered.wait(timeout=0.2))
            finally:
                release.set()

    def test_tls_handshake_failure_is_distinguished_from_tcp_failure(self) -> None:
        connected_socket = socket.socket()
        context = mock.Mock()
        context.wrap_socket.side_effect = TimeoutError("synthetic handshake timeout")
        try:
            with mock.patch.object(network_probe, "resolve", return_value=[(socket.AF_INET, ("127.0.0.1", 443))]):
                with mock.patch.object(network_probe, "_connect_any", return_value=(connected_socket, [])):
                    with mock.patch.object(network_probe.ssl, "create_default_context", return_value=context):
                        result = network_probe.probe_tcp_tls("example.invalid", 443, timeout=1, tls=True)
        finally:
            connected_socket.close()
        self.assertTrue(result["tcp_connected"])
        self.assertEqual(result["error"], "TLS_VERIFICATION_FAILED")

    def test_loopback_tcp_probe_redacts_addresses_by_default(self) -> None:
        listener = socket.socket()
        listener.bind(("127.0.0.1", 0))
        listener.listen(1)
        port = listener.getsockname()[1]
        accepted: list[bool] = []

        def accept_one() -> None:
            connection, _address = listener.accept()
            accepted.append(True)
            connection.close()
            listener.close()

        worker = threading.Thread(target=accept_one, daemon=True)
        worker.start()
        result = network_probe.probe_tcp_tls("localhost", port, timeout=2, tls=False)
        worker.join(timeout=2)
        self.assertTrue(result["tcp_connected"])
        self.assertEqual(result["address_redaction"], "sha256-prefix")
        self.assertNotIn("127.0.0.1", json.dumps(result))
        self.assertTrue(accepted)

    def test_http_health_uses_head_and_reads_no_body(self) -> None:
        state = {"method": None}

        class Handler(BaseHTTPRequestHandler):
            def do_HEAD(self) -> None:  # noqa: N802 - stdlib protocol method
                state["method"] = "HEAD"
                self.send_response(204)
                self.end_headers()

            def do_GET(self) -> None:  # noqa: N802 - fail the test if the probe reads a body
                state["method"] = "GET"
                self.send_response(200)
                self.end_headers()
                self.wfile.write(b"body-must-not-be-read")

            def log_message(self, _format: str, *_args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            result = network_probe.probe_http_head(f"http://127.0.0.1:{server.server_port}/health", timeout=2)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)
        self.assertEqual(state["method"], "HEAD")
        self.assertTrue(result["healthy"])
        self.assertEqual(result["status_code"], 204)
        self.assertFalse(result["body_read"])
        self.assertFalse(result["redirects_followed"])

    def test_http_redirect_is_reported_without_following_target(self) -> None:
        state = {"requests": 0}

        class Handler(BaseHTTPRequestHandler):
            def do_HEAD(self) -> None:  # noqa: N802 - stdlib protocol method
                state["requests"] += 1
                self.send_response(302)
                self.send_header("Location", "/target")
                self.end_headers()

            def log_message(self, _format: str, *_args: object) -> None:
                return

        server = ThreadingHTTPServer(("127.0.0.1", 0), Handler)
        worker = threading.Thread(target=server.serve_forever, daemon=True)
        worker.start()
        try:
            result = network_probe.probe_http_head(f"http://127.0.0.1:{server.server_port}/health", timeout=2)
        finally:
            server.shutdown()
            server.server_close()
            worker.join(timeout=2)
        self.assertEqual(state["requests"], 1)
        self.assertEqual(result["status_code"], 302)
        self.assertFalse(result["healthy"])
        self.assertFalse(result["redirects_followed"])

    def test_http_rejects_credentials_query_and_fragment(self) -> None:
        for url in (
            "https://user:secret@example.test/health",
            "https://example.test/health?token=secret",
            "https://example.test/health#fragment",
        ):
            with self.subTest(url=url):
                with self.assertRaises(network_probe.ProbeError):
                    network_probe.probe_http_head(url, timeout=1)


if __name__ == "__main__":
    unittest.main()
