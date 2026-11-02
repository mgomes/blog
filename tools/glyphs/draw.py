# /// script
# requires-python = ">=3.11"
# dependencies = ["shapely"]
# ///
"""Draw the glyph library into static/glyphs.svg, one <symbol> per glyph.

`just glyphs` runs it. The glyphs are the art on notes: chunky one-color
pictograms in the spirit of the Love, Death & Robots title cards, three to an
entry. Each is built from circles, boxes and polygons with shapely booleans
on a 32-unit grid, so a cut-out (an eye socket, a window) is a real hole and
every symbol is a single filled path that takes currentColor.

Pass --sheet <file.html> to also write a contact sheet for reviewing them.
"""

import math
import pathlib
import re
import sys

from shapely import affinity
from shapely.geometry import LineString, MultiPolygon, Point, Polygon, box
from shapely.ops import unary_union

ROOT = pathlib.Path(__file__).resolve().parents[2]
OUT = ROOT / "static" / "glyphs.svg"


# PRIMITIVES

def C(cx, cy, r):
    return Point(cx, cy).buffer(r, quad_segs=24)


def E(cx, cy, rx, ry, rot=0):
    e = affinity.scale(Point(0, 0).buffer(1, quad_segs=32), rx, ry)
    return affinity.translate(affinity.rotate(e, rot, origin=(0, 0)), cx, cy)


def R(x, y, w, h, r=0):
    if not r:
        return box(x, y, x + w, y + h)
    return box(x + r, y + r, x + w - r, y + h - r).buffer(r, quad_segs=8)


def P(*pts):
    return Polygon(pts)


def L(x1, y1, x2, y2, w):
    return LineString([(x1, y1), (x2, y2)]).buffer(w / 2, cap_style="flat")


def ring(cx, cy, r, w):
    return C(cx, cy, r) - C(cx, cy, r - w)


def rot(g, deg, cx=16, cy=16):
    return affinity.rotate(g, deg, origin=(cx, cy))


def path(d):
    """A filled outline from absolute M/L/C/Z commands, curves sampled."""
    toks = re.findall(r"[MLCZ]|-?\d*\.?\d+", d)
    pts, i, cur = [], 0, None
    while i < len(toks):
        cmd = toks[i]
        i += 1
        if cmd in "ML":
            cur = (float(toks[i]), float(toks[i + 1]))
            pts.append(cur)
            i += 2
        elif cmd == "C":
            p1, p2, p3 = [(float(toks[i + k]), float(toks[i + k + 1])) for k in (0, 2, 4)]
            for s in range(1, 17):
                t = s / 16
                u = 1 - t
                pts.append((
                    u**3 * cur[0] + 3 * u * u * t * p1[0] + 3 * u * t * t * p2[0] + t**3 * p3[0],
                    u**3 * cur[1] + 3 * u * u * t * p1[1] + 3 * u * t * t * p2[1] + t**3 * p3[1],
                ))
            cur = p3
            i += 6
        elif cmd == "Z":
            pass
    return Polygon(pts).buffer(0)


def U(*gs):
    return unary_union(gs)


def star(cx, cy, ro, ri, n=5, start=-90):
    pts = []
    for k in range(n * 2):
        r = ro if k % 2 == 0 else ri
        a = math.radians(start + k * 180 / n)
        pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return Polygon(pts)


# THE LIBRARY. Keep shapes chunky: details under ~1.5 units vanish when the
# glyph prints at 20px on a card.

def heart():
    return U(C(10.5, 11.5, 6.6), C(21.5, 11.5, 6.6), P((4.3, 14.2), (16, 27.5), (27.7, 14.2), (16, 9)))


def skull():
    head = U(C(16, 14, 12), R(9, 19, 14, 10, 2))
    return head - U(
        C(11, 15, 3.4), C(21, 15, 3.4), P((16, 18.6), (14, 22.2), (18, 22.2)),
        R(12.9, 25, 1.6, 4.5), R(17.5, 25, 1.6, 4.5),
    )


