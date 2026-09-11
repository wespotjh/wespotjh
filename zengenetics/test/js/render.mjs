/* ============================================================================
 * 실렌더 하네스 (Chromium) — 신아린 QA모바일_칼륨_4차 §1·§2·§5 방법의 자동화판.
 *
 *   라이브 HTML(curl 캐시) + 스킨 CSS/JS 를 **번들 순서 그대로** 인라인 →
 *   env(safe-area-inset-bottom) 토큰 치환 → 실제 렌더 후 측정.
 *
 * 교차출처는 전부 차단한다(웹폰트 0벌 상태). 동일출처 자산은 캐시에서 채운다.
 * 이미지는 지정 크기의 스텁 PNG 로 채운다 — 원본 폭 가정을 바꿔 가며 확대 배율을
 * 재현할 수 있어야 하기 때문이다(§4 반례 재현).
 * ==========================================================================*/
import fs from 'node:fs';
import path from 'node:path';
import zlib from 'node:zlib';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const cfgPath = process.argv[2];
const cfg = JSON.parse(fs.readFileSync(cfgPath, 'utf8'));

/* ------------------------------------------------------------- 스텁 PNG */
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
  ihdr[8] = 8; ihdr[9] = 2; /* 8bit truecolor */
  const row = Buffer.alloc(1 + w * 3, 0xDD); row[0] = 0;
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  const png = Buffer.concat([
    Buffer.from([0x89, 0x50, 0x4E, 0x47, 0x0D, 0x0A, 0x1A, 0x0A]),
    chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0)),
  ]);
  pngCache.set(key, png);
  return png;
}

/* --------------------------------------------------------------- 토큰 치환 */
function subst(text, safe) {
  return text.replace(/env\(\s*safe-area-inset-bottom\s*(?:,[^)]*)?\)/g, safe + 'px')
             .replace(/env\(\s*safe-area-inset-top\s*(?:,[^)]*)?\)/g, '0px');
}

/* ------------------------------------------------------------------ 본체 */
const assets = cfg.assets;              /* url -> {file, ctype, status} */
const ours = cfg.ours;                  /* url -> 로컬 파일 경로 */
const results = [];

function ctypeFor(url, fallback) {
  if (/\.css(\?|$)/.test(url) || /type=css/.test(url)) return 'text/css; charset=utf-8';
  if (/\.js(\?|$)/.test(url) || /type=js/.test(url)) return 'application/javascript; charset=utf-8';
  return fallback || 'application/octet-stream';
}

async function makeContext(browser, vp, safe, stub) {
  const ctx = await browser.newContext({
    viewport: { width: vp, height: 900 },
    deviceScaleFactor: 1,
    userAgent: cfg.ua,
    isMobile: vp <= 767,
    hasTouch: vp <= 767,
  });
  const blocked = [];
  await ctx.route('**/*', async (route) => {
    const req = route.request();
    const u = new URL(req.url());
    const key = u.pathname + (u.search || '');
    if (u.host !== 'zengenetics.co.kr') { blocked.push(req.url()); return route.abort(); }
    if (key === cfg.docPath) {
      return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8',
                             body: subst(fs.readFileSync(cfg.fixture, 'utf8'), safe) });
    }
    if (ours[key]) {
      const body = subst(fs.readFileSync(ours[key], 'utf8'), safe);
      return route.fulfill({ status: 200, contentType: ctypeFor(key), body });
    }
    if (req.resourceType() === 'image' || /\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(key)) {
      const sz = stub || cfg.stub || { w: 640, h: 948 };
      return route.fulfill({ status: 200, contentType: 'image/png', body: stubPng(sz.w, sz.h) });
    }
    const a = assets[key];
    if (a && a.status === 200 && fs.existsSync(a.file)) {
      let body = fs.readFileSync(a.file);
      if (/css/.test(ctypeFor(key, a.ctype))) body = subst(body.toString('utf8'), safe);
      return route.fulfill({ status: 200, contentType: ctypeFor(key, a.ctype), body });
    }
    blocked.push(req.url());
    return route.abort();
  });
  return { ctx, blocked };
}

