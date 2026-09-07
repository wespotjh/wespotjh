/* ============================================================================
 * 계측 하네스 — 배시우 QA계측_칼륨_3차/4차 방법의 자동화판.
 *
 *   라이브 HTML(캐시) + `zg-ga4.js` + `detail-ui.js` 를 실제로 올리고
 *   `window.dataLayer` 를 받아 **이벤트 목록·파라미터 키**를 baseline 과 비교한다.
 *   합격 조건: 기존 이벤트 **소실 0** · **중복 0**.
 *
 * 시나리오는 config 의 `steps` 로 준다(클릭 셀렉터 목록).
 * ==========================================================================*/
import fs from 'node:fs';
import zlib from 'node:zlib';
import { chromium } from '/opt/node22/lib/node_modules/playwright/index.mjs';

const cfg = JSON.parse(fs.readFileSync(process.argv[2], 'utf8'));

function crc32(buf) {
  let c, t = [];
  for (let n = 0; n < 256; n++) { c = n; for (let k = 0; k < 8; k++) c = c & 1 ? 0xEDB88320 ^ (c >>> 1) : c >>> 1; t[n] = c >>> 0; }
  let x = 0xFFFFFFFF; for (let i = 0; i < buf.length; i++) x = t[(x ^ buf[i]) & 0xFF] ^ (x >>> 8);
  return (x ^ 0xFFFFFFFF) >>> 0;
}
function chunk(type, data) {
  const len = Buffer.alloc(4); len.writeUInt32BE(data.length);
  const td = Buffer.concat([Buffer.from(type, 'ascii'), data]);
  const crc = Buffer.alloc(4); crc.writeUInt32BE(crc32(td));
  return Buffer.concat([len, td, crc]);
}
let PNG = null;
function stub(w, h) {
  if (PNG) return PNG;
  const ihdr = Buffer.alloc(13); ihdr.writeUInt32BE(w, 0); ihdr.writeUInt32BE(h, 4); ihdr[8] = 8; ihdr[9] = 2;
  const row = Buffer.alloc(1 + w * 3, 0xDD); row[0] = 0;
  const raw = Buffer.concat(Array.from({ length: h }, () => row));
  PNG = Buffer.concat([Buffer.from([0x89,0x50,0x4E,0x47,0x0D,0x0A,0x1A,0x0A]),
        chunk('IHDR', ihdr), chunk('IDAT', zlib.deflateSync(raw)), chunk('IEND', Buffer.alloc(0))]);
  return PNG;
}
const ctypeFor = (u, f) => /\.css(\?|$)|type=css/.test(u) ? 'text/css; charset=utf-8'
  : (/\.js(\?|$)|type=js/.test(u) ? 'application/javascript; charset=utf-8' : (f || 'application/octet-stream'));

const browser = await chromium.launch();
const out = [];

for (const scen of cfg.scenarios) {
  const ctx = await browser.newContext({
    viewport: { width: scen.vp || 390, height: 900 }, userAgent: cfg.ua,
    isMobile: (scen.vp || 390) <= 767, hasTouch: (scen.vp || 390) <= 767,
  });
  await ctx.route('**/*', async (route) => {
    const req = route.request(); const u = new URL(req.url());
    const key = u.pathname + (u.search || '');
    if (u.host !== 'zengenetics.co.kr') return route.abort();
    if (key === scen.docPath) return route.fulfill({ status: 200, contentType: 'text/html; charset=utf-8',
        body: fs.readFileSync(scen.fixture, 'utf8').replace(/env\(\s*safe-area-inset-bottom[^)]*\)/g, '0px') });
    if (cfg.ours[key]) return route.fulfill({ status: 200, contentType: ctypeFor(key),
        body: fs.readFileSync(cfg.ours[key], 'utf8').replace(/env\(\s*safe-area-inset-bottom[^)]*\)/g, '0px') });
    if (req.resourceType() === 'image' || /\.(png|jpe?g|gif|webp|svg)(\?|$)/i.test(key))
      return route.fulfill({ status: 200, contentType: 'image/png', body: stub(640, 948) });
    const a = (scen.assets || cfg.assets)[key];
    if (a && a.status === 200 && fs.existsSync(a.file))
      return route.fulfill({ status: 200, contentType: ctypeFor(key, a.ctype), body: fs.readFileSync(a.file) });
    return route.abort();
  });
  const page = await ctx.newPage();
  const errors = [];
  page.on('pageerror', e => errors.push({ msg: String(e.message).slice(0, 160), stack: String(e.stack || '').slice(0, 300) }));
  const rec = { name: scen.name, docPath: scen.docPath, ok: true };
  try {
    await page.goto('https://zengenetics.co.kr' + scen.docPath, { waitUntil: 'load', timeout: 60000 });
    await page.waitForTimeout(scen.settle || 1200);
    rec.boot = await page.evaluate(() => ({
      hasDataLayer: Array.isArray(window.dataLayer),
      gaLoaded: !!window.__ZG_GA4_LOADED__ || (Array.isArray(window.dataLayer) && window.dataLayer.length > 0),
      uiLoaded: !!window.__ZG_DETAIL_UI__,
    }));
    for (const step of (scen.steps || [])) {
      try {
        if (step === '__scroll__') {
          /* 스크롤 계측(zg_scroll_depth)을 결정적으로 발사시킨다 */
          await page.evaluate(async () => {
            const H = document.documentElement.scrollHeight;
            for (let y = 0; y <= H; y += Math.max(400, window.innerHeight)) {
              window.scrollTo(0, y); await new Promise(r => setTimeout(r, 90));
            }
          });
          await page.waitForTimeout(600);
        } else {
          await page.evaluate((sel) => {
            const el = document.querySelector(sel);
            if (el) el.click(); else window.__ZG_STEP_MISS__ = (window.__ZG_STEP_MISS__ || []).concat(sel);
          }, step);
          await page.waitForTimeout(400);
        }
      } catch (e) { /* 스텝 실패는 아래 stepMiss 로 드러난다 */ }
    }
    rec.stepMiss = await page.evaluate(() => window.__ZG_STEP_MISS__ || []);
    rec.dl = await page.evaluate(() => {
      const norm = (v) => {
        if (v === null || v === undefined) return v;
        if (Array.isArray(v)) return v.map(norm);
        if (typeof v === 'object') { const o = {}; for (const k of Object.keys(v).sort()) o[k] = norm(v[k]); return o; }
        return v;
      };
      return (window.dataLayer || []).map(a => {
        if (a && a.length !== undefined && typeof a[0] === 'string') {
          return { kind: a[0], name: a[1] === undefined ? null : (typeof a[1] === 'object' ? '(obj)' : String(a[1])),
                   params: a[2] && typeof a[2] === 'object' ? norm(a[2]) : null };
        }
        return { kind: '(raw)', name: null, params: norm(a) };
      });
    });
  } catch (e) { rec.ok = false; rec.error = String(e.message).slice(0, 300); }
  rec.errors = errors;
  rec.errorsOurs = errors.filter(e => /detail-ui\.js|zg-ga4\.js|\/ds\//.test(e.stack || ''));
  out.push(rec);
  await ctx.close();
}
await browser.close();
console.log('__JSON__' + JSON.stringify({ results: out }));
