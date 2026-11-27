# Azure CloudOps & Enterprise Infrastructure

**Status:** Stage 2 E5 Azure Pipelines engineering. Stage 1 B0–B9 and Stage 2 E0–E4 are complete. The master-prompt CI/secret-scan gate and refreshed Stage 2 packages remain open.
**Repository:** miku-wwl/azure-cloudops, main
**Approved implementation baseline:** 853ba6cbaa4ee67e448550fbe192c6c89b24fd2f
**Roadmap:** AZURE_SPECIALTY_ROADMAP.md
**Curriculum:** textbook/CURRICULUM.md

This is an enterprise Azure engineering practice repository and a 23-lecture illustrated technical textbook. It is for experienced engineers learning Azure mechanisms, architecture, infrastructure delivery, diagnosis and recovery. It is not certification revision, a banking product, a cloud management platform, or a claim of production banking experience.

## Execution sequence

| Stage | Objective | Current status |
|---|---|---|
| 1 — Technical textbook | Research, author, illustrate, experiment and publish 23 independent PDFs with editable sources | `TEXTBOOK_V1_RELEASE_READY` for Stage 1 publication; current cross-stage CI/security acceptance remains separately tracked |
| 2 — Engineering readiness | Harden local labs, Terraform, controlled delivery, automation and incident replay | E0–E4 complete; E5 Azure Pipelines current |
| 3 — Live Azure validation | Read-only preflight first; perform only specifically authorized, reliably costed experiments | Not started; no Azure resources created; spend remains `NOT_VERIFIED` |

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
- textbook/architecture/ — three distinct reference, local-learning and conditional live-lab views, plus six ADRs; designs do not authorize cloud changes.
- textbook/LAB_ENVIRONMENT.md and textbook/E2_LOCAL_SUBSTRATE.md — checked Windows/WSL inventory and local command/test-substrate acceptance.
- textbook/terraform/azure-enterprise-reference/ — safe-by-default AzureRM/AzAPI source and reusable Terraform modules.
- textbook/terraform/azure-remote-state-backend/ — conditional Azure Storage backend source; never initialized in Stage 2.
- textbook/tools/controlled_apply.py — fail-closed signed plan verifier and one-shot apply wrapper; trusted signer/service-side checks remain external.
- textbook/REFERENCE_ANALYSIS.md — source-grounded B0 AWS publisher review.
- textbook/COST_LEDGER.md and textbook/VERIFICATION_MATRIX.md — cost and evidence state.
- textbook/chapters/ — authoritative per-lecture source, diagrams and applicable experiments.
- textbook/dist/ — generated PDFs and verified publication packages.
