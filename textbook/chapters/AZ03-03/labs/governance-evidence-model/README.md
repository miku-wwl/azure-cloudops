# AZ03-03 offline governance/evidence lab

Run from the repository root:

~~~powershell
python -m unittest discover -s textbook/chapters/AZ03-03/labs/governance-evidence-model -p "test_*.py" -v
python textbook/chapters/AZ03-03/labs/governance-evidence-model/governance_evidence_model.py
~~~

The JSON fixtures are fictional. The model compares three independent questions: Policy effect outcomes for requests and existing resources; Activity Log, resource-log and client-evidence boundaries; and Defender recommendations versus separately configured Policy effects and current plan-price review.

This is not an Azure Policy evaluator, ARM emulator, Activity Log schema validator, Defender API, or pricing calculator. It does not parse policy JSON or aliases, model assignment scope or provider modes, run evaluations or remediation, promise real log delivery, or estimate current prices. It makes no Azure calls, authenticates no identity, and creates no resource. A passing test establishes only the fixture branches.
