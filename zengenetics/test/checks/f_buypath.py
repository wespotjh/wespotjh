# -*- coding: utf-8 -*-
u"""
F. 구매 경로 검사 — 13종 전수. **「보이는가」가 아니라 「눌렀을 때 무엇이 발사되는가」.**

왜 생겼나 (2026-09-09)
  같은 `product/detail.html` 하나가 **13개 상품을 전부 렌더**한다. 그런데 회귀 하네스는
  9종(11 13 16 61 62 63 64 71 98)만 보고 있었고, 34·60·91·93 이 사각지대였다.
  13종으로 넓히자마자 사각지대에서 결함이 나왔다 — 34·91·93 은 **팔지 않는 안내 페이지**인데
  카페24가 인라인 버튼만 죽이고 **하단 고정바의 「구매하기」에는 그 표시를 안 준다.**
  12차 B안으로 리뷰 칩·장바구니가 빠지면서 화면 폭을 가득 채운 커다란 버튼이
  **눌러도 아무 일도 안 하는 상태**가 됐다. → `isUnsellable()` + `.zg-bar--dead` 로 바를 내렸다.

  그 수정은 **양날**이다. 판정이 과하면 팔 수 있는 10종에서 바가 사라져 **매출이 죽는다.**
  그래서 이 스위트는 두 방향을 동시에 잰다.

무엇을 어떻게 재나
  `window.product_submit` 과 `window.PRODUCTSUBMIT.sendLoginPage` 를 **둘 다 스텁으로 갈아끼우고**
  실제로 눌러 호출 인자를 기록한다. 주문·이동은 만들지 않는다.
  「어디로도 가지 않았음」의 증명을 위해 form submit · window.open · location.assign/replace ·
  프레임 내비게이션까지 전부 가로챈다.

  화면 상태는 스킨 `checkScroll()` 원문 그대로 계산한다:
      top = $('.infoArea').offset().top + $('.infoArea').outerHeight()
      scrollTop > top → `.mobile-layer.fixed`  → 바 「구매하기」가 **시트를 연다**
      그 이하                                  → `mobileLayerOn()` 이 인라인 버튼에 **위임**한다

  ⚠ 2026-09-11 개편으로 **위임 분기는 폐기됐다.**
     상단 구매 블록을 감췄기 때문에 위임할 인라인 버튼이 화면에 없다. 그 상태로 두면
     최상단에서 「구매하기」를 눌렀을 때 옵션이 안 골라진 채 결제가 시도돼
     「옵션을 선택해 주세요」 만 뜨고 끝난다 — 실제로 구매 경로가 막혔다.
     → `detail-ui.js` 의 `armSheetOpen()` 이 바 클릭을 캡처 단계에서 받아
       `.fixed` 를 먼저 붙인다. 이제 **어느 스크롤 위치에서든 시트가 열린다.**
     그래서 `top`·`bnd-3` 의 기대값은 「시트 열림 True · barBuy 발사 없음」 이다.
     판매 상품이 아닌 페이지(C군)에서는 `zg-bar--dead` 가드로 열지 않는다.

왜 13종 × 6폭 × 6상태를 매번 돌리지 않나 (표본 축소의 근거)
  전수(13종 × 6폭 × 6상태 = 468셀)를 2026-09-09 에 **한 번 실측**했다. 결과:
    · 320·390·414·768·1023 은 **전 상품에서 완전히 동일**했다 (CSS 분기가 `max-width:1023px`
      하나뿐이고 JS 에 폭 분기가 없다). → 대표로 390 · 1023 · 1280 만 남긴다.
    · `top` 과 `bnd-3` 은 같은 `.fixed=false` 분기, `bnd+3`·`mid`·`bottom` 은 같은 `.fixed=true`
      분기였다. → 각 분기 대표 1개씩 + 경계 직전(`bnd-3`)을 남긴다.
    · 같은 그룹 안의 상품들은 **구매 마크업이 글자 단위로 같은 모양**이었다.
  마지막 한 줄이 표본 축소의 유일한 근거라서, 그 전제를 **매 실행 F0 이 13종 전수로 다시 확인한다.**
  표본 밖 상품의 지문이 대표와 갈리는 순간 F0 이 FAIL 하고 "렌더 표본에 추가하라"고 말한다.
  (표본에 든 상품 자체는 직접 렌더하므로 이 대조에서 뺀다 — 71 이 sendLoginPage 라 대표와 다른데,
   그건 결함이 아니라 71 을 표본에 넣은 이유다.)
  (F0 은 라이브 캐시를 읽는 정적 검사라 0.1초다 — 전수를 포기한 게 아니라 **싸게 전수한다.**)

음성 대조군 (규칙을 빼면 FAIL 이 나는가)
  · `F9.css`  — `.zg-bar--dead{display:none}` 을 **뺀 CSS 사본**을 서빙하면 34 의 바가 다시 보여야 한다.
                안 보이면 이 검사는 CSS 규칙을 재고 있는 게 아니다.
  · `F9.kill` — 팔 수 있는 상품(11)의 인라인 두 버튼을 죽이면 `zg-bar--dead` 가 **붙어야** 한다.
                안 붙으면 판정이 상품번호에 하드코딩된 것이지 실제 신호를 보는 게 아니다.
  제품 파일은 손대지 않는다. CSS 사본은 `build/` 에 만들어 서빙하고, DOM 변조는 페이지 안에서만 한다.
"""
import json, os, re, shutil
from .common import Suite, ROOT, BUILD, OUT, SKIN, node, read
from . import fixture, fetch

