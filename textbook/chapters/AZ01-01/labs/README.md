# AZ01-01 labs

## reliability-model

Run from `textbook/chapters/AZ01-01/labs/reliability-model`:

    python -m unittest -v
    python reliability_model.py

The synthetic JSON fixture treats a critical flow as required AND stages, with OR alternatives inside each stage. Faults explicitly mark synthetic components unavailable. It shows how a serial singleton dependency can defeat replicated APIs and how a single-region topology remains exposed to a regional outage. `NOT_MODELED` means the fixture does not make a claim about that topology/event pair.

The probability formulas assume independent component failures, and the topology matrix is deterministic. Neither is an Azure service or RBAC emulator. This lab does not authenticate, make network calls, inject faults, produce an Azure SLA, measure live SLI, or create resources.

Cloud status: LIVE_NOT_RUN. Local results are changed only from actual test and command output recorded in `textbook/PROGRESS.md`.
