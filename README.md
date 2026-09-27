# 경매 분석 자동화 시스템

부동산 경매 물건을 **매일 자동 수집·분석**해 물건마다 **적정 입찰가 · 낙찰 성공률 · 예상 순이익 · 종합 점수**를 산정하고, 과거 낙찰 데이터로 **실제(추정) 수익률**과 **내 예측 백테스트**를 계산하며, 결과를 **반응형 웹 대시보드**와 **네이버 블로그 콘텐츠**로 자동 생성하는 시스템입니다.

- 파이썬 **표준 라이브러리만** 사용, GitHub Actions에서 무료로 매일 실행
- 대규모 수집(현재 1만+·과거 수만 건)을 고려한 **캐싱·페이지네이션·경량화** 설계
- 데이터 출처: **법원경매정보** · **국토부 실거래가/공동주택 단지정보** · **네이버 이미지검색**

---

## 1. 파이프라인 (매일 06:00 KST · GitHub Actions)

```
crawl.py   법원경매 크롤 → properties.json(진행) · past-results.json(과거 낙찰)
   ↓
analyze.py 시세·적정입찰가·성공률·순이익·점수·특수물건·시장통계 → analysis.json
                                          예측 백테스트·패인분석 → backtest.json(비공개)
   ↓
track.py   예측 스냅샷·실제결과 대조 → predictions/outcomes/calibration.json
   ↓
content.py 종합점수 top10 → 네이버 블로그 HTML(사진·태그·블라인드)
   ↓
결과 커밋 → Cloudflare/GitHub Pages 배포
```

---

## 2. 폴더 구조

```
auction/
├─ index.html                     웹 대시보드(구조만)
├─ assets/
│  ├─ app.css                     스타일(반응형·다크토큰 등)
│  └─ app.js                      로직(필터·페이지네이션·차트·미리보기 데이터)
├─ scripts/
│  ├─ crawl.py                    진행물건 + 과거 매각결과 수집
│  ├─ analyze.py                  분석·점수·수익률·특수물건·통계·백테스트
│  ├─ track.py                    예측→실제 대조(자기학습)
│  └─ content.py                  블로그 콘텐츠 생성(사진·태그)
├─ data/
│  ├─ 설정: crawl-config.json · baselines.json · assumptions.json
│  ├─ 사전(외부화): lawd-codes.json · text-rules.json · blog-config.json · priority-tenant.json
│  ├─ 시드/폴백: auction-history.json · properties.sample.json
│  ├─ (생성) properties · past-results · analysis · backtest · published.json
│  ├─ (생성) predictions · outcomes · calibration.json
│  └─ (캐시) molit-cache · apt-list-cache · apt-info-cache · photo-cache · spec-cache.json
├─ content/<날짜>/*.html          (생성) 블로그 글
└─ .github/workflows/analyze.yml  자동화 워크플로우
```

**설정·사전 외부화** — 코드 수정 없이 JSON만 편집해 조정합니다.
- `crawl-config.json` 수집 조건 · `assumptions.json` 세금·비용·점수 가중치·이론 파라미터 · `baselines.json` 지역·유형별 낙찰가율 기준선
- `lawd-codes.json` 시군구→법정동코드 · `text-rules.json` 특수물건·인수권리 키워드·브랜드·단지명 접미사 · `blog-config.json` 블로그명·닉네임·문구 · `priority-tenant.json` 소액임차인 최우선변제 기준
- 파일이 없어도 각 스크립트는 안전한 폴백으로 동작합니다.

---

## 3. 스크립트

- **crawl.py** — 진행물건·과거 매각결과를 세션 재사용·병렬·재시도로 수집. 주소→법정동코드(검색응답 `srchHjguSiguCd` 직접). `--details N`: 상위 N건에 **물건 상세**(실제 사진·회차별 기일·말소기준일·조회수)와 **매각물건명세서**(courtauction→ecfs→StreamDocs 텍스트레이어 파싱 → 임차인 보증금·전입·확정·배당요구)를 보강해 **예상 배당표** 입력을 자동 생성. 옵션 `--sample`·`--active-only`·`--details N`
- **analyze.py** — 시세(국토부 실거래, 월 단위 캐시)·적정입찰가·성공률·순이익·종합점수·특수물건·시장통계·과거 백테스트 산출. 점수 상위 `photo_top_n`건은 courtauction 상세에서 **실물건 사진 전량** 수집(캐시). 단지정보(세대수·시공사·주차·난방)·사진용 필드 포함
- **track.py** — 예측 스냅샷을 실제 결과와 대조해 오차·보정 제안 축적(추후 튜닝)
- **content.py** — 종합점수 top을 네이버 블로그 리치 HTML로 생성(사진 자동수집·태그 고도화·핵심 금액 블라인드+댓글 유도). 페르소나는 `blog-config.json`

---

## 4. 방법론 (검증된 경매·투자 이론)

