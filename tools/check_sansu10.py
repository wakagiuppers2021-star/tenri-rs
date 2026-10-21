"""算数 大問10の検算。import すると走る。

答えは、データ（tenri_rs_sansu10.py）の解説とは別の方法で、問題文・図の数値から求めなおして確かめる。
  第01 動く三角形：三角形を長方形で切り取る多角形の切り取り（Fraction）で、時刻ごとの重なりの面積を求める。
  第02 往復する点：区間ごとの1次式を、Fraction で解いて、重なる時刻をすべて数える（2026秒まで、くり返しを使わずに数える）。
  第03 速さのグラフ：グラフの折れ線から、区間ごとの式を作って、答えを求める。
  第04 水そうとブロック：水そうの底面積を、1つずつためして、グラフの点と合うものをさがす。
  第05 場合の数：itertools で数え上げ。あまりと人数は、人数を1つずつためす。組み合わせの人数は、全部の組を数える。
  第06 歩はば：歩はばと歩数を、cm・歩で別の形に書いて、道のりを1つずつためす。
  第07 三角形の面積：座標（ショーレース）で、4つの面積が等しくなる点の位置を、1つずつためして求める（解は1つだけ）。
  第08 規則性：実際に数を並べて、数える。
  第09 正方形をジグザグに重ねた図形：格子の上で、正方形をぬりつぶして、周・面積・頂点を数える。
  第10 流水算（エンジンが止まった船）：船を1/60分ごとに実際に動かして、グラフの点・終点・止まらなかったときの時刻を確かめる。
"""
import itertools
import math
import re
from fractions import Fraction as Fr

from check_common import FAIL, eq, ans, q_text, val
import tenri_rs_sansu10 as M10
import figs_sansu10 as F10

SETS = M10.SETS


def num_of(s):
    """答えの文字列（5秒後・<1/4>・4.8km・時速4km など）の、最初の数を、Fraction で返す。"""
    m = re.search(r'<(?:(\d+) )?(\d+)/(\d+)>|(\d+\.\d+|\d+)', s)
    if m.group(4):
        return Fr(m.group(4))
    return Fr(int(m.group(1) or 0)) + Fr(int(m.group(2)), int(m.group(3)))


def a_(s, q):
    """第s セットの第q問の答え（数）。grid の答えは、数のリスト。"""
    a = ans(M10, s, q)
    return [num_of(x) for x in a] if isinstance(a, list) else num_of(a)


def lead_of(s):
    return SETS[s - 1]['lead']


def grab(pattern, text, group=1):
    m = re.search(pattern, text)
    assert m, (pattern, text[:60])
    return Fr(m.group(group)) if re.fullmatch(r'\d+(\.\d+)?', m.group(group)) else m.group(group)


def interp(pts, t):
    """折れ線（点の列）の、時刻 t での値（Fraction）。"""
    pts = [(Fr(a), Fr(b)) for a, b in pts]
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return v1 if t2 == t1 else v1 + (v2 - v1) * (t - t1) / (t2 - t1)
    raise ValueError(t)


# =====================================================================================
# 第01セット 動く三角形と重なりの面積のグラフ
# =====================================================================================
def clip_to_rect(poly, x0, x1, y0, y1):
    """多角形を、長方形で切り取る（ショーレース・ホッジマン法）。"""
    def clip(poly, inside, cross):
        out = []
        for cur, prev in zip(poly, [poly[-1]] + poly[:-1]):
            if inside(cur):
                if not inside(prev):
                    out.append(cross(prev, cur))
                out.append(cur)
            elif inside(prev):
                out.append(cross(prev, cur))
        return out
    xs = lambda xv: (lambda p, q: (xv, p[1] + (q[1] - p[1]) * (xv - p[0]) / (q[0] - p[0])))
    ys = lambda yv: (lambda p, q: (p[0] + (q[0] - p[0]) * (yv - p[1]) / (q[1] - p[1]), yv))
    for inside, cross in ((lambda p: p[0] >= x0, xs(x0)), (lambda p: p[0] <= x1, xs(x1)),
                          (lambda p: p[1] >= y0, ys(y0)), (lambda p: p[1] <= y1, ys(y1))):
        if not poly:
            break
        poly = clip(poly, inside, cross)
    return poly


