# -*- coding: utf-8 -*-
import engine
cfg = {
 'title': '가루의 지형',
 'bg': '#EFEDE7',
 'extraCss': ':root{--ink:#14161A;--ink-2:#4E535C;--ink-3:#8A8F98}',
 'eyebrow': 'Version B · Terrain',
 'h1': '가루의 지형,<br>한 줄기의 길.',
 'lede': [
   '제품은 화면에 고정되고, <b>그 주변 세계가 통째로</b> 바뀝니다. 몬스터 레퍼런스의 문법입니다.',
   '백색 분말 지형 위로 라임빛 길이 드러나고, 스틱이 그 길을 가릅니다. 전부 실제 촬영·렌더 소재입니다.',
 ],
 'chapters': [
   {'seq':'terrain00','span':2.05},
   {'seq':'dark26','span':1.35,'q':66},
 ],
 'caps': [
   {'at':[0.02,0.14],'pos':'b','theme':'light','k':'Zengenetics','h':'가루가<br>지형이 될 때.'},
   {'at':[0.22,0.36],'pos':'b','theme':'light','k':'Potassium','h':'한 줄기,<br>라임의 길.'},
   {'at':[0.44,0.58],'pos':'b','theme':'light','k':'2.5 g','h':'그 길 위에<br>한 포.'},
   {'at':[0.66,0.80],'pos':'t','theme':'dark','k':'Open','h':'열면,<br>이 가루다.'},
   {'at':[0.86,1.00],'pos':'t','theme':'dark','k':'525 mg','h':'칼륨 525mg,<br>하루 두 포.','p':'1포 262.5mg · 한 상자 20포 · 라임 맛'},
 ],
 'trackH': 660,
 'tailTitle': '이 버전이 하는 것',
 'tail': [
   '<b>세계가 바뀐다</b> — 제품은 중심에 두고 주변 재질·색이 통째로 교체됩니다.',
   '<b>분말이 배경이 아니라 지형</b> — 가루 자체가 화면을 채우는 풍경이 됩니다.',
   '<b>밝은 세계 → 어둠</b> — 지형에서 개봉으로 넘어가며 톤이 반전됩니다.',
   '<b>제품 동일성</b> — 라벨을 실물과 4회 대조했습니다.',
 ],
}
b,f = engine.build(cfg, '/tmp/claude-0/seq/v2.html'); print('v2', b//1024,'KB', f,'프레임')
