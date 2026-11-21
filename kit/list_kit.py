"""리스트 릴스(스레드 글 화면형): python3 list_kit.py <list.json> <repo_dir>
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
    img = Image.new("RGB", (W, H), BGC); d = ImageDraw.Draw(img)
    x0, y = 70, 300
    av = Image.new("RGBA", (96, 96), (0, 0, 0, 0)); ImageDraw.Draw(av).ellipse([0, 0, 95, 95], fill=(196, 168, 240))
    ch = CH["open"].copy(); ch.thumbnail((78, 78), Image.LANCZOS); av.paste(ch, (48 - ch.width // 2, 52 - ch.height // 2), ch)
    m = Image.new("L", (96, 96), 0); ImageDraw.Draw(m).ellipse([0, 0, 95, 95], fill=255); img.paste(av, (x0, y), m)
    d.text((x0 + 120, y + 30), "byeori.fortune_", font=FT("Bold", 40), fill=FG, anchor="lm")
    d.text((x0 + 120, y + 74), "별이 운세 · 2027 정미년", font=FT("Medium", 30), fill=SUB, anchor="lm")
    y += 160
    tf = FT("Black", fit(d, s["title"], W - 2 * x0, "Black", 50))
    for ln in wrap(d, s["title"], tf, W - 2 * x0): d.text((x0, y), ln, font=tf, fill=FG); y += 70
    y += 30
    f = FT("Medium", 40)
    for i, it in enumerate(s["items"], 1):
        lines = wrap(d, f"{i}. {it}", f, W - 2 * x0)
        for j, ln in enumerate(lines): d.text((x0 + (0 if j == 0 else 44), y), ln, font=f, fill=FG); y += 58
        y += 14
    y += 20
    for ln in wrap(d, s["note"], FT("Medium", 32), W - 2 * x0): d.text((x0, y), ln, font=FT("Medium", 32), fill=SUB); y += 46
    y += 40
    d.rounded_rectangle([x0, y, W - x0, y + 150], 28, fill=(32, 26, 46))
    d.text((W / 2, y + 48), "팔로우하면 매일 2027 운세 리스트", font=FT("Bold", 38), fill=ACC, anchor="mm")
    d.text((W / 2, y + 104), "내 운세 티어는 프로필 링크 클릭!", font=FT("Bold", 36), fill=FG, anchor="mm")
    assert y + 150 < H - 120, "글이 너무 길어요: 항목 수나 길이를 줄이세요"
    d.text((W / 2, H - 70), "※ 재미로 보는 운세입니다 · 전통 사주 해석 기준", font=FT("Medium", 26), fill=SUB, anchor="mm")
    return img

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
