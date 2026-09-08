# -*- coding: utf-8 -*-
u"""
H. 홈(index.html) 검사 — 정적 + Chromium 실렌더.

출처
  설계서 08 §6-4(overflow → sticky) · §6-5(조건④) · §7-6(지연로더) · §7-9(M-1~M-5) · §11(확정 마크업)
  개발 11 §5(자체 검증 표) · QA카페24_홈_1차 §C-1(main_js TypeError) · QASEO_홈_1차 P1-A~E
  QA모바일_홈_1차 §2~§5

거짓 통과 방지
  - 랜드마크(.zg-pblock 3 · .zg-fr 72 · 썸네일 3 · h1 1) 가 하나라도 빠지면 그 뷰포트를 신뢰하지 않는다
  - **음성 대조군 H4**: `.zg-home{overflow-x:hidden}` 을 주입하면 sticky 가 "깨져야" PASS.
    안 깨지면 sticky 측정 자체가 죽은 것이다.
  - **대조군 H6**: 변경 전 라이브 홈에서 `reading 'pause'` 오류가 0 임을 같이 잰다.
    변경 후에도 0 이어야 하며, 스텁이 빠지면 여기서 잡힌다.
"""
import json, os, re
from .common import Suite, ROOT, SKIN, PROJ, BUILD, OUT, read, node, strip_comments
from . import fetch

TEMPLATE = 'index.html'
CSS      = 'ds/css/home.css'
JS       = ['ds/js/home-blocks.js', 'ds/js/home-hero.js']
IMG_DIR  = os.path.join(PROJ, u'전달', u'2026-09-08_홈', u'이미지')
THREE    = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js'

VPS = [390, 360, 768, 1023, 1280]

FORBID_CODE = ['claude.ai', u'레몬라임', u'평점', '26,961', 'data:image',
               'ec-data-src', 'asyncImage', 'scroll-effect', '100vw']


def _p(rel):
    return os.path.join(SKIN, rel)


# ------------------------------------------------------------------ 정적
def _static():
    idx = read(_p(TEMPLATE))
    css = read(_p(CSS))
    code_idx = strip_comments(idx, 'html')
    code_css = strip_comments(css, 'css')
    obs = {}
    obs['imports'] = re.findall(r'<!--@import\(([^)]*)\)-->', idx)
    obs['css_directives'] = re.findall(r'<!--@css\(([^)]*)\)-->', idx)
    obs['js_directives'] = re.findall(r'<!--@js\(([^)]*)\)-->', idx)
    obs['h1'] = len(re.findall(r'<h1[\s>]', idx))
    obs['preload'] = len(re.findall(r'<link[^>]+rel="preload"[^>]+zg-home-bg-dawn', idx))
    obs['three_async'] = len(re.findall(r'<script[^>]+async[^>]+three\.min\.js[^>]*data-zg-three', idx))
    obs['three_defer'] = len(re.findall(r'<script[^>]+defer[^>]+three', idx))
    obs['forbid'] = {}
    for tok in FORBID_CODE:
        n = code_idx.count(tok) + code_css.count(tok)
        for rel in JS:
            n += strip_comments(read(_p(rel)), 'js').count(tok)
        if n:
            obs['forbid'][tok] = n
    obs['css_url'] = len(re.findall(r'url\(', code_css))
    obs['stub'] = (idx.count('window.runMainBannerSlidePC') + idx.count('window.runMainBannerSlideMobile'))
    obs['body_class_code'] = sum(strip_comments(read(_p(r)), 'js').count("body.classList") +
                                 strip_comments(read(_p(r)), 'js').count("$('body')") for r in JS)
    obs['onload_code'] = sum(strip_comments(read(_p(r)), 'js').count('window.onload') for r in JS)
    # 매니페스트 ↔ 실파일
    m = re.search(r'window\.ZG_HOME_IMG\s*=\s*(\{.*?\});', idx, re.S)
    names = re.findall(r'"(zg-home-[^"]+)"', m.group(1)) if m else []
    files = set(os.listdir(IMG_DIR)) if os.path.isdir(IMG_DIR) else set()
    obs['manifest'] = {'count': len(names), 'dup': len(names) - len(set(names)),
                       'missing': sorted(n for n in names if n not in files),
                       'extra': sorted(f for f in files if f not in set(names) and f.startswith('zg-home-'))}
    # 본문 직접 참조 이미지도 실파일이어야 한다
    refs = set(re.findall(r'/ds/image/(zg-home-[A-Za-z0-9._-]+)', idx))
    obs['ref_missing'] = sorted(r for r in refs if r not in files)
    return obs


