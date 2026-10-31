"""Original penguin sprite-sheet generator (SVG -> PNG via Playwright/Chromium).
Each sheet = one animation = one state. Frames are 320x320 with 40px gaps, transparent bg.

Style: round chibi penguin, sitting, big head, heart-shaped white face, bean eyes with
little brows, light-blue beak, stubby flippers, yellow feet pointing forward, soft shadow.
Usage: python3 gen.py OUT && node render.js OUT && python3 assemble.py OUT
"""
import os, sys, json, math

OUT = sys.argv[1] if len(sys.argv) > 1 else "./out"
os.makedirs(OUT, exist_ok=True)

BODY, FACE, LINE, BEAK, FEET = "#7ec3ef", "#ffffff", "#1f2a3c", "#8fcdf3", "#ffe64a"
ACC, MOTION, SHADOW = "#f6c343", "#8fcdf3", "#c9d0d8"
LW = 3.4

# ---------- face parts ----------
def eyes(kind, dy=0):
    L, R, y = 46, 74, 58 + dy
    if kind in ("open", "focus", "sad"):
        s = f'<ellipse cx="{L}" cy="{y}" rx="3.6" ry="5.2" fill="{LINE}"/><ellipse cx="{R}" cy="{y}" rx="3.6" ry="5.2" fill="{LINE}"/>'
        s += f'<circle cx="{L+1.3}" cy="{y-2}" r="1.1" fill="#fff"/><circle cx="{R+1.3}" cy="{y-2}" r="1.1" fill="#fff"/>'
        if kind == "open":
            s += f'<path d="M{L-5} {y-10} q5 -3 10 0 M{R-5} {y-10} q5 -3 10 0" stroke="{LINE}" stroke-width="2.4" fill="none"/>'
        elif kind == "focus":
            s += f'<path d="M{L-6} {y-12} l12 3 M{R+6} {y-12} l-12 3" stroke="{LINE}" stroke-width="2.6" fill="none"/>'
        else:
            s += f'<path d="M{L-6} {y-9} l12 -3 M{R+6} {y-9} l-12 -3" stroke="{LINE}" stroke-width="2.4" fill="none"/>'
        return s
    if kind == "half":
        return (f'<path d="M{L-5} {y-3} q5 4 10 0 M{R-5} {y-3} q5 4 10 0" stroke="{LINE}" stroke-width="2.8" fill="none"/>'
                f'<ellipse cx="{L}" cy="{y+0.5}" rx="3.4" ry="2.2" fill="{LINE}"/><ellipse cx="{R}" cy="{y+0.5}" rx="3.4" ry="2.2" fill="{LINE}"/>')
    if kind == "sleep":   # closed, relaxed
        return f'<path d="M{L-5} {y} q5 4 10 0 M{R-5} {y} q5 4 10 0" stroke="{LINE}" stroke-width="3" fill="none"/>'
    if kind == "happy":   # closed, smiling arcs
        return f'<path d="M{L-5} {y+1} q5 -6 10 0 M{R-5} {y+1} q5 -6 10 0" stroke="{LINE}" stroke-width="3" fill="none"/>'
    if kind == "squint":  # > <
        return f'<path d="M{L-5} {y-4} l6 4 l-6 4 M{R+5} {y-4} l-6 4 l6 4" stroke="{LINE}" stroke-width="3" fill="none"/>'
    if kind == "wink":    # left open, right happy
        return (f'<ellipse cx="{L}" cy="{y}" rx="3.6" ry="5.2" fill="{LINE}"/><circle cx="{L+1.3}" cy="{y-2}" r="1.1" fill="#fff"/>'
                f'<path d="M{L-5} {y-10} q5 -3 10 0 M{R-5} {y+1} q5 -6 10 0" stroke="{LINE}" stroke-width="2.6" fill="none"/>')
    if kind == "wide":
        return (f'<circle cx="{L}" cy="{y}" r="5.6" fill="#fff" stroke="{LINE}" stroke-width="1.8"/><circle cx="{R}" cy="{y}" r="5.6" fill="#fff" stroke="{LINE}" stroke-width="1.8"/>'
                f'<circle cx="{L}" cy="{y}" r="2.8" fill="{LINE}"/><circle cx="{R}" cy="{y}" r="2.8" fill="{LINE}"/>'
                f'<path d="M{L-5} {y-11} q5 -3 10 0 M{R-5} {y-11} q5 -3 10 0" stroke="{LINE}" stroke-width="2.4" fill="none"/>')
    if kind == "heart":
        def h(cx): return (f'<path d="M{cx} {y+6} C {cx-7} {y}, {cx-8} {y-6}, {cx-3.5} {y-7.5} C {cx-1} {y-8}, {cx} {y-6}, {cx} {y-5} '
                           f'C {cx} {y-6}, {cx+1} {y-8}, {cx+3.5} {y-7.5} C {cx+8} {y-6}, {cx+7} {y}, {cx} {y+6} Z" fill="#ff6f8e" stroke="{LINE}" stroke-width="1.8"/>')
        return h(L) + h(R)
    if kind == "star":
        def s(cx):
            pts = []
            for i in range(10):
                r = 7 if i % 2 == 0 else 3
                a = -math.pi / 2 + i * math.pi / 5
                pts.append(f"{cx + r*math.cos(a):.1f},{y + r*math.sin(a):.1f}")
            return f'<polygon points="{" ".join(pts)}" fill="{ACC}" stroke="{LINE}" stroke-width="1.6"/>'
        return s(L) + s(R)
    return ""