UA = 'iphone'

# ---------------------------------------------------------------- 실렌더 표본
#   (상품, 폭, 상태) — 무엇을 왜 넣었는지는 위 문서화 참조.
SAMPLE = [
    # 11: 기준 상품(옵션 + 추가상품). 폭 분기(≤1023 / ≥1024)를 여기서만 전부 본다.
    ('p11', 390,  ['top', 'bnd-3', 'bnd+3', 'sheet']),
    ('p11', 1023, ['top', 'bnd+3']),
    ('p11', 1280, ['top']),
    # 71: **13종 중 유일하게 `PRODUCTSUBMIT.sendLoginPage`** 를 쓴다(회원 전용). 한 번도 검증된 적 없다.
    ('p71', 390,  ['top', 'bnd-3', 'bnd+3', 'sheet']),
    # 61: B군(옵션 select 없음) 대표. `buildOptionCards()` 가 일찍 반환하는 경로.
    ('p61', 390,  ['top', 'bnd-3', 'bnd+3', 'sheet']),
    # 98: A군 최대 케이스 — 갤러리 7장(R-9/R-10 상한). 1280 은 좌측 세로 썸네일 7장을 재려고 넣는다.
    ('p98', 390,  ['top', 'bnd+3']),
    ('p98', 1280, ['top']),
    # 34: C군 대표(팔지 않는 페이지). 갤러리 1장 1024×559 가로형(R-9/R-10 하한).
    ('p34', 390,  ['top', 'bnd-3', 'bnd+3', 'sheet']),
    ('p34', 1280, ['top']),
    # 93: C군 2번째 — 「과소 판정」(dead 가 안 붙는 것)을 한 상품에만 걸지 않기 위한 이중화.
    ('p93', 390,  ['top', 'bnd+3']),
]

# 그룹 — F0 이 지문에서 직접 유도한 것과 대조한다 (여기 값은 "기대"가 아니라 "표기"다)
REP = {'A': 'p11', 'B': 'p61', 'C': 'p34'}
SAMPLED = sorted(set(n for n, _, _ in SAMPLE))   # 직접 렌더하는 상품 — 동형성 대조에서 제외한다

WAITS = {'scroll': 420, 'tap': 220, 'sheet': 800, 'close': 200, 'settle': 900}
CONC = 3


# ============================================================ F0 정적 지문
_TAG = {
    'cart': re.compile(r'<button[^>]*\bid="actionCart"[^>]*>', re.I),
    'buy':  re.compile(r'<div class="btnSubmit gFull sizeL relative[^>]*>', re.I),
}
_BAR = re.compile(r'<div class="[^"]*mobile-fix-footer[^"]*"[^>]*>(.*?)<div class="guideArea', re.S)


def _attr(tag, name):
    m = re.search(r'\b%s="([^"]*)"' % name, tag or '')
    return m.group(1) if m else None


def _dead(tag):
    u"""`isUnsellable()` 의 `dead()` 와 **같은 규칙**으로 판정한다 (JS 를 그대로 옮긴 것)."""
    if not tag:
        return True
    cls = (_attr(tag, 'class') or '').split()
    if 'displaynone' in cls:
        return True
    oc = _attr(tag, 'onclick')
    return (not oc) or (not re.sub(r'\s', '', oc))


def _fn(tag):
    oc = _attr(tag, 'onclick') or ''
    m = re.search(r'product_submit\(\s*(\d+)', oc)
    if m:
        return 'product_submit(%s)' % m.group(1)
    if 'sendLoginPage' in oc:
        return 'sendLoginPage'
    return ''


def fingerprint(doc):
    u"""라이브 HTML 에서 「구매 마크업 지문」을 뽑는다. 하나라도 못 찾으면 None 을 남겨 probe 가 FAIL 한다."""
    cart = (_TAG['cart'].search(doc) or [None]) and (_TAG['cart'].search(doc).group(0)
                                                     if _TAG['cart'].search(doc) else None)
    buy = _TAG['buy'].search(doc).group(0) if _TAG['buy'].search(doc) else None
    bm = _BAR.search(doc)
    bar = bm.group(1) if bm else None
    bar_cart = None
    if bar:
        m = re.search(r'<div class="btnNormal[^"]*"[^>]*>', bar)
        bar_cart = m.group(0) if m else None
    fp = {
        'cart_found': cart is not None, 'buy_found': buy is not None, 'bar_found': bar is not None,
        'cart_dead': _dead(cart), 'buy_dead': _dead(buy),
        'cart_fn': _fn(cart), 'buy_fn': _fn(buy),
        'bar_cart_fn': _fn(bar_cart),
        'bar_cart_dead': _dead(bar_cart),
        'bar_layer_btn': len(re.findall(r'jsLayerBtn', bar or '')),
        'bar_review_hook': len(re.findall(r'alpha_review_count', bar or '')),
        'opt_selects': len(re.findall(r'<select[^>]*name="option', doc)),
        'add_set': doc.count('productSet additional'),
        'soldout_hidden': bool(re.search(r'<div class="flex soldout displaynone"', doc)),
    }
    # 그룹은 **지문에서 유도한다** — 상품번호로 하드코딩하지 않는다
    if fp['cart_dead'] and fp['buy_dead']:
        fp['group'] = 'C'
    elif fp['opt_selects'] == 0:
        fp['group'] = 'B'
    else:
        fp['group'] = 'A'
    return fp


