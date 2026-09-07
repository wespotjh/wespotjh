# -*- coding: utf-8 -*-
u"""
C. 실렌더 검사 (Chromium) — 신아린 QA모바일_칼륨_4차 방법의 자동화판.

출처
  §1 H-1 이미지 확대 (641·768·900·1023px 에서 1.00x)
  §2 H-2 가로 넘침 (320·390·414·768·1023·1280 에서 scrollWidth == clientWidth)
  §4 `min(100%,640px)` 상수 반례 — 원본 400px 이면 768/1023px 에서 1.60x 로 확대된다
  §5 G-1/G-2 하단바 82px · 푸터 여유 > 0 · safe 0/34 양쪽 · 1024↑ 바 display:none
  §5 갤러리 `.thumbnail__list > li` 4개 · 바텀시트 3버튼 겹침 [0,0,0] · pageerror 0
  §5 지연로딩/색인 `ec-data-src` 0 · `src` 14/14 · `alt` 14/14

거짓 통과 방지
  - 템플릿 델타(`.zg-detail`/`.zg-fold`/카드)가 실제로 적용됐는지 landmark 로 먼저 확인한다.
    하나라도 0이면 그 뷰포트 결과 전체를 신뢰하지 않는다.
  - **음성 대조군**: 원본 폭 400px 스텁을 넣으면 확대가 **일어나야** 한다.
    안 일어나면 확대 측정 자체가 죽은 것이므로 FAIL 이다.
"""
import json, os
from .common import Suite, ROOT, node, OUT
from . import fixture

VP_OVERFLOW = [320, 390, 414, 768, 1023, 1280]
VP_ZOOM     = [641, 768, 900, 1023]
VP_BAR      = [320, 390, 414, 768, 1023]
VP_NOBAR    = [1024, 1280]


def scenarios():
    sc = []
    for vp in VP_OVERFLOW:
        sc.append({'name': 'ovf%d' % vp, 'vp': vp, 'safe': 0, 'settle': 1100})
    for vp in VP_BAR:
        for safe in (0, 34):
            sc.append({'name': 'bar%d_s%d' % (vp, safe), 'vp': vp, 'safe': safe, 'settle': 1100})
    for vp in VP_NOBAR:
        sc.append({'name': 'nobar%d' % vp, 'vp': vp, 'safe': 0, 'settle': 1100})
    for vp in VP_ZOOM:
        sc.append({'name': 'zoom%d' % vp, 'vp': vp, 'safe': 0, 'settle': 1100,
                   'stub': {'w': 640, 'h': 948}, 'expand': True})
    # 음성 대조군 — 원본이 좁으면 확대가 일어나야 한다 (신아린 §4)
    for vp in (768, 1023):
        sc.append({'name': 'neg%d' % vp, 'vp': vp, 'safe': 0, 'settle': 1100,
                   'stub': {'w': 400, 'h': 600}, 'expand': True})
    sc.append({'name': 'sheet390', 'vp': 390, 'safe': 0, 'settle': 1300, 'sheet': True})
    return sc


def measure():
    f, diag = fixture.build('iphone', 'p11')
    cfg = fixture.write_cfg('render', '/product/detail.html?product_no=11', f, scenarios())
    rc, out, data = node(os.path.join(ROOT, 'js', 'render.mjs'), cfg, timeout=1800)
    if data is None:
        raise RuntimeError(u'렌더 하네스 실패(rc=%s):\n%s' % (rc, out[-2500:]))
    res = {r['name']: r for r in data['results']}
    with open(os.path.join(OUT, 'render.json'), 'wb') as fp:
        fp.write(json.dumps(data, ensure_ascii=False, indent=1).encode('utf-8'))
    return {'diag': diag, 'res': res}


def _land(s, r, tag):
    u"""델타·랜드마크가 살아 있는지 — 여기서 실패하면 그 뷰포트 결과는 무의미하다."""
    m = r.get('m') or {}
    d = m.get('delta') or {}
    ok = True
    ok &= s.eq('C0.%s.delta_err' % tag, u'[%s] 템플릿 델타 예외' % tag, None, d.get('err'))
    for k, want in (('zgDetail', 1), ('zgFold', 1), ('zgMore', 1), ('zgChip', 3)):
        ok &= s.eq('C0.%s.%s' % (tag, k), u'[%s] 델타 %s' % (tag, k), want, d.get(k))
    L = m.get('landmarks') or {}
    for k in ('prdDetail', 'zgBar', 'optionSelect'):
        s.probe('C0.%s.%s' % (tag, k), u'[%s] landmark %s' % (tag, k), L.get(k, 0))
    return ok


