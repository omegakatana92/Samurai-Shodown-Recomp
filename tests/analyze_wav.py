#!/usr/bin/env python3
"""Print per-second RMS and silence runs for a WAV capture.

Usage: tests/analyze_wav.py FILE [BOOT_SECONDS]

Used for native/interpreter/reference comparison. It reports peak, RMS,
clipped samples and the silent runs (per-second RMS < 50) after boot.
"""
import array
import math
import sys
import wave

BOOT = 10


def main(path):
    w = wave.open(path, "rb")
    rate, ch, width, n = w.getframerate(), w.getnchannels(), w.getsampwidth(), w.getnframes()
    raw = w.readframes(n)
    w.close()
    a = array.array("h")
    a.frombytes(raw)
    if ch == 2:
        mono = [(a[i] + a[i + 1]) / 2.0 for i in range(0, len(a), 2)]
    else:
        mono = a
    peak = max(abs(x) for x in mono)
    clipped = sum(1 for x in mono if abs(x) >= 32767)
    rms = math.sqrt(sum(x * x for x in mono) / len(mono))
    print(f"{path}: {n / rate:.2f} s, {rate} Hz, {ch} ch, peak {peak:.0f}, "
          f"rms {rms:.1f}, clipped {clipped}")
    secs = []
    for s in range(0, len(mono) // rate):
        b = mono[s * rate:(s + 1) * rate]
        secs.append(math.sqrt(sum(x * x for x in b) / len(b)))
    silent = [i for i, r in enumerate(secs) if i >= BOOT and r < 50.0]
    runs = []
    for i in silent:
        if runs and i == runs[-1][1] + 1:
            runs[-1] = (runs[-1][0], i)
        else:
            runs.append((i, i))
    print("  silent runs:", [(a, b) for a, b in runs])
    print("  per-second rms (0-25 s):",
          [round(secs[i], 1) for i in range(0, min(26, len(secs)))])
    print("  per-second rms (100-180 s):",
          [round(secs[i], 1) for i in range(100, min(181, len(secs)))])


if __name__ == "__main__":
    main(sys.argv[1])
