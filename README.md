# Doomscroll - Anti Distraction

App that detects when you get distracted (looking down or off-screen or holding a phone) and plays a meme. Regain focus? The video stops.

## How it works
- **MediaPipe Face Landmarker** & **Object Detector** for distraction and phone detection
- After `1.5s` of distraction or phone detection → `video.mp4` in `MEME ALERT` window
- Focus regained → immediate stop

## Usage (macOS App)
Download `Doomscroll-macos-arm64.zip` (Apple Silicon M1/M2/M3/M4) or `Doomscroll-macos-x86_64.zip` (Intel) from the GitHub Actions artifacts or Releases.

1. Unzip `Doomscroll.app` and move it to `/Applications`.
2. **First launch (Gatekeeper workaround):** Since the app is self-compiled, macOS may warn that it cannot be opened. Right-click (or Ctrl+click) `Doomscroll.app`, select **Open**, and confirm. Alternatively, run:
   ```bash
   xattr -cr /Applications/Doomscroll.app
   ```
3. Grant camera access when prompted.

## Development & Local Build
```bash
pip install -r requirements.txt
./build.sh
# output: dist/Doomscroll.app
```