# 표본 축소의 전제 — 표본 밖 상품이 대표와 **반드시** 같아야 하는 항목
PATH_KEYS = ('group', 'cart_dead', 'buy_dead', 'cart_fn', 'buy_fn',
             'bar_cart_fn', 'bar_cart_dead', 'bar_layer_btn', 'bar_review_hook')


# ============================================================ 음성 대조군 자산
def _css_without_dead():
    u"""`.zg-bar--dead{display:none}` 규칙만 뺀 detail.css **사본**을 build/ 에 만든다.
    제품 파일은 건드리지 않는다. 규칙을 못 찾으면 예외 — 조용히 "대조군이 통과"하면 안 된다."""
    src = os.path.join(SKIN, 'ds/css/detail.css')
    txt = read(src)
    pat = re.compile(r'\.zg-detail\s+\.mobile-fix-footer\.zg-bar--dead\s*\{[^}]*\}')
    if not pat.search(txt):
        raise RuntimeError(u'음성 대조군: detail.css 에서 `.zg-bar--dead` 규칙을 못 찾았다 — '
                           u'셀렉터가 바뀌었으면 checks/f_buypath.py 의 패턴을 고쳐라')
    out = pat.sub(u'/* ZG-TEST 음성대조: 규칙 제거 */', txt, count=1)
    # 이 사본이 **정말로 서빙됐는지**를 페이지 안에서 확인할 표식.
    # 없으면 「규칙을 빼도 바가 안 보인다」가 규칙이 죽은 건지 대조군이 안 걸린 건지 구분이 안 된다.
    out += u'\n.zg-detail .mobile-fix-footer { --zg-negctl: 1; }\n'
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, 'neg-detail-nodead.css')
    with open(p, 'wb') as f:
        f.write(out.encode('utf-8'))
    return p


# ============================================================ 관측
def _pages():
    u"""실렌더 대상 목록을 만든다. 픽스처는 **한 프로세스에서 순차로** 만든다
    (소독본 자산을 여러 프로세스가 동시에 덮어쓰면 찢어진 읽기가 난다)."""
    cache = {}

    def base(name):
        if name not in cache:
            cache[name] = fixture.build(UA, name)
        return cache[name]

    pages, byname = [], {}
    for name, vp, states in SAMPLE:
        f, diag = base(name)
        key = (name, tuple(states))
        e = byname.get(key)
        if e is None:
            e = {'name': name, 'tag': name, 'docPath': '/product/detail.html?product_no=%s' % name[1:],
                 'fixture': f, 'assets': diag['assets'], 'vps': [], 'states': list(states)}
            byname[key] = e
            pages.append(e)
        e['vps'].append(vp)

    # --- 음성 대조군 / 경계 조건 (전부 390px · top 상태 1개면 충분하다) ---
    def extra(tag, name, mutate=None, ours=None):
        f, diag = base(name)
        pg = {'name': name, 'tag': tag, 'docPath': '/product/detail.html?product_no=%s' % name[1:],
              'fixture': f, 'assets': diag['assets'], 'vps': [390], 'states': ['top']}
        if mutate:
            pg['mutate'] = mutate
        if ours:
            pg['ours'] = ours
        pages.append(pg)

    extra('neg_kill_inline', 'p11', mutate='kill-inline')   # 신호를 주면 dead 가 붙어야 한다
    extra('edge_fill_late', 'p34', mutate='fill-late-onclick')
    extra('edge_fill_touch', 'p34', mutate='fill-with-class-touch')
    extra('edge_soldout_wrap', 'p11', mutate='soldout-wrap')
    extra('edge_soldout_kids', 'p11', mutate='soldout-children')

    # R-9/R-10 원본 종횡비 — 하네스 기본 스텁은 640×948 **세로형**이다.
    #   34·91·93 의 실제 갤러리 원본은 1024×559 **가로형**이라 기본 스텁으로는 그 경우를 못 잰다.
    #   같은 규칙이 가로형에서도 잘라내지 않는지 별도 셀에서 확인한다.
    f, diag = base('p34')
    pages.append({'name': 'p34', 'tag': 'r9_landscape',
                  'docPath': '/product/detail.html?product_no=34',
                  'fixture': f, 'assets': diag['assets'], 'vps': [1280], 'states': ['top'],
                  'stub': {'w': 1024, 'h': 559}})

    # --- 음성 대조군(CSS) — **맨 마지막에** 만든다 --------------------------------
    #   `detail.css` 는 라이브 번들 **안**에 있다. build() 는 번들의 그 구간을 `OURS[url]` 의
    #   내용으로 제자리 교체한다 → `<link>` 라우트만 바꿔치기하면 **아무 효과가 없다**
    #   (실제로 첫 시도가 그렇게 조용히 통과했다). 그래서 OURS 자체를 잠시 사본으로 돌린 뒤
    #   그 상태에서 픽스처와 자산 지도를 만든다. 만든 다음 원복한다.
    #   ⚠ 대조군을 못 만드는 것(=규칙이 이미 없다)은 **본검사를 죽일 이유가 아니다.**
    #     오히려 그때야말로 본검사(F6.bardisp)가 회귀를 잡아야 한다. 그래서 예외를 잡아
    #     사유만 남기고 계속 간다 — 사유는 F9 가 FAIL 로 보고한다.
    negerr = None
    try:
        neg = _css_without_dead()
        with fixture.override('/ds/css/detail.css', neg):
            nf, ndiag = fixture.build(UA, 'p34')
            nfx = os.path.join(BUILD, 'fixture-negctl-p34.html')
            shutil.copyfile(nf, nfx)
            nours = dict(fixture.OURS)
            pages.append({'name': 'p34', 'tag': 'neg_css_nodead',
                          'docPath': '/product/detail.html?product_no=34',
                          'fixture': nfx, 'assets': ndiag['assets'], 'ours': nours,
                          'vps': [390], 'states': ['top']})
    except Exception as e:
        negerr = u'%s: %s' % (type(e).__name__, e)
    return pages, negerr


