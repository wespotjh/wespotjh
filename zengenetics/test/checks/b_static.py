# -*- coding: utf-8 -*-
u"""
B. 정적 검사 — 파일만 보고 판정할 수 있는 것.

출처
  - 신아린 4차 §5 「위생」 행: `!important` 0/0 · `node --check` 2/2 · 인명/판정용어 0건
  - 오세진 3차 §1 C-1·C-2 (인명·호칭 제거 확인) · C-3 (옛 경로 `ds/js/ga4.js`)
  - 개발 6차 §3 「스캔 패턴에 옛 경로 `ds/js/ga4.js` 를 상시 항목으로 추가했다」
  - 팀 README 「제출 동결」 — md5·바이트 표로 판정 대상을 고정

특히 B4(주석 안 `{$`)는 카페24 고유 함정이다. 템플릿 엔진은 **HTML 주석 안의
변수도 치환**한다. 치환 결과가 `-->` 를 만들거나 따옴표를 깨면 주석이 열린 채
남아 그 아래 마크업이 통째로 사라진다.  → HTML 템플릿에서만 0건이어야 한다.
(.js/.css 는 템플릿 엔진을 타지 않으므로 대상이 아니다.)
"""
import os, re
from .common import Suite, SKIN, read, md5, sh, strip_comments

TEMPLATES = ['product/detail.html',
             'moa/import/product_detail/detail.html',
             'moa/layout/head.html',
             'index.html']                                   # 홈 (2026-09-08)
CSS = ['ds/css/detail.css', 'ds/css/price.css', 'ds/css/home.css']
JS  = ['ds/js/detail-ui.js', 'ds/js/zg-ga4.js', 'ds/js/home-blocks.js', 'ds/js/home-hero.js']
ALL = TEMPLATES + CSS + JS

# 공개 소스에 나가면 안 되는 내부 토큰.
#  - 인명 9명 · 호칭 · 판정 용어 · 라운드 표기
FORBIDDEN = [
    u'이도현', u'신아린', u'배시우', u'문가온', u'조문규', u'나윤설', u'오세진',
    u'유나래', u'홍시아', u'대표님', u'판정서', u'반려', u'REJECT', u'컴플라이언스',
    u'검수 항목', u'검수 근거', u'차 제출', u'재작업',
]
OLD_PATH = 'ds/js/ga4.js'   # zg-ga4.js 로 개명되기 전 경로


def _p(rel):
    return os.path.join(SKIN, rel)


def _kind(rel):
    return 'html' if rel.endswith('.html') else ('css' if rel.endswith('.css') else 'js')


def comment_vars(rel):
    u"""HTML 주석 안에 남은 `{$` 위치. @css/@js/@import 디렉티브 주석은 제외."""
    if not rel.endswith('.html'):
        return []
    t = read(_p(rel))
    hits = []
    for m in re.finditer(r'<!--.*?-->', t, re.S):
        body = m.group(0)
        if re.match(r'<!--\s*@(css|js|import|layout)\(', body):
            continue
        for mm in re.finditer(r'\{\$', body):
            ln = t.count('\n', 0, m.start() + mm.start()) + 1
            hits.append('%s:%d' % (rel, ln))
    return hits


def measure():
    obs = {'md5': {}, 'bytes': {}, 'important': {}, 'jscheck': {},
           'forbidden': {}, 'old_path': {}, 'comment_vars': {}}
    for rel in ALL:
        obs['md5'][rel] = md5(_p(rel))
        obs['bytes'][rel] = os.path.getsize(_p(rel))

    for rel in CSS:
        # 주석을 지운 뒤 세야 한다 — 본문 주석에 "important-플래그" 설명이 많다
        code = strip_comments(read(_p(rel)), 'css')
        obs['important'][rel] = code.count('!important')

    for rel in JS:
        rc, out = sh(['node', '--check', _p(rel)])
        obs['jscheck'][rel] = {'rc': rc, 'out': out.strip()[:400]}

    for rel in ALL:
        t = read(_p(rel))
        hit = {}
        for tok in FORBIDDEN:
            c = t.count(tok)
            if c:
                hit[tok] = c
        obs['forbidden'][rel] = hit
        obs['old_path'][rel] = t.count(OLD_PATH)
        obs['comment_vars'][rel] = comment_vars(rel)
    return obs


