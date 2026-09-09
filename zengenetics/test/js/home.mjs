/* ============================================================================
 * 홈 실렌더 하네스 (Chromium) — checks/h_home.py 가 부른다.
 *   라이브 홈 HTML 의 <main> 을 새 index.html 본문으로 바꾼 픽스처를 띄운다.
 *   동일출처 자산은 캐시에서, 이미지 86장은 전달 폴더 실파일에서, three.js 는 캐시에서.
 *   그 밖 교차출처는 전부 차단한다.
 * ==========================================================================*/
import fs from 'node:fs';
import path from 'node:path';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));
const MIME = { '.webp': 'image/webp', '.jpg': 'image/jpeg', '.jpeg': 'image/jpeg', '.png': 'image/png' };
const results = [];

function ctypeFor(url, fallback) {
  if (/\.css(\?|$)/.test(url) || /type=css/.test(url)) return 'text/css; charset=utf-8';
  if (/\.js(\?|$)/.test(url) || /type=js/.test(url)) return 'application/javascript; charset=utf-8';
  return fallback || 'application/octet-stream';
}
const sleep = (ms) => new Promise(r => setTimeout(r, ms));

async function makeContext(browser, scen) {
  const ctx = await browser.newContext({
    viewport: { width: scen.vp, height: scen.vp <= 767 ? 844 : 900 },
    deviceScaleFactor: 1, userAgent: cfg.ua, isMobile: scen.vp <= 767, hasTouch: scen.vp <= 767,
  });
  await ctx.route('**/*', async (route) => {
    const req = route.request();
    const u = new URL(req.url());
    const key = u.pathname + (u.search || '');
    if (u.hostname === 'cdnjs.cloudflare.com') {
      if (scen.block3d || !cfg.three) return route.abort();
      if (scen.delay3d) await sleep(scen.delay3d);
      return route.fulfill({ status: 200, contentType: 'application/javascript', body: fs.readFileSync(cfg.three) });
    }
    if (u.host !== 'zengenetics.co.kr') return route.abort();
    if (key === cfg.docPath) {
      return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8',
                             body: fs.readFileSync(scen.fixture, 'utf8') });
    }
    if (cfg.ours[key]) {
      /* 표본 반전: 시나리오가 지정한 대체본(가드 제거판)을 대신 내려 준다 */
      const f = (scen.oursOverride && scen.oursOverride[key]) || cfg.ours[key];
      return route.fulfill({ status: 200, contentType: ctypeFor(key), body: fs.readFileSync(f, 'utf8') });
    }
    if (u.pathname.startsWith('/ds/image/')) {
      /* 프레임 이미지 도착이 늦는 실기 상황 — 게이트가 빈 판을 막는지 보는 조건 */
      if (scen.imgDelay && /diss/.test(u.pathname)) await sleep(scen.imgDelay);
      const f = path.join(cfg.imgdir, path.basename(u.pathname));
      if (fs.existsSync(f)) return route.fulfill({ status: 200, contentType: MIME[path.extname(f)] || 'application/octet-stream', body: fs.readFileSync(f) });
      return route.fulfill({ status: 404, body: '' });
    }
    /* 배너매니저 로더는 `?v=<timestamp>` 를 붙여 부른다 — 경로만으로도 찾는다 */
    const a = cfg.assets[key] || cfg.assets[u.pathname];
    if (a && a.status === 200 && fs.existsSync(a.file)) {
      return route.fulfill({ status: 200, contentType: ctypeFor(key, a.ctype), body: fs.readFileSync(a.file) });
    }
    return route.abort();
  });
  return ctx;
}

/* 문서 좌표 — offsetTop 은 offsetParent 기준이라 쓰면 안 된다 */
const docTop = (el) => el.getBoundingClientRect().top + window.pageYOffset;

