# AZ03-02 lecture acceptance record

Acceptance date: 2026-11-26 (Pacific/Auckland). Repository: `D:/workshop/nov/azure-cloudops`, branch `main`.

## Source and content review

- Researched current Microsoft Learn documentation for managed identity lifecycle and selector behavior, IMDS token requests, Azure Identity Python credentials, workload identity federation, case-sensitive federated credential claims, Key Vault token audience, Key Vault RBAC/access-policy modes and Key Vault network security.
- Added three editable source-generated figures: managed identity lifecycle/selection, OIDC assertion exchange, and the independent Key Vault request gates.
- `SOURCE_MAP.md` ties the chapter's claims to official sources and records whether they are source analysis, documentation, local verification or live evidence.
- The Python SDK sample and the Azure CLI role-list command are documented examples only; neither was run against Azure.

## Local experiment and evidence boundary

- The pure-Python `credential-flow` lab checks managed identity selection, exact external FIC claim matching, synthetic Entra Key Vault audience/tenant/principal claims, one independent network result, and a small symbolic subset of Azure RBAC and legacy access policies.
- Targeted Windows Python 3.13.9 run: 16 tests passed. Sample fixture output was executed locally; it emits decisions only and no token string or secret value.
- Full Windows suite: 116 tests across 8 lab directories passed. Full `devops-lab` WSL suite: 116 tests across 8 directories passed.
- The fixture does not parse or validate JWT signatures, call Entra/IMDS/OIDC, acquire or exchange tokens, call Azure or Microsoft Graph, resolve DNS, send network traffic, retrieve a secret, or inspect real Azure roles. It omits role scope inheritance, deny assignments, ABAC conditions, PIM, groups, propagation, token caching, claims challenges and service-specific network behavior.
- No Azure login, tenant/subscription query, Key Vault request, role query/change, network probe, resource operation, deployment or billing query was performed. Stage 3 remains gated; actual Azure spend remains NOT_VERIFIED.

## Publication inspection

- Reproduction from the repository root: `python textbook/tools/build.py AZ03-02`.
- Output: `textbook/dist/pdf/AZ03-02_managed-identity-key-vault-federation.pdf`; 9 A4 pages, 1,702,197 bytes, SHA-256 `093FB346D0325CD7ADEFBED5F711CE1EA23E1937BF4E841844F99B85878DA813`.
- Final publisher report: 15,794 extracted characters, no placeholder markers or overflow flags; page fill 63%, 90%, 92%, 92%, 93%, 97%, 91%, 93%, 30% (the final page contains primary references).
- All nine final pages were rendered and visually reviewed at 88 DPI on 2026-11-26. Pages 2–8, including all figures, the SDK example, the local experiment, diagnostics and exercises, were additionally reviewed at 140 DPI.
- No clipping, missing glyphs, broken references or unintended blank pages were observed. The publisher retains the known non-blocking Pillow `Image.getdata()` deprecation warning.

## Gate result

**PASS — source mapping, Chinese chapter, three editable figures, offline credential-flow model, targeted and full Windows/WSL tests, documented read-only diagnostic, reproducible PDF and final visual review are complete.** No real Azure identity, authorization, network, resource, billing or Key Vault behavior is claimed as verified.
