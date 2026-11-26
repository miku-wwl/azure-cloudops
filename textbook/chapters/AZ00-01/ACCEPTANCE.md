# AZ00-01 lecture acceptance record

**Lecture:** Azure Landing Zone, ARM and Control Plane

**Acceptance date:** 2026-11-26 (Pacific/Auckland)
**Status:** ACCEPTED for Stage 1 lecture gate. Azure behavior itself remains `LIVE_NOT_RUN`.

## Research and source

- Research was performed against Microsoft Learn primary sources on 2026-11-26. URLs, claim mapping and limits are in `textbook/SOURCE_MAP.md`.
- Topics include Cloud Adoption Framework landing zones, management-group and subscription design, ARM requests, control/data plane separation, asynchronous operations, provider registration, RBAC scope and Azure Policy scope.
- Three original mechanism figures are editable in `figures/figs.py`; generated SVGs are `landing-zone-hierarchy.svg`, `arm-request-lifecycle.svg` and `provider-registration.svg`.

## Experiment and evidence boundary

- The pure-Python `labs/scope-model` fixture uses synthetic scopes and assignments. It demonstrates ancestor inheritance and separate Actions/DataActions matching only; it does not implement Azure RBAC or emulate Azure.
- Seven unit tests passed on the Windows host's Python 3.13.9. The printed Windows test output is preserved in the lecture. The suite also passed in `devops-lab` WSL through `textbook/tools/test_all.sh --python`: 7 tests, 1 test directory, 0 failures (2026-11-26).
- The lab instructions and exclusions are in `labs/README.md`. Azure authentication, subscription inspection, provider registration, and resource creation were not performed.

## Publication inspection

- Reproduction from the repository root: `python textbook/tools/build.py AZ00-01`.
- Output: `textbook/dist/pdf/AZ00-01_azure-landing-zone-arm-control-plane.pdf`; 8 pages, 1,975,358 bytes.
- Final automated report: 13,443 extracted characters; no placeholder markers; no overflow warnings; page fill 49%, 96%, 99%, 96%, 84%, 82%, 100%, 91%.
- All 8 final pages were rendered at readable scale and visually inspected on 2026-11-26. The three original figures, code, console output, exercises, references, headers, page numbering and margins were checked.
- Two confirmed presentation issues were corrected before acceptance: the code excerpt now wraps at syntax boundaries, and the provider reference label no longer splits an English word. The affected pages were rebuilt and re-inspected.
- Build succeeds with a Pillow `Image.getdata()` deprecation warning from the QA ink calculation. It does not affect rendering or the current build; the warning is retained as a known tool maintenance item.

## Gate result

**PASS — lecture source, research mapping, figures, applicable offline experiment, actual tests, live-lab instructions, PDF build, full-page visual inspection, corrections, rebuild and evidence record are complete.** This result does not claim Azure service behavior was verified.
