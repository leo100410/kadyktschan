"""Gable mosaics (photo 6480317815 / briefing R3): a figure in a white fur coat and a leaping reindeer.

Shapes are authored in viewer coordinates (x to the right as seen from outside, y up, metres) and
built only from convex pieces (ellipses, strips, one trapezoid) so they need no triangulation.
Stylised re-creation, not a copy of the photo (art bible 1: the photos are reference only).
"""
import math


def ellipse(cx, cy, rx, ry, rot=0.0, n=18):
    c, s = math.cos(math.radians(rot)), math.sin(math.radians(rot))
    return [(cx + rx * math.cos(t) * c - ry * math.sin(t) * s, cy + rx * math.cos(t) * s + ry * math.sin(t) * c)
            for t in (2 * math.pi * k / n for k in range(n))]


def strip(x0, y0, x1, y1, w):
    dx, dy = x1 - x0, y1 - y0
    l = math.hypot(dx, dy) or 1.0
    nx, ny = -dy / l * w / 2, dx / l * w / 2
    return [(x0 + nx, y0 + ny), (x0 - nx, y0 - ny), (x1 - nx, y1 - ny), (x1 + nx, y1 + ny)]


def reindeer():
    """Leaping reindeer facing left; (polygon, slot, layer) with layer 0 base, 1 details on top."""
    red, brown = "Mural_Red", "Mural_Brown"
    out = [(ellipse(0, 0, 1.6, 0.75, -10), red, 0), (strip(-1.2, 0.3, -1.9, 1.1, 0.6), red, 0),
           (ellipse(-2.2, 1.25, 0.45, 0.28, 20), red, 0), (ellipse(-2.6, 1.1, 0.2, 0.15), red, 0),
           (strip(1.55, 0.25, 1.9, 0.5, 0.15), red, 0)]
    for seg in ((-2.0, 1.45, -1.5, 2.6, 0.12), (-1.5, 2.6, -0.8, 3.0, 0.1), (-1.7, 2.2, -2.3, 2.7, 0.1),
                (-2.1, 1.5, -2.8, 2.3, 0.12), (-2.8, 2.3, -3.2, 2.9, 0.1), (-1.6, 2.95, -1.2, 3.4, 0.08)):
        out.append((strip(*seg), brown, 0))  # antlers
    for seg in ((-1.1, -0.4, -2.3, -1.2, 0.22), (-2.3, -1.2, -2.9, -1.0, 0.16), (-0.9, -0.5, -1.8, -1.6, 0.2),
                (-1.8, -1.6, -2.2, -1.9, 0.15), (1.2, -0.3, 2.4, -1.0, 0.25), (2.4, -1.0, 3.2, -0.8, 0.16),
                (1.0, -0.5, 1.9, -1.5, 0.22), (1.9, -1.5, 2.6, -1.8, 0.15)):
        out.append((strip(*seg), red, 0))  # legs
    for cx, cy, r in ((-0.6, 0.15, 0.18), (0.1, 0.3, 0.2), (0.7, 0.05, 0.16), (-0.1, -0.25, 0.15), (0.9, -0.3, 0.12)):
        out.append((ellipse(cx, cy, r, r * 0.8), brown, 1))  # ornament spots
    return out


def figure():
    """Figure in a white fur coat (malitsa-like) with red trims, arm stretched out, facing the reindeer."""
    white, red, skin = "Mural_White", "Mural_Red", "Mural_Skin"
    out = [(ellipse(0, 1.75, 0.45, 0.5), white, 0), ([(-0.75, 1.2), (0.75, 1.2), (1.0, -0.9), (-1.0, -0.9)], white, 0),
           (strip(0.6, 1.0, 1.7, 0.9, 0.35), white, 0), (strip(-0.6, 1.0, -1.2, 0.2, 0.33), white, 0),
           (ellipse(1.95, 0.9, 0.2, 0.15), white, 0), (strip(-0.35, -0.9, -0.6, -1.9, 0.35), white, 0),
           (strip(0.35, -0.9, 0.5, -1.9, 0.35), white, 0),
           (ellipse(0, 1.7, 0.25, 0.3), skin, 1), (strip(-1.0, -0.82, 1.0, -0.82, 0.16), red, 1),
           (strip(-0.72, 1.22, 0.72, 1.22, 0.12), red, 1), (strip(1.55, 0.72, 1.6, 1.08, 0.1), red, 1),
           (strip(-1.22, 0.36, -1.0, 0.1, 0.1), red, 1), (ellipse(-0.7, -2.0, 0.35, 0.15), red, 0),
           (ellipse(0.6, -2.0, 0.35, 0.15), red, 0)]
    for k in range(5):  # ornament dots on the coat
        out.append((ellipse(-0.5 + k * 0.25, 0.2 - (k % 2) * 0.25, 0.07, 0.07), red, 1))
    return out


MURALS = {"reindeer_and_figure": [(figure, 3.0, 18.0, 1.25), (reindeer, 8.6, 20.5, 1.0)]}  # (shapes, x, y, scale) on a 12 m gable


def family():
    """Wall silhouettes of children and parents holding hands, one red balloon (user photo 2026-11-07, Kadykchan
    club). Generic figures in the spirit of that street art, not a copy of it."""
    dark, red = "Stencil", "Mural_Red"
    out = []
    for x, h in ((0.0, 1.05), (0.8, 1.25), (1.6, 1.2), (2.5, 1.75), (3.3, 1.65), (4.2, 1.0)):
        out += [(ellipse(x, h - 0.12, 0.11 * h / 1.2, 0.13 * h / 1.2), dark, 0),         # head
                (strip(x, h - 0.27, x, h * 0.45, 0.26 * h / 1.2), dark, 0),               # body
                (strip(x - 0.06, h * 0.47, x - 0.1, 0.0, 0.07), dark, 0),                 # legs
                (strip(x + 0.06, h * 0.47, x + 0.1, 0.0, 0.07), dark, 0)]
        if x < 4.0:
            out.append((strip(x + 0.1, h * 0.62, x + 0.7, h * 0.6, 0.05), dark, 0))      # hand in hand
    out += [(strip(4.3, 0.75, 4.55, 1.55, 0.02), dark, 1), (ellipse(4.6, 1.75, 0.16, 0.2), red, 1)]  # balloon
    return out