def beak(kind="closed", dy=0):
    y = 67 + dy
    d = f'<path d="M51 {y-1} Q60 {y-7} 69 {y-1} Q60 {y+9} 51 {y-1} Z" fill="{BEAK}" stroke="{LINE}" stroke-width="2.6"/>'
    if kind == "closed":
        return d + f'<path d="M54 {y} Q60 {y+3} 66 {y}" stroke="{LINE}" stroke-width="1.8" fill="none"/>'
    if kind == "open":
        return d + f'<path d="M54 {y} Q60 {y+8} 66 {y} Z" fill="#e2557a" stroke="{LINE}" stroke-width="1.6"/>'
    if kind == "smile":
        return d + f'<path d="M53 {y-1} Q60 {y+4} 67 {y-1}" stroke="{LINE}" stroke-width="1.8" fill="none"/>'
    return d

# ---------- flippers ----------
# Angles use the LEFT flipper convention: 0 = hanging down, 90 = straight out, 135 = up-out,
# 180 = straight up, -75 = hand to chin (inward-up), -35 = resting on the belly.
def flipper(side, angle=0, length=26):
    if side == "l":
        px, py = 25, 76
        rot = angle
    else:
        px, py = 95, 76
        rot = -angle
    w = 13
    path = (f'<path d="M{px-w/2} {py} C {px-w/2-1} {py+length*0.55}, {px-w/2+1} {py+length}, {px} {py+length} '
            f'C {px+w/2-1} {py+length}, {px+w/2+1} {py+length*0.55}, {px+w/2} {py} Z" fill="{BODY}" stroke="{LINE}" stroke-width="{LW}"/>')
    return f'<g transform="rotate({rot} {px} {py})">{path}</g>'

# ---------- character ----------
def penguin(eye="open", mouth="closed", bob=0, squash=0.0, tilt=0, fl=0, fr=0, feet=True, shadow=True,
            belly=True, blink=False, extra_front="", extra_back=""):
    """Drawn in 120x120 user space; the character sits on the floor at y=106."""
    sy, sx = 1 - squash, 1 + squash * 0.8
    e = "sleep" if blink else eye
    parts = []
    if shadow:
        parts.append(f'<ellipse cx="60" cy="110" rx="{42 - bob*0.4:.1f}" ry="4.5" fill="{SHADOW}" opacity=".55"/>')
    parts.append(extra_back)
    body = f'''
<path d="M60 8 C 32 8, 15 28, 15 54 C 15 70, 20 80, 24 84 C 18 92, 26 106, 60 106 C 94 106, 102 92, 96 84 C 100 80, 105 70, 105 54 C 105 28, 88 8, 60 8 Z" fill="{BODY}" stroke="{LINE}" stroke-width="{LW}"/>
<path d="M60 46 C 55 36, 43 30, 35 36 C 25 44, 25 62, 31 74 C 37 86, 49 90, 60 90 C 71 90, 83 86, 89 74 C 95 62, 95 44, 85 36 C 77 30, 65 36, 60 46 Z" fill="{FACE}"/>'''
    if belly:
        body += f'<path d="M44 106 C 44 92, 76 92, 76 106 Z" fill="{FACE}"/>'
    body += eyes(e) + beak(mouth)
    fl_svg = flipper("l", fl) + flipper("r", fr)
    feet_svg = (f'<ellipse cx="41" cy="105" rx="13" ry="7.5" fill="{FEET}" stroke="{LINE}" stroke-width="2.8" transform="rotate(-12 41 105)"/>'
                f'<ellipse cx="79" cy="105" rx="13" ry="7.5" fill="{FEET}" stroke="{LINE}" stroke-width="2.8" transform="rotate(12 79 105)"/>') if feet else ""
    inner = body + feet_svg + fl_svg + extra_front
    parts.append(f'<g transform="translate(60 106) scale({sx:.3f} {sy:.3f}) translate(-60 -106) translate(0 {bob}) rotate({tilt} 60 100)">{inner}</g>')
    return "".join(parts)

