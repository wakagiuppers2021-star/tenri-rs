"""算数 大問3 の検算。答え（データ）を、問題文の数・図の座標から、解説とは別の方法（総あたり・分数・座標・マスの変換・格子の数え上げ）で求めなおして比べる。

import すると検算が走る（tools/check_tenri_rs.py が、check_sansu*.py をすべて import する）。単独でも動く：cd tools && python -X utf8 check_sansu3.py
"""
import itertools
import math
import re
from fractions import Fraction

from check_common import FAIL, ans, eq, q_text, val
import tenri_rs_sansu3 as M3

S = M3.SETS
KANA = 'アイウエオカキク'


def lead(s):
    return S[s - 1]['lead']


def fr(text):
    """文中の <3/8> を、Fraction にして、ならべて返す。"""
    return [Fraction(int(a), int(b)) for a, b in re.findall(r'<(\d+)/(\d+)>', text)]


def ratios(text):
    """文中の「3：5：4」の形を、整数の組にして、ならべて返す。"""
    return [tuple(int(x) for x in m.split('：')) for m in re.findall(r'\d+(?:：\d+)+', text)]


def hm(minutes):
    h, m = divmod(int(minutes), 60)
    return f'{h}時間{m}分' if h else f'{m}分'


def kana_pick(flags):
    return '・'.join(KANA[i] for i, f in enumerate(flags) if f)


# ======================= 第01セット 赤玉と白玉 =======================
total = int(re.search(r'合わせて(\d+)個', lead(1))[1])
wf = fr(lead(1))[0]
white = next(w for w in range(total + 1) if Fraction(w, total) == wf)                      # 白玉の個数（総あたり）
red = next(r for r in range(total + 1) if r + white == total)
eq('算3-1(1) 赤玉', ans(M3, 1, 1), f'{red}個')

target = fr(q_text(M3, 1, 2))[0]
eq('算3-1(2) 赤玉を入れて、白玉が全体の割合になる', ans(M3, 1, 2),
   '{}個'.format(next(x for x in range(0, 20000) if Fraction(white, total + x) == target)))

w3, r3, b3 = ratios(q_text(M3, 1, 3))[0]
assert red * w3 == white * r3, '赤玉と白玉の比が、比とあっていない'
eq('算3-1(3) 白：赤：青の比から青玉', ans(M3, 1, 3),
   '{}個'.format(next(y for y in range(0, 5000) if white * b3 == y * w3)))

(wa, ba), (ra, bb) = ratios(q_text(M3, 1, 4))                                                # 白：青、赤：青
sols = [(r, b) for r in range(red + 1) for b in range(0, 3000) if white * ba == b * wa and (red - r) * bb == b * ra]
assert len(sols) == 1, sols
eq('算3-1(4) 取り出した赤玉（赤を取り出し、青を入れる）', ans(M3, 1, 4), f'{sols[0][0]}個')

# ======================= 第02セット 流水算 =======================
D = int(re.search(r'道のりは(\d+)km', lead(2))[1])
still = int(re.search(r'船の速さは、時速(\d+)km', lead(2))[1])
t_down = int(re.search(r'下ると(\d+)時間', lead(2))[1])
speeds = [Fraction(k, 4) for k in range(0, 4 * still)]                                       # 流れの速さの候補（4分の1km刻み）
v1 = [v for v in speeds if Fraction(D) / (still + v) == t_down]
assert len(v1) == 1
v1 = v1[0]
eq('算3-2(1) 1日目の流れの速さ', ans(M3, 2, 1), f'時速{v1}km')
t_up = int(re.search(r'(\d+)時間かかりました', q_text(M3, 2, 2))[1])
v2 = [v for v in speeds if Fraction(D) / (still - v) == t_up][0]
d = v2 - v1
eq('算3-2(2) 流れの速さの変化', ans(M3, 2, 2), f'時速{abs(d)}km{"速く" if d > 0 else "おそく"}なった')
rt = Fraction(D) / (still + v1) + Fraction(D) / (still - v1)
eq('算3-2(3) 往復の時間', ans(M3, 2, 3), hm(rt * 60))
# (4) 秒ごとに、船の位置を進めて、数える（エンジンが止まっている間は、流れの速さで進む）
q4 = q_text(M3, 2, 4)
stop_km = int(re.search(r'から(\d+)kmの地点', q4)[1])
drift_min = int(re.search(r'(\d+)時間(\d+)分のあいだ', q4)[1]) * 60 + int(re.search(r'(\d+)時間(\d+)分のあいだ', q4)[2])
pos, sec, drifted = Fraction(0), 0, 0
down_v, flow_v = Fraction(still + v1, 3600), Fraction(v1, 3600)                             # km/秒
while pos < D:
    if pos >= stop_km and drifted < drift_min * 60:
        pos += flow_v
        drifted += 1
    else:
        pos += down_v
    sec += 1
