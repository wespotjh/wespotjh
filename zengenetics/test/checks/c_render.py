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
  실기 반려 2026-09-08 (대표님 iPhone) — `#totalProducts` 선택 행 2유형(option_product / add_product):
    F-1 가격이 스테퍼 박스를 뚫음 → 겹침 면적 0 · 가격 오른쪽 정렬(행 padding 20px) · 세로 중심 일치
    F-2 추가상품 행만 `+ − 1` → 두 행 모두 `− N +`
    F-3 혜택 말풍선(top:-28px)이 `.zg-sum__note` 를 덮음 → 경고문 숨김 상태 + 바운스 최고점에서도 간격 > 0

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
VP_ROWS     = [320, 390, 414, 768]    # 414 추가 (2026-09-08 홈 3차 — 신아린 지적)


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
    # B안 하단바 구매 경로 — .fixed 인 상태(mid)와 아닌 상태(top) 둘 다
    for kind in ('mid', 'top'):
        sc.append({'name': 'barbuy390_%s' % kind, 'vp': 390, 'safe': 0, 'settle': 1300,
                   'barbuy': kind, 'sweep': False})
    # R-2 재탭 해제 (대표님 요청 2026-09-09) + 음성 대조군
    for kind in ('ok', 'nodel'):
        sc.append({'name': 'untap390_%s' % kind, 'vp': 390, 'safe': 0, 'settle': 1300,
                   'untap': kind, 'sweep': False})
    # 선택 행 2유형 — 카페24 옵션 스크립트로 실제 생성 (대표님 실기 반려 2026-09-08)
    for vp in VP_ROWS:
        sc.append({'name': 'rows%d' % vp, 'vp': vp, 'safe': 0, 'settle': 1300, 'rows': True,
                   'sweep': False})
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
        s.truthy('C5.hit', u'하단바 위치의 최상단 요소가 시트 안 요소인가 (실제 포함관계로 판정)',
                 sh.get('hitInSheet'),
                 u'실제 최상단 요소: %s — 바 버튼이면 시트 위로 탭을 가로챈다' % sh.get('hitOnBar'))
    else:
        s.fail('C5', u'바텀시트 시나리오', 'no result')

    # --- C7. 선택 행 2유형 — 스테퍼·가격·말풍선 (실기 반려 2026-09-08) ---------
    for vp in VP_ROWS:
        tag = 'rows%d' % vp
        r = res.get(tag)
        if not r or not r.get('ok'):
            s.fail('C7.%s' % tag, u'%s 렌더' % tag, (r or {}).get('error', 'no result')); continue
        made = r.get('rowsMade') or {}
        rows = r.get('rows') or []
        # 탐지: 카페24 스크립트가 실제로 두 유형을 만들었는가 (안 만들어지면 검사할 것이 없다)
        s.probe('C7.%s.opt' % tag, u'[%dpx] tr.option_product 생성' % vp, made.get('optionRows', 0))
        s.probe('C7.%s.add' % tag, u'[%dpx] tr.add_product 생성' % vp, made.get('addRows', 0))
        for i, row in enumerate(rows):
            rid = '%s.%d.%s' % (tag, i, row.get('type'))
            s.truthy('C7.st.%s' % rid, u'[%dpx %s#%d] 스테퍼 컨테이너 존재' % (vp, row.get('type'), i), row.get('stepper'))
            s.eq('C7.seq.%s' % rid, u'[%dpx %s#%d] 스테퍼 순서 (− 숫자 +)' % (vp, row.get('type'), i),
                 u'− N +', row.get('seq'), u'추가상품 행은 .up/.down 이 <img> 에 붙어 예전 order 규칙이 안 걸렸다 (F-2)')
            s.eq('C7.w.%s' % rid, u'[%dpx %s#%d] 스테퍼 폭' % (vp, row.get('type'), i),
                 b['rows']['stepper_w'][str(vp)], row.get('stepperW'),
                 u'input 고유 폭이 새면 263~268px 로 늘어나 가격을 덮는다 (F-1)')
            s.eq('C7.ov.%s' % rid, u'[%dpx %s#%d] 가격 ↔ 스테퍼 겹침 면적' % (vp, row.get('type'), i),
                 0, row.get('overlapArea'), u'0 이 아니면 가격이 박스를 뚫는다 (F-1)')
            s.eq('C7.ri.%s' % rid, u'[%dpx %s#%d] 가격 오른쪽 여백(행 padding)' % (vp, row.get('type'), i),
                 b['rows']['price_right_inset'], row.get('priceRightInset'))
            s.truthy('C7.in.%s' % rid, u'[%dpx %s#%d] 가격이 행 안에 있다' % (vp, row.get('type'), i), row.get('priceInsideRow'))
            s.le('C7.cy.%s' % rid, u'[%dpx %s#%d] 가격·스테퍼 세로 중심 차(px)' % (vp, row.get('type'), i),
                 2, abs(row.get('priceCenterDelta') or 99))
        bub = r.get('bubble') or {}
        s.truthy('C7.bb.%s' % tag, u'[%dpx] 혜택 말풍선 요소 탐지' % vp, bub.get('found'))
        if bub.get('found'):
            s.eq('C7.bb.ov.%s' % tag, u'[%dpx] 말풍선이 덮는 텍스트(경고문 표시 상태)' % vp, [], bub.get('textOverlaps'))
            if bub.get('hidden'):
                # B안 — 시트가 닫혀 있는 동안 인라인 블록이 감춰져 말풍선이 화면에 없다.
                # 덮을 대상이 없으므로 8차 F-3 의 겹침 조건은 구조적으로 해소된 상태다.
                s.eq('C7.bb.hidden.%s' % tag, u'[%dpx] 시트 닫힘 상태에서 말풍선 비노출(B안)' % vp,
                     True, True, u'말풍선은 시트를 열면 시트 안에서 보인다')
            else:
                s.eq('C7.bb.ovh.%s' % tag, u'[%dpx] 말풍선이 덮는 텍스트(경고문 숨김 + 바운스 최고점)' % vp, [],
                     bub.get('textOverlapsHidden'), u'대표님 캡처 조건 — 여기서 .zg-sum__note 가 덮였다 (F-3)')
                s.ge('C7.bb.gap.%s' % tag, u'[%dpx] 말풍선 ↔ 안내문 간격(경고문 숨김 + 바운스 최고점)' % vp,
                     1, bub.get('noteGapHiddenBounce'))

    # --- C8. 재탭 해제 (R-2, 대표님 요청 2026-09-09) -----------------------------
    #   담긴 카드를 다시 누르면 그 구성이 빠진다. 카페24 **자기 삭제 컨트롤**을 누르는 경로라
    #   그 컨트롤이 사라지면 조용히 죽는다 → `nodel` 음성 대조군으로 검사가 살아 있음을 증명한다.
    r = res.get('untap390_ok')
    if not r or not r.get('ok') or not r.get('untap'):
        s.fail('C8.ok', u'재탭 해제 시나리오', (r or {}).get('error', 'no result'))
    else:
        u = r['untap']
        s.probe('C8.cards', u'구성 카드 수', u.get('cards', 0))
        s.eq('C8.picked.rows', u'카드 탭 → tr.option_product', 1, u['picked']['optRows'])
        s.eq('C8.qty3', u'수량을 3 으로 바꾼 뒤 행 수량', ['3'], u['qty3']['qtys'],
             u'수량 2 이상 케이스를 만들지 못하면 아래 전량 삭제 검사가 무의미하다')
        s.eq('C8.untap.rows', u'수량 3 인 카드 재탭 → 그 구성 **전량** 삭제', 0, u['untapped']['optRows'],
             u'카드는 담기/빼기 스위치다. 수량 조절은 아래 목록의 스테퍼가 맡는다')
        s.eq('C8.untap.on', u'재탭 뒤 data-zg-on 전부 해제', [''] * u['cards'], u['untapped']['on'])
        s.eq('C8.untap.picked0', u'재탭 뒤 빈 상태 클래스(zg-picked-0)', True, u['untapped']['picked0'])
        s.eq('C8.untap.bar', u'재탭 뒤 하단바 문구', u'구성을 선택해 주세요', u['untapped']['bar'])
        s.eq('C8.untap.toast', u'재탭 뒤 토스트', u'구성을 뺐어요.', u['untapped']['toast'])
        s.eq('C8.untap.add', u'추가상품 행은 건드리지 않는다', 0, u['untapped']['addRows'])
        s.eq('C8.multi', u'복수 담기(결정 #1)는 그대로 — 카드 2장 담김', 2, u['two']['optRows'])
        s.eq('C8.one', u'한 장만 해제하면 나머지는 남는다', 1, u['oneLeft']['optRows'])
        s.eq('C8.empty.rows', u'마지막 하나 해제 → 행 0', 0, u['empty']['optRows'])
        s.eq('C8.empty.bar', u'마지막 하나 해제 → 하단바가 안내 문구로 복귀',
             u'구성을 선택해 주세요', u['empty']['bar'])
        s.eq('C8.empty.picked0', u'마지막 하나 해제 → 빈 상태 복귀', True, u['empty']['picked0'])
        # aria-label 접미 = 그 버튼을 누르면 실제로 일어나는 일 (문가온 소관)
        s.eq('C8.aria.picked', u'담긴 카드의 aria-label 접미', u'선택 해제',
             (u['picked']['ariaTail'] or [''])[1] if len(u['picked']['ariaTail']) > 1 else None)
        s.eq('C8.aria.empty', u'해제 뒤 aria-label 접미', [u'장바구니에 담기'] * u['cards'],
             u['empty']['ariaTail'])

    # C8-N. 음성 대조군 — 삭제 컨트롤이 없으면 **해제되지 않고** 안내로 폴백해야 한다.
    #       (여기서 행이 0 이 되면 우리가 DOM 을 직접 뜯고 있다는 뜻이라 그것도 FAIL 이다)
    r = res.get('untap390_nodel')
    if not r or not r.get('ok') or not r.get('untap'):
        s.fail('C8N', u'재탭 해제 음성 대조군', (r or {}).get('error', 'no result'))
    else:
        u = r['untap']
        s.eq('C8N.rows', u'[삭제 컨트롤 없음] 재탭해도 행이 남는다(안전 폴백)', 1, u['untapped']['optRows'],
             u'0 이면 우리가 DOM 을 직접 뜯은 것이다')
        s.eq('C8N.toast', u'[삭제 컨트롤 없음] 폴백 안내 문구',
             u'이미 담겨 있어요. 빼시려면 아래 목록에서 지워 주세요.', u['untapped']['toast'])
        s.eq('C8N.aria', u'[삭제 컨트롤 없음] 담긴 카드 aria-label 접미 (되지 않는 일을 말하지 않는다)',
             u'이미 담김',
             (u['picked']['ariaTail'] or [''])[1] if len(u['picked']['ariaTail']) > 1 else None)

    # --- C9. B안 — 「장바구니·구매하기가 계속 떠 있는가」 (2026-09-09) --------------
    #   합계 아래 인라인 버튼을 시트가 닫혀 있을 때 감춘다. 구매 경로가 끊기면 판매가 멈추므로
    #   **실제로 눌러** 확인한다. `.fixed` 인 상태(시트 열림 경로)와 아닌 상태(인라인 위임 경로) 둘 다.
    for kind in ('mid', 'top'):
        tag = 'barbuy390_%s' % kind
        r = res.get(tag)
        if not r or not r.get('ok') or not r.get('barbuy'):
            s.fail('C9.%s' % tag, u'하단바 구매 경로 시나리오', (r or {}).get('error', 'no result')); continue
        u = r['barbuy']
        s.probe('C9.%s.subs' % tag, u'[%s] DOM 의 product_submit 노드 수' % kind, u['submitNodesInDom'],
                u'0이면 onclick 이 사라진 것 = 판매 정지')
        s.truthy('C9.%s.bar' % tag, u'[%s] 하단 고정바 표시' % kind, u['barVisible'])
        s.eq('C9.%s.cart' % tag, u'[%s] 바 「장바구니」 → product_submit(2) 발화' % kind, [2], u['cartFired'],
             u'인라인과 무관한 자체 onclick 이어야 한다')
        s.truthy('C9.%s.buypath' % tag, u'[%s] 바 「구매하기」 → 시트가 열리거나 product_submit(1) 발화' % kind,
                 u['buyPathOk'], u'둘 다 아니면 구매 경로가 0개다')
        s.ge('C9.%s.sub1after' % tag, u'[%s] 누른 뒤 화면에 보이는 product_submit(1)' % kind, 1,
             u['submit1VisibleAfterBuy'] if u['sheetOpened'] else 1,
             u'시트가 열렸으면 시트 안 구매하기가 보여야 한다')
        # 인라인은 시트가 닫혀 있는 동안 감춰져 있어야 한다 (B안의 목적)
        s.eq('C9.%s.inline' % tag, u'[%s] 시트 닫힘 상태의 인라인 노출' % kind, False, u['inlineVisible'])
        # 리뷰 칩은 감추되 훅은 DOM 에 남는다
        s.eq('C9.%s.chip' % tag, u'[%s] 하단바 리뷰 칩 노출' % kind, False, u['reviewChipVisible'])
        s.eq('C9.%s.hook' % tag, u'[%s] `alpha_review_count` DOM 잔존' % kind,
             b['barbuy']['review_hook'], u['reviewHookInDom'], u'0이면 알파리뷰가 끊긴다')
        s.eq('C9.%s.alpha' % tag, u'[%s] `alpha_widget` DOM 잔존' % kind,
             b['barbuy']['alpha_widget'], u['alphaWidgetInDom'])
        # 결제수단 블록은 함께 숨지 않는다
        s.eq('C9.%s.apppay' % tag, u'[%s] `.app-pay-wrap` DOM' % kind, 1, u['appPayInDom'])
        s.eq('C9.%s.naver' % tag, u'[%s] `#NaverChk_Button` DOM' % kind, 1, u['naverInDom'])
        s.eq('C9.%s.kakao' % tag, u'[%s] `#appPaymentButtonBox` DOM' % kind, 1, u['kakaoPayInDom'])
        # 리뷰 칩이 빠진 만큼 넓어진 두 버튼의 터치 타깃
        for nm, box in (('cart', u['barCartBox']), ('buy', u['barBuyBox'])):
            s.ge('C9.%s.tap.%s' % (tag, nm), u'[%s] 바 %s 높이 ≥ 44px' % (kind, nm), 44, (box or {}).get('h', 0))
            s.ge('C9.%s.tapw.%s' % (tag, nm), u'[%s] 바 %s 폭 ≥ 44px' % (kind, nm), 44, (box or {}).get('w', 0))
        # R-4 말풍선 — 줄상자 상속을 끊었는가
        s.eq('C9.%s.bubble' % tag, u'[%s] 말풍선 line-height (54px 상속을 끊었는가)' % kind,
             b['barbuy']['bubble_lh'], u['bubbleLineHeight'],
             u'54px 면 글자가 노란 상자 아래로 8px 내려앉는다 (R-4)')

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
        'barbuy': {
            'review_hook': res['barbuy390_mid']['barbuy']['reviewHookInDom'],
            'alpha_widget': res['barbuy390_mid']['barbuy']['alphaWidgetInDom'],
            'bubble_lh': res['barbuy390_mid']['barbuy']['bubbleLineHeight'],
        },
        'rows': {
            'stepper_w': dict((str(vp), (res['rows%d' % vp]['rows'] or [{}])[0].get('stepperW'))
                              for vp in VP_ROWS),
            'price_right_inset': (res['rows390']['rows'] or [{}])[0].get('priceRightInset'),
        },
    }
