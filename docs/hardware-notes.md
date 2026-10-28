# Hardware notes - Samurai Shodown

Samurai Shodown is a plain PROGBK1 MVS/AES cart. Bringing it up needed no
title-specific hardware work beyond the generic toolkit model.

## Program layout

```
$000000-$0FFFFF   fixed bank      045-p1.p1
$200000-$2FFFFF   banked window   045-pg2.sp2 (one 1 MB bank)
$C00000-$C1FFFF   system ROM
```

The bank selector is the standard write to `$2FFFF0-$2FFFFF`. `ng_bank_base`
is the offset inside the 2 MB program image, so selector 0 maps to
`prom + 0x100000`, the same as hardware. There is no NEO-SMA, CMC42/CMC50,
protection read or S ROM banking.

## Fixed layer

The S ROM is 128 KB, so `ng_game_t.fix_bank_type` stays at
`NG_FIX_BANK_NONE`. The fix layer draws menus, HUD, INSERT COIN and the
HOW TO PLAY text from the game's own S ROM after the BIOS hands over.

## Sprites

The C ROMs are 10 MB: two 4 MB odd/even pairs and one 2 MB pair. Ten
megabytes is not a power of two, so the renderer's tile-code mask reaches
16 MB worth of codes. The decoder pads the decoded tile array to that mask
with transparent tiles; without the padding, a sprite code above the 81,920
real tiles read past the buffer and crashed. This is the first title in this
workspace to exercise that path at 10 MB.

## Sound

The M1 is a plain 128 KB Z80 driver. The runtime models the four bank windows
at `$8000/$C000/$E000/$F000`, NMI/reply latches and the YM2610's FM, SSG and
ADPCM-A/B. The generic fixes present in the vendored `audio.c` are:

* bank-window offsets masked with `(size - 1) & 0x3FFFF`;
* banked windows always read the cart M1, even while the main `$0000-$7FFF`
  bank is the BIOS SM1;
* YM2610 status flags set on timer expiry independently of the IRQ enable
  bits, with the Z80 INT line gated by those bits;
* `audio_take_samples()` syncs the Z80 once per frame so a 68000 that stops
  polling the latches cannot starve the sequencer;
* a board reset clears the sample ring.

## Timing

The measured build runs at the MVS refresh rate (59.1856 Hz). The 19,000-frame
soak completes with 0 interpreted instructions after one profile pass.

## Untested hardware

Physical Steam Deck, Steam Input, a physical gamepad, the test/service menu,
two-player versus and the memory-card interface were not exercised.
