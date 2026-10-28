# Samurai Shodown v0.1.0 - native recompilation

First public build of the Samurai Shodown static recompilation on NeoGeoRecomp
v0.2.0.

## Downloads

* `Samurai-Shodown-Windows-x64.zip` - Windows 10/11 x64, SDL2 and VC runtime
  included.
* `Samurai Shodown-SteamDeck-x86_64.AppImage` - Linux x86_64 / Steam Deck.
* `SHA256SUMS.txt` - hashes for both packages.

No game ROMs or BIOS files are included. Unzip your own legally obtained MAME
`samsho` and `neogeo` sets into a `roms` folder next to the executable or
AppImage, or pass `--rom-path`.

## Verified

* ROM layout and hashes match MAME `ROM_START( samsho )`; 12 game files and 4
  required BIOS files pass size/CRC32/SHA1 validation.
* 16,019 recompiled entry points after one profile pass.
* `--verify`: 989,214 blocks, 0 mismatches.
* 19,000-frame soak: 327,044,516 native instructions, 100.000% native, 0
  interpreted, 0 uncovered.
* Native and interpreter frames are byte-identical at character select.
* Audio: 202.75 s capture, 55,555 Hz stereo, peak 24,409, no clipping; the
  silent windows are the game's own HOW TO PLAY/round transitions and match
  the interpreter.
* Windows and the Linux AppImage both boot through the real MVS BIOS, render
  attract mode and play a full match.

## Generic toolkit fixes in this build

* C-ROM tile array padded to the sprite address mask (10/24/40 MB sets).
* Z80 banked windows always read the cart M1.
* YM2610 timer status latched independently of IRQ enable, INT gated.
* Audio ring cleared on board reset.
* SDL output path converts the YM2610 rate, cushions 60 ms and trims only on
  overrun.
* Fullscreen is 4:3 pillarboxed on 16:10 panels.

## Not tested

Physical Steam Deck (Gaming Mode, Steam Input, LCD/OLED), physical gamepads,
two-player versus, service menu, memory cards, and listening on a real audio
device.
