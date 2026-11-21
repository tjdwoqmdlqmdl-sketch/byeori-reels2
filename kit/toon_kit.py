"""사주툰 빌드: python3 toon_kit.py <toon.json> <repo_dir>
6장 캐러셀(1080x1350 JPEG) + 15초 릴스(1080x1920) + posts json 2개(캐러셀/릴스) 생성.
toon.json 키: id, ep, slot_carousel, slot_reel, title, cover{l1,l2,l3,preview,time,sub}, chat1{narr,title,time,msgs[[L|R,text]]},
 chat2{...}, star{narr,b1,b2,reply}, explain{title,chips[[hj,el]],rows[4],hi,box[2]}, twist{l1,l2,l3,q,a,b}, caption_body, hashtags, comment
"""
import os, sys, json, math, subprocess
KIT = os.path.dirname(os.path.abspath(__file__)); os.chdir(KIT); sys.path.insert(0, KIT)
import numpy as np
from PIL import Image, ImageDraw, ImageFont
from render import put_char, sparkle, text, pill, eob, YEL, WHITE, DARK, base, disclaimer
from reels import C

TW, TH = 1080, 1350
FD = "/usr/share/fonts/opentype/noto/"
RAW = "https://raw.githubusercontent.com/tjdwoqmdlqmdl-sketch/byeori-reels2/main"
CTA = ("👉 팔로우하면 사주툰 다음 화 계속 올려줄게!\n"
       "🔗 내 운세 티어는 프로필 링크에서 바로 확인해봐\n"
       "※ 재미로 보는 운세야 (전통 사주 해석 기준)")
_f = {}
def FT(w, sz):
    k = (w, int(sz))
    if k not in _f: _f[k] = ImageFont.truetype(FD + f"NotoSansCJK-{w}.ttc", int(sz), index=1)
    return _f[k]

def bg(dark=False):
    top, bot = (np.array([46, 30, 78]), np.array([24, 16, 44])) if dark else (np.array([214, 186, 250]), np.array([176, 146, 232]))
    g = np.zeros((TH, TW, 3), np.uint8)
    for c in range(3): g[:, :, c] = (top[c] + (bot[c] - top[c]) * np.linspace(0, 1, TH))[:, None]
    return Image.fromarray(g)

def frame(img, ep, page):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 36, 380, 96], 30, fill=(255, 112, 150))
    d.text((210, 66), f"사주툰 EP.{ep} · 별이 운세", font=FT("Bold", 30), fill=WHITE, anchor="mm")
    d.text((TW - 50, 66), f"{page}/6", font=FT("Bold", 32), fill=WHITE, anchor="rm")
    d.text((TW / 2, TH - 34), "※ 재미로 보는 운세입니다 · 전통 사주 해석 기준", font=FT("Medium", 26), fill=(235, 225, 255), anchor="mm")

def fit(d, s, w, wt, size):
    while d.textlength(s, font=FT(wt, size)) > w and size > 20: size -= 2
    return size

def phone(img, title, time_str, msgs, top=210, bottom=1230):
    d = ImageDraw.Draw(img); x0, x1 = 90, TW - 90
    d.rounded_rectangle([x0 + 10, top + 16, x1 + 10, bottom + 16], 48, fill=(60, 30, 110))
    d.rounded_rectangle([x0, top, x1, bottom], 48, fill=(250, 248, 255), outline=DARK, width=6)
    d.rounded_rectangle([x0, top, x1, top + 110], 48, fill=(236, 230, 250)); d.rectangle([x0, top + 60, x1, top + 110], fill=(236, 230, 250))
    d.line([x0, top + 110, x1, top + 110], fill=(210, 200, 230), width=3)
    d.ellipse([x0 + 36, top + 25, x0 + 96, top + 85], fill=(190, 180, 210))
    d.text((x0 + 116, top + 55), title, font=FT("Bold", 40), fill=(40, 30, 60), anchor="lm")
    d.text((x1 - 36, top + 55), time_str, font=FT("Medium", 30), fill=(130, 120, 150), anchor="rm")
    y = top + 150
    for side, s in msgs:
        f = FT("Medium", 44); lines = s.split("\n")
        w = max(d.textlength(l, font=f) for l in lines); h = 60 * len(lines) + 28
        bx0, col, fg = (x0 + 40, (232, 228, 242), (40, 30, 60)) if side == "L" else (x1 - 40 - w - 56, (255, 222, 110), (60, 40, 20))
        d.rounded_rectangle([bx0, y, bx0 + w + 56, y + h], 34, fill=col)
        for i, l in enumerate(lines): d.text((bx0 + 28, y + 14 + i * 60), l, font=f, fill=fg)
        y += h + 26

def narr(img, s, y=150):
    d = ImageDraw.Draw(img); size = fit(d, s, 900, "Black", 48); w = d.textlength(s, font=FT("Black", size))
    d.rounded_rectangle([TW / 2 - w / 2 - 30, y - 42, TW / 2 + w / 2 + 30, y + 42], 20, fill=(30, 20, 50))
    d.text((TW / 2, y), s, font=FT("Black", size), fill=YEL, anchor="mm")

