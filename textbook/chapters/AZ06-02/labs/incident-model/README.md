# Offline incident and RCA model

This standard-library Python lab evaluates one fully synthetic banking incident. It keeps event time and observation/ingestion time separate, compares concrete hypotheses, requires an evidence-supported causal sequence, and checks a bounded authorization repair against the same payment probe, ledger invariants, idempotency, a negative access test, a stable window, and an RTO target.

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ06-02/labs/incident-model -p "test_*.py" -v
python textbook/chapters/AZ06-02/labs/incident-model/incident_model.py
```

The model is a deterministic teaching contract, not an Azure Monitor, Activity Log, Resource Health, Microsoft Entra, RBAC, Storage, SQL, KQL, or payment application emulator. It makes no Azure request and does not verify any live incident. Its fixture establishes only synthetic evidence and a synthetic counterfactual. The twelve V3 incident specifications and eight mandatory local closures remain separate contracts in `AZURE_SPECIALTY_ROADMAP.md` and `textbook/LIVE_LAB_INDEX.md`.
