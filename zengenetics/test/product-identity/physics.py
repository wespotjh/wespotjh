# -*- coding: utf-8 -*-
u"""가루 물리 검수 — 대표님 지시 2026-09-11.

  "가루가 들어갈때 무슨 핵폭탄처럼 위로 가루가 퍼지는거 정말 어색하다
   실물고증하나두 안되있다"

가루는 물보다 무겁다. **가라앉는다.** 위로 퍼지는 건 연기다.
소재의 인상이 아니라 수치로 판정한다: 채도가 있는 픽셀(= 가루)의
세로 무게중심이 재생 내내 **아래로 내려가야** 한다.

사용:
    python3 test/product-identity/physics.py <영상.mp4> [...]

판정:
    PASS  — 무게중심이 내려가고(+0.10 이상) 되올라가지 않고, 수면 위가 비어 있다
    FAIL  — 올라간다 / 제자리다 / 컵 위로 연기 기둥이 솟는다

주의 1: 잔이 색으로 가득 차면 무게중심이 화면 중앙으로 수렴한다.
        그래서 **투입 구간(면적 35% 도달 전)** 만 본다.
주의 2: 공중 검사는 **스틱이 화면 밖인 컷**을 전제한다. 스틱이나 쏟아지는
        줄기가 화면 위쪽에 있으면 그걸 연기로 오인한다. 라벨이 보이는 컷은
        이 항목을 눈으로 판정하라.
주의 3: 통과했다고 쓸 수 있는 게 아니다. 이건 명백한 탈락을 걸러내는 체이지
        합격 도장이 아니다 — 판정은 검수팀이 눈으로 한다.
"""
import os, sys, glob, shutil, subprocess
import numpy as np
from PIL import Image

FF = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
FPS = 2.0
SAT_MIN = 0.20      # 유리·물·흰 배경은 무채색이라 이 아래로 떨어진다
VAL_MIN = 0.15      # 검은 배경 소재의 그림자를 가루로 세지 않는다
SIDE = 0.12         # 좌우 가장자리(라벨·배경)는 제외
FULL = 0.35         # 잔이 이만큼 차면 확산이 아니라 착색 — 판정에서 뺀다
ENTERED = 0.02      # 가루가 실제로 들어온 시점. 이 아래는 빈 잔의 노이즈다
DROP_MIN = 0.10     # 통과 하한. 실측: 합격컷 +0.137~+0.267, 반려컷 +0.054 — 그 사이에 둔다
TOP_BAND = 0.15     # 화면 위쪽 이 비율을 '공중'으로 본다
TOP_MAX = 0.10      # 공중에 이만큼 차면 연기 기둥이다 (실측: 김 기둥 0.86, 정상 0.01)


def frames(src, out):
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    subprocess.run([FF, '-v', 'error', '-i', src, '-vf', f'fps={FPS},scale=540:-1',
                    out + '/%03d.png', '-y'], capture_output=True)
    return sorted(glob.glob(out + '/*.png'))


def airborne(path):
    u"""화면 위쪽 '공중' 구역의 이물 비율.

    컵 위로 솟는 연기 기둥·분진을 잡는다. 가라앉음 수치만으로는 안 잡힌다 —
    무게중심이 제자리여도 김 기둥은 그대로 남는다.
    """
    im = np.asarray(Image.open(path).convert('RGB')).astype(np.float32) / 255.
    H, W, _ = im.shape
    top = im[:int(H * TOP_BAND), int(W * 0.18):int(W * 0.82)]
    mx = top.max(2); mn = top.min(2)
    sat = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0)
    bg = np.percentile(top.mean(2), 90)
    return float(((sat > 0.12) | (top.mean(2) < bg - 0.10)).mean())


def plume(path):
    u"""가루 픽셀의 세로 무게중심(0=위, 1=아래)과 화면 점유 면적."""
    im = np.asarray(Image.open(path).convert('RGB')).astype(np.float32) / 255.
    H, W, _ = im.shape
    mx = im.max(2); mn = im.min(2)
    sat = np.where(mx > 1e-5, (mx - mn) / np.maximum(mx, 1e-5), 0)
    m = (sat > SAT_MIN) & (mx > VAL_MIN)
    m[:, :int(W * SIDE)] = False
    m[:, int(W * (1 - SIDE)):] = False
    if m.sum() < 200:
        return None, 0.0
    return np.nonzero(m)[0].mean() / H, m.sum() / float(H * W)


def check(src, tmp):
    fs = frames(src, tmp)
    rows = [(i / FPS,) + plume(p) for i, p in enumerate(fs)]
    air = [airborne(p) for p in fs]
    nbad = sum(1 for a in air if a > TOP_MAX)
    if nbad:
        return ('FAIL', rows,
                u'수면 위에 연기 기둥/분진 — %d/%d 프레임, 최대 %.3f' % (nbad, len(air), max(air)))
    live = [(t, y, a) for t, y, a in rows if y is not None]
    if len(live) < 4:
        return 'JUDGE_FAIL', rows, u'가루가 잡히지 않는다 — 해당없음이거나 소재가 잘못됐다'
    # 가루가 들어오기 전 프레임을 시작점으로 삼으면 안 된다 —
    # 빈 잔에서 잡히는 0.5% 안팎의 잡픽셀 위치는 색보정만으로도 흔들려서
    # 같은 영상이 보정 전후로 다르게 판정된다(실측: +0.137 vs +0.015).
    start = next((i for i, r in enumerate(live) if r[2] >= ENTERED), 0)
    win = [r for r in live[start:] if r[2] < FULL] or live[start:start + max(1, (len(live) - start) // 2)]
    if len(win) < 3:
        return 'JUDGE_FAIL', rows, u'투입 구간이 너무 짧다 — 눈으로 봐라'
    ys = [y for _, y, _ in win]
    drop = ys[-1] - ys[0]
    rise = max((ys[i] - min(ys[i:]) for i in range(len(ys))), default=0.0)
    if drop < DROP_MIN:
        return 'FAIL', rows, u'가라앉지 않는다 (하강 %+.3f)' % drop
    if rise > 0.06:
        return 'FAIL', rows, u'중간에 되올라간다 (최대 상승 %.3f)' % rise
    return 'PASS', rows, u'하강 %+.3f' % drop


def main(argv):
    if not argv:
        print(__doc__); return 2
    bad = 0
    for i, src in enumerate(argv):
        tmp = f'/tmp/physics_{os.getpid()}_{i}'
        verdict, rows, why = check(src, tmp)
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"\n== {os.path.basename(src)}")
        for t, y, a in rows:
            print(f"   t={t:4.1f}s  " + ('--' if y is None else f"y={y:.3f}  면적={a*100:5.1f}%"))
        print(f"   → {verdict} — {why}")
        if verdict != 'PASS':
            bad += 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
