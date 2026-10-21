"""算数 大問7（面積と体積・反比例・斜線部分・歯車・平均と度数分布・点対称・角度・動く2点・水そうのグラフ・数表と四捨五入）の検算。

答え（データ）とは別の方法で、問題文と図の数値から、答えを求めなおして比べる。
- 図の頂点・円の座標（データの fig の args）から、くつ下の公式・格子の細かい数え上げ（円周率は本物）・対称性を使う。
- 選択問題は、文ごとの関係式を式にして、積・比がいつも一定かどうかを、数値で調べる。
- 動く点・水そうは、時刻や体積を、実際にシミュレーションする。
- 問題文の数は、正規表現でぬき出して使う（問題文と図・答えの食いちがいを見つける）。
"""
import itertools
import math
import re
import statistics
from collections import Counter
from fractions import Fraction

from check_common import FAIL, eq, ans, q_text, val
import kanji_grade as KG
import tenri_rs_sansu7 as M7

PI = math.pi
PI314 = Fraction('3.14')


# ---------- 道具 ----------
def S(s):
    return M7.SETS[s - 1]


def Q(s, q):
    return S(s)['qs'][q - 1]


def fig_args(s):
    return S(s)['fig']['args']


def anum(a):
    """答えの文字列（'13cm²'・'2.5秒後'）の、はじめの数。"""
    return Fraction(re.match(r'\s*([\d.]+)', a).group(1))


def nums_in(text):
    return [Fraction(x) for x in re.findall(r'\d+\.\d+|\d+', text)]


def shoelace(poly):
    n = len(poly)
    return abs(sum(Fraction(poly[i][0]) * Fraction(poly[(i + 1) % n][1]) - Fraction(poly[(i + 1) % n][0]) * Fraction(poly[i][1]) for i in range(n))) / 2


def inside_poly(pt, poly):
    x, y = pt
    ins = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            ins = not ins
    return ins


def count_area(inside, x0, x1, y0, y1, n=600):
    """領域の面積を、格子（n×n）の中心点を数えて求める。"""
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    cnt = sum(1 for i in range(n) for j in range(n) if inside(x0 + (i + .5) * dx, y0 + (j + .5) * dy))
    return cnt * dx * dy


def prims_of(panel, kind):
    return [p for p in panel['prims'] if p[0] == kind]


def in_sector(pt, cx, cy, r, a0, a1):
    dx, dy = pt[0] - cx, pt[1] - cy
    if dx * dx + dy * dy > r * r:
        return False
    ang = math.degrees(math.atan2(dy, dx)) % 360
    return a0 <= ang <= a1


def chk(label, cond):
    eq(label, bool(cond), True)


def close(a, b, tol):
    return abs(float(a) - float(b)) < tol


# ======================================================================
# 第01セット（2024）：方眼の中の四角形・レンズ形、円柱を4等分した立体
# ======================================================================
a1 = fig_args(1)
pn1, pn2 = a1['panels']
(gr1,) = prims_of(pn1, 'grid')
N1 = gr1[2][0]
poly1 = prims_of(pn1, 'poly')[0][1]
chk('算7-1 (1)の頂点が、方眼の交点', all(isinstance(x, int) and isinstance(y, int) and 0 <= x <= N1 and 0 <= y <= N1 for x, y in poly1))
a_shoe = shoelace(poly1)
a_cnt = count_area(lambda x, y: inside_poly((x, y), poly1), 0, N1, 0, N1, 500)
chk('算7-1(1) 数え上げと、くつ下の公式の一致', close(a_cnt, a_shoe, .1))
eq('算7-1(1) 四角形の面積', ans(M7, 1, 1), f'{a_shoe}cm²')
sec_a, sec_b = prims_of(pn2, 'and')[0][1]
r1 = sec_a[2]
chk('算7-1 (2)の2つの四分円は、向かい合う頂点が中心・半径が同じ', sec_a[2] == sec_b[2] == r1 and (sec_a[1], sec_b[1]) == ((0, 0), (r1, r1)) and r1 == prims_of(pn2, 'grid')[0][2][0])
chk('算7-1 問題文の「1辺◯cm・半径◯cm」が、図と一致', set(nums_in(q_text(M7, 1, 2))) >= {r1} and f'{r1}cm' in q_text(M7, 1, 2))
in_lens = lambda x, y: x * x + y * y <= r1 * r1 and (x - r1) ** 2 + (y - r1) ** 2 <= r1 * r1
lens_true = count_area(in_lens, 0, r1, 0, r1, 900)                           # 円周率は本物
lens_314 = PI314 * r1 * r1 / 2 - r1 * r1
chk('算7-1(2) 数え上げ（円周率は本物）が、答えに近い', close(lens_true, anum(ans(M7, 1, 2)), .1))
eq('算7-1(2) レンズ形の面積（円周率3.14）', ans(M7, 1, 2), f'{float(lens_314):g}cm²')
sol1 = a1['solid']
R1_, H1_ = sol1['r'], sol1['h']
vol_true = count_area(lambda x, y: x * x + y * y <= R1_ * R1_, 0, R1_, 0, R1_, 900) * H1_
chk('算7-1(3) 数え上げの体積（円周率は本物）が、答えに近い', close(vol_true, anum(ans(M7, 1, 3)), .3))
eq('算7-1(3) 円柱を4等分した立体の体積', ans(M7, 1, 3), f'{float(PI314 * R1_ * R1_ / 4 * H1_):g}cm³')
base1 = count_area(lambda x, y: x * x + y * y <= R1_ * R1_, 0, R1_, 0, R1_, 900)
arc1 = sum(math.dist((R1_ * math.cos(math.pi / 2 * i / 4000), R1_ * math.sin(math.pi / 2 * i / 4000)),
                     (R1_ * math.cos(math.pi / 2 * (i + 1) / 4000), R1_ * math.sin(math.pi / 2 * (i + 1) / 4000))) for i in range(4000))
