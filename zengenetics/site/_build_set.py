# -*- coding: utf-8 -*-
"""젠제네틱스 세트 상품페이지 빌더 (칼마비 / 붓기 부스터 / 퍼포먼스 부스터 공용)

규칙 (CLAUDE.md 영구규칙):
  - 가격·할인율을 지어내지 않는다. cafe24 등록값 그대로 넣고 변수 주석을 단다 (규칙 11)
  - 평점·리뷰 수를 쓰지 않는다. 알파리뷰 훅 자리만 둔다 (규칙 13)
  - 상세 이미지는 대표님 작업물을 공홈 게시 순서 그대로 (assets/detail/<slug>/)
"""
import io, json, os, base64
from PIL import Image
Image.MAX_IMAGE_PIXELS = None

ROOT = '/home/user/wespotjh/zengenetics/'
SC   = '/tmp/claude-0/-home-user-zengenetics-meta-ads/e69fe25c-69a9-5d8c-8bc1-a1caba101472/scratchpad/'
KMB  = SC + 'kmb/'

css0 = io.open(KMB+'style0.css', encoding='utf-8').read()
cssP = io.open(KMB+'style.css',  encoding='utf-8').read()
stk  = json.load(open(KMB+'stk.json'))

def enc(path, w=860, q=80):
    im = Image.open(path)
    if im.width > w:
        im = im.resize((w, int(im.height*w/im.width)), Image.LANCZOS)
    b = io.BytesIO(); im.convert('RGB').save(b, 'WEBP', quality=q, method=6)
    return 'data:image/webp;base64,' + base64.b64encode(b.getvalue()).decode()

