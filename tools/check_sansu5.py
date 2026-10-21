"""算数 大問5 の検算。答え・図の数値・問題文の数値を、データ（tenri_rs_sansu5.py）の解説とは別の方法で計算しなおして、照合する。

- 図形（第02・04・05・06・08・10セット）：図の座標（cm）から、斜線部分の面積を「横の線ごとに区間を足したり引いたりして」数え直す（本物の円周率）。
  公式による値（円周率3.14）と、答えの文字列が一致することも確かめる。図の中の長さの文字と、座標から求めた長さが一致することも確かめる。
- 数・割合（第01・03セット）：Fraction・総あたり。仕事算（第07セット）：Fraction・総あたり。カード（第09セット）：総あたり。
- 円の転がり（第10セット）：ふれる点が止まる（すべらない）条件を、数値で確かめながら、点Pの位置を求めなおす。
import しただけで検算が走る（tools/check_tenri_rs.py が import する）。
"""
import itertools
import math
import re
from fractions import Fraction

from check_common import FAIL, eq, ans, q_text
import tenri_rs_sansu5 as M5

PI3 = Fraction('3.14')
SETS = M5.SETS


def S(i):
    return SETS[i - 1]


def panels(i):
    return S(i)['fig']['args']['panels']


def anum(s, q):
    """答えの文字列の、先頭の数。"""
    return Fraction(re.match(r'\d+(?:\.\d+)?', ans(M5, s, q)).group())


def fmt(v, unit=''):
    """Fraction（小数第2位まで）を、答えの書き方（112、56.52、25.5）にする。"""
    f = Fraction(v)
    r = round(f, 2)
    assert r == f, ('小数第2位より先がある', f)
    s = f'{float(r):g}'
    return s + unit


def cm_numbers(text):
    return sorted(float(x) for x in re.findall(r'(\d+(?:\.\d+)?)cm', text))


# ---------------- 図形の数え直し（横の線ごとの区間） ----------------
def _merge(iv):
    iv = sorted((a, b) for a, b in iv if b - a > 1e-12)
    out = []
    for a, b in iv:
        if out and a <= out[-1][1] + 1e-12:
            out[-1] = (out[-1][0], max(out[-1][1], b))
        else:
            out.append((a, b))
    return out


def _intersect(a, b):
    out, i, j = [], 0, 0
    while i < len(a) and j < len(b):
        lo, hi = max(a[i][0], b[j][0]), min(a[i][1], b[j][1])
        if hi - lo > 1e-12:
            out.append((lo, hi))
        if a[i][1] < b[j][1]:
            i += 1
        else:
            j += 1
    return out


def _subtract(a, b):
    out = []
    for lo, hi in a:
        cur = lo
        for blo, bhi in b:
            if bhi <= cur or blo >= hi:
                continue
            if blo > cur:
                out.append((cur, blo))
            cur = max(cur, bhi)
            if cur >= hi:
                break
        if cur < hi:
            out.append((cur, hi))
    return out


def row_iv(sh, y):
    """図形 sh（poly・circle・sector）の、高さ y の横線の上の、中にある区間。"""
    k = sh[0]
    if k == 'poly':
        pts = sh[1]
        xs = []
        for i in range(len(pts)):
            (x1, y1), (x2, y2) = pts[i], pts[(i + 1) % len(pts)]
            if (y1 <= y < y2) or (y2 <= y < y1):
                xs.append(x1 + (y - y1) * (x2 - x1) / (y2 - y1))
        xs.sort()
        return [(xs[i], xs[i + 1]) for i in range(0, len(xs) - 1, 2)]
    if k == 'circle':
        (cx, cy), r = sh[1], sh[2]
        d = r * r - (y - cy) ** 2
        return [] if d <= 0 else [(cx - math.sqrt(d), cx + math.sqrt(d))]
    if k == 'sector':
        (cx, cy), r, a0, a1 = sh[1], sh[2], sh[3], sh[4]
        iv = row_iv(('circle', (cx, cy), r), y)
        assert 0 < a1 - a0 <= 180 + 1e-9, 'おうぎ形は、中心角180度以下'
        u0, u1 = (math.cos(math.radians(a0)), math.sin(math.radians(a0))), (math.cos(math.radians(a1)), math.sin(math.radians(a1)))
        py = y - cy
        for a, b in ((-u0[1], u0[0]), (u1[1], -u1[0])):           # a*px + b*py >= 0
            if abs(a) < 1e-12:
                if b * py < -1e-12:
                    return []
                continue
            bound = cx - b * py / a
            iv = _intersect(iv, [(bound, 1e9)] if a > 0 else [(-1e9, bound)])
        return iv
    raise ValueError(k)


def hatched_rows(prims, y):
    cur = []
    for pr in prims:
        k = pr[0]
        o = pr[-1] if isinstance(pr[-1], dict) else {}
        f = o.get('fill')
        if k in ('poly', 'circle', 'sector') and f in ('hatch', 'white', 'gray', 'black'):
            iv = row_iv(pr, y)
            cur = _merge(cur + iv) if f == 'hatch' else _subtract(cur, iv)
        elif k == 'and' and o.get('fill', 'hatch') == 'hatch':
            cur = _merge(cur + _intersect(row_iv(pr[1][0], y), row_iv(pr[1][1], y)))
    return cur


