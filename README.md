# Azure CloudOps & Enterprise Infrastructure

**V1.0.1 textbook refinement:** 23 lectures with field-level configuration, worked diagnosis and recovery exercises. [Review and acceptance](textbook/V1_0_1_TEXTBOOK_REVIEW.md) · [PDF collection](textbook/dist/Azure-CloudOps-PDF.zip) · [Editable sources](textbook/dist/Azure-CloudOps-Sources.zip) · [Manifest](textbook/dist/publication-manifest.json). The refinement uses the accepted V1 publication as its baseline and has an additional Azure budget of USD 0.00.

**V1 status:** `TEXTBOOK_V1_RELEASE_READY`, `LIVE_LAB_READY` and `READ_ONLY_AZURE_VERIFIED`. LAB-IR-11 reached F1 plan provisioning and verified cleanup. The app release and rollback remain unverified in Azure. [Final acceptance report](textbook/FINAL_ACCEPTANCE_REPORT.md).
**Repository:** miku-wwl/azure-cloudops, main
**Approved implementation baseline:** 853ba6cbaa4ee67e448550fbe192c6c89b24fd2f
**Roadmap:** AZURE_SPECIALTY_ROADMAP.md
**Curriculum:** textbook/CURRICULUM.md

This is an enterprise Azure engineering practice repository and a 23-lecture illustrated technical textbook. It is for experienced engineers learning Azure mechanisms, architecture, infrastructure delivery, diagnosis and recovery. It is not certification revision, a banking product, a cloud management platform, or a claim of production banking experience.

## Execution sequence

| Stage | Objective | Current status |
|---|---|---|
| 1 — Technical textbook | Publish 23 independent PDFs with editable sources | B0–B9 accepted. The V1 update includes the observed Azure results and checked publication packages. |
| 2 — Engineering readiness | Validate local labs, Terraform, controlled delivery, diagnostics and replay | E0–E10 accepted. All eight mandatory local incidents and the independent replay passed. |
| 3 — Live Azure validation | Verify the current subscription scope and run the one authorized batch | L0 passed. IR-11 stopped at the Linux plan verification gate and both temporary resources were removed. Billing is `BILLING_PENDING`. |

The cumulative incremental Azure ceiling is USD 1.00 for the entire project. Plan against USD 0.70 and retain USD 0.30 for contingency. Actual billing is not verified until billing evidence is checked. A budget alert is not a hard spending cap. Expensive services remain design-only unless current pricing, account capability, narrow authorization and cleanup all pass the live gate.

## Evidence rules

Designs, static checks, local experiments, official demos, Azure read-only observations, plans, deployments, live verification, recovery and cleanup are separate evidence states. Local analogues do not prove Azure enforcement. Expected output is not an observed result. Portal screenshots are used only when captured from an authorized existing session and redacted; otherwise the book uses original mechanism diagrams.

The lab scenario uses synthetic data. No employer, customer, production, shared or unknown resources may receive fault injection. Preserve the repository's Apache 2.0 license. Work only on main and do not modify the AWS reference repository.

## Repository guide

- AZURE_SPECIALTY_ROADMAP.md — full scope, retained V3 engineering contracts and three-stage execution sequence.
- textbook/CURRICULUM.md — approved lecture list and learning questions.
- textbook/PROGRESS.md — current gate, evidence and restart point.
- textbook/E0_INDEPENDENT_AUDIT.md — Stage 1 audit findings, corrections and remaining evidence gaps.
- textbook/E3_TERRAFORM_ENGINEERING.md — locked AzureRM/AzAPI reference configuration, scope/cost guards, mock-test evidence and live limits.
- textbook/E4_STATE_CONTROLLED_DELIVERY.md — state/import/recovery lab, signed exact-plan gate and conditional OIDC backend evidence/limits.
- textbook/E5_AZURE_DEVOPS_DELIVERY.md — Plan/PlanReview/Apply template, exact-plan artifact binding, offline verification and server-side prerequisites.
- textbook/E6_DIAGNOSTICS_AUTOMATION.md — explicit-scope Resource Graph inventory, 13 read-only diagnostics, five source-reviewed KQL templates and verification limits.
- textbook/E7_INCIDENT_CONTRACTS.md and textbook/incidents/ — twelve mapped incident contracts and local evidence.
- textbook/E8_LOCAL_INCIDENTS.md and textbook/E10_INDEPENDENT_REPLAY.md — bounded local incident evidence and second complete replay cycle.
- textbook/LIVE_LAB_CATALOGUE.md — E9 requirements, Terraform gaps, cost classes, and delayed-billing checks for L0 and all twelve incident candidates.
- .github/workflows/ci.yml — offline Python/Terraform/Pester acceptance, publication checks and repository-history secret scan; read-only token and no Azure provisioning.
- textbook/architecture/ — three distinct reference, local-learning and conditional live-lab views, plus six ADRs; designs do not authorize cloud changes.
- textbook/LAB_ENVIRONMENT.md and textbook/E2_LOCAL_SUBSTRATE.md — checked Windows/WSL inventory and local command/test-substrate acceptance.
- textbook/terraform/azure-enterprise-reference/ — safe-by-default AzureRM/AzAPI source and reusable Terraform modules.
- textbook/terraform/azure-remote-state-backend/ — conditional Azure Storage backend source; never initialized in Stage 2.
- textbook/tools/controlled_apply.py — fail-closed signed plan verifier and one-shot apply wrapper; trusted signer/service-side checks remain external.
- textbook/REFERENCE_ANALYSIS.md — source-grounded B0 AWS publisher review.
- textbook/COST_LEDGER.md and textbook/VERIFICATION_MATRIX.md — cost and evidence state.
- textbook/chapters/ — authoritative per-lecture source, diagrams and applicable experiments.
- [PDF collection](textbook/dist/Azure-CloudOps-PDF.zip), [editable sources](textbook/dist/Azure-CloudOps-Sources.zip) and [publication manifest](textbook/dist/publication-manifest.json).
