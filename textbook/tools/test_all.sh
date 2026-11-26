#!/usr/bin/env bash
# Offline test runner. It installs providers only; it never authenticates to Azure,
# creates Azure resources, or invokes Terraform apply/destroy.
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
python_dirs=0
tf_dirs=0
python_failures=0
tf_failures=0

if [ "$run_python" -eq 1 ]; then
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    python_dirs=$((python_dirs + 1))
    echo "== Python: $d"
    if ! (cd "$d" && "$PY" -m unittest -v); then
      python_failures=$((python_failures + 1))
    fi
  done < <(find chapters -type f -name 'test_*.py' -not -path '*/build/*' -not -path '*/.terraform/*' -printf '%h\n' | sort -u)
  echo "Python test directories: $python_dirs; failed: $python_failures"
fi

if [ "$run_terraform" -eq 1 ]; then
  if ! command -v terraform >/dev/null 2>&1; then
    echo "terraform is required for --terraform" >&2
    exit 2
  fi
  terraform fmt -check -recursive -diff chapters
  while IFS= read -r d; do
    [ -n "$d" ] || continue
    tf_dirs=$((tf_dirs + 1))
    echo "== Terraform: $d"
    if ! terraform -chdir="$d" init -backend=false -input=false -no-color; then
      tf_failures=$((tf_failures + 1))
      continue
    fi
    if ! terraform -chdir="$d" validate -no-color; then
      tf_failures=$((tf_failures + 1))
      continue
    fi
    if find "$d" -type f -path '*/tests/*.tftest.hcl' -print -quit | grep -q .; then
      if ! terraform -chdir="$d" test -no-color; then
        tf_failures=$((tf_failures + 1))
      fi
    fi
  done < <(find chapters -type f -name 'main.tf' -not -path '*/build/*' -not -path '*/.terraform/*' -printf '%h\n' | sort -u)
  echo "Terraform roots: $tf_dirs; failed: $tf_failures"
fi

if [ "$run_package" -eq 1 ]; then
  "$PY" tools/package.py --verify
fi

if [ "$python_failures" -gt 0 ] || [ "$tf_failures" -gt 0 ]; then exit 1; fi
