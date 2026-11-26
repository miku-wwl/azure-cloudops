import unittest

from dns_model import DNSContext, Endpoint, ModelInputError, evaluate, resolve


ENDPOINT = Endpoint(
    service_fqdn="settlementarchive.blob.core.windows.net",
    private_fqdn="settlementarchive.privatelink.blob.core.windows.net",
    private_ip="10.60.4.7",
    public_ip="198.51.100.26",
    connection_status="Approved",
)


def context(**changes):
    values = {
        "vnet_linked": True,
        "custom_dns": False,
        "forwards_from_linked_vnet": False,
        "private_a_record_present": True,
        "fallback_to_internet": False,
    }
    values.update(changes)
    return DNSContext(**values)


class PrivateDnsModelTests(unittest.TestCase):
    def test_linked_vnet_with_a_record_resolves_to_private_ip(self):
        result = resolve(ENDPOINT, context())
        self.assertEqual((result.kind, result.address), ("PRIVATE_ENDPOINT", "10.60.4.7"))

    def test_unlinked_vnet_uses_public_fixture_answer(self):
        result = resolve(ENDPOINT, context(vnet_linked=False))
        self.assertEqual((result.kind, result.address), ("PUBLIC_ENDPOINT", "198.51.100.26"))

    def test_custom_dns_without_forwarding_does_not_see_private_zone(self):
        result = resolve(ENDPOINT, context(custom_dns=True))
        self.assertEqual(result.kind, "PUBLIC_ENDPOINT")

    def test_custom_dns_forwarded_from_linked_vnet_sees_private_zone(self):
        result = resolve(ENDPOINT, context(custom_dns=True, forwards_from_linked_vnet=True))
        self.assertEqual((result.kind, result.address), ("PRIVATE_ENDPOINT", "10.60.4.7"))

    def test_custom_dns_forwarding_without_zone_link_does_not_see_record(self):
        result = resolve(
            ENDPOINT,
            context(vnet_linked=False, custom_dns=True, forwards_from_linked_vnet=True),
        )
        self.assertEqual(result.kind, "PUBLIC_ENDPOINT")

    def test_linked_zone_without_a_record_returns_nxdomain_by_default(self):
        result = resolve(ENDPOINT, context(private_a_record_present=False))
        self.assertEqual((result.kind, result.address), ("NXDOMAIN", None))

    def test_fallback_to_internet_selects_public_answer_when_a_record_is_missing(self):
        result = resolve(
            ENDPOINT,
            context(private_a_record_present=False, fallback_to_internet=True),
        )
        self.assertEqual((result.kind, result.address), ("PUBLIC_ENDPOINT", "198.51.100.26"))

    def test_private_endpoint_access_can_succeed_when_public_access_is_disabled(self):
        _, outcome = evaluate(
            ENDPOINT, context(), public_network_enabled=False, data_authorized=True
        )
        self.assertEqual(outcome, "PRIVATE_ACCESS_ALLOWED")

    def test_pending_endpoint_blocks_private_path_even_with_private_dns(self):
        pending = Endpoint(**(ENDPOINT.__dict__ | {"connection_status": "Pending"}))
        answer, outcome = evaluate(
            pending, context(), public_network_enabled=False, data_authorized=True
        )
        self.assertEqual(answer.kind, "PRIVATE_ENDPOINT")
        self.assertEqual(outcome, "ENDPOINT_NOT_APPROVED")

    def test_rejected_endpoint_blocks_private_path(self):
        rejected = Endpoint(**(ENDPOINT.__dict__ | {"connection_status": "Rejected"}))
        _, outcome = evaluate(
            rejected, context(), public_network_enabled=True, data_authorized=True
        )
        self.assertEqual(outcome, "ENDPOINT_NOT_APPROVED")

    def test_disconnected_endpoint_blocks_private_path(self):
        disconnected = Endpoint(**(ENDPOINT.__dict__ | {"connection_status": "Disconnected"}))
        _, outcome = evaluate(
            disconnected, context(), public_network_enabled=True, data_authorized=True
        )
        self.assertEqual(outcome, "ENDPOINT_NOT_APPROVED")

    def test_private_dns_does_not_grant_data_plane_authorization(self):
        _, outcome = evaluate(
            ENDPOINT, context(), public_network_enabled=False, data_authorized=False
        )
        self.assertEqual(outcome, "DATA_PLANE_AUTH_DENIED")

    def test_public_answer_is_rejected_when_public_access_is_disabled(self):
        _, outcome = evaluate(
            ENDPOINT,
            context(vnet_linked=False),
            public_network_enabled=False,
            data_authorized=True,
        )
        self.assertEqual(outcome, "PUBLIC_NETWORK_ACCESS_DISABLED")

    def test_public_path_can_succeed_when_network_and_data_authorization_allow(self):
        _, outcome = evaluate(
            ENDPOINT,
            context(vnet_linked=False),
            public_network_enabled=True,
            data_authorized=True,
        )
        self.assertEqual(outcome, "PUBLIC_ACCESS_ALLOWED")

    def test_pending_private_endpoint_does_not_block_a_separate_public_path(self):
        pending = Endpoint(**(ENDPOINT.__dict__ | {"connection_status": "Pending"}))
        _, outcome = evaluate(
            pending,
            context(vnet_linked=False),
            public_network_enabled=True,
            data_authorized=True,
        )
        self.assertEqual(outcome, "PUBLIC_ACCESS_ALLOWED")

    def test_service_hostname_is_preserved_for_client_and_tls(self):
        result = resolve(ENDPOINT, context())
        self.assertEqual(result.service_hostname, "settlementarchive.blob.core.windows.net")
        self.assertNotEqual(result.service_hostname, ENDPOINT.private_fqdn)

    def test_endpoint_rejects_mismatched_private_dns_name(self):
        with self.assertRaises(ModelInputError):
            Endpoint(**(ENDPOINT.__dict__ | {"private_fqdn": "other.privatelink.blob.core.windows.net"}))

    def test_endpoint_rejects_invalid_status(self):
        with self.assertRaises(ModelInputError):
            Endpoint(**(ENDPOINT.__dict__ | {"connection_status": "Creating"}))


if __name__ == "__main__":
    unittest.main()
