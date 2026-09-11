# -*- coding: utf-8 -*-
u"""영상 → 9:16 프레임 시퀀스. 스크롤 스크럽용."""
import os, subprocess, sys, json, glob
from PIL import Image
FF='/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
W,H=540,960

def build(src, name, n, quality=68, fit='contain', bg=(0,0,0), trim=(0.0,1.0), zoom=1.0, shift=0.0):
    out=f'/tmp/claude-0/seq/{name}'
    os.makedirs(out, exist_ok=True)
    for f in glob.glob(out+'/*.jpg'): os.remove(f)
    raw=out+'/_raw'; os.makedirs(raw, exist_ok=True)
    for f in glob.glob(raw+'/*.png'): os.remove(f)
    # 균등 간격 추출
    subprocess.run([FF,'-v','error','-i',src,'-vf',f'fps={n}/5' if False else 'null','-f','null','-'],capture_output=True)
    d=subprocess.run([FF,'-hide_banner','-i',src],capture_output=True,text=True).stderr
    dur=5.0
    for line in d.splitlines():
        if 'Duration:' in line:
            h,m,s=line.split('Duration:')[1].split(',')[0].strip().split(':')
            dur=int(h)*3600+int(m)*60+float(s); break
    # trim = (시작비율, 끝비율). 정지 구간과 검은 꼬리를 잘라낸다.
    t0, t1 = trim[0]*dur, trim[1]*dur
    win = max(0.1, t1-t0)
    subprocess.run([FF,'-v','error','-ss',f'{t0:.3f}','-t',f'{win:.3f}','-i',src,
                    '-vf',f'fps={n/win:.6f}','-frames:v',str(n),'-y',raw+'/%03d.png'],capture_output=True)
    files=sorted(glob.glob(raw+'/*.png'))
    tot=0
    for i,p in enumerate(files[:n]):
        im=Image.open(p).convert('RGB')
        if fit=='cover':
            s=max(W/im.width, H/im.height)
        else:
            s=min(W/im.width, H/im.height)
        s*=zoom
        nw,nh=max(1,round(im.width*s)),max(1,round(im.height*s))
        im=im.resize((nw,nh),Image.LANCZOS)
        cv=Image.new('RGB',(W,H),bg)
        cv.paste(im,((W-nw)//2, int((H-nh)//2 - H*shift)))
        fp=f'{out}/{i:03d}.jpg'
        cv.save(fp,'JPEG',quality=quality,optimize=True,progressive=True)
        tot+=os.path.getsize(fp)
    for f in glob.glob(raw+'/*.png'): os.remove(f)
    os.rmdir(raw)
    got=len(glob.glob(out+'/*.jpg'))
    print(f'{name:10s} {got:3d}장  {tot//1024:5d}KB  평균 {tot//max(1,got)//1024}KB  dur={dur:.1f}s')
    return got, tot

if __name__=='__main__':
    V='/tmp/claude-0/hf/video/'
    plan=[
      (V+'27_흑배경_기울여_가루기둥_더미_최상.mp4','dark27',54,'contain',(0,0,0)),
      (V+'00_백색가루지형_주황길_스틱슬라이드_9x16.mp4','terrain00',60,'cover',(255,255,255)),
      (V+'24_흑배경_정지에서기울여_가루쏟기_최상.mp4','dark24',48,'contain',(0,0,0)),
      (V+'26_흑배경_절취캡분리_대량가루_10s.mp4','dark26',60,'contain',(0,0,0)),
      (V+'03_주황가루_잔에낙하_확산.mp4','glass03',44,'cover',(245,244,240)),
      (V+'05_주황가루_잔바닥에서_상승확산.mp4','glass05',44,'cover',(245,244,240)),
      (V+'21_흑배경_클로즈업_굵은줄기_큰더미.mp4','dark21',48,'contain',(0,0,0)),
    ]
    grand=0
    for src,name,n,fit,bg in plan:
        if not os.path.exists(src): print('없음',src); continue
        g,t=build(src,name,n,fit=fit,bg=bg); grand+=t
    print('합계', grand//1024,'KB')
