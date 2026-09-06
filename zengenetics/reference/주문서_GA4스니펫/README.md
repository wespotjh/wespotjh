# 주문서·주문완료 GA4 스니펫 — QA 검증 완료본

**넣을 곳**: 카페24 관리자 › 디자인 › 디자인 관리 › **스마트 주문서(주문서 디자인)**
- `order/orderform.html` 의 `</head>` **바로 위**
- `order/order_result.html` 의 `</head>` **바로 위**
- **두 파일에 넣는 코드는 완전히 같다** (`붙여넣기_3줄.txt`)

⚠️ **전체 파일 교체가 아니다. 3줄 삽입뿐이다.**
주문서 하단에는 대표님이 운영 중인 퀵계좌이체 뱃지·포기방지 레이어 인라인 스크립트가 있어,
전체 교체하면 그것이 유실된다.

## 왜 필요한가

이 두 페이지는 `<!--@layout()-->` 을 안 쓰는 독립 페이지라 `moa/layout/head.html` 을 안 거친다.
라이브 실측: `/order/orderform.html` 에 `/moa/` **0회**, `G-GZHFY596SS` **0회**.
→ `begin_checkout` 과 `purchase` 가 실행될 자리에 로더가 없었다.

## QA(배시우)가 A/B 대조 실험으로 확인한 것

라이브 원문에 실제로 삽입해 넣기 전/후를 비교했다.

| 확인 | 결과 |
|---|---|
| 기존 `G-84HNK1MRBG` 집계가 끊기는가 | 안 끊긴다. `dataLayer` 에 두 측정 ID가 **함께** 들어간다 |
| GTM(`GTM-5W5PV3CD`) | 그대로 |
| 결제 버튼 | 정상 — HTML·활성상태·클릭 도달 전부 동일 |
| 퀵계좌이체 뱃지·포기방지 레이어 | 동일 (`checkQuickTransfer`·`fillAccountHolderName`·`toggleOffRecentPayMethod`·`createCancelLayer`) |
| PG 진행 표시 `#progressPaybar` | 동일 (존재·`display:none`) |
| 예외가 나면 결제가 막히는가 | 안 막힌다. `try{...}catch(e){}` 가 삼킨다 — 강제 예외 3종 대조(있음 0건 / 없음 3건) |
| `gtag/js` 로더를 또 넣는가 | 안 넣는다 (이미 페이지에 있다. 두 번 넣으면 방문수가 중복된다) |

## GTM 경유는 권하지 않는다

`GTM-5W5PV3CD` 소유자가 확인되지 않았고, 그 안에 `G-GZHFY596SS` 태그가 이미 있으면
**그때부터 2배로 집계**된다.

## 넣은 뒤 확인 (2분)

1. `/order/orderform.html` 소스 보기(Ctrl+U) → `G-GZHFY596SS` 검색 → 나오면 성공
2. F12 → Network → `ga4.js` → **상태 200**
   (지금 라이브는 moa 스킨이라 **404 가 정상**이다. v2 작업본 적용 후 200이면 된다.
    404여도 **첫 줄은 이미 동작**하므로 GA4 연결 자체는 살아 있다)
