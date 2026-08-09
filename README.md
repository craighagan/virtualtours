# Virtual Tours

Open walking tour content for the [Footnotes](https://github.com/virtual-tours) app.

Each folder is a self-contained tour bundle: narration, audio, waypoints, and metadata. Download a folder, zip it as `.tourguide`, and AirDrop to the app — or import via URL.

## Tours

| Tour | Location | Stops | Distance | Time | Terrain |
|------|----------|-------|----------|------|---------|
| [brookline-coolidge-corner](brookline-coolidge-corner/) | Brookline, MA | 6 | 1.9 km | ~60 min | Flat |
| [brookline-aspinwall-hill](brookline-aspinwall-hill/) | Brookline, MA | 4 | 260 m | ~20 min | Moderate hill |
| [brookline-coolidge-village](brookline-coolidge-village/) | Brookline, MA | 8 | 2.4 km | ~60 min | Flat |
| [brookline-olmsted](brookline-olmsted/) | Brookline, MA | 7 | 4.0 km | ~70 min | Gentle |
| [brookline-aspinwall-paths](brookline-aspinwall-paths/) | Brookline, MA | 8 | 2.8 km | ~75 min | Steep, stairs |
| [york-village](york-village/) | York, ME | 6 | 1.2 km | ~45 min | Flat |
| [york-beach](york-beach/) | York Beach, ME | 11 | 5.6 km | ~70 min | Coastal, varied |

## Personas

Each tour includes 4 narrator personas — pick a different one per family member:

- **Gus** (oldtimer) — Personal memory, tall tales, rambles. Regional flavor varies by location.
- **Onyx** (operator) — What things cost, who maintains them, who got away with something.
- **Nova** (confidante) — Who got to become who, people's choices, what's not on the plaque.
- **Jessica** (fieldnaturalist) — What's living here right now, architecture as ecology, present-tense observation.

## How to use

**With the Footnotes app:**
1. Download a tour folder
2. Zip it: `zip -r tour.tourguide brookline-coolidge-corner/`
3. AirDrop the `.tourguide` file to your phone
4. Or: host the zip at a URL → paste URL in app → Import

**Without the app:**
The `tour.json` and `personas/*.json` files are human-readable. Each stop has a dossier with sourced historical facts, and each persona has full narration text you can read aloud.

## Bundle structure

```
tour-name/
├── manifest.json          # Tour metadata, persona list, tags
├── tour.json              # Waypoints, dossiers, walking cues
├── personas/
│   ├── oldtimer.json      # Gus — narration per stop
│   ├── operator.json      # Onyx
│   ├── confidante.json    # Nova
│   └── fieldnaturalist.json  # Jessica
└── audio/
    ├── oldtimer/*.m4a     # Pre-rendered narration audio
    ├── operator/*.m4a
    ├── confidante/*.m4a
    └── fieldnaturalist/*.m4a
```

## Contributing

Want to add a tour? See the [tour authoring guide](https://github.com/virtual-tours/virtualtours/wiki) (coming soon).

Requirements:
- 5-12 stops, walkable in 45-90 minutes
- All facts sourced (no made-up history)
- All narration text safe for Kokoro TTS (spell out years, no abbreviations)
- GPS coordinates (even desk estimates work — mark as unverified)

## License

This work is licensed under the [Creative Commons Attribution-ShareAlike 4.0 International License](https://creativecommons.org/licenses/by-sa/4.0/).

You are free to share and adapt this content for any purpose, including commercial, as long as you give appropriate credit and distribute your contributions under the same license. See [LICENSE](LICENSE) for the full legal text.

## Attribution

See [ATTRIBUTION.md](ATTRIBUTION.md) for source credits (NPS, historical societies, OpenStreetMap).