def shape_y_range(sh):
    if sh[0] == 'poly':
        ys = [p[1] for p in sh[1]]
        return min(ys), max(ys)
    return sh[1][1] - sh[2], sh[1][1] + sh[2]


def hatched_area(prims, n=6000):
    """斜線部分の面積（本物の円周率）。"""
    shapes = [pr for pr in prims if pr[0] in ('poly', 'circle', 'sector') and (pr[-1] if isinstance(pr[-1], dict) else {}).get('fill') == 'hatch']
    shapes += [sh for pr in prims if pr[0] == 'and' for sh in pr[1]]
    lo, hi = min(shape_y_range(s)[0] for s in shapes), max(shape_y_range(s)[1] for s in shapes)
    dy = (hi - lo) / n
    tot = 0.0
    for j in range(n):
        tot += sum(b - a for a, b in hatched_rows(prims, lo + (j + .5) * dy)) * dy
    return tot


def shoelace(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def labels_ok(prims):
    """寸法（dim）の文字の長さが、座標から求めた長さと一致するか。"""
    bad = []
    for pr in prims:
        if pr[0] == 'dim':
            lab = float(pr[3].replace('cm', ''))
            if abs(lab - dist(pr[1], pr[2])) > 1e-6:
                bad.append((pr[3], dist(pr[1], pr[2])))
    return bad


def near(a, b, tol):
    return abs(a - b) <= tol


def check_area(label, got_str, formula_true, formula_314, area_true):
    """答えの文字列・公式（円周率3.14）・図の座標から数え直した面積（本物の円周率）を、照合する。"""
    eq(f'{label} 答え', got_str, fmt(formula_314, 'cm²'))
    ok = abs(area_true - formula_true) < max(.01, formula_true * 3e-4)
    eq(f'{label} 図の座標から数えた面積（{area_true:.3f}）と公式（{formula_true:.3f}）', ok, True)


def solid_cm(text):
    return cm_numbers(text)


# ====================================================================== 第01セット：平均と中央値
t1 = S(1)['table']['rows']
vals1 = [int(x) for x in t1[1][1:]]
assert t1[0][1:] == [str(i) for i in range(1, 10)] and len(vals1) == 9 and '9人' in S(1)['lead']
tot1 = sum(vals1)
eq('算5-1(1) 平均', ans(M5, 1, 1), f'{Fraction(tot1, 9)}m')
srt1 = sorted(vals1)
eq('算5-1(2) 中央値（9人）', ans(M5, 1, 2), f'{srt1[4]}m')
assert srt1[4] != Fraction(tot1, 9)                               # 平均と中央値が、ちがう値になる
d1 = Fraction(re.search(r'(\d+\.\d+)m大きく', q_text(M5, 1, 3)).group(1))
cand1 = [x for x in range(0, 200) if Fraction(tot1 + x, 10) == Fraction(tot1, 9) + d1]       # Aさんの記録を、総あたりで探す
assert len(cand1) == 1
eq('算5-1(3) Aさんの記録', ans(M5, 1, 3), f'{cand1[0]}m')
srt10 = sorted(vals1 + [cand1[0]])
med10 = Fraction(srt10[4] + srt10[5], 2)
eq('算5-1(4) 中央値（10人）', ans(M5, 1, 4), f'{float(med10):g}m')
assert srt10[4] != srt10[5]

# ====================================================================== 第02セット：斜線部分の面積（長方形・円・正方形）
p2 = panels(2)
for pn in p2:
    eq(f'算5-2 図の寸法の文字 {pn["cap"]}', labels_ok(pn['prims']), [])
# (1) 長方形から、ななめの帯
rect2, band2 = p2[0]['prims'][0][1], p2[0]['prims'][1][1]
assert rect2 == [(0, 0), (16, 0), (16, 10), (0, 10)]
left_w = band2[1][1] - band2[0][1]
right_w = band2[2][1] - band2[3][1]
assert band2[0][0] == band2[1][0] == 0 and band2[2][0] == band2[3][0] == 16 and left_w == right_w == 3     # 左右のはしの長さが、どちらも3cm
slope1 = (band2[3][1] - band2[0][1]) / 16
slope2 = (band2[2][1] - band2[1][1]) / 16
assert abs(slope1 - slope2) < 1e-12                                                                      # 帯の2本の線が平行
assert cm_numbers(q_text(M5, 2, 1)) == sorted([10, 16, 3, 3])
ar21 = hatched_area(p2[0]['prims'])
check_area('算5-2(1) 長方形から帯', ans(M5, 2, 1), 16 * 10 - 3 * 16, Fraction(16 * 10 - 3 * 16), ar21)
# (2) 円の中の2つの円
c2 = [pr for pr in p2[1]['prims'] if pr[0] == 'circle']
R2, (ra, rb) = c2[0][2], (c2[1][2], c2[2][2])
assert sorted(cm_numbers(q_text(M5, 2, 2))) == sorted([2 * R2, 2 * ra, 2 * rb])
assert dist(c2[1][1], c2[2][1]) == ra + rb and dist(c2[0][1], c2[1][1]) + ra == R2 and dist(c2[0][1], c2[2][1]) + rb == R2     # ぴったり入っている
ar22 = hatched_area(p2[1]['prims'])
check_area('算5-2(2) 円の中の2つの円', ans(M5, 2, 2), math.pi * (R2 ** 2 - ra ** 2 - rb ** 2), PI3 * (R2 ** 2 - ra ** 2 - rb ** 2), ar22)
# (3) 正方形3つ
sq, dia, inn = p2[2]['prims'][0][1], p2[2]['prims'][1][1], p2[2]['prims'][2][1]
mid = lambda a, b: ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2)
assert sorted(dia) == sorted(mid(sq[i], sq[(i + 1) % 4]) for i in range(4))                              # ひし形は、各辺のまん中の点を結んだもの
assert sorted(inn) == sorted(mid(dia[i], dia[(i + 1) % 4]) for i in range(4))                            # 小さい正方形は、ひし形の各辺のまん中の点を結んだもの
assert cm_numbers(q_text(M5, 2, 3)) == [12]
ar23 = hatched_area(p2[2]['prims'])
check_area('算5-2(3) 正方形3つ', ans(M5, 2, 3), (shoelace(sq) - shoelace(dia)) + shoelace(inn), Fraction(int(shoelace(sq) - shoelace(dia) + shoelace(inn))), ar23)

