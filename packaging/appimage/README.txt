Samurai Shodown - native static recompilation (Steam Deck / Linux x86_64)
========================================================================

This AppImage contains the recompiled game and the SDL2 window/audio layer.
It does not contain game ROMs or the Neo Geo BIOS: supply your own legally
obtained dump.

Quick start
-----------
1. Put your MAME "samsho" set and "neogeo" set in a folder, unzipped:

     mkdir -p roms
     unzip samsho.zip -d roms
     unzip neogeo.zip -d roms

   The AppRun script finds a "roms" directory next to the AppImage, a folder
   named by SAMSHO_ROM_DIR, or the per-user folder
   $HOME/.local/share/samsho/roms.

2. Make the AppImage executable and run it:

     chmod +x "Samsho-SteamDeck-x86_64.AppImage"
     "./Samsho-SteamDeck-x86_64.AppImage"

   It starts in fullscreen with a 4:3 pillarboxed image.

If no ROM folder is found the game reports the missing file by name. In
Gaming Mode, put the roms folder next to the AppImage or set SAMSHO_ROM_DIR
in the game's launch options.

If the system has no FUSE 2 runtime (some minimal SteamOS images), run the
AppImage in extraction mode instead:

     APPIMAGE_EXTRACT_AND_RUN=1 "./Samsho-SteamDeck-x86_64.AppImage"

Steam Deck
----------
Copy the AppImage and a roms folder to the Deck, mark the AppImage executable,
and add it as a non-Steam game. It runs in Game Mode and Desktop Mode.

Controls
--------
  D-pad / left stick     move
  A B X Y (Xbox layout)  Neo Geo A B C D
  Back                   insert coin
  Start                  start
  Left shoulder          select
  F11                    toggle fullscreen
  Esc                    quit

Steam Input: the AppImage uses SDL2's GameController API. The default Steam
Deck template maps the built-in controls to a standard pad, so no extra
configuration is needed. If you use a custom layout, keep A/B/X/Y, the D-pad
or left stick, Start and Back mapped.

The game boots the real MVS BIOS, so insert a coin (Back) before Start.

License
-------
The original project code is PolyForm Noncommercial 1.0.0. The bundled
neogeorecomp runtime is MIT; Musashi and z80 are MIT; ymfm is BSD-3-Clause;
SDL2 is zlib. Full notices are in usr/share/doc/samsho/. No ROMs or BIOS
images are included. Samurai Shodown and Neo Geo are trademarks of SNK
Corporation; this project is not affiliated with or endorsed by SNK.
