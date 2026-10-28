#!/usr/bin/env python3
"""Audio continuity regression for Samurai Shodown.

Usage: tests/check_audio.py <capture.wav>

Fails on music-sized silent runs after the BIOS boot. This catches a stalled
Z80 music stream while one-shot effects still play, which a whole-file RMS
check would miss.
"""
import math
import struct
import sys
import wave

MIN_PEAK = 1000
MAX_SILENCE = 3.0
BOOT_SECONDS = 10


def fail(msg):
    print(f"FAIL: {msg}")
    return 1


def main(path):
    try:
        w = wave.open(path, "rb")
    except OSError as e:
        return fail(f"cannot open {path}: {e}")
    rate, channels, width = w.getframerate(), w.getnchannels(), w.getsampwidth()
    n = w.getnframes()
    raw = w.readframes(n)
    w.close()
    if rate < 8000 or channels not in (1, 2) or width != 2:
        return fail(f"unexpected WAV format: {rate} Hz, {channels} ch, {width * 8} bit")

    samples = struct.unpack("<%dh" % (len(raw) // 2), raw)
    if channels == 2:
        mono = [(samples[i] + samples[i + 1]) / 2.0 for i in range(0, len(samples), 2)]
    else:
        mono = list(samples)

    peak = max((abs(x) for x in mono), default=0)
    if peak < MIN_PEAK:
        return fail(f"capture is silent (peak {peak:.0f})")

    secs = []
    for start in range(0, len(mono) - rate + 1, rate):
        block = mono[start:start + rate]
        secs.append(math.sqrt(sum(x * x for x in block) / len(block)))

    silent = [i for i, r in enumerate(secs) if i >= BOOT_SECONDS and r < 50.0]
    runs = []
    for i in silent:
        if runs and i == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], i)
        else:
            runs.append((i, i))
    longest = max((b - a + 1 for a, b in runs), default=0)
    print(f"duration {len(mono) / rate:.1f} s, peak {peak:.0f}, "
          f"longest silent run {longest} s")
    if longest > MAX_SILENCE:
        print("silent runs:", [(a, b, b - a + 1) for a, b in runs])
        return fail(f"silent run longer than {MAX_SILENCE:.0f} s")
    print("PASS: audio is continuous after boot")
    return 0


if __name__ == "__main__":
    if len(sys.argv) != 2:
        print("usage: tests/check_audio.py <capture.wav>")
        sys.exit(2)
    sys.exit(main(sys.argv[1]))

