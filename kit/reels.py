import sys, os, math, subprocess
os.chdir(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.getcwd())
from PIL import Image, ImageDraw
from render import (base, text, pill, put_char, sparkle, burst, eob, eoc, clamp, disclaimer,
                    W, H, FPS, F, YEL, WHITE, DARK)

DUR = 15.0
C = {"목": (92, 200, 130), "화": (255, 112, 100), "토": (232, 182, 84), "금": (150, 165, 205), "수": (84, 158, 255)}

REELS = {
 "A": dict(rank=1, header="2027 정미년 · 인연운",
    hook=["내년 인연운,", "들어오는 일간", "딱 4개!"], card_d=2.2,
    cards=[("庚", "경금", "금", ["듬직한 사람이", "눈에 들어오는 해"]),
           ("辛", "신금", "금", ["일상 속 인연이", "새롭게 보이는 해"]),
           ("壬", "임수", "수", ["마음이 열리는 만큼", "인연도 넓어져"]),
           ("癸", "계수", "수", ["천천히 다가오는", "안정적인 인연"])],
    tip=("인연운은 '기회'일 뿐!", "먼저 나를 챙겨야 좋은 사람이 와"), tip_d=1.7,
    foot=" · 전통 십성 해석 기준"),
 "B": dict(rank=2, header="2027 정미년 · 일간별 키워드",
    hook=["2027 정미년,", "내 일간은", "어떤 해일까?"], card_d=1.9,
    cards=[("甲乙", "갑목 · 을목", "목", ["표현력과 재능이", "빛나는 해"]),
           ("丙丁", "병화 · 정화", "화", ["내 사람도 경쟁도", "많아지는 해"]),
           ("戊己", "무토 · 기토", "토", ["도움과 배움이", "붙는 해"]),
           ("庚辛", "경금 · 신금", "금", ["책임과 역할이", "커지는 해"]),
           ("壬癸", "임수 · 계수", "수", ["돈과 기회가", "움직이는 해"])],
    tip=None, tip_d=0, foot=" · 전통 십성 해석 기준"),
 "C": dict(rank=3, header="2027 정미년 · 재물운",
    hook=["내년 돈 기회가", "움직이는 일간", "딱 4개!"], card_d=2.2,
    cards=[("甲", "갑목", "목", ["새 수입 아이디어가", "떠오르는 해"]),
           ("乙", "을목", "목", ["꾸준히 쌓으면", "돈이 붙는 해"]),
           ("壬", "임수", "수", ["돈의 흐름이", "눈에 보이는 해"]),
           ("癸", "계수", "수", ["작은 기회를 잡으면", "커지는 해"])],
    tip=("들어오는 돈보다", "새는 돈 점검이 먼저!"), tip_d=1.7,
    foot=" · 전통 십성 해석 기준"),
}
HOOK_D = 2.5
def timeline(s):
    n = len(s["cards"]); c0 = HOOK_D; c1 = c0 + n * s["card_d"]
    t1 = c1 + s["tip_d"]
    return dict(c0=c0, c1=c1, t0=c1, t1=t1, o0=t1)

