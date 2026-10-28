# License status

**Status: PolyForm Noncommercial 1.0.0, confirmed by the repository owner on
2026-10-27.**

The original project code in this repository (the game host, the ROM
validation helper, the packaging scripts and the documentation) is licensed
under the **PolyForm Noncommercial License 1.0.0** (see `LICENSE`).

Required Notice: Copyright (c) 2026 The Samurai Shodown Recompilation authors.

What this license does **not** cover
------------------------------------
* `neogeorecomp/` is the upstream toolkit by sp00nznet, MIT licensed. Its
  `LICENSE`, `NOTICE` and `LICENSES/` directory are preserved. Do not
  relicense those files under PolyForm. This copy is upstream v0.2.0
  (commit `af96b2b`) plus the generic fixes listed in
  `docs/runtime-changes.md`.
* Musashi (MIT), superzazu/z80 (MIT) and ymfm (BSD-3-Clause) are vendored
  under `neogeorecomp/ext/`; their notices are preserved.
* SDL2 is zlib licensed; the Windows DLL and the AppImage bundle it under
  that license.
* The game ROMs, the Neo Geo BIOS, and anything generated from them
  (recompiled C, entry lists, screenshots of gameplay) are **not** part of
  this project's licensed source and are not distributed. Users supply
  their own legally obtained dumps.
* `src/game.c` is the ROM layout for a specific commercial game. It contains
  no SNK code or data, but the game it describes is SNK's copyrighted work.

PolyForm Noncommercial is not a free/open-source license and does not permit
commercial redistribution. Do not assume otherwise. If you need commercial
terms, contact the project owner.

See `THIRD_PARTY_NOTICES.md` for the complete attribution list.
