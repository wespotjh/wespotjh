# -*- coding: utf-8 -*-
u"""
H. 홈(index.html) 검사 — 정적 + Chromium 실렌더.

출처
  설계서 08 §6-4(overflow → sticky) · §6-5(조건④) · §7-6(지연로더) · §7-9(M-1~M-5) · §11(확정 마크업)
  개발 11 §5(자체 검증 표) · QA카페24_홈_1차 §C-1(main_js TypeError) · QASEO_홈_1차 P1-A~E
  QA모바일_홈_1차 §2~§5

거짓 통과 방지
  - 랜드마크가 하나라도 빠지면 그 뷰포트를 신뢰하지 않는다.
    우리 인트로(.zg-hero-skin · .zg-bigword 5 · .zg-hcap 5 · h1 1)와
    **건드리지 않은 기존 홈**(메인 배너 · BEST · 페럴랙스 · 신상품)을 같이 센다 —
    한쪽이 0 이면 인트로를 얹다가 기존 홈을 덮은 것이다
  - **음성 대조군 H4**: `.zg-home{overflow-x:hidden}` 을 주입하면 sticky 가 "깨져야" PASS.
    안 깨지면 sticky 측정 자체가 죽은 것이다.
  - **대조군 H6**: 변경 전 라이브 홈에서 `reading 'pause'` 오류가 0 임을 같이 잰다.
    변경 후에도 0 이어야 하며, 스텁이 빠지면 여기서 잡힌다.
"""
import json, os, re
from .common import Suite, ROOT, SKIN, PROJ, BUILD, OUT, read, node, strip_comments
from . import fetch, fixture

TEMPLATE = 'index.html'
CSS      = 'ds/css/home.css'
JS       = ['ds/js/home-blocks.js', 'ds/js/home-hero.js']
IMG_DIR  = os.path.join(PROJ, u'전달', u'2026-09-08_홈', u'이미지')
THREE    = 'https://cdnjs.cloudflare.com/ajax/libs/three.js/r134/three.min.js'

VPS = [390, 360, 414, 768, 1023, 1280]

FORBID_CODE = ['claude.ai', u'레몬라임', u'평점', '26,961', 'data:image',
               'ec-data-src', 'asyncImage', 'scroll-effect', '100vw']


def _p(rel):
    return os.path.join(SKIN, rel)


# ------------------------------------------------------------------ 정적
RESTORE = os.path.join(PROJ, u'전달', u'2026-09-09_홈복구', u'1_index.html.txt')


def _imports(text):
    u"""@import 지시자 목록. 한 줄짜리 주석(<!-@import)은 "그 구간을 끈다"는 표기라 따로 센다."""
    on  = re.findall(r'<!--@import\(([^)]*)\)-->', text)
    off = re.findall(r'<!-@import\(([^)]*)\)-->', text)
    return on, off


