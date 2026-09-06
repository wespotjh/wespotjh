/* ============================================================================
 * ds/js/ga4.js — 젠제네틱스 GA4 계측 (전 페이지 공통)
 *
 * 원칙
 *  1. 템플릿을 고치지 않는다. 화면에 이미 그려진 DOM 에서만 읽는다.
 *  2. 값을 못 읽으면 이벤트를 쏘지 않는다. 틀린 숫자보다 없는 게 낫다.
 *  3. 가격·할인율을 코드에 쓰지 않는다 (가격_백엔드구조.md).
 *  4. 개인정보(이름·전화·주소·이메일)는 어떤 파라미터에도 담지 않는다.
 *  5. 모든 이벤트에 zg_ver·send_to 를 붙인다 → 개편 단계별 before/after 비교용.
 *
 * 로드 위치
 *  - 일반 페이지   : moa/layout/head.html 의 <!--@js(/ds/js/ga4.js)--> 한 줄
 *  - 주문서/주문완료 : 이 두 페이지는 <!--@layout()--> 을 안 쓰는 독립 페이지라
 *    moa/layout/head.html 을 거치지 않는다(라이브 실측: /moa/ 0회, G-GZHFY596SS 0회).
 *    → 관리자 '스마트 주문서' 디자인의 </head> 바로 앞에 스니펫으로 직접 넣는다.
 *      (team/보고/개발_수정보고_2026-09-06.md 참조)
 * ==========================================================================*/
