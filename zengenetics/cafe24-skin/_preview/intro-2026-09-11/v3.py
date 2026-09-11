# -*- coding: utf-8 -*-
import engine
cfg = {
 'title': '당신의 방식으로',
 'bg': '#F3F1EC',
 'extraCss': ':root{--ink:#15171B;--ink-2:#4E535C;--ink-3:#8A8F98}',
 'eyebrow': 'Version C · Ritual',
 'h1': '뜯고,<br>붓고,<br>퍼진다.',
 'lede': [
   '한 포를 여는 순간부터 잔 속에 퍼질 때까지, <b>끊기지 않고</b> 이어집니다.',
   '어둠에서 시작해 물빛으로 열립니다. 꿀·차 레퍼런스의 「의식」 톤입니다.',
 ],
 'chapters': [
   {'seq':'dark24','span':1.15,'q':70},
   {'seq':'glass03','span':1.25},
   {'seq':'glass05','span':1.20},
 ],
 'caps': [
   {'at':[0.02,0.15],'pos':'b','theme':'dark','k':'Evening','h':'하루의 끝,<br>한 포.'},
   {'at':[0.20,0.32],'pos':'b','theme':'dark','k':'Tear line','h':'뜯어서,<br>3초면 끝.'},
   {'at':[0.42,0.56],'pos':'t','theme':'light','k':'Into water','h':'물 한 잔에,<br>그대로.'},
   {'at':[0.64,0.78],'pos':'t','theme':'light','k':'Dissolve','h':'퍼진다.'},
   {'at':[0.86,1.00],'pos':'t','theme':'light','k':'525 mg','h':'칼륨 525mg,<br>하루 두 포.','p':'1포 262.5mg · 한 상자 20포 · 라임 맛'},
 ],
 'trackH': 640,
 'tailTitle': '이 버전이 하는 것',
 'tail': [
   '<b>하나의 행동이 다음으로</b> — 개봉 → 낙하 → 확산이 한 줄기로 이어집니다.',
   '<b>어둠에서 빛으로</b> — 제품 구간은 어둡게, 물 구간은 밝게 반전됩니다.',
   '<b>섭취 방식을 보여준다</b> — 물에 타는 실제 장면입니다.',
   '<b>제품 동일성</b> — 라벨을 실물과 4회 대조했습니다.',
 ],
}
b,f = engine.build(cfg, '/tmp/claude-0/seq/v3.html'); print('v3', b//1024,'KB', f,'프레임')
