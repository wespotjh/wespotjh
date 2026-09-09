/* ============================================================================
 * ds/js/detail-ui.js — 젠제네틱스 상품 상세 UI (칼륨 product_no=11 기준, 9종 공용)
 *
 * 절대 규칙
 *   - 가격을 계산하지 않는다. 화면에 쓰는 금액은 전부 `#totalPrice .total strong`
 *     (없으면 `… em`)에서 읽고 `(N개)` 꼬리만 떼어 쓴다.
 *   - 평점·리뷰수를 쓰지 않는다 (알파리뷰 위젯 담당).
 *   - `#freeShipGuide` 는 스킨 JS 가 이미 구동한다. 여기서 진행률·금액을 만들지 않는다.
 *   - `#totalProducts` 내부에 래퍼를 추가하지 않는다 (스킨 셀렉터가 7단 자손 체인이다).
 *   - 옵션 선택의 진실원장은 `tr.option_product` 행 목록이다 (select 는 `*` 로 되돌아간다).
 *
 * 로드 경로 (실측으로 확정한 사실만 적는다)
 *   이 파일은 `product/detail.html` 상단의 `@js()` 로 선언된다. 카페24는 `@css/@js` 디렉티브를
 *   모아 번들 2벌을 만든다 — **CSS 번들은 `<head>`, JS 번들은 `</body>` 근처**다.
 *   번들 안 순서 규칙: ① 콘텐츠 페이지의 직접 선언(줄 순서) → ② 레이아웃 → ③ 콘텐츠가 import 한 파일.
 *   따라서 이 파일은 **사용자 JS 번들 1번**이고, 같은 페이지의 스킨 JS 보다 먼저 실행된다.
 *   두 번들 모두 defer/async 없는 classic script 라 문서 순서대로 동기 실행된다.
 *
 * 그 순서에 기대는 것 2가지 (뒤집혀도 안전하게 실패하도록 만들어 두었다)
 *   ① 스킨 JS 가 지워 버리는 `#freeShipGuide[data-delivery]` / `.delivery_price_css` 를 먼저 붙잡는다.
 *      못 잡으면 배송비 줄이 안내 문구로 폴백한다 — 숫자를 지어내지 않는다.
 *   ② 상세 이미지 승격을 지연로더(jQuery ready)보다 먼저 한다.
 *      밀리더라도 로더는 교차 전까지 원본 속성을 남기므로 init() 의 재승격이 회수한다.
 * ==========================================================================*/

/* ── 확정 사양. 아래 두 값이 현재 동작이다.
 *    플래그는 지우지 않는다 — 전 상품 전개 후 A/B 검증 때 한 줄로 뒤집기 위해 남겨 둔다.
 *    값만 바꾸면 동작이 바뀐다. ── */
var ZG_OPT_MODE = 'multi';      /* 'multi' = 구성 카드를 눌러 여러 구성을 담을 수 있다 (현재 라이브 동작, 확정 기본값)
                                   'single' = 라디오처럼 택1. 카페24가 만든 tr.option_product 를 프로그램 삭제한다
                                              (삭제 컨트롤을 못 찾으면 'multi' 로 안전 폴백) */
var ZG_OPT_AUTOSELECT = false;  /* 확정 = false (총액 0원에서 시작, 고객이 직접 선택)
                                   true = 페이지 진입 시 2box 를 자동 선택 */

/* ── 부작용이 확인되면 즉시 되돌리기 위한 안전핀 (설계 규칙) ── */
var ZG_MOVE_TOTALPRODUCTS = true; /* true = ≤767px 에서 선택목록(#totalProducts)을 구성카드 바로 아래로 옮긴다 */

