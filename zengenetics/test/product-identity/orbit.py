# -*- coding: utf-8 -*-
u"""카메라 회전 검수 — 대표님 지시 2026-09-11 ("물컵을 360도로 돌리면").

잔은 회전대칭이라 돌려도 실루엣이 안 변한다. 그래서 잔이 아니라
**스틱의 짙은 네이비 인쇄**를 추적한다. 축에서 벗어나 있는 스틱은
카메라가 둘레를 돌면 화면 가로축을 크게 쓸고 지나간다.
푸시인만 있는 고정 카메라면 x 가 거의 안 변한다.

사용:
    python3 test/product-identity/orbit.py <영상.mp4> [...]

판정 (가로 이동폭):
    > 0.30  회전함        0.12~0.30  약간 움직임        < 0.12  고정
"""
import os, sys, glob, shutil, subprocess
import numpy as np
from PIL import Image

FF = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
FPS = 2.0


def navy_x(path):
    u"""워드마크·한글 인쇄의 짙은 네이비 픽셀 가로 무게중심 (0=좌, 1=우)."""
    a = np.asarray(Image.open(path).convert('RGB')).astype(np.float32)
    H, W, _ = a.shape
    r, g, b = a[..., 0], a[..., 1], a[..., 2]
    m = (b > r + 18) & (b > g + 10) & (a.max(2) < 175)
    m[int(H * 0.55):] = False        # 아래쪽 잔·물은 제외
    if m.sum() < 60:
        return None
    return np.nonzero(m)[1].mean() / W


def check(src, tmp):
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    subprocess.run([FF, '-v', 'error', '-i', src, '-vf', f'fps={FPS},scale=540:-1',
                    tmp + '/%03d.png', '-y'], capture_output=True)
    xs = [navy_x(p) for p in sorted(glob.glob(tmp + '/*.png'))]
    got = [x for x in xs if x is not None]
    if len(got) < 3:
        return 'JUDGE_FAIL', xs, 0.0, u'스틱 인쇄가 잡히지 않는다'
    span = max(got) - min(got)
    if span > 0.30:
        return 'PASS', xs, span, u'회전함'
    return 'FAIL', xs, span, (u'약간 움직임' if span > 0.12 else u'고정 — 회전 없음')


def main(argv):
    if not argv:
        print(__doc__); return 2
    bad = 0
    for i, src in enumerate(argv):
        tmp = f'/tmp/orbit_{os.getpid()}_{i}'
        verdict, xs, span, why = check(src, tmp)
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"\n== {os.path.basename(src)}  (스틱 인쇄 x)")
        for j, x in enumerate(xs):
            print(f"   t={j/FPS:4.1f}s  " + ('--' if x is None else f"x={x:.3f}"))
        print(f"   → {verdict} — 가로 이동폭 {span:.3f}, {why}")
        if verdict != 'PASS':
            bad += 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
