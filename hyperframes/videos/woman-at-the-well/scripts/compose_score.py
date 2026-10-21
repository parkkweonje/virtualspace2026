"""Original score + sound design for "The Woman at the Well" (42s), synthesized with numpy.

Timings follow index.html scene windows. Run:
  python3 scripts/compose_score.py assets/audio/score_raw.wav
then loudness-normalize with ffmpeg (see README in the commit message).
"""
import sys
import wave

import numpy as np

SR = 44100
LEN = 42.0
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


def pluck(m, dur=0.3, vel=1.0):
    """Oud-like pluck: bright attack, quick decay."""
    return vel * partials(m2f(m), dur, [1, 2, 3, 4, 5, 6], [1, 0.6, 0.45, 0.25, 0.15, 0.08], [0.9, 0.45, 0.3, 0.2, 0.14, 0.1], 0.002, 0.2)


def drum(t0, low=True, vel=1.0):
    if low:
        place(boom(70, 0.6, 1.0) * 0.8, t0, gain=0.22 * vel, send=0.15)
    else:
        place(noise_band(0.18, 2500, 3500, 0.7, "burst"), t0, gain=0.07 * vel, send=0.2)


def clap(t0, vel=1.0):
    place(noise_band(0.22, 1400, 1800, 0.9, "burst"), t0, pan=0.2, gain=0.09 * vel, send=0.35)


# ---------------- S0 · empty jar on paper (0 – 5.4) — lonely pluck in D dorian ----------------
for i, (m, d) in enumerate([(62, 0.45), (65, 0.45), (67, 0.45), (69, 0.9), (72, 0.45), (69, 0.45), (67, 0.45), (69, 1.0)]):
    place(pluck(m, d, 0.9), 0.3 + sum(x for _, x in [(62, 0.45), (65, 0.45), (67, 0.45), (69, 0.9), (72, 0.45), (69, 0.45), (67, 0.45), (69, 1.0)][:i]), pan=0.15, gain=0.26, send=0.4)
chordpad([50, 57, 62], 0.2, 4.0, 0.05, attack=1.2, release=1.0, bright=1.5)
place(ping(86, 0.16, 0.05) + ping(74, 0.1, 0.05), 3.0, gain=1.0, send=0.6)  # drop into the jar
whoosh(4.2, 5.4, 900, 160, gain=0.3)
place(boom(55, 1.6, 0.8), 5.3, gain=0.18, send=0.6)  # hollow inside the jar

# ---------------- S1 · noon in Sychar (5.4 – 10.1) — heat, frame drum, oud ----------------
chordpad([38, 45, 50, 57], 5.4, 3.8, 0.07, attack=0.6, release=0.8, bright=2.0, vib=0.002)
place(noise_band(3.8, 5000, 7000, 0.5, "swell"), 5.4, gain=0.04, send=0.5)  # heat shimmer
B = 0.75
for k in range(6):
    t0 = 5.6 + k * B
    drum(t0, True, 0.9)
    drum(t0 + B * 0.5, False, 0.8)
    drum(t0 + B * 0.75, False, 0.5)
mel = [(69, 0.375), (72, 0.375), (74, 0.75), (76, 0.375), (74, 0.375), (72, 0.75), (69, 0.375), (67, 0.375), (69, 0.9)]
tm = 5.9
for m, d in mel:
    place(pluck(m, d, 1.0), tm, pan=-0.15, gain=0.24, send=0.35)
    tm += d
whoosh(9.2, 10.15, 800, 9000, gain=0.28)
place(noise_band(0.8, 7000, 9000, 0.6, "swell"), 9.4, gain=0.08, send=0.6)

# ---------------- S2 · at the well (10.1 – 15.3) — warmth arrives ----------------
for k, (ch, b) in enumerate([([53, 57, 60], 41), ([48, 52, 55], 36), ([50, 53, 57], 38), ([46, 50, 53], 34)]):
    t0 = 10.1 + k * 1.05
    chordpad(ch, t0, 1.05, 0.065, attack=0.5, release=1.0, bright=2.0)
    place(bass(b, 1.0, 0.8), t0, gain=0.17, send=0.15)
    drum(t0, True, 0.5)