const MEASURE = () => {
  const out = {};
  const q = (s) => document.querySelector(s);
  const qa = (s) => Array.from(document.querySelectorAll(s));
  const vis = (el) => { if (!el) return false; const c = getComputedStyle(el);
    return c.display !== 'none' && c.visibility !== 'hidden'; };

  out.delta = window.__ZG_TEST_DELTA__ || null;   /* 템플릿 델타가 실제로 적용됐는가 */
  out.viewport = { w: window.innerWidth, h: window.innerHeight };
  out.overflow = { scrollWidth: document.documentElement.scrollWidth,
                   clientWidth: document.documentElement.clientWidth };

  /* --- 델타 적용 확인 (거짓 통과 방지) --- */
  out.landmarks = {
    zgDetail: qa('.zg-detail').length,
    detailContainer: qa('.detail-container').length,
    prdDetail: qa('#prdDetail').length,
    optionSelect: qa('.productOption select[name^="option"]').length,
    zgOpts: qa('.zg-opt').length,
    zgBar: qa('.mobile-fix-footer').length,
    zgSum: qa('.zg-sum__row').length,
    galleryLi: qa('.thumbnail__list > li').length,
    foldImgs: qa('#prdDetail .zg-fold img').length,
    prdDetailImgs: qa('#prdDetail img').length,
  };

  /* --- R-9 좌측 세로 썸네일 (≥1024px 에서만 보인다) ---------------------
   * 스킨은 `li{height:90px;overflow:hidden}` + `img{max-width:100%;height:auto}` 라
   * **세로가 긴 원본이면 아래가 잘린다.** 하네스 기본 스텁이 640×948(세로 길다)이라
   * 규칙이 없으면 여기서 반드시 잘린다 — 즉 이 검사는 자기 음성 대조군을 내장한다. */
  out.thumbs = qa('.listImg li').map((li) => {
    const img = li.querySelector('img');
    const lr = li.getBoundingClientRect();
    const cs = getComputedStyle(li);
    const pad = parseFloat(cs.borderTopWidth) + parseFloat(cs.borderBottomWidth);
    const inner = +(lr.height - pad).toFixed(2);
    if (!img) return { img: false };
    const ir = img.getBoundingClientRect();
    const ics = getComputedStyle(img);
    return {
      img: true,
      liH: +lr.height.toFixed(2), liInnerH: inner,
      imgH: +ir.height.toFixed(2), imgW: +ir.width.toFixed(2),
      overflowPx: +(ir.height - inner).toFixed(2),   /* >0 이면 잘린다 */
      objectFit: ics.objectFit,
      natural: [img.naturalWidth, img.naturalHeight],
    };
  });

  /* --- 하단바 --- */
  const bar = q('.mobile-fix-footer');
  if (bar) {
    const r = bar.getBoundingClientRect(), cs = getComputedStyle(bar);
    out.bar = { h: +r.height.toFixed(2), display: cs.display, position: cs.position,
                zIndex: cs.zIndex, top: +r.top.toFixed(2), bottom: +r.bottom.toFixed(2),
                visible: vis(bar) };
  } else out.bar = null;

  /* --- 푸터 여유 ---------------------------------------------------------
   * 재는 것은 푸터 **박스**가 아니라 푸터 안 **마지막으로 보이는 콘텐츠**의 하단이다.
   * 스킨이 `.footer{padding-bottom:100px !important}` 로 100px 을 이미 예약해 두었고,
   * detail.css 는 body padding 으로 safe-area 만큼만 더한다.
   *   여유 = 100 + safe - (82 + safe) = 18px  (신아린 4차 §5 G-1/G-2: +17.6~18.4px)
   * 푸터 박스로 재면 항상 음수가 나온다 — 그건 예약된 padding 을 재는 것이라 무의미하다. */
  window.scrollTo(0, document.documentElement.scrollHeight);
  const foot = q('#footer') || q('.footer') || q('footer');
  out.footerProbe = null;
  if (foot) {
    let last = null, lastBottom = -1e9;
    for (const el of foot.querySelectorAll('*')) {
      if (el.children.length) continue;
      const t = (el.textContent || '').trim();
      if (!t && el.tagName !== 'IMG') continue;
      if (!vis(el)) continue;
      const r = el.getBoundingClientRect();
      if (r.height <= 0) continue;
      if (r.bottom > lastBottom) { lastBottom = r.bottom; last = el; }
    }
    out.footerProbe = last ? { tag: last.tagName, text: (last.textContent||'').trim().slice(0,40),
                               bottom: +lastBottom.toFixed(2) } : null;
    if (last && bar && vis(bar)) {
      out.footerGap = +(bar.getBoundingClientRect().top - lastBottom).toFixed(2);
    } else if (last) {
      out.footerGap = 999;   /* 바가 없는 폭(데스크톱) — 가릴 것이 없다 */
    } else out.footerGap = null;
  } else out.footerGap = null;
  out.scrollHeight = document.documentElement.scrollHeight;
  window.scrollTo(0, 0);

  /* --- 상세 이미지 확대 배율 --- */
  const imgs = qa('#prdDetail .zg-fold img, #prdDetail img');
  const z = [];
  for (const im of imgs) {
    if (!im.naturalWidth) continue;
    z.push(+(im.getBoundingClientRect().width / im.naturalWidth).toFixed(3));
  }
  out.zoom = { n: z.length, max: z.length ? Math.max(...z) : null,
               min: z.length ? Math.min(...z) : null };

  /* --- 지연로딩 / 색인 --- */
  out.lazy = {
    ecDataSrc: qa('#prdDetail img[ec-data-src]').length,
    withSrc: qa('#prdDetail img[src]').length,
    withAlt: qa('#prdDetail img[alt]').filter(i => (i.getAttribute('alt') || '').trim()).length,
    total: qa('#prdDetail img').length,
  };

  /* --- 갤러리 --- */
  out.gallery = { li: qa('.thumbnail__list > li').length,
                  liVisible: qa('.thumbnail__list > li').filter(vis).length };

  /* --- 접기 --- */
  const fold = q('.zg-fold');
  out.fold = fold ? { maxHeight: getComputedStyle(fold).maxHeight,
                      open: fold.classList.contains('zg-open'),
                      more: !!q('.zg-more') } : null;

  /* --- 삭제 섹션 흔적: 빈 공간·이중 여백 --- */
  /*  높이가 있는데 눈에 보이는 내용이 하나도 없는 블록 = 빈 공간 잔재 */
  const ghosts = [];
  for (const el of qa('.zg-detail div, .zg-detail section, .zg-detail ul')) {
    const r = el.getBoundingClientRect();
    if (r.height < 24 || r.width < 40) continue;
    if (el.children.length) continue;
    if ((el.textContent || '').trim()) continue;
    const cs = getComputedStyle(el);
    if (cs.backgroundImage !== 'none' || cs.borderTopWidth !== '0px') continue;
    ghosts.push({ cls: el.className || el.tagName, h: +r.height.toFixed(1) });
  }
  out.ghostBlocks = ghosts.slice(0, 10);
  /* 이중 여백: 인접 형제의 margin-bottom + margin-top 이 둘 다 24px 이상 */
  const dbl = [];
  for (const el of qa('.zg-detail > * , .detail-container > *')) {
    const n = el.nextElementSibling; if (!n) continue;
    const a = parseFloat(getComputedStyle(el).marginBottom) || 0;
    const b = parseFloat(getComputedStyle(n).marginTop) || 0;
    if (a >= 24 && b >= 24) dbl.push({ a, b, cls: (el.className || el.tagName) + '→' + (n.className || n.tagName) });
  }
  out.doubleMargins = dbl.slice(0, 10);

  /* --- 삭제 컨트롤 / 스테퍼 터치타깃 --- */
  const taps = qa('#totalProducts .delete, .zg-opt, .up, .down').map(el => {
    const r = el.getBoundingClientRect();
    return { cls: (el.className || el.tagName).toString().slice(0, 40),
             w: +r.width.toFixed(1), h: +r.height.toFixed(1) };
  });
  out.tapTargets = taps.slice(0, 20);

  /* --- a11y 숨김 select --- */
  const sel = q('.productOption select[name^="option"], .productOption select[id^="product_option_id"]');
  if (sel) {
    const r = sel.getBoundingClientRect(), cs = getComputedStyle(sel);
    out.a11ySelect = { w: +r.width.toFixed(1), h: +r.height.toFixed(1),
                       display: cs.display, visibility: cs.visibility,
                       clipPath: cs.clipPath,
                       hit: (() => { const e = document.elementFromPoint(
                            Math.round(r.left + r.width / 2), Math.round(r.top + r.height / 2));
                            return e ? (e.tagName + '.' + (e.className || '')).slice(0, 40) : null; })() };
  } else out.a11ySelect = null;

  return out;
};

/* --- 선택 행 2유형 (대표님 실기 반려 2026-09-08 F-1·F-2·F-3) ------------------
 * 카페24 옵션 스크립트(optimizer.php 캐시)로 tr.option_product / tr.add_product 를 실제로 만든다.
 * 픽스처 주입이 아니라 라이브와 같은 코드 경로다 — 두 행의 DOM 이 다르다는 사실 자체가 검사 대상이다. */
const MAKE_ROWS = async () => {
  const fire = (sel, last) => {
    const el = document.querySelector(sel); if (!el) return 'no ' + sel;
    const opts = Array.from(el.options).filter(o => o.value && o.value !== '*' && o.value !== '**');
    const o = last ? opts[opts.length - 1] : (opts[1] || opts[0]); if (!o) return 'no option';
    el.value = o.value; el.dispatchEvent(new Event('change', { bubbles: true })); return 'ok';
  };
  const r = { opt: fire('select[name="option1"]', false) };
  await new Promise(res => setTimeout(res, 500));
  r.add63 = fire('select[name="addproduct_option_name_63"]', true);
  await new Promise(res => setTimeout(res, 500));
  r.add13 = fire('select[name="addproduct_option_name_13"]', true);
  await new Promise(res => setTimeout(res, 700));
  r.optionRows = document.querySelectorAll('#totalProducts tr.option_product').length;
  r.addRows = document.querySelectorAll('#totalProducts tr.add_product').length;
  return r;
};