const FULL = async () => {
  const q = (s) => document.querySelector(s);
  const qa = (s) => Array.from(document.querySelectorAll(s));
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const dt = (el) => el.getBoundingClientRect().top + window.pageYOffset;
  const out = {};
  out.landmark = { pblock: qa('.zg-pblock').length, frames: qa('.zg-fr').length,
                   thumbs: qa('.zg-thumbs a').length, h1: qa('h1').length, ctabar: qa('.zg-ctabar').length };
  out.overflow = { scrollWidth: document.documentElement.scrollWidth, clientWidth: document.documentElement.clientWidth };
  const root = q('.zg-home');
  const cs = root ? getComputedStyle(root) : null;
  out.wrapper = cs ? { overflowX: cs.overflowX, overflowY: cs.overflowY, transform: cs.transform, filter: cs.filter, contain: cs.contain } : null;
  const track = q('.zg-hero-track'), stage = q('.zg-hero-stage');
  /* 히어로 진행률은 rAF 로 천천히 따라간다(lerp). 고정 대기 대신 캡션 opacity 가 안정될 때까지 폴링한다.
     메인 스레드가 무거운 환경(스킨 setInterval 등)에서 고정 대기는 거짓 FAIL 을 만든다. */
  const caps = ['.zg-cap-a', '.zg-cap-m', '.zg-cap-e', '.zg-cap-n', '.zg-cap-s'].map(q);
  const settle = async () => {
    let last = null, stable = 0;
    for (let i = 0; i < 40; i++) {
      await wait(100);
      const ops = caps.map(c => c ? Number(getComputedStyle(c).opacity) : -1);
      const mx = Math.max(...ops), am = ops.indexOf(mx);
      const key = am + ':' + mx.toFixed(2);
      if (key === last && mx > 0.5) { if (++stable >= 3) return am; } else { stable = 0; last = key; }
    }
    const ops = caps.map(c => c ? Number(getComputedStyle(c).opacity) : -1);
    return ops.indexOf(Math.max(...ops));
  };
  const argmax = [];
  /* 진행률 p = -rect.top / (trackH - vh) 이다. 트랙 높이의 비율이 아니라 p 기준으로 스크롤한다.
     캡션 창: A p<0.063 · M 0.159~0.289 · E 0.418~0.523 · N 0.653~0.759 · S >0.926 */
  const span = track.offsetHeight - window.innerHeight;
  for (const p of [0.02, 0.22, 0.47, 0.70, 0.96]) {
    window.scrollTo(0, Math.round(dt(track) + span * p));
    argmax.push(await settle());
  }
  out.progressArgmax = argmax;
  window.scrollTo(0, Math.round(dt(track) + track.offsetHeight * 0.5)); await wait(300);
  out.sticky = { stageTop: Math.round(stage.getBoundingClientRect().top), cs: getComputedStyle(stage).position };
  const b = q('.zg-pblock[data-zg-p="pot"]'); const bt = b.querySelector('.zg-track');
  const idxOf = () => Array.from(b.querySelectorAll('.zg-fr')).findIndex(x => x.classList.contains('zg-on'));
  const idx = [];
  for (const f of [0.02, 0.5, 0.95]) { window.scrollTo(0, Math.round(dt(bt) + bt.offsetHeight * f)); await wait(320); idx.push(idxOf()); }
  out.scrub = { frames: b.querySelectorAll('.zg-fr').length, idx, v0: b.querySelector('.zg-v0')?.textContent, v1: b.querySelector('.zg-v1')?.textContent };
  /* 조건 ④ */
  window.scrollTo(0, Math.round(dt(track) + track.offsetHeight * 0.5)); await wait(320);
  const before = Math.round(window.pageYOffset);
  document.body.classList.add('eMobilePopup'); await wait(150);
  const frozen = !!(window.ZG_HOME && window.ZG_HOME.frozen);
  document.body.classList.remove('eMobilePopup'); await wait(350);
  out.cond4 = { before, frozen, restored: Math.round(window.pageYOffset), stillFrozen: !!(window.ZG_HOME && window.ZG_HOME.frozen) };
  /* R16 */
  const rc = root.className; document.body.removeAttribute('class');
  out.bodywipe = { survived: root.className === rc, bodyClass: document.body.className };
  return out;
};

const NO3D = () => {
  const root = document.querySelector('.zg-home'), fb = document.querySelector('.zg-fallback');
  return { zgNo3d: root.classList.contains('zg-no3d'), bodyClass: document.body.className,
           fallbackDisplay: getComputedStyle(fb).display, trackH: document.querySelector('.zg-hero-track').offsetHeight,
           viewportH: window.innerHeight, capAOpacity: getComputedStyle(document.querySelector('.zg-cap-a')).opacity,
           scrollW: document.documentElement.scrollWidth, clientW: document.documentElement.clientWidth,
           three: typeof THREE !== 'undefined' };
};

const NEG = async () => {
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const dt = (el) => el.getBoundingClientRect().top + window.pageYOffset;
  const track = document.querySelector('.zg-hero-track'), stage = document.querySelector('.zg-hero-stage');
  window.scrollTo(0, Math.round(dt(track) + track.offsetHeight * 0.5)); await wait(300);
  const cs = getComputedStyle(document.querySelector('.zg-home'));
  return { overflowX: cs.overflowX, overflowY: cs.overflowY, stageTop: Math.round(stage.getBoundingClientRect().top) };
};

