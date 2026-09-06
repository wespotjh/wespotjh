/* ============================================================
   젠제네틱스 — 장바구니 무료배송 진행바
   ------------------------------------------------------------
   B안 1단계. HTML 템플릿은 건드리지 않는다.
   basket.html 에 추가한 것은 <!--@js(/ds/js/basket.js)--> 한 줄뿐이고,
   진행바 DOM 은 이 스크립트가 합계 카드 위에 끼워 넣는다.

   원칙 (CLAUDE.md 영구규칙 11)
     - 기준 금액(무료배송 조건)을 코드에 쓰지 않는다.
       화면에 이미 있는 카페24 문구에서 읽는다. 못 읽으면 아무것도 그리지 않는다.
     - 합계 금액도 카페24가 그린 값을 그대로 읽는다.
   ============================================================ */
(function () {
    'use strict';

    var BAR_ID = 'zgFreeShip';

    function won(n) { return n.toLocaleString('ko-KR') + '원'; }

    /* 화면 문구에서 무료배송 기준 금액을 찾는다.
       "50,000원 이상 무료" / "5만원 이상 무료" 둘 다 받는다. */
    function findThreshold(scope) {
        var t = scope.innerText || '';
        var m = t.match(/([0-9][0-9,]*)\s*만\s*원?\s*이상/);
        if (m) return parseInt(m[1].replace(/,/g, ''), 10) * 10000;
        m = t.match(/([0-9][0-9,]{3,})\s*원\s*이상/);
        if (m) return parseInt(m[1].replace(/,/g, ''), 10);
        return 0;
    }

    /* 총 상품금액 — 합계 카드의 첫 항목. 배송비를 뺀 금액으로 판단한다. */
    function readGoods(scope) {
        var el = scope.querySelector('.totalSummary__item .heading .data strong');
        if (!el) return -1;
        var n = (el.textContent || '').replace(/[^0-9]/g, '');
        return n === '' ? -1 : parseInt(n, 10);
    }

    function build(scope) {
        var box = document.createElement('div');
        box.id = BAR_ID;
        box.className = 'zg-freeship';
        box.innerHTML =
            '<div class="zg-freeship__t"></div>' +
            '<div class="zg-freeship__bar"><i></i></div>';
        var summary = scope.querySelector('.totalSummary');
        if (summary && summary.parentNode) summary.parentNode.insertBefore(box, summary);
        return box;
    }

    function paint(box, goods, limit) {
        var t = box.querySelector('.zg-freeship__t');
        var i = box.querySelector('.zg-freeship__bar i');
        if (goods >= limit) {
            box.classList.add('is-done');
            t.textContent = won(limit) + '을 넘겨서 배송비가 없습니다.';
            i.style.width = '100%';
        } else {
            box.classList.remove('is-done');
            t.innerHTML = '<em>' + won(limit - goods) + '</em> 더 담으시면 배송비가 없습니다.';
            i.style.width = Math.max(2, Math.min(100, goods / limit * 100)).toFixed(1) + '%';
        }
    }

    function init() {
        var scope = document.querySelector('.cart-container');
        if (!scope) return;

        var limit = findThreshold(scope);
        if (!limit) return;               /* 기준 금액을 못 읽으면 그리지 않는다 */

        var goods = readGoods(scope);
        if (goods < 0) return;            /* 합계를 못 읽으면 그리지 않는다 */

        var box = document.getElementById(BAR_ID) || build(scope);
        paint(box, goods, limit);

        /* 수량 변경·선택 삭제로 카페24가 합계를 다시 그리면 따라 갱신한다.
           (상품상세의 무료배송 안내가 쓰는 것과 같은 방식) */
        var target = scope.querySelector('.totalSummary__item .heading .data');
        if (target && window.MutationObserver) {
            new MutationObserver(function () {
                var g = readGoods(scope);
                if (g >= 0) paint(box, g, limit);
            }).observe(target, { childList: true, subtree: true, characterData: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
