"""算数 大問9 の検算。答えは、データ（tools/tenri_rs_sansu9.py）の解説とは別の方法で、問題文の条件・図の座標から計算しなおして確かめる。

- 図形（第01・05セット）：図の頂点の座標から、ショーレースの公式・格子点の細かい数え上げで、面積・長さ・重なりのなさを調べる。
  第05セットは、「5つの面積が等しい」という条件だけから、BCの長さを総あたりで求めて、解説の長さの比と一致するか確かめる。
- 水そう（第02）・流水算（第04・07）：1秒きざみのシミュレーション。船の速さは、グラフの区間から、整数の組を総あたりで探す。
- 立体（第03）：1cm角の立方体を数える・格子点の数え上げ（円周率は本物の値で近い値になること）。
- 規則性（第06・08）：実際にならべて、数える。
- 場合の数（第09）：itertools で、並び方・整数・道順をすべて数える。
- 第10セット：正方形のかさなりを、1cm角のマス目で数えて、周・頂点・面積を調べる。ビー玉は、個数を総あたりで探す。
問題文の数（正規表現でぬき出す）と、図の args の数が、一致することも確かめる。
"""
import itertools
import math
import re
from fractions import Fraction

from check_common import FAIL, eq, ans, q_text, is_simplest
import tenri_rs_sansu9 as M9
import kanji_grade as KG

SETS = M9.SETS
COVER = set()                              # 検算した (セット, 小問)


def chk(s, q, what, got, want):
    COVER.add((s, q))
    eq(f'算9-{s}({q}) {what}', got, want)


def fig_args(s):
    return SETS[s - 1]['fig']['args']


def nums(text):
    return [Fraction(x) for x in re.findall(r'\d+(?:\.\d+)?', text)]


def parse_ans(a):
    """答えの文字列から、(数, 単位) を取り出す。'49cm²'→(49,'cm²')、'<4 8/13>cm'→(60/13,'cm')。"""
    m = re.fullmatch(r'<(?:(\d+) )?(\d+)/(\d+)>(.*)', a)
    if m:
        return Fraction(int(m[1] or 0)) + Fraction(int(m[2]), int(m[3])), m[4]
    m = re.fullmatch(r'(\d+(?:\.\d+)?)(.*)', a)
    return Fraction(m[1]), m[2]


def shoelace(poly):
    return abs(sum(Fraction(poly[i][0]) * Fraction(poly[(i + 1) % len(poly)][1]) - Fraction(poly[(i + 1) % len(poly)][0]) * Fraction(poly[i][1])
                   for i in range(len(poly)))) / 2


def inside(poly, x, y):
    """点が多角形の内がわか（境界は、さけた点だけを使うので、どちらでもよい）。"""
    n, c = len(poly), False
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            c = not c
    return c


def grid_area(polys_in, x0, x1, y0, y1, n=300):
    """条件 polys_in(x, y) を満たす格子点（マスの中心）を数えて、面積を返す。"""
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    cnt = sum(1 for i in range(n) for j in range(n) if polys_in(x0 + (i + .5) * dx, y0 + (j + .5) * dy))
    return cnt * dx * dy


def fmt_g(v):
    return f'{v:g}'


def mixed(f):
    w, r = divmod(f, 1)
    return f'<{w} {r.numerator}/{r.denominator}>' if w else f'<{r.numerator}/{r.denominator}>'


# ================= 第01セット：直角三角形4つで正方形 =================
S1 = SETS[0]
a1, b1 = sorted(int(x) for x in re.search(r'(\d+)cmと(\d+)cm', S1['lead']).groups())
pan1, pan2 = fig_args(1)['panels']
tri1 = [p for p in pan1['prims'] if p[0] == 'poly'][0][1]
legs1 = sorted([math.dist(tri1[0], tri1[1]), math.dist(tri1[0], tri1[2])])
assert (a1, b1) == tuple(legs1), '図1と問題文の長さが一致しない'
assert {f'{a1}cm', f'{b1}cm'} <= {p[2] for p in pan1['prims'] if p[0] == 'text'}
hat = [p[1] for p in pan2['prims'] if p[0] == 'poly' and p[2].get('fill') == 'hatch'][0]
outer = [p[1] for p in pan2['prims'] if p[0] == 'poly' and len(p[1]) == 4 and p[2].get('w') == 1.5][0]
tris = [p[1] for p in pan2['prims'] if p[0] == 'poly' and len(p[1]) == 3]
assert len(tris) == 4
sides = [math.dist(outer[i], outer[(i + 1) % 4]) for i in range(4)]
assert max(sides) - min(sides) < 1e-9 and abs(math.dist(outer[0], outer[2]) - math.dist(outer[1], outer[3])) < 1e-9     # 正方形
for t in tris:                                                                                          # 4つとも、図1と合同（辺の長さの組が同じ）
    ls = sorted(math.dist(t[i], t[(i + 1) % 3]) for i in range(3))
    assert all(abs(x - y) < 1e-9 for x, y in zip(ls, [a1, b1, math.hypot(a1, b1)]))
