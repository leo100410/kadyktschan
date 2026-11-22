"""Shooter mode sounds, synthesised like gen_audio.py (no recordings): shots near and far, impacts, turret spin-up,
the tracked drone's motor loop and the camcorder's own hit glitch.

Usage: python -I shooter_audio.py <out dir>     (needs numpy; 48 kHz 16-bit mono WAV)
"""
import os
import sys
import numpy as np
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from gen_audio import SR, one_pole_lowpass, resonator, seamless, write

rng = np.random.default_rng(2011)


def env(n, attack, decay):
    t = np.arange(n) / SR
    return np.minimum(1.0, t / max(attack, 1e-4)) * np.exp(-t / decay)


def soft_clip(x, drive=2.5):
    """Loudness without harsh digital clipping: the report stays punchy at full volume."""
    return np.tanh(x * drive) / np.tanh(drive)


def echoes(x, delays, gains, cutoff):
    """Slapback off the panel blocks: delayed, darker copies."""
    out = x.copy()
    dark = one_pole_lowpass(x, cutoff)
    for d, g in zip(delays, gains):
        n = int(d * SR)
        out[n:] += dark[:-n] * g
    return out


def shot(dur=1.6):
    """Rifle report (user 2026-11-11: louder, better): supersonic crack, muzzle blast, low boom, bolt clack and
    the echo off the five-storey blocks."""
    n = int(dur * SR)
    t = np.arange(n) / SR
    noise = rng.standard_normal(n)
    crack = np.diff(noise, prepend=0) * env(n, 0.0002, 0.003) * 1.4               # bright, very short
    blast = resonator(noise * env(n, 0.0005, 0.03), 1400, 0.9) * 3.0              # mid-band blast
    boom = np.sin(2 * np.pi * np.cumsum(45 + 140 * np.exp(-t * 30)) / SR) * env(n, 0.001, 0.12) * 1.1
    clack = np.zeros(n)
    i = int(0.035 * SR)
    m = int(0.03 * SR)
    clack[i:i + m] = np.sin(2 * np.pi * 2400 * t[:m]) * np.exp(-t[:m] * 180) * 0.25
    dry = crack + blast + boom + clack
    tail = one_pole_lowpass(noise, 1200) * env(n, 0.02, 0.45) * 0.35               # diffuse street reverb
    wet = echoes(dry, (0.07, 0.15, 0.24, 0.41), (0.45, 0.32, 0.22, 0.14), 2200)
    return soft_clip(wet + tail)


def far_shot():
    """The same gun 40-80 m away: the crack and boom arrive dull, the echo rolls longer between the blocks."""
    x = one_pole_lowpass(shot(2.4), 650) * 1.6
    x = echoes(x, (0.12, 0.27, 0.45, 0.7), (0.5, 0.35, 0.25, 0.15), 500)
    return soft_clip(x, 1.8)


def impact():
    """Bullet into concrete or sheet metal: a click with a short metallic ring."""
    n = int(0.35 * SR)
    t = np.arange(n) / SR
    click = rng.standard_normal(n) * env(n, 0.0003, 0.006)
    ring = sum(np.sin(2 * np.pi * f * t) * np.exp(-t * d) for f, d in ((1850, 30), (2930, 40), (4400, 55))) * 0.25
    return click + ring


def spin_up():
    """Turret warning: a servo whine rising over 1.5 s, then relay clicks."""
    n = int(1.8 * SR)
    t = np.arange(n) / SR
    f = 220 + 620 * np.minimum(1, t / 1.5) ** 1.5
    whine = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.35 + np.sin(4 * np.pi * np.cumsum(f) / SR) * 0.12
    clicks = np.zeros(n)
    for c in (1.52, 1.6, 1.66):
        i = int(c * SR)
        clicks[i:i + 400] += rng.standard_normal(400) * np.exp(-np.arange(400) / 60)
    return whine * np.minimum(1, t / 0.1) + clicks * 0.8


def motor_loop(seconds=6):
    """Tracked crawler: electric motor hum, gear whine and track rattle, seamless."""
    n = int(seconds * SR)
    t = np.arange(n) / SR
    hum = np.sin(2 * np.pi * 110 * t) * 0.3 + np.sin(2 * np.pi * 330 * t) * 0.12
    whine = resonator(rng.standard_normal(n) * 0.3, 1450, 30) * 2.0
    rattle_src = (np.sin(2 * np.pi * 14 * t) > 0.6) * rng.standard_normal(n)
    rattle = one_pole_lowpass(rattle_src, 2500) * 0.5
    return seamless(hum + whine + rattle, 0.5)


def glitch():
    """The camcorder's own reaction to a hit: tape dropout buzz (heard instead of a pain sound)."""
    n = int(0.45 * SR)
    t = np.arange(n) / SR
    buzz = np.sign(np.sin(2 * np.pi * 60 * t)) * 0.3 + rng.standard_normal(n) * 0.5
    gate = (np.sin(2 * np.pi * 23 * t) > -0.2).astype(float)
    return one_pole_lowpass(buzz * gate, 3500) * env(n, 0.002, 0.18)


def click():
    """Empty magazine / reload clack."""
    n = int(0.25 * SR)
    t = np.arange(n) / SR
    return (rng.standard_normal(n) * env(n, 0.0002, 0.004) + np.sin(2 * np.pi * 2400 * t) * np.exp(-t * 60) * 0.3)


if __name__ == '__main__':
    out = sys.argv[1]
    os.makedirs(out, exist_ok=True)
    for name, x, peak in (('A_Shot', shot(), 0.95), ('A_ShotFar', far_shot(), 0.8), ('A_Impact', impact(), 0.6),
                          ('A_TurretSpin', spin_up(), 0.6), ('A_DroneMotor_Loop', motor_loop(), 0.5),
                          ('A_CamGlitch', glitch(), 0.7), ('A_Click', click(), 0.6)):
        write(os.path.join(out, name + '.wav'), x, peak)
    print('SHOOTER AUDIO OK')