surf_true = 2 * base1 + arc1 * H1_ + 2 * R1_ * H1_                              # 底面2つ＋まがった面＋長方形の面2つ
chk('算7-1(4) 数え上げの表面積が、答えに近い', close(surf_true, anum(ans(M7, 1, 4)), .5))
eq('算7-1(4) 表面積', ans(M7, 1, 4), f'{float(2 * (PI314 * R1_ * R1_ / 4) + PI314 * 2 * R1_ / 4 * H1_ + 2 * R1_ * H1_):g}cm²')

# ======================================================================
# 第02セット（2023）：反比例の関係をすべて選ぶ
# ======================================================================
# 文ごとの、「xとy」の関係式（x＝文の中で先に出る量、y＝あとに出る量）
REL = {
    '12kmの道のりを走るときの、時速とかかる時間': lambda x: Fraction(12) / x,        # 時間＝道のり÷時速
    '1本60円のえんぴつを買うときの、本数と代金': lambda x: 60 * x,
    '面積が20cm²の平行四辺形の、底辺の長さと高さ': lambda x: Fraction(20) / x,
    '正方形の、1辺の長さと面積': lambda x: x * x,
    '高さが6cmの三角形の、底辺の長さと面積': lambda x: x * 6 / 2,
}
items2 = dict(S(2)['items'])
XS = [Fraction(v) for v in (1, 2, 3, 4, 5, 6, 8, 10, 12)]
kind2 = {}
for lab, body in items2.items():
    ys = [REL[body](x) for x in XS]
    prop = len({y / x for x, y in zip(XS, ys)}) == 1                               # y÷x がいつも同じ
    inv = len({x * y for x, y in zip(XS, ys)}) == 1                                # x×y がいつも同じ
    kind2[lab] = 'prop' if prop else 'inv' if inv else 'none'
chk('算7-2 5つの文すべてに、関係式がある', set(REL) == set(items2.values()))
eq('算7-2(1) 反比例', ans(M7, 2, 1), '・'.join(k for k, v in kind2.items() if v == 'inv'))
eq('算7-2(2) 比例', ans(M7, 2, 2), '・'.join(k for k, v in kind2.items() if v == 'prop'))
eq('算7-2(3) どちらでもない', ans(M7, 2, 3), '・'.join(k for k, v in kind2.items() if v == 'none'))
rows2 = S(2)['table']['rows']
xs2, ys2 = rows2[0][1:], rows2[1][1:]
known2 = [(Fraction(x), Fraction(y)) for x, y in zip(xs2, ys2) if x.isdigit() and y.isdigit()]
k2 = {x * y for x, y in known2}
chk('算7-2(4) 表の、数がそろっている列の積が、すべて同じ', len(k2) == 1)
(k2_,) = k2
unk2 = {}
for x, y in zip(xs2, ys2):
    if not y.isdigit():
        unk2[y] = k2_ / Fraction(x)
    if not x.isdigit():
        unk2[x] = k2_ / Fraction(y)
eq('算7-2(4) 表の空らん', ans(M7, 2, 4), [str(unk2[k]) for k in ('ア', 'イ')])

