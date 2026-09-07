# -*- coding: utf-8 -*-
u"""
D. 계측 검사 — 배시우 QA계측_칼륨_3차 §4 / 4차 (a) 방법의 자동화판.

  `zg-ga4.js` + `detail-ui.js` 를 실제로 올리고 `window.dataLayer` 를 받아
  **이벤트 목록과 파라미터 키**를 baseline 과 비교한다.
  합격 조건: 기존 이벤트 **소실 0** · **중복 0**.

  덧붙여 배시우가 매 라운드 확인하는 것들:
   - `zg_ver` 전수 일치 (버전 스탬프 누락 0)
   - `send_to` 누락 0
   - PII 0 (이메일·전화번호 형태 문자열이 파라미터에 없어야 한다)
   - 회귀 4페이지: 장바구니 `view_cart` · 주문서 `begin_checkout` · 완료 `purchase`

거짓 통과 방지
  - 클릭 스텝의 셀렉터가 하나라도 안 잡히면(`stepMiss`) FAIL. 아무것도 안 눌러 놓고
    "중복 없음"으로 통과하는 것을 막는다.
  - baseline 에 있는 이벤트가 관측에 없으면 소실로 FAIL.
"""
import json, os, re
from .common import Suite, ROOT, node, OUT
from . import fixture

PII = re.compile(r'[\w.+-]+@[\w-]+\.[\w.]+|01[016-9]-?\d{3,4}-?\d{4}')


def scenarios():
    f11, _ = fixture.build('iphone', 'p11', with_ga4=True)
    f61, _ = fixture.build('iphone', 'p61', with_ga4=True)
    fbk, _ = fixture.build('iphone', 'basket', with_ga4=True, delta=False, with_ui=False)
    fhm, _ = fixture.build('iphone', 'home', with_ga4=True, delta=False, with_ui=False)
    # 주문서(/order/orderform.html)·주문완료는 **비로그인·빈 장바구니면 홈으로 리다이렉트**된다.
    # 세션 없이 curl 로 받은 HTML 은 로드 즉시 location 이 '/' 로 바뀌어 측정 자체가 불가능하다.
    # → `begin_checkout` / `purchase` 는 실주문이 필요한 **실기 항목**으로 남긴다(README §자동화 못 한 것).
    #   대신 그 두 페이지에 계측 3줄이 실려 있는지는 E4(라이브 대조)가 정적으로 본다.
    return [
        {'name': 'p11_load', 'vp': 390, 'docPath': '/product/detail.html?product_no=11',
         'fixture': f11, 'settle': 1600, 'assets': fixture.asset_map('iphone', 'p11')},
        {'name': 'p11_interact', 'vp': 390, 'docPath': '/product/detail.html?product_no=11',
         'fixture': f11, 'settle': 1600, 'steps': ['.zg-opt', '.zg-more', '__scroll__'],
         'assets': fixture.asset_map('iphone', 'p11')},
        {'name': 'p61_load', 'vp': 390, 'docPath': '/product/detail.html?product_no=61',
         'fixture': f61, 'settle': 1600, 'assets': fixture.asset_map('iphone', 'p61')},
        {'name': 'basket', 'vp': 390, 'docPath': '/order/basket.html',
         'fixture': fbk, 'settle': 1400, 'assets': fixture.asset_map('iphone', 'basket')},
        {'name': 'home', 'vp': 390, 'docPath': '/', 'steps': ['__scroll__'],
         'fixture': fhm, 'settle': 1400, 'assets': fixture.asset_map('iphone', 'home')},
    ]


# 매출·전환에 직결되는 값. 키만 보면 "값이 0원이 된 것"을 못 잡는다.
CRITICAL = {
    'view_item': ['currency', 'value'],
    'add_to_cart': ['currency', 'value'],
    'zg_option_select': ['item_id'],
}


def _critical(dl):
    out = {}
    for e in dl:
        if e.get('kind') != 'event':
            continue
        n = e.get('name')
        if n not in CRITICAL:
            continue
        pr = e.get('params') or {}
        rec = {k: pr.get(k) for k in CRITICAL[n]}
        items = pr.get('items')
        if isinstance(items, list) and items and isinstance(items[0], dict):
            rec['item_id'] = items[0].get('item_id')
            rec['item_name'] = items[0].get('item_name')
        out.setdefault(n, []).append(rec)
    return out


def _shape(dl):
    u"""dataLayer 를 비교 가능한 형태로 축약: 이벤트별 개수 + 파라미터 키 집합."""
    events, keys = {}, {}
    for e in dl:
        if e.get('kind') != 'event':
            continue
        n = e.get('name')
        events[n] = events.get(n, 0) + 1
        ks = sorted((e.get('params') or {}).keys())
        keys.setdefault(n, set()).update(ks)
    return events, {k: sorted(v) for k, v in keys.items()}


