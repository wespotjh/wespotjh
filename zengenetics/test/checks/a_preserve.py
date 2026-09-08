# -*- coding: utf-8 -*-
u"""
A. 보존 검사 — **판매가 멈추는 종류**. 가장 중요하다.

출처
  - 신아린 QA모바일_칼륨_4차 §5 「보존 태그 24항목」 표
  - 오세진 QA카페24_칼륨_3차 §2-1 「보존 회귀 — 0건」 표
  - 개발 03F_개발_칼륨_6차 §2 「보존 태그 24항목 감소 0건」

무엇을 보나
  카페24 템플릿은 `{$변수}` · `module=` · `onclick="{$action_*}"` 같은 토큰이
  **하나라도 사라지면 그 자리의 기능이 통째로 죽는다**(장바구니 버튼·옵션·가격).
  재스킨 과정에서 마크업을 옮기다 토큰을 흘리는 사고가 실제로 있었으므로,
  개수를 baseline 에 고정해 두고 **감소**를 잡는다.

기대값은 하드코딩하지 않는다 — 전부 baseline.json 의 `preserve` / `hooks` / `balance` 에 있다.
의도적으로 마크업을 바꿨다면 `./run.sh --update-baseline` 로 갱신하고 커밋 메시지에 남긴다.
"""
import os, re
from .common import Suite, SKIN, read, strip_comments

# 보존 토큰 — 리터럴 문자열 카운트
TOKENS = [
    'module=', '{$', 'onclick="{$action_', '{$form.', 'id="{$', '{$total.',
    '{$soldout_display', '{$basket_display', 'displaynone', 'selectButton',
    'ec-base-qty', 'id="', '<!--@import(', '<!--@css(', '<!--@js(',
]

# 플러그인 훅 8종 — 하나라도 사라지면 외부 앱(리뷰·배너·네이버·카카오·페북)이 끊긴다
HOOKS = [
    'alpha_widget', 'alpha_review_count', 'df-banner-code', 'df-banner-clone',
    'NaverChk_Button', '{$app_payment_button_box_id}', 'id="kakaoKey"',
    'facebook-domain-verification',
]
# ⚠ 토큰은 '#kakaoKey' 가 아니라 'id="kakaoKey"' 다 — 전자는 zg-ga4.js 의 **주석**에만 맞고
#   detail.html 에는 0건이라 div 가 사라져도 PASS 했다 (팀장 결정 T-3 · 오세진 ⓓ, 2026-09-08).

# 카카오 JavaScript 키 — 공개값(모든 페이지 소스에 노출)이라 저장소에 실제 값을 둔다 (팀장 결정 T-1).
#   자리표시 문구가 전달본까지 흘러가 작업본 공유가 불능이 된 회귀가 실제로 났다.
KAKAO_RE = re.compile(r'id="kakaoKey"[^>]*>\s*([^<]*?)\s*</div>')
KAKAO_FMT = re.compile(r'^[0-9a-f]{32}$')

TEMPLATES = ['product/detail.html',
             'moa/import/product_detail/detail.html',
             'moa/layout/head.html',
             'index.html']                                   # 홈 (2026-09-08)
ASSETS    = ['ds/css/detail.css', 'ds/js/detail-ui.js',
             'ds/css/price.css',  'ds/js/zg-ga4.js',
             'ds/css/home.css', 'ds/js/home-blocks.js', 'ds/js/home-hero.js']   # 홈
ALLFILES  = TEMPLATES + ASSETS


def _text(rel):
    return read(os.path.join(SKIN, rel))


def measure():
    obs = {'preserve': {}, 'hooks': {}, 'balance': {}, 'directives': {},
           'missing_paths': []}

    for rel in TEMPLATES:
        t = _text(rel)
        obs['preserve'][rel] = {k: t.count(k) for k in TOKENS}
        obs['balance'][rel] = {'div_open': len(re.findall(r'<div\b', t)),
                               'div_close': t.count('</div>')}

    # 훅은 7개 파일 어디에 있든 총계로 본다(위치가 옮겨가도 사라지지만 않으면 된다)
    for h in HOOKS:
        per = {}
        for rel in ALLFILES:
            c = _text(rel).count(h)
            if c:
                per[rel] = c
        obs['hooks'][h] = per

    for rel in ['ds/css/detail.css', 'ds/css/price.css', 'ds/css/home.css']:
        t = _text(rel)
        obs['balance'][rel] = {'brace_open': t.count('{'), 'brace_close': t.count('}')}

    # @css / @js / @import 경로가 실재하는 파일인지
    paths = {}
    for rel in TEMPLATES:
        t = _text(rel)
        for kind in ('css', 'js', 'import'):
            for m in re.finditer(r'<!--@%s\(([^)]*)\)-->' % kind, t):
                p = m.group(1).strip()
                paths.setdefault(p, []).append('%s(@%s)' % (rel, kind))
    obs['directives'] = {p: sorted(set(v)) for p, v in paths.items()}

    # 카카오 공유 키 값 (product/detail.html 의 #kakaoKey div 내용)
    m = KAKAO_RE.search(_text('product/detail.html'))
    obs['kakao_key'] = m.group(1) if m else None
    obs['missing_paths'] = sorted(
        p for p in paths if not os.path.isfile(os.path.join(SKIN, p.lstrip('/'))))
    return obs


