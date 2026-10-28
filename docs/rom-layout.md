# ROM layout - MAME set `samsho` (NGH-045)

Validated against MAME's `src/mame/snk/neogeo.cpp`, `ROM_START( samsho )`
(the MVS version). All 12 game files and the 4 required system-ROM files were
checked by size, CRC32 and SHA1 with `python scripts/validate-roms.py roms`;
every one matched.

## Game set

| File | Size | CRC32 | MAME load | Role |
|---|---:|---|---|---|
| `045-p1.p1` | 1,048,576 | `dfe51bf0` | `ROM_LOAD16_WORD_SWAP` @ 0x000000 | 68000 fixed bank |
| `045-pg2.sp2` | 1,048,576 | `46745b94` | `ROM_LOAD16_WORD_SWAP` @ 0x100000 | banked program |
| `045-s1.s1` | 131,072 | `9142a4d3` | `NEO_SFIX_128K` | fixed layer |
| `045-m1.m1` | 131,072 | `95170640` | `NEO_BIOS_AUDIO_128K` | Z80 sound driver |
| `045-v1.v1` | 2,097,152 | `37f78a9b` | `ROM_LOAD` @ 0x000000 | ADPCM-A |
| `045-v2.v2` | 2,097,152 | `568b20cf` | `ROM_LOAD` @ 0x200000 | ADPCM-A |
| `045-c1.c1` | 2,097,152 | `2e5873a4` | `ROM_LOAD16_BYTE` @ 0x000000 | sprite planes 0,1 |
| `045-c2.c2` | 2,097,152 | `04febb10` | `ROM_LOAD16_BYTE` @ 0x000001 | sprite planes 2,3 |
| `045-c3.c3` | 2,097,152 | `f3dabd1e` | `ROM_LOAD16_BYTE` @ 0x400000 | sprite planes 0,1 |
| `045-c4.c4` | 2,097,152 | `935c62f0` | `ROM_LOAD16_BYTE` @ 0x400001 | sprite planes 2,3 |
| `045-c51.c5` | 1,048,576 | `81932894` | `ROM_LOAD16_BYTE` @ 0x800000 | sprite planes 0,1 |
| `045-c61.c6` | 1,048,576 | `be30612e` | `ROM_LOAD16_BYTE` @ 0x800001 | sprite planes 2,3 |

Totals: 2 MB program (1 MB fixed + 1 MB banked), 10 MB sprite data,
4 MB ADPCM-A, 128 KB fixed layer, 128 KB Z80 program.

## System set (`neogeo.zip`)

| File | Size | CRC32 | Role |
|---|---:|---|---|
| `sp-s2.sp1` | 131,072 | `9036d879` | MVS Asia/Europe v2 BIOS (default `--bios`) |
| `sfix.sfix` | 131,072 | `c2ea0cfd` | BIOS fixed-layer graphics |
| `sm1.sm1` | 131,072 | `94416d67` | BIOS Z80 sound driver |
| `000-lo.lo` | 131,072 | `5a86cff2` | sprite shrink table |

The supplied `samsho.zip` also contains a copy of the `neogeo` sets; the
project only uses the four files above.

## How the dump maps into `ng_game_t`

* **P ROM.** Both files are stored 16-bit word-swapped, so `swap = 1`. After
  the swap the fixed bank carries `NEO-GEO` at `$100`; the cartridge header
  entry points at `$122`, `$128`, `$12E` and `$134` are what the BIOS calls.
  `prom_size = 0x200000`: the first 1 MB is the fixed bank at
  `$000000-$0FFFFF`, the remaining 1 MB is the single bank behind the
  `$200000` window, selected through `$2FFFF0-$2FFFFF`.
* **C ROMs.** MAME loads them as three `ROM_LOAD16_BYTE` pairs: 4 MB at
  `0x000000`, 4 MB at `0x400000` and 2 MB at `0x800000`. The runtime's
  `crom_pairs` interleaves each pair byte-for-byte into the same 10 MB layout,
  which the per-scanline sprite renderer indexes directly.
* **V ROMs.** Concatenated in MAME order into one 4 MB ADPCM-A space.
* **S ROM / M1.** Single 128 KB files, copied as-is.

## Hardware profile

| Item | Result |
|---|---|
| Board | standard MVS/AES PROGBK1 cart |
| Encryption | none |
| Protection / daughterboard | none (no NEO-SMA, CMC42/CMC50) |
| Banking | one 1 MB bank at `$200000`; selector byte at `$2FFFFF` |
| Raster / IRQ | standard LSPC, IRQ1 (VBlank) and IRQ2 (timer) |
| Sound | standard M1 driver + YM2610 (SSG, FM, ADPCM-A/B) |

No MAME code is copied. The layout was read from the public driver as a
hardware reference.
