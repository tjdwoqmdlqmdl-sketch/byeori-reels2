"""별이 사주툰 (그림 리스트형): python3 toon2_kit.py <vol.json> <repo_dir>
vol.json: id, vol, slot_carousel, slot_reel, title, sub, items[10] = [label(십성/일간), line1, line2], question, note, caption_body, hashtags, comment
캐러셀 3장(1080x1350): 표지 / 10칸 그리드(캐릭터+라벨+2줄) / 질문+CTA,  릴스 15초: 표지 → 그리드를 위에서 아래로 훑기 → CTA
캐릭터: 별이를 칸마다 다른 파스텔 색으로 칠하고 머리 위에 라벨 원.
"""
import os, sys, json, subprocess
KIT = os.path.dirname(os.path.abspath(__file__)); os.chdir(KIT); sys.path.insert(0, KIT)
import numpy as np
from PIL import Image, ImageDraw
from render import CH, sparkle, text, pill, eob, YEL, WHITE, DARK
from toon_kit import FT, fit, RAW

TW, TH = 1080, 1350
PAPER, INK = (252, 250, 255), (36, 28, 52)
TINTS = [(170, 215, 255), (255, 190, 200), (255, 226, 150), (200, 235, 180), (255, 205, 160),
         (210, 195, 255), (175, 230, 225), (255, 200, 235), (230, 230, 240), (250, 240, 200)]
CTA = ("👉 팔로우하면 별이 사주툰 다음 VOL. 계속 올려줄게!\n"
       "🔗 내 운세 티어는 프로필 링크에서 바로 확인해봐\n"
       "※ 재미로 보는 운세야 (전통 사주 해석 기준)")
_tint = {}
def tinted(i, h):
    k = (i, h)
    if k in _tint: return _tint[k]
    src = CH["open"]; a = np.asarray(src).astype(float); rgb, al = a[..., :3], a[..., 3:]
    lum = rgb.mean(-1, keepdims=True); light = (lum > 200) & (rgb.min(-1, keepdims=True) > 185)
    col = np.array(TINTS[i % 10], float)
    out = np.where(light, col * (lum / 245.0), rgb).clip(0, 255)
    im = Image.fromarray(np.concatenate([out, al], -1).astype(np.uint8), "RGBA")
    im = im.resize((int(im.width * h / im.height), h), Image.LANCZOS); _tint[k] = im
    return im

def char_with_label(img, i, cx, cy, h, label):
    im = tinted(i, h); img.paste(im, (int(cx - im.width / 2), int(cy - im.height / 2)), im)
    d = ImageDraw.Draw(img); r = int(h * 0.27); ly = cy - h * 0.18
    d.ellipse([cx - r - 7, ly - r - 7, cx + r + 7, ly + r + 7], fill=WHITE, outline=INK, width=5)
    d.ellipse([cx - r - 18, ly - 7, cx - r - 4, ly + 7], fill=WHITE, outline=INK, width=3)
    d.ellipse([cx + r + 4, ly - 7, cx + r + 18, ly + 7], fill=WHITE, outline=INK, width=3)
    d.text((cx, ly), label, font=FT("Black", fit(d, label, r * 1.8, "Black", int(r * 0.75))), fill=INK, anchor="mm")

def cover(s):
    img = Image.new("RGB", (TW, TH), PAPER); d = ImageDraw.Draw(img)
    d.text((TW / 2, 200), f"VOLUME {s['vol']}.", font=FT("Black", 110), fill=INK, anchor="mm")
    y = 340
    for ln in s["title"].split("\n"):
        d.text((TW / 2, y), ln, font=FT("Black", fit(d, ln, 980, "Black", 112)), fill=INK, anchor="mm"); y += 135
    for k in range(6): sparkle(d, 200 + k * 140, 1180 - (k % 2) * 40, 18, (255, 200, 90))
    im = CH["wink"]; im = im.resize((int(im.width * 560 / im.height), 560), Image.LANCZOS)
    img.paste(im, (int(TW / 2 - im.width / 2), 640), im)
    d.text((TW / 2, TH - 60), "별이 사주툰 · @byeori.fortune_", font=FT("Bold", 34), fill=(140, 120, 170), anchor="mm")
    return img

def grid(s):
    img = Image.new("RGB", (TW, TH), PAPER); d = ImageDraw.Draw(img)
    d.rounded_rectangle([20, 18, TW - 20, 138], 26, fill=INK)
    t = s["title"].replace("\n", " ")
    d.text((TW / 2, 78), t, font=FT("Black", fit(d, t, TW - 80, "Black", 66)), fill=WHITE, anchor="mm")
    top, ch = 160, 236
    for i, (lab, l1, l2) in enumerate(s["items"]):
        col, row = i % 2, i // 2; x0, y0 = col * TW / 2, top + row * ch
        char_with_label(img, i, x0 + 115, y0 + ch / 2 + 6, 205, lab)
        for j, ln in enumerate((l1, l2)):
            d.text((x0 + 228, y0 + ch / 2 - 30 + j * 58), ln, font=FT("Bold", fit(d, ln, TW / 2 - 250, "Bold", 34)), fill=INK, anchor="lm")
    for r in range(6): d.line([20, top + r * ch, TW - 20, top + r * ch], fill=(200, 192, 215), width=3)
    d.line([TW / 2, top, TW / 2, top + 5 * ch], fill=(200, 192, 215), width=3)
    return img

