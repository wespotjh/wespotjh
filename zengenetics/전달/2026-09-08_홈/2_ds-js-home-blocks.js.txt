/* ==========================================================================
   젠제네틱스 홈 — 제품 블록 스크롤 스크럽 + 공용 런타임
   ZG_VER 스탬프 없음(계측은 ds/js/zg-ga4.js 소관).

   이 파일이 소유하는 것
     1) window.ZG_HOME 네임스페이스 — 히어로(home-hero.js)와 공유한다
     2) 상태 클래스 감시자 — body.eMobilePopup / html.scroll-disabled 가 붙으면
        문서가 흐름에서 떨어져 sticky 가 죽는다. 붙는 동안 렌더를 동결하고,
        떨어지면 스크롤 위치를 되돌린 뒤 강제 재계산한다. 3초 안전장치 포함.
     3) 제품 3블록의 프레임 이미지 부착과 스크롤 스크럽

   지키는 규칙
     - document.body 에 클래스를 붙이지 않는다. 상태는 .zg-home 에만 붙인다.
       (메인 인라인 스크립트가 body 의 class 속성을 통째로 지우는 경로가 있다)
     - window.onload 를 쓰지 않는다 (메인 인라인 스크립트가 통째로 할당한다)
     - asyncImage / ec-data-src / scroll-effect 클래스를 쓰지 않는다
       (스킨·플랫폼 지연로더가 그 이름을 가로챈다)
     - 스크롤 리스너는 passive + requestAnimationFrame 1틱
     - 진행률은 캐시하지 않고 매번 rect 로 다시 잰다
   ========================================================================== */