def _static():
    idx = read(os.environ.get('ZG_HOME_INDEX') or _p(TEMPLATE))   # 재현 실험용 오버라이드 (build_fixture 와 동일)
    css = read(_p(CSS))
    code_idx = strip_comments(idx, 'html')
    code_css = strip_comments(css, 'css')
    obs = {}
    obs['imports'], obs['imports_off'] = _imports(idx)
    # 기존 홈(2026-09-09 복구본)과 import 목록이 켠 것·끈 것 모두 같아야 한다.
    # 인트로를 얹는 작업이 기존 홈 구성을 건드리지 않았다는 가장 강한 증거다.
    if os.path.isfile(RESTORE):
        r_on, r_off = _imports(read(RESTORE))
        obs['restore'] = {'on_same': r_on == obs['imports'], 'off_same': r_off == obs['imports_off'],
                          'on': r_on, 'off': r_off}
    else:
        obs['restore'] = None
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
    # 접근자 스텁: defineProperty 로 세 변수를 덮는다. 세 이름이 다 있고 defineProperty 가 있어야 3
    obs['stub'] = (len(re.findall(r"'run(?:MainBannerSlidePC|MainBannerSlideMobile|SubBannerSlide)'", idx))
                  if 'Object.defineProperty(window, k' in idx else 0)
    obs['body_class_code'] = sum(strip_comments(read(_p(r)), 'js').count("body.classList") +
                                 strip_comments(read(_p(r)), 'js').count("$('body')") for r in JS)
    obs['onload_code'] = sum(strip_comments(read(_p(r)), 'js').count('window.onload') for r in JS)
    # 매니페스트 ↔ 실파일
    m = re.search(r'window\.ZG_HOME_IMG\s*=\s*(\{.*?\});', idx, re.S)
    names = re.findall(r'"(zg-home-[^"]+)"', m.group(1)) if m else []
    files = set(os.listdir(IMG_DIR)) if os.path.isdir(IMG_DIR) else set()
    # extra(매니페스트에 없는 실파일)는 가루 블록·스틱 컷을 홈에서 뺀 뒤로 정상이다.
    # 남은 파일은 지우지 않는다 — 되돌릴 때 다시 쓴다. 그래서 판정이 아니라 관측으로만 남긴다.
    obs['manifest'] = {'count': len(names), 'dup': len(names) - len(set(names)),
                       'missing': sorted(n for n in names if n not in files),
                       'unused': len([f for f in files if f not in set(names) and f.startswith('zg-home-')])}
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
    # 홈 3종은 아직 라이브에 없어서 **주입**으로 검사한다. 배포되어 번들에 실리는 순간
    # 주입본과 번들본이 겹쳐(JS 2회 실행 · CSS 는 라이브본이 이김) 검사가 거짓이 된다.
    # 상세(C·D)가 2026-09-09 에 당한 사고다 — 여기서는 미리 큰 소리로 막는다.
    fixture.assert_not_bundled('iphone', 'home',
                               ['/ds/css/home.css', '/ds/js/home-blocks.js', '/ds/js/home-hero.js'])
    diag = {'src_bytes': len(doc)}
    # main_js.html 인라인 원문은 live_main 안에 통째로 들어온다. 여기서는 "있는가"만 확인한다.
    mainjs = _mainjs_inline(doc)
    diag['mainjs_bytes'] = len(mainjs) if mainjs else 0
    if not mainjs:
        raise RuntimeError(u'main_js.html 인라인 원문을 라이브 홈에서 못 찾았다')

    idx = read(os.environ.get('ZG_HOME_INDEX') or _p(TEMPLATE))   # 재현 실험용 오버라이드
    body = re.sub(r'<!--@(layout|css|js)\([^)]*\)-->[ \t]*\n?', '', idx)

    # 기존 홈 구간은 "지우고 흉내내는" 게 아니라 **라이브에서 펼쳐진 결과물을 그대로** 끼운다.
    # index.html 의 @import 목록과 라이브 홈의 @import 목록이 같음을 H1 에서 따로 못 박는다.
    # live_main 끝에는 main_js.html 인라인과 rv_frame 이 이미 들어 있으므로,
    # 우리 본문의 @import 는 첫 번째(main_banner) 자리만 살리고 나머지는 지운다.
    # (그래서 고지 문구는 rv_frame 뒤로 밀린다 — rv_frame 은 숨은 고정 레이어라 눈에 보이는 순서는 같다)
    mm = re.search(r'(<main[^>]*id="contents"[^>]*>)(.*?)(</main>)', doc, re.S)
    if not mm:
        raise RuntimeError(u'라이브 홈에서 main#contents 를 못 찾았다')
    live_main = mm.group(2)
    diag['live_main_bytes'] = len(live_main)

    marks = list(re.finditer(r'<!--@import\([^)]*\)-->', body))
    diag['body_imports'] = len(marks)
    if not marks:
        raise RuntimeError(u'index.html 에 @import 가 없다 — 기존 홈을 끼울 자리가 없다')
    first = marks[0]
    body = body[:first.start()] + live_main + body[first.end():]
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