# ── 공통 CSS ────────────────────────────────────────────────────────────
EXTRA = """
  :root{ --k:#D9641F; --mg:#6D4FC9; --b:#D9285A; }
  /* 세트 히어로는 대표님이 만드신 배너라 꽉 채워 보여준다 */
  .gal .sl{height:auto;padding:0}
  .gal .sl img{max-width:100%;width:100%;max-height:none;filter:none;display:block}
  .gal .dots{bottom:10px}

  /* ── 하루 루틴 ─────────────────────────────────────── */
  .rt{padding-block:34px;border-top:1px solid var(--hair);background:var(--bg-2)}
  .rt .lab{display:block;text-align:center;margin-bottom:9px}
  .rt h2{font-size:clamp(20px,5.4vw,24px);font-weight:700;letter-spacing:-.025em;
         text-align:center;margin:0 0 8px;line-height:1.35;word-break:keep-all}
  .rt .dek{text-align:center;font-size:13.5px;color:var(--ink-2);margin:0 0 26px;word-break:keep-all}
  .tl{position:relative;display:grid;gap:11px}
  .tl::before{content:"";position:absolute;left:23px;top:16px;bottom:16px;width:1px;
              background:var(--tlline);opacity:.35}
  .st{position:relative;display:grid;grid-template-columns:47px 1fr;gap:13px;align-items:start;
      background:#fff;border:1px solid var(--hair);border-radius:15px;padding:15px 16px 15px 13px}
  .st .pin{width:47px;display:flex;flex-direction:column;align-items:center;gap:7px}
  .st .dot{width:11px;height:11px;border-radius:50%;border:3px solid #fff;
           box-shadow:0 0 0 1.5px currentColor;margin-top:5px}
  .st .pouch{width:34px;height:88px;object-fit:contain;
             filter:drop-shadow(0 5px 8px rgba(30,22,12,.16))}
  .st .when{display:flex;align-items:center;gap:7px;margin-bottom:5px;flex-wrap:wrap}
  .st .clock{font-family:var(--f-m);font-size:10.5px;letter-spacing:.13em;text-transform:uppercase;
             color:currentColor;font-weight:500}
  .st .chip{font-size:11px;font-weight:700;letter-spacing:-.01em;color:#fff;
            border-radius:999px;padding:3px 9px}
  .st.k .chip{background:var(--k)} .st.mg .chip{background:var(--mg)} .st.b .chip{background:var(--b)}
  .st h3{font-size:16.5px;font-weight:700;letter-spacing:-.02em;margin:0 0 5px;color:var(--ink)}
  .st p{margin:0;font-size:13.5px;color:var(--ink-2);line-height:1.72;word-break:keep-all}
  .st .meta{margin-top:9px;display:flex;flex-wrap:wrap;gap:5px}
  .st .meta span{font-size:11px;color:var(--ink-2);background:var(--bg-2);
                 border:1px solid var(--hair);border-radius:999px;padding:4px 9px}
  .st.k{color:var(--k)} .st.mg{color:var(--mg)} .st.b{color:var(--b)}

  /* 칼륨 A/B 타입 */
  .type{margin-top:11px;border:1px solid var(--hair);border-radius:15px;background:#fff;padding:15px 16px}
  .type .tt{font-size:13px;font-weight:700;letter-spacing:-.015em;margin:0 0 3px}
  .type .td{font-size:12.5px;color:var(--ink-2);margin:0 0 12px;word-break:keep-all}
  .tabs{display:grid;grid-template-columns:1fr 1fr;gap:7px;margin-bottom:13px}
  .tabs button{appearance:none;border:1px solid var(--hair-2);background:#fff;color:var(--ink-2);
        font-family:var(--f-b);font-size:12.5px;font-weight:600;letter-spacing:-.01em;
        border-radius:10px;padding:11px 8px;min-height:44px;cursor:pointer;line-height:1.4;
        transition:border-color .16s,color .16s,background .16s}
  .tabs button[aria-selected="true"]{border-color:var(--k);color:var(--k);background:#FDF4EE}
  .slots{display:flex;align-items:center;gap:8px}
  .slots .sl2{flex:1;border:1px dashed var(--hair-2);border-radius:11px;padding:11px 10px;text-align:center}
  .slots .sl2 i{display:block;font-style:normal;font-family:var(--f-m);font-size:10px;
                letter-spacing:.1em;color:var(--ink-3);margin-bottom:4px}
  .slots .sl2 b{font-size:13.5px;font-weight:700;letter-spacing:-.015em;color:var(--k)}
  .slots .plus{font-family:var(--f-d);font-size:15px;color:var(--hair-2)}
  .rt .foot{margin-top:14px;font-size:12px;color:var(--ink-3);text-align:center;
            line-height:1.75;word-break:keep-all}

  /* 세트 구성 카드 */
  .kit{display:grid;gap:8px;margin-top:16px}
  .kit.n2{grid-template-columns:repeat(2,1fr)} .kit.n3{grid-template-columns:repeat(3,1fr)}
  .kit .c{border:1px solid var(--hair);border-radius:13px;background:#fff;padding:13px 10px;text-align:center}
  .kit .c img{width:26px;height:72px;object-fit:contain;margin-bottom:8px}
  .kit .c em{display:block;font-style:normal;font-size:12.5px;font-weight:700;letter-spacing:-.015em}
  .kit .c s{display:block;font-family:var(--f-b);font-size:11px;color:var(--ink-3);
            text-decoration:none;margin-top:3px}
  .rate a{color:var(--ink-2);text-decoration:none;border-bottom:1px solid var(--hair-2)}

  /* 카페24 옵션 선택 (상품에 옵션이 걸린 경우만) */
  .opt24{padding-block:30px;border-top:1px solid var(--hair)}
  .opt24 h2{font-size:16px;font-weight:700;letter-spacing:-.015em;margin:0 0 4px}
  .opt24 .hint{font-size:13px;color:var(--ink-2);margin:0 0 16px;word-break:keep-all}
  .opt24 .list{display:grid;gap:9px}
  .opt24 .o{display:grid;grid-template-columns:20px 1fr auto;gap:12px;align-items:center;
            border:1px solid var(--hair-2);border-radius:13px;padding:14px 15px;background:#fff;
            cursor:pointer;transition:border-color .16s,box-shadow .16s}
  .opt24 .o[aria-checked="true"]{border-color:var(--ink);box-shadow:0 0 0 1px var(--ink) inset}
  .opt24 .tick{width:20px;height:20px;border-radius:50%;border:1.5px solid var(--hair-2);
               display:grid;place-items:center}
  .opt24 .o[aria-checked="true"] .tick{border-color:var(--ink);background:var(--ink)}
  .opt24 .tick i{width:7px;height:7px;border-radius:50%;background:#fff;display:none}
  .opt24 .o[aria-checked="true"] .tick i{display:block}
  .opt24 .nm{font-weight:600;font-size:14.5px;letter-spacing:-.015em;word-break:keep-all;line-height:1.5}
  .opt24 .nm em{display:block;font-style:normal;font-size:12px;color:var(--ink-2);margin-top:3px}
  .opt24 .pz{text-align:right;font-family:var(--f-d);font-weight:700;font-size:15px;
             font-variant-numeric:tabular-nums;white-space:nowrap}
  .opt24 .flag{font-size:10.5px;font-weight:700;color:#fff;background:var(--acc-deep);
               border-radius:999px;padding:2px 8px;margin-right:6px;vertical-align:1px}
"""