def frame_svg(inner, bg_extra=""):
    return (f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -24 148 148" width="320" height="320">'
            f'<g stroke-linecap="round" stroke-linejoin="round">{bg_extra}{inner}</g></svg>')

# ---------- effects & props ----------
def rays(x, y, flip=False, size=8, color=ACC):
    """Three yellow strokes radiating up-right (or up-left if flip): the 'ひらめき' marks."""
    out = ""
    for a in (-70, -35, 0):
        rad = math.radians(a if not flip else 180 - a)
        x1, y1 = x + 4*math.cos(rad), y + 4*math.sin(rad)
        x2, y2 = x + (4+size)*math.cos(rad), y + (4+size)*math.sin(rad)
        out += f'<path d="M{x1:.1f} {y1:.1f} L{x2:.1f} {y2:.1f}" stroke="{color}" stroke-width="3.2" fill="none"/>'
    return out

def motion(x, y, flip=False, n=2, color=MOTION):
    """Blue double arcs = movement."""
    s = -1 if flip else 1
    out = ""
    for i in range(n):
        r = 10 + i * 6
        out += f'<path d="M{x} {y-r} q{-s*r*0.6} {r} 0 {2*r}" stroke="{color}" stroke-width="3" fill="none" opacity=".9"/>'
    return out

def sparkle(x, y, r=4, color=ACC):
    return (f'<path d="M{x} {y-r} L{x+r*0.3} {y-r*0.3} L{x+r} {y} L{x+r*0.3} {y+r*0.3} L{x} {y+r} L{x-r*0.3} {y+r*0.3} L{x-r} {y} L{x-r*0.3} {y-r*0.3} Z" '
            f'fill="{color}" stroke="{LINE}" stroke-width="1.4"/>')

def bulb(x=100, y=14, lit=True):
    g = f'<circle cx="{x}" cy="{y}" r="9" fill="{"#fff27a" if lit else "#eee"}" stroke="{LINE}" stroke-width="2.2"/>'
    g += f'<rect x="{x-4}" y="{y+8}" width="8" height="6" rx="1.5" fill="#bfc5cc" stroke="{LINE}" stroke-width="1.8"/>'
    g += f'<path d="M{x-2} {y+10} h4 M{x-2} {y+13} h4" stroke="{LINE}" stroke-width="1.2"/>'
    if lit:
        g += rays(x - 12, y - 10, flip=True, size=6) + rays(x + 12, y - 10, size=6)
    return g

def zz(phase):
    o = [0, -3, -6, -9, -6, -3][phase % 6]
    return (f'<g fill="{LINE}" font-weight="700" font-family="Arial,sans-serif">'
            f'<text x="96" y="{24+o}" font-size="15">z</text><text x="107" y="{12+o}" font-size="11">z</text>'
            f'<text x="115" y="{4+o}" font-size="8" opacity=".6">z</text></g>')

def mug(x=100, y=84, steam=0):
    st = "".join(f'<path d="M{x+4+i*5} {y-4-steam} q3 -4 0 -8 q-3 -4 0 -8" stroke="#9fb4c4" stroke-width="1.8" fill="none" opacity=".9"/>' for i in range(2))
    return (f'<g>{st}<rect x="{x}" y="{y}" width="15" height="18" rx="3.5" fill="#fff" stroke="{LINE}" stroke-width="2.4"/>'
            f'<path d="M{x+15} {y+4} q7 0 7 6 q0 6 -7 6" stroke="{LINE}" stroke-width="2.4" fill="none"/></g>')