def last(s):
    img = Image.new("RGB", (TW, TH), PAPER); d = ImageDraw.Draw(img)
    d.text((TW / 2, 230), s["question"], font=FT("Black", fit(d, s["question"], 980, "Black", 84)), fill=INK, anchor="mm")
    d.text((TW / 2, 340), "댓글로 번호 남겨줘!", font=FT("Black", 60), fill=(220, 80, 140), anchor="mm")
    y = 450
    for ln in s["note"].split("\n"):
        d.text((TW / 2, y), ln, font=FT("Bold", fit(d, ln, 960, "Bold", 38)), fill=(110, 95, 140), anchor="mm"); y += 56
    for k in range(5): char_with_label(img, k * 2, 140 + k * 200, 820, 190, s["items"][k * 2][0])
    pill(img, TW / 2, 1080, 760, 110, (255, 112, 150)); text(img, (TW / 2, 1076), f"팔로우하고 VOL.{s['vol'] + 1} 보기", 52)
    pill(img, TW / 2, 1210, 820, 96, (255, 250, 235)); text(img, (TW / 2, 1206), "내 운세 티어는 프로필 링크 클릭!", 44, DARK, (255, 255, 255), 0)
    d.text((TW / 2, TH - 40), "※ 재미로 보는 운세입니다 · 전통 사주 해석 기준", font=FT("Medium", 26), fill=(140, 120, 170), anchor="mm")
    return img

def reel(s, pages, out):
    W, H, FPS = 1080, 1920, 30
    tmp = out + ".v.mp4"
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    gy = (H - TH) // 2
    for f in range(15 * FPS):
        t = f / FPS; img = Image.new("RGB", (W, H), PAPER)
        if t < 2.5:
            img.paste(pages[0], (0, gy))
        elif t < 12.5:
            img.paste(pages[1], (0, gy)); d = ImageDraw.Draw(img)
            i = min(9, int((t - 2.5) / 1.0)); col, row = i % 2, i // 2
            x0, y0 = col * TW / 2 + 8, gy + 160 + row * 236 + 6
            d.rounded_rectangle([x0, y0, x0 + TW / 2 - 16, y0 + 224], 24, outline=(255, 90, 150), width=9)
            tag = f"VOL.{s['vol']} · 별이 사주툰"
            d.text((W / 2, gy - 90), tag, font=FT("Black", 56), fill=INK, anchor="mm")
            d.text((W / 2, gy + TH + 90), "너는 몇 번이야? 댓글로!", font=FT("Black", 58), fill=(220, 80, 140), anchor="mm")
        else:
            img.paste(pages[2], (0, gy))
        p.stdin.write(img.tobytes())
    p.stdin.close(); assert p.wait() == 0
    src = open(os.path.join(KIT, "audio.py")).read()
    head = src.split("BPM = 124")[0].replace("DUR = 30.0", "DUR = 15.0").replace("os.chdir(os.path.dirname(os.path.abspath(__file__)))", "pass")
    bgm = "BPM = 124" + src.split("BPM = 124")[1].split("# SFX")[0]
    wav = out + ".wav"; tail = ("# fades" + src.split("# fades")[1]).replace('"audio.wav"', repr(wav))
    ev = "add(pop(), 0.05, gain=0.8); add(whoosh(0.4), 2.5, gain=0.5); add(whoosh(0.4), 12.5, gain=0.5); add(bell(91, 1.5), 12.6, gain=0.8)\n"
    exec(head + bgm + ev + tail, {})
    assert subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                            "-b:a", "192k", "-shortest", out + ".tmp.mp4"]) == 0
    os.replace(out + ".tmp.mp4", out); os.remove(tmp); os.remove(wav)

def build(s, repo, preview_only=False):
    rid = s["id"]; pages = [cover(s), grid(s), last(s)]
    for dd in ("toon", "reels", "posts"): os.makedirs(os.path.join(repo, dd), exist_ok=True)
    urls = []
    for i, im in enumerate(pages, 1):
        fn = f"{rid}_{i}.jpg"; im.save(os.path.join(repo, "toon", fn), quality=92); urls.append(f"{RAW}/toon/{fn}")
    if preview_only: print("pages", rid); return
    reel(s, pages, os.path.join(repo, "reels", f"{rid}_reel.mp4"))
    caption = s["caption_body"].strip() + "\n\n" + CTA + "\n\n" + s["hashtags"]; assert len(caption) <= 2200
    json.dump(dict(id=f"{rid}_carousel", kind="carousel", slot=s["slot_carousel"], image_urls=urls, caption=caption, comment=s["comment"]),
              open(os.path.join(repo, "posts", f"{rid}_carousel.json"), "w"), ensure_ascii=False, indent=1)
    json.dump(dict(id=f"{rid}_reel", kind="reel", slot=s["slot_reel"], video_url=f"{RAW}/reels/{rid}_reel.mp4", thumb_offset=500,
                   caption=caption, comment=s["comment"]), open(os.path.join(repo, "posts", f"{rid}_reel.json"), "w"), ensure_ascii=False, indent=1)
    print("built", rid)

if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2], preview_only=len(sys.argv) > 3)
