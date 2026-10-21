"""Original score + sound design for "David and Goliath" (40s), synthesized with numpy.

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


# ---------------- S0 · a stone on paper (0 – 5.4) — shepherd's flute ----------------
seq([(69, 0.4), (74, 0.4), (76, 0.4), (77, 0.8), (76, 0.4), (74, 0.4), (72, 0.4), (74, 1.0)], 0.4, flute, 0.2, pan=0.1, send=0.45)
chordpad([50, 57, 62], 0.3, 4.0, 0.045, attack=1.0, release=1.0, bright=1.5)
place(mix(boom(140, 0.25, 0.6), ping(62, 0.12, 0.03)), 1.1, gain=0.25, send=0.3)  # stone lands
whoosh(4.2, 5.4, 300, 2500, gain=0.28)

# ---------------- S1 · Goliath (5.4 – 10.4) — footsteps, dark brass ----------------
chordpad([26, 33, 38], 5.4, 4.0, 0.1, attack=0.6, release=0.8, bright=3.5)
brass([38, 45, 50], 5.6, 3.6, 0.05)
for i in range(4):  # the giant's steps
    place(boom(34, 1.6, 1.0), 6.1 + i * 0.8, gain=0.42, send=0.3)
    place(noise_band(0.4, 200, 120, 1.0, "burst"), 6.1 + i * 0.8, gain=0.12, send=0.2)
n = int(3.2 * SR)  # trembling strings (tremolo)
tt = np.arange(n) / SR
trem = pad([62, 65, 69], 3.2, attack=0.4, release=0.6, bright=2.5)
trem[: len(tt)] *= 0.55 + 0.45 * np.sin(2 * np.pi * 11 * tt)
place(trem, 6.2, gain=0.06, send=0.4)
whoosh(9.45, 10.4, 2500, 120, gain=0.3)

# ---------------- S2 · fear (10.4 – 15.2) — low tremolo, campfire, a light ----------------
for k, (ch, b) in enumerate([([50, 53, 57], 38), ([46, 50, 53], 34), ([43, 46, 50], 31)]):
    t0 = 10.45 + k * 0.95
    p = pad(ch, 0.95, attack=0.3, release=0.8, bright=2.0)
    tt = np.arange(len(p)) / SR
    place(p * (0.6 + 0.4 * np.sin(2 * np.pi * 9 * tt)), t0, gain=0.07, send=0.4)
    place(bass(b, 0.9, 0.7), t0, gain=0.15, send=0.2)
r2 = np.random.default_rng(3)
for i in range(16):  # fire crackle
    place(noise_band(0.05, 2500, 3500, 0.6, "burst"), 10.5 + r2.uniform(0, 4.5), pan=-0.1, gain=0.035, send=0.2)
chordpad([62, 66, 69, 74], 13.2, 1.8, 0.07, attack=0.8, release=1.0, bright=2.2)  # David arrives — hope
place(noise_band(1.6, 6000, 9000, 0.5, "swell"), 13.2, gain=0.05, send=0.6)
seq([(78, 0.5), (81, 0.5), (86, 1.0)], 13.4, flute, 0.18, pan=0.3, send=0.6)
place(noise_band(0.7, 1500, 9000, 0.6, "swell"), 14.6, gain=0.14, send=0.6)

# ---------------- S3 · the brook (15.2 – 20.4) — harp, water, five stones ----------------
place(noise_band(5.0, 1200, 2600, 1.2, "swell")[::-1] * 0.5 + noise_band(5.0, 1400, 3000, 1.2, "swell") * 0.5, 15.3, gain=0.05, send=0.3)
for k, (ch, b) in enumerate([([62, 66, 69], 38), ([55, 59, 62], 43), ([59, 62, 66], 47), ([57, 61, 64], 45)]):
    t0 = 15.3 + k * 1.15
    chordpad(ch, t0, 1.15, 0.045, attack=0.5, release=0.9, bright=1.8)
    place(bass(b, 1.1, 0.7), t0, gain=0.15, send=0.2)
    tones = sorted(ch) + [c + 12 for c in sorted(ch)]
    for j in range(6):
        place(box(tones[j] + 12, 0.18, 0.7), t0 + j * 0.19, pan=-0.5 + j * 0.2, gain=0.12, send=0.45)
for i in range(5):  # one, two, three, four, five
    place(mix(ping(81 + [0, 2, 4, 7, 9][i], 0.16, 0.06), ping(69 + [0, 2, 4, 7, 9][i], 0.08, 0.05)), 16.5 + i * 0.5 + 0.55, pan=-0.2, gain=1.0, send=0.5)
whoosh(19.9, 20.55, 300, 3200, gain=0.28, pan=-0.5)

# ---------------- S4 · face-off (20.4 – 25.7) — drums gather ----------------
chordpad([38, 45, 50], 20.4, 4.6, 0.08, attack=0.5, release=0.8, bright=3.0)
t, gap = 20.6, 0.6
while t < 25.6:
    drum(t, True, 0.9)
    drum(t + gap / 2, False, 0.8)
    t += gap
    gap = max(0.22, gap * 0.93)
seq([(50, 0.3), (50, 0.3), (53, 0.3), (50, 0.3), (55, 0.3), (53, 0.3), (52, 0.6)] * 2, 20.9, pluck, 0.18, pan=-0.2, send=0.25)
brass([38, 45, 50, 53], 22.0, 0.9, 0.09)  # spear raised
for i in range(12):  # snare roll as David runs
    place(noise_band(0.08, 2000, 4000, 0.8, "burst"), 24.2 + i * (0.12 - i * 0.004), gain=0.05 + i * 0.006, send=0.2)
whoosh(25.0, 25.75, 400, 6000, gain=0.3)

# ---------------- S5 · the sling (25.6 – 30.6) — whirl, release, impact ----------------
tw, per = 25.65, 0.6
while tw < 27.45:  # each whirl a little faster
    place(noise_band(per, 500, 1800, 0.5, "whoosh"), tw, pan=-0.3, gain=0.12, send=0.25)
    tw += per
    per = max(0.18, per * 0.78)
place(noise_band(0.5, 800, 6000, 0.5, "whoosh"), 27.48, pan=0.4, gain=0.3, send=0.3)  # release
place(boom(42, 2.6, 1.0), 27.97, gain=0.5, send=0.45)  # impact
place(noise_band(2.4, 5000, 8000, 1.0, "burst"), 27.97, gain=0.16, send=0.5)
place(bell(57, 1.0), 27.97, gain=0.18, send=0.6)
chordpad([62, 69, 74], 28.4, 1.6, 0.05, attack=0.6, release=1.0, bright=2.0)
place(noise_band(0.5, 1500, 9000, 0.6, "swell"), 30.15, gain=0.14, send=0.6)

# ---------------- S6 · the giant falls, victory (30.6 – 35.6) ----------------
n = int(1.0 * SR)
tt = np.arange(n) / SR
fall = np.sin(2 * np.pi * np.cumsum(120 * (1 - 0.6 * tt)) / SR) * env(n, 0.05, 0.8, 0.2)
place(fall, 30.95, gain=0.15, send=0.3)
place(boom(30, 2.2, 1.0), 31.9, gain=0.5, send=0.4)  # crash
place(noise_band(1.2, 400, 200, 1.0, "burst"), 31.9, gain=0.2, send=0.4)  # dust
for k, (ch, b) in enumerate([([62, 66, 69, 74], 38), ([55, 59, 62, 67], 43), ([57, 61, 64, 69], 45), ([62, 66, 69, 74, 78], 50)]):
    t0 = 32.3 + k * 0.75
    d = 0.75 if k < 3 else 1.6
    brass(ch, t0, d, 0.085)
    place(bass(b, d, 1.0), t0, gain=0.22, send=0.15)
    drum(t0, True, 1.0)
    drum(t0 + 0.375, False, 1.0)
for i in range(6):  # cheering claps
    place(noise_band(0.2, 1300, 1800, 0.9, "burst"), 32.6 + i * 0.375, pan=-0.4, gain=0.08, send=0.35)
seq([(74, 0.375), (78, 0.375), (81, 0.75), (78, 0.375), (81, 0.375), (86, 1.4)], 32.3, piano, 0.22, pan=0.15, send=0.35)
place(noise_band(0.6, 1500, 9000, 0.6, "swell"), 35.1, gain=0.14, send=0.6)

# ---------------- S7 · the golden stone (35.6 – 40) — flute theme in major ----------------
seq([(69, 0.4), (74, 0.4), (76, 0.4), (78, 0.8), (76, 0.4), (74, 1.4)], 35.9, flute, 0.2, pan=0.1, send=0.5)
chordpad([62, 66, 69], 35.7, 1.6, 0.05, attack=0.4, release=0.8)
place(box(86, 2.4, 0.9) + box(81, 2.4, 0.6) + box(78, 2.4, 0.5) + box(74, 2.4, 0.5), 37.6, gain=0.24, send=0.55)
chordpad([50, 57, 62, 66, 69], 37.6, 1.6, 0.065, attack=0.2, release=0.9)
place(bass(38, 1.8, 0.9), 37.6, gain=0.2, send=0.2)
for i in range(4):
    place(ping(95 + 2 * i, 0.1, 0.05), 37.2 + i * 0.1, pan=-0.4 + 0.3 * i, gain=1.0, send=0.5)


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
