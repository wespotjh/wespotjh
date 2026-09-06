#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
젠제네틱스 site/*.html 에 인라인 편집 모드(_edit-mode.js)를 주입한다.
이도현 / 웹·모바일 개발팀 / 2026-09-06

  python3 _inject-edit-mode.py                 # 기본 5개 페이지 전부
  python3 _inject-edit-mode.py home.html       # 지정 파일만
  python3 _inject-edit-mode.py --dry           # 변경 없이 대상 수만 출력

동작
  1) 이전 주입 블록(<!--zg-edit-mode:start--> … :end-->)을 제거한다.
     이미 저장된 편집 데이터(#zg-edits JSON)는 보존해서 다시 넣는다.
  2) 기존 data-zg / data-zg-o 표식을 모두 제거하고 다시 부여한다.
  3) 직접 텍스트 노드를 가진 본문 요소에 data-zg="eNNN" (문서 순서) 을 부여한다.
  4) 원본 <script> 전부에 data-zg-o="1" 을 붙인다.
     (런타임이 주입한 스크립트를 스냅샷에서 걸러내기 위한 표식)
  5) </body> 직전(없으면 파일 끝)에 편집 데이터 블록 + 편집 스크립트를 넣는다.

재실행 가능(idempotent). HTML 은 속성 삽입 외에는 한 글자도 건드리지 않는다
(파서 재직렬화로 인한 마크업 변형을 피하기 위해 문자열 삽입 방식만 쓴다).
"""
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
SNIPPET = os.path.join(HERE, '_edit-mode.js')
DEFAULT_FILES = ['home.html', 'brand-story.html',
                 'product-potassium.html', 'product-vitaminb.html', 'product-magnesium.html']

VOID = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
        'meta', 'param', 'source', 'track', 'wbr'}
RAW = {'script', 'style', 'textarea', 'title'}
# 본문 텍스트로 취급할 태그
TARGET = {'h1', 'h2', 'h3', 'h4', 'h5', 'h6', 'p', 'li', 'span', 'a', 'button',
          'figcaption', 'div', 'td', 'th', 'strong', 'em', 'small', 'label', 'blockquote'}
# 이 안쪽은 아예 훑지 않는다
MEDIA = {'img', 'source', 'video', 'audio', 'iframe'}
SKIP_SUBTREE = {'script', 'style', 'noscript', 'svg', 'template', 'head'}

TAG_RE = re.compile(r'<(/?)([a-zA-Z][a-zA-Z0-9:-]*)', re.S)
START_MARK = '<!--zg-edit-mode:start-->'
# 주입 블록 제거용. 끝 표시 주석에 의존하지 않는다 —
# 브라우저는 인라인 스크립트 실행 시점에 그 뒤 마크업을 아직 파싱하지 않아,
# 스냅샷에는 스크립트 뒤의 주석이 담기지 않기 때문이다.
BLOCK_RE = re.compile(
    r'\n?(?:<!--zg-edit-mode:start-->\s*)?'
    r'<script\b[^>]*\bid="zg-edits"[^>]*>[\s\S]*?</script\s*>\s*'
    r'<script\b[^>]*\bid="zg-edit-mode"[^>]*>[\s\S]*?</script\s*>'
    r'\s*(?:<!--zg-edit-mode:end-->)?\n?')
EDITS_RE = re.compile(r'<script\b[^>]*\bid="zg-edits"[^>]*>([\s\S]*?)</script\s*>', re.I)
ATTR_CLEAN_RE = re.compile(r'\s+data-zg(?:-[oes])?="[^"]*"')


def scan(src):
    """아주 얇은 HTML 스캐너. (elements, script_open_positions) 반환.
    elements: dict(tag, open_start, open_end, text, kids, skipped)"""
    i, n = 0, len(src)
    stack, out, scripts = [], [], []
    skip_depth = 0
    while i < n:
        lt = src.find('<', i)
        if lt < 0:
            if stack:
                stack[-1]['text'] += src[i:]
            break
        if lt > i and stack:
            stack[-1]['text'] += src[i:lt]
        if src.startswith('<!--', lt):
            e = src.find('-->', lt + 4)
            i = (e + 3) if e >= 0 else n
            continue
        if src.startswith('<!', lt) or src.startswith('<?', lt):
            e = src.find('>', lt)
            i = (e + 1) if e >= 0 else n
            continue
        m = TAG_RE.match(src, lt)
        if not m:
            if stack:
                stack[-1]['text'] += '<'
            i = lt + 1
            continue
        closing = m.group(1) == '/'
        name = m.group(2).lower()
        j = m.end()
        selfclose = False
        while j < n:
            c = src[j]
            if c == '"' or c == "'":
                k = src.find(c, j + 1)
                j = (k + 1) if k >= 0 else n
                continue
            if c == '>':
                selfclose = src[j - 1] == '/'
                break
            j += 1
        open_end = j + 1
        if closing:
            for idx in range(len(stack) - 1, -1, -1):
                if stack[idx]['tag'] == name:
                    for rec in stack[idx:]:
                        out.append(rec)
                        if rec['tag'] in SKIP_SUBTREE:
                            skip_depth -= 1
                    del stack[idx:]
                    break
            i = open_end
            continue
        rec = {'tag': name, 'open_start': lt, 'open_end': open_end,
               'text': '', 'kids': [], 'skipped': skip_depth > 0}
        if stack:
            stack[-1]['kids'].append(name)
        if name == 'script':
            scripts.append((lt, len(name)))
        if name in VOID or selfclose:
            out.append(rec)
            i = open_end
            continue
        if name in RAW:
            ce = re.compile(r'</' + re.escape(name) + r'\s*>', re.I).search(src, open_end)
            out.append(rec)
            i = ce.end() if ce else n
            continue
        stack.append(rec)
        if name in SKIP_SUBTREE:
            skip_depth += 1
        i = open_end
    out.extend(stack)
    return out, scripts


def pick_targets(src):
    """편집 대상 요소 목록 (문서 순서)."""
    recs, scripts = scan(src)
    res = []
    for r in recs:
        if r['skipped'] or r['tag'] not in TARGET:
            continue
        t = r['text']
        if not t.strip():
            continue
        if not re.sub(r'&nbsp;|&#160;|&#xa0;|\s', '', t):
            continue
        res.append(r)
    res.sort(key=lambda r: r['open_start'])
    return res, scripts


def inject(path, js, dry=False):
    src = open(path, encoding='utf-8').read()
    before = len(src)

    # 1) 이전 주입분 제거 + 편집 데이터 보존
    keep = '[]'
    old = BLOCK_RE.search(src)
    if old:
        me = EDITS_RE.search(old.group(0))
        if me and me.group(1).strip():
            keep = me.group(1).strip()
        src = BLOCK_RE.sub('', src)
    # 2) 옛 표식 제거
    src = ATTR_CLEAN_RE.sub('', src)

    # 3) 대상 탐색
    targets, scripts = pick_targets(src)
    leaf = 0
    inserts = []
    for idx, r in enumerate(targets, 1):
        eid = 'e%03d' % idx
        pos = r['open_start'] + 1 + len(r['tag'])
        inserts.append((pos, ' data-zg="%s"' % eid))
        if not [k for k in r['kids'] if k != 'br']:
            leaf += 1
    # 4) 원본 script 표식
    for lt, ln in scripts:
        inserts.append((lt + 1 + ln, ' data-zg-o="1"'))

    # 5) 원본에서 비어 있는 컨테이너 표식
    #    (페이지 자체 스크립트가 나중에 채우는 자리 — 스냅샷에서 원상 복구한다)
    recs, _ = scan(src)
    empties = 0
    for r in recs:
        if r['skipped'] or r['tag'] in VOID or r['tag'] in RAW:
            continue
        if r['text'].strip() or r['kids']:
            continue
        inserts.append((r['open_start'] + 1 + len(r['tag']), ' data-zg-e="1"'))
        empties += 1

    # 6) 원본에 src 가 없는 미디어 태그 표식
    #    (스크립트가 base64 를 채워 넣는 자리 — 스냅샷에서 src 를 벗겨 용량 증가를 막는다)
    srcless = 0
    for r in recs:
        if r['skipped'] or r['tag'] not in MEDIA:
            continue
        if re.search(r'\ssrc\s*=', src[r['open_start']:r['open_end']]):
            continue
        inserts.append((r['open_start'] + 1 + len(r['tag']), ' data-zg-s="1"'))
        srcless += 1

    if dry:
        return before, before, len(targets), leaf, len(scripts), empties, srcless

    inserts.sort(key=lambda x: x[0], reverse=True)
    buf = src
    for pos, txt in inserts:
        buf = buf[:pos] + txt + buf[pos:]

    block = ('\n' + START_MARK + '\n'
             + '<script type="application/json" id="zg-edits">' + keep + '</script>\n'
             + '<script id="zg-edit-mode" data-zg-o="1">\n' + js + '\n</script>\n')

    cut = buf.rfind('</body>')
    if cut < 0:
        buf = buf.rstrip() + '\n' + block
    else:
        buf = buf[:cut] + block + buf[cut:]

    open(path, 'w', encoding='utf-8').write(buf)
    return before, len(buf), len(targets), leaf, len(scripts), empties, srcless


def main():
    args = [a for a in sys.argv[1:] if not a.startswith('--')]
    dry = '--dry' in sys.argv
    files = args or DEFAULT_FILES
    js = open(SNIPPET, encoding='utf-8').read()
    print('%-26s %10s %10s %8s %8s %6s %7s %6s %8s' %
          ('file', 'before', 'after', '+chars', 'targets', 'leaf', 'script', 'empty', 'srcless'))
    for f in files:
        p = f if os.path.isabs(f) else os.path.join(HERE, f)
        b, a, t, l, s, e, sl = inject(p, js, dry)
        print('%-26s %10d %10d %+8d %8d %6d %7d %6d %8d' %
              (os.path.basename(p), b, a, a - b, t, l, s, e, sl))


if __name__ == '__main__':
    main()