# ------------------------------------------------------------------ 픽스처
def _mainjs_inline(doc):
    u"""라이브 홈 본문의 main_js.html 인라인 스크립트 원문(태그 제외)."""
    for m in re.finditer(r'<script\b([^>]*)>', doc):
        if 'src=' in m.group(1):
            continue
        end = doc.find('</script>', m.end())
        body = doc[m.end():end]
        if 'jsMainSlidePC' in body and 'handleClosePopup' in body:
            return body
    return None


def build_fixture():
    doc = fetch.html('iphone', 'home')
    if doc is None:
        raise RuntimeError(u'라이브 캐시 없음: iphone/home — ./run.sh --refresh')
    diag = {'src_bytes': len(doc)}
    mainjs = _mainjs_inline(doc)
    diag['mainjs_bytes'] = len(mainjs) if mainjs else 0
    if not mainjs:
        raise RuntimeError(u'main_js.html 인라인 원문을 라이브 홈에서 못 찾았다')

    idx = read(os.environ.get('ZG_HOME_INDEX') or _p(TEMPLATE))   # 재현 실험용 오버라이드
    body = re.sub(r'<!--@(layout|css|js)\([^)]*\)-->[ \t]*\n?', '', idx)
    body = body.replace('<!--@import(/moa/js/main_js.html)-->',
                        '<script>\n' + mainjs + '\n</script>')
    body = re.sub(r'<!--@import\([^)]*\)-->', '', body)

    out = doc
    m = re.search(r'<link[^>]*optimizer_user\.php[^>]*>', out, re.I)
    diag['css_anchor'] = bool(m)
    css_tag = u'<link rel="stylesheet" href="/ds/css/home.css">\n'
    out = (out[:m.start()] + css_tag + out[m.start():]) if m else out.replace('</head>', css_tag + '</head>', 1)

    m = re.search(r'<script[^>]*optimizer_user\.php[^>]*>', out, re.I)
    diag['js_anchor'] = bool(m)
    js_tag = (u'<script src="/ds/js/home-blocks.js"></script>\n'
              u'<script src="/ds/js/home-hero.js"></script>\n')
    out = (out[:m.start()] + js_tag + out[m.start():]) if m else out.replace('</body>', js_tag + '</body>', 1)

    m = re.search(r'(<main[^>]*id="contents"[^>]*>)(.*?)(</main>)', out, re.S)
    diag['main_anchor'] = bool(m)
    if not m:
        raise RuntimeError(u'main#contents 를 못 찾았다')
    out = out[:m.start(2)] + body + out[m.end(2):]

    os.makedirs(BUILD, exist_ok=True)
    fp = os.path.join(BUILD, 'fixture-home-new.html')
    with open(fp, 'wb') as f:
        f.write(out.encode('utf-8'))
    diag['out'] = fp
    diag['out_bytes'] = len(out)
    # 대조군: 변경 전 라이브 홈 그대로
    fo = os.path.join(BUILD, 'fixture-home-old.html')
    with open(fo, 'wb') as f:
        f.write(doc.encode('utf-8'))
    diag['old'] = fo
    return fp, fo, diag


def scenarios(fnew, fold):
    sc = []
    for vp in VPS:
        sc.append({'name': 'vp%d' % vp, 'vp': vp, 'fixture': fnew, 'kind': 'full'})
    sc.append({'name': 'no3d390', 'vp': 390, 'fixture': fnew, 'kind': 'no3d', 'block3d': True})
    sc.append({'name': 'neg390', 'vp': 390, 'fixture': fnew, 'kind': 'neg',
               'inject': '.zg-home{overflow-x:hidden}'})
    sc.append({'name': 'safety390', 'vp': 390, 'fixture': fnew, 'kind': 'safety'})
    sc.append({'name': 'old390', 'vp': 390, 'fixture': fold, 'kind': 'old'})
    sc.append({'name': 'promote390', 'vp': 390, 'fixture': fnew, 'kind': 'promote', 'delay3d': 3000})
    sc.append({'name': 'late390', 'vp': 390, 'fixture': fnew, 'kind': 'late', 'delay3d': 3000})
    return sc


