#!/bin/bash
set -e
pyinstaller --clean --noconfirm doomscroll.spec
echo "OK -> dist/Doomscroll.app"