def shoelace(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2 if len(poly) >= 3 else Fr(0)


s1 = SETS[0]
f1 = s1['fig']['args']
leg1 = grab(r'どちらも(\d+)cm', lead_of(1))
rh1 = grab(r'長方形のたての長さも(\d+)cm', lead_of(1))
v1 = grab(r'秒速(\d+)cm', lead_of(1))
gap1 = grab(r'左のはしから(\d+)cm', lead_of(1))
eq('算10-1 図の数値と問題文（辺・たて・速さ・はなれた長さ）', (leg1, rh1, v1, gap1), (f1['leg'], f1['leg'], f1['v'], f1['gap']))
rw1 = Fr(f1['rw'])


def overlap1(t):
    """時刻 t（秒）のとき、三角形PQR（Rが先）と長方形（左はし x=0）の重なりの面積。"""
    xr = v1 * t - gap1
    tri = [(xr - leg1, Fr(0)), (xr, Fr(0)), (xr - leg1, leg1)]
    return shoelace(clip_to_rect(tri, Fr(0), rw1, Fr(0), rh1))


grid1 = [Fr(k, 20) for k in range(0, 20 * 25)]
area1 = {t: overlap1(t) for t in grid1}
peak1 = max(area1.values())
t_peak0 = min(t for t in grid1 if area1[t] == peak1)
t_peak1 = max(t for t in grid1 if area1[t] == peak1)
t_first = max(t for t in grid1 if area1[t] == 0 and t < t_peak0)               # 重なり始める直前（はなれている最後の時刻）
t_end = max(t for t in grid1 if area1[t] > 0) + Fr(1, 20)                       # 重なりがなくなる時刻
# 図のグラフの点が、実際の重なりの面積と合うか
bad1 = [(t, y) for t, y in F10.move_curve(f1['leg'], f1['gap'], f1['rw'], f1['v']) if abs(overlap1(Fr(t).limit_denominator(10 ** 6)) - Fr(y).limit_denominator(10 ** 6)) > Fr(1, 10 ** 4)]
eq('算10-1 図のグラフの点（250点以上）が、重なりの面積と合う', bad1, [])
eq('算10-1 図のx軸の目もり（重なり始め・平らな部分の終わり・重なりがなくなる）', tuple(Fr(x).limit_denominator(100) for x in F10.move_ticks(f1['leg'], f1['gap'], f1['rw'], f1['v'])), (t_first, t_peak1, t_end))
eq('算10-1(1) 4秒後の面積', a_(1, 1), overlap1(Fr(int(grab(r'(\d+)秒後に', q_text(M10, 1, 1))))))
eq('算10-1(2) ア・イ', a_(1, 2), [peak1, t_end])
eq('算10-1(3) 長方形の面積（平らな部分の長さから、横を求める）', a_(1, 3), v1 * (t_peak1 - t_first) * rh1)
target1 = grab(r'(\d+)cm²になる', q_text(M10, 1, 4))
hit1 = [t for t in grid1 if area1[t] == target1]
cross1 = sum(1 for t, u in zip(grid1, grid1[1:]) if (area1[t] - target1) * (area1[u] - target1) < 0)
eq('算10-1(4) 面積が18cm²になる時刻（2回だけ）', a_(1, 4), hit1)
eq('算10-1(4) 18cm²をまたぐ区間は、ほかにない', cross1, 0)

# =====================================================================================
# 第02セット 往復する2点
# =====================================================================================
s2 = SETS[1]
f2 = s2['fig']['args']
L2 = grab(r'(\d+)cmはなれた', lead_of(2))
p2 = grab(r'毎秒(\d+)cmの速さで、点Q', lead_of(2))
q2 = grab(r'点Bを出発して毎秒(\d+)cmの速さ', lead_of(2))
eq('算10-2 図の数値と問題文（距離・2つの速さ）', (L2, p2, q2), (f2['L'], f2['p'], f2['q']))


def pos2(t, speed, start_at_b):
    """往復する点の、点Aからの距離。時刻 t（Fraction）。折り返しは、道のりを 2L でわったあまりで考える。"""
    d = (speed * t) % (2 * L2)
    x = d if d <= L2 else 2 * L2 - d
    return L2 - x if start_at_b else x


def meetings(T):
    """0<t<=T で、2点が重なる時刻を、すべて数える。区間ごとに2点とも1次式（折り返しの時刻で区切る）なので、1次式を解く。"""
    cut = {Fr(0), Fr(T)}
    for sp in (p2, q2):
        k = 1
        while Fr(k) * L2 / sp <= T:
            cut.add(Fr(k) * L2 / sp)
            k += 1
    cut = sorted(cut)
    out = set()
    for a, b in zip(cut, cut[1:]):
        fa = pos2(a, p2, False) - pos2(a, q2, True)
        fb = pos2(b, p2, False) - pos2(b, q2, True)
        # 区間の内がわで、折り返しが起きないように、中点での傾きを使う（端点の値は、かならず線形な区間の値）
        # 端点では折り返すので、端点の値でなく、区間内の2点から1次式を作る
        ma, mb = a + (b - a) / 3, a + 2 * (b - a) / 3
        da, db = pos2(ma, p2, False) - pos2(ma, q2, True), pos2(mb, p2, False) - pos2(mb, q2, True)
        slope = (db - da) / (mb - ma)
        if slope == 0:
            assert da != 0                                    # ずっと重なる区間はない
            continue
        root = ma - da / slope
        if a < root <= b:
            out.add(root)
    return sorted(out)


m2 = meetings(60)
eq('算10-2(1) 3回目に重なる時刻', a_(2, 1), m2[2])
dist2 = lambda t: abs(pos2(Fr(t), p2, False) - pos2(Fr(t), q2, True))
opts2 = {lab: pts for lab, pts in f2['graphs']}
ok2 = [lab for lab, pts in opts2.items() if all(interp(pts, Fr(k, 4)) == dist2(Fr(k, 4)) for k in range(0, 4 * 12 + 1))]
eq('算10-2(2) 距離のグラフ（実際に動かして、12秒間を1/4秒ごとに比べる）', ans(M10, 2, 2), '・'.join(ok2))
big2 = grab(r'(\d+)秒後までに', q_text(M10, 2, 3))
mm2 = meetings(int(big2))
eq('算10-2(3) 2026秒までに重なる回数', a_(2, 3), len(mm2))
eq('算10-2(3) 2026秒ちょうどには重ならない（数え方が分かれない）', len(meetings(int(big2) - 1)) == len(mm2), True)
big2b = grab(r'(\d+)秒後の、点P', q_text(M10, 2, 4))
eq('算10-2(4) 2026秒後の2点の間の距離', a_(2, 4), dist2(big2b))
eq('算10-2 問題文の2026が、(3)(4)で同じ', big2, big2b)

# =====================================================================================
# 第03セット 速さのグラフ（忘れ物）
# =====================================================================================
s3 = SETS[2]
f3 = s3['fig']['args']
pts3 = [(Fr(a), Fr(b)) for a, b in f3['pts']]
school3 = grab(r'(\d+)mはなれた', lead_of(3))
eq('算10-3 学校までの道のりと、グラフの終点', school3, pts3[-1][1])
eq('算10-3 折れ線の点が、方眼の交点にある', [p for p in pts3 if p[0] != int(p[0]) or p[1] % 300 != 0], [])
g3 = lambda t: interp(pts3, Fr(t))
eq('算10-3(1) 走った速さ（途中の2点の差から）', a_(3, 1), (g3(Fr(11, 2)) - g3(Fr(13, 2))) / 1)
eq('算10-3(2) 自転車の速さ', a_(3, 2), g3(15) - g3(14))
walk3 = g3(1) - g3(0)                                              # 最初の1分に進む道のり＝歩く速さ
arrive3 = min(Fr(k, 60) for k in range(0, int(60 * pts3[-1][0]) + 1) if g3(Fr(k, 60)) == school3)
eq('算10-3(3) 妹がのこす道のり（かんなさんの到着時に）', a_(3, 3), school3 - walk3 * arrive3)
# (4)：かんなさんが家を出る時刻から、1分ずつ、妹との差を見る（差は1次式なので、符号が変わる区間を1次式で解く）
home3 = min(t for t in range(1, int(pts3[-1][0])) if g3(t) == 0 and g3(t + 1) == 0)               # 家にもどった時刻（グラフが0になる最初の時刻）
diffs = [(Fr(t), g3(t) - walk3 * t) for t in range(home3, int(arrive3) + 1)]
for (ta, da), (tb, db) in zip(diffs, diffs[1:]):
    if da < 0 <= db:
        root3 = ta + (tb - ta) * (-da) / (db - da)
eq('算10-3(4) 追いつく地点（家からの道のり）', a_(3, 4), g3(root3))
eq('算10-3(4) 追いつくのは、学校に着くより前', root3 < arrive3, True)

# =====================================================================================
# 第04セット 水そうとブロック
# =====================================================================================
s4 = SETS[3]
f4 = s4['fig']['args']
cube4, tank_h4 = f4['cube'], f4['tank_h']
eq('算10-4 図の数値と問題文（立方体の個数・1辺・水そうの高さ）',
   (sum(f4['cols']), cube4, tank_h4),
   (int(grab(r'(\d+)個はり合わせた', lead_of(4))), int(grab(r'1辺(\d+)cm', lead_of(4))), int(grab(r'高さは(\d+)cm', lead_of(4)))))


def water_volume(S, z):
    """底面積 S の水そうに、ブロックを置いたとき、高さ z（cm）までにたまる水の量。ブロックの断面（1段ごとの個数）を、下から数えて、たしていく。"""
    total, bottom = Fr(0), Fr(0)
    while bottom < z:
        top = min(Fr(z), bottom + cube4)
        layer = int(bottom // cube4)
        cubes = sum(1 for h in f4['cols'] if h > layer)
        total += (S - cubes * cube4 * cube4) * (top - bottom)
        bottom = top
    return total


pts4 = [(Fr(a), Fr(b)) for a, b in f4['pts']]
sol4 = []
for S in range(300 + 1, 3001):                                            # 底面積を1つずつためす（ブロックの底が入る広さから）
    R = water_volume(S, pts4[1][1]) / pts4[1][0]                         # 1段目のグラフの点から、1分間の水の量
    if all(water_volume(S, h) == R * t for t, h in pts4[1:-1]):
        sol4.append((S, R))
eq('算10-4 グラフと合う（底面積, 毎分の量）は、1つだけ', len(sol4), 1)
S4, R4 = sol4[0]
eq('算10-4 図の水そうの底（よこ×おくゆき）が、底面積と同じ', f4['tank_w'] * f4['tank_d'], S4)
eq('算10-4(1) 底面積', a_(4, 1), S4)
eq('算10-4(2) 1分間に入れる水の量', a_(4, 2), R4)
eq('算10-4(3) 水面が40cmになる時刻', a_(4, 3), water_volume(S4, tank_h4) / R4)
eq('算10-4 グラフの最後の点（52分後）', pts4[-1], (water_volume(S4, tank_h4) / R4, tank_h4))
t4 = int(grab(r'から(\d+)分後に水を止めて', q_text(M10, 4, 4)))
eq('算10-4(4) ブロックを取り出したあとの水面の高さ（水の量÷底面積）', a_(4, 4), R4 * t4 / S4)
eq('算10-4(4) 取り出したあとの水面は、ブロックの高さより低い（水そうの底全体に広がる）', R4 * t4 / S4 < max(f4['cols']) * cube4, True)

# =====================================================================================
# 第05セット 場合の数と配る個数
# =====================================================================================
s5 = SETS[4]
kinds5 = [int(x) for x in re.findall(r'(\d+)個', lead_of(5))]
tab5 = [int(x) for x in s5['table']['rows'][1][1:]]
eq('算10-5 問題文のあめの個数と表の個数', kinds5, tab5)
n5 = int(grab(r'から(\d+)個を選ぶ', q_text(M10, 5, 1)))
sel5 = [c for c in itertools.combinations_with_replacement(range(3), n5) if all(c.count(k) <= tab5[k] for k in range(3))]
eq('算10-5(1) 同じ味もよい選び方（重複組み合わせ）', a_(5, 1), len(sel5))
eq('算10-5(2) 3つの味がすべてふくまれる', a_(5, 2), sum(1 for c in sel5 if set(c) == {0, 1, 2}))
rest5 = [int(x) for x in re.findall(r'が(\d+)個、レモン味が(\d+)個、ぶどう味が(\d+)個あまりました', q_text(M10, 5, 3))[0]]
kids5 = [n for n in range(1, 200) if all(r < n and (x - r) % n == 0 and (x - r) // n >= 1 for x, r in zip(tab5, rest5))]
eq('算10-5(3) 子どもの人数（あまりより多い人数で、割りきれるもの）は、1つだけ', a_(5, 3), kids5[0])
eq('算10-5(3) 人数の候補は、1つだけ', len(kids5), 1)
N5 = int(grab(r'(\d+)人の生徒', q_text(M10, 5, 4)))
sols5 = [(a, b, c) for a in range(N5 + 1) for b in range(N5 + 1) for c in range(N5 + 1)
         if a + b + c == N5 and a + b == tab5[0] and a + c == tab5[1] and b + c == tab5[2]]      # (いちご・レモン)(いちご・ぶどう)(レモン・ぶどう)
eq('算10-5(4) 組み合わせの人数の解は、1組だけ', len(sols5), 1)
eq('算10-5(4) いちご味とぶどう味をもらった生徒', a_(5, 4), sols5[0][1])
eq('算10-5 あめの総数は、人数×2', sum(tab5), 2 * N5)

# =====================================================================================
# 第06セット 歩はばと速さの比
# =====================================================================================
s6 = SETS[5]
a6, b6 = int(grab(r'姉の(\d+)歩の長さは、弟の(\d+)歩', lead_of(6), 1)), int(grab(r'姉の(\d+)歩の長さは、弟の(\d+)歩', lead_of(6), 2))
c6, d6 = int(grab(r'姉が(\d+)歩進む間に、弟は(\d+)歩', lead_of(6), 1)), int(grab(r'姉が(\d+)歩進む間に、弟は(\d+)歩', lead_of(6), 2))
step_a6 = int(grab(r'姉の1歩の長さは(\d+)cm', lead_of(6)))
step_b6 = next(Fr(x, 4) for x in range(1, 4000) if a6 * step_a6 == b6 * Fr(x, 4))        # 弟の1歩（cm）を、4分の1cm単位でためす
eq('算10-6(1) 弟の1歩', a_(6, 1), step_b6)
dist_a6, dist_b6 = c6 * step_a6, d6 * step_b6                                           # 同じ時間に進む道のり（cm）
g6 = math.gcd(int(dist_a6), int(dist_b6))
eq('算10-6(2) 速さの比', ans(M10, 6, 2), f'{int(dist_a6) // g6}：{int(dist_b6) // g6}')
spm6 = int(grab(r'1分間に(\d+)歩', q_text(M10, 6, 3)))
eq('算10-6(3) 弟の分速（姉の1分間の歩数から、弟の歩数をもとめる）', a_(6, 3), Fr(spm6 * d6, c6) * step_b6 / 100)
rem6 = int(grab(r'あと(\d+)mの所', q_text(M10, 6, 4)))
roads6 = [D for D in range(1, 20000) if D - Fr(D) * dist_b6 / dist_a6 == rem6]
eq('算10-6(4) 家から公園までの道のり（姉が着いたとき弟があと200m）', a_(6, 4), roads6[0])
eq('算10-6(4) 道のりは、1つだけ', len(roads6), 1)

# =====================================================================================
# 第07セット 三角形の面積の比
# =====================================================================================
s7 = SETS[6]
AB7 = int(grab(r'AB＝(\d+)cm', lead_of(7)))
DF7 = int(grab(r'DF＝(\d+)cm', lead_of(7)))


def tri_area(p, q, r):
    return abs((q[0] - p[0]) * (r[1] - p[1]) - (r[0] - p[0]) * (q[1] - p[1])) / 2


def quad_area(pts):
    return abs(sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))) / 2


def build7(c, d):
    """AB＝AB7 の直角三角形で、ACの長さc・点Dの位置d・F＝D＋DF7。E（辺BC上）は、三角形DBEの面積が三角形ABDと等しくなる位置。"""
    A, B, C = (Fr(0), Fr(0)), (Fr(0), Fr(AB7)), (Fr(c), Fr(0))
    D, F = (Fr(d), Fr(0)), (Fr(d + DF7), Fr(0))
    pt = lambda t: (B[0] + (C[0] - B[0]) * t, B[1] + (C[1] - B[1]) * t)
    a0, a1 = tri_area(D, B, pt(Fr(0))), tri_area(D, B, pt(Fr(1)))                      # 面積は、tの1次式（t＝0と1の値から、直線の式を作る）
    target = tri_area(A, B, D)
    if a1 == a0:
        return None
    t = (target - a0) / (a1 - a0)
    if not 0 < t < 1:
        return None
    return A, B, C, D, pt(t), F, t


sol7 = []
for c in range(DF7 + 1, 80):
    for d2 in range(1, 2 * c):
        d = Fr(d2, 2)
        if d + DF7 >= c:
            continue
        r = build7(c, d)
        if not r:
            continue
        A, B, C, D, E, F, t = r
        areas = [tri_area(A, B, D), tri_area(D, B, E), tri_area(D, E, F), tri_area(E, F, C)]
        if len(set(areas)) == 1:
            sol7.append((c, d, t, areas[0]))
eq('算10-7 4つの面積が等しくなる配置は、1つだけ', len(sol7), 1)
c7, d7, t7, area7 = sol7[0]
sol_pts7 = build7(c7, d7)
A7_, B7_, C7_, D7_, E7_, F7_, _ = sol_pts7
parts7 = [d7, DF7, c7 - d7 - DF7]
g7 = math.gcd(math.gcd(int(parts7[0] * 2), int(parts7[1] * 2)), int(parts7[2] * 2))
eq('算10-7(1) AD：DF：FC', ans(M10, 7, 1), '：'.join(str(int(x * 2) // g7) for x in parts7))
ratio7 = t7 / (1 - t7)                                                    # BE÷EC
eq('算10-7(2) BE：EC', ans(M10, 7, 2), f'{ratio7.numerator}：{ratio7.denominator}')
eq('算10-7(3) AC', a_(7, 3), c7)
eq('算10-7(4) 四角形BDFEの面積（B・D・F・Eの座標から）', a_(7, 4), quad_area([B7_, D7_, F7_, E7_]))
eq('算10-7(4) 四角形BDFEの面積＝三角形DBE＋三角形DEF', quad_area([B7_, D7_, F7_, E7_]), tri_area(D7_, B7_, E7_) + tri_area(D7_, E7_, F7_))
# 図の座標が、この配置と同じ
fig7 = {k: tuple(Fr(x).limit_denominator(1000) for x in v) for k, v in zip('ABCDEF', (M10.A7, M10.B7, M10.C7, M10.D7, M10.E7, M10.F7))}
eq('算10-7 図の座標（A〜F）が、解の配置と同じ', [fig7[k] for k in 'ABCDEF'], list(sol_pts7[:6]))
eq('算10-7 角Aは直角（辺ABとACが垂直）', (fig7['B'][0] - fig7['A'][0]) * (fig7['C'][0] - fig7['A'][0]) + (fig7['B'][1] - fig7['A'][1]) * (fig7['C'][1] - fig7['A'][1]), 0)
eq('算10-7 EはBC上にある（B・E・Cが一直線）', tri_area(fig7['B'], fig7['E'], fig7['C']), 0)

# =====================================================================================
# 第08セット 規則性（奇数を段に並べる）
# =====================================================================================
s8 = SETS[7]
odds8 = iter(range(1, 10 ** 6, 2))
rows8 = [[next(odds8) for _ in range(n)] for n in range(1, 41)]
tab8 = [[int(x) for x in r[1:]] for r in s8['table']['rows'][:5]]
eq('算10-8 表の1〜5段目が、実際に並べたものと同じ', tab8, rows8[:5])
eq('算10-8(1) 8段目の右はし', a_(8, 1), rows8[int(grab(r'(\d+)段目の、右はし', q_text(M10, 8, 1))) - 1][-1])
x8 = int(grab(r'^(\d+)は', q_text(M10, 8, 2)))
where8 = [(i + 1, len(r) - j) for i, r in enumerate(rows8) for j, v in enumerate(r) if v == x8]               # (段, 右から何番目)
eq('算10-8(2) 299の位置（段・右から）', a_(8, 2), list(map(Fr, where8[0])))
sums8 = [int(x) for x in re.findall(r'(\d+)、', q_text(M10, 8, 3))[:4]]
eq('算10-8(3) 問題文の、1〜4段目の和', sums8, [sum(r) for r in rows8[:4]])
eq('算10-8(3) 10段目の和', a_(8, 3), sum(rows8[int(grab(r'(\d+)段目の数の和', q_text(M10, 8, 3))) - 1]))
t8 = int(grab(r'が(\d+)になる', q_text(M10, 8, 4)))
r8 = [i + 1 for i, r in enumerate(rows8) if sum(r) == t8]
eq('算10-8(4) 和が3375になる段は、1つだけ', len(r8), 1)
eq('算10-8(4) その段と、左はしの数', a_(8, 4), [Fr(r8[0]), Fr(rows8[r8[0] - 1][0])])

# =====================================================================================
# 第09セット 正方形をジグザグに重ねた図形
# =====================================================================================
s9 = SETS[8]
side9 = int(grab(r'1辺が(\d+)cm', lead_of(9)))
dx9 = int(grab(r'右へ(\d+)cm', lead_of(9)))
dy9 = int(grab(r'上へ(\d+)cm', lead_of(9)))
dy9b = int(grab(r'下へ(\d+)cm', lead_of(9)))
eq('算10-9 上へのずれと、下へのずれが同じ', dy9, dy9b)


def squares9(n):
    """k枚目（0から）の正方形のマス。右へ dx9 ずつ、上と下へ dy9 を、かわるがわるずらす。"""
    out = []
    for k in range(n):
        y0 = dy9 if k % 2 == 1 else 0
        out.append({(k * dx9 + i, y0 + j) for i in range(side9) for j in range(side9)})
    return out


def cells9(n):
    return set().union(*squares9(n))


def edges9(cs):
    """ぬりつぶした格子（単位の正方形）のまわりの、単位の辺の数。"""
    return sum(1 for (x, y) in cs for nx, ny in ((x + 1, y), (x - 1, y), (x, y + 1), (x, y - 1)) if (nx, ny) not in cs)


def corners9(cs):
    """図形の頂点（まがり角）になる格子点。まわりの4つのマスのうち、1つか3つがぬりつぶされている点。"""
    pts, diag = set(), 0
    for x in range(-1, max(c[0] for c in cs) + 2):
        for y in range(-1, max(c[1] for c in cs) + 2):
            around = [(x - 1, y - 1) in cs, (x, y - 1) in cs, (x - 1, y) in cs, (x, y) in cs]
            if sum(around) in (1, 3):
                pts.add((x, y))
            elif sum(around) == 2 and around[0] == around[3]:
                diag += 1
    assert diag == 0
    return pts


def holes9(cs):
    """図形の中に、あながないか（外からつながっていない空白がないか）。外の空白から、ひろげて、たどり着けるか。"""
    x0, x1, y0, y1 = -1, max(c[0] for c in cs) + 2, -1, max(c[1] for c in cs) + 2
    outside, stack = set(), [(x0, y0)]
    while stack:
        p = stack.pop()
        if p in outside or p in cs or not (x0 <= p[0] <= x1 and y0 <= p[1] <= y1):
            continue
        outside.add(p)
        stack += [(p[0] + 1, p[1]), (p[0] - 1, p[1]), (p[0], p[1] + 1), (p[0], p[1] - 1)]
    return [(x, y) for x in range(x0, x1 + 1) for y in range(y0, y1 + 1) if (x, y) not in cs and (x, y) not in outside]


per9 = {n: edges9(cells9(n)) for n in range(1, 41)}
area9 = {n: len(cells9(n)) for n in range(1, 41)}
vert9 = {n: len(corners9(cells9(n))) for n in range(1, 41)}
eq('算10-9 どの枚数でも、図形に、あなはない（周がひとつながり）', [n for n in range(1, 41) if holes9(cells9(n))], [])
eq('算10-9 周は10n＋6、面積は14n＋2（実際に数えた値が、1次式になる）', [(per9[n] - per9[1]) // (n - 1) for n in range(2, 41)] + [(area9[n] - area9[1]) / (n - 1) for n in range(2, 41)], [10] * 39 + [14] * 39)


def overlaps9(n):
    """となり合う2枚どうしの重なる面積の合計。ほかの組（1枚おいた正方形どうしなど）が重ならないことも確かめる。"""
    sq = squares9(n)
    far = sum(len(sq[a] & sq[b]) for a in range(n) for b in range(a + 2, n))
    near = sum(len(sq[a] & sq[a + 1]) for a in range(n - 1))
    return near, far


eq('算10-9 図2の多角形の頂点が、3枚を重ねた図形のまがり角と同じ', {tuple(p) for p in M10.U9}, corners9(cells9(3)))
eq('算10-9 図2の多角形の周が、3枚の周と同じ', sum(abs(M10.U9[i][0] - M10.U9[i - 1][0]) + abs(M10.U9[i][1] - M10.U9[i - 1][1]) for i in range(len(M10.U9))), per9[3])
eq('算10-9(1) 5枚の周', a_(9, 1), per9[int(grab(r'(\d+)枚重ねてできる図形の周', q_text(M10, 9, 1)))])
p9 = int(grab(r'周の長さが(\d+)cmになるのは', q_text(M10, 9, 2)))
eq('算10-9(2) 周が156cmになる枚数', a_(9, 2), [n for n in per9 if per9[n] == p9][0])
eq('算10-9(2) 枚数は、1つだけ', len([n for n in per9 if per9[n] == p9]), 1)
eq('算10-9(3) 12枚の面積', a_(9, 3), area9[int(grab(r'(\d+)枚重ねてできる図形の面積', q_text(M10, 9, 3)))])
p94 = int(grab(r'周の長さが(\d+)cmになるとき', q_text(M10, 9, 4)))
n94 = [n for n in per9 if per9[n] == p94]
eq('算10-9(4) 周が106cmになるときの枚数は、1つだけ', len(n94), 1)
eq('算10-9(4) そのときの面積', a_(9, 4), area9[n94[0]])
eq('算10-9 となり合う2枚以外は、重ならない（面積の式が成り立つ）', [overlaps9(n)[1] for n in range(2, 14)], [0] * 12)
eq('算10-9 重なる部分の面積の合計＝(枚数－1)×((たて)×(横))', [overlaps9(n)[0] for n in range(1, 10)], [(n - 1) * (side9 - dx9) * (side9 - dy9) for n in range(1, 10)])

# =====================================================================================
# 第10セット 流水算（エンジンが止まった船）
# =====================================================================================
s10 = SETS[9]
f10 = s10['fig']['args']
pts10 = [(Fr(a), Fr(b)) for a, b in f10['pts']]


def simulate10(still, cur, Dq, t_stop, t_fix, dt=Fr(1, 60)):
    """1/60分ごとに、船を動かす。時速（km/時）を、分あたりに直して、道のりをたしていく。Q港（道のり Dq）に着いたら、向きをかえる。"""
    x, t, up = Fr(0), Fr(0), True
    track = {Fr(0): Fr(0)}
    while x >= 0 and t < 400:
        if up:
            v = (still - cur) if not (t_stop <= t < t_fix) else -cur
        else:
            v = -(still + cur)                                        # 下り：P港の向き（道のりがへる）
        x += v * dt / 60
        t += dt
        if up and x >= Dq:
            up = False
            x = Dq
        if not up and x <= 0:
            x = Fr(0)
            track[t] = x
            break
        track[t] = x
    return track


# グラフの点から決まること：30分後と60分後の道のりの差（流された道のり）、はじめの30分に上った道のり
t_stop10, t_fix10 = pts10[1][0], pts10[2][0]
up_dist10 = pts10[1][1]
drift10 = pts10[1][1] - pts10[2][1]
cur10 = drift10 / ((t_fix10 - t_stop10) / 60)                           # 流された道のり ÷ 流された時間（時間）
up10 = up_dist10 / (t_stop10 / 60)                                       # 上りの速さ
still10 = up10 + cur10
Dq10 = pts10[3][1]
trk10 = simulate10(still10, cur10, Dq10, t_stop10, t_fix10)
at10 = lambda m: trk10[Fr(m)]
eq('算10-10 グラフの点（30・60・90・125分後）が、船を動かしたようすと合う', [at10(m) for m in (30, 60, 90)], [pts10[1][1], pts10[2][1], pts10[3][1]])
end10 = max(t for t, x in trk10.items() if x > 0) + Fr(1, 60)
eq('算10-10 グラフの終点（P港にもどる時こく）', (end10, trk10[end10]), (pts10[4][0], 0))
eq('算10-10(1) 川の流れの速さ', a_(10, 1), cur10)
eq('算10-10(1) 流された時間（30分後〜60分後）は、グラフの目もりと同じ', [x for x, _ in f10['xticks'][:2]], [30, 60])
# 速さの組を、1つずつためして、グラフの2点（30分後8km・60分後6km）と合うものをさがす（時速の整数）
fit10 = [(w, c) for w in range(1, 61) for c in range(0, w)
         if Fr(w - c) * Fr(t_stop10, 60) == up_dist10 and up_dist10 - Fr(c) * Fr(t_fix10 - t_stop10, 60) == pts10[2][1]]
eq('算10-10(2) 静水時の速さ（流れの速さ・静水時の速さの組は、1つだけ）', (a_(10, 2), len(fit10)), (fit10[0][0], 1))
eq('算10-10(2) その組の流れの速さ', fit10[0][1], cur10)
eq('算10-10(3) ア・イ（Q港までの道のり・P港にもどる時こく）', a_(10, 3), [Dq10, end10])
no_fail10 = Dq10 / (still10 - cur10) * 60                                # エンジンが止まらなければ、Q港に着く時刻（分）
late10 = pts10[3][0] - no_fail10
m10, s10_ = divmod(late10 * 60, 60)
eq('算10-10(4) 止まらなければ、何分何秒早いか', ans(M10, 10, 4), f'{int(m10)}分{int(s10_)}秒')
eq('算10-10(4) 秒が整数', (late10 * 60).denominator, 1)
eq('算10-10 図の目もり：アの位置がQ港の道のり、イの位置が終点の時刻', ([(v, l) for v, l in f10['yticks'] if l == 'ア'], [(v, l) for v, l in f10['xticks'] if l == 'イ']), ([(Dq10, 'ア')], [(end10, 'イ')]))
eq('算10-10 グラフの点が、図の点線の折れ点と同じ', [tuple(Fr(x) for x in g) for g in f10['guides']], [pts10[1], pts10[2], pts10[3]])

# =====================================================================================
# 図の目もり・ラベルと、問題文・データの数値が合うか
# =====================================================================================
eq('算10-2 図のグラフの記号が ア・イ・ウ', [lab for lab, _ in f2['graphs']], ['ア', 'イ', 'ウ'])
eq('算10-2 3つのグラフは、どれも、0秒後が12cm・12秒後までの点', [(pts[0], pts[-1][0]) for _, pts in f2['graphs']], [((0, 12), 12)] * 3)
eq('算10-3 グラフの目もり（x：2〜20、y：300〜2400）', (f3['xticks'][0][0], f3['xticks'][-1][0], f3['yticks'][0][0], f3['yticks'][-1][0], f3['xmax'], f3['ymax']), (2, 20, 300, 2400, 20, 2400))
eq('算10-4 グラフの目もり・点線が、グラフの折れ点（時間・高さ）と同じ', ([t for t, _ in f4['xticks']], [h for _, h in f4['guides']], [(t, h) for t, h in f4['guides']]), ([int(p[0]) for p in pts4[1:-1]], [int(p[1]) for p in pts4[1:-1]], [(int(p[0]), int(p[1])) for p in pts4[1:-1]]))
eq('算10-4 縦軸の目もりが、10cmごと（ブロックの1段ごと）', [u for u, _ in f4['yticks']], [10, 20, 30, 40])
texts7 = [pr[2] for pr in s7['fig']['args']['panels'][0]['prims'] if pr[0] == 'text']
eq('算10-7 図の書き込み（10cm・DF＝6cm）が、問題文の数値と同じ', sorted(texts7), sorted([f'{AB7}cm', f'DF＝{DF7}cm']))
texts9 = sorted(pr[2] for pn in s9['fig']['args']['panels'] for pr in pn['prims'] if pr[0] == 'text')
eq('算10-9 図1の書き込み（4cm・3cm・2cm）が、問題文の数値と同じ', texts9, sorted([f'{side9}cm', f'{dx9}cm', f'{dy9}cm']))

# =====================================================================================
# 体裁：全小問の、答えと解説
# =====================================================================================
ARITH = re.compile(r'(?<![A-Za-z0-9.：:…<>/＋－×÷＝(（])((?:[\d.]+|<\d+/\d+>|\((?:[\d.＋－×÷]|<\d+/\d+>)+\))(?:[＋－×÷](?:[\d.]+|<\d+/\d+>|\((?:[\d.＋－×÷]|<\d+/\d+>)+\)))*(?:＝(?:[\d.]+|<\d+/\d+>|\((?:[\d.＋－×÷]|<\d+/\d+>)+\))(?:[＋－×÷](?:[\d.]+|<\d+/\d+>|\((?:[\d.＋－×÷]|<\d+/\d+>)+\)))*)+)(?![A-Za-z0-9.：:])')


def arith_errors(ex):
    """解説の中の「A＝B＝C」の形の等式（数と＋－×÷とかっこだけでできたもの）を、すべて値で確かめる。"""
    bad = []
    for m in ARITH.finditer(ex):
        parts = m.group(1).split('＝')
        try:
            vs = [val(p) for p in parts]
        except Exception as e:                                        # noqa: BLE001
            bad.append((m.group(1), 'よめない', str(e)))
            continue
        if len(set(vs)) > 1:
            bad.append((m.group(1), [str(v) for v in vs]))
    return bad


bad_ex, bad_ans = [], []
nq = 0
for i, st in enumerate(SETS, 1):
    for j, q in enumerate(st['qs'], 1):
        nq += 1
        bad_ex += [(i, j) + b for b in arith_errors(q['ex'])]
        a_list = q['ans'] if isinstance(q['ans'], list) else [q['ans']]
        for a in a_list:
            for tok in re.findall(r'<\d+/\d+>|\d+\.\d+|\d+', a):
                if tok not in q['ex']:
                    bad_ans.append((i, j, '答えの数が解説にない', tok))
            for sym in re.findall(r'[アイウエオ]', a):
                if sym not in q['ex']:
                    bad_ans.append((i, j, '答えの記号が解説にない', sym))
eq(f'算10 解説の中の等式（A＝B＝C）が、すべて成り立つ（{nq}小問）', bad_ex, [])
eq(f'算10 答えの数・記号が、解説にある（{nq}小問）', bad_ans, [])
eq('算10 10セット・各セット3〜4問', [len(st['qs']) for st in SETS], [4] * 10)
eq('算10 第07〜10セットの note に、●●と、大問10がないことを書いている', [('●●' in st['note'] and '大問10がない' in st['note']) for st in SETS[6:]], [True] * 4)
eq('算10 ANALYSIS に、補いの年（2021・2020・2019・2014）が●●つきで入っている', sorted(r[0] for r in M10.ANALYSIS['years'] if '●●' in r[1]), ['2014', '2019', '2020', '2021'])

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