const ROWS = () => {
  const R = el => { const r = el.getBoundingClientRect();
    return { l: r.left, t: r.top, r: r.right, b: r.bottom, w: r.width, h: r.height }; };
  const out = [];
  for (const tr of document.querySelectorAll('#totalProducts tr.option_product, #totalProducts tr.add_product')) {
    const st = tr.querySelector('p:not(.product), span.quantity');
    const price = tr.querySelector('td.right');
    const kids = st ? Array.from(st.querySelectorAll(':scope > a, :scope > input')).map(k => {
      const cls = k.className || '';
      const label = k.tagName === 'INPUT' ? 'N' : /DownClass|\bdown\b/.test(cls) ? '−' : /UpClass|\bup\b/.test(cls) ? '+' : '?';
      return { label, x: k.getBoundingClientRect().left };
    }).sort((a, b) => a.x - b.x) : [];
    const trR = R(tr), stR = st ? R(st) : null, prR = price ? R(price) : null;
    const ovx = (stR && prR) ? Math.max(0, Math.min(stR.r, prR.r) - Math.max(stR.l, prR.l)) : null;
    const ovy = (stR && prR) ? Math.max(0, Math.min(stR.b, prR.b) - Math.max(stR.t, prR.t)) : null;
    out.push({
      type: (tr.className.match(/option_product|add_product/) || ['?'])[0],
      stepper: !!st, stepperW: stR ? +stR.w.toFixed(1) : null, stepperH: stR ? +stR.h.toFixed(1) : null,
      seq: kids.map(k => k.label).join(' '),
      priceText: price ? (price.textContent || '').replace(/\s+/g, ' ').trim().slice(0, 20) : '',
      priceW: prR ? +prR.w.toFixed(1) : null,
      overlapArea: (ovx != null) ? +(ovx * ovy).toFixed(1) : null,
      priceRightInset: (prR && trR) ? +(trR.r - prR.r).toFixed(1) : null,
      priceInsideRow: (prR && trR) ? (prR.r <= trR.r + 0.5 && prR.b <= trR.b + 0.5) : null,
      priceCenterDelta: (stR && prR) ? +(((prR.t + prR.b) / 2) - ((stR.t + stR.b) / 2)).toFixed(1) : null,
    });
  }
  return out;
};

/* 스킨 혜택 말풍선(.benefit-bubble > a, top:-28px) 을 강제로 띄워 위 텍스트와의 간격을 잰다.
 * 실기(대표님 캡처)에서는 카페24가 .EC-price-warning 을 숨긴 상태였다 → 그 상태와
 * 바운스 최고점(bubbleBounce translateY -5px)까지 재현해서 잰다. */
const BUBBLE = () => {
  const q = s => document.querySelector(s);
  const bb = q('.benefit-bubble'); if (!bb) return { found: false };
  bb.removeAttribute('hidden');
  const a = bb.querySelector('a'); if (!a) return { found: false };
  a.removeAttribute('df-banner-clone'); a.textContent = '혜택 말풍선'; a.hidden = false;
  const R = el => el.getBoundingClientRect();
  const note = q('.zg-sum__note');
  const warn = q('.EC-price-warning');
  const cand = Array.from(document.querySelectorAll('.infoArea-footer *, .zg-sum *'))
    .filter(e => !e.children.length && (e.textContent || '').trim() && !bb.contains(e)
                 && getComputedStyle(e).display !== 'none' && R(e).height > 0);
  const overlaps = (ar) => cand.filter(e => { const r = R(e);
    return Math.min(ar.bottom, r.bottom) - Math.max(ar.top, r.top) > 0 &&
           Math.min(ar.right, r.right) - Math.max(ar.left, r.left) > 0; })
    .map(e => (e.className || e.tagName).toString().slice(0, 30));
  /* B안(2026-09-09) 이후 인라인 블록은 시트가 닫혀 있는 동안 `display:none` 이다.
     그러면 말풍선도 화면에 없으므로 「안내문을 덮는가」 자체가 성립하지 않는다.
     그 상태를 숨기지 말고 `hidden: true` 로 사실대로 보고한다. */
  const shown = (() => { const r = R(a); const c = getComputedStyle(a);
    return r.height > 0 && r.width > 0 && c.display !== 'none' && c.visibility !== 'hidden'; })();
  /* R-8: 가격 아래 카카오 혜택 띠(`.evt`, 배너앱 슬롯 `detail-benefit`)도 함께 내렸다.
     말풍선과 같은 방식으로 `hidden` 을 떼고도 화면에 안 나오는지 사실대로 보고한다. */
  const evt = (() => {
    const e = document.querySelector('.evt'); if (!e) return { found: false };
    const had = e.hasAttribute('hidden');
    e.removeAttribute('hidden');
    const cs = getComputedStyle(e); const r = R(e);
    const out = { found: true, display: cs.display,
                  shown: r.width > 0 && r.height > 0 && cs.display !== 'none' && cs.visibility !== 'hidden' };
    if (had) e.setAttribute('hidden', '');
    return out;
  })();
  const out = { found: true, hidden: !shown, warnDisplay: warn ? getComputedStyle(warn).display : null,
                evt: evt,
                textOverlaps: shown ? overlaps(R(a)) : [] };
  if (!shown) { bb.setAttribute('hidden', ''); return out; }
  if (warn) warn.style.display = 'none';
  const ar = R(a);
  out.noteGapHidden = note ? +(ar.top - R(note).bottom).toFixed(1) : null;
  out.noteGapHiddenBounce = note ? +(ar.top - 5 - R(note).bottom).toFixed(1) : null;
  out.textOverlapsHidden = overlaps({ top: ar.top - 5, bottom: ar.bottom, left: ar.left, right: ar.right });
  if (warn) warn.style.display = '';
  bb.setAttribute('hidden', '');
  return out;
};

/* --- R-2 재탭 해제 (대표님 요청 2026-09-09) --------------------------------
 * 담긴 카드를 다시 누르면 그 구성이 빠지는가. 카페24가 만든 행의 **자기 삭제 컨트롤**을
 * 프로그램으로 누르는 경로라, 그 컨트롤이 사라지면 기능이 조용히 죽는다
 * → `nodel`(삭제 컨트롤 제거) 음성 대조군을 같이 돌려 검사 자체가 살아 있음을 증명한다. */
