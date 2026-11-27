# Offline Log Analytics and Application Insights triage model

This standard-library Python lab consumes synthetic workspace-based `AppRequests`, `AppDependencies`, and `AppExceptions` rows. It demonstrates time-bounded grouping, sampled request-count weighting with `ItemCount`, operation-wide grouping by `OperationId`, and direct parent-child checks using `ParentId` and item IDs.

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ05-02/labs/telemetry-triage -p "test_*.py" -v
python textbook/chapters/AZ05-02/labs/telemetry-triage/telemetry_model.py
```

Seven KQL templates are in `queries/`. The five E6 additions cover failed Azure Activity operations, Heartbeat freshness, request failures, dependency failures, and exception groups. Each file names its table/column assumptions and is checked against the current Microsoft table reference. All seven are source-reviewed templates and **NOT_RUN** against a workspace; workspace schema, permissions and actual syntax execution remain unverified. Treat identifiers, targets and any query output as sensitive operational data.

The Python model does not parse or execute KQL, reproduce Azure sampling/export/ingestion, infer a real root cause, or prove that absent telemetry means no request occurred. `time_minute`, local event IDs, and fixture records are synthetic abstractions, not Azure logs.
