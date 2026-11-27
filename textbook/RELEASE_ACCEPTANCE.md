# Azure CloudOps Textbook V1 — B9 release acceptance

- Decision: **TEXTBOOK_V1_RELEASE_READY**.
- Acceptance date: 2026-11-27 (Pacific/Auckland).
- Scope: Stage 1 textbook engineering and publication only. This does not assert Azure deployment readiness, Stage 2 lab acceptance, or live Azure validation.
- Release target: `main`, using the project's approved Azure V3 baseline and subsequent lecture checkpoints.

## Technical and editorial completeness

- All 23 curriculum chapters have a Markdown source, per-chapter acceptance record, and matching PDF: 23/23/23. The final PDF package contains exactly 23 independently built PDFs.
- `SOURCE_MAP.md` has a section for every lecture and maps key claims to current primary sources, local implementations, or documented limitations. Chapter acceptance dates and source dates are recorded.
- Every chapter has completed its individual lecture gate. The final `FIN-01` chapter adds the cost estimation, Cost Management, budget, cost allocation/tag, commitments, and verified resource-cost recovery material; its nine-page PDF and all page layouts were reviewed at 88 and 140 DPI.
- Offline Python verification passed on Windows and the `devops-lab` WSL distribution: 402 tests across 22 test directories, zero failing directories. The FIN-01 synthetic lab accounts for 27 of those tests.
- Terraform 1.15.5 passed repository-wide `fmt -check`, backend-free `init` and `validate` in all three roots, and five Terraform test cases across two mock/local roots. No Azure provider was authenticated and no backend was contacted.
- The package builder verified both archives: the PDF ZIP has 23 files byte-for-byte identical to `textbook/dist/pdf/`; the source ZIP has 289 files byte-for-byte identical to the included `textbook/` source set. Verification passed from Windows and the `devops-lab` WSL distribution.
- PDF package SHA-256: `265DA32EE3CFAE05E14A16C9D3B2F80A0D5EC8294FD0B71731CBDD42F456B8FF` (27,790,777 bytes). The package outputs are `textbook/dist/Azure-CloudOps-PDF.zip` and `textbook/dist/Azure-CloudOps-Sources.zip`.

## Explicit limits

- This acceptance is based on local static/build/visual and synthetic lab evidence. No Azure authentication, account or subscription enumeration, Cost Management/billing query, resource inventory, deployment, resource mutation, DNS/network test or cloud cleanup was performed. Actual cumulative Azure spend remains `NOT_VERIFIED`.
- The cumulative Azure resource-cost ceiling remains USD 1.00 with a conservative USD 0.70 planning threshold. No live query batch or resource experiment has a reviewed estimate or authorization. Azure budget alerts are not hard spending limits.
- The optional local sensitive-pattern scan was skipped because `textbook/tools/sensitive.local.txt` is not configured. The package builder's file-count, archive-integrity and byte-for-byte content checks passed.
- Docker Desktop's Linux engine was unavailable at the AZ04-03 checkpoint, so a local kind cluster was not run. The affected lab remains a deterministic synthetic readiness model with that limit recorded in its chapter acceptance.
- No PDF/UA, print-proof, or external production CI result is claimed. The publisher continues to emit a non-blocking Pillow `Image.getdata()` deprecation warning.

## Release handoff

Stage 1 B9 is accepted. Continue automatically to Stage 2 E0, the independent audit of chapter claims, experiments, Terraform, tests, permissions, recovery and cleanup. Preserve V1 PDFs as the accepted Stage 1 release; if an audit correction changes a chapter or its PDF, record the correction and rerun package verification before shipping the revised artifact. Stage 3 remains gated by L0 and requires specific scope, separate authorization and a reliable cumulative cost review.