| 항목 | 이론 | 계산 |
|---|---|---|
| 적정 입찰가 ① | 승자의 저주(공통가치 경매) | `보정가치 = 시세 × (1 − 변동계수 × 응찰자수 보정)` |
| 가치평가(유형별) | 아파트=실거래 시세, 오피스텔=min(시세,수익환산), 상가=Cap Rate 환산 | 수익환산 = 연월세÷목표수익률+보증금 |
| 적정 입찰가 ② | 1차가격 봉인입찰(Vickrey·Milgrom–Weber) | 낙찰가율 분포로 낙찰확률 → 낙찰확률 × 보정순이익 최대가(보수·권장·공격) |
| 낙찰 성공률 | 낙찰가율 경험분포 + 정규분포 혼합 | 실측 표본↑ → 경험적 CDF 가중↑ + 경쟁도 반영 |
| 순이익·ROI | — | 보정 매도가 − 낙찰가 − 부대비용(취득·양도세·명도·수리·보유·중개·인수권리) |
| 점수: 안전마진 | Margin of Safety(Graham) | 보정가치 대비 입찰가 쿠션 |
| 점수: 위험조정 | Sharpe 개념 | 수익률 ÷ 시세 변동위험 |
| 자금배분 | Kelly(하프켈리) | `f* = 0.5 × μ/σ²` |
| 예상 배당표 | 배당순위(경매비용→소액임차 최우선변제→날짜순 우선변제) | 선순위 대항력 임차인 미배당분 = 낙찰자 인수액 |

**종합점수** = 가중합(환금성 35 / 안전마진 20 / 위험조정 20 / 권리 15 / 낙찰가능 10) × 환금성 게이트, 순손실 20점 상한.

---

## 5. 성능·캐싱

- **CPU** — 입찰가 탐색을 고정비용 사전계산(`cost_ctx`)+고속 경로(`_pf`)로 최적화, 반복 축소. 약 **7,000건/초**(13,000건 ≈ 2초)
- **네트워크(캐시, 저장소 커밋으로 유지)**
  - 실거래가: **월 단위** — 지난 달 캐시 재사용, 이번 달만 재조회
  - 단지 목록(30일 TTL)·단지 정보·사진: **영구 캐시**(신규만 조회)
  - 매각물건명세서(임차·권리): **영구 캐시**(`spec-cache.json`, ecdocId 키)
  - 물건 실사진(courtauction 상세, base64): **영구 캐시**(`photo-detail-cache.json`)
- **경량화** — `analysis.json` 컴팩트 직렬화, 성공률 곡선 11점, 과거 케이스 상한
- **프론트** — 40건씩 페이지네이션(수만 건도 가벼움), 상세 곡선은 펼칠 때만 렌더

---

## 6. 웹 대시보드

**반응형**: 모바일 1단 / 태블릿·PC(≥880px) 2단 / 와이드 PC(≥1280px) 3단.

- **현재 매물** — 검색 + 필터(지역·유형·판정·특수물건) + **테마경매**(반값·유찰多·고수익·소액·특수·수도권) + 정렬(점수·수익률·성공률·매각임박) + KPI + 페이지네이션. 카드 상세: **실물건 사진(courtauction 상세)**·3전략가·수익계산(미납관리비 포함)·**예상 배당표(인수/소멸)**·**꼭 확인 인수·리스크 체크리스트**·입찰보증금·**대출 레버리지 수익률**·지도(카카오/네이버)·점수구성·Kelly·성공률 곡선. **관심(★, localStorage)**
- **과거 실적** — 검색·필터·정렬·페이지네이션 + 시장 통계(매각가율·경쟁률) + 내 예측 vs 실제 낙찰(적중/미달) + 지역별 낙찰가율
- **산정 방법** — 각 지표 정의·공식·가중치
- **가이드** — 경매 절차·입찰 방법·용어 사전

데이터가 없을 때도 `app.js` 내장 샘플로 미리보기가 렌더됩니다.

---

## 7. 설치 & 배포

1. **API 키(GitHub Secrets)** — `MOLIT_SERVICE_KEY`(국토부 실거래가·공동주택정보) · `NAVER_CLIENT_ID`/`NAVER_CLIENT_SECRET`(사진). 없어도 해당 기능만 생략하고 동작
2. **자동화** — `.github/workflows/analyze.yml`을 기본 브랜치(main/master)에. Settings→Actions→Workflow permissions **Read and write**
3. **배포** — GitHub Pages 또는 Cloudflare Pages(빌드 없음). `index.html` + `assets/`가 함께 배포돼야 함
4. **로컬** — `python scripts/crawl.py --sample && python scripts/analyze.py && python scripts/content.py` 후 `python -m http.server 8000`

---

## 8. 주의
시세·세율·부대비용·확률·수익률·권리·특수물건은 **공개 데이터 기반 자동 추정**이며 투자 자문이 아닙니다. 과거 실적 매도가는 낙찰 후 시세 기준 추정입니다. **예상 배당표·정밀 권리분석(등기부)** 은 유료 데이터가 필요해 제외돼 있습니다. 입찰 전 매각물건명세서·현황조사서·감정평가서를 반드시 직접 확인하세요.
