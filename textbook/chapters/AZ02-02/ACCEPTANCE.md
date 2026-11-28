# AZ02-02 lecture acceptance record

## V1.0.1 教材修订

- 补 NIC 的 ASG 关联、优先级、五元组和新连接正反例。
- 最终教材 [PDF](../../dist/pdf/AZ02-02_azure-nsg-asg-network-diagnostics.pdf) 已用原出版工具重建。基线 8 页，修订 9 页。正文排入 3 个 SVG，保留 3 个可编辑图稿。最终页面已检查排版、图和代码，带入全套发布校验。
- 现有本地回归通过。新增云端步骤按文档例处理，历史证据与操作权限见 [V1.0.1 逐讲审查](../../V1_0_1_TEXTBOOK_REVIEW.md)。

**Lecture:** Azure NSG, ASG and Network Diagnostics

**Acceptance date:** 2026-11-26 (Pacific/Auckland)
**Status:** ACCEPTED for Stage 1 lecture gate. No Azure rule set or connection was queried.

## Research and source

- Microsoft Learn and Azure CLI primary sources were reviewed on 2026-11-26. Claim mappings, direct URLs, source-page dates, classifications and limitations are recorded in `textbook/SOURCE_MAP.md`.
- The lecture distinguishes per-NSG priority and first-match behavior, built-in default rules, inbound subnet/NIC filtering, ASG NIC membership, stateful flow records and three separate diagnostic evidence types.
- Current IP Flow Verify documentation includes Azure Virtual Network Manager admin rules and limits packet-rule queries to TCP/UDP. Connection Troubleshoot's CLI command is documented as Preview; active diagnostic probes were not run.
- Three original editable figures are authored in `figures/figs.py`; they cover priority, subnet/NIC + ASG scope, and flow state versus diagnostic evidence.

## Experiment and evidence boundary

- `labs/nsg-model` exercises custom priority ordering, first match, ASG membership, filtering at subnet and NIC scopes, TCP/UDP/ports and a simplified established-flow table.
- Thirteen unit tests passed on Windows Python 3.13.9 on 2026-11-26. The full WSL `test_all.sh --python` run passed 45 tests across 4 lab directories with 0 failures.
- The model intentionally excludes Azure default NSG rules, actual service-tag expansion, AVNM admin rules, ICMP, Azure effective-rule APIs, routing, active probes, guest firewall behavior and application listeners. Unmatched custom rules are marked `NOT_MODELED_DEFAULT_RULES`.
- No Azure CLI authentication, subscription query, Network Watcher request, packet probe, rule change, resource deployment or billing query was performed.

## Publication inspection

- Reproduction from the repository root: `python textbook/tools/build.py AZ02-02`.
- Output: `textbook/dist/pdf/AZ02-02_azure-nsg-asg-network-diagnostics.pdf`; 8 pages, 1,677,222 bytes.
- Final automated report: 13,393 extracted characters; no placeholder markers; no overflow warnings; page fill 53%, 95%, 93%, 97%, 91%, 93%, 94%, 95%.
- All eight final pages were rendered and visually inspected in readable two-page spreads on 2026-11-26. The cover, priority/default-rule table, three figures, worked NSG table, CLI blocks, experiment card/output, caveat, fault cards, exercises/solutions, references, headers, page numbers and margins were checked.
- The build completes with the existing non-blocking Pillow `Image.getdata()` deprecation warning in the QA ink calculation.

## Gate result

**PASS — current primary-source mapping, chapter source, editable figures, applicable local experiment, actual tests, live-lab preparation, PDF build, all-page visual review and evidence record are complete.** The result does not claim Azure filtering, IP Flow Verify or connectivity was tested.
