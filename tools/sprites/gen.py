"""Original penguin sprite-sheet generator (SVG -> PNG via Playwright/Chromium).
Each sheet = one animation = one state. Frames are 320x320 with 40px gaps, transparent bg.
"""
import asyncio, os, sys, json

OUT = sys.argv[1] if len(sys.argv) > 1 else "./out"
os.makedirs(OUT, exist_ok=True)

BODY, FACE, LINE, BEAK, FEET, CHEEK, HEART = "#7fc4ee", "#ffffff", "#1e2c44", "#9fd3f5", "#f6d84a", "#ffc1cc", "#ff6b8a"
LW = 3

def eyes(kind, dx=0, dy=0, lift=0):
    L, R = 46 + dx, 74 + dx
    y = 58 + dy
    if kind == "open":
        return f'''<ellipse cx="{L}" cy="{y}" rx="3.2" ry="4.6" fill="{LINE}"/><ellipse cx="{R}" cy="{y}" rx="3.2" ry="4.6" fill="{LINE}"/>
<circle cx="{L+1.2}" cy="{y-1.8}" r="1" fill="#fff"/><circle cx="{R+1.2}" cy="{y-1.8}" r="1" fill="#fff"/>'''
    if kind == "half":  # sleepy half-closed
        return f'''<path d="M{L-4} {y-1} q4 4 8 0" stroke="{LINE}" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="M{R-4} {y-1} q4 4 8 0" stroke="{LINE}" stroke-width="2.6" fill="none" stroke-linecap="round"/>
<ellipse cx="{L}" cy="{y+1.5}" rx="3" ry="2" fill="{LINE}"/><ellipse cx="{R}" cy="{y+1.5}" rx="3" ry="2" fill="{LINE}"/>'''
    if kind == "sleep":
        return f'''<path d="M{L-5} {y+1} q5 3 10 0" stroke="{LINE}" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="M{R-5} {y+1} q5 3 10 0" stroke="{LINE}" stroke-width="2.6" fill="none" stroke-linecap="round"/>'''
    if kind == "happy":
        return f'''<path d="M{L-5} {y+1} q5 -5 10 0" stroke="{LINE}" stroke-width="2.6" fill="none" stroke-linecap="round"/><path d="M{R-5} {y+1} q5 -5 10 0" stroke="{LINE}" stroke-width="2.6" fill="none" stroke-linecap="round"/>'''
    if kind == "heart":
        def h(cx): return f'<path d="M{cx} {y+5} C {cx-6} {y}, {cx-7} {y-6}, {cx-3} {y-7} C {cx-1} {y-7.5}, {cx} {y-6}, {cx} {y-5} C {cx} {y-6}, {cx+1} {y-7.5}, {cx+3} {y-7} C {cx+7} {y-6}, {cx+6} {y}, {cx} {y+5} Z" fill="{HEART}" stroke="{LINE}" stroke-width="1.6" stroke-linejoin="round"/>'
        return h(L) + h(R)
    if kind == "star":
        def s(cx):
            pts = []
            import math
            for i in range(10):
                r = 6 if i % 2 == 0 else 2.6
                a = -math.pi/2 + i*math.pi/5
                pts.append(f"{cx + r*math.cos(a):.1f},{y + r*math.sin(a):.1f}")
            return f'<polygon points="{" ".join(pts)}" fill="#ffd54a" stroke="{LINE}" stroke-width="1.5" stroke-linejoin="round"/>'
        return s(L) + s(R)
    if kind == "wide":
        return f'''<circle cx="{L}" cy="{y}" r="5" fill="#fff" stroke="{LINE}" stroke-width="1.6"/><circle cx="{R}" cy="{y}" r="5" fill="#fff" stroke="{LINE}" stroke-width="1.6"/>
<circle cx="{L}" cy="{y}" r="2.6" fill="{LINE}"/><circle cx="{R}" cy="{y}" r="2.6" fill="{LINE}"/>'''
    if kind == "focus":  # determined: open eyes with slanted brows
        return eyes("open", dx, dy) + f'''<path d="M{L-5} {y-9} l9 2" stroke="{LINE}" stroke-width="2.4" stroke-linecap="round"/><path d="M{R+5} {y-9} l-9 2" stroke="{LINE}" stroke-width="2.4" stroke-linecap="round"/>'''
    return ""