# ── 설정 ────────────────────────────────────────────────────────────────
# 값 출처: zengenetics.co.kr 상품 실등록값 (2026-09-06 수집)
CFG = {
 'kmb': dict(
   slug='set-kmb', out='product-set-kmb.html',
   doctitle='젠제네틱스 칼마비 세트 상품페이지', gnb='칼마비 건강 루틴',
   brand='Potassium &middot; Magnesium &middot; Vitamin B', h1='칼마비 건강 루틴',
   sub='칼륨 20포 &middot; 마그네슘 20포 &middot; 비타민B 20포 &mdash; 세 박스 한 상자',
   prd_no=98, price=107500, was=143000, off='25%',
   accent=('#3757C4','#E4E9F8','#1A2B6B'), tlline='linear-gradient(to bottom,var(--b),var(--k) 46%,var(--mg))',
   badges=['세 가지를 한 번에','배송비 무료','Kolmar BNH 생산','HACCP','스틱 분말'],
   kit=[('potassium','칼륨','2.5g &times; 20포<br>라임'),
        ('magnesium','마그네슘','2g &times; 20포<br>포도향'),
        ('vitaminb','비타민B','2g &times; 20포<br>사과향')],
   rt_h2='세 가지를 하루 어디에 넣으시나요',
   rt_dek='따로 챙기실 것 없습니다. 아침에 하나, 낮에 둘, 자기 전에 하나입니다.',
   steps=[
     dict(cls='b', pouch='vitaminb', clock='Morning', chip='하루 1포', h='아침 &mdash; 비타민B 컴플렉스',
          p='하루의 시동을 거는 자리입니다. 물 없이 뜯어서 그대로 드셔도 되고, 아침 물 한 잔에 타셔도 됩니다.',
          meta=['B1 &middot; B2 &middot; B6 &middot; B12','사과향','건강기능식품']),
     dict(cls='k', pouch='potassium', clock='Day &amp; Evening', chip='하루 2포', h='낮과 저녁 &mdash; 칼륨',
          p='짜게 드신 날에 챙기는 자리입니다. 한 포에 262.5mg, 두 포로 하루 525mg을 채웁니다. 아래에서 두 가지 타입 중 편한 쪽을 고르시면 됩니다.',
          meta=['525mg / 하루','라임','당류가공품'], type_after=True),
     dict(cls='mg', pouch='magnesium', clock='Night', chip='하루 1포', h='밤 &mdash; 마그네슘',
          p='하루를 마무리하는 자리입니다. 한 포에 400mg, 한 포면 그날 몫을 다 채웁니다.',
          meta=['400mg / 한 포','포도향','건강기능식품']),
   ],
   rt_foot='칼륨은 하루 두 포 기준이라 20포가 열흘분,<br>마그네슘과 비타민B는 하루 한 포라 각각 스무날분입니다.',
   qty_hint='세트는 한 상자에 세 박스가 들어 있습니다. 금액이 5만원을 넘어 배송비는 없습니다.',
   detail_h2='칼마비 세트 상세 안내',
   how='비타민B <b>하루 한 포</b>, 칼륨 <b>하루 두 포</b>, 마그네슘 <b>하루 한 포</b>가 기준입니다.<br>셋 다 뜯어서 그대로 드셔도 되고, 물 한 잔에 타서 드셔도 됩니다.',
   compose='젠제네틱스 포타슘 칼륨 525mg 다이렉트 &middot; 2.5g &times; 20포(50g) &middot; 라임<br>'
           '젠제네틱스 마그네슘 400mg &middot; 2g &times; 20포 &middot; 포도향<br>'
           '젠제네틱스 비타민B 컴플렉스 &middot; 2g &times; 20포 &middot; 사과향<br>'
           '낱개로 사시면 45,000원 + 49,000원 + 49,000원 = 143,000원입니다.',
   note2='*칼륨은 당류가공품이며 건강기능식품이 아닙니다. 마그네슘과 비타민B 컴플렉스는 건강기능식품입니다',
   cartname='칼마비 세트',
   adds=[('kd','칼륨 데이팩','2.5g × 6포 · 맛보기',14000,'potassium'),
         ('md','마그네슘 데이팩','2g × 6포 · 맛보기',15000,'magnesium'),
         ('bd','비타민B 데이팩','2g × 6포 · 맛보기',15000,'vitaminb')],
 ),

 'swell': dict(
   slug='set-swell', out='product-set-swell.html',
   doctitle='젠제네틱스 붓기 부스터 세트 상품페이지', gnb='붓기 부스터',
   brand='Potassium &times; Vitamin B', h1='붓기 부스터',
   sub='칼륨 2박스 40포 &middot; 비타민B 1박스 20포 &mdash; 스무날 루틴',
   prd_no=63, price=104000, was=139000, off='25%',
   accent=('#E0492F','#FBE4DE','#A32A15'), tlline='linear-gradient(to bottom,var(--b),var(--k))',
   badges=['설인아 PICK','칼륨 2박스 구성','배송비 무료','Kolmar BNH 생산','HACCP'],
   kit=[('potassium','칼륨 &times;2','2.5g &times; 20포 &times; 2<br>라임'),
        ('vitaminb','비타민B','2g &times; 20포<br>사과향')],
   rt_h2='나트륨은 내보내고, 수분은 돌리고',
   rt_dek='칼륨 하나만 챙기는 것보다 한 걸음 더 갑니다. 아침에 하나, 낮과 저녁에 둘입니다.',
   steps=[
     dict(cls='b', pouch='vitaminb', clock='Morning', chip='하루 1포', h='아침 &mdash; 비타민B 컴플렉스',
          p='체내 수분 순환을 돕는 자리입니다. 나트륨을 내보내는 칼륨과 함께 가면 붓기 관리가 한 방향으로 모입니다.',
          meta=['B1 &middot; B2 &middot; B6 &middot; B12','사과향','건강기능식품']),
     dict(cls='k', pouch='potassium', clock='Day &amp; Evening', chip='하루 2포', h='낮과 저녁 &mdash; 칼륨',
          p='짠 식습관으로 과해진 나트륨을 내보내는 자리입니다. 한 포에 262.5mg, 두 포로 하루 525mg을 채웁니다.',
          meta=['525mg / 하루','라임','당류가공품'], type_after=True),
   ],
   rt_foot='칼륨은 하루 두 포라 40포가 스무날분,<br>비타민B는 하루 한 포라 20포가 스무날분 &mdash; 둘이 같이 끝납니다.',
   qty_hint='칼륨 2박스와 비타민B 1박스가 한 상자입니다. 금액이 5만원을 넘어 배송비는 없습니다.',
   detail_h2='붓기 부스터 상세 안내',
   how='비타민B <b>하루 한 포</b>, 칼륨 <b>하루 두 포</b>가 기준입니다.<br>둘 다 뜯어서 그대로 드셔도 되고, 물 한 잔에 타서 드셔도 됩니다.',
   compose='젠제네틱스 포타슘 칼륨 525mg 다이렉트 &middot; 2.5g &times; 20포(50g) &middot; 라임 &mdash; <b>2박스</b><br>'
           '젠제네틱스 비타민B 컴플렉스 &middot; 2g &times; 20포 &middot; 사과향 &mdash; 1박스<br>'
           '낱개로 사시면 45,000원 &times; 2 + 49,000원 = 139,000원입니다.',
   note2='*칼륨은 당류가공품이며 건강기능식품이 아닙니다. 비타민B 컴플렉스는 건강기능식품입니다',
   cartname='붓기 부스터',
   adds=[('mg','젠제네틱스 마그네슘','2g × 20포 · 포도향',37900,'magnesium'),
         ('kd','칼륨 데이팩','2.5g × 6포 · 맛보기',14000,'potassium'),
         ('bd','비타민B 데이팩','2g × 6포 · 맛보기',15000,'vitaminb')],
 ),

 'perf': dict(
   slug='set-performance', out='product-set-performance.html',
   doctitle='젠제네틱스 퍼포먼스 부스터 세트 상품페이지', gnb='퍼포먼스 부스터',
   brand='Vitamin B &times; Magnesium', h1='퍼포먼스 부스터',
   sub='비타민B 20포 &middot; 마그네슘 20포 &mdash; 운동 스무 번 루틴',
   prd_no=64, price=71900, was=98000, off='27%',
   accent=('#7B3FD4','#EEE6FB','#4A1E8C'), tlline='linear-gradient(to bottom,var(--b),var(--mg))',
   badges=['러너 &middot; 하이록스','운동 전후 한 세트','배송비 무료','Kolmar BNH 생산','건강기능식품'],
   kit=[('vitaminb','비타민B','2g &times; 20포<br>사과향'),
        ('magnesium','마그네슘','2g &times; 20포<br>포도향')],
   rt_h2='운동 전에 하나, 운동 끝나고 하나',
   rt_dek='러닝이든 하이록스든 순서는 같습니다. 나가기 전에 비타민B, 씻기 전에 마그네슘.',
   steps=[
     dict(cls='b', pouch='vitaminb', clock='Before', chip='운동 전 1포', h='운동 전 &mdash; 비타민B 컴플렉스',
          p='출발선에 서기 전 채우는 자리입니다. 물 없이 뜯어서 그대로 드셔도 되니 가방에 한 포만 넣어 두시면 됩니다.',
          meta=['B1 &middot; B2 &middot; B6 &middot; B12','사과향','건강기능식품']),
     dict(cls='mg', pouch='magnesium', clock='After', chip='운동 후 1포', h='운동 후 &mdash; 마그네슘',
          p='다 뛰고 나서 채우는 자리입니다. 한 포에 400mg, 한 포면 그날 몫을 다 채웁니다.',
          meta=['400mg / 한 포','포도향','건강기능식품']),
   ],
   rt_foot='둘 다 20포씩이라 <b>운동 스무 번</b>이 한 세트입니다.<br>주 3회 뛰시면 한 달 반, 주 5회면 한 달 치입니다.',
   qty_hint='비타민B 1박스와 마그네슘 1박스가 한 상자입니다. 금액이 5만원을 넘어 배송비는 없습니다.',
   detail_h2='퍼포먼스 부스터 상세 안내',
   how='비타민B는 <b>운동 전 한 포</b>, 마그네슘은 <b>운동 후 한 포</b>가 기준입니다.<br>'
       '운동을 쉬는 날에는 비타민B를 아침에, 마그네슘을 자기 전에 드셔도 됩니다.<br>둘 다 뜯어서 그대로 드셔도 되고, 물 한 잔에 타서 드셔도 됩니다.',
   compose='젠제네틱스 비타민B 컴플렉스 &middot; 2g &times; 20포 &middot; 사과향<br>'
           '젠제네틱스 마그네슘 400mg &middot; 2g &times; 20포 &middot; 포도향<br>'
           '낱개로 사시면 49,000원 + 49,000원 = 98,000원입니다.',
   note2='*마그네슘과 비타민B 컴플렉스는 모두 건강기능식품입니다',
   cartname='퍼포먼스 부스터',
   adds=[('k','젠제네틱스 칼륨','2.5g × 20포 · 라임',34900,'potassium'),
         ('md','마그네슘 데이팩','2g × 6포 · 맛보기',15000,'magnesium'),
         ('bd','비타민B 데이팩','2g × 6포 · 맛보기',15000,'vitaminb')],
 ),

 # ── 데이팩 3종 · 생애 첫 구매 EVENT (2026-09-06 추가) ──────────────
 'dp_k': dict(
   slug='daypack-potassium', out='product-daypack-potassium.html',
   doctitle='젠제네틱스 칼륨 데이팩 상품페이지', gnb='칼륨 데이팩',
   brand='Potassium 525mg · Day pack', h1='칼륨 데이팩',
   sub='2.5g × 6포 — 하루 두 포로 사흘, 가볍게 시작하는 구성',
   prd_no=60, price=14000, was=None, off='',
   accent=('#D9641F','#F6E3D5','#8F3608'), tlline='var(--k)',
   badges=['6포 구성','하루 두 포','물 없이 3초','HACCP','당류가공품'],
   kit=[('potassium','칼륨 데이팩','2.5g &times; 6포<br>라임')],
   rt_h2='사흘, 이렇게 써 보세요',
   rt_dek='한 포에 262.5mg입니다. 하루 두 포 기준이라 6포는 사흘치입니다.',
   steps=[
     dict(cls='k', pouch='potassium', clock='Day &amp; Evening', chip='하루 2포', h='낮과 저녁 &mdash; 칼륨',
          p='짜게 드신 날에 챙기는 자리입니다. 두 포로 하루 525mg을 채웁니다. 아래 두 타입 중 편한 쪽을 고르시면 됩니다.',
          meta=['525mg / 하루','라임','당류가공품'], type_after=True),
   ],
   rt_foot='사흘 써 보시고 맞으면 20포 한 상자로 넘어가시면 됩니다.',
   qty_hint='한 상자에 6포가 들어 있습니다. 5만원 미만이면 배송비 3,500원이 붙습니다.',
   detail_h2='칼륨 데이팩 상세 안내',
   how='하루 <b>두 포</b>가 기준입니다.<br>뜯어서 그대로 드셔도 되고, 물 한 잔에 타서 드셔도 됩니다.',
   compose='젠제네틱스 포타슘 칼륨 525mg 다이렉트 데이팩 &middot; 2.5g &times; <b>6포</b> &middot; 라임<br>'
           '칼륨 262.5mg(1포당) &middot; 독일 Jungbunzlauer 구연산칼륨 &middot; HACCP &middot; 콜마비앤에이치 생산<br>'
           '20포 정품은 45,000원 &rarr; 34,900원입니다.',
   note2='*칼륨은 당류가공품이며 건강기능식품이 아닙니다',
   cartname='칼륨 데이팩',
   adds=[('md','마그네슘 데이팩','2g × 6포 · 맛보기',15000,'magnesium'),
         ('bd','비타민B 데이팩','2g × 6포 · 맛보기',15000,'vitaminb'),
         ('k','젠제네틱스 칼륨 20포','2.5g × 20포 · 라임',34900,'potassium')],
 ),

 'dp_m': dict(
   slug='daypack-magnesium', out='product-daypack-magnesium.html',
   doctitle='젠제네틱스 마그네슘 데이팩 상품페이지', gnb='마그네슘 데이팩',
   brand='Magnesium 400mg · Day pack', h1='마그네슘 데이팩',
   sub='2g × 6포 — 하루 한 포로 엿새, 운동 후와 잠들기 전에',
   prd_no=61, price=15000, was=None, off='',
   accent=('#7C21CE','#ECE0FA','#561FAA'), tlline='var(--mg)',
   badges=['6포 · 엿새치','하루 한 포 400mg','포도향','GMP','건강기능식품'],
   kit=[('magnesium','마그네슘 데이팩','2g &times; 6포<br>포도향')],
   rt_h2='엿새, 밤마다 한 포',
   rt_dek='한 포에 400mg입니다. 하루 한 포면 그날 몫이 끝나서 6포가 엿새치입니다.',
   steps=[
     dict(cls='mg', pouch='magnesium', clock='After &amp; Night', chip='하루 1포', h='운동 후, 또는 자기 전 &mdash; 마그네슘',
          p='다 뛰고 나서, 혹은 하루를 마무리하며 채우는 자리입니다. 한 포에 400mg이라 한 포면 그날 몫을 다 채웁니다.',
          meta=['400mg / 한 포','포도향','건강기능식품']),
   ],
   rt_foot='엿새 써 보시고 맞으면 20포 한 상자로 넘어가시면 됩니다.',
   qty_hint='한 상자에 6포가 들어 있습니다. 5만원 미만이면 배송비 3,500원이 붙습니다.',
   detail_h2='마그네슘 데이팩 상세 안내',
   how='하루 <b>한 포</b>가 기준입니다.<br>뜯어서 그대로 드셔도 되고, 물 한 잔에 타서 드셔도 됩니다.',
   compose='젠제네틱스 마그네슘 400mg 다이렉트 데이팩 &middot; 2g &times; <b>6포</b> &middot; 포도향<br>'
           '미국 AIC 원료 &middot; GMP &middot; 콜마비앤에이치 생산 &middot; 건강기능식품<br>'
           '20포 정품은 49,000원 &rarr; 37,900원입니다.',
   note2='*마그네슘은 건강기능식품이며, 질병의 예방 및 치료를 위한 의약품이 아닙니다',
   cartname='마그네슘 데이팩',
   adds=[('kd','칼륨 데이팩','2.5g × 6포 · 맛보기',14000,'potassium'),
         ('bd','비타민B 데이팩','2g × 6포 · 맛보기',15000,'vitaminb'),
         ('m','젠제네틱스 마그네슘 20포','2g × 20포 · 포도향',37900,'magnesium')],
 ),

 'dp_b': dict(
   slug='daypack-vitaminb', out='product-daypack-vitaminb.html',
   doctitle='젠제네틱스 비타민B 데이팩 상품페이지', gnb='비타민B 데이팩',
   brand='Vitamin B Complex · Day pack', h1='비타민B 데이팩',
   sub='2g × 6포 — 하루 한 포로 엿새, 아침마다 한 포',
   prd_no=62, price=15000, was=None, off='',
   accent=('#E11553','#FBDCE6','#A50A3C'), tlline='var(--b)',
   badges=['6포 · 엿새치','B1 · B2 · B6 · B12','사과향','GMP','건강기능식품'],
   kit=[('vitaminb','비타민B 데이팩','2g &times; 6포<br>사과향')],
   rt_h2='엿새, 아침마다 한 포',
   rt_dek='하루 한 포 기준이라 6포가 엿새치입니다. 가방에 넣어 두시면 됩니다.',
   steps=[
     dict(cls='b', pouch='vitaminb', clock='Morning', chip='하루 1포', h='아침 &mdash; 비타민B 컴플렉스',
          p='하루의 시동을 거는 자리입니다. 물 없이 뜯어서 그대로 드셔도 되고, 아침 물 한 잔에 타셔도 됩니다.',
          meta=['B1 &middot; B2 &middot; B6 &middot; B12','사과향','건강기능식품']),
   ],
   rt_foot='엿새 써 보시고 맞으면 20포 한 상자로 넘어가시면 됩니다.',
   qty_hint='한 상자에 6포가 들어 있습니다. 5만원 미만이면 배송비 3,500원이 붙습니다.',
   detail_h2='비타민B 데이팩 상세 안내',
   how='하루 <b>한 포</b>가 기준입니다.<br>뜯어서 그대로 드셔도 되고, 물 한 잔에 타서 드셔도 됩니다.',
   compose='젠제네틱스 비타민B 컴플렉스 다이렉트 데이팩 &middot; 2g &times; <b>6포</b> &middot; 사과향<br>'
           'B1 &middot; B2 &middot; B6 &middot; B12 네 가지 &middot; GMP &middot; 콜마비앤에이치 생산 &middot; 건강기능식품<br>'
           '20포 정품은 49,000원 &rarr; 37,900원입니다.',
   note2='*비타민B 컴플렉스는 건강기능식품이며, 질병의 예방 및 치료를 위한 의약품이 아닙니다',
   cartname='비타민B 데이팩',
   adds=[('kd','칼륨 데이팩','2.5g × 6포 · 맛보기',14000,'potassium'),
         ('md','마그네슘 데이팩','2g × 6포 · 맛보기',15000,'magnesium'),
         ('b','젠제네틱스 비타민B 20포','2g × 20포 · 사과향',37900,'vitaminb')],
 ),

 'first': dict(
   slug='first-buy', out='product-first-buy.html',
   doctitle='젠제네틱스 생애 첫 구매 EVENT 상품페이지', gnb='생애 첫 구매 EVENT',
   brand='First purchase only', h1='생애 첫 구매 특가',
   sub='데이팩으로 먼저 써 보시라고 만든 구성입니다 — 계정당 한 번',
   prd_no=71, price=8900, was=14000, off='36%',
   accent=('#3757C4','#E4E9F8','#1A2B6B'), tlline='linear-gradient(to bottom,var(--k),var(--mg) 50%,var(--b))',
   badges=['계정당 한 번','체험형 이벤트','쿠폰 사용 불가','재고 소진 시 종료','물 없이 3초'],
   kit=[('potassium','칼륨','2.5g &times; 6포<br>라임'),
        ('magnesium','마그네슘','2g &times; 6포<br>포도향'),
        ('vitaminb','비타민B','2g &times; 6포<br>사과향')],
   opt_h2='어느 것부터 써 보시겠어요?',
   opt_hint='아래 네 가지 중 하나를 고르시면 됩니다. 1+1은 같은 데이팩 두 상자입니다.',
   options=[
     dict(nm='붓기파우더(칼륨) 데이팩 2 box', mt='생애 첫 1+1 · 2.5g × 6포 × 2', add=5100, flag='BEST'),
     dict(nm='붓기파우더(칼륨) 데이팩 1 box', mt='지금 36% · 2.5g × 6포', add=0),
     dict(nm='마그네슘 데이팩 2 box', mt='생애 첫 1+1 · 2g × 6포 × 2', add=6100),
     dict(nm='비타민B 컴플렉스 데이팩 2 box', mt='생애 첫 1+1 · 2g × 6포 × 2', add=6100),
   ],
   rt_h2='세 가지가 각각 다른 시간에 들어갑니다',
   rt_dek='고르신 것이 하루의 어디에 들어가는지만 보시면 됩니다.',
   steps=[
     dict(cls='b', pouch='vitaminb', clock='Morning', chip='하루 1포', h='아침 &mdash; 비타민B 컴플렉스',
          p='하루의 시동을 거는 자리입니다. B1 · B2 · B6 · B12 네 가지가 한 포에 들어 있습니다.',
          meta=['사과향','건강기능식품']),
     dict(cls='k', pouch='potassium', clock='Day &amp; Evening', chip='하루 2포', h='낮과 저녁 &mdash; 칼륨',
          p='짜게 드신 날에 챙기는 자리입니다. 한 포에 262.5mg, 두 포로 하루 525mg을 채웁니다.',
          meta=['라임','당류가공품']),
     dict(cls='mg', pouch='magnesium', clock='Night', chip='하루 1포', h='자기 전 &mdash; 마그네슘',
          p='하루를 마무리하는 자리입니다. 한 포에 400mg, 한 포면 그날 몫을 다 채웁니다.',
          meta=['포도향','건강기능식품']),
   ],
   rt_foot='칼륨은 하루 두 포라 6포가 사흘치, 마그네슘과 비타민B는 하루 한 포라 6포가 엿새치입니다.',
   qty_hint='계정당 한 번만 구매하실 수 있는 상품입니다.', maxqty=1,
   detail_h2='생애 첫 구매 EVENT 상세 안내',
   how='비타민B는 아침 <b>한 포</b>, 칼륨은 낮·저녁 <b>두 포</b>, 마그네슘은 자기 전 <b>한 포</b>가 기준입니다.<br>'
       '셋 다 뜯어서 그대로 드셔도 되고, 물 한 잔에 타서 드셔도 됩니다.',
   compose='고르신 옵션의 데이팩이 배송됩니다. 각 데이팩은 <b>6포</b> 구성입니다.<br>'
           '칼륨 2.5g × 6포 · 라임 / 마그네슘 2g × 6포 · 포도향 / 비타민B 2g × 6포 · 사과향<br>'
           '<b>계정당 한 번</b>만 구매하실 수 있고, <b>쿠폰은 사용하실 수 없습니다.</b> 재고 소진 시 종료될 수 있습니다.',
   note2='*칼륨은 당류가공품이며 건강기능식품이 아닙니다. 마그네슘과 비타민B 컴플렉스는 건강기능식품입니다',
   cartname='생애 첫 구매 EVENT',
   adds=[],
 ),
}