# ====================================================================== 第03セット：売買損益
lead3 = S(3)['lead']
price3, off3, yen3, prof3 = (int(re.search(p, lead3).group(1)) for p in (r'定価(\d+)円', r'定価の(\d)割引き', r'さらに(\d+)円値下げ', r'仕入れ値の(\d)割の利益'))
sell3 = Fraction(price3) * (1 - Fraction(off3, 10)) - yen3
eq('算5-3(1) 売り値', ans(M5, 3, 1), f'{sell3}円')
cost3 = [c for c in range(1, 100000) if Fraction(c) * (1 + Fraction(prof3, 10)) == sell3]                 # 仕入れ値を、総あたりで探す
assert len(cost3) == 1
eq('算5-3(2) 仕入れ値', ans(M5, 3, 2), f'{cost3[0]}円')
eq('算5-3(3) 定価の利益の見こみ', ans(M5, 3, 3), f'{Fraction(price3 - cost3[0], cost3[0]) * 100}%')
q34 = q_text(M5, 3, 4)
mk4, dc4, pf4 = (int(re.search(p, q34).group(1)) for p in (r'(\d)割の利益を見こんで', r'定価の(\d)割', r'利益は(\d+)円'))
dc4 = Fraction(dc4, 10) + Fraction(int(re.search(r'割(\d)分引き', q34).group(1)), 100)
cost4 = [c for c in range(1, 200000) if Fraction(c) * (1 + Fraction(mk4, 10)) * (1 - dc4) - c == pf4]       # 定価＝仕入れ値×(1＋利益の割合)、売り値＝定価×(1－割引き)
assert len(cost4) == 1
eq('算5-3(4) 別の品物の仕入れ値', ans(M5, 3, 4), f'{cost4[0]}円')

# ====================================================================== 第04セット：斜線部分の面積（方眼・半円・長方形）
p4 = panels(4)
for pn in p4:
    eq(f'算5-4 図の寸法の文字 {pn["cap"]}', labels_ok(pn['prims']), [])
# (1) 方眼の三角形：格子点の数え上げ（ピックの定理）と、座標の公式
tri4 = p4[0]['prims'][1][1]
assert all(float(x).is_integer() and float(y).is_integer() for x, y in tri4)
gx0, gy0, gx1, gy1 = *p4[0]['prims'][0][1], *p4[0]['prims'][0][2]
assert all(gx0 <= x <= gx1 and gy0 <= y <= gy1 for x, y in tri4)


def lattice_counts(tri):
    """三角形の、ふちの上の格子点の数Bと、中の格子点の数I。"""
    B = sum(math.gcd(abs(tri[i][0] - tri[(i + 1) % 3][0]), abs(tri[i][1] - tri[(i + 1) % 3][1])) for i in range(3))
    I = 0
    for x in range(gx0, gx1 + 1):
        for y in range(gy0, gy1 + 1):
            cr = [(tri[(i + 1) % 3][0] - tri[i][0]) * (y - tri[i][1]) - (tri[(i + 1) % 3][1] - tri[i][1]) * (x - tri[i][0]) for i in range(3)]
            if all(c > 0 for c in cr) or all(c < 0 for c in cr):
                I += 1
    return B, I


