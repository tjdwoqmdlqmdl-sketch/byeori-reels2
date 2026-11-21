"""리스트 릴스(별이 브랜드 카드형, 캡처형 아님): python3 list_kit.py <list.json> <repo_dir>
list.json: id, slot, title, items[str], note, caption_body, hashtags, comment
출력: reels/<id>.mp4 (15초, 정지 카드 + 아주 느린 줌 + BGM), covers/<id>.jpg, posts/<id>.json
좋아요·댓글 수 같은 가짜 반응 숫자나 인증 배지는 넣지 않는다.
"""
import os, sys, json, subprocess
KIT = os.path.dirname(os.path.abspath(__file__)); os.chdir(KIT); sys.path.insert(0, KIT)
from PIL import Image, ImageDraw
from render import CH, sparkle
from toon_kit import FT, fit, RAW

W, H, FPS = 1080, 1920, 30
BGC, FG, SUB, ACC = (12, 10, 18), (240, 238, 246), (150, 144, 168), (255, 140, 180)
CTA = ("👉 팔로우하면 매일 2027 운세 리스트 올려줄게!\n"
       "🔗 내 운세 티어는 프로필 링크에서 바로 확인해봐\n"
       "※ 재미로 보는 운세야 (전통 사주 해석 기준)")

def wrap(d, s, font, maxw):
    out, cur = [], ""
    for ch in s:
        if d.textlength(cur + ch, font=font) > maxw and cur:
            cut = cur.rfind(" ")
            if cut > len(cur) * 0.5: out.append(cur[:cut]); cur = cur[cut + 1:] + ch
            else: out.append(cur); cur = ch
        else: cur += ch
    if cur: out.append(cur)
    return out

def card(s):
    # 별이 브랜드 리스트 카드 (스레드 캡처형 아님): 라벤더 배경 + 분홍 태그 + 큰 제목 + 크림색 항목 카드 + 별이
    from render import base, text, pill, put_char, YEL, WHITE, DARK
    img = base(0.6); d = ImageDraw.Draw(img); x0 = 60
    pill(img, W / 2, 170, 620, 92, (255, 112, 150)); text(img, (W / 2, 166), s.get("tag", "2027 정미년 · 별이 리스트"), 44, WHITE, DARK, 6)
    title = s["title"].strip("<>")
    tf = FT("Black", 76); lines = wrap(d, title, tf, W - 2 * x0)
    y = 290
    for i, ln in enumerate(lines):
        text(img, (W / 2, y), ln, 76, YEL if i == len(lines) - 1 else WHITE, DARK, 11); y += 100
    y += 20
    f = FT("Bold", 40)
    for i, it in enumerate(s["items"], 1):
        ls = wrap(d, it, f, W - 2 * x0 - 150); h = 58 * len(ls) + 44
        d.rounded_rectangle([x0, y, W - x0, y + h], 32, fill=(255, 250, 238), outline=DARK, width=5)
        cx, cy = x0 + 62, y + h / 2
        d.ellipse([cx - 38, cy - 38, cx + 38, cy + 38], fill=(255, 112, 150), outline=DARK, width=4)
        d.text((cx, cy - 2), str(i), font=FT("Black", 44), fill=WHITE, anchor="mm")
        for j, ln in enumerate(ls): d.text((x0 + 130, y + 22 + j * 58), ln, font=f, fill=(40, 30, 60))
        y += h + 18
    y += 10
    for ln in wrap(d, s["note"], FT("Bold", 32), W - 2 * x0):
        d.text((W / 2, y + 20), ln, font=FT("Bold", 32), fill=(70, 40, 110), anchor="mm"); y += 46
    y += 50
    assert y < 1560, "글이 너무 길어요: 항목 수나 길이를 줄이세요"
    pill(img, W / 2, 1620, 760, 110, (255, 112, 150)); text(img, (W / 2, 1616), "팔로우하고 다음 리스트 보기", 50, WHITE, DARK, 7)
    pill(img, W / 2, 1745, 820, 96, (255, 250, 235)); text(img, (W / 2, 1741), "내 운세 티어는 프로필 링크 클릭!", 44, DARK, (255, 255, 255), 0)
    put_char(img, "wink", 965, 1560, 190, rot=8)
    d = ImageDraw.Draw(img)
    d.text((W / 2, H - 60), "※ 재미로 보는 운세입니다 · 전통 사주 해석 기준", font=FT("Medium", 28), fill=WHITE, anchor="mm")
    return img.convert("RGB")

def build(s, repo):
    rid = s["id"]
    for dd in ("reels", "covers", "posts"): os.makedirs(os.path.join(repo, dd), exist_ok=True)
    img = card(s); img.save(os.path.join(repo, "covers", f"{rid}.jpg"), quality=92)
    tmp = os.path.join(KIT, f"_{rid}.v.mp4")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmp], stdin=subprocess.PIPE)
    for fr in range(15 * FPS):
        z = 1 + 0.025 * fr / (15 * FPS); im = img.resize((int(W * z), int(H * z)), Image.BILINEAR)
        l, t = (im.width - W) // 2, (im.height - H) // 2
        p.stdin.write(im.crop((l, t, l + W, t + H)).tobytes())
    p.stdin.close(); assert p.wait() == 0
    src = open(os.path.join(KIT, "audio.py")).read()
    head = src.split("BPM = 124")[0].replace("DUR = 30.0", "DUR = 15.0").replace("os.chdir(os.path.dirname(os.path.abspath(__file__)))", "pass")
    bgm = "BPM = 124" + src.split("BPM = 124")[1].split("# SFX")[0]
    wav = os.path.join(KIT, f"_{rid}.wav"); tail = ("# fades" + src.split("# fades")[1]).replace('"audio.wav"', repr(wav))
    exec(head + bgm + "add(pop(), 0.05, gain=0.6)\n" + tail, {})
    out = os.path.join(repo, "reels", f"{rid}.mp4")
    assert subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy", "-c:a", "aac",
                            "-b:a", "192k", "-shortest", out + ".tmp.mp4"]) == 0
    os.replace(out + ".tmp.mp4", out); os.remove(tmp); os.remove(wav)
    caption = s["caption_body"].strip() + "\n\n" + CTA + "\n\n" + s["hashtags"]; assert len(caption) <= 2200
    json.dump(dict(id=rid, kind="reel", slot=s["slot"], video_url=f"{RAW}/reels/{rid}.mp4", cover_url=f"{RAW}/covers/{rid}.jpg",
                   caption=caption, comment=s["comment"]), open(os.path.join(repo, "posts", f"{rid}.json"), "w"), ensure_ascii=False, indent=1)
    print("built", rid)

if __name__ == "__main__":
    build(json.load(open(sys.argv[1])), sys.argv[2])
