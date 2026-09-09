/* ============================================================================
 * 구매 경로 발사 가로채기 (Chromium) — 13종 전수
 *
 * 「보이는가」가 아니라 「눌렀을 때 실제로 무엇이 발사되는가」를 잰다.
 *   window.product_submit            (A·B 그룹의 정상 구매 경로)
 *   window.PRODUCTSUBMIT.sendLoginPage (71 회원전용 상품의 경로 — 검증 전례 0)
 * 둘 다 스텁으로 갈아끼우고 호출 인자를 기록한다. 실제 주문·이동은 만들지 않는다.
 *
 * 추가로 「어디로도 가지 않았음」을 증명하기 위해 다음도 전부 가로챈다:
 *   form submit(선언·프로그램) · window.open · location.assign/replace ·
 *   프레임 내비게이션(Playwright 쪽) · 클릭 중 발생한 window error
 *
 * 화면 상태는 스킨 `checkScroll()` 원문 그대로 계산한다:
 *   top = $('.infoArea').offset().top + $('.infoArea').outerHeight()
 *   scrollTop > top  →  .mobile-layer 에 `.fixed` (시트 경로)
 *   그 이하        →  `.fixed` 없음 (mobileLayerOn 이 인라인 버튼으로 **위임**)
 * ==========================================================================*/
import fs from 'node:fs';
import zlib from 'node:zlib';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

/* ---------------------------------------------------------------- 스텁 PNG */
function crc32(buf) {
  let c, t = [];
  for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  let x = 0xFFFFFFFF;
  for (let i = 0; i < buf.length; i++) x = t[(x ^ buf[i]) & 0xFF] ^ (x >>> 8);
  return (x ^ 0xFFFFFFFF) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
const pngCache = new Map();
function stubPng(w, h) {
  const key = w + 'x' + h;
  if (pngCache.has(key)) return pngCache.get(key);
  const ihdr = Buffer.alloc(13);
  ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4);
  ihdr[8] = 8; ihdr[9] = 2;
  const row = Buffer.alloc(1 + w * 3, 0xDD); row[0] = 0;
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  const png = Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
    chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0)),
  ]);
  pngCache.set(key, png);
  return png;
}
function subst(text, safe) {
  return text.replace(/env\(\s*safe-area-inset-bottom\s*(?:,[^)]*)?\)/g, safe + 'px')
             .replace(/env\(\s*safe-area-inset-top\s*(?:,[^)]*)?\)/g, '0px');
}
function ctypeFor(url, fallback) {
  if (/\.css(\?|$)/.test(url) || /type=css/.test(url)) return 'text/css; charset=utf-8';
  if (/\.js(\?|$)/.test(url) || /type=js/.test(url)) return 'application/javascript; charset=utf-8';
  return fallback || 'application/octet-stream';
}

/* ---------------------------------------------------------------- 변조 단계
 * 음성 대조군·경계 조건을 **라이브에 없는 상태**로 만든다.
 * 제품 파일은 절대 손대지 않는다 — DOM 을 그 자리에서 바꾸거나(여기),
 * 우리 파일의 **사본**을 바꿔 서빙한다(러너 쪽 `pg.ours`).
 * 반환값은 「변조 직전/직후에 zg-bar--dead 가 어떠했는가」다. */