(function () {
  'use strict';

  /* ------------------------------------------------------------------ 유틸 */
  function $(sel, ctx) { try { return (ctx || document).querySelector(sel); } catch (e) { return null; } }
  function $$(sel, ctx) {
    try { return Array.prototype.slice.call((ctx || document).querySelectorAll(sel)); }
    catch (e) { return []; }
  }
  function txt(el) { return el ? (el.textContent || '') : ''; }
  function squash(s) { return String(s || '').replace(/\s+/g, ' ').trim(); }
  function keyOf(s) { return String(s || '').replace(/\s+/g, ''); }
  function el(tag, cls, text) {
    var n = document.createElement(tag);
    if (cls) n.className = cls;
    if (text != null) n.textContent = text;
    return n;
  }
  function on(node, ev, fn) { if (node && node.addEventListener) node.addEventListener(ev, fn, false); }

  /* ================================================================== *
   * 검수 항목 · K-09 SEO 하드가드 (QA 검수)
   * ------------------------------------------------------------------
   * `.zg-fold` 는 overflow:hidden 이라 `CAFE24.lazyload()` 의 IntersectionObserver 가
   * 접힌 구간의 <img> 와 **영원히 교차하지 않는다**. IO 의 교차 사각형은 조상의 클립
   * 사각형과 교집합을 취하기 때문이다. 결과: 상세 14장 중 약 12장이 1x1 placeholder
   * 로 굳어 색인에서 사라진다(개편 전엔 되던 것 → 회귀).
   * 이전 판의 `dispatchEvent(new Event('scroll'))` 완화책은 **무효**였다 —
   * IO 는 scroll 이벤트를 구독하지 않는다. 그 코드는 삭제했다.
   *
   * 대신 `ec-data-src` 를 우리가 직접 `src` 로 승격하고 속성을 지워 로더 대상에서
   * 제외한다. 성능은 네이티브 loading="lazy" 로 유지한다(네이티브 지연로딩은
   * 마크업의 src 를 지우지 않으므로 크롤러가 URL 을 본다).
   * alt 는 {$name} 이 렌더된 h1.prd-name 에서 읽는다 — 문구를 창작하지 않는다.
   * NNEditor 원본은 그대로다(런타임 속성 승격일 뿐 설계 규칙 위반 아님).
   * ================================================================== */
  function unlazyDetailImages() {
    try {
      var host = document.getElementById('prdDetail');
      if (!host) return 0;
      var h1 = document.querySelector('.prd-name');
      var nm = h1 ? (h1.textContent || '').replace(/\s+/g, ' ').trim() : '';
      var imgs = host.querySelectorAll('img[ec-data-src]');
      var n = 0;
      for (var i = 0; i < imgs.length; i++) {
        var img = imgs[i], real = img.getAttribute('ec-data-src');
        if (!real) continue;
        img.removeAttribute('ec-data-src');          /* CAFE24.lazyload() 대상에서 제외 */
        /* [검수 근거] 첫 2장은 즉시(LCP 후보), 나머지는 지연.
         * 로드 전 높이 0 문제는 ds/css/detail.css 의 `aspect-ratio`/`min-width` 가 막는다 —
         * 자리를 차지해야 `loading="lazy"` 가 실제로 동작한다. */
        img.setAttribute('loading', n < 2 ? 'eager' : 'lazy');
        img.setAttribute('fetchpriority', n < 2 ? 'high' : 'low');
        img.setAttribute('decoding', 'async');
        if (!img.getAttribute('alt')) img.setAttribute('alt', nm + ' 상세 이미지 ' + (i + 1));
        img.src = real;
        n++;
      }
      return n;
    } catch (e) { return 0; }
  }
  /* 카페24 지연로더는 이렇게 기동한다:
   *     EC$(function(){ if (EC$('img[ec-data-src]').length > 0) CAFE24.lazyload(); });
   * 우리가 상세 이미지를 전부 승격하면 그 가드가 **0** 이 되어 로더가 아예 시작하지 않는다.
   * 로더는 IntersectionObserver 뿐 아니라 **MutationObserver 도** 걸어서 나중에 DOM 에 들어오는
   * 지연 이미지를 회수하는데, 그것까지 같이 죽는다.
   * (실측: 이 몰 상품들의 ec-data-src 는 전부 #prdDetail 안이라 지금은 피해가 없다.
   *  그러나 연관상품 등이 켜지면 조용히 깨진다 — 운이 좋은 것이지 설계가 아니다.)
   * → 승격을 끝낸 뒤 로더를 **우리가 한 번 불러** 관찰자를 되살린다. 대상이 0개여도
   *   관찰자만 설치되고 부작용이 없다. */
  function rearmLazyLoader() {
    try {
      var C = window.CAFE24;
      if (C && typeof C.lazyload === 'function' && !window.__ZG_LAZY_REARMED__) {
        window.__ZG_LAZY_REARMED__ = 1;
        C.lazyload();
      }
    } catch (e) {}
  }

  /* jQuery ready(= CAFE24.lazyload 실행 시점)보다 먼저 이겨야 하므로 파싱 시점에 즉시 실행.
   * 아직 #prdDetail 이 없으면 DOMContentLoaded 로 미룬다. init() 에서 한 번 더 돌려
   * 로더가 먼저 돌아 placeholder 를 씌운 경우도 회수한다(ec-data-src 는 교차 전까지 남는다). */
  if (document.getElementById('prdDetail')) unlazyDetailImages();
  else if (document.addEventListener) document.addEventListener('DOMContentLoaded', unlazyDetailImages, false);

  /* ------------------------------------------- 스킨 JS 보다 먼저 값을 확보 */
  /* moa/js/product/detail.js 는 초기화가 끝나면
   *   $('#freeShipGuide').removeAttr('data-delivery');  $('.delivery_price_css').remove();
   * 를 실행한다. 둘 다 사라지기 전에 문자열만 복사해 둔다(숫자를 파싱하지 않는다). */
  /* 한 번이라도 읽히면 기억한다. 로드 순서가 바뀌어도(검수 항목 로 @js 번들로 이동) 어느 한
   * 시점에서든 읽히면 되고, 끝내 못 읽으면 **숫자를 지어내지 않고** 안내 문구로 대체한다. */
  var CAPTURED = { delivery: '' };
  function captureDelivery() {
    if (CAPTURED.delivery) return CAPTURED.delivery;
    try {
      var g = document.getElementById('freeShipGuide');
      var a = g && g.getAttribute('data-delivery');
      if (a && squash(a)) { CAPTURED.delivery = squash(a); return CAPTURED.delivery; }
      var d = document.querySelector('.delivery_price_css');
      if (d && squash(txt(d))) { CAPTURED.delivery = squash(txt(d)); return CAPTURED.delivery; }
    } catch (e) {}
    return '';
  }
  captureDelivery();

  /* ------------------------------------------------------- 총액 (읽기 전용) */
  /* ds/js/zg-ga4.js screenTotal() 과 같은 규칙: `#totalPrice .total strong|em` 만 읽고
   * "(N개)" 꼬리를 뗀다. `#totalPrice` 전체 텍스트를 읽으면 "680001" 이 된다. */
  function totalNode() { return $('#totalPrice .total strong, #totalPrice .total em'); }
  function totalText() {
    var t = squash(txt(totalNode()));
    return t.replace(/\(\s*\d+\s*개\s*\)\s*$/, '').trim();
  }
  function totalNum() {
    var d = totalText().replace(/[^0-9]/g, '');
    return d ? parseInt(d, 10) : 0;
  }

  /* [13종 대비] "판매가가 실제로 있는 상품인가" — 계산하지 않고 스킨이 이미 써 둔 값만 읽는다.
   * 34/91/93 은 `.infoArea[data-price]` 가 "이벤트종료" · "구매 상품이 아닙니다" 같은 문구이고
   * 수량행 단가(`#totalProducts span.quantity_price`)도 비어 있다.
   * 60/61/62 는 옵션이 없어도 단가가 있으므로 여기서 true 가 되어 금액 줄을 유지한다. */
  function hasRealPrice() {
    var info = $('.infoArea[data-price]');
    if (info && /[0-9]/.test(info.getAttribute('data-price') || '')) return true;
    if (/[0-9]/.test(squash(txt($('#totalProducts span.quantity_price'))))) return true;
    return false;
  }

  /* -------------------------------------------------- 진실원장: 선택된 행 */
  function readRow(r) {
    var sp = $('p.product span', r);
    /* [9종 복제 대비] 옵션 없이 add_option 만 있는 상품은 p.product 에 <span> 이 없다.
     * 스킨의 `.product{font-size:0}` 설계 때문에 행 글자가 통째로 사라지고,
     * key 도 빈 문자열이 되어 카드 선택 표시가 붙지 않는다.
     * → <span> 이 없으면 p.product 전체 텍스트를 쓰고 행에 표식을 남겨 CSS 로 글자를 되살린다. */
    var src = sp;
    if (!sp) {
      src = $('p.product', r);
      /* p.product 가 있는데 <span> 만 없는 경우에만 표식을 남긴다.
       * (옵션 없는 상품의 정적행에는 p.product 자체가 없다 — 그 행은 스킨이 이미 그린다) */
      if (src && r.setAttribute) r.setAttribute('data-zg-nospan', '1');
    }
    var qi = $('input.quantity_opt, input[name^="quantity_opt"]', r);
    var q = 1;
    if (qi) {
      var dd = String(qi.value || '').replace(/[^0-9]/g, '');
      q = dd ? parseInt(dd, 10) : 1;
      if (q <= 0) q = 1;
    }
    return { el: r, key: keyOf(txt(src)), qty: q };
  }
  /* 카드 선택 표시의 진실원장 — 본품 구성 행만 센다 (설계 규칙) */
  function pickedRows() { return $$('tr.option_product').map(readRow); }

  /* 빈 상태 판정 = **화면에 실제로 보이는 행**의 개수.
   *
   * 클래스(`tr.option_product` / `tr.add_product`)로 세면 두 번 틀린다:
   *   ① 추가상품만 고른 고객에게 "구성을 선택해 주세요"가 뜬다 (필수옵션 상품)
   *   ② **옵션이 아예 없는 상품**에서는 그 두 클래스가 영원히 안 붙는다.
   *      실측: 필수옵션 상품은 정적행이 `<tbody class="displaynone">` 안에 숨어 있지만,
   *      옵션 없는 상품은 `<tbody class="">` 로 **노출**되고 그 행의
   *      `input[name="quantity_opt[]"]` 이 이미 value="1" 이다 (= 이미 1개가 담긴 상태).
   *      그 상품에서 클래스로 세면 영구 0 이라 금액은 뜨는데 안내문도 같이 뜬다.
   *
   * 그래서 "보이는 tbody 안의, 옵션 상세행이 아닌 tr" 을 센다. 9종 어느 형태에서도 성립한다. */
  function visibleRows() {
    var out = [];
    var tp = document.getElementById('totalProducts');
    if (!tp) return out;
    var table = null, i;
    for (i = 0; i < tp.children.length; i++) if (tp.children[i].tagName === 'TABLE') { table = tp.children[i]; break; }
    if (!table) return out;
    var hidden = /(^|\s)displaynone(\s|$)/;
    for (i = 0; i < table.children.length; i++) {
      var tb = table.children[i];
      if (tb.tagName !== 'TBODY' || hidden.test(tb.className || '')) continue;
      for (var j = 0; j < tb.children.length; j++) {
        var tr = tb.children[j];
        if (tr.tagName !== 'TR') continue;
        if (tr.id === 'totalProductsOption') continue;      /* 옵션 상세(주소·각인 등) 행 */
        if (hidden.test(tr.className || '')) continue;
        out.push(tr);
      }
    }
    return out;
  }
  function rowMatches(rowKey, cardKey) {
    if (!rowKey || !cardKey) return false;
    return rowKey.indexOf(cardKey) >= 0 || cardKey.indexOf(rowKey) >= 0;
  }
  function isFreeShip() {
    var f = document.getElementById('levelLineActive');
    return !!(f && f.classList && f.classList.contains('full'));
  }
  function isSoldout() {
    var s = $('.productAction .soldout');
    if (!s) return false;
    return !/(^|\s)displaynone(\s|$)/.test(s.className || '');
  }

  /* --------------------------------------------------------------- 토스트 */
  var toastEl = null, toastTimer = null;
  function toast(msg) {
    try {
      if (!toastEl) {
        toastEl = el('div', 'zg-toast');
        toastEl.setAttribute('role', 'status');
        document.body.appendChild(toastEl);
      }
      toastEl.textContent = msg;
      toastEl.classList.add('zg-on');
      clearTimeout(toastTimer);
      toastTimer = setTimeout(function () { toastEl.classList.remove('zg-on'); }, 2400);
    } catch (e) {}
  }

  /* ------------------------------------------------------- 옵션 텍스트 가공 */
  /* 문자열 가공까지만 한다 — 숫자는 손대지 않는다 (K-04 AC3).
   *
   * 관리자 옵션명은 작명 규칙이 두 가지다. 둘 다 받아야 한다.
   *   A) `[지금 24%▼] 상품명 N box (무료배송) (+33,100원)`
   *   B) `상품명 [6+3] (45%할인 | 9주 | 무료배송) (+126,000원)`
   * 예전 규칙은 소괄호를 `(+N원)`·`(무료배송)` **두 형태만** 지워서 B 형의
   * `(45%할인 | 9주 | 무료배송)` 이 제목에 통째로 남았다. 더 나쁜 것은 B 형의 BEST 옵션에
   * 상품명 부분이 아예 없어서 **제목 자리에 괄호 문구가 오는 것**이었다(제목 소실).
   * 그 값은 `aria-label` 로도 흘러가 보조기술이 괄호 문구를 상품명처럼 읽는다.
   *
   * → 소괄호는 **전부** 걷어내고, 걷어낸 내용을 잃지 않게 칩으로 되돌린다.
   *   제목이 비면 대괄호 → 메타 → 원문 순으로 폴백한다. 어떤 작명에서도 제목이 비지 않는다.
   *   숫자·문구를 새로 만들지 않는다. 원문 조각을 옮겨 붙일 뿐이다. */
  function parseOptionText(raw) {
    var s = squash(raw);
    var tagM = s.match(/\[([^\]]+)\]/);
    var addM = s.match(/\(\s*\+\s*[\d,]+\s*원\s*\)/);
    var meta = [];

    var nm = s
      .replace(/\(\s*\+\s*[\d,]+\s*원\s*\)/g, ' ')      /* 추가금은 따로 칩으로 나간다 */
      .replace(/\(([^)]*)\)/g, function (_m, inner) {       /* 나머지 소괄호 = 메타 정보 */
        meta.push(inner);
        return ' ';
      })
      .replace(/\[[^\]]*\]/g, ' ')
      .replace(/🔥/g, ' ')
      .replace(/BEST/gi, ' ')
      .replace(/\s+/g, ' ')
      .trim();

    /* 메타를 `|` 로 쪼개 칩 후보로 만든다 */
    var parts = [];
    for (var i = 0; i < meta.length; i++) {
      var seg = meta[i].split('|');
      for (var j = 0; j < seg.length; j++) {
        var v = squash(seg[j]);
        if (v) parts.push(v);
      }
    }

    var bracket = tagM ? squash(tagM[1]) : '';
    var usedBracketAsName = false;
    if (!nm) {                                   /* B 형 BEST 옵션: 제목이 비는 경우 */
      if (bracket) { nm = bracket; usedBracketAsName = true; }
      else if (parts.length) nm = parts.join(' · ');
      else nm = s;
    }

    var tags = [];                               /* 강조 칩 */
    var notes = [];                              /* 보조 칩 */
    if (bracket && !usedBracketAsName) tags.push(bracket);
    for (var k = 0; k < parts.length; k++) {
      if (parts[k].indexOf('무료배송') >= 0) continue;   /* 전용 칩이 따로 있다 */
      if (/\d\s*%\s*할인/.test(parts[k])) tags.push(parts[k]);
      else notes.push(parts[k]);
    }

    return {
      raw: s,
      nm: nm,
      tags: tags,
      notes: notes,
      add: addM ? addM[0] : '',
      free: s.indexOf('무료배송') >= 0,
      best: /BEST/i.test(s) || s.indexOf('🔥') >= 0
    };
  }

  /* ================================================================== *
   *  초기화
   * ================================================================== */
  function ready(fn) {
    if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', fn, false);
    else fn();
  }

  var root, optSel, cards = [], cardWrap = null;
  var pickedHead = null, pickedEmpty = null, tpNode = null, tpAnchor = null;
  var sumItemV = null, sumShipV = null, sumTotV = null;
  var barV = null, barSum = null;
  var pendingSingle = null, pendingTimer = null;
  var modeEffective = (ZG_OPT_MODE === 'single') ? 'single' : 'multi';

  ready(function () { try { init(); } catch (e) { /* 절대 페이지를 죽이지 않는다 */ } });

  function init() {
    /* 편집기에서 스크립트가 두 번 삽입돼도 카드가 두 벌 그려지지 않게 한다 */
    if (window.__ZG_DETAIL_UI__) return;
    window.__ZG_DETAIL_UI__ = 1;

    root = $('.zg-detail');
    if (!root) return;

    unlazyDetailImages();      /* 안전망: 로더가 먼저 돌았어도 회수한다 */
    /* 우리 DOMContentLoaded 리스너는 jQuery 것보다 뒤에 등록되므로, 이 시점이면
     * 스킨의 가드가 이미 지나갔다. 여기서 로더를 되살린다. */
    rearmLazyLoader();
    buildOptionCards();
    watchOptionSource();       /* [9종 복제 대비] 런타임에 옵션이 생기는 상품 대응 */
    buildPickedHead();
    buildSum();
    buildBar();
    bindFold();
    bindChips();
    bindAddProduct();
    watch();
    place();
    refresh();

    if (ZG_OPT_AUTOSELECT) scheduleAutoSelect();
  }

  /* ------------------------------------------------------ K-04 구성 카드 */
  function buildOptionCards() {
    var box = $('.productOption');
    if (!box) return;
    optSel = $('select[name^="option"]', box) || $('select[id^="product_option_id"]', box);
    if (!optSel) return;

    var opts = Array.prototype.filter.call(optSel.options || [], function (o) {
      return o && o.value && o.value !== '*' && o.value !== '**' && !o.disabled;
    });
    if (!opts.length) return;

    cardWrap = el('div', 'zg-opts');
    cardWrap.setAttribute('role', 'group');
    cardWrap.setAttribute('aria-label', '구성 선택');

    var title = el('div', 'zg-opts__title', '몇 박스로 하시겠어요?');

    cards = opts.map(function (o) {
      var p = parseOptionText(o.text);
      var b = el('button', 'zg-opt');
      b.type = 'button';
      /* [검수 근거] `aria-pressed` 는 "다시 누르면 해제된다"는 토글 약속이다.
       * multi 모드는 재탭해도 해제하지 않으므로 그 약속을 지킬 수 없다 → 상태는
       * data 속성(CSS 후크) + 눈에 보이는 텍스트 + aria-label 로만 사실대로 알린다.
       * <button> 의 암묵 role 이 이미 button 이라 role="button" 도 넣지 않는다. */
      b.setAttribute('data-zg-on', '');
      b.setAttribute('data-zg-value', o.value);
      b.setAttribute('data-zg-key', keyOf(o.text));

      b.appendChild(el('span', 'zg-opt__tick'));

      var body = el('span', 'zg-opt__body');
      body.appendChild(el('span', 'zg-opt__nm', p.nm));

      var mt = el('span', 'zg-opt__mt');
      p.tags.forEach(function (v) { mt.appendChild(el('em', 'zg-opt__tag', v)); });
      if (p.free) mt.appendChild(el('em', 'zg-opt__free', '무료배송'));
      p.notes.forEach(function (v) { mt.appendChild(el('em', 'zg-opt__add', v)); });
      if (p.add) mt.appendChild(el('em', 'zg-opt__add', p.add));
      var st = el('em', 'zg-opt__state', '');
      mt.appendChild(st);
      body.appendChild(mt);
      b.appendChild(body);

      if (p.best) b.appendChild(el('span', 'zg-opt__flag', '가장 많이 담아요'));

      b._zgState = st;
      b._zgBest = p.best;
      b._zgName = p.nm;

      /* 접근성 라벨은 카드에 보이는 정보를 그대로 읽힌다 — 이름만 읽고 할인율·추가금이
       * 빠지면 보조기술 사용자만 가격 정보를 못 듣는다. 금액은 계산하지 않고 원문 문자열이다. */
      var lab = [p.nm];
      p.tags.forEach(function (v) { lab.push(v); });
      if (p.free) lab.push('무료배송');
      p.notes.forEach(function (v) { lab.push(v); });
      if (p.add) lab.push('추가 ' + p.add.replace(/[()+\s]/g, ''));
      b._zgLabel = lab.filter(Boolean).join(', ');
      on(b, 'click', function () { pick(b); });
      cardWrap.appendChild(b);
      return b;
    });

    var hint = el('p', 'zg-opt-hint');
    hint.hidden = true;

    /* (검수 설계서에 없던 UI 「옵션을 직접 선택」 버튼은 삭제했다.
     *  설계 문서 어디에도 없었고 조작점 이원화 금지 규칙과도 충돌했다.) */

    box.insertBefore(title, box.firstChild);
    box.insertBefore(cardWrap, title.nextSibling);
    box.insertBefore(hint, cardWrap.nextSibling);

    /* select 는 DOM 에 그대로 두고 시각적으로만 클립한다 (display:none 금지) */
    optSel.classList.add('zg-a11y-hide');

    cardWrap._zgHint = hint;
  }

  /* [9종 복제 대비] `buildOptionCards()` 는 DOMContentLoaded 시점의 select.options 를
   * 한 번만 읽는다. 11번은 option_type="T"(서버 렌더)라 정상이지만, option_type="F"(품목 조합)
   * 상품은 카페24 옵션 스크립트가 나중에 <option> 을 채워 넣어 **카드가 0장**이 된다.
   * → 카드를 못 만들었으면 `.productOption` 을 관찰하다가 옵션이 생기는 순간 한 번 더 짓는다. */
  function watchOptionSource() {
    if (cards.length) return;
    var box = $('.productOption');
    var MO = window.MutationObserver || window.WebKitMutationObserver;
    if (!box || !MO) return;
    var tries = 0;
    var mo = new MO(function () {
      if (cards.length || ++tries > 40) { mo.disconnect(); return; }
      buildOptionCards();
      if (cards.length) { mo.disconnect(); refresh(); }
    });
    mo.observe(box, { childList: true, subtree: true });
    setTimeout(function () { try { mo.disconnect(); } catch (e) {} }, 15000);
  }

  function pick(card) {
    if (!optSel || !card) return;
    var val = card.getAttribute('data-zg-value');
    var key = card.getAttribute('data-zg-key');
    var rows = pickedRows();
    var already = rows.some(function (r) { return rowMatches(r.key, key); });

    /* 담긴 카드를 다시 누르면 그 구성이 빠진다.
     * 담기/빼기가 같은 조작점이라 「담을 땐 카드, 뺄 땐 아래 목록」이라는 이원화가 사라진다.
     * 복수 담기(결정 #1 `multi`)는 그대로다 — 다른 카드는 계속 더 담을 수 있다. */
    if (already) {
      if (unpick(key)) { toast('구성을 뺐어요.'); return; }
      /* 삭제 컨트롤을 못 찾은 상품 — 예전 동작(안내)으로 안전 폴백한다. DOM 을 직접 뜯지 않는다. */
      if (modeEffective === 'multi') toast('이미 담겨 있어요. 빼시려면 아래 목록에서 지워 주세요.');
      return;
    }

    try {
      optSel.value = val;
      optSel.dispatchEvent(new Event('change', { bubbles: true }));
    } catch (e) {
      /* 구형 브라우저 */
      try {
        var ev = document.createEvent('HTMLEvents');
        ev.initEvent('change', true, false);
        optSel.value = val;
        optSel.dispatchEvent(ev);
      } catch (e2) { return; }
    }

    if (modeEffective === 'single') {
      pendingSingle = key;
      clearTimeout(pendingTimer);
      pendingTimer = setTimeout(function () { pendingSingle = null; }, 2500);
    }
  }

  /* 카페24가 그 행에 직접 그려 넣은 **자기 삭제 컨트롤**을 찾는다.
   * 스킨 원문(옵션 스크립트)의 위임 핸들러가 이 요소를 받는다:
   *   `EC$(document).on('click', '#totalProducts a.delete', …)` → 내부 `.option_box_del` 클릭
   *   `EC$(document).on('click', '.option_box_del', …)`          → 실제 삭제 + 데이터 정리
   * 즉 **고객이 직접 누르는 그 버튼**을 누르는 것이지, 1.9MB 옵션 스크립트의 내부 상태를
   * 우리가 뒤에서 고치는 것이 아니다.
   * ⚠ `tr.option_product`(본품)에만 쓴다. 추가상품 행은 `.option_add_box_del` 로 경로가
   *   달라 여기 걸리지 않으며, 카드는 본품 구성만 다룬다(설계 규칙). */
  function delControl(row) {
    return $('a.delete, .option_box_del, a[class*="delete"], a[class*="Del"]', row);
  }

  /* R-2 재탭 해제 — 그 구성의 행을 카페24 삭제 컨트롤로 지운다.
   * 수량이 2 이상이어도 **그 구성 전체**를 뺀다. 근거: 카드는 담기/빼기 스위치이고,
   * 수량 조절은 아래 「선택한 구성」의 스테퍼가 맡는다(조작점 이원화 금지 규칙).
   * 컨트롤을 하나도 못 찾으면 아무것도 하지 않고 false 를 돌려 호출부가 폴백하게 한다. */
  function unpick(key) {
    var hits = pickedRows().filter(function (r) { return rowMatches(r.key, key); });
    if (!hits.length) return false;
    var done = 0;
    hits.forEach(function (r) {
      var del = delControl(r.el);
      if (!del) return;
      try { del.click(); done++; } catch (e) {}
    });
    if (!done) return false;
    schedule();      /* 총액·무료배송·하단바·빈 상태 안내문을 즉시 다시 맞춘다 */
    return true;
  }

  /* 'single' 경로 — 카페24가 새 행을 만든 뒤, 남은 다른 행을 카페24 자신의
   * 삭제 컨트롤로 지운다. 삭제 컨트롤을 못 찾으면 multi 로 안전 폴백한다. */
  function pruneRows(keepKey) {
    var rows = pickedRows();
    if (rows.length <= 1) return true;
    var kept = false, failed = false;
    rows.forEach(function (r) {
      if (!kept && rowMatches(r.key, keepKey)) { kept = true; return; }
      var del = delControl(r.el);
      if (del) { try { del.click(); } catch (e) { failed = true; } }
      else failed = true;
    });
    if (failed) {
      modeEffective = 'multi';
      showHint('구성을 여러 개 담을 수 있어요. 필요 없는 구성은 아래 목록에서 지워 주세요.');
    }
    return !failed;
  }

  function showHint(msg) {
    if (!cardWrap || !cardWrap._zgHint) return;
    var h = cardWrap._zgHint;
    if (msg) { h.textContent = msg; h.hidden = false; }
    else { h.textContent = ''; h.hidden = true; }
  }

  function scheduleAutoSelect() {
    var tries = 0;
    function attempt() {
      tries++;
      if (!cards.length) return;
      if (pickedRows().length > 0) return;
      var target = null;
      for (var i = 0; i < cards.length; i++) { if (cards[i]._zgBest) { target = cards[i]; break; } }
      if (!target) target = cards[1] || cards[0];
      pick(target);
      if (tries < 3) setTimeout(function () { if (pickedRows().length === 0) attempt(); }, 700);
    }
    if (document.readyState === 'complete') setTimeout(attempt, 400);
    else on(window, 'load', function () { setTimeout(attempt, 400); });
  }

  /* --------------------------------------------- K-05 선택 목록 · 위치 이동 */
  function buildPickedHead() {
    tpNode = document.getElementById('totalProducts');
    if (!tpNode || !tpNode.parentNode) return;

    tpAnchor = document.createComment('zg-totalproducts-home');
    tpNode.parentNode.insertBefore(tpAnchor, tpNode);

    pickedHead = el('div', 'zg-picked-head');
    pickedHead.appendChild(el('div', 'zg-picked-head__t', '선택한 구성'));
    pickedEmpty = el('div', 'zg-picked-head__empty', '구성을 선택해 주세요.');
    pickedHead.appendChild(pickedEmpty);
    tpNode.parentNode.insertBefore(pickedHead, tpNode);
  }

  /* ≤767px 에서만 구성카드 바로 아래로 옮긴다. 마크업·id·module 은 건드리지 않고
   * 노드만 이동한다. 되돌리기는 ZG_MOVE_TOTALPRODUCTS = false 한 줄. */
  function place() {
    if (!tpNode || !pickedHead || !tpAnchor) return;
    try {
      var mobile = (window.innerWidth || document.documentElement.clientWidth) <= 767;
      var po = $('.productOption');
      if (ZG_MOVE_TOTALPRODUCTS && mobile && po && po.parentNode) {
        if (pickedHead.previousSibling !== po || tpNode.previousSibling !== pickedHead) {
          po.parentNode.insertBefore(pickedHead, po.nextSibling);
          po.parentNode.insertBefore(tpNode, pickedHead.nextSibling);
        }
      } else if (tpAnchor.parentNode) {
        if (tpNode.nextSibling !== tpAnchor || pickedHead.nextSibling !== tpNode) {
          tpAnchor.parentNode.insertBefore(pickedHead, tpAnchor);
          tpAnchor.parentNode.insertBefore(tpNode, tpAnchor);
        }
      }
    } catch (e) {}
  }

  /* ---------------------------------------------------------- K-08 합계 */
  function sumRow(label, cls) {
    var row = el('div', 'zg-sum__row' + (cls ? ' ' + cls : ''));
    row.appendChild(el('span', null, label));
    var v = el('span', 'zg-sum__v', '—');
    row.appendChild(v);
    return { row: row, v: v };
  }

  function buildSum() {
    var tp = document.getElementById('totalPrice');
    if (!tp || !tp.parentNode) return;
    var box = el('div', 'zg-sum');

    var a = sumRow('상품 금액');
    var b = sumRow('배송비');
    var c = sumRow('총 구매 금액', 'zg-sum__row--tot');
    sumItemV = a.v; sumShipV = b.v; sumTotV = c.v;

    box.appendChild(a.row);
    box.appendChild(b.row);
    box.appendChild(c.row);
    box.appendChild(el('p', 'zg-sum__note', '최종 결제금액은 주문서에서 확인하실 수 있습니다.'));

    tp.parentNode.insertBefore(box, tp.nextSibling);
  }

  /* ------------------------------------------------------ K-12 하단 고정바 */
  function buildBar() {
    var bar = $('.mobile-fix-footer');
    if (!bar) return;
    var wrap = el('div', 'zg-bar__sum');
    wrap.appendChild(el('span', null, '총 구매 금액'));
    barV = el('strong', 'zg-bar__v zg-bar__v--hint', '구성을 선택해 주세요');
    wrap.appendChild(barV);
    barSum = wrap;
    bar.insertBefore(wrap, bar.firstChild);

    /* 품절 대체 슬롯 — 원본 「구매하기」 노드는 삭제하지 않고 CSS 로 감춘다 */
    var so = el('span', 'zg-bar__soldout', 'SOLD OUT');
    so.setAttribute('aria-disabled', 'true');
    bar.appendChild(so);
  }

  /* ------------------------------------------------- K-09 상세 접기·펼치기 */
  function bindFold() {
    var fold = $('.zg-fold');
    var more = $('.zg-more');
    if (!fold || !more) return;
    /* [검수 근거] 펼침 상태를 보조기술에 알린다 */
    if (!fold.id) fold.id = 'zgFold';
    more.setAttribute('aria-expanded', 'false');
    more.setAttribute('aria-controls', fold.id);
    on(more, 'click', function () {
      fold.classList.add('zg-open');
      more.setAttribute('aria-expanded', 'true');
      /* [검수 근거] 이전 판의 scroll/resize 재발사 완화책은 삭제했다 — IO 는 scroll 을
       * 구독하지 않아 무효였다. 이미지 승격은 unlazyDetailImages() 가 담당한다. */
    });
  }

  /* ---------------------------------------------------- K-10 바로가기 칩 */
  function bindChips() {
    $$('[data-zg-tab]').forEach(function (chip) {
      on(chip, 'click', function () {
        var id = chip.getAttribute('data-zg-tab');
        var tab = $('.detail-tab__item[data-link="' + id + '"]');
        if (tab) { try { tab.click(); return; } catch (e) {} }
        var target = document.getElementById(id);
        if (target && target.scrollIntoView) target.scrollIntoView({ behavior: 'smooth', block: 'start' });
      });
    });
  }

  /* -------------------------------------------------- K-06 추가 구성 상품 */
  function bindAddProduct() {
    var set = $('.productSet.additional');
    if (set && set.classList && !set.classList.contains('on')) set.classList.add('on');

    on(document, 'change', function (e) {
      var t = e.target;
      if (!t || t.tagName !== 'SELECT') return;
      var li = t.closest ? t.closest('.productSet .product > li') : null;
      if (!li) return;
      var v = t.value;
      if (v && v !== '*' && v !== '**') li.setAttribute('data-zg-picked', '1');
      else li.removeAttribute('data-zg-picked');
    });
  }

  /* ------------------------------------------------------------- 관측 */
  var rafId = 0;
  function schedule() {
    if (rafId) return;
    rafId = (window.requestAnimationFrame || function (f) { return setTimeout(f, 16); })(function () {
      rafId = 0;
      try { refresh(); } catch (e) {}
    });
  }

  function watch() {
    /* K-08 AC8: 총액 갱신은 MutationObserver 로만 처리한다. setInterval 폴링 없음. */
    var MO = window.MutationObserver || window.WebKitMutationObserver;
    if (!MO) return;

    var tn = totalNode();
    var totalWrap = $('#totalPrice .total') || (tn && tn.parentNode);
    if (totalWrap) {
      new MO(schedule).observe(totalWrap, { childList: true, characterData: true, subtree: true });
    }

    if (tpNode) {
      new MO(function () {
        if (pendingSingle) {
          var k = pendingSingle;
          var has = pickedRows().some(function (r) { return rowMatches(r.key, k); });
          if (has) { pendingSingle = null; clearTimeout(pendingTimer); pruneRows(k); }
        }
        schedule();
      }).observe(tpNode, { childList: true, subtree: true });
    }

    var layer = $('.mobile-layer');
    if (layer) {
      new MO(function () {
        if (!root) return;
        root.classList.toggle('zg-sheet-open', layer.classList.contains('on'));
      }).observe(layer, { attributes: true, attributeFilter: ['class'] });
    }

    var action = $('.productAction');
    if (action) new MO(schedule).observe(action, { attributes: true, subtree: true, attributeFilter: ['class'] });

    var ship = document.getElementById('levelLineActive');
    if (ship) new MO(schedule).observe(ship, { attributes: true, attributeFilter: ['class', 'style'] });

    var rt = null;
    on(window, 'resize', function () {
      clearTimeout(rt);
      rt = setTimeout(function () { place(); schedule(); }, 150);
    });
  }

  /* ------------------------------------------------------------- 렌더 */
  function refresh() {
    if (!root) return;
    var t = totalText();
    var num = totalNum();
    var rows = pickedRows();

    /* [검수 근거] 추가상품 행도 "담긴 것"이다. 여기서 0 이어야만 안내문을 보여준다. */
    root.classList.toggle('zg-picked-0', visibleRows().length === 0);
    /* K-12 AC7 문언대로 `.mobile-fix-footer` 에 `zg-bar--soldout` 을 붙인다
     * (이전 판에서는 `.zg-detail` 에 `zg-soldout` 이라 AC 문언과 어긋나 있었다). */
    var bar = $('.mobile-fix-footer');
    if (bar) bar.classList.toggle('zg-bar--soldout', isSoldout());

    if (sumItemV) sumItemV.textContent = num > 0 ? t : '—';
    if (sumTotV) sumTotV.textContent = num > 0 ? t : '0원';
    if (sumShipV) {
      var free = isFreeShip();
      var dtxt = captureDelivery();      /* 아직 못 읽었으면 이 시점에 한 번 더 시도 */
      sumShipV.textContent = free ? '무료' : (dtxt || '주문서에서 확인');
      sumShipV.classList.toggle('zg-sum__v--free', free);
    }

    if (barV) {
      if (num > 0) {
        barV.textContent = t;
        barV.classList.remove('zg-bar__v--hint');
        if (barSum) barSum.style.display = '';
      } else if (!optSel && !hasRealPrice()) {
        /* 고를 옵션도 없고 판매가도 없는 안내성 상품(34 이벤트종료 · 91/93 결제수단 안내).
         * "구성을 선택해 주세요" 는 고객이 할 수 있는 일이 없는 막다른 말이라 줄 자체를 접는다.
         * 옵션이 없어도 단가가 있는 상품(60/61/62)은 hasRealPrice() 가 true 라 여기로 오지 않는다. */
        if (barSum) barSum.style.display = 'none';
      } else {
        barV.textContent = '구성을 선택해 주세요';
        barV.classList.add('zg-bar__v--hint');
        if (barSum) barSum.style.display = '';
      }
    }

    /* 카드 상태 = tr.option_product 목록과 대조 (select.value 를 보지 않는다) */
    var picked = 0, removable = 0;
    cards.forEach(function (c) {
      var key = c.getAttribute('data-zg-key');
      var hit = null;
      for (var i = 0; i < rows.length; i++) { if (rowMatches(rows[i].key, key)) { hit = rows[i]; break; } }
      c.setAttribute('data-zg-on', hit ? '1' : '');
      /* 라벨의 마지막은 **이 버튼을 누르면 실제로 일어나는 일**이어야 한다 (R-2 로 담긴 카드의
       * 동작이 「담기」에서 「해제」로 바뀌었다). 삭제 컨트롤이 없어 해제가 안 되는 상품에서는
       * 「선택 해제」라고 말하지 않는다 — 되지 않는 일을 안내하지 않는다. */
      var canRemove = !!(hit && delControl(hit.el));
      if (canRemove) removable++;
      c.setAttribute('aria-label',
        (hit ? '선택됨, ' + hit.qty + '개. ' : '') + (c._zgLabel || c._zgName || '') +
        (hit ? (canRemove ? ', 선택 해제' : ', 이미 담김') : ', 장바구니에 담기'));
      if (c._zgState) c._zgState.textContent = hit ? ('선택됨 · ' + hit.qty + '개') : '';
      if (hit) picked++;
    });

    if (modeEffective === 'multi' && picked >= 2) {
      showHint('구성 ' + picked + '개가 담겼어요. ' + (removable === picked
        ? '카드를 다시 누르면 빠집니다.'
        : '필요 없는 구성은 아래에서 지워 주세요.'));
    } else if (modeEffective === 'multi') {
      showHint('');
    }
  }
})();
