"""주간 띠별·별자리 운세 캐러셀: python3 week_kit.py <tti|star> <월요일 YYYY-MM-DD> <slot ISO> <repo_dir>
근거(계산):
 - 띠별: 그 주 7일의 일진(日辰) 지지와 내 띠의 관계. 육합·삼합=행운의 날, 충=조심할 날, 같은 지지=내 날.
   일진 = (JDN + 49) mod 60 (0=甲子). 2000-01-01 = 戊午 로 검증.
 - 별자리: 그 주 매일 정오(KST)의 달 별자리(저정밀 달 황경 공식, 오차 1~2도).
   같은 원소 별자리·내 별자리에 달=행운의 날, 정반대 별자리에 달=조심할 날.
5장 캐러셀(1080x1350): 표지 / 4개씩 3장 / 질문+CTA
"""
import os, sys, json, math, datetime as dt
KIT = os.path.dirname(os.path.abspath(__file__)); os.chdir(KIT); sys.path.insert(0, KIT)
from PIL import ImageDraw
from toon_kit import bg, FT, fit, T, TW, TH, RAW, C
from render import put_char, sparkle, text, pill, YEL, WHITE, DARK

DOW = "월화수목금토일"
STEM = "甲乙丙丁戊己庚辛壬癸"; BR = "子丑寅卯辰巳午未申酉戌亥"
TTI = [("子", "쥐띠", "수"), ("丑", "소띠", "토"), ("寅", "호랑이띠", "목"), ("卯", "토끼띠", "목"), ("辰", "용띠", "토"), ("巳", "뱀띠", "화"),
       ("午", "말띠", "화"), ("未", "양띠", "토"), ("申", "원숭이띠", "금"), ("酉", "닭띠", "금"), ("戌", "개띠", "토"), ("亥", "돼지띠", "수")]
YUKHAP = {0: 1, 1: 0, 2: 11, 11: 2, 3: 10, 10: 3, 4: 9, 9: 4, 5: 8, 8: 5, 6: 7, 7: 6}
SAMHAP = [{8, 0, 4}, {11, 3, 7}, {2, 6, 10}, {5, 9, 1}]
SIGNS = [("♈", "양자리", "fire"), ("♉", "황소자리", "earth"), ("♊", "쌍둥이자리", "air"), ("♋", "게자리", "water"), ("♌", "사자자리", "fire"), ("♍", "처녀자리", "earth"),
         ("♎", "천칭자리", "air"), ("♏", "전갈자리", "water"), ("♐", "사수자리", "fire"), ("♑", "염소자리", "earth"), ("♒", "물병자리", "air"), ("♓", "물고기자리", "water")]
EL_KO = {"fire": "불", "earth": "흙", "air": "바람", "water": "물"}
EL_COL = {"fire": "화", "earth": "토", "air": "금", "water": "수"}
SIGN_DATES = ["3/21~4/19", "4/20~5/20", "5/21~6/21", "6/22~7/22", "7/23~8/22", "8/23~9/22", "9/23~10/22", "10/23~11/22", "11/23~12/24", "12/25~1/19", "1/20~2/18", "2/19~3/20"]

def jdn(d): return d.toordinal() + 1721425
def day_ganji(d): i = (jdn(d) + 49) % 60; return STEM[i % 10] + BR[i % 12], i % 12
assert day_ganji(dt.date(2000, 1, 1))[0] == "戊午"