const MUTATE = async (kind) => {
  const q = s => document.querySelector(s);
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const deadNow = () => { const b = q('.mobile-fix-footer');
    return !!(b && b.classList.contains('zg-bar--dead')); };
  const soldNow = () => { const b = q('.mobile-fix-footer');
    return !!(b && b.classList.contains('zg-bar--soldout')); };
  const dispNow = () => { const b = q('.mobile-fix-footer');
    return b ? getComputedStyle(b).display : null; };
  const cart = q('#actionCart');
  const buy = q('.buy-btn-wrap .btnSubmit.gFull');
  const wrap = q('.buy-btn-wrap');
  const soldout = q('.productAction .soldout');
  const out = { kind, before: { dead: deadNow(), soldout: soldNow(), display: dispNow() }, steps: [] };
  const OC = "product_submit(2, '/exec/front/order/basket/', this)";

  if (kind === 'kill-inline') {
    /* 팔 수 있는 상품에서 카페24가 인라인 두 버튼을 죽였다면 — 규칙이 반응해야 한다 */
    [cart, buy].forEach(e => { if (e) { e.setAttribute('onclick', ''); e.classList.add('displaynone'); } });
  } else if (kind === 'fill-late-onclick') {
    /* 「카페24가 나중에 onclick 을 채워 준다」는 가정의 정밀 검증.
     * ① 먼저 displaynone 만 벗긴다 (class 변경 → MutationObserver 가 물어 refresh 가 돈다).
     *    이 시점에도 onclick 이 비어 있으니 dead 는 그대로여야 한다.
     * ② 그 다음 **onclick 만** 채운다 (class 는 안 건드린다).
     *    observer 가 attributeFilter:['class'] 라 refresh 가 안 돌면 dead 가 남는다. */
    [cart, buy].forEach(e => { if (e) e.classList.remove('displaynone'); });
    await wait(800);
    out.steps.push({ at: 'displaynone 제거 후', dead: deadNow(), display: dispNow() });
    [cart, buy].forEach(e => { if (e) e.setAttribute('onclick', OC); });
  } else if (kind === 'fill-with-class-touch') {
    /* 같은 상황에서 class 도 함께 바뀌면(카페24가 보통 그렇게 한다) 회복되는가 */
    [cart, buy].forEach(e => { if (e) { e.setAttribute('onclick', OC); e.classList.remove('displaynone'); } });
  } else if (kind === 'soldout-wrap') {
    /* 카페24 품절 표준 출력 가설 A — 래퍼(.buy-btn-wrap)만 감춘다 */
    if (soldout) soldout.classList.remove('displaynone');
    if (wrap) wrap.classList.add('displaynone');
  } else if (kind === 'soldout-children') {
    /* 가설 B — 자식 두 버튼에 displaynone 을 준다 (34/91/93 과 같은 모양) */
    if (soldout) soldout.classList.remove('displaynone');
    [cart, buy].forEach(e => { if (e) { e.classList.add('displaynone'); e.setAttribute('onclick', ''); } });
  }
  await wait(900);
  out.after = { dead: deadNow(), soldout: soldNow(), display: dispNow(),
                soldoutSlotVisible: (() => { const e = q('.zg-bar__soldout');
                  if (!e) return null; const c = getComputedStyle(e), r = e.getBoundingClientRect();
                  return c.display !== 'none' && r.height > 0; })() };
  return out;
};

