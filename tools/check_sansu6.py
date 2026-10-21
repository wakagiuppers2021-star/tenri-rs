"""算数 大問6 の検算。答えを、データの解説とは別の方法（ボクセル・積分・総あたり・展開図の組み立て・時刻を刻んだシミュレーション）で求めなおして、比べる。

import されると、そのまま検算が走る（tools/check_tenri_rs.py が、tools/check_sansu*.py をすべて import する）。
単独でも動く:  cd tools && python -X utf8 check_sansu6.py
問題文の数値は、正規表現で取り出して使い、図の args（図に書く数値）とも一致することを確かめる。
"""
import itertools
import math
import re
from collections import defaultdict, deque
from fractions import Fraction as Fr

from check_common import FAIL, eq, ans, q_text, val
import tenri_rs_sansu6 as M6
import kanji_grade as KG

PI = Fr('3.14')
SETS = M6.SETS


def nums(s):
    """文字列にある数（整数・小数）を、Fraction で、出てくる順に。"""
    return [Fr(x) for x in re.findall(r'\d+(?:\.\d+)?', s)]


def first_num(s):
    return nums(s)[0]


def fmt(x):
    """数を、答えの書き方（cm³ などの前の数）に。小数は、必要なけただけ。"""
    x = Fr(x)
    if x.denominator == 1:
        return str(x.numerator)
    s = f'{float(x):.6f}'.rstrip('0')
    return s


def lead(s):
    return SETS[s - 1]['lead']


def fig_args(s):
    return SETS[s - 1]['fig']['args']


def in_poly(poly, x, y):
    """点（x, y）が、多角形の中にあるか（偶奇の判定）。"""
    inside = False
    n = len(poly)
    for i in range(n):
        (x1, y1), (x2, y2) = poly[i], poly[(i + 1) % n]
        if (y1 > y) != (y2 > y):
            xc = x1 + (y - y1) * (x2 - x1) / (y2 - y1)
            if xc > x:
                inside = not inside
    return inside


def grid_area(poly, step):
    """多角形の面積を、step 四方の細かい格子の、まん中の点を数えて求める。"""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    nx, ny = int(math.ceil((max(xs) - min(xs)) / step)), int(math.ceil((max(ys) - min(ys)) / step))
    cnt = 0
    for i in range(nx):
        x = min(xs) + (i + .5) * step
        for j in range(ny):
            if in_poly(poly, x, min(ys) + (j + .5) * step):
                cnt += 1
    return cnt * step * step