def measure():
    obs = {'static': _static()}
    fnew, fold, diag = build_fixture()
    three = fetch.fetch_asset(THREE)
    diag['three_status'] = three['status']
    cfg = {'fixture_new': fnew, 'docPath': '/', 'ua': fetch.UA['iphone'],
           'assets': {u: fetch.fetch_asset(u) for u in fetch.same_origin_assets(fetch.html('iphone', 'home'))},
           'ours': {'/ds/css/home.css': _p(CSS),
                    '/ds/js/home-blocks.js': _p(JS[0]),
                    '/ds/js/home-hero.js': _p(JS[1])},
           'imgdir': IMG_DIR, 'three': three['file'] if three['status'] == 200 else None,
           'scenarios': scenarios(fnew, fold)}
    os.makedirs(BUILD, exist_ok=True)
    cp = os.path.join(BUILD, 'cfg-home.json')
    with open(cp, 'wb') as f:
        f.write(json.dumps(cfg, ensure_ascii=False).encode('utf-8'))
    rc, out, data = node(os.path.join(ROOT, 'js', 'home.mjs'), cp, timeout=1800)
    if data is None:
        raise RuntimeError(u'홈 렌더 하네스 실패(rc=%s):\n%s' % (rc, out[-2500:]))
    with open(os.path.join(OUT, 'home.json'), 'wb') as fp:
        fp.write(json.dumps(data, ensure_ascii=False, indent=1).encode('utf-8'))
    obs['diag'] = diag
    obs['res'] = {r['name']: r for r in data['results']}
    return obs


def _pause_errors(r):
    return [e for e in (r.get('errors') or []) if "reading 'pause'" in e.get('msg', '')]


