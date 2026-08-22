#!/usr/bin/env python3
"""validate_bundle.py — pre-publish gate that mirrors the app's BundleValidator.

The Swift app (TourPlayer/Bundle/BundleValidator.swift) refuses to import a
bundle whose manifest.json or tour.json fails to decode against its Codable
models, or that trips an error-severity check. This script reproduces those
error-level checks in Python so a bad bundle is caught BEFORE it's zipped and
uploaded — not after a tester hits "validation failure" on download.

Run on one or more bundle directories:

    python3 validate_bundle.py mv-bike-loop mv-oak-bluffs
    python3 validate_bundle.py */          # all bundles in cwd

Exit code 0 = all bundles pass. Non-zero = at least one error.

Checks (error severity — these block import in the app):
  manifest.json present and decodes with required keys
    schema_version, bundle_id, title, core{id,kind,version,path}, personas[]
    each persona: id, version, path, display_name
  tour.json present and decodes: schema_version, waypoints[] with id + position
  schema major version == 1
  no duplicate waypoint ids
  no duplicate persona ids
  every manifest persona has personas/<id>.json on disk
  every waypoint trigger radius > 0
  no path traversal ('..' or leading '/') in any audio path
  every live persona covers every waypoint with narration + a real audio file
    (non-kokoro providers are allowed to fall back; kokoro requires the file)

Warnings (do NOT block, but printed):
  GPS out of range or (0,0); waypoint order gaps; missing walking cue on
  a non-terminal stop.
"""

import json
import sys
from pathlib import Path

ERRORS = []
WARNINGS = []


def err(bundle, msg):
    ERRORS.append(f"{bundle}: {msg}")


def warn(bundle, msg):
    WARNINGS.append(f"{bundle}: {msg}")


def _require(bundle, obj, keys, where):
    missing = [k for k in keys if k not in obj]
    if missing:
        err(bundle, f"{where} missing required key(s): {', '.join(missing)}")
    return not missing


def validate_manifest(bundle, root):
    p = root / "manifest.json"
    if not p.exists():
        err(bundle, "manifest.json missing from bundle")
        return None
    try:
        m = json.loads(p.read_text())
    except Exception as e:
        err(bundle, f"manifest.json malformed JSON: {e}")
        return None

    _require(bundle, m, ["schema_version", "bundle_id", "title", "core", "personas"], "manifest")

    if isinstance(m.get("core"), dict):
        _require(bundle, m["core"], ["id", "kind", "version", "path"], "manifest.core")
    elif "core" in m:
        err(bundle, "manifest.core must be an object")

    seen = set()
    for i, persona in enumerate(m.get("personas", [])):
        if not isinstance(persona, dict):
            err(bundle, f"manifest.personas[{i}] must be an object")
            continue
        _require(bundle, persona, ["id", "version", "path", "display_name"], f"manifest.personas[{i}]")
        pid = persona.get("id")
        if pid in seen:
            err(bundle, f"duplicate persona id in manifest: {pid}")
        seen.add(pid)

    ver = m.get("schema_version", "")
    if ver and not ver.split(".")[0] == "1":
        err(bundle, f"manifest schema_version major must be 1, got {ver}")
    return m


def validate_tour(bundle, root):
    p = root / "tour.json"
    if not p.exists():
        err(bundle, "tour.json missing from bundle")
        return None
    try:
        t = json.loads(p.read_text())
    except Exception as e:
        err(bundle, f"tour.json malformed JSON: {e}")
        return None

    _require(bundle, t, ["schema_version", "id", "version", "title", "locale", "kind", "waypoints"], "tour")
    ver = t.get("schema_version", "")
    if ver and not ver.split(".")[0] == "1":
        err(bundle, f"tour schema_version major must be 1, got {ver}")

    ids = []
    for i, wp in enumerate(t.get("waypoints", [])):
        if not _require(bundle, wp, ["id", "name", "position", "trigger", "dossier"],
                        f"tour.waypoints[{i}]"):
            continue
        ids.append(wp["id"])
        pos = wp.get("position", {})
        if isinstance(pos, dict):
            _require(bundle, pos, ["lat", "lon"], f"tour.waypoints[{i}].position")
        trig = wp.get("trigger", {})
        if isinstance(trig, dict):
            if trig.get("radius", 0) <= 0:
                err(bundle, f"waypoint '{wp['id']}' has non-positive trigger.radius: {trig.get('radius')}")
        doss = wp.get("dossier", {})
        if isinstance(doss, dict):
            _require(bundle, doss, ["summary", "text"], f"tour.waypoints[{i}].dossier")
        lat = pos.get("lat", 0) if isinstance(pos, dict) else 0
        lon = pos.get("lon", 0) if isinstance(pos, dict) else 0
        if not (-90 <= lat <= 90) or not (-180 <= lon <= 180):
            warn(bundle, f"waypoint '{wp['id']}' out-of-range coords ({lat},{lon})")
        elif lat == 0 and lon == 0:
            warn(bundle, f"waypoint '{wp['id']}' at (0,0)")

    dupes = {x for x in ids if ids.count(x) > 1}
    if dupes:
        err(bundle, f"duplicate waypoint ids: {', '.join(sorted(dupes))}")

    orders = sorted(wp["order"] for wp in t.get("waypoints", []) if "order" in wp)
    for a, b in zip(orders, orders[1:]):
        if b != a + 1:
            warn(bundle, f"waypoint order has gaps: {orders}")
            break
    return t