def beak(kind="closed", dx=0, dy=0):
    x, y = 60 + dx, 67.5 + dy
    d = f'<path d="M{x} {y-7.5} L {x+9} {y} L {x} {y+7.5} L {x-9} {y} Z" fill="{BEAK}" stroke="{LINE}" stroke-width="2.6" stroke-linejoin="round"/>'
    if kind == "closed":
        return d + f'<path d="M{x-7.5} {y} L {x+7.5} {y}" stroke="{LINE}" stroke-width="1.8" stroke-linecap="round"/>'
    if kind == "open":
        return d + f'<path d="M{x-6} {y} Q {x} {y+7} {x+6} {y} Z" fill="#e2557a" stroke="{LINE}" stroke-width="1.6" stroke-linejoin="round"/>'
    if kind == "smile":
        return d + f'<path d="M{x-7} {y-1} Q {x} {y+4} {x+7} {y-1}" stroke="{LINE}" stroke-width="1.8" fill="none" stroke-linecap="round"/>'
    return d

def cheeks(dx=0, dy=0, on=True):
    if not on: return ""
    return f'<ellipse cx="{36+dx}" cy="{68+dy}" rx="5" ry="3" fill="{CHEEK}" opacity=".85"/><ellipse cx="{84+dx}" cy="{68+dy}" rx="5" ry="3" fill="{CHEEK}" opacity=".85"/>'

def flipper(side, angle=0, raise_=0):
    """side: 'l' or 'r'; angle rotates around the shoulder (deg, positive = outward/up)."""
    if side == "l":
        px, py = 24, 64
        path = f'<path d="M22 62 C 8 68, 2 88, 12 96 C 22 100, 30 88, 32 72 Z" fill="{BODY}" stroke="{LINE}" stroke-width="{LW}"/>'
        return f'<g transform="translate({px} {py}) rotate({angle}) translate({-px} {-py-raise_})">{path}</g>'
    px, py = 96, 64
    path = f'<path d="M98 62 C 112 68, 118 88, 108 96 C 98 100, 90 88, 88 72 Z" fill="{BODY}" stroke="{LINE}" stroke-width="{LW}"/>'
    return f'<g transform="translate({px} {py}) rotate({-angle}) translate({-px} {-py-raise_})">{path}</g>'

def penguin(eye="open", mouth="closed", bob=0, squash=0.0, tilt=0, fl=0, fr=0, flr=0, frr=0, cheek=True, blink=False, extra_front="", extra_back="", feet=True, feet_dx=(0, 0), hide_face_shift=0):
    """Body drawn in 120x120 user space. bob: vertical shift (px, positive = down). squash: 0..0.15 flatten."""
    sy = 1 - squash
    sx = 1 + squash * 0.8
    feet_svg = ""
    if feet:
        feet_svg = f'''<ellipse cx="{45+feet_dx[0]}" cy="111" rx="13" ry="5.5" fill="{FEET}" stroke="{LINE}" stroke-width="2.4"/>
<ellipse cx="{75+feet_dx[1]}" cy="111" rx="13" ry="5.5" fill="{FEET}" stroke="{LINE}" stroke-width="2.4"/>'''
    e = "sleep" if blink else eye
    body = f'''
<g transform="translate(60 112) scale({sx:.3f} {sy:.3f}) translate(-60 -112) translate(0 {bob}) rotate({tilt} 60 112)">
<path d="M60 6 C 26 6, 12 34, 13 62 C 14 92, 32 112, 60 112 C 88 112, 106 92, 107 62 C 108 34, 94 6, 60 6 Z" fill="{BODY}" stroke="{LINE}" stroke-width="{LW}"/>
<path d="M60 52 C 55 40, 44 32, 35 40 C 26 48, 26 66, 29 86 C 32 102, 44 110, 60 110 C 76 110, 88 102, 91 86 C 94 66, 94 48, 85 40 C 76 32, 65 40, 60 52 Z" fill="{FACE}"/>
{flipper('l', fl, flr)}{flipper('r', fr, frr)}
{cheeks(on=cheek)}
{eyes(e)}
{beak(mouth)}
{extra_front}
</g>'''
    return extra_back + feet_svg + body

def frame_svg(inner, bg_extra=""):
    return f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="-14 -24 148 148" width="320" height="320">
<g stroke-linecap="round" stroke-linejoin="round">{bg_extra}{inner}</g></svg>'''

# ---------- props ----------
def laptop(dy=0, open_=True, screen="#cfe9fb"):
    return f'''<g transform="translate(0 {dy})">
