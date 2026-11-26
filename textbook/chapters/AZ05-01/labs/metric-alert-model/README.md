# Azure Monitor metric alert model

This deterministic Python lab evaluates synthetic metric points with a chosen aggregation, time window, dimension split, static threshold, alert state and notification-suppression flag. A small history gate illustrates why a dynamic threshold may not yet have enough training data.

The eleven fixtures contrast an Average rollup with Maximum and per-server splitting; Count of records; overlapping lookback windows; stateful fire/resolve/re-fire transitions; stateless repeated notifications; notification suppression while the condition remains fired; and three dynamic-history readiness cases. Fixture expectations are part of the test suite.

Run from the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ05-01/labs/metric-alert-model -p "test_*.py" -v
python textbook/chapters/AZ05-01/labs/metric-alert-model/metric_alert_model.py
```

The model is intentionally narrower than Azure Monitor. It does not simulate metric-provider pre-aggregation, ingestion delay, service-specific metric availability, missing-data policy, dynamic-threshold ML, alert service timing, or real action groups. The data is synthetic; the lab does not sign in, query Azure Metrics, create alerts, or send notifications.