const UNTAP = async (nodel) => {
  const q = s => document.querySelector(s), qa = s => Array.from(document.querySelectorAll(s));
  const wait = ms => new Promise(r => setTimeout(r, ms));
  if (nodel) {
    new MutationObserver(() => {
      qa('#totalProducts tr.option_product a.delete, #totalProducts tr.option_product .option_box_del')
        .forEach(e => e.remove());
    }).observe(document.getElementById('totalProducts'), { childList: true, subtree: true });
  }
  const snap = () => {
    const tot = q('#totalPrice .total strong, #totalPrice .total em');
    const sum = q('.zg-bar__sum'), bar = q('.zg-bar__v');
    return {
      optRows: qa('#totalProducts tr.option_product').length,
      addRows: qa('#totalProducts tr.add_product').length,
      qtys: qa('#totalProducts tr.option_product input.quantity_opt').map(i => i.value),
      total: (tot ? tot.textContent : '').replace(/\s+/g, ' ').trim(),
      bar: (sum && sum.style.display === 'none') ? '(숨김)' : (bar ? bar.textContent : ''),
      picked0: !!(q('.zg-detail') && q('.zg-detail').classList.contains('zg-picked-0')),
      on: qa('.zg-opt').map(c => c.getAttribute('data-zg-on') || ''),
      ariaTail: qa('.zg-opt').map(c => {
        const a = c.getAttribute('aria-label') || '';
        const i = a.lastIndexOf(', ');
        return i < 0 ? a : a.slice(i + 2);
      }),
      toast: (() => { const t = q('.zg-toast');
        return t && t.classList.contains('zg-on') ? t.textContent : ''; })(),
      /* R-17 합계 줄 중 **실제로 화면에 보이는 것**만 담는다.
         ⚠ `hidden` 속성으로 세면 안 된다 — CSS 가 그것을 이기면 속성은 붙어 있어도
           줄은 그대로 보인다. 실제로 그랬고, 구성을 취소해도 지난 금액이 남아 있었다
           (`.zg-sum__row{display:flex}` 가 `[hidden]{display:none}` 을 이겼다). */
      sumVisible: qa('.zg-sum__row').filter((r) => {
        const cs = getComputedStyle(r);
        return cs.display !== 'none' && cs.visibility !== 'hidden'
            && r.getBoundingClientRect().height > 0;
      }).map((r) => r.textContent.replace(/\s+/g, ' ').trim()),
    };
  };
  const tap = i => { const c = qa('.zg-opt')[i]; if (c) c.click(); };
  /* R-17 ≤767px 에서는 상단 구매 블록이 통째로 감춰져 있다(2026-09-11 개편).
     시트를 열지 않고 재면 카드도 합계도 **숨은 조상 안**이라, 「보이는가」를 묻는
     검사가 전부 공허하게 통과한다(실제로 `C8.sum.live` 탐지가 0 으로 잡아냈다).
     고객이 실제로 거치는 경로대로 시트를 먼저 연다. */
  if (window.innerWidth <= 767) {
    window.scrollTo(0, Math.round(document.documentElement.scrollHeight * 0.45));
    await wait(450);
    const bar = q('.mobile-fix-footer .jsLayerBtn');
    if (bar) bar.click();
    await wait(900);
  }
  const out = { cards: qa('.zg-opt').length,
                sheetOpen: !!(q('.mobile-layer') && q('.mobile-layer').classList.contains('on')) };
  out.start = snap();
  tap(1); await wait(600); out.picked = snap();
  const inp = q('#totalProducts tr.option_product input.quantity_opt');
  if (inp) { inp.value = '3'; inp.dispatchEvent(new Event('change', { bubbles: true })); }
  await wait(600); out.qty3 = snap();
  tap(1); await wait(700); out.untapped = snap();          /* 수량 3 인 구성을 재탭 */
  tap(0); tap(3); await wait(800); out.two = snap();        /* 복수 담기는 그대로인가 */
  tap(0); await wait(700); out.oneLeft = snap();
  tap(3); await wait(700); out.empty = snap();              /* 마지막 하나 해제 → 빈 상태 */
  return out;
};

/* --- B안 하단바 구매 경로 (대표님 확정 2026-09-09) ---------------------------
 * 「장바구니·구매하기가 계속 떠 있는가」를 **실제로 눌러** 확인한다.
 * `product_submit` 을 가로채 발화 여부만 기록한다(주문은 만들지 않는다).
 *   - 바 장바구니 → product_submit(2) 가 반드시 발화해야 한다
 *   - 바 구매하기 → 시트가 열리거나(.fixed 상태) product_submit(1) 이 발화해야 한다(.fixed 아닌 상태 위임)
 * 둘 중 어느 것도 아니면 구매 경로가 끊긴 것이다 = 판매 정지. */
