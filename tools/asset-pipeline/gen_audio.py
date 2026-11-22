"""Procedural ambience (briefing V7 "Leise, kalt, weit"): wind through empty window frames and water drips.

Usage: python -I gen_audio.py <out dir>     (needs numpy; writes 48 kHz 16-bit WAV, seamless loops)
No recorded material is used. Distant dogs and radio static are left out on purpose: synthesised
versions sound worse than silence; they need recordings or MetaSounds later.
"""
import os, sys, wave
import numpy as np

SR = 48000
rng = np.random.default_rng(1996)


def one_pole_lowpass(x, cutoff):
    a = np.exp(-2 * np.pi * cutoff / SR)
    y = np.empty_like(x)
    acc = 0.0
    for i in range(0, len(x), 4096):  # block-wise python loop is fast enough for a minute of audio
        blk = x[i:i + 4096]
        out = np.empty_like(blk)
        for k, v in enumerate(blk):
            acc = (1 - a) * v + a * acc
            out[k] = acc
        y[i:i + 4096] = out
    return y


def resonator(x, freq, q):
    """Two-pole band-pass around freq (the whistle of air through a gap)."""
    w = 2 * np.pi * freq / SR
    r = np.exp(-w / (2 * q))
    b1, b2 = 2 * r * np.cos(w), -r * r
    y = np.zeros_like(x)
    y1 = y2 = 0.0
    for k, v in enumerate(x):
        y0 = (1 - r) * v + b1 * y1 + b2 * y2
        y[k] = y0
        y2, y1 = y1, y0
    return y


def seamless(x, fade):
    """Crossfade the tail into the head so the loop has no click."""
    n = int(fade * SR)
    ramp = np.linspace(0, 1, n)
    head = x[:n] * ramp + x[-n:] * (1 - ramp)
    return np.concatenate([head, x[n:-n]])


def write(path, x, peak=0.6):
    x = x / (np.abs(x).max() or 1) * peak
    with wave.open(path, "wb") as w:
        w.setnchannels(1)
        w.setsampwidth(2)
        w.setframerate(SR)
        w.writeframes((x * 32767).astype("<i2").tobytes())


def wind(seconds=62):
    n = seconds * SR
    noise = rng.standard_normal(n)
    body = one_pole_lowpass(noise, 380)                                   # broad low rush
    t = np.arange(n) / SR
    gust = 0.55 + 0.45 * np.sin(2 * np.pi * 0.045 * t + 1.3) * np.sin(2 * np.pi * 0.11 * t)
    gust = np.clip(gust, 0.08, 1.0)
    whistle_src = rng.standard_normal(n // 4)
    whistle = resonator(np.repeat(whistle_src, 4)[:n] * 0.5, 920, 60)      # empty-frame whistle
    whistle *= np.clip(np.sin(2 * np.pi * 0.07 * t - 0.4), 0, 1) ** 3
    return seamless(body * gust + whistle * 0.35 * gust, 2.0)


def drips(seconds=31):
    n = seconds * SR
    x = rng.standard_normal(n) * 0.004                                   # room tone
    t = 0.3
    while t < seconds - 0.5:
        i = int(t * SR)
        f0 = rng.uniform(1400, 2600)
        dur = 0.09
        k = np.arange(int(dur * SR)) / SR
        f = f0 * (1 + 0.6 * np.exp(-k * 60))                             # pitch drop of a falling drop
        burst = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-k * 45) * rng.uniform(0.3, 1.0)
        x[i:i + len(burst)] += burst
        t += rng.uniform(0.6, 3.2)
    return seamless(x, 0.5)


def creaks(seconds=47):
    """Unsettling but natural: wind working loose sheet metal and a hanging door - slow creaks, a distant clank.
    No voices, no stingers (briefing: no horror cliches)."""
    n = seconds * SR
    x = rng.standard_normal(n) * 0.002
    t = rng.uniform(1, 4)
    while t < seconds - 4:
        i, k = int(t * SR), rng.random()
        if k < 0.6:  # creak: friction noise through a slowly gliding resonance
            dur = rng.uniform(0.8, 2.2); m = int(dur * SR)
            tt = np.arange(m) / SR
            f = rng.uniform(180, 420) * (1 + 0.3 * np.sin(2 * np.pi * rng.uniform(0.3, 0.9) * tt))
            src = rng.standard_normal(m) * (0.5 + 0.5 * (np.sin(2 * np.pi * rng.uniform(18, 35) * tt) > 0.2))
            burst = np.sin(2 * np.pi * np.cumsum(f) / SR) * src * np.sin(np.pi * tt / dur) ** 2 * 0.25
        else:        # distant metal clank: a few inharmonic modes ringing out
            dur = 2.5; m = int(dur * SR); tt = np.arange(m) / SR
            burst = sum(np.sin(2 * np.pi * f0 * tt) * np.exp(-tt * dec) for f0, dec in ((310, 3), (757, 4.5), (1210, 6))) * 0.3
        x[i:i + m] += burst[:n - i]
        t += rng.uniform(5, 13)
    return seamless(x, 1.0)


if __name__ == "__main__":
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    write(os.path.join(out, "A_Wind_Loop.wav"), wind(), 0.5)
    write(os.path.join(out, "A_Drips_Loop.wav"), drips(), 0.7)
    write(os.path.join(out, "A_Creaks_Loop.wav"), creaks(), 0.6)
    print("AUDIO OK")
