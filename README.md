# Doomscroll - Anti Distrazione

App che rileva quando ti distrai (sguardo in basso o fuori schermo) e fa partire un meme. Torni concentrato? Il video si ferma.

## Come funziona
- **MediaPipe Face Landmarker** per tracking volto
- Sguardo distratto se: `nose_ratio > 0.68` / `chin.y > 0.85` (in basso) o `h_off > 0.18` (laterale) o volto assente
- Dopo `1.5s` di distrazione → `video.mp4` in finestra `MEME ALERT`
- Ritorno concentrato → stop immediato

## Uso
```bash
pip install -r requirements.txt
python main.py
# q o X per chiudere
```

## Build eseguibile (1 comando)
```bash
./build.sh
# output: dist/Doomscroll / dist/Doomscroll.app (su macOS)
```
Richiede build **su Mac** per macOS (`brew install sdl2` gestito dallo script).

## Repo
```bash
git clone <url> && cd doomscroll
```

## File
- `main.py` - app
- `video.mp4` - meme (sostituibile)
- `doomscroll.spec` - config PyInstaller
- `face_landmarker.task` - auto-scaricato se assente
