# 주문완료 페이지 — 계측 선택자 근거

`구조참고.html` 은 대표님이 2026-09-06 전달한 `order/order_result.html` 을
**구조만 남기고 줄인 것**이다. 반복 블록(개별배송·해외배송·두 번째 배송지·
샘플 상품 2벌)을 지웠다.

> ⚠️ **이 파일을 라이브 스킨에 올리면 안 된다.** 원문이 아니다.
> `ds/js/ga4.js` 의 purchase 선택자를 검증하기 위한 참고본이다.

## purchase 가 읽는 곳

| 값 | 위치 |
|---|---|
| `transaction_id` | `.resultInfo` 표에서 `<th>주문번호</th>` 행 → `{$order_id}` |
| `value` | 하단 `.totalPay` 중 `.heading` 이 정확히 **"결제금액"** 인 것의 `<strong>` |
| `shipping` | 결제정보 표의 `배송비` + `지역별 배송비` |
| `tax` | 결제정보 표의 `부가세` |
| `items[]` | `[module="Order_normalresultlist"]` · `Order_individualresultlist` · `Order_oversearesultlist` 아래 `.ec-base-prdInfo` |

## 걸렸던 것

1. **`.totalPay` 가 두 군데다.** 결제정보(결제금액)와 적립 혜택(적립 예정금액).
   `.heading` 텍스트가 "결제금액" 인 것만 골라야 한다. 안 그러면 매출 자리에 적립금이 들어간다.
2. **`.ec-base-prdInfo` 가 네 군데다.** 주문상품(3종) · 배송지정보(`Order_deliverybindinglist`) · 사은품(`Order_giftresultlist`).
   주문상품 3종만 잡아야 한다. 배송지 것까지 세면 상품이 두 배로 잡힌다.
3. **`.refer` 는 외화 병기다.** `12,000원 (USD 9.00)` 처럼 나오므로 숫자를 뽑기 전에 지운다.
4. **새로고침 중복.** 주문완료 페이지는 새로고침·뒤로가기로 다시 열린다.
   `localStorage` 에 주문번호를 남겨 두 번째부터는 `zg_purchase_repeat_view` 만 쏜다.
   지금 GA4 의 431건이 부풀려졌을 수 있는 이유 중 하나다.