/* ================================================== 브라우저 안에서 도는 본체 */
const PROBE = async (ARG) => {
  const STATES = ARG.states, W = ARG.waits;
  const q = s => document.querySelector(s);
  const qa = s => Array.from(document.querySelectorAll(s));
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const vis = e => {
    if (!e) return false;
    const c = getComputedStyle(e), r = e.getBoundingClientRect();
    return c.display !== 'none' && c.visibility !== 'hidden' && c.opacity !== '0'
        && r.width > 0 && r.height > 0;
  };

  /* ---------------- 발사 가로채기 (실제 주문·이동은 만들지 않는다) ---------- */
  const FIRE = [];
  const ERRS = [];
  const rec = (fn, args) => FIRE.push(fn + '(' + Array.prototype.map.call(args, a =>
    (a === undefined ? 'undefined' : (a && typeof a === 'object' ? '[' + (a.tagName || 'obj') + ']' : JSON.stringify(a)))).join(',') + ')');

  const orig = {
    product_submit: typeof window.product_submit,
    PRODUCTSUBMIT: typeof window.PRODUCTSUBMIT,
    sendLoginPage: (window.PRODUCTSUBMIT && typeof window.PRODUCTSUBMIT.sendLoginPage) || 'undefined',
  };
  window.product_submit = function () { rec('product_submit', arguments); return false; };
  if (!window.PRODUCTSUBMIT) window.PRODUCTSUBMIT = {};
  window.PRODUCTSUBMIT.sendLoginPage = function () { rec('sendLoginPage', arguments); return false; };
  window.open = function () { rec('window.open', arguments); return null; };
  try {
    const os_ = HTMLFormElement.prototype.submit;
    HTMLFormElement.prototype.submit = function () { rec('form.submit', [this.getAttribute('action') || '']); };
    HTMLFormElement.prototype.__zgOrigSubmit = os_;
  } catch (e) {}
  try { location.assign = function (u) { rec('location.assign', [u]); }; } catch (e) {}
  try { location.replace = function (u) { rec('location.replace', [u]); }; } catch (e) {}
  document.addEventListener('submit', e => { rec('submit-event', [e.target.getAttribute('action') || '']); e.preventDefault(); }, true);
  window.addEventListener('error', e => { ERRS.push(String(e.message).slice(0, 160)); });

  /* ---------------- 화면 상태 만들기 (스킨 checkScroll 원문 기준) ---------- */
  const boundary = () => {
    const ia = q('.infoArea');
    if (!ia) return null;
    const r = ia.getBoundingClientRect();
    return Math.round(r.top + window.pageYOffset + ia.offsetHeight);
  };
  const isFixed = () => { const ml = q('.mobile-layer');
    return !!(ml && ml.classList.contains('fixed')); };
  const goto = async (kind) => {
    /* ⚠ 경계는 **스크롤하면 움직인다** — 지연 이미지가 자리를 잡으면서 `.infoArea` 높이가 바뀐다.
     * 한 번만 계산해서 그리 가면 `bnd+3` 인데 `.fixed` 가 안 붙는 일이 생긴다
     * (실제로 p11@1023 · p98@390 · p93@390 이 그랬다 — 검사가 의도한 분기에 도달하지 못한 채
     *  그 상태를 baseline 에 굳혀 버렸다). 원하는 분기에 실제로 닿을 때까지 다시 잡는다. */
    let last = null;
    for (let i = 0; i < 4; i++) {
      const H = document.documentElement.scrollHeight, b = boundary();
      let y = 0;
      if (kind === 'top') y = 0;
      else if (kind === 'bnd-3') y = b == null ? 0 : Math.max(0, b - 3);
      else if (kind === 'bnd+3') y = b == null ? 0 : b + 3;
      else if (kind === 'mid') y = Math.round(H * 0.45);
      else if (kind === 'bottom') y = H;
      window.scrollTo(0, y);
      await wait(W.scroll);
      last = { want: y, at: Math.round(window.pageYOffset), boundary: b, tries: i + 1,
               fixed: isFixed() };
      if (kind === 'bnd+3' && !last.fixed) continue;   /* 경계를 못 넘었다 → 다시 잡는다 */
      if (kind === 'bnd-3' && last.fixed) continue;    /* 넘어 버렸다 → 다시 잡는다 */
      break;
    }
    return last;
  };

  const sheetOn = () => !!(q('.mobile-layer') && q('.mobile-layer').classList.contains('on'));
  const closeSheet = async () => {
    try { if (window.mobileLayerOff) window.mobileLayerOff(); } catch (e) {}
    const ml = q('.mobile-layer'), bg = q('.mobile-layer-bg');
    if (ml) { ml.classList.remove('on'); ml.style.bottom = ''; }
    if (bg) bg.classList.remove('on');
    await wait(W.close);
  };

  /* 누를 대상 — 셀렉터를 못 찾으면 그 자체를 기록한다(조용한 통과 금지) */
  const TARGETS = {
    barCart:    '.mobile-fix-footer div.btnNormal',
    barBuy:     '.mobile-fix-footer .jsLayerBtn',
    inlineCart: '#actionCart',
    inlineBuy:  '.buy-btn-wrap .btnSubmit.gFull',
  };

  const box = e => { if (!e) return null; const r = e.getBoundingClientRect();
    return { w: +r.width.toFixed(1), h: +r.height.toFixed(1), top: +r.top.toFixed(1) }; };

  const tap = async (sel, ms) => {
    FIRE.length = 0; ERRS.length = 0;
    const e = q(sel);
    if (!e) return { found: false, fired: [], errs: [] };
    const v = vis(e);
    try { e.click(); } catch (err) { ERRS.push('click threw: ' + err); }
    await wait(ms);
    return { found: true, visible: v, box: box(e), fired: FIRE.slice(), errs: ERRS.slice(),
             sheet: sheetOn() };
  };

  /* ---------------------------------------------------------------- 관측 */
  const out = { orig, states: {}, dom: {} };

  const bar = q('.mobile-fix-footer');
  out.dom = {
    barInDom: qa('.mobile-fix-footer').length,
    reviewHook: qa('.mobile-fix-footer .alpha_review_count').length,
    reviewHookAll: qa('.alpha_review_count').length,
    alphaWidget: qa('[class*="alpha_widget"], [id*="alpha_widget"]').length,
    /* 인라인 구매 컨트롤의 「원본 상태」 — isUnsellable() 이 보는 바로 그 값 */
    inlineCartClass: (q('#actionCart') || {}).className || null,
    inlineCartOnclick: q('#actionCart') ? (q('#actionCart').getAttribute('onclick') || '') : null,
    inlineBuyClass: (q('.buy-btn-wrap .btnSubmit.gFull') || {}).className || null,
    inlineBuyOnclick: q('.buy-btn-wrap .btnSubmit.gFull')
      ? (q('.buy-btn-wrap .btnSubmit.gFull').getAttribute('onclick') || '') : null,
    barCartOnclick: q('.mobile-fix-footer div.btnNormal')
      ? (q('.mobile-fix-footer div.btnNormal').getAttribute('onclick') || '') : null,
    optionSelects: qa('.productOption select[name^="option"]').length,
    optCards: qa('.zg-opt').length,
    /* B 그룹(옵션 없음) — `buildOptionCards()` 가 일찍 반환하면 제목만 남는가 */
    optsWrap: qa('.zg-opts').length,
    optsTitle: qa('.zg-opts__title').length,
    optsTitleText: q('.zg-opts__title') ? q('.zg-opts__title').textContent.trim() : null,
    optsTitleVisible: vis(q('.zg-opts__title')),
    pickedHeadVisible: vis(q('.zg-picked-head')),
    pickedHeadText: q('.zg-picked-head') ? q('.zg-picked-head').textContent.replace(/\s+/g,' ').trim().slice(0,60) : null,
    /* 시트를 여는 트리거가 바 말고 또 있는가 (C 그룹에서 남는 경로가 없어야 한다) */
    layerBtnAll: qa('.jsLayerBtn').length,
    layerBtnVisible: qa('.jsLayerBtn').filter(vis).length,
    layerBtnOutsideBar: qa('.jsLayerBtn').filter(e => !e.closest('.mobile-fix-footer')).length,
    sumRows: qa('.zg-sum__row').length,
    sumVisible: vis(q('.zg-sum')),
    sumTexts: qa('.zg-sum__row').map(r => r.textContent.replace(/\s+/g, ' ').trim()),
    sumShip: (() => { const r = qa('.zg-sum__row')[1]; return r ? r.textContent.replace(/\s+/g, ' ').trim() : null; })(),
    sumTot: (() => { const r = q('.zg-sum__row--tot'); return r ? r.textContent.replace(/\s+/g, ' ').trim() : null; })(),
    barSumDisplay: q('.zg-bar__sum') ? q('.zg-bar__sum').style.display || '(기본)' : null,
    /* 음성 대조군 CSS 사본이 실제로 걸렸는지 알려 주는 표식 (평소엔 빈 문자열) */
    negCtlMarker: bar ? getComputedStyle(bar).getPropertyValue('--zg-negctl') : null,
    barSumText: q('.zg-bar__v') ? q('.zg-bar__v').textContent.trim() : null,
    addProductSet: qa('.productSet.additional').length,
    galleryLi: qa('.thumbnail__list > li').length,
    thumbLi: qa('.listImg li').length,
    prdDetailImgs: qa('#prdDetail img').length,
    soldoutFlag: !!(bar && bar.classList.contains('zg-bar--soldout')),
    deadFlag: !!(bar && bar.classList.contains('zg-bar--dead')),
    barDisplay: bar ? getComputedStyle(bar).display : null,
    /* 화면에서 실제로 「보이면서 눌러서 구매로 이어질 수 있는」 컨트롤 수 */
  };
  /* 좌측 세로 썸네일 R-9 */
  out.thumbs = qa('.listImg li').map(li => {
    const img = li.querySelector('img');
    const lr = li.getBoundingClientRect(), cs = getComputedStyle(li);
    const inner = +(lr.height - parseFloat(cs.borderTopWidth) - parseFloat(cs.borderBottomWidth)).toFixed(2);
    if (!img) return { img: false };
    const ir = img.getBoundingClientRect();
    /* 숨어 있으면 li 높이 0 → inner 가 -2(테두리) 라 overflowPx 가 +2 로 나온다.
     * 그건 잘린 게 아니라 **안 그려진 것**이다 → visible 을 함께 남기고 보이는 것만 판정한다
     * (1023px 에서 좌측 세로 썸네일은 원래 안 보인다 — 실측으로 확인). */
    return { img: true, visible: vis(li) && vis(img),
             liH: +lr.height.toFixed(2), imgH: +ir.height.toFixed(2),
             overflowPx: +(ir.height - inner).toFixed(2),
             objectFit: getComputedStyle(img).objectFit,
             natural: [img.naturalWidth, img.naturalHeight] };
  });

  for (const st of STATES) {
    await closeSheet();
    const pos = await goto(st === 'sheet' ? 'mid' : st);
    const ml = q('.mobile-layer');
    const rec0 = {
      pos, fixed: !!(ml && ml.classList.contains('fixed')),
      barVisible: vis(q('.mobile-fix-footer')),
      barDisplay: q('.mobile-fix-footer') ? getComputedStyle(q('.mobile-fix-footer')).display : null,
      barBox: box(q('.mobile-fix-footer')),
      dead: !!(q('.mobile-fix-footer') && q('.mobile-fix-footer').classList.contains('zg-bar--dead')),
      inlineVisible: vis(q('#fixedActionButton')),
      /* 바 한가운데를 실제로 히트테스트 — 안 보이는 바가 탭을 가로채는가 */
      hitAtBarCenter: (() => {
        const b2 = q('.mobile-fix-footer'); if (!b2) return null;
        const r = b2.getBoundingClientRect();
        if (!(r.width > 0 && r.height > 0)) return '(바 상자 0)';
        const e = document.elementFromPoint(Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2));
        return e ? (e.tagName + '.' + String(e.className || '')).slice(0, 70) : null;
      })(),
      /* 화면 하단 12px 지점(고객 엄지가 닿는 곳)의 최상단 요소 */
      hitAtScreenBottom: (() => {
        const e = document.elementFromPoint(Math.round(window.innerWidth / 2), window.innerHeight - 12);
        return e ? (e.tagName + '.' + String(e.className || '')).slice(0, 70) : null;
      })(),
      visibleBuyControls: [
        ['barCart', TARGETS.barCart], ['barBuy', TARGETS.barBuy],
        ['inlineCart', TARGETS.inlineCart], ['inlineBuy', TARGETS.inlineBuy],
      ].filter(([, s]) => vis(q(s))).map(([n]) => n),
      taps: {},
    };

    if (st === 'sheet') {
      const open = await tap(TARGETS.barBuy, W.sheet);
      rec0.sheetOpenTap = open;
      rec0.sheetOpened = sheetOn();
      rec0.sheetSumVisible = (() => { const t = q('.zg-sum__row--tot'); return vis(t); })();
      rec0.sheetSumOverlap = (() => {
        const t = q('.zg-sum__row--tot'); if (!t) return null;
        const T = t.getBoundingClientRect();
        const ov = e => { if (!e) return 0; const r = e.getBoundingClientRect();
          if (!(r.width > 0 && r.height > 0)) return 0;
          const y = Math.min(T.bottom, r.bottom) - Math.max(T.top, r.top);
          const x = Math.min(T.right, r.right) - Math.max(T.left, r.left);
          return (y > 0 && x > 0) ? +y.toFixed(1) : 0; };
        return { cart: ov(q('#actionCart')), buy: ov(q('.buy-btn-wrap .btnSubmit.gFull')) };
      })();
      rec0.sheetVisibleBuyControls = ['inlineCart', 'inlineBuy']
        .filter(n => vis(q(TARGETS[n])));
      /* 시트 안에서 실제로 눌러 본다 */
      rec0.taps.sheetCart = await tap(TARGETS.inlineCart, W.tap);
      rec0.taps.sheetBuy = await tap(TARGETS.inlineBuy, W.tap);
    } else {
      rec0.taps.barCart = await tap(TARGETS.barCart, W.tap);
      rec0.taps.barBuy = await tap(TARGETS.barBuy, W.sheet);
      rec0.taps.barBuy.sheetOpened = sheetOn();
      await closeSheet();
      await goto(st);
      rec0.taps.inlineCart = await tap(TARGETS.inlineCart, W.tap);
      rec0.taps.inlineBuy = await tap(TARGETS.inlineBuy, W.tap);
    }
    out.states[st] = rec0;
  }
  await closeSheet();
  return out;
};