const SAFETY = async () => {
  const wait = (ms) => new Promise(r => setTimeout(r, ms));
  const dt = (el) => el.getBoundingClientRect().top + window.pageYOffset;
  const t = document.querySelector('.zg-hero-track');
  window.scrollTo(0, Math.round(dt(t) + t.offsetHeight * 0.5)); await wait(300);
  document.body.classList.add('eMobilePopup'); await wait(300);
  const a = window.ZG_HOME.frozen; await wait(3200);
  return { frozenAt300ms: a, frozenAt3500ms: window.ZG_HOME.frozen, bodyStillHasClass: document.body.classList.contains('eMobilePopup') };
};

/* 스크럽 구간의 프레임타임·롱태스크·프레임 교체 준비상태를 페이지 안에서 모은다.
   MutationObserver 콜백은 그 프레임의 페인트 전에 돌기 때문에, 그 시점의 complete/naturalWidth 가
   "보여줄 때 이미 디코드돼 있었는가" 를 그대로 말해 준다. */
const PROBE = () => {
  window.__zg = { swaps: [], frames: [], long: [], gate: [], mark: 0, swapMark: 0, longMark: 0, t0: performance.now() };
  const Z = window.__zg;
  const start = () => {
    document.querySelectorAll('.zg-plate').forEach((pl) => {
      new MutationObserver((recs) => {
        for (const r of recs) {
          const el = r.target;
          if (!el.classList || !el.classList.contains('zg-fr') || !el.classList.contains('zg-on')) continue;
          const par = el.parentNode;
          Z.swaps.push({ idx: Array.prototype.indexOf.call(par.children, el),
                         complete: el.complete, nw: el.naturalWidth });
        }
      }).observe(pl, { attributes: true, attributeFilter: ['class'], subtree: true });
    });
    /* 게이트(data-zg-fr) 전이 시각 — 언제 열렸는지, 얼마나 걸렸는지 */
    document.querySelectorAll('.zg-plate').forEach((pl) => {
      new MutationObserver((recs) => {
        const key = (pl.closest('.zg-pblock') || {}).dataset.zgP || '?';
        for (const r of recs) Z.gate.push({ key, from: r.oldValue, to: pl.getAttribute('data-zg-fr'),
                                            t: Math.round(performance.now() - Z.t0) });
      }).observe(pl, { attributes: true, attributeFilter: ['data-zg-fr'], attributeOldValue: true });
    });
    let prev = performance.now();
    const tick = () => { const n = performance.now(); Z.frames.push(Math.round((n - prev) * 10) / 10); prev = n; requestAnimationFrame(tick); };
    requestAnimationFrame(tick);
    try { new PerformanceObserver((l) => { for (const e of l.getEntries()) Z.long.push(Math.round(e.duration)); })
      .observe({ entryTypes: ['longtask'] }); } catch (e) {}
  };
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', start); else start();
};

