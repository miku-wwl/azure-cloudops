# AZ03-01 lecture acceptance record

## V1.0.1 教材修订

- 用容器级 Blob Data Reader 做正反例，并标清 token、主体、scope 的检查顺序。
- 最终教材 [PDF](../../dist/pdf/AZ03-01_microsoft-entra-tokens-azure-rbac.pdf) 已用原出版工具重建。基线 9 页，修订 10 页。正文排入 3 个 SVG，保留 3 个可编辑图稿。最终页面已检查排版、图和代码，带入全套发布校验。
- 现有本地回归通过。新增云端步骤按文档例处理，历史证据与操作权限见 [V1.0.1 逐讲审查](../../V1_0_1_TEXTBOOK_REVIEW.md)。

**Lecture:** Microsoft Entra ID, access tokens and Azure RBAC

**Acceptance date:** 2026-11-26 (Pacific/Auckland)

**Status:** ACCEPTED for the Stage 1 lecture gate. No Azure authentication, token acquisition, identity/role query or role operation was performed.

## Research and source mapping

- Current Microsoft identity platform token claims and validation, Azure RBAC roles/assignments/scope, Azure Storage Entra authorization, role propagation and Azure CLI references were checked on 2026-11-26.
- The chapter separates token audience/issuer/tenant/time validation from later Azure RBAC principal/action/scope evaluation. It distinguishes app API scp/roles claims from Azure role assignments, management-plane Actions from data-plane DataActions, assignment scope from custom-role AssignableScopes, and role-local NotActions subtraction from deny assignments.
- Microsoft Storage documentation describes non-instantaneous role propagation and scopes where delays can be longer; the chapter records the documented range as service guidance, not a locally observed result or fixed universal SLA.
- Claim-to-section mapping, direct URLs and evidence limits are in textbook/SOURCE_MAP.md.

## Local experiment and evidence boundary

- The pure-Python labs/authorization-model fixture checks an asserted token trust prerequisite, issuer, tenant, audience, nbf/exp, tenant+object identity, scope ancestry, separate control/data operations, role-local NotActions/NotDataActions subtraction and multi-assignment grants.
- Targeted Windows Python 3.13.9 run: 17 tests passed. Targeted CLI output was also executed from the fixture.
- Full Windows suite: 100 tests across 7 directories passed. Full devops-lab WSL suite: 100 tests across 7 directories passed on Python 3.12.3.
- The fixture is synthetic. It does not create or parse JWTs, validate signatures or keys, fetch issuer metadata, acquire Entra tokens, call Azure or Microsoft Graph, or send network requests. It also omits token-version handling, groups, PIM, role conditions, deny assignments, permission propagation, Storage keys/SAS and provider-specific authorization behavior.
- No Azure login, tenant or subscription query, role assignment query/change, resource operation, live API request, billing query or Azure resource deployment was performed. Stage 3 remains gated; actual Azure spend remains NOT_VERIFIED.

## Publication inspection

- Reproduction: from the repository root, run:

~~~powershell
python textbook/tools/build.py AZ03-01
~~~

- Output: textbook/dist/pdf/AZ03-01_microsoft-entra-tokens-azure-rbac.pdf; 9 A4 pages, 1,719,556 bytes, SHA-256 48B64A5986EF2D7C4475579D82AC312A762225035022042D560550887AC4226E.
- Final publisher report: 17,129 extracted characters; no placeholder markers or overflow flags; page fill 58%, 96%, 96%, 98%, 97%, 98%, 95%, 99%, 79%.
- All nine final pages were rendered and reviewed at 88 DPI on 2026-11-26. The mechanism diagrams on pages 3–4 and the experiment/code output on page 6 were additionally reviewed at 140 DPI. The final review included a rebuilt scope hierarchy figure and shortened the diagnostic table so no row split across pages.
- No clipping, missing glyphs, broken references or unintended blank pages were observed. The publisher QA continues to emit the existing non-blocking Pillow Image.getdata() deprecation warning.

## Gate result

**PASS — source mapping, Chinese chapter, three editable mechanism diagrams, offline model, targeted and full Windows/WSL tests, read-only diagnostic procedure, reproducible PDF, final visual review and evidence record are complete.** No Azure enforcement, live identity, authorization, resource, cost or billing behavior is claimed as verified.
