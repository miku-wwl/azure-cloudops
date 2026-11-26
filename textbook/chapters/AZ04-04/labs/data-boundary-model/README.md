# Azure Storage and SQL data-boundary model

This deterministic Python lab classifies synthetic read and recovery cases. It models endpoint/DNS selection, public and private network gates, Storage data-plane authorization, SQL authentication and database authorization, and a narrow set of Blob and Azure SQL Database recovery choices.

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ04-04/labs/data-boundary-model -p "test_*.py" -v
python textbook/chapters/AZ04-04/labs/data-boundary-model/azure_data_boundary_model.py
```

The JSON values are synthetic. The lab does not contact Azure, obtain tokens, read local credentials, send DNS or network probes, connect to SQL, or change data. It is not an Azure service emulator and cannot prove that a real identity, endpoint, backup, restore point, RTO, or RPO exists. A live restore or endpoint change requires the later project authorization, scope, and cost gates.