def _variants():
    u"""표본 반전(negative control) 변이본 — 4차 가드를 한 줄씩 들어낸 사본.
    변이가 안 만들어지면 그 자체가 FAIL 이다(검사가 죽은 것을 통과로 읽지 않는다)."""
    os.makedirs(BUILD, exist_ok=True)
    out = {}

    hero = read(_p(JS[1]))
    cut = re.sub(r"\n[ \t]*if \(!onStage\) \{ pNow = pTarget; return; \}", '', hero, count=1)
    fp = os.path.join(BUILD, 'var-hero-noguard.js')
    with open(fp, 'wb') as f:
        f.write(cut.encode('utf-8'))
    out['hero'] = {'file': fp, 'applied': cut != hero}

    # 가루 블록(.zg-pblock)용 변이본 두 개(프레임 게이트 / decode 게이트)는
    # 홈에서 블록 자체를 뺐으므로 만들지 않는다. 블록을 되살리면 git 이력에서 되돌린다.
    return out


def scenarios(fnew, fold, var):
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
    # 회전·폭 전환 — main_js.html 이 destroy() 뒤 변수를 undefined 로 되돌리는 경로
    sc.append({'name': 'rot390', 'vp': 390, 'fixture': fnew, 'kind': 'resize', 'seq': [[844, 390], [390, 844]]})
    sc.append({'name': 'rot768', 'vp': 768, 'fixture': fnew, 'kind': 'resize', 'seq': [[1024, 768], [768, 1024]]})
    sc.append({'name': 'w768', 'vp': 768, 'fixture': fnew, 'kind': 'resize', 'seq': [[768, 1024], [768, 1000]]})
    sc.append({'name': 'oldrot390', 'vp': 390, 'fixture': fold, 'kind': 'resize', 'seq': [[844, 390], [390, 844]]})
    # 스크럽 프레임타임 — 가루 블록을 뺀 뒤로 스크럽 구간은 히어로 트랙 자체다.
    # 실기 반려(4차) 「버버버버벅」을 수치로 가르는 검사는 그대로 살리고 대상만 옮긴다.
    sc.append({'name': 'jank390', 'vp': 390, 'fixture': fnew, 'kind': 'back', 'throttle': 6, 'target': 'below'})
    sc.append({'name': 'jankneg390', 'vp': 390, 'fixture': fnew, 'kind': 'jank', 'throttle': 6, 'target': 'below',
               'oursOverride': {'/ds/js/home-hero.js': var['hero']['file']}})
    # 히어로 구간 자체의 프레임타임 — 판정이 아니라 관측이다(음성 대조가 성립하지 않는다:
    # 히어로 위에서는 렌더 가드가 원래 일하지 않으므로 반전본과 값이 같다)
    sc.append({'name': 'heroscrub390', 'vp': 390, 'fixture': fnew, 'kind': 'jank', 'throttle': 6, 'target': 'hero'})
    return sc


def measure():
    obs = {'static': _static()}
    var = _variants()
    obs['variants'] = {k: v['applied'] for k, v in var.items()}
    fnew, fold, diag = build_fixture()
    three = fetch.fetch_asset(THREE)
    diag['three_status'] = three['status']
    doc = fetch.html('iphone', 'home')
    asset_urls = fetch.same_origin_assets(doc)
    # 배너매니저 로더 2파일은 인라인 스크립트가 동적으로 붙인다 — <script src> 스캔에 안 잡히므로 따로 뽑는다
    asset_urls += re.findall(r"(?:COMMON_PATH|PC_PATH)\s*=\s*'([^']+)'", doc)
    cfg = {'fixture_new': fnew, 'docPath': '/', 'ua': fetch.UA['iphone'],
           'assets': {u: fetch.fetch_asset(u) for u in asset_urls},
           'ours': {'/ds/css/home.css': _p(CSS),
                    '/ds/js/home-blocks.js': _p(JS[0]),
                    '/ds/js/home-hero.js': _p(JS[1])},
           'imgdir': IMG_DIR, 'three': three['file'] if three['status'] == 200 else None,
           'scenarios': scenarios(fnew, fold, var)}
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


