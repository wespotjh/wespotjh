# cafe24 스킨 원본 보존

대표님 쇼핑몰(`wespotjo.cafe24.com`)의 **실제 스킨 템플릿**을 여기에 보존한다.
`site/` 가 우리 프로토타입이라면, 여기는 **실제로 돌아가는 화면의 설계도**다.

| 항목 | 값 |
|---|---|
| 라이브 대표디자인 | **바디랩 반응형** (모아스튜디오 제작, 유료) |
| 작업용 사본 | **젠제네틱스 v2 작업본** (2026-09-06 대표님이 복사 생성) — `skin_no=16`, `skin_code=skin10` |
| 편집기 | 관리자 → 디자인(PC/모바일) → 디자인 보관함 → 해당 디자인 `디자인 편집` |

> **라이브(바디랩 반응형)는 절대 직접 편집하지 않는다.** 작업은 사본에서만, 확인은 `미리보기`로.

## 확보한 파일

| 파일 | 내용 |
|---|---|
| `product/detail.html` | 상품 상세 (2026-09-06 확보) |

⚠️ `product/detail.html` 보존본에서 **두 곳을 축약**했다. 원본 전체가 필요하면 편집기에서 다시 받는다.
- `module="product_setproduct"` 세트상품 블록 내부 (구조가 추가구성상품과 동일한 반복 마크업)
- 카카오 공유 키 값 (자격증명이라 저장소에 남기지 않음 — 스킨 원본에 그대로 있음)

## 아직 필요한 파일 (우선순위 순)

| 파일 | 왜 필요한가 |
|---|---|
| `/ds/html/price.html` | **가격·할인율이 그려지는 실제 블록.** detail.html 은 이걸 import 만 한다 |
| `/ds/js/price-config.js` | 가격 표시 설정값 |
| `/moa/js/lib/calc_sale_rate.js` | 할인율 계산 로직 |
| `/order/basket.html` | 장바구니 (4번 과업 본체) |
| `/moa/import/product_detail/detail.html` | 상세정보 탭 — 우리 상세 이미지가 들어갈 자리 |
| `/moa/import/product_detail/review.html` | 리뷰 탭 — 알파리뷰가 붙는 자리 |
| `/layout/basic/layout.html` | 전체 레이아웃 (헤더·푸터·팝업 훅) |

## 읽어낸 구조 (product/detail.html 기준)

### 상품 데이터가 들어오는 자리
| 화면 요소 | 변수 |
|---|---|
| 상품명 | `{$name}` (h1.prd-name) |
| 요약 설명 | `{$simple_desc}` |
| 가격 | `{$product_price}` — 표시는 `/ds/html/price.html` 이 담당 |
| 대표 이미지 | `{$big_img}` · 추가 이미지 `{$aAddImage}` `{$add_img}` |
| 상품번호 | `{$product_no}` |
| 옵션 select | `{$form.option}` (module `product_option`) |
| 수량 | `{$form.quantity}` (module `product_quantity`) |
| 추가구성상품 | module `product_addproduct` |
| 합계 | `{$total.total_id}` `{$total.total_price_id}` `{$total.total_cnt}` |
| 품절·아이콘 | `{$soldout_icon}` `{$stock_icon}` `{$new_icon}` `{$benefit_icons}` … |
| 배송비 | `{$delivery_price}` (`#freeShipGuide` 의 `data-delivery`) |

`.infoArea` 가 `data-name` `data-price` `data-custom` `data-coupon` `data-prd-no` 로
값을 JS 에 넘긴다 — 모아 스킨의 계산 로직이 여기를 읽는다. **이 속성들을 지우면 가격·할인 표시가 깨진다.**

### 장바구니·구매 (우리가 만들지 않는다)
```html
<button class="actionCart" onclick="{$action_basket}">장바구니</button>
<div class="btnSubmit" onclick="{$action_buy}">구매하기</div>
```
`module="product_action"` 안에서 cafe24 가 채워 넣는다.
**우리 디자인의 버튼도 이 `module` 과 `onclick` 을 그대로 달고 있어야 동작한다.**

### 플러그인 앱이 붙는 자리 (건드리면 안 됨)
| 앱 | 훅 |
|---|---|
| 알파리뷰 (썸네일 하단 포토) | `<div class="alpha_widget" data-code="8d644bd9" data-value="{$product_no}">` |
| 알파리뷰 (리뷰 수) | `<span class="alpha_review_count">` — 상단 요약 + 모바일 하단바 2곳 |
| 알파리뷰 (리뷰 탭) | `/moa/import/product_detail/review.html` + `/moa/js/lib/rv_lt.js` |
| 네이버페이 | `<div id="NaverChk_Button">` |
| 카카오페이 | `<div id="{$app_payment_button_box_id}">` |
| 카카오 공유 | `#kakaoKey` |
| 배너 (모아) | `df-banner-code="detail-benefit"`, `df-banner-code="detail-bubble"` |

> cafe24 기본 `{$review_count}` 는 **주석 처리**되어 있고 알파리뷰가 대신 채운다.
> 즉 리뷰 수·평점은 **알파리뷰가 진실원장**이다. 우리 프로토타입의 리뷰 수치는 여기서 대체된다.

### 모아스튜디오 자체 기능 (유지 대상)
- 오늘출발 카운트다운 — `.shipping-today`, `{$custom_option1}` `{$custom_option2}` 사용
- 무료배송 진행바 — `#freeShipGuide`
- 오늘 N명 구매 — `.prd-view` / `.jsViewCount`
- 베스트 리뷰 슬라이드 — `.best-rv`
- 모바일 옵션 레이어 — `.jsMobileLayer`, `.mobile-fix-footer`

## 이식 방침 (여기서 도출된 결론)

**detail.html 을 우리 페이지로 통째 교체하지 않는다.** 이 파일에는 알파리뷰·오늘출발·
무료배송바·탭·모바일 레이어가 촘촘히 엮여 있어, 통째 교체하면 대표님이 걱정하신
"충돌"이 정확히 여기서 난다.

대신 **① CSS 로 우리 디자인 입히기 ② 필요한 자리에만 마크업 추가**로 간다.
`module` 속성, `{$변수}`, `onclick="{$action_*}"`, 앱 훅 클래스·id 는 **한 글자도 지우지 않는다.**