TYPE_BLOCK = """
    <div class="type">
      <p class="tt">칼륨 두 포, 언제 나눠 드시겠어요?</p>
      <p class="td">상세페이지의 루틴 안내와 같은 기준입니다. 편한 쪽 하나만 고르시면 됩니다.</p>
      <div class="tabs" role="tablist">
        <button role="tab" id="tA" aria-selected="true">A. 아침에 얼굴이 붓는 편</button>
        <button role="tab" id="tB" aria-selected="false">B. 저녁에 종아리가 붓는 편</button>
      </div>
      <div class="slots">
        <div class="sl2"><i>FIRST</i><b id="s1">자기 전 1포</b></div>
        <span class="plus">+</span>
        <div class="sl2"><i>SECOND</i><b id="s2">기상 직후 1포</b></div>
      </div>
    </div>
"""

OPT_JS = """
  /* 옵션 선택 — 선택한 옵션의 추가금액이 합계에 더해진다 (cafe24 옵션 추가금과 같은 방식) */
  var oc = document.getElementById('opt24');
  if (oc) {
    Array.prototype.forEach.call(oc.children, function (n) {
      n.addEventListener('click', function () {
        Array.prototype.forEach.call(oc.children, function (m) { m.setAttribute('aria-checked', 'false'); });
        n.setAttribute('aria-checked', 'true');
        optAdd = Number(n.dataset.add || 0);
        calc();
      });
    });
  }
"""