for k in range(4):                                                                                      # 4つの三角形の斜辺が、正方形の辺になっている
    assert any(frozenset(map(tuple, (t[i], t[(i + 1) % 3]))) == frozenset(map(tuple, (outer[k], outer[(k + 1) % 4]))) for t in tris for i in range(3))
pieces = tris + [hat]
cover1 = grid_area(lambda x, y: sum(inside(p, x, y) for p in pieces) == 1, -6, 13, -6, 13, 190)         # 5つの部分で、すきまなく・かさならずに、正方形をおおう
out1 = grid_area(lambda x, y: inside(outer, x, y), -6, 13, -6, 13, 190)
assert abs(cover1 - out1) < .1 and abs(out1 - float(shoelace(outer))) < .3
assert abs(grid_area(lambda x, y: sum(inside(p, x, y) for p in pieces) >= 1 and not inside(outer, x, y), -6, 13, -6, 13, 190)) < 1e-9
chk(1, 1, '斜線部分の面積', parse_ans(ans(M9, 1, 1)), (shoelace(hat), 'cm²'))
chk(1, 2, '正方形ABCDの面積', parse_ans(ans(M9, 1, 2)), (shoelace(outer), 'cm²'))
side1 = [x for x in range(1, 100) if x * x == shoelace(outer)]
chk(1, 3, '1辺の長さ', parse_ans(ans(M9, 1, 3)), (Fraction(side1[0]), 'cm'))
assert side1[0] ** 2 == a1 ** 2 + b1 ** 2
cross1 = abs(Fraction(tri1[1][0] - tri1[0][0]) * (tri1[2][1] - tri1[0][1]) - Fraction(tri1[2][0] - tri1[0][0]) * (tri1[1][1] - tri1[0][1]))
h1 = cross1 / side1[0]                                         # 2×面積÷いちばん長い辺
chk(1, 4, '斜辺を底辺としたときの高さ', parse_ans(ans(M9, 1, 4)), (h1, 'cm'))
assert ans(M9, 1, 4) == mixed(h1) + 'cm'
assert math.isclose(float(h1), math.dist((0, 0), (0, 0)) + abs(a1 * b1) / math.hypot(a1, b1))              # 直角の頂点から、斜辺までの距離

# ================= 第02セット：水そうとグラフ =================
S2 = SETS[1]
rateA, rateB = [int(x) for x in re.search(r'A管からは1分間に(\d+)L、B管からは1分間に(\d+)L', S2['lead']).groups()]
pts2 = fig_args(2)['series'][0]['pts']
(t0, h0), (t1, h1_), (t2, h2_), (t3, h3_) = pts2
ymax2 = fig_args(2)['ymax']
assert (t0, h0) == (0, 0) and h1_ == h3_ == ymax2
# 水の量（L）と水面の高さの関係：まず、グラフの傾きから、容積を求める（高さ1cmあたりの量は、(A＋B)÷(1分間にふえる高さ)）
slope1 = Fraction(h1_ - h0, t1 - t0)                         # cm/分
V2 = Fraction(rateA + rateB) / slope1 * ymax2                # 容積（L）
chk(2, 1, '容積', parse_ans(ans(M9, 2, 1)), (V2, 'L'))
perh = V2 / ymax2                                            # 高さ1cmあたりの水の量
C2 = perh * Fraction(h1_ - h2_) / (t2 - t1)                  # 水面が下がった分の水の量を、時間でわる
chk(2, 2, 'C管の量', parse_ans(ans(M9, 2, 2)), (C2, 'L'))
# シミュレーション：1秒ごとに、水の量をふやす
water, sec = perh * Fraction(h2_), 0
while water < V2:
    water += Fraction(rateB - C2, 60)
    sec += 1
