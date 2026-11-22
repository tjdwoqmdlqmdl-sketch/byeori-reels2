"""내일의 띠별 운세 릴스: python3 day_kit.py <대상 날짜 YYYY-MM-DD> <slot ISO> <repo_dir>
근거: 그날 일진(日辰) 지지와 각 띠의 관계 — 육합·삼합=행운, 충=조심, 같은 지지=내 띠의 날, 그 외=무난.
브랜드 카드(라벨 칩 12개 2열) 정지 화면 15초 + BGM. list_kit의 영상·게시 파이프라인 재사용.
"""
import os, sys, json, datetime as dt
KIT = os.path.dirname(os.path.abspath(__file__)); os.chdir(KIT); sys.path.insert(0, KIT)
from PIL import ImageDraw
import list_kit
from week_kit import day_ganji, TTI, YUKHAP, SAMHAP, BR, DOW
from toon_kit import FT, fit, C
from render import base, text, pill, put_char, YEL, WHITE, DARK

GOOD6 = ["짝꿍 기운, 고백·협상 굿", "부탁하면 술술 풀리는 날", "미뤄둔 연락 먼저 해봐"]
GOOD3 = ["팀플레이가 빛나는 날", "모임·소개팅 운 상승", "같이 하면 두 배로 풀림"]
BAD = ["큰 결정은 내일로 미루기", "감정 소비 금지, 일찍 귀가", "말은 한 템포 늦게"]
SAME = "내 띠의 날, 내 페이스대로"
OK = ["루틴대로 가면 충분해", "작은 정리 하기 좋은 날", "컨디션 관리 데이"]

def rows_for(d):
    gz, x = day_ganji(d); rows = []
    for bh, nm, el in TTI:
        b = BR.index(bh); k = (b + d.day) % 3
        if x == YUKHAP[b]: st, msg = "행운 ★ 육합", GOOD6[k]
        elif x != b and any(b in s and x in s for s in SAMHAP): st, msg = "행운 ★ 삼합", GOOD3[k]
        elif (x - b) % 12 == 6: st, msg = "조심 △ 충", BAD[k]
        elif x == b: st, msg = "내 띠의 날", SAME
        else: st, msg = "무난", OK[k]
        rows.append((bh, nm, el, st, msg))
    return gz, rows

def make_card(d, gz, rows):
    def card(s):
        img = base(0.6); dr = ImageDraw.Draw(img); W = 1080
        pill(img, W / 2, 150, 560, 88, (255, 112, 150)); text(img, (W / 2, 146), "별이 · 내일의 띠별 운세", 42, WHITE, DARK, 6)
        text(img, (W / 2, 290), f"{d.month}/{d.day} ({DOW[d.weekday()]}) 띠별 운세", 84, YEL, DARK, 12)
        text(img, (W / 2, 395), f"내일 일진: {gz}일", 52, WHITE, DARK, 8)
        for i, (bh, nm, el, st, msg) in enumerate(rows):
            col, row = i % 2, i // 2; x0 = 40 + col * 510; y0 = 470 + row * 180
            good = st.startswith("행운"); bad = st.startswith("조심")
            dr.rounded_rectangle([x0, y0, x0 + 490, y0 + 165], 30, fill=(255, 250, 238), outline=(220, 70, 130) if good else DARK, width=7 if good else 4)
            cx, cy = x0 + 75, y0 + 82
            dr.ellipse([cx - 52, cy - 52, cx + 52, cy + 52], fill=WHITE, outline=DARK, width=4); dr.ellipse([cx - 45, cy - 45, cx + 45, cy + 45], fill=C[el])
            text(img, (cx, cy - 4), bh, 56, WHITE, DARK, 6)
            dr.text((x0 + 148, y0 + 40), nm, font=FT("Black", 38), fill=(40, 30, 60), anchor="lm")
            dr.text((x0 + 148 + dr.textlength(nm, font=FT("Black", 38)) + 14, y0 + 42), st, font=FT("Black", 30),
                    fill=(220, 70, 130) if good else ((60, 110, 200) if bad else (120, 105, 150)), anchor="lm")
            dr.text((x0 + 148, y0 + 108), msg, font=FT("Bold", fit(dr, msg, 330, "Bold", 32)), fill=(40, 30, 60), anchor="lm")
        pill(img, W / 2, 1600, 760, 110, (255, 112, 150)); text(img, (W / 2, 1596), "팔로우하면 매일 내일 운세 알림", 46, WHITE, DARK, 7)
        pill(img, W / 2, 1725, 820, 96, (255, 250, 235)); text(img, (W / 2, 1721), "내 운세 티어는 프로필 링크 클릭!", 44, DARK, (255, 255, 255), 0)
        dr = ImageDraw.Draw(img); dr.text((W / 2, 1855), "※ 재미로 보는 운세입니다 · 일진 기준 · 띠는 입춘 기준", font=FT("Medium", 28), fill=WHITE, anchor="mm")
        return img.convert("RGB")
    return card

if __name__ == "__main__":
    d = dt.date.fromisoformat(sys.argv[1]); slot = sys.argv[2]; repo = sys.argv[3]
    gz, rows = rows_for(d)
    list_kit.card = make_card(d, gz, rows)
    good = [r[1] for r in rows if r[3].startswith("행운")]; bad = [r[1] for r in rows if r[3].startswith("조심")]
    body = (f"내일 {d.month}/{d.day}({DOW[d.weekday()]}) 띠별 운세 ⭐ 일진 {gz}일\n"
            f"★ 행운: {', '.join(good) or '-'}\n△ 조심: {', '.join(bad) or '-'}\n"
            "합(合)이 되는 띠는 부탁·약속·고백 잡기 좋고, 충(沖)인 띠는 큰 결정만 하루 미루면 돼!\n"
            "내 띠 친구 태그해서 내일 같이 체크하자 👇 (띠는 입춘 기준)")
    spec = dict(id=f"day_{d:%m%d}", slot=slot, title="", items=[], note="", caption_body=body,
                hashtags="#내일의운세 #띠별운세 #오늘의운세 #일진 #운세 #사주 #띠 #2027운세 #별이운세",
                comment="내일 행운인 사람 손! ✋ 조심인 사람은 같이 버티자 💪")
    list_kit.CTA = "👉 팔로우하면 매일 저녁 내일 운세 올려줄게!\n🔗 내 운세 티어는 프로필 링크에서 바로 확인해봐\n※ 재미로 보는 운세야 (일진 기준)"
    list_kit.build(spec, repo)
    print(gz, [(r[1], r[3]) for r in rows])
