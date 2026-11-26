# Offline Backup and Site Recovery acceptance model

This standard-library Python lab evaluates synthetic recovery cases. It calculates elapsed RPO and RTO from explicit timestamps, then checks the selected result against numeric objectives, expected record count, payload digest, an application probe, and test-failover isolation and cleanup.

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ06-01/labs/recovery-model -p "test_*.py" -v
python textbook/chapters/AZ06-01/labs/recovery-model/recovery_model.py
```

Passing the model means only that the synthetic case meets the coded local contract. It is not Azure Backup or Site Recovery, does not restore a VM or database, does not verify Azure jobs, cannot prove a real RPO/RTO, and does not estimate cost. The case timestamps, consistency labels, hashes, row counts and probes are synthetic. No Azure authentication or request is made.
