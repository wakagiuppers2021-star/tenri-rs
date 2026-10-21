"""検算の共通部品。tools/check_tenri_rs.py と、tools/check_sansu*.py（大問ごとの検算）が使う。

check_sansu<N>.py は、import されると、そのまま検算を走らせ、不一致を FAIL にためる（check_tenri_rs.py の最後に、まとめて数える）。
書き方の例（tools/check_sansu1.py）:
    from check_common import eq, ans, q_text, val
    import tenri_rs_sansu1 as M
    eq('算1-1(1)', val(ans(M, 1, 1)), val(M.SETS[0]['qs'][0]['meta']['expr']))
"""
from __future__ import annotations

import re
from fractions import Fraction

FAIL = []


def ans(mod, s, q):
    return mod.SETS[s - 1]['qs'][q - 1]['ans']


def eq(label, got, want):
    ok = got == want
    print(('OK ' if ok else 'NG ') + label, '|', got, '|', want)
    if not ok:
        FAIL.append(label)


def join(xs):
    return '・'.join(xs)


def choices(s):
    """問題文の「ア 〜　イ 〜」から {記号: 中身} を読み取る。"""
    return {m[0]: m[1] for m in re.findall(r'(?:^|\n|　)([アイウエオカキクケコ]) ([^\n　]+)', s)}


def q_text(mod, s, q):
    return mod.SETS[s - 1]['qs'][q - 1]['q']


def num(x):
    """小数第1位までの数を、答えの書き方（20.0→20、7.9→7.9）にそろえる。"""
    x = round(x, 1)
    return str(int(x)) if x == int(x) else str(x)


# ---------- 式の計算（分数・小数・かっこ） ----------
_TOK = re.compile(r'\s*(<(?:\d+ )?\d+/\d+>|\d+\.\d+|\d+|[＋+－−\-×*÷/＝=()（）])')


def _tokens(s):
    s = s.strip()
    out, pos = [], 0
    while pos < len(s):
        m = _TOK.match(s, pos)
        if not m:
            raise ValueError(f'式を読めない: {s!r} の {pos} 文字め')
        out.append(m.group(1))
        pos = m.end()
    return out


def _atom(tok):
    if tok.startswith('<'):
        m = re.fullmatch(r'<(?:(\d+) )?(\d+)/(\d+)>', tok)
        w = int(m.group(1) or 0)
        return Fraction(w) + Fraction(int(m.group(2)), int(m.group(3)))
    return Fraction(tok)


def val(expr):
    """式（<1/2>・<5 3/4> の分数、小数、＋－×÷、かっこ）の値を、Fraction で返す。「＝」より後ろは、読まない。"""
    toks = _tokens(expr)
    if '＝' in toks or '=' in toks:
        toks = toks[:toks.index('＝' if '＝' in toks else '=')]
    pos = [0]

    def peek():
        return toks[pos[0]] if pos[0] < len(toks) else None

    def take():
        pos[0] += 1
        return toks[pos[0] - 1]

    def expr_():
        v = term()
        while peek() in ('＋', '+', '－', '−', '-'):
            op = take()
            r = term()
            v = v + r if op in ('＋', '+') else v - r
        return v

    def term():
        v = factor()
        while peek() in ('×', '*', '÷', '/'):
            op = take()
            r = factor()
            v = v * r if op in ('×', '*') else v / r
        return v

    def factor():
        t = take()
        if t in ('(', '（'):
            v = expr_()
            assert take() in (')', '）')
            return v
        return _atom(t)
    v = expr_()
    assert pos[0] == len(toks), f'式の読み残し: {expr!r}'
    return v


def is_simplest(ans_s):
    """答えが分数のとき、約分されていて、仮分数でないか。分数でなければ True。"""
    m = re.fullmatch(r'<(?:(\d+) )?(\d+)/(\d+)>', ans_s.strip())
    if not m:
        return True
    from math import gcd
    n, d = int(m.group(2)), int(m.group(3))
    return gcd(n, d) == 1 and n < d