def run(base, obs=None):
    s = Suite('H', u'홈 검사 (정적 + 실렌더)')
    obs = obs or measure()
    st, res, diag = obs['static'], obs['res'], obs['diag']
    b = base.get('H', {})

    # ---- H0. 픽스처 살아 있는가
    s.truthy('H0.fixture.css', u'픽스처: 사용자 CSS 번들 앵커', diag['css_anchor'])
    s.truthy('H0.fixture.js', u'픽스처: 사용자 JS 번들 앵커', diag['js_anchor'])
    s.ge('H0.fixture.mainjs', u'픽스처: main_js.html 인라인 원문 바이트', 40000, diag['mainjs_bytes'],
         u'없으면 C-1 TypeError 재현 자체가 안 된다')
    s.eq('H0.fixture.three', u'three.js 로컬 캐시', 200, diag['three_status'])
    s.probe('H0.scenarios', u'실행한 시나리오 수', len(res))

    # ---- H1. 정적
    s.eq('H1.import', u'index.html @import 는 정확히 2개', 2, len(st['imports']),
         u'12개 삭제(결정 #5) · main_js.html 과 rv_frame.html 만 남는다')
    s.eq('H1.import.mainjs', u'@import main_js.html 유지', 1, st['imports'].count('/moa/js/main_js.html'),
         u'팝업 구동체 — 지우면 홈 팝업이 죽는다')
    s.eq('H1.import.rvframe', u'@import rv_frame.html 유지', 1,
         st['imports'].count('/moa/import/board/rv_frame.html'))
    css_d = st['css_directives']
    s.add('H1.css_order', css_d and css_d[-1] == '/ds/css/home.css' and css_d.count('/ds/css/home.css') == 1,
          u'@css(home.css) 는 기존 @css 뒤 마지막', 'last', css_d[-1] if css_d else None,
          u'앞에 두면 번들 1번이 되어 동률에서 진다')
    s.eq('H1.js_order', u'@js 는 home-blocks → home-hero 순', ['/ds/js/home-blocks.js', '/ds/js/home-hero.js'],
         st['js_directives'][-2:])
    s.eq('H1.h1', u'index.html <h1> 정확히 1개', 1, st['h1'])
    s.eq('H1.preload', u'첫 배경 preload 1개', 1, st['preload'])
    s.eq('H1.three.async', u'three.js async + data-zg-three', 1, st['three_async'])
    s.eq('H1.three.defer', u'three.js 지연실행 속성 0', 0, st['three_defer'],
         u'DOMContentLoaded 를 붙잡아 계측 부팅을 늦춘다')
    s.eq('H1.forbid', u'코드 금칙 토큰(주석 제외) 0', {}, st['forbid'])
    s.eq('H1.css.url', u'home.css 안 url() 0', 0, st['css_url'], u'이미지 경로는 index.html 매니페스트 한 곳')
    s.eq('H1.stub', u'main_js 배너 변수 스텁 2개', 2, st['stub'],
         u'없으면 main_js.html 이 reading pause TypeError 를 낸다 (QA카페24 C-1)')
    s.eq('H1.bodyclass', u'우리 JS 의 body 클래스 조작 0', 0, st['body_class_code'], u'M-1')
    s.eq('H1.onload', u'우리 JS 의 window.onload 0', 0, st['onload_code'], u'M-2')
    mf = st['manifest']
    s.eq('H1.manifest.count', u'매니페스트 파일명 수', 86, mf['count'])
    s.eq('H1.manifest.dup', u'매니페스트 중복', 0, mf['dup'])
    s.eq('H1.manifest.missing', u'매니페스트에 있는데 실파일 없음', [], mf['missing'])
    s.eq('H1.manifest.extra', u'실파일에 있는데 매니페스트 없음', [], mf['extra'])
    s.eq('H1.ref_missing', u'본문 직접 참조 이미지 실파일 없음', [], st['ref_missing'])

    # ---- H2. 뷰포트별 실렌더
    for vp in VPS:
        tag = 'vp%d' % vp
        r = res.get(tag)
        if not r or not r.get('ok'):
            s.fail('H2.%s' % tag, u'%dpx 렌더' % vp, (r or {}).get('error', 'no result')); continue
        m = r['m']
        L = m['landmark']
        ok = True
        for k, want in (('pblock', 3), ('frames', 72), ('thumbs', 3), ('h1', 1), ('ctabar', 1)):
            ok &= s.eq('H2.%s.land.%s' % (tag, k), u'[%d] 랜드마크 %s' % (vp, k), want, L.get(k))
        if not ok:
            continue
        o = m['overflow']
        s.eq('H2.%s.overflow' % tag, u'[%d] scrollWidth == clientWidth' % vp, o['clientWidth'], o['scrollWidth'])
        w = m['wrapper']
        s.eq('H2.%s.wrap' % tag, u'[%d] .zg-home overflow/transform/filter/contain' % vp,
             ['visible', 'visible', 'none', 'none', 'none'],
             [w['overflowX'], w['overflowY'], w['transform'], w['filter'], w['contain']],
             u'하나라도 걸리면 스크롤 컨테이너가 되어 sticky 가 죽는다 (§6-4)')
        sk = m['sticky']
        s.eq('H2.%s.sticky' % tag, u'[%d] 히어로 50%% 에서 stage top' % vp, 0, sk['stageTop'])
        s.eq('H2.%s.stickypos' % tag, u'[%d] stage position' % vp, 'sticky', sk['cs'])
        s.eq('H2.%s.progress' % tag, u'[%d] 캡션 5구간이 순서대로 최대' % vp, [0, 1, 2, 3, 4], m['progressArgmax'],
             u'히어로 진행률이 스크롤을 못 따라간다')
        sc = m['scrub']
        s.eq('H2.%s.scrub.frames' % tag, u'[%d] 칼륨 블록 프레임 수' % vp, 24, sc['frames'])
        s.add('H2.%s.scrub.idx' % tag, sc['idx'][0] == 0 and sc['idx'][1] > sc['idx'][0] and sc['idx'][2] >= 22,
              u'[%d] 스크럽 idx 0 → 중간 → 끝' % vp, '[0, >0, >=22]', sc['idx'])
        s.eq('H2.%s.counter' % tag, u'[%d] 카운터 최종값 v0/v1' % vp, ['525', '20'], [sc['v0'], sc['v1']])
        c4 = m['cond4']
        s.truthy('H2.%s.cond4.frozen' % tag, u'[%d] eMobilePopup 부착 → frozen' % vp, c4['frozen'])
        s.eq('H2.%s.cond4.restore' % tag, u'[%d] 제거 후 scrollY 복원' % vp, c4['before'], c4['restored'])
        s.eq('H2.%s.cond4.thaw' % tag, u'[%d] 제거 후 frozen 해제' % vp, False, c4['stillFrozen'])
        s.truthy('H2.%s.bodywipe' % tag, u'[%d] body class 제거 후 .zg-home 클래스 생존 (R16)' % vp,
                 m['bodywipe']['survived'])
        s.eq('H2.%s.err.pause' % tag, u'[%d] reading pause TypeError' % vp, 0, len(_pause_errors(r)),
             u'main_js.html 이 삭제된 배너를 찾다 던진다 — 스텁이 막아야 한다')
        s.eq('H2.%s.err.ours' % tag, u'[%d] 우리 파일 예외' % vp, 0, len(r.get('errorsOurs') or []))
        other = len(r.get('errors') or []) - len(_pause_errors(r)) - len(r.get('errorsOurs') or [])
        s.eq('H2.%s.err.other' % tag, u'[%d] 남의 예외(교차출처 차단 환경)' % vp,
             (b.get('errors_other') or {}).get(tag, 0), other,
             u'변하면 라이브 구성이 바뀐 것 — 확인 후 baseline 갱신')

    # ---- H3. 3D 폴백
    r = res.get('no3d390')
    if r and r.get('ok'):
        n = r['m']['no3d']
        s.truthy('H3.class', u'cdnjs 차단 → .zg-no3d', n['zgNo3d'])
        s.eq('H3.body', u'body 클래스 오염 없음', '', n['bodyClass'])
        s.eq('H3.fallback', u'.zg-fallback display', 'flex', n['fallbackDisplay'])
        s.eq('H3.track', u'트랙 높이 == 뷰포트(100vh)', n['viewportH'], n['trackH'])
        s.eq('H3.capA', u'캡션 A opacity 1', '1', n['capAOpacity'])
        s.eq('H3.overflow', u'가로 넘침 없음', n['clientW'], n['scrollW'])
        s.eq('H3.err.pause', u'폴백 경로 reading pause TypeError', 0, len(_pause_errors(r)))
    else:
        s.fail('H3', u'3D 폴백 시나리오', (r or {}).get('error', 'no result'))

    # ---- H4. 음성 대조군 — overflow-x:hidden 을 주입하면 sticky 가 깨져야 한다
    r = res.get('neg390')
    if r and r.get('ok'):
        n = r['m']['neg']
        s.eq('H4.overflowY', u'[음성대조] .zg-home overflow-y 계산값', 'auto', n['overflowY'],
             u'overflow-x:hidden → overflow-y:auto (명세)')
        s.add('H4.sticky_broken', n['stageTop'] != 0, u'[음성대조] sticky 가 깨져야 한다', '!= 0', n['stageTop'],
              u'안 깨지면 H2 sticky 검사가 죽은 검사다')
    else:
        s.fail('H4', u'음성 대조군', (r or {}).get('error', 'no result'))

    # ---- H5. 조건④ 3초 안전장치
    r = res.get('safety390')
    if r and r.get('ok'):
        n = r['m']['safety']
        s.truthy('H5.frozen300', u'부착 300ms 후 frozen', n['frozenAt300ms'])
        s.eq('H5.frozen3500', u'떼지 않고 3.5s 후 frozen', False, n['frozenAt3500ms'],
             u'화면을 멈춘 채 두지 않는다')
        s.truthy('H5.classkept', u'body 클래스는 여전히 붙어 있음(떼는 코드 없음 가정)', n['bodyStillHasClass'])
    else:
        s.fail('H5', u'안전장치 시나리오', (r or {}).get('error', 'no result'))

    # ---- H6. 대조군 — 변경 전 라이브 홈에는 pause 오류가 없다
    r = res.get('old390')
    if r and r.get('ok'):
        s.eq('H6.old.pause', u'[변경 전 홈] reading pause TypeError', 0, len(_pause_errors(r)),
             u'0 이어야 "변경이 만든 오류" 판정이 성립한다')
        s.add('H6.old.errors', True, u'[변경 전 홈] 전체 pageerror 수(정보)', '-', len(r.get('errors') or []))
    else:
        s.fail('H6', u'변경 전 대조군', (r or {}).get('error', 'no result'))

    # ---- H7. three.js async 승격
    r = res.get('promote390')
    if r and r.get('ok'):
        n = r['m']['promote']
        s.truthy('H7.first_no3d', u'three.js 도착 전 폴백(.zg-no3d)', n['no3dBefore'])
        s.eq('H7.promoted', u'도착 후(첫 화면 근처) 3D 승격', False, n['no3dAfter'])
        s.truthy('H7.three', u'THREE 정의됨', n['threeAfter'])
    else:
        s.fail('H7.promote', u'승격 시나리오', (r or {}).get('error', 'no result'))
    r = res.get('late390')
    if r and r.get('ok'):
        n = r['m']['promote']
        s.truthy('H7.late.first_no3d', u'[늦은 도착] 도착 전 폴백', n['no3dBefore'])
        s.eq('H7.late.kept', u'[늦은 도착·이미 스크롤] 폴백 유지 (화면 튐 방지)', True, n['no3dAfter'])
    else:
        s.fail('H7.late', u'늦은 승격 시나리오', (r or {}).get('error', 'no result'))
    return s.done()


def to_baseline(obs):
    eo = {}
    for tag, r in obs['res'].items():
        if tag.startswith('vp') and r.get('ok'):
            eo[tag] = len(r.get('errors') or []) - len(_pause_errors(r)) - len(r.get('errorsOurs') or [])
    return {'errors_other': eo}
