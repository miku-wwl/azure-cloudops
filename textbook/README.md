# Azure CloudOps Technical Textbook

This directory is the single authoritative home for the 23 lecture sources, editable mechanisms, chapter experiments, generated PDFs and release packages. Each chapter source is Chinese explanatory prose with the original English names of Azure mechanisms.

## Structure

- CURRICULUM.md — approved 23-lecture sequence and core questions.
- PROGRESS.md — current project gate and restart point.
- FINAL_ACCEPTANCE_REPORT.md — Stage 1/2 acceptance evidence, publication metrics, exact CI result, Stage 3 L0 findings and the proposed live-batch approval boundary.
- L0_READ_ONLY_PREFLIGHT.md — redacted Stage 3 Azure read-only results and the concrete LAB-IR-11 candidate.
- incidents/live_ir11/ — no-dependency good/fault ZIP sources, local package builder and probe runbook for the proposed IR-11 batch.
- LIVE_LAB_INDEX.md — twelve incident contracts and their evidence status.
- COST_LEDGER.md — cumulative Azure estimate, actual-billing status and budget controls.
- VERIFICATION_MATRIX.md — independent evidence-state definitions.
- E0_INDEPENDENT_AUDIT.md — E0 findings, corrections and current offline re-verification.
- E3_TERRAFORM_ENGINEERING.md — E3 provider configuration, locked versions, fail-closed guards and offline verification evidence.
- E4_STATE_CONTROLLED_DELIVERY.md — E4 local State lifecycle/import/recovery, signed exact-plan gate, and conditional Azure Storage backend evidence and limits.
- architecture/ — E1 enterprise/local/conditional-live views and architecture decision records.
- LAB_ENVIRONMENT.md and E2_LOCAL_SUBSTRATE.md — checked local tool inventory and E2 runner/lifecycle acceptance.
- terraform/azure-enterprise-reference/ and E3_TERRAFORM_ENGINEERING.md — E3 AzureRM/AzAPI reference root, reusable modules, plan-only mock tests, and provider/authentication safeguards.
- terraform/azure-remote-state-backend/ and tools/controlled_apply.py — conditional OIDC Azure Storage backend and signature-verified saved-plan apply gate; remote backend and service-side approval remain NOT_RUN.
- REFERENCE_ANALYSIS.md — B0 AWS source and publication audit.
- tools/ — adapted, reproducible publication and offline verification tools.
- chapters/<lecture-id>/ — chapter.md, figures, screenshots and only the applicable lab sources.
- dist/pdf/ — exactly one independent final PDF per completed lecture.

## Publication and verification

The publisher adapts the AWS CloudOps source-and-SVG workflow at commit b44160ea0f864ce7edf40cc0edb402cb53687a63. Adapted components and their Apache-2.0 attribution are identified in tools/README.md. Azure services are researched independently; AWS experiments are not treated as Azure evidence.

Build one chapter from the repository root:

    python textbook/tools/build.py AZ00-01

The command generates editable SVGs from the chapter's `figures/figs.py`, prepares the HTML and PDF, and writes an automated render report plus review sheet into an ignored per-chapter `build/` directory. Automated QA is not visual acceptance; every final page must be rendered and inspected before the chapter gate passes.

Run the offline Python suites in the `devops-lab` WSL distribution:

    wsl -d devops-lab -- bash /mnt/d/workshop/nov/azure-cloudops/textbook/tools/test_all.sh --python

When the curriculum contains Terraform roots, the default `test_all.sh` also runs recursive format checks, backend-free init, validate and applicable mock tests. After all 23 PDFs exist, build and verify packages with `python textbook/tools/package.py` and `python textbook/tools/package.py --verify`.

Do not mark a chapter complete from Markdown alone: its research, source-to-claim map, figures, applicable experiment, actual checks, generated PDF and rendered-page inspection must pass the current acceptance criteria.