def dumbbell(cx, cy, angle=0):
    return (f'<g transform="rotate({angle} {cx:.1f} {cy:.1f})">'
            f'<rect x="{cx-16:.1f}" y="{cy-2.5:.1f}" width="32" height="5" rx="2.5" fill="#9aa5b1" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="{cx-21:.1f}" y="{cy-8:.1f}" width="8" height="16" rx="2.5" fill="#5d6d7e" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="{cx+13:.1f}" y="{cy-8:.1f}" width="8" height="16" rx="2.5" fill="#5d6d7e" stroke="{LINE}" stroke-width="2"/></g>')

def sweat(phase, x=104, y=26):
    o = (phase % 3) * 2
    return (f'<g fill="{MOTION}" stroke="{LINE}" stroke-width="1.4">'
            f'<path d="M{x} {y+o} c-3 5 -3 8 0 8 c3 0 3 -3 0 -8z"/><path d="M{x+9} {y-8+o} c-2.5 4 -2.5 6.5 0 6.5 c2.5 0 2.5 -2.5 0 -6.5z"/></g>')

def headband():
    return f'<path d="M17 40 Q60 26 103 40 Q60 35 17 40 Z" fill="#ff7a7a" stroke="{LINE}" stroke-width="2.2"/>'

def desk():
    return f'<rect x="-12" y="96" width="144" height="16" rx="4" fill="#dbb88c" stroke="{LINE}" stroke-width="2.4"/>'

def laptop(dy=0, screen="#d6ecfb"):
    return (f'<g transform="translate(0 {dy})">'
            f'<rect x="33" y="74" width="54" height="22" rx="3" fill="#3b4a5c" stroke="{LINE}" stroke-width="2.4"/>'
            f'<rect x="37" y="78" width="46" height="14" rx="1.5" fill="{screen}"/>'
            f'<rect x="29" y="93" width="62" height="6" rx="2" fill="#aab4bf" stroke="{LINE}" stroke-width="2.4"/></g>')

def hands_on(xl, xr, y, dy=0):
    """Flipper tips seen from the front (e.g. on a keyboard)."""
    return (f'<ellipse cx="{xl}" cy="{y+dy}" rx="7.5" ry="4.5" fill="{BODY}" stroke="{LINE}" stroke-width="2.6"/>'
            f'<ellipse cx="{xr}" cy="{y-dy}" rx="7.5" ry="4.5" fill="{BODY}" stroke="{LINE}" stroke-width="2.6"/>')

def notepad(x=36, y=78, lines=2, w=40, h=26):
    g = f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="3" fill="#fff5de" stroke="{LINE}" stroke-width="2.4"/>'
    g += "".join(f'<circle cx="{x+6+i*7}" cy="{y}" r="1.6" fill="#fff" stroke="{LINE}" stroke-width="1.4"/>' for i in range(5))
    g += "".join(f'<path d="M{x+6} {y+9+i*6} h{w-14-i*8}" stroke="#b8c4d0" stroke-width="2"/>' for i in range(lines))
    return g

def pencil(x, y, angle=-35):
    return (f'<g transform="rotate({angle} {x} {y})">'
            f'<rect x="{x-3}" y="{y-26}" width="6" height="26" rx="1.5" fill="{ACC}" stroke="{LINE}" stroke-width="2"/>'
            f'<rect x="{x-3}" y="{y-26}" width="6" height="5" rx="1.5" fill="#f4a0a0" stroke="{LINE}" stroke-width="1.6"/>'
            f'<path d="M{x-3} {y} l6 0 l-3 7 z" fill="#f7d7b5" stroke="{LINE}" stroke-width="1.6"/></g>')

def pillow():
    return f'<rect x="6" y="90" width="108" height="20" rx="9" fill="#fff0f5" stroke="{LINE}" stroke-width="2.4"/>'

def blanket(bob=0):
    return (f'<path d="M10 {78+bob} Q60 {68+bob} 110 {78+bob} L113 110 L7 110 Z" fill="#bcd9ff" stroke="{LINE}" stroke-width="2.8"/>'
            f'<path d="M14 {87+bob} Q60 {79+bob} 106 {87+bob}" stroke="{LINE}" stroke-width="1.6" fill="none" opacity=".45"/>')

