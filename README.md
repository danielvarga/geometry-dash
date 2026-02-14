# Stereo Madness (Pygame Fan Remake)

## Run

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

## Web Build (pygbag / emscripten runtime)

```bash
pip install pygbag pygame-ce
python -m pygbag --build .
```

- Output is generated under `build/web/`.
- Local preview:

```bash
python -m pygbag .
```

- Deploy by uploading the contents of `build/web/` to your static folder:
  - `https://static.renyi.hu/ai-shared/daniel/squid/`
  - Ensure `index.html`, `.js`, `.wasm`, and data/assets are all uploaded together.

## Map Editor

```bash
python map_viewer.py
```

- Default level: `levels/stereo_madness.txt`
- Optional custom level path: `python map_viewer.py levels/level1.txt`
- Tile select: `1` empty, `2` solid, `3` spike, `4` start, `5` end
- Paint: left click
- Erase: right click
- Save: `Cmd+S` (macOS) or `Ctrl+S` (also auto-saves on quit if unsaved changes exist)
- Reload from disk: `R`
- Navigation: mouse wheel or `+/-` zoom, arrows/WASD pan, `F` fit, `Esc` quit

## Controls

- `Space` or mouse click: jump / continue
- `Esc`: quit

## Level Symbols

- `#` solid block
- `^` spike (death)
- `S` start
- `E` end

## Notes

- Current gameplay is intentionally minimal: cube + jump + spikes + solids.
- The included `levels/stereo_madness.txt` is a Stereo Madness-inspired layout built for this MVP ruleset.
