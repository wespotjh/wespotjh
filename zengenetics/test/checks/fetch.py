# -*- coding: utf-8 -*-
u"""
라이브 수집기 (느린 검사). Playwright 는 zengenetics.co.kr 에 막혀 있어 **curl 만** 쓴다.

- 받은 응답은 `cache/live/` 에 저장하고, 이후 실행은 캐시를 쓴다.
- `--refresh` 를 주면 다시 받는다.
- 실렌더(C)·계측(D) 이 쓰는 자산 번들도 여기서 함께 받아 둔다.
"""
import json, os, re, subprocess, sys, urllib.parse
from .common import CACHE, sh

BASE = 'https://zengenetics.co.kr'
LIVE = os.path.join(CACHE, 'live')
ASSET = os.path.join(CACHE, 'asset')

UA = {
    'iphone':  'Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 Mobile/15E148 Safari/604.1',
    'android': 'Mozilla/5.0 (Linux; Android 14; SM-S918N) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36',
    'desktop': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
}

# 라이브 판매·노출 중인 상품 **전 13종**. 같은 `product/detail.html` 하나가 13개를 다 렌더한다
# → 한 곳을 고치면 13개가 동시에 바뀐다. 9종만 보던 시절에 34·60·91·93 이 사각지대였다.
#   A군(옵션+추가상품) 11 13 16 63 64 71 98 · B군(옵션 없음, 단가 있음) 60 61 62
#   C군(판매 상품 아님 — 이벤트·혜택 안내) 34 91 93
#   104 는 2026-09-11 에 새로 올라온 상품(추석 감사제)이다. 하네스가 모르고 있었고,
#   그 사이 합계에 **가짜 할인 39,000원**이 떠 있었다. 새 상품은 여기에 반드시 넣는다.
PRODUCTS = [11, 13, 16, 34, 60, 61, 62, 63, 64, 71, 91, 93, 98, 104]
PAGES = ([('p%d' % n, '/product/detail.html?product_no=%d' % n) for n in PRODUCTS]
         + [('home', '/'),
            ('orderform', '/order/orderform.html'),
            ('order_result', '/order/order_result.html'),
            ('basket', '/order/basket.html')])


def _path(ua, name):
    return os.path.join(LIVE, ua, name + '.html')


def _meta(ua, name):
    return os.path.join(LIVE, ua, name + '.json')


def fetch_page(ua, name, url, refresh=False, timeout=60):
    os.makedirs(os.path.join(LIVE, ua), exist_ok=True)
    fp, mp = _path(ua, name), _meta(ua, name)
    if os.path.exists(fp) and os.path.exists(mp) and not refresh:
        return json.load(open(mp))
    cmd = ['curl', '-sS', '--compressed', '-L', '--max-time', str(timeout),
           '-o', fp, '-w', '%{http_code} %{size_download} %{num_redirects}',
           '-H', 'User-Agent: ' + UA[ua], '-H', 'Accept-Language: ko-KR,ko;q=0.9',
           BASE + url]
    rc, out = sh(cmd, timeout=timeout + 30)
    parts = (out.strip().split() + ['0', '0', '0'])[:3]
    meta = {'ua': ua, 'name': name, 'url': url, 'rc': rc,
            'status': int(parts[0] or 0), 'bytes': int(parts[1] or 0),
            'redirects': int(parts[2] or 0)}
    json.dump(meta, open(mp, 'w'))
    return meta


# 우리 파일의 **라이브 단독본**. 2026-09-09 배포로 이 파일들이 optimizer_user.php 번들 안에
# 들어갔고, fixture.py 는 번들에서 우리 구간을 찾을 때 이 원문을 기준 참조본으로 쓴다.
# → 페이지 캐시를 새로 받을 때 **같이** 새로 받아야 번들과 어긋나지 않는다.
OURS_LIVE = ['/ds/css/detail.css', '/ds/css/price.css',
             '/ds/js/detail-ui.js', '/ds/js/zg-ga4.js',
             '/ds/css/home.css', '/ds/js/home-blocks.js', '/ds/js/home-hero.js']


def fetch_all(refresh=False, uas=('iphone', 'android', 'desktop'), log=print):
    got = {}
    for ua in uas:
        for name, url in PAGES:
            m = fetch_page(ua, name, url, refresh)
            got[(ua, name)] = m
            if refresh:
                log('  fetch %-8s %-14s -> %s (%s B)' % (ua, name, m['status'], m['bytes']))
    if refresh:
        for u in OURS_LIVE:
            m = fetch_asset(u, refresh=True)
            log('  fetch ours    %-22s -> %s' % (u, m['status']))
    return got


PREVIEW_P11 = 'https://wespotjo.cafe24.com/skin-skin10/product/detail.html?product_no=11&cate_no=42&display_group=1'
KAKAO_RE = re.compile(r'id="kakaoKey"[^>]*>\s*([^<]*?)\s*</div>')
KAKAO_FMT = re.compile(r'^[0-9a-f]{32}$')