/* ================================================================== 러너 */
const WAITS = cfg.waits || { scroll: 650, tap: 700, sheet: 1200, close: 250, settle: 1100 };
const CONC = cfg.concurrency || 1;
const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });
const results = [];

/* 작업 목록 — (페이지 × 뷰포트) */
const JOBS = [];
for (const pg of cfg.pages) for (const vp of pg.vps) JOBS.push({ pg, vp });

async function runJob({ pg, vp }) {
  const ctx = await browser.newContext({
    viewport: { width: vp, height: 900 }, deviceScaleFactor: 1,
    userAgent: cfg.ua, isMobile: vp <= 767, hasTouch: vp <= 767,
  });
  const blocked = [];
  await ctx.route('**/*', async (route) => {
    const req = route.request();
    const u = new URL(req.url());
    const key = u.pathname + (u.search || '');
    if (u.host !== 'zengenetics.co.kr') { blocked.push(req.url()); return route.abort(); }
    if (key === pg.docPath) {
      return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8',
                             body: subst(fs.readFileSync(pg.fixture, 'utf8'), 0) });
    }
    const OURS = pg.ours || cfg.ours;
    if (OURS[key]) {
      return route.fulfill({ status: 200, contentType: ctypeFor(key),
                             body: subst(fs.readFileSync(OURS[key], 'utf8'), 0) });
    }
    if (req.resourceType() === 'image' || /\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(key)) {
      const sz = pg.stub || cfg.stub || { w: 640, h: 948 };
      return route.fulfill({ status: 200, contentType: 'image/png', body: stubPng(sz.w, sz.h) });
    }
    const a = pg.assets[key];
    if (a && a.status === 200 && fs.existsSync(a.file)) {
      let body = fs.readFileSync(a.file);
      if (/css/.test(ctypeFor(key, a.ctype))) body = subst(body.toString('utf8'), 0);
      return route.fulfill({ status: 200, contentType: ctypeFor(key, a.ctype), body });
    }
    blocked.push(req.url());
    return route.abort();
  });
  const page = await ctx.newPage();
  const errors = [], navs = [];
  page.on('pageerror', e => errors.push({ msg: String(e.message).slice(0, 200), stack: String(e.stack || '').slice(0, 300) }));
  page.on('framenavigated', f => { if (f === page.mainFrame()) navs.push(f.url()); });
  const rec = { product: pg.name, tag: pg.tag || pg.name, vp, stub: pg.stub || cfg.stub || { w: 640, h: 948 }, ok: true };
  try {
    await page.goto('https://zengenetics.co.kr' + pg.docPath, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(WAITS.settle);
    if (pg.mutate) rec.mutate = await page.evaluate(MUTATE, pg.mutate);
    rec.probe = await page.evaluate(PROBE, { states: pg.states || cfg.states, waits: WAITS });
    rec.errors = errors;
    rec.errorsOurs = errors.filter(e => /\/ds\/(js|css)\//.test(e.stack || '') || /detail-ui\.js/.test(e.stack || ''));
    /* 최초 문서 1건 외의 내비게이션은 「어디론가 갔다」는 뜻이다 */
    rec.navigations = navs.slice(1);
  } catch (e) {
    rec.ok = false; rec.error = String(e.message).slice(0, 400); rec.errors = errors;
  }
  results.push(rec);
  await ctx.close();
}

let next = 0;
await Promise.all(Array.from({ length: Math.min(CONC, JOBS.length) }, async () => {
  while (true) {
    const i = next++;
    if (i >= JOBS.length) return;
    await runJob(JOBS[i]);
  }
}));
await browser.close();
console.log('__JSON__' + JSON.stringify({ results }));