eq('算3-2(4) エンジンが止まったときの、かかった時間', ans(M3, 2, 4), hm(Fraction(sec, 60)))

# ======================= 第03セット 論理（総あたり） =======================
ps = ['A', 'B', 'C']
st1 = [
    ('A「Bさんは銅メダルではありません」', lambda m: m['B'] != '銅'),
    ('B「私は銀メダルでした」', lambda m: m['B'] == '銀'),
    ('C「Aさんは金メダルでした」', lambda m: m['A'] == '金'),
]
for text, _ in st1:
    assert text in q_text(M3, 3, 1), text
sol1 = []
for perm in itertools.permutations(['金', '銀', '銅']):
    m = dict(zip(ps, perm))
    if sum(1 for _, f in st1 if not f(m)) == 1:                                              # うそは、ちょうど1人
        sol1.append(perm)
assert len(sol1) == 1, sol1
eq('算3-3(1) 3人のメダル', ans(M3, 3, 1), list(sol1[0]))

p4 = ['A', 'B', 'C', 'D']
st2 = [
    ('A「私は2位でした」', lambda r: r['A'] == 2),
    ('B「Cさんは4位でした」', lambda r: r['C'] == 4),
    ('C「私の順位は、Dさんのとなりです」', lambda r: abs(r['C'] - r['D']) == 1),
    ('D「Bさんは1位でした」', lambda r: r['B'] == 1),
]
for text, _ in st2:
    assert text in q_text(M3, 3, 2), text
sol2 = []
for perm in itertools.permutations([1, 2, 3, 4]):
    r = dict(zip(p4, perm))
    if sum(1 for _, f in st2 if not f(r)) == 1:
        sol2.append(perm)
assert len(sol2) == 1, sol2
eq('算3-3(2) 4人の順位', ans(M3, 3, 2), [f'{x}位' for x in sol2[0]])

# (3) わった人は、うそを言い、わっていない3人は、本当のことを言う
st3 = [
    ('A「Bさんがわりました」', lambda X: X == 'B'),
    ('B「Dさんがわりました」', lambda X: X == 'D'),
    ('C「私はわっていません」', lambda X: X != 'C'),
    ('D「Bさんは、うそを言っています」', lambda X: X == 'B'),                                  # Bがうそを言っている ＝ Bがわった人
]
for text, _ in st3:
    assert text in q_text(M3, 3, 3), text
culprits = [X for X in p4 if all(f(X) == (p != X) for p, (_, f) in zip(p4, st3))]
assert len(culprits) == 1, culprits
eq('算3-3(3) ガラスをわった人', ans(M3, 3, 3), culprits[0])

# ======================= 第04セット じゃんけんの得点 =======================
win_pt = int(re.search(r'勝った人には(\d+)点', lead(4))[1])
draw_pt = int(re.search(r'2人に(\d+)点ずつ', lead(4))[1])


def score(seq):
    """seq は、ある人から見た、1回ごとの結果（勝ち・あいこ・負け）。"""
    return sum({'勝ち': win_pt, 'あいこ': draw_pt, '負け': 0}[x] for x in seq)


seq_a = re.findall(r'勝ち|あいこ|負け', q_text(M3, 4, 1))
assert len(seq_a) == int(re.match(r'(\d+)回', q_text(M3, 4, 1))[1])
seq_b = [{'勝ち': '負け', '負け': '勝ち', 'あいこ': 'あいこ'}[x] for x in seq_a]
eq('算3-4(1) 弟の得点', ans(M3, 4, 1), f'{score(seq_b)}点')

