"""Original score for "Joseph" chapter 1 (78s) — a bed that sits under narration, synthesized with numpy.

Timings follow index.html scene windows. Run:
  python3 scripts/compose_score.py assets/audio/score_raw.wav
then loudness-normalize with ffmpeg (see README in the commit message).
"""
import sys
import wave

import numpy as np

SR = 44100
LEN = 78.0
N = int(SR * (LEN + 0.5))
rng = np.random.default_rng(7)

dry = np.zeros((2, N))
wet = np.zeros((2, N))


def m2f(m):
    return 440.0 * 2 ** ((m - 69) / 12)


def place(sig, t0, pan=0.0, gain=1.0, send=0.25):
    i0 = int(t0 * SR)
    if i0 >= N:
        return
    sig = sig[: N - i0] * gain
    a = (pan + 1) * np.pi / 4
    lr = (np.cos(a), np.sin(a))
    for ch in (0, 1):
        dry[ch, i0 : i0 + len(sig)] += sig * lr[ch] * (1 - send * 0.5)
        wet[ch, i0 : i0 + len(sig)] += sig * lr[ch] * send


def env(n, attack, release_start, release):
    t = np.arange(n) / SR
    e = np.minimum(1.0, t / max(attack, 1e-4))
    rel = np.clip((t - release_start) / max(release, 1e-4), 0, 1)
    return e * (0.5 + 0.5 * np.cos(np.pi * rel))


def partials(f, dur, ratios, amps, taus, attack=0.004, release=0.3):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for r, a, tau in zip(ratios, amps, taus):
        if f * r > SR / 2.2:
            continue
        s += a * np.sin(2 * np.pi * f * r * t + rng.uniform(0, 6.28)) * np.exp(-t / tau)
    return s * env(n, attack, dur, release)


def box(m, dur=0.4, vel=1.0):
    return vel * partials(m2f(m), dur, [1, 2, 3.0, 4.16], [1, 0.4, 0.12, 0.06], [1.4, 0.6, 0.3, 0.18], 0.003, 0.35)


def piano(m, dur=0.6, vel=1.0):
    f = m2f(m)
    B = 0.0004
    ks = np.arange(1, 9)
    ratios = ks * np.sqrt(1 + B * ks**2)
    amps = 1 / ks**1.3
    amps[1] *= 1.3
    base = 2.6 * (261.6 / f) ** 0.35
    taus = base / ks**0.7
    return vel * partials(f, dur, ratios, amps, taus, 0.005, 0.35)


def pad(ms, dur, attack=0.9, release=1.4, detune=(-6, 0, 6), bright=2.5, vib=0.0):
    n = int((dur + release) * SR)
    t = np.arange(n) / SR
    s = np.zeros(n)
    for m in ms:
        for c in detune:
            f = m2f(m) * 2 ** (c / 1200)
            ph = 2 * np.pi * f * t
            if vib:
                ph += (vib * f / 5.2) * np.sin(2 * np.pi * 5.2 * t)
            for k in range(1, 9):
                if f * k > 9000:
                    break
                s += (1 / k) * np.exp(-(k - 1) / bright) * np.sin(k * ph + rng.uniform(0, 6.28))
    s /= max(1, len(ms) * len(detune))
    return s * env(n, attack, dur, release)


def bass(m, dur, vel=1.0):
    f = m2f(m)
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    s = (np.sin(2 * np.pi * f * t) + 0.3 * np.sin(4 * np.pi * f * t)) * np.exp(-t / 2.2)
    return vel * s * env(n, 0.02, dur, 0.25)


def bell(m, vel=1.0):
    f = m2f(m)
    return vel * partials(
        f, 2.4, [0.5, 1, 1.2, 1.5, 2, 2.5, 3.0, 4.2], [0.45, 1, 0.55, 0.35, 0.5, 0.22, 0.18, 0.08], [2.2, 1.8, 1.5, 1.3, 1.1, 0.9, 0.7, 0.5], 0.003, 1.0
    )