B4, I4 = lattice_counts([(int(x), int(y)) for x, y in tri4])
eq('算5-4(1) 方眼の三角形（ピックの定理 I＋B÷2－1）', ans(M5, 4, 1), fmt(Fraction(I4) + Fraction(B4, 2) - 1, 'cm²'))
assert abs(hatched_area(p4[0]['prims']) - shoelace(tri4)) < 1e-3
assert 'cm' in q_text(M5, 4, 1)
# (2) 半円の帯2つ
pr42 = p4[1]['prims']
secs = [pr for pr in pr42 if pr[0] == 'sector']
Rr = sorted({s_[2] for s_ in secs})
assert Rr == [2, 6] and secs[0][1] == (0, 0) and secs[2][1] == (8, 0)
assert (secs[0][1][0] + Rr[0], secs[0][1][0] + Rr[1]) == (2, 6) and (secs[2][1][0] - Rr[1], secs[2][1][0] - Rr[0]) == (2, 6)     # 上の帯の右はしと、下の帯の左はしが、ぴったりつながる
assert cm_numbers(q_text(M5, 4, 2)) == [2, 6]
check_area('算5-4(2) 半円の帯', ans(M5, 4, 2), math.pi * (6 ** 2 - 2 ** 2), PI3 * (6 ** 2 - 2 ** 2), hatched_area(pr42))
# (3) 長方形の中の三角形
pr43 = p4[2]['prims']
rc, tri43 = pr43[0][1], pr43[1][1]
Aa, Ee, Ff = tri43
assert rc == [(0, 0), (12, 0), (12, 9), (0, 9)] and Aa == (0, 9) and Ee[1] == 0 and Ff[0] == 12
BE, CF = Ee[0] - 0, Ff[1] - 0
assert cm_numbers(q_text(M5, 4, 3)) == sorted([BE, CF]) and (BE, CF) == (8, 6)
corner = shoelace([(0, 9), (0, 0), Ee]) + shoelace([Ee, (12, 0), Ff]) + shoelace([Aa, Ff, (12, 9)])
eq('算5-4(3) 三角形AEF（長方形－3つの直角三角形）', ans(M5, 4, 3), fmt(Fraction(12 * 9) - Fraction(int(corner)), 'cm²'))
assert abs(hatched_area(pr43) - shoelace(tri43)) < 1e-3 and abs(hatched_area(pr43) - 42) < 1e-3

# ====================================================================== 第05セット：立体の体積
sol = S(5)['fig']['args']['solids']
ptsz = lambda s_: s_['pts']


def sec_area(pts, n=4000):
    """正面の多角形の面積を、横の線で数える。"""
    ys = [p[1] for p in pts]
    lo, hi = min(ys), max(ys)
    dy = (hi - lo) / n
    return sum(sum(b - a for a, b in row_iv(('poly', pts), lo + (j + .5) * dy)) * dy for j in range(n))


for k, s_ in enumerate(sol, 1):
    if s_['kind'] == 'prism':
        for (q1, q2, lab, *_r) in s_['dims']:
            d3 = math.dist(q1, q2)
            assert abs(float(lab.replace('cm', '')) - d3) < 1e-9, (k, lab, d3)
# (1) 三角柱
w1, h1, d1_ = 9, 4, 6
assert ptsz(sol[0]) == [(0, 0), (w1, 0), (0, h1)] and sol[0]['d'] == d1_
assert cm_numbers(q_text(M5, 5, 1)) == sorted([w1, h1, d1_])
vol1 = sec_area(ptsz(sol[0])) * d1_
assert abs(vol1 - shoelace(ptsz(sol[0])) * d1_) < 1e-3
eq('算5-5(1) 三角柱', ans(M5, 5, 1), fmt(Fraction(round(vol1)), 'cm³'))
# (2) くりぬいた円柱（底面を、横の線で数える）
pp = sol[1]
assert (pp['Dlabel'], pp['dlabel'], pp['hlabel']) == (f'{2 * pp["R"]}cm', f'{2 * pp["r"]}cm', f'{pp["h"]}cm')
assert cm_numbers(q_text(M5, 5, 2)) == sorted([2 * pp['R'], 2 * pp['r'], pp['h']])
ring = lambda pi_: pi_ * (pp['R'] ** 2 - pp['r'] ** 2)
base2 = sum(sum(b - a for a, b in _subtract(row_iv(('circle', (0, 0), pp['R']), -pp['R'] + (j + .5) * 2 * pp['R'] / 6000), row_iv(('circle', (0, 0), pp['r']), -pp['R'] + (j + .5) * 2 * pp['R'] / 6000))) * 2 * pp['R'] / 6000 for j in range(6000))
assert abs(base2 - math.pi * (pp['R'] ** 2 - pp['r'] ** 2)) < 1e-3
eq('算5-5(2) くりぬいた円柱（体積）', ans(M5, 5, 2), fmt(ring(PI3) * pp['h'], 'cm³'))
assert abs(base2 * pp['h'] - math.pi * (pp['R'] ** 2 - pp['r'] ** 2) * pp['h']) < .05
# (3) 直方体の角を切りとった立体（正面の五角形×おくゆき）
pn3 = sol[2]
pt3, d3_ = ptsz(pn3), pn3['d']
assert cm_numbers(q_text(M5, 5, 3)) == sorted([6, 8, d3_, 4, 3]) and shoelace(pt3) == 8 * 6 - 4 * 3 / 2
assert pt3 == [(0, 0), (8, 0), (8, 3), (4, 6), (0, 6)]                       # 横8cm・たて6cm。右上の角を、横に4cm・たてに3cm切りとった形
vol3 = sec_area(pt3) * d3_
eq('算5-5(3) 角を切りとった直方体', ans(M5, 5, 3), fmt(Fraction(round(vol3)), 'cm³'))
# (4) 表面積：底面（上下）＋外がわの側面＋穴のかべ（円周は、正3600角形の周で近似）
n_ = 3600
circ = lambda r: n_ * 2 * r * math.sin(math.pi / n_)
surf = 2 * base2 + circ(pp['R']) * pp['h'] + circ(pp['r']) * pp['h']
eq('算5-5(4) 表面積', ans(M5, 5, 4), fmt(2 * ring(PI3) + PI3 * 2 * pp['R'] * pp['h'] + PI3 * 2 * pp['r'] * pp['h'], 'cm²'))
assert abs(surf - (2 * math.pi * (pp['R'] ** 2 - pp['r'] ** 2) + 2 * math.pi * (pp['R'] + pp['r']) * pp['h'])) < .05