<rect x="34" y="72" width="52" height="22" rx="3" fill="#34495e" stroke="{LINE}" stroke-width="2"/>
<rect x="38" y="76" width="44" height="14" rx="1.5" fill="{screen}"/>
<rect x="30" y="92" width="60" height="6" rx="2" fill="#9aa9b8" stroke="{LINE}" stroke-width="2"/></g>'''

def desk():
    return f'<rect x="-10" y="96" width="140" height="16" rx="4" fill="#d9b68a" stroke="{LINE}" stroke-width="2"/>'

def typing_hands(phase):
    # little flipper tips on keyboard, alternating
    a = 2 if phase % 2 == 0 else -2
    return f'''<ellipse cx="44" cy="{92+a*0.6}" rx="7" ry="4" fill="{BODY}" stroke="{LINE}" stroke-width="2.2"/>
<ellipse cx="76" cy="{92-a*0.6}" rx="7" ry="4" fill="{BODY}" stroke="{LINE}" stroke-width="2.2"/>'''

def motion_lines(x, y, flip=False, n=3):
    s = -1 if flip else 1
    out = ""
    for i in range(n):
        out += f'<path d="M{x} {y+i*5} q{s*4} 1 {s*8} 0" stroke="{LINE}" stroke-width="1.8" fill="none" opacity=".7"/>'
    return out

def sparkles(pts, color="#ffd54a"):
    out = ""
    for (x, y, r) in pts:
        out += f'<path d="M{x} {y-r} L{x+r*0.3} {y-r*0.3} L{x+r} {y} L{x+r*0.3} {y+r*0.3} L{x} {y+r} L{x-r*0.3} {y+r*0.3} L{x-r} {y} L{x-r*0.3} {y-r*0.3} Z" fill="{color}" stroke="{LINE}" stroke-width="1.2"/>'
    return out

def zz(phase):
    ys = [0, -4, -8, -12, -8, -4]
    o = ys[phase % 6]
    return f'''<g fill="{LINE}" font-weight="700" font-family="Arial,sans-serif">
<text x="96" y="{26+o}" font-size="14">z</text><text x="106" y="{14+o}" font-size="10">z</text><text x="114" y="{6+o}" font-size="7" opacity=".6">z</text></g>'''

def mug(x=100, steam=0):
    st = ""
    for i in range(2):
        st += f'<path d="M{x+3+i*5} {80-steam} q3 -4 0 -8 q-3 -4 0 -8" stroke="#8ab" stroke-width="1.6" fill="none" opacity=".8"/>'
    return f'''<g>{st}<rect x="{x}" y="82" width="14" height="18" rx="3" fill="#fff" stroke="{LINE}" stroke-width="2"/>
<path d="M{x+14} 86 q7 0 7 6 q0 6 -7 6" stroke="{LINE}" stroke-width="2" fill="none"/></g>'''

def bottle(dx=0, dy=0, tilt=0):
    return f'''<g transform="translate({dx} {dy}) rotate({tilt} 111 95)">
<rect x="106" y="84" width="10" height="22" rx="3" fill="#cfe9fb" stroke="{LINE}" stroke-width="2"/>
<rect x="108" y="78" width="6" height="7" rx="1.5" fill="#3f9bdc" stroke="{LINE}" stroke-width="2"/></g>'''

def dumbbell(cx, cy, angle=0):
    return f'''<g transform="rotate({angle} {cx} {cy})">