# ======================================================================
# 第03セット（2022）：斜線部分の面積（正方形と円、直角三角形とおうぎ形、円と正方形）
# ======================================================================
pn31, pn32, pn33 = fig_args(3)['panels']
sq3 = prims_of(pn31, 'poly')[0][1]
ci3 = prims_of(pn31, 'circle')[0]
side3 = sq3[1][0] - sq3[0][0]
chk('算7-3(1) 円が、正方形の4つの辺にふれる', ci3[1] == (side3 / 2, side3 / 2) and ci3[2] == side3 / 2)
chk('算7-3(1) 問題文の辺の長さが、図と一致', f'{side3}cm' in q_text(M7, 3, 1) and f'{side3}cm' in [t[2] for t in prims_of(pn31, 'text')])
r3 = side3 / 2
ar31 = count_area(lambda x, y: not ((x - r3) ** 2 + (y - r3) ** 2 <= r3 * r3), 0, side3, 0, side3, 900)
chk('算7-3(1) 数え上げ（円周率は本物）が、答えに近い', close(ar31, anum(ans(M7, 3, 1)), .2))
eq('算7-3(1) 正方形－円', ans(M7, 3, 1), f'{float(side3 ** 2 - PI314 * r3 * r3):g}cm²')
tri3 = prims_of(pn32, 'poly')[0][1]
sec3 = prims_of(pn32, 'sector')[0]
(A3, B3, C3) = tri3
dot = lambda u, v: u[0] * v[0] + u[1] * v[1]
vec = lambda p, q: (q[0] - p[0], q[1] - p[1])
chk('算7-3(2) 角Bが直角で、AB＝BC', dot(vec(B3, A3), vec(B3, C3)) == 0 and math.dist(A3, B3) == math.dist(B3, C3))
chk('算7-3(2) 問題文の「AB＝BC＝◯cm」が、図と一致', f'AB＝BC＝{int(math.dist(A3, B3))}cm' in q_text(M7, 3, 2))
ang3 = math.degrees(math.acos(dot(vec(A3, B3), vec(A3, C3)) / (math.dist(A3, B3) * math.dist(A3, C3))))
chk('算7-3(2) おうぎ形は、Aを中心・半径AB・中心角は角A', sec3[1] == A3 and sec3[2] == math.dist(A3, B3) and close(sec3[4] - sec3[3], ang3, 1e-6))
rr3 = sec3[2]
ar32 = count_area(lambda x, y: inside_poly((x, y), tri3) and not in_sector((x, y), A3[0], A3[1], rr3, sec3[3], sec3[4]), 0, 8, 0, 8, 900)
chk('算7-3(2) 数え上げ（円周率は本物）が、答えに近い', close(ar32, anum(ans(M7, 3, 2)), .1))
eq('算7-3(2) 三角形－おうぎ形', ans(M7, 3, 2), f'{float(shoelace(tri3) - PI314 * int(rr3) ** 2 * Fraction(round(ang3), 360)):g}cm²')
ci33 = prims_of(pn33, 'circle')[0]
dia3 = prims_of(pn33, 'poly')[0][1]
chk('算7-3(3) 正方形の頂点が、円周の上', all(close(math.hypot(*p), ci33[2], 1e-9) for p in dia3))
chk('算7-3(3) 問題文の直径が、図と一致', f'直径{int(2 * ci33[2])}cm' in q_text(M7, 3, 3) and f'{int(2 * ci33[2])}cm' in [t[2] for t in prims_of(pn33, 'text')])
ar33 = count_area(lambda x, y: x * x + y * y <= ci33[2] ** 2 and not inside_poly((x, y), dia3), -6, 6, -6, 6, 900)
chk('算7-3(3) 数え上げ（円周率は本物）が、答えに近い', close(ar33, anum(ans(M7, 3, 3)), .3))
eq('算7-3(3) 円－正方形', ans(M7, 3, 3), f'{float(PI314 * int(ci33[2]) ** 2 - shoelace(dia3)):g}cm²')

# ======================================================================
# 第04セット（2021）：歯車の回転数
# ======================================================================
teeth4 = fig_args(4)['teeth']
tA, tB, tC = [int(x) for x in re.search(r'Aが(\d+)個、Bが(\d+)個、Cが(\d+)個', S(4)['lead']).groups()]
chk('算7-4 リード文の歯の数が、図と一致', (tA, tB, tC) == tuple(teeth4))
T = {'A': tA, 'B': tB, 'C': tC}


def turns_of(src, t_src, dst):
    """src が t_src 回転するとき、かみ合う歯車（つながっている歯車）dst は何回転するか。ふれ合う歯の数が同じ。"""
    return Fraction(t_src) * T[src] / T[dst]