def measure():
    sc = scenarios()
    cfg = {'ua': fixture.fetch.UA['iphone'], 'ours': fixture.OURS,
           'assets': fixture.asset_map('iphone', 'p11'), 'scenarios': sc}
    p = os.path.join(os.path.dirname(sc[0]['fixture']), 'cfg-datalayer.json')
    with open(p, 'wb') as f:
        f.write(json.dumps(cfg, ensure_ascii=False).encode('utf-8'))
    rc, out, data = node(os.path.join(ROOT, 'js', 'datalayer.mjs'), p, timeout=1800)
    if data is None:
        raise RuntimeError(u'계측 하네스 실패(rc=%s):\n%s' % (rc, out[-2500:]))
    with open(os.path.join(OUT, 'datalayer.json'), 'wb') as f:
        f.write(json.dumps(data, ensure_ascii=False, indent=1).encode('utf-8'))
    obs = {}
    for r in data['results']:
        ev, ks = _shape(r.get('dl') or [])
        vers, sends, pii = set(), 0, []
        for e in (r.get('dl') or []):
            if e.get('kind') != 'event':
                continue
            pr = e.get('params') or {}
            if 'zg_ver' in pr:
                vers.add(str(pr['zg_ver']))
            if 'send_to' not in pr:
                sends += 1
            blob = json.dumps(pr, ensure_ascii=False)
            if PII.search(blob):
                pii.append(e.get('name'))
        obs[r['name']] = {'critical': _critical(r.get('dl') or []),
                          'ok': r.get('ok'), 'boot': r.get('boot'),
                          'stepMiss': r.get('stepMiss') or [],
                          'events': ev, 'keys': ks, 'zg_ver': sorted(vers),
                          'missing_send_to': sends, 'pii': pii,
                          'errorsOurs': len(r.get('errorsOurs') or []),
                          'error': r.get('error')}
    return obs


def run(base, obs=None):
    s = Suite('D', u'계측 검사 (dataLayer)')
    obs = obs or measure()
    b = base['D']
    s.probe('D0.scenarios', u'실행한 계측 시나리오 수', len(obs))

    for name in sorted(b['scenarios'].keys()):
        want = b['scenarios'][name]
        got = obs.get(name)
        if not got or not got.get('ok'):
            s.fail('D0.%s' % name, u'[%s] 시나리오 실행' % name,
                   (got or {}).get('error', 'no result'))
            continue

        # 하네스가 실제로 부팅했는가
        s.truthy('D0.boot.%s' % name, u'[%s] dataLayer 존재' % name,
                 (got['boot'] or {}).get('hasDataLayer'))
        s.eq('D0.step.%s' % name, u'[%s] 못 찾은 클릭 셀렉터' % name, [], got['stepMiss'],
             u'셀렉터가 안 잡히면 아무것도 안 누른 채 통과한다')
        s.probe('D0.nev.%s' % name, u'[%s] 관측 이벤트 종류 수' % name, len(got['events']))

        # 소실 0
        lost = sorted(k for k in want['events'] if k not in got['events'])
        s.eq('D1.lost.%s' % name, u'[%s] 소실 이벤트' % name, [], lost)
        # 중복 0 (baseline 개수 초과)
        dup = {k: [want['events'][k], got['events'][k]]
               for k in want['events'] if got['events'].get(k, 0) > want['events'][k]}
        s.eq('D1.dup.%s' % name, u'[%s] 중복 발사(baseline 초과)' % name, {}, dup)
        # 신규(예상 못 한) 이벤트
        new = sorted(k for k in got['events'] if k not in want['events'])
        s.eq('D1.new.%s' % name, u'[%s] baseline 에 없는 신규 이벤트' % name, [], new,
             u'의도한 신규면 --update-baseline')
        # 파라미터 키 소실
        klost = {k: sorted(set(want['keys'][k]) - set(got['keys'].get(k, [])))
                 for k in want['keys'] if set(want['keys'][k]) - set(got['keys'].get(k, []))}
        s.eq('D2.keys.%s' % name, u'[%s] 파라미터 키 소실' % name, {}, klost)

        # 매출·전환 값 (0원·빈값으로 무너지는 것을 키 검사로는 못 잡는다)
        s.eq('D2.crit.%s' % name, u'[%s] 매출·전환 핵심 값' % name,
             want.get('critical', {}), got.get('critical', {}),
             u'`view_item.value` 가 0 이 되면 GA4 매출이 통째로 틀어진다')

        # 버전 스탬프 · send_to · PII
        s.eq('D3.ver.%s' % name, u'[%s] zg_ver' % name, want['zg_ver'], got['zg_ver'])
        s.eq('D3.send.%s' % name, u'[%s] send_to 누락 이벤트 수' % name, 0, got['missing_send_to'])
        s.eq('D3.pii.%s' % name, u'[%s] PII 형태 값' % name, [], got['pii'])
        s.eq('D3.err.%s' % name, u'[%s] 우리 JS 예외' % name, 0, got['errorsOurs'])

    # baseline 에 없는 시나리오가 관측됐다면 알린다
    extra = sorted(set(obs) - set(b['scenarios']))
    s.eq('D0.extra', u'baseline 에 없는 시나리오', [], extra)
    return s.done()


def to_baseline(obs):
    out = {}
    for name, r in obs.items():
        if not r.get('ok'):
            raise RuntimeError(u'계측 baseline: %s 시나리오가 실패한 상태다 — 갱신 거부' % name)
        out[name] = {'events': r['events'], 'keys': r['keys'],
                     'zg_ver': r['zg_ver'], 'critical': r['critical']}
    return {'scenarios': out}
