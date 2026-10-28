#!/usr/bin/env python3
"""Validate the Samurai Shodown (MAME set `samsho`) ROM files.

Checks every file the runtime loads against MAME's neogeo.cpp: size, CRC32
and SHA1. The game set and the required `neogeo` system ROMs may live in one
directory or be passed as two.

Usage:
    python scripts/validate-roms.py ROM_DIR [BIOS_DIR]

Exit code 0 means every file matched; 1 means a problem was found.
No ROM data is read from or written anywhere except the paths given.
"""
import hashlib
import os
import sys
import zlib

# MAME src/mame/snk/neogeo.cpp, ROM_START( samsho ) (MVS version).
GAME = {
    "045-p1.p1":   (0x100000, "dfe51bf0", "2243af3770a516ae698b69bcd9daf53632d9128d"),
    "045-pg2.sp2": (0x100000, "46745b94", "d9e959fd1f88c9402915c1d0dcdb4a9e3d49cdcb"),
    "045-s1.s1":   (0x020000, "9142a4d3", "54088e99fcfd75fd0f94852890a56350066a05a3"),
    "045-m1.m1":   (0x020000, "95170640", "125c502db0693e8d11cef619b090081c14a9a300"),
    "045-v1.v1":   (0x200000, "37f78a9b", "6279b497d12fa90b49ab5ac3aae20fb302ec8b81"),
    "045-v2.v2":   (0x200000, "568b20cf", "61af858685472a1fad608e230cccc2b108509ddb"),
    "045-c1.c1":   (0x200000, "2e5873a4", "65c74c1e2d34390666bbb630df7d1f4c9570c3db"),
    "045-c2.c2":   (0x200000, "04febb10", "16a8cbf0fd9468e81bf9eab6dbe7a8e3623a843e"),
    "045-c3.c3":   (0x200000, "f3dabd1e", "c80e52df42be9f8b2e89b467b11ab140a480cee8"),
    "045-c4.c4":   (0x200000, "935c62f0", "0053d40085fac14096b683f4341f65e543b71dc1"),
    "045-c51.c5":  (0x100000, "81932894", "550f15dc5892c4602422c51869f0d59f70f01e9e"),
    "045-c61.c6":  (0x100000, "be30612e", "5e8b785f917c176d6796eba0caed37b13ddb3e63"),
}

BIOS = {
    "sp-s2.sp1": (0x020000, "9036d879", "4f5ed7105b7128794654ce82b51723e16e389543"),
    "sfix.sfix": (0x020000, "c2ea0cfd", "fd4a618cdcdbf849374f0a50dd8efe9dbab706c3"),
    "sm1.sm1":   (0x020000, "94416d67", "42f9d7ddd6c0931fd64226a60dc73602b2819dcf"),
    "000-lo.lo": (0x020000, "5a86cff2", "5992277debadeb64d1c1c64b0a92d9293eaf7e4a"),
}


def check(name, expected, search):
    size, crc, sha1 = expected
    for d in search:
        p = os.path.join(d, name)
        if os.path.isfile(p):
            break
    else:
        print("MISSING   %-14s (looked in %s)" % (name, ", ".join(search)))
        return False
    data = open(p, "rb").read()
    got_crc = "%08x" % (zlib.crc32(data) & 0xFFFFFFFF)
    got_sha1 = hashlib.sha1(data).hexdigest()
    ok = len(data) == size and got_crc == crc and got_sha1 == sha1
    if ok:
        print("OK        %-14s %9d bytes  crc32 %s" % (name, len(data), got_crc))
    else:
        print("MISMATCH  %-14s size %d (want %d) crc32 %s (want %s)"
              % (name, len(data), size, got_crc, crc))
    return ok


def main():
    if len(sys.argv) < 2:
        print(__doc__)
        return 2
    game_dir = sys.argv[1]
    bios_dir = sys.argv[2] if len(sys.argv) > 2 else game_dir
    ok = True
    print("== game set samsho ==")
    for n, e in GAME.items():
        ok &= check(n, e, [game_dir])
    print("== system set neogeo ==")
    for n, e in BIOS.items():
        ok &= check(n, e, [bios_dir, game_dir])
    print("result:", "all files verified" if ok else "PROBLEMS FOUND")
    return 0 if ok else 1


if __name__ == "__main__":
    sys.exit(main())
