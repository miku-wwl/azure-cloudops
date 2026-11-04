# Azure Cloud Operations & Enterprise Infrastructure

> **Repository:** `azure-cloudops`  
> **Status:** Learning roadmap / no live Azure validation recorded in this repository  
> **Focus:** Enterprise Azure architecture · Networking · Identity & Governance · Terraform/IaC · Observability · Incident Response · Recovery

## Purpose

This repository is an **evidence-driven Azure engineering learning plan**, not a new cloud platform product. Its purpose is to close the gap between certification-level knowledge and practical cloud infrastructure engineering: **designing, deploying, troubleshooting, securing, and recovering Azure resources** in a controlled, authorized, non-production environment.

For each exercise, the expected loop is:

**Design & trade-offs → Deployment or configuration → Baseline verification → Controlled failure/change → Diagnosis → Recovery or rollback → Evidence & RCA → Cleanup.**

A design document, a passing static check, and an Azure deployment are **different levels of evidence**. Do not report an exercise as validated without execution records.

## What changed in the learning scope

The original focus on Azure CloudOps and incident response is retained. The roadmap additionally covers the enterprise-infrastructure competencies commonly expected in senior Cloud / Platform / Infrastructure Engineer roles:

- **Azure Landing Zone design:** management-group/subscription structure, policies, identity boundaries, connectivity and operational ownership. Start with a **reference architecture and design decisions**; do not build a full enterprise landing zone for a personal lab.
- **Terraform engineering:** small reusable modules, version pinning, state design, isolation between environments, CI validation and review/approval of changes.
- **Security and governance:** least-privilege Azure RBAC, managed identities, Azure Policy, private connectivity and auditable changes.
- **Operational readiness:** actionable telemetry, KQL, incident troubleshooting, rollback/restore verification, costs and post-exercise cleanup.

**Out of scope:** a second Kubernetes control plane; a cloud management UI; multi-tenant provisioning service; production-like claims; expensive always-on enterprise networking; and pursuing more certificates for their own sake.

## Relationship to KPCP

| KPCP | Azure CloudOps |
|---|---|
| Kubernetes controllers and platform reconciliation | Azure-specific infrastructure architecture and operations |
| Infrastructure lifecycle orchestration | Azure networking, Entra ID / RBAC and governance |
| Approval and workflow mechanics | Enterprise IaC practices and cloud change evidence |
| Platform design and local integration | Azure Monitor / KQL, troubleshooting and disaster recovery |

The goal is complementary hands-on evidence, **not duplicating KPCP's product scope**.

## Learning tracks

| Priority | Track | What to demonstrate |
|---|---|---|
| P0 | Enterprise architecture / Landing Zone | Management-group and subscription topology, connectivity, identity, policies, ADRs and trade-offs |
| P0 | Azure networking & diagnostics | VNet, peering, routing, NSG, Private Endpoint, Private DNS and Network Watcher diagnosis |
| P0 | Terraform / infrastructure delivery | Versioned modules, remote-state design, validation, plan review and safe rollback/teardown |
| P1 | Identity & governance | Scoped RBAC, managed identity, Key Vault access and Azure Policy allowed/denied cases |
| P1 | Monitoring & incident response | KQL, Azure Monitor signals/alerts, repeatable fault investigation, RCA |
| P1 | Recovery & continuity | Backup **and restore verification**, RPO/RTO assumptions and measured recovery |
| P2 | Operational scripting | Read-only PowerShell / Azure CLI resource inventory with tests and predictable error handling |
| P2 | Hybrid architecture (design first) | On-premises connectivity scenarios, DNS, routing and security trade-offs; no costly mandatory deployment |

The detailed order, study outcomes, experiment gates and cost boundaries are in [AZURE_SPECIALTY_ROADMAP.md](AZURE_SPECIALTY_ROADMAP.md).

## Evidence-based outcomes (targets, not completed work)

A portfolio-ready version of this repository should contain evidence of:

1. **One enterprise Azure architecture decision package:** Landing Zone boundaries, network topology, identity/Policy model, ADRs and diagrams.
2. **One small Terraform-managed lab:** reviewed configuration, reproducible `fmt` / `validate` / `plan` results, explicit state design and verified cleanup. CI checks alone do not prove a live deployment.
3. **Two independently diagnosed incidents:** preferably one DNS/network incident and one RBAC/identity or alerting incident, each with baseline, symptoms, diagnostic commands, recovery evidence and RCA.
4. **Five reproducible KQL queries** with known data sources and interpreted results; demo queries must be marked as demo-only.
5. **One read-only resource-inventory script** with error handling and tests.
6. **One completed backup-to-restore drill** with data-integrity verification and recorded elapsed recovery time.
7. **Cost and security evidence:** pre-execution cost review, redacted artifacts and post-teardown inventory.

If a live Azure subscription is unavailable, complete the **design/offline** portion and label the live validation **NOT RUN**, rather than presenting design as hands-on proof.

## Execution and verification rules

- **Plan before provisioning.** Identify subscription permissions, region, scope, expected cost and teardown steps before each paid experiment.
- **Use an authorized, isolated non-production scope.** No employer, shared, customer or production fault injection.
- **Separate evidence states:** `PLANNED`, `DESIGNED`, `STATIC_CHECK_PASS`, `DEPLOYED`, `LIVE_VERIFIED`, `RECOVERED`, `CLEANED_UP`, and `BLOCKED` / `NOT_RUN` where appropriate.
- **Avoid secrets in Git.** Redact tenant/subscription IDs, principal identifiers, private DNS names, tokens, keys and sensitive logs before publishing.
- **Use least privilege.** Avoid broad Owner assignments and long-lived credentials; consider federated identity for CI when live deployments are introduced.
- **Budget alerts are not spending caps.** Private Endpoints, VMs, log ingestion, public IPs, backup retention and Azure Firewall can incur costs even while idle. Review actual pricing and check for retained resources after cleanup.
- **No fabricated screenshots, run outputs or production experience.** An unchecked item remains unchecked until there is verifiable evidence.

## Current repository status

At the time of this documentation update, this repository contains **planning documents only**. The roadmap describes proposed work; it does **not** claim successful Terraform execution, Azure deployment, cloud incident, automated test or recovery drill.

**Next action:** start with the roadmap's first architecture decision and the lowest-cost networking/diagnostics lab. Record validation evidence only after the corresponding activity has really been performed.

## Reference material

Use the [Azure Specialty Roadmap](AZURE_SPECIALTY_ROADMAP.md) to choose official Microsoft documentation, labs and assessment resources. This repository intentionally does not mirror or copy third-party learning materials.