def make_fn(s):
    tl = timeline(s); n = len(s["cards"])
    def hook(t, T):
        img = base(T); p = eob(t / 0.6)
        pill(img, W / 2, 150, 760, 90, (255, 250, 235), eob(t / 0.4)); text(img, (W / 2, 146), s["header"], 44, DARK, (255, 255, 255), 0, scale=eob(t / 0.4))
        put_char(img, "open", W / 2, 1290 + (1 - p) * 500 + 14 * math.sin(t * 6), 640 * max(p, 0.01), rot=6 * math.sin(t * 9) if t > 0.5 else 0)
        for i, ln in enumerate(s["hook"]):  # 첫 프레임부터 훅 문구가 보이도록 (이탈 방지)
            q = 1 + 0.04 * math.sin(t * 8 + i)
            if ln: text(img, (W / 2, 330 + i * 175), ln, 132 if i < 2 else 160, WHITE if i < 2 else YEL, DARK, 15, scale=q)
        burst(img, W / 2, 900, (t - 0.4) / 0.9); disclaimer(img, s["foot"]); return img
    def card(t, T, i):
        hj, nm, el, kw = s["cards"][i]; col = C[el]
        img = base(T)
        pill(img, W / 2, 160, 800, 90, (255, 250, 235)); text(img, (W / 2, 156), s["header"], 44, DARK, (255, 255, 255), 0)
        q = eob(t / 0.4); r = 280 * q * (1 + 0.02 * math.sin(t * 8))
        d = ImageDraw.Draw(img); cy = 700
        d.ellipse([W / 2 - r - 14, cy - r - 14, W / 2 + r + 14, cy + r + 14], fill=(255, 255, 255), outline=DARK, width=8)
        d.ellipse([W / 2 - r, cy - r, W / 2 + r, cy + r], fill=col)
        text(img, (W / 2, cy - 10), hj, 250 if len(hj) == 1 else 190, WHITE, DARK, 14, scale=q)
        for k in range(4):
            a = t * 2 + k * 1.57; sparkle(d, W / 2 + (r + 70) * math.cos(a), cy + (r + 40) * math.sin(a), 22, YEL)
        q2 = eob((t - 0.15) / 0.4)
        if q2 > 0: text(img, (W / 2, 1085), nm, 90, WHITE, DARK, 12, scale=q2)
        q3 = eob((t - 0.3) / 0.4)
        if q3 > 0:
            pill(img, W / 2, 1270, 900, 230, (255, 250, 235), q3)
            text(img, (W / 2, 1230), kw[0], 62, DARK, (255, 255, 255), 0, scale=q3); text(img, (W / 2, 1312), kw[1], 70, (170, 70, 150), (255, 255, 255), 0, scale=q3)
        for k in range(n):
            x = W / 2 + (k - (n - 1) / 2) * 50; rr = 14 if k == i else 9
            d.ellipse([x - rr, 1450 - rr, x + rr, 1450 + rr], fill=YEL if k == i else (230, 215, 255))
        put_char(img, "open", W / 2, 1680, 300, rot=5 * math.sin(t * 7)); disclaimer(img, s["foot"]); return img
    def tip(t, T):
        img = base(T); a, b = s["tip"]
        pill(img, W / 2, 160, 800, 90, (255, 250, 235)); text(img, (W / 2, 156), s["header"], 44, DARK, (255, 255, 255), 0)
        q = eob(t / 0.4); text(img, (W / 2, 520), a, 96, YEL, DARK, 13, scale=q)
        q2 = eob((t - 0.2) / 0.4)
        if q2 > 0: text(img, (W / 2, 690), b, 62, WHITE, DARK, 10, scale=q2)
        put_char(img, "open", W / 2, 1150 + 10 * math.sin(t * 6), 520, rot=4 * math.sin(t * 6)); disclaimer(img, s["foot"]); return img
    def outro(t, T):
        img = base(T); p = eob(t / 0.5)
        put_char(img, "wink", W / 2, 1200, 600 * max(p, 0.01), rot=5 * math.sin(t * 7))
        o1, o2 = s.get("outro", ("저장해두고", "1월에 다시 봐!"))
        for i, (ln, col) in enumerate([(o1, WHITE), (o2, YEL)]):
            q = eob((t - 0.1 - i * 0.2) / 0.4)
            if q > 0: text(img, (W / 2, 330 + i * 190), ln, 150 if i == 0 else 140, col, DARK, 15, scale=q)
        q = eob((t - 0.6) / 0.45)
        if q > 0:
            pill(img, W / 2, 1610, 760, 120, (255, 112, 150), q * (1 + 0.03 * math.sin(t * 9))); text(img, (W / 2, 1606), "팔로우하고 다음 편 보기", 56, scale=q)
        q2 = eob((t - 0.9) / 0.45)
        if q2 > 0:
            pill(img, W / 2, 1750, 800, 100, (255, 250, 235), q2)
            text(img, (W / 2, 1746), "내 운세 티어는 프로필 링크 클릭!", 48, DARK, (255, 255, 255), 0, scale=q2)
        burst(img, W / 2, 1000, (t - 0.3) / 1.0, 10, 400); disclaimer(img, s["foot"]); return img
    def fn(T):
        if T < tl["c0"]: return hook(T, T)
        if T < tl["c1"]:
            i = min(n - 1, int((T - tl["c0"]) / s["card_d"])); return card(T - tl["c0"] - i * s["card_d"], T, i)
        if s["tip"] and T < tl["t1"]: return tip(T - tl["t0"], T)
        return outro(T - tl["o0"], T)
    return fn

def render(name):
    s = REELS[name]; fn = make_fn(s); n = int(DUR * FPS); out = f"reel_{name}.mp4"; tmp = f"reel_{name}.tmp.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", "-r", str(FPS), tmp], stdin=subprocess.PIPE)
    for f in range(n): p.stdin.write(fn(f / FPS).convert("RGB").tobytes())
    p.stdin.close()
    if p.wait() == 0: os.rename(tmp, out); print("done", name)
    else: sys.exit(1)

if __name__ == "__main__":
    if sys.argv[1] == "preview":
        sheet = Image.new("RGB", (W * 3 // 2, H * 4 // 4))
        pts = {"A": [1.5, 4.0, 12.4, 14.0], "B": [1.5, 6.0, 12.5, 14.0], "C": [1.5, 4.0, 12.4, 14.0]}
        sheet = Image.new("RGB", (W // 2 * 4, H // 2 * 3))
        for r, nm in enumerate("ABC"):
            fn = make_fn(REELS[nm])
            for c, T in enumerate(pts[nm]): sheet.paste(fn(T).resize((W // 2, H // 2), Image.LANCZOS), (c * W // 2, r * H // 2))
        sheet.save("preview_reels.png")
    else: render(sys.argv[1])