def shoelace(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2


# ============================================================ 第01セット：速さのグラフ（歩く人と自転車の兄）
a1 = fig_args(1)
pts1 = a1['lines'][0]['pts']


def pos1(t):
    """グラフ（折れ線）の、時刻 t での道のり。"""
    for (t1, v1), (t2, v2) in zip(pts1, pts1[1:]):
        if t1 <= t <= t2:
            return Fr(v1) + Fr(v2 - v1) * Fr(t - t1) / (t2 - t1)
    raise ValueError(t)


D1 = Fr(first_num(re.search(r'図書館から(\d+)m', lead(1)).group(0)))
assert D1 == pts1[-1][1], '家までの道のりが、グラフと合わない'
sp_first = pos1(Fr(9)) / 9                                               # 歩きはじめの区間の速さ
sp_last = (pos1(Fr(29)) - pos1(Fr(14))) / (29 - 14)                       # さいごの区間の速さ
eq('算6-1(1) 歩く速さ（前半・後半の傾き）', ans(M6, 1, 1), f'分速{fmt(sp_first)}m' if sp_first == sp_last else None)
vb1 = first_num(re.search(r'分速(\d+)m', q_text(M6, 1, 2)).group(0))
t_meet1 = Fr(pts1[1][0])                                                  # 出会って、立ち話をはじめた時刻
t_talk_end1 = Fr(pts1[2][0])
t_home1 = Fr(pts1[3][0])
# 兄は、時刻 t0 に家を出て、分速 vb で図書館へ向かう。出会いの時刻に、みおさんと同じ場所にいる t0 を、細かく探す。
cands1 = [Fr(k, 12) for k in range(0, 12 * 40) if D1 - vb1 * (t_meet1 - Fr(k, 12)) == pos1(t_meet1) and Fr(k, 12) <= t_meet1]
eq('算6-1(2) 兄の出発（総あたり）', ans(M6, 1, 2), f'{fmt(cands1[0])}分後' if len(cands1) == 1 else None)
late1 = first_num(re.search(r'(\d+)分後に、兄も家に着きました', q_text(M6, 1, 3)).group(0))
t0 = cands1[0]
sol3 = []
for k in range(0, 12 * 60):                                               # 図書館にいた時間 X を、5秒きざみで総あたり
    X = Fr(k, 12)
    # 家を出る → 出会い → 立ち話 → 図書館 → X だけいる → 家
    t = t0 + (D1 - pos1(t_meet1)) / vb1                                   # 出会い（＝t_meet1 のはず）
    assert t == t_meet1
    t = t_talk_end1 + pos1(t_meet1) / vb1                                 # 図書館に着く
    t_lib_arrive = t
    t = t + X + D1 / vb1                                                  # 図書館を出て、家に着く
    if t == t_home1 + late1:
        sol3.append((X, t_lib_arrive))
eq('算6-1(3) 図書館にいた時間（総あたり）', ans(M6, 1, 3), f'{fmt(sol3[0][0])}分間' if len(sol3) == 1 else None)
eq('算6-1 グラフの値と文章（家まで1440m・540m・9分・14分・29分）', [D1, pts1[1][1], pts1[1][0], pts1[2][0], pts1[3][0]], [1440, 540, 9, 14, 29])
eq('算6-1 図の目盛りの数字が、折れ線の点と一致', (a1['xticks'], a1['yticks'], a1['guides']), ([9, 14, 29], [540, 1440], [(9, 540), (14, 540), (29, 1440)]))

# ============================================================ 第02セット：立体の体積3つ
a2 = fig_args(2)['specs']
cb = dict(a2[0][1])
hFL, hFR, hBR, hBL = cb['h']
Lx, Wy = cb['L'], cb['W']
# 平面 z＝c0＋a·x＋b·y を、見えている3本の高さ（前左・前右・後ろ右）から求める
c0 = Fr(hFL)
pa = (Fr(hFR) - c0) / Lx
pb = (Fr(hBR) - c0 - pa * Lx) / Wy
hBL_plane = c0 + pb * Wy
eq('算6-2(1) 点線の辺（平面から）', ans(M6, 2, 1), f'{fmt(hBL_plane)}cm')
eq('算6-2 ア：4本目の高さが、図の値と平面で一致', hBL_plane, hBL)
n_ = 80                                                                   # 0.1cm四方の細かい格子で、高さを足して体積（平面なので、まん中の点で、ちょうど求まる）
vol_a = sum((c0 + pa * (Fr(2 * i + 1, 2 * n_) * Lx) + pb * (Fr(2 * j + 1, 2 * n_) * Wy)) * Fr(Lx, n_) * Fr(Wy, n_) for i in range(n_) for j in range(n_))
eq('算6-2(2) 直方体の切断（積分）', ans(M6, 2, 2), f'{fmt(vol_a)}cm³')
cy = dict(a2[1][1])
r2 = Fr(cy['d'], 2)
hl2, hr2 = cy['h']
step2 = .02                                                               # 円の中の点を細かく数え、高さの平均を求める（高さは、中心からの横の位置 x で一次式）
sum_h, cnt_h = 0.0, 0
nn = int(2 * float(r2) / step2)
for i in range(nn):
    x = -float(r2) + (i + .5) * step2
    h_x = (hl2 + hr2) / 2 + (hr2 - hl2) / (2 * float(r2)) * x            # 左はし（x＝－r）で hl2、右はし（x＝r）で hr2
    for j in range(nn):
        y = -float(r2) + (j + .5) * step2
        if x * x + y * y <= float(r2) ** 2:
            sum_h += h_x
            cnt_h += 1
mean_h = sum_h / cnt_h
eq('算6-2(3) 円柱の切断（積分）：高さの平均×底面積（円周率3.14）', ans(M6, 2, 3), f'{fmt(round(PI * r2 * r2 * Fr(str(round(mean_h, 3))), 2))}cm³')
boxes2 = dict(a2[2][1])['boxes']
vox = [set((x, y, z) for x in range(b[0], b[3]) for y in range(b[1], b[4]) for z in range(b[2], b[5])) for b in boxes2]
union2 = set().union(*vox)
eq('算6-2(4) 立方体3つ（ボクセル）：重ならない', sum(len(v) for v in vox), len(union2))


def touches(v1, v2):
    """2つの立体が、面で（ボクセルの面が）接しているか。"""
    return any((x + dx, y + dy, z + dz) in v2 for (x, y, z) in v1 for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)))


