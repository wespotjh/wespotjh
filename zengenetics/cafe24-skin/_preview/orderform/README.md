# 주문서(order/orderform.html) — 구조 참고본

대표님이 2026-09-06 전달한 원문에서 **구조만 남긴 것**.
맨 아래 대표님이 운영 중인 인라인 `<script>`/`<style>`(퀵계좌이체 뱃지·포기방지 레이어)는
**일부러 뺐다** — 원문 그대로 보존해야 하는 코드라 여기 복사본을 두면 위험하다.

> ⚠️ **이 파일을 라이브 스킨에 올리면 안 된다.** 결제수단 유도 로직이 통째로 사라진다.
> 수정은 **전체 교체가 아니라 head 에 2줄 삽입**으로만 한다.

## 확인된 사실

- 이 페이지는 **`<!--@layout()-->` 을 안 쓴다.** 자기 `<head>` 를 직접 가진 독립 페이지다.
  → `moa/layout/head.html` 을 안 거치므로 **우리 GA4(`G-GZHFY596SS`)가 실리지 않는다.**
  라이브 실측: `/order/orderform.html` 에 `/moa/` **0회**, `G-GZHFY596SS` **0회**
  (같은 시각 홈·장바구니는 `/moa/` 100회 이상, `G-GZHFY596SS` 2회)
- `order/order_result.html` 도 같은 구조다. 둘 다 손봐야 한다.
- SEO 코드직접입력이 넣는 `G-84HNK1MRBG`·`GTM-5W5PV3CD` 는 여기에도 실린다(쇼핑몰 전체 설정이라).
  → 그래서 **남의 속성에는 잡히는데 우리 속성에만 안 잡히는** 상태였다.

## begin_checkout 이 읽어야 할 값 (원문에서 확인)

```html
<button type="button" class="btnSubmit" id="{$btn_payment_id}">
  {$total_order_price_front_head}<span id="{$total_order_price_front_id}">{$total_order_price_front}</span>{$total_order_price_front_tail}
  <span class="...">결제하기</span>
</button>
```

`{$total_order_price_front_id}` 가 붙은 `<span>` 이 **결제예정금액의 정본**이다.
QA(배시우) R4 가 지적한 대로 `#totalOrderPrice`·`.totalPrice` 는 이 페이지에 없거나
다른 것(배송비 블록)을 가리킨다.

결제수단 라디오는 `input[name="addr_paymethod"]` → `add_payment_info` 훅으로 쓸 수 있다.

## 건드리면 안 되는 것

- 맨 아래 인라인 `<script>` 전부 (퀵계좌이체 뱃지, 포기방지 레이어, `fillAccountHolderName`,
  `checkQuickTransfer`, `toggleOffRecentPayMethod`) — 대표님이 운영 중인 결제 전환 로직이다
- `#progressPaybar` 블록 (PG 결제 진행 표시)
- `<!--@import(...)-->` 12개, `module="Order_form"`, `$move_order_after`/`$move_basket` 주석
- `{$btn_payment_id}`, `{$payment_proc_id}`, `{$sPrdName}`
