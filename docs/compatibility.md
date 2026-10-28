# Compatibility and verification report

Game: **Samurai Shodown** (SNK, MVS/AES), MAME set `samsho`, NGH-045.

Toolkit: **NeoGeoRecomp v0.2.0**, commit
`af96b2b4b39b42b392b17bcaa6a74a5f27088202`, plus the generic fixes in
`docs/runtime-changes.md` (watchdog, bank guard, 4:3 fullscreen, M1 bank and
timer fixes, C-ROM padding).

Everything below was run in this workspace. Anything not run is marked
**untested**, not assumed.

## Hardware profile

| Area | Result |
|---|---|
| 68000 program | 2 MB P ROM: 1 MB fixed + one 1 MB bank |
| Encryption / protection | none (normal PROGBK1 MVS/AES cart) |
| C ROMs | 10 MB, three odd/even pairs (2+2 MB, 2+2 MB, 1+1 MB) |
| S ROM | 128 KB fixed layer |
| M ROM | 128 KB Z80 driver |
| V ROMs | 4 MB ADPCM-A/B |
| BIOS | real `sp-s2.sp1` (MVS Asia/Europe v2), no BIOS HLE |
| Banking | standard `$2FFFF0-$2FFFFF` 1 MB window |

## ROM validation - passed

All 12 game files and the 4 required system-ROM files match MAME
`ROM_START( samsho )` by size, CRC32 and SHA1
(`python scripts/validate-roms.py roms`). Table in `docs/rom-layout.md`.
The word-swapped fixed bank carries `NEO-GEO` at `$100`.

## Boot and hardware

| Test | Environment / run | Result |
|---|---|---|
| Interpreter boot | Windows x64, headless | **Passed**; BIOS self-test, eyecatcher, intro, attract |
| Native boot, 5,000 frames | Windows x64, headless | **Passed**; intro cards, title, attract match |
| Native frames vs interpreter | frame 1500 | **Byte-identical** PNG (SHA-256 `83F5A597...`) |
| Window launch | Windows x64, SDL2 2.32.10 | **Passed**, exit 0 |
| Fullscreen launch | Windows x64, `--fullscreen` | **Passed**, exit 0 |
| Window audio device | Windows x64, `NG_AUDIO_TRACE=1` | **Opened**: 55,555 Hz, 2 ch, 32-bit, 0 stalls over 240 frames |
| Audio | 12,000-frame `--wav`, native | **202.75 s**, 55,555 Hz stereo, peak 24,409, RMS 3,175, 0 clipped |
| Audio, interpreter | same script, `--interp` | same duration and identical silent windows |

The native and interpreter captures share the silent windows at 11 s,
20-21 s, 144-147 s and 161 s. The 144-147 s gap is the game's own HOW TO PLAY
demonstration screen (confirmed by a screenshot), not a stalled driver.

## Recompilation and correctness

| Metric | Result |
|---|---|
| Static discovery | 241,589 instructions, 10,820 routines, 15,953 entries |
| Profile pass (6,000 + 19,000 frames) | 59 runtime-only entry points added |
| Final table | **16,019** entries, 241,997 instructions emitted |
| `--verify`, 2,000 frames | **989,214 blocks, 0 mismatches** |
| AppImage `--verify`, 1,500 frames | **678,767 blocks, 0 mismatches** |
| Native instructions, 19,000-frame soak | **327,044,516** |
| Interpreted instructions after profiling | **0** |
| Uncovered entry points after profiling | **0** |
| Native coverage | **100.000%** of the executed instructions in these sessions |

The 100% figure is measured over the scripted sessions (boot, intro, attract,
HOW TO PLAY, character select, VS screen, rounds and continue). It is not a
proof that every reachable path in the 2 MB program is native.

## Gameplay

| Item | Result |
|---|---|
| BIOS warning / eyecatcher | Yes (frame 600) |
| Intro / attract | Yes ("A samurai fears not death", title, demo fight) |
| Coin insertion | Yes (credit counter increments) |
| Start | Yes |
| HOW TO PLAY | Yes (frame 1100) |
| Character select | Yes (full roster, Haohmaru selected, frame 1500) |
| VS / stage intro | Yes (BEGIN, frame 2200) |
| Match: movement, A/B/C/D, hits, health bars, timer | Yes (frames 2200-3999) |
| ROUND 2 / continue transitions | Observed during the 19,000-frame soak |
| Two-player versus | **Untested** |
| Test / service menu | **Untested** |
| Memory card | Not implemented by the toolkit |
| Audio device playback | **Verified device opens**; not listened to by a human |
| Physical gamepad / Steam Input | **Untested** (toolkit mapping only) |

Screenshots collected during these runs are not shipped because they contain
SNK artwork.

## Windows deliverable

| Item | Result |
|---|---|
| Toolchain | MSVC 19.51 (Visual Studio 18 2026), CMake 4.3.3, Release x64 |
| Build | **built**; 16 generated C files |
| Package | `dist/windows/Samurai Shodown-Windows-x64/` - exe + SDL2.dll + VC runtime + docs + licences |
| Headless smoke test | **Passed** (1,200 frames) |
| Full soak, native | **Passed** (19,000 frames, 100.000% native) |
| `--verify` | **Passed**, 989,214 blocks, 0 mismatches |
| ROMs in package | none |

## Steam Deck AppImage

| Item | Result |
|---|---|
| Build host | Windows 11 + WSL2, Ubuntu 22.04 x86_64 |
| Output | `dist/steamdeck/Samurai Shodown-SteamDeck-x86_64.AppImage` (6.9 MB) |
| Headless run | **Passed**, 3,000 frames, 100.000% native, 0 interpreted |
| `--verify` on AppImage | **Passed**, 1,500 frames, 0 mismatches, 100.000% native |
| Windowed/fullscreen launch | **Passed** under Xvfb 1280x800 |
| Aspect at 1280x800 | renderer output 1280x800, destination **107,0 1066x800**, 4:3 pillarboxed, not stretched (`NG_WINDOW_TRACE=1`) |
| `ldd` | no missing libraries; glibc/libstdc++/libgcc not bundled; SDL2 bundled in `usr/lib` |
| ROMs inside AppImage | none |
| Steam Deck hardware | **Not available**: Gaming Mode, Steam Input, LCD/OLED panels **untested** |

## Audio verification against MAME

A 25-second MAME 0.242 attract capture and the corresponding native capture
have the same per-second level envelope once the BIOS boot offset is removed
(Samurai Shodown: music starts at 4 s in both; peak 14,396 in MAME at its
default route, 24,409 in the recompilation). The comparison is a timeline and
level check, not a sample-by-sample match: MAME applies its own output gain.

## Known limitations

* Native coverage is 100% for the scripted sessions only.
* No Steam Deck hardware, no physical gamepad, no keyboard-by-hand test, no
  two-player or service-menu test, no listening test on a real audio device.
* The toolkit's controller layout is fixed (no remapping).
* PolyForm Noncommercial 1.0.0 does not permit commercial distribution of the
  original code. The variant was confirmed by the owner on 2026-10-27.
* No ROMs or BIOS files are bundled; a legally obtained `neogeo` set is
  required.
* The AES variant (`samshoh`) and bootleg/hack sets are not configured.
