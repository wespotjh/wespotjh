# -*- coding: utf-8 -*-
u"""스크롤 스크럽 홈 인트로 빌더.

레퍼런스(몬스터·NOIR·꿀)가 쓰는 구조 그대로:
  미리 렌더된 연속 장면을 스크롤 진행률로 넘긴다. 브라우저에서 움직임을 만들지 않는다.
"""
import base64, glob, json, os
from PIL import Image
import io

SEQ = '/tmp/claude-0/seq'


def load_seq(name, quality=None, maxw=None):
    fs = sorted(glob.glob(f'{SEQ}/{name}/*.jpg'))
    out = []
    for p in fs:
        if quality or maxw:
            im = Image.open(p).convert('RGB')
            if maxw and im.width > maxw:
                im = im.resize((maxw, round(im.height * maxw / im.width)), Image.LANCZOS)
            b = io.BytesIO(); im.save(b, 'JPEG', quality=quality or 68, optimize=True, progressive=True)
            raw = b.getvalue()
        else:
            raw = open(p, 'rb').read()
        out.append('data:image/jpeg;base64,' + base64.b64encode(raw).decode())
    return out


CSS = r'''
:root{
  --ink:#F4F3EF; --ink-2:#A9ADB6; --ink-3:#767B85;
  --f-d:"Archivo",-apple-system,BlinkMacSystemFont,sans-serif;
  --f-b:"Pretendard Variable",Pretendard,-apple-system,BlinkMacSystemFont,"Apple SD Gothic Neo","Malgun Gothic",sans-serif;
}
*{box-sizing:border-box}
html,body{margin:0}
body{background:var(--pg);color:var(--ink);font-family:var(--f-b);
     -webkit-text-size-adjust:100%;overflow-x:hidden}
img{max-width:100%}

.lead{padding:60px 24px 44px;max-width:620px;margin:0 auto}
.lead .k{font-family:var(--f-d);font-size:10px;letter-spacing:.3em;text-transform:uppercase;
  color:var(--ink-3);margin-bottom:14px}
.lead h1{font-weight:700;font-size:clamp(30px,8.6vw,46px);line-height:1.14;letter-spacing:-.042em;
  margin:0 0 16px;text-wrap:balance}
.lead p{color:var(--ink-2);font-size:15px;line-height:1.8;margin:0 0 10px;word-break:keep-all}
.lead .cue{margin-top:26px;font-family:var(--f-d);font-size:10.5px;letter-spacing:.22em;color:var(--ink-3)}
.lead .cue::after{content:"";display:block;width:1px;height:32px;background:currentColor;margin-top:10px;
  animation:drip 2s ease-in-out infinite;opacity:.55}
@keyframes drip{0%{transform:scaleY(0);transform-origin:top}58%{transform:scaleY(1);transform-origin:top}100%{transform:scaleY(1);opacity:0}}

.track{position:relative}
.stage{position:sticky;top:0;height:100svh;overflow:hidden;background:var(--pg)}
.stage canvas{position:absolute;inset:0;width:100%;height:100%;display:block}

.caps{position:absolute;inset:0;pointer-events:none;z-index:5}
.cap{position:absolute;left:0;right:0;padding:0 26px;opacity:0;will-change:opacity,transform}
.cap .k{font-family:var(--f-d);font-size:9.5px;letter-spacing:.3em;text-transform:uppercase;
  color:var(--ink-3);margin-bottom:9px}
.cap h2{font-weight:700;font-size:clamp(28px,8.6vw,50px);line-height:1.1;letter-spacing:-.045em;margin:0;
  word-break:keep-all;text-wrap:balance}
.cap p{margin:10px 0 0;color:var(--ink-2);font-size:14.5px;line-height:1.7;max-width:20em}
.cap--t{top:0;padding-top:9svh;padding-bottom:6svh}
.cap--b{bottom:0;padding-bottom:12svh;padding-top:7svh}
/* 장마다 배경 톤이 뒤집힌다. 자막 색도 그 장을 따라가야 읽힌다.
   스크림은 자막 띠에만 깐다 — 화면 전체를 덮으면 영상이 죽는다. */
.cap.on-dark{color:#F4F3EF}
.cap.on-dark .k{color:#8B909B} .cap.on-dark p{color:#A9ADB6}
.cap.on-dark.cap--t{background:linear-gradient(180deg,rgba(4,5,7,.72),rgba(4,5,7,.30) 64%,transparent)}
.cap.on-dark.cap--b{background:linear-gradient(0deg,rgba(4,5,7,.76),rgba(4,5,7,.34) 62%,transparent)}
.cap.on-light{color:#14161A}
.cap.on-light .k{color:#7E838D} .cap.on-light p{color:#4E535C}
.cap.on-light.cap--t{background:linear-gradient(180deg,rgba(246,245,241,.86),rgba(246,245,241,.42) 64%,transparent)}
.cap.on-light.cap--b{background:linear-gradient(0deg,rgba(246,245,241,.88),rgba(246,245,241,.44) 62%,transparent)}

.hud{position:absolute;left:0;right:0;bottom:18px;z-index:6;display:flex;justify-content:space-between;
  align-items:center;padding:0 22px;pointer-events:none}
.bar{display:flex;gap:5px}
.bar i{width:14px;height:2px;background:currentColor;opacity:.2;transition:opacity .3s,width .3s}
.bar i.on{opacity:1;width:24px}
.pn{font-family:var(--f-d);font-size:10px;letter-spacing:.14em;opacity:.55;font-variant-numeric:tabular-nums}

.load{position:absolute;left:0;right:0;bottom:56px;z-index:7;text-align:center;
  font-family:var(--f-d);font-size:10px;letter-spacing:.2em;opacity:0;transition:opacity .3s}
.load.on{opacity:.6}

.tail{padding:60px 24px 96px;max-width:620px;margin:0 auto}
.tail h3{font-size:18px;font-weight:700;margin:0 0 14px;letter-spacing:-.02em}
.tail ul{margin:0;padding-left:18px;color:var(--ink-2);font-size:14.5px;line-height:1.9}
.tail li{margin-bottom:7px;word-break:keep-all}
.tail .fine{margin-top:26px;font-size:11.5px;color:var(--ink-3);line-height:1.8}
@media (prefers-reduced-motion:reduce){.lead .cue::after{animation:none}}
'''