mm, ss = divmod(sec, 60)
chk(2, 3, '満水までの時間（分・秒）', tuple(int(x) for x in re.findall(r'\d+', ans(M9, 2, 3))), (mm, ss))
assert abs(t2 + sec / 60 - t3) < 1e-9, 'グラフの最後の点の時間が、シミュレーションと合わない'
# 時間の刻みを細かくして、水面の高さの折れ線が、3つの区間の式と合うことを確かめる
water, hist = Fraction(0), []
for k in range(0, int(t3 * 60) + 1):
    t = Fraction(k, 60)
    if t < t1:
        water = (rateA + rateB) * t
    elif t < t2:
        water = V2 - C2 * (t - t1)
    else:
        water = perh * h2_ + (rateB - C2) * (t - t2)
    hh = water / perh
    gh = [h0 + (h1_ - h0) * (t - t0) / (t1 - t0), h1_ + (h2_ - h1_) * (t - t1) / (t2 - t1), h2_ + (h3_ - h2_) * (t - t2) / (t3 - t2)]
    want = gh[0] if t < t1 else gh[1] if t < t2 else gh[2]
    if abs(hh - want) > Fraction(1, 1000):
        hist.append((float(t), float(hh), float(want)))
eq('算9-2 グラフの折れ線が、水の量の計算と合う（1秒ごと）', hist[:3], [])
assert set(fig_args(2)['xticks']) == {0, t1, t2} and set(fig_args(2)['yticks']) == {0, h2_, ymax2}

# ================= 第03セット：立体の体積 =================
S3 = SETS[2]
pan3 = fig_args(3)['panels']
cube3, hole3 = pan3[0]['side'], pan3[0]['d']
assert re.search(rf'1辺{cube3}cmの立方体から、直径{hole3}cmの円柱', S3['lead'])
PI = Fraction('3.14')
# (1) 1cm角（のさらに細かい）立方体を数える：円の内がわの細かい点を数えて、円周率を本物の値で近づける
cnt_cells = 0
n3 = 400
for i in range(n3):
    for j in range(n3):
        x, y = (i + .5) * cube3 / n3, (j + .5) * cube3 / n3
        if (x - cube3 / 2) ** 2 + (y - cube3 / 2) ** 2 > (hole3 / 2) ** 2:
            cnt_cells += 1
vol_grid = cnt_cells * (cube3 / n3) ** 2 * cube3                # 底面の、穴をのぞいた格子点の数×高さ
want31 = cube3 ** 3 - PI * Fraction(hole3, 2) ** 2 * cube3
assert abs(vol_grid - float(want31)) < 3, (vol_grid, want31)
chk(3, 1, '立方体−円柱', parse_ans(ans(M9, 3, 1)), (want31, 'cm³'))
steps3 = pan3[1]['steps']
dep3 = pan3[1]['depth']
cells = 0
for i in range(sum(w for w, _ in steps3)):
    xs_, acc = i, 0
    for w, hh in steps3:                                          # i 番目の1cmの列が、どの段にあるか
        if xs_ < acc + w:
            height = hh
            break
        acc += w
    cells += height * dep3
chk(3, 2, '階段の立体（立方体の数）', parse_ans(ans(M9, 3, 2)), (Fraction(cells), 'cm³'))
# (3) 表面積：立方体の面を細かく数える（円周は、正多角形の周で近づける）
circ3 = 36000 * hole3 * math.sin(math.pi / 36000)
surf_real = 6 * cube3 ** 2 - 2 * math.pi * (hole3 / 2) ** 2 + circ3 * cube3
want33 = 6 * cube3 ** 2 - 2 * PI * Fraction(hole3, 2) ** 2 + PI * hole3 * cube3
assert abs(surf_real - float(want33)) < .5
chk(3, 3, '表面積', parse_ans(ans(M9, 3, 3)), (want33, 'cm²'))
assert all(steps3[k][1] > steps3[k + 1][1] for k in range(len(steps3) - 1))                               # 左がいちばん高い階段（図の段差の数値は、高さの差）

