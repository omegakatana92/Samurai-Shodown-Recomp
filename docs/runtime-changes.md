# Generic changes in the vendored toolkit

`neogeorecomp/` is upstream **v0.2.0**, commit
`af96b2b4b39b42b392b17bcaa6a74a5f27088202` (`toolkit.ref`), plus the generic
changes below. None contains game addresses or ROM data; each is a hardware
model or host fix that any title can use. They are released under the
toolkit's MIT license.

## MVS watchdog

`src/neogeo.c`, `src/io.c`, `src/ng_internal.h`. The board resets after
3,244,030 master clocks without a write to `$300001`, preserving work and
backup RAM. Samurai Shodown does not depend on it, but late carts do.

## Bank-aware native dispatch

`src/exec.c`, `src/bus.c`, `include/neogeorecomp/neogeo.h`. A native routine is
tied to the bytes of one bank, so the dispatcher interprets code in the
`$200000` window when `ng_bank_base != 0`. This prevents running bank 0's
translation against bank 1's bytes.

## Fixed-layer banking selectors

`NG_FIX_BANK_GAROU` and `NG_FIX_BANK_KOF2000` cover the two larger-S-ROM
layouts. Samurai Shodown uses the plain 128 KB `NG_FIX_BANK_NONE` path.

## C-ROM tile array padded to the address mask (`src/video.c`)

The renderer masks sprite tile codes to the next power of two, because the
address lines above the fitted ROMs are not connected. A 10 MB set
(Samurai Shodown), 24 MB set (Waku Waku 7) or 40 MB set (KOF '97) therefore
addresses more tiles than the ROM contains. The decoder now allocates the
padded array with `calloc`, leaves the unused tail transparent, and never
reads past it. Before this fix a sprite code above the ROM's tile count could
read beyond the allocated buffer and crash.

## Z80 bank windows always use the cart M1 (`src/audio.c`)

MAME's `init_audio()` configures the four `$8000/$C000/$E000/$F000` windows
from the cartridge audio region. `set_use_cart_audio()` switches only the main
`$0000-$7FFF` bank between the BIOS SM1 and the cart M1; the four windows keep
pointing at the cart M1. Reading the BIOS SM1 from those windows gave the BIOS
driver the wrong banked data, which caused missing or wrong music. The runtime
now always reads the cart M1 in the banked windows.

## M1 bank mask from the M1 file size (`src/audio.c`)

MAME's `init_audio()` builds each Z80 bank entry as
`0x10000 + ((bank << (11 + window)) & address_mask)` in the audio region, and
`ROM_RELOAD` places the first byte of the M1 file at region offset `0x10000`.
The file offset is therefore the masked value alone:

```c
off = (bank & ((size - 1) & 0x3FFFF)) + (a & window_mask);
```

The old formula added a second `0x10000` and/or used
`(size - 0x10000 - 1)`, which rotated or truncated banks that drivers use for
music data. The generic fix is present here.

## YM2610 status flags and IRQ masking (`src/audio.c`)

The YM2610 latches timer A/B expiry in its status register regardless of
whether the timer's IRQ is enabled; the control register's enable bits gate
the IRQ line, not the status flag. The runtime now sets the status flags
unconditionally, and drives the Z80's INT line only when the matching enable
bit is set. This matches MAME and keeps drivers that poll status without
enabling interrupts in step.

## Frame-boundary Z80 sync (`src/audio.c`)

`audio_take_samples()` calls `audio_sync()` before generating samples, so the
Z80 and YM2610 timers keep running even when the 68000 stops polling the sound
latches. This prevents a pull-based audio path from starving the music driver.
A board reset also clears the sample ring, so nothing from the previous driver
is played after a reset.

## Fullscreen with 4:3 pillarboxing

`src/window_sdl.c`, `src/neogeo.c`, `src/platform.c`. `--fullscreen` creates a
desktop-fullscreen window and scales the 320x224 image into a 4:3 rectangle
centred in the output with black bars. It is never stretched to 16:10. F11
toggles the mode. This is what the Steam Deck AppRun passes by default.

## SDL output path (`src/window_sdl.c`)

The device is opened with frequency/format/channel changes allowed and fed
through `SDL_AudioStream`, instead of demanding exactly 55,555 Hz. Playback
starts with a 60 ms cushion; a queue overrun trims only the oldest excess down
to 80 ms rather than clearing all queued audio. The renderer falls back to
SDL's software renderer when no accelerated one is available. This removes
silent devices, clicks and music cut-outs on jittery schedulers.

## Native instruction accounting

`src/exec.c` reports native instructions and a coverage percentage beside the
interpreted count, so coverage is measured rather than estimated.