eq('算6-2(4) 立方体3つは、つながっている', all(any(touches(vox[i], vox[j]) for j in range(3) if j != i) for i in range(3)), True)
eq('算6-2(4) 立方体3つ（ボクセル）', ans(M6, 2, 4), f'{len(union2)}cm³')
edges2 = [b[3] - b[0] for b in boxes2]
eq('算6-2(4) 3つとも立方体で、図の長さの文字と一致', ([(b[3] - b[0], b[4] - b[1], b[5] - b[2]) for b in boxes2], sorted(int(re.sub(r'\D', '', n[1])) for n in dict(a2[2][1])['notes'])),
   ([(e, e, e) for e in edges2], sorted(edges2)))
ex23 = nums(SETS[1]['qs'][2]['ex'])
eq('算6-2(3) 解説の、半径4・高さの平均7が、図（直径8・高さ9と5）から出る値と一致', (r2 in ex23, Fr(hl2 + hr2, 2) in ex23, (cy['d'], cy['h'])), (True, True, (8, (9, 5))))

# ============================================================ 第03セット：規則性（白黒の正方形）
ns3 = fig_args(3)['ns']


def board(n):
    """n番目：たて n・よこ n+1 の、左上が黒の市松もよう。1が黒。"""
    return [[1 if (r + k) % 2 == 0 else 0 for k in range(n + 1)] for r in range(n)]


def count_color(n, color):
    return sum(cell == color for row in board(n) for cell in row)


eq('算6-3 図の、1〜4番目の黒の数（1・3・6・10）', [count_color(n, 1) for n in ns3], [1, 3, 6, 10])
n31 = int(re.search(r'(\d+)番目の図形の中に、黒い', q_text(M6, 3, 1)).group(1))
eq('算6-3(1) 5番目の黒', ans(M6, 3, 1), f'{count_color(n31, 1)}個')
n32 = int(re.search(r'(\d+)番目の図形の中に、白い', q_text(M6, 3, 2)).group(1))
eq('算6-3(2) 40番目の白', ans(M6, 3, 2), f'{count_color(n32, 0)}個')
need3 = int(re.search(r'黒い正方形が(\d+)個', q_text(M6, 3, 3)).group(1))
which3 = [n for n in range(1, 200) if count_color(n, 1) == need3]
eq('算6-3(3) 黒が105個になる番号（ならべて数える）', ans(M6, 3, 3), f'{which3[0]}番目' if len(which3) == 1 else None)
n34 = int(re.search(r'1番目から(\d+)番目まで', q_text(M6, 3, 4)).group(1))
eq('算6-3(4) 1〜10番目の黒の合計', ans(M6, 3, 4), f'{sum(count_color(n, 1) for n in range(1, n34 + 1))}個')
eq('算6-3 黒と白が、どの番号でも同じ数（市松もよう）', all(count_color(n, 1) == count_color(n, 0) for n in range(1, 60)), True)

# ============================================================ 第04セット：立体の体積3つ
a4 = fig_args(4)['specs']
tp = dict(a4[0][1])
off4 = Fr(tp['b1'] - tp['b2'], 2)
trap = [(0, 0), (tp['b1'], 0), (tp['b1'] - off4, tp['hh']), (off4, tp['hh'])]
area_t = grid_area([(float(x), float(y)) for x, y in trap], .02)
eq('算6-4(1) 台形の柱（面積を格子で数え、おくゆきをかける）', ans(M6, 4, 1), f'{round(area_t * tp["d"])}cm³')
eq('算6-4(1) 台形の面積（ショーレースの公式でも）', round(area_t), shoelace(trap))
rv = dict(a4[1][1])
poly4 = [(Fr(u), Fr(v)) for u, v in rv['poly']]
# 回転する図形に書きこんだ長さが、点の座標（軸からの横・高さ）から出る値と一致するか
lab_rv = sorted(int(re.sub(r'\D', '', l[-1])) for l in rv['labels'])
xs4 = sorted({u for u, _ in poly4})
ys4 = sorted({v for _, v in poly4})
eq('算6-4(2) 回転する図形の、長さの書きこみ（6・3・5・4・2）', lab_rv, sorted([xs4[-1], ys4[1] - ys4[0], ys4[2] - ys4[1], xs4[-1] - xs4[1], xs4[1] - xs4[0]]))


def slice_intervals(poly, z):
    """高さ z で、多角形を水平に切ったときの、軸（u＝0）からの横の範囲 [(u0, u1)]。"""
    xs = sorted(x1 + (z - y1) * (x2 - x1) / (y2 - y1) for (x1, y1), (x2, y2) in zip(poly, poly[1:] + poly[:1]) if (y1 > z) != (y2 > z))
    return list(zip(xs[0::2], xs[1::2]))