const browser = await chromium.launch({ args: ['--use-gl=swiftshader', '--enable-unsafe-swiftshader', '--force-color-profile=srgb'] });
for (const scen of cfg.scenarios) {
  const ctx = await makeContext(browser, scen);
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push({ msg: String(e.message).slice(0, 200), stack: String(e.stack || '').slice(0, 400) }));
  const rec = { name: scen.name, vp: scen.vp, kind: scen.kind, ok: true, m: {} };
  try {
    if (scen.kind === 'late' || scen.kind === 'promote') {
      /* 시각 의존을 없앤다: .zg-home 의 class 변화를 페이지 안에서 기록하고,
         "THREE 가 없을 때 .zg-no3d 가 붙은 적이 있는가" 를 그 기록으로 판정한다. */
      await page.addInitScript(() => {
        window.__zgLog = [];
        const mo = new MutationObserver(() => {
          const r = document.querySelector('.zg-home');
          if (r) window.__zgLog.push({ cls: r.className, three: typeof THREE !== 'undefined', t: performance.now() });
        });
        document.addEventListener('DOMContentLoaded', () => {
          const r = document.querySelector('.zg-home');
          if (r) mo.observe(r, { attributes: true, attributeFilter: ['class'] });
        });
      });
    }
    if (scen.kind === 'jank' || scen.kind === 'back') {
      const cdp = await ctx.newCDPSession(page);
      if (scen.stallDecode) {
        /* 보고된 병리의 통제 재현 — 겹쳐 쌓인 안 보이는 이미지의 decode() 가 끝내 확정되지 않는 상태 */
        await page.addInitScript(() => {
          Object.defineProperty(HTMLImageElement.prototype, 'decode', {
            value: function () { return new Promise(function () {}); }, configurable: true, writable: true });
        });
      }
      await page.addInitScript(PROBE);
      /* 프레임 도착이 늦는 조건에서는 load 를 기다리지 않는다 — 기다리면 지연이 다 지나가 버린다 */
      await page.goto('https://zengenetics.co.kr' + cfg.docPath,
                      { waitUntil: scen.imgDelay ? 'domcontentloaded' : 'load', timeout: 90000 });
      await page.waitForTimeout(2500);
      const geo = await page.evaluate((bk) => {
        const el = document.querySelector('.zg-pblock[data-zg-p="' + bk + '"] .zg-track');
        const hero = document.querySelector('.zg-hero-track');
        return { top: el.getBoundingClientRect().top + window.pageYOffset, h: el.offsetHeight,
                 vh: window.innerHeight, heroTop: hero.getBoundingClientRect().top + window.pageYOffset,
                 heroH: hero.offsetHeight };
      }, scen.block || 'pot');
      await page.evaluate((y) => window.scrollTo(0, y - 40), geo.top);
      await page.waitForTimeout(scen.imgDelay ? 1200 : 1500);
      if (scen.throttle) await cdp.send('Emulation.setCPUThrottlingRate', { rate: scen.throttle });
      await page.evaluate(() => { const Z = window.__zg; Z.mark = Z.frames.length; Z.swapMark = Z.swaps.length; Z.longMark = Z.long.length; Z.t1 = performance.now(); });
      const span = geo.h - geo.vh, STEPS = 40, DUR = 1600;
      for (let i = 1; i <= STEPS; i++) {
        await page.evaluate((y) => window.scrollTo(0, y), geo.top - 40 + Math.round(span * i / STEPS));
        await page.waitForTimeout(DUR / STEPS);
      }
      /* decode 무응답 조건에서는 8초 안전장치가 뜨는 시점까지 본다 — 반전본이 'late' 로 열리는 것을 잡으려면 필요하다 */
      await page.waitForTimeout(scen.stallDecode ? 4000 : 400);
      rec.m.jank = await page.evaluate((bk) => {
        const Z = window.__zg;
        const fr = Z.frames.slice(Z.mark), sw = Z.swaps.slice(Z.swapMark), lt = Z.long.slice(Z.longMark);
        const so = fr.slice().sort((a, b) => a - b);
        const pct = (q) => so.length ? so[Math.min(so.length - 1, Math.floor(so.length * q))] : 0;
        const pl = document.querySelector('.zg-pblock[data-zg-p="' + bk + '"] .zg-plate');
        return { n: fr.length, p50: pct(0.5), p95: pct(0.95), max: Math.max(0, ...fr),
                 over50: fr.filter(x => x > 50).length, over100: fr.filter(x => x > 100).length,
                 longN: lt.length, longMs: lt.reduce((a, b) => a + b, 0),
                 swaps: sw.length, uniq: new Set(sw.map(x => x.idx)).size,
                 notReady: sw.filter(x => !x.complete || !x.nw).length,
                 state: pl ? (pl.getAttribute('data-zg-fr') || '-') : '?',
                 gate: Z.gate.filter(g => g.key === bk),
                 imgLoaded: Array.from(document.querySelectorAll('.zg-pblock[data-zg-p="' + bk + '"] .zg-fr'))
                   .filter(i => i.complete && i.naturalWidth).length };
      }, scen.block || 'pot');
      if (scen.kind === 'back') {
        /* 히어로로 되돌아왔을 때 다시 그리는가 — 캡션 argmax 로 확인한다(픽셀 비의존) */
        if (scen.throttle) await cdp.send('Emulation.setCPUThrottlingRate', { rate: 1 });
        rec.m.back = await page.evaluate(async (g) => {
          const wait = (ms) => new Promise(r => setTimeout(r, ms));
          const caps = ['.zg-cap-a', '.zg-cap-m', '.zg-cap-e', '.zg-cap-n', '.zg-cap-s'].map(s => document.querySelector(s));
          const read = () => caps.map(c => c ? Number(getComputedStyle(c).opacity) : -1);
          const at = async (p) => {
            window.scrollTo(0, Math.round(g.heroTop + (g.heroH - g.vh) * p));
            let last = null, stable = 0;
            for (let i = 0; i < 30; i++) {
              await wait(100);
              const o = read(), mx = Math.max(...o), am = o.indexOf(mx), key = am + ':' + mx.toFixed(2);
              if (key === last && mx > 0.5) { if (++stable >= 3) return am; } else { stable = 0; last = key; }
            }
            const o = read(); return o.indexOf(Math.max(...o));
          };
          const a = await at(0.47), b = await at(0.02);
          return { atMid: a, atTop: b, canvas: !!document.querySelector('.zg-hero-stage canvas') };
        }, geo);
      }
    } else if (scen.kind === 'resize') {
      /* 회전·폭 전환: 실제 뷰포트를 바꿔 resize 이벤트를 낸다 (main_js.html 의 destroy → undefined 경로) */
      await page.goto('https://zengenetics.co.kr' + cfg.docPath, { waitUntil: 'load', timeout: 60000 });
      await page.waitForTimeout(1500);
      await page.evaluate(() => { window.__zgResize = 0; window.addEventListener('resize', () => { window.__zgResize++; }); });
      for (const [w, h] of scen.seq) {
        await page.setViewportSize({ width: w, height: h });
        await page.waitForTimeout(700);
      }
      rec.m.resize = await page.evaluate(() => ({
        resizeCount: window.__zgResize,
        stubTypes: ['runMainBannerSlidePC', 'runMainBannerSlideMobile', 'runSubBannerSlide'].map(k => typeof window[k]),
        width: window.innerWidth }));
    } else if (scen.kind === 'late') {
      /* three.js 가 오기 전에 아래로 내려간 상태를 만든다 */
      await page.goto('https://zengenetics.co.kr' + cfg.docPath, { waitUntil: 'domcontentloaded', timeout: 60000 });
      await page.waitForTimeout(300);
      const before = await page.evaluate(() => { window.scrollTo(0, window.innerHeight * 2.5);
        return document.querySelector('.zg-home').classList.contains('zg-no3d'); });
      await page.waitForTimeout(scen.delay3d + 1200);
      rec.m.promote = await page.evaluate((b) => ({
        no3dBefore: b || (window.__zgLog || []).some(x => /zg-no3d/.test(x.cls) && !x.three),
        no3dAfter: document.querySelector('.zg-home').classList.contains('zg-no3d'), threeAfter: typeof THREE !== 'undefined',
        log: (window.__zgLog || []).slice(0, 8) }), before);
    } else if (scen.kind === 'promote') {
      await page.goto('https://zengenetics.co.kr' + cfg.docPath, { waitUntil: 'domcontentloaded', timeout: 60000 });
      const before = await page.evaluate(() => document.querySelector('.zg-home').classList.contains('zg-no3d'));
      await page.waitForTimeout(scen.delay3d + 1200);
      rec.m.promote = await page.evaluate((b) => ({
        no3dBefore: b || (window.__zgLog || []).some(x => /zg-no3d/.test(x.cls) && !x.three),
        no3dAfter: document.querySelector('.zg-home').classList.contains('zg-no3d'), threeAfter: typeof THREE !== 'undefined',
        log: (window.__zgLog || []).slice(0, 8) }), before);
    } else {
      await page.goto('https://zengenetics.co.kr' + cfg.docPath, { waitUntil: 'load', timeout: 60000 });
      if (scen.inject) await page.addStyleTag({ content: scen.inject });
      await page.waitForTimeout(1400);
      if (scen.kind === 'full') rec.m = await page.evaluate(FULL);
      else if (scen.kind === 'no3d') rec.m.no3d = await page.evaluate(NO3D);
      else if (scen.kind === 'neg') rec.m.neg = await page.evaluate(NEG);
      else if (scen.kind === 'safety') rec.m.safety = await page.evaluate(SAFETY);
      else if (scen.kind === 'old') { await page.evaluate(() => window.scrollTo(0, 800)); await page.waitForTimeout(600); }
    }
    rec.errors = errors;
    rec.errorsOurs = errors.filter(e => /\/ds\/(js|css)\/home/.test(e.stack || ''));
  } catch (e) {
    rec.ok = false; rec.error = String(e.message).slice(0, 400); rec.errors = errors;
  }
  results.push(rec);
  await ctx.close();
}
await browser.close();
console.log('__JSON__' + JSON.stringify({ results }));