def robot():
    head = R(6, 9, 20, 16, 3) - U(C(11.5, 16, 2.7), C(20.5, 16, 2.7), R(11, 20.6, 10, 2, 1))
    return U(head, R(15, 4.5, 2, 5), C(16, 4.2, 2.4), R(3, 13, 3, 8, 1), R(26, 13, 3, 8, 1))


def x():
    return U(L(7, 7, 25, 25, 5.5), L(25, 7, 7, 25, 5.5))


def rocket():
    body = path("M16 2 C21 6 23 11 23 18 L23 23 L9 23 L9 18 C9 11 11 6 16 2 Z") - C(16, 12, 3)
    fins = U(P((9, 16), (3.5, 22), (3.5, 27), (9, 23.5)), P((23, 16), (28.5, 22), (28.5, 27), (23, 23.5)))
    return U(body, fins, P((12.5, 24.8), (19.5, 24.8), (16, 31)))


def planet():
    band = rot(E(16, 16, 15.5, 5.6) - E(16, 16, 12.6, 3.2), -20)
    return U(C(16, 16, 9.6) - band.buffer(1.1), band)


def starg():
    return star(16, 17, 13.5, 5.6)


def moon():
    return C(15, 16, 12.5) - C(21.5, 11.5, 10)


def sun():
    rays = [rot(R(14.6, 1.5, 2.8, 6, 1.2), a) for a in range(0, 360, 45)]
    return U(C(16, 16, 6.5), *rays)


def eye():
    almond = path("M2 16 C7 7.5 25 7.5 30 16 C25 24.5 7 24.5 2 16 Z")
    return U(almond - C(16, 16, 6), C(16, 16, 3.6))


def book():
    left = P((2.5, 7), (15, 9.5), (15, 27), (2.5, 24.5))
    right = P((29.5, 7), (17, 9.5), (17, 27), (29.5, 24.5))
    lines = U(
        P((5, 12), (12.5, 13.5), (12.5, 15.3), (5, 13.8)),
        P((5, 16.6), (12.5, 18.1), (12.5, 19.9), (5, 18.4)),
        P((27, 12), (19.5, 13.5), (19.5, 15.3), (27, 13.8)),
        P((27, 16.6), (19.5, 18.1), (19.5, 19.9), (27, 18.4)),
    )
    return U(left, right) - lines


def reel():
    holes = [C(16 + 7.6 * math.cos(math.radians(a)), 16 + 7.6 * math.sin(math.radians(a)), 3.3)
             for a in range(-90, 270, 72)]
    return C(16, 16, 13.5) - U(C(16, 16, 2.2), *holes)


def tv():
    body = R(2.5, 9, 27, 19, 3) - U(R(5.5, 12, 17, 13, 2), C(26, 15.5, 1.5), C(26, 21, 1.5))
    return U(body, L(16, 9.5, 10, 2.5, 2), L(16, 9.5, 22, 2.5, 2))


def note():
    return U(
        rot(E(9, 24.5, 4.4, 3.2), -20, 9, 24.5), rot(E(23, 21.5, 4.4, 3.2), -20, 23, 21.5),
        R(11.2, 7, 2.4, 17.5), R(25.2, 4, 2.4, 17.5),
        P((11.2, 6.5), (27.6, 3.2), (27.6, 8.4), (11.2, 11.7)),
    )


def wave():
    return path(
        "M2 27 C6.5 27 8 23 9.5 19 C12 12 16.5 6 23 6 C27.5 6 30.5 9 30.5 13 "
        "C30.5 16.5 27.5 18.5 25 17.5 C27 15.5 26 12.5 23 12.5 C19 12.5 17.5 17 17.5 21 "
        "C17.5 24 19.5 26 23 26 L30 26 L30 30 L2 30 Z"
    )


