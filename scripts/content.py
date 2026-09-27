#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
경매 블로그 콘텐츠 생성기 (네이버 블로그 리치 포맷).

레퍼런스(전문 경매 블로그) 구조를 우리 데이터로 재현:
  키워드 → 사건 요약 → 인사말 → 물건 정보(입지·단지) → 단지 정보 표 →
  면적 정보 → 권리 분석 → 시세(실거래) → 매각기일 표 → [적정가·수익 블라인드+댓글] → 마무리 → 태그

프리미엄: 적정 입찰가·예상 순이익·전략가는 HTML에 넣지 않아 개발자도구로도 안 보임(댓글 유도).
데이터 출처: 법원경매정보(물건)·국토부 실거래가(시세)·공동주택 단지정보(세대수·시공사·주차·난방 등).
표준 라이브러리만 사용.
"""
import os, sys, json, re, hashlib, urllib.parse, urllib.request
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")
CONTENT = os.path.join(ROOT, "content")


def _cfg_json(name, default):
    p = os.path.join(DATA, name)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return default
    return default
KST = timezone(timedelta(hours=9))
DAILY_COUNT = 10

# ── 페르소나(원하는 블로그명·닉네임으로 바꾸세요) ─────────────────
_BLOG = _cfg_json("blog-config.json", {})
BLOG_NAME = _BLOG.get("blog_name", "매일경매레터")
NICK = _BLOG.get("nick", "경매노트")
SITE_URL = _BLOG.get("site_url", "https://example.com").rstrip("/")
SITE_NAME = _BLOG.get("site_name", "경매 분석")
ADSENSE = (_BLOG.get("adsense_client") or "").strip()   # ca-pub-XXXXXXXX (비우면 광고 미표시)


def _verdict(sc):
    return ("입찰 적합", "ok") if sc >= 65 else (("조건부", "cond") if sc >= 50 else ("보류", "hold"))


def analysis_card(r):
    """대시보드 스타일 분석 카드(현재 매물 시각화 · 캡쳐 대용) + 사이트 유입."""
    sc = int(r.get("score") or 0)
    vt, vc = _verdict(sc)
    nm = (r.get("apt_name") or r.get("type") or "")
    lq = (r.get("liquidity") or {}).get("grade", "—")
    sp = (r.get("special") or [])[:3]
    badge = "".join('<span class="c-sp">%s</span>' % x for x in sp)
    return ('<a class="acard" href="%s/" target="_blank" rel="noopener">'
            '<div class="c-top"><span class="c-score s-%s">%d</span>'
            '<span class="c-nm">%s</span><span class="c-v v-%s">%s</span></div>'
            '<div class="c-grid">'
            '<div><span>적정 입찰가</span><b class="lock">🔒 프리미엄</b></div>'
            '<div><span>예상 순이익</span><b class="lock">🔒 프리미엄</b></div>'
            '<div><span>낙찰 성공률</span><b>%s</b></div>'
            '<div><span>환금성</span><b>%s등급</b></div></div>'
            '%s<div class="c-cta">%s에서 전체 분석 무료로 보기 ›</div></a>') % (
        SITE_URL, vc, sc, nm, vc, vt, pct(r.get("success_prob")), lq,
        ('<div class="c-badges">%s</div>' % badge if badge else ""), SITE_NAME)


def site_promo():
    return ('<div class="promo"><b>📊 이 물건, %s에서 이렇게 분석했어요</b><br>'
            '전국 경매 물건의 <b>적정 입찰가·예상 배당표·수익률·권리 리스크</b>를 '
            '<a href="%s/" target="_blank" rel="noopener">%s</a>에서 무료로 확인하세요. '
            '반값·마감임박·고수익 테마로 골라볼 수도 있어요.</div>') % (SITE_NAME, SITE_URL, SITE_NAME)


def adsense_slot():
    if not ADSENSE:
        return ""
    return ('<ins class="adsbygoogle" style="display:block;margin:1.4em 0" data-ad-client="%s" '
            'data-ad-format="auto" data-full-width-responsive="true"></ins>'
            '<script async src="https://pagead2.googlesyndication.com/pagead/js/adsbygoogle.js?client=%s" crossorigin="anonymous"></script>'
            '<script>(adsbygoogle=window.adsbygoogle||[]).push({});</script>') % (ADSENSE, ADSENSE)
# ─────────────────────────────────────────────────────────────


def load(n, default=None):
    p = os.path.join(DATA, n)
    return json.load(open(p, encoding="utf-8")) if os.path.exists(p) else default


def today():
    return datetime.now(KST).strftime("%Y-%m-%d")


def won(n):
    if n is None or n == "":
        return "—"
    neg = n < 0
    n = abs(int(round(n)))
    eok, man = n // 10**8, round((n % 10**8) / 10**4)
    s = f"{eok}억 {man:,}만" if eok else f"{man:,}만"
    return ("−" if neg else "") + s + "원"


def pyeong(area):
    return round(area / 3.3058, 1) if area else None


def pct(x):
    return f"{x*100:.0f}%" if x is not None else "—"


def slugify(s):
    return re.sub(r"[^0-9A-Za-z가-힣]+", "-", str(s)).strip("-")[:60]


def dong(a):
    m = re.search(r"([가-힣]+(?:동|읍|면))", a or "")
    return m.group(1) if m else ""


def pname(r):
    return (r.get("apt_name") or "").strip() or dong(r.get("address")) or r.get("type") or "물건"


def _seed(s):
    return int(hashlib.md5(str(s).encode()).hexdigest(), 16)


def _pick(pool, seed, salt=0):
    return pool[(seed + salt) % len(pool)]


def y(d):  # YYYYMMDD/YYYY-MM-DD → YYYY년
    d = str(d or "")
    m = re.search(r"((?:19|20)\d{2})", d)
    return m.group(1) + "년" if m else "—"


LOCK = '<span class="lock">🔒 블라인드</span>'

# 법원 사진: 법원명 -> 이미지 URL. 라이선스 확인 후 직접 채우세요(비우면 표시 안 됨).
COURT_PHOTOS = {
    # "수원지방법원": "https://.../suwon-court.jpg",
}


def img(url, cap=""):
    if not url:
        return ""
    c = ('<div class="cap">%s</div>' % cap) if cap else ""
    return '<figure class="photo"><img src="%s" alt="%s" loading="lazy">%s</figure>' % (url, cap, c)


def gallery(urls, cap=""):
    urls = [u for u in (urls or []) if u]
    if not urls:
        return ""
    imgs = "".join('<img src="%s" alt="" loading="lazy">' % u for u in urls[:6])
    c = ('<div class="cap">%s</div>' % cap) if cap else ""
    return '<div class="gallery">%s</div>%s' % (imgs, c)


# ── 사진 자동 수집: 네이버 이미지 검색 API (공식) ──────────────
NAVER_ID = os.environ.get("NAVER_CLIENT_ID", "").strip()
NAVER_SECRET = os.environ.get("NAVER_CLIENT_SECRET", "").strip()
PHOTO_CACHE = os.path.join(DATA, "photo-cache.json")
try:
    _img_cache = json.load(open(PHOTO_CACHE, encoding="utf-8"))   # 영구 캐시(정적 사진)
except Exception:  # noqa: BLE001
    _img_cache = {}
_img_dirty = False
_court_cache = {}


def save_photo_cache():
    if _img_dirty:
        try:
            json.dump(_img_cache, open(PHOTO_CACHE, "w", encoding="utf-8"), ensure_ascii=False)
        except Exception:  # noqa: BLE001
            pass


def naver_images(query, n=2):
    """검색어로 이미지 URL 목록(썸네일=핫링크 안정). 결과를 영구 캐시(단지·법원 사진은 정적)."""
    global _img_dirty
    if not query:
        return []
    if query in _img_cache:                       # 캐시 히트 → API 호출 안 함
        return _img_cache[query][:n]
    if not (NAVER_ID and NAVER_SECRET):
        return []
    try:
        url = "https://openapi.naver.com/v1/search/image?" + urllib.parse.urlencode(
            {"query": query, "display": max(n, 3), "sort": "sim", "filter": "large"})
        req = urllib.request.Request(url, headers={
            "X-Naver-Client-Id": NAVER_ID, "X-Naver-Client-Secret": NAVER_SECRET})
        with urllib.request.urlopen(req, timeout=8) as r:
            data = json.loads(r.read().decode("utf-8"))
        out = [it.get("thumbnail") or it.get("link") for it in data.get("items", []) if it.get("thumbnail") or it.get("link")]
    except Exception:  # noqa: BLE001
        out = []
    _img_cache[query] = out
    _img_dirty = True
    return out[:n]


def court_image(court):
    if not court:
        return None
    if court not in _court_cache:
        imgs = naver_images(court + " 전경", 1)
        _court_cache[court] = imgs[0] if imgs else None
    return _court_cache[court]


def fetch_photos(r):
    """단지·커뮤니티·법원 사진을 이미지검색으로 자동 수집 + 법원경매 원본(있으면)."""
    nm = (r.get("apt_name") or "").strip()
    apt = naver_images(nm + " 아파트", 2) if nm else []
    comm = naver_images(nm + " 커뮤니티", 1) if nm else []
    return {"apt": apt, "community": comm, "orig": r.get("photos") or [],
            "court": court_image(r.get("court"))}

_FB_CTA = ["궁금하신 분은 댓글 남겨주시면 알려드릴게요."]
CTA_LINES = _BLOG.get("cta_lines", _FB_CTA)

TITLE_INTRO = _BLOG.get("title_intro", ["오늘 살펴볼 물건은 <b>{reg} {nm}</b>입니다."])


STYLE = """
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<style>
.auc{max-width:760px;margin:0 auto;font-family:'Pretendard',system-ui,'Malgun Gothic','Apple SD Gothic Neo',sans-serif;font-size:16px;line-height:1.85;color:#333}
.auc p{margin:.9em 0}
.auc .kw{color:#ba0000;font-weight:800;line-height:1.7;margin:.2em 0}
.auc .summary{background:#f7f8fa;border-left:4px solid #003960;border-radius:0 10px 10px 0;padding:14px 18px;color:#333;line-height:1.9}
.auc h2{font-size:1.25em;color:#333;margin:1.7em 0 .5em;padding-left:.5em;border-left:6px solid #ba0000;font-weight:800}
.auc table{width:100%;border-collapse:collapse;margin:1em 0;font-size:.97em}
.auc th,.auc td{border:1px solid #e2e2e2;padding:9px 12px}
.auc th{background:#dee5ee;color:#003960;text-align:center;font-weight:700;white-space:nowrap}
.auc td{background:#fff;color:#222}
.auc td.r{text-align:right}.auc td.c{text-align:center}
.auc .now{background:#fff6e6}
.auc .lock{display:inline-block;background:linear-gradient(90deg,#fff3d6,#ffe6b0);color:#8a6d1a;border:1px dashed #e0b64e;border-radius:8px;padding:2px 12px;font-weight:800}
.auc .ask{background:#f3faf5;border:1px solid #cdead9;border-radius:14px;padding:16px 18px;line-height:1.75;margin:1.2em 0}
.auc .ask b{color:#127a4a}
.auc .tags{margin-top:1.8em;color:#3d7bd6;font-size:.92em;line-height:2;word-break:keep-all}
.auc .disc{font-size:.85em;color:#9aa0a8;border-top:1px solid #eee;margin-top:1.8em;padding-top:1em}
.auc .acard{display:block;text-decoration:none;color:#333;border:1px solid #e2e2e2;border-radius:16px;padding:16px;margin:1.2em 0;box-shadow:0 2px 10px rgba(0,0,0,.05);background:#fff}
.auc .c-top{display:flex;align-items:center;gap:10px;margin-bottom:12px}
.auc .c-score{flex:0 0 auto;width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px;border:2px solid}
.auc .c-score.s-ok{color:#00a152;border-color:#00c85a;background:#e9fbf0}
.auc .c-score.s-cond{color:#a76a00;border-color:#e6941a;background:#fff6e6}
.auc .c-score.s-hold{color:#777;border-color:#ccc;background:#f5f5f5}
.auc .c-nm{flex:1;font-weight:800;font-size:16px}
.auc .c-v{flex:0 0 auto;font-size:12px;font-weight:700;border-radius:999px;padding:4px 10px}
.auc .c-v.v-ok{background:#e9fbf0;color:#00a152}.auc .c-v.v-cond{background:#fff6e6;color:#a76a00}.auc .c-v.v-hold{background:#f0f0f0;color:#777}
.auc .c-grid{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.auc .c-grid>div{background:#fafafa;border-radius:10px;padding:9px 11px}
.auc .c-grid span{display:block;font-size:11.5px;color:#8a9098}
.auc .c-grid b{font-size:15px;font-weight:800;color:#111}
.auc .c-grid b.lock{color:#00a152;font-size:13px}
.auc .c-badges{margin-top:10px}.auc .c-sp{display:inline-block;background:#fff3e0;color:#c46a00;border-radius:8px;padding:3px 9px;font-size:11.5px;font-weight:700;margin:0 4px 4px 0}
.auc .c-cta{margin-top:12px;text-align:center;color:#00a152;font-weight:800;font-size:13.5px}
.auc .promo{background:linear-gradient(135deg,#e9fbf0,#f7f8fa);border:1px solid #cfeede;border-radius:14px;padding:16px 18px;margin:1.4em 0;line-height:1.8}
.auc .promo a{color:#00a152;font-weight:800;text-decoration:none}
.auc .sign{color:#888;font-size:.92em;margin-top:.3em}
.auc .photo{margin:1.1em 0}.auc .photo img{width:100%;border-radius:12px;display:block}
.auc figure{margin:1.1em 0}
.auc .cap{font-size:.82em;color:#9aa0a8;text-align:center;margin-top:.4em}
.auc .gallery{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:8px;margin:1em 0}
.auc .gallery img{width:100%;height:150px;object-fit:cover;border-radius:10px}
</style>
"""


BRANDS = _cfg_json("text-rules.json", {}).get("brands", ["자이","푸르지오","힐스테이트","래미안","e편한세상"])


def tag_line(r):
    """게시글에 등장하는 키워드에서 태그 추출: 지역(시도·시군구·동)·단지·브랜드·평형·상태 + 투자태그."""
    reg = r.get("region") or ""
    parts = reg.split()
    sido = parts[0] if parts else ""
    sigungu = parts[1] if len(parts) > 1 else ""
    addr = r.get("address") or ""
    d = dong(addr)
    typ = r.get("type") or "아파트"
    nm = (r.get("apt_name") or "").strip()
    py = pyeong(r.get("exclusive_area"))
    tags = []

    def add(*ts):
        for t in ts:
            t = (t or "").replace(" ", "")
            if t and t not in tags:
                tags.append(t)

    if sido:
        add(sido + typ, sido + "경매", sido + typ + "경매")
    if sigungu:
        add(sigungu + typ, sigungu + "경매", sigungu + typ + "경매")
        short = re.sub(r"(시|군|구)$", "", sigungu)
        if short and short != sigungu:
            add(short + typ, short + typ + "경매")
    if d:
        add(d + typ, d + "경매")
    if nm:
        add(nm, nm + "경매")
        low = nm.lower()
        for br in BRANDS:
            if br.lower() in low:
                add(br if not br.lower().startswith("sk") else "SK뷰")
                break
    if r.get("court"):
        add(r["court"])
    if r.get("case_no"):
        add(r["case_no"], (r.get("court") or "") + r["case_no"])
    if py:
        add(f"{round(py)}평{typ}")
    if r.get("fail_rounds"):
        add("유찰물건", "저감물건")
    if (r.get("liquidity") or {}).get("grade") in ("A", "B"):
        add("환금성좋은경매")
    add("부동산경매", "법원경매", "경매물건", "경매투자", "부동산재테크", "경매공부", "소액경매", "내집마련경매")
    return " ".join("#" + t for t in tags[:24])


def schedule_table(r):
    appr, mn, fr = r["appraisal"], r["min_bid"], r.get("fail_rounds", 0)
    ratio = (mn / appr) ** (1 / fr) if fr and appr else 1.0
    rows = ""
    for k in range(fr + 1):
        low = round(appr * (ratio ** k))
        pv = round((ratio ** k) * 100)
        cur = (k == fr)
        date = (r.get("sale_date") or "예정") if cur else "—"
        rows += (f'<tr class="{ "now" if cur else "" }"><td class="c">{k+1}차{" (예정)" if cur else ""}</td>'
                 f'<td class="c">{date}</td><td class="r">{low:,.0f}원</td><td class="c">{pv}%</td></tr>')
    return (f'<table><tr><th>회차</th><th>매각기일</th><th>최저가</th><th>비율</th></tr>{rows}</table>')


def complex_table(r):
    rows = []
    add = lambda k, v: rows.append(f'<tr><th style="width:38%">{k}</th><td>{v}</td></tr>') if v not in (None, "", "—") else None
    add("시공사", r.get("builder"))
    add("사용승인(준공)", y(r.get("approve_date")) if r.get("approve_date") else (str(r["built_year"]) + "년" if r.get("built_year") else None))
    hh = r.get("households")
    dc = r.get("dong_count")
    if hh:
        add("세대수 / 동수", f"{hh:,}세대" + (f" · {dc}개동" if dc else ""))
    add("난방방식", r.get("heating"))
    if r.get("parking"):
        add("주차대수", f"{r['parking']:,}대")
    if r.get("total_area"):
        add("연면적", f"{r['total_area']:,.0f}㎡")
    if not rows:
        return ""
    return '<h2>단지 정보</h2><table>' + "".join(rows) + '</table>'


def info_table(r):
    """물건 정보 상세: 소재지·건물내역·층·준공·실거래·평단가·최근실거래범위·매각기일·비고."""
    rows = []
    def add(k, v):
        if v not in (None, "", "—"):
            rows.append(f'<tr><th style="width:32%">{k}</th><td>{v}</td></tr>')
    add("소재지", r.get("address"))
    add("건물내역", r.get("building_detail"))
    if r.get("floor"):
        add("층", f'{r["floor"]}층' + (f' / 총 {r["total_floors"]}층' if r.get("total_floors") else ""))
    built = y(r.get("approve_date")) if r.get("approve_date") else (str(r["built_year"]) + "년" if r.get("built_year") else None)
    add("준공", built)
    if r.get("molit_count"):
        add("실거래(최근)", f'{r["molit_count"]}건')
    if r.get("price_per_pyeong"):
        add("평단가", f'약 {round(r["price_per_pyeong"]/1e4):,}만원/평')
    if r.get("molit_low"):
        add("최근 실거래가", f'{won(r["molit_low"])}~{won(r["molit_high"])}')
    add("매각기일", r.get("sale_date"))
    add("비고", r.get("note"))
    return '<table>' + "".join(rows) + '</table>' if rows else ""


def cost_table(r):
    """예상 부대비용 상세(권장가 기준). 적정입찰가·순이익은 블라인드 유지."""
    ci = r.get("cost_items") or {}
    rows = "".join(f'<tr><th style="width:38%">− {k}</th><td class="c">{won(v)}</td></tr>'
                   for k, v in ci.items() if v)
    if not rows:
        return ""
    return ('<h3 style="font-size:1.05em;margin:1.2em 0 .3em">예상 부대비용 (권장가 기준)</h3><table>'
            + rows + '</table><p style="font-size:.9em;color:#8a9098">권장 입찰가에 맞춰 추정한 비용입니다. '
            '적정 입찰가·예상 순이익은 프리미엄으로 가려두었어요.</p>')


def area_table(r):
    area = r.get("exclusive_area")
    py = pyeong(area)
    rows = ""
    if area:
        rows += f'<tr><th style="width:38%">전용면적</th><td>{area:.2f}㎡ ({py}평)</td></tr>'
    rows += f'<tr><th>감정가</th><td>{won(r["appraisal"])}</td></tr>'
    rows += f'<tr><th>최저입찰가</th><td>{won(r["min_bid"])} (유찰 {r.get("fail_rounds",0)}회)</td></tr>'
    if r.get("price_per_pyeong"):
        rows += f'<tr><th>실거래 평단가</th><td>약 {round(r["price_per_pyeong"]/1e4):,}만원/평</td></tr>'
    return '<h2>면적 · 가격</h2><table>' + rows + '</table>'


def market_para(r):
    if r.get("molit_count"):
        rng = f"{won(r['molit_low'])}~{won(r['molit_high'])}" if r.get("molit_low") else won(r["market_price"])
        pp = f" 전용 기준 평단가는 약 {round(r['price_per_pyeong']/1e4):,}만원 수준이고요." if r.get("price_per_pyeong") else ""
        return (f"국토교통부 실거래가를 보면 이 단지·면적대는 최근 <b>{r['molit_count']}건</b> 거래됐고, "
                f"가격대는 <b>{rng}</b>에 형성돼 있습니다.{pp} 감정가가 {won(r['appraisal'])}이니 "
                f"실거래·감정가를 같이 놓고 보면 대략의 눈높이가 잡힙니다.")
    return (f"인근 시세는 대략 <b>{won(r['market_price'])}</b> 안팎으로 보고 있습니다. "
            f"감정가({won(r['appraisal'])})와 비교해 가격 메리트를 따져봐야 합니다.")


def rights_para(r):
    rk = r.get("rights_risk") or {}
    flags = rk.get("flags") or []
    note = f" 현황조사서상 특이사항으로 {r['note']} 부분이 확인됩니다." if r.get("note") else ""
    if rk.get("level") == "높음":
        return (f"이 물건은 <b>권리 쪽을 특히 조심</b>해야 합니다. {' · '.join(flags)} — 위험도 '높음'으로 봤습니다. "
                f"대항력 있는 임차인 보증금은 배당받지 못하면 낙찰자가 인수하는데, 이 금액이 그대로 취득원가에 얹힙니다."
                f"{note} 매각물건명세서·현황조사서에서 임차인 전입일·배당요구 여부를 반드시 직접 확인하세요.")
    if rk.get("level") == "보통" or flags:
        return (f"권리는 보통 수준입니다. {(' · '.join(flags)) if flags else '임차인 관계'} 부분은 배당요구 여부에 따라 "
                f"인수 금액이 달라지니 명세서에서 꼭 확인하세요.{note}")
    return (f"권리관계는 비교적 깔끔한 편입니다. 말소기준권리 이후 권리가 소멸되는 일반적인 구조라 인수 위험은 낮게 봤습니다."
            f"{note} 그래도 명세서 확인은 습관처럼 하시고요.")


def generate_post(r, rank):
    nm = pname(r)
    s = _seed(r["id"])
    reg, typ = r["region"], r["type"]
    area = r.get("exclusive_area")
    py = pyeong(area)
    title = f"{reg} {typ} 경매 {nm}" + (f" {round(py)}평" if py else "")
    cta = _pick(CTA_LINES, s, 3)
    intro = _pick(TITLE_INTRO, s).format(reg=reg, nm=nm)
    ph = fetch_photos(r)
    cover_url = ph["orig"][0] if ph["orig"] else (ph["apt"][0] if ph["apt"] else None)
    cover = img(cover_url, nm) if cover_url else ""
    court_photo = img(ph["court"], r.get("court", "")) if ph["court"] else ""
    _gal = list(dict.fromkeys((ph["orig"][1:] + ph["apt"][1:] + ph["community"])))  # courtauction 원본 우선
    gal = gallery(_gal, "단지·현황 사진 (네이버 이미지검색·법원경매 제공)")

    kw = " ".join(f"#{k}" for k in [reg.split()[0] + typ, nm.replace(" ", ""), (reg.split()[-1] + typ + "경매")])

    # 사건 요약
    body_line = []
    if area:
        body_line.append(f"{r.get('floor','')}층 " if r.get('floor') else "")
        body_line.append(f"{area:.0f}㎡ {round(py)}평 ")
        body_line.append(f"{r.get('orientation','')}" if r.get('orientation') else "")
    summ = (f"<b>{r.get('court') or ''} {r.get('case_no') or ''}</b><br>{r.get('address') or reg}<br>"
            f"{''.join(body_line)}<br>최저가 {won(r['min_bid'])} · 감정가 {won(r['appraisal'])} · 유찰 {r.get('fail_rounds',0)}회"
            + (f"<br>매각기일 {r.get('sale_date')}" if r.get("sale_date") else ""))

    # 입지·단지 스토리
    hh = r.get("households")
    approve = y(r.get("approve_date")) if r.get("approve_date") else (str(r["built_year"]) + "년" if r.get("built_year") else None)
    story = f"{intro} "
    if approve:
        story += f"{approve.replace('년','')}년에 준공된 단지로, "
    if hh:
        story += f"총 {hh:,}세대" + (f"({r['dong_count']}개동)" if r.get("dong_count") else "") + " 규모입니다. "
    if r.get("builder"):
        story += f"{r['builder']}가 시공했고요. "
    if r.get("floor"):
        story += f"본 물건은 {r['floor']}층{('·'+r['orientation']) if r.get('orientation') else ''}이라 "
        story += "채광·전망 측면에서 무난합니다. " if (r.get("floor") or 0) >= 5 else "저층이라 이 부분은 임장 때 직접 확인해보시길 권합니다. "

    body = STYLE + f"""
<div class="auc">
<p class="kw">{kw}</p>
{cover}
<div class="summary">{summ}</div>
{analysis_card(r)}
{court_photo}
<p>안녕하세요, 매일 수도권 경매 물건을 데이터로 분석해 정리하는 <b>{NICK}</b>입니다.</p>

<h2>물건 정보</h2>
<p>{story}</p>
{info_table(r)}
{gal}
{complex_table(r)}
{area_table(r)}

<h2>권리 분석</h2>
<p>{rights_para(r)}</p>

<h2>시세</h2>
<p>{market_para(r)}</p>

<h2>매각기일 · 최저가 흐름</h2>
{schedule_table(r)}
<p>{'유찰이 이어지며 최저가가 감정가 대비 꽤 내려왔습니다. ' if r.get('fail_rounds') else '아직 유찰 없는 신건이라 경쟁이 붙으면 값이 빠르게 오를 수 있습니다. '}다음 회차까지 기다릴지, 이번에 들어갈지는 물건의 상태와 경쟁 강도를 같이 보고 판단해야 합니다.</p>

<h2>그래서, 얼마에 써야 할까</h2>
<p>제가 취득세·양도세·명도비·수리비까지 다 넣고, 이 지역·유형의 실제 낙찰가율과 경쟁도를 반영해
<b>보수·권장·공격 세 가지 적정 입찰가</b>와 <b>예상 순이익·수익률</b>을 계산해 뒀습니다. 다만 이건 프리미엄이라 블라인드 처리했어요.</p>
<table>
<tr><th style="width:40%">적정 입찰가(권장)</th><td class="c">{LOCK}</td></tr>
<tr><th>예상 순이익 · 수익률</th><td class="c">{LOCK}</td></tr>
<tr><th>낙찰 성공률(참고)</th><td class="c">{pct(r.get('success_prob'))} · 환금성 {(r.get('liquidity') or {}).get('grade','—')}등급</td></tr>
</table>
{cost_table(r)}
<div class="ask"><b>💬 적정 입찰가·예상 수익 문의</b><br>{cta}</div>
{site_promo()}
{adsense_slot()}

<h2>정리</h2>
<p>{'입지·환금성이 받쳐주는 물건입니다. ' if (r.get('liquidity') or {}).get('score',0)>=55 else '환금성은 다소 아쉬우니 매도 기간을 넉넉히 잡는 게 좋습니다. '}
권리 위험은 {(r.get('rights_risk') or {}).get('level','낮음')} 수준으로 봤고요. 꼼꼼히 확인하시고 무리하지 않는 선에서 도전해보시기 바랍니다. 비슷하게 보고 계신 분, 임장 다녀오신 분 있으면 댓글로 정보 나눠요.</p>

<p class="sign">— {BLOG_NAME} · {NICK}</p>
<div class="tags">{tag_line(r)}</div>
<div class="disc">공개 데이터(법원경매·국토부 실거래·공동주택정보) 기반 자동 분석이며 투자 자문이 아닙니다. 세율·부대비용은 근사값입니다. 입찰 전 매각물건명세서·현황조사서를 반드시 직접 확인하세요.</div>
</div>"""
    return title, body


def generate_past_post(c, rank):
    nm = c["region"] + " " + c["type"]
    s = _seed(c["id"])
    cta = _pick(CTA_LINES, s, 3)
    title = f"[경매 복기] {c['region']} {c['type']} 낙찰 → 재매도 수익률 {c['roi']*100:.0f}%"
    body = STYLE + f"""
<div class="auc">
<p class="kw">#{c['region'].split()[0]}경매 #경매복기 #부동산경매</p>
<p>안녕하세요, <b>{NICK}</b>입니다. 오늘은 이미 끝난 경매를 복기해봅니다.</p>
<div class="summary"><b>{c['region']} {c['type']}</b><br>감정가 {won(c.get('appraisal'))} · 낙찰가율 {c.get('sale_ratio','—')}%<br>재매도 수익률 <b>{c['roi']*100:.1f}%</b></div>
<h2>결과 요약</h2>
<p>이 물건은 낙찰가율 {c.get('sale_ratio','—')}%에 낙찰됐고, 응찰자는 약 {c.get('bidders','—')}명이었습니다.
이후 재매도까지 이어지며 최종 수익률 <b>{c['roi']*100:.1f}%</b>를 남긴 사례입니다. 실제 낙찰가·매도가·순이익 액수는 아껴둘게요.</p>
<div class="ask"><b>💬 이 사례 실제 숫자 문의</b><br>{cta}</div>
<p>지금 진행 중인 비슷한 물건에 이 기준을 대입해보면 감을 잡기 좋습니다.</p>
<p class="sign">— {BLOG_NAME} · {NICK}</p>
<div class="tags">{tag_line(c)}</div>
<div class="disc">과거 실적 복기이며 투자 자문이 아닙니다. 시장 상황에 따라 결과는 달라질 수 있습니다.</div>
</div>"""
    return title, body


def select(analysis, published, count):
    picks = []
    for r in analysis.get("properties", []):
        if r["id"] in published:
            continue
        picks.append(("current", r))
        if len(picks) >= count:
            return picks
    cases = sorted([c for c in (analysis.get("backtest", {}).get("cases") or [])
                    if c.get("resale_price")], key=lambda c: c.get("roi", 0), reverse=True)
    for c in cases:
        if ("past_" + c["id"]) in published:
            continue
        picks.append(("past", c))
        if len(picks) >= count:
            break
    return picks


def main():
    analysis = load("analysis.json")
    if not analysis:
        print("analysis.json 없음 — analyze.py 먼저 실행", file=sys.stderr)
        return
    published = load("published.json", {}) or {}
    picks = select(analysis, published, DAILY_COUNT)
    if not picks:
        print("발행할 새 콘텐츠 없음")
        return
    day = today()
    outdir = os.path.join(CONTENT, day)
    os.makedirs(outdir, exist_ok=True)
    index = []
    for rank, (kind, item) in enumerate(picks, 1):
        title, html = (generate_post(item, rank) if kind == "current" else generate_past_post(item, rank))
        pid = item["id"] if kind == "current" else "past_" + item["id"]
        base = pname(item) if kind == "current" else item["id"]
        fname = f"{rank:02d}-{slugify(base)}.html"
        doc = (f'<!doctype html>\n<html lang="ko">\n<head>\n<meta charset="utf-8">\n'
               f'<meta name="viewport" content="width=device-width, initial-scale=1">\n'
               f'<title>{title}</title>\n</head>\n<body>\n{html}\n</body>\n</html>\n')
        open(os.path.join(outdir, fname), "w", encoding="utf-8").write(doc)
        published[pid] = {"date": day, "title": title, "kind": kind}
        index.append({"rank": rank, "kind": kind, "id": pid, "title": title, "file": fname})
    json.dump({"date": day, "count": len(index), "posts": index},
              open(os.path.join(outdir, "index.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    json.dump(published, open(os.path.join(DATA, "published.json"), "w", encoding="utf-8"), ensure_ascii=False, indent=2)
    save_photo_cache()
    cur = sum(1 for k, _ in picks if k == "current")
    print(f"[content] {day}: {len(index)}편 (현재 {cur}/과거 {len(index)-cur}) → content/{day}/")
    for x in index:
        print(f"  {x['rank']:>2}. {x['title'][:52]}")


if __name__ == "__main__":
    main()