const BARBUY = async (atTop) => {
  const q = s => document.querySelector(s), qa = s => Array.from(document.querySelectorAll(s));
  const wait = ms => new Promise(r => setTimeout(r, ms));
  const vis = e => { if (!e) return false; const c = getComputedStyle(e), r = e.getBoundingClientRect();
    return c.display !== 'none' && c.visibility !== 'hidden' && c.opacity !== '0' && r.height > 0 && r.width > 0; };
  window.__SUB__ = [];
  window.product_submit = function (mode) { window.__SUB__.push(mode); return false; };
  const H = document.documentElement.scrollHeight;
  window.scrollTo(0, atTop ? 0 : Math.round(H * 0.45));
  await wait(900);
  const ml = q('.mobile-layer');
  const subs = () => qa('[onclick*="product_submit"]');
  const out = {
    atTop: !!atTop,
    mlFixed: !!(ml && ml.classList.contains('fixed')),
    barVisible: vis(q('.mobile-fix-footer')),
    reviewChipVisible: vis(q('.mobile-fix-footer .jsGoReview')),
    reviewHookInDom: qa('.alpha_review_count').length,
    alphaWidgetInDom: qa('[class*="alpha_widget"], [id*="alpha_widget"]').length,
    submitNodesInDom: subs().length,
    inlineVisible: vis(q('#fixedActionButton')),
    appPayInDom: qa('.app-pay-wrap').length,
    naverInDom: qa('#NaverChk_Button').length,
    kakaoPayInDom: qa('#appPaymentButtonBox').length,
    /* 2026-09-11 개편 이후 이 셋은 **개수가 아니라 보이는지**가 계약이다.
       · `.app-pay-wrap` 은 마크업에서 걷어냈다(요건: 네이버페이·카카오페이 제거)
       · 나머지 둘은 앱이 런타임에 만든다 — 지우면 다시 생기므로 **감춘다**.
         실측상 상자가 3벌까지 생기는데(앱 스크립트가 여러 번 돈다) 전부 감춰야 한다. */
    payVisible: (() => {
      const sel = '.app-pay-wrap, [id^="NaverChk"], #appPaymentButtonBox, #kakao-checkout-button';
      return qa(sel).filter((e) => {
        const cs = getComputedStyle(e);
        return cs.display !== 'none' && cs.visibility !== 'hidden'
            && e.getBoundingClientRect().height > 0;
      }).length;
    })(),
    bubbleLineHeight: (() => { const a = q('.benefit-bubble > a'); return a ? getComputedStyle(a).lineHeight : null; })(),
    barCartBox: (() => { const b = qa('.mobile-fix-footer [onclick*="product_submit"]')[0];
      if (!b) return null; const r = b.getBoundingClientRect(); return { w: +r.width.toFixed(1), h: +r.height.toFixed(1) }; })(),
    barBuyBox: (() => { const b = q('.mobile-fix-footer .jsLayerBtn');
      if (!b) return null; const r = b.getBoundingClientRect(); return { w: +r.width.toFixed(1), h: +r.height.toFixed(1) }; })(),
  };
  /* ① 바 장바구니 */
  window.__SUB__ = [];
  const cart = qa('.mobile-fix-footer [onclick*="product_submit"]')[0];
  if (cart) cart.click();
  await wait(500);
  out.cartFired = window.__SUB__.slice();
  /* ② 바 구매하기 */
  window.__SUB__ = [];
  const buy = q('.mobile-fix-footer .jsLayerBtn');
  if (buy) buy.click();
  await wait(1300);
  out.buyFired = window.__SUB__.slice();
  out.sheetOpened = !!(ml && ml.classList.contains('on'));
  out.inlineVisibleAfterBuy = vis(q('#fixedActionButton'));
  out.submit1VisibleAfterBuy = subs().filter(e => /product_submit\(\s*1/.test(e.getAttribute('onclick')) && vis(e)).length;
  out.buyPathOk = !!(out.sheetOpened || out.buyFired.indexOf(1) >= 0);
  /* 혜택 말풍선 — **실제로 그려 놓고** 글자가 26px 상자 안에 들어가는지 잰다.
   * `line-height` 계산값만 보면 버튼 쪽 값이나 말풍선의 font-size/height 가 바뀌어도
   * 14.4px 은 그대로라 계속 통과한다 = 고객이 보게 될 것을 하나도 지키지 못한다.
   * R-8 로 지금은 `display:none` 이라 그냥 재면 0 이 나오므로 강제로 띄운다.
   * 인라인 style 은 우리 비-important 규칙을 이긴다(실증). 조상(`#fixedActionButton`)도
   * 시트가 닫히면 `display:none` 이라 같이 띄운다. 잰 뒤 **전부 원상복구**한다. */
  out.bubbleFit = await (async () => {
    const bb = q('.benefit-bubble'); if (!bb) return { found: false };
    const a = bb.querySelector('a'); if (!a) return { found: false };
    const fab = q('#fixedActionButton');
    const sav = { fab: fab ? fab.style.display : null, bbD: bb.style.display,
                  bbH: bb.hasAttribute('hidden'), aH: a.hasAttribute('hidden'), aT: a.textContent };
    if (fab) fab.style.display = 'block';
    bb.hidden = false; bb.style.display = 'block';
    a.hidden = false;
    /* 문구가 비어 있으면(배너앱 미가동) 잴 것이 없다 → 대표 길이의 문구를 넣고 나중에 되돌린다.
     * ⚠ `textContent` 를 쓰면 자식 노드가 날아가므로, 넣은 경우에만 되돌린다. */
    const putText = !(a.textContent || '').trim();
    if (putText) a.textContent = '카카오로 구매하고 평생 무료배송 받기';
    /* 스킨은 `<a>` 안에 꼬리 삼각형용 빈 <span>(`bottom:-5px`, border 5px)을 둔다.
     * 그 5px 은 **의도된 장식**이라 글자 넘침과 섞이면 안 된다 → 재는 동안만 감춘다. */
    const kids = Array.from(a.children);
    const kidD = kids.map(k => k.style.display);
    kids.forEach(k => { k.style.display = 'none'; });
    await wait(80);
    const r = a.getBoundingClientRect(), cs = getComputedStyle(a);
    let outside = null;
    try {
      const rg = document.createRange(); rg.selectNodeContents(a);
      const tr = rg.getBoundingClientRect();
      outside = +(Math.max(0, tr.bottom - r.bottom) + Math.max(0, r.top - tr.top)).toFixed(1);
    } catch (e) {}
    const m = { found: true, renderable: r.width > 0 && r.height > 0,
                lineHeight: cs.lineHeight, fontSize: cs.fontSize,
                boxH: +r.height.toFixed(1),
                overflowPx: Math.max(0, a.scrollHeight - a.clientHeight),
                textOutsidePx: outside };
    kids.forEach((k, i) => { k.style.display = kidD[i]; });
    if (putText) a.textContent = sav.aT;
    if (sav.aH) a.setAttribute('hidden', ''); else a.removeAttribute('hidden');
    bb.style.display = sav.bbD;
    if (sav.bbH) bb.setAttribute('hidden', ''); else bb.removeAttribute('hidden');
    if (fab) fab.style.display = sav.fab;
    return m;
  })();
  return out;
};

/* 2026-09-11 개편 — 인라인 상단에서 구매 블록을 감췄다.
   옵션·수량 스테퍼는 **구매 시트 안**에서만 보이므로, 기하를 재려면 시트를 먼저 열어야 한다.
   검사를 없애는 게 아니라 **고객이 실제로 보는 자리**로 옮기는 것이다.
   여는 방법은 SHEET 과 동일하게 실제 경로(스크롤 → 하단바 클릭)를 쓴다. */
const OPEN_SHEET = () => {
  const btn = document.querySelector('.jsLayerBtn');
  if (!btn) return Promise.resolve({ opened: false, reason: 'no .jsLayerBtn' });
  window.scrollTo(0, Math.round(document.documentElement.scrollHeight * 0.45));
  return new Promise((res) => setTimeout(() => {
    btn.click();
    setTimeout(() => res({ opened: !!document.querySelector('.mobile-layer.on') }), 700);
  }, 450));
};

/* 2026-09-11 — **페이지 최상단**에서 하단바 「구매하기」 를 누르는 경로.
   스킨 `mobileLayerOn()` 은 `.fixed` 가 없으면 시트를 열지 않고 인라인 구매
   버튼을 대신 누른다. 상단 블록을 감춘 뒤로 그 버튼이 숨어 있어 옵션이 안 골라진
   채 결제가 시도되고 「옵션을 선택해 주세요」 만 떴다. 여기서 그 경로를 잡는다. */
const SHEET_TOP = () => {
  const q = (s) => document.querySelector(s);
  const btn = q('.mobile-fix-footer .jsLayerBtn');
  if (!btn) return Promise.resolve({ btn: false });
  window.scrollTo(0, 0);
  return new Promise((res) => setTimeout(() => {
    btn.click();
    setTimeout(() => {
      const ml = q('.mobile-layer');
      const opts = q('.zg-opts');
      const vis = (e) => { if (!e) return false; const cs = getComputedStyle(e);
        const r = e.getBoundingClientRect(); return cs.display !== 'none' && r.height > 0; };
      res({ btn: true,
            opened: !!(ml && ml.classList.contains('on')),
            optsVisible: vis(opts),
            cls: ml ? ml.className.trim() : '' });
    }, 1200);
  }, 400));
};

/* R-12 (2026-09-11) 열린 시트의 합계가 **구매 버튼 블록에 깔리지 않는가**.
   이 검사가 없어서 실기기에서 「할인금액」 줄이 잘린 채 배포됐다.
   같이 잰다: 카페24 간편결제 앱이 런타임에 넣는 결제/찜 블록이 내려가 있는가.
   ⚠ 노드 존재 검사(C9)는 그대로다 — 우리는 **지우지 않고 감춘다**. */
/* R-13 (2026-09-11) 시트를 연 채 **손가락으로 끌었을 때** 뒤 본문이 같이 밀리는가.
   ⚠ `mouse.wheel` 로는 못 잡는다 — `touch-action` 은 휠에 적용되지 않고, 아이폰에는 휠이 없다.
   ⚠ JS 로 만든 TouchEvent 로도 못 잡는다 — 합성 이벤트는 네이티브 스크롤을 일으키지 않는다.
   → CDP `Input.dispatchTouchEvent` 로 **진짜 터치 입력**을 넣는다.
   네 자리를 각각 끌어 본다. 통 안에서만 움직이고 나머지는 본문이 1px 도 움직이면 안 된다.
     · 딤(뒤 흐린 곳)        → 아무 일도 없어야 한다
     · 스크롤 통             → 통만 움직여야 한다
     · 고정된 합계 · 버튼    → `position:absolute` 라 통 바깥으로 취급돼 본문으로 새던 자리다 */
async function touchDrag(ctx, page, x, y, dy) {
  const cdp = await ctx.newCDPSession(page);
  const STEPS = 24;
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchStart', touchPoints: [{ x, y }] });
  await page.waitForTimeout(30);
  for (let i = 1; i <= STEPS; i++) {
    await cdp.send('Input.dispatchTouchEvent',
      { type: 'touchMove', touchPoints: [{ x, y: Math.round(y + dy * i / STEPS) }] });
    await page.waitForTimeout(24);
  }
  await cdp.send('Input.dispatchTouchEvent', { type: 'touchEnd', touchPoints: [] });
  await page.waitForTimeout(700);
  try { await cdp.detach(); } catch (e) {}
}

/* R-13/R-15 열린 시트의 **스크롤 격리 계약**.
   손가락이 닿는 네 곳의 `touch-action` 과 스크롤 통의 연쇄 차단을 그대로 읽는다.
   ⚠ 왜 「끌어 보고」 판정하지 않는가 — CDP `Input.dispatchTouchEvent` 는 합성 입력이라
     `touch-action` 을 제대로 타지 않는다. 차단이 걸린 요소(TA=none)에서 끌어도 본문이
     밀리는 것이 실측으로 확인됐다(2026-09-11). 그 결과로 판정하면 거짓 합격·거짓 불합격이
     둘 다 난다. → 동작을 만드는 **CSS 속성 자체**를 계약으로 고정하고,
     실제 끌기는 라이브 미러에서 사람이 확인한다(그쪽은 통 130px 스크롤·누출 0 확인). */
const TOUCH_CONTRACT = () => {
  const q = (s) => document.querySelector(s);
  const ta = (el) => (el ? getComputedStyle(el).touchAction : null);
  const tub = q('.mobile-layer__inner');
  const sumRow = q('.mobile-layer .infoArea-footer .zg-sum .zg-sum__row');
  const actKid = q('.mobile-layer .infoArea-footer .productAction .buy-btn-wrap');
  return {
    layer: ta(q('.mobile-layer')),
    dim: ta(q('.mobile-layer-bg')),
    tub: ta(tub),
    tubOverflowY: tub ? getComputedStyle(tub).overflowY : null,
    tubOverscroll: tub ? getComputedStyle(tub).overscrollBehaviorY : null,
    tubScrollable: tub ? (tub.scrollHeight - tub.clientHeight) : -1,
    sum: ta(q('.mobile-layer .infoArea-footer .zg-sum')),
    sumRow: ta(sumRow),
    act: ta(q('.mobile-layer .infoArea-footer .productAction')),
    actKid: ta(actKid),
  };
};

const SPOTS = () => {
  const q = (s) => document.querySelector(s);
  const ml = q('.mobile-layer'); if (!ml) return null;
  const mr = ml.getBoundingClientRect();
  const sum = q('.mobile-layer .infoArea-footer .zg-sum');
  const act = q('.mobile-layer .infoArea-footer .productAction');
  const y = {
    dim: Math.max(30, Math.round(mr.top) - 60),
    tub: Math.round(mr.top) + 300,
    sum: sum ? Math.round(sum.getBoundingClientRect().top) + 20 : null,
    act: act ? Math.round(act.getBoundingClientRect().top) + 30 : null,
  };
  /* 각 지점이 **의도한 것에 실제로 닿는가** — 엉뚱한 데를 끌고 「안 움직인다」고
     보고하면 검사가 거짓말을 한다. 최상단 요소를 같이 남긴다. */
  const x = Math.round(innerWidth / 2);
  y.hit = {};
  for (const k of ['dim', 'tub', 'sum', 'act']) {
    if (y[k] == null) { y.hit[k] = null; continue; }
    const e = document.elementFromPoint(x, y[k]);
    y.hit[k] = e ? {
      tag: e.tagName + '.' + (e.className || '').toString().split(' ')[0],
      inTub: !!(e.closest && e.closest('.mobile-layer__inner')),
      inSum: !!(e.closest && e.closest('.zg-sum')),
      inAct: !!(e.closest && e.closest('.productAction')),
      inLayer: !!(e.closest && e.closest('.mobile-layer')),
    } : null;
  }
  return y;
};

const SCROLLPOS = () => {
  const t = document.querySelector('.mobile-layer__inner');
  const d = document.documentElement;
  return {
    page: Math.round(window.pageYOffset || 0),
    tub: Math.round(t ? t.scrollTop : -1),
    /* **검사가 살아 있는지**를 같이 기록한다 — 움직일 수 없는 상태에서 잰
       「0px 움직였다」는 통과가 아니라 무의미다(거짓 통과 방지). */
    pageRoom: Math.max(0, Math.round(d.scrollHeight - window.innerHeight)),
    tubRoom: t ? Math.max(0, Math.round(t.scrollHeight - t.clientHeight)) : 0,
  };
};

const SHEET_SUM = () => {
  const q = (s) => document.querySelector(s);
  const ml = q('.mobile-layer');
  if (!ml) return { ok: false, reason: 'no .mobile-layer' };
  const act = q('.mobile-layer .infoArea-footer .productAction');
  const mr = ml.getBoundingClientRect();
  const ar = act ? act.getBoundingClientRect() : null;
  const rows = [...document.querySelectorAll('.mobile-layer .zg-sum__row')]
    .filter((r) => getComputedStyle(r).display !== 'none' && !r.hidden)
    .map((r) => {
      const b = r.getBoundingClientRect();
      return { t: r.textContent.replace(/\s+/g, ' ').trim().slice(0, 24),
               top: Math.round(b.top), bot: Math.round(b.bottom) };
    });
  /* 가림/잘림: 버튼 블록 위로 넘어갔거나 시트 밖으로 나간 줄 */
  const covered = rows.filter((r) =>
    (ar && r.bot > Math.round(ar.top) + 1) ||
    r.bot > Math.round(mr.bottom) + 1 ||
    r.top < Math.round(mr.top) - 1);
  const off = (sel) => { const e = q(sel); if (!e) return 'absent';
    return getComputedStyle(e).display === 'none' ? 'hidden' : 'SHOWN'; };
  /* R-14 정가는 **옵션 이름에 적힌 박스 수**로만 계산할 수 있다(시중가는 1박스 기준).
     한 줄이라도 박스 수를 못 읽으면 정가를 낼 수 없다 — 그때 정가 줄이 보이면
     그 숫자는 지어낸 것이다(실제로 product_no=104 에서 가짜 39,000원이 떴다). */
  const listDerivable = (() => {
    const rows = [...document.querySelectorAll('#totalProducts tr.option_product, #totalProducts tr.add_product')]
      .filter((r) => r.offsetParent !== null || r.getBoundingClientRect().height > 0);
    if (!rows.length) return false;
    return rows.every((r) => {
      const pd = r.querySelector('p.product');
      return /(\d+)\s*(?:box|박스)/i.test(pd ? pd.textContent : '');
    });
  })();
  const listShown = (() => {
    const r = [...document.querySelectorAll('.mobile-layer .zg-sum__row--list')][0];
    return !!(r && !r.hidden && getComputedStyle(r).display !== 'none');
  })();
  return {
    ok: true,
    open: !!(ml.classList.contains('fixed') && ml.classList.contains('on')),
    actH: ar ? Math.round(ar.height) : null,
    rowCount: rows.length,
    covered,
    listDerivable, listShown,
    appBox: off('#appPaymentButtonBox'),
    naver: off('#NaverChk_Button'),
    kakao: off('#kakao-checkout-button'),
  };
};

const SHEET = () => {
  const q = (s) => document.querySelector(s);
  const btn = q('.jsLayerBtn');
  if (!btn) return { opened: false, reason: 'no .jsLayerBtn' };
  /* ⚠ 페이지 최상단에서는 `.mobile-layer` 에 `.fixed` 가 없어 스킨 `mobileLayerOn()` 이
     **시트를 열지 않고 인라인 구매 버튼에 위임**한다(원문 확인). 시트를 실제로 여는 경로를
     재현하려면 먼저 스크롤해 `.fixed` 를 만들어야 한다 — 고객이 바를 쓰는 상태가 그 상태다. */
  window.scrollTo(0, Math.round(document.documentElement.scrollHeight * 0.45));
  return new Promise((res) => setTimeout(() => {
  btn.click();
  setTimeout(() => {
    const bar = q('.mobile-fix-footer');
    const sheet = q('.mobile-layer.fixed') || q('.mobile-layer');
    if (!bar || !sheet) return res({ opened: false, reason: 'no bar/sheet' });
    const br = bar.getBoundingClientRect(), sr = sheet.getBoundingClientRect();
    const overlap = Math.max(0, Math.min(br.bottom, sr.bottom) - Math.max(br.top, sr.top));
    const buttons = Array.from(sheet.querySelectorAll('button, .btnSubmit, .btnNormal')).slice(0, 3)
      .map(b => { const r = b.getBoundingClientRect();
                  return Math.max(0, Math.min(br.bottom, r.bottom) - Math.max(br.top, r.top)); });
    res({ opened: true,
          sheetVisible: getComputedStyle(sheet).display !== 'none',
          barZ: getComputedStyle(bar).zIndex, sheetZ: getComputedStyle(sheet).zIndex,
          overlapPx: +overlap.toFixed(2), buttonOverlap: buttons.map(v => +v.toFixed(2)),
          hitOnBar: (() => { const e = document.elementFromPoint(
              Math.round(br.left + br.width / 2), Math.round(br.top + br.height / 2));
              return e ? (e.tagName + '.' + (e.className || '')).toString().slice(0, 60) : null; })(),
          /* 문자열로 판정하지 않는다 — 그 지점의 최상단 요소가 **시트 안에 있는지**를 직접 본다.
             바 버튼이 opacity:0 으로만 감춰져 있으면 탭을 가로채므로 여기서 잡힌다. */
          hitInSheet: (() => { const e = document.elementFromPoint(
              Math.round(br.left + br.width / 2), Math.round(br.top + br.height / 2));
              return !!(e && sheet.contains(e)); })(),
          /* R-8 혜택 말풍선 끄기 — 시트를 **연** 상태가 말풍선이 마지막으로 보이던 자리다.
             배너앱은 `hidden` 속성을 떼고 배너를 채워 넣으므로, 여기서도 속성을 떼고
             그래도 화면에 안 나오는지(=CSS 가 이긴다) 본다. 잰 뒤 속성을 원래대로 돌린다.
             음성 대조: 규칙이 빠지면 빈 `<a>` 도 `padding:0 14px; height:26px` 으로
             28×26 상자를 만들어 shown 이 true 가 된다 → 검사가 살아 있음이 증명된다. */
          /* R-11: 시트를 열었을 때 합계가 구매 버튼에 가리는가.
             버튼 블록은 `position:absolute; bottom:0` 이라 스크롤과 무관하게 바닥에 붙어 있고,
             합계는 그 위에 같이 고정돼야 한다. 겹치면 결제 직전 숫자가 안 보인다. */
          sumOverlap: (() => {
            const tot = q('.zg-sum__row--tot'), cart = q('#actionCart');
            const buy = document.querySelector('.buy-btn-wrap .btnSubmit.gFull');
            if (!tot) return null;
            const T = tot.getBoundingClientRect();
            const ovl = (e) => { if (!e) return 0; const r = e.getBoundingClientRect();
              if (!(r.width > 0 && r.height > 0)) return 0;
              const y = Math.min(T.bottom, r.bottom) - Math.max(T.top, r.top);
              const x = Math.min(T.right, r.right) - Math.max(T.left, r.left);
              return (y > 0 && x > 0) ? +y.toFixed(1) : 0; };
            const cs = getComputedStyle(tot);
            return { cart: ovl(cart), buy: ovl(buy),
                     visible: T.height > 0 && cs.visibility !== 'hidden' && cs.display !== 'none',
                     top: +T.top.toFixed(1), bottom: +T.bottom.toFixed(1) };
          })(),
          bubble: (() => {
            const bb = q('.benefit-bubble'); if (!bb) return { found: false };
            const had = bb.hasAttribute('hidden');
            bb.removeAttribute('hidden');
            const display = getComputedStyle(bb).display;
            const a = bb.querySelector('a');
            let shown = false;
            if (a) { a.hidden = false; const r = a.getBoundingClientRect();
                     const c = getComputedStyle(a);
                     shown = r.width > 0 && r.height > 0 && c.visibility !== 'hidden'; }
            if (had) bb.setAttribute('hidden', '');
            return { found: true, shown: shown, display: display };
          })() });
  }, 900);
  }, 900));
};

const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });

