"""Original score + sound design for the Holy Week film (40s), synthesized with numpy.

Timings follow index.html scene windows. Run:
  python3 scripts/compose_score.py assets/audio/score_raw.wav
then loudness-normalize with ffmpeg (see README in the commit message).
"""
import sys
import wave

import numpy as np

SR = 44100
LEN = 40.0
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


# ---------------- S0 · lamb on paper (0 – 5.5) — music-box theme in D ----------------
E8 = 0.3
theme = [74, 78, 81, 78, 78, 74, 71, 74, 79, 83, 81, 79, 76, 81]
for i, m in enumerate(theme):
    d = E8 * (3 if i == len(theme) - 1 else 1)
    place(box(m, d, 0.9), 0.3 + i * E8, pan=0.2 * np.sin(i), gain=0.32, send=0.35)
for k, (ch, b) in enumerate([([62, 66, 69], 50), ([59, 62, 66], 47), ([55, 59, 62], 43), ([57, 61, 64], 45)]):
    chordpad(ch, 0.3 + k * 1.2, 1.2, 0.06, attack=0.5, release=0.9, bright=1.8)
    place(bass(b, 1.1, 0.7), 0.3 + k * 1.2, gain=0.16, send=0.15)
whoosh(4.3, 5.55, 200, 5200, gain=0.32)

# ---------------- S1 · Palm Sunday (5.5 – 10.0) — bright, rising ----------------
t = 5.5
prog = [([62, 66, 69], 38, 50), ([55, 59, 62], 43, 55), ([54, 57, 62], 42, 54), ([57, 61, 64], 45, 57)]
arp = [0, 1, 2, 3, 2, 1, 2, 3]
for k, (ch, b, r) in enumerate(prog):
    t0 = t + k * 1.2
    chordpad([c + 12 for c in ch], t0, 1.2, 0.07, attack=0.35, release=1.0, bright=2.6)
    place(bass(b, 1.15, 0.9), t0, gain=0.22, send=0.12)
    tones = [r, r + 7, r + 12, ch[1] + 12]
    for j, a in enumerate(arp):
        place(piano(tones[a] + 12, 0.25, 0.55), t0 + j * 0.15, pan=-0.3 + 0.08 * j, gain=0.16, send=0.3)
mel = [(81, 0.6), (83, 0.6), (86, 1.2), (85, 0.6), (83, 0.6), (81, 0.5), (83, 0.15), (85, 0.15), (88, 0.3)]
tm = t
for m, d in mel:
    place(piano(m, d, 0.9), tm, pan=0.15, gain=0.24, send=0.35)
    tm += d
whoosh(9.0, 10.05, 160, 3800, gain=0.34)

# ---------------- S2 · temple (10.0 – 14.3) — B minor tension, coins ----------------
t = 10.0
for k, (ch, b) in enumerate([([59, 62, 66], 35), ([55, 59, 62], 31), ([52, 55, 59], 28), ([54, 58, 61], 30)]):
    t0 = t + k * 1.0
    chordpad(ch, t0, 1.0, 0.07, attack=0.15, release=0.6, bright=3.2)
    for j in range(4):  # staccato pulses
        place(bass(b + 12, 0.12, 1.0), t0 + j * 0.25, gain=0.2 - 0.03 * (j % 2), send=0.1)
place(piano(47, 0.4, 1.0) + piano(48, 0.4, 0.8) + piano(53, 0.4, 0.7), 10.6, gain=0.22, send=0.3)  # flip accent
place(boom(58, 1.4, 1.0), 11.15, gain=0.32, send=0.2)  # table crash
place(noise_band(0.5, 900, 300, 1.2, "burst"), 11.13, gain=0.18, send=0.3)
coin_notes = [86, 88, 90, 93, 95, 98, 100]
r2 = np.random.default_rng(5)
for i in range(26):  # spill
    place(ping(int(r2.choice(coin_notes)), 0.13, 0.04), 10.78 + i * 0.03 + r2.uniform(0, 0.08), pan=r2.uniform(-0.8, 0.8), gain=1.0, send=0.25)