def validate_coverage(bundle, root, manifest, tour):
    if not manifest or not tour:
        return
    wp_ids = [w["id"] for w in tour.get("waypoints", [])]
    terminal = {w["id"] for w in tour.get("waypoints", []) if w.get("terminal")}
    last_id = None
    if tour.get("waypoints"):
        last_id = sorted(tour["waypoints"], key=lambda w: w.get("order", 0))[-1]["id"]

    for pc in manifest.get("personas", []):
        pid = pc.get("id")
        pf = root / "personas" / f"{pid}.json"
        if not pf.exists():
            err(bundle, f"persona file missing: personas/{pid}.json")
            continue
        try:
            persona = json.loads(pf.read_text())
        except Exception as e:
            err(bundle, f"personas/{pid}.json malformed: {e}")
            continue

        provider_default = persona.get("voice", {}).get("provider", "")
        lines = {ln["waypoint"]: ln for ln in persona.get("lines", [])}
        for wid in wp_ids:
            ln = lines.get(wid)
            if ln is None:
                err(bundle, f"{pid}: no line for waypoint {wid}")
                continue
            for field in ("narration", "walking_cue_narration", "deep_narration"):
                if field not in ln:
                    if field == "walking_cue_narration" and wid != last_id and wid not in terminal:
                        warn(bundle, f"{pid} @ {wid}: missing walking_cue_narration")
                    continue
                block = ln[field]
                audio = block.get("audio", {})
                path = audio.get("path", "")
                if ".." in path or path.startswith("/"):
                    err(bundle, f"{pid} @ {wid} {field}: unsafe audio path {path!r}")
                provider = audio.get("voice_provider", provider_default)
                if provider == "kokoro":
                    if not path:
                        err(bundle, f"{pid} @ {wid} {field}: kokoro line has no audio path")
                    elif not (root / path).exists():
                        err(bundle, f"{pid} @ {wid} {field}: audio file missing on disk: {path}")
                    elif audio.get("duration", 0) <= 0:
                        err(bundle, f"{pid} @ {wid} {field}: audio duration is {audio.get('duration')} (not measured)")


def validate_bundle(bundle_dir):
    root = Path(bundle_dir)
    bundle = root.name.rstrip("/")
    if not root.is_dir() or not (root / "manifest.json").exists():
        return  # not a bundle
    m = validate_manifest(bundle, root)
    t = validate_tour(bundle, root)
    validate_coverage(bundle, root, m, t)


def main(args):
    if not args:
        print("usage: validate_bundle.py <bundle_dir> [<bundle_dir> ...]")
        return 2
    checked = 0
    for a in args:
        root = Path(a)
        if root.is_dir() and (root / "manifest.json").exists():
            validate_bundle(a)
            checked += 1

    for w in WARNINGS:
        print(f"  WARN  {w}")
    if ERRORS:
        print()
        for e in ERRORS:
            print(f"  ERROR {e}")
        print(f"\nFAIL — {len(ERRORS)} error(s) across {checked} bundle(s). "
              f"These would fail import in the app.")
        return 1
    print(f"\nOK — {checked} bundle(s) passed app-model validation"
          + (f" ({len(WARNINGS)} warning(s))" if WARNINGS else ""))
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
