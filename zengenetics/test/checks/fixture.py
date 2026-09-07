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
import json, os, re
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


def build(ua='iphone', name='p11', with_ga4=False, delta=True, with_ui=True):
    doc = fetch.html(ua, name)
    if doc is None:
        raise RuntimeError(u'라이브 캐시 없음: %s/%s — ./run.sh --refresh 로 받아라' % (ua, name))
    diag = {'src_bytes': len(doc)}

    m = re.search(r'<link[^>]*optimizer_user\.php[^>]*>', doc, re.I)
    diag['css_anchor'] = bool(m)
    if m:
        doc = doc[:m.start()] + OUR_CSS + doc[m.start():]
    else:
        doc = doc.replace('</head>', OUR_CSS + '</head>', 1)

    inject = ((_delta_script() if delta else u'')
              + (OUR_JS if with_ui else u'')
              + (GA4_JS if with_ga4 else u''))
    m = re.search(r'<script[^>]*optimizer_user\.php[^>]*>', doc, re.I)
    diag['js_anchor'] = bool(m)
    if m:
        doc = doc[:m.start()] + inject + doc[m.start():]
    else:
        doc = doc.replace('</body>', inject + '</body>', 1)

    os.makedirs(BUILD, exist_ok=True)
    tag = '%s-%s%s%s%s' % (ua, name, '-ga4' if with_ga4 else '',
                           '' if delta else '-nodelta', '' if with_ui else '-noui')
    out = os.path.join(BUILD, 'fixture-%s.html' % tag)
    with open(out, 'wb') as f:
        f.write(doc.encode('utf-8'))
    diag['out'] = out
    diag['out_bytes'] = len(doc)
    return out, diag


def asset_map(ua='iphone', name='p11'):
    doc = fetch.html(ua, name) or ''
    return {u: fetch.fetch_asset(u) for u in fetch.same_origin_assets(doc)}


def write_cfg(tag, doc_path, fixture, scenarios, ua_key='iphone', name='p11', stub=None):
    cfg = {'fixture': fixture, 'docPath': doc_path, 'ua': fetch.UA[ua_key],
           'assets': asset_map(ua_key, name), 'ours': OURS,
           'stub': stub or {'w': 640, 'h': 948}, 'scenarios': scenarios}
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, 'cfg-%s.json' % tag)
    with open(p, 'wb') as f:
        f.write(json.dumps(cfg, ensure_ascii=False).encode('utf-8'))
    return p