n2, a2, b2 = (int(x) for x in re.search(r'(\d+)回じゃんけんをして、兄は(\d+)回、弟は(\d+)回勝ち', q_text(M3, 4, 2)).groups())
games = ['兄'] * a2 + ['弟'] * b2 + ['あいこ'] * (n2 - a2 - b2)                              # 1回ごとの結果を、ならべる
tot = sum({'兄': win_pt, '弟': win_pt, 'あいこ': 2 * draw_pt}[g] for g in games)
eq('算3-4(2) 得点の合計', ans(M3, 4, 2), f'{tot}点')

mm = re.search(r'兄の得点は(\d+)点、弟の得点は(\d+)点で、じゃんけんをした回数は全部で(\d+)回', q_text(M3, 4, 3))
sa, sb, n3 = int(mm[1]), int(mm[2]), int(mm[3])
sol4 = [(a, b, n3 - a - b) for a in range(n3 + 1) for b in range(n3 + 1 - a)
        if win_pt * a + draw_pt * (n3 - a - b) == sa and win_pt * b + draw_pt * (n3 - a - b) == sb]
assert len(sol4) == 1, sol4
eq('算3-4(3) あいこの回数・兄が勝った回数', ans(M3, 4, 3), [f'{sol4[0][2]}回', f'{sol4[0][0]}回'])

ratio = Fraction(re.search(r'(\d+\.\d+)倍', q_text(M3, 4, 4))[1])
cands = [(a, b) for a in range(0, 60) for b in range(0, 60) if a + b >= 1 and win_pt * a == ratio * win_pt * b]   # あいこがないので、得点は勝った回数×3
eq('算3-4(4) あいこなしで、得点が2.5倍になる最少の回数', ans(M3, 4, 4), f'{min(a + b for a, b in cands)}回')


# ======================= 第05セット 図形の対称（頂点の座標） =======================
def close(p, q, eps=2e-3):
    return abs(p[0] - q[0]) < eps and abs(p[1] - q[1]) < eps


def same_set(P, Q):
    return len(P) == len(Q) and all(any(close(p, q) for q in Q) for p in P) and all(any(close(p, q) for p in P) for q in Q)


def is_point_sym(poly):
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    return same_set(poly, [(2 * cx - x, 2 * cy - y) for x, y in poly])


def axes(poly):
    """線対称の軸の本数。軸は、ある頂点を通るか、ある2頂点の垂直二等分線なので、その候補を、すべて調べる。"""
    cx = sum(p[0] for p in poly) / len(poly)
    cy = sum(p[1] for p in poly) / len(poly)
    angles = [math.atan2(y - cy, x - cx) for x, y in poly if abs(x - cx) + abs(y - cy) > 1e-9]
    angles += [math.atan2(q[1] - p[1], q[0] - p[0]) + math.pi / 2 for p, q in itertools.combinations(poly, 2)]
    found = []
    for th in angles:
        c2, s2 = math.cos(2 * th), math.sin(2 * th)
        ref = [(cx + (x - cx) * c2 + (y - cy) * s2, cy + (x - cx) * s2 - (y - cy) * c2) for x, y in poly]
        if same_set(poly, ref):
            t = th % math.pi
            if not any(min(abs(t - u), math.pi - abs(t - u)) < 1e-3 for u in found):
                found.append(t)
    return len(found)


