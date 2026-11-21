import os, sys, math
os.chdir(os.path.dirname(os.path.abspath(__file__))); sys.path.insert(0, os.getcwd())
from PIL import Image, ImageDraw
from render import base, text, pill, put_char, sparkle, W, H, YEL, WHITE, DARK
from reels import C

# 시리즈 공통 커버 템플릿 (1080x1920, 핵심 요소는 가운데 3:4 영역 y 240~1680 안)
COVERS = {
    "A": dict(tag="2027 정미년 · 인연운", l1="인연운 들어오는", l2="일간 4개", chips=[("庚", "금"), ("辛", "금"), ("壬", "수"), ("癸", "수")]),
    "B": dict(tag="2027 정미년 · 일간별", l1="내 일간은", l2="어떤 해?", chips=[("甲乙", "목"), ("丙丁", "화"), ("戊己", "토"), ("庚辛", "금"), ("壬癸", "수")]),
    "C": dict(tag="2027 정미년 · 재물운", l1="돈 기회 오는", l2="일간 4개", chips=[("甲", "목"), ("乙", "목"), ("壬", "수"), ("癸", "수")]),
}

def cover(k):
    s = COVERS[k]
    img = base(0.6)
    d = ImageDraw.Draw(img)
    # 상단 시리즈 태그
    pill(img, W / 2, 330, 640, 96, (255, 112, 150)); text(img, (W / 2, 325), s["tag"], 46, WHITE, DARK, 6)
    # 큰 제목
    text(img, (W / 2, 505), s["l1"], 118, WHITE, DARK, 16)
    text(img, (W / 2, 680), s["l2"], 176, YEL, DARK, 20)
    # 일간 한자 칩
    n = len(s["chips"]); r = 92 if n == 4 else 84; gap = 2 * r + 30
    for i, (hj, el) in enumerate(s["chips"]):
        x = W / 2 + (i - (n - 1) / 2) * gap; y = 960
        d.ellipse([x - r - 8, y - r - 8, x + r + 8, y + r + 8], fill=WHITE, outline=DARK, width=7)
        d.ellipse([x - r, y - r, x + r, y + r], fill=C[el])
        text(img, (x, y - 6), hj, 96 if len(hj) == 1 else 62, WHITE, DARK, 9)
    sparkle(d, 150, 470, 40, YEL); sparkle(d, 935, 640, 34, YEL); sparkle(d, 120, 1250, 30, WHITE); sparkle(d, 960, 1180, 36, YEL)
    # 별이
    put_char(img, "open", W / 2, 1360, 480)
    return img

if __name__ == "__main__":
    os.makedirs("covers", exist_ok=True)
    grid = Image.new("RGB", (3 * 360 + 20, 480), (255, 255, 255))
    for i, k in enumerate("ABC"):
        im = cover(k); im.convert("RGB").save(f"covers/cover_{k}.jpg", quality=92)
        crop = im.crop((0, 240, 1080, 1680)).resize((360, 480), Image.LANCZOS)  # 프로필 그리드 3:4 미리보기
        grid.paste(crop, (i * 370, 0))
    grid.save("cover_grid.png")
    print("ok")