(function () {
  'use strict';

  /* 개편할 때마다 이 숫자만 올린다. GA4 에서 이 값으로 버전을 나눠 본다. */
  var ZG_VER = '2.001';

  /* 우리 속성으로만 보낸다.
   * 라이브에는 SEO 고급설정 '코드 직접입력'이 넣은 두 번째 GA4(G-84HNK1MRBG)와
   * GTM(GTM-5W5PV3CD)이 같이 떠 있다. send_to 를 안 쓰면 gtag 는 페이지에 설정된
   * 모든 측정ID로 이벤트를 뿌린다 — 남의 속성까지 오염된다. */
  var ZG_ID = 'G-GZHFY596SS';

  /* head 에서 로드되므로 DOM 이 그려진 뒤에 실행한다 */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', waitForGtag);
  } else {
    waitForGtag();
  }

  /* R-1 대비: 주문서·주문완료에서는 이 파일이 head.html 이 아니라 관리자 스니펫으로
   * 로드된다. 삽입 순서가 어긋나 gtag 정의가 아직 없을 수 있으므로 잠깐만 기다린다.
   * 끝까지 없으면 아무것도 하지 않는다 — 에러 0건·이벤트 0건(기존 동작 유지). */
  var gtagTries = 0;
  function waitForGtag() {
    if (typeof window.gtag === 'function') { boot(); return; }
    if (gtagTries++ >= 20) return;                  /* 150ms × 20 = 3초 */
    setTimeout(waitForGtag, 150);
  }

  function boot() {

  /* R7 수정: gtag('set', {zg_ver:…}) 는 페이지에 설정된 **모든 측정 ID에 전역 적용**된다.
   * 라이브에는 G-84HNK1MRBG·GTM-5W5PV3CD 가 같이 떠 있어 우리 파라미터가
   * 남의 속성 이벤트에도 붙었다. zg_ver 는 sendAlways() 가 이벤트마다 개별로
   * 붙이고 있으므로(실측 전수 확인) 전역 set 은 삭제한다. */

  var path = location.pathname;
  var sent = {};                                    /* 중복 발사 방지 */

  function send(name, params) {
    if (sent[name]) return;
    sent[name] = 1;
    sendAlways(name, params);
  }
  function sendAlways(name, params) {
    params = params || {};
    params.zg_ver = ZG_VER;
    params.send_to = ZG_ID;
    gtag('event', name, params);
  }
  function n(v) {                                   /* "34,900원" → 34900 */
    if (v === null || v === undefined) return 0;
    var d = String(v).replace(/[^0-9]/g, '');
    return d ? parseInt(d, 10) : 0;
  }
  function txt(el) { return el ? (el.textContent || '').trim() : ''; }
  function norm(s) { return String(s || '').replace(/\s+/g, ' ').trim(); }

  /* 라이브 실측(2026-09-06): 카페24는 렌더할 때 module="Order_xxx" 를
   * class="xans-order-xxx" 로 바꿔 내보낸다. 라이브 /order/order_result.html 에는
   * module= 속성이 **0건**이고 xans-order-normalresultlist 등만 남는다.
   * (프리뷰 목 렌더에는 module= 이 그대로 있다) → 두 형태를 모두 잡는다. */
  function modSel(name) {
    return '[module="Order_' + name + '"], .xans-order-' + name.toLowerCase();
  }

  /* ------------------------------------------------------------------ *
   * 현재 상품 — 상세페이지 .infoArea 가 값을 전부 물고 있다
   *   product/detail.html:79
   *   data-name / data-price / data-custom / data-prd-no
   * ------------------------------------------------------------------ */
  function infoArea() { return document.querySelector('.infoArea'); }

  function currentItem() {
    var a = infoArea();
    if (!a) return null;
    var price = n(a.getAttribute('data-price'));
    var id    = a.getAttribute('data-prd-no') || '';
    var name  = a.getAttribute('data-name') || '';
    if (!id || !price) return null;                 /* 못 읽으면 안 쏜다 */
    return { item_id: String(id), item_name: name, price: price, currency: 'KRW' };
  }

  /* R6: currentItem() 이 null 이어도 상품번호는 대개 읽을 수 있다.
   * 상품 93 처럼 data-price="구매 상품이 아닙니다" 인 경우에도
   * 최소한 "어느 상품에서 침묵했는지"는 남긴다. */
  function currentPrdNo() {
    var a = infoArea();
    return a ? (a.getAttribute('data-prd-no') || '') : '';
  }

  /* 화면의 수량 입력값 (없으면 1)
   * 주의: 젠제네틱스는 "수량선택"이 옵션(1box/2box/3box/5box)이라
   *      이 입력값은 대개 0 이다. 실제 수량 개념은 옵션명에 있다. */
  function currentQty() {
    var q = document.querySelector('.infoArea input[name="quantity"], input#quantity, .quantity input');
    var v = q ? n(q.value) : 0;
    return v > 0 ? v : 1;
  }

  /* 선택된 옵션명 → item_variant
   * 라이브 옵션 실측(2026-09-06, 상품 11·16·63·64·71·98):
   *   11 "🔥BEST🔥[지금 24%▼] 젠제네틱스 붓기파우더 2 box (무료배송) (+33,100원)"
   *   16 "[지금 3+2▼] 젠제네틱스 마그네슘 5 box (무료배송) (+115,100원)"
   *   63 "붓기부스터 [6+3] (45%할인 | 9주 | 무료배송) (+126,000원)"
   *   64 "🔥BEST🔥 [3+3] (45%할인 | 60일 | 무료배송) (+91,100원)"
   *   71 "🔥BEST🔥[생애 첫 1+1] 젠제네틱스 붓기파우더 데이팩 2 box (+5,100원)"
   *   98 "칼+마+비 [3set] (45%할인 | 무료배송) (+128,500원)"
   *
   * R5 수정: 예전에는 대괄호를 통째로 지워서 [6+3]·[3+3]·[3set]·[생애 첫 1+1] 같은
   * **박스 수량**(추적계획 §3 의 핵심 지표)이 사라지고, 정작 저장하면 안 되는
   * "45%할인"(규칙 11)은 그대로 남았다 — 목적과 정확히 반대였다.
   * → 할인율이 든 토큰만 지우고 수량 표기는 살린다. */
  function cleanVariant(t) {
    return String(t || '')
      /* 대괄호: %가 들어 있으면(=할인율) 통째로 버리고, 아니면 알맹이를 살린다 */
      .replace(/\[([^\]]*)\]/g, function (_m, inner) {
        if (inner.indexOf('%') !== -1) return ' ';              /* [지금 24%▼] → 제거 */
        return ' ' + inner.replace(/지금|[▲▼◀▶]/g, '') + ' ';
                                                                /* [6+3]·[3set]·[생애 첫 1+1] → 살린다 */
      })
      .replace(/\(\+[^)]*\)/g, '')                              /* (+33,100원) 제거 */
      .replace(/\d+\s*%\s*할인\s*\|?/g, '')                      /* (45%할인 | …) 의 할인율 제거 */
      .replace(/\d+\s*%\s*[▲▼]?/g, '')                 /* 남은 맨 % 표기 제거 */
      .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, '')   /* 🔥 등 이모지 */
      .replace(/[▲▼◀▶]/g, '')                /* ▲▼◀▶ */
      .replace(/\s+/g, ' ')
      .replace(/\(\s*\|\s*/g, '(')                              /* "( | 9주" → "(9주" */
      .replace(/\(\s+/g, '(')
      .replace(/\s+\)/g, ')')
      .replace(/\(\s*\)/g, '')
      .replace(/\s+/g, ' ')
      .trim();
  }
  function currentVariant() {
    var sel = document.querySelector('select[name^="option"]:not([name^="addproduct"])');
    if (!sel || !sel.value || sel.value === '*' || sel.value === '**') return '';
    return cleanVariant((sel.options[sel.selectedIndex] || {}).text || '');
  }

  /* 화면에 그려진 합계. 옵션 추가금이 반영된 진짜 금액이다.
   *
   * R1 수정: 예전 선택자 '#totalPrice, .totalPrice' 는 요소 **전체 텍스트**를 긁었다.
   * 라이브 실측 DOM (prd_11.html):
   *   <div id="totalPrice" class="totalPrice">
   *     <strong class="title">총 구매 금액 <span class="qty displaynone">(QUANTITY)</span></strong>
   *     <span class="total"><strong><em>68,000원</em></strong> (1개)</span>
   *   </div>
   * → "총 구매 금액 (QUANTITY)68,000원 (1개)" 에서 숫자만 뽑으면 "68000"+"1" = 680001.
   *   매출이 10배로 나갔다.
   * 카페24 자기 스킨(moa/js/product/detail.js)이 관측하는 선택자와 동일하게 좁힌다
   *   — 그 파일의 문자열 테이블에 '#totalPrice .total strong' 이 그대로 들어 있다.
   * '.totalPrice'(클래스만)는 주문서에서 **배송비 블록** 이름으로 재사용되므로 뺀다(R4 동일 원인).
   * 못 읽으면 null → 호출부가 base_price 로 폴백하는 기존 동작 유지. */
  function screenTotal() {
    var el = document.querySelector('#totalPrice .total strong, #totalPrice .total em');
    var v = n(txt(el));
    return v > 0 ? v : null;
  }

  /* ================================================================== *
   * 1. 상품 상세 — view_item
   * ================================================================== */
  var item = currentItem();
  if (item) {
    send('view_item', {
      currency: 'KRW',
      value: item.price,
      items: [item]
    });
  } else if (infoArea()) {
    /* R6 수정: 상세페이지인데 값을 못 읽으면 예전에는 아무 신호 없이 침묵했다
     * (라이브 상품 93: data-price="구매 상품이 아닙니다" → view_item 0건, 진단도 0건).
     * 관리자에서 가격 표기를 바꾸거나 품절 처리하면 정상 상품도 소리 없이 빠진다.
     * 장바구니·주문완료처럼 진단 이벤트를 남긴다. */
    var ia = infoArea();
    send('zg_view_item_unreadable', {
      has_id: ia.getAttribute('data-prd-no') ? 1 : 0,
      has_price: n(ia.getAttribute('data-price')) > 0 ? 1 : 0,
      prd_no: currentPrdNo()
    });
  }

  /* ================================================================== *
   * 2. 장바구니 담기 / 바로구매 — add_to_cart, zg_buy_click
   *    버튼은 스킨 여러 곳에 중복돼 있다(상단·플로팅·레이어).
   *    선택자로 잡지 말고 document 위임 + onclick 문자열로 판별한다.
   * ================================================================== */
  document.addEventListener('click', function (e) {
    var el = e.target && e.target.closest ? e.target.closest('[onclick],a,button,div,span') : null;
    if (!el) return;

    /* 클릭 지점에서 위로 올라가며 onclick 을 가진 조상을 찾는다 */
    var hit = null, cur = el, depth = 0;
    while (cur && depth++ < 6) {
      var oc = cur.getAttribute && cur.getAttribute('onclick');
      if (oc) { hit = { el: cur, oc: oc }; break; }
      cur = cur.parentElement;
    }
    if (!hit) return;

    var it = currentItem();
    var qty = currentQty();

    /* 라이브 실측(2026-09-06, 상품11 캡처):
     *   장바구니  → product_submit(2, '/exec/front/order/basket/', this)
     *   구매하기  → product_submit(1, '/exec/front/order/basket/', this)
     * 둘 다 URL 에 'basket' 이 들어간다. 구분은 첫 번째 인자다.
     *   1 = 바로구매 / 2 = 장바구니
     * 숫자를 못 읽으면 버튼 글자로 판별한다. */
    var m = hit.oc.match(/product_submit\s*\(\s*(\d+)/);
    var mode = m ? m[1] : null;
    if (!mode && /basket/i.test(hit.oc)) {
      /* QA L2 대비: 상세페이지(.infoArea)가 아닌 곳 — 장바구니의 수량증가·전체상품주문
       * 버튼 등 — 에서는 이 문자열 폴백을 쓰지 않는다. 오발사 방지. */
      if (!infoArea()) return;
      mode = /장바구니|cart/i.test(txt(hit.el) + ' ' + (hit.el.className || '')) ? '2' : '1';
    }
    if (!mode) return;

    var variant = currentVariant();
    var total = screenTotal();
    var payload = {};
    if (it) {
      var val  = total !== null ? total : it.price * qty;
      /* R8 수정: GA4 전자상거래 보고서는 items[] 로 상품별 매출을 계산한다.
       * Σ(items.price × quantity) 와 value 가 어긋나면 이벤트 매출과 상품별 매출이
       * 서로 다른 숫자가 된다. 화면 총액을 읽었을 때는 단가를 총액에서 역산해
       * Σ(price×quantity) === value 를 보장한다.
       * (가격을 코드에 쓰는 게 아니다 — 화면에 그려진 값을 나눌 뿐이다) */
      var unit = qty > 0 ? Math.round((val / qty) * 100) / 100 : val;
      var v    = Math.round(unit * qty * 100) / 100;
      payload = {
        currency: 'KRW',
        value: v,
        value_source: total !== null ? 'screen_total' : 'base_price',
        items: [{
          item_id: it.item_id, item_name: it.item_name,
          item_variant: variant, price: unit, quantity: qty
        }]
      };
    }

    if (mode === '2') {
      sendAlways('add_to_cart', payload);
    } else if (mode === '1') {
      /* begin_checkout 은 주문서 페이지에서 한 번만 쏜다(중복 방지).
       * 여기서는 '바로구매를 눌렀다'는 의도만 남긴다. */
      payload.checkout_route = 'direct_buy';
      sendAlways('zg_buy_click', payload);
    }
  }, true);

  /* 옵션을 실제로 고른 순간 — 최대 이탈 구간(35,019 → 1,153)을 직접 재는 이벤트 */
  document.addEventListener('change', function (e) {
    var sel = e.target;
    if (!sel || sel.tagName !== 'SELECT') return;
    if (!/^option/.test(sel.name || '')) return;
    if (!sel.value || sel.value === '*' || sel.value === '**') return;
    var it2 = currentItem();
    sendAlways('zg_option_select', {
      item_id: it2 ? it2.item_id : currentPrdNo(),
      item_name: it2 ? it2.item_name : '',
      item_variant: currentVariant()
    });
  }, true);

  /* 옵션 레이어 열림 — 지금 최대 이탈 지점(상품조회 35,019 → 옵션선택 1,153) */
  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('.jsLayerBtn') : null;
    if (!t) return;
    var it3 = currentItem();
    /* R6 수정: 예전에는 currentItem() 이 null 이면 빈 페이로드 {} 를 쏴서
     * 어느 상품인지조차 알 수 없었다(라이브 상품 93 실측). data-prd-no 는 읽힌다. */
    sendAlways('zg_option_layer_open', {
      item_id: it3 ? it3.item_id : currentPrdNo(),
      item_name: it3 ? it3.item_name : ''
    });
  }, true);

  /* ================================================================== *
   * 3. 장바구니 페이지 — view_cart
   * ================================================================== */
  if (/\/order\/basket\.html/i.test(path)) {
    /* R2 수정 (a) — 행을 못 찾던 문제.
     * 우리 스킨 order/basket.html:75-77 의 장바구니 한 줄은
     *   <div module="Order_list"><div class="ec-base-prdInfo gCheck"><div class="prdBox">…
     * 즉 <tr> 도 <li> 도 아니다 → closest('tr, li, .xans-record-') 가 항상 null 이었고
     * view_cart 가 한 건도 안 나갔다(실측: zg_cart_unreadable {link_count:2}).
     * 템플릿상 상품 1건 = .ec-base-prdInfo 1개가 보장된다. */
    var seen = {}, cartItems = [], cartVal = 0, rowCount = 0;
    var links = document.querySelectorAll('a[href*="product_no="]');
    Array.prototype.forEach.call(links, function (a) {
      var row = a.closest ? a.closest('.ec-base-prdInfo, tr, li, .xans-record-') : null;
      if (!row) return;
      if (seen[row.__zg = (row.__zg || Math.random())]) return;
      seen[row.__zg] = 1;
      rowCount++;

      /* R2 수정 (c) — item_id 는 썸네일 링크로 한정한다.
       * .prdName a 는 href 에 product_no 가 없다(프리뷰·라이브 실측). */
      var idLink = row.querySelector('.thumbnail a[href*="product_no="]') || a;
      var mm = (idLink.getAttribute('href') || '').match(/product_no=(\d+)/);
      if (!mm) return;

      var nm = txt(row.querySelector('.prdName')) || txt(a);

      /* R2 수정 (b) — 금액이 1.1조원으로 파괴되던 문제.
       * 예전 '[class*="price"]' 와일드카드가 <ul class="price"> **전체**에 매칭됐다.
       * 그 안에는 상품구매금액·합계·할인 3줄이 들어 있어
       *   "34,900원 34,900원 -0원" → 34900349000 이 됐다.
       * 템플릿(order/basket.html:82)상 첫 번째 <li> 안의 <strong> 하나가
       * {$product_purchase_price_front} = 상품구매금액이다. 그것만 읽는다. */
      var priceEl = row.querySelector('ul.price > li:first-child strong')
                 || row.querySelector('ul.price li strong')
                 || row.querySelector('.sumPrice strong');
      var pr = n(txt(priceEl));

      var qi = row.querySelector('input[name*="quantity"], .quantity input');
      var qt = qi ? n(qi.value) : 1; if (qt <= 0) qt = 1;

      /* 값을 못 읽으면 그 줄은 넣지 않는다 — 틀린 매출을 만들지 않기 위해서다 */
      if (!nm || !pr) return;

      cartItems.push({ item_id: mm[1], item_name: nm, price: pr, quantity: qt });
      cartVal += pr * qt;
    });
    if (cartItems.length) {
      send('view_cart', { currency: 'KRW', value: cartVal, items: cartItems });
    } else {
      send('zg_cart_unreadable', { link_count: links.length, row_count: rowCount });
    }
  }

  /* ================================================================== *
   * 4. 주문서 — begin_checkout (페이지 도달 기준)
   *    바로구매 클릭에서도 쏘지만, 장바구니 경유는 여기서만 잡힌다.
   * ================================================================== */
  if (/\/order\/orderform\.html/i.test(path)) {
    /* R4 수정.
     * 라이브 /order/orderform.html 원문(265KB) 실측:
     *   #totalOrderPrice   → 없음
     *   #total_order_price → 없음
     *   .totalPrice        → 10개 전부 <div class="totalPrice"><h3>배송비</h3>… (배송비 블록)
     * 예전 선택자 '.totalPrice strong' 은 **배송비를 매출로** 읽었다(실측 value:3000).
     *
     * 이 페이지는 카페24 '원터치(스마트) 주문서'라 서버가 빈 껍데기를 주고
     * ( <span id=""></span> 처럼 id 조차 비어 있다 ) 카페24 JS 가 값을 채운다.
     * → 렌더 후 id 를 알 수 없으므로 **구조**로 짚고, 채워질 때까지 짧게 기다린다.
     *   ① .totalPay 중 heading 이 "최종 결제 금액" 인 블록의 <strong>  (라이브 유일)
     *   ② 같은 블록의 클래스 별칭 .totalPay.paymentPrice strong
     *   ③ 결제 버튼(#orderFixItem .btnSubmit) 안의 금액 span
     *      — README(_preview/orderform)가 지목한 {$total_order_price_front_id} 자리
     * 셋 다 못 읽으면 **값 없이** begin_checkout 만 쏘고 진단을 남긴다.
     * 틀린 금액보다 없는 금액이 낫다(설계 원칙 2). */
    var ckTries = 0;
    (function checkoutTick() {
      var v = checkoutTotal();
      if (v) {
        send('begin_checkout', { currency: 'KRW', value: v, checkout_route: 'orderform' });
        return;
      }
      if (ckTries++ >= 25) {                        /* 200ms × 25 = 5초 */
        send('begin_checkout', { checkout_route: 'orderform' });
        sendAlways('zg_checkout_value_unreadable', {
          has_paybox: document.querySelector('.totalPay') ? 1 : 0,
          has_paybtn: document.querySelector('#orderFixItem .btnSubmit') ? 1 : 0
        });
        return;
      }
      setTimeout(checkoutTick, 200);
    })();
  }

  /* 주문서 결제예정금액 — 구조로만 짚는다. 금액 문자열은 코드에 쓰지 않는다. */
  function checkoutTotal() {
    var v = payBoxAmount(document, ['최종 결제 금액', '결제예정금액']);
    if (v) return v;
    v = numFromEl(document.querySelector('.totalPay.paymentPrice strong'));
    if (v) return v;
    var btn = document.querySelector('#orderFixItem .btnSubmit');
    if (!btn) return null;
    var kids = btn.children;
    for (var i = 0; i < kids.length; i++) {
      if (kids[i].tagName !== 'SPAN') continue;
      if (/결제하기|신청하기|주문하기/.test(txt(kids[i]))) continue;   /* 라벨 span 은 건너뛴다 */
      var pv = numFromEl(kids[i]);
      if (pv) return pv;
    }
    return null;
  }

  /* .totalPay 블록 중 heading 이 지정한 라벨인 것의 금액.
   * 주의: .totalPay 는 결제금액·적립 예정금액·적용금액 등 여러 곳이 함께 쓴다
   *       (주문서 5곳 / 주문완료 2곳 — 실측).
   *       heading 으로 골라야 매출 자리에 적립금이 들어가지 않는다. */
  function payBoxAmount(root, labels) {
    var boxes = (root || document).querySelectorAll('.totalPay');
    for (var i = 0; i < boxes.length; i++) {
      var h = norm(txt(boxes[i].querySelector('.heading')));
      for (var j = 0; j < labels.length; j++) {
        if (h === labels[j] || h.replace(/ /g, '') === labels[j].replace(/ /g, '')) {
          var v = numFromEl(boxes[i].querySelector('strong'));
          if (v) return v;
        }
      }
    }
    return null;
  }

  /* 요소에서 숫자만 뽑는다.
   * .refer 는 외화 병기(예: "(USD 25.00)") 라 반드시 뺀다.
   * .displaynone 은 카페24가 '지금 화면에 안 쓰는 값'을 숨겨 두는 클래스라 같이 뺀다
   *   — 라이브 주문완료의 외화 병기 span 은 class="refer displaynone" 이다. */
  function numFromEl(el) {
    if (!el) return null;
    var c = el.cloneNode(true);
    Array.prototype.forEach.call(c.querySelectorAll('.refer, .displaynone'), function (r) {
      if (r.parentNode) r.parentNode.removeChild(r);
    });
    var v = n(c.textContent);
    return v > 0 ? v : null;
  }

  /* ================================================================== *
   * 5. 주문완료 — purchase
   *    선택자 근거: _preview/order_result/README.md + 라이브 실측(2026-09-06)
   *    값을 못 읽으면 purchase 를 쏘지 않는다 — 틀린 매출을 넣지 않기 위해서다.
   *    (못 쏜 경우 zg_purchase_unreadable 로 남겨 놓아 바로 알 수 있게 한다)
   * ================================================================== */
  var resultRoot = document.querySelector('[module="Order_result"], #mCafe24Order, .xans-order-result');
  if (resultRoot && /order_result/i.test(path + ' ' + document.title)) {

    /* 표에서 <th>라벨</th><td>값</td> 을 찾아 숫자만 뽑는다.
     * scope 가 <table> 이면 그 표에 **직접** 속한 th 만 본다 —
     * 라이브 '결제정보 상세' 표 안에는 '상세내역' 중첩 표가 들어 있다(실측). */
    function rowNum(scope, label) {
      if (!scope) return null;
      var ths = scope.querySelectorAll('th');
      var isTable = scope.tagName === 'TABLE';
      for (var i = 0; i < ths.length; i++) {
        if (norm(txt(ths[i])) !== label) continue;
        if (isTable && ths[i].closest('table') !== scope) continue;   /* 중첩 표 배제 */
        var td = ths[i].parentElement && ths[i].parentElement.querySelector('td');
        var v = numFromEl(td);
        if (v) return v;
      }
      return null;
    }

    /* --- 주문번호: .resultInfo 표의 "주문번호" 행 (템플릿상 {$order_id}) --- */
    var oid = '';
    var info = resultRoot.querySelector('.resultInfo');
    var ths2 = (info || resultRoot).querySelectorAll('th');
    for (var i2 = 0; i2 < ths2.length; i2++) {
      if (norm(txt(ths2[i2])) === '주문번호') {
        var td2 = ths2[i2].parentElement.querySelector('td');
        oid = txt(td2 && (td2.querySelector('.txtEm') || td2)).replace(/\s+/g, '');
        if (oid) break;
      }
    }

    /* --- 결제금액 ---
     * 하단 .totalPay 가 정본이다. 단 "적립 예정금액" 블록도 .totalPay 를 쓰므로
     * heading 이 정확히 "결제금액" 인 것만 고른다. 없으면 상단 표에서 읽는다. */
    var pay = payBoxAmount(resultRoot, ['결제금액', '최종 결제 금액']);
    if (pay === null) pay = rowNum(info, '결제금액');

    /* --- 배송비 / 부가세 ---
     * 주의: '배송비' 라벨은 배송유형별 소계 표(금액정보)에도 있고 그쪽이 문서상 먼저 나온다.
     *       반드시 <caption>결제정보 상세</caption> 표 안에서만 읽는다.
     *       라이브 결제정보 상세는 '지역별 배송비'(띄어쓰기 있음), 소계표는 '지역별배송비'(없음)다. */
    var payTable = null;
    var caps = resultRoot.querySelectorAll('caption');
    for (var i4 = 0; i4 < caps.length; i4++) {
      if (norm(txt(caps[i4])) === '결제정보 상세') { payTable = caps[i4].closest('table'); break; }
    }
    var shipFee  = payTable ? rowNum(payTable, '배송비') : null;
    var localFee = payTable ? (rowNum(payTable, '지역별 배송비') || rowNum(payTable, '지역별배송비')) : null;
    var vat      = payTable ? rowNum(payTable, '부가세') : null;

    /* --- 상품 목록 ---
     * 국내(기본)·개별·해외 주문내역 세 모듈만 본다.
     * 배송지정보(deliverybindinglist)와 사은품(giftresultlist)은 제외 —
     * 같은 .ec-base-prdInfo 마크업을 쓰기 때문에 넣으면 중복된다.
     * ⚠ 라이브에서는 module= 이 class="xans-order-…" 로 바뀐다 → modSel() 이 둘 다 잡는다. */
    var items = [];
    var lists = resultRoot.querySelectorAll(
      modSel('normalresultlist') + ', ' + modSel('individualresultlist') + ', ' + modSel('oversearesultlist')
    );
    Array.prototype.forEach.call(lists, function (list) {
      Array.prototype.forEach.call(list.querySelectorAll('.ec-base-prdInfo'), function (box) {
        var link = box.querySelector('.thumbnail a[href*="product_no="], .prdName a[href*="product_no="]');
        var mm = link ? (link.getAttribute('href') || '').match(/product_no=(\d+)/) : null;
        var nm = txt(box.querySelector('.prdName'));
        if (!nm) return;

        var qty = 1, buy = null, variant = '';
        Array.prototype.forEach.call(box.querySelectorAll('li'), function (li) {
          var t = norm(txt(li));
          if (/^수량\s*:/.test(t)) { var q = n(t); if (q > 0) qty = q; }
          else if (/^상품구매금액\s*:/.test(t) && buy === null) { buy = numFromEl(li); }
        });
        var optEl = box.querySelector('p.option');
        /* R5 와 같은 규칙을 옵션 표기에도 적용한다 (할인율은 저장하지 않는다) */
        if (optEl) variant = cleanVariant(norm(txt(optEl)));

        items.push({
          item_id: mm ? mm[1] : '',
          item_name: nm,
          item_variant: variant,
          quantity: qty,
          price: buy !== null && qty > 0 ? Math.round(buy / qty) : 0
        });
      });
    });

    if (oid && pay) {
      /* 새로고침·뒤로가기로 같은 주문이 두 번 잡히는 것을 막는다.
       * (지금 GA4 의 431건이 부풀려졌을 수 있는 이유 중 하나다) */
      var key = 'zg_p_' + oid, dup = false;
      try { dup = !!localStorage.getItem(key); if (!dup) localStorage.setItem(key, '1'); } catch (e) {}
      if (!dup) {
        var pp = {
          transaction_id: oid,
          currency: 'KRW',
          value: pay,
          item_count: items.length
        };
        if (shipFee !== null || localFee !== null) pp.shipping = (shipFee || 0) + (localFee || 0);
        if (vat !== null) pp.tax = vat;
        if (items.length) pp.items = items;
        send('purchase', pp);
      } else {
        send('zg_purchase_repeat_view', { transaction_id: oid });
      }
    } else {
      /* 값을 못 읽으면 매출을 지어내지 않는다. 대신 신호를 남긴다. */
      send('zg_purchase_unreadable', {
        has_order_id: oid ? 1 : 0,
        has_value: pay ? 1 : 0,
        item_count: items.length
      });
    }
  }

  /* ================================================================== *
   * 6. 로그인 동선 — 카카오 로그인이 병목으로 의심되는 구간
   *    (규칙 10: 카카오 단독 로그인은 플러스친구 확보를 위한 의도된 전략이다)
   * ================================================================== */
  if (/login|member\/login|loginSns|mapping_login/i.test(path)) {
    send('zg_login_view', { login_page: path });
  }
  document.addEventListener('click', function (e) {
    /* R3 수정.
     * (a) 예전 '[class*="kakao"]' 는 CSS 속성 선택자라 **대소문자를 구분**한다.
     *     라이브 로그인 버튼은
     *       <a href="#none" class="btnKakao " onclick="MemberAction.kakaosyncLogin('13c140b6…')">
     *     이므로 소문자 'kakao' 로는 **매칭되지 않았다** → login 0건.
     * (b) 반면 전 페이지 사이드메뉴의
     *       <li class="aside-category__item kakao_link">…채팅상담</li>
     *     는 매칭돼서 상담 클릭이 login 으로 오발사됐다(실측).
     * (c) #kakaoKey 는 카카오 '공유하기' 키 보관용 hidden div 다. 로그인과 무관 → 제거.
     * → 로그인 버튼만 정확히 잡고, 채팅상담(.kakao_link)과
     *   숨김 샘플 버튼(.fake-sns-login)은 명시적으로 제외한다. */
    var t = e.target && e.target.closest
      ? e.target.closest('.btnKakao, [onclick*="kakaosyncLogin"], [onclick*="KakaoLogin"]') : null;
    if (!t) return;
    if (t.closest('.kakao_link, .fake-sns-login')) return;
    sendAlways('login', { method: 'kakao' });
  }, true);

  /* ================================================================== *
   * 7. 스크롤 깊이 — "긴 상세페이지 어디서 나가는가"
   *    GA4 기본 scroll 은 90% 한 번뿐이라 구간을 못 본다. 직접 쪼갠다.
   * ================================================================== */
  (function () {
    /* cafe24 는 /product/detail.html 과 pretty URL(/product/이름/11/...) 을 둘 다 쓴다.
     * 경로로 판별하지 말고 DOM 으로 판별한다. */
    var isProduct = !!infoArea();
    var isHome = (path === '/' || path === '/index.html');
    if (!isProduct && !isHome) return;
    var marks = [10, 25, 50, 75, 90, 100], fired = {};
    var start = Date.now();
    function onScroll() {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      if (h <= 0) return;
      var pct = Math.round((window.pageYOffset / h) * 100);
      for (var i = 0; i < marks.length; i++) {
        var m = marks[i];
        if (pct >= m && !fired[m]) {
          fired[m] = 1;
          sendAlways('zg_scroll_depth', {
            percent: m,
            seconds: Math.round((Date.now() - start) / 1000),
            page_kind: isProduct ? 'product' : 'home',
            item_id: isProduct ? currentPrdNo() : ''
          });
        }
      }
    }
    var t = null;
    window.addEventListener('scroll', function () {
      if (t) return;
      t = setTimeout(function () { t = null; onScroll(); }, 200);
    }, { passive: true });
  })();

  } /* boot */

})();