def run(base, obs=None):
    s = Suite('B', u'정적 검사')
    obs = obs or measure()
    b = base['B']

    # B0. 제출 동결 — md5/바이트가 baseline 과 같은가
    #     (판정 도중 파일이 바뀌어 판정서가 자기모순에 빠진 사고의 재발 방지)
    for rel in ALL:
        s.eq('B0.md5.%s' % rel, u'%s md5' % rel,
             b['md5'][rel], obs['md5'][rel],
             u'다르면 파일이 바뀐 것. 의도적이면 --update-baseline')
        s.eq('B0.bytes.%s' % rel, u'%s 바이트' % rel, b['bytes'][rel], obs['bytes'][rel])
    s.probe('B0.probe', u'해시 고정 대상 파일 수', len(ALL))

    # B1. 새 !important 0개
    for rel in CSS:
        s.eq('B1.%s' % rel, u'%s 의 `!important` (주석 제외)' % rel,
             b['important'][rel], obs['important'][rel],
             u'설계 원칙 2 — 새 important 금지')

    # B2. node --check 전 JS
    for rel in JS:
        s.eq('B2.%s' % rel, u'node --check %s' % rel, 0, obs['jscheck'][rel]['rc'],
             obs['jscheck'][rel]['out'])

    # B3. 내부 인명·호칭·판정용어·이슈ID 0건
    for rel in ALL:
        hit = obs['forbidden'][rel]
        want = b['forbidden'].get(rel, {})
        s.eq('B3.%s' % rel, u'%s 내부 토큰' % rel, {}, hit,
             u'공개 소스에 나간다' + (u' / baseline 등재 기존 %d건' % sum(want.values()) if want else ''),
             known=(bool(want) and hit == want))
    s.probe('B3.probe', u'검사한 파일 수', len(ALL))
    # 스캐너 자체가 살아 있는지 — 일부러 존재하는 문자열로 자가검증
    self_ok = read(_p('ds/css/detail.css')).count(u'젠제네틱스') > 0
    s.truthy('B3.selftest', u'토큰 스캐너 자가검증(한글 매칭 동작)', self_ok,
             u'실패면 인코딩 문제로 B3 전체가 거짓 통과 중')

    # B4. HTML 주석 안 `{$` 0건 — 카페24 주석 내 변수 치환 함정
    for rel in TEMPLATES:
        got = obs['comment_vars'][rel]
        want = b['comment_vars'].get(rel, [])
        known = len(want) > 0
        s.eq('B4.%s' % rel, u'%s 주석 안 `{$`' % rel, [], got,
             u'baseline 등재 기존 결함 %d건' % len(want) if known else '',
             known=known and got == want)
    s.probe('B4.probe', u'주석 스캔한 템플릿 수', len(TEMPLATES))

    # B5. 옛 경로 문자열 `ds/js/ga4.js` 0건
    for rel in ALL:
        got = obs['old_path'][rel]
        want = b['old_path'].get(rel, 0)
        s.eq('B5.%s' % rel, u'%s 의 `%s`' % (rel, OLD_PATH), 0, got,
             u'baseline 등재 기존 결함(C-3 다음판 이월) %d건' % want if want else '',
             known=(want > 0 and got == want))
    return s.done()


def to_baseline(obs):
    return {'md5': obs['md5'], 'bytes': obs['bytes'],
            'important': obs['important'],
            'forbidden': {k: v for k, v in obs['forbidden'].items() if v},
            'comment_vars': {k: v for k, v in obs['comment_vars'].items() if v},
            'old_path': {k: v for k, v in obs['old_path'].items() if v}}
