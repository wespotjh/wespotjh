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

const SHEET = () => {
  const q = (s) => document.querySelector(s);
  const btn = q('.jsLayerBtn');
  if (!btn) return { opened: false, reason: 'no .jsLayerBtn' };
  btn.click();
  return new Promise((res) => setTimeout(() => {
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
              return e ? (e.tagName + '.' + (e.className || '')).toString().slice(0, 60) : null; })() });
  }, 400));
};

const browser = await chromium.launch({ args: ['--force-color-profile=srgb', '--font-render-hinting=none'] });

for (const scen of cfg.scenarios) {
  const { ctx, blocked } = await makeContext(browser, scen.vp, scen.safe, scen.stub);
  const page = await ctx.newPage();
  const errors = [], consoleErr = [];
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
    rec.m = await page.evaluate(MEASURE);
    if (scen.sheet) rec.sheet = await page.evaluate(SHEET);
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
