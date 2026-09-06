/* zengenetics inline edit mode — 이도현 / 웹·모바일 개발팀 / 2026-09-06
   페이지 자체에 인라인 편집 모드를 붙인다.
   - 편집 결과는 항상 데이터(#zg-edits JSON) → 렌더 로 재현된다.
   - 저장은 "원본 스냅샷 문자열의 #zg-edits 블록만 치환" → artifact.publish().
   - claude.use('artifact') 가 null 이면 편집 UI 자체를 만들지 않는다(일반 열람자). */
(function () {
  'use strict';
  if (window.__ZG_EDIT_MODE__) return;
  window.__ZG_EDIT_MODE__ = 1;

  /* ---------- 0. 원본 스냅샷 (우리가 DOM 을 건드리기 전, 단 한 번) ---------- */
  var SNAPSHOT = '';
  try {
    var clone = document.documentElement.cloneNode(true);
    var sc = clone.querySelectorAll('script');
    for (var si = 0; si < sc.length; si++) {
      var s = sc[si];
      /* 원본 스크립트(data-zg-o)와 편집 데이터 블록만 남기고,
         아티팩트 런타임이 주입한 스크립트는 스냅샷에서 제거한다. */
      if (!s.hasAttribute('data-zg-o') && s.id !== 'zg-edits' && s.parentNode) s.parentNode.removeChild(s);
    }
    /* 원본에서 비어 있던 컨테이너(페이지 스크립트가 채운 자리)는 원상 복구한다.
       그러지 않으면 스크립트가 만든 base64 이미지까지 스냅샷에 박혀 용량이 불어난다. */
    var emp = clone.querySelectorAll('[data-zg-e]');
    for (var ei = 0; ei < emp.length; ei++) emp[ei].innerHTML = '';
    /* 원본에 src 가 없던 미디어(스크립트가 base64 를 넣는 자리)도 원상 복구 */
    var sl = clone.querySelectorAll('[data-zg-s]');
    for (var xi = 0; xi < sl.length; xi++) { sl[xi].removeAttribute('src'); sl[xi].removeAttribute('srcset'); }
    SNAPSHOT = '<!doctype html>' + clone.outerHTML;
  } catch (e) { SNAPSHOT = ''; }
  var RE_EDITS = /(<script\b[^>]*\bid="zg-edits"[^>]*>)[\s\S]*?(<\/script\s*>)/i;

  /* ---------- 1. 편집 데이터 ---------- */
  var EDITS = {};   /* id -> {s,t,ls,fs,w,lh} */
  var ORIG = {};    /* id -> 원래 인라인 스타일/문구 */
  try {
    var blk = document.getElementById('zg-edits');
    var arr = blk ? JSON.parse(blk.textContent || '[]') : [];
    for (var i = 0; i < arr.length; i++) if (arr[i] && arr[i].s) EDITS[arr[i].s] = arr[i];
  } catch (e2) { EDITS = {}; }

  function node(id) { return document.querySelector('[data-zg="' + id + '"]'); }

  function kids(el) {
    var br = false, other = false, c = el.children;
    for (var i = 0; i < c.length; i++) { if (c[i].tagName === 'BR') br = true; else other = true; }
    return { br: br, other: other };
  }
  function textOf(el) {
    if (kids(el).other) return null;
    var out = '', n = el.childNodes;
    for (var i = 0; i < n.length; i++) {
      if (n[i].nodeType === 3) out += n[i].nodeValue;
      else if (n[i].nodeType === 1 && n[i].tagName === 'BR') out += '\n';
    }
    return out;
  }
  function setText(el, txt) {
    var k = kids(el);
    if (k.other) return false;
    txt = String(txt);
    if (k.br || txt.indexOf('\n') >= 0) {
      var parts = txt.split('\n');
      el.textContent = '';
      for (var j = 0; j < parts.length; j++) {
        if (j) el.appendChild(document.createElement('br'));
        el.appendChild(document.createTextNode(parts[j]));
      }
    } else { el.textContent = txt; }
    return true;
  }
  function orig(el, id) {
    if (!ORIG[id]) ORIG[id] = {
      ls: el.style.letterSpacing, fs: el.style.fontSize,
      w: el.style.fontWeight, lh: el.style.lineHeight, tx: textOf(el)
    };
    return ORIG[id];
  }

  function applyOne(id) {
    var e = EDITS[id], el = node(id);
    if (!el || !e) return;
    var o = orig(el, id);
    if (e.t != null) setText(el, e.t);
    el.style.letterSpacing = (e.ls != null) ? (e.ls + 'em') : o.ls;
    el.style.fontWeight = (e.w != null) ? String(e.w) : o.w;
    el.style.lineHeight = (e.lh != null) ? String(e.lh) : o.lh;
    el.style.fontSize = o.fs;
    if (e.fs != null && Number(e.fs) !== 1) {
      var base = parseFloat(getComputedStyle(el).fontSize) || 16;
      el.style.fontSize = (base * Number(e.fs)).toFixed(2) + 'px';
    }
  }
  function applyAll() { for (var id in EDITS) applyOne(id); }

  /* ---------- 2. 로드 시 데이터 → 렌더 ---------- */
  applyAll();
  var rzT = 0;
  window.addEventListener('resize', function () {
    clearTimeout(rzT); rzT = setTimeout(applyAll, 260);
  });
  window.addEventListener('load', function () { setTimeout(applyAll, 80); });

  /* ---------- 3. 편집 UI (권한이 있을 때만) ---------- */
  var CSS = [
    '#zg-edit-fab{position:fixed;right:14px;bottom:calc(84px + env(safe-area-inset-bottom,0px));z-index:2147483000;',
    'width:46px;height:46px;padding:0;border:0;border-radius:50%;background:rgba(17,17,17,.38);color:#fff;',
    'font-size:19px;line-height:46px;text-align:center;cursor:pointer;opacity:.5;box-shadow:0 4px 14px rgba(0,0,0,.2);',
    '-webkit-backdrop-filter:blur(6px);backdrop-filter:blur(6px);transition:opacity .18s,background .18s,bottom .22s}',
    '#zg-edit-fab:hover{opacity:1}',
    'html.zg-on #zg-edit-fab{opacity:1;background:#C2410C}',
    'html.zg-panel #zg-edit-fab{bottom:calc(47vh + 10px)}',
    'html.zg-on [data-zg]{outline:1px dashed rgba(194,65,12,.5);outline-offset:2px;cursor:pointer}',
    'html.zg-on [data-zg]:hover{outline:1.5px dashed #C2410C;background:rgba(194,65,12,.07)}',
    'html.zg-on [data-zg].zg-sel{outline:2px solid #C2410C;background:rgba(194,65,12,.12)}',
    '.zg-duck{transform:translateY(180%)!important;transition:transform .22s ease!important;pointer-events:none!important}',
    '#zg-edit-panel{position:fixed;left:0;right:0;bottom:0;z-index:2147483001;box-sizing:border-box;',
    'max-height:45vh;overflow-y:auto;-webkit-overflow-scrolling:touch;background:#fff;color:#141413;',
    'border-top:1px solid #E2E1DA;box-shadow:0 -8px 28px rgba(0,0,0,.16);letter-spacing:0;',
    'font:13px/1.5 -apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;',
    'padding:10px 12px calc(12px + env(safe-area-inset-bottom,0px));transform:translateY(106%);transition:transform .22s ease}',
    '#zg-edit-panel.zg-open{transform:none}',
    '#zg-edit-panel *{box-sizing:border-box;font-family:inherit;letter-spacing:0}',
    '.zg-hd{display:flex;align-items:center;gap:8px;margin-bottom:8px}',
    '.zg-hd b{font-size:12px;font-weight:700;color:#C2410C;letter-spacing:.04em}',
    '.zg-hd span{flex:1;font-size:11.5px;color:#77787C;overflow:hidden;text-overflow:ellipsis;white-space:nowrap}',
    '#zg-edit-text{width:100%;min-height:52px;max-height:120px;resize:vertical;padding:8px;border:1px solid #DDDCD6;',
    'border-radius:7px;font-size:13.5px;line-height:1.5;color:#141413;background:#FCFCFA}',
    '#zg-edit-text[disabled]{background:#F3F2EE;color:#9A9B9F}',
    '.zg-note{font-size:11px;color:#9A6A3A;margin:5px 0 0}',
    '.zg-row{display:flex;align-items:center;gap:8px;margin-top:7px}',
    '.zg-row label{width:52px;flex:none;font-size:11.5px;color:#5F626C}',
    '.zg-row input[type=range]{flex:1;min-width:0;accent-color:#C2410C;height:22px}',
    '.zg-row i{width:52px;flex:none;text-align:right;font-style:normal;font-size:11px;color:#141413;',
    'font-family:ui-monospace,SFMono-Regular,Menlo,monospace}',
    '.zg-act{display:flex;gap:6px;margin-top:10px}',
    '.zg-act button{flex:1;padding:9px 4px;border-radius:8px;border:1px solid #DDDCD6;background:#fff;color:#3B3D45;',
    'font-size:12.5px;font-weight:600;cursor:pointer}',
    '.zg-act button#zg-edit-save{background:#C2410C;border-color:#C2410C;color:#fff;flex:1.3}',
    '.zg-act button[disabled]{opacity:.45;cursor:default}',
    '#zg-edit-msg{margin-top:7px;font-size:11.5px;min-height:15px;color:#5F626C}',
    '#zg-edit-msg.zg-err{color:#B4290C}'
  ].join('');

  var MODE = false, CUR = null, DUCK = [], DIRTY = false, ART = null, UI = null;
  var $ = {};

  function el(t, p, tx) { var n = document.createElement(t); if (p) n.className = p; if (tx != null) n.textContent = tx; return n; }

  function buildUI() {
    var st = el('style'); st.id = 'zg-edit-css'; st.textContent = CSS;
    document.head.appendChild(st);

    var fab = el('button'); fab.id = 'zg-edit-fab'; fab.type = 'button';
    fab.setAttribute('aria-label', '텍스트 편집 모드');
    fab.innerHTML = '&#9998;';
    document.body.appendChild(fab);

    var p = document.createElement('div'); p.id = 'zg-edit-panel';
    p.innerHTML =
      '<div class="zg-hd"><b id="zg-edit-tag">—</b><span id="zg-edit-path"></span>' +
      '<button id="zg-edit-close" type="button" style="border:0;background:none;font-size:16px;color:#8A8B90;cursor:pointer;padding:2px 4px">&#10005;</button></div>' +
      '<textarea id="zg-edit-text" spellcheck="false"></textarea>' +
      '<div class="zg-note" id="zg-edit-note" style="display:none"></div>' +
      '<div class="zg-row"><label>자간</label><input type="range" id="zg-ls" min="-0.1" max="0.3" step="0.005"><i id="zg-ls-v"></i></div>' +
      '<div class="zg-row"><label>크기</label><input type="range" id="zg-fs" min="0.7" max="1.6" step="0.01"><i id="zg-fs-v"></i></div>' +
      '<div class="zg-row"><label>굵기</label><input type="range" id="zg-w" min="300" max="800" step="100"><i id="zg-w-v"></i></div>' +
      '<div class="zg-row"><label>줄간격</label><input type="range" id="zg-lh" min="1" max="2.2" step="0.05"><i id="zg-lh-v"></i></div>' +
      '<div class="zg-act">' +
      '<button id="zg-edit-revert" type="button">되돌리기</button>' +
      '<button id="zg-edit-discard" type="button">전체 취소</button>' +
      '<button id="zg-edit-save" type="button">저장</button></div>' +
      '<div id="zg-edit-msg"></div>';
    document.body.appendChild(p);
    UI = { fab: fab, panel: p, style: st };

    ['zg-edit-tag', 'zg-edit-path', 'zg-edit-text', 'zg-edit-note', 'zg-ls', 'zg-fs', 'zg-w', 'zg-lh',
      'zg-ls-v', 'zg-fs-v', 'zg-w-v', 'zg-lh-v', 'zg-edit-msg'].forEach(function (k) { $[k] = document.getElementById(k); });

    fab.addEventListener('click', function (ev) { ev.preventDefault(); ev.stopPropagation(); toggleMode(!MODE); });
    document.getElementById('zg-edit-close').addEventListener('click', function () { closePanel(); });
    document.getElementById('zg-edit-revert').addEventListener('click', revert);
    document.getElementById('zg-edit-discard').addEventListener('click', discardAll);
    document.getElementById('zg-edit-save').addEventListener('click', save);
    $['zg-edit-text'].addEventListener('input', onText);
    bindRange('zg-ls', 'ls'); bindRange('zg-fs', 'fs'); bindRange('zg-w', 'w'); bindRange('zg-lh', 'lh');
    document.addEventListener('click', onPick, true);
    document.addEventListener('keydown', function (e) { if (e.key === 'Escape' && MODE) { if (CUR) closePanel(); else toggleMode(false); } });
  }

  function hideUI() {
    toggleMode(false);
    if (UI) { [UI.fab, UI.panel, UI.style].forEach(function (n) { if (n && n.parentNode) n.parentNode.removeChild(n); }); UI = null; }
  }

  function toggleMode(on) {
    MODE = !!on;
    document.documentElement.classList.toggle('zg-on', MODE);
    if (!MODE) closePanel();
  }

  function duck(on) {
    if (on) {
      if (DUCK.length) { DUCK.forEach(function (n) { n.classList.add('zg-duck'); }); return; }
      var all = document.body.getElementsByTagName('*'), h = window.innerHeight;
      for (var i = 0; i < all.length; i++) {
        var n = all[i];
        if (n.id && n.id.indexOf('zg-edit') === 0) continue;
        var cs;
        try { cs = getComputedStyle(n); } catch (e) { continue; }
        if (cs.position !== 'fixed') continue;
        var r = n.getBoundingClientRect();
        if (r.width < 40 || r.height < 12) continue;
        if (r.bottom > h - 160 && r.top > h * 0.35) { n.classList.add('zg-duck'); DUCK.push(n); }
      }
    } else { DUCK.forEach(function (n) { n.classList.remove('zg-duck'); }); }
  }

  function openPanel() {
    UI.panel.classList.add('zg-open');
    document.documentElement.classList.add('zg-panel');
    duck(true);
  }
  function closePanel() {
    if (!UI) return;
    UI.panel.classList.remove('zg-open');
    document.documentElement.classList.remove('zg-panel');
    duck(false);
    if (CUR) { var n = node(CUR); if (n) n.classList.remove('zg-sel'); }
    CUR = null;
  }

  function onPick(ev) {
    if (!MODE || !UI) return;
    var t = ev.target;
    if (!t || !t.closest) return;
    if (t.closest('#zg-edit-panel') || t.closest('#zg-edit-fab')) return;
    ev.preventDefault(); ev.stopPropagation();
    var target = t.closest('[data-zg]');
    if (target) select(target);
  }

  function num(v, d) { var x = parseFloat(v); return isFinite(x) ? x : d; }

  function select(node_) {
    if (CUR) { var pv = node(CUR); if (pv) pv.classList.remove('zg-sel'); }
    CUR = node_.getAttribute('data-zg');
    node_.classList.add('zg-sel');
    orig(node_, CUR);
    var e = EDITS[CUR] || {};
    var cs = getComputedStyle(node_);
    var fsPx = num(cs.fontSize, 16) || 16;

    $['zg-edit-tag'].textContent = node_.tagName.toLowerCase() + ' · ' + CUR;
    var txt = textOf(node_);
    $['zg-edit-path'].textContent = (txt || '').replace(/\s+/g, ' ').trim().slice(0, 28);
    if (txt === null) {
      $['zg-edit-text'].value = (node_.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 200);
      $['zg-edit-text'].disabled = true;
      $['zg-edit-note'].style.display = '';
      $['zg-edit-note'].textContent = '이 요소는 하위 태그를 포함해 문구는 수정할 수 없습니다 (스타일만 조절).';
    } else {
      $['zg-edit-text'].value = txt;
      $['zg-edit-text'].disabled = false;
      $['zg-edit-note'].style.display = 'none';
    }

    var ls = (e.ls != null) ? Number(e.ls) : (cs.letterSpacing === 'normal' ? 0 : num(cs.letterSpacing, 0) / fsPx);
    var fs = (e.fs != null) ? Number(e.fs) : 1;
    var w = (e.w != null) ? Number(e.w) : Math.min(800, Math.max(300, Math.round(num(cs.fontWeight, 400) / 100) * 100));
    var lhRaw = (cs.lineHeight === 'normal') ? fsPx * 1.5 : num(cs.lineHeight, fsPx * 1.5);
    var lh = (e.lh != null) ? Number(e.lh) : lhRaw / fsPx;
    setRange('zg-ls', ls); setRange('zg-fs', fs); setRange('zg-w', w); setRange('zg-lh', lh);
    msg('');
    openPanel();
    try { node_.scrollIntoView({ block: 'center', behavior: 'smooth' }); } catch (e3) { }
  }

  function fmt(k, v) {
    if (k === 'zg-ls') return (v > 0 ? '+' : '') + Number(v).toFixed(3) + 'em';
    if (k === 'zg-fs') return '×' + Number(v).toFixed(2);
    if (k === 'zg-w') return String(Math.round(v));
    return Number(v).toFixed(2);
  }
  function setRange(k, v) {
    var lo = num($[k].min, 0), hi = num($[k].max, 1);
    v = Math.min(hi, Math.max(lo, Number(v) || (k === 'zg-fs' ? 1 : 0)));
    $[k].value = v; $[k + '-v'].textContent = fmt(k, v);
  }
  function bindRange(k, prop) {
    $[k].addEventListener('input', function () {
      if (!CUR) return;
      var v = Number($[k].value);
      $[k + '-v'].textContent = fmt(k, v);
      var e = EDITS[CUR] || (EDITS[CUR] = { s: CUR });
      e[prop] = (prop === 'w') ? Math.round(v) : Number(v.toFixed(3));
      DIRTY = true;
      applyOne(CUR);
      msg('');
    });
  }
  function onText() {
    if (!CUR) return;
    var e = EDITS[CUR] || (EDITS[CUR] = { s: CUR });
    e.t = $['zg-edit-text'].value;
    DIRTY = true;
    var n = node(CUR); if (n) setText(n, e.t);
    msg('');
  }

  function revert() {
    if (!CUR) return;
    var n = node(CUR), o = ORIG[CUR];
    if (n && o) {
      if (o.tx != null) setText(n, o.tx);
      n.style.letterSpacing = o.ls; n.style.fontSize = o.fs;
      n.style.fontWeight = o.w; n.style.lineHeight = o.lh;
    }
    delete EDITS[CUR];
    DIRTY = true;
    if (n) select(n);
    msg('이 요소를 원래대로 되돌렸습니다. (저장해야 반영됩니다)');
  }

  function discardAll() {
    if (DIRTY && !window.confirm('저장하지 않은 편집을 모두 버리고 마지막 저장 상태로 되돌립니다. 계속할까요?')) return;
    location.reload();
  }

  function msg(t, err) {
    if (!$['zg-edit-msg']) return;
    $['zg-edit-msg'].textContent = t || '';
    $['zg-edit-msg'].className = err ? 'zg-err' : '';
  }

  function save() {
    if (!ART || !SNAPSHOT) { msg('저장할 수 없는 환경입니다.', 1); return; }
    var out = [];
    for (var id in EDITS) {
      var e = EDITS[id];
      if (!e) continue;
      if (e.t == null && e.ls == null && e.fs == null && e.w == null && e.lh == null) continue;
      e.s = id; out.push(e);
    }
    var json = JSON.stringify(out).replace(/</g, '\\u003c');
    if (!RE_EDITS.test(SNAPSHOT)) { msg('저장 지점(zg-edits)을 찾지 못했습니다.', 1); return; }
    var html = SNAPSHOT.replace(RE_EDITS, function (m, a, b) { return a + json + b; });
    var btn = document.getElementById('zg-edit-save');
    btn.disabled = true; msg('저장하는 중…');
    ART.publish(html).then(function () {
      DIRTY = false; btn.disabled = false;
      msg('저장했습니다. 이 주소를 여는 모두에게 반영됩니다.');
    }).catch(function (err) {
      btn.disabled = false;
      var c = (err && err.code) || '';
      if (c === 'conflict') { msg('다른 화면에서 먼저 저장되었습니다. 새로고침 후 다시 시도해 주세요', 1); return; }
      if (c === 'not_granted' || c === 'not_writer' || c === 'not_declared' ||
        c === 'consent_required' || c === 'capability_disabled' || c === 'capability_removed') { hideUI(); return; }
      if (c === 'too_large') { msg('페이지 용량이 한도를 넘어 저장할 수 없습니다.', 1); return; }
      if (c === 'rate_limited') { msg('저장이 너무 잦습니다. 잠시 후 다시 시도해 주세요.', 1); return; }
      msg('저장에 실패했습니다' + (c ? ' (' + c + ')' : '') + '. 잠시 후 다시 시도해 주세요.', 1);
    });
  }

  /* ---------- 4. 권한 확인 ---------- */
  if (!window.claude || typeof window.claude.use !== 'function') return;   /* 편집 UI 없음 */
  try {
    window.claude.use('artifact').then(function (a) {
      if (!a || typeof a.publish !== 'function') return;                    /* 열람 전용 */
      ART = a;
      if (document.body) buildUI();
      else window.addEventListener('DOMContentLoaded', buildUI);
    }, function () { });
  } catch (e4) { }
})();