<rect x="{cx-16}" y="{cy-2}" width="32" height="4" rx="2" fill="#8d99a6" stroke="{LINE}" stroke-width="1.8"/>
<rect x="{cx-20}" y="{cy-7}" width="7" height="14" rx="2" fill="#5d6d7e" stroke="{LINE}" stroke-width="1.8"/>
<rect x="{cx+13}" y="{cy-7}" width="7" height="14" rx="2" fill="#5d6d7e" stroke="{LINE}" stroke-width="1.8"/></g>'''

def sweat(phase):
    o = (phase % 3) * 2
    return f'<g fill="#58a9e6"><path d="M{104} {24+o} c-3 5 -3 8 0 8 c3 0 3 -3 0 -8z"/><path d="M{112} {16+o} c-2 4 -2 6 0 6 c2 0 2 -2 0 -6z"/></g>'

def headband():
    return f'<path d="M20 36 Q60 24 100 36 Q60 32 20 36 Z" fill="#ff6b6b" stroke="{LINE}" stroke-width="2"/>'

def pillow():
    return f'<rect x="4" y="92" width="112" height="18" rx="8" fill="#fff2f6" stroke="{LINE}" stroke-width="2"/>'

def blanket(bob=0):
    return f'<path d="M10 {80+bob} Q60 {70+bob} 110 {80+bob} L112 112 L8 112 Z" fill="#b8d8ff" stroke="{LINE}" stroke-width="2.4"/><path d="M12 {88+bob} Q60 {80+bob} 108 {88+bob}" stroke="{LINE}" stroke-width="1.6" fill="none" opacity=".5"/>'

def moon():
    return f'<path d="M110 10 a9 9 0 1 0 8 12 a7 7 0 1 1 -8 -12z" fill="#ffe28a" stroke="{LINE}" stroke-width="1.6"/>'

def confetti(phase):
    import random
    rnd = random.Random(phase)
    out = ""
    cols = ["#ff6b8a", "#ffd54a", "#7fc4ee", "#9be28a", "#c69bff"]
    for i in range(12):
        x = rnd.uniform(-4, 124); y = rnd.uniform(-8, 60) + (phase % 6) * 6
        out += f'<rect x="{x:.1f}" y="{y:.1f}" width="4" height="7" rx="1" fill="{cols[i%5]}" transform="rotate({rnd.uniform(-40,40):.0f} {x:.1f} {y:.1f})" stroke="{LINE}" stroke-width="1"/>'
    return out

def notes(phase):
    o = (phase % 4) * 2
    return f'<g fill="#3f9bdc" font-family="Arial,sans-serif"><text x="100" y="{26-o}" font-size="16">♪</text><text x="112" y="{14+o}" font-size="12">♫</text></g>'

def banner(text):
    return f'''<rect x="22" y="-18" width="76" height="20" rx="10" fill="#fff" stroke="{LINE}" stroke-width="2"/>
