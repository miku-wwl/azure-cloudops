# Azure Cloud Operations & Incident Response

> **Repository:** `azure-cloudops`  
> **Status:** Planning / Not yet validated on live Azure resources  
> **Focus:** Azure Networking · Identity · PowerShell Automation · Azure Monitor / KQL · Incident Response · Recovery

## Overview

Azure Cloud Operations & Incident Response is a hands-on engineering portfolio focused on operating, diagnosing, securing, and recovering Azure workloads in a **controlled non-production environment**.

The repository documents repeatable training exercises, scripts, KQL queries, incident investigations, and verified recovery evidence. Each completed scenario follows a consistent engineering workflow:

**Architecture design → Deployment → Baseline verification → Controlled fault → Diagnosis → Recovery → RCA → Cleanup.**

This is not a replacement for production operations experience and does not claim that the exercises run in a real enterprise environment.

## Why this project exists

This project complements [KPCP (kube-platform-control-plane)](https://github.com/miku-wwl/kube-platform-control-plane):

| KPCP focus | Azure CloudOps focus |
|---|---|
| Kubernetes controllers, Terraform orchestration, infrastructure lifecycle | Azure networking and connectivity diagnostics |
| Saved-plan approvals, provisioning and reconciliation | Entra ID, RBAC, managed identity and access incidents |
| Platform automation and local E2E | PowerShell/Azure CLI operational scripting |
| Controller recovery and platform reliability | Azure Monitor, KQL, alerting, incident response and data restore |

**Non-goals:** another Terraform control plane, Kubernetes management UI, custom cloud dashboard, enterprise-scale landing zone, or simulated production employment history.

## Learning tracks

| Track | Scope | Suggested official source | Status |
|---|---|---|---|
| AZ-305 design | Network / identity / governance / logging architecture decisions | [Microsoft AZ-305 case studies](https://microsoftlearning.github.io/AZ-305-DesigningMicrosoftAzureInfrastructureSolutions/) | Planned |
| Azure networking | VNet, Peering, NSG, routing, Private DNS/Endpoints | [AZ-700 exercises](https://microsoftlearning.github.io/AZ-700-Designing-and-Implementing-Microsoft-Azure-Networking-Solutions/) | Planned |
| Identity / governance | Entra ID, RBAC, managed identity, Azure Policy | [AZ-104 labs](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/) | Planned |
| Observability | Log Analytics, KQL, Monitor, actionable alerts | [Log Analytics tutorial](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-tutorial) | Planned |
| Operations automation | Read-only resource inventory and repeatable PowerShell tooling | [Microsoft ARI](https://github.com/microsoft/ARI) | Planned |
| Recovery | Azure Backup, restore validation and RCA | [AZ-104 Lab 10](https://microsoftlearning.github.io/AZ-104-MicrosoftAzureAdministrator/Instructions/Labs/LAB_10-Implement_Data_Protection.html) | Planned |

See **[Azure Specialty Roadmap](docs/AZURE_SPECIALTY_ROADMAP.md)** for the eight modules, checklists, recommended 3-week progression, gates, costs and links.

## Engineering outcomes

The target evidence set, **not yet claimed as completed**, is:

1. At least one design decision record relating to Azure network/identity/monitoring choices.
2. Two reproducible non-production incidents, including diagnosis, rollback/recovery, and root-cause analyses.
3. One scoped, read-only PowerShell inventory or compliance script with offline tests.
4. Five documented KQL queries, with verified schema/data source and sample output.
5. One backup **and actual restore verification**, including recorded recovery time.
6. Deployment and cleanup evidence, including a checked Azure cost estimate and post-cleanup resource inventory.

## Proposed repository structure

```text
azure-cloudops/
├── README.md
├── docs/
│   ├── AZURE_SPECIALTY_ROADMAP.md
│   ├── JD_SKILL_MAPPING.md
│   ├── STATUS.md
│   ├── incidents/
│   └── templates/
│       ├── EXPERIMENT.md
│       └── INCIDENT_RCA.md
├── automation/              # Scoped PowerShell scripts (future)
├── monitoring/
│   └── kql/                 # Verified KQL queries (future)
└── evidence/                # Sanitized, shareable evidence only
```

The repository intentionally does not contain live Azure deployment modules or incident results until they have been implemented and validated.

## Safety and cost controls

- Exercises run only in a subscription or resource group explicitly authorized for testing.
- Never inject faults into employer, shared, or production resources.
- Start with [the free Log Analytics demo](https://learn.microsoft.com/en-us/azure/azure-monitor/logs/log-analytics-tutorial) before deploying billable resources.
- Review Azure regional pricing and access prerequisites **before** each live exercise.
- Use narrow permissions, explicit resource tags, scoped deployment, and short-lived resources.
- Azure budget alerts are **notifications, not hard spending limits**.
- Remove or redact all tenant IDs, subscription IDs, usernames, tokens, keys, resource IDs and private URLs before committing evidence.
- Record teardown verification; deleting a resource group may not remove every dependent or retained resource (for example, backup data).

## Portfolio use

For Azure CloudOps/Operations-heavy job descriptions, this evidence-based work can occupy the second project position on a tailored résumé **once real exercises have been completed**. For Java/Full Stack roles, LedgerCore or another full-stack project may be a stronger second choice.

## Upstream resources and attribution

This independent training repository references Microsoft learning labs and open-source examples. The examples remain owned by their respective authors. If actual upstream source code is copied into this repository, preserve its applicable copyright and license obligations.

## Status

**Planning only.** No live Azure experiment, cloud deployment, incident drill, certification assessment, or automated test is represented as completed by the current repository scaffold.