JS = r'''
(function(){
  var CFG = window.__ZG__;
  var track=document.getElementById('track'), stage=document.getElementById('stage');
  var cv=document.getElementById('cv'), ctx=cv.getContext('2d', {alpha:false});
  var pn=document.getElementById('pn'), bar=document.getElementById('bar'), load=document.getElementById('load');
  var capEls=CFG.caps.map(function(_,i){return document.getElementById('cap'+i);});

  function cl(v,a,b){return v<a?a:(v>b?b:v);}
  function seg(p,a,b){return cl((p-a)/(b-a),0,1);}
  function bell(p,a,b,f){f=f||.028;return Math.min(seg(p,a,a+f),1-seg(p,b-f,b));}

  /* ── 프레임 적재 ──
     각 장(chapter)의 첫 프레임을 "바닥 판"으로 먼저 띄운다.
     그래야 빠르게 스크롤해도 빈 화면이 안 나온다. */
  var chapters = CFG.chapters.map(function(ch){
    return {span:ch.span, imgs:new Array(ch.src.length), src:ch.src, ready:0, floor:null};
  });
  var totalSpan = chapters.reduce(function(a,c){return a+c.span;},0);
  var totalFrames = chapters.reduce(function(a,c){return a+c.src.length;},0);
  var loaded = 0;

  function loadFrame(ci, fi, prio){
    var ch=chapters[ci];
    if (ch.imgs[fi]) return;
    var im=new Image();
    ch.imgs[fi]=im;
    im.onload=function(){ ch.ready++; loaded++; onProgress(); draw(); };
    im.onerror=function(){ ch.ready++; loaded++; onProgress(); };
    im.decoding='async';
    im.src=ch.src[fi];
  }
  function onProgress(){
    if (loaded>=totalFrames){ load.classList.remove('on'); }
    else { load.classList.add('on'); load.textContent='LOADING '+Math.round(loaded/totalFrames*100)+'%'; }
  }
  /* 첫 장을 먼저 전부, 나머지는 순서대로 */
  (function warm(){
    var order=[];
    chapters.forEach(function(ch,ci){
      order.push([ci,0]);                       /* 바닥 판 먼저 */
      order.push([ci,ch.src.length-1]);
    });
    chapters.forEach(function(ch,ci){
      for(var i=1;i<ch.src.length-1;i++) order.push([ci,i]);
    });
    var k=0;
    (function pump(){
      var burst=0;
      while(k<order.length && burst<6){ loadFrame(order[k][0],order[k][1]); k++; burst++; }
      if(k<order.length) setTimeout(pump, 40);
    })();
  })();

  /* ── 캔버스 ── */
  var DPR=Math.min(window.devicePixelRatio||1,2), W=0, H=0;
  function size(){
    W=stage.clientWidth; H=stage.clientHeight;
    cv.width=Math.round(W*DPR); cv.height=Math.round(H*DPR);
    ctx.setTransform(DPR,0,0,DPR,0,0);
  }

  function pickReady(ch, idx){
    /* 교체 직전 낱장 검사 — 준비 안 된 프레임은 절대 그리지 않는다.
       그 자리에는 가장 가까운 준비된 프레임을 쓴다(빈 판 방지). */
    var n=ch.src.length;
    for(var d=0; d<n; d++){
      var a=idx-d, b=idx+d;
      if(a>=0 && ch.imgs[a] && ch.imgs[a].complete && ch.imgs[a].naturalWidth) return ch.imgs[a];
      if(b<n  && ch.imgs[b] && ch.imgs[b].complete && ch.imgs[b].naturalWidth) return ch.imgs[b];
    }
    return null;
  }

  function paint(im){
    if(!im) return;
    var s=Math.max(W/im.naturalWidth, H/im.naturalHeight);
    var w=im.naturalWidth*s, h=im.naturalHeight*s;
    ctx.drawImage(im, (W-w)/2, (H-h)/2, w, h);
  }

  function draw(){
    if(!W) size();
    var r=track.getBoundingClientRect();
    /* 분모는 트랙이 아니라 (트랙 − 스테이지) 다 — sticky 에서 실제 연출 거리 */
    var span=track.offsetHeight-stage.offsetHeight;
    var p=cl((-r.top)/(span||1),0,1);

    pn.textContent=String(Math.round(p*100)).padStart(2,'0');
    for(var i=0;i<bar.children.length;i++) bar.children[i].classList.toggle('on', p*bar.children.length>i);

    /* 전역 진행률 → 어느 장의 몇 번째 프레임인가 */
    var acc=0, ci=0, t=0;
    for(var c=0;c<chapters.length;c++){
      var w=chapters[c].span/totalSpan;
      if(p<=acc+w || c===chapters.length-1){ ci=c; t=cl((p-acc)/w,0,1); break; }
      acc+=w;
    }
    var ch=chapters[ci];
    var idx=Math.min(ch.src.length-1, Math.round(t*(ch.src.length-1)));
    paint(pickReady(ch, idx));

    for(var m=0;m<capEls.length;m++){
      var wnd=CFG.caps[m].at;
      var o=bell(p,wnd[0],wnd[1]);
      capEls[m].style.opacity=String(o);
      capEls[m].style.transform='translateY('+((1-o)*13).toFixed(1)+'px)';
    }
  }

  var ticking=false;
  function onScroll(){ if(ticking) return; ticking=true;
    requestAnimationFrame(function(){ ticking=false; draw(); }); }
  window.addEventListener('scroll', onScroll, {passive:true});
  window.addEventListener('resize', function(){ size(); draw(); }, {passive:true});
  size(); draw(); onProgress();
})();
'''


