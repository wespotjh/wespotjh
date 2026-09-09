# -*- coding: utf-8 -*-
u"""
실렌더용 픽스처 조립.

라이브 HTML(= **옛** 템플릿이 카페24에서 렌더된 실제 DOM)에 **새 템플릿의 델타만** 얹는다.
델타는 git 으로 확인한 두 파일의 diff 가 전부다:

  `git diff b2912fb^ b2912fb -- cafe24-skin/product/detail.html`
    ① `.detail-container` 를 `<div class="zg-detail">` 로 감싼다
    ② `.name-top` 앞에 `<div class="zg-brand"></div>`
    ③ `.summary-info` 뒤에 `<ul class="zg-badges"></ul>`
  `git diff … cafe24-skin/moa/import/product_detail/detail.html`
    ④ `#prdDetail` 의 상세설명 div 를 `.zg-fold`(+`.zg-veil`/`.zg-more`) 로 감싸고
       앞에 `.zg-dh`, `#related` 앞에 `.zg-guide` · `.zg-note` 를 넣는다

④ 의 마크업 조각은 **하드코딩하지 않고 실제 템플릿 파일에서 잘라 온다.**
템플릿이 바뀌면 하네스도 따라 바뀐다. 잘라내기에 실패하면 예외를 던져 C 스위트가
통째로 FAIL 한다 — 조용히 "측정할 게 없어서 통과"하지 않는다.
"""
import bisect, hashlib, json, os, re
from .common import BUILD, SKIN, read
from . import fetch

IMPORT_TPL = 'moa/import/product_detail/detail.html'


def _fragments():
    u"""④ 델타의 마크업 조각을 실제 템플릿에서 추출."""
    t = read(os.path.join(SKIN, IMPORT_TPL))
    # 주석 제거(템플릿 주석은 DOM 에 영향 없음)
    t = re.sub(r'<!--.*?-->', '', t, flags=re.S)
    body = re.search(r'<div id="prdDetail"[^>]*>(.*)</div>\s*$', t, re.S)
    if not body:
        raise RuntimeError(u'델타④: #prdDetail 본문을 못 찾았다 — %s' % IMPORT_TPL)
    inner = body.group(1)

    dh = re.search(r'(<div class="zg-dh">(?:(?!<div\b).)*?</div>)', inner, re.S)
    if not dh:
        raise RuntimeError(u'델타④: .zg-dh 조각을 못 찾았다')
    veil = re.search(r'(<div class="zg-veil">.*?</div>)', inner, re.S)
    if not veil:
        raise RuntimeError(u'델타④: .zg-veil 조각을 못 찾았다')
    guide = re.search(r'(<div class="zg-guide">(?:(?!<div\b).)*?</div>)', inner, re.S)
    if not guide:
        raise RuntimeError(u'델타④: .zg-guide 조각을 못 찾았다')
    note = re.search(r'(<p class="zg-note">.*?</p>)', inner, re.S)
    if not note:
        raise RuntimeError(u'델타④: .zg-note 조각을 못 찾았다')

    frag = {'dh': dh.group(1), 'veil': veil.group(1),
            'guide': guide.group(1), 'note': note.group(1)}
    for k, v in frag.items():
        if not v.strip():
            raise RuntimeError(u'델타④: %s 조각이 비었다' % k)
    return frag


