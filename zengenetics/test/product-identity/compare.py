# -*- coding: utf-8 -*-
u"""제품 동일성 대조 시트 생성기 (대표님 지시 2026-09-10 · 4회 검수).

후보(정지 이미지 또는 영상)에서 프레임을 뽑아 **실물 누끼와 나란히** 붙인다.
판정은 사람이 눈으로 한다 — 이 스크립트는 판정하지 않는다.

  python3 compare.py --ref pot --out /tmp/sheet.png 후보1.png 후보2.mp4 ...
  python3 compare.py --ref pot --frames 5 --out /tmp/s.png 영상.mp4
"""
import argparse, os, subprocess, sys, tempfile
from PIL import Image, ImageDraw
Image.MAX_IMAGE_PIXELS = None

HERE = os.path.dirname(os.path.abspath(__file__))
REF_DIR = os.path.normpath(os.path.join(HERE, '..', '..', 'assets', 'product-ref', 'intro'))
REFS = {'pot': 'stick-pot.webp', 'vitb': 'stick-vitb.webp', 'mag': 'stick-mag.webp'}

FFMPEG = '/usr/local/lib/python3.11/dist-packages/imageio_ffmpeg/binaries/ffmpeg-linux-x86_64-v7.0.2'
VIDEO_EXT = ('.mp4', '.mov', '.webm', '.m4v')


def video_frames(path, n, tmpdir):
    u"""영상에서 균등 간격으로 n 장. 시작·중간·끝이 반드시 포함되도록 잡는다."""
    dur = None
    try:
        out = subprocess.run([FFMPEG, '-hide_banner', '-i', path],
                             capture_output=True, text=True).stderr
        for line in out.splitlines():
            if 'Duration:' in line:
                h, m, s = line.split('Duration:')[1].split(',')[0].strip().split(':')
                dur = int(h) * 3600 + int(m) * 60 + float(s)
                break
    except Exception:
        pass
    if not dur:
        dur = 5.0
    shots = []
    for i in range(n):
        t = dur * (i / max(1, n - 1)) * 0.96 + 0.05
        fp = os.path.join(tmpdir, 'f%02d.png' % i)
        subprocess.run([FFMPEG, '-v', 'error', '-ss', '%.3f' % t, '-i', path,
                        '-frames:v', '1', '-y', fp], capture_output=True)
        if os.path.exists(fp):
            shots.append((round(t, 2), Image.open(fp).convert('RGB')))
    return shots


def load_ref(key, h):
    p = os.path.join(REF_DIR, REFS[key])
    im = Image.open(p).convert('RGBA')
    bg = Image.new('RGBA', im.size, (247, 246, 242, 255))
    bg.alpha_composite(im)
    im = bg.convert('RGB')
    w = round(im.width * h / im.height)
    return im.resize((w, h), Image.LANCZOS)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument('--ref', default='pot', choices=list(REFS))
    ap.add_argument('--frames', type=int, default=3, help=u'영상에서 뽑을 프레임 수')
    ap.add_argument('--height', type=int, default=760)
    ap.add_argument('--out', required=True)
    ap.add_argument('inputs', nargs='+')
    a = ap.parse_args()

    H = a.height
    ref = load_ref(a.ref, H)
    tiles = [(u'실물 %s' % a.ref, ref)]

    tmpdir = tempfile.mkdtemp()
    for p in a.inputs:
        if not os.path.exists(p):
            print(u'없음:', p, file=sys.stderr); continue
        if p.lower().endswith(VIDEO_EXT):
            for t, im in video_frames(p, a.frames, tmpdir):
                w = round(im.width * H / im.height)
                tiles.append(('%s @%.1fs' % (os.path.basename(p)[:16], t), im.resize((w, H), Image.LANCZOS)))
        else:
            im = Image.open(p).convert('RGB')
            w = round(im.width * H / im.height)
            tiles.append((os.path.basename(p)[:22], im.resize((w, H), Image.LANCZOS)))

    pad, lab = 10, 22
    W = sum(t[1].width for t in tiles) + pad * (len(tiles) + 1)
    sheet = Image.new('RGB', (W, H + pad * 2 + lab), (255, 255, 255))
    d = ImageDraw.Draw(sheet)
    x = pad
    for i, (name, im) in enumerate(tiles):
        sheet.paste(im, (x, pad))
        d.text((x + 2, pad + H + 4), name, fill=(180, 0, 0) if i == 0 else (0, 0, 0))
        if i == 0:
            d.rectangle([x - 2, pad - 2, x + im.width + 1, pad + H + 1], outline=(200, 0, 0), width=2)
        x += im.width + pad
    sheet.save(a.out)
    print(a.out, sheet.size, u'— 왼쪽 빨간 테두리가 실물이다. 눈으로 4회 대조해라.')


if __name__ == '__main__':
    main()