eq('算7-4(1) AからB', ans(M7, 4, 1), f'{float(turns_of("A", 1, "B")):g}回転')
t_c = int(re.search(r'Cが(\d+)回転', q_text(M7, 4, 2)).group(1))
eq('算7-4(2) CからA（Bを通しても同じ）', ans(M7, 4, 2), f'{float(turns_of("C", t_c, "A")):g}回転')
chk('算7-4(2) Bを通して、CからBへ、BからAへ求めても同じ', turns_of('B', turns_of('C', t_c, 'B'), 'A') == turns_of('C', t_c, 'A'))
step = next(s_ for s_ in itertools.count(1) if s_ % tB == 0 and s_ % tC == 0)     # 1歯ずつすすめて、しるしがもう一度ふれ合うまで
eq('算7-4(3) しるしがふれ合う', ans(M7, 4, 3), [f'{step // tB}回転', f'{step // tC}回転'])
chk('算7-4(3) 図のしるしは、B・Cのふれ合うところ', fig_args(4)['mark'] == 1 and 'Bのしるし' in q_text(M7, 4, 3) and 'Cのしるし' in q_text(M7, 4, 3))
rpm = int(re.search(r'Aが1分間に(\d+)回転', q_text(M7, 4, 4)).group(1))
eq('算7-4(4) 1分間のCの回転', ans(M7, 4, 4), f'{float(Fraction(rpm * tA, tC)):g}回転')

# ======================================================================
# 第05セット（2020）：平均と度数分布
# ======================================================================
a5 = fig_args(5)
hx, hc = a5['hist']['xs'], a5['hist']['counts']
nA5, nB5 = [int(x) for x in re.search(r'A組（(\d+)人）とB組（(\d+)人）', S(5)['lead']).groups()]
totA5 = int(re.search(r'合計は、(\d+)日', S(5)['lead']).group(1))
chk('算7-5 リード文の人数が、ヒストグラムと一致', sum(hc) == nB5 and f'B組（{nB5}人）' == a5['hist']['title'] and f'A組（{nA5}人）' == a5['table']['title'])
dataB = [x for x, k in zip(hx, hc) for _ in range(k)]
eq('算7-5(1) B組の平均', ans(M7, 5, 1), f'{float(Fraction(sum(dataB), len(dataB))):g}日')
tx, ty = a5['table']['xs'], a5['table']['ys']
unk5 = [i for i, v in enumerate(ty) if not isinstance(v, int)]
sols = []
for vals in itertools.product(range(0, nA5 + 1), repeat=len(unk5)):
    cnt = list(ty)
    for i, v in zip(unk5, vals):
        cnt[i] = v
    if sum(cnt) == nA5 and sum(x * k for x, k in zip(tx, cnt)) == totA5:
        sols.append((vals, cnt))
chk('算7-5(2) 人数の合計と日数の合計の両方に合う組は、ただ1つ', len(sols) == 1)
(vals5, cntA5), = sols
eq('算7-5(2) ア・イ', ans(M7, 5, 2), [f'{v}人' for v in vals5])
dataA = [x for x, k in zip(tx, cntA5) for _ in range(k)]
mode_c = Counter(dataA).most_common()
chk('算7-5(3) 最ひん値がただ1つ', len(mode_c) == 1 or mode_c[0][1] > mode_c[1][1])
eq('算7-5(3) A組の中央値・最ひん値', ans(M7, 5, 3), [f'{float(Fraction(statistics.median(dataA))):g}日', f'{mode_c[0][0]}日'])
eq('算7-5(4) 全体の平均', ans(M7, 5, 4), f'{float(Fraction(sum(dataA) + sum(dataB), len(dataA) + len(dataB))):g}日')
chk('算7-5 A組の日数の合計が、リード文の数と一致', sum(dataA) == totA5)