def measure():
    pages, negerr = _pages()
    cfg = {'ua': fetch.UA[UA], 'ours': fixture.OURS, 'states': ['top'],
           'waits': WAITS, 'concurrency': CONC, 'pages': pages}
    os.makedirs(BUILD, exist_ok=True)
    p = os.path.join(BUILD, 'cfg-buypath.json')
    with open(p, 'wb') as f:
        f.write(json.dumps(cfg, ensure_ascii=False).encode('utf-8'))
    rc, out, data = node(os.path.join(ROOT, 'js', 'buypath.mjs'), p, timeout=1800)
    if data is None:
        raise RuntimeError(u'구매 경로 하네스 실패(rc=%s):\n%s' % (rc, out[-2500:]))
    with open(os.path.join(OUT, 'buypath.json'), 'wb') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1).encode('utf-8'))

    fps = {}
    for ua in ('iphone', 'android', 'desktop'):
        for n in fetch.PRODUCTS:
            doc = fetch.html(ua, 'p%d' % n)
            if doc is None:
                continue
            fps['%s/p%d' % (ua, n)] = fingerprint(doc)
    return {'res': {'%s@%d' % (r['tag'], r['vp']): r for r in data['results']}, 'fp': fps,
            'negerr': negerr}


# ============================================================ 판정
def _fired(t):
    return (t or {}).get('fired') or []


