# -*- coding: utf-8 -*-
u"""회전 검수 — 라벨이 없는 컷용 (검수팀 지적 2026-09-11).

`orbit.py` 는 스틱의 네이비 인쇄를 추적한다. 스틱을 화면에서 뺀 컷에서는
추적 대상이 없어 **판정불가**가 된다. 잔은 회전대칭이라 실루엣도 안 변한다.

그래서 잔이 아니라 **조명**을 본다. 카메라가 궤도를 돌면
배경 그라디언트·캐스트 섀도·키라이트 하이라이트가 화면을 쓸고 지나간다.
상단 배경 띠의 가로 휘도 프로파일이 프레임마다 얼마나 옆으로 밀리는지 누적한다.

사용:
    python3 test/product-identity/orbit_bg.py <영상.mp4> [...]

판정: 누적 수평 이동폭 > 0.30 이면 회전함.
주의: 한 프레임에서 크게 튀는 건 컷 전환이지 회전이 아니다 — 단발 튐은 따로 보고한다.
"""
import os, sys, glob, shutil, subprocess
import numpy as np
from PIL import Image

FF = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
FPS = 4.0
CORR_MIN = 0.90     # 프로파일이 이만큼 닮았을 때만 이동으로 친다 (장면이 바뀌면 버린다)


def profile(path):
    u"""상단 배경 띠의 가로 휘도 프로파일."""
    a = np.asarray(Image.open(path).convert('L')).astype(np.float32)
    H, W = a.shape
    band = a[int(H * 0.04):int(H * 0.16), :].mean(0)
    return band - band.mean()


def shift(p0, p1, maxlag):
    u"""정규상관이 가장 큰 지연을 찾는다. 상관이 낮으면 None."""
    best, bl = -2.0, 0
    d0 = np.linalg.norm(p0)
    for lag in range(-maxlag, maxlag + 1):
        q = np.roll(p1, lag)
        d = d0 * np.linalg.norm(q)
        if d < 1e-6:
            continue
        c = float(np.dot(p0, q) / d)
        if c > best:
            best, bl = c, lag
    return (bl, best) if best >= CORR_MIN else (None, best)


def check(src, tmp):
    shutil.rmtree(tmp, ignore_errors=True); os.makedirs(tmp)
    subprocess.run([FF, '-v', 'error', '-i', src, '-vf', f'fps={FPS},scale=540:-1',
                    tmp + '/%04d.png', '-y'], capture_output=True)
    fs = sorted(glob.glob(tmp + '/*.png'))
    if len(fs) < 4:
        return 'JUDGE_FAIL', 0.0, 0.0, u'프레임이 모자라다'
    W = Image.open(fs[0]).size[0]
    ps = [profile(p) for p in fs]
    steps, pos = [], 0.0
    track = [0.0]
    for i in range(1, len(ps)):
        lag, _ = shift(ps[i - 1], ps[i], maxlag=int(W * 0.25))
        s = 0.0 if lag is None else lag / float(W)
        steps.append(abs(s))
        pos += s
        track.append(pos)
    span = max(track) - min(track)
    jump = max(steps) if steps else 0.0
    if span > 0.30:
        note = u'회전함'
        if jump > span * 0.6:
            return 'FAIL', span, jump, u'이동폭의 대부분이 한 프레임의 튐(%.3f) — 컷 전환이지 회전이 아니다' % jump
        return 'PASS', span, jump, note
    return 'FAIL', span, jump, u'회전 없음 — 고정 카메라'


def main(argv):
    if not argv:
        print(__doc__); return 2
    bad = 0
    for i, src in enumerate(argv):
        tmp = f'/tmp/orbitbg_{os.getpid()}_{i}'
        verdict, span, jump, why = check(src, tmp)
        shutil.rmtree(tmp, ignore_errors=True)
        print(f"{os.path.basename(src):24s} {verdict:10s} 누적 이동폭 {span:.3f} (최대 단발 {jump:.3f}) — {why}")
        if verdict != 'PASS':
            bad += 1
    return 1 if bad else 0


if __name__ == '__main__':
    sys.exit(main(sys.argv[1:]))