# ====================================================================== 第06セット：斜線部分の面積（同心円・半円・トラック）
p6 = panels(6)
for pn in p6:
    eq(f'算5-6 図の寸法の文字 {pn["cap"]}', labels_ok(pn['prims']), [])
# (1) 同心円を4等分
pr61 = p6[0]['prims']
rs = sorted({pr[2] for pr in pr61 if pr[0] == 'circle'})
assert rs == [4, 7] and cm_numbers(q_text(M5, 6, 1)) == [4, 7]
lbs = {pr[2]: pr[1] for pr in pr61 if pr[0] == 'lbl'}
assert set(lbs) == {'4cm', '3cm'} and 4 == rs[0] and 3 == rs[1] - rs[0] and rs[0] > -lbs['4cm'][0] > 0 and rs[0] < lbs['3cm'][0] < rs[1]       # 文字が、内がわの半径・輪のはばの位置にある
# 斜線は、外がわの輪のI・IIIと、内がわの円のII・IV
check_area('算5-6(1) 同心円', ans(M5, 6, 1), math.pi * 7 ** 2 / 2, PI3 * 7 ** 2 / 2, hatched_area(pr61))
alt = (math.pi * (7 ** 2 - 4 ** 2) / 4) * 2 + (math.pi * 4 ** 2 / 4) * 2
assert abs(hatched_area(pr61) - alt) < .01                                                            # 輪の4分の1が2つ＋円の4分の1が2つ
# (2) 4つの半円（花びら）
pr62 = p6[1]['prims']
assert cm_numbers(q_text(M5, 6, 2)) == [12]
ar62 = hatched_area(pr62)
check_area('算5-6(2) 花びら', ans(M5, 6, 2), 4 * (math.pi * 6 ** 2 / 2) - 12 * 12, 4 * (PI3 * 6 ** 2 / 2) - 12 * 12, ar62)


def cover_count(x, y):
    """正方形の中の点が、4つの半円のうち、いくつにふくまれるか。"""
    return sum(1 for sh in [('sector', (6, 0), 6, 0, 180), ('sector', (0, 6), 6, -90, 90), ('sector', (6, 12), 6, 180, 360), ('sector', (12, 6), 6, 90, 270)]
               if any(a <= x <= b for a, b in row_iv(sh, y)))


cnt = [0, 0, 0, 0, 0]
for i_ in range(120):
    for j_ in range(120):
        cnt[cover_count((i_ + .5) * .1, (j_ + .5) * .1)] += 1
assert cnt[0] == 0 and cnt[3] == 0 and cnt[4] == 0 and cnt[1] + cnt[2] == 120 * 120                    # 正方形は、4つの半円でおおわれ、3つ以上が重なる点はない（だから、合計－正方形＝重なり）
assert abs(cnt[2] * .01 - ar62) < .3
# (3) 三日月
pr63 = p6[2]['prims']
tri63 = [pr for pr in pr63 if pr[0] == 'poly' and not pr[-1]][0][1]
Ap, Bp, Cp = (0, 6), (8, 0), (0, 0)
assert tri63 == [Cp, Bp, Ap] and cm_numbers(q_text(M5, 6, 3)) == [6, 8, 10]
assert abs(dist(Ap, Cp) ** 2 + dist(Cp, Bp) ** 2 - dist(Ap, Bp) ** 2) < 1e-9
secs63 = [pr for pr in pr63 if pr[0] == 'sector']
assert [round(s_[2]) for s_ in secs63] == [4, 3, 5] and secs63[0][1] == (4, 0) and secs63[1][1] == (0, 3) and secs63[2][1] == (4, 3)      # 3つの辺を直径とする半円
semi = lambda r, pi_: pi_ * r * r / 2
eq('算5-6(3) 三日月', ans(M5, 6, 3), fmt(semi(3, PI3) + semi(4, PI3) + Fraction(6 * 8, 2) - semi(5, PI3), 'cm²'))
ar63 = hatched_area(pr63)
assert abs(ar63 - 24) < 5e-3 and abs(ar63 - (semi(3, math.pi) + semi(4, math.pi) + 24 - semi(5, math.pi))) < 5e-3
# (4) トラックの道
pr64 = p6[3]['prims']
assert cm_numbers(q_text(M5, 6, 4)) == [2, 8, 12]
ar64 = hatched_area(pr64)
outer = 12 * 8 + math.pi * 4 ** 2
inner = 12 * 4 + math.pi * 2 ** 2
check_area('算5-6(4) トラックの道', ans(M5, 6, 4), outer - inner, (12 * 8 + PI3 * 16) - (12 * 4 + PI3 * 4), ar64)
assert abs(ar64 - (2 * 12 * 2 + math.pi * (4 ** 2 - 2 ** 2))) < 5e-3                                 # まっすぐな部分2つ＋輪