def moon():
    return f'<path d="M108 6 a9 9 0 1 0 8 12 a7 7 0 1 1 -8 -12z" fill="#ffe28a" stroke="{LINE}" stroke-width="1.8"/>'

def confetti(phase):
    import random
    rnd = random.Random(7)
    out = ""
    cols = ["#ff6f8e", ACC, BODY, "#9be28a", "#c69bff"]
    for i in range(12):
        x = rnd.uniform(-8, 128); y0 = rnd.uniform(-20, 40); rot = rnd.uniform(-40, 40)
        y = y0 + (phase % 6) * 6
        out += f'<rect x="{x:.1f}" y="{y:.1f}" width="4.5" height="8" rx="1.2" fill="{cols[i%5]}" transform="rotate({rot:.0f} {x:.1f} {y:.1f})" stroke="{LINE}" stroke-width="1.2"/>'
    return out

def notes(phase):
    o = (phase % 4) * 2
    return (f'<g fill="#3f9bdc" font-family="Arial,sans-serif" font-weight="700">'
            f'<text x="100" y="{24-o}" font-size="17">♪</text><text x="112" y="{12+o}" font-size="13">♫</text></g>')

def banner(text):
    return (f'<rect x="20" y="-19" width="80" height="21" rx="10.5" fill="#fff" stroke="{LINE}" stroke-width="2.4"/>'
            f'<text x="60" y="-3.5" text-anchor="middle" font-size="11.5" font-weight="700" font-family="Arial,sans-serif" fill="{LINE}">{text}</text>')

def floating_hearts(phase):
    hy = (phase % 6) * 4
    return "".join(f'<path d="M{x} {y-hy} c-5 -6 -11 1 0 9 c11 -8 5 -15 0 -9z" fill="#ff6f8e" stroke="{LINE}" stroke-width="1.6" opacity="{1 - hy/30:.2f}"/>'
                   for (x, y) in [(8, 34), (114, 26), (104, 52)])

# ---------- animations: name -> (state, frames fn) ----------
A = {}

def work_typing():
    fr = []
    for i in range(6):
        bob = [0, 1, 0, 1, 0, 1][i]
        eye = "focus" if i < 4 else "happy"
        mouth = "closed" if i < 4 else "smile"
        hands = hands_on(44, 76, 92, 1.2 if i % 2 == 0 else -1.2)
        fr.append(frame_svg(penguin(eye=eye, mouth=mouth, bob=bob - 8, fl=-10, fr=-10, feet=False, shadow=False) + desk() + laptop() + hands))
    return fr
A["work-typing"] = ("work", work_typing)

def work_thinking():
    # hand on chin -> eyes closed -> look up -> idea! (bulb + rays)
    fr = []
    spec = [("open", "closed", -88, -10, ""), ("half", "closed", -88, -10, motion(8, 80, True, 2)),
            ("open", "closed", -88, -10, ""), ("wide", "open", -92, -92, rays(84, 12, size=7) + rays(36, 12, True, 7)),
            ("open", "smile", -92, -92, bulb()), ("happy", "smile", -92, -92, bulb() + sparkle(16, 20, 3))]
    for eye, mouth, fl, fr_, fx in spec:
        fr.append(frame_svg(penguin(eye=eye, mouth=mouth, fl=fl, fr=fr_) + fx))
    return fr
A["work-thinking"] = ("work", work_thinking)

def work_writing():
    fr = []
    for i in range(6):
        px = [0, 3, 6, 9, 5, 1][i]
        pad = notepad(38, 74, lines=1 + (i >= 3))
        hand_l = f'<ellipse cx="38" cy="92" rx="7.5" ry="5" fill="{BODY}" stroke="{LINE}" stroke-width="2.6"/>'
        pen = pencil(72 + px * 0.6, 93, -35) + f'<ellipse cx="{74+px*0.6}" cy="92" rx="7.5" ry="5" fill="{BODY}" stroke="{LINE}" stroke-width="2.6"/>'
        fx = rays(92, 20, size=6) if i in (4, 5) else ""
        fr.append(frame_svg(penguin(eye="focus" if i != 3 else "open", mouth="closed" if i < 4 else "smile", bob=(1 if i % 2 else 0) - 8, fl=-30, fr=-30, feet=False, shadow=False) + desk() + pad + hand_l + pen + fx))
    return fr
A["work-writing"] = ("work", work_writing)

