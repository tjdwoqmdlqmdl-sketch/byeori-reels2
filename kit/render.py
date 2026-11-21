import sys, math, random, subprocess, os
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageChops

os.chdir(os.path.dirname(os.path.abspath(__file__)))
W, H, FPS = 1080, 1920, 30
FONT = "/usr/share/fonts/opentype/noto/NotoSansCJK-Black.ttc"
_fc = {}
def F(sz):
    sz = int(max(8, sz))
    if sz not in _fc: _fc[sz] = ImageFont.truetype(FONT, sz, index=1)
    return _fc[sz]

# ---------- assets ----------
CH = {}
for k, n in [("open", "char.png"), ("closed", "char_closed.png"), ("wink", "char_wink.png")]:
    im = Image.open(n).convert("RGBA").crop((51, 42, 1167, 1242))
    CH[k] = im.resize((int(im.width * 800 / im.height), 800), Image.LANCZOS)

BG = Image.new("RGB", (W, H))
g = np.zeros((H, W, 3), np.uint8)
top = np.array([214, 186, 250]); bot = np.array([176, 146, 232])
for c in range(3):
    g[:, :, c] = (top[c] + (bot[c] - top[c]) * np.linspace(0, 1, H))[:, None]
BG = Image.fromarray(g)

random.seed(7)
SPK = [(random.randint(60, 1020), random.randint(80, 1800), random.uniform(0, 6.28), random.uniform(18, 44)) for _ in range(16)]
DARK = (86, 52, 120)
WHITE = (255, 255, 255)
YEL = (255, 226, 120)

def clamp(x): return max(0.0, min(1.0, x))
def eob(x):
    x = clamp(x); c1 = 1.70158; c3 = c1 + 1
    return 1 + c3 * (x - 1) ** 3 + c1 * (x - 1) ** 2
def eoc(x): x = clamp(x); return 1 - (1 - x) ** 3

def sparkle(d, cx, cy, r, col=YEL):
    k = 0.28
    pts = []
    for i in range(8):
        a = math.pi / 4 * i - math.pi / 2
        rr = r if i % 2 == 0 else r * k
        pts.append((cx + rr * math.cos(a), cy + rr * math.sin(a)))
    d.polygon(pts, fill=col)

def base(T):
    img = BG.copy(); d = ImageDraw.Draw(img)
    for x, y, ph, r in SPK:
        s = 0.5 + 0.5 * math.sin(T * 3 + ph)
        sparkle(d, x, y - (T * 12) % 40, r * (0.35 + 0.65 * s), (240, 220, 255))
    return img

def text(img, xy, s, size, fill=WHITE, stroke=DARK, sw=10, scale=1.0, anchor="mm"):
    d = ImageDraw.Draw(img)
    d.text(xy, s, font=F(size * scale), fill=fill, anchor=anchor, stroke_width=int(sw * scale), stroke_fill=stroke)

def pill(img, cx, cy, w, h, fill, scale=1.0, outline=DARK):
    d = ImageDraw.Draw(img)
    w *= scale; h *= scale
    d.rounded_rectangle([cx - w / 2, cy - h / 2, cx + w / 2, cy + h / 2], radius=h / 2, fill=fill, outline=outline, width=8)

def put_char(img, variant, cx, cy, h, rot=0, sx=1.0, sy=1.0):
    src = CH[variant]; sc = h / src.height
    im = src.resize((max(1, int(src.width * sc * sx)), max(1, int(src.height * sc * sy))), Image.LANCZOS)
    if rot: im = im.rotate(rot, Image.BICUBIC, expand=True)
    sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
    ImageDraw.Draw(sh).ellipse([cx - im.width * 0.32, cy + h * 0.46, cx + im.width * 0.32, cy + h * 0.52], fill=(110, 70, 160, 90))
    img.paste(sh, (0, 0), sh)
    img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)

def disclaimer(img, extra=""):
    text(img, (W / 2, 1855), "※ 재미로 보는 운세입니다" + extra, 32, WHITE, (140, 100, 190), 5)

def burst(img, cx, cy, t, n=8, rmax=260):
    if t < 0 or t > 1: return
    d = ImageDraw.Draw(img)
    for i in range(n):
        a = 2 * math.pi * i / n + 0.3
        r = rmax * eoc(t)
        sparkle(d, cx + r * math.cos(a), cy + r * math.sin(a), 34 * (1 - t) + 6)

