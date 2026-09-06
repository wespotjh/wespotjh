# -*- coding: utf-8 -*-
import io, json
T = json.load(open('thumbs.json'))
OUT = '/home/user/wespotjh/zengenetics/site/index.html'

PAGES = [
 dict(g='홈 · 브랜드', items=[
   dict(k='home', nm='홈', dek='히어로 · 제품 3종 · 세트 3종 · 실적 · FAQ — 상품 카드에서 각 페이지로 연결',
        url='https://claude.ai/code/artifact/9656f1c2-3dd7-4f5f-b9a8-a26d74b25be8',
        st='피그마 수정 반영 완료', tone='ok', tag='home.html'),
   dict(k='brand-story', nm='브랜드 스토리 「하루를 고르게」', dek='zen 웰니스·명상 톤 10장 · 이미지 위 제목',
        url='https://claude.ai/code/artifact/1fd7a5ca-973c-4731-b9db-af263ab98343',
        st='마지막 확인 대기', tone='wait', tag='brand-story.html'),
 ]),
 dict(g='단품 3종', items=[
   dict(k='product-potassium', nm='칼륨', dek='45,000 → 34,900 · 22% · 상세 14장',
        url='https://claude.ai/code/artifact/9ee9223d-6eff-4d2d-8d97-9e50927adbe1',
        st='리뷰 수 훅 교체 필요', tone='wait', tag='product-potassium.html'),
   dict(k='product-vitaminb', nm='비타민B 컴플렉스', dek='49,000 → 37,900 · 23% · 상세 15장',
        url='https://claude.ai/code/artifact/a95de7da-56b0-43b6-bd19-ac997e830b4a',
        st='리뷰 수 훅 교체 필요', tone='wait', tag='product-vitaminb.html'),
   dict(k='product-magnesium', nm='마그네슘', dek='49,000 → 37,900 · 23% · 상세 16장',
        url='https://claude.ai/code/artifact/4cd6d9e9-53fc-45ad-b8fb-6170e3d4e090',
        st='리뷰 수 훅 교체 필요', tone='wait', tag='product-magnesium.html'),
 ]),
 dict(g='세트 3종 — 신규', items=[
   dict(k='product-set-kmb', nm='칼마비 건강 루틴', dek='143,000 → 107,500 · 25% · 상세 15장 + 하루 루틴 · 3박스',
        url='https://claude.ai/code/artifact/abe7bfbd-cce3-478c-97d4-526284dd94e0',
        st='신규', tone='new', tag='product-set-kmb.html'),
   dict(k='product-set-swell', nm='붓기 부스터', dek='139,000 → 104,000 · 25% · 상세 25장 + 하루 루틴',
        url='https://claude.ai/code/artifact/3fa36b43-5e8d-46a3-bc9d-57f0aa009c60',
        st='신규', tone='new', tag='product-set-swell.html'),
   dict(k='product-set-performance', nm='퍼포먼스 부스터', dek='98,000 → 71,900 · 27% · 상세 27장 + 운동 전후 루틴',
        url='https://claude.ai/code/artifact/02650a10-0f76-423b-9141-62ee3fd3b3be',
        st='신규', tone='new', tag='product-set-performance.html'),
 ]),
]

cards = ''
for grp in PAGES:
    cards += '<h2 class="gh">%s <i>%d</i></h2>\n<div class="grid">\n' % (grp['g'], len(grp['items']))
    for it in grp['items']:
        cards += """<a class="card" href="%s" target="_blank" rel="noopener">
  <span class="shot"><img src="%s" alt="%s 미리보기" loading="lazy"></span>
  <span class="body">
    <span class="st %s">%s</span>
    <strong>%s</strong>
    <em>%s</em>
    <code>%s</code>
  </span>
</a>\n""" % (it['url'], T[it['k']], it['nm'], it['tone'], it['st'], it['nm'], it['dek'], it['tag'])
    cards += '</div>\n'

