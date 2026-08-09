# Media directory

Tier-1 media files (historical stills, bundled offline) for this tour.
Referenced by waypoints via the `media` array in `tour.json`.

## Conventions

- **Images <500KB:** include here (JPEG preferred, PNG for diagrams)
- **Images >500KB:** reference via URL in `media.schema.json` tier-2 entry
- **Videos:** always reference via URL (tier-2 or tier-3), never bundle
- **Naming:** `{waypoint-id}-{descriptor}.{ext}` (e.g., `beals-83-porch-1920.jpg`)
- **License:** every file needs a corresponding entry in `tour.json`'s credits
  and/or the waypoint's `dossier.sources` with license metadata

## File size budget

Total bundle target: <50MB (including all audio).
Audio currently runs ~10-12MB per bundle.
That leaves ~35MB for media — roughly 70 images at 500KB each,
which is more than enough for a 15-stop tour at 4-5 images per stop.

## In the schema

Each media file is declared in `tour.json` under either:
- `waypoints[].media` — array of media IDs referenced at that stop
- A top-level `media` array (if added to `tour.schema.json`)

The `media.schema.json` defines the full metadata shape (tier, type,
title, caption, license, path, dimensions, etc.).