dz = Fr(1, 200)
hmax4 = max(v for _, v in poly4)
vol_rev = sum(PI * sum(u1 * u1 - u0 * u0 for u0, u1 in slice_intervals(poly4, (k + Fr(1, 2)) * dz)) * dz for k in range(int(hmax4 / dz)))
eq('算6-4(2) 回転体（高さごとの輪の面積を積分）', ans(M6, 4, 2), f'{fmt(vol_rev)}cm³')
pit = dict(a4[2][1])
pxs0, pxs1, pys0, pys1, ppd = pit['pit']
Lp, Hp = pit['L'], pit['H']
q43 = q_text(M6, 4, 3)
vol_target = int(re.search(r'(\d+)cm³のとき', q43).group(1))
txt_pit = (int(re.search(r'1辺(\d+)cm', q43).group(1)), int(re.search(r'深さ(\d+)cm', q43).group(1)))
sol4 = []
for k in range(2, 41):                                                    # xを、0.5ずつ、総あたり
    xv = Fr(k, 2)
    V = 0
    for i in range(int(Lp * 2)):                                          # 0.5cm四方・0.5cm高さのボクセル
        for j in range(int(xv * 2)):
            for m in range(int(Hp * 2)):
                cx_, cy_, cz_ = Fr(2 * i + 1, 4), Fr(2 * j + 1, 4), Fr(2 * m + 1, 4)
                in_pit = pxs0 <= cx_ <= pxs1 and pys0 <= cy_ <= pys1 and Hp - ppd <= cz_ <= Hp
                if not in_pit:
                    V += Fr(1, 8)
    if V == vol_target:
        sol4.append(xv)
eq('算6-4(3) xの値（ボクセルの総あたり）', ans(M6, 4, 3), f'{fmt(sol4[0])}cm' if len(sol4) == 1 else None)
eq('算6-4(3) 問題文の穴（1辺3cmの正方形・深さ4cm）と図の穴が一致', ((pxs1 - pxs0, pys1 - pys0), ppd), ((txt_pit[0], txt_pit[0]), txt_pit[1]))
eq('算6-4(3) 図の穴が、直方体の中にある（x＝4のとき）', 0 <= pys0 and pys1 <= sol4[0] and pxs0 >= 0 and pxs1 <= Lp, True)

# ============================================================ 第05セット：カードで作る3けたの整数
cards5 = fig_args(5)['digits']
made5 = sorted({100 * cards5[i] + 10 * cards5[j] + cards5[k] for i, j, k in itertools.permutations(range(len(cards5)), 3) if cards5[i] != 0})
eq('算6-5 問題文のカードの数字が、図と一致', [int(x) for x in re.findall(r'\d', lead(5).split('の数字')[0])], cards5)
eq('算6-5(1) 全部で', ans(M6, 5, 1), f'{len(made5)}個')
eq('算6-5(2) 偶数', ans(M6, 5, 2), f'{sum(1 for x in made5 if x % 2 == 0)}個')
target5 = int(first_num(re.search(r'(\d+)は、小さいほう', q_text(M6, 5, 3)).group(0)))
eq('算6-5(3) 231は小さいほうから何番目', ans(M6, 5, 3), f'{made5.index(target5) + 1}番目')
nth5 = int(first_num(re.search(r'(\d+)番目の整数は何', q_text(M6, 5, 4)).group(0)))
eq('算6-5(4) 大きいほうから10番目', ans(M6, 5, 4), str(sorted(made5, reverse=True)[nth5 - 1]))

# ============================================================ 第06セット：三角柱・くりぬいた立体
a6 = fig_args(6)['specs']
tri = dict(a6[0][1])
area_tri = grid_area([(0., 0.), (float(tri['b']), 0.), (0., float(tri['hh']))], .02)
eq('算6-6(1) 三角柱（面積を格子で数え、高さをかける）', ans(M6, 6, 1), f'{round(area_tri * tri["d"])}cm³')
eq('算6-6(1) 図の三辺（5・12・13）が直角三角形', (tri['hh'] ** 2 + tri['b'] ** 2, int(re.sub(r'\D', '', tri['slant'])) ** 2), (169, 169))
nt = dict(a6[1][1])
nx0, nx1, nh, nd = nt['notch']
V6 = 0
for i in range(nt['L']):
    for j in range(nt['D']):
        for k in range(nt['H']):
            cx_, cy_, cz_ = i + .5, j + .5, k + .5
            if not (nx0 <= cx_ <= nx1 and cy_ <= nd and cz_ >= nt['H'] - nh):
                V6 += 1
