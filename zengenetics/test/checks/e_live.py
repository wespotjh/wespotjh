# -*- coding: utf-8 -*-
u"""
E. 라이브 대조 — 오세진 QA카페24_칼륨_3차 §2-2 · 문가온 QASEO 4차 §6 방법의 자동화판.

  `curl` 로 상품 9종 + 홈 + 장바구니 + 주문서 + 주문완료를 **UA 3종**으로 받아:
   - `@css`/`@js` 404 개수 (예상된 것만 있어야 한다 — baseline 의 허용목록)
   - `<title>` 1개 · `canonical` 1개 · `facebook-domain-verification` 1개
     (09-06 사고: 전 페이지 title 2개 · canonical 2개, 상품이 홈을 canonical 로 가리킴)
   - 스킨에 하드코딩된 `기본 레이아웃` 이 라이브에 새어 나오지 않는가
   - 상세 이미지 IHDR 최소 폭 ≥ 640px (신아린 4차 §4: 640 미만이면 확대가 재발한다)

  라이브 응답은 캐시한다. `--refresh` 로 다시 받는다.
"""
import os, re
from .common import Suite
from . import fetch

UAS = ('iphone', 'android', 'desktop')
IMG_RE = re.compile(r'ec-data-src="([^"]+)"|<img[^>]+src="(/web/upload/NNEditor/[^"]+)"')


CSS_MIN_W = 640   # ds/css/detail.css 의 `min-width: min(100%, 640px)` 상수와 같아야 한다


def measure(refresh=False, log=print):
    fetch.fetch_all(refresh=refresh, uas=UAS, log=log)
    obs = {'pages': {}, 'assets404': {}, 'ihdr': {}}

    for ua in UAS:
        for name, url in fetch.PAGES:
            doc = fetch.html(ua, name)
            if doc is None:
                continue
            obs['pages']['%s/%s' % (ua, name)] = {
                'title': len(re.findall(r'<title[\s>]', doc, re.I)),
                'canonical': len(re.findall(r'rel=["\']canonical["\']', doc, re.I)),
                'fbdv': len(re.findall(r'facebook-domain-verification', doc, re.I)),
                'basic_layout': doc.count(u'기본 레이아웃'),
                'bytes': len(doc),
                'canonical_href': (re.search(r'<link[^>]+rel=["\']canonical["\'][^>]*href=["\']([^"\']+)', doc, re.I)
                                   or re.search(r'<link[^>]+href=["\']([^"\']+)["\'][^>]*rel=["\']canonical', doc, re.I)
                                   or [None, None])[1] if 'canonical' in doc else None,
            }

    # 주문서·주문완료 계측 3줄이 실려 있는가 (배시우 4차 d-1/d-2)
    #  스마트 주문서는 `/moa/` 스킨을 안 타므로 스킨 head.html 의 @js 가 도달하지 않는다.
    #  관리자 › 디자인 › 스마트 주문서 의 적용 중인 디자인에 3줄을 직접 넣어야 한다.
    obs['order_ga4'] = {}
    for ua in UAS:
        for name in ('orderform', 'order_result'):
            doc = fetch.html(ua, name) or ''
            obs['order_ga4']['%s/%s' % (ua, name)] = {
                'measurement_id': doc.count('G-GZHFY596SS'),
                'zg_ga4_js': doc.count('zg-ga4.js'),
            }

    # 우리 스킨이 선언하는 정적 자산이 라이브에서 몇 개 404 인가
    #  (아직 미배포 파일은 404 가 정상 — baseline 허용목록에 있다)
    doc = fetch.html('iphone', 'p11') or ''
    urls = set(fetch.same_origin_assets(doc))
    for extra in ('/ds/css/detail.css', '/ds/js/detail-ui.js', '/ds/js/zg-ga4.js',
                  '/ds/css/price.css', '/ds/css/basket.css', '/ds/js/basket.js'):
        urls.add(extra)
    obs['assets_scanned'] = len(urls)
    for u in sorted(urls):
        m = fetch.fetch_asset(u, refresh=refresh)
        if m['status'] != 200:
            obs['assets404'][u] = m['status']

    # 카카오 공유 키 — 라이브(skin4) vs 미리보기 작업본(skin10) (팀장 결정 T-3 · 오세진 ⓓ)
    #   미리보기는 캐시를 쓰지 않고 매번 받는다 — 대표님이 622행을 고치는 순간 KNOWN→PASS 로 바뀌어야 한다.
    obs['kakao'] = fetch.kakao_keys()

    # 상세 이미지 원본 폭
    for name in ['p%d' % n for n in fetch.PRODUCTS]:
        d = fetch.html('iphone', name)
        if not d:
            continue
        host = d[d.find('id="prdDetail"'):] if 'id="prdDetail"' in d else d
        host = host[:200000]
        imgs = []
        for m in IMG_RE.finditer(host):
            u = m.group(1) or m.group(2)
            if u and u.startswith('/web/upload'):
                imgs.append(u)
        widths = []
        for u in imgs[:40]:
            w = fetch.ihdr_width(u, refresh=refresh)
            if w:
                widths.append(w)
        obs['ihdr'][name] = {'n_img': len(imgs), 'n_read': len(widths),
                             'min': min(widths) if widths else None,
                             'max': max(widths) if widths else None}
    return obs