def run(base, obs=None):
    s = Suite('F', u'구매 경로 (13종 발사 가로채기)')
    obs = obs or measure()
    res, fps = obs['res'], obs['fp']
    b = base['F']

    # ---------------------------------------------- F0. 13종 전수 정적 지문
    s.probe('F0.n', u'지문을 뽑은 (UA×상품) 수', len(fps))
    for key in sorted(fps):
        fp = fps[key]
        s.truthy('F0.found.%s' % key, u'[%s] 구매 마크업 3종(인라인 장바구니·구매하기·하단바) 탐지' % key,
                 fp['cart_found'] and fp['buy_found'] and fp['bar_found'],
                 u'못 찾으면 아래 지문 대조가 통째로 거짓 통과한다')
        exp = (b.get('fp') or {}).get(key)
        if exp is None:
            s.add('F0.new.%s' % key, False, u'baseline 에 없는 (UA×상품)', '-', key,
                  u'상품이 늘었으면 --update-baseline')
            continue
        s.eq('F0.fp.%s' % key, u'[%s] 구매 마크업 지문' % key, exp, fp,
             u'바뀌면 그 상품의 구매 경로 모양이 달라진 것이다')

    # 그룹 인원 — 지문에서 유도한 값이다
    got = {}
    for key, fp in fps.items():
        if key.startswith('iphone/'):
            got.setdefault(fp['group'], []).append(key.split('/')[1])
    s.eq('F0.groups', u'그룹별 상품(지문에서 유도)', b['groups'],
         dict((g, sorted(v)) for g, v in got.items()),
         u'C군이 늘었는데 표본에 없으면 그 상품은 아무도 안 본다')

    # **표본 축소의 전제** — 표본 밖 상품이 대표와 같은 경로 모양인가
    for key in sorted(fps):
        ua, name = key.split('/')
        if ua != 'iphone':
            continue
        fp = fps[key]
        if name in SAMPLED:
            continue          # 표본에 들어 있는 상품은 직접 렌더해서 본다 (71 이 그래서 여기 없다)
        rep = REP.get(fp['group'])
        if not rep:
            continue
        rfp = fps.get('iphone/' + rep)
        if not rfp:
            continue
        s.eq('F0.same.%s' % name, u'[%s] 구매 경로 모양이 그룹 대표(%s)와 같은가' % (name, rep),
             dict((k, rfp[k]) for k in PATH_KEYS), dict((k, fp[k]) for k in PATH_KEYS),
             u'다르면 이 상품은 렌더 표본이 대신 검증해 주지 못한다 — SAMPLE 에 추가하라')

    # ---------------------------------------------- F1~F4. 실렌더 발사
    s.probe('F1.cells', u'실렌더한 (표본×폭) 셀 수', len(res))
    for name, vp, states in SAMPLE:
        tag = '%s@%d' % (name, vp)
        r = res.get(tag)
        if not r or not r.get('ok'):
            s.fail('F1.%s' % tag, u'%s 렌더' % tag, (r or {}).get('error', 'no result')); continue
        p = r['probe']
        grp = (fps.get('iphone/' + name) or {}).get('group')
        exp = b['render'][tag]

        # 스텁이 진짜 걸렸는가 — 원래 두 전역이 있었는지부터 본다 (없으면 스텁이 허수다)
        s.eq('F1.orig.%s' % tag, u'[%s] 가로채기 전 전역 존재(product_submit · PRODUCTSUBMIT.sendLoginPage)' % tag,
             {'product_submit': 'function', 'PRODUCTSUBMIT': 'object', 'sendLoginPage': 'function'},
             p['orig'], u'없으면 스텁이 남의 자리를 차지한 것이라 발사 기록이 무의미하다')
        s.eq('F1.nav.%s' % tag, u'[%s] 문서 밖으로의 내비게이션' % tag, [], r.get('navigations'),
             u'가로채기가 샜다 = 이 셀의 발사 기록을 믿을 수 없다')
        s.eq('F1.err.%s' % tag, u'[%s] 우리 파일(/ds/) JS 예외' % tag, 0, len(r.get('errorsOurs') or []))

        # DOM 보존 — 바를 내려도 알파리뷰 훅은 남아야 한다
        s.eq('F1.hook.%s' % tag, u'[%s] 하단바 안 리뷰수 훅(알파리뷰)' % tag,
             exp['reviewHook'], p['dom']['reviewHook'],
             u'0 이면 알파리뷰 리뷰수가 끊긴다 — 바를 내려도 DOM 에는 남아야 한다')
        s.eq('F1.hookall.%s' % tag, u'[%s] 페이지 전체 리뷰수 훅' % tag,
             exp['reviewHookAll'], p['dom']['reviewHookAll'])
        s.eq('F1.dead.%s' % tag, u'[%s] `.zg-bar--dead` 부착 (C군만 True)' % tag,
             exp['dead'], p['dom']['deadFlag'],
             u'A·B군에서 True 면 팔 수 있는 상품의 바가 사라진 것 = 매출 정지')
        s.eq('F1.soldout.%s' % tag, u'[%s] `.zg-bar--soldout` 부착' % tag, False, p['dom']['soldoutFlag'],
             u'라이브 13종에 품절 상품은 없다 — True 면 라이브가 바뀐 것')

        for st in states:
            v = p['states'].get(st)
            sid = '%s.%s' % (tag, st)
            if not v:
                s.fail('F2.%s' % sid, u'[%s] 상태 %s' % (tag, st), 'no state'); continue
            e = exp['states'][st]
            s.eq('F2.fixed.%s' % sid, u'[%s %s] `.mobile-layer.fixed` (시트 경로 여부)' % (tag, st),
                 e['fixed'], v['fixed'],
                 u'다르면 스킨 checkScroll 의 경계가 바뀐 것 — 아래 발사 기대값이 통째로 어긋난다')
            # 이 셀이 **의도한 분기에 실제로 도달했는가**. baseline 값이 아니라 규칙으로 본다 —
            # 경계를 못 넘은 채 그 상태를 baseline 에 굳히면 검사가 조용히 무의미해진다.
            if st == 'bnd+3':
                s.eq('F2.branch.%s' % sid, u'[%s] 경계 +3px 에서 시트 경로(.fixed)에 도달했는가' % tag,
                     True, v['fixed'],
                     u'스크롤 %s / 경계 %s / 재시도 %s회' % ((v.get('pos') or {}).get('at'),
                        (v.get('pos') or {}).get('boundary'), (v.get('pos') or {}).get('tries')))
            if st in ('top', 'bnd-3'):
                s.eq('F2.branch.%s' % sid, u'[%s %s] 위임 경로(.fixed 없음)에 있는가' % (tag, st),
                     False, v['fixed'])
            s.eq('F2.barvis.%s' % sid, u'[%s %s] 하단바 표시' % (tag, st), e['barVisible'], v['barVisible'])
            s.eq('F2.ctl.%s' % sid, u'[%s %s] 화면에 보이는 구매 컨트롤' % (tag, st),
                 e['visibleBuyControls'], v['visibleBuyControls'],
                 u'A·B군에서 빈 목록이면 고객이 누를 것이 하나도 없다')
            if grp in ('A', 'B'):
                s.ge('F2.nctl.%s' % sid, u'[%s %s] 보이는 구매 컨트롤 수' % (tag, st), 1,
                     len(v['visibleBuyControls']), u'0 = 판매 정지')

            for k, want in e['fired'].items():
                s.eq('F3.%s.%s' % (sid, k), u'[%s %s] 「%s」를 눌렀을 때 발사된 것' % (tag, st, k),
                     want, _fired(v['taps'].get(k)),
                     u'A·B군은 반드시 발사돼야 하고 C군은 반드시 비어 있어야 한다')
                if grp == 'C':
                    s.eq('F3.dead.%s.%s' % (sid, k), u'[%s %s] 「%s」 탭이 아무 데도 안 간다' % (tag, st, k),
                         [], _fired(v['taps'].get(k)),
                         u'「안 보인다」가 아니라 「어디로도 가지 않는다」를 본다')
            if 'sheetOpened' in e:
                s.eq('F3.sheet.%s' % sid, u'[%s %s] 바 「구매하기」가 시트를 여는가' % (tag, st),
                     e['sheetOpened'], (v.get('taps', {}).get('barBuy') or {}).get('sheetOpened'),
                     u'`.fixed` 이면 시트, 아니면 인라인 위임 — 두 분기가 다 살아 있어야 한다')
            if st == 'sheet':
                s.eq('F4.sheetctl.%s' % sid, u'[%s] 시트 안에 보이는 구매 컨트롤' % tag,
                     e['sheetVisibleBuyControls'], v.get('sheetVisibleBuyControls'))
                so = v.get('sheetSumOverlap') or {}
                # R-11(합계를 버튼 위에 고정)은 **팔 수 있는 상품**의 요구사항이다.
                # C군(34·91·93)은 팔지 않는 페이지라 결제 UI 자체를 내리므로(`zg-unsellable`)
                # 합계가 안 보이는 것이 정답이다. 그룹별로 기대를 뒤집는다.
                s.eq('F4.sumvis.%s' % sid,
                     u'[%s] 시트 열림 상태의 합계 노출 (%s군 기대)' % (tag, grp),
                     grp != 'C', bool(v.get('sheetSumVisible')),
                     u'A·B군은 보여야 하고, C군은 결제 UI 를 함께 내리므로 안 보여야 한다')
                s.eq('F4.sumov.%s' % sid, u'[%s] 합계 ↔ 시트 버튼 겹침(px) (R-11)' % tag,
                     {'cart': 0, 'buy': 0}, so,
                     u'0 이 아니면 결제 직전 숫자가 버튼에 가린다')

        # --- B군: 옵션 select 가 없을 때 화면이 무너지지 않는가 -----------------
        if grp == 'B':
            d = p['dom']
            s.eq('F5.opts.%s' % tag, u'[%s] 옵션 select 수(B군은 0)' % tag, 0, d['optionSelects'])
            s.eq('F5.cards.%s' % tag, u'[%s] 구성 카드 수' % tag, 0, d['optCards'])
            s.eq('F5.title.%s' % tag, u'[%s] 「몇 박스로 하시겠어요?」 제목 잔존' % tag, 0, d['optsTitle'],
                 u'`buildOptionCards()` 가 일찍 반환하는데 제목만 남으면 빈 제목이 덩그러니 남는다')
            s.eq('F5.wrap.%s' % tag, u'[%s] `.zg-opts` 래퍼 잔존' % tag, 0, d['optsWrap'])
            # 2026-09-11 — 정가·할인금액 2줄이 늘어 5줄이다.
            # 숫자만 세면 어느 줄이 빠졌는지 못 잡으므로, 바로 아래 `F5.sum` 이
            # 줄 **내용**을 통째로 대조한다. 여기서는 개수만 고정한다.
            s.eq('F5.sumrows.%s' % tag,
                 u'[%s] 합계 줄 수(정가·할인금액·상품금액·배송비·총결제금액)' % tag,
                 5, d['sumRows'])
            s.eq('F5.sum.%s' % tag, u'[%s] 합계 줄 내용' % tag, exp['sumTexts'], d['sumTexts'])
            s.eq('F5.barsum.%s' % tag, u'[%s] 하단바 금액 줄' % tag, exp['barSum'],
                 [d['barSumDisplay'], d['barSumText']],
                 u'B군은 단가가 있으므로 금액 줄을 접지 않는다')

        # --- C군: 안내 페이지에서 남는 경로가 없는가 ---------------------------
        if grp == 'C':
            d = p['dom']
            s.eq('F6.bardisp.%s' % tag, u'[%s] 하단바 계산된 display' % tag, exp['barDisplay'], d['barDisplay'])
            s.eq('F6.layer.%s' % tag, u'[%s] 바 밖에 남은 시트 트리거(.jsLayerBtn)' % tag,
                 0, d['layerBtnOutsideBar'],
                 u'바를 내려도 다른 곳에 트리거가 남으면 안내 페이지에서 시트가 열린다')
            # ⚠ 프로그램 클릭은 `display:none` 요소에도 먹으므로 F3 의 sheetOpened 는 C군에서도 True 다.
            #   고객이 **닿을 수 있는** 트리거가 0인지는 여기서 따로 본다.
            s.eq('F6.trigvis.%s' % tag, u'[%s] 화면에서 누를 수 있는 시트 트리거 수' % tag,
                 0, d['layerBtnVisible'],
                 u'0 이 아니면 팔지 않는 페이지에서 고객이 시트를 열 수 있다')
            s.eq('F6.barsum.%s' % tag, u'[%s] 하단바 금액 줄(막다른 안내는 접는다)' % tag,
                 exp['barSum'], [d['barSumDisplay'], d['barSumText']])

        # --- R-9 좌측 세로 썸네일 (갤러리 장수가 상품마다 1~7장) -----------------
        #   1023px 에서는 이 목록이 **원래 안 보인다**(실측). 안 보이는 것을 재면
        #   li 높이 0 · 테두리 2px 때문에 overflowPx 가 +2 로 나와 거짓 FAIL 이 된다.
        #   그래서 보이는 것만 판정하고, ≥1024 에서 하나도 안 보이면 그것 자체가 FAIL 이다.
        if vp >= 1024:
            th = p.get('thumbs') or []
            s.probe('F7.n.%s' % tag, u'[%s] 좌측 세로 썸네일 수' % tag, len(th))
            s.probe('F7.vis.%s' % tag, u'[%s] 그중 실제로 그려진 것' % tag,
                    sum(1 for t in th if t.get('visible')),
                    u'0 이면 아래 R-9 검사가 통째로 거짓 통과한다')
            for i, t in enumerate(th):
                if not t.get('visible'):
                    continue
                s.le('F7.ovf.%s.%d' % (tag, i), u'[%s] 썸네일#%d 상자 밖 넘침(px) (R-9)' % (tag, i), 0,
                     t.get('overflowPx'),
                     u'0 초과면 `overflow:hidden` 이 그만큼 잘라낸다 (원본 %s)' % (t.get('natural'),))
                s.eq('F7.fit.%s.%d' % (tag, i), u'[%s] 썸네일#%d object-fit (R-9)' % (tag, i),
                     'contain', t.get('objectFit'))
        s.eq('F7.gallery.%s' % tag, u'[%s] 갤러리 `.thumbnail__list > li` 표시 수 (R-10)' % tag,
             exp['galleryLi'], p['dom']['galleryLi'],
             u'상품마다 1~7장으로 제각각이다 — 4장 고정 규칙이 장수와 무관하게 도는지 본다')

    # ---------------------------------------------- F8. 경계 조건 (라이브에 없는 상태)
    #   라이브 13종에는 품절 상품이 **하나도 없다**(전부 `.soldout` 이 displaynone).
    #   그래서 품절 × dead 의 충돌은 관측으로 못 닫는다 → 합성해서 결과를 기록한다.
    for tag, what in (('edge_soldout_wrap', u'품절 가설A: 래퍼(.buy-btn-wrap)만 감춤'),
                      ('edge_soldout_kids', u'품절 가설B: 자식 두 버튼에 displaynone'),
                      ('edge_fill_late',    u'카페24가 **onclick 만** 나중에 채움(클래스 변화 없음)'),
                      ('edge_fill_touch',   u'카페24가 onclick + 클래스를 함께 되살림')):
        r = res.get('%s@390' % tag)
        if not r or not r.get('ok') or not r.get('mutate'):
            s.fail('F8.%s' % tag, u'경계 조건 %s' % what, (r or {}).get('error', 'no result')); continue
        m = r['mutate']
        s.eq('F8.%s' % tag, u'[경계] %s → (dead, soldout, display, SOLD OUT 노출)' % what,
             b['edge'][tag], [m['after']['dead'], m['after']['soldout'],
                              m['after']['display'], m['after']['soldoutSlotVisible']],
             u'라이브에 표본이 없어 합성으로만 확인한다. 값이 바뀌면 판정 규칙이 바뀐 것')
        if m.get('steps'):
            s.eq('F8.step.%s' % tag, u'[경계] %s 중간 단계' % what, b['edge_steps'][tag],
                 [[x['at'], x['dead'], x['display']] for x in m['steps']])

    # ---------------------------------------------- F7L. 가로형 원본에서의 R-9
    r = res.get('r9_landscape@1280')
    if not r or not r.get('ok'):
        s.fail('F7L', u'가로형 원본(1024×559) 썸네일', (r or {}).get('error', 'no result'))
    else:
        th = [t for t in (r['probe'].get('thumbs') or []) if t.get('visible')]
        s.probe('F7L.n', u'[가로형 1024×559] 그려진 좌측 썸네일 수', len(th))
        for i, t in enumerate(th):
            s.le('F7L.ovf.%d' % i, u'[가로형 1024×559] 썸네일#%d 상자 밖 넘침(px) (R-9)' % i, 0,
                 t.get('overflowPx'), u'34·91·93 의 실제 원본 종횡비다')
            s.eq('F7L.fit.%d' % i, u'[가로형 1024×559] 썸네일#%d object-fit' % i, 'contain',
                 t.get('objectFit'))

    # ---------------------------------------------- F9. 음성 대조군
    r = res.get('neg_css_nodead@390')
    if obs.get('negerr'):
        s.fail('F9.css.build', u'음성 대조군(CSS 규칙 제거) 자체를 못 만들었다', obs['negerr'])
    elif not r or not r.get('ok'):
        s.fail('F9.css', u'음성 대조군(CSS 규칙 제거)', (r or {}).get('error', 'no result'))
    else:
        d = r['probe']['dom']
        st = r['probe']['states']['top']
        s.eq('F9.css.served', u'[음성대조] 규칙 뺀 CSS 사본이 실제로 서빙됐다(표식 --zg-negctl)',
             '1', (d.get('negCtlMarker') or '').strip(),
             u'비어 있으면 대조군 CSS 가 안 걸린 것 — 아래 판정은 규칙과 무관하다. '
             u'(라이브 번들 안 구간을 갈아끼웠는지 확인하라)')
        s.eq('F9.css.dead', u'[음성대조] 규칙을 빼도 `.zg-bar--dead` 클래스는 붙는다(JS 는 그대로)',
             True, d['deadFlag'])
        s.add('F9.css.vis', d['barDisplay'] != 'none',
              u'[음성대조] `.zg-bar--dead{display:none}` 을 빼면 34 의 바가 **다시 보여야** 한다',
              '!= none', d['barDisplay'],
              u'none 이면 이 검사는 CSS 규칙을 재고 있는 게 아니다 = F1.dead 가 죽은 검사다')
        s.add('F9.css.ctl', len(st['visibleBuyControls']) > 0,
              u'[음성대조] 규칙을 빼면 눌러도 아무 일 없는 버튼이 화면에 다시 나타난다', '> 0',
              st['visibleBuyControls'])
        s.eq('F9.css.fired', u'[음성대조] 그 버튼은 여전히 아무 데도 안 간다(규칙이 막던 것이 이것)',
             [], _fired(st['taps'].get('barBuy')))

    r = res.get('neg_kill_inline@390')
    if not r or not r.get('ok') or not r.get('mutate'):
        s.fail('F9.kill', u'음성 대조군(팔 수 있는 상품의 인라인 버튼 죽이기)', (r or {}).get('error', 'no result'))
    else:
        m = r['mutate']
        s.eq('F9.kill.before', u'[음성대조] 변조 전 11 은 dead 가 아니다', False, m['before']['dead'])
        s.eq('F9.kill.after', u'[음성대조] 인라인 두 버튼을 죽이면 dead 가 **붙어야** 한다',
             True, m['after']['dead'],
             u'안 붙으면 판정이 상품번호에 박힌 것이지 실제 신호를 보는 게 아니다')
        s.eq('F9.kill.disp', u'[음성대조] 그때 바는 화면에서 내려간다', 'none', m['after']['display'])

    return s.done()


