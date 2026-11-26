import unittest

from terraform_model import (
    ModelError,
    ResourceBinding,
    choose_provider,
    classify_change,
    import_existing,
    topological_order,
    validate_bindings,
)


class GraphTests(unittest.TestCase):
    def test_dependency_first_order_is_stable(self):
        nodes = {"vnet", "subnet", "private-endpoint", "dns"}
        edges = {("vnet", "subnet"), ("subnet", "private-endpoint"), ("dns", "private-endpoint")}
        order = topological_order(nodes, edges)
        self.assertLess(order.index("vnet"), order.index("subnet"))
        self.assertLess(order.index("subnet"), order.index("private-endpoint"))
        self.assertLess(order.index("dns"), order.index("private-endpoint"))
        self.assertEqual(order, topological_order(nodes, edges))

    def test_independent_nodes_are_all_included(self):
        self.assertEqual(["a", "b"], topological_order({"b", "a"}, set()))

    def test_cycle_is_rejected(self):
        with self.assertRaisesRegex(ModelError, "cycle"):
            topological_order({"a", "b"}, {("a", "b"), ("b", "a")})

    def test_unknown_dependency_is_rejected(self):
        with self.assertRaisesRegex(ModelError, "unknown graph"):
            topological_order({"a"}, {("missing", "a")})


class ProviderTests(unittest.TestCase):
    def test_typed_resource_selects_azurerm(self):
        self.assertEqual("azurerm", choose_provider("azurerm_storage_account"))

    def test_generic_arm_resource_selects_azapi(self):
        self.assertEqual("azapi", choose_provider("azapi_resource"))

    def test_explicit_provider_is_preserved(self):
        self.assertEqual("azapi", choose_provider("azurerm_example", "azapi"))

    def test_unknown_provider_is_rejected(self):
        with self.assertRaisesRegex(ModelError, "azurerm or azapi"):
            choose_provider("custom_resource", "custom")


class StateBindingTests(unittest.TestCase):
    def test_unique_address_and_remote_binding_passes(self):
        validate_bindings([
            ResourceBinding("azurerm_vnet.main", "azurerm", "/vnet/1"),
            ResourceBinding("azapi_resource.preview", "azapi", "/resource/2"),
        ])

    def test_duplicate_address_is_rejected(self):
        bindings = [
            ResourceBinding("resource.shared", "azurerm", "/resource/1"),
            ResourceBinding("resource.shared", "azapi", "/resource/2"),
        ]
        with self.assertRaisesRegex(ModelError, "address"):
            validate_bindings(bindings)

    def test_duplicate_remote_object_is_rejected(self):
        bindings = [
            ResourceBinding("azurerm_storage.logs", "azurerm", "/storage/1"),
            ResourceBinding("azapi_resource.logs", "azapi", "/storage/1"),
        ]
        with self.assertRaisesRegex(ModelError, "remote object"):
            validate_bindings(bindings)

    def test_empty_binding_field_is_rejected(self):
        with self.assertRaisesRegex(ModelError, "required"):
            validate_bindings([ResourceBinding("", "azurerm", "/resource/1")])


class LifecycleTests(unittest.TestCase):
    def test_missing_before_means_create(self):
        self.assertEqual("create", classify_change(None, {"name": "x"}).action)

    def test_missing_after_means_destroy(self):
        self.assertEqual("destroy", classify_change({"name": "x"}, None).action)

    def test_prevent_destroy_blocks_removal(self):
        with self.assertRaisesRegex(ModelError, "prevent_destroy"):
            classify_change({"name": "x"}, None, prevent_destroy=True)

    def test_same_configuration_is_noop(self):
        self.assertEqual("no-op", classify_change({"name": "x"}, {"name": "x"}).action)

    def test_changed_mutable_field_is_update(self):
        plan = classify_change({"tags": {"env": "dev"}}, {"tags": {"env": "test"}})
        self.assertEqual(("tags",), plan.changed_fields)
        self.assertEqual("update", plan.action)

    def test_force_new_field_means_replacement(self):
        plan = classify_change({"name": "old"}, {"name": "new"}, force_new={"name"})
        self.assertEqual("replace", plan.action)

    def test_create_before_destroy_changes_order_label_only(self):
        plan = classify_change(
            {"name": "old"}, {"name": "new"},
            force_new={"name"}, create_before_destroy=True,
        )
        self.assertEqual("replace-cbd", plan.action)

    def test_ignore_changes_hides_only_declared_field(self):
        plan = classify_change(
            {"tags": "manual", "size": "small"},
            {"tags": "desired", "size": "large"},
            ignore_changes={"tags"},
        )
        self.assertEqual(("size",), plan.changed_fields)
        self.assertEqual("update", plan.action)


class ImportTests(unittest.TestCase):
    def test_existing_remote_object_proposes_import(self):
        plan = import_existing(
            remote_id="/storage/1", destination="azurerm_storage.logs",
            remote_catalog={"/storage/1"}, bindings=[], provider="azurerm",
        )
        self.assertEqual("import", plan.action)

    def test_import_does_not_offer_create_action(self):
        plan = import_existing(
            remote_id="/storage/1", destination="azurerm_storage.logs",
            remote_catalog={"/storage/1"}, bindings=[], provider="azurerm",
        )
        self.assertNotEqual("create", plan.action)

    def test_missing_remote_id_is_not_created(self):
        with self.assertRaisesRegex(ModelError, "absent"):
            import_existing(
                remote_id="/storage/missing", destination="azurerm_storage.logs",
                remote_catalog=set(), bindings=[], provider="azurerm",
            )

    def test_import_same_address_is_idempotent(self):
        binding = ResourceBinding("azurerm_storage.logs", "azurerm", "/storage/1")
        plan = import_existing(
            remote_id="/storage/1", destination=binding.address,
            remote_catalog={"/storage/1"}, bindings=[binding], provider="azurerm",
        )
        self.assertEqual("already-bound", plan.action)

    def test_import_duplicate_remote_at_another_address_is_rejected(self):
        binding = ResourceBinding("azurerm_storage.logs", "azurerm", "/storage/1")
        with self.assertRaisesRegex(ModelError, "already bound"):
            import_existing(
                remote_id="/storage/1", destination="azapi_resource.logs",
                remote_catalog={"/storage/1"}, bindings=[binding], provider="azapi",
            )

    def test_import_empty_inputs_are_rejected(self):
        with self.assertRaisesRegex(ModelError, "required"):
            import_existing(
                remote_id="", destination="address",
                remote_catalog=set(), bindings=[], provider="azurerm",
            )


if __name__ == "__main__":
    unittest.main()
