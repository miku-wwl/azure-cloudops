# AZ06-02 Acceptance — Incident Response, RCA and Integrated Banking Case

- Status: ACCEPTED for the offline lecture gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 18 / 23; phase B6 is complete.

## Publication artifact

- PDF: `textbook/dist/pdf/AZ06-02_incident-response-rca-integrated-banking-case.pdf`
- Pages: 7; size: 1,901,077 bytes.
- SHA-256: `c114b02270541c383b210c6dbb904aeb22416f745aeb20b3b19f3fb45e11b35b`.
- Publisher QA: 9,189 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: 20% cover, 96%, 96%, 97%, 93%, 98%, 86%.
- Every page was rendered and visually reviewed at 88 and 140 DPI.

## Technical and teaching evidence

- Five original editable SVG figures cover incident command, evidence timelines, competing hypotheses, a synthetic causal chain, and bounded repair.
- The standard-library `incident-model` lab contains one synthetic banking incident and 30 local unit tests.
- The model preserves event and observation/ingestion times separately; requires evidence of the known-good baseline, release identity change, correlated Storage 403, token audience, principal mapping and missing data role; distinguishes `unknown` from disproven; and will not treat a platform health snapshot as proof that no Azure issue exists.
- The repair gate accepts only the synthetic `payments-mi-v2` principal, `Storage Blob Data Reader`, the exact synthetic `rates` container scope, and a recorded approval. Recovery must reuse the baseline transfer probe, verify Storage and ledger results, preserve idempotency and unrelated-scope denial, drain the queue, remain stable for five minutes, and meet the case RTO target.
- The fixture reports a synthetic 18-minute interval from first failed request to stable verified service and a one-minute alert delay. These are fixture measurements only.
- Full offline suites passed on Windows and in WSL: 310 tests across 18 lab directories in each environment.
- Microsoft Learn references and section-level claim mapping are recorded in `textbook/SOURCE_MAP.md`.

## Scope and limits

- This lab is a deterministic local teaching model, not Azure Monitor/KQL, Activity Log, Resource Health, Microsoft Entra, RBAC propagation, Azure Storage, SQL or payment-service emulation. No actual incident has been diagnosed or recovered.
- The chapter maps all twelve V3 incident IDs but does not mark any of the eight mandatory local incident contracts complete. Those require their own controlled injection, expected failure, diagnosis, repair, same-probe verification and cleanup.
- No Azure sign-in, identity/account/context enumeration, telemetry query, resource operation, network probe, role assignment, deployment, or billing query was performed.
- Actual cumulative Azure spend remains `NOT_VERIFIED`. Offline tests made no Azure request and created no project Azure resource charge.
- Stage 2 readiness engineering and Stage 3 authorization/cost gates remain outstanding for the overall project.

## Reproduction

From the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ06-02/labs/incident-model -p "test_*.py" -v
python textbook/chapters/AZ06-02/labs/incident-model/incident_model.py
python textbook/tools/build.py AZ06-02
```

The full Windows and WSL suite commands and observed results are summarized in `textbook/PROGRESS.md` and `textbook/VERIFICATION_MATRIX.md`.
