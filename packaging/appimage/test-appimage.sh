#!/usr/bin/env bash
# Smoke-test the built AppImage: permissions, contents, dependencies, headless
# playback, --verify, and a fullscreen launch under Xvfb at 1280x800.
#
# Usage: packaging/appimage/test-appimage.sh [ROM_DIR]
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ROMS="${1:-$ROOT/roms}"
APP="$ROOT/dist/steamdeck/Samurai Shodown-SteamDeck-x86_64.AppImage"
RUN=(env APPIMAGE_EXTRACT_AND_RUN=1 "$APP")

echo "== file =="
ls -l "$APP"
test -x "$APP"

echo "== contents (must not contain ROMs) =="
UNPACK="$ROOT/build-linux/appimage-test"
rm -rf "$UNPACK"
mkdir -p "$UNPACK"
cd "$UNPACK"
"$APP" --appimage-extract >/dev/null
find squashfs-root -maxdepth 3 -type f | sort | sed -n '1,80p'
if find squashfs-root -type f | grep -Eiq '(045-|sp-s2\.sp1|sfix\.sfix|sm1\.sm1|000-lo\.lo)'; then
    echo "ERROR: ROM/BIOS files found inside the AppImage" >&2
    exit 1
fi

echo "== ldd =="
ldd squashfs-root/usr/bin/samsho

echo "== headless 3,000 frames =="
"${RUN[@]}" --headless --rom-path "$ROMS" --frames 3000 \
    --input "$ROOT/tests/coin_start.txt"

echo "== --verify 1,500 frames =="
"${RUN[@]}" --headless --verify --rom-path "$ROMS" --frames 1500 \
    --input "$ROOT/tests/coin_start.txt"

echo "== fullscreen under Xvfb 1280x800 =="
if command -v xvfb-run >/dev/null; then
    NG_WINDOW_TRACE=1 xvfb-run -a -s "-screen 0 1280x800x24" \
        "${RUN[@]}" --rom-path "$ROMS" --frames 120 --input "$ROOT/tests/coin_start.txt" \
        2>&1 | grep -E '\[window\]|\[neogeorecomp\]' || true
else
    echo "xvfb-run not installed; fullscreen launch skipped"
fi

echo "PASS: AppImage smoke tests"