# ======================================================================
# 第06セット（2019）：点対称な図形
# ======================================================================
pn6 = fig_args(6)['panels'][0]
poly6 = prims_of(pn6, 'poly')[0][1]
V6 = {p[2]: p[1] for p in prims_of(pn6, 'pt') if p[2] != 'O'}
O6 = [p[1] for p in prims_of(pn6, 'pt') if p[2] == 'O'][0]
chk('算7-6 頂点の記号A〜Hが、図形の頂点と同じ順', [V6[k] for k in 'ABCDEFGH'] == poly6)
refl = lambda p: (2 * O6[0] - p[0], 2 * O6[1] - p[1])
chk('算7-6 点Oのまわりに180度回すと、頂点が頂点にうつる', {refl(p) for p in V6.values()} == set(V6.values()))
corr6 = {k: [kk for kk, vv in V6.items() if vv == refl(V6[k])][0] for k in V6}
Lh = lambda a_, b_: math.dist(V6[a_], V6[b_])
per6 = sum(Lh('ABCDEFGH'[i], 'ABCDEFGH'[(i + 1) % 8]) for i in range(8))
chk('算7-6 リード文の周りの長さが、図形の周りと一致', int(re.search(r'周りの長さは(\d+)cm', S(6)['lead']).group(1)) == per6)
for t_ in prims_of(pn6, 'text'):                                                 # 図の長さの文字は、いちばん近い辺の長さと一致
    edges = [('ABCDEFGH'[i], 'ABCDEFGH'[(i + 1) % 8]) for i in range(8)]
    def seg_dist(p, a_, b_):
        (x1, y1), (x2, y2) = V6[a_], V6[b_]
        t = max(0, min(1, ((p[0] - x1) * (x2 - x1) + (p[1] - y1) * (y2 - y1)) / ((x2 - x1) ** 2 + (y2 - y1) ** 2)))
        return math.hypot(p[0] - (x1 + t * (x2 - x1)), p[1] - (y1 + t * (y2 - y1)))
    near = min(edges, key=lambda e: seg_dist(t_[1], *e))
    chk(f'算7-6 図の「{t_[2]}」は、辺{near[0]}{near[1]}の長さ', int(re.match(r'(\d+)', t_[2]).group(1)) == Lh(*near))
eq('算7-6(1) 点Cに対応する点', ans(M7, 6, 1), corr6[re.search(r'点(\w)に対応', q_text(M7, 6, 1)).group(1)])
side_q = lambda s_: re.search(r'辺(\w\w)の長さ', q_text(M7, 6, s_)).group(1)
eq('算7-6(2) 辺BCの長さ', ans(M7, 6, 2), f'{Lh(*side_q(2)):g}cm')
eq('算7-6(3) 辺HAの長さ', ans(M7, 6, 3), f'{Lh(*side_q(3)):g}cm')
chk('算7-6(2)(3) 対応する辺の長さは等しい', Lh('B', 'C') == Lh(corr6['B'], corr6['C']) and Lh('H', 'A') == Lh(corr6['H'], corr6['A']))
eq('算7-6(4) 面積', ans(M7, 6, 4), f'{shoelace(poly6)}cm²')
xs6, ys6 = [p[0] for p in poly6], [p[1] for p in poly6]
cnt6 = count_area(lambda x, y: inside_poly((x, y), poly6), min(xs6), max(xs6), min(ys6), max(ys6), 450)
chk('算7-6(4) 数え上げの面積が、くつ下の公式と一致', close(cnt6, shoelace(poly6), .1))

# ======================================================================
# 第07セット（2018）：角度2つ、斜線部分の面積2つ
# ======================================================================
p71, p72, p73, p74 = fig_args(7)['panels']
ang_at = lambda v, a_, b_: math.degrees(math.acos(dot(vec(v, a_), vec(v, b_)) / (math.dist(v, a_) * math.dist(v, b_))))
tri71 = prims_of(p71, 'poly')[0][1]
P_, Q_, R_ = tri71
angs71 = {'P': ang_at(P_, Q_, R_), 'Q': ang_at(Q_, P_, R_), 'R': ang_at(R_, P_, Q_)}
labs71 = {p[1]: p for p in prims_of(p71, 'angle')}
chk('算7-7 図(1)の角の印が、頂点の角度と一致', close(labs71[P_][3] - labs71[P_][2], angs71['P'], .05) and int(labs71[P_][4][:-1]) == round(angs71['P'])
    and close(labs71[R_][3] - labs71[R_][2], angs71['R'], .1) and int(labs71[R_][4][:-1]) == round(angs71['R']))
