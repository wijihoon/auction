#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
경매 물건 분석 엔진 v2.

지표: ① 적정 입찰가  ② 낙찰 성공률(경쟁도 반영)  ③ 재매매 순이익(정밀 세금·권리 인수 반영)
시세: 국토부 실거래가 OpenAPI(아파트/오피스텔/연립다세대) + 층·향·면적 보정.
권리분석: 대항력 임차 인수보증금·특수권리(유치권 등) → 순이익 차감 + 권리 위험도.
세금: 취득세(구간·농특·교육세·중과) / 양도세(단기중과·누진·장특공제·지방소득세).
표준 라이브러리만 사용. GitHub Actions에서 secrets.MOLIT_SERVICE_KEY 주입.
"""
import os, sys, json, math, bisect, statistics, urllib.parse, urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timezone, timedelta

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def load(n, default=None):
    p = os.path.join(DATA, n)
    if not os.path.exists(p):
        return default
    with open(p, encoding="utf-8") as f:
        return json.load(f)


def save(n, o):
    with open(os.path.join(DATA, n), "w", encoding="utf-8") as f:
        json.dump(o, f, ensure_ascii=False, separators=(",", ":"))


def norm_cdf(z):
    return 0.5 * (1 + math.erf(z / math.sqrt(2)))


def _probit(p):
    """표준정규 역함수(Acklam 근사). 승자의 저주 보정용."""
    p = min(max(p, 1e-9), 1 - 1e-9)
    a = [-3.969683028665376e+01, 2.209460984245205e+02, -2.759285104469687e+02,
         1.383577518672690e+02, -3.066479806614716e+01, 2.506628277459239e+00]
    b = [-5.447609879822406e+01, 1.615858368580409e+02, -1.556989798598866e+02,
         6.680131188771972e+01, -1.328068155288572e+01]
    c = [-7.784894002430293e-03, -3.223964580411365e-01, -2.400758277161838e+00,
         -2.549732539343734e+00, 4.374664141464968e+00, 2.938163982698783e+00]
    d = [7.784695709041462e-03, 3.224671290700398e-01, 2.445134137142996e+00, 3.754408661907416e+00]
    plow, phigh = 0.02425, 1 - 0.02425
    if p < plow:
        q = math.sqrt(-2 * math.log(p))
        return (((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    if p > phigh:
        q = math.sqrt(-2 * math.log(1 - p))
        return -(((((c[0]*q+c[1])*q+c[2])*q+c[3])*q+c[4])*q+c[5]) / ((((d[0]*q+d[1])*q+d[2])*q+d[3])*q+1)
    q = p - 0.5
    r = q * q
    return (((((a[0]*r+a[1])*r+a[2])*r+a[3])*r+a[4])*r+a[5])*q / (((((b[0]*r+b[1])*r+b[2])*r+b[3])*r+b[4])*r+1)


def expected_max_normal(n):
    """N개 표준정규 표본의 최댓값 기대(Blom 근사). 승자의 저주 보정계수."""
    n = max(1, int(round(n)))
    if n <= 1:
        return 0.0
    return _probit((n - 0.375) / (n + 0.25))


def _parse_date(s):
    if not s:
        return None
    s = str(s)[:10]
    for fmt in ("%Y-%m-%d", "%Y-%m"):
        try:
            return datetime.strptime(s, fmt).date()
        except ValueError:
            continue
    return None


def filter_recent_history(history, days):
    """과거 경매 실적을 최근 days일로 제한(기준일=재매도일 우선, 없으면 낙찰일).
    날짜가 없는 기록은 보존한다."""
    if not days or days <= 0:
        return history
    cutoff = datetime.now(timezone(timedelta(hours=9))).date() - timedelta(days=days)
    out = []
    for h in history:
        ref = _parse_date(h.get("resale_date")) or _parse_date(h.get("result_date"))
        if ref is None or ref >= cutoff:
            out.append(h)
    return out


# ----------------------- 시세: 국토부 실거래가 -----------------------
ENDPOINTS = {
    "아파트": ("1613000/RTMSDataSvcAptTradeDev/getRTMSDataSvcAptTradeDev", ("aptNm", "아파트")),
    "오피스텔": ("1613000/RTMSDataSvcOffiTrade/getRTMSDataSvcOffiTrade", ("offiNm", "단지")),
    "빌라": ("1613000/RTMSDataSvcRHTrade/getRTMSDataSvcRHTrade", ("mhouseNm", "연립다세대")),
}
BASE = "https://apis.data.go.kr/"


def _load_json(name):
    p = os.path.join(DATA, name)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:  # noqa: BLE001
            return {}
    return {}


def _save_json(name, obj):
    try:
        json.dump(obj, open(os.path.join(DATA, name), "w", encoding="utf-8"), ensure_ascii=False)
    except Exception:  # noqa: BLE001
        pass


def recent_months(n=6):
    d = datetime.now(timezone(timedelta(hours=9)))
    y, m, out = d.year, d.month, []
    for _ in range(n):
        out.append(f"{y}{m:02d}")
        m -= 1
        if m == 0:
            y, m = y - 1, 12
    return out


def _fetch_month(path, name_tags, lawd_cd, key, ym):
    """(법정동, 월) 실거래 1개월치. 반환: [[price,name,area,floor,buildYear], ...]."""
    q = urllib.parse.urlencode({"serviceKey": key, "LAWD_CD": lawd_cd, "DEAL_YMD": ym, "numOfRows": "1000"})
    out = []
    with urllib.request.urlopen(f"{BASE}{path}?{q}", timeout=20) as r:
        root = ET.fromstring(r.read().decode("utf-8", "ignore"))
    for it in root.iter("item"):
        def g(*tags):
            for t in tags:
                e = it.find(t)
                if e is not None and e.text:
                    return e.text.strip()
            return ""
        amt = g("dealAmount", "거래금액").replace(",", "")
        if not amt:
            continue
        try:
            price = int(amt) * 10000
        except ValueError:
            continue
        try:
            area = float(g("excluUseAr", "전용면적") or 0) or None
        except ValueError:
            area = None
        try:
            floor = int(g("floor", "층") or 0) or None
        except ValueError:
            floor = None
        try:
            by = int(g("buildYear", "건축년도") or 0) or None
        except ValueError:
            by = None
        out.append([price, g(*name_tags), area, floor, by])
    return out


def fetch_lawd_trades(typ, lawd_cd, key, months, mcache, cur_ym):
    """(유형,법정동) 최근 months개월 실거래. 지난 달=확정값이라 캐시 재사용, 이번 달만 재조회.
    반환: (rows, new) — new는 이번에 새로 받아 캐시에 반영할 {키: 월데이터}."""
    ep = ENDPOINTS.get(typ)
    if not key or not lawd_cd or not ep:
        return [], {}
    path, name_tags = ep
    rows, new = [], {}
    for ym in recent_months(months):
        ck = f"{typ}|{lawd_cd}|{ym}"
        if ym < cur_ym and ck in mcache:              # 지난 달 → 캐시(변동 없음)
            month = mcache[ck]
        else:                                         # 이번 달(변동) 또는 미캐시 → 조회
            try:
                month = _fetch_month(path, name_tags, lawd_cd, key, ym)
            except Exception:  # noqa: BLE001
                month = mcache.get(ck, [])
            new[ck] = month
        rows.extend(tuple(t) for t in month)
    return rows, new


def matched_trades(prop, cache):
    """물건의 (유형·시군구) 캐시에서 단지명·면적으로 필터한 실거래 목록."""
    rows = cache.get((prop.get("type"), prop.get("lawd_cd"))) or []
    name = (prop.get("apt_name") or "").strip()
    area = prop.get("exclusive_area") or 0
    out = []
    for t in rows:
        price, nm, ar, fl, by = (list(t) + [None] * 5)[:5]
        if name and name not in (nm or "") and (nm or "") not in name:
            continue
        if area and ar and abs(ar - area) > 10:
            continue
        out.append((price, nm, ar, fl, by))
    return out


def trade_info(prop, cache):
    """실거래에서 뽑는 정보성 데이터: 최근 거래 건수·건축년도·평단가·최근 실거래 범위."""
    rows = matched_trades(prop, cache)
    if not rows:
        return {}
    prices = [r[0] for r in rows]
    bys = [r[4] for r in rows if r[4]]
    info = {"molit_count": len(rows), "molit_low": min(prices), "molit_high": max(prices)}
    if bys:
        info["build_year"] = max(set(bys), key=bys.count)     # 최빈 건축년도
    area = prop.get("exclusive_area")
    if area:
        info["price_per_pyeong"] = int(statistics.median(prices) / (area / 3.3058))
    return info


def build_trade_cache(props, key, months=6, workers=8):
    """(유형, 법정동코드) 중복 제거 후 동시 조회. 지난 달은 캐시 재사용, 이번 달만 재조회."""
    uniq = sorted({(p.get("type"), p.get("lawd_cd")) for p in props
                   if p.get("lawd_cd") and ENDPOINTS.get(p.get("type"))})
    if not key or not uniq:
        return {}
    mcache = _load_json("molit-cache.json")
    cur_ym = recent_months(1)[0]

    def work(k):
        r, new = fetch_lawd_trades(k[0], k[1], key, months, mcache, cur_ym)
        return k, r, new

    cache = {}
    with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
        for k, rows, new in ex.map(work, uniq):
            cache[k] = rows
            mcache.update(new)
    keep = set(recent_months(months + 1))                 # 오래된 월 캐시 정리
    mcache = {ck: v for ck, v in mcache.items() if ck.rsplit("|", 1)[-1] in keep}
    _save_json("molit-cache.json", mcache)
    print(f"[analyze] 시세: {len(uniq)}개 (유형·시군구) — 지난달 캐시 재사용, 이번달만 조회", file=sys.stderr, flush=True)
    return cache


# ----------------------- 공동주택 단지정보(세대수 등) -----------------------
APT_LIST = "1613000/AptListService3/getSigunguAptList3"
APT_INFO = "1613000/AptBasisInfoServiceV3/getAphusBassInfoV3"
APT_DTL = "1613000/AptBasisInfoServiceV3/getAphusDtlInfoV3"


def _xml_items(url):
    with urllib.request.urlopen(url, timeout=20) as r:
        return list(ET.fromstring(r.read().decode("utf-8", "ignore")).iter("item"))


def _apt_list(lawd, key):
    """시군구(5자리) 아파트 단지 목록 → [(단지명, kaptCode)]."""
    try:
        q = urllib.parse.urlencode({"serviceKey": key, "sigunguCode": lawd, "numOfRows": "5000", "pageNo": "1"})
        out = []
        for it in _xml_items(f"{BASE}{APT_LIST}?{q}"):
            def g(t):
                e = it.find(t)
                return e.text.strip() if e is not None and e.text else ""
            nm, code = (g("kaptName") or g("kaptNm")), g("kaptCode")
            if nm and code:
                out.append((nm, code))
        return out
    except Exception:  # noqa: BLE001
        return []


def _apt_fields(url, code, key):
    """단지 API 한 엔드포인트의 item 하위 태그를 dict로."""
    q = urllib.parse.urlencode({"serviceKey": key, "kaptCode": code})
    its = _xml_items(f"{BASE}{url}?{q}")
    if not its:
        return {}
    return {c.tag: (c.text.strip() if c.text else "") for c in its[0]}


def _apt_basis(code, key):
    """기본+상세정보 → 세대수·동수·사용승인·시공사·난방·주차·연면적."""
    d = {}
    for url in (APT_INFO, APT_DTL):
        try:
            d.update(_apt_fields(url, code, key))
        except Exception:  # noqa: BLE001
            pass
    if not d:
        return {}

    def g(*keys):
        for k in keys:
            if d.get(k):
                return d[k]
        return ""
    info = {}
    if g("kaptdaCnt").isdigit():
        info["households"] = int(g("kaptdaCnt"))
    if g("kaptDongCnt").isdigit():
        info["dong_count"] = int(g("kaptDongCnt"))
    if g("kaptUsedate"):
        info["approve_date"] = g("kaptUsedate")
    if g("kaptBcompany", "kaptAcompany"):
        info["builder"] = g("kaptBcompany", "kaptAcompany")
    if g("codeHeatNm"):
        info["heating"] = g("codeHeatNm")
    p1, p2 = g("kaptdPcnt"), g("kaptdPcntu")
    pk = (int(p1) if p1.isdigit() else 0) + (int(p2) if p2.isdigit() else 0)
    if pk:
        info["parking"] = pk
    ta = g("kaptTarea", "kaptMarea")
    try:
        if ta:
            info["total_area"] = round(float(ta))
    except ValueError:
        pass
    return info


def build_apt_cache(props, key, workers=6):
    """세대수·시공사·주차·난방 등 정적 단지정보. 목록·기본정보를 영구 캐시(신규만 조회)."""
    if not key:
        return {}
    apts = [p for p in props if p.get("type") == "아파트" and p.get("lawd_cd") and (p.get("apt_name") or "").strip()]
    if not apts:
        return {}
    list_cache = _load_json("apt-list-cache.json")   # {lawd: {"ts": ordinal, "list": [[name,code],...]}}
    info_cache = _load_json("apt-info-cache.json")   # {kaptCode: {정적 단지정보}}
    today = datetime.now(timezone(timedelta(hours=9))).toordinal()
    lawds = sorted({p["lawd_cd"] for p in apts})
    need_list = [l for l in lawds if not (list_cache.get(l) and today - list_cache[l].get("ts", 0) < 30)]
    if need_list:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            for l, lst in ex.map(lambda l: (l, _apt_list(l, key)), need_list):
                if lst:
                    list_cache[l] = {"ts": today, "list": [[n, c] for n, c in lst]}
        _save_json("apt-list-cache.json", list_cache)
    code_by_prop, codes = {}, set()
    for p in apts:
        nm = p["apt_name"].replace(" ", "")
        for cnm, code in (list_cache.get(p["lawd_cd"], {}) or {}).get("list", []):
            if nm and (nm in cnm.replace(" ", "") or cnm.replace(" ", "") in nm):
                code_by_prop[p["id"]] = code
                codes.add(code)
                break
    need_info = [c for c in codes if c not in info_cache]
    if need_info:
        with ThreadPoolExecutor(max_workers=max(1, workers)) as ex:
            for c, info in ex.map(lambda c: (c, _apt_basis(c, key)), sorted(need_info)):
                info_cache[c] = info or {}
        _save_json("apt-info-cache.json", info_cache)
    print(f"[analyze] 단지정보: 목록 신규 {len(need_list)}개 시군구 · 기본정보 신규 {len(need_info)}건 (나머지 캐시)",
          file=sys.stderr, flush=True)
    return {pid: info_cache.get(code, {}) for pid, code in code_by_prop.items()}


def floor_bucket(prop):
    fl, tot = prop.get("floor"), prop.get("total_floors")
    if not fl:
        return "mid"
    if fl <= 3:
        return "low"
    if tot and fl >= tot * 0.75:
        return "high"
    return "mid"


def income_value(prop, a):
    """수익환원 가치: 연월세/목표수익률 + 보증금. 오피스텔·상가용.
    물건에 임대 데이터(monthly_rent·lease_deposit)가 있으면 사용, 없으면 유형·면적 기반 기본값."""
    v = (a.get("valuation") or {}).get(prop.get("type"))
    if not v:
        return None
    area = prop.get("exclusive_area") or 0
    monthly = prop.get("monthly_rent") or (area * v.get("monthly_per_m2", 0))
    deposit = prop.get("lease_deposit")
    if deposit is None:
        deposit = int((prop.get("appraisal") or 0) * v.get("deposit_ratio", 0))
    y = v.get("target_yield") or 0
    if monthly <= 0 or y <= 0:
        return None
    return int(monthly * 12 / y + deposit)


def valued_price(prop, cache, a):
    """유형별 가치: 아파트/주거=실거래 시세, 오피스텔=min(시세,수익환산), 상가=수익환산(Cap Rate)."""
    sale, src, n = market_price(prop, cache, a)
    iv = income_value(prop, a)
    if iv:
        t = prop.get("type")
        if t == "상가":                       # 감정가·시세 왜곡 큼 → 수익환원으로 재산출
            return iv, f"{src}→수익환산(CapRate)", n
        if sale and iv < sale:                # 오피스텔 등: 급매가·수익가치 중 낮은 값
            return iv, f"{src}→수익환산(min)", n
    return sale, src, n


def market_price(prop, cache, a):
    """캐시된 시군구 실거래에서 단지·면적으로 필터 → 중앙값에 층·향 보정."""
    rows = matched_trades(prop, cache)
    if rows:
        prices = [r[0] for r in rows]
        base = statistics.median(prices)
        adj = 1 + a["floor_adj"].get(floor_bucket(prop), 0) \
                + a["orientation_adj"].get(prop.get("orientation", ""), 0)
        return int(base * adj), f"molit({len(prices)})+보정", len(prices)
    if prop.get("market_price_override"):
        return int(prop["market_price_override"]), "override", None
    return int(prop["appraisal"]), "appraisal_fallback", None


# ----------------------- 세금 (정밀) -----------------------
def acquisition_tax(price, area, a):
    t = a["tax"]
    eok = price / 1e8
    if price <= 6e8:
        base = 0.01
    elif price <= 9e8:
        base = (eok * 2 / 3 - 3) / 100      # 6~9억 구간 1~3% 선형
    else:
        base = 0.03
    tax = price * base * t["acq_edu_multiplier"]   # + 지방교육세(근사)
    if area > 85:
        tax += price * t["acq_nongtuk_over85"]     # 농특세
    if t.get("multi_home"):
        tax += price * t["acq_multi_home_surcharge"]
    return tax


def progressive(base, brackets):
    for cap, rate, ded in brackets:
        if base <= cap:
            return base * rate - ded
    cap, rate, ded = brackets[-1]
    return base * rate - ded


def capital_gains_tax(gain, months, a):
    t = a["tax"]
    if gain <= 0:
        return 0.0
    taxable = gain - t["cgt_basic_deduction"]
    if taxable <= 0:
        return 0.0
    if months < 12:
        cgt = taxable * 0.70                        # 1년 미만 단기중과
    elif months < 24:
        cgt = taxable * 0.60                        # 2년 미만
    else:
        years = months // 12
        if t.get("cgt_single_home"):
            ltd = min(0.80, years * 0.08) if years >= 3 else 0.0
        else:
            ltd = min(t["cgt_ltd_max"], years * t["cgt_ltd_rate_per_year"]) if years >= 3 else 0.0
        after = taxable * (1 - ltd)
        cgt = progressive(after, a["progressive_brackets"])
        cgt += after * t.get("cgt_adjusted_surcharge", 0.0)   # 조정지역 다주택 중과 %p
    cgt += cgt * t["cgt_local_surtax"]              # 지방소득세 10%
    return max(cgt, 0.0)


# ----------------------- 부대비용 + 권리 인수 -----------------------
def assumed_rights_cost(prop):
    return (prop.get("assumed_deposit") or 0) + (prop.get("lien_amount") or 0)


def cost_ctx(prop, sale, a):
    """물건·매도가 기준 bid-독립 비용을 1회 계산(탐색 루프에서 재사용)."""
    months = prop.get("holding_months", a["holding_months"])
    area = prop.get("exclusive_area") or 0
    evic = a["eviction_cost"].get(prop.get("eviction", "normal"), a["eviction_cost"]["normal"])
    repair = area * a["repair_cost_per_m2"]
    broker = sale * a["brokerage_rate"]
    fixed = a["extra_fixed"]
    arrear = area * a.get("unpaid_mgmt_reserve_m2", 0)      # 미납 관리비 예비비(공용부분 인수)
    assumed = assumed_rights_cost(prop)
    mgmt = a["monthly_mgmt_fee"] * months
    return {"sale": sale, "months": months, "area": area, "assumed": assumed,
            "evic": evic, "repair": repair, "broker": broker, "fixed": fixed, "mgmt": mgmt, "arrear": arrear,
            "hold_bidrate": a["holding_cost_annual_rate"] * months / 12,
            "fixed_noncgt": assumed + evic + repair + broker + fixed + mgmt + arrear,
            "invest_fixed": assumed + evic + repair + arrear}


def _pf(bid, c, a):
    """profit, roi 만 반환하는 고속 경로(items·round 없음) — 입찰가 탐색용."""
    acq = acquisition_tax(bid, c["area"], a)
    non_cgt = c["fixed_noncgt"] + acq + bid * c["hold_bidrate"]
    pre_gain = c["sale"] - bid - non_cgt
    profit = pre_gain - capital_gains_tax(pre_gain, c["months"], a)
    invested = bid + c["invest_fixed"] + acq
    return profit, (profit / invested if invested else 0)


def net_profit(bid, sale, prop, a, ctx=None):
    c = ctx if (ctx and ctx.get("sale") == sale) else cost_ctx(prop, sale, a)
    acq = acquisition_tax(bid, c["area"], a)
    holding = bid * c["hold_bidrate"] + c["mgmt"]
    assumed, evic, repair = c["assumed"], c["evic"], c["repair"]
    non_cgt = assumed + acq + evic + repair + holding + c["broker"] + c["fixed"] + c["arrear"]
    pre_gain = sale - bid - non_cgt
    cgt = capital_gains_tax(pre_gain, c["months"], a)
    items = {"인수권리": round(assumed), "취득세": round(acq), "명도비": round(evic),
             "수리비": round(repair), "미납관리비": round(c["arrear"]), "보유비용": round(holding),
             "매도중개": round(c["broker"]), "등기·법무 등": round(c["fixed"]), "양도세": round(cgt)}
    costs = sum(items.values())
    profit = sale - bid - costs
    invested = bid + assumed + items["취득세"] + evic + repair + round(c["arrear"])
    return profit, (profit / invested if invested else 0), costs, items




# ----------------------- 권리 위험도 -----------------------
def rights_risk(prop):
    score, flags = 0, []
    if prop.get("senior_tenant"):
        score += 35
        flags.append("대항력 임차인")
    dep = prop.get("assumed_deposit") or 0
    if dep:
        score += min(30, dep / 1e8 * 25)
        flags.append(f"인수보증금 {int(dep/1e4):,}만")
    sr = prop.get("special_rights") or []
    if sr:
        score += min(35, len(sr) * 18)
        flags += sr
    if prop.get("lien_amount"):
        score += 10
    lvl = "높음" if score >= 60 else "보통" if score >= 30 else "낮음"
    return {"score": min(100, round(score)), "level": lvl, "flags": flags}


# 특수물건 키워드: data/text-rules.json 에서 로드
SPECIAL_KW = _load_json("text-rules.json").get("special_keywords", {})


def special_tags(prop, risk):
    text = " ".join(str(prop.get(k) or "") for k in ("note", "usage_detail", "building_detail", "address"))
    text = text.replace(" ", "")
    tags = []
    for label, kws in SPECIAL_KW.items():
        if any(kw.replace(" ", "") in text for kw in kws):
            tags.append(label)
    if "대항력 임차인" in (risk or {}).get("flags", []) and "선순위임차인" not in tags:
        tags.append("선순위임차인")
    return tags


def _pt_group(region):
    cfg = _load_json("priority-tenant.json").get("groups", [])
    for g in cfg:
        if any(m in (region or "") for m in g.get("match", [])):
            return g
    return cfg[-1] if cfg else {"cap": 0, "top": 0}


def distribution_table(won_bid, reg_rights, tenants, region, a):
    """예상 배당표: 낙찰가 → 경매비용 → 최우선변제 → 날짜순 우선변제. 대항력 임차인 미배당분은 인수.
    reg_rights: [{type, amount, date}], tenants: [{deposit, movein, fixed, demand, }].
    등기 권리·임차 내역이 있을 때만 계산(법원경매 물건상세에서 취득)."""
    if not (reg_rights or tenants):
        return None
    cost = int(won_bid * a.get("auction_cost_rate", 0.015))
    pool = won_bid - cost
    g = _pt_group(region)
    base = None                                    # 말소기준일
    for r in reg_rights:
        if r.get("type") in ("근저당", "근저당권", "압류", "가압류", "담보가등기") and r.get("date"):
            base = r["date"] if base is None else min(base, r["date"])

    claims = []
    for t in tenants or []:
        dep = t.get("deposit", 0) or 0
        senior = bool(base and t.get("movein") and t["movein"] < base)
        small = dep <= g.get("cap", 0)
        top = min(dep, g.get("top", 0)) if (small and t.get("demand")) else 0
        claims.append({"label": "임차보증금", "amount": dep, "date": t.get("fixed") or t.get("movein"),
                       "top": top, "senior": senior, "demand": bool(t.get("demand"))})
    for r in reg_rights or []:
        if r.get("type") in ("근저당", "근저당권", "전세권", "임차권", "확정일자부임차"):
            claims.append({"label": r.get("type"), "amount": r.get("amount", 0) or 0, "date": r.get("date"),
                           "top": 0, "senior": False, "demand": True})

    remaining = pool
    remaining -= min(remaining, sum(c["top"] for c in claims))     # 1) 최우선변제
    rows, assumed = [], 0
    for c in sorted(claims, key=lambda c: c.get("date") or "9999"):  # 2) 날짜순 우선변제
        need = max(0, c["amount"] - c["top"])
        paid = min(max(0, remaining), need) if c["demand"] else 0
        remaining -= paid
        got = paid + c["top"]
        unpaid = c["amount"] - got
        if unpaid > 0 and c["senior"]:
            status, assumed = "일부배당·잔액 인수", assumed + unpaid
        elif unpaid > 0:
            status = "미배당·소멸" if not c["senior"] else "인수"
        else:
            status = "전액배당"
        rows.append({"권리": c["label"], "청구액": int(c["amount"]), "배당액": int(got), "상태": status})
    return {"낙찰가": int(won_bid), "경매비용": cost, "배당재원": int(pool),
            "말소기준일": base, "인수합계": int(assumed), "rows": rows,
            "note": "법원경매 물건상세의 등기·임차 데이터 기반 추정. 실제 배당은 법원 판단."}


def analysis_checklist(prop, res):
    """경매에서 놓치면 안 되는 인수·리스크 확인 항목. level: high(치명)·warn(주의)·info(참고)."""
    sp = res.get("special") or []
    flags = (res.get("rights_risk") or {}).get("flags", [])
    out = []

    def add(item, note, level):
        out.append({"item": item, "note": note, "level": level})

    if "대항력 임차인" in flags:
        add("선순위 임차인 배당요구 확인",
            "배당요구를 안 했거나 배당이 부족하면 보증금을 낙찰자가 인수합니다. 명세서에서 전입일·확정일자·배당요구 종기를 확인하세요.", "high")
    if "유치권" in sp:
        add("유치권 성립·금액 확인", "성립 시 변제 전까지 인도 거부가 가능합니다. 공사대금 근거와 실제 점유를 현장에서 확인하세요.", "high")
    if "법정지상권" in sp:
        add("법정지상권 여부", "토지·건물 소유가 갈리면 철거 불가·지료 부담이 생깁니다. 성립 여부를 확인하세요.", "high")
    if "대지권미등기" in sp:
        add("대지권 미등기", "토지 지분 확보가 불확실합니다. 추후 대지권 취득 비용·분쟁 가능성을 확인하세요.", "high")
    if "선순위임차인" in sp:
        add("선순위 권리 인수 여부", "말소기준권리보다 앞선 전세권·임차권은 인수될 수 있습니다.", "high")
    if "토지별도등기" in sp:
        add("토지 별도등기", "토지에 별도 근저당 등이 있으면 인수 위험이 있습니다. 등기부를 확인하세요.", "warn")
    if "위반건축물" in sp:
        add("위반건축물", "이행강제금·양성화 불가·대출 제한 가능. 건축물대장을 확인하세요.", "warn")
    if "농지취득자격" in sp:
        add("농지취득자격증명(농취증)", "미제출 시 보증금이 몰수됩니다. 입찰 전 발급 가능 여부를 확인하세요.", "high")
    if "재매각" in sp:
        add("재매각 보증금", "재매각은 입찰 보증금이 최저가의 20~30%입니다. 자금을 준비하세요.", "info")

    by = prop.get("built_year")
    if prop.get("type") == "아파트" and by and (datetime.now(timezone(timedelta(hours=9))).year - by) >= 30:
        add(f"재건축 연한({by}년 준공)", "노후 단지는 재건축 기대이익/멸실 리스크가 큽니다. 정비사업 단계를 확인하세요.", "info")

    # 항상 확인 (흔히 누락)
    add("미납 관리비 확인", "공용부분 미납 관리비(대법원 판례상 최대 3년치)는 낙찰자가 인수합니다. 관리사무소에 확인하세요.", "warn")
    if sp:
        add("경락잔금대출 가능 여부", "특수물건·위반건축물은 대출이 제한될 수 있어 실투자금이 커질 수 있습니다.", "warn")
    add("서류 교차 확인", "매각물건명세서·현황조사서·감정평가서·등기부를 반드시 직접 대조하세요.", "info")
    return out


# ----------------------- 경매 시장 통계 -----------------------
def market_stats(past):
    """실제 매각결과 기반 시장 통계: 매각건수·평균 매각가율·평균 경쟁률·최고/최저·유형별."""
    if not past:
        return None
    ratios = [p["sale_ratio"] for p in past if p.get("sale_ratio")]
    bidders = [p.get("bidders") for p in past if p.get("bidders")]
    by_type = {}
    for p in past:
        t = p.get("type") or "기타"
        by_type.setdefault(t, []).append(p.get("sale_ratio"))
    types = {t: {"n": len(v), "avg_ratio": round(statistics.mean([x for x in v if x]), 1) if any(v) else None}
             for t, v in by_type.items()}
    hi = max(past, key=lambda p: p.get("sale_ratio") or 0)
    lo = min([p for p in past if p.get("sale_ratio")], key=lambda p: p["sale_ratio"], default=None)
    return {
        "sold": len(past),
        "avg_ratio": round(statistics.mean(ratios), 1) if ratios else None,
        "avg_bidders": round(statistics.mean(bidders), 1) if bidders else None,
        "by_type": types,
        "top": {"region": hi.get("region"), "type": hi.get("type"), "ratio": hi.get("sale_ratio")} if ratios else None,
        "bottom": {"region": lo.get("region"), "type": lo.get("type"), "ratio": lo.get("sale_ratio")} if lo else None,
    }


# ----------------------- 성공률 (경쟁도) -----------------------
def base_ratio(prop, baselines):
    b = (baselines["sale_ratio"].get(prop.get("region"), {}).get(prop.get("type"))
         or baselines["default"].get(prop.get("type")) or baselines["default"]["기타"])
    return float(b["mean"]), float(b["std"]), float(b.get("bidders", 5))


def ratio_and_bidders(prop, sale, baselines, history, a):
    mean, std, base_bid = base_ratio(prop, baselines)
    # 과거사례 blend (낙찰가율)
    samples = [100 * h["won_bid"] / h["appraisal"] for h in history
               if h.get("region") == prop.get("region") and h.get("type") == prop.get("type") and h.get("appraisal")]
    if samples:
        w, n = baselines.get("blend_prior_weight", 8), len(samples)
        mean = (w * mean + n * statistics.mean(samples)) / (w + n)
        if n >= 2:
            std = (w * std + n * max(statistics.pstdev(samples), 3)) / (w + n)
    mean -= baselines.get("fail_round_penalty", 6) * (prop.get("fail_rounds") or 0)

    # 예상 입찰자 수(경쟁도): 물건 매력도(시세/감정가) ↑ → 경쟁 ↑, 유찰 → ↓
    c = a["competition"]
    attract = 1 + c["discount_boost"] * max(-0.3, (sale / prop["appraisal"]) - 0.95)
    lam = base_bid * attract * (1 - c["fail_damp"] * (prop.get("fail_rounds") or 0))
    hb = [h["bidders"] for h in history
          if h.get("region") == prop.get("region") and h.get("type") == prop.get("type") and h.get("bidders")]
    if hb:
        lam = (1 - c["history_weight"]) * lam + c["history_weight"] * statistics.mean(hb)
    lam = max(1.0, lam)
    # 경쟁 → 기대 낙찰가율 상향
    mean_adj = mean + c["k_ratio_per_bidder"] * (lam - c["ref_bidders"])
    return mean_adj, max(std, 3), round(lam, 1), round(mean, 1), sorted(samples)


def emp_cdf(x, samples):
    if not samples:
        return None
    return bisect.bisect_right(samples, x) / len(samples)


def success_prob(bid, appraisal, mean_adj, std, samples=None, w=0.0):
    """낙찰 성공확률. 실측 낙찰가율 경험분포(있으면)와 정규분포를 표본수만큼 가중 혼합."""
    my_ratio = 100 * bid / appraisal
    normal = norm_cdf((my_ratio - mean_adj) / std)
    if samples and w > 0:
        e = emp_cdf(my_ratio, samples)
        if e is not None:
            return w * e + (1 - w) * normal
    return normal


# ----------------------- 환금성(유동성) 점수 -----------------------
def liquidity_score(prop, baselines, a, trade_count):
    """빠른 재매도 가능성 0~100. 실거래 회전율·유형·수요·면적·가격대 반영."""
    L = a["liquidity"]
    tliq = L["type"].get(prop.get("type"), 0.3)
    _, _, bidders = base_ratio(prop, baselines)          # 지역·유형 수요(입찰자) 대리지표
    demand = min(1.0, bidders / 10.0)
    # 실거래 회전율: 실측 있으면 사용, 없으면(폴백) 수요로 대체
    tf = min(1.0, trade_count / L["trade_count_full"]) if trade_count is not None else demand
    area = prop.get("exclusive_area") or 0
    size = 1.0 if L["size_ideal_min"] <= area <= L["size_ideal_max"] else 0.6
    pb = 0.6 if prop["appraisal"] > L["price_high"] else 1.0
    raw = 0.30 * tliq + 0.25 * demand + 0.25 * tf + 0.10 * size + 0.10 * pb
    score = round(raw * 100)
    grade = "A" if score >= 75 else "B" if score >= 55 else "C" if score >= 35 else "D"
    signals = []
    if trade_count is not None:
        signals.append(f"최근거래 {trade_count}건")
    signals.append({"아파트": "아파트(높음)", "오피스텔": "오피스텔(중)",
                    "빌라": "빌라(낮음)"}.get(prop.get("type"), "기타"))
    if area and not (L["size_ideal_min"] <= area <= L["size_ideal_max"]):
        signals.append("비선호 면적")
    if prop["appraisal"] > L["price_high"]:
        signals.append("고가 구간")
    return {"score": score, "grade": grade, "signals": signals}


# ----------------------- 적정 입찰가 고도화(전략가) -----------------------
def bid_strategies(sale, prop, a, appr, mean_adj, std, liq, samples=None, w=0.0, ctx=None):
    """세 가지 전략가(ev_optimal·safe_max·win_target). 고정비용 ctx 재사용·고속 경로 사용."""
    c = ctx if (ctx and ctx.get("sale") == sale) else cost_ctx(prop, sale, a)
    lo, hi = prop["min_bid"], int(appr * 1.05)
    min_floor = a.get("min_roi_floor", 0.08)
    best_b, best_ev = None, -1e18
    any_b, any_ev = float(prop["min_bid"]), -1e18
    N = 61
    for i in range(N):
        b = lo + (hi - lo) * i / (N - 1)
        pr, roi = _pf(b, c, a)
        ev = success_prob(b, appr, mean_adj, std, samples, w) * pr
        if pr > 0 and ev > any_ev:
            any_ev, any_b = ev, b
        if roi >= min_floor and ev > best_ev:
            best_ev, best_b = ev, b
    ev_opt = int(best_b if best_b is not None else any_b)

    floor = a["target_profit_rate"] + (1 - liq / 100.0) * a.get("illiquid_margin_add", 0.10)
    lo2, hi2 = 0.0, float(sale)
    for _ in range(34):
        m = (lo2 + hi2) / 2
        if _pf(m, c, a)[1] >= floor:
            lo2 = m
        else:
            hi2 = m
    safe_max = int(lo2)

    wt = a.get("win_target", 0.6)
    lo3, hi3 = float(prop["min_bid"]), float(int(appr * 1.2))
    for _ in range(34):
        m = (lo3 + hi3) / 2
        if success_prob(m, appr, mean_adj, std, samples, w) >= wt:
            hi3 = m
        else:
            lo3 = m
    win_tgt = int(hi3)
    return {"ev_optimal": ev_opt, "safe_max": safe_max, "win_target": win_tgt,
            "roi_floor": round(floor, 3), "min_roi_floor": min_floor}, best_ev


# ----------------------- 종합 점수 (검증된 투자이론 기반) -----------------------
def composite_score(res, a):
    """환금성 최우선 + 유명 투자이론 조합:
      · 안전마진(Graham Margin of Safety): (보정가치−권장입찰가)/보정가치
      · 위험조정수익(Sharpe 개념): 수익률 ÷ 시세 변동위험
      · 낙찰가능성(성공률), 권리안전, 환금성.
    """
    w = a["score_weights"]
    liq = res["liquidity"]["score"]
    va = res.get("value_adjusted") or res.get("market_price") or 0
    rec = res.get("recommended_bid") or 0

    # 안전마진 (MoS): 25% 쿠션이면 만점
    mos = max(0.0, (va - rec) / va) if va else 0.0
    margin_s = min(1.0, mos / 0.25) * 100
    # 위험조정수익 (Sharpe-ish): ROI ÷ 위험(시세 변동계수), Sharpe 3 만점
    risk = max(a.get("resale_cv", 0.06), 0.03)
    sharpe_s = min(1.0, max(0.0, (res["roi"] / risk) / 3.0)) * 100
    win_s = res["success_prob"] * 100
    rights_s = 100 - res["rights_risk"]["score"]

    base = (w["liquidity"] * liq + w["margin"] * margin_s + w["sharpe"] * sharpe_s
            + w["rights"] * rights_s + w["win"] * win_s)
    gate = a["liquidity_gate"] + (1 - a["liquidity_gate"]) * (liq / 100.0)   # 환금성 게이트
    total = base * gate
    if res["net_profit"] <= 0:                                   # 순손실이면 상한 억제
        total = min(total, 20)
    br = {"환금성": round(liq), "안전마진": round(margin_s), "위험조정수익": round(sharpe_s),
          "권리안전": round(rights_s), "낙찰가능성": round(win_s)}
    return round(total), br


def kelly_fraction(res, a):
    """Kelly Criterion(연속형 하프켈리): f* = 0.5 · μ/σ².
    μ=기대수익률(ROI), σ=재매도가 불확실성에서 온 수익률 변동성. 자금배분 가이드(0~1)."""
    inv = (res.get("recommended_bid") or 0) + res.get("assumed_rights", 0)
    mu = res.get("roi") or 0
    if inv <= 0 or mu <= 0:
        return 0.0
    sale = res.get("value_adjusted") or res.get("market_price") or inv
    sigma = (sale * a.get("resale_cv", 0.06)) / inv
    if sigma <= 0:
        return 0.0
    return round(max(0.0, min(0.5 * mu / (sigma * sigma), 1.0)), 3)


# ----------------------- 물건 분석 -----------------------
def analyze_property(prop, baselines, a, history, cache, apt_info=None):
    appr = prop["appraisal"]
    sale, src, trade_count = valued_price(prop, cache, a)
    mean_adj, std, bidders, mean_raw, samples = ratio_and_bidders(prop, sale, baselines, history, a)
    w_emp = min(0.6, len(samples) / 20.0) if samples else 0.0   # 실측 표본 많을수록 경험분포 가중↑
    liq = liquidity_score(prop, baselines, a, trade_count)

    # 승자의 저주 보정(공통가치 경매): 낙찰 = 내 평가가 최고였다는 뜻 → 조건부 기대가치는
    # 시세보다 낮다. V_adj = 시세 × (1 − cv × E[max of N normals]).
    # 경쟁(N)·시세 불확실성(cv)이 클수록 보정폭↑ → 과열 물건일수록 보수적으로 써서 과다낙찰 방지.
    cv = a.get("resale_cv", 0.06)
    wc = min(a.get("wc_cap", 0.20), cv * expected_max_normal(bidders))
    sale_eff = int(sale * (1 - wc))
    ctx = cost_ctx(prop, sale_eff, a)                     # 고정비용 1회 계산 → 재사용

    strat, _ = bid_strategies(sale_eff, prop, a, appr, mean_adj, std, liq["score"], samples, w_emp, ctx)
    rec = max(strat["ev_optimal"], prop["min_bid"])
    profit, roi, costs, items = net_profit(rec, sale_eff, prop, a, ctx)   # 보정가치 기준(보수적)
    win = success_prob(rec, appr, mean_adj, std, samples, w_emp)
    ev = win * profit
    risk = rights_risk(prop)

    curve = []
    lo, hi = prop["min_bid"], int(appr * 1.05)
    for i in range(11):
        b = lo + (hi - lo) * i / 10
        pr, r = _pf(b, ctx, a)
        curve.append({"bid": int(b), "win": round(success_prob(b, appr, mean_adj, std, samples, w_emp), 4),
                      "profit": int(pr), "roi": round(r, 4)})

    res = {"id": prop["id"], "court": prop.get("court"), "address": prop.get("address"),
           "region": prop.get("region"), "type": prop.get("type"), "apt_name": prop.get("apt_name"),
           "exclusive_area": prop.get("exclusive_area"), "floor": prop.get("floor"),
           "total_floors": prop.get("total_floors"), "built_year": prop.get("built_year"),
           "building_detail": prop.get("building_detail"), "note": prop.get("note"),
           "orientation": prop.get("orientation"), "appraisal": appr, "min_bid": prop["min_bid"],
           "fail_rounds": prop.get("fail_rounds", 0), "sale_date": prop.get("sale_date"),
           "case_no": prop.get("case_no"), "views": prop.get("views"), "dept": prop.get("dept"),
           "market_price": sale, "market_source": src,
           "value_adjusted": sale_eff, "winners_curse": round(wc, 3),
           "recommended_bid": rec, "bid_strategies": strat,
           "discount_vs_market": round(1 - rec / sale, 4) if sale else None,
           "success_prob": round(win, 4), "expected_bidders": bidders,
           "net_profit": int(profit), "roi": round(roi, 4), "expected_value": int(ev),
           "cost_items": items, "total_cost": int(costs), "assumed_rights": assumed_rights_cost(prop),
           "rights_risk": risk, "liquidity": liq,
           "ratio_dist": {"mean": round(mean_adj, 1), "mean_raw": mean_raw, "std": round(std, 1)},
           "curve": curve}
    res.update(trade_info(prop, cache))          # 건축년도·실거래건수·평단가·범위
    if apt_info:
        res.update(apt_info)                     # 세대수·동수·사용승인일
    res["score"], res["score_breakdown"] = composite_score(res, a)
    res["kelly_fraction"] = kelly_fraction(res, a)
    res["special"] = special_tags(prop, res.get("rights_risk"))
    res["checklist"] = analysis_checklist(prop, res)
    res["distribution"] = distribution_table(res["recommended_bid"], prop.get("reg_rights"), prop.get("tenants"), prop.get("region"), a)
    return res


# ----------------------- 내 예측 vs 실제 낙찰 (패인 분석·학습) -----------------------
def predicted_bid(rec, baselines, a, cache):
    """과거/후보 물건에 현재 모델을 적용한 권장 입찰가(baseline만 사용해 누수 방지)."""
    appr = rec.get("appraisal") or 0
    sale, _, _ = valued_price(rec, cache, a)
    p = dict(rec)
    p.setdefault("min_bid", int(appr * (0.8 ** (rec.get("fail_rounds") or 0))))
    mean_adj, std, bidders, _, _ = ratio_and_bidders(p, sale, baselines, [], a)
    cv = a.get("resale_cv", 0.06)
    wc = min(a.get("wc_cap", 0.20), cv * expected_max_normal(bidders))
    sale_eff = int(sale * (1 - wc))
    liq = liquidity_score(p, baselines, a, None)["score"]
    strat, _ = bid_strategies(sale_eff, p, a, appr, mean_adj, std, liq)
    return max(strat["ev_optimal"], p["min_bid"]), sale, mean_adj


def strategy_review(past, baselines, a, cache):
    """과거 실제 낙찰 건에 내 현재 모델을 적용해 '내 권장가로 낙찰됐을지'를 채점하고,
    졌다면 패인을 진단한다(과열/과소예측/제약). 화면엔 노출하지 않고 파일로만 보관."""
    rows, gaps, biases = [], [], []
    reasons = {}
    for rec in past:
        appr = rec.get("appraisal") or 0
        won = rec.get("won_bid") or 0
        if not appr or not won:
            continue
        my_bid, sale, mean_adj = predicted_bid(rec, baselines, a, cache)
        would_win = my_bid >= won
        actual_ratio = 100 * won / appr
        my_ratio = 100 * my_bid / appr
        biases.append(actual_ratio - mean_adj)          # +면 실제가 예측보다 높음(과소예측)
        reason = None
        if not would_win:
            shortfall = (won - my_bid) / won
            gaps.append(shortfall)
            if actual_ratio > mean_adj + 3:
                reason = "낙찰가율 과소예측(경쟁 과열)"
            elif my_ratio < mean_adj - 3:
                reason = "목표수익률 제약으로 권장가가 낮음"
            else:
                reason = "시세·비용 보수적 산정으로 소폭 미달"
            reasons[reason] = reasons.get(reason, 0) + 1
        rows.append({"id": rec["id"], "region": rec.get("region"), "type": rec.get("type"),
                     "my_bid": my_bid, "won_bid": won, "would_win": would_win,
                     "pred_ratio": round(mean_adj, 1), "actual_ratio": round(actual_ratio, 1),
                     "shortfall_pct": round((won - my_bid) / won, 3) if not would_win else 0.0,
                     "reason": reason})
    n = len(rows)
    wins = sum(1 for r in rows if r["would_win"])
    dom = sorted(reasons.items(), key=lambda x: -x[1])
    summary = {
        "n": n, "would_win": wins,
        "would_win_rate": round(wins / n, 3) if n else 0,
        "avg_shortfall_pct": round(statistics.mean(gaps), 3) if gaps else 0,
        "ratio_bias": round(statistics.mean(biases), 1) if biases else 0,   # +면 낙찰가율 과소예측
        "top_reasons": [{"reason": k, "n": v} for k, v in dom],
        "lesson": _lesson(dom, statistics.mean(biases) if biases else 0),
    }
    return {"summary": summary, "cases": rows[:60]}


def _lesson(dom, bias):
    tips = []
    if bias >= 2:
        tips.append(f"낙찰가율을 평균 {bias:.1f}%p 과소예측 → baseline mean 상향 필요")
    elif bias <= -2:
        tips.append(f"낙찰가율을 평균 {abs(bias):.1f}%p 과대예측 → baseline mean 하향 여지")
    if dom and dom[0][0] == "목표수익률 제약으로 권장가가 낮음":
        tips.append("목표수익률(min_roi_floor)이 높아 좋은 물건을 놓침 → 하향 검토")
    if dom and dom[0][0] == "낙찰가율 과소예측(경쟁 과열)":
        tips.append("경쟁도(competition) 상향 또는 승자의 저주 보정 완화 검토")
    return " · ".join(tips) or "예측이 실측과 대체로 부합"


# ----------------------- 백테스트 · 통계 -----------------------
def backtest(history):
    rows = []
    for h in history:
        if not h.get("resale_price") or not h.get("won_bid"):
            continue
        profit = h["resale_price"] - h["won_bid"] - h.get("costs", 0)
        inv = h["won_bid"] + h.get("costs", 0)
        rows.append({"id": h["id"], "court": h.get("court"), "case_no": h.get("case_no"),
                     "region": h["region"], "type": h["type"], "apt_name": h.get("apt_name"),
                     "won_bid": h["won_bid"], "resale_price": h["resale_price"], "net_profit": profit,
                     "my_predicted_bid": h.get("my_predicted_bid"), "would_win": h.get("would_win"),
                     "roi": round(profit / inv, 4) if inv else 0,
                     "sale_ratio": round(100 * h["won_bid"] / h["appraisal"], 1) if h.get("appraisal") else None,
                     "bidders": h.get("bidders"), "resale_date": h.get("resale_date")})
    ps = [r["net_profit"] for r in rows]
    rs = [r["roi"] for r in rows]
    s = {"n": len(rows),
         "avg_net_profit": int(statistics.mean(ps)) if ps else 0,
         "median_net_profit": int(statistics.median(ps)) if ps else 0,
         "avg_roi": round(statistics.mean(rs), 4) if rs else 0,
         "win_rate_positive": round(sum(1 for p in ps if p > 0) / len(ps), 4) if ps else 0,
         "total_net_profit": int(sum(ps))}
    return {"summary": s, "cases": sorted(rows, key=lambda x: x.get("roi", 0), reverse=True)[:150]}


def region_stats(history):
    by = {}
    for h in history:
        if not h.get("appraisal"):
            continue
        by.setdefault(f'{h["region"]}·{h["type"]}', {"r": [], "b": []})
        by[f'{h["region"]}·{h["type"]}']["r"].append(100 * h["won_bid"] / h["appraisal"])
        if h.get("bidders"):
            by[f'{h["region"]}·{h["type"]}']["b"].append(h["bidders"])
    return {k: {"avg_sale_ratio": round(statistics.mean(v["r"]), 1),
                "avg_bidders": round(statistics.mean(v["b"]), 1) if v["b"] else None,
                "n": len(v["r"])} for k, v in sorted(by.items())}


def realized_from_past(past, cache, a, baselines):
    """실제 낙찰 + 국토부 시세(매도가 추정) → 실현(추정) 수익률 + 내 예측 적정가."""
    out = []
    for rec in past:
        sale, _, _ = valued_price(rec, cache, a)      # 현재 시세 = 매도가 추정
        won = rec.get("won_bid")
        if not won or not sale:
            continue
        _, _, costs, _ = net_profit(won, sale, rec, a)
        my_bid, _, _ = predicted_bid(rec, baselines, a, cache)   # 내가 예측했을 적정가
        out.append({"id": rec["id"], "court": rec.get("court"), "case_no": rec.get("case_no"),
                    "region": rec.get("region"), "type": rec.get("type"),
                    "apt_name": rec.get("apt_name"), "appraisal": rec.get("appraisal"), "won_bid": won,
                    "my_predicted_bid": my_bid, "would_win": my_bid >= won,
                    "resale_price": int(sale), "costs": int(costs),
                    "sale_ratio": rec.get("sale_ratio"),
                    "result_date": rec.get("result_date"), "resale_date": rec.get("result_date"),
                    "bidders": rec.get("bidders")})
    return out


def main():
    key = os.environ.get("MOLIT_SERVICE_KEY", "").strip()
    props = load("properties.json")
    baselines = load("baselines.json")
    a = load("assumptions.json")
    lookback = a.get("history_lookback_days", 30)
    months = a.get("molit_months", 6)
    workers = a.get("molit_workers", 8)

    past_real = load("past-results.json", []) or []
    if past_real:
        past_real = filter_recent_history(past_real, lookback)   # 최근 N일 낙찰만
        cache = build_trade_cache(props + past_real, key, months, workers)
        history = realized_from_past(past_real, cache, a, baselines)
        hsrc = "실제 낙찰가 + 국토부 시세(매도가 추정)"
    else:
        cache = build_trade_cache(props, key, months, workers)
        history = filter_recent_history(load("auction-history.json") or [], lookback)
        hsrc = "내장 샘플"

    print(f"[analyze] 물건 {len(props)}건 · 과거 실적 {len(history)}건({hsrc}) · 분석 중...", flush=True)
    apt_cache = build_apt_cache(props, key) if a.get("fetch_apt_details", True) else {}
    results = [analyze_property(p, baselines, a, history, cache, apt_cache.get(p["id"])) for p in props]
    results.sort(key=lambda r: r["score"], reverse=True)

    # 점수 상위 물건에 courtauction 실제 사진(HAR 상세) 자동 수집 — 영구 캐시
    photo_n = a.get("photo_top_n", 12)
    if photo_n and results:
        try:
            import crawl
            pcache = _load_json("photo-detail-cache.json")
            by_id = {p.get("id"): p for p in props}
            opener, added = None, 0
            for r in results[:photo_n]:
                if r.get("photos"):
                    continue
                pid = r.get("id")
                shot = pcache.get(pid)
                if shot is None:
                    src = by_id.get(pid) or {}
                    court, case = src.get("bo_cd"), src.get("case_no")
                    if not (court and case):
                        continue
                    if opener is None:
                        opener = crawl.make_opener()
                    d = crawl.fetch_detail(opener, court, case, src.get("maemul_ser", 1))
                    shot = (d.get("photos") or []) if d else []
                    pcache[pid] = shot
                if shot:
                    r["photos"] = shot
                    added += 1
            save("photo-detail-cache.json", pcache)
            if added:
                print(f"[analyze] 물건 사진: 상위 {photo_n}건 중 {added}건 수집(courtauction 상세)", flush=True)
        except Exception as e:  # noqa: BLE001
            print(f"[analyze] 사진 수집 건너뜀: {type(e).__name__}", file=sys.stderr)
    save("analysis.json", {
        "generated_at": datetime.now(timezone(timedelta(hours=9))).isoformat(),
        "market_source_used": "molit_api" if key else "fallback(override/appraisal)",
        "history_lookback_days": lookback, "history_used": len(history),
        "history_total": len(past_real) if past_real else None, "history_source": hsrc,
        "assumptions": a, "properties": results,
        "backtest": backtest(history), "region_stats": region_stats(history),
        "market_stats": market_stats(past_real if past_real else history)})

    # 백테스트/패인분석은 화면에 노출하지 않고 별도 파일로만 보관(나중에 모델 고도화 근거로 사용)
    if past_real:
        review = strategy_review(past_real, baselines, a, cache)
        review["generated_at"] = datetime.now(timezone(timedelta(hours=9))).isoformat()
        review["how_to_use"] = "이 파일을 업로드하면 예측 vs 실제 낙찰 오차·패인을 근거로 baselines/assumptions를 고도화합니다."
        save("backtest.json", review)
        print(f"[analyze] 전략 백테스트 → data/backtest.json "
              f"(적중률 {review['summary']['would_win_rate']*100:.0f}%)", flush=True)
    print(f"[analyze] 완료: {len(results)}건 → data/analysis.json", flush=True)
    for r in results:
        lq = r["liquidity"]
        print(f'  [{r["score"]:>3}점] {r["apt_name"] or r["type"]} {r["region"]}: '
              f'적정 {r["recommended_bid"]:,} / 성공률 {r["success_prob"]*100:.0f}% / '
              f'순이익 {r["net_profit"]:,}(ROI {r["roi"]*100:.1f}%) / '
              f'환금성 {lq["grade"]}({lq["score"]}) / 권리 {r["rights_risk"]["level"]}')


if __name__ == "__main__":
    main()
