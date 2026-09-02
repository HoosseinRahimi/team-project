#!/usr/bin/env bash
# Fail if unresolved Git conflict markers are committed to tracked source files.
set -euo pipefail

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

pattern='^(<<<<<<<|=======|>>>>>>>)'
if git rev-parse --is-inside-work-tree >/dev/null 2>&1; then
  files=$(git ls-files)
else
  files=$(find . -type f -not -path './.git/*' -not -path './frontend/node_modules/*' -not -path './.venv/*')
fi

violations=$(echo "$files" | xargs -r grep -InE "$pattern" -- 2>/dev/null | grep -vE 'docs/|README|CONTRIBUTING' || true)
if [[ -n "$violations" ]]; then
  echo "Unresolved conflict markers found:" >&2
  echo "$violations" >&2
  exit 1
fi
echo "No unresolved conflict markers found."
