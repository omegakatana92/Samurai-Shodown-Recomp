#!/usr/bin/env bash
# Build the Linux x86_64 player and package it as a Steam Deck AppImage.
#
# Prerequisites: gcc, g++, cmake 3.21+, make, libsdl2-dev, wget.
# The user's ROMs are never bundled: the AppImage contains only the recompiled
# player and its runtime libraries.
#
# Usage: ./packaging/appimage/build-appimage.sh [ROM_DIR]
# Default ROM_DIR=$ROOT/roms, output
# dist/steamdeck/Samsho-SteamDeck-x86_64.AppImage
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/../.." && pwd)"
ROMS="${1:-$ROOT/roms}"
BUILD="$ROOT/build-linux"
APPDIR="$BUILD/AppDir"
OUT="$ROOT/dist/steamdeck/Samsho-SteamDeck-x86_64.AppImage"

echo "== configure/build (Release) =="
cmake -S "$ROOT" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release "-DSAMSHO_ROM_DIR=$ROMS"
cmake --build "$BUILD" --parallel "$(nproc)"

echo "== assemble AppDir =="
rm -rf "$APPDIR"
mkdir -p "$APPDIR/usr/bin" "$APPDIR/usr/lib" \
         "$APPDIR/usr/share/applications" \
         "$APPDIR/usr/share/icons/hicolor/256x256/apps" \
         "$APPDIR/usr/share/doc/samsho"
cp "$BUILD/samsho" "$APPDIR/usr/bin/samsho"
strip --strip-unneeded "$APPDIR/usr/bin/samsho" 2>/dev/null || true

# Bundle the SDL2 the build linked against; SteamOS's system copy may differ.
SDL=$(ldd "$BUILD/samsho" | awk '/libSDL2-2\.0\.so\.0/{print $3; exit}')
if [ -n "$SDL" ]; then cp "$SDL" "$APPDIR/usr/lib/"; fi

cp "$ROOT/packaging/appimage/samsho.png" "$APPDIR/samsho.png"
cp "$ROOT/packaging/appimage/samsho.png" "$APPDIR/usr/share/icons/hicolor/256x256/apps/samsho.png"
cp "$ROOT/packaging/appimage/samsho.desktop" "$APPDIR/samsho.desktop"
cp "$ROOT/packaging/appimage/samsho.desktop" "$APPDIR/usr/share/applications/samsho.desktop"
cp "$ROOT/packaging/appimage/README.txt" "$APPDIR/usr/share/doc/samsho/README.txt"
cp "$ROOT/LICENSE" "$APPDIR/usr/share/doc/samsho/LICENSE.txt"
cp "$ROOT/LICENSE-STATUS.md" "$APPDIR/usr/share/doc/samsho/LICENSE-STATUS.txt" 2>/dev/null || true
cp "$ROOT/THIRD_PARTY_NOTICES.md" "$APPDIR/usr/share/doc/samsho/THIRD_PARTY_NOTICES.txt"
mkdir -p "$APPDIR/usr/share/doc/samsho/LICENSES"
cp "$ROOT/neogeorecomp/LICENSE" "$APPDIR/usr/share/doc/samsho/LICENSES/neogeorecomp.txt"
cp "$ROOT/neogeorecomp/NOTICE" "$APPDIR/usr/share/doc/samsho/LICENSES/neogeorecomp-NOTICE.txt"
cp "$ROOT/neogeorecomp/LICENSES/"*.txt "$APPDIR/usr/share/doc/samsho/LICENSES/"
cp "$ROOT/packaging/windows/SDL2.txt" "$APPDIR/usr/share/doc/samsho/LICENSES/SDL2.txt"

cat > "$APPDIR/AppRun" <<'EOF'
#!/bin/sh
HERE=$(dirname "$(readlink -f "$0")")
export LD_LIBRARY_PATH="$HERE/usr/lib${LD_LIBRARY_PATH:+:$LD_LIBRARY_PATH}"

# An explicit --rom-path always wins.
has_rom=0
for a in "$@"; do
    [ "$a" = "--rom-path" ] && has_rom=1
done

if [ "$has_rom" = 0 ]; then
    cand=""
    if [ -n "${SAMSHO_ROM_DIR:-}" ]; then
        cand="$SAMSHO_ROM_DIR"
    elif [ -n "${APPIMAGE:-}" ]; then
        for d in "$(dirname "$APPIMAGE")/roms" \
                 "$(dirname "$APPIMAGE")/roms/samsho" \
                 "$HOME/.local/share/samsho/roms" \
                 "$HOME/Emulation/roms/samsho" \
                 "$HOME/roms/samsho" "$HOME/roms"; do
            if [ -d "$d" ]; then cand="$d"; break; fi
        done
    fi
    if [ -n "$cand" ]; then
        set -- --rom-path "$cand" "$@"
    fi
fi

# Steam Deck / Gaming Mode wants a fullscreen game. Keep --headless and an
# explicit --scale or --fullscreen from being overridden.
add_fs=1
for a in "$@"; do
    case "$a" in --headless|--fullscreen|--scale) add_fs=0;; esac
done
[ "$add_fs" = 1 ] && set -- --fullscreen "$@"

exec "$HERE/usr/bin/samsho" "$@"
EOF
chmod +x "$APPDIR/AppRun"

echo "== appimagetool =="
mkdir -p "$ROOT/dist/steamdeck"
TOOL="${APPIMAGETOOL:-$HOME/appimagetool-x86_64.AppImage}"
if [ ! -x "$TOOL" ]; then
    TOOL="$BUILD/appimagetool.AppImage"
    wget -q -O "$TOOL" \
      https://github.com/AppImage/appimagetool/releases/download/continuous/appimagetool-x86_64.AppImage
    chmod +x "$TOOL"
fi
ARCH=x86_64 "$TOOL" --appimage-extract-and-run --no-appstream "$APPDIR" "$OUT"
chmod +x "$OUT"

# Release-folder companions: README and the license set.
DIST="$ROOT/dist/steamdeck"
mkdir -p "$DIST/LICENSES"
cp "$ROOT/packaging/appimage/README.txt" "$DIST/README.txt"
cp "$ROOT/LICENSE" "$DIST/LICENSES/LICENSE.txt"
cp "$ROOT/LICENSE-STATUS.md" "$DIST/LICENSES/LICENSE-STATUS.txt" 2>/dev/null || true
cp "$ROOT/THIRD_PARTY_NOTICES.md" "$DIST/LICENSES/THIRD_PARTY_NOTICES.txt"
cp "$ROOT/packaging/windows/SDL2.txt" "$DIST/LICENSES/SDL2.txt"
cp "$ROOT/neogeorecomp/LICENSE" "$DIST/LICENSES/neogeorecomp.txt"
cp "$ROOT/neogeorecomp/NOTICE" "$DIST/LICENSES/neogeorecomp-NOTICE.txt"
cp "$ROOT/neogeorecomp/LICENSES/"*.txt "$DIST/LICENSES/"

echo "wrote $OUT"