def break_stretch():
    fr = []
    seq = [(0, "open", "closed", 1, ""), (60, "half", "open", 0, ""), (150, "sleep", "open", -2, ""),
           (175, "squint", "open", -3, rays(10, 20, True, 6) + rays(110, 20, size=6)), (150, "happy", "smile", -1, sparkle(14, 24, 3) + sparkle(108, 18, 3)), (70, "happy", "smile", 1, "")]
    for ang, eye, mouth, bob, fx in seq:
        fr.append(frame_svg(penguin(eye=eye, mouth=mouth, bob=bob, fl=ang, fr=ang) + fx))
    return fr
A["break-stretch"] = ("break", break_stretch)

def break_tea():
    fr = []
    for i in range(6):
        up = i in (2, 3)
        cup = f'<g transform="translate(-14 {-24 if up else 0})">{mug(100, 84, (i % 3) * 2)}</g>'
        fr.append(frame_svg(penguin(eye="happy" if up else "open", mouth="closed", bob=1 if i % 2 else 0, fl=-20, fr=-70 if up else -30) + cup))
    return fr
A["break-tea"] = ("break", break_tea)

def break_music():
    fr = []
    tilts = [-6, -3, 0, 3, 6, 3]
    for i, t in enumerate(tilts):
        fr.append(frame_svg(penguin(eye="happy", mouth="smile", tilt=t, bob=1 if i % 2 else 0, fl=30 if i % 2 else 10, fr=30 if not i % 2 else 10) + notes(i)))
    return fr
A["break-music"] = ("break", break_music)

def tip(px, py, a, sign, length=26):
    """Flipper tip position for a flipper at angle a (left convention); sign=+1 left, -1 right."""
    rad = math.radians(a)
    return px - sign * length * math.sin(rad), py + length * math.cos(rad)

def ex_dumbbell():
    fr = []
    for i in range(6):
        lift = [0, 0.3, 1, 1, 0.5, 0][i]
        ang = 20 + 90 * lift
        lx, ly = tip(25, 76, ang, 1); rx, ry = tip(95, 76, ang, -1)
        d = dumbbell(lx, ly, ang) + dumbbell(rx, ry, -ang)
        fr.append(frame_svg(penguin(eye="focus" if lift < 1 else "squint", mouth="open" if lift >= 0.5 else "closed", fl=ang, fr=ang, squash=0.02 if lift >= 1 else 0,
                                    extra_front=d) + headband() + sweat(i)))
    return fr
A["exercise-dumbbell"] = ("ex", ex_dumbbell)

def ex_jump():
    fr = []
    seq = [(0, 0.10, 10), (-7, 0, 60), (-15, 0, 150), (-17, 0, 165), (-9, 0, 110), (0, 0.08, 30)]
    for i, (bob, sq, fl) in enumerate(seq):
        shadow = f'<ellipse cx="60" cy="110" rx="{42 + bob*0.8}" ry="4.5" fill="{SHADOW}" opacity=".55"/>'
        eye = "happy" if bob < -12 else "open"
        body = penguin(eye=eye, mouth="open" if bob < -8 else "closed", squash=sq, fl=fl, fr=fl, shadow=False) + headband()
        fx = (rays(12, 30, True, 6) + rays(108, 30, size=6)) if bob < -12 else ""
        fr.append(frame_svg('<g transform="translate(0 %s)">%s%s</g>' % (bob, body, fx), bg_extra=shadow))
    return fr
A["exercise-jump"] = ("ex", ex_jump)

def ex_walk():
    fr = []
    for i in range(6):
        ph = i % 4
        bob = 2 if ph % 2 else 0
        fl = [20, 70, 20, -20][ph]; fr_ = [20, -20, 20, 70][ph]
        fx = motion(4, 86, True, 2) + motion(116, 86, False, 2)
        fr.append(frame_svg(penguin(eye="open", mouth="smile", bob=bob, tilt=[0, -3, 0, 3][ph], fl=fl, fr=fr_, extra_back=fx) + headband() + sweat(i)))
    return fr
A["exercise-walk"] = ("ex", ex_walk)

def rest_sleep():
    fr = []
    for i in range(6):
        bob = [0, 1, 2, 2, 1, 0][i]
        fr.append(frame_svg(penguin(eye="sleep", mouth="closed", bob=bob, fl=-20, fr=-20, extra_back=pillow(), extra_front=blanket(bob)) + zz(i) + moon()))
    return fr
