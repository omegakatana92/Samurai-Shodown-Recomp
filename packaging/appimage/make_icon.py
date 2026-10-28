#!/usr/bin/env python3
"""Draw an original 256x256 icon for the Samurai Shodown recompilation.

No SNK artwork is used: a dusk gradient, a rising sun, a stylised blade and
block letters drawn from a tiny bitmap font.
"""
import os
import struct
import zlib

W = H = 256
px = bytearray(W * H * 3)


def put(x, y, r, g, b):
    if 0 <= x < W and 0 <= y < H:
        i = (y * W + x) * 3
        px[i] = r
        px[i + 1] = g
        px[i + 2] = b


def rect(x0, y0, x1, y1, r, g, b):
    for y in range(max(0, y0), min(H, y1)):
        for x in range(max(0, x0), min(W, x1)):
            put(x, y, r, g, b)


# Background: dusk red to deep violet.
for y in range(H):
    t = y / (H - 1)
    put(0, y, 0, 0, 0)
    for x in range(W):
        put(x, y, int(28 + 90 * (1 - t)), int(8 + 32 * (1 - t)), int(40 + 50 * t))

# Rising sun disk.
cx, cy, rad = 128, 104, 62
for y in range(cy - rad, cy + rad):
    for x in range(cx - rad, cx + rad):
        d2 = (x - cx) ** 2 + (y - cy) ** 2
        if d2 <= rad * rad:
            blend = 1.0 - (d2 / (rad * rad)) * 0.35
            put(x, y, int(226 * blend), int(58 * blend), int(44 * blend))

# Blade: a long diagonal highlight.
for i in range(150):
    x = 36 + i
    y = 196 - i
    for w in range(5):
        put(x, y + w, 235, 240, 250)
    for w in range(1, 4):
        put(x, y + 5 + w, 150, 160, 180)

# Dark panel behind the lettering.
rect(8, 184, 248, 244, 10, 8, 16)
rect(10, 186, 246, 242, 24, 14, 28)

FONT = {
    "S": ["01111", "10000", "10000", "01110", "00001", "00001", "11110"],
    "A": ["01110", "10001", "10001", "11111", "10001", "10001", "10001"],
    "M": ["10001", "11011", "10101", "10101", "10001", "10001", "10001"],
    "U": ["10001", "10001", "10001", "10001", "10001", "10001", "01110"],
    "R": ["11110", "10001", "10001", "11110", "10100", "10010", "10001"],
    "I": ["11111", "00100", "00100", "00100", "00100", "00100", "11111"],
}


def draw_text(text, x, y, scale, r, g, b):
    cx = x
    for ch in text:
        glyph = FONT.get(ch)
        if glyph:
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        rect(cx + gx * scale, y + gy * scale,
                             cx + (gx + 1) * scale, y + (gy + 1) * scale, r, g, b)
        cx += 6 * scale


draw_text("SAMURAI", 16, 190, 3, 255, 226, 120)
draw_text("SHODOWN", 150, 202, 2, 245, 245, 245)

raw = bytearray()
for y in range(H):
    raw.append(0)
    raw += px[y * W * 3:(y + 1) * W * 3]


def chunk(tag, data):
    return (struct.pack(">I", len(data)) + tag + data +
            struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF))


out = b"\x89PNG\r\n\x1a\n"
out += chunk(b"IHDR", struct.pack(">IIBBBBB", W, H, 8, 2, 0, 0, 0))
out += chunk(b"IDAT", zlib.compress(bytes(raw), 9))
out += chunk(b"IEND", b"")

path = os.path.join(os.path.dirname(os.path.abspath(__file__)), "samsho.png")
with open(path, "wb") as f:
    f.write(out)
print("wrote", path, len(out), "bytes")