for i in range(18):  # landing bounces
    place(ping(int(r2.choice(coin_notes)) - 12, 0.08, 0.03), 11.35 + r2.uniform(0, 0.8), pan=r2.uniform(-0.9, 0.9), gain=1.0, send=0.2)
place(noise_band(0.9, 1800, 3500, 0.5, "burst"), 11.0, pan=0.4, gain=0.05, send=0.3)  # dove wings
whoosh(13.4, 14.25, 400, 6500, gain=0.3)
place(ping(98, 0.18, 0.4) + ping(93, 0.12, 0.4), 14.15, gain=1.0, send=0.5)

# ---------------- S3 · Last Supper (14.3 – 18.6) — intimate piano in G ----------------
t = 14.3
for k, (ch, b) in enumerate([([55, 59, 62], 43), ([52, 55, 59], 40), ([48, 52, 55], 36), ([50, 54, 57], 38)]):
    t0 = t + k * 1.08
    chordpad(ch, t0, 1.08, 0.045, attack=0.6, release=1.0, bright=1.6)
    place(piano(b, 1.0, 0.7), t0, pan=-0.2, gain=0.22, send=0.3)
    place(piano(ch[1] + 12, 0.5, 0.45) + piano(ch[2] + 12, 0.5, 0.4), t0 + 0.54, pan=0.1, gain=0.18, send=0.3)
mel = [(79, 0.54), (78, 0.54), (76, 1.08), (74, 0.54), (76, 0.54), (79, 0.8)]
tm = t + 0.27
for m, d in mel:
    place(piano(m + 12, d, 0.7), tm, pan=0.2, gain=0.17, send=0.45)
    tm += d
place(noise_band(0.25, 2500, 1500, 0.8, "burst"), 15.4, gain=0.05, send=0.2)  # bread breaks
whoosh(17.7, 18.62, 500, 7000, gain=0.26)

# ---------------- S4 · Gethsemane (18.6 – 23.0) — minor strings ----------------
t = 18.55
for k, (ch, b) in enumerate([([52, 55, 59], 40), ([48, 52, 55], 36), ([45, 48, 52], 33), ([47, 51, 54], 35)]):
    t0 = t + k * 1.1
    chordpad(ch, t0, 1.1, 0.075, attack=0.8, release=1.3, bright=2.2, vib=0.003)
    place(bass(b, 1.05, 0.8), t0, gain=0.17, send=0.2)
for i, m in enumerate([83, 81, 79, 78, 76, 74]):
    place(piano(m, 0.7, 0.55), 19.0 + i * 0.66, pan=0.25, gain=0.15, send=0.55)
for d in [0, 0.5, 1.0, 1.5, 2.0]:  # drops land
    place(ping(91, 0.07, 0.02) + ping(79, 0.05, 0.02), 20.7 + d, pan=0.35, gain=1.0, send=0.6)
place(noise_band(1.0, 120, 60, 0.8, "swell"), 22.3, gain=0.12, send=0.4)

# ---------------- S5 · the Cross (23.0 – 28.3) — low drone, bell ----------------
t = 23.0
chordpad([28, 35, 40], t, 3.9, 0.09, attack=1.4, release=1.0, bright=3.0)
for k, (ch, b) in enumerate([([52, 55, 59], 28), ([48, 52, 55], 24), ([45, 48, 52], 33), ([47, 51, 54, 57], 35)]):
    t0 = t + 0.4 + k * 1.15
    chordpad(ch, t0, 1.15, 0.06, attack=0.7, release=1.2, bright=2.0, vib=0.004)
    place(bass(b, 1.1, 0.8), t0, gain=0.15, send=0.2)
place(bell(64, 1.0), 24.85, pan=0.0, gain=0.24, send=0.5)
place(bell(64, 0.7), 26.25, pan=-0.1, gain=0.15, send=0.6)
for i, (m, d) in enumerate([(76, 1.0), (74, 0.6), (72, 0.6), (71, 1.6)]):
    place(piano(m, d, 0.5), 25.2 + sum(x[1] for x in [(76, 1.0), (74, 0.6), (72, 0.6), (71, 1.6)][:i]), pan=0.2, gain=0.13, send=0.55)