for (const scen of cfg.scenarios) {
  const { ctx, blocked } = await makeContext(browser, scen.vp, scen.safe, scen.stub);
  const page = await ctx.newPage();
  const errors = [], consoleErr = [], dialogs = [];
  /* 알럿을 닫아 주지 않으면 이후 evaluate 가 전부 멈춘다.
     「옵션을 선택해 주세요」 같은 결제 차단 알럿을 세기 위해 모은다. */
  page.on('dialog', d => { dialogs.push(String(d.message()).slice(0, 120)); d.dismiss().catch(() => {}); });
  page.on('pageerror', e => errors.push({ msg: String(e.message).slice(0, 200), stack: String(e.stack || '').slice(0, 400) }));
  page.on('console', m => { if (m.type() === 'error') consoleErr.push(String(m.text()).slice(0, 160)); });
  let rec = { name: scen.name, vp: scen.vp, safe: scen.safe, stub: scen.stub || cfg.stub, ok: true };
  try {
    await page.goto('https://zengenetics.co.kr' + cfg.docPath, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(scen.settle || 900);
    /* 접기를 펼쳐 상세 14장을 전부 살린다 (신아린 4차 §1 "펼친 뒤 14/14 로드") */
    if (scen.expand) {
      const clicked = await page.evaluate(() => {
        const m = document.querySelector('.zg-more');
        if (!m) return false; m.click(); return true;
      });
      rec.expandClicked = clicked;
      await page.waitForTimeout(400);
    }
    /* 지연 이미지까지 실제로 로드시킨다 — naturalWidth 가 0 이면 확대 배율을 못 잰다.
     * (측정 대상 수가 뷰포트마다 달라지면 그 자체가 거짓 통과의 씨앗이다) */
    if (scen.sweep !== false) {
      await page.evaluate(async () => {
        const H = document.documentElement.scrollHeight;
        for (let y = 0; y < H; y += Math.max(300, window.innerHeight * 0.8)) {
          window.scrollTo(0, y); await new Promise(r => setTimeout(r, 60));
        }
        window.scrollTo(0, 0); await new Promise(r => setTimeout(r, 120));
      });
      await page.waitForTimeout(500);
    }
    if (scen.barbuy) {
      rec.barbuy = await page.evaluate(BARBUY, scen.barbuy === 'top');
    }
    if (scen.untap) {
      rec.untap = await page.evaluate(UNTAP, scen.untap === 'nodel');
    }
    if (scen.rows) {
      /* 모바일은 시트를 열어야 스테퍼가 보인다 (2026-09-11 개편) */
      if (scen.vp <= 767) rec.rowsSheet = await page.evaluate(OPEN_SHEET);
      rec.rowsMade = await page.evaluate(MAKE_ROWS);
      await page.waitForTimeout(600);
      rec.rows = await page.evaluate(ROWS);
      rec.bubble = await page.evaluate(BUBBLE);
    }
    rec.m = await page.evaluate(MEASURE);
    if (scen.sheet) rec.sheet = await page.evaluate(SHEET);
    if (scen.sheet) { await page.waitForTimeout(400); rec.sheetSum = await page.evaluate(SHEET_SUM); }
    /* R-12 **구성을 고른 뒤** 시트를 여는 경로 — 고객이 실제로 거치는 순서다.
     * 고르지 않으면 정가·할인금액 줄이 숨어 있어 합계가 짧고, 가림이 드러나지 않는다.
     * 이 시나리오가 없어서 「할인금액」 잘림이 검사를 통과해 버렸다 (2026-09-11). */
    if (scen.sheetSum) {
      rec.rowsMade = await page.evaluate(MAKE_ROWS);
      await page.waitForTimeout(700);
      rec.sheetOpen = await page.evaluate(OPEN_SHEET);
      await page.waitForTimeout(700);
      rec.sheetSum = await page.evaluate(SHEET_SUM);
    }
    if (scen.sheetDrag) {
      rec.rowsMade = await page.evaluate(MAKE_ROWS);
      await page.waitForTimeout(700);
      rec.sheetOpen = await page.evaluate(OPEN_SHEET);
      await page.waitForTimeout(700);
      const spots = await page.evaluate(SPOTS);
      rec.dragSpots = spots;
      rec.touch = await page.evaluate(TOUCH_CONTRACT);
      rec.drag = {};
      if (spots) {
        /* 본문이 **움직일 수 있는 자리**로 한 번 내려놓는다 — 맨 위면 위로 끌어도
           움직일 데가 없어 무엇을 해도 0 이 나와 검사가 거짓 통과한다. */
        await page.evaluate(() => {
          const d = document.documentElement;
          window.scrollTo(0, Math.round((d.scrollHeight - window.innerHeight) * 0.4));
        });
        await page.waitForTimeout(500);
        for (const name of ['dim', 'tub', 'sum', 'act']) {
          if (spots[name] == null) { rec.drag[name] = null; continue; }
          /* ⚠ 끌기 **직전에** 페이지를 스크롤하면 그 관성이 이어지는 터치를 삼켜
             통이 안 움직인다(실측: tubMoved 0). 스크롤은 루프 **앞에서 한 번만** 한다. */
          const before = await page.evaluate(SCROLLPOS);
          /* 끌기 **그 시점의 상태**를 남긴다 — 왜 새는지 추측하지 않기 위해서다 */
          const state = await page.evaluate((y) => {
            const ml = document.querySelector('.mobile-layer');
            const sum = document.querySelector('.mobile-layer .infoArea-footer .zg-sum');
            const e = document.elementFromPoint(Math.round(innerWidth / 2), y);
            return {
              layer: ml ? ml.className.trim() : null,
              sumPos: sum ? getComputedStyle(sum).position : null,
              hit: e ? (e.tagName + '.' + (e.className || '').toString().split(' ')[0]) : null,
              hitTA: e ? getComputedStyle(e).touchAction : null,
              inSum: !!(e && e.closest && e.closest('.zg-sum')),
              inTub: !!(e && e.closest && e.closest('.mobile-layer__inner')),
            };
          }, spots[name]);
          await touchDrag(ctx, page, Math.round(scen.vp / 2), spots[name], -200);
          const after = await page.evaluate(SCROLLPOS);
          rec.drag[name] = {
            pageMoved: after.page - before.page,
            tubMoved: after.tub - before.tub,
            pageRoom: before.pageRoom, tubRoom: before.tubRoom,
            pageAt: before.page,
            tubAt: before.tub,
            state: state,
          };
        }
      }
    }
    if (scen.sheetTop) {
      const before = dialogs.length;
      rec.sheetTop = await page.evaluate(SHEET_TOP);
      rec.sheetTop.alerts = dialogs.length - before;
    }
    /* 에러 분류 — 우리 파일(/ds/) 에서 난 것만이 우리 책임이다.
     * 교차출처 차단으로 Kakao/AuthSSLManager 같은 남의 전역이 없어 나는 것은 하네스 환경 탓. */
    rec.errors = errors;
    rec.errorsOurs = errors.filter(e => /\/ds\/(js|css)\//.test(e.stack || '') ||
                                        /detail-ui\.js|zg-ga4\.js/.test(e.stack || ''));
    rec.consoleErrors = consoleErr.slice(0, 10);
    rec.blockedSameOrigin = blocked.filter(u => u.includes('zengenetics.co.kr')).slice(0, 20);
  } catch (e) {
    rec.ok = false; rec.error = String(e.message).slice(0, 400); rec.errors = errors;
  }
  results.push(rec);
  await ctx.close();
}
await browser.close();
console.log('__JSON__' + JSON.stringify({ results }));