eq('算6-6(2) くりぬいた立体（ボクセル）', ans(M6, 6, 2), f'{V6}cm³')
full6 = nt['L'] * nt['D'] * nt['H']
eq('算6-6(3) 体積の割合（分数）', ans(M6, 6, 3), f'<{Fr(V6, full6).numerator}/{Fr(V6, full6).denominator}>')
eq('算6-6(2) 図の長さ（12・6・7、切りとり 4・2・3）', (nt['L'], nt['D'], nt['H'], nx1 - nx0, nh, nd), (12, 6, 7, 4, 2, 3))

# ============================================================ 第07セット：展開図から直方体（実際に折って、面と点の対応を求める）
a7 = fig_args(7)
cols7, rows7, faces7, pts7 = a7['cols'], a7['rows'], a7['faces'], a7['pts']


def fold_net(cols, rows, faces):
    """展開図を、1つの面を底にして、となりあう面を順に90度折り上げて、3次元の座標にする。
    (列, 行) の面ごとに、アフィン写像 (O, U, V, 内向きの法線) を持つ。格子の点 (i, j) の座標は、その点をふくむ面から、写像で求める。"""
    xs = [0]
    for w in cols:
        xs.append(xs[-1] + w)
    ys = [0]
    for h in rows:
        ys.append(ys[-1] + h)
    have = {(c, r): n for c, r, n in faces}
    first = faces[0][:2]
    maps = {first: ((0, 0, 0), (1, 0, 0), (0, 1, 0), (0, 0, 1))}
    dq, seen = deque([first]), {first}

    def mp(m, p):
        O, U, V, _ = m
        return tuple(O[i] + p[0] * U[i] + p[1] * V[i] for i in range(3))
    while dq:
        c, r = dq.popleft()
        m = maps[(c, r)]
        O, U, V, n = m
        for dc, dr in ((1, 0), (-1, 0), (0, 1), (0, -1)):
            nb = (c + dc, r + dr)
            if nb in have and nb not in seen:
                seen.add(nb)
                if dc:
                    edge_net, e_net = (xs[c + 1] if dc == 1 else xs[c], 0), (0, 1)
                else:
                    edge_net, e_net = (0, ys[r + 1] if dr == 1 else ys[r]), (1, 0)
                d_in, d_out = (-dc, -dr), (dc, dr)
                u_in = tuple(d_in[0] * U[i] + d_in[1] * V[i] for i in range(3))              # となりの面の、内向きの法線
                P0 = mp(m, edge_net)
                E3 = tuple(e_net[0] * U[i] + e_net[1] * V[i] for i in range(3))
                dotE = edge_net[0] * e_net[0] + edge_net[1] * e_net[1]
                dotD = edge_net[0] * d_out[0] + edge_net[1] * d_out[1]
                O2 = tuple(P0[i] - dotE * E3[i] - dotD * n[i] for i in range(3))
                U2 = tuple(E3[i] * e_net[0] + n[i] * d_out[0] for i in range(3))
                V2 = tuple(E3[i] * e_net[1] + n[i] * d_out[1] for i in range(3))
                maps[nb] = (O2, U2, V2, u_in)
                dq.append(nb)
    assert len(maps) == len(faces), '展開図がつながっていない'
    return maps, mp, xs, ys, have


maps7, mp7, xs7, ys7, have7 = fold_net(cols7, rows7, faces7)
v3 = {}
for lab_pt, ij in ((l, k) for k, l in pts7.items()):
    i, j = ij
    cand = set()
    for (c, r), m in maps7.items():
        if xs7[c] <= xs7[i] <= xs7[c + 1] and ys7[r] <= ys7[j] <= ys7[r + 1] and xs7[i] in (xs7[c], xs7[c + 1]) and ys7[j] in (ys7[r], ys7[r + 1]):
            cand.add(mp7(m, (xs7[i], ys7[j])))
    assert len(cand) == 1, ('点が、面によって、ちがう位置になる', lab_pt, cand)
    v3[lab_pt] = next(iter(cand))
verts7 = set(v3.values())
eq('算6-7 組み立てると、頂点が8個の、直方体になる', (len(verts7), len(pts7)), (8, 14))
ext7 = [max(v[k] for v in verts7) - min(v[k] for v in verts7) for k in range(3)]
box_ok = all(sum(1 for v in verts7 if v[k] == lo) == 4 for k in range(3) for lo in (min(v[k] for v in verts7), max(v[k] for v in verts7)))
eq('算6-7 8つの頂点が、直方体の8つのかど', box_ok, True)


