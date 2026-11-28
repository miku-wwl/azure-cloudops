# E7 — Twelve incident contracts

**Completed:** 2026-11-27. All twelve contracts from the approved V3 roadmap are documented in [`incidents/CONTRACTS.md`](../../incidents/CONTRACTS.md), with a lecture mapping and index in [`incidents/README.md`](../../incidents/README.md).

Each incident specifies the healthy baseline, target scope, fault mechanism, expected failure category, competing hypotheses, discriminating probes, root-cause evidence, minimal repair, same-probe recovery, negative assertions, cleanup, required permissions, cost assumptions, and actual verification status.

The eight mandatory local scenarios—IR-01, IR-02, IR-05, IR-07, IR-08, IR-10, IR-11 and IR-12—are marked `MANDATORY_LOCAL_E8`. IR-03, IR-04, IR-06 and IR-09 are design-only. Existing Terraform lock/drift evidence from E4 is linked as prior evidence but does not count as an E8 incident closure. Every Azure scenario remains `NOT_RUN`; no live Azure resources or billing data were accessed.

## Verification

- Three contract tests verify the exact twelve IDs, all required fields, lecture mappings, live-not-run markers, and the exact eight mandatory IDs.
- Windows Python 3.13.9 and WSL Python 3.12.3 each passed 510 tests across 24 directories.
- The test result validates contract completeness only. It does not validate any fault, probe, permission, cost, Azure behavior, or local incident recovery.
- E8 execution is now the next gate. The local Kubernetes image-pull requirement still depends on a functioning disposable cluster and container engine; the last checked-in host inventory records that prerequisite as unavailable. Recheck it before IR-07; if it remains unavailable, preserve the scenario as blocked and ask the owner before proposing a substitute.
