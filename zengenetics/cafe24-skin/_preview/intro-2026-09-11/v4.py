# -*- coding: utf-8 -*-
import engine
cfg = {
 'title': '아침부터 밤까지',
 'bg': '#0A0B0D',
 'eyebrow': 'Version D · Morning to night',
 'h1': '아침부터<br>밤까지,<br>한 포씩.',
 'lede': [
   '하루의 세 시간대를 <b>세 개의 세계</b>로 지나갑니다 — 밝은 가루 지형, 어둠 속 개봉, 물속 확산.',
   '제품은 계속 같은 대상으로 이어지고, 주변만 바뀝니다.',
 ],
 'chapters': [
   {'seq':'terrain00','span':1.60,'q':60},
   {'seq':'dark24','span':1.10,'q':70},
   {'seq':'glass05','span':1.15,'q':64},
 ],
 'caps': [
   {'at':[0.02,0.13],'pos':'b','theme':'light','k':'Morning','h':'아침엔<br>가볍게.'},
   {'at':[0.20,0.34],'pos':'b','theme':'light','k':'Potassium','h':'라임의 길,<br>한 줄기.'},
   {'at':[0.46,0.66],'pos':'b','theme':'dark','k':'Evening','h':'저녁엔<br>뜯어서.','p':'물도 컵도 필요 없는 분말 스틱.'},
   {'at':[0.73,0.86],'pos':'t','theme':'light','k':'Night','h':'밤엔<br>물 한 잔에.'},
   {'at':[0.87,1.00],'pos':'t','theme':'light','k':'525 mg','h':'칼륨 525mg,<br>하루 두 포.','p':'1포 262.5mg · 한 상자 20포 · 라임 맛'},
 ],
 'trackH': 650,
 'tailTitle': '이 버전이 하는 것',
 'tail': [
   '<b>하루 서사</b> — 아침·저녁·밤을 세 개의 세계로 지나갑니다.',
   '<b>세계는 바뀌고 제품은 이어진다</b> — 지형 → 어둠 → 물, 같은 스틱입니다.',
   '<b>톤이 세 번 반전</b> — 밝음 → 어둠 → 밝음. 강약이 생깁니다.',
   '<b>제품 동일성</b> — 라벨을 실물과 4회 대조했습니다.',
 ],
}
b,f = engine.build(cfg, '/tmp/claude-0/seq/v4.html'); print('v4', b//1024,'KB', f,'프레임')