for i, m in enumerate([69, 72, 76, 81]):  # "Give me a drink" — harp chord
    place(box(m, 1.2, 0.8), 12.3 + i * 0.07, pan=-0.3 + 0.2 * i, gain=0.2, send=0.55)
place(pluck(76, 0.12, 1.0), 13.5, gain=0.2, send=0.3)
place(pluck(77, 0.12, 1.0), 13.65, gain=0.2, send=0.3)
for i, m in enumerate([74, 72, 69]):
    place(pluck(m, 0.4, 0.8), 14.0 + i * 0.3, pan=0.2, gain=0.18, send=0.45)
whoosh(14.35, 15.35, 4000, 180, gain=0.3)

# ---------------- S3 · down the well (15.3 – 20.2) — dark, echoing drips ----------------
chordpad([33, 40, 45], 15.3, 3.9, 0.08, attack=0.8, release=1.0, bright=1.8)
r3 = np.random.default_rng(13)
for i in range(9):
    place(ping(int(r3.choice([79, 81, 84, 86, 88])), 0.07, 0.03), 15.6 + i * 0.4 + r3.uniform(0, 0.2), pan=r3.uniform(-0.8, 0.8), gain=1.0, send=0.85)
for i, m in enumerate([69, 67, 65, 64, 62, 60, 57]):  # bucket descends
    place(pluck(m, 0.35, 0.7), 15.6 + i * 0.4, pan=0.0, gain=0.15, send=0.6)
place(noise_band(0.7, 1200, 400, 1.0, "burst"), 18.3, gain=0.2, send=0.6)  # splash
place(ping(84, 0.2, 0.1) + ping(91, 0.12, 0.1), 18.3, gain=1.0, send=0.8)
whoosh(19.25, 20.25, 200, 6000, gain=0.3)
for i in range(10):  # bubbles
    place(ping(72 + 2 * i, 0.05, 0.02), 19.5 + i * 0.07, pan=r3.uniform(-0.6, 0.6), gain=1.0, send=0.5)

# ---------------- S4 · living water (20.2 – 25.8) — D major, flowing harp ----------------
place(boom(38, 2.0, 0.8), 20.4, gain=0.25, send=0.4)
place(noise_band(1.2, 3000, 9000, 0.7, "burst"), 20.4, gain=0.07, send=0.5)
for k, (ch, b) in enumerate([([62, 66, 69], 38), ([55, 59, 62], 43), ([59, 62, 66], 47), ([57, 61, 64], 45), ([62, 66, 69], 50)]):
    t0 = 20.4 + k * 1.0
    d = 1.0 if k < 4 else 1.4
    chordpad([c + 12 for c in ch], t0, d, 0.07, attack=0.3, release=1.0, bright=2.6, vib=0.003)
    place(bass(b, d, 0.9), t0, gain=0.2, send=0.15)
    tones = sorted(ch) + [c + 12 for c in sorted(ch)]
    for j in range(8):
        place(box(tones[j % 6] + 12, 0.14, 0.75), t0 + j * 0.125, pan=-0.6 + j * 0.16, gain=0.13, send=0.45)
mel = [(78, 1.0), (81, 0.5), (83, 0.5), (86, 1.0), (85, 0.5), (83, 0.5), (81, 1.2)]
tm = 20.6
for m, d in mel:
    place(piano(m, d, 0.9), tm, pan=0.15, gain=0.2, send=0.45)
    tm += d
for i in range(10):
    place(ping(93 + (i % 4) * 2, 0.09, 0.04), 21.9 + i * 0.09, pan=-0.7 + 0.15 * i, gain=1.0, send=0.5)
place(noise_band(0.9, 1500, 9000, 0.6, "swell"), 25.0, gain=0.16, send=0.6)