(function () {
  "use strict";

  var ZG = window.ZG_HOME = window.ZG_HOME || {};
  var IMG = window.ZG_HOME_IMG || null;

  ZG.frozen = false;
  ZG._subs = [];
  ZG.onThaw = function (fn) { if (typeof fn === 'function') ZG._subs.push(fn); };
  ZG.src = function (name) { return IMG ? (IMG.base + name) : ''; };

  function clamp01(v) { return v < 0 ? 0 : (v > 1 ? 1 : v); }

  /* ---------------------------------------------------------------- 조건 ④
     상태 클래스에 의한 sticky 정지 대응.
     붙이는 코드는 플랫폼 쪽에 있고 떼는 코드는 문자열로 확인되지 않는다.
     그래서 "안 떨어질 수도 있다"를 전제로 3초 안전장치를 둔다.               */
  var WATCH = /(^|\s)(eMobilePopup|scroll-disabled)(\s|$)/;
  var frozenY = 0, restorePending = false, safety = 0;
  /* 동결 직전의 스크롤 위치. MutationObserver 가 깨어난 시점에는
     body 가 이미 position:fixed 라 pageYOffset 이 0 으로 무너져 있다.
     그래서 평소 스크롤에서 미리 받아 둔다. */
  var lastY = 0;

  function watched() {
    var b = document.body, h = document.documentElement;
    return (!!b && WATCH.test(b.className || '')) || (!!h && WATCH.test(h.className || ''));
  }

  function freeze() {
    if (ZG.frozen) return;
    ZG.frozen = true;
    frozenY = lastY;
    restorePending = true;
    if (safety) clearTimeout(safety);
    /* 떼는 코드가 없어 영영 안 풀리는 경우 — 화면을 멈춘 채로 두지 않는다.
       위치 복원은 하지 않고 렌더만 재개한다. */
    safety = setTimeout(function () {
      safety = 0;
      if (!ZG.frozen) return;
      ZG.frozen = false;
      restorePending = false;
      thaw(false);
    }, 3000);
  }

  function thaw(restore) {
    if (restore && restorePending) {
      restorePending = false;
      try { window.scrollTo(0, frozenY); } catch (e) { /* 위치 복원 실패는 치명적이지 않다 */ }
    }
    for (var i = 0; i < B.length; i++) B[i].lastP = -1;
    for (var j = 0; j < ZG._subs.length; j++) {
      try { ZG._subs[j](); } catch (e) { /* 구독자 하나가 실패해도 나머지는 돈다 */ }
    }
    onScroll();
  }

  function checkState() {
    if (watched()) { freeze(); return; }
    if (!ZG.frozen) return;
    ZG.frozen = false;
    if (safety) { clearTimeout(safety); safety = 0; }
    thaw(true);
  }

  function startWatch() {
    if (typeof MutationObserver !== 'function') return;
    var opt = { attributes: true, attributeFilter: ['class'] };
    var mo = new MutationObserver(checkState);
    if (document.body) mo.observe(document.body, opt);
    mo.observe(document.documentElement, opt);
  }

  /* ------------------------------------------------------------- 제품 블록 */
  var ORDER = ['pot', 'mag', 'vitb'];
  var FRAMES = 24;

  /* 스크롤 진행률 → 캡션 전환점. 마크업의 data-cap0~3 문구와 짝이다. */
  var CAP_AT = [0, 0.28, 0.60, 0.86];

  var B = [];
  var ticking = false;

  /* 프레임 접근을 이 함수 하나로 격리한다 — 낱장 <img> 를 다른 방식(스프라이트 등)으로
     바꾸더라도 renderBlock 은 손대지 않는다. */
  function frameEl(b, i) { return b.imgs[i]; }

  function buildFrames(b) {
    if (!IMG || !IMG.diss || !IMG.diss[b.key]) return;
    var list = IMG.diss[b.key], n = Math.min(FRAMES, list.length), i, im;
    for (i = 0; i < n; i++) {
      im = document.createElement('img');
      im.className = 'zg-fr' + (i === 0 ? ' zg-on' : '');
      im.alt = '';
      im.decoding = 'async';
      im.loading = i < 3 ? 'eager' : 'lazy';
      im.src = IMG.base + list[i];
      b.plate.appendChild(im);
      b.imgs.push(im);
    }
  }

  function renderBlock(b) {
    var r = b.track.getBoundingClientRect(), vh = window.innerHeight;
    if (r.bottom < -vh || r.top > vh * 2) return;
    var total = b.track.offsetHeight - vh;
    var p = total > 0 ? clamp01(-r.top / total) : 0;
    if (Math.abs(p - b.lastP) < 0.0015) return;
    b.lastP = p;

    if (b.imgs.length) {
      var idx = Math.min(b.imgs.length - 1, Math.floor(p * b.imgs.length));
      if (idx !== b.last) {
        if (b.last >= 0 && frameEl(b, b.last)) frameEl(b, b.last).classList.remove('zg-on');
        if (frameEl(b, idx)) frameEl(b, idx).classList.add('zg-on');
        b.last = idx;
      }
    }
    if (b.hint) b.hint.style.opacity = (1 - clamp01(p * 8)).toFixed(2);

    var np = clamp01((p - 0.62) / 0.34), e = 1 - Math.pow(1 - np, 3);
    if (b.band) {
      b.band.style.opacity = np.toFixed(3);
      b.band.style.transform = 'translateY(' + (12 * (1 - np)).toFixed(1) + 'px)';
    }
    if (b.v0) b.v0.textContent = Math.round(b.n0 * e);
    if (b.v1) b.v1.textContent = Math.round(b.n1 * e);

    var ci = 0;
    for (var i = 0; i < CAP_AT.length; i++) if (p >= CAP_AT[i]) ci = i;
    if (ci !== b.lastCap && b.caps[ci] != null) {
      b.cap.textContent = b.caps[ci];
      b.lastCap = ci;
    }
  }

  function update() {
    ticking = false;
    if (ZG.frozen) return;
    for (var i = 0; i < B.length; i++) renderBlock(B[i]);
  }

  function onScroll() {
    if (!ZG.frozen) lastY = window.pageYOffset || 0;
    if (ticking) return;
    ticking = true;
    requestAnimationFrame(update);
  }

  function collect() {
    var root = document.querySelector('.zg-home');
    if (!root) return;
    for (var i = 0; i < ORDER.length; i++) {
      var key = ORDER[i];
      var el = root.querySelector('.zg-pblock[data-zg-p="' + key + '"]');
      if (!el) continue;
      var track = el.querySelector('.zg-track');
      var plate = el.querySelector('.zg-plate');
      var cap = el.querySelector('.zg-bcap .zg-t');
      if (!track || !plate || !cap) continue;

      var caps = [];
      for (var c = 0; c < CAP_AT.length; c++) {
        caps.push(cap.getAttribute('data-zg-cap' + c));
      }
      var b = {
        key: key, el: el, track: track, plate: plate, cap: cap, imgs: [],
        band: el.querySelector('.zg-band'),
        hint: el.querySelector('.zg-hint'),
        v0: el.querySelector('.zg-v0'),
        v1: el.querySelector('.zg-v1'),
        n0: parseFloat(el.getAttribute('data-zg-n0')) || 0,
        n1: parseFloat(el.getAttribute('data-zg-n1')) || 0,
        caps: caps, last: -1, lastCap: -1, lastP: -1
      };
      buildFrames(b);
      B.push(b);
    }
  }

  function boot() {
    collect();
    startWatch();
    checkState();
    lastY = window.pageYOffset || 0;
    window.addEventListener('scroll', onScroll, { passive: true });
    window.addEventListener('resize', function () {
      for (var i = 0; i < B.length; i++) B[i].lastP = -1;
      onScroll();
    }, { passive: true });
    /* 스킨이 스크롤 중 #wrap 에 여백을 더해 문서가 통째로 내려가는 구간이 있다.
       진행률을 캐시하지 않으므로 다음 스크롤에서 스스로 맞춰지지만,
       그 순간에도 한 번은 다시 재도록 방향 전환 시 무효화한다. */
    update();
  }

  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', boot);
  } else {
    boot();
  }
})();
