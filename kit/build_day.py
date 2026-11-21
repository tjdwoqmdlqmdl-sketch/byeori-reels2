"""하루치 릴스 빌드: python3 build_day.py <day.json> <repo_dir>
day.json = {"reels": [ {id, slot, header, hook[3], card_d, cards[[hanja,name,element,[l1,l2]]], tip|null, tip_d,
             foot, outro?[a,b], cover{tag,l1,l2,chips[[hj,el]]}, caption_body, save_line, hashtags, comment} ]}
출력: <repo>/reels/<id>.mp4, <repo>/covers/<id>.jpg, <repo>/posts/<id>.json
"""
import sys, os, json, subprocess, shutil
KIT = os.path.dirname(os.path.abspath(__file__)); os.chdir(KIT); sys.path.insert(0, KIT)
import reels, cover
from render import W, H, FPS

RAW = "https://raw.githubusercontent.com/tjdwoqmdlqmdl-sketch/byeori-reels2/main"
CTA = ("👉 팔로우하면 2027 띠별·일간별 운세 계속 올려줄게!\n"
       "🔗 내 운세 티어는 프로필 링크에서 바로 확인해봐\n"
       "※ 재미로 보는 운세야 (전통 사주 해석 기준)")

def audio(spec, out):
    src = open(os.path.join(KIT, "audio.py")).read()
    head = src.split("BPM = 124")[0].replace("DUR = 30.0", "DUR = 15.0").replace("os.chdir(os.path.dirname(os.path.abspath(__file__)))", "pass")
    bgm = "BPM = 124" + src.split("BPM = 124")[1].split("# SFX")[0]
    tail = ("# fades" + src.split("# fades")[1]).replace('"audio.wav"', repr(out))
    tl = reels.timeline(spec); n = len(spec["cards"])
    ev = "add(whoosh(0.5), 0.0, gain=0.5); add(pop(), 0.1, gain=0.8)\n"
    for i in range(n):
        T0 = tl["c0"] + i * spec["card_d"]
        ev += f"add(whoosh(0.35), {T0}, gain=0.4); add(pop(), {T0 + 0.05}, gain=0.8); add(bell([72,76,79,84,88][{i}%5], 1.2), {T0 + 0.3}, gain=0.8)\n"
    if spec.get("tip"): ev += f"add(sweep(0.6), {tl['t0']}, gain=0.7); add(bell(91, 1.5), {tl['t0'] + 0.2}, gain=0.8)\n"
    o = tl["o0"]
    ev += f"add(whoosh(0.4), {o}, gain=0.45); add(pop(), {o + 0.1}, gain=0.8); add(bell(91, 1.8), {o + 0.1}, gain=0.7)\n"
    ev += f"add(marimba(84, 1.0), {o + 0.5}, gain=0.8); add(marimba(88, 1.0), {o + 0.7}, gain=0.8); add(marimba(91, 1.2), {o + 0.9}, gain=0.9)\n"
    exec(head + bgm + ev + tail, {})

def build(spec, repo):
    rid = spec["id"]; spec.setdefault("tip_d", 0); spec.setdefault("foot", " · 전통 사주 해석 기준")
    if spec.get("tip"): spec["tip"] = tuple(spec["tip"])
    if spec.get("outro"): spec["outro"] = tuple(spec["outro"])
    spec["cards"] = [tuple(c) for c in spec["cards"]]
    fn = reels.make_fn(spec)
    tmpv = os.path.join(KIT, f"_{rid}.v.mp4"); wav = os.path.join(KIT, f"_{rid}.wav")
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{W}x{H}", "-r", str(FPS), "-i", "-",
                          "-c:v", "libx264", "-crf", "18", "-preset", "veryfast", "-pix_fmt", "yuv420p", tmpv], stdin=subprocess.PIPE)
    for f in range(int(15 * FPS)): p.stdin.write(fn(f / FPS).convert("RGB").tobytes())
    p.stdin.close(); assert p.wait() == 0
    audio(spec, wav)
    for d in ("reels", "covers", "posts"): os.makedirs(os.path.join(repo, d), exist_ok=True)
    out = os.path.join(repo, "reels", f"{rid}.mp4")
    assert subprocess.call(["ffmpeg", "-y", "-loglevel", "error", "-i", tmpv, "-i", wav, "-map", "0:v", "-map", "1:a", "-c:v", "copy",
                            "-c:a", "aac", "-b:a", "192k", "-shortest", out + ".tmp.mp4"]) == 0
    os.replace(out + ".tmp.mp4", out); os.remove(tmpv); os.remove(wav)
    c = spec["cover"]; cover.COVERS[rid] = dict(tag=c["tag"], l1=c["l1"], l2=c["l2"], chips=[tuple(x) for x in c["chips"]])
    cover.cover(rid).convert("RGB").save(os.path.join(repo, "covers", f"{rid}.jpg"), quality=92)
    caption = spec["caption_body"].strip() + "\n\n" + spec.get("save_line", "저장해 두고 1월에 다시 봐 ⭐") + "\n" + CTA + "\n\n" + spec["hashtags"]
    assert len(caption) <= 2200
    json.dump(dict(id=rid, slot=spec["slot"], video_url=f"{RAW}/reels/{rid}.mp4", cover_url=f"{RAW}/covers/{rid}.jpg",
                   caption=caption, comment=spec["comment"]), open(os.path.join(repo, "posts", f"{rid}.json"), "w"), ensure_ascii=False, indent=1)
    print("built", rid)

if __name__ == "__main__":
    day = json.load(open(sys.argv[1])); repo = sys.argv[2]
    only = sys.argv[3] if len(sys.argv) > 3 else None
    for s in day["reels"]:
        if only is None or s["id"] == only: build(s, repo)
