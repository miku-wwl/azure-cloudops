# AZ03-03 lecture acceptance record

Acceptance date: 2026-11-26 (Pacific/Auckland). Repository: `D:/workshop/nov/azure-cloudops`, branch `main`.

## Source and content review

- Researched current Microsoft Learn documentation for Azure Policy effect order and compliance states; deployIfNotExists and remediation; Activity Log coverage, schema, retention and CLI queries; Defender for Cloud posture assessment, MCSB recommendation effects, secure-score model differences and plan cost boundaries.
- Authored three original editable figures covering Policy request/post-success timing, management versus data-plane evidence, and the optional Defender-to-Policy enforcement path.
- `SOURCE_MAP.md` maps lecture claims to Microsoft primary sources and records evidence classifications.
- Azure CLI examples are documentation templates only. They are not authorized or executed in this stage.

## Local experiment and evidence boundary

- Synthetic lab coverage: three Policy effects, create/update/existing phases, Activity Log visibility classes, configured versus unconfigured resource diagnostics, Defender recommendation versus selected Policy effects, and a separate plan-price review state.
- Targeted Windows run: 16 tests passed.
- Full Windows suite: 132 tests across 9 lab directories passed.
- Full `devops-lab` WSL suite: 132 tests across 9 lab directories passed.
- The fixture is not an Azure Policy, ARM, Azure Monitor, Defender, log-delivery, or pricing emulator. No token acquisition, Azure/Entra/Graph query, subscription query, Policy evaluation request, network query, deployment, resource operation, plan enablement, or billing check was performed.
- Actual cumulative Azure billing remains NOT_VERIFIED.

## Publication inspection

- Reproduction: `python textbook/tools/build.py AZ03-03`.
- Output: `textbook/dist/pdf/AZ03-03_azure-policy-activity-log-defender-cloud.pdf`; 8 pages, 1,602,724 bytes, SHA-256 `5ED79075A8227194798FA1BE54E18AC6C2C98DFC74561F6A6A76EC599A489A60`.
- Publisher report: 14,066 extracted characters, no placeholder markers or overflow flags; page fill 54%, 99%, 91%, 95%, 96%, 98%, 93%, 76%.
- All eight final pages were rendered and visually reviewed at 88 and 140 DPI on 2026-11-26. No clipping, missing glyphs, broken references or unintended blank pages were observed.
- Known non-blocking publisher warning: Pillow `Image.getdata()` deprecation.

## Gate result

**PASS — source mapping, Chinese chapter, three editable figures, offline governance/evidence model, targeted and full Windows/WSL tests, documented read-only diagnostics, reproducible PDF and final page-by-page visual review are complete.** No live Azure behavior or billing is claimed as verified.
