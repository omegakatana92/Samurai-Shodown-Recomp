/*
 * game.c - Samurai Shodown (MAME set "samsho", NGH-045), the verified ROM
 * layout shared by the player and the recompiler.
 *
 * Layout and hashes were checked against MAME's src/mame/snk/neogeo.cpp,
 * ROM_START( samsho ) (the MVS version):
 *
 *   045-p1.p1    1 MB  TC538200   fixed program bank, 16-bit word-swapped
 *   045-pg2.sp2  1 MB  TC538200   banked program image, word-swapped
 *   045-s1.s1  128 KB  TC531000   fixed layer
 *   045-m1.m1  128 KB  TC531001   Z80 sound program
 *   045-v1.v1    2 MB  TC5316200  ADPCM-A
 *   045-v2.v2    2 MB  TC5316200  ADPCM-A
 *   045-c1.c1    2 MB  TC5316200  sprite planes 0,1
 *   045-c2.c2    2 MB  TC5316200  sprite planes 2,3
 *   045-c3.c3    2 MB  TC5316200  sprite planes 0,1
 *   045-c4.c4    2 MB  TC5316200  sprite planes 2,3
 *   045-c51.c5   1 MB  TC538200   sprite planes 0,1
 *   045-c61.c6   1 MB  TC538200   sprite planes 2,3
 *
 * The cart is a normal MVS/AES PROGBK1 board: 1 MB fixed at $000000 and one
 * 1 MB bank behind the $200000 window, selected through $2FFFF0. There is no
 * encryption, no NEO-SMA/CMC protection and no S ROM banking, so the generic
 * toolkit path is used.
 */
#include "game.h"

const ng_game_t k_samsho = {
    .name = "samsho",
    .title = "Samurai Shodown",
    .prom_size = 0x200000,          /* 1 MB fixed + 1 MB banked */
    .prom = {
        /* file          file offset  dest       length    swap */
        {"045-p1.p1",   0x000000,    0x000000,  0x100000, 1},
        {"045-pg2.sp2", 0x000000,    0x100000,  0x100000, 1},
    },
    .crom_size = 0xa00000,          /* 10 MB after pairing */
    .crom_pairs = {
        {"045-c1.c1",  "045-c2.c2"},     /* 4 MB */
        {"045-c3.c3",  "045-c4.c4"},     /* 4 MB */
        {"045-c51.c5", "045-c61.c6"},    /* 2 MB */
    },
    .srom = "045-s1.s1",
    .m1 = "045-m1.m1",
    .vrom = {"045-v1.v1", "045-v2.v2"},
};