def _delta_script():
    f = _fragments()
    return u"""
<script>/* ZG-TEST: 새 템플릿 델타 — git diff b2912fb^..b2912fb 로 확인한 것만 적용 */
(function(){
  var D = %s;
  var report = {err: null};
  try {
    /* ① .detail-container 를 .zg-detail 로 감싼다 */
    var dc = document.querySelector('.detail-container');
    if (dc && !document.querySelector('.zg-detail')) {
      var w = document.createElement('div'); w.className = 'zg-detail';
      dc.parentNode.insertBefore(w, dc); w.appendChild(dc);
    }
    /* ② .name-top 앞 .zg-brand */
    var nt = document.querySelector('.name-top');
    if (nt && !document.querySelector('.zg-brand')) {
      var b = document.createElement('div'); b.className = 'zg-brand';
      nt.parentNode.insertBefore(b, nt);
    }
    /* ③ .summary-info 뒤 .zg-badges */
    var si = document.querySelector('.summary-info');
    if (si && !document.querySelector('.zg-badges')) {
      var u = document.createElement('ul'); u.className = 'zg-badges';
      si.parentNode.insertBefore(u, si.nextSibling);
    }
    /* ④ #prdDetail 접기 래퍼 */
    var host = document.getElementById('prdDetail');
    if (host && !host.querySelector('.zg-fold')) {
      var first = null, kids = host.children;
      for (var i = 0; i < kids.length; i++) {
        if (kids[i].id === 'related') break;
        if (kids[i].tagName === 'DIV' && kids[i].querySelector('img')) { first = kids[i]; break; }
      }
      if (first) {
        var fold = document.createElement('div');
        fold.className = 'zg-fold'; fold.id = 'zgFold';
        host.insertBefore(fold, first);
        fold.appendChild(first);
        fold.insertAdjacentHTML('beforeend', D.veil);
        fold.insertAdjacentHTML('beforebegin', D.dh);
        var rel = document.getElementById('related');
        if (rel) rel.insertAdjacentHTML('beforebegin', D.guide + D.note);
        else host.insertAdjacentHTML('beforeend', D.guide + D.note);
      }
    }
  } catch (e) { report.err = String(e); }
  window.__ZG_TEST_DELTA__ = {
    err: report.err,
    zgDetail: document.querySelectorAll('.zg-detail').length,
    zgBrand:  document.querySelectorAll('.zg-brand').length,
    zgBadges: document.querySelectorAll('.zg-badges').length,
    zgFold:   document.querySelectorAll('.zg-fold').length,
    zgMore:   document.querySelectorAll('.zg-more').length,
    zgChip:   document.querySelectorAll('.zg-chip').length
  };
})();
</script>
""" % json.dumps(f, ensure_ascii=False)


OUR_CSS = u'<link rel="stylesheet" href="/ds/css/detail.css">\n'
OUR_JS  = u'<script src="/ds/js/detail-ui.js"></script>\n'
GA4_JS  = u'<script src="/ds/js/zg-ga4.js"></script>\n'

OURS = {
    '/ds/css/detail.css':  os.path.join(SKIN, 'ds/css/detail.css'),
    '/ds/js/detail-ui.js': os.path.join(SKIN, 'ds/js/detail-ui.js'),
    '/ds/js/zg-ga4.js':    os.path.join(SKIN, 'ds/js/zg-ga4.js'),
    '/ds/css/price.css':   os.path.join(SKIN, 'ds/css/price.css'),
}

# 주입 방식으로 검사하는 파일들 — 아직 라이브 번들에 없다. 들어가는 순간
# 이 하네스는 '작업본'이 아니라 '라이브본 + 작업본 중복'을 보게 되므로 감시한다.
HOME_OURS = {
    '/ds/css/home.css':       os.path.join(SKIN, 'ds/css/home.css'),
    '/ds/js/home-blocks.js':  os.path.join(SKIN, 'ds/js/home-blocks.js'),
    '/ds/js/home-hero.js':    os.path.join(SKIN, 'ds/js/home-hero.js'),
}
LOCAL = dict(OURS)
LOCAL.update(HOME_OURS)


# ============================================================================
# 라이브 번들 소독 (2026-09-09)
# ----------------------------------------------------------------------------
# 9/9 배포로 우리 파일이 카페24 `optimizer_user.php` 번들 **안**에 들어갔다.
# 라이브 HTML 을 그대로 쓰는 이 하네스가 우리 파일을 한 번 더 주입하면 두 가지가 깨진다.
#
#   (1) 계측 중복 — `zg-ga4.js` 가 번들+주입으로 2번 돌아 이벤트가 2배로 발사된다.
#   (2) **작업본이 아니라 라이브본을 검사한다** — 번들이 주입 링크보다 뒤에 오므로
#       동일 특정도면 번들(=라이브본)이 이긴다. 로컬에서 지운 선언이 계속 살아 있고,
#       배포 전 검증 도구가 "이미 배포된 것"을 재확인하는 꼴이 된다.
#
# 그래서 서빙 전에 번들에서 **우리 파일이 차지한 구간을 찾아**
#   · CSS  → 그 자리를 **작업본 원문으로 교체**한다.
#     (자리를 옮기지 않는 이유: detail.css 는 라이브 번들 오프셋 1 — 스킨 CSS 보다 **앞**이다.
#      잘라내고 뒤에 붙이면 캐스케이드 순서가 라이브와 달라진다. 제자리 교체가 유일하게 충실하다.)
#   · JS   → 그 자리를 **들어낸다**. 실행 주체는 주입한 `<script src="/ds/...">` 하나뿐이다.
#     (교체가 아니라 들어내는 이유 둘: ① `with_ui=False`/`with_ga4=False` 시나리오가
#      "그 파일을 안 올린 상태"를 실제로 만들 수 있어야 한다. ② 브라우저 스택트레이스가
#      `/ds/js/detail-ui.js` 로 남아야 render.mjs·datalayer.mjs 의 `errorsOurs`
#      (우리 파일에서 난 예외만 우리 책임) 분류가 계속 작동한다. 번들 안에서 돌면
#      스택이 optimizer_user.php 가 되어 우리 예외가 0 으로 보이는 **거짓 통과**가 된다.)
#
# 구간을 못 찾으면 **예외를 던진다.** 조용히 넘어가면 지금과 똑같은 함정이 다시 생긴다.
# ============================================================================