# ================= 第04セット：流水算（往復のグラフ） =================
S4 = SETS[3]
g4 = fig_args(4)
pts4 = g4['series'][0]['pts']
D4 = Fraction(str(g4['ymax'])) * 1000                           # m
stop4 = int(re.search(r'(\d+)分間とまった', S4['lead']).group(1))
(_, _), (tA, dA), (tB, dB), (tC, dC) = pts4
assert dA == dB == g4['ymax'] and dC == 0 and tB - tA == stop4
t_down, t_up = Fraction(tA), Fraction(tC - tB)
sol4 = [(v, u) for v in range(1, 800) for u in range(0, v) if D4 / (v + u) == t_down and D4 / (v - u) == t_up]
assert len(sol4) == 1
v4, u4 = sol4[0]
chk(4, 1, '流れの速さ', parse_ans(ans(M9, 4, 1)), (Fraction(u4), 'm'))
chk(4, 2, '静水での速さ', parse_ans(ans(M9, 4, 2)), (Fraction(v4), 'm'))
chk(4, 3, '流れがないときの1往復', parse_ans(ans(M9, 4, 3)), (D4 * 2 / v4, '分'))
v4b = int(re.search(r'分速(\d+)mの別の船', q_text(M9, 4, 4)).group(1))
x1 = lambda t: (v4 + u4) * t                                      # P港から、下る船の位置
x2 = lambda t: D4 - (v4b - u4) * t                                # P港から、別の船（Q港から上る）の位置
sec4 = next(k for k in range(0, 100000) if x1(Fraction(k, 60)) >= x2(Fraction(k, 60)))
chk(4, 4, 'すれちがう時刻', parse_ans(ans(M9, 4, 4)), (Fraction(sec4, 60), '分後'))
# グラフの折れ線を、区間の式から細かくたしかめる
bad4 = []
for k in range(0, tC * 60 + 1):
    t = Fraction(k, 60)
    pos = (v4 + u4) * t if t <= tA else D4 if t <= tB else D4 - (v4 - u4) * (t - tB)
    gv = 0 + (dA - 0) * t / tA if t <= tA else dA if t <= tB else dA + (dC - dA) * (t - tB) / (tC - tB)
    if abs(pos / 1000 - Fraction(str(gv))) > Fraction(1, 10 ** 6):
        bad4.append(float(t))
eq('算9-4 グラフの折れ線が、区間ごとの式と合う', bad4[:3], [])
assert set(g4['xticks']) == {0, tA, tC} and set(g4['yticks']) == {0, g4['ymax']} and fmt_g(g4['ymax']) in g4['ylabels'][g4['ymax']]

# ================= 第05セット：三角形の面積比 =================
S5 = SETS[4]
pr5 = fig_args(5)['panels'][0]['prims']
P5 = {p[2]: tuple(Fraction(v).limit_denominator(1000) for v in p[1]) for p in pr5 if p[0] == 'pt'}
AB5, GC5 = [int(x) for x in re.search(r'AB＝(\d+)cm、GC＝(\d+)cm', S5['lead']).groups()]
A5, B5, C5, D5, E5, F5, G5 = (P5[k] for k in 'ABCDEFG')
dist = lambda p, q: math.hypot(p[0] - q[0], p[1] - q[1])
assert dist(A5, B5) == AB5 and dist(G5, C5) == GC5 and B5[0] == A5[0] and B5[1] == C5[1]                  # 図の長さ＝問題文。直角はB
areas5 = [shoelace(t) for t in ([A5, B5, D5], [D5, B5, F5], [D5, F5, E5], [E5, F5, G5], [E5, G5, C5])]
assert len(set(areas5)) == 1, areas5                                                                      # 図の座標で、5つの面積が等しい
col = lambda p, q, r: (q[0] - p[0]) * (r[1] - p[1]) - (q[1] - p[1]) * (r[0] - p[0])
assert col(A5, D5, C5) == 0 and col(A5, E5, C5) == 0 and F5[1] == G5[1] == 0                              # D・EはAC上、F・GはBC上
# 条件（5つの面積が等しい）だけから、BCの長さ c と点の位置を、総あたりで求める
# B=(0,0), C=(c,0), A=(0,AB)。F=(f,0), G=(c−GC,0)。D=A+s(C−A), E=A+t(C−A)。
sols5 = []
for c in range(GC5 + 1, 80):
    for f in range(1, c - GC5):
        g = c - GC5
        # 三角形EFGとEGC：頂点Eから辺BCまでの高さが同じ → 面積が等しいのは、FG＝GCのとき
        if g - f != GC5:
            continue
        Sx = Fraction(AB5 * c * f, 2 * (c + f))                  # ABD＝(1/2)·AB·c·s、DBF＝(1/2)·f·AB(1−s) が、ともに Sx → s を消す
        s_ = Sx * 2 / (AB5 * c)
        if Sx * 2 / (AB5 * f) + s_ != 1:
            continue
        t_ = 1 - Sx * 2 / (AB5 * GC5)                             # EGC＝(1/2)·GC·AB(1−t)＝Sx
        Dp, Ep = (c * s_, AB5 * (1 - s_)), (c * t_, AB5 * (1 - t_))
        a5 = [shoelace(t) for t in ([(0, AB5), (0, 0), Dp], [Dp, (0, 0), (f, 0)], [Dp, (f, 0), Ep], [Ep, (f, 0), (g, 0)], [Ep, (g, 0), (c, 0)])]
        if len(set(a5)) == 1 and 0 < s_ < t_ < 1:
            sols5.append((c, f, g, s_, t_, a5[0]))