# ---------- scenes ----------
def s1(t, T):
    img = base(T); d = ImageDraw.Draw(img)
    p = eob(t / 0.7)
    bob = 18 * math.sin(t * 6)
    rot = 7 * math.sin(t * 9) if t > 0.6 else 0
    put_char(img, "open", W / 2, 1050 + bob + (1 - p) * 500, 780 * max(p, 0.01), rot=rot, sy=1 + 0.03 * math.sin(t * 6))
    burst(img, W / 2, 800, (t - 0.5) / 1.0)
    for i, s in enumerate(["오늘 내 운,", "몇 티어일까?"]):
        q = eob((t - 0.5 - i * 0.25) / 0.45)
        if q > 0: text(img, (W / 2, 260 + i * 140), s, 112, scale=q)
    disclaimer(img); return img

BADGES = [("자미두수", (255, 150, 190)), ("점성술", (120, 190, 255)), ("사주팔자", (255, 190, 90))]
def s2(t, T):
    img = base(T)
    put_char(img, "open", W / 2, 1000 + 12 * math.sin(t * 5), 560, rot=3 * math.sin(t * 4))
    for i, (nm, col) in enumerate(BADGES):
        q = eob((t - 0.3 - i * 0.5) / 0.5)
        if q <= 0: continue
        a = t * 1.5 + i * 2 * math.pi / 3 - math.pi / 2
        cx = W / 2 + 330 * math.cos(a); cy = 1000 + 300 * math.sin(a)
        pill(img, cx, cy, 330, 120, col, q)
        text(img, (cx, cy - 4), nm, 58, scale=q, sw=8)
    for i, s in enumerate(["세 가지 방법으로", "모두 봤어요!"]):
        q = eob((t - 0.1 - i * 0.2) / 0.4)
        if q > 0: text(img, (W / 2, 250 + i * 130), s, 96, scale=q)
    if t > 3.2:
        q = eob((t - 3.2) / 0.5)
        text(img, (W / 2, 1620), "자미두수 + 점성술 + 사주팔자", 52, YEL, DARK, 9, scale=q)
    disclaimer(img); return img