ext_a = 180 - angs71['Q']
chk('算7-7 図(1)の角あの印が、外角と一致', close(labs71[Q_][3] - labs71[Q_][2], ext_a, .05) and labs71[Q_][4] == 'あ')
eq('算7-7(1) 角あ', ans(M7, 7, 1), f'{round(ext_a)}度')
tri72 = prims_of(p72, 'poly')[0][1]
B_, C_, A_ = tri72
chk('算7-7 図(2)は、AB＝AC', close(math.dist(A_, B_), math.dist(A_, C_), 1e-3))
base_b = ang_at(B_, A_, C_)
chk('算7-7 問題文の角Bが、図の角と一致', int(re.search(r'角Bが(\d+)度', q_text(M7, 7, 2)).group(1)) == round(base_b) and [p for p in prims_of(p72, 'angle') if p[1] == B_][0][4] == f'{round(base_b)}°')
apex = ang_at(A_, B_, C_)
chk('算7-7 図(2)の角いの印が、頂角と一致', close([p for p in prims_of(p72, 'angle') if p[1] == A_][0][3] - [p for p in prims_of(p72, 'angle') if p[1] == A_][0][2], apex, .1))
eq('算7-7(2) 角い', ans(M7, 7, 2), f'{round(apex)}度')
(gr7,) = prims_of(p73, 'grid')
tri73 = prims_of(p73, 'poly')[0][1]
gw, gh = gr7[2]
chk('算7-7 問題文のたて・横が、図の方眼と一致', re.search(r'たて(\d+)cm、横(\d+)cm', q_text(M7, 7, 3)).groups() == (str(gh), str(gw)))
chk('算7-7 図(3)の三角形の頂点が、方眼の交点', all(isinstance(x, int) and isinstance(y, int) for x, y in tri73))
ar73 = count_area(lambda x, y: inside_poly((x, y), tri73), 0, gw, 0, gh, 600)
chk('算7-7(3) 数え上げの面積が、くつ下の公式と一致', close(ar73, shoelace(tri73), .1))
eq('算7-7(3) 方眼の中の三角形', ans(M7, 7, 3), f'{shoelace(tri73)}cm²')
big, s1_, s2_ = prims_of(p74, 'sector')
chk('算7-7 図(4)の小さい半円2つが、大きい半円の直径をつくす', s1_[1][0] - s1_[2] == big[1][0] - big[2] and s1_[1][0] + s1_[2] == s2_[1][0] - s2_[2] and s2_[1][0] + s2_[2] == big[1][0] + big[2])
chk('算7-7 問題文の直径が、図と一致', [int(x) for x in re.findall(r'直径(\d+)cm', q_text(M7, 7, 4))] == [2 * big[2], 2 * s1_[2], 2 * s2_[2]])
in_s = lambda sc_: (lambda x, y: in_sector((x, y), sc_[1][0], sc_[1][1], sc_[2], sc_[3], sc_[4]))
ar74 = count_area(lambda x, y: in_s(big)(x, y) and not in_s(s1_)(x, y) and not in_s(s2_)(x, y), -6, 6, 0, 6, 900)
chk('算7-7(4) 数え上げ（円周率は本物）が、答えに近い', close(ar74, anum(ans(M7, 7, 4)), .1))
eq('算7-7(4) 大きい半円－小さい半円2つ', ans(M7, 7, 4), f'{float(PI314 * (big[2] ** 2 - s1_[2] ** 2 - s2_[2] ** 2) / 2):g}cm²')

# ======================================================================
# 第08セット（2017）：長方形の辺の上を動く2点
# ======================================================================
W8, H8 = fig_args(8)['W'], fig_args(8)['H']
vP, vQ = [Fraction(x) for x in re.search(r'点Pは.*秒速(\d+)cmで、点Qは.*秒速(\d+)cmで', S(8)['lead']).groups()]
Bp, Cp, Dp, Ap = (0, 0), (W8, 0), (W8, H8), (0, H8)
chk('算7-8 問題文の頂点の順（Pは辺BC、CD、DA／Qは辺DC、CB、BA）', 'Pは辺BC、CD、DA' in S(8)['lead'] and 'Qは辺DC、CB、BA' in S(8)['lead'])


def along(path, d):
    """折れ線 path の上を、はじめから距離 d だけ進んだ点（終点で止まる）。"""
    d = Fraction(d)
    for p1, p2 in zip(path, path[1:]):
        L = Fraction(int(math.dist(p1, p2)))
        if d <= L:
            return (p1[0] + (p2[0] - p1[0]) * d / L, p1[1] + (p2[1] - p1[1]) * d / L)
        d -= L
    return path[-1]