def build(cfg, out_path):
    chapters = []
    for ch in cfg['chapters']:
        src = load_seq(ch['seq'], quality=ch.get('q'), maxw=ch.get('w'))
        chapters.append({'span': ch['span'], 'src': src})
    payload = {'chapters': chapters, 'caps': [{'at': c['at']} for c in cfg['caps']]}

    caps_html = ''
    for i, c in enumerate(cfg['caps']):
        pos = 'cap--' + c.get('pos', 'b') + ' on-' + c.get('theme', 'dark')
        k = ('<div class="k">%s</div>' % c['k']) if c.get('k') else ''
        sub = ('<p>%s</p>' % c['p']) if c.get('p') else ''
        caps_html += ('<div class="cap %s" id="cap%d">%s<h2>%s</h2>%s</div>\n' % (pos, i, k, c['h'], sub))

    dots = '<i></i>' * 8
    total_frames = sum(len(c['src']) for c in chapters)
    track_h = cfg.get('trackH', 620)

    html = ('<title>%s</title>\n' % cfg['title'] +
      '<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Archivo:wght@400;600;700&display=swap">\n'
      '<style>\n:root{--pg:%s}\n%s\n%s</style>\n' % (cfg['bg'], CSS, cfg.get('extraCss', '')) +
      '<div class="lead">\n'
      '  <div class="k">%s</div>\n  <h1>%s</h1>\n' % (cfg['eyebrow'], cfg['h1']) +
      ''.join('  <p>%s</p>\n' % x for x in cfg['lede']) +
      '  <div class="cue">SCROLL</div>\n</div>\n'
      '<div class="track" id="track" style="height:%dsvh">\n'
      '  <div class="stage" id="stage">\n'
      '    <canvas id="cv"></canvas>\n'
      '    <div class="caps">\n%s    </div>\n'
      '    <div class="hud"><div class="bar" id="bar">%s</div><div class="pn" id="pn">00</div></div>\n'
      '    <div class="load" id="load"></div>\n'
      '  </div>\n</div>\n' % (track_h, caps_html, dots) +
      '<div class="tail">\n  <h3>%s</h3>\n  <ul>%s</ul>\n'
      '  <p class="fine">*화면 연출은 제품 이미지이며, 섭취에 따른 효과를 나타내지 않습니다<br>'
      '*건강기능식품은 질병의 예방 및 치료를 위한 의약품이 아닙니다</p>\n</div>\n'
      % (cfg['tailTitle'], ''.join('<li>%s</li>' % x for x in cfg['tail'])) +
      '<script>window.__ZG__=' + json.dumps(payload) + ';</script>\n' +
      '<script>' + JS + '</script>\n')

    open(out_path, 'w', encoding='utf-8').write(html)
    return len(html.encode()), total_frames