def T(img, xy, s, size, fill=WHITE, stroke=DARK, sw=10, maxw=980):
    d = ImageDraw.Draw(img); size = fit(d, s, maxw, "Black", size)
    text(img, xy, s, size, fill, stroke, sw)

def pages(s):
    ep = s["ep"]; out = []
    c = s["cover"]; img = bg(True); d = ImageDraw.Draw(img)
    for k in range(18): sparkle(d, (k * 263) % TW, 120 + (k * 397) % 1100, 10 + k % 4 * 4, (255, 230, 150))
    T(img, (TW / 2, 260), c["l1"], 96, sw=12); T(img, (TW / 2, 380), c["l2"], 96, sw=12); T(img, (TW / 2, 520), c["l3"], 140, YEL, sw=16)
    d.rounded_rectangle([160, 640, 920, 730], 45, fill=(250, 248, 255), outline=DARK, width=6)
    d.text((220, 685), c["preview"], font=FT("Bold", fit(d, c["preview"], 520, "Bold", 44)), fill=(40, 30, 60), anchor="lm")
    d.text((890, 685), c["time"], font=FT("Medium", 30), fill=(130, 120, 150), anchor="rm")
    put_char(img, "closed", TW / 2, 1010, 400, rot=-6)
    T(img, (TW / 2, 1240), c["sub"], 44, sw=7); frame(img, ep, 1); out.append(img)
    for i, key in enumerate(("chat1", "chat2")):
        ch = s[key]; img = bg(); narr(img, ch["narr"]); phone(img, ch["title"], ch["time"], ch["msgs"])
        if i == 0: put_char(img, "closed", 880, 1120, 230, rot=8)
        frame(img, ep, 2 + i); out.append(img)
    st = s["star"]; img = bg(); d = ImageDraw.Draw(img); narr(img, st["narr"])
    x, y, w, h = 150, 230, 780, 300
    d.polygon([(x + w * 0.3, y + h - 4), (x + w * 0.3 + 60, y + h - 4), (560, 640)], fill=WHITE, outline=DARK)
    d.rounded_rectangle([x, y, x + w, y + h], 40, fill=WHITE, outline=DARK, width=7); d.rectangle([x + w * 0.3 + 4, y + h - 10, x + w * 0.3 + 56, y + h - 2], fill=WHITE)
    for j, (ln, col) in enumerate([(st["b1"], DARK), (st["b2"], (200, 60, 120))]):
        d.text((x + w / 2, y + 110 + j * 80), ln, font=FT("Black", fit(d, ln, w - 60, "Black", 58)), fill=col, anchor="mm")
    put_char(img, "open", TW / 2, 850, 430, rot=-8)
    rw = d.textlength(st["reply"], font=FT("Bold", 46)) + 80
    d.rounded_rectangle([990 - rw, 1080, 990, 1180], 50, fill=(255, 222, 110), outline=DARK, width=5)
    d.text((990 - rw / 2, 1130), st["reply"], font=FT("Bold", 46), fill=(60, 40, 20), anchor="mm"); frame(img, ep, 4); out.append(img)
    ex = s["explain"]; img = bg(True); d = ImageDraw.Draw(img); T(img, (TW / 2, 210), ex["title"], 70, YEL)
    n = len(ex["chips"])
    for i, (hj, el) in enumerate(ex["chips"]):
        x = TW / 2 + (i - (n - 1) / 2) * 230; y = 400
        d.ellipse([x - 98, y - 98, x + 98, y + 98], fill=WHITE, outline=DARK, width=7); d.ellipse([x - 88, y - 88, x + 88, y + 88], fill=C[el])
        text(img, (x, y - 6), hj, 110 if len(hj) == 1 else 70, WHITE, DARK, 10)
    for i, r in enumerate(ex["rows"]):
        hi = i == ex.get("hi", 1); T(img, (TW / 2, 600 + i * 95 + (20 if i >= 2 else 0)), r, 90 if hi else 62, YEL if hi else WHITE, sw=9)
    d.rounded_rectangle([90, 1020, 990, 1180], 40, fill=(255, 250, 235), outline=DARK, width=6)
    for j, (ln, col) in enumerate([(ex["box"][0], DARK), (ex["box"][1], (200, 60, 120))]):
        d.text((TW / 2, 1070 + j * 65), ln, font=FT("Black", fit(d, ln, 840, "Black", 50)), fill=col, anchor="mm")
    frame(img, ep, 5); out.append(img)
    tw = s["twist"]; img = bg(); d = ImageDraw.Draw(img)
    T(img, (TW / 2, 200), tw["l1"], 76, sw=11); T(img, (TW / 2, 320), tw["l2"], 92, sw=12); T(img, (TW / 2, 450), tw["l3"], 92, YEL, sw=12)
    put_char(img, "wink", 270, 760, 380, rot=-6)
    d.rounded_rectangle([480, 620, 1010, 900], 40, fill=WHITE, outline=DARK, width=6)
    for j, (ln, col) in enumerate([(tw["q"], DARK), (tw["a"], (200, 60, 120)), (tw["b"], (80, 110, 220))]):
        d.text((745, 690 + j * 80), ln, font=FT("Black", fit(d, ln, 480, "Black", 52)), fill=col, anchor="mm")
    pill(img, TW / 2, 1040, 760, 110, (255, 112, 150)); text(img, (TW / 2, 1036), f"팔로우하고 EP.{ep + 1} 보기", 52)
    pill(img, TW / 2, 1170, 820, 96, (255, 250, 235)); text(img, (TW / 2, 1166), "내 운세 티어는 프로필 링크 클릭!", 44, DARK, (255, 255, 255), 0)
    frame(img, ep, 6); out.append(img)
    return out