# ---------------- S6 · Saturday (28.3 – 31.4) — near silence, a crack of light ----------------
chordpad([76, 83], 28.2, 2.4, 0.03, attack=1.2, release=1.0, bright=1.0)
place(box(88, 0.6, 0.6), 28.9, pan=-0.4, gain=0.12, send=0.7)
place(box(86, 0.6, 0.5), 29.6, pan=0.4, gain=0.1, send=0.7)
place(noise_band(1.6, 600, 9000, 0.4, "swell"), 29.9, gain=0.12, send=0.6)  # light seeps
whoosh(30.6, 31.62, 250, 8000, gain=0.3)

# ---------------- S7 · Resurrection (31.6 – 36.4) — full D major swell ----------------
t = 31.6
place(boom(37, 2.6, 1.0), t, gain=0.4, send=0.35)
place(noise_band(2.4, 6000, 9000, 1.0, "burst"), t, gain=0.12, send=0.5)  # cymbal bloom
prog = [([62, 66, 69, 74], 38), ([55, 59, 62, 67], 43), ([57, 61, 64, 69], 45), ([62, 66, 69, 74, 78], 50)]
for k, (ch, b) in enumerate(prog):
    t0 = t + k * 1.0
    d = 1.0 if k < 3 else 2.2
    chordpad(ch, t0, d, 0.085, attack=0.25, release=1.2, bright=3.0, vib=0.003)
    place(bass(b, d, 1.0), t0, gain=0.24, send=0.15)
    for j in range(8):
        m = ch[j % len(ch)] + 12 + 12 * (j // len(ch))
        place(box(m, 0.12, 0.7), t0 + j * 0.125, pan=-0.5 + j * 0.14, gain=0.14, send=0.4)
mel = [(81, 1.0), (86, 1.0), (85, 0.5), (88, 0.5), (86, 2.0)]
tm = t
for m, d in mel:
    place(piano(m, d, 1.0) + 0.5 * piano(m - 12, d, 1.0), tm, pan=0.1, gain=0.22, send=0.4)
    tm += d
for i in range(5):  # lilies bloom
    place(ping(93 + (i % 3) * 2, 0.1, 0.05), 33.0 + i * 0.12, pan=-0.6 + 0.3 * i, gain=1.0, send=0.5)
place(noise_band(0.9, 1500, 9000, 0.6, "swell"), 35.6, gain=0.16, send=0.6)  # light floods

# ---------------- S8 · lamb again (36.3 – 40) — theme returns, resolves ----------------
for i, (m, d) in enumerate([(74, 0.35), (78, 0.35), (81, 0.7), (79, 0.35), (78, 0.35), (76, 0.7)]):
    place(box(m, d, 0.85), 36.4 + sum(x for _, x in [(74, 0.35), (78, 0.35), (81, 0.7), (79, 0.35), (78, 0.35), (76, 0.7)][:i]), pan=0.15, gain=0.3, send=0.4)
chordpad([62, 66, 69], 36.3, 1.4, 0.06, attack=0.5, release=0.8)
chordpad([55, 59, 62], 37.2, 0.8, 0.06, attack=0.3, release=0.8)
place(box(86, 2.0, 0.9) + box(81, 2.0, 0.6) + box(78, 2.0, 0.5) + box(74, 2.0, 0.5), 38.6, gain=0.26, send=0.5)
chordpad([50, 57, 62, 66, 69], 38.6, 1.2, 0.07, attack=0.2, release=0.9)
place(bass(38, 1.3, 0.9), 38.6, gain=0.2, send=0.2)
# hop "boing" + sparkles
n = int(0.32 * SR)
tt = np.arange(n) / SR
fb = 420 + 520 * np.sin(np.pi * np.clip(tt / 0.32, 0, 1))
place(0.5 * np.sin(2 * np.pi * np.cumsum(fb) / SR) * env(n, 0.005, 0.22, 0.1), 38.2, gain=0.18, send=0.2)
for i in range(4):
    place(ping(95 + 2 * i, 0.1, 0.05), 38.3 + i * 0.1, pan=-0.4 + 0.3 * i, gain=1.0, send=0.5)

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