VC = [(540, 640), (410, 860), (670, 860)]
VCOL = [(255, 150, 190), (120, 190, 255), (255, 200, 100)]
VLAB = [("자미두수", (540, 470)), ("점성술", (265, 940)), ("사주팔자", (815, 940))]
def s3(t, T):
    img = base(T)
    R = 250; box = (100, 330, 980, 1170); S = 2
    bw, bh = (box[2] - box[0]) * S, (box[3] - box[1]) * S
    masks = []
    for i, (cx, cy) in enumerate(VC):
        q = eoc((t - 0.2 - i * 0.25) / 0.9)
        ox = [0, -240, 240][i] * (1 - q); oy = [-300, 200, 200][i] * (1 - q)
        m = Image.new("L", (bw, bh), 0)
        x = (cx + ox - box[0]) * S; y = (cy + oy - box[1]) * S
        ImageDraw.Draw(m).ellipse([x - R * S, y - R * S, x + R * S, y + R * S], fill=255)
        masks.append(m.resize((bw // S, bh // S), Image.LANCZOS))
    for m, col in zip(masks, VCOL):
        img.paste(Image.new("RGB", masks[0].size, col), (box[0], box[1]), m.point(lambda v: int(v * 0.55)))
    inter = ImageChops.multiply(ImageChops.multiply(masks[0], masks[1]), masks[2])
    glow = clamp((t - 2.4) / 0.6)
    if glow > 0:
        pulse = 0.85 + 0.15 * math.sin(t * 8)
        img.paste(Image.new("RGB", inter.size, (255, 238, 120)), (box[0], box[1]), inter.point(lambda v: int(v * glow * pulse)))
        d = ImageDraw.Draw(img)
        for k in range(6):
            a = t * 2 + k
            sparkle(d, 540 + 70 * math.cos(a * 1.3 + k), 800 + 60 * math.sin(a + k * 2), 18 + 8 * math.sin(a * 3), WHITE)
        q = eob((t - 2.6) / 0.5)
        text(img, (540, 790), "겹치는", 64, WHITE, (200, 120, 20), 9, scale=q)
        text(img, (540, 860), "운만!", 64, WHITE, (200, 120, 20), 9, scale=q)
    for i, (nm, (x, y)) in enumerate(VLAB):
        q = eob((t - 1.2 - i * 0.2) / 0.4)
        if q > 0: text(img, (x, y), nm, 54, scale=q, sw=8)
    q = eob((t - 0.1) / 0.5)
    for i, s in enumerate(["셋 다 똑같이 나온 것만", "풀이해요"]):
        text(img, (W / 2, 200 + i * 120), s, 84, scale=q)
    put_char(img, "open", W / 2, 1470 + 12 * math.sin(t * 6), 380, rot=4 * math.sin(t * 5))
    if t > 4.5:
        q = eob((t - 4.5) / 0.5)
        pill(img, W / 2, 1720, 760, 120, (255, 250, 235), q)
        text(img, (W / 2, 1716), "그래서 더 믿음이 가요", 56, DARK, (255, 255, 255), 0, scale=q)
    disclaimer(img); return img

TIERS = [("브론즈", (205, 127, 50)), ("실버", (192, 196, 208)), ("골드", (255, 198, 40)),
         ("플래티넘", (70, 215, 185)), ("다이아", (100, 185, 255))]
def s4(t, T):
    img = base(T)
    head = "브론즈? 실버?"
    if t >= 2.3: head = "골드?"
    if t >= 3.15: head = "플래티넘?"
    if t >= 4.0: head = "설마 다이아?!"
    text(img, (W / 2, 260), head, 108, scale=1 + 0.05 * math.sin(t * 10))
    for i, (nm, col) in enumerate(TIERS):
        tl = 0.6 + 0.85 * i
        q = eob((t - tl) / 0.45)
        cy = 1380 - i * 175; w = 560 + i * 70
        if q <= 0:
            pill(img, W / 2, cy, w, 140, (176, 150, 224), 1)
            text(img, (W / 2, cy - 3), nm, 62, (210, 190, 245), (150, 120, 205), 6)
        else:
            sc = 1 + 0.12 * math.sin(clamp((t - tl) / 0.5) * math.pi)
            sh = 0
            if i == 4: sh = 8 * math.sin(t * 25) if t > 4.0 and t < 4.6 else 0
            pill(img, W / 2 + sh, cy, w, 140, col, sc)
            text(img, (W / 2 + sh, cy - 3), nm, 66, WHITE, DARK, 9, scale=sc)
            d = ImageDraw.Draw(img)
            sparkle(d, W / 2 - w / 2 - 20, cy - 40, 30 * q, YEL); sparkle(d, W / 2 + w / 2 + 20, cy + 30, 24 * q, YEL)
            burst(img, W / 2, cy, (t - tl) / 0.7, 6, 240)
    if t > 4.0:
        d = ImageDraw.Draw(img)
        for k in range(5):
            a = t * 2.5 + k * 1.26
            sparkle(d, W / 2 + 330 * math.cos(a), 680 + 90 * math.sin(a * 1.1), 26, WHITE)
    put_char(img, "open", W / 2, 1655, 330, rot=5 * math.sin(t * 7))
    disclaimer(img); return img

def conf(img, t):
    rnd = random.Random(3)
    d = ImageDraw.Draw(img)
    cols = [(255, 150, 190), (120, 190, 255), (255, 210, 90), (255, 255, 255), (130, 230, 190)]
    for i in range(70):
        x0 = rnd.uniform(0, W); v = rnd.uniform(300, 900); a0 = rnd.uniform(-1.2, 1.2)
        x = x0 + math.sin(a0) * v * t * 0.4 + 30 * math.sin(t * 6 + i)
        y = 700 - math.cos(a0) * v * t * 0.9 + 900 * t * t
        r = rnd.uniform(10, 20); ang = t * 8 + i
        pts = [(x + r * math.cos(ang + k * 1.57), y + r * 0.6 * math.sin(ang + k * 1.57)) for k in range(4)]
        d.polygon(pts, fill=cols[i % 5])

def diamond(d, cx, cy, r):
    pts = [(cx - r, cy - r * 0.3), (cx - r * 0.55, cy - r * 0.8), (cx + r * 0.55, cy - r * 0.8), (cx + r, cy - r * 0.3), (cx, cy + r)]
    d.polygon(pts, fill=(130, 200, 255), outline=DARK)
    d.line([pts[0], pts[3]], fill=DARK, width=6)
    d.line([(cx - r * 0.2, cy - r * 0.3), (cx, cy + r), (cx + r * 0.2, cy - r * 0.3)], fill=(230, 245, 255), width=6)
    d.line([pts[1], (cx - r * 0.2, cy - r * 0.3)], fill=DARK, width=5); d.line([pts[2], (cx + r * 0.2, cy - r * 0.3)], fill=DARK, width=5)

def s5(t, T):
    img = base(T)
    rev = 1.8
    if t < rev:
        sh = 22 * math.sin(t * 38) * clamp(t / 0.8)
        put_char(img, "closed", W / 2 + sh, 760, 560 * (1 + 0.04 * math.sin(t * 20)))
        text(img, (W / 2, 250), "두근두근…", 118, scale=1 + 0.05 * math.sin(t * 10))
    else:
        u = t - rev
        put_char(img, "open", W / 2, 700 - 40 * math.sin(clamp(u / 0.4) * math.pi), 520, rot=6 * math.sin(u * 8) * (1 - clamp(u / 2)))
        text(img, (W / 2, 250), "당신의 운빨 티어는?", 98, scale=eob(u / 0.4))
        q = eob((u - 0.15) / 0.55)
        if q > 0:
            cw, ch = 840 * q, 560 * q; cy = 1330
            d = ImageDraw.Draw(img)
            d.rounded_rectangle([W / 2 - cw / 2, cy - ch / 2, W / 2 + cw / 2, cy + ch / 2], 60, fill=(255, 250, 238), outline=DARK, width=10)
            diamond(d, W / 2, cy - 130 * q, 90 * q)
            text(img, (W / 2, cy + 50 * q), "다이아", 140, (70, 160, 240), (255, 255, 255), 14, scale=q)
            text(img, (W / 2, cy + 190 * q), "오늘은 운빨 폭발!", 58, DARK, (255, 255, 255), 0, scale=q)
        conf(img, u)
        fl = 1 - clamp(u / 0.25)
        if fl > 0: img = Image.blend(img, Image.new("RGB", img.size, WHITE), fl * 0.85)
    disclaimer(img, " · 결과는 예시입니다"); return img

def s6(t, T):
    img = base(T)
    p = eob(t / 0.5)
    put_char(img, "wink", W / 2, 1190, 640 * max(p, 0.01), rot=5 * math.sin(t * 7), sy=1 + 0.03 * math.sin(t * 8))
    for i, s in enumerate(["당신의 운빨은", "몇 티어?"]):
        q = eob((t - 0.1 - i * 0.25) / 0.45)
        if q > 0:
            text(img, (W / 2, 330 + i * 190), s, 138 if i == 0 else 190, WHITE if i == 0 else YEL, DARK, 16, scale=q)
    q = eob((t - 1.0) / 0.5)
    if q > 0:
        pill(img, W / 2, 1640, 700, 130, (255, 150, 190), q * (1 + 0.04 * math.sin(t * 9)))
        text(img, (W / 2, 1636), "지금 확인하기", 68, scale=q)
    burst(img, W / 2, 1000, (t - 0.3) / 1.0, 10, 400)
    disclaimer(img); return img

SCENES = [(0, 3, s1), (3, 8, s2), (8, 15, s3), (15, 22, s4), (22, 27, s5), (27, 30, s6)]

def render(i):
    a, b, fn = SCENES[i]
    n = (b - a) * FPS
    out = f"scene{i}.mp4"; tmp = f"scene{i}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for f in range(n):
        t = f / FPS
        p.stdin.write(fn(t, a + t).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.rename(tmp, out); print("done", i)
    else: sys.exit(1)

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        pts = [(0, 1.5), (1, 5.5), (2, 12.0), (3, 20.0), (4, 24.0), (5, 28.5)]
        sheet = Image.new("RGB", (W * 3 // 2, H * 2 // 2))
        for k, (i, T) in enumerate(pts):
            a, b, fn = SCENES[i]
            im = fn(T - a, T).resize((W // 2, H // 2), Image.LANCZOS)
            sheet.paste(im, ((k % 3) * W // 2, (k // 3) * H // 2))
        sheet.save("preview.png"); fn = SCENES[3][2]; fn(5.0, 20.0).save("full4.png")
    else:
        render(int(sys.argv[1]))