# ====================================================================== 第07セット：仕事算
lead7 = S(7)['lead']
tA, tB = (int(x) for x in re.findall(r'(\d+)分', lead7))
rA, rB = Fraction(1, tA), Fraction(1, tB)
eq('算5-7(1) 2台で', ans(M5, 7, 1), f'{1 / (rA + rB)}分')
t72 = int(re.search(r'2台で(\d+)分間', q_text(M5, 7, 2)).group(1))
# 時刻を1分ずつ進めて、仕事の量が1になる時刻を探す（Aだけに変えたあと）
done, t = Fraction(0), 0
while done < 1:
    done += (rA + rB) if t < t72 else rA
    t += 1
eq('算5-7(2) 途中からAだけ', ans(M5, 7, 2), f'{t}分')
tot73 = int(re.search(r'全部で(\d+)分', q_text(M5, 7, 3)).group(1))
sol73 = [x for x in range(0, tot73 + 1) if x * (rA + rB) + (tot73 - x) * rB == 1]                    # 2台でx分、そのあとBだけで、のこり
assert len(sol73) == 1
eq('算5-7(3) Bだけの時間', ans(M5, 7, 3), f'{tot73 - sol73[0]}分間')
b74 = int(re.search(r'Bだけで(\d+)分間', q_text(M5, 7, 4)).group(1))
sol74 = [y for y in range(0, 200) if b74 * rB + y * (rA + rB) == 1]
assert len(sol74) == 1
eq('算5-7(4) 2台の時間', ans(M5, 7, 4), f'{sol74[0]}分間')

# ====================================================================== 第08セット：正三角形と正方形
pr8 = panels(8)[0]['prims']
tri8 = [pr for pr in pr8 if pr[0] == 'poly' and pr[-1].get('fill') == 'hatch'][0][1]
sqp = [pr for pr in pr8 if pr[0] == 'poly' and not pr[-1].get('fill')][0][1]
Bp8, Cp8, Ep8 = tri8
Ap8, Dp8 = sqp[0], sqp[3]
assert (Bp8, Cp8) == ((0, 0), (12, 0)) and sqp == [(0, 12), (0, 0), (12, 0), (12, 12)] and cm_numbers(S(8)['lead']) == [12]
assert abs(dist(Cp8, Dp8) - dist(Cp8, Ep8)) < 1e-9 and abs(dist(Cp8, Dp8) - dist(Dp8, Ep8)) < 1e-9       # 三角形CDEは正三角形（辺が12cm）
assert Ep8[0] > Cp8[0]                                                                                   # Eは、正方形の外がわ


def angle(v, p, q):
    """頂点 v での、半直線 vp と vq のつくる角（度）。"""
    a1, a2 = math.atan2(p[1] - v[1], p[0] - v[0]), math.atan2(q[1] - v[1], q[0] - v[0])
    d = abs(math.degrees(a1 - a2)) % 360
    return min(d, 360 - d)


eq('算5-8(1) 角BCE', ans(M5, 8, 1), f'{round(angle(Cp8, Bp8, Ep8), 6):g}度')
eq('算5-8(2) 角CBE', ans(M5, 8, 2), f'{round(angle(Bp8, Cp8, Ep8), 6):g}度')
eq('算5-8(3) 角AEB', ans(M5, 8, 3), f'{round(angle(Ep8, Ap8, Bp8), 6):g}度')
eq('算5-8(4) 三角形BCEの面積', ans(M5, 8, 4), f'{round(shoelace([Bp8, Cp8, Ep8]), 6):g}cm²')
assert abs(hatched_area(pr8) - 36) < 1e-3
assert abs(angle(Dp8, Ap8, Ep8) - 150) < 1e-9 and abs(angle(Ep8, Dp8, Ap8) - 15) < 1e-9                  # 解説で使った、三角形DAEの角

