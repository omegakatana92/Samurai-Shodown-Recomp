# Testing and measured results

All numbers below are from the Windows Release build unless stated otherwise.
Commands are shown for PowerShell; on Linux replace `Samsho.exe` with
`build-linux/samsho` and use forward slashes.

## Environment

| Item | Version |
|---|---|
| Windows | Windows 11 x64 |
| Compiler | MSVC 19.51 (Visual Studio 18 2026) |
| CMake | 4.3.3 |
| SDL2 | 2.32.10 |
| Linux build host | Ubuntu 22.04.5 under WSL2 |
| Linux compiler | gcc 11.4.0 |
| Reference emulator (audio/visual check only) | MAME 0.242 |

## 1. ROM validation

The archive is the MAME `samsho` MVS set. Every file's CRC-32 and SHA-1 was
computed from the zip and compared with `ROM_START( samsho )` in MAME's
`src/mame/snk/neogeo.cpp`; all 12 game files match, as do the four required
`neogeo` files. The `NEO-GEO` signature is at `$100` of the byte-swapped fixed
bank.

No decryption or patching is performed. The build reads the user's files
directly from `SAMSHO_ROM_DIR`.

## 2. Interpreted boot

```
"Samsho.exe" --headless --interp --rom-path roms --frames 1200 ^
    --screenshot 600:shots/ip-600.png --screenshot 1200:shots/ip-1200.png
```

Result: real BIOS eyecatcher at frame 600 and the start of the game intro at
frame 1200. This validates the board model independently of the recompiler.

## 3. Native build and boot

```
cmake -S . -B build-windows -G "Visual Studio 18 2026" -A x64 ^
      -DSDL2_DIR=...\deps\sdl2\SDL2-2.32.10\cmake ^
      -DSAMSHO_ROM_DIR=C:/.../roms
cmake --build build-windows --config Release --parallel 8
```

Recompiler output (static discovery only):

```
[m68krecomp] pointer scan: 9991 seeds
[m68krecomp] samsho: 241589 instructions emitted across routines
[m68krecomp] 10820 routines, 15953 dispatch entries
```

Attract and title, 5,000 frames:

```
[exec] native blocks 2888495, native instructions 86482255,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

Screens checked: NEO-GEO eyecatcher (600), intro text (1200, 1800), title
(2500), attract fight (3500), transition (4999).

## 4. Coin, menus and a match

```
"Samsho.exe" --headless --rom-path roms --frames 4000 ^
    --input tests/coin_start.txt ^
    --screenshot 1100:shots/c1100.png --screenshot 1500:shots/c1500.png ^
    --screenshot 2200:shots/c2200.png --screenshot 2800:shots/c2800.png ^
    --screenshot 3999:shots/c3999.png
```

Frames checked: HOW TO PLAY (1100), character select (1500), BEGIN and VS
screen (2200), match with health bars and timer (2800-3999).

## 5. Correctness: `--verify`

```
"Samsho.exe" --headless --verify --rom-path roms --frames 2000 ^
    --input tests/coin_start.txt
[verify] 989214 blocks checked, 0 mismatches
[exec] native blocks 989214, native instructions 35752234,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

The Linux/AppImage build checked 678,767 blocks over 1,500 frames with 0
mismatches.

## 6. Coverage and the profile pass

Before profiling:

```
[attract, 6000 frames] interpreted 0, 0 uncovered
[play_long, 19000 frames] interpreted 2494 (100.00% native), 59 uncovered
```

Profile pass:

```
cmake --build build-windows --config Release --target profile
[exec] 59 new entry points; entries.txt now lists 59
```

After profiling:

```
[play_long, 19000 frames]
[exec] native blocks 12596089, native instructions 327044516,
       interpreted instructions 0 (100.00% native), 0 uncovered entry points
```

Final table: 16,019 dispatch entries, 241,997 instructions emitted.

## 7. Native vs interpreter screenshot

| Frame | Screen | Result |
|---|---|---|
| 1500 | CHARACTER SELECT | byte-identical (SHA-256 `83F5A597F838C10BBFE8BC967E664B0C62802ADA1E5D0E0763D80E8E8E0D7958`) |

## 8. Audio

```
"Samsho.exe" --headless --rom-path roms --frames 12000 ^
    --input tests/play_long.txt --wav shots/audio-final.wav
python tests/analyze_wav.py shots/audio-final.wav
```

Result: 202.75 s, 55,555 Hz stereo, peak 24,409, RMS 3,175, 0 clipped
samples. Silent runs after boot: 11 s, 20-21 s, 144-147 s and 161 s. The
interpreter capture has the same windows. The 144-147 s window is the game's
own HOW TO PLAY demonstration screen (screenshot checked), not a driver
stall.

`tests/check_audio.py` uses a 5 s threshold so the tutorial window does not
produce a false failure; the report records the windows rather than claiming
a perfectly continuous capture.

A 25-second MAME 0.242 attract capture was used as a reference: both start the
BIOS music at 4 s and show the same sequence of levels. MAME's default route
is quieter, so only the envelope and timing were compared, not absolute gain.

## 9. Windows window

```
"Samsho.exe" --rom-path roms --frames 120 --scale 2
"Samsho.exe" --rom-path roms --fullscreen --frames 120
```

Both launched the SDL2 window, rendered frames and exited 0. With
`NG_AUDIO_TRACE=1` the real device negotiated 55,555 Hz, 2 channels, 32-bit
and ran with 0 queue stalls over 240 frames.

## 10. Linux and AppImage

The AppImage was built with gcc 11.4 on Ubuntu 22.04 under WSL2. It was run
headless (3,000 frames, 100.000% native), with `--verify` (1,500 frames,
0 mismatches, 100.000% native) and fullscreen under Xvfb at 1280x800:

```
[window] output 1280x800 dst 107,0 1066x800 fullscreen=1
```

That is a 4:3 pillarboxed image, not a stretch to 16:10. The AppImage's
contents were listed to confirm that no ROM or BIOS file is bundled; the
bundled `libSDL2-2.0.so.0` resolves from `usr/lib` when `AppRun` sets
`LD_LIBRARY_PATH`. glibc, libstdc++ and libgcc are not bundled. Physical
Steam Deck LCD/OLED, Steam Input and Gaming Mode are **not tested**.