def moon_sign(d):
    jd = jdn(d) - 0.5 + 3 / 24  # KST 정오 = UT 03시
    n = jd - 2451545.0
    L = 218.316 + 13.176396 * n; M = math.radians(134.963 + 13.064993 * n)
    lam = (L + 6.289 * math.sin(M)) % 360
    return int(lam // 30)

def md(d): return f"{DOW[d.weekday()]}({d.month}/{d.day})"

def tti_rows(mon):
    days = [mon + dt.timedelta(i) for i in range(7)]; br = [day_ganji(d)[1] for d in days]; rows = []
    for bh, nm, el in TTI:
        b = BR.index(bh)
        good = [d for d, x in zip(days, br) if x == YUKHAP[b] or (x != b and any(b in s and x in s for s in SAMHAP))]
        bad = [d for d, x in zip(days, br) if (x - b) % 12 == 6]; mine = [d for d, x in zip(days, br) if x == b]
        g = good[0] if good else (mine[0] if mine else None); c = bad[0] if bad else None
        l1 = (f"행운 {md(g)}" if g else "무난한 한 주") + (f" · 조심 {md(c)}" if c else "")
        if good:
            x = br[days.index(good[0])]
            if x == YUKHAP[b]: l2 = ["짝꿍 기운 육합(六合), 고백·협상 잡기 좋은 날", "육합의 날, 미뤄둔 연락 먼저 해봐", "육합이라 부탁하면 술술 풀리는 날"][b % 3]
            else: l2 = ["삼합(三合)의 날, 모임·협업에서 빛나", "삼합이라 팀으로 움직이면 이득인 날", "삼합의 날, 소개받기·새 인연에 강해"][b % 3]
        elif mine: l2 = "내 띠의 날이 있는 주, 내 페이스대로 밀고 가기"
        else: l2 = "큰 합·충 없는 주, 루틴만 지켜도 충분해"
        if c: l2 = l2 + " (충 날엔 말 조심)" if len(l2) < 24 else l2
        rows.append((bh, nm, el, l1, l2))
    return rows, " ".join(day_ganji(d)[0] for d in days)

def star_rows(mon):
    days = [mon + dt.timedelta(i) for i in range(7)]; ms = [moon_sign(d) for d in days]; rows = []
    for k, (sym, nm, el) in enumerate(SIGNS):
        good = [d for d, m in zip(days, ms) if m == k or SIGNS[m][2] == el]; bad = [d for d, m in zip(days, ms) if (m - k) % 12 == 6]
        l1 = (f"행운 {md(good[0])}" if good else "무난한 한 주") + (f" · 조심 {md(bad[0])}" if bad else "")
        if good:
            m = ms[days.index(good[0])]
            l2 = f"달이 {SIGNS[m][1]}에 오는 날, {EL_KO[el]}의 기운이 통해서 일이 술술" if m != k else "달이 내 별자리에 오는 날, 존재감 최고"
        else: l2 = "같은 원소 날이 없는 주, 무리한 약속은 다음 주로"
        rows.append((sym, nm, EL_COL[el], l1, l2, SIGN_DATES[k]))
    return rows, " ".join(SIGNS[m][1].replace("자리", "") for m in ms)

def frame(img, label, page, total):
    d = ImageDraw.Draw(img)
    d.rounded_rectangle([40, 36, 430, 96], 30, fill=(255, 112, 150)); d.text((235, 66), label, font=FT("Bold", 30), fill=WHITE, anchor="mm")
    d.text((TW - 50, 66), f"{page}/{total}", font=FT("Bold", 32), fill=WHITE, anchor="rm")

def chip(img, x, y, r, s, el, star=False):
    d = ImageDraw.Draw(img)
    d.ellipse([x - r - 6, y - r - 6, x + r + 6, y + r + 6], fill=WHITE, outline=DARK, width=5); d.ellipse([x - r, y - r, x + r, y + r], fill=C[el])
    if star: d.text((x, y), s, font=FT("Black", int(r * 0.55)), fill=WHITE, anchor="mm", stroke_width=4, stroke_fill=DARK)
    else: text(img, (x, y - 4), s, int(r * 1.15), WHITE, DARK, 6)

def build(kind, mon, slot, repo):
    sun = mon + dt.timedelta(6); rng = f"{mon.month}/{mon.day}~{sun.month}/{sun.day}"
    if kind == "tti": rows, basis = tti_rows(mon); title, label, foot = "이번 주 띠별 운세", "주간 띠별 운세 · 별이", "근거: 이번 주 일진 " + basis
    else: rows, basis = star_rows(mon); title, label, foot = "이번 주 별자리 운세", "주간 별자리 운세 · 별이", "근거: 매일 달의 별자리 " + basis
    pages = []; total = 5
    img = bg(True); d = ImageDraw.Draw(img)
    for k in range(16): sparkle(d, (k * 263) % TW, 130 + (k * 397) % 1100, 10 + k % 4 * 4, (255, 230, 150))
    T(img, (TW / 2, 260), title, 104, YEL, sw=14); T(img, (TW / 2, 390), rng, 96, WHITE, sw=12)
    T(img, (TW / 2, 500), "행운의 날 · 조심할 날 한 번에 체크!", 46, WHITE, sw=7)
    for i, r in enumerate(rows):
        x = TW / 2 + ((i % 6) - 2.5) * 150; y = 650 + (i // 6) * 150
        chip(img, x, y, 56, r[0] if kind == "tti" else r[1].replace("자리", ""), r[2], star=(kind == "star"))
    put_char(img, "open", TW / 2, 1080, 300, rot=-5); frame(img, label, 1, total); pages.append(img)
    for pg in range(3):
        img = bg(); d = ImageDraw.Draw(img)
        for j, r in enumerate(rows[pg * 4:(pg + 1) * 4]):
            y = 230 + j * 270
            d.rounded_rectangle([50, y - 110, TW - 50, y + 120], 36, fill=(255, 250, 238), outline=DARK, width=5)
            chip(img, 150, y, 62, r[0] if kind == "tti" else r[1].replace("자리", ""), r[2], star=(kind == "star"))
            name = r[1] + (f" ({r[5]})" if kind == "star" else "")
            d.text((245, y - 62), name, font=FT("Black", fit(d, name, 760, "Black", 44)), fill=(170, 60, 130), anchor="lm")
            d.text((245, y - 4), r[3], font=FT("Bold", fit(d, r[3], 760, "Bold", 38)), fill=(60, 40, 110), anchor="lm")
            d.text((245, y + 56), r[4], font=FT("Medium", fit(d, r[4], 760, "Medium", 34)), fill=(40, 30, 60), anchor="lm")
        d.text((TW / 2, TH - 70), foot, font=FT("Medium", fit(d, foot, 980, "Medium", 24)), fill=(235, 225, 255), anchor="mm")
        frame(img, label, 2 + pg, total); pages.append(img)
    img = bg(); d = ImageDraw.Draw(img)
    T(img, (TW / 2, 240), "너는 이번 주 몇 요일이 행운?", 70, WHITE, sw=10); T(img, (TW / 2, 350), "댓글로 남기고 주말에 확인!", 56, YEL, sw=8)
    put_char(img, "wink", TW / 2, 700, 420, rot=-5)
    pill(img, TW / 2, 1010, 760, 110, (255, 112, 150)); text(img, (TW / 2, 1006), "팔로우하고 다음 주도 보기", 52)
    pill(img, TW / 2, 1140, 820, 96, (255, 250, 235)); text(img, (TW / 2, 1136), "내 운세 티어는 프로필 링크 클릭!", 44, DARK, (255, 255, 255), 0)
    d.text((TW / 2, TH - 40), "※ 재미로 보는 운세입니다", font=FT("Medium", 26), fill=WHITE, anchor="mm")
    frame(img, label, 5, total); pages.append(img)
    rid = f"week_{kind}_{mon:%m%d}"; urls = []
    for i, im in enumerate(pages, 1):
        fn = f"{rid}_{i}.jpg"; im.convert("RGB").save(os.path.join(repo, "toon", fn), quality=92); urls.append(f"{RAW}/toon/{fn}")
    body = f"{title} ({rng}) ⭐\n" + "\n".join(f"{r[1]}: {r[3]}" for r in rows)
    body += ("\n\n띠는 입춘 기준이야." if kind == "tti" else "\n\n태양 별자리(생일 기준)로 봐줘.") + "\n" + foot
    cta = "👉 팔로우하면 매주 운세 올려줄게!\n🔗 내 운세 티어는 프로필 링크에서 바로 확인해봐\n※ 재미로 보는 운세야"
    tags = ("#띠별운세 #주간운세 #이번주운세 #오늘의운세 #사주 #운세 #일진 #2027운세 #별이운세" if kind == "tti"
            else "#별자리운세 #주간운세 #이번주운세 #별자리 #점성술 #사수자리 #운세 #오늘의운세 #별이운세")
    caption = body + "\n\n" + cta + "\n\n" + tags; assert len(caption) <= 2200, len(caption)
    json.dump(dict(id=rid, kind="carousel", slot=slot, image_urls=urls, caption=caption,
                   comment="이번 주 내 행운의 날 맞았는지 주말에 댓글로 알려줘! ⭐"),
              open(os.path.join(repo, "posts", f"{rid}.json"), "w"), ensure_ascii=False, indent=1)
    print("built", rid, basis)

if __name__ == "__main__":
    build(sys.argv[1], dt.date.fromisoformat(sys.argv[2]), sys.argv[3], sys.argv[4])