# url -> (로컬 작업본 경로 키, 종류, 처리)  처리: 'replace' = 작업본으로 교체 / 'strip' = 들어냄
BUNDLED = [
    ('/ds/css/detail.css',  'css', 'replace'),
    ('/ds/css/price.css',   'css', 'replace'),
    ('/ds/js/detail-ui.js', 'js',  'strip'),
    ('/ds/js/zg-ga4.js',    'js',  'strip'),
]

ANCHOR = 160          # 앞·뒤 앵커 길이(공백 제거 기준)
MINREF = 200          # 이보다 짧은 참조본은 위치 식별에 못 쓴다


def _decomment(text, kind):
    u"""CSS 번들은 블록 주석을 지운다 — 길이를 보존하며 공백으로 바꿔 원문 인덱스를 지킨다."""
    if kind != 'css':
        return text
    return re.sub(r'/\*.*?\*/', lambda m: u' ' * len(m.group(0)), text, flags=re.S)


def _norm(text, kind):
    u"""공백을 모두 제거한 비교용 문자열. 번들이 축약을 해도 같은 자리를 찾게 해 준다."""
    return re.sub(r'\s+', u'', _decomment(text, kind))


_SEG = {}
_NORM = {}
_SANI = {}


def _normc(text, kind, key):
    u"""정규화 결과 캐시 — 같은 번들을 여러 번 훑으므로."""
    k = (key, kind)
    if k not in _NORM:
        _NORM[k] = _norm(text, kind)
    return _NORM[k]


def _segmap(text, kind, key):
    u"""정규화 위치 -> 원문 위치 역매핑표. (비싸므로 실제로 매칭된 번들만 만든다)"""
    if key in _SEG:
        return _SEG[key]
    t = _decomment(text, kind)
    ns, os_ = [], []
    n = 0
    for m in re.finditer(r'\S+', t):
        ns.append(n); os_.append(m.start())
        n += m.end() - m.start()
    _SEG[key] = (ns, os_)
    return _SEG[key]


def _to_orig(seg, npos):
    ns, os_ = seg
    i = bisect.bisect_right(ns, npos) - 1
    if i < 0:
        return 0
    return os_[i] + (npos - ns[i])


def _hit(nb, nref):
    u"""정규화 번들 nb 안에서 참조본 nref 의 구간을 찾는다. (n0, n1, 방법) 또는 (None, None, 사유)."""
    if len(nref) < MINREF:
        return None, None, 'ref-too-short'
    c = nb.count(nref)
    if c == 1:
        i = nb.find(nref)
        return i, i + len(nref), 'exact'
    if c > 1:
        return None, None, 'exact-ambiguous(%d)' % c
    h, t = nref[:ANCHOR], nref[-ANCHOR:]
    ch, ct = nb.count(h), nb.count(t)
    if ch == 1 and ct == 1:
        i, j = nb.find(h), nb.find(t) + len(t)
        if j > i:
            return i, j, 'anchor'
        return None, None, 'anchor-inverted'
    if ch or ct:
        return None, None, 'anchor-partial(head=%d tail=%d)' % (ch, ct)
    return None, None, 'absent'


