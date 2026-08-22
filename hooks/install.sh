#!/usr/bin/env bash
# Installs the tracked git hooks into .git/hooks.
# Run once per clone:  ./hooks/install.sh
set -euo pipefail

REPO_ROOT="$(git rev-parse --show-toplevel)"
HOOK_SRC="$REPO_ROOT/hooks"
HOOK_DST="$REPO_ROOT/.git/hooks"

for hook in pre-push; do
    cp "$HOOK_SRC/$hook" "$HOOK_DST/$hook"
    chmod +x "$HOOK_DST/$hook"
    echo "installed $hook -> .git/hooks/$hook"
done

echo "Done. Hooks active for this clone."
