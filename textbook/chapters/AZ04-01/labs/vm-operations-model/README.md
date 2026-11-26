# AZ04-01 offline VM operations model

This lab is a deterministic teaching fixture. It uses only the checked-in JSON scenarios and standard-library Python. It does not invoke Azure CLI, the Azure SDK, IMDS, an Azure Monitor endpoint, a subscription, or the network.

## Run

From the repository root:

~~~powershell
python -m unittest discover -s textbook/chapters/AZ04-01/labs/vm-operations-model -p "test_*.py" -v
python textbook/chapters/AZ04-01/labs/vm-operations-model/vm_operations_model.py
~~~

## Model boundary

- Power and provisioning state are independent strings; the fixture does not enforce Azure state transitions.
- Compute billing labels cover the states listed in this small model. Attached resource charges are a separate possibility, not an estimate.
- Guest metrics are treated as collected only when both AMA and a DCR association are represented. This omits configuration nuance.
- VMSS policies are conceptual. The fixture is not a VMSS API contract and marks Flexible policy support for recheck.
- Disk calculations cover one uncached managed disk with no cache, burst, queueing, or shared multi-disk contention. IOPS and throughput are separate.
- Boot diagnostics evidence does not establish application availability.