face_n = {have7[k]: m[3] for k, m in maps7.items()}                       # 面の名前 → 内向きの法線（軸に平行なので、その向きで、面の位置がわかる）
face_axis = {nm: [k for k in range(3) if n[k] != 0][0] for nm, n in face_n.items()}
face_side = {}
for (c, r), m in maps7.items():                                           # その面が、直方体の、どの軸のどちらがわ（最小・最大）にあるか
    pts3 = [mp7(m, p) for p in ((xs7[c], ys7[r]), (xs7[c + 1], ys7[r]), (xs7[c + 1], ys7[r + 1]), (xs7[c], ys7[r + 1]))]
    k = face_axis[have7[(c, r)]]
    assert len({p[k] for p in pts3}) == 1
    face_side[have7[(c, r)]] = (k, 0 if pts3[0][k] == min(v[k] for v in verts7) else 1)
eq('算6-7 6つの面が、直方体の6つの面（軸×2がわ）にそろう', sorted(face_side.values()), [(k, s) for k in range(3) for s in (0, 1)])
ask7 = re.search(r'点(.)と重なる点', q_text(M6, 7, 1)).group(1)
eq('算6-7(1) 点エと重なる点', ans(M6, 7, 1), '・'.join(sorted((l for l, p in v3.items() if p == v3[ask7] and l != ask7), key=lambda s: 'アイウエオカキクケコサシスセ'.index(s))))
par_face = re.search(r'面(.)と平行', q_text(M6, 7, 2)).group(1)
eq('算6-7(2) 面あと平行な面（むかい合う面）', ans(M6, 7, 2), '・'.join(nm for nm, (k, s) in face_side.items() if k == face_side[par_face][0] and s != face_side[par_face][1]))
perp_face = re.search(r'面(.)と垂直', q_text(M6, 7, 3)).group(1)
eq('算6-7(3) 面いと垂直な面', ans(M6, 7, 3), '・'.join(sorted((nm for nm, (k, s) in face_side.items() if k != face_side[perp_face][0]), key='あいうえおか'.index)))
eq('算6-7(4) 直方体の体積（頂点の座標の、はば×たて×高さ）', ans(M6, 7, 4), f'{ext7[0] * ext7[1] * ext7[2]}cm³')
dim_txt = sorted(int(re.sub(r'\D', '', d[2])) for d in a7['dims'])
eq('算6-7 図に書いた3つの長さが、直方体の3辺', dim_txt, sorted(ext7))
dim_net = [cols7[c] if side in ('top', 'bottom') else rows7[r] for side, (c, r), _ in a7['dims']]       # 書きこんだ辺（面のはし）の、展開図での長さ
eq('算6-7 図に書いた長さの文字が、展開図の辺の長さと合う', [int(re.sub(r'\D', '', d[2])) for d in a7['dims']], dim_net)

# ============================================================ 第08セット：円柱から四角柱をくりぬいた立体
cyh = dict(fig_args(8)['specs'][0][1])
r8, h8, s8 = cyh['r'], cyh['hh'], cyh['s']
eq('算6-8 問題文の半径5cm・高さ8cm・1辺3cmが、図と一致', ([n for n in nums(lead(8))][:2], Fr(re.search(r'1辺(\d+)cm', q_text(M6, 8, 2)).group(1))), ([r8, h8], s8))
vol_cyl = PI * r8 * r8 * h8
eq('算6-8(1) 円柱', ans(M6, 8, 1), f'{fmt(vol_cyl)}cm³')


def square_cells(side_pred, half, step):
    """格子（step 四方）のまん中の点で、side_pred（x, y）を満たす面積を数える。"""
    n = int(2 * half / step)
    return sum(1 for i in range(n) for j in range(n) if side_pred(-half + (i + .5) * step, -half + (j + .5) * step)) * step * step


sq_area = square_cells(lambda x, y: abs(x) <= s8 / 2 and abs(y) <= s8 / 2, 5, .05)
eq('算6-8(2) 四角柱（底面を格子で数える）', ans(M6, 8, 2), f'{round(sq_area * h8)}cm³')
circ_area_pi = square_cells(lambda x, y: x * x + y * y <= r8 * r8, r8, .02)
eq('算6-8(3) 円の面積の格子の数えが、3.14の値と、1%以内で合う', abs(circ_area_pi - float(PI * r8 * r8)) / float(PI * r8 * r8) < .01, True)
eq('算6-8(3) くりぬいた立体', ans(M6, 8, 3), f'{fmt(vol_cyl - Fr(round(sq_area)) * h8)}cm³')
diag8 = first_num(re.search(r'対角線の長さが(\d+)cm', q_text(M6, 8, 4)).group(0))
dia_area = square_cells(lambda x, y: abs(x) + abs(y) <= float(diag8) / 2, 5, .05)                  # 対角線が6cmの正方形は、|x|＋|y|≦3
eq('算6-8(4) 対角線6cmの正方形をくりぬく', ans(M6, 8, 4), f'{fmt(PI * r8 * r8 * h8 - Fr(round(dia_area)) * h8)}cm³')

