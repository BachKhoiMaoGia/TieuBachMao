#!/usr/bin/env bash
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel 2>/dev/null || pwd)"
cd "$REPO_ROOT"

PATTERNS=(
  "authorization[[:space:]]*:[[:space:]]*bearer[[:space:]]+[A-Za-z0-9._-]{20,}"
  "(^|[^A-Za-z])(spc_tk|spc_cds|csrftoken|af_ac_enc_dat|sessionid|shopee_token)[[:space:]]*[=:][[:space:]]*[^[:space:]]+"
  "(access|refresh)_token[[:space:]]*[=:][[:space:]]*['\" ]?[A-Za-z0-9._-]{10,}"
  "client_secret[[:space:]]*[=:][[:space:]]*['\" ]?[A-Za-z0-9._-]{10,}"
  "api[_-]?key[[:space:]]*[=:][[:space:]]*['\" ]?[A-Za-z0-9._-]{10,}"
  "password[[:space:]]*[=:][[:space:]]*[^[:space:]]+"
)

SKIP_FILES=(
  "scripts/scan-secrets.sh"
  "scripts/install-hooks.sh"
  ".githooks/pre-push"
)

skip_file() {
  local f="$1"
  local s
  for s in "${SKIP_FILES[@]}"; do
    if [[ "$f" == "$s" ]]; then
      return 0
    fi
  done
  return 1
}

is_text_candidate() {
  local f="$1"
  case "$f" in
    *.png|*.jpg|*.jpeg|*.webp|*.ico|*.gif|*.svg|*.pdf|*.zip|*.gz|*.tar|*.woff|*.woff2|*.ttf|*.otf|*.mp4|*.mov)
      return 1
      ;;
    *)
      return 0
      ;;
  esac
}

FOUND=0

while IFS= read -r file; do
  [[ -z "$file" ]] && continue
  [[ -f "$file" ]] || continue
  skip_file "$file" && continue
  is_text_candidate "$file" || continue

  for pattern in "${PATTERNS[@]}"; do
    if grep -nEI -- "$pattern" "$file" >/dev/null; then
      if [[ $FOUND -eq 0 ]]; then
        echo "[secret-scan] Found potential sensitive data:"
      fi
      FOUND=1
      echo ""
      echo "- File: $file"
      grep -nEI -- "$pattern" "$file" || true
      break
    fi
  done
done < <(git ls-files)

if [[ $FOUND -eq 1 ]]; then
  echo ""
  echo "[secret-scan] Blocked. Remove sensitive data before push."
  exit 1
fi

echo "[secret-scan] OK - no obvious secrets found."
