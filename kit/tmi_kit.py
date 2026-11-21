"""일간 TMI 캐러셀: python3 tmi_kit.py <tmi.json> <repo_dir>
tmi.json: id, no(탄 번호), slot, title(예: '별이의 일간 TMI'), sub, items[10] = [hanja, name, element, line1, line2], question, caption_body, hashtags, comment
4장(1080x1350): 표지 / 1~5 / 6~10 / 질문+CTA
"""
import os, sys, json
KIT = os.path.dirname(os.path.abspath(__file__)); os.chdir(KIT); sys.path.insert(0, KIT)
from PIL import ImageDraw
from toon_kit import bg, FT, fit, T, TW, TH, RAW, C
from render import put_char, sparkle, text, pill, YEL, WHITE, DARK

CTA = ("👉 팔로우하면 일간 TMI·2027 운세 계속 올려줄게!\n"
       "🔗 내 운세 티어는 프로필 링크에서 바로 확인해봐\n"
       "※ 재미로 보는 운세야 (일간 상징 기반 해석)")

def frame(img, no, page):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 36, 400, 96], 30, fill=(255, 112, 150))
    d.text((220, 66), f"일간 TMI {no}탄 · 별이 운세", font=FT("Bold", 30), fill=WHITE, anchor="mm")
    d.text((TW - 50, 66), f"{page}/4", font=FT("Bold", 32), fill=WHITE, anchor="rm")
    d.text((TW / 2, TH - 34), "※ 재미로 보는 운세입니다 · 일간 상징 기반 해석", font=FT("Medium", 26), fill=(235, 225, 255), anchor="mm")

def chip(img, x, y, r, hj, el):
    d = ImageDraw.Draw(img)
    d.ellipse([x - r - 6, y - r - 6, x + r + 6, y + r + 6], fill=WHITE, outline=DARK, width=5)
    d.ellipse([x - r, y - r, x + r, y + r], fill=C[el]); text(img, (x, y - 4), hj, int(r * 1.15), WHITE, DARK, 6)

def pages(s):
    no = s["no"]; out = []
    img = bg(True); d = ImageDraw.Draw(img)
    for k in range(16): sparkle(d, (k * 263) % TW, 130 + (k * 397) % 1100, 10 + k % 4 * 4, (255, 230, 150))
    T(img, (TW / 2, 250), s["title"], 104, YEL, sw=14); T(img, (TW / 2, 390), f"{no}탄", 120, WHITE, sw=14)
    T(img, (TW / 2, 510), s["sub"], 50, WHITE, sw=8)
    for i, (hj, nm, el, *_r) in enumerate(s["items"]):
        x = TW / 2 + ((i % 5) - 2) * 170; y = 660 + (i // 5) * 160; chip(img, x, y, 62, hj, el)
    put_char(img, "open", TW / 2, 1100, 330, rot=-5); frame(img, no, 1); out.append(img)
    for pg, chunk in enumerate((s["items"][:5], s["items"][5:])):
        img = bg(); d = ImageDraw.Draw(img)
        for j, (hj, nm, el, l1, l2) in enumerate(chunk):
            y = 200 + j * 215; n = pg * 5 + j + 1
            d.rounded_rectangle([60, y - 90, TW - 60, y + 95], 36, fill=(255, 250, 238), outline=DARK, width=5)
            chip(img, 160, y, 62, hj, el)
            d.text((250, y - 48), f"{n}. {nm}", font=FT("Black", 44), fill=(170, 60, 130), anchor="lm")
            d.text((250, y + 8), l1, font=FT("Bold", fit(d, l1, 740, "Bold", 38)), fill=(40, 30, 60), anchor="lm")
            d.text((250, y + 56), l2, font=FT("Bold", fit(d, l2, 740, "Bold", 38)), fill=(40, 30, 60), anchor="lm")
        frame(img, no, 2 + pg); out.append(img)
    img = bg(); d = ImageDraw.Draw(img)
    T(img, (TW / 2, 240), s["question"], 84, WHITE, sw=12); T(img, (TW / 2, 360), "맞으면 ⭕ 아니면 ❌".replace("⭕", "O").replace("❌", "X"), 70, YEL, sw=10)
    put_char(img, "wink", TW / 2, 700, 420, rot=-5)
    pill(img, TW / 2, 1010, 760, 110, (255, 112, 150)); text(img, (TW / 2, 1006), f"팔로우하고 {no + 1}탄 보기", 52)
    pill(img, TW / 2, 1140, 820, 96, (255, 250, 235)); text(img, (TW / 2, 1136), "내 운세 티어는 프로필 링크 클릭!", 44, DARK, (255, 255, 255), 0)
    frame(img, no, 4); out.append(img)
    return out

def build(s, repo):
    rid = s["id"]; os.makedirs(os.path.join(repo, "toon"), exist_ok=True); os.makedirs(os.path.join(repo, "posts"), exist_ok=True)
    urls = []
    for i, im in enumerate(pages(s), 1):
        fn = f"{rid}_{i}.jpg"; im.convert("RGB").save(os.path.join(repo, "toon", fn), quality=92); urls.append(f"{RAW}/toon/{fn}")
    caption = s["caption_body"].strip() + "\n\n" + CTA + "\n\n" + s["hashtags"]; assert len(caption) <= 2200
    json.dump(dict(id=rid, kind="carousel", slot=s["slot"], image_urls=urls, caption=caption, comment=s["comment"]),
              open(os.path.join(repo, "posts", f"{rid}.json"), "w"), ensure_ascii=False, indent=1)
    print("built", rid)

if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
