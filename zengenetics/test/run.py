#!/usr/bin/env python3
# -*- coding: utf-8 -*-
u"""
젠제네틱스 카페24 상세 회귀 테스트 하네스 — 진입점.

  ./run.sh              전체 (A~E)
  ./run.sh --fast       정적만 (A·B) — 라이브·브라우저를 안 쓴다
  ./run.sh --only C,D   원하는 분류만
  ./run.sh --refresh    라이브 응답을 다시 받는다 (느리다)
  ./run.sh --update-baseline   현재 관측을 기준선으로 굳힌다 (의도적 변경 시에만)

설계 원칙
  - **기대값을 코드에 하드코딩하지 않는다.** 전부 baseline.json 에 있다.
  - 측정 코드와 baseline 생성 코드는 **같은 함수**(각 모듈의 measure())를 쓴다.
    둘이 갈리면 기준선이 조용히 틀려진다.
  - 실패는 「어느 검사가 · 무엇이 · 기대 대비 실제」를 반드시 찍는다.
"""
import argparse, json, os, sys, time

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from checks.common import (Suite, ROOT, OUT, C_RED, C_GRN, C_YEL, C_DIM, C_BLD, C_OFF,
                           load_baseline, save_baseline)
from checks.common import SKIN, md5 as _md5
from checks import a_preserve, b_static, c_render, d_datalayer, e_live, f_buypath, h_home

FROZEN = ['product/detail.html', 'moa/import/product_detail/detail.html',
          'ds/css/detail.css', 'ds/js/detail-ui.js', 'ds/css/price.css',
          'moa/layout/head.html', 'ds/js/zg-ga4.js',
          # 홈 (2026-09-08 추가)
          'index.html', 'ds/css/home.css', 'ds/js/home-blocks.js', 'ds/js/home-hero.js']


def snapshot():
    u"""판정 대상 11개 파일(상세 7 + 홈 4)의 해시. 팀 규칙 「제출 동결」 — 판정 시작·종료 2회 측정한다."""
    out = {}
    for rel in FROZEN:
        p = os.path.join(SKIN, rel)
        out[rel] = _md5(p) if os.path.exists(p) else None
    return out

ORDER = ['A', 'B', 'C', 'D', 'E', 'F', 'H']
MOD = {'A': a_preserve, 'B': b_static, 'C': c_render, 'D': d_datalayer, 'E': e_live,
       'F': f_buypath, 'H': h_home}
FAST = ['A', 'B']


def fmt(v, w=46):
    s = json.dumps(v, ensure_ascii=False) if isinstance(v, (dict, list)) else str(v)
    return s if len(s) <= w else s[:w - 1] + u'…'


