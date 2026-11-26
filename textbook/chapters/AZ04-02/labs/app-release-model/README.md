# App Service / Container Apps release model

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ04-02/labs/app-release-model -p "test_*.py" -v
python textbook/chapters/AZ04-02/labs/app-release-model/app_release_model.py
```

The JSON fixture is deterministic and local. It models selected rules documented in Microsoft Learn: App Service swap warm-up status filtering and slot identity association; Container Apps template versus application scopes; single/multiple revision cutover; and route-only rollback. The multiple-revision readiness policy in this model is a local release guard, because the Azure documentation tells operators to wait for readiness but does not claim that manual traffic edits are technically blocked.

This is not an Azure API, hosting, networking, identity-token, billing, or performance emulator. It performs no Azure CLI, SDK, subscription, token, endpoint, container, or network operation. Results are not live service evidence.