TYPE_JS = """
  var TYPE={ A:['자기 전 1포','기상 직후 1포'], B:['출근 전 1포','오후 3시 1포'] };
  function setType(t){
    el('tA').setAttribute('aria-selected', t==='A'?'true':'false');
    el('tB').setAttribute('aria-selected', t==='B'?'true':'false');
    el('s1').textContent=TYPE[t][0]; el('s2').textContent=TYPE[t][1];
  }
  el('tA').addEventListener('click',function(){setType('A')});
  el('tB').addEventListener('click',function(){setType('B')});
  setType('A');
"""

def build(key):
    c = CFG[key]
    slug = c['slug']
    ddir = ROOT + 'assets/detail/' + slug
    n = len([f for f in os.listdir(ddir) if f.endswith('.webp')])
    det  = [enc(f'{ddir}/{i:02d}.webp') for i in range(1, n+1)]
    if key == 'kmb':
        hero = [enc(SC+'hero1.webp', 1000, 84), enc(SC+'hero2.webp', 1000, 84)]
    else:
        hero = [enc(SC+f'{slug}_hero1.webp', 1000, 84), enc(SC+f'{slug}_hero2.webp', 1000, 84)]
    if not c.get('adds'):
        pass

    css = cssP.replace('--acc:#D9641F; --acc-soft:#F6E3D5; --acc-deep:#8F3608;',
                       '--acc:%s; --acc-soft:%s; --acc-deep:%s;' % c['accent'])
    extra = EXTRA.replace('var(--tlline)', c['tlline'])

    kit = ''.join(
        '<div class="c"><img id="k%d" alt=""><em>%s</em><s>%s</s></div>' % (i+1, nm, mt)
        for i,(p,nm,mt) in enumerate(c['kit']))
    kit_js = ''.join("el('k%d').src=S.%s.v;" % (i+1, p) for i,(p,nm,mt) in enumerate(c['kit']))

    steps, step_js, has_type = '', '', False
    for i, s in enumerate(c['steps']):
        steps += """
    <div class="st %s">
      <div class="pin"><span class="dot"></span><img class="pouch" id="p%d" alt=""></div>
      <div>
        <div class="when"><span class="clock">%s</span><span class="chip">%s</span></div>
        <h3>%s</h3>
        <p>%s</p>
        <div class="meta">%s</div>
      </div>
    </div>
""" % (s['cls'], i+1, s['clock'], s['chip'], s['h'], s['p'],
       ''.join('<span>%s</span>' % m for m in s['meta']))
        step_js += "el('p%d').src=S.%s.v;" % (i+1, s['pouch'])
        if s.get('type_after'):
            steps += TYPE_BLOCK; has_type = True

    # 가격 행 — 정가=판매가(또는 정가 없음)면 정가·할인율 줄을 넣지 않는다.
    # cafe24 스킨도 같은 조건에서 product_custom_css 를 displaynone 처리한다.
    if c.get('was'):
        pricerow = ('<div class="prow"><span class="off">%s</span>'
                    '<span class="now">%s</span><span class="was">%s</span></div>'
                    % (c['off'], '{:,}원'.format(c['price']), '{:,}원'.format(c['was'])))
    else:
        pricerow = ('<!-- 정가(product_custom)와 판매가가 같아 정가 줄이 없다.'
                    ' cafe24 스킨도 이 경우 자동으로 정가 줄을 숨긴다 -->\n'
                    '  <div class="prow"><span class="now">%s</span></div>'
                    % '{:,}원'.format(c['price']))

    # 옵션 블록 — cafe24 상품에 옵션이 걸린 경우만
    if c.get('options'):
        rows = ''
        for i, o in enumerate(c['options']):
            flag = '<span class="flag">%s</span>' % o['flag'] if o.get('flag') else ''
            rows += ('      <div class="o" role="radio" data-i="%d" data-add="%d" aria-checked="%s">'
                     '<span class="tick"><i></i></span>'
                     '<span class="nm">%s%s<em>%s</em></span>'
                     '<span class="pz">%s</span></div>\n'
                     % (i, o.get('add', 0), 'true' if i == 0 else 'false',
                        flag, o['nm'], o['mt'],
                        ('+' + '{:,}'.format(o['add']) + '원') if o.get('add') else '기본'))
        options = ('<div class="w opt24">\n'
                   '  <!-- cafe24: <div module="product_option"> … {$product_option} 으로 치환된다.\n'
                   '       옵션명·추가금액은 관리자 상품등록 값이라 여기서 지어내지 않는다 -->\n'
                   '  <h2>%s</h2>\n  <p class="hint">%s</p>\n'
                   '  <div class="list" id="opt24" role="radiogroup">\n%s  </div>\n</div>'
                   % (c['opt_h2'], c['opt_hint'], rows))
    else:
        options = ''

    adds_js = json.dumps([dict(id=a[0], nm=a[1], mt=a[2], price=a[3], img=a[4]) for a in c['adds']],
                         ensure_ascii=False)

    html = TPL
    for k, v in dict(
        CSS0=css0, CSS1=css, EXTRA=extra,
        DOCTITLE=c['doctitle'], GNB=c['gnb'], BRAND=c['brand'], H1=c['h1'], SUB=c['sub'],
        PRDNO=str(c['prd_no']), PRICEROW=pricerow, OPTIONS=options,
        BADGES=''.join('<span>%s</span>' % b for b in c['badges']),
        KITN=str(len(c['kit'])), KIT=kit, KITJS=kit_js,
        RTH2=c['rt_h2'], RTDEK=c['rt_dek'], STEPS=steps, STEPJS=step_js, RTFOOT=c['rt_foot'],
        TYPEJS=(TYPE_JS if has_type else '') + (OPT_JS if c.get('options') else ''),
        QTYHINT=c['qty_hint'], DETAILH2=c['detail_h2'], HOW=c['how'], COMPOSE=c['compose'],
        NOTE2=c['note2'], CARTNAME=c['cartname'],
        NPRICE=str(c['price']), NWAS=str(c.get('was') or c['price']),
        HASOPT=('true' if c.get('options') else 'false'),
        MAXQTY=str(c.get('maxqty', 10)), ADDS=adds_js,
        STK=json.dumps(stk, ensure_ascii=False), HERO=json.dumps(hero), DET=json.dumps(det),
    ).items():
        html = html.replace('@@%s@@' % k, v)

    assert '@@' not in html, [x for x in html.split('@@')[1::2][:5]]
    out = ROOT + 'site/' + c['out']
    io.open(out, 'w', encoding='utf-8').write(html)
    print('%-34s %2d장  %.2fMB' % (c['out'], n, os.path.getsize(out)/1048576))

TPL = io.open(KMB+'set.tpl', encoding='utf-8').read()

if __name__ == '__main__':
    import sys
    for k in (sys.argv[1:] or ['kmb','swell','perf','dp_k','dp_m','dp_b','first']):
        build(k)