def run(base, obs=None, refresh=False):
    s = Suite('E', u'라이브 대조 (curl)')
    obs = obs or measure(refresh)
    b = base['E']

    s.probe('E0.pages', u'대조한 (UA×페이지) 수', len(obs['pages']))

    # E1. title / canonical / fbdv
    for key in sorted(obs['pages']):
        p = obs['pages'][key]
        exp = b['pages'].get(key)
        if exp is None:
            s.add('E1.new.%s' % key, False, u'baseline 에 없는 페이지', '-', key,
                  u'--update-baseline 필요')
            continue
        s.eq('E1.title.%s' % key, u'[%s] <title> 개수' % key, exp['title'], p['title'],
             u'2개면 09-06 사고 재발')
        s.eq('E1.canon.%s' % key, u'[%s] canonical 개수' % key, exp['canonical'], p['canonical'])
        s.eq('E1.fbdv.%s' % key, u'[%s] facebook-domain-verification' % key,
             exp['fbdv'], p['fbdv'], u'0이면 메타 광고 도메인 인증이 끊긴다')
        s.eq('E1.layout.%s' % key, u'[%s] 스킨 하드코딩 "기본 레이아웃" 노출' % key,
             0, p['basic_layout'])
        if exp.get('canonical_href') is not None:
            s.eq('E1.canonhref.%s' % key, u'[%s] canonical 대상' % key,
                 exp['canonical_href'], p['canonical_href'],
                 u'상품이 홈을 가리키면 색인이 통째로 사라진다')

    # E2. 404 — 예상된 것만
    allow = set(b['assets404_ok'])
    got = obs['assets404']
    new404 = {u: c for u, c in got.items() if u not in allow}
    fixed = sorted(u for u in allow if u not in got)
    s.eq('E2.new404', u'예상 밖 @css/@js 404', {}, new404,
         u'라이브에서 파일이 사라진 것 = 전 페이지 사고 위험')
    # ⚠ 예전에는 `len(allow) + len(got)` 를 탐지값으로 썼다 — **404 개수**다.
    #   라이브에 404 가 하나도 없으면(정상 상태!) 0 이 되어 검사가 스스로 FAIL 했다
    #   (basket.css/js 가 배포되면서 실제로 그렇게 됐다, 2026-09-11).
    #   탐지값은 「훑은 자산 수」여야 한다 — 그게 0 이어야만 검사가 헛돈 것이다.
    s.probe('E2.probe', u'상태를 확인한 자산 수', obs.get('assets_scanned', 0))
    if fixed:
        s.add('E2.fixed', True, u'404 였다가 200 이 된 자산(정보)', '-', fixed,
              u'배포가 됐다는 뜻 — baseline 갱신 시점')

    # E3. 상세 이미지 원본 폭 ≥ 640
    for name in sorted(obs['ihdr']):
        r = obs['ihdr'][name]
        s.probe('E3.probe.%s' % name, u'[%s] IHDR 을 읽은 이미지 수' % name, r['n_read'],
                u'0이면 이미지 URL 추출이 깨진 것')
        if r['min'] is not None:
            # 절대 하한(639px) 대신 **확대율**로 본다 — 13종으로 넓히니 34(637px)·93(635px)이
            # 하한을 2~4px 밑돌았는데, 그건 결함이 아니라 하한이 9종 표본에 맞춰져 있었던 것이다.
            # 이 검사가 원래 막으려던 것은 신아린 4차 §4 의 **+55% 확대**(400px 원본이 640 으로
            # 늘어 흐려지던 사건)다. 그래서 우리 CSS 상수(`min-width: min(100%,640px)`)가
            # 원본을 몇 % 늘리는지를 직접 재고 **1% 를 상한**으로 둔다.
            #   639→640 +0.16% · 637→640 +0.47% · 635→640 +0.79%  (전부 육안 식별 불가)
            #   400→640 +60%   ← 이건 걸린다
            # 상품이 늘어도 하한을 손볼 필요가 없다.
            ratio = round(float(CSS_MIN_W) / r['min'], 4)
            s.le('E3.%s' % name, u'[%s] 우리 CSS 상수(%dpx)가 원본을 늘리는 비율' % (name, CSS_MIN_W),
                 1.01, ratio,
                 u'원본 최소 폭 %spx. 1.01 초과면 768~1023px 뷰포트에서 확대가 눈에 보인다' % r['min'])
            # 상품별 실측값 자체도 고정한다 — 이미지를 바꿔 끼우면 여기서 잡힌다
            exp = (b.get('ihdr_by_product') or {}).get(name)
            if exp:
                s.eq('E3.fix.%s' % name, u'[%s] 상세 이미지 원본 폭 (min/max)' % name,
                     exp, [r['min'], r['max']],
                     u'이미지 교체 시 갱신. 낮아지면 확대 회귀')
    # E4. 주문서·주문완료 계측 3줄 (배시우 4차 d-1·d-5)
    #     목표 상태는 "각 1건 이상". 현재 0건이면 baseline 에 등재돼 KNOWN 으로 뜬다.
    #     대표님이 3줄을 붙여넣고 적용하면 자동으로 PASS 로 바뀐다.
    for key in sorted(obs.get('order_ga4', {})):
        got = obs['order_ga4'][key]
        want = (b.get('order_ga4') or {}).get(key, {})
        for f, label in (('measurement_id', u'G-GZHFY596SS'), ('zg_ga4_js', u'zg-ga4.js')):
            known = want.get(f, 0) == 0 and got[f] == 0
            s.add('E4.%s.%s' % (key, f), got[f] >= 1,
                  u'[%s] 계측 `%s` 실림' % (key, label), '>= 1', got[f],
                  u'0이면 결제단계(begin_checkout)·매출(purchase)이 GA4 에 0건으로 남는다'
                  u' — 관리자 › 디자인 › 스마트 주문서에 3줄 삽입 필요 (배시우 4차 d-3)',
                  known=known)
    s.probe('E4.probe', u'주문서 계측 확인한 (UA×페이지) 수', len(obs.get('order_ga4', {})))

    # E5. #kakaoKey — 라이브 값은 32-hex, 미리보기 작업본 값은 라이브와 동일해야 한다
    #     자리표시 문구가 들어간 미리보기는 baseline `kakao_preview_known` 이 true 인 동안 KNOWN,
    #     대표님이 622행을 고치면 다음 실행에서 자동으로 PASS.
    kk = obs.get('kakao') or {}
    fmt = fetch.KAKAO_FMT
    s.probe('E5.probe.live', u'라이브 p11 의 #kakaoKey div 탐지', 1 if kk.get('live') is not None else 0)
    s.probe('E5.probe.preview', u'미리보기(skin10) p11 응답·#kakaoKey div 탐지',
            1 if kk.get('preview') is not None else 0,
            u'0이면 미리보기 URL 이 죽었거나 div 가 사라진 것')
    live_ok = bool(kk.get('live')) and bool(fmt.match(kk['live']))
    s.truthy('E5.live.format', u'라이브 #kakaoKey 가 32자리 hex', live_ok)
    prev = kk.get('preview')
    prev_ok = bool(prev) and bool(fmt.match(prev))
    known = bool(b.get('kakao_preview_known')) and not prev_ok
    s.add('E5.preview.format', prev_ok, u'미리보기 #kakaoKey 가 32자리 hex (자리표시 아님)',
          '32-hex', (prev or '')[:16], u'대표님 622행 1줄 수정 대기 (T-2)', known=known)
    same = bool(prev_ok and live_ok and prev == kk['live'])
    s.add('E5.same', same, u'미리보기 #kakaoKey == 라이브 값 (같은 몰·같은 앱)',
          u'동일', u'동일' if same else u'다름', u'다르면 도메인 등록이 다른 앱 키다',
          known=(bool(b.get('kakao_preview_known')) and not same))
    return s.done()


def to_baseline(obs):
    return {'pages': obs['pages'],
            'assets404_ok': sorted(obs['assets404'].keys()),
            # 하한 639 = 신아린 4차 §4 가 실측·승인한 바닥값 (라이브 101장이 639~640px)
            'ihdr_min': 639,
            'ihdr_by_product': {k: [v['min'], v['max']]
                                for k, v in obs['ihdr'].items() if v['min']},
            'order_ga4': obs.get('order_ga4', {}),
            # 미리보기 #kakaoKey 가 아직 자리표시면 KNOWN 으로 두는 플래그 — 고쳐지면 PASS 로 자동 전환
            'kakao_preview_known': not ((obs.get('kakao') or {}).get('preview_ok'))}
