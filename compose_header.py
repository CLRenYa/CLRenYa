# -*- coding: utf-8 -*-
"""合成顶部横幅:星空 GIF 背景 + 霓虹艺术字(CLVe 逐帧呼吸) + 流星 + 樱花瓣"""
import io
import math
import os
import random
import sys
import subprocess

from PIL import Image, ImageDraw

try:
    import resvg_py
except ImportError:
    subprocess.check_call([sys.executable, "-m", "pip", "install", "-q", "resvg-py"])
    import resvg_py

WT = r"C:\Users\Administrator\AppData\Local\Temp\assets-wt5"
SRC = os.path.join(WT, "starry-sky.gif")
OUT = os.path.join(WT, "header-composed.gif")

W, H = 900, 220
FRAMES = 48
DURATION = 80

NEON_SVG = """<svg xmlns="http://www.w3.org/2000/svg" width="720" height="220" viewBox="0 0 720 220">
  <defs>
    <linearGradient id="neonD" x1="0" y1="0" x2="1" y2="0">
      <stop offset="0" stop-color="#ff69b4"/>
      <stop offset="0.5" stop-color="#bb9af7"/>
      <stop offset="1" stop-color="#7aa2f7"/>
    </linearGradient>
    <filter id="glowD" x="-60%" y="-60%" width="220%" height="220%">
      <feGaussianBlur stdDeviation="5" result="b"/>
      <feMerge><feMergeNode in="b"/><feMergeNode in="SourceGraphic"/></feMerge>
    </filter>
  </defs>
  <rect x="120" y="60" width="480" height="100" rx="14" fill="none" stroke="url(#neonD)" stroke-width="2.5" filter="url(#glowD)"/>
  <text x="360" y="125" text-anchor="middle" font-family="'Segoe Script','Brush Script MT',cursive" font-size="52" font-weight="bold" fill="url(#neonD)" filter="url(#glowD)">CLRenYa</text>
  <text x="360" y="148" text-anchor="middle" font-family="monospace" font-size="13" fill="#a9b8ff" letter-spacing="4" opacity="0.9">CODE &#183; ANIME &#183; AESTHETIC</text>
</svg>"""

png = resvg_py.svg_to_bytes(svg_string=NEON_SVG, width=720, height=220)
neon = Image.open(io.BytesIO(png)).convert("RGBA")
neon_x = (W - 720) // 2

# 两档呼吸透明度
def scale_alpha(img, a):
    r, g, b, al = img.split()
    al = al.point(lambda p: int(p * a))
    return Image.merge("RGBA", (r, g, b, al))

variants = [neon, scale_alpha(neon, 0.85)]

src = Image.open(SRC)
n = getattr(src, "n_frames", 1)
star_frames = []
for i in range(n):
    src.seek(i)
    star_frames.append(src.convert("RGBA"))

random.seed(42)
stars = []
for _ in range(70):
    x = random.uniform(0, W); y = random.uniform(0, H)
    size = random.choice([1, 1, 2, 2, 3])
    phase = random.uniform(0, math.tau); speed = random.choice([1, 2, 3])
    color = random.choice([(255,255,255),(200,210,255),(255,205,235),(170,190,255)])
    stars.append((x, y, size, phase, speed, color))

bright = random.sample(stars, 4)

meteors = [
    {"t0": 0.08, "dur": 0.14, "x0": 140, "y0": -20, "dx": 300, "dy": 170},
    {"t0": 0.55, "dur": 0.13, "x0": 760, "y0": -20, "dx": -260, "dy": 160},
]

petals = []
for _ in range(10):
    petals.append({"x": random.uniform(0, W), "y": random.uniform(20, H-20),
                   "v": random.uniform(0.5, 1.2), "amp": random.uniform(4, 10),
                   "phase": random.uniform(0, math.tau), "size": random.uniform(2, 3.6)})

fx0, fx1 = 120 + neon_x, 600 + neon_x
fy0, fy1 = 60, 160

frames = []
for f in range(FRAMES):
    p = f / FRAMES
    img = star_frames[f % n].copy()
    d = ImageDraw.Draw(img, "RGBA")

    for (x, y, size, phase, speed, color) in stars:
        tw = 0.55 + 0.45 * math.sin(phase + p * math.tau * speed)
        r = size / 2
        d.ellipse([x-r, y-r, x+r, y+r], fill=color + (int(255*tw),))
    for (x, y, size, phase, speed, color) in bright:
        tw = 0.4 + 0.6*(0.5+0.5*math.sin(phase + p*math.tau*speed))
        gl = int(9 + 12*tw); a = int(170*tw)
        d.line([x-gl, y, x+gl, y], fill=color+(a,), width=1)
        d.line([x, y-gl, x, y+gl], fill=color+(a,), width=1)
    for pt in petals:
        x = (pt["x"] + pt["v"]*f) % W
        y = pt["y"] + pt["amp"]*math.sin(pt["phase"] + p*math.tau*2)
        s = pt["size"]
        d.ellipse([x-s, y-s*0.6, x+s, y+s*0.6], fill=(255,160,200,120))

    img.alpha_composite(variants[0] if f % 2 == 0 else variants[1], (neon_x, 0))

    per = 2*((fx1-fx0)+(fy1-fy0))
    t = (p*2 % 1.0) * per
    if t < (fx1-fx0): px, py = fx0+t, fy0
    elif t < (fx1-fx0)+(fy1-fy0): px, py = fx1, fy0+(t-(fx1-fx0))
    elif t < 2*(fx1-fx0)+(fy1-fy0): px, py = fx1-(t-((fx1-fx0)+(fy1-fy0))), fy1
    else: px, py = fx0, fy1-(t-(2*(fx1-fx0)+(fy1-fy0)))
    d.ellipse([px-4, py-4, px+4, py+4], fill=(255, 150, 205, 230))
    d.ellipse([px-7, py-7, px+7, py+7], outline=(255,160,210,90))

    for m in meteors:
        t = (p - m["t0"]) / m["dur"]
        if 0 <= t <= 1:
            fade = math.sin(t*math.pi)
            hx, hy = m["x0"]+m["dx"]*t, m["y0"]+m["dy"]*t
            L = math.hypot(m["dx"], m["dy"]); tail = 90*fade
            tx, ty = hx - m["dx"]/L*tail, hy - m["dy"]/L*tail
            d.line([tx, ty, hx, hy], fill=(255,255,255,int(200*fade)), width=2)
            d.ellipse([hx-2, hy-2, hx+2, hy+2], fill=(255,255,255,int(255*fade)))

    frames.append(img.convert("P", palette=Image.ADAPTIVE, colors=160))

frames[0].save(OUT, save_all=True, append_images=frames[1:], duration=DURATION, loop=0, optimize=True)
print("done", os.path.getsize(OUT))