def mountain():
    m = P((1, 27), (11.5, 8), (17.5, 18.5), (21.5, 13), (31, 27))
    cap = P((11.5, 8), (8, 14.4), (10.4, 13), (12, 15.5), (14.2, 13), (15.6, 15.2))
    return m - cap


def tree():
    return U(P((16, 2), (24.5, 12.5), (20.5, 12.5), (27, 21.5), (5, 21.5), (11.5, 12.5), (7.5, 12.5)),
             R(13.8, 21, 4.4, 8))


def fish():
    body = E(13.5, 16, 10.5, 7) - C(8.5, 14.3, 1.8)
    tail = P((21, 16), (30.5, 8.5), (28, 16), (30.5, 23.5))
    return U(body, tail) - L(16.5, 10, 16.5, 22, 1.6).intersection(E(13.5, 16, 9, 5.6))


def ghost():
    g = path("M5.5 29 L5.5 14 C5.5 7.5 10.5 3.5 16 3.5 C21.5 3.5 26.5 7.5 26.5 14 L26.5 29 "
             "L23 25.5 L19.5 29 L16 25.5 L12.5 29 L9 25.5 Z")
    return g - U(E(12.3, 14, 2.1, 3), E(19.7, 14, 2.1, 3))


def key():
    return U(C(9, 16, 7) - C(9, 16, 2.8), R(15, 14.4, 15, 3.4), R(22.5, 17.5, 3, 4.5), R(27, 17.5, 3, 3.5))


def bolt():
    return P((19, 1.5), (5.5, 18.5), (14, 18.5), (12, 30.5), (26.5, 13), (17.8, 13), (21, 1.5))


def flame():
    outer = path("M16 30 C9.5 30 6 25.5 6 20.5 C6 14 11 11 12 4.5 C15.5 6.8 17.2 10 17.2 13.2 "
                 "C18.8 12 19.8 10.3 19.8 8.2 C23.8 11.4 26 16 26 20.5 C26 25.5 22.5 30 16 30 Z")
    inner = path("M16 27.8 C13.2 27.8 11.6 25.8 11.6 23.4 C11.6 20 14.6 18.8 15.6 15.8 "
                 "C18.2 17.5 20.4 20.4 20.4 23.4 C20.4 25.8 18.8 27.8 16 27.8 Z")
    return outer - inner


def drop():
    d = path("M16 2.5 C16 2.5 6.5 13.5 6.5 20 C6.5 25.5 10.8 29.5 16 29.5 "
             "C21.2 29.5 25.5 25.5 25.5 20 C25.5 13.5 16 2.5 16 2.5 Z")
    shine = (C(16, 20, 6.2) - C(17.6, 18.4, 6.2)).intersection(E(13, 23, 4, 5))
    return d - shine


def crown():
    top = P((3.5, 24), (3.5, 8.5), (10, 16), (16, 5.5), (22, 16), (28.5, 8.5), (28.5, 24))
    return U(top - C(16, 18.5, 2.4), R(3.5, 25.5, 25, 3.5, 1))


def die():
    pips = [C(10, 10, 2.4), C(16, 16, 2.4), C(22, 22, 2.4), C(22, 10, 2.4), C(10, 22, 2.4)]
    return R(3.5, 3.5, 25, 25, 4.5) - U(*pips)


def chip():
    pins = []
    for o in (11, 15, 19):
        pins += [R(o, 3, 2, 5), R(o, 24, 2, 5), R(3, o, 5, 2), R(24, o, 5, 2)]
    return U(R(7.5, 7.5, 17, 17, 2.5) - R(12, 12, 8, 8, 1), *pins)


def atom():
    orbits = [rot(E(16, 16, 14, 5.4) - E(16, 16, 11.8, 3.4), a) for a in (0, 60, 120)]
    return U(*orbits, C(16, 16, 3))