def boom(f0=46, dur=2.2, vel=1.0):
    n = int(dur * SR)
    t = np.arange(n) / SR
    f = f0 * (1 + 1.6 * np.exp(-t / 0.04))
    ph = 2 * np.pi * np.cumsum(f) / SR
    return vel * np.sin(ph) * np.exp(-t / 0.7) * env(n, 0.002, dur - 0.3, 0.3)


def noise_band(dur, f0, f1, width_oct=0.6, shape="whoosh"):
    """Band-passed noise whose centre sweeps f0 -> f1 (STFT overlap-add)."""
    n = int(dur * SR)
    frame, hop = 2048, 512
    out = np.zeros(n + frame)
    win = np.hanning(frame)
    freqs = np.fft.rfftfreq(frame, 1 / SR)
    K = max(1, (n - frame) // hop + 1)
    for k in range(K):
        fc = f0 * (f1 / f0) ** (k / K)
        mask = np.exp(-0.5 * (np.log2(np.maximum(freqs, 1) / fc) / width_oct) ** 2)
        spec = np.fft.rfft(rng.standard_normal(frame) * win) * mask
        out[k * hop : k * hop + frame] += np.fft.irfft(spec) * win
    out = out[:n]
    out /= np.max(np.abs(out)) + 1e-9
    t = np.linspace(0, 1, n)
    if shape == "whoosh":  # swell, peak late, quick release
        e = np.sin(np.pi * np.clip(t / 0.88, 0, 1) * 0.5) ** 2 * np.clip((1 - t) / 0.12, 0, 1)
    elif shape == "swell":
        e = t**2
    else:  # burst: fast attack, long decay
        e = np.minimum(1, t * dur / 0.01) * np.exp(-t * dur / 0.9)
    return out * e


def whoosh(t0, t1, f0=300, f1=4000, gain=0.35, pan=0.0):
    place(noise_band(t1 - t0, f0, f1), t0, pan=pan, gain=gain, send=0.35)


def ping(m, vel=0.12, dur=0.05):
    return vel * partials(m2f(m), dur, [1, 2.76, 5.4], [1, 0.35, 0.12], [0.5, 0.15, 0.06], 0.001, 0.25)


def chordpad(ms, t0, dur, gain, **kw):
    place(pad(ms, dur, detune=(-7, 3), **kw), t0, pan=-0.45, gain=gain, send=0.4)
    place(pad(ms, dur, detune=(-3, 7), **kw), t0, pan=0.45, gain=gain, send=0.4)



def mix(*sigs):
    out = np.zeros(max(len(x) for x in sigs))
    for x in sigs:
        out[: len(x)] += x
    return out


def flute(m, dur=0.5, vel=1.0):
    f = m2f(m)
    n = int((dur + 0.25) * SR)
    t = np.arange(n) / SR
    ph = 2 * np.pi * f * t + (0.004 * f / 5.0) * np.sin(2 * np.pi * 5.0 * t) * np.minimum(1, t / 0.3)
    s = np.sin(ph) + 0.22 * np.sin(2 * ph) + 0.06 * np.sin(3 * ph)
    s += 0.04 * rng.standard_normal(n) * np.exp(-t / 0.08)  # breath
    return vel * s * env(n, 0.06, dur, 0.25)


def pluck(m, dur=0.3, vel=1.0):
    return vel * partials(m2f(m), dur, [1, 2, 3, 4, 5], [1, 0.6, 0.4, 0.22, 0.12], [0.9, 0.45, 0.3, 0.2, 0.14], 0.002, 0.2)


def brass(ms, t0, dur, gain):
    chordpad(ms, t0, dur, gain, attack=0.08, release=0.5, bright=4.5, vib=0.004)


def drum(t0, low=True, vel=1.0):
    if low:
        place(boom(66, 0.6, 1.0) * 0.8, t0, gain=0.22 * vel, send=0.15)
    else:
        place(noise_band(0.16, 2400, 3400, 0.7, "burst"), t0, gain=0.07 * vel, send=0.2)


def seq(notes, t0, fn, gain, pan=0.0, send=0.4):
    t = t0
    for m, d in notes:
        if m:
            place(fn(m, d, 1.0), t, pan=pan, gain=gain, send=send)
        t += d



# ---------------- A1 · Jacob's tents (0 – 13.6) — pastoral flute in G ----------------
for k, (ch, b) in enumerate([([55, 59, 62], 43), ([52, 55, 59], 40), ([48, 52, 55], 36), ([50, 54, 57], 38)] * 2):
    t0 = 0.4 + k * 1.65
    chordpad(ch, t0, 1.65, 0.045, attack=0.6, release=1.0, bright=1.6)
    place(bass(b, 1.6, 0.6), t0, gain=0.13, send=0.2)
seq([(74, 0.55), (71, 0.55), (74, 0.55), (76, 1.1), (74, 0.55), (72, 0.55), (71, 1.1), (69, 0.55), (71, 0.55), (74, 1.65), (79, 0.55), (78, 0.55), (76, 1.1)], 0.8, flute, 0.17, pan=0.15, send=0.45)

# ---------------- A2 · the coat (13.6 – 31) — warmth, a stripe sparkles ----------------
for k, (ch, b) in enumerate([([55, 59, 62, 66], 43), ([60, 64, 67], 48), ([52, 55, 59, 62], 40), ([50, 54, 57, 60], 38)] * 2):
    t0 = 13.6 + k * 2.15
    chordpad([c + 12 for c in ch], t0, 2.15, 0.05, attack=0.8, release=1.2, bright=2.0, vib=0.002)
    place(bass(b, 2.1, 0.7), t0, gain=0.14, send=0.2)
for i in range(7):  # each stripe of the coat
    place(ping(83 + [0, 2, 4, 7, 9, 11, 12][i], 0.12, 0.06), 16.6 + i * 0.35, pan=-0.4 + 0.13 * i, gain=1.0, send=0.55)
seq([(79, 1.0), (83, 0.5), (81, 0.5), (79, 1.0), (76, 1.0), (74, 2.0)], 21.0, piano, 0.15, pan=0.2, send=0.5)

# ---------------- A3 · jealousy (31 – 43.9) — E minor, low pulse ----------------
chordpad([28, 35, 40], 31.0, 12.0, 0.07, attack=2.0, release=1.2, bright=2.4)
for k, (ch, b) in enumerate([([52, 55, 59], 40), ([48, 52, 55, 58], 36), ([45, 48, 52], 33), ([47, 51, 54], 35)] * 2):
    t0 = 31.2 + k * 1.55
    chordpad(ch, t0, 1.55, 0.045, attack=0.5, release=0.9, bright=1.8, vib=0.004)
for k in range(16):
    place(bass(28 + 12, 0.18, 1.0), 31.4 + k * 0.78, gain=0.12, send=0.15)
place(noise_band(2.5, 300, 900, 0.8, "swell"), 32.0, gain=0.05, send=0.4)  # the scribble cloud

# ---------------- B · dream of sheaves (43.9 – 54.6) — celesta, shimmer ----------------
place(noise_band(1.2, 4000, 9000, 0.6, "swell"), 43.2, gain=0.08, send=0.6)
for k, (ch, b) in enumerate([([62, 66, 69, 76], 38), ([59, 62, 66, 73], 35), ([55, 59, 62, 69], 43), ([57, 61, 64, 71], 45)]):
    t0 = 44.0 + k * 2.6
    chordpad([c + 12 for c in ch], t0, 2.6, 0.045, attack=0.9, release=1.2, bright=1.4)
    tones = sorted(ch) + [c + 12 for c in sorted(ch)]
    for j in range(12):
        place(box(tones[j % 8] + 12, 0.2, 0.6), t0 + j * 0.215, pan=-0.6 + 0.1 * j, gain=0.09, send=0.6)
place(box(86, 1.5, 0.9) + box(81, 1.5, 0.6), 48.6, gain=0.18, send=0.6)  # Joseph's sheaf rises
for i in range(11):  # the sheaves bow
    place(ping(81 - i, 0.06, 0.04), 51.6 + i * 0.06, pan=-0.7 + 0.14 * i, gain=1.0, send=0.6)

# ---------------- C · sun, moon, eleven stars (54.6 – 60.1) ----------------
chordpad([50, 57, 62, 66, 69], 54.6, 5.2, 0.05, attack=1.0, release=1.0, bright=1.6)
for i in range(13):
    place(ping(86 + (i * 5) % 12, 0.08, 0.05), 54.9 + i * 0.06, pan=-0.8 + 0.13 * i, gain=1.0, send=0.65)
place(bell(74, 0.8), 57.0, gain=0.14, send=0.65)
whoosh(59.6, 60.5, 600, 7000, gain=0.2)

# ---------------- D · night tent (60.1 – 70.1) — low strings, a held heart ----------------
for k, (ch, b) in enumerate([([47, 50, 55], 31), ([45, 48, 52], 33), ([43, 47, 50], 31), ([45, 48, 52, 55], 33)]):
    t0 = 60.4 + k * 2.4
    chordpad(ch, t0, 2.4, 0.06, attack=0.9, release=1.2, bright=1.8, vib=0.003)
    place(bass(b, 2.3, 0.6), t0, gain=0.13, send=0.2)
place(piano(40, 0.6, 1.0) + piano(47, 0.6, 0.8), 61.4, gain=0.18, send=0.3)  # rebuke
seq([(71, 0.6), (74, 0.6), (79, 1.2), (78, 0.6), (76, 0.6), (74, 1.6)], 65.8, piano, 0.15, pan=0.15, send=0.55)

# ---------------- E · "Here comes this dreamer" (70.1 – 78) — unease ----------------
chordpad([28, 35, 40, 43], 70.1, 7.0, 0.08, attack=1.2, release=1.0, bright=2.6)
for k in range(9):  # heartbeat
    place(boom(55, 0.5, 0.8), 70.6 + k * 0.85, gain=0.14, send=0.2)
    place(boom(55, 0.4, 0.6), 70.82 + k * 0.85, gain=0.09, send=0.2)
seq([(76, 0.8), (75, 0.8), (76, 1.6), (71, 2.4)], 72.2, flute, 0.13, pan=-0.2, send=0.6)


# ---------------- reverb + master ----------------
ir_len = int(2.6 * SR)
ti = np.arange(ir_len) / SR
mix = dry.copy()
size = 1 << int(np.ceil(np.log2(N + ir_len)))
fr = np.fft.rfftfreq(size, 1 / SR)
hp_wet = 1 / (1 + (220 / np.maximum(fr, 1)) ** 4)  # keep the reverb out of the low end
hp_mst = 1 / (1 + (38 / np.maximum(fr, 1)) ** 6)
for ch in (0, 1):
    ir = np.random.default_rng(100 + ch).standard_normal(ir_len) * np.exp(-ti / 0.55) * np.minimum(1, ti / 0.012)
    ir /= np.sqrt(np.sum(ir**2))
    w = np.fft.irfft(np.fft.rfft(wet[ch], size) * np.fft.rfft(ir, size) * hp_wet, size)[:N]
    mix[ch] += w * 0.9
    mix[ch] = np.fft.irfft(np.fft.rfft(mix[ch], size) * hp_mst, size)[:N]
fade = np.clip((LEN - np.arange(N) / SR) / 0.9, 0, 1)
mix *= fade
mix = np.tanh(mix / (np.max(np.abs(mix)) + 1e-9) * 1.2) * 0.89

out = sys.argv[1] if len(sys.argv) > 1 else "score_raw.wav"
data = (np.clip(mix.T, -1, 1) * 32767).astype("<i2")
with wave.open(out, "wb") as wf:
    wf.setnchannels(2)
    wf.setsampwidth(2)
    wf.setframerate(SR)
    wf.writeframes(data.tobytes())
print("wrote", out, f"{N / SR:.2f}s")