def to_baseline(obs):
    res, fps = obs['res'], obs['fp']
    groups = {}
    for key, fp in fps.items():
        if key.startswith('iphone/'):
            groups.setdefault(fp['group'], []).append(key.split('/')[1])
    render = {}
    for name, vp, states in SAMPLE:
        tag = '%s@%d' % (name, vp)
        r = res.get(tag)
        if not r or not r.get('ok'):
            continue
        p = r['probe']
        d = p['dom']
        ent = {'reviewHook': d['reviewHook'], 'reviewHookAll': d['reviewHookAll'],
               'dead': d['deadFlag'], 'barDisplay': d['barDisplay'],
               'galleryLi': d['galleryLi'], 'sumTexts': d['sumTexts'],
               'barSum': [d['barSumDisplay'], d['barSumText']], 'states': {}}
        for st in states:
            v = p['states'].get(st) or {}
            e = {'fixed': v.get('fixed'), 'barVisible': v.get('barVisible'),
                 'visibleBuyControls': v.get('visibleBuyControls'),
                 'fired': dict((k, (t or {}).get('fired') or []) for k, t in (v.get('taps') or {}).items())}
            if st != 'sheet':
                e['sheetOpened'] = (v.get('taps', {}).get('barBuy') or {}).get('sheetOpened')
            else:
                e['sheetVisibleBuyControls'] = v.get('sheetVisibleBuyControls')
            ent['states'][st] = e
        render[tag] = ent
    edge, edge_steps = {}, {}
    for tag in ('edge_soldout_wrap', 'edge_soldout_kids', 'edge_fill_late', 'edge_fill_touch'):
        r = res.get('%s@390' % tag)
        if not r or not r.get('mutate'):
            continue
        m = r['mutate']
        edge[tag] = [m['after']['dead'], m['after']['soldout'], m['after']['display'],
                     m['after']['soldoutSlotVisible']]
        if m.get('steps'):
            edge_steps[tag] = [[x['at'], x['dead'], x['display']] for x in m['steps']]
    return {'fp': fps, 'groups': dict((g, sorted(v)) for g, v in groups.items()),
            'render': render, 'edge': edge, 'edge_steps': edge_steps}