assert len(sols5) == 1, sols5
c5, f5, g5, s5, t5, S_each5 = sols5[0]
assert (C5[0], F5[0], G5[0]) == (c5, f5, g5) and D5[0] == c5 * s5 and E5[0] == c5 * t5                       # 図の点が、条件から求めた位置と同じ
chk(5, 1, 'FG', parse_ans(ans(M9, 5, 1)), (Fraction(g5 - f5), 'cm'))
chk(5, 2, 'BF', parse_ans(ans(M9, 5, 2)), (Fraction(f5), 'cm'))
chk(5, 3, '三角形ABCの面積', parse_ans(ans(M9, 5, 3)), (shoelace([(0, AB5), (0, 0), (c5, 0)]), 'cm²'))
assert shoelace([(0, AB5), (0, 0), (c5, 0)]) == 5 * S_each5
chk(5, 4, 'DEはACの何分のいくつ', parse_ans(ans(M9, 5, 4)), (t5 - s5, ''))                                 # AC上の点は、x座標の比で位置がきまる

# ================= 第06セット：数を段にならべる =================
S6 = SETS[5]
mult6 = int(re.search(r'(\d+)の倍数を', S6['lead']).group(1))
seq6 = iter(range(mult6, 10 ** 7, mult6))
rows6 = [[next(seq6) for _ in range(2 * n - 1)] for n in range(1, 41)]
assert fig_args(6)['rows'] == rows6[:4]
r_, k_ = [int(x) for x in re.search(r'(\d+)段目の、左から(\d+)番目', q_text(M9, 6, 1)).groups()]
chk(6, 1, 'k段目の左からm番目', parse_ans(ans(M9, 6, 1)), (Fraction(rows6[r_ - 1][k_ - 1]), ''))
x6 = int(re.search(r'^(\d+)は', q_text(M9, 6, 2)).group(1))
chk(6, 2, 'ある数が何段目か', parse_ans(ans(M9, 6, 2)), (Fraction(next(i for i, r in enumerate(rows6, 1) if x6 in r)), '段目'))
r3 = int(re.search(r'(\d+)段目の、まん中', q_text(M9, 6, 3)).group(1))
assert len(rows6[r3 - 1]) % 2 == 1
chk(6, 3, 'まん中の数', parse_ans(ans(M9, 6, 3)), (Fraction(rows6[r3 - 1][len(rows6[r3 - 1]) // 2]), ''))
r4 = int(re.search(r'1段目から(\d+)段目まで', q_text(M9, 6, 4)).group(1))
chk(6, 4, '合計', parse_ans(ans(M9, 6, 4)), (Fraction(sum(sum(r) for r in rows6[:r4])), ''))

# ================= 第07セット：流水算（2そうの船のグラフ） =================
S7 = SETS[6]
g7 = fig_args(7)
D7 = int(re.search(r'道のりは(\d+)kmです', S7['lead']).group(1))
(pl, pe), (ql, qe) = g7['series'][0]['pts'], g7['series'][1]['pts']
assert pl[0] == (0, D7)[0] and pl[1] == D7 and pe[1] == 0 and ql[1] == 0 and qe[1] == D7 and g7['ymax'] == D7
t_pq, t_qp = Fraction(pe[0], 60), Fraction(qe[0], 60)            # 時間
sol7 = [(v, u) for v in range(1, 100) for u in range(0, v) if Fraction(D7, v + u) == t_pq and Fraction(D7, v - u) == t_qp]
assert len(sol7) == 1
v7, u7 = sol7[0]
chk(7, 1, 'P港を出た船の速さ', parse_ans(ans(M9, 7, 1)), (Fraction(v7 + u7), 'km'))
chk(7, 2, '流れの速さ', parse_ans(ans(M9, 7, 2)), (Fraction(u7), 'km'))
# すれちがい：1秒ごとに、2そうの位置（Q港から）をたどる
posP = lambda t: D7 - (v7 + u7) * t                                # P港を出た船（下る）
posQ = lambda t: (v7 - u7) * t                                    # Q港を出た船（上る）
k7 = next(k for k in range(0, 10 ** 6) if posP(Fraction(k, 3600)) <= posQ(Fraction(k, 3600)))
chk(7, 3, 'すれちがう時刻', parse_ans(ans(M9, 7, 3)), (Fraction(k7, 60), '分後'))
chk(7, 4, 'すれちがう地点（P港から）', parse_ans(ans(M9, 7, 4)), (D7 - posP(Fraction(k7, 3600)), 'km'))
assert posP(Fraction(k7, 3600)) == posQ(Fraction(k7, 3600))                                  # 同じ地点
assert set(g7['xticks']) == {0, pe[0], qe[0]} and str(D7) in g7['ylabels'][D7]

# ================= 第08セット：白石と黒石 =================
pat8 = fig_args(8)['pattern']
reps8 = fig_args(8)['reps']
assert all(pat8 != pat8[:p] * (len(pat8) // p) for p in range(1, len(pat8)) if len(pat8) % p == 0)     # くり返しの単位が、これより短くない
seq8 = pat8 * 400
assert pat8 * reps8 == ''.join(seq8[:len(pat8) * reps8])
n1 = int(re.search(r'左から(\d+)番目の石は', q_text(M9, 8, 1)).group(1))
chk(8, 1, 'n番目の石の色', ans(M9, 8, 1), '白' if seq8[n1 - 1] == '○' else '黒')
n2 = int(re.search(r'左から(\d+)番目までの石', q_text(M9, 8, 2)).group(1))
chk(8, 2, 'n番目までの白石の数', parse_ans(ans(M9, 8, 2)), (Fraction(seq8[:n2].count('○')), '個'))
n3 = int(re.search(r'(\d+)番目の黒い石', q_text(M9, 8, 3)).group(1))
blk = [i for i, ch in enumerate(seq8, 1) if ch == '●']
chk(8, 3, 'n番目の黒石の位置', parse_ans(ans(M9, 8, 3)), (Fraction(blk[n3 - 1]), '番目'))
n4 = int(re.search(r'(\d+)番目の白い石より左', q_text(M9, 8, 4)).group(1))
wht = [i for i, ch in enumerate(seq8, 1) if ch == '○']
chk(8, 4, 'n番目の白石より左の黒石', parse_ans(ans(M9, 8, 4)), (Fraction(sum(1 for i in blk if i < wht[n4 - 1])), '個'))

# ================= 第09セット：場合の数 =================
S9 = SETS[8]
flags = '赤青黄緑白'
assert all(ch in S9['qs'][0]['q'] for ch in flags) and '赤と青' in S9['qs'][0]['q']
chk(9, 1, '赤と青がとなり合う並び方', parse_ans(ans(M9, 9, 1)),
    (Fraction(sum(1 for p in itertools.permutations(flags) if abs(p.index('赤') - p.index('青')) == 1)), '通り'))
cards = [int(x) for x in re.findall(r'\d', re.search(r'(\d(?:、\d)+)の数字', q_text(M9, 9, 2)).group(1))]
digits = int(re.search(r'(\d)けたの整数', q_text(M9, 9, 2)).group(1))
chk(9, 2, '偶数の個数', parse_ans(ans(M9, 9, 2)), (Fraction(sum(1 for p in itertools.permutations(cards, digits) if p[-1] % 2 == 0)), '個'))
g9 = fig_args(9)
nx9, ny9, blocked9 = g9['nx'], g9['ny'], {frozenset(b) for b in g9['blocked']}
lab9 = {nm: (i, j) for i, j, nm in g9['labels']}
assert lab9['A'] == (0, 0) and lab9['B'] == (nx9, ny9)


def all_paths(nx, ny):
    for ups in itertools.combinations(range(nx + ny), ny):          # 全部で nx+ny 回の移動のうち、上に進む回を選ぶ
        i = j = 0
        route = [(0, 0)]
        for k in range(nx + ny):
            i, j = (i, j + 1) if k in ups else (i + 1, j)
            route.append((i, j))
        yield route


ok9 = [r for r in all_paths(nx9, ny9) if not any(frozenset((r[k], r[k + 1])) in blocked9 for k in range(len(r) - 1))]
chk(9, 3, '道順の数', parse_ans(ans(M9, 9, 3)), (Fraction(len(ok9)), '通り'))
chk(9, 4, 'Pを通る道順', parse_ans(ans(M9, 9, 4)), (Fraction(sum(1 for r in ok9 if lab9['P'] in r)), '通り'))
# 解説に書いた、各交差点までの行き方の数（下の道から順に）を、1本ずつ数えなおした値と比べる
ex93 = M9.SETS[8]['qs'][2]['ex']
rows_ex = [[int(x) for x in r.split('・')] for r in re.findall(r'1(?:・\d+)+', ex93)]
rows_cnt = [[sum(1 for r in all_paths(i, j) if not any(frozenset((r[k], r[k + 1])) in blocked9 for k in range(len(r) - 1))) for i in range(nx9 + 1)]
            for j in range(1, ny9 + 1)]
eq('算9-9(3) 解説の、交差点ごとの行き方の数', rows_ex, rows_cnt)
assert len(blocked9) == 2 and all(abs(a[0] - b[0]) + abs(a[1] - b[1]) == 1 for a, b in map(tuple, blocked9))

# ================= 第10セット：正方形をかさねた図形・ビー玉 =================
S10 = SETS[9]
side10, dx10, dy10 = [int(x) for x in re.search(r'1辺(\d+)cmの正方形を、右へ(\d+)cm、上へ(\d+)cm', S10['lead']).groups()]


def shape(n):
    """n枚の正方形がおおう1cm角のマス（(i, j) は、左下の角の座標）。"""
    return {(x, y) for k in range(n) for x in range(k * dx10, k * dx10 + side10) for y in range(k * dy10, k * dy10 + side10)}


def perimeter(cs):
    return sum(1 for (x, y) in cs for (a, b) in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (x + a, y + b) not in cs)


def corners(cs):
    """図形のかどの数（4つのマスが集まる点で、斜めに2つだけのときは2つと数える）。"""
    cnt = 0
    pts = {(x + a, y + b) for (x, y) in cs for a in (0, 1) for b in (0, 1)}
    for (px, py) in pts:
        q = [((px - 1, py - 1) in cs), ((px, py - 1) in cs), ((px - 1, py) in cs), ((px, py) in cs)]
        n = sum(q)
        if n in (1, 3):
            cnt += 1
        elif n == 2 and q[0] == q[3]:
            cnt += 2
    return cnt


per = {n: perimeter(shape(n)) for n in range(1, 41)}
# 表の値（1枚の周＝12）が、数え上げと合う
tab10 = S10['table']['rows']
assert tab10[0][1:] == ['1', '2', '…', '10', '…'] and tab10[1][1] == str(per[1])
chk(10, 1, '表のア・イ', ans(M9, 10, 1), [str(per[2]), str(per[10])])
t90 = int(re.search(r'周りの長さが(\d+)cm', q_text(M9, 10, 2)).group(1))
chk(10, 2, '周りの長さが90cmになる枚数', parse_ans(ans(M9, 10, 2)), (Fraction(next(n for n in per if per[n] == t90)), '枚'))
assert sum(1 for n in per if per[n] == t90) == 1
quant = {                                                           # ①〜⑤：n枚のときの値
    '①': lambda n: perimeter(shape(n)),
    '②': lambda n: len(shape(n)),
    '③': lambda n: corners(shape(n)),
    '④': lambda n: sum(1 for k in range(n - 1)),
    '⑤': lambda n: n * side10 * side10,
}
prop = [k for k, f in quant.items() if len({Fraction(f(n), n) for n in range(1, 21)}) == 1]
q103 = q_text(M9, 10, 3)
assert [m for m in re.findall(r'([①-⑤]) ', q103)] == list(quant)
chk(10, 3, '比例するもの', ans(M9, 10, 3), '・'.join(prop))
# 図1（3枚）の外周の座標から、周りの長さ・頂点の数を調べ、表の考え方と合うことを確かめる
outline = [p[1] for p in fig_args(10)['panels'][0]['prims'] if p[0] == 'poly' and p[2].get('w') == 1.5][0]
sq3 = shape(3)
assert math.isclose(sum(math.dist(outline[i], outline[(i + 1) % len(outline)]) for i in range(len(outline))), per[3]) and len(outline) == corners(sq3)
assert shoelace(outline) == len(sq3)
# ビー玉：個数を総あたりで探す
fr = [(int(a), int(b)) for a, b in re.findall(r'<(\d+)/(\d+)>', q_text(M9, 10, 4))][:2]
last = int(re.search(r'残った(\d+)個すべて', q_text(M9, 10, 4)).group(1))
sol10 = []
for T in range(1, 2000):
    A = Fraction(fr[0][0], fr[0][1]) * T
    B = Fraction(fr[1][0], fr[1][1]) * (T - A)
    if A.denominator == 1 and B.denominator == 1 and T - A - B == last:
        sol10.append((T, A, B))
assert len(sol10) == 1
T10, A10, B10 = sol10[0]
chk(10, 4, 'AとBの合計の割合', parse_ans(ans(M9, 10, 4)), ((A10 + B10) / T10, ''))
assert ans(M9, 10, 4) == mixed((A10 + B10) / T10)
chk(10, 5, 'もとの個数', parse_ans(ans(M9, 10, 5)), (Fraction(T10), '個'))

# ================= 全体の確認 =================
total_q = sum(len(s['qs']) for s in SETS)
assert COVER == {(i, j) for i, s in enumerate(SETS, 1) for j in range(1, len(s['qs']) + 1)}, '検算していない小問がある'
# 答えの数が、解説の中にも出てくる（数の答えだけ）
bad = []
for i, s in enumerate(SETS, 1):
    for j, q in enumerate(s['qs'], 1):
        if q['kind'] != 'short' or not re.match(r'[<\d]', q['ans']):
            continue
        a = q['ans']
        key = re.match(r'(<[^>]+>|[\d.]+)', a).group(1)
        if key not in q['ex']:
            bad.append((i, j, a))
eq('算9 答えが解説の中に出てくる', bad, [])
# 答えの書き方：分数は約分・帯分数
fr_ans = [m for s_ in SETS for q in s_['qs'] for a_ in ([q['ans']] if isinstance(q['ans'], str) else q['ans']) for m in re.findall(r'<[^>]+>', a_)]
eq('算9 分数の答えが、約分された（帯分数の）形', [m for m in fr_ans if not is_simplest(m)], [])
# 漢字は、小学校で習う範囲。ただし、過去問でもそのまま使われる算数の用語「斜線部分」「偶数」の、斜・偶は、ふりがななしで使う
EXAM_TERMS = '斜偶'
bad_k = set()
for s in SETS:
    texts = [s['title'], s['lead']] + [q['q'] + q['ex'] for q in s['qs']] + [b for _, b in s.get('items', [])] + [q.get('head', '') for q in s['qs']]
    for t in texts:
        for ch in t:
            if '\u4e00' <= ch <= '\u9fff' and not KG.elementary(ch) and ch not in EXAM_TERMS:
                bad_k.add(ch)
eq('算9 小学校で習わない漢字', sorted(bad_k), [])
print(f'算9：{len(SETS)}セット・{total_q}問を、すべて検算した')

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
