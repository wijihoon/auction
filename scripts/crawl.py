#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
법원경매정보(courtauction.go.kr) 실시간 물건 수집기.

검증된 공식 웹스퀘어 엔드포인트를 직접 호출한다:
  검색       POST /pgj/pgjsearch/searchControllerMain.on
  사건상세   POST /pgj/pgj15A/selectAuctnCsSrchRslt.on

이 수집기는 결과를 analyze.py/track.py가 먹는 공용 스키마로 직접 저장하며,
주소에서 법정동코드(lawd_cd)를 파생해 국토부 실거래가 시세 조회가 동작하게 한다.

설계 원칙(안정성):
- 세션 초기화가 실패해도 포기하지 않고 검색으로 진행(불안정한 해외 접속 대비).
- 페이지마다 독립 try/except. 수집 0건이면 기존 properties.json을 보존(덮어쓰지 않음).
- 항상 정상 종료(exit 0). 추정·하드코딩 값은 넣지 않는다(모르면 null).

표준 라이브러리만 사용.
"""
import os, sys, json, re, ssl, time, math, random, socket, threading
import http.cookiejar
import urllib.request, urllib.error
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DATA = os.path.join(ROOT, "data")


def _load_cfg(name, default):
    p = os.path.join(DATA, name)
    if os.path.exists(p):
        try:
            return json.load(open(p, encoding="utf-8"))
        except Exception:
            return default
    return default
OUT = os.path.join(DATA, "properties.json")
KST = timezone(timedelta(hours=9))

BASE = "https://www.courtauction.go.kr"
SEARCH_EP = BASE + "/pgj/pgjsearch/searchControllerMain.on"
UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36")

# 용도 표시명 → 공용 스키마 type
def type_from_usage(u):
    u = u or ""
    if "아파트" in u:
        return "아파트"
    if "오피스텔" in u:
        return "오피스텔"
    if any(k in u for k in ("연립", "다세대", "빌라")):
        return "빌라"
    return "기타"


# 법정동코드(시군구→5자리): data/lawd-codes.json 에서 로드(없으면 빈 맵→시세 폴백)
SIGUNGU_LAWD = _load_cfg("lawd-codes.json", {})
_TEXT_RULES = _load_cfg("text-rules.json", {})
_LAWD_KEYS = sorted(SIGUNGU_LAWD.keys(), key=len, reverse=True)


def lawd_from_address(addr):
    a = addr or ""
    for k in _LAWD_KEYS:
        if k in a:
            return SIGUNGU_LAWD[k]
    return ""


def region_from_address(addr):
    """baseline 매칭용: 서울/인천은 '시도 구', 경기는 '경기 시'."""
    if not addr:
        return ""
    p = addr.split()
    sido = p[0]
    short = ("서울" if "서울" in sido else "인천" if "인천" in sido
             else "경기" if "경기" in sido else sido.replace("특별시", "").replace("광역시", "").replace("도", ""))
    if short in ("서울", "인천"):
        for t in p[1:]:
            if t.endswith("구") or t.endswith("군"):
                return f"{short} {t}"
    if short == "경기":
        for t in p[1:]:
            if t.endswith("시"):
                return f"{short} {t}"
    return f"{short} {p[1]}" if len(p) > 1 else short


def extract_area(text):
    m = re.search(r'([\d.]+)\s*(?:㎡|m2|M2)', str(text or ""))
    if m:
        try:
            return round(float(m.group(1)), 2)
        except ValueError:
            pass
    return None


def extract_floor(text):
    m = re.search(r'제?\s*(\d+)\s*층', str(text or ""))
    return int(m.group(1)) if m else None


def extract_apt_name(addr, bld):
    """단지/건물명 추정. ①도로명주소 '(동명, 건물명)'의 건물명 → ②접미사 패턴 → ③동명 폴백."""
    addr = addr or ""
    for grp in re.findall(r'\(([^)]+)\)', addr):      # ① "(매탄동, 매탄위브하늘채)" → 콤마 뒤 건물명
        if "," in grp:
            nm = grp.split(",")[-1].strip()
            if nm and not re.fullmatch(r'[\d\-.,\s]+', nm) and not nm.endswith(("동", "호", "층", "가")):
                return nm
    suffix = ("|".join(_TEXT_RULES.get("apt_suffixes", ["아파트"])) or "아파트")
    pat = re.compile(r'([가-힣A-Za-z0-9]{2,}(?:%s)\d*(?:단지)?)' % suffix)
    for src in (bld or "", addr):                     # ② 건물명 접미사
        m = pat.search(src)
        if m:
            return m.group(1)
    m = re.search(r'([가-힣]+(?:동|읍|면))', addr)      # ③ 동/읍/면 폴백
    return m.group(1) if m else ""


SPECIAL_RIGHTS_KW = _TEXT_RULES.get("special_rights", ["유치권", "법정지상권", "지분", "대지권미등기"])


def analyze_rights(row):
    """검색행의 비고/현황 텍스트에서 권리 위험을 보수적으로 추출(공용 스키마)."""
    notes = " ".join(str(row.get(k, "") or "") for k in ("mulBigo", "pjbBuldList", "gdsDspslObjClsNm", "rmk"))
    senior_tenant = False
    assumed_deposit = 0
    special = [k for k in SPECIAL_RIGHTS_KW if k in notes]
    lien = 0
    if any(w in notes for w in ("임차인", "대항력", "전입", "보증금")):
        if "대항력" in notes and "없음" not in notes:
            if "배당요구" not in notes or "미배당" in notes or "배당요구종기" in notes:
                senior_tenant = True
                m = re.search(r'보증금\s*([\d,]+)\s*만', notes)
                if m:
                    assumed_deposit = int(m.group(1).replace(",", "")) * 10000
    if "유치권" in notes:
        m = re.search(r'유치권\D*([\d,]+)\s*만', notes)
        if m:
            lien = int(m.group(1).replace(",", "")) * 10000
    return {"senior_tenant": senior_tenant, "assumed_deposit": assumed_deposit,
            "special_rights": special, "lien_amount": lien}


# --------------------- 세션 ---------------------
def make_opener():
    cj = http.cookiejar.CookieJar()
    ctx = ssl.create_default_context()
    ctx.check_hostname = False
    ctx.verify_mode = ssl.CERT_NONE
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj),
                                     urllib.request.HTTPSHandler(context=ctx))
    try:  # 세션 쿠키 확보(실패해도 계속 진행)
        req = urllib.request.Request(BASE + "/", headers={
            "User-Agent": UA, "Accept-Language": "ko-KR,ko;q=0.9,en;q=0.7",
            "Accept": "text/html,application/xhtml+xml,*/*;q=0.8"})
        op.open(req, timeout=12).read()
    except Exception as e:  # noqa: BLE001
        print(f"[crawl] 세션 초기화 경고(무시하고 진행): {type(e).__name__}", file=sys.stderr)
    return op


def _to_int(x, d=0):
    try:
        return int(str(x).replace(",", ""))
    except (ValueError, TypeError):
        return d


# --------------------- 수집 ---------------------
def fetch_page(opener, page, bgn, end, timeout=12, retries=3):
    """검색 1페이지. 지수 백오프+지터 재시도. 실패 None, (rows, total_cnt) 반환."""
    headers = {"User-Agent": UA, "Content-Type": "application/json;charset=UTF-8",
               "Accept": "application/json", "Accept-Language": "ko-KR,ko;q=0.9",
               "Referer": BASE + "/pgj/index.on?w2xPath=/pgj/ui/pgj100/PGJ151F00.xml",
               "submissionid": "sbm_selectGdsDtlSrch", "SC-Pgmid": "PGJ151M01"}
    payload = {
        "dma_pageInfo": {"pageNo": str(page), "pageSize": "40", "totalYn": "Y" if page == 1 else "N"},
        "dma_srchGdsDtlSrchInfo": {"mvprpRletDvsCd": "00031R", "cortAuctnSrchCondCd": "0004601",
                                   "cortStDvs": "0", "bidBgngYmd": bgn, "bidEndYmd": end, "pgmId": "PGJ151M01"},
    }
    for attempt in range(retries):
        try:
            req = urllib.request.Request(SEARCH_EP, data=json.dumps(payload).encode("utf-8"),
                                         headers=headers, method="POST")
            with opener.open(req, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8")).get("data", {})
                total = None
                if page == 1:
                    try:
                        total = int(data.get("dma_pageInfo", {}).get("totalCnt", 0))
                    except Exception:
                        total = None
                return data.get("dlt_srchResult", []), total
        except urllib.error.HTTPError as e:
            if attempt == retries - 1:
                print(f"[crawl] p{page} HTTP {e.code}", file=sys.stderr, flush=True)
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                print(f"[crawl] p{page} {type(e).__name__}", file=sys.stderr, flush=True)
        time.sleep(0.35 * (attempt + 1) + random.uniform(0.05, 0.15))
    return None, None


def row_to_item(row, f):
    sido = row.get("hjguSido", "") or row.get("printSt", "")
    usage = row.get("dspslUsgNm", "") or ""
    if not any(s in sido for s in f["sido"]):
        return None
    if not any(u in usage for u in f["usage"]):
        return None
    appr = _to_int(row.get("gamevalAmt"))
    if appr < f["min_appr"] or appr > f["max_appr"]:
        return None
    case = row.get("srnSaNo", "")
    if not case:
        return None
    court = row.get("jiwonNm", "법원")
    seq = _to_int(row.get("maemulSer", 1), 1)
    addr = (row.get("printSt", "") or "").strip()
    bld = row.get("pjbBuldList", "") or ""
    raw = str(row.get("maeGiil", ""))
    sale_date = f"{raw[:4]}-{raw[4:6]}-{raw[6:]}" if len(raw) == 8 else None
    tf = re.search(r'(\d+)\s*층', row.get("buldList") or bld or "")
    by = re.search(r'((?:19|20)\d{2})\s*(?:년|\.)', bld)
    item = {"id": f"{court}_{case}_{seq}", "court": court, "case_no": case, "address": addr,
            "region": region_from_address(addr), "type": type_from_usage(usage),
            "apt_name": extract_apt_name(addr, bld),
            "lawd_cd": (row.get("srchHjguSiguCd") if (str(row.get("srchHjguSiguCd") or "").isdigit() and len(str(row.get("srchHjguSiguCd")))==5) else lawd_from_address(addr)),
            "exclusive_area": extract_area(bld), "floor": extract_floor(row.get("buldList") or bld),
            "total_floors": int(tf.group(1)) if tf else None,
            "built_year": int(by.group(1)) if by else None,
            "building_detail": (bld or "").strip()[:120] or None,
            "note": ((row.get("mulBigo") or row.get("rmk") or "").strip()[:160]) or None,
            "usage_detail": usage or None, "views": _to_int(row.get("inqCnt")), "dept": row.get("jpDeptNm") or None,
            "appraisal": appr, "min_bid": _to_int(row.get("minmaePrice"), appr),
            "fail_rounds": _to_int(row.get("yuchalCnt")), "sale_date": sale_date,
            "eviction": "normal", "market_price_override": None, "photos": [], "bo_cd": row.get("boCd"), "maemul_ser": seq,
            "reg_rights": [], "tenants": []}  # 물건상세(등기·임차)에서 채우면 배당표 자동 계산
    item.update(analyze_rights(row))
    return item


def crawl(cfg):
    f = {"sido": cfg.get("sido", ["서울특별시", "경기도", "인천광역시"]),
         "usage": cfg.get("usage", ["아파트", "오피스텔", "연립다세대", "다세대", "연립", "빌라"]),
         "min_appr": cfg.get("min_appraisal", 50000000),
         "max_appr": cfg.get("max_appraisal", 5000000000)}
    days = cfg.get("sale_date_to_days", 60)
    cap = cfg.get("max_properties", 100000) or 100000
    workers = cfg.get("max_workers", 8)
    timeout = cfg.get("request_timeout_sec", 12)
    retries = cfg.get("max_retries", 3)
    max_pages_cap = cfg.get("max_pages", 800)
    now = datetime.now(KST)
    bgn, end = now.strftime("%Y%m%d"), (now + timedelta(days=days)).strftime("%Y%m%d")

    t0 = time.time()
    print(f"[crawl] 수집 시작 · 기간 {bgn}~{end} · 워커 {workers}", flush=True)
    print("[crawl] 세션 준비 중...", flush=True)
    opener = make_opener()          # 세션 1개(데운)를 모든 스레드가 공유
    print("[crawl] 1페이지 조회(총건수 확인) 중...", flush=True)
    first_rows, total = fetch_page(opener, 1, bgn, end, timeout, retries)
    if first_rows is None:
        print("[crawl] 1페이지 실패(재시도 초과) — 수집 중단", file=sys.stderr, flush=True)
        return []
    if total and total > 0:
        total_pages = min(math.ceil(total / 40), max_pages_cap)
        print(f"[crawl] 총 {total:,}건 / {total_pages}페이지 · 병렬 수집 시작", flush=True)
    else:
        total_pages = min(60, max_pages_cap)
        print(f"[crawl] 총건수 확인불가 — 기본 {total_pages}페이지 스캔", flush=True)

    props, seen = [], set()

    def take(rows):
        for row in rows or []:
            if len(props) >= cap:
                return
            item = row_to_item(row, f)
            if not item or item["id"] in seen:
                continue
            seen.add(item["id"])
            props.append(item)

    take(first_rows)
    pages = list(range(2, total_pages + 1))
    batch = 20
    for i in range(0, len(pages), batch):
        chunk = pages[i:i + batch]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            results = list(ex.map(lambda p: fetch_page(opener, p, bgn, end, timeout, retries)[0], chunk))
        ok = sum(1 for r in results if r is not None)
        for rows in results:
            take(rows)
        done = chunk[-1]
        pctv = done * 100 // total_pages
        print(f"[crawl] {done}/{total_pages}p ({pctv}%) · 응답 {ok}/{len(chunk)} · 누적 {len(props)}건 · {time.time()-t0:.0f}s",
              flush=True)
        if len(props) >= cap:
            break
    print(f"[crawl] 완료: 수집 {len(props)}건 · 총 {time.time()-t0:.0f}s", flush=True)
    return props


PAST_EP = BASE + "/pgj/pgjsearch/selectDspslSchdRsltSrch.on"
PAST_OUT = os.path.join(DATA, "past-results.json")


def fetch_past_page(opener, page, timeout=12, retries=3):
    """매각결과(과거 낙찰) 1페이지. 지수 백오프 재시도."""
    headers = {"User-Agent": UA, "Content-Type": "application/json;charset=UTF-8",
               "Accept": "application/json", "Accept-Language": "ko-KR,ko;q=0.9",
               "Referer": BASE + "/pgj/index.on?w2xPath=/pgj/ui/pgj100/PGJ158M02.xml",
               "submissionid": "sbm_selectDspslRsltSrch", "SC-Pgmid": "PGJ158M02"}
    payload = {"dma_pageInfo": {"pageNo": str(page), "pageSize": "40", "totalYn": "Y" if page == 1 else "N"},
               "dma_srchGdsDtlSrchInfo": {"pgmId": "PGJ158M02", "statNum": "3", "cortStDvs": "0",
                                          "mvprpRletDvsCd": "00031R"}}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(PAST_EP, data=json.dumps(payload).encode("utf-8"),
                                         headers=headers, method="POST")
            with opener.open(req, timeout=timeout) as r:
                data = json.loads(r.read().decode("utf-8")).get("data", {})
                total = None
                if page == 1:
                    try:
                        total = int(data.get("dma_pageInfo", {}).get("totalCnt", 0))
                    except Exception:
                        total = None
                return data.get("dlt_srchResult", []), total
        except urllib.error.HTTPError as e:
            if attempt == retries - 1:
                print(f"[past] p{page} HTTP {e.code}", file=sys.stderr)
        except Exception as e:  # noqa: BLE001
            if attempt == retries - 1:
                print(f"[past] p{page} {type(e).__name__}", file=sys.stderr)
        time.sleep(0.35 * (attempt + 1) + random.uniform(0.05, 0.15))
    return None, None


def past_row_to_item(row, f, cutoff):
    won = _to_int(row.get("maeAmt"))
    if won <= 0:                                  # 낙찰 건만
        return None
    appr = _to_int(row.get("gamevalAmt"))
    if appr < f["min_appr"] or appr > f["max_appr"]:
        return None
    usage = row.get("dspslUsgNm", "") or ""
    if not any(u in usage for u in f["usage"]):
        return None
    sido = row.get("hjguSido", "") or row.get("printSt", "")
    if not any(s in sido for s in f["sido"]):
        return None
    raw = str(row.get("maeGiil", ""))
    if len(raw) == 8 and raw < cutoff:            # 최근 N일만
        return None
    case = row.get("srnSaNo", "")
    if not case:
        return None
    court = row.get("jiwonNm", "법원")
    seq = _to_int(row.get("maemulSer", 1), 1)
    addr = (row.get("printSt", "") or "").strip()
    bld = row.get("pjbBuldList", "") or ""
    rdate = f"{raw[:4]}-{raw[4:6]}-{raw[6:]}" if len(raw) == 8 else None
    return {"id": f"{court}_{case}_{seq}", "court": court, "case_no": case,
            "region": region_from_address(addr),
            "type": type_from_usage(usage), "apt_name": extract_apt_name(addr, bld),
            "lawd_cd": lawd_from_address(addr), "exclusive_area": extract_area(bld),
            "appraisal": appr, "won_bid": won,
            "sale_ratio": round(100 * won / appr, 1) if appr else None,
            "result_date": rdate, "fail_rounds": _to_int(row.get("yuchalCnt")),
            "eviction": "normal", "address": addr, "bidders": _to_int(row.get("gugsu")) or None}


def crawl_past(cfg):
    f = {"sido": cfg.get("sido", ["서울특별시", "경기도", "인천광역시"]),
         "usage": cfg.get("usage", ["아파트", "오피스텔", "연립다세대", "다세대", "연립", "빌라"]),
         "min_appr": cfg.get("min_appraisal", 50000000), "max_appr": cfg.get("max_appraisal", 5000000000)}
    days = cfg.get("past_history_days", 60)
    workers = cfg.get("max_workers", 8)
    timeout = cfg.get("request_timeout_sec", 12)
    retries = cfg.get("max_retries", 3)
    max_pages_cap = cfg.get("max_pages", 800)
    cutoff = (datetime.now(KST) - timedelta(days=days)).strftime("%Y%m%d")
    t0 = time.time()
    print(f"[past] 매각결과 수집 시작 · 최근 {days}일({cutoff}~)", flush=True)
    opener = make_opener()
    first, total = fetch_past_page(opener, 1, timeout, retries)
    if first is None:
        print("[past] 1페이지 실패 — 매각결과 수집 중단", file=sys.stderr)
        return []
    total_pages = min(math.ceil(total / 40), max_pages_cap) if total else min(120, max_pages_cap)
    print(f"[past] 총 {total or '?'}건 / {total_pages}페이지", flush=True)
    out, seen = [], set()

    def take(rows):
        for row in rows or []:
            it = past_row_to_item(row, f, cutoff)
            if not it or it["id"] in seen:
                continue
            seen.add(it["id"])
            out.append(it)

    take(first)
    pages = list(range(2, total_pages + 1))
    for i in range(0, len(pages), 20):
        chunk = pages[i:i + 20]
        with ThreadPoolExecutor(max_workers=workers) as ex:
            res = list(ex.map(lambda p: fetch_past_page(opener, p, timeout, retries)[0], chunk))
        before = len(out)
        for rows in res:
            take(rows)
        print(f"[past] ~{chunk[-1]}/{total_pages}p · 누적 {len(out)}건 · {time.time()-t0:.0f}s", flush=True)
        if out and len(out) == before:            # 최근 구간을 지나 더 안 늘면 종료
            break
    print(f"[past] 완료: 낙찰 {len(out)}건 · {time.time()-t0:.0f}s", flush=True)
    return out


DETAIL_EP = BASE + "/pgj/pgj15B/selectAuctnCsSrchRslt.on"


def parse_detail(res):
    """물건 상세(dma_result) → 실제 사진·회차별 기일·권리텍스트·말소기준일."""
    g = res.get("dspslGdsDxdyInfo", {}) or {}
    b = res.get("csBaseInfo", {}) or {}
    photos = []
    for pic in res.get("csPicLst", []) or []:
        data = pic.get("picFile") or ""
        if isinstance(data, str) and data.startswith("/9j/"):        # JPEG base64 인라인
            photos.append("data:image/jpeg;base64," + data)
        elif isinstance(data, str) and data.startswith("iVBOR"):     # PNG base64
            photos.append("data:image/png;base64," + data)
    schedule = []
    for x in res.get("gdsDspslDxdyLst", []) or []:
        ymd = str(x.get("dxdyYmd") or "")
        if len(ymd) == 8:
            schedule.append({"date": f"{ymd[:4]}-{ymd[4:6]}-{ymd[6:]}",
                             "low": _to_int(x.get("tsLwsDspslPrc")),
                             "sold": _to_int(x.get("dspslAmt")) or None,
                             "result": x.get("auctnDxdyRsltCd")})
    spec = " ".join(str(g.get(k) or "") for k in ("gdsSpcfcRmk", "dspslGdsRmk", "ndstrcRghCtt")).strip()
    m = re.search(r'((?:19|20)\d{2})[.\s]+(\d{1,2})[.\s]+(\d{1,2})', g.get("tprtyRnkHypthcStngDts") or "")
    base_date = f"{m.group(1)}-{int(m.group(2)):02d}-{int(m.group(3)):02d}" if m else None
    demn = (res.get("dstrtDemnInfo") or [{}])
    dd = demn[0].get("dstrtDemnLstprdYmd") if demn else None
    demand_end = f"{dd[:4]}-{dd[4:6]}-{dd[6:]}" if (dd and len(str(dd)) == 8) else None
    objs = res.get("gdsDspslObjctLst") or [{}]
    return {"photos": photos[:4], "schedule": schedule,
            "detail_note": (spec[:400] or None), "base_date": base_date,
            "claim_amt": _to_int(b.get("clmAmt")) or None, "demand_end": demand_end,
            "ecdoc_id": g.get("dspslGdsSpcfcEcdocId") or None,
            "orv_param": (objs[0] or {}).get("orvParam") or g.get("orvParam"),
            "dspsl_gds_seq": g.get("dspslGdsSeq") or 1, "cs_no14": b.get("csNo") or None}


def fetch_detail(opener, court_cd, cs_no, seq, timeout=15, retries=2):
    """물건 상세 조회. court_cd=boCd, cs_no=srnSaNo, seq=maemulSer."""
    headers = {"User-Agent": UA, "Content-Type": "application/json;charset=UTF-8", "Accept": "application/json",
               "SC-Pgmid": "PGJ15BM01", "submissionid": "mf_wfm_mainFrame_sbm_selectGdsDtlSrchDtlInfo",
               "Referer": BASE + "/pgj/index.on?w2xPath=/pgj/ui/pgj100/PGJ151F00.xml"}
    payload = {"dma_srchGdsDtlSrch": {"csNo": cs_no, "cortOfcCd": court_cd, "dspslGdsSeq": str(seq),
               "pgmId": "PGJ151F01", "srchInfo": {"bidDvsCd": "000331", "mvprpRletDvsCd": "00031R",
               "cortAuctnSrchCondCd": "0004601", "cortOfcCd": court_cd}}}
    for attempt in range(retries):
        try:
            req = urllib.request.Request(DETAIL_EP, data=json.dumps(payload).encode("utf-8"),
                                         headers=headers, method="POST")
            with opener.open(req, timeout=timeout) as r:
                res = json.loads(r.read().decode("utf-8")).get("data", {}).get("dma_result", {})
            return parse_detail(res)
        except Exception:  # noqa: BLE001
            if attempt == retries - 1:
                return {}
            time.sleep(0.4)
    return {}


ECFS = "https://ecfs.scourt.go.kr"
SDOC = "https://pvo.scourt.go.kr/streamdocs/v4/documents"
SPEC_CACHE = os.path.join(DATA, "spec-cache.json")


def _post_json(opener, url, payload, referer, timeout=15):
    headers = {"User-Agent": UA, "Content-Type": "application/json;charset=UTF-8",
               "Accept": "application/json", "Referer": referer}
    req = urllib.request.Request(url, data=json.dumps(payload).encode("utf-8"),
                                 headers=headers, method="POST")
    with opener.open(req, timeout=timeout) as r:
        return json.loads(r.read().decode("utf-8"))


def fetch_specification(opener, court, cs_no14, seq, ecdoc_id, orv_param, max_pages=20):
    """매각물건명세서 → 임차인·말소기준일·배당요구종기. 실패 시 {} (파이프라인 계속)."""
    if not (court and cs_no14 and ecdoc_id):
        return {}
    try:
        # 1) courtauction: encParam 발급(+세션)
        r1 = _post_json(opener, BASE + "/pgj/pgj15B/insertDspslGdsSpecArtcWdrwInf.on",
                        {"dma_dspslGdsSpecLog": {"cortOfcCd": court, "csNo": cs_no14,
                         "dspslGdsSeq": int(seq or 1), "orvParam": orv_param or "",
                         "dspslGdsSpcfcEcdocId": ecdoc_id}}, BASE + "/pgj/index.on")
        info = (r1.get("data") or {}).get("dma_dspslSpcfcInfo") or {}
        enc, ecfs_url = info.get("encParam"), info.get("url")
        if not (enc and ecfs_url):
            return {}
        # 2) ecfs 뷰어 세션 프라이밍(encParam → 쿠키)
        try:
            sep = "&" if "?" in ecfs_url else "?"
            opener.open(urllib.request.Request(ecfs_url + sep + "encParam=" + enc,
                        headers={"User-Agent": UA}), timeout=timeout_default()).read()
        except Exception:  # noqa: BLE001
            pass
        # 3) getPdf → streamdocsId
        r3 = _post_json(opener, ECFS + "/sgvo/sgvomain/getPdf.on",
                        {"dma_srchEdms": {"ecdocId": ecdoc_id, "ecdocDtlSeq": "1",
                         "csNo": cs_no14, "extnlUserYn": "Y", "bubviewerYn": "N", "jobKind": "JH"}},
                        ECFS + "/sgvo/websquare/websquare.html")
        sdoc = (r3.get("data") or {}).get("streamdocsId")
        if not sdoc:
            return {}
        # 4) streamdocs 텍스트 레이어 페이지 수집
        pages = {}
        for n in range(max_pages):
            try:
                req = urllib.request.Request(f"{SDOC}/{sdoc}/texts/{n}",
                      headers={"User-Agent": UA, "Referer": "https://pvo.scourt.go.kr/streamdocs/view"})
                pages[n] = json.loads(opener.open(req, timeout=15).read().decode("utf-8"))
            except Exception:  # noqa: BLE001
                break
        return parse_specification(pages) if pages else {}
    except Exception:  # noqa: BLE001
        return {}


def timeout_default():
    return 15


def _spec_page_lines(items):
    """ecfs 문서뷰어 페이지(text+rect 조각들)를 위치 기준으로 줄 복원."""
    frags = []
    for it in items or []:
        rects = it.get("rect") or []
        if not rects:
            continue
        top = max(r["top"] for r in rects)
        left = min(r["left"] for r in rects)
        frags.append((top, left, (it.get("text") or "").replace(" ", "")))
    frags.sort(key=lambda f: (-f[0], f[1]))
    lines, buf, cur = [], [], None
    for top, left, txt in frags:
        if cur is None or abs(top - cur) <= 6:
            buf.append(txt)
            cur = cur or top
        else:
            lines.append("".join(buf))
            buf, cur = [txt], top
    if buf:
        lines.append("".join(buf))
    return lines


_SPEC_ROW = re.compile(r'(\d{4})\.(\d{2})\.(\d{2})\.?(\d{1,3}(?:,\d{3})+)'
                       r'(\d{4})\.(\d{2})\.(\d{2})\.?(\d{4})\.(\d{2})\.(\d{2})')


def parse_specification(pages):
    """매각물건명세서(ecfs 문서뷰어 페이지 dict {페이지no: [조각]}) → 임차인·말소기준일·배당요구종기.
    임차 행: 임대차기간·보증금·전입일·확정일을 텍스트 레이어에서 추출."""
    lines = []
    for _, items in sorted(pages.items()):
        lines += _spec_page_lines(items)
    text = " ".join(lines)
    base = re.search(r'(\d{4})\.(\d{1,2})\.(\d{1,2})\.\s*근저당', text)
    base_date = f"{base[1]}-{int(base[2]):02d}-{int(base[3]):02d}" if base else None
    de = re.search(r'배당요구종기\s*(\d{4})\.(\d{1,2})\.(\d{1,2})', text)
    demand_end = f"{de[1]}-{int(de[2]):02d}-{int(de[3]):02d}" if de else None
    tenants, seen = [], set()
    for ln in lines:
        for m in _SPEC_ROW.finditer(ln.replace(" ", "")):
            g = m.groups()
            key = (g[3], g[4] + g[5] + g[6], g[7] + g[8] + g[9])
            if key in seen:
                continue
            seen.add(key)
            tenants.append({"deposit": int(g[3].replace(",", "")),
                            "lease_start": f"{g[0]}-{g[1]}-{g[2]}",
                            "movein": f"{g[4]}-{g[5]}-{g[6]}",
                            "fixed": f"{g[7]}-{g[8]}-{g[9]}",
                            "demand": True})   # 배당요구 여부는 열 위치 기반으로 추후 정밀화
    return {"base_date": base_date, "demand_end": demand_end, "tenants": tenants}


def sample_properties():
    p = os.path.join(DATA, "properties.sample.json")
    if os.path.exists(p):
        with open(p, encoding="utf-8") as f:
            return json.load(f)
    return []


def save(props):
    with open(OUT, "w", encoding="utf-8") as f:
        json.dump(props, f, ensure_ascii=False, indent=2)


def main():
    cfg = {}
    cp = os.path.join(DATA, "crawl-config.json")
    if os.path.exists(cp):
        with open(cp, encoding="utf-8") as f:
            cfg = json.load(f)

    if "--sample" in sys.argv:
        props = sample_properties()
        save(props)
        print(f"[sample] {len(props)}건 → properties.json")
        return

    socket.setdefaulttimeout(cfg.get("socket_timeout_sec", 15))  # 행(hang) 방지
    try:
        props = crawl(cfg)
    except Exception as e:  # noqa: BLE001
        print(f"[crawl] 수집 오류: {type(e).__name__}: {e}", file=sys.stderr)
        props = []

    if props:
        save(props)
        with_lawd = sum(1 for p in props if p.get("lawd_cd"))
        print(f"[crawl] 수집 {len(props)}건 → properties.json "
              f"(법정동코드 확보 {with_lawd}/{len(props)}, 시세조회 가능)")

    # 물건 상세(등기·임차·사진·회차별 기일) — 무거우므로 상위 N건만(opt-in)
    n_detail = 0
    for i, a in enumerate(sys.argv):
        if a == "--details" and i + 1 < len(sys.argv):
            try:
                n_detail = int(sys.argv[i + 1])
            except ValueError:
                n_detail = 30
    if n_detail and props:
        opener = make_opener()
        spec_cache = _load_cfg("spec-cache.json", {})
        done = 0
        for p in props[:n_detail]:
            court, case, seq = p.get("bo_cd"), p.get("case_no"), p.get("dspsl_gds_seq", 1)
            if not (court and case):
                continue
            d = fetch_detail(opener, court, case, p.get("maemul_ser", 1))
            if d:
                if d.get("photos"):
                    p["photos"] = d["photos"]
                if d.get("schedule"):
                    p["schedule"] = d["schedule"]
                if d.get("base_date"):
                    p["base_date"] = d["base_date"]
                if d.get("demand_end"):
                    p["demand_end"] = d["demand_end"]
                if d.get("detail_note"):
                    p["note"] = ((p.get("note") or "") + " " + d["detail_note"]).strip()[:400]
                done += 1
            time.sleep(0.3)
        save(props)
        print(f"[detail] 상세 보강 {done}/{min(n_detail, len(props))}건 (사진·회차·권리텍스트)")
    elif not props and os.path.exists(OUT):
        print("[crawl] 수집 0건 — 기존 properties.json 유지", file=sys.stderr)
    else:
        props = sample_properties()
        save(props)
        print(f"[crawl] 수집 0건 — 최초 실행이라 샘플 {len(props)}건으로 시작", file=sys.stderr)

    # 과거 매각결과(실적) 수집
    if "--active-only" not in sys.argv:
        try:
            past = crawl_past(cfg)
        except Exception as e:  # noqa: BLE001
            print(f"[past] 수집 오류: {type(e).__name__}", file=sys.stderr)
            past = []
        if past:
            with open(PAST_OUT, "w", encoding="utf-8") as fp:
                json.dump(past, fp, ensure_ascii=False, indent=2)
            print(f"[past] {len(past)}건 → past-results.json")
        elif os.path.exists(PAST_OUT):
            print("[past] 0건 — 기존 past-results.json 유지", file=sys.stderr)


if __name__ == "__main__":
    main()
