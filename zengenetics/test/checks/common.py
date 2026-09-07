# -*- coding: utf-8 -*-
"""
공통 뼈대 — 결과 기록 · 거짓 통과(false pass) 방지 장치.

거짓 통과 방지의 핵심 규칙 (모든 검사가 지킨다):
  1) 셀렉터/패턴이 "0개 매칭"이면 그 자체가 FAIL 이다. 대상을 못 찾은 것을
     "문제 없음"으로 보고하지 않는다.
  2) baseline 에 있는 키를 검사가 한 번도 건드리지 않으면 FAIL(미실행)로 잡는다.
  3) 각 검사는 자신이 실제로 무엇을 몇 개 봤는지(probe) 결과에 남긴다.
"""
import json, os, re, subprocess, sys, time

ROOT   = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))   # zengenetics/test
PROJ   = os.path.dirname(ROOT)                                         # zengenetics
SKIN   = os.path.join(PROJ, 'cafe24-skin')
CACHE  = os.path.join(ROOT, 'cache')
OUT    = os.path.join(ROOT, '.out')
BUILD  = os.path.join(ROOT, 'build')

C_RED   = '\033[31m'; C_GRN = '\033[32m'; C_YEL = '\033[33m'
C_DIM   = '\033[2m';  C_BLD = '\033[1m'; C_OFF = '\033[0m'
if not sys.stdout.isatty() or os.environ.get('NO_COLOR'):
    C_RED = C_GRN = C_YEL = C_DIM = C_BLD = C_OFF = ''


class Suite(object):
    """한 분류(A~E)의 검사 결과 모음."""

    def __init__(self, code, title):
        self.code = code
        self.title = title
        self.rows = []            # (id, ok, what, expect, actual, note)
        self.t0 = time.time()
        self.elapsed = 0.0

    # --- 기록 ---------------------------------------------------------
    # status: PASS / FAIL / KNOWN
    #   KNOWN = 규칙상 틀렸지만 baseline 에 "이미 알려진 결함"으로 등재된 것.
    #           종료코드를 막지 않되 요약표에 반드시 노출된다. 0 이 되면 baseline 에서 뺀다.
    def add(self, cid, ok, what, expect, actual, note='', known=False):
        st = 'PASS' if ok else ('KNOWN' if known else 'FAIL')
        self.rows.append(dict(id=cid, ok=bool(ok), status=st, what=what,
                              expect=expect, actual=actual, note=note))
        return ok

    def eq(self, cid, what, expect, actual, note='', known=False):
        return self.add(cid, expect == actual, what, expect, actual, note, known)

    def truthy(self, cid, what, actual, note='', known=False):
        return self.add(cid, bool(actual), what, 'truthy', actual, note, known)

    def ge(self, cid, what, minimum, actual, note='', known=False):
        ok = isinstance(actual, (int, float)) and actual >= minimum
        return self.add(cid, ok, what, '>= %s' % minimum, actual, note, known)

    def le(self, cid, what, maximum, actual, note='', known=False):
        ok = isinstance(actual, (int, float)) and actual <= maximum
        return self.add(cid, ok, what, '<= %s' % maximum, actual, note, known)

    def near(self, cid, what, expect, actual, tol, note='', known=False):
        ok = isinstance(actual, (int, float)) and abs(actual - expect) <= tol
        return self.add(cid, ok, what, '%s +-%s' % (expect, tol), actual, note, known)

    def fail(self, cid, what, note=''):
        return self.add(cid, False, what, '-', 'ERROR', note)

    # --- 거짓 통과 방지 -----------------------------------------------
    def probe(self, cid, what, found, note=''):
        """대상을 실제로 찾았는지 확인하는 계측용 검사. found==0 이면 FAIL."""
        return self.add(cid, found > 0, u'[탐지] ' + what, '> 0', found,
                        note or u'0이면 검사가 대상을 못 찾은 것 = 거짓 통과 위험')

    # --- 집계 ---------------------------------------------------------
    def done(self):
        self.elapsed = time.time() - self.t0
        return self

    @property
    def n(self):    return len(self.rows)
    @property
    def nfail(self): return sum(1 for r in self.rows if r['status'] == 'FAIL')
    @property
    def nknown(self): return sum(1 for r in self.rows if r['status'] == 'KNOWN')
    @property
    def npass(self): return sum(1 for r in self.rows if r['status'] == 'PASS')
    @property
    def ok(self):   return self.nfail == 0


def sh(cmd, cwd=None, timeout=600):
    p = subprocess.run(cmd, shell=isinstance(cmd, str), cwd=cwd,
                       stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                       timeout=timeout)
    return p.returncode, p.stdout.decode('utf-8', 'replace')


def read(path):
    with open(path, 'rb') as f:
        return f.read().decode('utf-8', 'replace')


def md5(path):
    import hashlib
    h = hashlib.md5()
    with open(path, 'rb') as f:
        for b in iter(lambda: f.read(65536), b''):
            h.update(b)
    return h.hexdigest()


def load_baseline():
    with open(os.path.join(ROOT, 'baseline.json'), 'rb') as f:
        return json.loads(f.read().decode('utf-8'))


def save_baseline(data):
    with open(os.path.join(ROOT, 'baseline.json'), 'wb') as f:
        f.write(json.dumps(data, indent=2, ensure_ascii=False).encode('utf-8'))


def strip_comments(text, kind):
    """주석을 공백으로 치환해 길이/줄바꿈을 보존한다."""
    def blank(m):
        return re.sub(r'[^\n]', ' ', m.group(0))
    if kind == 'html':
        return re.sub(r'<!--.*?-->', blank, text, flags=re.S)
    # css / js
    text = re.sub(r'/\*.*?\*/', blank, text, flags=re.S)
    if kind == 'js':
        text = re.sub(r'(?m)//[^\n]*', blank, text)
    return text


def count(text, needle):
    return text.count(needle)


def node(script, *args, **kw):
    """node 로 스크립트 실행. stdout 마지막 JSON 줄을 파싱해 돌려준다."""
    cmd = ['node', script] + [str(a) for a in args]
    rc, out = sh(cmd, timeout=kw.get('timeout', 900))
    data = None
    for line in out.splitlines():
        line = line.strip()
        if line.startswith('__JSON__'):
            data = json.loads(line[len('__JSON__'):])
    return rc, out, data
