# Publishing and capture tools

The build, style, SVG figure, page-review, image-normalization and window-capture components in this directory are adapted from the AWS CloudOps textbook at commit b44160ea0f864ce7edf40cc0edb402cb53687a63. The source repository is licensed under Apache License 2.0; this adaptation retains that attribution. The Azure repository's original LICENSE remains unchanged. AWS chapter content and experiments are not reused as Azure evidence.

## Build one chapter

From the repository root, run:

    python textbook/tools/build.py AZ00-01

The command generates editable SVGs from the chapter's figures/figs.py, converts Markdown with Pandoc, applies the shared print stylesheet, prints PDF through installed headless Edge, and produces page-review sheets and a QA report in that chapter's ignored build directory.

The output path is textbook/dist/pdf/<id>_<slug>.pdf. A build and automated report do not equal complete visual acceptance: render and inspect every final page, inspect significant figures and dense code at readable scale, correct defects, then rebuild and inspect the affected pages again.

## Review and package

    python textbook/tools/pages.py path/to/chapter.pdf path/to/review 66
    python textbook/tools/package.py
    python textbook/tools/package.py --verify

The collection package is accepted only with exactly 23 PDFs. The source package includes editable sources and Terraform dependency lock files, and excludes build directories, provider caches, local-only redaction maps, raw state and plans. Optional local secret-pattern scans use tools/sensitive.local.txt, which is ignored by Git.

## Azure Portal captures

Capture only an existing owner-authorized browser session and navigate read-only. Do not create resources, save configuration, enable a paid service or change identity/tenant settings. Use console_prep.js only as a visual redaction aid; review the resulting image before it enters the chapter. The script redacts Azure resource paths, GUIDs, email addresses and IP addresses and supports additional local substitutions through window.__AZURE_REDACTIONS__. Do not place live replacement values in tracked files. Never claim a screenshot is genuine unless it was actually captured from the interface.