def main():
    ap = argparse.ArgumentParser(add_help=True)
    ap.add_argument('--fast', action='store_true', help=u'정적 검사(A·B)만')
    ap.add_argument('--only', default='', help=u'A,B,C,D,E,F,H 중 골라서')
    ap.add_argument('--refresh', action='store_true', help=u'라이브 응답 재수집')
    ap.add_argument('--update-baseline', action='store_true', dest='update')
    ap.add_argument('--files', default='',
                    help=u'--update-baseline 과 함께: 갱신을 허용할 파일(저장소 상대경로, 쉼표). '
                         u'A/B 구역에서 이 목록 밖 파일의 항목이 바뀌어 있으면 갱신을 거부한다')
    ap.add_argument('--verbose', '-v', action='store_true', help=u'PASS 항목도 전부 출력')
    a = ap.parse_args()

    sel = [c for c in (a.only.split(',') if a.only else (FAST if a.fast else ORDER)) if c in MOD]
    if not sel:
        print(u'검사 분류를 못 골랐다: %r' % a.only); return 2
    os.makedirs(OUT, exist_ok=True)

    t0 = time.time()
    snap0 = snapshot()
    print(u'%s젠제네틱스 카페24 상세 — 회귀 테스트%s  (%s)' % (C_BLD, C_OFF, u' · '.join(sel)))
    print(u'%s%s%s' % (C_DIM, '-' * 96, C_OFF))

    # ---------------- 관측 -------------------------------------------------
    obs, timing, errors = {}, {}, {}
    for c in sel:
        t = time.time()
        try:
            if c == 'E':
                obs[c] = MOD[c].measure(refresh=a.refresh)
            else:
                obs[c] = MOD[c].measure()
        except Exception as e:
            errors[c] = u'%s: %s' % (type(e).__name__, e)
            obs[c] = None
        timing[c] = time.time() - t
        print(u'  %s 관측 %.1fs%s' % (C_DIM, timing[c], C_OFF), end=' ', flush=True)
        print(u'%s%s%s' % (C_RED if c in errors else C_GRN, c, C_OFF))

    # ---------------- baseline 갱신 ----------------------------------------
    if a.update:
        base = load_baseline() if os.path.exists(os.path.join(ROOT, 'baseline.json')) else {}
        # 갱신 범위를 명시하지 않으면 거부한다. 한 세션의 갱신이 다른 세션의 미검수 파일을
        # "검수됨"으로 굳힌 사고(2026-09-08, detail.css)의 재발 방지.
        if not a.only:
            print(u'%sbaseline 갱신 거부 — --only 로 구역을 지정하라 (예: --only B,D --files ds/js/zg-ga4.js)%s' % (C_RED, C_OFF))
            return 2
        allow = set(f.strip().lstrip('/') for f in a.files.split(',') if f.strip())
        newbase = {}
        for c in sel:
            if obs[c] is None:
                print(u'%s%s 관측 실패 — baseline 갱신 중단: %s%s' % (C_RED, c, errors[c], C_OFF))
                return 2
            newbase[c] = MOD[c].to_baseline(obs[c])
        # A·B 는 파일별 항목이다 — 허용 목록 밖 파일이 바뀌어 있으면 거부
        refused = []
        for c in ('A', 'B'):
            if c not in newbase or c not in base:
                continue
            for sect, val in newbase[c].items():
                oldv = base[c].get(sect)
                if isinstance(val, dict) and all(isinstance(v, dict) or sect in ('md5', 'bytes', 'important', 'old_path') for v in val.values()):
                    # {file: ...} 또는 {hook: {file: n}} 형태
                    keys = set(val) | set(oldv or {})
                    for k in keys:
                        nv, ov = val.get(k), (oldv or {}).get(k)
                        if nv == ov:
                            continue
                        files = [k] if ('/' in k or k.endswith('.html')) else list(set(nv or {}) | set(ov or {}))
                        bad = [f for f in files if f not in allow]
                        if bad:
                            refused.append('%s.%s.%s' % (c, sect, k))
                elif val != oldv:
                    # paths_missing_ok 같은 목록 — 템플릿을 허용 목록에 넣었을 때만
                    if not any(f.endswith('.html') for f in allow):
                        refused.append('%s.%s' % (c, sect))
        if refused:
            print(u'%sbaseline 갱신 거부 — --files 밖 파일의 항목이 바뀌어 있다:%s' % (C_RED, C_OFF))
            for r in refused:
                print(u'    ' + r)
            print(u'  그 파일이 네 것이면 --files 에 넣고, 남의 것이면 그쪽이 갱신하게 두어라')
            return 2
        for c in sel:
            # 구역을 통째로 바꾸되, 사람이 남긴 '_note*' 메모는 이월한다 (갱신이 남의 메모를 지운 사고 방지)
            notes = dict((k, v) for k, v in (base.get(c) or {}).items() if k.startswith('_note'))
            base[c] = newbase[c]
            base[c].update(notes)
        base.setdefault('_meta', {})
        base['_meta']['updated'] = time.strftime('%Y-%m-%d %H:%M:%S')
        base['_meta']['note'] = u'의도적 변경으로 갱신했다면 커밋 메시지에 무엇을 왜 바꿨는지 남길 것'
        save_baseline(base)
        print(u'%sbaseline.json 갱신 (%s)%s' % (C_YEL, ','.join(sel), C_OFF))
        return 0

    base = load_baseline()

    # ---------------- 판정 -------------------------------------------------
    suites = []
    for c in sel:
        if obs[c] is None:
            s = Suite(c, MOD[c].__doc__.strip().split('\n')[0])
            s.fail('%s.MEASURE' % c, u'관측 단계 실패', errors[c])
            suites.append(s.done())
            continue
        try:
            s = MOD[c].run(base, obs[c])
        except Exception as e:
            s = Suite(c, u'판정 실패')
            s.fail('%s.RUN' % c, u'판정 단계 예외', u'%s: %s' % (type(e).__name__, e))
            s.done()
        s.elapsed = timing[c]
        suites.append(s)

    # ---------------- 출력 -------------------------------------------------
    for s in suites:
        head = u'%s[%s] %s%s' % (C_BLD, s.code, s.title, C_OFF)
        print(u'\n%s  %s(%.1fs)%s' % (head, C_DIM, s.elapsed, C_OFF))
        shown = 0
        for r in s.rows:
            if r['status'] == 'PASS' and not a.verbose:
                continue
            shown += 1
            col = C_GRN if r['status'] == 'PASS' else (C_YEL if r['status'] == 'KNOWN' else C_RED)
            print(u'  %s%-5s%s %-34s %s' % (col, r['status'], C_OFF, r['id'][:34], r['what']))
            if r['status'] != 'PASS':
                print(u'        기대: %s' % fmt(r['expect'], 80))
                print(u'        실제: %s' % fmt(r['actual'], 80))
                if r['note']:
                    print(u'        %s%s%s' % (C_DIM, r['note'], C_OFF))
        if not shown:
            print(u'  %s전부 통과 (%d항목)%s' % (C_DIM, s.n, C_OFF))

    # ---------------- 실행 중 파일 변동 검사 (팀 규칙: 시작·종료 2회 측정) ---
    snap1 = snapshot()
    moved = {k: [snap0[k], snap1[k]] for k in snap0 if snap0[k] != snap1[k]}
    sz = Suite('Z', u'제출 동결 (실행 중 파일 불변)')
    sz.eq('Z0.moved', u'검사가 도는 동안 바뀐 파일', {}, moved,
          u'바뀌었다면 이 실행 결과는 무효다 — 판정서가 자기모순에 빠진 그 사고다')
    sz.probe('Z0.probe', u'해시를 잰 판정 대상 파일 수',
             sum(1 for v in snap1.values() if v))
    suites.append(sz.done())
    if moved:
        for r in sz.rows:
            if r['status'] != 'PASS':
                print(u'\n  %sFAIL%s %-34s %s' % (C_RED, C_OFF, r['id'], r['what']))
                print(u'        실제: %s' % fmt(r['actual'], 90))
                print(u'        %s%s%s' % (C_DIM, r['note'], C_OFF))

    # ---------------- 요약표 -----------------------------------------------
    print(u'\n%s%s%s' % (C_DIM, '=' * 96, C_OFF))
    print(u'%s%-4s %-34s %6s %6s %6s %6s  %8s%s'
          % (C_BLD, u'분류', u'이름', u'검사', u'PASS', u'FAIL', u'KNOWN', u'시간', C_OFF))
    tp = tf = tk = tn = 0
    for s in suites:
        tp += s.npass; tf += s.nfail; tk += s.nknown; tn += s.n
        col = C_GRN if s.ok else C_RED
        print(u'%s%-4s%s %-34s %6d %6d %s%6d%s %s%6d%s  %7.1fs'
              % (col, s.code, C_OFF, s.title[:34], s.n, s.npass,
                 C_RED if s.nfail else C_DIM, s.nfail, C_OFF,
                 C_YEL if s.nknown else C_DIM, s.nknown, C_OFF, s.elapsed))
    print(u'%s%s%s' % (C_DIM, '-' * 96, C_OFF))
    print(u'%-4s %-34s %6d %6d %s%6d%s %s%6d%s  %7.1fs'
          % (u'계', u'', tn, tp, C_RED if tf else C_DIM, tf, C_OFF,
             C_YEL if tk else C_DIM, tk, C_OFF, time.time() - t0))
    verdict = (u'%sPASS%s' % (C_GRN + C_BLD, C_OFF) if tf == 0
               else u'%sFAIL%s' % (C_RED + C_BLD, C_OFF))
    print(u'\n판정: %s   (KNOWN %d건은 baseline 에 등재된 기존 결함이다 — 0 이 되면 baseline 에서 뺀다)'
          % (verdict, tk))

    with open(os.path.join(OUT, 'last-run.json'), 'wb') as f:
        f.write(json.dumps({'suites': [{'code': s.code, 'title': s.title, 'rows': s.rows,
                                        'elapsed': s.elapsed} for s in suites]},
                           ensure_ascii=False, indent=1).encode('utf-8'))
    return 0 if tf == 0 else 1


if __name__ == '__main__':
    sys.exit(main())
