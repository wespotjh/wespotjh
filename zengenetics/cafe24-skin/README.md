# cafe24 스킨 원본 보존

대표님 쇼핑몰(`wespotjo.cafe24.com`)의 **실제 스킨 템플릿**을 여기에 보존한다.
`site/` 가 우리 프로토타입이라면, 여기는 **실제로 돌아가는 화면의 설계도**다.

| 항목 | 값 |
|---|---|
| 라이브 대표디자인 | **바디랩 반응형** (모아스튜디오 제작, 유료) |
| 작업용 사본 | **젠제네틱스 v2 작업본** (2026-09-06 대표님이 복사 생성) — `skin_no=16`, `skin_code=skin10` |
| 편집기 | 관리자 → 디자인(PC/모바일) → 디자인 보관함 → 해당 디자인 `디자인 편집` |

> **라이브(바디랩 반응형)는 절대 직접 편집하지 않는다.** 작업은 사본에서만, 확인은 `미리보기`로.

## 확보한 파일 (2026-09-06)

| 파일 | 내용 | 보존 상태 |
|---|---|---|
| `product/detail.html` | 상품 상세 | 축약 2곳 (아래) |
| `order/basket.html` | 장바구니 | 반복 블록 축약 (아래) |
| `ds/html/price.html` | 가격·혜택 표시 블록 | **전문** |
| `moa/import/product_detail/review.html` | 리뷰 탭 | 반복 rv__item 1개 축약 |
| `layout/basic/layout.html` | 전체 레이아웃 셸 | **전문** |

> ⚠️ **이 폴더는 "작업용 참조본"이지 완전한 백업이 아니다.**
> cafe24 모듈은 같은 마크업을 여러 번 반복해 표본을 보여주는 구조라, 반복분을 축약해 보존했다.
> **진짜 백업은 스킨 전체 다운로드(zip)** 이며 아직 확보하지 못했다.

축약한 곳:
- `product/detail.html` — `module="product_setproduct"` 세트상품 블록 내부, 카카오 공유 키 값
- `order/basket.html` — 상품 행 블록을 **캐논니컬 1개만** 남기고, 이를 재사용하는 7개 영역
  (`Order_NormNormal` `Order_SuppNormal` `Order_NormOversea` `Order_NormIndividual`
  `Order_InstNormal` `Order_InstIndividual` `Order_InstOversea`)은 주석으로 명시.
  할인 항목 10종, 해외배송 합계 블록도 주석으로 명시
- `moa/import/product_detail/review.html` — 반복되는 `rv__item` 2개 중 1개

## 아직 필요한 파일

| 파일 | 왜 필요한가 |
|---|---|
| **스킨 전체 zip** | 진짜 백업. 되돌릴 안전판 |
| `/ds/js/price-config.js` | **가격·할인율을 실제로 그리는 로직.** price.html 은 빈 껍데기고 이 JS 가 채운다 |
| `/ds/js/detail.js` | 상세 동작 |
| `/ds/css/price.css` | 가격 영역 스타일 — 우리 디자인을 입힐 1순위 지점 |
| `/moa/js/lib/calc_sale_rate.js` | 할인율 계산 |
| `/moa/import/product_detail/detail.html` | 상세정보 탭 — 우리 상세 이미지가 들어갈 자리 |
| `/moa/import/product/detail_tab.html` | 탭 메뉴 |
| `/moa/layout/header.html` `footer.html` `aside.html` | 헤더·푸터·사이드 |
| `/moa/import/banner_manager.html` | **팝업·배너 관리 (대표님이 말씀하신 팝업)** |
| `/moa/import/top_banner.html` | 상단 띠배너 (현재 "🍊 OLIVE YOUNG 1등!") |

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

## 추가 해독 (2026-09-06, price / basket / review / layout)

### 가격은 JS가 그린다 — 우리 디자인의 1순위 작업 지점
`/ds/html/price.html` 은 **빈 껍데기**다:
```html
<div class="ds_benefit" style="display:none;">
  <div class="ds_benefit_max"></div>
  <div class="ds_benefit_list" id="benefitList"><!-- 가격 항목이 JS로 자동 추가됨 --></div>
</div>
```
즉 **가격·할인율 화면은 `/ds/js/price-config.js` + `/ds/js/detail.js` 가 `#benefitList` 에 그린다.**
`.infoArea` 의 `data-price` `data-custom` `data-coupon` 이 그 입력값이다.
→ 우리 상품페이지의 가격 영역 디자인은 **`/ds/css/price.css` 를 갈아입히는 것**으로 대부분 해결된다.
   HTML 을 새로 짜면 이 JS 가 못 찾는다.

### 장바구니 구조
- 좌: `.cart-product` (상품 목록) / 우: `.cart-total > .sticky` (합계, 스티키)
- 상품 행 하나 = `.ec-base-prdInfo.gCheck > .prdBox` — 체크박스 · 썸네일 · 설명 · 수량 · 버튼
- 수량 변경은 `{$add_shortcut}` `{$out_shortcut}` + `{$action_modify}`("변경" 버튼)
- 주문 이동: `{$action_order_all}` / `{$action_order_select}` →
  `link-order="/order/orderform.html{$param}"`, `link-login="/member/login.html"`
  **비로그인이면 로그인으로 보내는 분기가 이 속성에 들어 있다.**
- 하단 고정 바(`#orderFixArea`)가 모바일용으로 따로 있다
- 옵션변경 레이어 `#ec-basketOptionModifyLayer` 는 jQuery 로 열고 닫는다 (`$('#…').hide()`)
- 배송비 할인 툴팁, 무이자할부 안내, 국내/해외 탭이 모두 모듈로 붙어 있다

### 리뷰 = 알파리뷰가 완전히 대체
```html
<div id="alph_new_board"><div class="alpha_widget" data-code="a070d8ba" data-value="{$product_no}"></div></div>
<div id="alph_origin_board" style="display:none">  ← cafe24 원래 리뷰 UI 전체가 여기 숨겨져 있다
```
- 즉 **화면에 보이는 리뷰는 전부 알파리뷰**이고, cafe24 기본 리뷰 마크업은 `display:none` 으로 남겨만 뒀다
- 알파리뷰 위젯 코드: 상세 썸네일 하단 `8d644bd9`, 리뷰 탭 `a070d8ba`
- 포토리뷰 전체보기: `/board/review/list_photo.html?board_no=4` (**리뷰 게시판 board_no = 4**)
- 별점 아이콘: `/moa/img/default/icon-star-rating{$point_count}.svg`

### 레이아웃 셸
```
head → top_banner → header → aside → banner_manager → quick_menu
     → #wrap > #container > main#contents > {페이지 내용}
     → footer → cafe24PRO 로케일 팝업 스크립트
```
- **팝업/배너는 `/moa/import/banner_manager.html` 과 `top_banner.html` 이 담당** — 대표님이 말씀하신 팝업이 여기다
- 페이지 본문은 `<!--@contents-->` 자리에만 들어간다.
  **우리 페이지는 이 자리에 들어가는 조각이지, 통째 문서가 아니다.**
