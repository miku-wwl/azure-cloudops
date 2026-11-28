# AZ06-01 Acceptance — Azure Backup, Recovery and Site Recovery

## V1.0.1 教材修订

- 更正 RTO 图注，补策略/point、隔离恢复、完整性及 retained 资源。
- 最终教材 [PDF](../../dist/pdf/AZ06-01_azure-backup-restore-site-recovery.pdf) 已用原出版工具重建。基线 7 页，修订 8 页。正文排入 5 个 SVG，保留 5 个可编辑图稿。最终页面已检查排版、图和代码，带入全套发布校验。
- 现有本地回归通过。新增云端步骤按文档例处理，历史证据与操作权限见 [V1.0.1 逐讲审查](../../V1_0_1_TEXTBOOK_REVIEW.md)。

- Status: ACCEPTED for the offline lecture gate.
- Review date: 2026-11-27 (Pacific/Auckland).
- Lecture: 17 / 23; phase B6 is in progress.

## Publication artifact

- PDF: `textbook/dist/pdf/AZ06-01_azure-backup-restore-site-recovery.pdf`
- Pages: 7; size: 1,594,885 bytes.
- SHA-256: `366d9c0f715a8bd0041b5a9b2ad68f80004e0e71e949c2c75daa134e292cdbbc`.
- Publisher QA: 10,790 extracted characters; no placeholder markers or overflow warnings.
- Page fill ratios: 76%, 73%, 98%, 94%, 95%, 96%, 56%.
- All pages were rendered and visually reviewed at 88 and 140 DPI. Pages 5–7 were rechecked at 140 DPI after correcting the operational RTO definition and timeline.

## Technical and teaching evidence

- Five original editable SVG mechanism figures cover Backup versus replication, consistency levels, restore paths, Site Recovery flow, and RPO/RTO timing.
- The standard-library `recovery-model` lab has six synthetic recovery cases and 16 local unit tests.
- The model calculates RPO from the failure/data-loss start to the selected recovery point. It calculates operational RTO from business interruption to verified service; recovery-start delay is included. Integrity, record-count, application-probe, isolation, and cleanup gates are checked separately.
- Full offline suites passed on Windows and in WSL: 280 tests across 17 lab directories in each environment.
- Microsoft Learn sources and section-level claim mapping are recorded in `textbook/SOURCE_MAP.md`.

## Scope and limits

- The fixtures, timestamps, data digests, record counts, consistency labels, and probes are synthetic. The lab is not an Azure Backup or Site Recovery simulator and does not establish a service SLA or real workload RPO/RTO.
- No Azure sign-in, identity/account/context enumeration, Azure/ARM/Backup/Site Recovery request, resource operation, network probe, or billing query was performed.
- Actual cumulative Azure spend remains `NOT_VERIFIED`. Offline tests made no Azure request and created no project Azure resource charge.
- Stage 2 readiness engineering and Stage 3 authorization/cost gates remain outstanding for the overall project.

## Reproduction

From the repository root:

```powershell
python -m unittest discover -s textbook/chapters/AZ06-01/labs/recovery-model -p "test_*.py" -v
python textbook/chapters/AZ06-01/labs/recovery-model/recovery_model.py
python textbook/tools/build.py AZ06-01
```

The full Windows and WSL suite commands and observed results are summarized in `textbook/PROGRESS.md` and `textbook/VERIFICATION_MATRIX.md`.
