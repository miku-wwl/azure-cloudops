#!/usr/bin/env bash
# Repository test runner. Terraform init can fetch locked provider binaries.
# The Terraform runner removes Azure credentials and executes mock-backed plan tests only.
set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

run_python=1
run_terraform=1
run_package=0
case "${1:-}" in
  "") ;;
  --python) run_terraform=0 ;;
  --terraform) run_python=0 ;;
  --package) run_python=0; run_terraform=0; run_package=1 ;;
  *) echo "usage: bash tools/test_all.sh [--python|--terraform|--package]" >&2; exit 2 ;;
esac

PY=python3
"$PY" -c 'import sys' >/dev/null 2>&1 || PY=python
export PYTHONDONTWRITEBYTECODE=1 PYTHONIOENCODING=utf-8
python_failures=0

if [ "$run_python" -eq 1 ]; then
  echo "== Python: repository-wide test runner"
  if ! "$PY" tools/test_python.py; then
    python_failures=1
  fi
fi

if [ "$run_terraform" -eq 1 ]; then
  if ! "$PY" tools/verify_terraform.py; then
    exit 1
  fi
fi

if [ "$run_package" -eq 1 ]; then
  "$PY" tools/package.py --verify
fi

if [ "$python_failures" -gt 0 ]; then exit 1; fi