pathP, pathQ = [Bp, Cp, Dp, Ap], [Dp, Cp, Bp, Ap]
P_at = lambda t: along(pathP, vP * t)
Q_at = lambda t: along(pathQ, vQ * t)
area_ABP = lambda t: shoelace([Ap, Bp, P_at(t)])
area_APQ = lambda t: shoelace([Ap, P_at(t), Q_at(t)])
t81, t82 = [int(x) for x in re.findall(r'(\d+)秒後の、三角形ABP', q_text(M7, 8, 1) + q_text(M7, 8, 2))]
t83 = int(re.search(r'(\d+)秒後の、三角形APQ', q_text(M7, 8, 3)).group(1))
eq('算7-8(1) ABP', ans(M7, 8, 1), f'{area_ABP(t81)}cm²')
eq('算7-8(2) ABP', ans(M7, 8, 2), f'{area_ABP(t82)}cm²')
eq('算7-8(3) APQ', ans(M7, 8, 3), f'{area_APQ(t83)}cm²')
target8 = int(re.search(r'(\d+)cm²になる', q_text(M7, 8, 4)).group(1))
hits8 = [Fraction(k, 100) for k in range(0, 1601) if area_ABP(Fraction(k, 100)) == target8]   # Pが、Aに着くまで（0〜16秒）を、0.01秒ずつ
chk('算7-8(4) PがAに着くのは16秒後', P_at(16) == Ap and P_at(15) != Ap)
eq('算7-8(4) 面積が20cm²になる時刻', ans(M7, 8, 4), [f'{float(t):g}秒後' for t in hits8])

# ======================================================================
# 第09セット（2016）：水そうの底に金属の立方体
# ======================================================================
a9 = fig_args(9)
pts9 = a9['pts']
(k_t, k_h), (e_t, e_h) = pts9[1], pts9[2]
cands = []
for Sb in range(1, 2000):                                                         # 底面積 S（cm²）を、1から順にためす
    for a_ in range(1, 40):                                                       # 立方体の1辺 a（cm）
        if a_ * a_ >= Sb:
            continue
        Qm = Fraction(a_) * (Sb - a_ * a_) / k_t                                  # 立方体の高さまでに、k_t 分かかる
        # 水の量 V のときの水面の高さ
        lvl = lambda V, Sb=Sb, a_=a_: V / (Sb - a_ * a_) if V <= (Sb - a_ * a_) * a_ else a_ + (V - (Sb - a_ * a_) * a_) / Sb
        if lvl(Qm * k_t) == k_h and lvl(Qm * e_t) == e_h:
            cands.append((Sb, a_, Qm, lvl))
chk('算7-9 グラフの2点に合う（底面積・立方体・水量）は、ただ1組', len(cands) == 1)
Sb9, a9_, Q9, lvl9 = cands[0]
chk('算7-9 図の立方体の1辺（args）と一致', a9['a'] == a9_ and k_h == a9_)
eq('算7-9(1) 立方体の1辺', ans(M7, 9, 1), f'{a9_}cm')
t92 = int(re.search(r'(\d+)分後', q_text(M7, 9, 2)).group(1))
eq('算7-9(2) 18分後の水面', ans(M7, 9, 2), f'{float(lvl9(Q9 * t92)):g}cm')
eq('算7-9(3) 底面積', ans(M7, 9, 3), f'{Sb9}cm²')
eq('算7-9(4) 1分間に入れる水の量', ans(M7, 9, 4), f'{Q9}cm³')
# 時間を0.01分ずつ刻んで、水面の高さの折れ線（グラフ）と、からだの式が一致する
chk('算7-9 0.01分ごとの水面が、グラフの折れ線と一致', all(close(lvl9(Q9 * Fraction(k, 100)), (k / 100) * (k_h / k_t) if k / 100 <= k_t else k_h + (k / 100 - k_t) * (e_h - k_h) / (e_t - k_t), 1e-9) for k in range(0, e_t * 100 + 1)))

