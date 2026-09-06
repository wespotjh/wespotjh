# GA4 추적 계획 — 젠제네틱스 (v2.001)

측정 ID `G-GZHFY596SS` · 속성 `젠제네틱스_속성 (498152534)`
구현 파일 **`cafe24-skin/ds/js/ga4.js`** · 로드 위치 `moa/layout/head.html` (전 페이지 1줄)
작성 2026-09-06 · **아직 라이브 아님 (작업본)**

---

## 0. 왜 이걸 심는가

개편 전에는 전자상거래 이벤트가 **0건**이었다 (`page_view`만 있었다).
그래서 431건이라는 주문 수도, 84,508원이라는 객단가도 확인할 방법이 없었다.

이번 개편부터는 **모든 이벤트에 `zg_ver` 를 붙인다.**
개편 단계(2.001 → 2.002 → …)마다 이 값만 올리면 GA4에서 단계별로 나눠 볼 수 있다.

```js
var ZG_VER = '2.001';   // ds/js/ga4.js 최상단 — 개편할 때 이 줄만 고친다
```

---

## 1. 이벤트 표

| 이벤트 | 언제 | 파라미터 | 검증 |
|---|---|---|---|
| `view_item` | 상세페이지 진입 | value, items[item_id·item_name·price] | ✅ 라이브 DOM으로 검증 |
| `zg_option_select` | 옵션 select 변경 | item_id, item_variant | ✅ 검증 |
| `zg_option_layer_open` | 하단 구매바 → 옵션 레이어 열림 | item_id | ✅ 검증 |
| `add_to_cart` | 장바구니 담기 | value, value_source, items[+item_variant] | ✅ 검증 |
| `zg_buy_click` | **바로구매** 클릭 | 위와 동일 + checkout_route | ✅ 검증 |
| `zg_scroll_depth` | 상세/홈 스크롤 10·25·50·75·90·100% | percent, seconds, page_kind, item_id | ✅ 검증 |
| `view_cart` | 장바구니 페이지 | value, items[] | ⚠️ **미검증** |
| `begin_checkout` | 주문서 페이지 도달 | value, checkout_route | ⚠️ **미검증** |
| `purchase` | 주문완료 페이지 | transaction_id, value | ❌ **템플릿 필요** |
| `login` | 카카오 로그인 버튼 클릭 | method='kakao' | ⚠️ 미검증 |
| `zg_login_view` | 로그인 계열 페이지 진입 | login_page | ⚠️ 미검증 |

**진단용 이벤트** — 이게 GA4에 뜨면 선택자가 틀렸다는 뜻이다. 뜨는 즉시 고친다.

| 이벤트 | 의미 |
|---|---|
| `zg_cart_unreadable` | 장바구니 행을 못 읽었다 |
| `zg_purchase_unreadable` | 주문번호나 결제금액을 못 읽었다 |

---

## 2. 설계 규칙 (지킨 것)

1. **템플릿을 안 고쳤다.** `head.html`에 `<!--@js(/ds/js/ga4.js)-->` **한 줄**이 전부다.
   되돌리려면 그 줄만 빼면 된다.
2. **값을 못 읽으면 안 쏜다.** 틀린 매출을 GA4에 넣느니 비워 두고, 대신 진단 이벤트를 남긴다.
3. **가격·할인율을 코드에 안 썼다.** 전부 화면에 그려진 값에서 읽는다 (`가격_백엔드구조.md`).
4. **개인정보를 안 담는다.** 이름·전화·주소·이메일은 어떤 파라미터에도 없다.
5. `value` 에 `value_source` 를 같이 보낸다 — `screen_total`(옵션 추가금 반영된 진짜 합계) /
   `base_price`(합계를 못 읽어 기본가로 대체). GA4에서 이 비율을 보면 신뢰도를 알 수 있다.

---

## 3. 라이브에서 확인한 사실 (테스트 중 발견)

**장바구니와 구매하기가 같은 함수를 쓴다.** 처음에 `basket` 문자열로 구분하려다 잡았다.

```html
<!-- 장바구니 -->  onclick="product_submit(2, '/exec/front/order/basket/', this)"
<!-- 구매하기 -->  onclick="product_submit(1, '/exec/front/order/basket/', this)"
```

둘 다 URL 에 `basket` 이 들어간다. **구분은 첫 번째 인자(1=바로구매 / 2=장바구니)** 다.
그대로 뒀으면 바로구매가 전부 `add_to_cart` 로 잡혀서 퍼널이 통째로 틀어질 뻔했다.

**"수량"은 수량 입력칸이 아니라 옵션이다.**
`<option>🔥BEST🔥[지금 24%▼] … 2 box (무료배송) (+33,100원)</option>`
그래서 몇 박스가 팔리는지는 `item_variant` 로 잡는다. 앞의 `[할인율]`·이모지, 뒤의 `(+가격)`은 떼고 보낸다.

---

## 4. 아직 막힌 것

**`purchase` 하나다.** 주문완료 템플릿(`order/order_result.html`)이 작업본에 없다
(받은 스킨은 `detail.html` / `basket.html` / `login.html` 셋뿐).
지금 코드의 선택자는 카페24 기본 스킨 기준 **추정**이라,
값을 못 읽으면 `purchase` 대신 `zg_purchase_unreadable` 을 쏘게 해 뒀다.
템플릿을 받으면 그 블록만 정확히 다시 잡으면 된다 — 10분이면 된다.

---

## 5. 중복 집계 주의

`head.html:2-10`에 gtag 스니펫이 직접 박혀 있다.
나중에 **카페24 관리자의 GA4 연동 기능을 켜면 태그가 두 벌 돌아 전부 2배로 잡힌다.**
켤 거면 그 스니펫을 먼저 빼야 한다. 지금은 스니펫 쪽만 쓰는 전제로 만들었다.

---

## 6. GA4 관리자에서 해야 할 설정

1. **맞춤 측정기준(이벤트 범위) 등록** — 이걸 안 하면 보고서에서 못 쓴다
   `zg_ver` · `value_source` · `item_variant` · `checkout_route` · `page_kind` · `percent`
2. **전환 표시**: `purchase`, `add_to_cart`, `begin_checkout`
3. **DebugView 로 검수**: 실제 폰에서 상품 → 옵션 → 담기 → 주문 → 완료까지 한 번 태우고
   위 표대로 이벤트가 순서대로 뜨는지 눈으로 확인한다. 이걸 안 하고 넘어가면 안 된다.

---

## 7. 개편 단계별로 볼 표 (2.001 기준선)

`zg_ver` 로 나눠서 이 다섯 줄만 보면 된다.

| 지표 | 계산 | 2.001 기준선 |
|---|---|---|
| 상세 도달 → 옵션 선택 | `zg_option_select` / `view_item` | (측정 시작) |
| 옵션 선택 → 담기·구매 | (`add_to_cart`+`zg_buy_click`) / `zg_option_select` | (측정 시작) |
| 구매의도 → 주문서 | `begin_checkout` / (`add_to_cart`+`zg_buy_click`) | (측정 시작) |
| 주문서 → 결제완료 | `purchase` / `begin_checkout` | 페이지경로 기준 52.4% |
| 전체 전환율 | `purchase` / 세션 | 페이지경로 기준 0.74% |

여기에 `zg_scroll_depth` 를 겹쳐 보면 **긴 상세페이지 어느 지점에서 나가는지**가 나온다.
그 지점이 다음 개편(2.002)에서 손볼 곳이다.