def alien():
    head = path("M16 3 C23.5 3 28.5 8 28.5 14 C28.5 21 21.5 29.5 16 29.5 "
                "C10.5 29.5 3.5 21 3.5 14 C3.5 8 8.5 3 16 3 Z")
    return head - U(rot(E(10.5, 16, 4.6, 2.5), 32, 10.5, 16), rot(E(21.5, 16, 4.6, 2.5), -32, 21.5, 16))


def ufo():
    dome = E(16, 14.5, 6.5, 7).intersection(box(0, 0, 32, 14.5))
    saucer = E(16, 17.5, 14.5, 4.6) - U(C(8.5, 17.5, 1.4), C(16, 18.6, 1.4), C(23.5, 17.5, 1.4))
    beam = P((11.5, 23.5), (20.5, 23.5), (25, 31), (7, 31)) - U(R(0, 25.6, 32, 1.3), R(0, 28.4, 32, 1.3))
    return U(dome, saucer, beam)


def globe():
    g = C(16, 16, 13.5)
    cuts = U(R(2, 15, 28, 2), E(16, 16, 6.5, 14) - E(16, 16, 4.5, 14),
             L(2, 9.5, 30, 9.5, 1.6), L(2, 22.5, 30, 22.5, 1.6))
    return g - cuts


def clock():
    return U(ring(16, 16, 13.5, 3), R(14.7, 7.5, 2.6, 10, 1.3), R(14.7, 14.7, 8.3, 2.6, 1.3))


def bird():
    return path("M1.5 9 C7.5 7.5 12.5 10.5 16 15.5 C19.5 10.5 24.5 7.5 30.5 9 "
                "C26.5 12.5 21 17.5 16 27 C11 17.5 5.5 12.5 1.5 9 Z")


def cat():
    head = path("M5 3.5 L12.3 10 C14.8 9.2 17.2 9.2 19.7 10 L27 3.5 L27.4 15.5 "
                "C28.6 23.5 23.4 28.5 16 28.5 C8.6 28.5 3.4 23.5 4.6 15.5 Z")
    return head - U(E(11.5, 17.5, 1.9, 2.8), E(20.5, 17.5, 1.9, 2.8), P((14.3, 22), (17.7, 22), (16, 24)))


def flower():
    petals = [C(16 + 7 * math.cos(math.radians(a)), 14 + 7 * math.sin(math.radians(a)), 5)
              for a in range(-90, 270, 72)]
    head = U(*petals) - C(16, 14, 4.3)
    return U(head, C(16, 14, 2.6), R(15, 21, 2, 9))


def house():
    return U(P((16, 3), (30, 15), (26, 15), (26, 29), (6, 29), (6, 15), (2, 15)), R(21, 5, 3.5, 7)) \
        - U(R(13.5, 20, 5, 9), R(9, 16, 3.5, 3.5))


def ship():
    hull = P((2, 21), (30, 21), (25.5, 28), (6.5, 28))
    return U(hull, P((15, 3), (15, 18.5), (5, 18.5)), P((17, 6), (17, 18.5), (26, 18.5)))


def bomb():
    return U(C(14, 19, 10) - C(10, 15.5, 2.4), R(18.2, 6.5, 6, 5, 1.2),
             L(22, 7, 24.5, 4, 1.6), star(26.5, 3.5, 3.4, 1.2, n=4, start=0))


def leaf():
    blade = rot(E(16, 16, 13, 6.8), -45)
    return U(blade - L(7, 25, 23.5, 8.5, 1.6), L(3, 29, 9.5, 22.5, 2.2))


def mushroom():
    cap = E(16, 15, 14, 11).intersection(box(0, 0, 32, 15))
    cap = cap - U(C(10, 9.5, 2.4), C(19, 7, 1.8), C(23.5, 11.5, 2.2))
    return U(cap, R(11.5, 16.5, 9, 12.5, 3))


