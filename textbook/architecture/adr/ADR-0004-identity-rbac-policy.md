# ADR-0004 — Identity, RBAC and Policy responsibilities

- Status: Accepted as the reference pattern; no role or policy assignment changed.
- Date: 2026-11-27.
- Context: control-plane rights, data access, workload identity, Policy evaluation and remediation are separate permission paths.

## Decision

Use Entra groups for human roles and separate per-workload/per-environment managed identities for runtime access. Prefer workload identity federation for approved pipeline integrations rather than long-lived client secrets. Bind identities to exact issuer, subject and audience; scope Azure role assignments to the smallest subscription, resource group, service or state container that supports the operation. Review management-plane `Actions` separately from data-plane permissions.

Place broad Policy guardrails at management-group or subscription scope, with workload roles assigned below those scopes. Begin with audit effects and test their impact; use `deny`, `modify` or `deployIfNotExists` only after change review. A policy remediation identity is distinct from a user or pipeline identity and receives only the permissions needed for its remediation. A pipeline service connection must not inherit subscription-wide Contributor just because that is convenient.

## Consequences

- Narrow scopes increase the number of explicit roles but improve least privilege and incident attribution.
- A valid token alone does not prove resource permission, data-plane permission, network reachability or policy compliance.
- Federation removes a stored secret, not the need for service-connection governance, branch controls, approvals or narrow authorization.
- Role/policy operations are mutations and require exact separate Stage 3 approval.

## Source

- [Azure RBAC overview](https://learn.microsoft.com/en-us/azure/role-based-access-control/overview)
- [Azure Policy overview and recommendations](https://learn.microsoft.com/en-us/azure/governance/policy/overview)
- [Azure Policy effect basics](https://learn.microsoft.com/en-us/azure/governance/policy/concepts/effect-basics)
- [Configure workload identity service connections](https://learn.microsoft.com/en-us/azure/devops/pipelines/release/configure-workload-identity?view=azure-devops)