def _refs(url, kind):
    u"""위치를 식별할 참조본 — ① 라이브 단독본(번들에 들어간 바로 그 원문) ② 작업본.
    둘 다 써서 서로 교차 검증한다. 서로 다른 구간을 가리키면 예외."""
    out = []
    try:
        meta = fetch.fetch_asset(url)
        if meta.get('status') == 200 and os.path.exists(meta['file']):
            body = open(meta['file'], 'rb').read().decode('utf-8', 'replace')
            if len(_norm(body, kind)) >= MINREF:
                out.append(('live', body))
    except Exception:
        pass
    lp = LOCAL.get(url)
    if lp and os.path.exists(lp):
        out.append(('work', read(lp)))
    return out


def _locate(bundle, bkey, url, kind):
    u"""번들에서 우리 파일 구간 (원문 start, end, 방법) 을 찾는다.
    번들에 아예 없으면 None. **있는 것 같은데 못 찾으면 예외** — 조용한 통과 금지."""
    nb = _normc(bundle, kind, bkey)
    found, hows, why = None, [], []
    for rname, ref in _refs(url, kind):
        n0, n1, how = _hit(nb, _norm(ref, kind))
        if n0 is None:
            why.append('%s:%s' % (rname, how))
            continue
        seg = _segmap(bundle, kind, bkey)
        o0, o1 = _to_orig(seg, n0), _to_orig(seg, n1 - 1) + 1
        hows.append('%s:%s' % (rname, how))
        if found is None:
            found = (o0, o1)
        elif found != (o0, o1):
            raise RuntimeError(
                u'번들 소독: %s 의 구간이 참조본마다 다르다 (%s vs %s) — 번들이 바뀐 것 같다. '
                u'./run.sh --refresh 로 라이브를 다시 받아라' % (url, found, (o0, o1)))
    if found:
        return found[0], found[1], '+'.join(hows)
    if all(w.endswith(':absent') for w in why) and why:
        return None
    raise RuntimeError(
        u'번들 소독 실패: %s 가 번들에 **들어 있는 것 같은데 구간을 못 찾았다** (%s).\n'
        u'  번들: %s\n'
        u'  그냥 넘어가면 우리 파일이 두 번 실행되거나(계측 중복) 라이브본이 작업본을 이긴다.\n'
        u'  ./run.sh --refresh 로 라이브·자산 캐시를 다시 받아 보고, 그래도 안 되면 '
        u'checks/fixture.py 의 BUNDLED/_hit 를 손봐라.' % (url, ', '.join(why) or 'no-ref', bkey))


def _kind(meta):
    u"""자산이 CSS 인지 JS 인지 — 둘 다 아니면 None. 번들 URL 은 확장자가 없어 type= 도 본다."""
    path = meta.get('file')
    if meta.get('status') != 200 or not path or not os.path.exists(path):
        return None
    ct = (meta.get('ctype') or '').lower()
    url = meta.get('url') or ''
    if 'css' in ct or re.search(r'\.css(\?|$)|type=css', url):
        return 'css'
    if 'javascript' in ct or 'ecmascript' in ct or re.search(r'\.js(\?|$)|type=js', url):
        return 'js'
    return None


def assert_not_bundled(ua, name, urls):
    u"""`urls` 가 라이브 번들 안에 들어와 있으면 예외.

    주입 방식(H 홈)으로 검사하는 파일이 배포되어 번들에 실리면, 주입본과 번들본이
    **둘 다** 걸려 JS 는 두 번 돌고 CSS 는 뒤에 오는 번들(=라이브본)이 이긴다.
    상세(C·D)가 2026-09-09 에 당한 바로 그 사고다. 조용히 넘기지 않는다."""
    doc = fetch.html(ua, name) or ''
    bad = []
    for u in fetch.same_origin_assets(doc):
        meta = fetch.fetch_asset(u)
        k = _kind(meta)
        if not k or (meta.get('url') or '') in LOCAL:
            continue
        raw = open(meta['file'], 'rb').read().decode('utf-8', 'replace')
        for our in urls:
            if (k == 'css') != our.endswith('.css'):
                continue
            r = _locate(raw, meta['file'], our, k)
            if r:
                bad.append('%s @ %s(+%d)' % (our, u[:60], r[0]))
    if bad:
        raise RuntimeError(
            u'%s/%s: 주입해서 검사하는 파일이 라이브 번들에도 들어 있다 — %s\n'
            u'  이대로 두면 JS 는 두 번 실행되고 CSS 는 라이브본이 작업본을 이긴다.\n'
            u'  checks/fixture.py 의 BUNDLED 에 넣어 소독 대상으로 돌려라.'
            % (ua, name, ' / '.join(bad)))
    return True


