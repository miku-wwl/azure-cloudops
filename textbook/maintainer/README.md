# Maintainer archive

This directory holds the source maps, lecture acceptance records and engineering history used to maintain the publication. The reader-facing publication remains the 23 PDFs in the PDF archive.

## Editorial and lecture records

- [V1.0.1 textbook refinement review](V1_0_1_TEXTBOOK_REVIEW.md) — the accepted technical review and lecture-by-lecture configuration coverage.
- [Final editorial freeze](EDITORIAL_FREEZE.md) — cleanup scope, source and publication QA, and preservation notes.
- [Per-lecture acceptance records](lecture-acceptance/) — source, experiment and acceptance history.
- [Source-to-claim map](SOURCE_MAP.md) — primary references and evidence classification.
- [Future Azure exercise catalogue](LIVE_LAB_CATALOGUE.md) — scope, permissions, cost notes and recovery conditions for future exercises.

## Engineering and release history

These records preserve previously accepted engineering stages, observations and operational boundaries. Historical status refers to the evidence available when each record was written.

- [Project progress history](history/PROJECT_PROGRESS_HISTORY.md)
- [Final engineering acceptance](history/FINAL_ACCEPTANCE_REPORT.md)
- [Release acceptance](history/RELEASE_ACCEPTANCE.md)
- [Verification matrix](history/VERIFICATION_MATRIX.md)
- [Cost ledger](history/COST_LEDGER.md)
- [Read-only Azure preflight](history/L0_READ_ONLY_PREFLIGHT.md)
- [Incident contracts and evidence](../incidents/README.md)
- [Architecture decisions](../architecture/README.md)
- Local substrate and delivery records: [E2](history/E2_LOCAL_SUBSTRATE.md), [E3](history/E3_TERRAFORM_ENGINEERING.md), [E4](history/E4_STATE_CONTROLLED_DELIVERY.md), [E5](history/E5_AZURE_DEVOPS_DELIVERY.md), [E6](history/E6_DIAGNOSTICS_AUTOMATION.md), [E7](history/E7_INCIDENT_CONTRACTS.md), [E8](history/E8_LOCAL_INCIDENTS.md), and [E10](history/E10_INDEPENDENT_REPLAY.md).

## Rebuild and verify

From the repository root, rebuild one lecture with:

    python textbook/tools/build.py AZ00-01

The existing tool regenerates that lecture's editable figures, HTML, PDF and temporary visual QA renders under its ignored build directory. Run the repository's existing offline checks with:

    python textbook/tools/test_python.py
    python textbook/tools/verify_terraform.py
    python textbook/tools/verify_repository.py
    python textbook/tools/package.py
    python textbook/tools/package.py --verify

Terraform verification uses mock plans and backend-free configuration. It does not call Azure or perform apply/destroy. The package tool preserves reproducible sources and educational experiments, excludes generated build directories and archives, normalizes text files, and records archive-member hashes in the publication manifest.