# ============================================================ 第09セット：速さのグラフ（出会う地点）
va9 = first_num(re.search(r'分速(\d+)m', lead(9)).group(0))
late9 = first_num(re.search(r'(\d+)分後に、駅を出発', lead(9)).group(0))
tb9 = first_num(re.search(r'駅を出発して(\d+)分後に', lead(9)).group(0))
ta9 = Fr(fig_args(9)['xticks'][-1])                                       # グラフで、駅に着く時刻
D9 = va9 * ta9
eq('算6-9(1) 図書館から駅までの道のり', ans(M6, 9, 1), f'{fmt(D9)}m')
vb9 = [v for v in range(1, 1000) if v * tb9 == D9]                          # 兄の速さ：12分で、全部の道のりを進む
eq('算6-9(2) 兄の速さ（総あたり）', ans(M6, 9, 2), f'分速{vb9[0]}m' if len(vb9) == 1 else None)


def pos_A(t):
    return min(va9 * t, D9) if t >= 0 else 0


def pos_B(t):
    """兄の、図書館からの道のり（駅を、出発の時刻 late9 に出て、図書館へ）。出発前は駅、着いたあとは図書館。"""
    if t <= late9:
        return D9
    return max(D9 - vb9[0] * (t - late9), 0)


meet9 = [Fr(k, 60) for k in range(0, 60 * 40) if pos_A(Fr(k, 60)) == pos_B(Fr(k, 60)) and Fr(k, 60) > late9]
eq('算6-9(3) すれちがう時刻（1秒きざみで、2人の位置が同じになる時刻）', ans(M6, 9, 3), f'{fmt(meet9[0])}分後' if len(meet9) == 1 else None)
eq('算6-9(4) すれちがう地点', ans(M6, 9, 4), f'{fmt(pos_A(meet9[0]))}m')
eq('算6-9 グラフの、ゆうこさんの線が、分速75mと合う', (fig_args(9)['lines'][0]['pts'], fig_args(9)['ymax']), ([(0, 0), (24, 6)], 6))

# ============================================================ 第10セット：植木算・速さ
q10 = [q_text(M6, 10, k) for k in range(1, 6)]
n_tree, gap1 = (int(x) for x in re.search(r'(\d+)本の木を、(\d+)mおきに', q10[0]).groups())
tree_pos = [gap1 * k for k in range(n_tree)]                              # 実際に、木を植えていく位置
eq('算6-10(1) まっすぐな道（木の位置の、はしからはし）', ans(M6, 10, 1), f'{tree_pos[-1] - tree_pos[0]}m')
circ, gap2 = (int(x) for x in re.search(r'1周(\d+)mの道に、(\d+)mおき', q10[1]).groups())
planted, p_ = [], 0
while p_ < circ:                                                          # 池のまわりを、1周しながら植えて、スタートにもどったら、おわり
    planted.append(p_)
    p_ += gap2
eq('算6-10(2) 池のまわり（1周しながら植える）', ans(M6, 10, 2), f'{len(planted)}本' if p_ == circ else None)
dist10 = Fr(first_num(re.search(r'(\d+\.\d+)km', q10[2]).group(0))) * 1000
va10 = first_num(re.search(r'分速(\d+)m', q10[2]).group(0))
t_walk = [Fr(t) for t in range(1, 200) if va10 * t == dist10]
eq('算6-10(3) ゆうきさんの時間（総あたり）', ans(M6, 10, 3), f'{t_walk[0]}分')
late10, vs10 = (int(x) for x in re.search(r'(\d+)分後に、家を出発し、分速(\d+)m', q10[3]).groups())
t_sister = [Fr(t) for t in range(1, 200) if vs10 * (t - late10) == dist10]                  # 姉が駅に着く時刻（ゆうきさんが出てからの時刻）
eq('算6-10(4) 姉が早い時間', ans(M6, 10, 4), f'{t_walk[0] - t_sister[0]}分')
meet10 = int(re.search(r'出発して(\d+)分後に', q10[4]).group(1))
sol10 = [v for v in range(1, 1000) if (va10 + v) * meet10 == dist10]
eq('算6-10(5) 友だちの速さ（総あたり）', ans(M6, 10, 5), f'分速{sol10[0]}m' if len(sol10) == 1 else None)
eq('算6-10 図の木の数と、問題文の木の数は別（図は1列に5本）', fig_args(10)['n'], 5)