def cup():
    body = path("M4 11 L24 11 L24 21 C24 25.5 20.5 29 16 29 L12 29 C7.5 29 4 25.5 4 21 Z")
    handle = ring(24.5, 17, 5, 2.4) - box(0, 0, 24, 32)
    steam = U(L(10, 3, 10, 8.5, 1.8), L(14, 2, 14, 8.5, 1.8), L(18, 3, 18, 8.5, 1.8))
    return U(body, handle, steam)


def bulb():
    glass = U(C(16, 12, 9.5), P((10, 18), (22, 18), (20, 23), (12, 23)))
    filament = U(ring(16, 11, 3.2, 1.5), R(15.2, 13, 1.6, 9))
    return U(glass - filament, R(11.5, 24.2, 9, 2, 1), R(12.5, 27.2, 7, 2, 1))


def anchor():
    return U(ring(16, 6, 3.5, 2.2), R(14.7, 9, 2.6, 19), R(9, 12, 14, 2.6, 1.3),
             ring(16, 16, 12, 2.6).intersection(box(0, 18, 32, 32)),
             P((2.5, 20), (6.5, 16), (7.5, 21)), P((29.5, 20), (25.5, 16), (24.5, 21)))


def sword():
    blade = P((16, 1.5), (19, 5), (19, 21), (13, 21), (13, 5))
    return U(blade, R(8, 21, 16, 3, 1.5), R(14.5, 24, 3, 5), C(16, 29.5, 2.2))


def camera():
    body = U(R(2.5, 9, 27, 18, 3), R(10, 5.5, 8.5, 5, 1.5))
    return body - ring(16, 18, 6.8, 2.2) - C(25, 13, 1.4)


def headphones():
    band = ring(16, 17, 13, 3).intersection(box(0, 0, 32, 18))
    return U(band, R(3, 16, 7, 12, 2.5), R(22, 16, 7, 12, 2.5))


def popcorn():
    tub = P((7, 14), (25, 14), (22.5, 30), (9.5, 30))
    stripes = U(P((12, 14), (14.5, 14), (14.8, 30), (12.6, 30)), P((17.5, 14), (20, 14), (19.4, 30), (17.2, 30)))
    puffs = U(C(9.5, 12, 3.6), C(14, 8.5, 3.8), C(19, 9.5, 3.6), C(23, 12.5, 3.2), C(16, 13, 3))
    return U(tub - stripes, puffs - box(0, 13.3, 32, 32))


def helmet():
    shell = U(C(16, 15, 13), R(5, 22, 22, 7.5, 2.5))
    visor = R(8, 10, 16, 10, 5)
    return U(shell - visor - R(12.5, 25, 7, 2, 1), C(20.5, 13, 1.8))


def hand():
    palm = R(7, 14, 16, 15, 5)
    fingers = U(R(7, 6.5, 3.6, 12, 1.8), R(11.2, 3, 3.6, 14, 1.8), R(15.4, 3.5, 3.6, 14, 1.8),
                R(19.6, 6, 3.4, 12, 1.7), rot(R(22, 13, 3.6, 10, 1.8), 40, 23.8, 18))
    return U(palm, fingers)


def spiral():
    pts = []
    for k in range(0, 721, 6):
        t = math.radians(k)
        r = 1.2 + 11.5 * k / 720
        pts.append((16 + r * math.cos(t), 16 + r * math.sin(t)))
    return LineString(pts).buffer(1.6, cap_style="round")


def snake():
    pts = []
    for k in range(0, 101):
        t = k / 100
        pts.append((4 + 24 * t, 16 + 7 * math.sin(t * math.pi * 2.4)))
    body = LineString(pts).buffer(2.4, cap_style="round")
    return U(body, C(28.2, 14.5, 3.6)) - C(29, 13.5, 0.9)


