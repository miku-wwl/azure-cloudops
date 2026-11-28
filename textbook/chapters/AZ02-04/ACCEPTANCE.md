# AZ02-04 lecture acceptance record

## V1.0.1 教材修订

- 补探针与后端设置、监听规则的绑定和同请求复验。
- 最终教材 [PDF](../../dist/pdf/AZ02-04_azure-load-balancer-application-gateway-front-door.pdf) 已用原出版工具重建。基线 9 页，修订 9 页。正文排入 3 个 SVG，保留 3 个可编辑图稿。最终页面已检查排版、图和代码，带入全套发布校验。
- 现有本地回归通过。新增云端步骤按文档例处理，历史证据与操作权限见 [V1.0.1 逐讲审查](../../V1_0_1_TEXTBOOK_REVIEW.md)。

**Lecture:** Azure Load Balancer, Application Gateway and Front Door

**Acceptance date:** 2026-11-26 (Pacific/Auckland)

**Status:** ACCEPTED for the Stage 1 lecture gate. No Azure authentication, query, probe or resource operation was performed.

## Research and source mapping

- Microsoft Learn pages for Load Balancer flow hashing/probes, Application Gateway components/routing/probes/backend health/TLS, Front Door health/routing, WAF and pricing were checked on 2026-11-26. Claim-to-section mapping and primary URLs are in `textbook/SOURCE_MAP.md`.
- The chapter distinguishes regional Layer 4/Layer 7 scopes from global Front Door delivery. It includes the current Application Gateway TCP/TLS Layer 4 proxy capability but keeps the experiment scoped to HTTP(S) routing.
- Documented probe semantics are kept separate: Load Balancer TCP is a listener check; Load Balancer HTTP and Front Door HTTP(S) require status 200; Application Gateway's default HTTP(S) probe accepts 200–399 and has backend setting, host/path and HTTPS certificate conditions.
- Front Door sample-window thresholds, priority/latency/weight routing, probe volume and the documented all-origins-unhealthy round-robin behavior are identified as source-analyzed, not observed locally.
- Official pricing dimensions are cited, but no account, region, offer, SKU, request volume or runtime was selected for an estimate.

## Experiment and evidence boundary

- `labs/probe-model` compares synthetic TCP listener, HTTP status, Application Gateway accepted range/path/TLS-validity assertion and Front Door last-N origin health/priority decisions.
- The fixture includes redirect, failed readiness, healthy-backup, all-origins-unhealthy and HTTPS certificate/SNI-assertion cases. Its all-unhealthy output reports the documented candidate fallback set and does not invent a real request assignment.
- The targeted Windows Python 3.13.9 run passed 20 tests. The complete Windows suite passed 83 tests across six lab directories. `devops-lab` WSL also passed 83 tests across six lab directories using `textbook/tools/test_all.sh --python`.
- The model does not start servers, issue HTTP/TCP requests, create TLS certificates, reproduce the Front Door edge mesh, choose by latency, assign weighted/session-affinity requests, execute WAF or Application Gateway routing, emulate Load Balancer flow state, or call Azure APIs.
- No Azure CLI login, resource inventory, probe, WAF request, deployment, teardown, billing query or live network operation was performed. Stage 3 remains gated; the chapter experiment is LOCAL_VERIFIED only.

## Publication inspection

- Reproduction: `python textbook/tools/build.py AZ02-04`.
- Output: `textbook/dist/pdf/AZ02-04_azure-load-balancer-application-gateway-front-door.pdf`; 9 A4 pages, 1,709,929 bytes, SHA-256 `858D34BCF65574FC7CF5D55AFA9FAEDA4A26C72F8F875DBCD2FBA2E51CAF393C`.
- Final build report: 16,465 extracted characters, no placeholder markers or overflow flags; page fill 56%, 96%, 94%, 96%, 98%, 82%, 91%, 98%, 71%.
- All nine final PDF pages were rendered and reviewed in five readable two-page spreads on 2026-11-26. The signature figures on pages 3–4 were additionally reviewed at 140 DPI; all three figures correspond to their source and remain legible at page size.
- First review found a sparse references page. A concise symptom-to-first-evidence table was added, the PDF rebuilt, and all final pages re-inspected. No clipping, broken diagram, overflow or missing-glyph defect was observed.
- Publisher QA continues to emit the existing non-blocking Pillow `Image.getdata()` deprecation warning.

## Gate result

**PASS — current primary-source mapping, Chinese chapter, three editable mechanism figures, local decision model, Windows/WSL tests, future read-only diagnostics, reproducible PDF and complete final-page visual review are complete.** Azure traffic distribution, real health probes, WAF, TLS, live cost and billing remain unverified.