# ============================================================ 図に書いた数が、解説で使われている（図と解説のくいちがいを防ぐ）
def uses(setno, qno, need):
    got = set(nums(SETS[setno - 1]['qs'][qno - 1]['ex']))
    return [n for n in need if Fr(n) not in got]


eq('算6-2(2) 解説が、図アの数（8・5・4本の高さ）を使っている', uses(2, 2, [cb['L'], cb['W'], hFL, hFR, hBR, hBL]), [])
eq('算6-2(3) 解説が、図イの数（直径の半分4・高さ9と5）を使っている', uses(2, 3, [r2, hl2, hr2]), [])
eq('算6-2(4) 解説が、図ウの数（6・3・2）を使っている', uses(2, 4, edges2), [])
eq('算6-4(1) 解説が、図(1)の数（上底・下底・高さ・おくゆき）を使っている', uses(4, 1, [tp['b1'], tp['b2'], tp['hh'], tp['d']]), [])
eq('算6-4(2) 解説が、図(2)の数（6・3・5・2）を使っている', uses(4, 2, [xs4[-1], ys4[1], ys4[2] - ys4[1], xs4[1]]), [])
eq('算6-4(3) 解説が、図(3)の数（9・6・3・4・180）を使っている', uses(4, 3, [Lp, Hp, pxs1 - pxs0, ppd, vol_target]), [])
eq('算6-6(1) 解説が、図(1)の数（5・12・9）を使っている', uses(6, 1, [tri['hh'], tri['b'], tri['d']]), [])
eq('算6-6(2) 解説が、図(2)の数（12・6・7・4・2・3）を使っている', uses(6, 2, [nt['L'], nt['D'], nt['H'], nx1 - nx0, nh, nd]), [])
eq('算6-8 解説が、図の数（半径5・高さ8・1辺3・対角線6）を使っている', uses(8, 1, [r8, h8]) + uses(8, 2, [s8, h8]) + uses(8, 4, [diag8, h8]), [])

# ============================================================ 全体：形式・漢字・解説の式
eq('算6 セットの数と、年度の順', [s['year'] for s in SETS], [2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015])
ELEM = set(''.join(KG.BY_GRADE[g] for g in range(1, 7)))
bad_k = []
for i, st in enumerate(SETS, 1):
    texts = [st['title'], st['lead']]
    for q in st['qs']:
        texts += [q['q'], q['ex'], q['ans'], q.get('unit', '')]
    for t in texts:
        for ch in t:
            if '一' <= ch <= '龥' and ch not in ELEM:
                bad_k.append((i, ch))
eq('算6 小学校で習わない漢字がない', sorted(set(bad_k)), [])


def chains(ex):
    """解説の中の「A＝B＝C」の形の等式（数と＋－×÷（）だけでできた式。文字や言葉が、つながっているものは、のぞく）をぬき出す。"""
    out = []
    for m in re.finditer(r'[\d.＋－×÷（）＝<>/ ]*＝[\d.＋－×÷（）＝<>/ ]*', ex):
        t = m.group(0).strip().rstrip('（ ')                       # 単位のかっこ「（cm²）」の、はじめのかっこは、のぞく
        if t.count('（') != t.count('）') or t[0] in '＋－×÷）＝' or t[-1] in '＋－×÷（＝':
            continue
        out.append(t)
    return out


bad_c = []
for i, st in enumerate(SETS, 1):
    for j, q in enumerate(st['qs'], 1):
        for ch in chains(q['ex']):
            sides = []
            for side in ch.split('＝'):
                try:
                    sides.append(val(side.strip()))
                except Exception:
                    sides.append(None)
            sides = [s_ for s_ in sides if s_ is not None]
            if len(set(sides)) > 1:
                bad_c.append((i, j, ch, [str(s_) for s_ in sides]))
eq('算6 解説の中の等式（A＝B＝C）が、すべて成り立つ', bad_c, [])

bad_l = []
for i, st in enumerate(SETS, 1):
    for j, q in enumerate(st['qs'], 1):
        if re.fullmatch(r'(分速)?[\d.]+[^\d]*', q['ans']) and not q['ans'].startswith('<'):
            tail = re.sub(r'（[^）]*）', '', q['ex']).rstrip('。 ')
            last = nums(tail)[-1]
            if last != first_num(q['ans']):
                bad_l.append((i, j, str(last), q['ans']))
eq('算6 解説の最後の数が、答えの数と同じ（数の答え）', bad_l, [])

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
