# Azure CloudOps Technical Textbook

This directory is the single authoritative home for the 23 lecture sources, editable mechanisms, chapter experiments, generated PDFs and release packages. Each chapter source is Chinese explanatory prose with the original English names of Azure mechanisms.

## Structure

- CURRICULUM.md — approved 23-lecture sequence and core questions.
- PROGRESS.md — current project gate and restart point.
- LIVE_LAB_INDEX.md — twelve incident contracts and their evidence status.
- COST_LEDGER.md — cumulative Azure estimate, actual-billing status and budget controls.
- VERIFICATION_MATRIX.md — independent evidence-state definitions.
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
