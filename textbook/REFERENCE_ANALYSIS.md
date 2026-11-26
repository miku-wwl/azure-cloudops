# B0 — AWS CloudOps reference analysis

## Scope and provenance

- Reference repository: https://github.com/miku-wwl/aws-cloudops
- Required revision: b44160ea0f864ce7edf40cc0edb402cb53687a63
- Local checkout: D:/workshop/nov/aws-cloudops, branch main at that exact revision.
- The reference checkout was clean before and after inspection. No files in it were changed.
- Azure target baseline: 853ba6cbaa4ee67e448550fbe192c6c89b24fd2f on main; origin/main was fetched and matched.

## Inspected engineering and publication structure

At the specified AWS revision, the tracked source contains 19 chapter directories and 19 editable diagram programs. The inventory contains 22 Python test files and 18 Terraform mock-test files. The reference textbook reports 119 passing Python unit tests and 95 mock-provider test runs; those totals are recorded here as source-reported results, not as tests rerun during this Azure project.

The local AWS publication directory contains 19 PDFs. The reference package verifier was run read-only against the exact checkout and reported that the PDF ZIP contains 19 byte-consistent PDFs and the source ZIP contains 445 files consistent with the source tree.

The review covered all 22 pages of A00-01 and all 10 pages of FIN-01 as contact sheets. Pages 3, 14 and 21 of A00-01 were additionally rendered at 130 dpi and inspected at full resolution. The reviewed examples use problem-led openings, mechanism diagrams with explicit arrow meanings, code and configuration beside their reasoning, fault and exercise cards, detailed solutions, page numbering and source references. The selected pages were legible at page size; no clipping or missing-glyph defect was found in these inspected pages. This is a representative reference review, not a claim that every AWS page was re-reviewed.

## Publishing architecture selected for adaptation

The AWS pipeline is:

1. An editable per-chapter Python program generates SVG diagrams through textbook/tools/figlib.py.
2. Pandoc converts the chapter Markdown to HTML.
3. textbook/tools/build.py adds syntax highlighting and book styles, then prints with headless Chrome or Edge.
4. Poppler renders PDF pages for review; textbook/tools/pages.py creates two-page review sheets.
5. textbook/tools/package.py builds and verifies separate PDF and editable-source ZIPs, checks byte consistency, excludes caches and sensitive local files, and scans optional local deny patterns.

The browser screenshot workflow is read-only. console_prep.js performs in-page substitution before capture; shot.py crops and normalizes a derived image; local replacement maps and sensitive-pattern lists are excluded from publication. No Azure Portal session was used and no Azure screenshot is included or implied.

The offline CI uses least-privilege repository read access and no cloud credentials. It verifies packages, runs Python unit tests, and runs Terraform fmt/validate/mock-provider checks. These checks do not establish cloud behavior.

## Host capability snapshot (2026-11-26)

- Python 3.13.9, Pandoc 3.8, Terraform 1.15.5 and Poppler tools are available.
- Microsoft Edge is available at the standard Program Files path. Noto Sans SC, Noto Serif SC and Cascadia Mono fonts are installed.
- Azure CLI, PowerShell, Node.js and kubectl commands are present; their versions and runtime behavior were not checked in B0.
- Podman is not installed. Local Kubernetes/container runtime readiness is not established.
- Python packages reportlab, pdfplumber, pypdf, Pillow, PyYAML, Pygments, CairoSVG, PyMuPDF and lxml are installed. WeasyPrint is not installed.

## Attribution and limits

The adapted publishing components retain the AWS CloudOps Apache-2.0 attribution in textbook/tools/README.md. The Azure repository's original LICENSE is preserved unchanged. AWS-specific experiments and content are not copied as Azure teaching material. Azure mechanisms must be researched independently from current primary sources.
