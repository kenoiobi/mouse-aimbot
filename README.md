# kill-mouse

Local daemon that detects on-screen GUI widgets and **magnetically snaps** the OS cursor toward them. Built for imprecise pointing (eye trackers, trackpoints, low-DPI mice).

Detection + overlay pattern come from **[TargetFinder Toolkit](https://github.com/ahmedbenakouche/target_finder_toolkit)** (MIT, pulled from PyPI); snap math is ours. See `NOTICE`.

> **MVP status:** Primary monitor focus. Force-quit hotkey required — this moves your real cursor.

## Safety

**`Ctrl+Alt+Q`** force-quits immediately.

## Setup

Needs [uv](https://docs.astral.sh/uv/).

```powershell
cd kill-mouse
uv sync
```

Or just `.\run.ps1` / `.\debug.ps1` — installs uv if missing, syncs, and runs.

## Run

```powershell
.\run.ps1          # snap only (no overlay) — daily driver
.\debug.ps1        # snap + on-screen detection boxes
uv run kill-mouse  # same as debug
uv run python -m kill_mouse --no-overlay
```

## What to expect

- UI-trained YOLO26 via TargetFinder (buttons, links, inputs, …)
- Cyan outlines = candidates; green = snapped target
- Magnetic pull within ~50px of a box (`kill_mouse/config.py`)

## License

- **kill-mouse code:** MIT
- **TargetFinder Toolkit:** MIT — https://github.com/ahmedbenakouche/target_finder_toolkit
- **ultralytics:** AGPL-3.0 — see `NOTICE`
