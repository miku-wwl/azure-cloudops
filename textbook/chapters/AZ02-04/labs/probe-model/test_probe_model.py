import unittest

from probe_model import (
    Backend,
    ModelInputError,
    appgw_healthy,
    backend_from_dict,
    front_door_healthy,
    lb_healthy,
    select_priority_candidates,
)


def backend(**changes):
    values = {
        "name": "pay-east",
        "priority": 1,
        "tcp_open": True,
        "responses": {"/": 302, "/ready": 200},
        "afd_samples": (302, 302, 302),
        "backend_tls_valid": True,
        "enabled": True,
    }
    values.update(changes)
    return Backend(**values)


class ProbeModelTests(unittest.TestCase):
    def test_open_tcp_listener_is_healthy_to_load_balancer_tcp_probe(self):
        self.assertTrue(lb_healthy(backend(), "TCP"))

    def test_tcp_probe_fails_when_listener_is_closed(self):
        self.assertFalse(lb_healthy(backend(tcp_open=False), "TCP"))

    def test_load_balancer_http_probe_requires_exact_200(self):
        self.assertFalse(lb_healthy(backend(), "HTTP", "/"))
        self.assertTrue(lb_healthy(backend(), "HTTP", "/ready"))

    def test_load_balancer_http_probe_rejects_redirect(self):
        self.assertFalse(lb_healthy(backend(responses={"/": 302}), "HTTP"))

    def test_load_balancer_http_probe_rejects_204_and_503(self):
        for status in (204, 302, 503):
            with self.subTest(status=status):
                self.assertFalse(lb_healthy(backend(responses={"/": status}), "HTTP"))

    def test_app_gateway_default_accepts_redirect_in_200_to_399(self):
        self.assertTrue(appgw_healthy(backend(), path="/"))

    def test_app_gateway_default_rejects_400_and_503(self):
        for status in (400, 503):
            with self.subTest(status=status):
                self.assertFalse(appgw_healthy(backend(responses={"/": status}), path="/"))

    def test_app_gateway_probe_uses_selected_path(self):
        self.assertTrue(appgw_healthy(backend(), path="/ready"))
        self.assertFalse(appgw_healthy(backend(responses={"/": 200}), path="/ready"))

    def test_app_gateway_custom_range_can_accept_deliberate_status(self):
        self.assertTrue(appgw_healthy(backend(), accepted_range=(200, 399)))
        self.assertTrue(
            appgw_healthy(backend(responses={"/": 403}), accepted_range=(200, 403))
        )
        self.assertFalse(appgw_healthy(backend(responses={"/": 403})))

    def test_app_gateway_https_requires_tls_validity_assertion(self):
        self.assertFalse(appgw_healthy(backend(backend_tls_valid=False), path="/ready", protocol="HTTPS"))
        self.assertTrue(appgw_healthy(backend(), path="/ready", protocol="HTTPS"))

    def test_app_gateway_requires_probe_path_to_have_tcp_connection(self):
        self.assertFalse(appgw_healthy(backend(tcp_open=False), path="/ready"))

    def test_front_door_requires_exactly_200_in_configured_window(self):
        self.assertFalse(front_door_healthy((302, 302, 302), sample_size=3, successful_required=2))
        self.assertTrue(front_door_healthy((503, 200, 200), sample_size=3, successful_required=2))

    def test_front_door_uses_last_n_responses(self):
        self.assertTrue(front_door_healthy((503, 503, 200, 200), sample_size=3, successful_required=2))
        self.assertFalse(front_door_healthy((200, 200, 503, 503), sample_size=3, successful_required=2))

    def test_front_door_is_unhealthy_when_window_is_incomplete(self):
        self.assertFalse(front_door_healthy((200,), sample_size=3, successful_required=1))

    def test_priority_selects_lowest_number_among_healthy_origins(self):
        east = backend(name="pay-east", priority=1)
        west = backend(name="pay-west", priority=2)
        decision = select_priority_candidates([east, west], {"pay-east": False, "pay-west": True})
        self.assertEqual(decision.candidates, ("pay-west",))
        self.assertFalse(decision.all_unhealthy_fallback)

    def test_same_best_priority_can_have_multiple_candidates(self):
        east = backend(name="pay-east", priority=1)
        west = backend(name="pay-west", priority=1)
        decision = select_priority_candidates([east, west], {"pay-east": True, "pay-west": True})
        self.assertEqual(decision.candidates, ("pay-east", "pay-west"))

    def test_all_unhealthy_fallback_returns_enabled_origins(self):
        east = backend(name="pay-east", priority=1)
        west = backend(name="pay-west", priority=2)
        disabled = backend(name="pay-disabled", priority=1, enabled=False)
        decision = select_priority_candidates([east, west, disabled], {})
        self.assertEqual(decision.candidates, ("pay-east", "pay-west"))
        self.assertTrue(decision.all_unhealthy_fallback)

    def test_invalid_protocol_is_rejected_instead_of_guessed(self):
        with self.assertRaises(ModelInputError):
            lb_healthy(backend(), "UDP")
        with self.assertRaises(ModelInputError):
            lb_healthy(backend(), "HTTPS")

    def test_invalid_front_door_threshold_is_rejected(self):
        with self.assertRaises(ModelInputError):
            front_door_healthy((200,), sample_size=2, successful_required=3)

    def test_fixture_status_and_priority_are_validated(self):
        raw = {
            "name": "bad",
            "priority": 0,
            "tcp_open": True,
            "responses": {"/": 600},
            "afd_samples": [200],
        }
        with self.assertRaises(ModelInputError):
            backend_from_dict(raw)


if __name__ == "__main__":
    unittest.main()
