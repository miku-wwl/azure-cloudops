# Offline Log Analytics and Application Insights triage model

This standard-library Python lab consumes synthetic workspace-based `AppRequests`, `AppDependencies`, and `AppExceptions` rows. It demonstrates time-bounded grouping, sampled request-count weighting with `ItemCount`, operation-wide grouping by `OperationId`, and direct parent-child checks using `ParentId` and item IDs.

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ05-02/labs/telemetry-triage -p "test_*.py" -v
python textbook/chapters/AZ05-02/labs/telemetry-triage/telemetry_model.py
```

Two companion KQL templates are in `queries/`. They are examples for schema inspection and controlled adaptation; they are not executed against a workspace by the lab. The model does not parse or execute KQL, reproduce Azure sampling/export/ingestion, infer a real root cause, or prove that absent telemetry means no request occurred. `time_minute`, local event IDs, and fixture records are synthetic abstractions, not Azure logs.