HTML = """<!doctype html><html><head><meta charset=utf8><meta name=viewport content="width=device-width,initial-scale=1"></head><body>
<title>젠제네틱스 리뉴얼 — 전체 페이지</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@500;600;700&family=IBM+Plex+Sans+KR:wght@300;400;500;600;700&family=IBM+Plex+Mono:wght@400;500&display=swap">
<style>
 :root{--bg:#FBFAF8;--card:#fff;--ink:#15161A;--ink2:#5F626C;--ink3:#93959D;
       --hair:#E9E8E4;--navy:#1A2B6B;--ok:#127A4B;--wait:#B4740B;--new:#3757C4;
       --fd:"Archivo","IBM Plex Sans KR",sans-serif;
       --fb:"IBM Plex Sans KR",-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo",sans-serif;
       --fm:"IBM Plex Mono",ui-monospace,monospace}
 *{box-sizing:border-box}
 body{margin:0;background:var(--bg);color:var(--ink);font-family:var(--fb);line-height:1.7;
      -webkit-text-size-adjust:100%;padding:0 0 60px}
 .w{max-width:1120px;margin:0 auto;padding:0 22px}
 header{border-bottom:1px solid var(--hair);background:#fff;padding:34px 0 30px;margin-bottom:34px}
 .lab{font-family:var(--fm);font-size:10.5px;letter-spacing:.2em;text-transform:uppercase;color:var(--ink3)}
 h1{font-size:clamp(24px,4.6vw,32px);font-weight:700;letter-spacing:-.03em;margin:11px 0 9px;line-height:1.28}
 header p{margin:0;color:var(--ink2);font-size:14.5px;max-width:640px;word-break:keep-all}
 .meta{margin-top:18px;display:flex;flex-wrap:wrap;gap:7px}
 .meta span{font-size:11.5px;color:var(--ink2);background:var(--bg);border:1px solid var(--hair);
            border-radius:999px;padding:5px 12px}
 .gh{font-size:15px;font-weight:700;letter-spacing:-.015em;margin:36px 0 14px;
     display:flex;align-items:center;gap:8px}
 .gh i{font-style:normal;font-family:var(--fd);font-size:11px;font-weight:600;color:var(--ink3);
       border:1px solid var(--hair);border-radius:999px;padding:1px 8px}
 .grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(248px,1fr));gap:16px}
 .card{display:block;text-decoration:none;color:inherit;background:var(--card);
       border:1px solid var(--hair);border-radius:16px;overflow:hidden;
       transition:transform .16s ease,box-shadow .16s ease,border-color .16s}
 .card:hover{transform:translateY(-3px);border-color:#D8D6D0;box-shadow:0 10px 26px rgba(20,26,45,.09)}
 .shot{display:block;height:250px;overflow:hidden;background:#F2F1ED;border-bottom:1px solid var(--hair)}
 .shot img{width:100%;display:block}
 .body{display:block;padding:15px 16px 17px}
 .st{display:inline-block;font-size:10.5px;font-weight:700;letter-spacing:-.01em;
     border-radius:999px;padding:3px 9px;margin-bottom:9px}
 .st.ok{background:#E7F3EC;color:var(--ok)} .st.wait{background:#FBF1DE;color:var(--wait)}
 .st.new{background:#E4E9F8;color:var(--new)}
 .body strong{display:block;font-size:15.5px;font-weight:700;letter-spacing:-.02em;margin-bottom:4px}
 .body em{display:block;font-style:normal;font-size:12.5px;color:var(--ink2);word-break:keep-all;line-height:1.6}
 .body code{display:block;font-family:var(--fm);font-size:10.5px;color:var(--ink3);margin-top:9px}
 .foot{margin-top:44px;border-top:1px solid var(--hair);padding-top:22px;
       font-size:12.5px;color:var(--ink2);line-height:1.85;word-break:keep-all}
 .foot b{color:var(--ink)}
 .foot a{color:var(--navy)}
 @media(max-width:520px){ .shot{height:210px} }
</style>

<header><div class="w">
  <span class="lab">Zengenetics renewal</span>
  <h1>지금까지 만든 페이지 전부</h1>
  <p>카드를 누르면 실제 페이지가 새 탭에서 열립니다. 전부 모바일 기준으로 만들었고,
     아직 <b>라이브(zengenetics.co.kr)에는 올리지 않았습니다.</b></p>
  <div class="meta"><span>총 8장</span><span>세트 3종 신규</span><span>피그마 반영 완료</span><span>2026-09-06</span></div>
</div></header>

<div class="w">
@@CARDS@@
<div class="foot">
  <b>보시는 순서 제안</b> — 홈 → 브랜드 스토리 → 단품 3종 → 세트 3종.<br>
  <b>가격·할인율</b>은 cafe24 상품등록 값 그대로입니다. %는 스킨이 계산하는 자리라 우리가 쓰지 않습니다.<br>
  <b>평점·리뷰 수</b>는 넣지 않았습니다. 알파리뷰 앱이 채울 자리만 비워 뒀습니다.
  단품 3종에는 예전 숫자가 남아 있어 다음에 훅으로 교체합니다.<br>
  <b>상세 이미지</b>는 대표님이 만드신 것을 공홈 게시 순서 그대로 넣었습니다.<br>
  고쳤으면 하는 곳을 말씀해 주시면 그대로 반영하고, 같은 링크로 다시 올립니다.
</div>
</div>

</body></html>
"""
io.open(OUT,'w',encoding='utf-8').write(HTML.replace('@@CARDS@@',cards))
import os; print(OUT,'%.2fMB'%(os.path.getsize(OUT)/1048576))