def reel(s, pgs, out_mp4):
    W, H, FPS, PER = 1080, 1920, 30, 2.5
    pw, ph = 1000, 1250; py = 390
    small = [p.resize((pw, ph), Image.LANCZOS) for p in pgs]
    tmp = out_mp4 + ".v.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for f in range(int(15 * FPS)):
        t = f / FPS; i = min(5, int(t / PER)); u = t - i * PER
        img = base(t); d = ImageDraw.Draw(img)
        pill(img, W / 2, 110, 420, 80, (255, 112, 150)); text(img, (W / 2, 106), f"사주툰 EP.{s['ep']}", 44, WHITE, DARK, 6)
        T(img, (W / 2, 250), s["title"], 96, YEL, sw=14)
        z = 1 + 0.03 * (u / PER); pg = small[i]
        if z != 1: pg = pg.resize((int(pw * z), int(ph * z)), Image.BILINEAR)
        k = eob(u / 0.3) if i > 0 else 1
        x = int(W / 2 - pg.width / 2 + (1 - k) * 300); y = int(py + ph / 2 - pg.height / 2)
        d.rounded_rectangle([x + 8, y + 14, x + pg.width + 8, y + pg.height + 14], 30, fill=(110, 70, 160))
        img.paste(pg, (x, y))
        for j in range(6):
            cx = W / 2 + (j - 2.5) * 44; r = 12 if j == i else 8
            d.ellipse([cx - r, 1700 - r, cx + r, 1700 + r], fill=YEL if j == i else (230, 215, 255))
        text(img, (W / 2, 1790), "끝까지 보면 반전 있음", 44, WHITE, DARK, 7)
        disclaimer(img); p.stdin.write(img.convert("RGB").tobytes())
    p.stdin.close(); assert p.wait() == 0
    src = open(os.path.join(KIT, "audio.py")).read()
    head = src.split("BPM = 124")[0].replace("DUR = 30.0", "DUR = 15.0").replace("os.chdir(os.path.dirname(os.path.abspath(__file__)))", "pass")
    bgm = "BPM = 124" + src.split("BPM = 124")[1].split("# SFX")[0]
    wav = out_mp4 + ".wav"; tail = ("# fades" + src.split("# fades")[1]).replace('"audio.wav"', repr(wav))
    ev = "".join(f"add(whoosh(0.35), {i * PER}, gain=0.45); add(pop(), {i * PER + 0.05}, gain=0.8)\n" for i in range(6))
    ev += f"add(bell(91, 1.5), {4 * PER + 0.3}, gain=0.8); add(sweep(0.6), {5 * PER}, gain=0.7); add(bell(96, 1.8), {5 * PER + 0.2}, gain=0.7)\n"
    exec(head + bgm + ev + tail, {})
    assert subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                            "-b:a", "192k", "-shortest", out_mp4 + ".tmp.mp4"]) == 0
    os.replace(out_mp4 + ".tmp.mp4", out_mp4); os.remove(tmp); os.remove(wav)

def build(s, repo):
    rid = s["id"]
    for d in ("toon", "reels", "posts", "covers"): os.makedirs(os.path.join(repo, d), exist_ok=True)
    pgs = pages(s); urls = []
    for i, im in enumerate(pgs, 1):
        fn = f"{rid}_{i}.jpg"; im.convert("RGB").save(os.path.join(repo, "toon", fn), quality=92); urls.append(f"{RAW}/toon/{fn}")
    pgs[0].convert("RGB").resize((1080, 1350)).save(os.path.join(repo, "covers", f"{rid}_reel.jpg"), quality=92)
    reel(s, pgs, os.path.join(repo, "reels", f"{rid}_reel.mp4"))
    caption = s["caption_body"].strip() + "\n\n" + CTA + "\n\n" + s["hashtags"]; assert len(caption) <= 2200
    json.dump(dict(id=f"{rid}_carousel", kind="carousel", slot=s["slot_carousel"], image_urls=urls, caption=caption, comment=s["comment"]),
              open(os.path.join(repo, "posts", f"{rid}_carousel.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(dict(id=f"{rid}_reel", kind="reel", slot=s["slot_reel"], video_url=f"{RAW}/reels/{rid}_reel.mp4", thumb_offset=1000,
                   caption=caption, comment=s["comment"]), open(os.path.join(repo, "posts", f"{rid}_reel.json"), "w"), ensure_ascii=False, indent=1)
    print("built", rid)

if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
