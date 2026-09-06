/* ============================================================================
 * ds/js/ga4.js — 젠제네틱스 GA4 계측 (전 페이지 공통)
 *
 * 원칙
 *  1. 템플릿을 고치지 않는다. 화면에 이미 그려진 DOM 에서만 읽는다.
 *  2. 값을 못 읽으면 이벤트를 쏘지 않는다. 틀린 숫자보다 없는 게 낫다.
 *  3. 가격·할인율을 코드에 쓰지 않는다 (가격_백엔드구조.md).
 *  4. 개인정보(이름·전화·주소·이메일)는 어떤 파라미터에도 담지 않는다.
 *  5. 모든 이벤트에 zg_ver 를 붙인다 → 개편 단계별 before/after 비교용.
 * ==========================================================================*/
(function () {
  'use strict';

  /* 개편할 때마다 이 숫자만 올린다. GA4 에서 이 값으로 버전을 나눠 본다. */
  var ZG_VER = '2.001';

  /* head 에서 로드되므로 DOM 이 그려진 뒤에 실행한다 */
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }

  function boot() {
  if (typeof window.gtag !== 'function') return;

  /* 모든 이벤트에 공통으로 붙는 파라미터 */
  gtag('set', { zg_ver: ZG_VER });

  var path = location.pathname;
  var sent = {};                                    /* 중복 발사 방지 */

  function send(name, params) {
    if (sent[name]) return;
    sent[name] = 1;
    params = params || {};
    params.zg_ver = ZG_VER;
    gtag('event', name, params);
  }
  function sendAlways(name, params) {
    params = params || {};
    params.zg_ver = ZG_VER;
    gtag('event', name, params);
  }
  function n(v) {                                   /* "34,900원" → 34900 */
    if (v === null || v === undefined) return 0;
    var d = String(v).replace(/[^0-9]/g, '');
    return d ? parseInt(d, 10) : 0;
  }
  function txt(el) { return el ? (el.textContent || '').trim() : ''; }

  /* ------------------------------------------------------------------ *
   * 현재 상품 — 상세페이지 .infoArea 가 값을 전부 물고 있다
   *   product/detail.html:79
   *   data-name / data-price / data-custom / data-prd-no
   * ------------------------------------------------------------------ */
  function currentItem() {
    var a = document.querySelector('.infoArea');
    if (!a) return null;
    var price = n(a.getAttribute('data-price'));
    var id    = a.getAttribute('data-prd-no') || '';
    var name  = a.getAttribute('data-name') || '';
    if (!id || !price) return null;                 /* 못 읽으면 안 쏜다 */
    return { item_id: String(id), item_name: name, price: price, currency: 'KRW' };
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
   * 라이브 옵션 예: "🔥BEST🔥[지금 24%▼] 젠제네틱스 붓기파우더 2 box (무료배송) (+33,100원)"
   * 앞의 [할인율]·이모지와 뒤의 (+가격)을 떼고 알맹이만 남긴다.
   * 할인율·가격은 우리가 저장하지 않는다 (가격_백엔드구조.md). */
  function currentVariant() {
    var sel = document.querySelector('select[name^="option"]:not([name^="addproduct"])');
    if (!sel || !sel.value || sel.value === '*' || sel.value === '**') return '';
    var t = (sel.options[sel.selectedIndex] || {}).text || '';
    return t.replace(/\[[^\]]*\]/g, '')          /* [지금 24%▼] 제거 */
            .replace(/\(\+[^)]*\)/g, '')          /* (+33,100원) 제거 */
            .replace(/[\u{1F300}-\u{1FAFF}\u{2600}-\u{27BF}]/gu, '')
            .replace(/\s+/g, ' ').trim();
  }

  /* 화면에 그려진 합계(#totalPrice). 옵션 추가금이 반영된 진짜 금액이다.
   * 못 읽으면 null 을 돌려주고, 호출부가 기본가로 대체한다. */
  function screenTotal() {
    var el = document.querySelector('#totalPrice, .totalPrice');
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
  }

  /* ================================================================== *
   * 2. 장바구니 담기 / 바로구매 — add_to_cart, begin_checkout
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
      mode = /장바구니|cart/i.test(txt(hit.el) + ' ' + (hit.el.className || '')) ? '2' : '1';
    }
    if (!mode) return;

    var variant = currentVariant();
    var total = screenTotal();
    var payload = it ? {
      currency: 'KRW',
      value: total !== null ? total : it.price * qty,
      value_source: total !== null ? 'screen_total' : 'base_price',
      items: [{
        item_id: it.item_id, item_name: it.item_name,
        item_variant: variant, price: it.price, quantity: qty
      }]
    } : {};

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
      item_id: it2 ? it2.item_id : '',
      item_name: it2 ? it2.item_name : '',
      item_variant: currentVariant()
    });
  }, true);

  /* 옵션 레이어 열림 — 지금 최대 이탈 지점(상품조회 35,019 → 옵션선택 1,153) */
  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('.jsLayerBtn') : null;
    if (!t) return;
    var it = currentItem();
    sendAlways('zg_option_layer_open', it ? { item_id: it.item_id, item_name: it.item_name } : {});
  }, true);

  /* ================================================================== *
   * 3. 장바구니 페이지 — view_cart
   * ================================================================== */
  if (/\/order\/basket\.html/i.test(path)) {
    /* ⚠ 미검증. cafe24 가 렌더할 때 붙이는 .xans-record- 는 프리뷰에 없어서
     *   로컬에서 확인이 불가능했다. 그래서 클래스에 기대지 않고
     *   "상품 링크(a[href*=product_no])" 를 기준점으로 잡고 위로 올라간다.
     *   행을 못 찾으면 아무것도 쏘지 않는다. */
    var seen = {}, cartItems = [], cartVal = 0;
    var links = document.querySelectorAll('a[href*="product_no="]');
    Array.prototype.forEach.call(links, function (a) {
      var row = a.closest ? a.closest('tr, li, .xans-record-') : null;
      if (!row || seen[row.__zg = (row.__zg || Math.random())]) return;
      seen[row.__zg] = 1;
      var mm = (a.getAttribute('href') || '').match(/product_no=(\d+)/);
      if (!mm) return;
      var nm = txt(a) || txt(row.querySelector('.prdName, .name'));
      var pr = n(txt(row.querySelector('.price, td.price, [class*="price"]')));
      var qi = row.querySelector('input[name*="quantity"], .quantity input');
      var qt = qi ? n(qi.value) : 1; if (qt <= 0) qt = 1;
      if (!nm) return;
      cartItems.push({ item_id: mm[1], item_name: nm, price: pr, quantity: qt });
      cartVal += pr * qt;
    });
    if (cartItems.length) {
      send('view_cart', { currency: 'KRW', value: cartVal, items: cartItems });
    } else {
      send('zg_cart_unreadable', { link_count: links.length });
    }
  }

  /* ================================================================== *
   * 4. 주문서 — begin_checkout (페이지 도달 기준)
   *    바로구매 클릭에서도 쏘지만, 장바구니 경유는 여기서만 잡힌다.
   * ================================================================== */
  if (/\/order\/orderform\.html/i.test(path)) {
    var totEl = document.querySelector('#totalOrderPrice, .totalPrice strong, #total_order_price');
    var tot = n(txt(totEl));
    sendAlways('begin_checkout', tot
      ? { currency: 'KRW', value: tot, checkout_route: 'orderform' }
      : { checkout_route: 'orderform' });
  }

  /* ================================================================== *
   * 5. 주문완료 — purchase
   *    ⚠ order/order_result.html 템플릿을 아직 못 받았다.
   *      아래 선택자는 카페24 기본 스킨 기준 추정이다.
   *      템플릿을 받으면 이 블록만 정확히 다시 잡으면 된다.
   *      값을 못 읽으면 purchase 를 쏘지 않는다 — 틀린 매출을 넣지 않기 위해서다.
   *      (못 쏜 경우 zg_purchase_unreadable 로 남겨 놓아 바로 알 수 있게 한다)
   * ================================================================== */
  var resultRoot = document.querySelector('[module="Order_result"], #mCafe24Order');
  if (resultRoot && /order_result/i.test(path + ' ' + document.title)) {

    /* 표에서 <th>라벨</th><td>값</td> 을 찾아 숫자만 뽑는다.
     * .refer 는 외화 병기(예: "(USD 25.00)") 라 반드시 뺀다. */
    function numFromEl(el) {
      if (!el) return null;
      var c = el.cloneNode(true);
      Array.prototype.forEach.call(c.querySelectorAll('.refer'), function (r) { r.remove(); });
      var v = n(c.textContent);
      return v > 0 ? v : null;
    }
    function rowNum(scope, label) {
      var ths = (scope || document).querySelectorAll('th');
      for (var i = 0; i < ths.length; i++) {
        if (txt(ths[i]) === label) {
          var td = ths[i].parentElement && ths[i].parentElement.querySelector('td');
          return numFromEl(td);
        }
      }
      return null;
    }

    /* --- 주문번호: .resultInfo 표의 "주문번호" 행 (템플릿상 {$order_id}) --- */
    var oid = '';
    var info = resultRoot.querySelector('.resultInfo');
    var ths2 = (info || resultRoot).querySelectorAll('th');
    for (var i2 = 0; i2 < ths2.length; i2++) {
      if (txt(ths2[i2]) === '주문번호') {
        var td2 = ths2[i2].parentElement.querySelector('td');
        oid = txt(td2 && (td2.querySelector('.txtEm') || td2)).replace(/\s+/g, '');
        break;
      }
    }

    /* --- 결제금액 ---
     * 하단 .totalPay 가 정본이다. 단 "적립 예정금액" 블록도 .totalPay 를 쓰므로
     * heading 이 정확히 "결제금액" 인 것만 고른다. 없으면 상단 표에서 읽는다. */
    var pay = null;
    var pays = resultRoot.querySelectorAll('.totalPay');
    for (var i3 = 0; i3 < pays.length; i3++) {
      if (txt(pays[i3].querySelector('.heading')) === '결제금액') {
        pay = numFromEl(pays[i3].querySelector('strong'));
        break;
      }
    }
    if (pay === null) pay = rowNum(info, '결제금액');

    /* --- 배송비 / 부가세 ---
     * 주의: '배송비' 라벨은 배송유형별 소계 표([기본배송] 등)에도 있고 그쪽이 문서상 먼저 나온다.
     *       반드시 <caption>결제정보 상세</caption> 표 안에서만 읽는다. */
    var payTable = null;
    var caps = resultRoot.querySelectorAll('caption');
    for (var i4 = 0; i4 < caps.length; i4++) {
      if (txt(caps[i4]) === '결제정보 상세') { payTable = caps[i4].closest('table'); break; }
    }
    var shipFee = payTable ? rowNum(payTable, '배송비') : null;
    var localFee = payTable ? rowNum(payTable, '지역별 배송비') : null;
    var vat = payTable ? rowNum(payTable, '부가세') : null;

    /* --- 상품 목록 ---
     * 국내(기본)·개별·해외 주문내역 세 모듈만 본다.
     * 배송지정보(Order_deliverybindinglist)와 사은품(Order_giftresultlist)은 제외 —
     * 같은 .ec-base-prdInfo 마크업을 쓰기 때문에 넣으면 중복된다. */
    var items = [];
    var lists = resultRoot.querySelectorAll(
      '[module="Order_normalresultlist"], [module="Order_individualresultlist"], [module="Order_oversearesultlist"]'
    );
    Array.prototype.forEach.call(lists, function (list) {
      Array.prototype.forEach.call(list.querySelectorAll('.ec-base-prdInfo'), function (box) {
        var link = box.querySelector('.thumbnail a[href*="product_no="], .prdName a[href*="product_no="]');
        var mm = link ? (link.getAttribute('href') || '').match(/product_no=(\d+)/) : null;
        var nm = txt(box.querySelector('.prdName'));
        if (!nm) return;

        var qty = 1, buy = null, variant = '';
        Array.prototype.forEach.call(box.querySelectorAll('li'), function (li) {
          var t = txt(li);
          if (/^수량\s*:/.test(t)) { var q = n(t); if (q > 0) qty = q; }
          else if (/^상품구매금액\s*:/.test(t) && buy === null) { buy = numFromEl(li); }
        });
        var optEl = box.querySelector('p.option');
        if (optEl) variant = txt(optEl).replace(/\s+/g, ' ');

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
   * ================================================================== */
  if (/login|member\/login|loginSns|mapping_login/i.test(path)) {
    send('zg_login_view', { login_page: path });
  }
  document.addEventListener('click', function (e) {
    var t = e.target && e.target.closest ? e.target.closest('#kakaoKey, [class*="kakao"], [id*="kakao"]') : null;
    if (t) sendAlways('login', { method: 'kakao' });
  }, true);

  /* ================================================================== *
   * 7. 스크롤 깊이 — "긴 상세페이지 어디서 나가는가"
   *    GA4 기본 scroll 은 90% 한 번뿐이라 구간을 못 본다. 직접 쪼갠다.
   * ================================================================== */
  (function () {
    /* cafe24 는 /product/detail.html 과 pretty URL(/product/이름/11/...) 을 둘 다 쓴다.
     * 경로로 판별하지 말고 DOM 으로 판별한다. */
    var isProduct = !!document.querySelector('.infoArea');
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
            item_id: isProduct ? (document.querySelector('.infoArea').getAttribute('data-prd-no') || '') : ''
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
