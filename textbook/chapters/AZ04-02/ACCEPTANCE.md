# AZ04-02 lecture acceptance record

Acceptance date: 2026-11-26 (Pacific/Auckland). Repository: `D:/workshop/nov/azure-cloudops`, branch: `main`.

## Source and content review

- Researched current Microsoft Learn documentation for App Service deployment slots and swap phases; swap settings, custom warm-up, slot-specific settings, managed identities, and Health Check behavior; Container Apps revision and app-wide configuration scopes, startup/readiness/liveness probes, ingress and traffic weights, scaling, managed identities, and secret troubleshooting.
- The chapter separates slot warm-up, per-instance Health Check, Container Apps readiness, application smoke tests, and business SLI checks. It distinguishes route rollback from global configuration and data restoration.
- Four editable mechanism figures cover slot/revision release units, source-side App Service swap, Container Apps configuration scopes, and the release/readiness gates.
- The Azure CLI slot and revision list commands are documented as future read-only templates; neither was executed.

## Local experiment and evidence boundary

- The deterministic lab models warm-up HTTP status filtering, slot route movement with identity remaining associated with the slot, Container Apps revision versus app-wide changes, single/multiple revision traffic policies, and route-only rollback.
- Targeted Windows run: 16 tests passed. Full Windows suite: 166 tests across 11 lab directories passed.
- Full `devops-lab` WSL Python suite: 166 tests across 11 lab directories passed.
- The multiple-revision readiness guard is a local release policy. It does not emulate Azure service enforcement. The fixture is not an App Service or Container Apps emulator and does not test HTTP, containers, identity tokens, Azure APIs, scale behavior, or billing.
- No Azure authentication, subscription query, Azure CLI execution, resource operation, deployment, probe request, identity-token request, or billing query was performed. Actual cumulative Azure billing remains `NOT_VERIFIED`.

## Publication inspection

- Reproduction: `python textbook/tools/build.py AZ04-02`.
- Output: `textbook/dist/pdf/AZ04-02_appservice-container-apps-deployment.pdf`; 7 pages, 1,553,080 bytes, SHA-256 `8C7E5DE41841500C16AA22765729D113D6146D35AAF6796464DED6512CF9D7D3`.
- Publisher report: 12,507 extracted characters, no placeholder markers or overflow flags; page fill 49%, 91%, 98%, 96%, 99%, 93%, 78%.
- All seven final pages were rendered and visually inspected at 88 and 140 DPI on 2026-11-26. Figure captions, tables, code, references, and page breaks were reviewed; no clipping, missing glyphs, broken references, or unintended blank pages were observed.
- Known non-blocking publisher warning: Pillow `Image.getdata()` deprecation.

## Gate result

**PASS — current primary-source mapping, Chinese chapter, four editable mechanism figures, deterministic offline release model, targeted and full Windows/WSL tests, documented read-only diagnostic templates, reproducible PDF, and final visual review are complete.** No live Azure behavior or billing is claimed as verified.

## V1 closure addendum (2026-11-28)

- Observed F1 provisioning and cleanup. App creation, ZIP release and rollback remain NOT_RUN in Azure; the two Node packages passed the same local probe.
- [Final PDF](../../dist/pdf/AZ04-02_appservice-container-apps-deployment.pdf) has 7 pages and 1,587,372 bytes. SHA-256 is `B376554C3F78F909B57F40665D614E73608C984AAA1AC8E98119A6B7D96269BB`.
- Visually inspected all 7 pages at 88 DPI and page 6 at 140 DPI. The final page proof was compared with the prior reviewed render and every changed page was rechecked. Publisher QA, PDF outline and extracted text checks passed.
- Scope and observed evidence are linked from the [V1 source map](../../SOURCE_MAP.md#v1-closure-source-map--2026-11-28).
