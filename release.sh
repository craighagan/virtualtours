#!/usr/bin/env bash
# release.sh — Build .tourguide zip files and create a GitHub Release.
#
# Usage:
#   ./release.sh v1.0        # Creates release v1.0 with all tour zips
#   ./release.sh v1.1 --dry-run   # Shows what would be uploaded
#
# Requires: gh CLI (brew install gh), authenticated (gh auth login)

set -euo pipefail

VERSION="${1:-}"
DRY_RUN="${2:-}"

if [ -z "$VERSION" ]; then
    echo "Usage: ./release.sh <version-tag> [--dry-run]"
    echo "Example: ./release.sh v1.0"
    exit 1
fi

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
DIST_DIR="$SCRIPT_DIR/.release-build"
rm -rf "$DIST_DIR"
mkdir -p "$DIST_DIR"

echo "=== Building .tourguide files for $VERSION ==="
echo ""

# --- Pre-publish validation gate ------------------------------------------
# Every bundle must decode against the app's models before it can be zipped.
# This catches the flat-waypoint / missing-core manifest class of bug that
# shipped broken MV and Boston tours in Aug 2026 (validation failure on
# download). See tools/validate_bundle.py.
echo "=== Validating bundles ==="
VALIDATE_TARGETS=()
for dir in "$SCRIPT_DIR"/*/; do
    [ -f "$dir/manifest.json" ] && VALIDATE_TARGETS+=("$dir")
done
if ! python3 "$SCRIPT_DIR/tools/validate_bundle.py" "${VALIDATE_TARGETS[@]}"; then
    echo ""
    echo "ABORT: one or more bundles failed validation. Nothing published." >&2
    rm -rf "$DIST_DIR"
    exit 1
fi
echo ""


TOURS=()
for dir in "$SCRIPT_DIR"/*/; do
    if [ -f "$dir/manifest.json" ]; then
        name=$(basename "$dir")
        zip_file="$DIST_DIR/$name.tourguide"
        echo "  Zipping $name..."
        (cd "$SCRIPT_DIR" && zip -r "$zip_file" "$name/" -x "*.DS_Store" -x "*/.git/*" > /dev/null)
        size=$(du -h "$zip_file" | cut -f1)
        echo "    → $name.tourguide ($size)"
        TOURS+=("$zip_file")
    fi
done

echo ""
echo "=== ${#TOURS[@]} tours built ==="
echo ""

if [ "$DRY_RUN" = "--dry-run" ]; then
    echo "[DRY RUN] Would create release $VERSION with:"
    for t in "${TOURS[@]}"; do
        echo "  $(basename "$t")"
    done
    echo ""
    echo "Run without --dry-run to publish."
    rm -rf "$DIST_DIR"
    exit 0
fi

# Create the release
echo "Creating GitHub Release $VERSION..."
NOTES="Walking tours for the Footnotes app.

Download any .tourguide file and:
- AirDrop it to your iPhone, or
- Host it at a URL and paste into the app's Import function

${#TOURS[@]} tours included in this release. See README.md for the full tour list."

gh release create "$VERSION" \
    --title "Virtual Tours $VERSION" \
    --notes "$NOTES" \
    "${TOURS[@]}"

echo ""
echo "=== Release $VERSION published ==="
echo "https://github.com/craighagan/virtualtours/releases/tag/$VERSION"

# Cleanup
rm -rf "$DIST_DIR"