# ======================================================================
# 第10セット（2015・2014）：数表・四捨五入と人数の範囲
# ======================================================================
a10 = fig_args(10)
cols10 = a10['cols']
cell = lambda r, c: a10['start'] + r * cols10 + c                              # r・c は0から数える
pos10 = lambda n: divmod(n - a10['start'], cols10)
tl10 = int(re.search(r'左上の数が(\d+)のとき', q_text(M7, 10, 1)).group(1))
r_, c_ = pos10(tl10)
chk('算7-10(1) わくが、表の右はしをこえない', c_ <= cols10 - 2)
eq('算7-10(1) 右下の数', ans(M7, 10, 1), str(cell(r_ + 1, c_ + 1)))
sum10 = int(re.search(r'和が(\d+)のとき', q_text(M7, 10, 2)).group(1))
hit10 = [cell(r, c) for r in range(0, 60) for c in range(0, cols10 - 1) if cell(r, c) + cell(r, c + 1) + cell(r + 1, c) + cell(r + 1, c + 1) == sum10]
chk('算7-10(2) 4つの和がその数になるわくの位置は、ただ1つ', len(hit10) == 1)
eq('算7-10(2) 左上の数', ans(M7, 10, 2), str(hit10[0]))
br10, bc10 = a10['box']
chk('算7-10 図のわくが、表の中にある', 1 <= br10 <= a10['rows'] - 1 and 1 <= bc10 <= cols10 - 1)
rnd = lambda x: (x + 5) // 10 * 10                                             # 一の位を四捨五入
n_men = int(re.search(r'(\d+)人になりました', q_text(M7, 10, 3)).group(1))
men = [x for x in range(0, 5000) if rnd(x) == n_men]
chk('算7-10(3) 問題文は「一の位を四捨五入」', '一の位を四捨五入' in q_text(M7, 10, 3))
eq('算7-10(3) 男の人の範囲', ans(M7, 10, 3), [f'{min(men)}人', f'{max(men)}人'])
n_women = int(re.search(r'(\d+)人になりました', q_text(M7, 10, 4)).group(1))
women = [x for x in range(0, 5000) if x // 10 * 10 == n_women]                # 一の位を切り捨て
chk('算7-10(4) 問題文は「一の位を切り捨て」', '一の位を切り捨て' in q_text(M7, 10, 4))
tot = [m_ + w_ for m_ in men for w_ in women]
eq('算7-10(4) 男女あわせた人数の範囲', ans(M7, 10, 4), [f'{min(tot)}人', f'{max(tot)}人'])

# ======================================================================
# 全体：形式・単位・解説の式・漢字
# ======================================================================
ALLOWED_KANJI = set('斜称')                                                    # 学年配当外だが、算数の用語として使う
UNIT_BAD, END_BAD, CHAIN_BAD, KANJI_BAD, NSET_BAD = [], [], [], [], []
NQS = [4, 4, 3, 4, 4, 4, 4, 4, 4, 4]
for si, st in enumerate(M7.SETS, 1):
    if len(st['qs']) != NQS[si - 1]:
        NSET_BAD.append((si, len(st['qs'])))
    texts = [st['title'], st['lead']] + [b for _, b in st.get('items', [])]
    for qi, q in enumerate(st['qs'], 1):
        texts += [q['q'], q['ex']] + ([q['ans']] if isinstance(q['ans'], str) else q['ans'])
        a_ = q['ans']
        if q['kind'] == 'short' and q.get('unit') and not a_.endswith(q['unit']):
            UNIT_BAD.append((si, qi, a_, q['unit']))
        if q['kind'] == 'short' and re.match(r'[\d.]+', a_):
            t_ = re.sub(r'（[^）]*）', '', q['ex']).rstrip('。 ')
            last = re.findall(r'\d+\.\d+|\d+', t_)[-1]
            if Fraction(last) != anum(a_):
                END_BAD.append((si, qi, a_, last))
        # 解説の中の「A＝B＝C」（数と ＋－×÷ ( ) だけ）は、どの辺も同じ値
        for m in re.finditer(r'[\d.＋－×÷＝()]+', q['ex']):
            run, pre, post = m.group(0), q['ex'][m.start() - 1] if m.start() else '', q['ex'][m.end()] if m.end() < len(q['ex']) else ''
            if '＝' not in run or re.match(r'[A-Za-zアイウエオ□]', pre) or re.match(r'[A-Za-zアイウエオ□]', post):
                continue
            sides = run.split('＝')
            if sides[0] and sides[0][0] in '＋－×÷':                                 # 文字の式の続き（「面積＝底辺×6÷2＝…」など）は、はじめの辺をのぞく
                sides = sides[1:]
            if sides and sides[-1] and sides[-1][-1] in '＋－×÷':
                sides = sides[:-1]
            sides = [x for x in sides if x]
            if len(sides) < 2:
                continue
            try:
                vs = {val(x_) for x_ in sides}
            except Exception:
                CHAIN_BAD.append((si, qi, run, '式を読めない'))
                continue
            if len(vs) > 1:
                CHAIN_BAD.append((si, qi, run, vs))
    for t_ in texts:
        KANJI_BAD += [(si, ch) for ch in t_ if '一' <= ch <= '龥' and not KG.elementary(ch) and ch not in ALLOWED_KANJI]
eq('算7 小問の数（第01〜10セット）', NSET_BAD, [])
eq('算7 答えの単位が、解答らんの単位と一致', UNIT_BAD, [])
eq('算7 解説の最後の数が、答えと一致', END_BAD, [])
eq('算7 解説の式「A＝B＝C」が成り立つ', CHAIN_BAD, [])
eq('算7 小学校で習わない漢字がない', sorted(set(KANJI_BAD)), [])
eq('算7 セットの数・小問の総数', (len(M7.SETS), sum(len(s['qs']) for s in M7.SETS)), (10, sum(NQS)))

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
