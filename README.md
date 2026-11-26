# Azure CloudOps & Enterprise Infrastructure

**Status:** Stage 1, B3 complete — AZ00-01, AZ01-01, AZ02-01 through AZ02-04, and AZ03-01 through AZ03-03 accepted (9/23); AZ04-01 is next.
**Repository:** miku-wwl/azure-cloudops, main
**Approved implementation baseline:** 853ba6cbaa4ee67e448550fbe192c6c89b24fd2f
**Roadmap:** AZURE_SPECIALTY_ROADMAP.md
**Curriculum:** textbook/CURRICULUM.md

This is an enterprise Azure engineering practice repository and a 23-lecture illustrated technical textbook. It is for experienced engineers learning Azure mechanisms, architecture, infrastructure delivery, diagnosis and recovery. It is not certification revision, a banking product, a cloud management platform, or a claim of production banking experience.

## Execution sequence

| Stage | Objective | Current status |
|---|---|---|
| 1 — Technical textbook | Research, author, illustrate, experiment and publish 23 independent PDFs with editable sources | B0/B1/B2 accepted; B3 complete; 9 of 23 accepted |
| 2 — Engineering readiness | Harden local labs, Terraform, controlled delivery, automation and incident replay | Not started |
| 3 — Live Azure validation | Read-only preflight first; perform only specifically authorized, reliably costed experiments | Not started; no Azure resources created |

The cumulative incremental Azure ceiling is USD 1.00 for the entire project. Plan against USD 0.70 and retain USD 0.30 for contingency. Actual billing is not verified until billing evidence is checked. A budget alert is not a hard spending cap. Expensive services remain design-only unless current pricing, account capability, narrow authorization and cleanup all pass the live gate.

## Evidence rules

Designs, static checks, local experiments, official demos, Azure read-only observations, plans, deployments, live verification, recovery and cleanup are separate evidence states. Local analogues do not prove Azure enforcement. Expected output is not an observed result. Portal screenshots are used only when captured from an authorized existing session and redacted; otherwise the book uses original mechanism diagrams.

The lab scenario uses synthetic data. No employer, customer, production, shared or unknown resources may receive fault injection. Preserve the repository's Apache 2.0 license. Work only on main and do not modify the AWS reference repository.

## Repository guide

- AZURE_SPECIALTY_ROADMAP.md — full scope, retained V3 engineering contracts and three-stage execution sequence.
- textbook/CURRICULUM.md — approved lecture list and learning questions.
- textbook/PROGRESS.md — current gate, evidence and restart point.
- textbook/REFERENCE_ANALYSIS.md — source-grounded B0 AWS publisher review.
- textbook/COST_LEDGER.md and textbook/VERIFICATION_MATRIX.md — cost and evidence state.
- textbook/chapters/ — authoritative per-lecture source, diagrams and applicable experiments.
- textbook/dist/ — generated PDFs and verified publication packages.