def side_lens(poly):
    return [math.dist(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]


def parallel(p1, p2, q1, q2):
    return abs((p2[0] - p1[0]) * (q2[1] - q1[1]) - (p2[1] - p1[1]) * (q2[0] - q1[0])) < 1e-6


def check_name(name, poly):
    """図の頂点が、名前の図形になっているか。"""
    L = side_lens(poly)
    n = len(poly)
    close_ = lambda a, b: abs(a - b) < 2e-3
    if name == '二等辺三角形':
        return n == 3 and sum(close_(L[i], L[(i + 1) % 3]) for i in range(3)) == 1
    if name == '台形':
        pairs = [parallel(poly[i], poly[(i + 1) % 4], poly[(i + 2) % 4], poly[(i + 3) % 4]) for i in range(4)]
        return n == 4 and sum(pairs[:2]) == 1
    if name == '平行四辺形':
        return n == 4 and parallel(poly[0], poly[1], poly[3], poly[2]) and parallel(poly[1], poly[2], poly[0], poly[3]) and not close_(L[0], L[1])
    if name == 'たこ形':
        return n == 4 and ((close_(L[0], L[1]) and close_(L[2], L[3])) or (close_(L[1], L[2]) and close_(L[3], L[0]))) and not close_(L[0], L[2]) and not close_(L[1], L[3]) \
            and not all(close_(L[0], x) for x in L)
    if name == 'ひし形':
        return n == 4 and all(close_(L[0], x) for x in L) and not close_(math.dist(poly[0], poly[2]), math.dist(poly[1], poly[3]))
    if name in ('正八角形', '正五角形'):
        k = 8 if name == '正八角形' else 5
        diag = [math.dist(poly[i], poly[(i + 2) % n]) for i in range(n)]
        return n == k and all(close_(L[0], x) for x in L) and all(close_(diag[0], x) for x in diag)
    if name == 'L字形':
        return n == 6
    raise ValueError(name)


shapes5 = S[4]['fig']['args']['shapes']
assert len(shapes5) == 8 and re.search(r'ア〜(.)', lead(5))[1] == KANA[len(shapes5) - 1]
for nm, poly in shapes5:
    assert check_name(nm, poly), nm
ax5 = [axes(p) for _, p in shapes5]
pt5 = [is_point_sym(p) for _, p in shapes5]
eq('算3-5(1) 線対称', ans(M3, 5, 1), kana_pick([a > 0 for a in ax5]))
eq('算3-5(2) 点対称', ans(M3, 5, 2), kana_pick(pt5))
eq('算3-5(3) 線対称でも点対称でもある', ans(M3, 5, 3), kana_pick([a > 0 and p for a, p in zip(ax5, pt5)]))
eq('算3-5(4) どちらでもない', ans(M3, 5, 4), kana_pick([a == 0 and not p for a, p in zip(ax5, pt5)]))
eq('算3-5 対称の軸の本数（解説の本数）', ax5, [1, 0, 0, 1, 2, 8, 5, 0])

# ======================= 第06セット 割合 =======================
N6 = int(re.search(r'全校生徒は(\d+)人', lead(6))[1])
f_male, f_glass = fr(lead(6))
males = [i for i in range(N6) if i < N6 * f_male]                                            # 男子の番号（番号を、生徒1人ずつにわりあてる）
M6 = len(males)
F6 = N6 - M6
eq('算3-6(1) 女子の人数', ans(M3, 6, 1), f'{F6}人')
G6 = N6 * f_glass
mg = int(re.search(r'男子が(\d+)人', q_text(M3, 6, 2))[1])
fg = G6 - mg
eq('算3-6(2) 女子のメガネの割合', ans(M3, 6, 2), f'{fg * 100 / F6:g}%')
assert all(int(re.search(r'男子が(\d+)人', q_text(M3, 6, k))[1]) == mg for k in (3, 4))
eq('算3-6(3) メガネの生徒のうち男子の割合（割）', ans(M3, 6, 3), f'{Fraction(mg, 1) / G6 * 10:g}割')
nm_, nf_ = M6 - mg, F6 - fg
g_ = math.gcd(int(nm_), int(nf_))
eq('算3-6(4) メガネなしの男女の比', ans(M3, 6, 4), f'{int(nm_) // g_}：{int(nf_) // g_}')

# ======================= 第07セット リレーの走る順（総あたり） =======================
runners = 'ABCDE'
perms7 = list(itertools.permutations(range(5)))                                              # perm[k]＝runners[k] の走る順番（0が第1走者）
eq('算3-7(1) 5人の順番', ans(M3, 7, 1), f'{len(perms7)}通り')
conds7 = [
    ('(ア) AはBより先に走ります。', lambda p: p[0] < p[1]),
    ('(イ) BはDより先に走ります。', lambda p: p[1] < p[3]),
    ('(ウ) CはDからバトンを受け取ります。', lambda p: p[2] == p[3] + 1),
    ('(エ) Cは最終走者ではありません。', lambda p: p[2] != 4),
]
for text, _ in conds7:
    assert text in q_text(M3, 7, 2), text
sol7 = [p for p in perms7 if all(f(p) for _, f in conds7)]
assert len(sol7) == 1
eq('算3-7(2) 条件から決まる順', ans(M3, 7, 2), '→'.join(runners[k] for k in sorted(range(5), key=lambda k: sol7[0][k])))
eq('算3-7(3) AとBが続けて走る', ans(M3, 7, 3), f'{sum(1 for p in perms7 if abs(p[0] - p[1]) == 1)}通り')
eq('算3-7(4) CがEより先', ans(M3, 7, 4), f'{sum(1 for p in perms7 if p[2] < p[4])}通り')
eq('算3-7(5) AとBが続けては走らない', ans(M3, 7, 5), f'{sum(1 for p in perms7 if abs(p[0] - p[1]) != 1)}通り')


# ======================= 第08セット 正方形4個の対称（マスの変換） =======================
def norm(cells):
    mx, my = min(c[0] for c in cells), min(c[1] for c in cells)
    return frozenset((x - mx, y - my) for x, y in cells)


def connected(cells):
    cells = set(cells)
    seen, todo = set(), [next(iter(cells))]
    while todo:
        c = todo.pop()
        if c in seen:
            continue
        seen.add(c)
        todo += [(c[0] + dx, c[1] + dy) for dx, dy in ((1, 0), (-1, 0), (0, 1), (0, -1)) if (c[0] + dx, c[1] + dy) in cells]
    return seen == cells


REFL = [lambda x, y: (-x, y), lambda x, y: (x, -y), lambda x, y: (y, x), lambda x, y: (-y, -x)]           # 縦・横・ななめ2本の折り返し


def n_axes(cells):
    return sum(1 for R in REFL if norm([R(x, y) for x, y in cells]) == norm(cells))


def n_axes_box(cells):
    """別の数え方：外わく（最小の長方形）のまん中を通る4本の線で、折り返す。"""
    xs, ys = [c[0] for c in cells], [c[1] for c in cells]
    cx, cy = Fraction(min(xs) + max(xs), 2), Fraction(min(ys) + max(ys), 2)
    maps = [lambda x, y: (2 * cx - x, y), lambda x, y: (x, 2 * cy - y),
            lambda x, y: (cx + (y - cy), cy + (x - cx)), lambda x, y: (cx - (y - cy), cy - (x - cx))]
    return sum(1 for m in maps if {m(x, y) for x, y in cells} == {(Fraction(x), Fraction(y)) for x, y in cells})


def is_point_cells(cells):
    return norm([(-x, -y) for x, y in cells]) == norm(cells)


cells8 = S[7]['fig']['args']['items']
assert len(cells8) == 7 and re.search(r'ア〜(.)', lead(8))[1] == KANA[len(cells8) - 1]
assert all(len(set(c)) == 4 and connected(c) for c in cells8)
ROT = [lambda x, y: (x, y), lambda x, y: (-y, x), lambda x, y: (-x, -y), lambda x, y: (y, -x)]
canon = lambda cells: min(tuple(sorted(norm([R(x, y) for x, y in cells]))) for R in ROT)          # 回して重なるものは、同じ形（裏返しは、ちがう形）
assert len({canon(c) for c in cells8}) == 7                                                   # 7つとも、ちがう形（S字とZ字、L字とJ字は、鏡うつしなので、別）
for c in cells8:
    assert n_axes(c) == n_axes_box(c)
ax8 = [n_axes(c) for c in cells8]
pt8 = [is_point_cells(c) for c in cells8]
eq('算3-8(1) 線対称', ans(M3, 8, 1), kana_pick([a > 0 for a in ax8]))
eq('算3-8(2) 点対称', ans(M3, 8, 2), kana_pick(pt8))
eq('算3-8(3) 線対称でも点対称でもある', ans(M3, 8, 3), kana_pick([a > 0 and p for a, p in zip(ax8, pt8)]))
eq('算3-8(4) 対称の軸がちょうど2本', ans(M3, 8, 4), kana_pick([a == 2 for a in ax8]))
eq('算3-8 対称の軸の本数（解説の本数）', ax8, [1, 0, 0, 2, 4, 0, 0])

# ======================= 第09セット 小問6つ =======================
q9 = [q_text(M3, 9, k) for k in range(1, 7)]
n_, hp, tp, tot9 = (int(x) for x in re.search(r'(\d+)回投げて、表が出ると(\d+)点、裏が出ると(\d+)点をもらえるゲームをしました。\d+回投げたとき、得点の合計は(\d+)点', q9[0]).groups())
eq('算3-9(1) コインの表の回数', ans(M3, 9, 1), '{}回'.format(next(h for h in range(n_ + 1) if hp * h + tp * (n_ - h) == tot9)))

m = re.search(r'(\d+)人で毎日(\d+)時間ずつ働くと(\d+)日で仕上がる', q9[1])
work = int(m[1]) * int(m[2]) * int(m[3])
m = re.search(r'(\d+)人で毎日(\d+)時間ずつ(\d+)日間働いたあと、のこりを(\d+)人で(\d+)日間で', q9[1])
first = int(m[1]) * int(m[2]) * int(m[3])
hrs = [h for h in (Fraction(k, 4) for k in range(1, 97)) if first + int(m[4]) * int(m[5]) * h == work]
assert len(hrs) == 1
eq('算3-9(2) 仕事算', ans(M3, 9, 2), f'{hrs[0]}時間')

(a1, b1), (a2_, b2_) = ratios(q9[2])[:2]
spent = int(re.search(r'(\d+)円使った', q9[2])[1])
sol9 = [(7 * 0 + k * a1, k * b1) for k in range(1, 5000) if (k * a1 - spent) * b2_ == k * b1 * a2_]          # 兄＝a1×k、弟＝b1×k
assert len(sol9) == 1
eq('算3-9(3) 弟のお金', ans(M3, 9, 3), f'{sol9[0][1]}円')

i1, i2, diff = (int(x) for x in re.search(r'間かくを(\d+)mにする場合と、(\d+)mにする場合では、必要な木の本数が(\d+)本ちがいます', q9[3]).groups())
i3 = int(re.search(r'間かくを(\d+)mにして木を植える', q9[3])[1])
Ls = [L for L in range(1, 3000) if L % i1 == 0 and L % i2 == 0 and abs(L // i1 - L // i2) == diff]
assert len(Ls) == 1 and Ls[0] % i3 == 0
eq('算3-9(4) 植木算', ans(M3, 9, 4), f'{Ls[0] // i3}本')

pn, pe, cnt, cost = (int(x) for x in re.search(r'1冊(\d+)円と、えんぴつ1本(\d+)円を、合わせて(\d+)こ買ったところ、代金は(\d+)円', q9[4]).groups())
sol95 = [k for k in range(cnt + 1) if pn * k + pe * (cnt - k) == cost]
assert len(sol95) == 1
eq('算3-9(5) つるかめ算', ans(M3, 9, 5), f'{sol95[0]}冊')

# (6) xとyの関係を、式にして、反比例か（xとyの積が一定）を、いくつかのxで調べる
lines9 = {ln[0]: ln for ln in q9[5].split('\n')[1:]}
assert list(lines9) == list('アイウエオ')
area = int(re.search(r'面積が(\d+)cm', lines9['ア'])[1])
perim = int(re.search(r'周りの長さが(\d+)cm', lines9['イ'])[1])
rate = int(re.search(r'1分間に(\d+)L', lines9['ウ'])[1])
pages = int(re.search(r'(\d+)ページの本', lines9['エ'])[1])
ribbon = int(re.search(r'(\d+)cmのリボン', lines9['オ'])[1])
rel = {'ア': lambda x: Fraction(area, x), 'イ': lambda x: Fraction(perim, 2) - x, 'ウ': lambda x: rate * x,
       'エ': lambda x: Fraction(pages, x), 'オ': lambda x: ribbon - x}
xs9 = [1, 2, 3, 4, 5]
inverse = [k for k, f in rel.items() if len({x * f(x) for x in xs9}) == 1]
prop = [k for k, f in rel.items() if len({f(x) / x for x in xs9}) == 1]
eq('算3-9(6) 反比例', ans(M3, 9, 6), ['・'.join(inverse)])
eq('算3-9(6) 比例（解説）', prop, ['ウ'])


# ======================= 第10セット 斜線部分の面積（座標・格子の数え上げ） =======================
PI = Fraction(314, 100)
panels = S[9]['fig']['args']['panels']


def shoelace(poly):
    return abs(sum(Fraction(poly[i][0]) * poly[(i + 1) % len(poly)][1] - Fraction(poly[(i + 1) % len(poly)][0]) * poly[i][1] for i in range(len(poly)))) / 2


def in_poly(pt, poly):
    x, y = pt
    inside = False
    for i in range(len(poly)):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            inside = not inside
    return inside


def raster(region, box, step=.04):
    """格子の数え上げ：box のなかを、step 刻みの点（真ん中）でわけて、region に入る点を数え、面積にする。"""
    x0, y0, x1, y1 = box
    nx, ny = int((x1 - x0) / step), int((y1 - y0) / step)
    cnt = sum(1 for i in range(nx) for j in range(ny) if region(x0 + (i + .5) * step, y0 + (j + .5) * step))
    return cnt * step * step


def labels_of(panel):
    return sorted(int(re.match(r'\d+', p[2])[0]) for p in panel['prims'] if p[0] == 'text' and p[2].endswith('cm'))


def prim(panel, kind, k=0):
    return [p for p in panel['prims'] if p[0] == kind][k]


def ok(label, got, want, tol=.01):
    """格子の数え上げの値（本物の円周率）が、答えの値と、1%以内で近いか。"""
    good = abs(got - float(want)) <= tol * float(want)
    eq(label, good, True)


# (1) 長方形から平行四辺形の帯
rect, band = prim(panels[0], 'poly', 0)[1], prim(panels[0], 'poly', 1)[1]
W1, H1 = max(p[0] for p in rect) - min(p[0] for p in rect), max(p[1] for p in rect) - min(p[1] for p in rect)
q1 = q_text(M3, 10, 1)
assert (H1, W1) == tuple(int(x) for x in re.search(r'たて(\d+)cm、よこ(\d+)cm', q1).groups())
assert labels_of(panels[0]) == sorted([W1, H1, int(band[1][0] - band[0][0])])                  # 図の長さの文字が、座標とあっている
a1 = shoelace(rect) - shoelace(band)
eq('算3-10(1) 長方形−平行四辺形（座標）', ans(M3, 10, 1), f'{a1}cm²')
ok('算3-10(1) 格子の数え上げ', raster(lambda x, y: in_poly((x, y), rect) and not in_poly((x, y), band), (0, 0, W1, H1)), a1)

# (2) 平行四辺形ABCDと、辺AD上の点E
P = {nm[2]: nm[1] for nm in panels[1]['prims'] if nm[0] == 'pt'}
A, B, C, Dd, E = P['A'], P['B'], P['C'], P['D'], P['E']
q2 = q_text(M3, 10, 2)
assert parallel(A, Dd, B, C) and parallel(A, B, Dd, C) and math.dist(B, C) == math.dist(A, Dd)
assert (math.dist(B, C), math.dist(A, E), abs(A[1] - B[1])) == tuple(float(x) for x in (re.search(r'BCは(\d+)cm', q2)[1], re.search(r'AEは(\d+)cm', q2)[1], re.search(r'高さは(\d+)cm', q2)[1]))
assert E[1] == A[1] and min(A[0], Dd[0]) < E[0] < max(A[0], Dd[0])
assert labels_of(panels[1]) == sorted([int(math.dist(B, C)), int(math.dist(A, E)), int(abs(A[1] - B[1]))])
a2 = shoelace([A, B, E]) + shoelace([E, C, Dd])
eq('算3-10(2) 三角形ABE＋三角形ECD（座標）', ans(M3, 10, 2), f'{a2}cm²')
tri1, tri2 = [A, B, E], [E, C, Dd]
ok('算3-10(2) 格子の数え上げ', raster(lambda x, y: in_poly((x, y), tri1) or in_poly((x, y), tri2), (0, 0, 11, 6)), a2)

# (3) 円と、円に内接する正方形
circ = prim(panels[2], 'circle')
r3 = circ[2]
sq3 = prim(panels[2], 'poly')[1]
assert 2 * r3 == int(re.search(r'直径(\d+)cm', q_text(M3, 10, 3))[1])
assert all(abs(math.hypot(x - circ[1][0], y - circ[1][1]) - r3) < 1e-9 for x, y in sq3)           # 正方形の4つの頂点が、円周上にある
assert len({round(l, 6) for l in side_lens(sq3)}) == 1 and abs(math.dist(sq3[0], sq3[2]) - 2 * r3) < 1e-9
assert labels_of(panels[2]) == [2 * r3]
a3 = PI * r3 * r3 - shoelace(sq3)
eq('算3-10(3) 円−正方形', ans(M3, 10, 3), f'{float(a3):g}cm²')
ok('算3-10(3) 格子の数え上げ（本物の円周率）', raster(lambda x, y: x * x + y * y < r3 * r3 and not in_poly((x, y), sq3), (-r3, -r3, r3, r3)), a3)

# (4) 正方形の中の、4つの円
sq4 = prim(panels[3], 'poly')[1]
circles4 = [p for p in panels[3]['prims'] if p[0] == 'circle']
side4 = sq4[1][0] - sq4[0][0]
q4_ = q_text(M3, 10, 4)
assert side4 == int(re.search(r'1辺(\d+)cm', q4_)[1]) and {c[2] for c in circles4} == {int(re.search(r'半径(\d+)cm', q4_)[1])}
r4 = circles4[0][2]
cs4 = [c[1] for c in circles4]
assert len(circles4) == 4
for (c1, c2) in itertools.combinations(cs4, 2):                                               # となり合う円は、ふれ合う（中心の間が 2r）。ななめの円は、はなれている
    assert math.dist(c1, c2) >= 2 * r4 - 1e-9
assert sum(1 for c1, c2 in itertools.combinations(cs4, 2) if abs(math.dist(c1, c2) - 2 * r4) < 1e-9) == 4
assert all(r4 <= c[0] <= side4 - r4 and r4 <= c[1] <= side4 - r4 and (abs(c[0] - r4) < 1e-9 or abs(c[0] - (side4 - r4)) < 1e-9) and (abs(c[1] - r4) < 1e-9 or abs(c[1] - (side4 - r4)) < 1e-9) for c in cs4)
assert labels_of(panels[3]) == sorted([side4, r4])
a4 = side4 * side4 - 4 * PI * r4 * r4
eq('算3-10(4) 正方形−円4つ', ans(M3, 10, 4), f'{float(a4):g}cm²')
ok('算3-10(4) 格子の数え上げ（本物の円周率）', raster(lambda x, y: not any((x - c[0]) ** 2 + (y - c[1]) ** 2 < r4 * r4 for c in cs4), (0, 0, side4, side4), .08), a4)

# ======================= 解説の中の式 =======================
CHAIN = re.compile(r'((?:\d+(?:\.\d+)?|<(?:\d+ )?\d+/\d+>|[＋−×÷()（）])+)＝(\d+(?:\.\d+)?)')
bad_ex, n_ex = [], 0
for i, st in enumerate(S, 1):
    for j, q in enumerate(st['qs'], 1):
        for left, right in CHAIN.findall(q['ex']):
            if not re.search(r'[＋−×÷]', left):
                continue
            try:
                got = val(left)
            except (ValueError, AssertionError, ZeroDivisionError):
                continue
            n_ex += 1
            if got != Fraction(right):
                bad_ex.append((i, j, left, right, str(got)))
        for tok in re.findall(r'\d+(?:\.\d+)?', q['ans'] if isinstance(q['ans'], str) else '・'.join(q['ans'])):
            if tok not in q['ex']:
                bad_ex.append((i, j, '答えの数が、解説に出てこない', tok))
eq(f'算3 解説の途中の式（{n_ex}個）がすべて成り立つ・答えの数が解説に出てくる', bad_ex, [])

# ======================= 漢字（小学校で習う漢字を中心に。入試の用語の対称・軸・斜線だけは、そのまま使う） =======================
import kanji_grade as KG

EXAM_TERMS = '称軸斜'
bad_k = set()
for st in S:
    texts = [st['title'], st['lead']] + [nm for nm, _ in st.get('fig', {}).get('args', {}).get('shapes', [])]
    for q in st['qs']:
        texts += [q['q'], q['ex'], *q.get('labels', []), q['ans'] if isinstance(q['ans'], str) else ''.join(q['ans'])]
    for t in texts:
        bad_k |= {ch for ch in t if '一' <= ch <= '鿿' and not KG.elementary(ch) and ch not in EXAM_TERMS}
eq('算3 小学校で習わない漢字（対称・軸・斜線をのぞく）', sorted(bad_k), [])

# ======================= 全体の形 =======================
eq('算3-0 セット数', len(S), 10)
eq('算3-0 小問数（各セット）', [len(st['qs']) for st in S], [4, 4, 3, 4, 4, 4, 5, 4, 6, 4])
eq('算3-0 年度（第01〜10セット）', [st['year'] for st in S], [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015])
eq('算3-0 解答の欠けなし', [(i, j) for i, st in enumerate(S, 1) for j, q in enumerate(st['qs'], 1) if not (q['ans'] and q['ex'])], [])

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