def _sanitize(meta, want):
    u"""자산 1개를 소독해 (파일경로, 처리내역) 을 돌려준다. 소독할 게 없으면 원본 그대로."""
    path = meta.get('file')
    kind = _kind(meta)
    if not kind:
        return meta, {}
    url = meta.get('url') or ''
    if url in LOCAL:                     # 우리 파일 원본 — `ours` 라우트가 작업본을 준다
        return meta, {}
    is_css = kind == 'css'
    ck = (path, tuple(sorted((k, bool(v)) for k, v in want.items())))
    if ck in _SANI:
        return _SANI[ck]
    raw = open(path, 'rb').read().decode('utf-8', 'replace')
    bkey = path
    cuts, done = [], {}
    for our, k, mode in BUNDLED:
        if k != kind:
            continue
        r = _locate(raw, bkey, our, kind)
        if not r:
            continue
        o0, o1, how = r
        if mode == 'replace' and want.get(our, True):
            body = u'\n' + read(OURS[our]) + u'\n'
        else:
            body = u'\n'
        cuts.append((o0, o1, body))
        done[our] = {'how': how, 'at': o0, 'len': o1 - o0, 'mode': mode,
                     'body': len(body)}
    if not cuts:
        _SANI[ck] = (meta, {})
        return _SANI[ck]
    cuts.sort(reverse=True)
    out = raw
    for o0, o1, body in cuts:
        out = out[:o0] + body + out[o1:]
    d = os.path.join(BUILD, 'asset')
    os.makedirs(d, exist_ok=True)
    sig = hashlib.md5((path + '|' + json.dumps(done, sort_keys=True)).encode('utf-8')).hexdigest()
    fp = os.path.join(d, sig + ('.css' if is_css else '.js'))
    with open(fp, 'wb') as f:
        f.write(out.encode('utf-8'))
    m2 = dict(meta); m2['file'] = fp; m2['zg_sanitized'] = done
    _SANI[ck] = (m2, done)
    return _SANI[ck]


class override(object):
    u"""우리 파일 한 개를 **사본으로 바꿔** 픽스처를 만드는 컨텍스트 매니저.

    음성 대조군 전용이다. 제품 파일은 건드리지 않는다 — `OURS` 가 가리키는 **경로**만 바꾼다.
    ⚠ 이게 필요한 이유: 2026-09-09 배포 이후 `detail.css` 는 라이브 번들 **안**에 있고,
      `build()` 는 번들 안 그 구간을 `OURS[url]` 의 내용으로 **제자리 교체**한다.
      따라서 `<link href="/ds/css/detail.css">` 라우트만 바꿔치기하면 아무 효과가 없다
      (그 링크는 애초에 주입되지도 않는다). 소독 결과 캐시(`_SANI`)도 같이 비워야 한다.
    """

    def __init__(self, url, path):
        self.url, self.path, self.old = url, path, None

    def __enter__(self):
        self.old = OURS[self.url]
        OURS[self.url] = self.path
        LOCAL[self.url] = self.path
        _SANI.clear()
        return self

    def __exit__(self, *a):
        OURS[self.url] = self.old
        LOCAL[self.url] = self.old
        _SANI.clear()
        return False


def plan(ua='iphone', name='p11', with_ga4=False, with_ui=True):
    u"""이 픽스처가 쓸 자산 지도(소독본) + 우리 파일이 몇 번 실리는지를 함께 계산한다."""
    doc = fetch.html(ua, name) or ''
    want = {'/ds/css/detail.css': True, '/ds/css/price.css': True,
            '/ds/js/detail-ui.js': with_ui, '/ds/js/zg-ga4.js': with_ga4}
    assets, inbundle = {}, {}
    for u in fetch.same_origin_assets(doc):
        meta = fetch.fetch_asset(u)
        m2, done = _sanitize(meta, want)
        assets[u] = m2
        for our, info in done.items():
            inbundle.setdefault(our, []).append(dict(info, bundle=u))
    return {'assets': assets, 'inbundle': inbundle, 'want': want}