def run(base, obs=None):
    s = Suite('A', u'보존 검사 (판매 정지급)')
    obs = obs or measure()
    b = base['A']

    # A1. 토큰 개수 — 감소 금지 (증가도 의도치 않으면 알린다)
    seen = 0
    for rel in TEMPLATES:
        exp = b['preserve'].get(rel, {})
        act = obs['preserve'][rel]
        for k, want in sorted(exp.items()):
            got = act.get(k, 0)
            seen += 1
            s.eq('A1.%s.%s' % (rel, k), u'%s 의 `%s` 개수' % (rel, k), want, got,
                 u'감소하면 그 자리의 카페24 기능이 죽는다' if got < want else '')
    s.probe('A1.probe', u'보존 토큰 비교 건수', seen)

    # A2. 플러그인 훅 8종
    for h in HOOKS:
        want = b['hooks'].get(h, {})
        got = obs['hooks'].get(h, {})
        wt = sum(want.values()); gt = sum(got.values())
        s.eq('A2.%s' % h, u'훅 `%s` 총 출현' % h, wt, gt,
             u'기대위치=%s 실제위치=%s' % (want or u'(스킨 밖: 관리자/라이브)', got or '-'))
    s.probe('A2.probe', u'스킨 파일에서 발견된 훅 종류',
            sum(1 for h in HOOKS if obs['hooks'].get(h)),
            u'0이면 파일 경로가 틀렸다는 뜻')

    # A3. 개폐 균형
    for rel in TEMPLATES:
        bal = obs['balance'][rel]
        s.eq('A3.div.%s' % rel, u'%s <div> 개폐 균형' % rel,
             bal['div_open'], bal['div_close'])
        s.eq('A3.divN.%s' % rel, u'%s <div> 개수' % rel,
             b['balance'][rel]['div_open'], bal['div_open'])
    for rel in ['ds/css/detail.css', 'ds/css/price.css', 'ds/css/home.css']:
        bal = obs['balance'][rel]
        s.eq('A3.brace.%s' % rel, u'%s 중괄호 균형' % rel,
             bal['brace_open'], bal['brace_close'])

    # A4. @css/@js/@import 경로 실재 여부
    #     저장소는 카페24 스킨의 부분 미러다 — 미러링 안 된 경로는 baseline 허용목록에 있다.
    allow = set(b['paths_missing_ok'])
    new_missing = [p for p in obs['missing_paths'] if p not in allow]
    gone = [p for p in allow if p not in obs['missing_paths']]
    s.eq('A4.new_missing', u'새로 깨진 @css/@js/@import 경로', [], new_missing,
         u'저장소에 없는 새 경로 = 라이브에서 404 위험')
    s.probe('A4.probe', u'검사한 디렉티브 경로 수', len(obs['directives']))
    if gone:
        s.add('A4.allow_stale', True, u'허용목록에 남은 죽은 항목(정보)', '-', gone,
              u'파일이 저장소에 생겼다 — baseline 정리 가능')

    # A5. 우리가 새로 선언한 경로(ds/)는 반드시 저장소에 실재해야 한다
    ours = [p for p in obs['directives'] if p.startswith('/ds/')]
    s.probe('A5.probe', u'우리 소유(/ds/) 디렉티브 수', len(ours))
    for p in ours:
        s.truthy('A5.%s' % p, u'우리 파일 실재: %s' % p,
                 os.path.isfile(os.path.join(SKIN, p.lstrip('/'))))

    # A5-kakao. #kakaoKey 값 형식 — 32자리 hex 여야 한다 (자리표시 문구·빈값이면 FAIL)
    #   T-1(2026-09-08): 자리표시 `(키 값은 스킨 원본 참조 …)` 가 전달본을 타고 미리보기에 들어가
    #   카카오 공유하기가 죽었다. 값 자체는 공개값이라 형식만 본다.
    kv = obs.get('kakao_key')
    s.probe('A5.kakaoKey.probe', u'product/detail.html 의 #kakaoKey div 탐지', 1 if kv is not None else 0)
    s.truthy('A5.kakaoKey.format', u'#kakaoKey 값이 32자리 hex (자리표시·빈값 아님)',
             bool(kv) and bool(KAKAO_FMT.match(kv)),
             u'실제: %r' % ((kv or '')[:12] + (u'…' if kv and len(kv) > 12 else '')))
    return s.done()


def to_baseline(obs):
    return {'preserve': obs['preserve'],
            'hooks': obs['hooks'],
            'balance': obs['balance'],
            'paths_missing_ok': obs['missing_paths']}