def gem():
    stone = P((9, 4.5), (23, 4.5), (29.5, 12), (16, 29), (2.5, 12))
    facets = U(L(2, 12, 30, 12, 1.8), L(12.5, 12, 16, 26, 1.8), L(19.5, 12, 16, 26, 1.8),
               L(12.5, 12, 15.5, 4, 1.6), L(19.5, 12, 16.5, 4, 1.6))
    return stone - facets


def cactus():
    return U(R(13, 4, 6, 25, 3), R(5.5, 9, 4.5, 9, 2.25), R(5.5, 15, 9, 4.5, 2.25),
             R(22, 7, 4.5, 9, 2.25), R(17.5, 13, 9, 4.5, 2.25), R(9, 27.5, 14, 2.5, 1))


GLYPHS = {
    "heart": heart, "skull": skull, "robot": robot, "x": x,
    "rocket": rocket, "planet": planet, "star": starg, "moon": moon, "sun": sun,
    "eye": eye, "hand": hand, "book": book, "reel": reel, "tv": tv, "note": note,
    "popcorn": popcorn, "camera": camera, "headphones": headphones,
    "wave": wave, "mountain": mountain, "tree": tree, "fish": fish, "bird": bird,
    "cat": cat, "snake": snake, "flower": flower, "leaf": leaf, "mushroom": mushroom,
    "cactus": cactus, "ghost": ghost, "alien": alien, "ufo": ufo, "helmet": helmet,
    "key": key, "bolt": bolt, "flame": flame, "drop": drop, "crown": crown,
    "die": die, "chip": chip, "atom": atom, "globe": globe, "clock": clock,
    "house": house, "ship": ship, "anchor": anchor, "bomb": bomb, "sword": sword,
    "cup": cup, "bulb": bulb, "spiral": spiral, "gem": gem,
}


def to_d(g):
    polys = g.geoms if isinstance(g, MultiPolygon) else [g]
    out = []
    for p in polys:
        p = p.simplify(0.04)
        for ringc in [p.exterior, *p.interiors]:
            xs = list(ringc.coords)[:-1]
            out.append("M" + "L".join(f"{fmt(a)} {fmt(b)}" for a, b in xs) + "Z")
    return "".join(out)


def fmt(v):
    s = f"{v:.2f}".rstrip("0").rstrip(".")
    return "0" if s in ("-0", "") else s


def main():
    symbols = []
    for name, fn in GLYPHS.items():
        g = fn()
        if g.is_empty or not g.is_valid:
            sys.exit(f"glyph {name} is empty or invalid")
        symbols.append(f'<symbol id="{name}" viewBox="0 0 32 32"><path fill-rule="evenodd" d="{to_d(g)}"/></symbol>')
    OUT.write_text(
        "<!-- GENERATED by `just glyphs` (tools/glyphs/draw.py). Do not edit by hand. -->\n"
        '<svg xmlns="http://www.w3.org/2000/svg">\n' + "\n".join(symbols) + "\n</svg>\n"
    )
    print(f"{len(symbols)} glyphs -> {OUT.relative_to(ROOT)}")

    if "--sheet" in sys.argv:
        sheet = pathlib.Path(sys.argv[sys.argv.index("--sheet") + 1])
        cells = "".join(
            f'<figure><svg viewBox="0 0 32 32"><path fill-rule="evenodd" d="{to_d(GLYPHS[n]())}"/></svg>'
            f"<figcaption>{n}</figcaption></figure>" for n in GLYPHS
        )
        sheet.write_text(
            "<style>body{margin:0;padding:16px;background:#ff4127;font:12px monospace;display:flex;flex-wrap:wrap;gap:12px}"
            "figure{margin:0;width:96px;text-align:center}svg{width:72px;height:72px;fill:#141517}"
            ".s svg{width:22px;height:22px}</style>" + cells + '<div style="width:100%"></div>'
            + cells.replace("<figure>", '<figure class="s">')
        )


if __name__ == "__main__":
    main()