def build(ua='iphone', name='p11', with_ga4=False, delta=True, with_ui=True):
    doc = fetch.html(ua, name)
    if doc is None:
        raise RuntimeError(u'라이브 캐시 없음: %s/%s — ./run.sh --refresh 로 받아라' % (ua, name))
    diag = {'src_bytes': len(doc)}

    pl = plan(ua, name, with_ga4=with_ga4, with_ui=with_ui)
    inb = pl['inbundle']
    diag['assets'] = pl['assets']
    diag['inbundle'] = dict((k, [dict(x) for x in v]) for k, v in inb.items())

    # --- CSS: 번들 안에서 제자리 교체했으면 주입하지 않는다 (하면 중복 로드) ---
    css_in_bundle = len(inb.get('/ds/css/detail.css') or [])
    if css_in_bundle > 1:
        raise RuntimeError(u'번들 소독: detail.css 가 번들 %d곳에 있다 — 하네스가 감당 못 한다' % css_in_bundle)
    m = re.search(r'<link[^>]*optimizer_user\.php[^>]*>', doc, re.I)
    diag['css_anchor'] = bool(m)
    if not css_in_bundle:                       # 아직 라이브에 없다 → 예전처럼 주입
        if m:
            doc = doc[:m.start()] + OUR_CSS + doc[m.start():]
        else:
            doc = doc.replace('</head>', OUR_CSS + '</head>', 1)

    # --- JS: 번들에서는 항상 들어냈다. 실행 주체는 주입 한 번뿐 ---
    inject = ((_delta_script() if delta else u'')
              + (OUR_JS if with_ui else u'')
              + (GA4_JS if with_ga4 else u''))
    m = re.search(r'<script[^>]*optimizer_user\.php[^>]*>', doc, re.I)
    diag['js_anchor'] = bool(m)
    if m:
        doc = doc[:m.start()] + inject + doc[m.start():]
    else:
        doc = doc.replace('</body>', inject + '</body>', 1)

    # --- 우리 파일이 정확히 「원하는 만큼만」 실리는지 (중복 0 · 누락 0) ---
    served = {
        '/ds/css/detail.css':  css_in_bundle + (0 if css_in_bundle else 1),
        '/ds/css/price.css':   len(inb.get('/ds/css/price.css') or []),
        '/ds/js/detail-ui.js': (1 if with_ui else 0),
        '/ds/js/zg-ga4.js':    (1 if with_ga4 else 0),
    }
    diag['served'] = served
    for k in ('/ds/css/detail.css', '/ds/js/detail-ui.js', '/ds/js/zg-ga4.js'):
        want_n = 1 if (k == '/ds/css/detail.css' or (k == '/ds/js/detail-ui.js' and with_ui)
                       or (k == '/ds/js/zg-ga4.js' and with_ga4)) else 0
        if served[k] != want_n:
            raise RuntimeError(u'픽스처 %s/%s: %s 가 %d번 실린다 (기대 %d)' % (ua, name, k, served[k], want_n))

    os.makedirs(BUILD, exist_ok=True)
    tag = '%s-%s%s%s%s' % (ua, name, '-ga4' if with_ga4 else '',
                           '' if delta else '-nodelta', '' if with_ui else '-noui')
    out = os.path.join(BUILD, 'fixture-%s.html' % tag)
    with open(out, 'wb') as f:
        f.write(doc.encode('utf-8'))
    diag['out'] = out
    diag['out_bytes'] = len(doc)
    return out, diag


def asset_map(ua='iphone', name='p11', with_ga4=False, with_ui=True):
    u"""**소독된** 자산 지도. 번들 안의 우리 구간은 작업본으로 바뀌었거나(CSS) 들어내졌다(JS)."""
    return plan(ua, name, with_ga4=with_ga4, with_ui=with_ui)['assets']


def write_cfg(tag, doc_path, fixture, scenarios, ua_key='iphone', name='p11', stub=None,
              assets=None):
    cfg = {'fixture': fixture, 'docPath': doc_path, 'ua': fetch.UA[ua_key],
           'assets': assets if assets is not None else asset_map(ua_key, name),
           'ours': OURS,
           'stub': stub or {'w': 640, 'h': 948}, 'scenarios': scenarios}
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, 'cfg-%s.json' % tag)
    with open(p, 'wb') as f:
        f.write(json.dumps(cfg, ensure_ascii=False).encode('utf-8'))
    return p