def kakao_keys():
    u"""#kakaoKey 값 — 라이브(캐시 p11) 와 미리보기 작업본(skin10, **매번** 받는다)."""
    out = {'live': None, 'preview': None, 'preview_status': None}
    doc = html('iphone', 'p11') or ''
    m = KAKAO_RE.search(doc)
    out['live'] = m.group(1) if m else None
    os.makedirs(os.path.join(LIVE, 'iphone'), exist_ok=True)
    fp = os.path.join(LIVE, 'iphone', 'preview_p11.html')
    cmd = ['curl', '-sS', '--compressed', '-L', '--max-time', '60', '-o', fp, '-w', '%{http_code}',
           '-H', 'User-Agent: ' + UA['iphone'], '-H', 'Accept-Language: ko-KR,ko;q=0.9', PREVIEW_P11]
    rc, o = sh(cmd, timeout=90)
    try:
        out['preview_status'] = int((o or '0').strip().split()[0])
    except Exception:
        out['preview_status'] = 0
    if os.path.exists(fp):
        m = KAKAO_RE.search(open(fp, 'rb').read().decode('utf-8', 'replace'))
        out['preview'] = m.group(1) if m else None
    out['preview_ok'] = bool(out['preview']) and bool(KAKAO_FMT.match(out['preview'])) \
        and out['preview'] == out['live']
    return out


def html(ua, name):
    fp = _path(ua, name)
    if not os.path.exists(fp):
        return None
    return open(fp, 'rb').read().decode('utf-8', 'replace')


# ---------------------------------------------------------------- 자산 캐시
def asset_key(url):
    import hashlib
    return hashlib.md5(url.encode('utf-8')).hexdigest()


def fetch_asset(url, refresh=False, timeout=90):
    u"""동일출처 자산 1개를 받아 캐시. (url, 로컬경로, status) 반환."""
    os.makedirs(ASSET, exist_ok=True)
    k = asset_key(url)
    fp = os.path.join(ASSET, k)
    mp = fp + '.json'
    if os.path.exists(fp) and os.path.exists(mp) and not refresh:
        return json.load(open(mp))
    cmd = ['curl', '-sS', '--compressed', '-L', '--max-time', str(timeout),
           '-o', fp, '-w', '%{http_code} %{content_type}',
           '-H', 'User-Agent: ' + UA['iphone'], BASE + url if url.startswith('/') else url]
    rc, out = sh(cmd, timeout=timeout + 30)
    tok = out.strip().split()
    meta = {'url': url, 'file': fp, 'status': int(tok[0] or 0) if tok else 0,
            'ctype': tok[1] if len(tok) > 1 else ''}
    json.dump(meta, open(mp, 'w'))
    return meta


def same_origin_assets(doc):
    u"""문서에서 동일출처 <script src> / <link rel=stylesheet href> 를 뽑는다."""
    urls = []
    for m in re.finditer(r'<script[^>]+src=["\']([^"\']+)["\']', doc, re.I):
        urls.append(m.group(1))
    for m in re.finditer(r'<link[^>]+href=["\']([^"\']+)["\']', doc, re.I):
        tag = m.group(0)
        if 'stylesheet' in tag.lower():
            urls.append(m.group(1))
    out = []
    for u in urls:
        if u.startswith('//') or u.startswith('http'):
            if 'zengenetics.co.kr' not in u:
                continue
            u = re.sub(r'^https?://[^/]+', '', re.sub(r'^//', 'https://', u))
        if not u.startswith('/'):
            continue
        out.append(u)
    # 중복 제거, 순서 유지
    seen, res = set(), []
    for u in out:
        if u not in seen:
            seen.add(u); res.append(u)
    return res


def fetch_fixture_assets(ua='iphone', name='p11', refresh=False, log=print):
    doc = html(ua, name)
    if doc is None:
        return []
    urls = same_origin_assets(doc)
    metas = []
    for u in urls:
        metas.append(fetch_asset(u, refresh))
    if refresh:
        log('  fixture assets: %d개' % len(metas))
    return metas


def ihdr_width(url, refresh=False):
    u"""PNG/JPEG 헤더만 Range 로 받아 폭을 읽는다 (전체 다운로드 회피)."""
    os.makedirs(ASSET, exist_ok=True)
    k = asset_key('HDR' + url)
    fp = os.path.join(ASSET, k)
    if not os.path.exists(fp) or refresh:
        full = url if url.startswith('http') else (BASE + url)
        sh(['curl', '-sS', '-r', '0-4095', '--max-time', '30', '-o', fp,
            '-H', 'User-Agent: ' + UA['iphone'], full], timeout=60)
    try:
        d = open(fp, 'rb').read()
    except Exception:
        return None
    if d[:8] == b'\x89PNG\r\n\x1a\n' and d[12:16] == b'IHDR':
        return int.from_bytes(d[16:20], 'big')
    if d[:2] == b'\xff\xd8':                       # JPEG
        i = 2
        while i + 9 < len(d):
            if d[i] != 0xFF:
                i += 1; continue
            m = d[i + 1]
            if m in (0xC0, 0xC1, 0xC2, 0xC3):
                return int.from_bytes(d[i + 7:i + 9], 'big')
            if m in (0xD8, 0xD9) or 0xD0 <= m <= 0xD7:
                i += 2; continue
            ln = int.from_bytes(d[i + 2:i + 4], 'big')
            i += 2 + ln
    return None
