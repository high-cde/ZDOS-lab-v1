#!/usr/bin/env bash
# Verify that ZDOS Lab tracks orchestration and contracts, not generated bundles.
set -Eeuo pipefail

ROOT=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
cd "$ROOT"

fail() {
  printf 'ZDOS_LAB_HYGIENE_FAILED: %s\n' "$*" >&2
  exit 1
}

command -v git >/dev/null 2>&1 || fail 'git is required'
git diff --check || fail 'whitespace errors detected'

forbidden=$(git ls-files | grep -E '^artifacts/lab-state\.json$|^artifacts/portable/|(^|/)__pycache__/|\.py[co]$|(^|/)\.pytest_cache/' | grep -v '^artifacts/portable/\.gitkeep$' || true)
if [[ -n "$forbidden" ]]; then
  printf '%s\n' "$forbidden" >&2
  fail 'generated state or distributable bundle is tracked'
fi

git check-ignore -q --no-index artifacts/lab-state.json || fail 'generated lab state is not ignored'
git check-ignore -q --no-index artifacts/portable/release.zip || fail 'portable bundle output is not ignored'
printf 'ZDOS_LAB_HYGIENE_OK\n'
