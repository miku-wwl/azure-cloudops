# Live lab index

The [E9 live-lab catalogue](LIVE_LAB_CATALOGUE.md) contains the required per-lab architecture, permissions, region/SKU, Terraform coverage, cost status, runtime, probes, recovery, teardown, residual checks and delayed-billing checks.

| Incident | Local evidence | Live Azure state | E9 classification |
|---|---|---|---|
| IR-01 | `LOCAL_VERIFIED` | `NOT_RUN` | Budget-deferred |
| IR-02 | `LOCAL_VERIFIED` | `NOT_RUN` | Potentially zero-cost live mutation, only on existing approved lab network |
| IR-03 | `CONTRACTED_NOT_RUN` | `NOT_RUN` | Potentially zero-cost live mutation, only on existing approved lab route table |
| IR-04 | `CONTRACTED_NOT_RUN` | `NOT_RUN` | Budget-deferred |
| IR-05 | `LOCAL_VERIFIED` | `NOT_RUN` | Permission-deferred |
| IR-06 | `CONTRACTED_NOT_RUN` | `NOT_RUN` | Budget-deferred |
| IR-07 | `LOCAL_VERIFIED` | `NOT_RUN` | Budget-deferred |
| IR-08 | `LOCAL_VERIFIED` | `NOT_RUN` | Budget-deferred |
| IR-09 | `CONTRACTED_NOT_RUN` | `NOT_RUN` | Permission-deferred |
| IR-10 | `LOCAL_VERIFIED` | `NOT_RUN` | Budget-deferred |
| IR-11 | `LOCAL_VERIFIED` | `NOT_RUN` | Potentially zero-cost only if the exact App Service F1 offer and quotas are confirmed |
| IR-12 | `LOCAL_VERIFIED` | `NOT_RUN` | Budget-deferred |

The eight mandatory local contracts are verified at E8 with evidence in [`E8_LOCAL_INCIDENTS.md`](E8_LOCAL_INCIDENTS.md). Independent second-cycle replay evidence is in [`E10_INDEPENDENT_REPLAY.md`](E10_INDEPENDENT_REPLAY.md). Local execution does not prove Azure behavior. E9 preparation does not authorize resource mutation. Every live experiment remains gated by Stage 3 L0, specific owner authorization, an exact resource allowlist, reliable gross-cost estimate at or below USD 0.70 cumulative, USD 0.30 contingency, and verified teardown.
