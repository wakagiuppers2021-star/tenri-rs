"""算数 大問1（計算）の検算。式を Python の Fraction で、答えとは別に計算しなおし、答え・解説の終わりの数と比べる。"""
import re
from fractions import Fraction

from check_common import FAIL, eq, is_simplest, val
import tenri_rs_sansu1 as M1


def py_value(expr):
    """式を、Python の式に書きかえて計算する（tools/check_common.py の val とは、別の方法）。"""
    s = expr
    s = re.sub(r'<(\d+) (\d+)/(\d+)>', lambda m: f'(Fraction({m[1]})+Fraction({m[2]},{m[3]}))', s)
    s = re.sub(r'<(\d+)/(\d+)>', lambda m: f'Fraction({m[1]},{m[2]})', s)
    s = re.sub(r'(?<![\d.])(\d+\.\d+)', lambda m: f"Fraction('{m[1]}')", s)
    s = re.sub(r'(?<![\w.\'(])(\d+)(?![\w.\'])', lambda m: f'Fraction({m[1]})', s)
    s = s.replace('×', '*').replace('÷', '/').replace('＋', '+').replace('－', '-')
    return eval(s, {'Fraction': Fraction})


def ans_value(a):
    m = re.fullmatch(r'<(?:(\d+) )?(\d+)/(\d+)>', a)
    if m:
        return Fraction(int(m[1] or 0)) + Fraction(int(m[2]), int(m[3]))
    return Fraction(a)


def last_number(ex):
    """解説の、いちばん最後に出てくる数（帯分数・小数・整数）。（　）の中は、のぞく。"""
    t = re.sub(r'（[^）]*）', '', ex).rstrip('。 ')
    toks = re.findall(r'<(?:\d+ )?\d+/\d+>|\d+\.\d+|\d+', t)
    return toks[-1] if toks else None


def chains(ex):
    """解説の中の「A＝B＝C」の形（式は、数と＋－×÷と<分数>だけ）をぬき出す。"""
    return re.findall(r'(?<![\w.>])((?:[\d.＋－×÷()<>/ ]+＝)+[\d.＋－×÷()<>/ ]+?)(?=[。、（]|$)', ex)


seen = set()
bad = []
for i, st in enumerate(M1.SETS, 1):
    if len(st['qs']) != 8:
        bad.append((i, '問題数'))
    for j, q in enumerate(st['qs'], 1):
        e, a, ex = q['q'], q['ans'], q['ex']
        try:
            pv = py_value(e)
        except Exception as err:
            bad.append((i, j, '式を読めない', e, err))
            continue
        if pv != val(e):
            bad.append((i, j, '二通りの計算が一致しない', e))
        if pv != ans_value(a):
            bad.append((i, j, '答えが違う', e, a, pv))
        if not is_simplest(a):
            bad.append((i, j, '答えが約分されていない・仮分数', a))
        m = last_number(ex)
        if m is None:
            bad.append((i, j, '解説の最後に答えがない', ex))
        elif ans_value(m) != pv:
            bad.append((i, j, '解説の最後の数が、答えと違う', ex[-30:], pv))
        if j in (6, 7) and '<' not in a and pv.denominator != 1:
            bad.append((i, j, '分数の答えの形'))
        if j == 6 and pv.denominator == 1:
            bad.append((i, j, '(6)の答えが整数'))
        if e in seen:
            bad.append((i, j, '同じ式がほかのセットにもある', e))
        seen.add(e)
        # 解説の中の「A＝B＝C」の等式を、すべて値で確かめる
        for ch in chains(ex):
            vs = []
            for side in ch.split('＝'):
                try:
                    vs.append(py_value(side.strip()))
                except Exception:
                    vs.append(None)
            vs = [v for v in vs if v is not None]
            if len(set(vs)) > 1:
                bad.append((i, j, '解説の等式が成り立たない', ch, vs))
eq(f'算1 計算{len(M1.SETS)}セット×8問の答え・約分・解説の最後の数・途中の整数式・式の重複', bad, [])

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
