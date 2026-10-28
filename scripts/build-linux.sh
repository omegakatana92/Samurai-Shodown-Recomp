#!/usr/bin/env bash
# Configure and build the Linux x86_64 player.
#
# Usage: ./scripts/build-linux.sh [ROM_DIR]
# Default ROM_DIR=$ROOT/roms.  Output: build-linux/samsho.
set -euo pipefail

ROOT="$(cd "$(dirname "$0")/.." && pwd)"
ROMS="${1:-$ROOT/roms}"
BUILD="$ROOT/build-linux"

cmake -S "$ROOT" -B "$BUILD" -DCMAKE_BUILD_TYPE=Release "-DSAMSHO_ROM_DIR=$ROMS"
cmake --build "$BUILD" --parallel "$(nproc)"
echo "built $BUILD/samsho"