def _rel_errors(r):
    return [e for e in (r.get('errors') or []) if "reading 'removeEventListener'" in e.get('msg', '')]


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
    s.eq('H1.import', u'index.html 켠 @import 6개 (기존 홈 그대로)', 6, len(st['imports']),
         u'인트로는 기존 홈 위에 얹는 것이다 — 홈 구간을 지우지 않는다')
    s.eq('H1.import.off', u'끈 @import(한 줄 주석) 8개', 8, len(st['imports_off']),
         u'<!-@import 는 오타가 아니라 "그 구간을 끈다"는 표기다')
    rs = st.get('restore') or {}
    s.truthy('H1.restore.on', u'켠 @import 목록이 2026-09-09 복구본과 동일', rs.get('on_same'),
             u'다르면 기존 홈 구성을 건드린 것이다')
    s.truthy('H1.restore.off', u'끈 @import 목록이 복구본과 동일', rs.get('off_same'))
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
    s.eq('H1.stub', u'main_js 배너 변수 스텁 0개', 0, st['stub'],
         u'메인 배너 구간을 되살렸으므로 스텁이 남아 있으면 진짜 슬라이더 생성을 가로막는다')
    s.eq('H1.bodyclass', u'우리 JS 의 body 클래스 조작 0', 0, st['body_class_code'], u'M-1')
    s.eq('H1.onload', u'우리 JS 의 window.onload 0', 0, st['onload_code'], u'M-2')
    mf = st['manifest']
    s.eq('H1.manifest.count', u'매니페스트 파일명 수 (배경 5 + 텍스처 3)', 8, mf['count'],
         u'가루 프레임 72장·스틱 컷 6장은 홈에서 뺐다')
    s.eq('H1.manifest.dup', u'매니페스트 중복', 0, mf['dup'])
    s.eq('H1.manifest.missing', u'매니페스트에 있는데 실파일 없음', [], mf['missing'])
    s.probe('H1.manifest.unused', u'매니페스트에 없는 zg-home-* 실파일 수(관측)', mf['unused'])
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
        # 우리 인트로
        for k, want in (('hero', 1), ('bigword', 5), ('hcap', 5), ('h1', 1), ('jump', 1),
                        ('ctabar', 0), ('pblock', 0), ('legalnote', 1)):
            ok &= s.eq('H2.%s.land.%s' % (tag, k), u'[%d] 인트로 랜드마크 %s' % (vp, k), want, L.get(k))
        # 건드리지 않은 기존 홈 — 하나라도 0 이면 인트로가 홈을 덮은 것이다
        for k, what in (('best', u'BEST 상품'), ('newlist', u'신상품'), ('mid2', u'페럴랙스 배너')):
            ok &= s.add('H2.%s.old.%s' % (tag, k), (L.get(k) or 0) > 0,
                        u'[%d] 기존 홈 %s 살아 있는가' % (vp, what), '> 0', L.get(k),
                        u'0 이면 인트로를 얹다가 기존 홈을 덮었다')
        ok &= s.add('H2.%s.old.banner' % tag, (L.get('bannerMob') or 0) + (L.get('bannerPc') or 0) > 0,
                    u'[%d] 기존 홈 메인 배너 살아 있는가' % vp, '> 0',
                    '%s/%s' % (L.get('bannerMob'), L.get('bannerPc')))
        o2 = m.get('order') or {}
        ok &= s.add('H2.%s.order' % tag, o2.get('heroTop') is not None
                    and o2['heroTop'] < o2['oldTop'] and o2['jumpTop'] <= o2['oldTop'],
                    u'[%d] 인트로가 기존 홈보다 위' % vp, 'hero < jump <= old',
                    '%s < %s <= %s' % (o2.get('heroTop'), o2.get('jumpTop'), o2.get('oldTop')),
                    u'확정 사항: 하루→ALL DAY 인트로가 최상단이다')
        ok &= s.ge('H2.%s.order.oldN' % tag, u'[%d] 실제로 보이는 기존 홈 구간 수' % vp, 3, o2.get('oldN'))
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
        # 가루 블록 스크럽·카운터 검사는 블록을 홈에서 뺀 뒤로 대상이 없다.
        s.eq('H2.%s.scrub.none' % tag, u'[%d] 가루 블록 스크럽 대상 없음' % vp, None, m['scrub'])
        c4 = m['cond4']
        s.truthy('H2.%s.cond4.frozen' % tag, u'[%d] eMobilePopup 부착 → frozen' % vp, c4['frozen'])
        s.eq('H2.%s.cond4.restore' % tag, u'[%d] 제거 후 scrollY 복원' % vp, c4['before'], c4['restored'])
        s.eq('H2.%s.cond4.thaw' % tag, u'[%d] 제거 후 frozen 해제' % vp, False, c4['stillFrozen'])
        s.truthy('H2.%s.bodywipe' % tag, u'[%d] body class 제거 후 .zg-home 클래스 생존 (R16)' % vp,
                 m['bodywipe']['survived'])
        s.eq('H2.%s.err.pause' % tag, u'[%d] reading pause TypeError' % vp, 0, len(_pause_errors(r)),
             u'배너 구간을 되살렸으므로 main_js.html 이 진짜 슬라이더를 만든다 — 0 이어야 한다')
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
        # 기존 홈을 되살린 뒤로 body 에는 스킨이 붙이는 클래스(white 등)가 있다.
        # 우리가 봐야 할 것은 "우리 상태 클래스가 body 로 새지 않았는가" 다 (M-1).
        s.eq('H3.body', u'body 에 zg- 상태 클래스 없음', [],
             [c for c in (n['bodyClass'] or '').split() if c.startswith('zg-')],
             u'상태는 .zg-home 에만 붙인다 — 스킨이 body class 를 통째로 지우는 경로가 있다')
        s.add('H3.body.skin', True, u'body 클래스 원문(정보)', '-', n['bodyClass'])
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
        s.truthy('H5.classkept', u'html.scroll-disabled 는 여전히 붙어 있음(떼는 코드 없음 조건)',
                 n['bodyStillHasClass'],
                 u'떨어졌다면 3초 안전장치가 아니라 클래스 제거로 풀린 것 — 검사가 죽는다')
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

    # ---- H8. 회전·폭 전환 — 스텁이 되돌려지지 않는가 (QA모바일 2차 §1-3 · QA카페24 2차 §G)
    for tag, what in (('rot390', u'폰 회전 390→844→390'), ('rot768', u'태블릿 회전 768→1024→768'),
                      ('w768', u'정확히 768 에서 resize')):
        r = res.get(tag)
        if not r or not r.get('ok'):
            s.fail('H8.%s' % tag, what, (r or {}).get('error', 'no result')); continue
        m = r['m']['resize']
        s.ge('H8.%s.resizes' % tag, u'[%s] resize 이벤트가 실제로 났는가' % what, 2, m['resizeCount'],
             u'0 이면 시나리오가 아무것도 안 돌린 것')
        s.eq('H8.%s.pause' % tag, u'[%s] reading pause TypeError' % what, 0, len(_pause_errors(r)))
        s.eq('H8.%s.removeEL' % tag, u'[%s] reading removeEventListener TypeError' % what, 0, len(_rel_errors(r)))
        # 스텁을 걷어냈으므로 이 세 변수는 main_js.html 이 폭에 따라 만들고 지우는 진짜 값이다.
        # 값 자체는 판정 대상이 아니고, 위 두 줄(pause · removeEventListener)이 실제 결과를 본다.
        s.add('H8.%s.stubs' % tag, True, u'[%s] 전환 뒤 배너 변수 타입(정보)' % what, '-', m['stubTypes'])
        s.eq('H8.%s.err.ours' % tag, u'[%s] 우리 파일 예외' % what, 0, len(r.get('errorsOurs') or []))
    r = res.get('oldrot390')
    if r and r.get('ok'):
        s.eq('H8.old.pause', u'[변경 전 홈·회전] reading pause', 0, len(_pause_errors(r)),
             u'변경 전에도 0 이어야 "우리가 만든 오류" 판정이 성립한다')
        s.add('H8.old.errors', True, u'[변경 전 홈·회전] 전체 pageerror 수(정보 — 스킨 자체 오류 포함)', '-',
              len(r.get('errors') or []))
    else:
        s.fail('H8.old', u'변경 전 회전 대조군', (r or {}).get('error', 'no result'))

    # ---- H9. 스크럽 프레임타임 — 실기 반려(대표님 4차) 「버버버버벅」을 수치로 가른다
    #        가루 블록을 뺀 뒤 렌더 가드가 실제로 일하는 지점은 '인트로를 지나 기존 홈을 훑는' 구간이다.
    #        (히어로 위에서는 가드가 원래 일하지 않아 음성 대조가 성립하지 않는다 — 그쪽은 관측만)
    v = obs.get('variants') or {}
    s.truthy('H9.var.hero', u'표본 반전본(히어로 렌더 가드 제거) 생성', v.get('hero'),
             u'만들어지지 않으면 아래 음성 대조가 죽은 검사다')

    r = res.get('jank390')
    if r and r.get('ok'):
        m = r['m']['jank']
        s.ge('H9.frames', u'[6배 스로틀·인트로 아래 구간] 잰 프레임 수', 40, m['n'],
             u'너무 적으면 측정 자체가 안 돈 것')
        s.le('H9.p95', u'[6배 스로틀·인트로 아래 구간] 프레임타임 p95(ms)', 45, m['p95'])
        s.eq('H9.over100', u'[스크럽] 100ms 넘는 프레임', 0, m['over100'])
        s.le('H9.long', u'[스크럽] 롱태스크 합(ms)', 800, m['longMs'])
        b2 = r['m'].get('back') or {}
        s.eq('H9.back.mid', u'히어로로 되돌아온 뒤 p=0.47 캡션', 2, b2.get('atMid'),
             u'화면 밖에서 렌더를 멈춘 뒤 복귀 시 다시 그리는가')
        s.eq('H9.back.top', u'되돌아와 맨 위 캡션', 0, b2.get('atTop'))
    else:
        s.fail('H9', u'스크럽 프레임타임 시나리오', (r or {}).get('error', 'no result'))

    r = res.get('heroscrub390')
    if r and r.get('ok'):
        m = r['m']['jank']
        s.add('H9.hero.p95', True, u'[6배 스로틀·히어로 구간] 프레임타임 p95(ms) — 관측', '-', m['p95'],
              u'히어로는 3D 를 매 프레임 그린다. 판정 기준선이 아직 없어 값만 남긴다')
        s.add('H9.hero.long', True, u'[히어로 구간] 롱태스크 합(ms) — 관측', '-', m['longMs'])
        s.eq('H9.hero.over100', u'[히어로 구간] 100ms 넘는 프레임', 0, m['over100'])
    else:
        s.fail('H9.hero', u'히어로 구간 관측', (r or {}).get('error', 'no result'))

    # 음성 대조: 히어로 가드를 빼면 같은 검사가 반드시 걸려야 한다
    r = res.get('jankneg390')
    if r and r.get('ok'):
        m = r['m']['jank']
        s.add('H9.neg.jank', m['p95'] > 45 or m['longMs'] > 800,
              u'[음성대조] 히어로 렌더 가드 제거 시 스크럽이 실제로 끊기는가', u'p95>45 또는 롱태스크>800',
              'p95=%s long=%s' % (m['p95'], m['longMs']),
              u'안 걸리면 H9.p95/H9.long 은 죽은 검사다')
    else:
        s.fail('H9.neg', u'음성대조(가드 제거)', (r or {}).get('error', 'no result'))

    return s.done()


def to_baseline(obs):
    eo = {}
    for tag, r in obs['res'].items():
        if tag.startswith('vp') and r.get('ok'):
            eo[tag] = len(r.get('errors') or []) - len(_pause_errors(r)) - len(r.get('errorsOurs') or [])
    return {'errors_other': eo}
