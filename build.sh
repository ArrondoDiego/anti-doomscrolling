#!/bin/bash
set -e
pip install -q pyinstaller 2>/dev/null || pip3 install -q pyinstaller
if [[ "$(uname)" == "Darwin" ]]; then brew list sdl2 >/dev/null 2>&1 || brew install sdl2 sdl2_mixer >/dev/null 2>&1 || true; fi
pyinstaller --clean --noconfirm doomscroll.spec
echo "OK -> dist/Doomscroll(.app)"