A["rest-sleep"] = ("sleep", rest_sleep)

def rest_relax():
    fr = []
    for i in range(6):
        sq = [0, 0.015, 0.03, 0.03, 0.015, 0][i]
        eye = "half" if i != 3 else "sleep"
        sofa = f'<rect x="-10" y="98" width="140" height="12" rx="6" fill="#dff0ff" stroke="{LINE}" stroke-width="2.4"/>'
        cup = f'<g transform="translate(-16 -2)">{mug(104, 84, (i % 3) * 2)}</g>'
        fr.append(frame_svg(penguin(eye=eye, mouth="smile", squash=sq, fl=-30, fr=-60, extra_back=sofa) + cup))
    return fr
A["rest-relax"] = ("sleep", rest_relax)

def reward_cheer():
    fr = []
    for i in range(6):
        bob = [0, -5, -10, -5, 0, -3][i]
        body = penguin(eye="star" if i in (2, 3) else "happy", mouth="open", fl=150, fr=150, squash=0.06 if bob == 0 else 0, shadow=False)
        fx = (rays(8, 28, True, 6) + rays(112, 28, size=6)) if i % 2 else ""
        shadow = f'<ellipse cx="60" cy="110" rx="{42 + bob*0.8}" ry="4.5" fill="{SHADOW}" opacity=".55"/>'
        fr.append(frame_svg('<g transform="translate(0 %s)">%s%s</g>' % (bob, body, fx), bg_extra=shadow + confetti(i)))
    return fr
A["reward-cheer"] = ("happy", reward_cheer)

def reward_love():
    fr = []
    for i in range(6):
        fr.append(frame_svg(penguin(eye="heart", mouth="smile", bob=1 if i % 2 else 0, tilt=[-4, -2, 0, 2, 4, 2][i], fl=-75, fr=-75) + floating_hearts(i)))
    return fr
A["reward-love"] = ("happy", reward_love)

def reward_pump():
    fr = []
    for i in range(6):
        up = i in (1, 2, 4, 5)
        side = i < 3
        fl = 140 if (up and side) else -20
        fr_ = 140 if (up and not side) else -20
        fx = (rays(6, 26, True, 7) if side else rays(114, 26, size=7)) if up else ""
        fr.append(frame_svg(penguin(eye="wink" if i in (2, 5) else "happy", mouth="open" if up else "smile", bob=-2 if up else 0, fl=fl, fr=fr_) + fx + banner("だいちゃーじ！")))
    return fr
A["reward-pump"] = ("happy", reward_pump)

STATE_JA = {"work": "作業中", "break": "休憩中", "ex": "運動中", "sleep": "休息・終了後", "happy": "ごほうび（終了直後）"}
VERSION = 2  # bump when the drawings change so the app re-imports them
# name_ja, fps, pingpong (False = one-way loop for cyclic motions)
META = {
    "work-typing": ("タイピング", 3, False), "work-thinking": ("ひらめき", 2, True), "work-writing": ("メモ書き", 3, False),
    "break-stretch": ("のびのび", 2, True), "break-tea": ("お茶タイム", 2, False), "break-music": ("音楽でゆらゆら", 3, False),
    "exercise-dumbbell": ("ダンベル", 3, False), "exercise-jump": ("ジャンプ", 4, False), "exercise-walk": ("足踏み", 4, False),
    "rest-sleep": ("おやすみ", 2, False), "rest-relax": ("まったり", 2, False),
    "reward-cheer": ("ばんざい", 4, False), "reward-love": ("ハート目", 3, False), "reward-pump": ("だいちゃーじ！", 3, False),
}

def main():
    svgdir = os.path.join(OUT, "svg"); os.makedirs(svgdir, exist_ok=True)
    manifest = []
    for name, (state, fn) in A.items():
        frames = fn()
        for k, svg in enumerate(frames):
            open(os.path.join(svgdir, f"{name}-{k}.svg"), "w").write(svg)
        ja, fps, pp = META[name]
        manifest.append({"name": name, "name_ja": ja, "file": f"{name}.png", "state": state, "state_ja": STATE_JA[state],
                         "frames": len(frames), "frame_size": 320, "gap": 40, "fps": fps, "pingpong": pp, "version": VERSION})
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=1)
    print("svgs written", sum(m["frames"] for m in manifest))

main()
