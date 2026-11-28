# AZ04-01 lecture acceptance record

## V1.0.1 教材修订

- 补 Update Manager 补丁环、任务与代理故障排查。Flexible VMSS 升级策略的官方冲突仍已注明。
- 最终教材 [PDF](../../dist/pdf/AZ04-01_vm-vmss-managed-disk-operations.pdf) 已用原出版工具重建。基线 6 页，修订 8 页。正文排入 3 个 SVG，保留 3 个可编辑图稿。最终页面已检查排版、图和代码，带入全套发布校验。
- 现有本地回归通过。新增云端步骤按文档例处理，历史证据与操作权限见 [V1.0.1 逐讲审查](../../V1_0_1_TEXTBOOK_REVIEW.md)。

Acceptance date: 2026-11-26 (Pacific/Auckland). Repository: `D:/workshop/nov/azure-cloudops`, branch: `main`.

## Source and content review

- Researched current Microsoft Learn sources for VM power/provisioning states and billing; VM host versus guest monitoring; boot diagnostics; VMSS orchestration, upgrade policy, and Application Health Extension; managed-disk and VM I/O limits; and the Azure CLI instance-view command.
- Recorded an inconsistency between the current upgrade-policy and orchestration-mode pages about Flexible VMSS upgrade-policy support. The chapter and fixture mark mode/API support for recheck; they do not claim a universal configuration contract.
- Authored three editable mechanism figures: VM state/evidence planes, VMSS model and instance rollout, and the single uncached disk/VM I/O ceiling.
- The Azure CLI instance-view command is documented as a future read-only template; it was not executed.

## Local experiment and evidence boundary

- Synthetic lab covers allocated versus deallocated compute billing labels, independent power/provisioning values, guest telemetry configuration, VMSS model drift and conceptual health gates, single-disk IOPS/throughput caps, and boot evidence versus app health.
- Targeted Windows run: 18 tests passed.
- Full Windows Python suite: 150 tests across 10 lab directories passed.
- Full `devops-lab` WSL Python suite: 150 tests across 10 lab directories passed.
- The fixture is not an Azure VM, ARM, VMSS, health-extension, disk-performance, monitoring, or billing emulator. No Azure authentication, subscription query, Azure CLI execution, network probe, resource operation, deployment, telemetry query, or billing query was performed.
- Actual cumulative Azure billing remains `NOT_VERIFIED`.

## Publication inspection

- Reproduction: `python textbook/tools/build.py AZ04-01`.
- Output: `textbook/dist/pdf/AZ04-01_vm-vmss-managed-disk-operations.pdf`; 6 pages, 1,552,689 bytes, SHA-256 `46E2C261981BC9C9F44C607D2E292F0BE1E1020D62BFC86CF996D0B6DA2B38D8`.
- Publisher report: 9,424 extracted characters, no placeholder markers or overflow flags; page fill 56%, 97%, 100%, 96%, 90%, 99%.
- All six final pages were rendered and visually inspected at 88 and 140 DPI on 2026-11-26. No clipping, missing glyphs, broken references, or unintended blank pages were observed. All three figures were reviewed in the rendered pages.
- Known non-blocking publisher warning: Pillow `Image.getdata()` deprecation.

## Gate result

**PASS — current source mapping, Chinese chapter, three editable figures, offline VM operations model, targeted and full Windows/WSL tests, documented read-only diagnostic template, reproducible PDF, and final page-by-page visual review are complete.** No live Azure behavior or billing is claimed as verified.