def run(base, obs=None):
    s = Suite('C', u'실렌더 검사 (Chromium)')
    obs = obs or measure()
    res = obs['res']
    b = base['C']

    s.truthy('C0.fixture.css', u'픽스처: 사용자 CSS 번들 앵커', obs['diag']['css_anchor'])
    s.truthy('C0.fixture.js', u'픽스처: 사용자 JS 번들 앵커', obs['diag']['js_anchor'])
    s.probe('C0.scenarios', u'실행한 렌더 시나리오 수', len(res))

    # --- C1. 가로 넘침 0 --------------------------------------------------
    for vp in VP_OVERFLOW:
        r = res.get('ovf%d' % vp)
        if not r or not r.get('ok'):
            s.fail('C1.%d' % vp, u'%dpx 렌더' % vp, (r or {}).get('error', 'no result')); continue
        _land(s, r, 'ovf%d' % vp)
        o = r['m']['overflow']
        s.eq('C1.%d' % vp, u'%dpx scrollWidth == clientWidth' % vp,
             o['clientWidth'], o['scrollWidth'], u'다르면 가로 스크롤이 생긴다')

    # --- C2. 하단바 높이 · 푸터 여유 --------------------------------------
    for vp in VP_BAR:
        for safe in (0, 34):
            tag = 'bar%d_s%d' % (vp, safe)
            r = res.get(tag)
            if not r or not r.get('ok'):
                s.fail('C2.%s' % tag, u'%s 렌더' % tag, (r or {}).get('error', 'no result')); continue
            m = r['m']
            want_h = b['bar_height'][str(safe)]
            s.eq('C2.h.%s' % tag, u'[%dpx safe%d] 하단바 높이' % (vp, safe), want_h, m['bar']['h'])
            s.truthy('C2.vis.%s' % tag, u'[%dpx safe%d] 하단바 표시' % (vp, safe), m['bar']['visible'])
            s.probe('C2.probe.%s' % tag, u'[%s] 푸터 마지막 콘텐츠 탐지' % tag,
                    1 if m.get('footerProbe') else 0)
            gap = m.get('footerGap')
            s.add('C2.gap.%s' % tag, isinstance(gap, (int, float)) and gap > 0,
                  u'[%dpx safe%d] 푸터 여유 > 0' % (vp, safe), '> 0', gap,
                  u'0 이하면 사업자정보가 하단바에 가린다')
        # safe 가 늘어난 만큼 스크롤 영역이 늘어야 한다 (margin 으론 안 늘어난다 — 신아린 §5)
        r0, r34 = res.get('bar%d_s0' % vp), res.get('bar%d_s34' % vp)
        if r0 and r34 and r0.get('ok') and r34.get('ok'):
            s.eq('C2.scroll.%d' % vp, u'[%dpx] safe 34 일 때 scrollHeight 증가분' % vp, 34,
                 r34['m']['scrollHeight'] - r0['m']['scrollHeight'],
                 u'body padding 이 아니라 margin 으로 잡으면 0 이 된다')
            s.eq('C2.gapinv.%d' % vp, u'[%dpx] 푸터 여유가 safe 와 무관한가' % vp,
                 r0['m']['footerGap'], r34['m']['footerGap'])

    for vp in VP_NOBAR:
        r = res.get('nobar%d' % vp)
        if not r or not r.get('ok'):
            s.fail('C2.nobar%d' % vp, u'%dpx 렌더' % vp, (r or {}).get('error', 'no result')); continue
        s.eq('C2.nobar%d' % vp, u'[%dpx] 하단바 display' % vp, 'none', r['m']['bar']['display'])

    # --- C3. 상세 이미지 확대 배율 ----------------------------------------
    for vp in VP_ZOOM:
        r = res.get('zoom%d' % vp)
        if not r or not r.get('ok'):
            s.fail('C3.%d' % vp, u'%dpx 렌더' % vp, (r or {}).get('error', 'no result')); continue
        z = r['m']['zoom']
        s.truthy('C3.expand.%d' % vp, u'[%dpx] 접기 펼침 클릭' % vp, r.get('expandClicked'))
        s.eq('C3.n.%d' % vp, u'[%dpx] 배율을 잰 상세 이미지 수 (펼친 뒤 14/14)' % vp,
             b['detail_imgs'], z['n'],
             u'모자라면 naturalWidth 를 못 읽은 것 = 거짓 통과 위험')
        s.near('C3.%d' % vp, u'[%dpx] 상세 이미지 최대 확대 배율' % vp, 1.00, z['max'], 0.01,
               u'1.00 초과 = 원본보다 크게 늘려 그린다(화질 회귀)')

    # --- C3-N. 음성 대조군: 좁은 원본이면 확대가 "일어나야" 한다 ----------
    for vp in (768, 1023):
        r = res.get('neg%d' % vp)
        if not r or not r.get('ok'):
            s.fail('C3N.%d' % vp, u'음성대조 %dpx' % vp, (r or {}).get('error', 'no result')); continue
        z = r['m']['zoom']
        s.probe('C3N.n.%d' % vp, u'[음성대조 %dpx] 잰 이미지 수' % vp, z['n'])
        s.add('C3N.%d' % vp, isinstance(z['max'], float) and z['max'] > 1.05,
              u'[음성대조 %dpx] 원본 400px 이면 확대가 발생해야 한다' % vp, '> 1.05', z['max'],
              u'확대가 안 잡히면 C3 전체가 죽은 검사다 (신아린 4차 §4 반례)')

    # --- C4. 갤러리 / 지연로딩 / 접기 -------------------------------------
    r = res.get('bar390_s0')
    if r and r.get('ok'):
        m = r['m']
        s.eq('C4.gallery', u'갤러리 `.thumbnail__list > li` 표시 수',
             b['gallery_li'], m['gallery']['liVisible'])
        s.eq('C4.lazy.ec', u'`#prdDetail img[ec-data-src]` 잔존', 0, m['lazy']['ecDataSrc'],
             u'남아 있으면 색인에서 사라진다')
        s.eq('C4.lazy.src', u'`#prdDetail img[src]`', b['detail_imgs'], m['lazy']['withSrc'])
        s.eq('C4.lazy.alt', u'`#prdDetail img[alt]` 채움', b['detail_imgs'], m['lazy']['withAlt'])
        s.eq('C4.fold', u'`.zg-fold` max-height(모바일)', b['fold_max_mobile'],
             m['fold']['maxHeight'])
        s.truthy('C4.more', u'`.zg-more` 버튼 존재', m['fold']['more'])
        # 삭제 섹션 잔재
        s.eq('C4.ghost', u'빈 공간 잔재 블록(높이 24px+ 인데 내용 없음)', [], m['ghostBlocks'])
        s.eq('C4.dblmargin', u'이중 여백(인접 형제 margin 24px+ 양쪽)', [], m['doubleMargins'])
        # a11y 숨김 select
        a = m.get('a11ySelect')
        s.probe('C4.a11y.probe', u'숨김 select 탐지', 1 if a else 0)
        if a:
            s.eq('C4.a11y.w', u'숨김 select 폭 (=2*padding10 + 2*border1)', b['a11y_select']['w'], a['w'])
            s.eq('C4.a11y.h', u'숨김 select 높이', b['a11y_select']['h'], a['h'])
            s.eq('C4.a11y.display', u'숨김 select display (none 이면 카페24 검증이 깨진다)',
                 'block', a['display'])
            s.eq('C4.a11y.hit', u'숨김 select 가 클릭을 가로채는가', None, a['hit'])
    else:
        s.fail('C4', u'390px 기준 렌더', 'no result')

    # --- C5. 바텀시트 겹침 -------------------------------------------------
    r = res.get('sheet390')
    if r and r.get('ok') and r.get('sheet'):
        sh = r['sheet']
        s.truthy('C5.open', u'바텀시트 열림', sh.get('opened') and sh.get('sheetVisible'))
        s.eq('C5.overlap', u'시트 3버튼 ↔ 하단바 겹침(px)', [0, 0, 0], sh.get('buttonOverlap'))
        s.add('C5.hit', 'btnNormal' in str(sh.get('hitOnBar')) or 'mobile-layer' in str(sh.get('hitOnBar')),
              u'하단바 위치의 최상단 요소가 시트 요소인가', u'시트 요소', sh.get('hitOnBar'))
    else:
        s.fail('C5', u'바텀시트 시나리오', 'no result')

    # --- C6. pageerror 0 ---------------------------------------------------
    tot_ours = 0
    for name, r in sorted(res.items()):
        tot_ours += len(r.get('errorsOurs') or [])
    s.eq('C6.ours', u'우리 파일(/ds/)에서 난 JS 예외 총합', 0, tot_ours,
         u'교차출처 차단으로 나는 남의 전역 미정의 예외는 제외')
    third = sum(len(r.get('errors') or []) for r in res.values()) - tot_ours
    s.eq('C6.third', u'하네스 환경(교차출처 차단)에서 나는 남의 예외', b['third_party_errors'], third,
         u'변하면 라이브 페이지 구성이 바뀐 것 — 확인 후 baseline 갱신')
    return s.done()


def to_baseline(obs):
    res = obs['res']
    m390 = res['bar390_s0']['m']
    third = 0
    ours = 0
    for r in res.values():
        ours += len(r.get('errorsOurs') or [])
        third += len(r.get('errors') or [])
    third -= ours
    return {
        'bar_height': {'0': res['bar390_s0']['m']['bar']['h'],
                       '34': res['bar390_s34']['m']['bar']['h']},
        'gallery_li': m390['gallery']['liVisible'],
        'detail_imgs': m390['lazy']['withSrc'],
        'fold_max_mobile': m390['fold']['maxHeight'],
        'a11y_select': {'w': m390['a11ySelect']['w'], 'h': m390['a11ySelect']['h']},
        'third_party_errors': third,
    }