# ---------------- S5 · "I am he" (25.8 – 31.3) — majestic ----------------
place(boom(37, 2.6, 1.0), 25.85, gain=0.32, send=0.35)
for k, (ch, b) in enumerate([([62, 66, 69, 74], 38), ([59, 62, 66, 71], 35), ([55, 59, 62, 67], 43), ([57, 61, 64, 69], 45)]):
    t0 = 25.85 + k * 1.2
    chordpad(ch, t0, 1.2, 0.085, attack=0.35, release=1.2, bright=3.0, vib=0.003)
    place(bass(b, 1.2, 1.0), t0, gain=0.22, send=0.15)
place(bell(74, 0.9), 26.85, gain=0.2, send=0.55)
mel = [(69, 0.6), (74, 0.6), (78, 1.2), (76, 0.6), (74, 0.6), (73, 0.6), (74, 1.2)]
tm = 26.6
for m, d in mel:
    place(piano(m, d, 1.0) + 0.45 * piano(m - 12, d, 1.0), tm, pan=0.1, gain=0.2, send=0.4)
    tm += d
place(boom(80, 0.5, 0.6), 28.8, gain=0.14, send=0.2)  # jar set down
whoosh(30.7, 31.4, 300, 3000, gain=0.3, pan=0.5)

# ---------------- S6 · "Come, see!" (31.0 – 36.1) — joyful, rhythmic ----------------
B = 0.5
for k in range(10):
    t0 = 31.1 + k * B
    drum(t0, True, 1.0 if k % 2 == 0 else 0.7)
    drum(t0 + B * 0.5, False, 0.9)
    if k >= 4 and k % 2 == 1:
        clap(t0)
for k, (ch, b) in enumerate([([62, 66, 69], 38), ([55, 59, 62], 43), ([57, 61, 64], 45), ([62, 66, 69], 38), ([55, 59, 62], 43)]):
    t0 = 31.1 + k * 1.0
    chordpad(ch, t0, 1.0, 0.06, attack=0.15, release=0.6, bright=2.6)
    place(bass(b, 0.45, 1.0), t0, gain=0.2, send=0.1)
    place(bass(b + 7, 0.4, 0.8), t0 + 0.5, gain=0.15, send=0.1)
mel = [(74, 0.25), (76, 0.25), (78, 0.5), (81, 0.5), (78, 0.25), (76, 0.25), (74, 0.5), (76, 0.25), (78, 0.25), (81, 0.5), (83, 0.5), (81, 1.0)]
tm = 31.6
for m, d in mel * 1:
    place(pluck(m, d, 1.0), tm, pan=-0.1, gain=0.24, send=0.3)
    tm += d
place(noise_band(0.7, 1500, 9000, 0.6, "swell"), 35.5, gain=0.15, send=0.6)

# ---------------- S7 · the jar overflows (36.1 – 42) — theme returns in major ----------------
place(noise_band(2.2, 3000, 5000, 0.8, "burst"), 37.3, gain=0.05, send=0.5)  # trickle
for i, (m, d) in enumerate([(62, 0.4), (66, 0.4), (67, 0.4), (69, 0.8), (74, 0.4), (69, 0.4), (67, 0.4)]):
    place(box(m + 12, d, 0.85), 36.4 + sum(x for _, x in [(62, 0.4), (66, 0.4), (67, 0.4), (69, 0.8), (74, 0.4), (69, 0.4), (67, 0.4)][:i]), pan=0.15, gain=0.28, send=0.45)
chordpad([62, 66, 69], 36.3, 1.6, 0.055, attack=0.5, release=0.8)
chordpad([55, 59, 62], 37.9, 0.7, 0.055, attack=0.3, release=0.8)
place(box(86, 2.6, 0.9) + box(81, 2.6, 0.6) + box(78, 2.6, 0.5) + box(74, 2.6, 0.5), 39.2, gain=0.26, send=0.55)
chordpad([50, 57, 62, 66, 69], 39.2, 1.6, 0.07, attack=0.2, release=1.0)
place(bass(38, 1.8, 0.9), 39.2, gain=0.2, send=0.2)
for i in range(4):
    place(ping(95 + 2 * i, 0.1, 0.05), 38.6 + i * 0.1, pan=-0.4 + 0.3 * i, gain=1.0, send=0.5)


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
