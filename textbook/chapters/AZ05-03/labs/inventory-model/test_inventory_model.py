"""Unit tests for the offline synthetic inventory model."""

from __future__ import annotations

import unittest

from inventory_model import audit_pages, load_fixture, page_by_offset, paginate_stable, select_visible_resources


class InventoryModelTests(unittest.TestCase):
    def setUp(self):
        self.data = load_fixture()

    def test_requested_scope_and_readable_rows_are_applied(self):
        rows = select_visible_resources(self.data["resources"], ["sub-a", "sub-b"])
        self.assertEqual({"sub-a", "sub-b"}, {row["subscription_id"] for row in rows})
        self.assertTrue(all(row["readable"] for row in rows))

    def test_unrequested_subscription_is_excluded(self):
        rows = select_visible_resources(self.data["resources"], ["sub-a"])
        self.assertEqual({"sub-a"}, {row["subscription_id"] for row in rows})

    def test_unreadable_objects_are_omitted(self):
        rows = select_visible_resources(self.data["resources"], ["sub-a", "sub-b", "sub-c"])
        self.assertEqual(5, len(rows))
        self.assertNotIn("sql01", {row["name"] for row in rows})
        self.assertNotIn("keys01", {row["name"] for row in rows})

    def test_empty_requested_scope_returns_no_rows(self):
        self.assertEqual([], select_visible_resources(self.data["resources"], []))

    def test_visible_rows_are_sorted_by_resource_id(self):
        rows = select_visible_resources(self.data["resources"], self.data["requested_subscriptions"])
        self.assertEqual(sorted(row["id"].casefold() for row in rows),
                         [row["id"].casefold() for row in rows])

    def test_static_pages_cover_every_expected_id_once(self):
        rows = select_visible_resources(self.data["resources"], self.data["requested_subscriptions"])
        pages = paginate_stable(rows, page_size=2)
        report = audit_pages(pages, [row["id"] for row in rows])
        self.assertEqual(5, report["row_count"])
        self.assertEqual(5, report["unique_count"])
        self.assertEqual([], report["duplicate_ids"])
        self.assertEqual([], report["missing_ids"])
        self.assertEqual([], report["unexpected_ids"])

    def test_page_limit_splits_at_requested_size(self):
        pages = paginate_stable(self.data["resources"], page_size=2)
        self.assertTrue(all(len(page) <= 2 for page in pages))
        self.assertEqual([2, 2, 2, 1], [len(page) for page in pages])

    def test_empty_pagination_has_no_empty_page(self):
        self.assertEqual([], paginate_stable([], page_size=2))

    def test_invalid_page_size_is_rejected(self):
        for size in (0, -1, True, 1.5):
            with self.subTest(size=size), self.assertRaises(ValueError):
                paginate_stable([], page_size=size)

    def test_invalid_offset_is_rejected(self):
        for offset in (-1, True, 1.5):
            with self.subTest(offset=offset), self.assertRaises(ValueError):
                page_by_offset([], offset=offset, page_size=1)

    def test_audit_detects_duplicate_ids(self):
        rows = self.data["resources"][:2]
        report = audit_pages([[rows[0]], [rows[0], rows[1]]], [rows[0]["id"], rows[1]["id"]])
        self.assertEqual([rows[0]["id"]], report["duplicate_ids"])

    def test_audit_detects_missing_and_unexpected_ids(self):
        expected = [row["id"] for row in self.data["resources"][:2]]
        observed = [{"id": "synthetic-unexpected-id"}]
        report = audit_pages([observed], expected)
        self.assertEqual(sorted(expected), report["missing_ids"])
        self.assertEqual(["synthetic-unexpected-id"], report["unexpected_ids"])

    def test_deletion_between_offset_pages_can_skip_a_resource(self):
        resources = [{"id": f"id-{index}"} for index in range(1, 6)]
        first_page = page_by_offset(resources, offset=0, page_size=2)
        changed = [row for row in resources if row["id"] != "id-1"]
        second_page = page_by_offset(changed, offset=2, page_size=2)
        report = audit_pages([first_page, second_page], [row["id"] for row in resources])
        self.assertEqual(["id-3"], report["missing_ids"])


if __name__ == "__main__":
    unittest.main()