<text x="60" y="-3" text-anchor="middle" font-size="11" font-weight="700" font-family="Arial,sans-serif" fill="{LINE}">{text}</text>'''

# ---------- animations: list of frame functions ----------
A = {}

# 作業中 1: typing at laptop (6 frames)
def work_typing():
    fr = []
    for i in range(6):
        bob = [0, 1, 0, 1, 0, 1][i]
        eye = "focus" if i < 4 else "happy"
        mouth = "closed" if i < 4 else "smile"
        fr.append(frame_svg(penguin(eye=eye, mouth=mouth, bob=bob, fl=-10, fr=-10, feet=False) + desk() + laptop() + typing_hands(i)
                            + (motion_lines(14, 86, True, 2) if i % 2 else motion_lines(98, 86, False, 2))))
    return fr
A["work-typing"] = ("work", work_typing)

# 作業中 2: reading / thinking with nod and occasional blink
def work_thinking():
    fr = []
    states = [("open", 0, 0), ("open", 0, 1), ("half", 0, 2), ("open", 1, 1), ("open", 0, 0), ("open", 0, 0)]
    for i, (eye, blink, bob) in enumerate(states):
        bulb = ""
        if i >= 4:
            bulb = f'<g><circle cx="104" cy="18" r="8" fill="#fff4b3" stroke="{LINE}" stroke-width="2"/><rect x="100" y="26" width="8" height="5" rx="1.5" fill="#bbb" stroke="{LINE}" stroke-width="1.6"/>' + (sparkles([(92, 6, 3), (118, 12, 3)]) if i == 5 else "") + '</g>'
        fr.append(frame_svg(penguin(eye=eye, blink=bool(blink), bob=bob, fl=-5, fr=30 if i < 4 else 55, frr=0, mouth="closed" if i < 5 else "smile", feet=False)
                            + desk() + laptop() + bulb))
    return fr
A["work-thinking"] = ("work", work_thinking)

# 作業中 3: writing notes with pencil
def work_writing():
    fr = []
    for i in range(6):
        px = [0, 4, 8, 12, 6, 0][i]
        pencil = f'<g transform="translate({px} 0) rotate(30 80 80)"><rect x="77" y="62" width="6" height="26" rx="1.5" fill="#ffd54a" stroke="{LINE}" stroke-width="1.8"/><path d="M77 88 l6 0 l-3 7 z" fill="#f4c8a8" stroke="{LINE}" stroke-width="1.5"/></g>'
        paper = f'<rect x="28" y="84" width="58" height="13" rx="2" fill="#fff" stroke="{LINE}" stroke-width="1.8"/><path d="M34 89 h{8+px*2} M34 93 h{20+px}" stroke="#8ab" stroke-width="1.4"/>'
        hand = f'<ellipse cx="{78+px}" cy="{90}" rx="7" ry="4.5" fill="{BODY}" stroke="{LINE}" stroke-width="2.2"/>'
        fr.append(frame_svg(penguin(eye="focus" if i != 3 else "open", bob=1 if i % 2 else 0, fl=-8, fr=-20, feet=False) + desk() + paper + pencil + hand))
    return fr
A["work-writing"] = ("work", work_writing)

# 休憩中 1: stretch arms up with yawn
def break_stretch():
    fr = []
    seq = [(0, "open", "closed", 2), (25, "half", "open", 0), (60, "sleep", "open", -2), (80, "sleep", "open", -3), (60, "happy", "smile", -1), (20, "happy", "smile", 1)]
    for i, (ang, eye, mouth, bob) in enumerate(seq):
        extra = sparkles([(14, 20, 3), (106, 16, 3)]) if i in (3, 4) else ""
        fr.append(frame_svg(penguin(eye=eye, mouth=mouth, bob=bob, fl=ang, fr=ang, squash=max(0, -bob) * 0.0, extra_front=extra)))
    return fr
A["break-stretch"] = ("break", break_stretch)

# 休憩中 2: drinking tea
def break_tea():
    fr = []
    for i in range(6):
        up = i in (2, 3)
        steam = (i % 3) * 2
        cup_y = -22 if up else 0
        cup = f'<g transform="translate(-12 {cup_y})">{mug(96, steam)}</g>'
        fr.append(frame_svg(penguin(eye="happy" if up else "open", mouth="closed", bob=1 if i % 2 else 0, fl=-5, fr=70 if up else 20, frr=0, extra_front=cup, cheek=True)))
    return fr
A["break-tea"] = ("break", break_tea)

# 休憩中 3: looking around / neck roll with music
def break_music():
    fr = []
    tilts = [-6, -3, 0, 3, 6, 3]
    for i, t in enumerate(tilts):
        fr.append(frame_svg(penguin(eye="happy", mouth="smile", tilt=t, bob=1 if i % 2 else 0, fl=10 if i % 2 else 0, fr=10 if not i % 2 else 0, extra_front=notes(i))))
    return fr
A["break-music"] = ("break", break_music)

# 運動中 1: dumbbell curls with headband and sweat
def ex_dumbbell():
    fr = []
    for i in range(6):
        up = i in (2, 3)
        lift = [0, 10, 24, 24, 10, 0][i]
        d = dumbbell(14, 92 - lift, -20 + lift) + dumbbell(106, 92 - lift, 20 - lift)
        fr.append(frame_svg(penguin(eye="focus" if not up else "open", mouth="open" if up else "closed", bob=0, fl=lift * 2.2, fr=lift * 2.2, squash=0.02 if up else 0,
                                    extra_front=headband() + d + sweat(i), cheek=True)))
    return fr
A["exercise-dumbbell"] = ("ex", ex_dumbbell)

# 運動中 2: jumping (hop with squash & stretch)
def ex_jump():
    fr = []
    seq = [(0, 0.10, 0), (-8, 0, 20), (-16, -0.03, 60), (-18, -0.04, 70), (-10, 0, 40), (0, 0.08, 10)]
    for i, (bob, sq, fl) in enumerate(seq):
        feet_on = bob > -5
        shadow = f'<ellipse cx="60" cy="112" rx="{30 + bob*0.3}" ry="4" fill="#000" opacity=".12"/>'
        eye = "happy" if bob < -15 else "open"
        body = penguin(eye=eye, mouth="open" if bob < -10 else "closed", squash=max(sq, 0), fl=fl, fr=fl, extra_front=headband() + (sparkles([(20, 30, 3), (100, 26, 3)]) if bob < -14 else ""))
        fr.append(frame_svg('<g transform="translate(0 %s)">%s</g>' % (bob, body), bg_extra=shadow))
    return fr
A["exercise-jump"] = ("ex", ex_jump)

# 運動中 3: side steps / walking in place
def ex_walk():
    fr = []
    for i in range(6):
        ph = i % 4
        lf = [0, -6, 0, 6][ph]; rf = [0, 6, 0, -6][ph]
        bob = 2 if ph % 2 else 0
        fr.append(frame_svg(penguin(eye="open", mouth="smile", bob=bob, tilt=[0, -3, 0, 3][ph], fl=20 if ph in (1,) else 0, fr=20 if ph == 3 else 0, feet_dx=(lf, rf),
                                    extra_front=headband() + sweat(i), extra_back=motion_lines(-6, 88, True) + motion_lines(118, 88))))
    return fr
A["exercise-walk"] = ("ex", ex_walk)

# 休息・終了後 1: sleeping with zzz
def rest_sleep():
    fr = []
    for i in range(6):
        bob = [0, 1, 2, 2, 1, 0][i]
        fr.append(frame_svg(penguin(eye="sleep", mouth="closed", bob=bob, fl=-15, fr=-15, cheek=True, extra_back=pillow(), extra_front=blanket(bob) + zz(i)) + moon()))
    return fr
A["rest-sleep"] = ("sleep", rest_sleep)

# 休息・終了後 2: relaxing with eyes half closed, slow breathing
def rest_relax():
    fr = []
    for i in range(6):
        sq = [0, 0.015, 0.03, 0.03, 0.015, 0][i]
        eye = "half" if i != 3 else "sleep"
        sofa = '<rect x="-6" y="100" width="132" height="12" rx="6" fill="#dff0ff" stroke="%s" stroke-width="2"/>' % LINE
        cup = '<g transform="translate(-14 -2)">%s</g>' % mug(104, (i % 3) * 2)
        fr.append(frame_svg(penguin(eye=eye, mouth="smile", squash=sq, fl=-20, fr=-20, extra_back=sofa) + cup))
    return fr
A["rest-relax"] = ("sleep", rest_relax)

# ごほうび 1: cheering with confetti
def reward_cheer():
    fr = []
    for i in range(6):
        bob = [0, -6, -12, -6, 0, -3][i]
        body = penguin(eye="star" if i in (2, 3) else "happy", mouth="open", fl=75, fr=75, squash=0.06 if bob == 0 else 0, extra_front=(sparkles([(10, 24, 3), (110, 18, 3)]) if i % 2 else ""))
        fr.append(frame_svg('<g transform="translate(0 %s)">%s</g>' % (bob, body), bg_extra=confetti(i)))
    return fr
A["reward-cheer"] = ("happy", reward_cheer)

# ごほうび 2: heart eyes, hugging, hearts float
def reward_love():
    fr = []
    for i in range(6):
        hy = (i % 6) * 4
        hearts = "".join(f'<path d="M{x} {y-hy} c-4 -5 -9 1 0 8 c9 -7 4 -13 0 -8z" fill="{HEART}" stroke="{LINE}" stroke-width="1.4" opacity="{1 - hy/30:.2f}"/>' for (x, y) in [(10, 34), (112, 28), (100, 50)])
        fr.append(frame_svg(penguin(eye="heart", mouth="smile", bob=1 if i % 2 else 0, tilt=[-4, -2, 0, 2, 4, 2][i], fl=-30, fr=-30, extra_front=hearts)))
    return fr
A["reward-love"] = ("happy", reward_love)

# ごほうび 3: fist pump with 「だいちゃーじ！」 banner
def reward_pump():
    fr = []
    for i in range(6):
        up = i in (1, 2, 4, 5)
        side = i < 3
        fl = 140 if (up and side) else 0
        fr_ = 140 if (up and not side) else 0
        fr.append(frame_svg(penguin(eye="wide" if i in (2, 5) else "happy", mouth="open" if up else "smile", bob=-2 if up else 0, fl=fl, fr=fr_, extra_front=(sparkles([(8, 30, 4)]) if (up and side) else sparkles([(112, 30, 4)]) if up else "")) + banner("だいちゃーじ！")))
    return fr
A["reward-pump"] = ("happy", reward_pump)

STATE_JA = {"work": "作業中", "break": "休憩中", "ex": "運動中", "sleep": "休息・終了後", "happy": "ごほうび（終了直後）"}


def main():
    svgdir = os.path.join(OUT, "svg"); os.makedirs(svgdir, exist_ok=True)
    manifest = []
    for name, (state, fn) in A.items():
        frames = fn()
        for k, svg in enumerate(frames):
            open(os.path.join(svgdir, f"{name}-{k}.svg"), "w").write(svg)
        manifest.append({"name": name, "file": f"{name}.png", "state": state, "state_ja": STATE_JA[state], "frames": len(frames)})
    json.dump(manifest, open(os.path.join(OUT, "manifest.json"), "w"), ensure_ascii=False, indent=1)
    print("svgs written", sum(m["frames"] for m in manifest))

main()