# ====================================================================== 第09セット：カードの和
lead9 = S(9)['lead']
a9, b9 = (int(x) for x in re.findall(r'「(\d)」のカード', lead9)[:2])
assert (a9, b9) == (3, 8) and math.gcd(a9, b9) == 1
reach = lambda n: any((n - b9 * j) >= 0 and (n - b9 * j) % a9 == 0 for j in range(n // b9 + 1))        # nが、a9の倍数とb9の倍数の和になるか
sums4 = {a9 * i + b9 * (4 - i) for i in range(5)}
eq('算5-9(1) 4枚の和', ans(M5, 9, 1), f'{len(sums4)}通り')
assert len(set(sum(c) for c in itertools.combinations_with_replacement([a9, b9], 4))) == len(sums4)
no9 = [n for n in range(1, 16) if not reach(n)]
eq('算5-9(2) 1〜15でできない数', ans(M5, 9, 2), f'{len(no9)}個')
assert '15' in q_text(M5, 9, 2)
no_all = [n for n in range(1, 400) if not reach(n)]
eq('算5-9(3) できない最大の数', ans(M5, 9, 3), str(max(no_all)))
assert max(no_all) == a9 * b9 - a9 - b9 and all(reach(n) for n in range(max(no_all) + 1, 400))
n9 = int(re.search(r'ちょうど(\d+)になる', q_text(M5, 9, 4)).group(1))
ways9 = [(i, j) for i in range(n9 // a9 + 1) for j in range(n9 // b9 + 1) if a9 * i + b9 * j == n9]
eq('算5-9(4) 合計50の取り出し方', ans(M5, 9, 4), f'{len(ways9)}通り')

# ====================================================================== 第10セット：円の転がりと平行四辺形
p10 = panels(10)
for pn in p10:
    eq(f'算5-10 図の寸法の文字 {pn.get("cap", pn.get("rect"))}', labels_ok(pn['prims']), [])
# (1) 円Aが通った部分：Aの中心を、Bのまわりに、細かく動かして、円Aがおおう部分を数える
cs10 = [pr for pr in p10[0]['prims'] if pr[0] == 'circle']
(cB, RB), (cA, RA) = (cs10[0][1], cs10[0][2]), (cs10[1][1], cs10[1][2])
assert cB == (0, 0) and cA == (0, 3)
assert re.search(r'半径(\d)cmの円Bと半径(\d)cmの円A', S(10)['lead']).groups() == (str(RB), str(RA))
assert abs(dist(cB, cA) - (RB + RA)) < 1e-9                                                              # はじめ、AはBにふれている
steps = 720
centers = [((RB + RA) * math.cos(2 * math.pi * t / steps + math.pi / 2), (RB + RA) * math.sin(2 * math.pi * t / steps + math.pi / 2)) for t in range(steps)]
n_rows = 4000
yr = RB + 2 * RA + .01
dy_ = 2 * yr / n_rows
cover = 0.0
for j in range(n_rows):
    y_ = -yr + (j + .5) * dy_
    iv = _merge([iv_ for c_ in centers for iv_ in row_iv(('circle', c_, RA), y_)])
    iv = _subtract(iv, row_iv(('circle', cB, RB), y_))
    cover += sum(b - a for a, b in iv) * dy_
want10 = math.pi * ((RB + 2 * RA) ** 2 - RB ** 2)
eq(f'算5-10(1) 円Aが通った部分の面積（数え直し {cover:.2f}）', abs(cover - want10) < .1, True)
eq('算5-10(1) ドーナツの面積', ans(M5, 10, 1), fmt(PI3 * ((RB + 2 * RA) ** 2 - RB ** 2), 'cm²'))

# (2) 点Pの位置：Aの向き ori(θ) を、ふれ合う点が止まる（すべらない）条件で決めて、点Pの位置を求める
th = math.radians(90)                                                                                    # 4分の1周（左まわり）
ori = lambda t: t * (RB + RA) / RA
ctr = lambda t: ((RB + RA) * math.cos(t + math.pi / 2), (RB + RA) * math.sin(t + math.pi / 2))
u0 = (0.0, 1.0)                                                                                          # はじめ、点Pは、Aの中心の真上
body = lambda t, beta: (ctr(t)[0] + RA * math.cos(ori(t) + beta), ctr(t)[1] + RA * math.sin(ori(t) + beta))
for tt in (0.3, 1.0, 2.2):                                                                               # ふれ合う点（Aの上の、Bの中心の向きの点）は、止まっている
    beta_c = (tt + math.pi / 2 + math.pi) - ori(tt)                                                      # 中心Aから、Bの中心へ向かう向き ＝ ori＋beta
    p_a, p_b = body(tt, beta_c), body(tt + 1e-6, beta_c)
    assert dist(p_a, p_b) < 1e-9, ('すべっている', dist(p_a, p_b))
beta_p = math.atan2(u0[1], u0[0]) - ori(0)
P_end = body(th, beta_p)
assert abs(ctr(th)[0] + 3) < 1e-9 and abs(ctr(th)[1]) < 1e-9                                           # Aは、Bの真横（左がわ）にきた
opts = {}
for pn in p10[2:]:
    letter = [pr[2] for pr in pn['prims'] if pr[0] == 'lbl' and pr[2] in 'アイウエ'][0]
    P = [pr[1] for pr in pn['prims'] if pr[0] == 'pt' and pr[2] == 'P'][0]
    opts[letter] = P
    cc = [pr for pr in pn['prims'] if pr[0] == 'circle']
    assert cc[0][1] == (0, 0) and cc[1][1] == (-3, 0) and abs(dist(P, cc[1][1]) - RA) < 1e-9                  # どの選択肢も、PはAの円周の上
pick = [k for k, P in opts.items() if dist(P, P_end) < 1e-6]
eq('算5-10(2) 点Pの位置', ans(M5, 10, 2), ''.join(pick))
assert sorted(opts) == ['ア', 'イ', 'ウ', 'エ'] and len({tuple(v) for v in opts.values()}) == 4

# (3)(4) 平行四辺形：座標（Fraction）から、面積を求めなおす。ずらし方によらないことも確かめる
Fr = Fraction
pgm = [pr for pr in p10[1]['prims'] if pr[0] == 'poly'][0][1]
Ap, Bp, Cp, Dp = [tuple(Fr(v).limit_denominator() for v in p) for p in pgm]
assert (Bp, Cp) == ((0, 0), (15, 0)) and Ap[1] == Dp[1] and Ap[1] * 15 == 240 and dist(Ap, Dp) == 15       # 面積240cm²、BC＝15cm
Ep_ = [pr[1] for pr in p10[1]['prims'] if pr[0] == 'pt' and pr[2] == 'E'][0]


def meet(p1, p2, p3, p4):
    """直線p1p2と直線p3p4の交点。"""
    x1, y1 = p1
    x2, y2 = p2
    x3, y3 = p3
    x4, y4 = p4
    den = (x1 - x2) * (y3 - y4) - (y1 - y2) * (x3 - x4)
    px = ((x1 * y2 - y1 * x2) * (x3 - x4) - (x1 - x2) * (x3 * y4 - y3 * x4)) / den
    py = ((x1 * y2 - y1 * x2) * (y3 - y4) - (y1 - y2) * (x3 * y4 - y3 * x4)) / den
    return (px, py)


tri_area = lambda *p: Fr(abs(sum(p[i][0] * p[(i + 1) % len(p)][1] - p[(i + 1) % len(p)][0] * p[i][1] for i in range(len(p)))), 2)
q10c = q_text(M5, 10, 3)
fbc = int(re.search(r'三角形FBCの面積が(\d+)cm', q10c).group(1))
for shear in (Fr(4), Fr(0), Fr(-7), Fr(11, 2)):                                                           # 平行四辺形のななめのずれは、どれでもよい
    A_, D_ = (shear, Ap[1]), (shear + 15, Ap[1])
    # 点Eの位置を、総あたり（ADを1/10cmきざみ）で探す：三角形FBCの面積が72になる点
    hits = []
    for k in range(0, 151):
        E_ = (shear + Fr(k, 10), Ap[1])
        F_ = meet(Bp, E_, A_, Cp)
        if tri_area(F_, Bp, Cp) == fbc:
            hits.append((E_, F_))
    assert len(hits) == 1, (shear, hits)
    E_, F_ = hits[0]
    assert E_[0] - shear == 10                                                                           # AE＝10cm
    eq(f'算5-10(3) 三角形ABF（ずれ{shear}）', ans(M5, 10, 3), f'{tri_area(A_, Bp, F_)}cm²')
    eq(f'算5-10(4) 三角形ECD（ずれ{shear}）', ans(M5, 10, 4), f'{tri_area(E_, Cp, D_)}cm²')
Fp = meet(Bp, tuple(Fr(v).limit_denominator() for v in Ep_), Ap, Cp)
assert abs(float(Fp[0]) - 8.4) < 1e-9 and abs(float(Fp[1]) - 9.6) < 1e-9                                   # 図のFの位置
assert tri_area(Fp, Bp, Cp) == 72

# ====================================================================== 全セットの形：答え・解説
def py_value(expr):
    s = re.sub(r'<(\d+) (\d+)/(\d+)>', lambda m: f'(Fraction({m[1]})+Fraction({m[2]},{m[3]}))', expr)
    s = re.sub(r'<(\d+)/(\d+)>', lambda m: f'Fraction({m[1]},{m[2]})', s)
    s = re.sub(r'(?<![\d.])(\d+\.\d+)', lambda m: f"Fraction('{m[1]}')", s)
    s = re.sub(r'(?<![\w.\'(])(\d+)(?![\w.\'])', lambda m: f'Fraction({m[1]})', s)
    s = s.replace('×', '*').replace('÷', '/').replace('＋', '+').replace('－', '-')
    return eval(s, {'Fraction': Fraction})


def chains(ex):
    return re.findall(r'(?<![\w.>])((?:[\d.＋－×÷()<>/ ]+＝)+[\d.＋－×÷()<>/ ]+?)(?=[。、（]|$)', ex)


def last_number(ex):
    t = re.sub(r'（[^）]*）', '', ex).rstrip('。 ')
    toks = re.findall(r'\d+\.\d+|\d+', t)
    return toks[-1] if toks else None


bad = []
for i, st in enumerate(SETS, 1):
    for j, q in enumerate(st['qs'], 1):
        a, ex = q['ans'], q['ex']
        for ch in chains(ex):                                                                          # 解説の「A＝B＝C」が、成り立つか
            vs = []
            for side in ch.split('＝'):
                try:
                    vs.append(py_value(side.strip()))
                except Exception:
                    vs.append(None)
            vs = [v for v in vs if v is not None]
            if len(set(vs)) > 1:
                bad.append((i, j, '解説の等式が成り立たない', ch, [str(v) for v in vs]))
        m = re.match(r'\d+(?:\.\d+)?', a)
        if m:                                                                                          # 数の答え：解説の最後の数と一致するか
            ln = last_number(ex)
            if ln is None or Fraction(ln) != Fraction(m.group()):
                bad.append((i, j, '解説の最後の数が、答えとちがう', a, ex[-24:]))
        if q.get('unit') and not a.endswith(q['unit'].replace('　', '')) and q['unit'] not in ('',):
            bad.append((i, j, '答えの単位が、解答らんの単位とちがう', a, q['unit']))
eq(f'算5 全{sum(len(s["qs"]) for s in SETS)}問：解説の等式・解説の最後の数・単位', bad, [])
eq('算5 セット数と年度', [st['year'] for st in SETS], [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015])

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
