# Doomscroll - Anti Distraction

App that detects when you get distracted (looking down or off-screen) and plays a meme. Regain focus? The video stops.

## How it works
- **MediaPipe Face Landmarker** for face tracking
- Distracted gaze if: `nose_ratio > 0.68` / `chin.y > 0.85` (looking down) or `h_off > 0.18` (sideways) or face absent
- After `1.5s` of distraction → `video.mp4` in `MEME ALERT` window
- Focus regained → immediate stop

## Usage
```bash
pip install -r requirements.txt
python main.py
# q or X to close
```

## Build executable (1 command)
```bash
./build.sh
# output: dist/Doomscroll / dist/Doomscroll.app (on macOS)
```
Requires building **on Mac** for macOS (`brew install sdl2` handled by the script).

## Repo
```bash
git clone <url> && cd doomscroll
```

## Files
- `main.py` - app
- `video.mp4` - meme (replaceable)
- `doomscroll.spec` - PyInstaller config
- `face_landmarker.task` - auto-downloaded if missing
