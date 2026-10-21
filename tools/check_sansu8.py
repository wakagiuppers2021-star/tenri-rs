"""算数 大問8（角度・円形の遊歩道・平行線の間の面積・水そう・速さのグラフ・立体・ろうそく・割合と比・玉の割合）の検算。

データ（tools/tenri_rs_sansu8.py）の答えを、解説の式の写しではなく、次のような別の方法で求めなおして比べる。
  角度            図の頂点の座標から、角度を計算しなおす（折り返しは、点Aを折り目で対称にうつして、点Fと重なるかも確かめる）
  遊歩道          1秒きざみで、2人の位置（周の上の位置）がそろう時刻を数える
  面積            座標のショーレース（Fraction）と、細かい格子（0.02cm）の数え上げ
  水そう・グラフ  区分ごとの式で、1秒きざみに、水の量・道のり・長さを計算する
  立体            1cmの立方体の数え上げ（体積）と、外にむいた面の数え上げ（表面積）。半円柱は、積分（細かい和）で、3.14と本物のπの差も確かめる
  割合・比        整数を総あたりして、条件にあうものを数える
問題文の数値は、正規表現で取り出して検算に使い、図の中の数値（args・座標）とも一致するか確かめる。
import しただけで検算が走る（tools/check_tenri_rs.py が import する）。単独でも、cd tools && python -X utf8 check_sansu8.py で動く。
"""
import math
import re
from fractions import Fraction as Fr

from check_common import FAIL, eq, ans, q_text, val
from kanji_grade import GRADE
import tenri_rs_sansu8 as M8

S = M8.SETS
TOK = re.compile(r'<(?:(\d+) )?(\d+)/(\d+)>|\d+\.\d+|\d+')


def nums(s):
    """文字列の中の数（整数・小数・<分数>・<帯分数>）を、出てきた順に Fraction で返す。"""
    out = []
    for m in TOK.finditer(s):
        t = m.group(0)
        if t.startswith('<'):
            out.append(Fr(int(m.group(1) or 0)) + Fr(int(m.group(2)), int(m.group(3))))
        else:
            out.append(Fr(t))
    return out


def rx(pattern, text, g=1):
    """問題文から、パターンにあう数（Fraction）をぬき出す。見つからなければ、検算を止める（問題文が変わったしるし）。"""
    m = re.search(pattern, text)
    assert m, f'問題文に {pattern!r} がない: {text[:40]}'
    return Fr(m.group(g))


def A(i, j):
    return ans(M8, i, j)


def AN(i, j):
    return nums(A(i, j))


def Q(i, j):
    return q_text(M8, i, j)


def lead(i):
    return S[i - 1]['lead']


def figargs(i):
    return S[i - 1]['fig']['args']


def prims(i, k=0):
    return figargs(i)['panels'][k]['prims']


def points(pr):
    """prims のなかの ('pt', (x, y), '記号', ...) から {記号: (x, y)}。"""
    return {p[2]: tuple(p[1]) for p in pr if p[0] == 'pt'}


def ang(P, v, a, b):
    """頂点 v で、点 a・点 b にはさまれる角（度、0〜180）。"""
    ax, ay = P[a][0] - P[v][0], P[a][1] - P[v][1]
    bx, by = P[b][0] - P[v][0], P[b][1] - P[v][1]
    c = (ax * bx + ay * by) / (math.hypot(ax, ay) * math.hypot(bx, by))
    return math.degrees(math.acos(max(-1, min(1, c))))


def dist(p, q):
    return math.hypot(p[0] - q[0], p[1] - q[1])


def near(x, y, tol=0.01):
    return abs(x - y) <= tol


def mmss(sec):
    return f'{sec // 60}分{sec % 60}秒'


# ============================================================ 共通：10セット・答え・解説・漢字・解説の式
eq('算8 セット数', len(S), 10)
bad = []
for i, st in enumerate(S, 1):
    for j, q in enumerate(st['qs'], 1):
        if not (q.get('q') and q.get('ans') and q.get('ex')):
            bad.append((i, j, '問・答・解説のどれかがない'))
        if q['kind'] not in ('short', 'grid'):
            bad.append((i, j, 'kind'))
        if q['kind'] == 'grid' and len(q['labels']) != len(q['ans']):
            bad.append((i, j, 'grid の長さ'))
        a_nums = AN(i, j) if q['kind'] == 'short' else [x for a in q['ans'] for x in nums(a)]
        ex_nums = set(nums(q['ex']))
        if not a_nums or any(x not in ex_nums for x in a_nums):
            bad.append((i, j, '答えの数が、解説に出てこない', q['ans']))
eq('算8 全小問に問・答・解説があり、答えの数が解説にある', bad, [])

# 使う漢字は、小学校で習うものだけ（教育漢字）
bad = []
for i, st in enumerate(S, 1):
    texts = [st['title'], st['lead']]
    for q in st['qs']:
        texts += [q['q'], q['ex'], q.get('head', '')] + (q['ans'] if isinstance(q['ans'], list) else [q['ans']]) + q.get('labels', [])
    for t in texts:
        for ch in t:
            if '一' <= ch <= '鿿' and GRADE.get(ch, 8) > 6:
                bad.append((i, ch, t[:20]))
eq('算8 使った漢字はすべて小学校の教育漢字', sorted(set(bad)), [])

# 解説の中の「A＝B＝C」の式を、値で確かめる（左右の式が、数と＋−×÷かっこだけのとき）
CHAIN = re.compile(r'[\d.<>/ ()＋−×÷]+(?:＝[\d.<>/ ()＋−×÷]+)+')
bad, n_chain = [], 0
for i, st in enumerate(S, 1):
    for j, q in enumerate(st['qs'], 1):
        for ch in CHAIN.findall(q['ex']):
            vs = []
            for side in ch.split('＝'):
                try:
                    vs.append(val(side.strip()))
                except Exception:
                    pass
            if len(vs) >= 2:
                n_chain += 1
                if len(set(vs)) > 1:
                    bad.append((i, j, ch, vs))
eq(f'算8 解説の等式{n_chain}個が成り立つ', bad, [])

# ============================================================ 第01セット：角度（座標から、角度を計算しなおす）
P1 = points(prims(1, 0))
P2 = points(prims(1, 1))
q11 = Q(1, 1)
ab, ac = rx(r'角Bが(\d+)度、角Cが(\d+)度', q11, 1), rx(r'角Bが(\d+)度、角Cが(\d+)度', q11, 2)
eq('算8-1 図(1)：三角定規ABC（問題文のB＝90度、C＝30度。A＝60度）', [round(ang(P1, 'B', 'A', 'C'), 2), round(ang(P1, 'C', 'A', 'B'), 2), round(ang(P1, 'A', 'B', 'C'), 2)],
   [float(ab), float(ac), float(180 - ab - ac)])
eq('算8-1 図(1)：角BDF（問題文の40度）', round(ang(P1, 'D', 'B', 'F'), 1), float(rx(r'角BDFが(\d+)度', q11)))
eq('算8-1 図(1)：点Fは辺BC上、点Dは辺AB上、点Eは辺AC上', (P1['F'][1] == 0, P1['D'][0] == 0, abs((P1['C'][0] - P1['A'][0]) * (P1['E'][1] - P1['A'][1]) - (P1['C'][1] - P1['A'][1]) * (P1['E'][0] - P1['A'][0])) < 1e-3), (True, True, True))


def reflect(p, a, b):
    """点 p を、直線 ab について対称にうつした点。"""
    dx, dy = b[0] - a[0], b[1] - a[1]
    t = ((p[0] - a[0]) * dx + (p[1] - a[1]) * dy) / (dx * dx + dy * dy)
    fx, fy = a[0] + t * dx, a[1] + t * dy
    return (2 * fx - p[0], 2 * fy - p[1])


rf = reflect(P1['A'], P1['D'], P1['E'])
eq('算8-1 図(1)：Aを折り目DEで折ると、Fに重なる', (round(rf[0], 2), round(rf[1], 2)), (round(P1['F'][0], 2), round(P1['F'][1], 2)))
eq('算8-1(1) 角ア（角ADE）', A(1, 1), f'{round(ang(P1, "D", "A", "E")):g}度')
eq('算8-1(2) 角イ（角FEC）', A(1, 2), f'{round(ang(P1, "E", "F", "C")):g}度')
eq('算8-1 図(2)：ABCDは1辺6の正方形', sorted(round(dist(P2[a], P2[b]), 3) for a, b in ('AB', 'BC', 'CD', 'DA')), [6.0] * 4)
eq('算8-1 図(2)：AB＝AE（問題文）、角DAE＝30度（問題文）', (near(dist(P2['A'], P2['B']), dist(P2['A'], P2['E']), 1e-3), round(ang(P2, 'A', 'D', 'E'), 3)),
   (True, float(rx(r'角DAEは(\d+)度', Q(1, 3)))))
eq('算8-1(3) 角ウ（角BEC）', A(1, 3), f'{round(ang(P2, "E", "B", "C")):g}度')
eq('算8-1(4) 角エ（角CED）', A(1, 4), f'{round(ang(P2, "E", "C", "D")):g}度')
# 図にかいた角の印（円弧の向き）の大きさが、図の座標・答えと合っている
arcs1 = {p[4]: (round((p[3] - p[2]) % 360, 1)) for p in prims(1, 0) if p[0] == 'angle'}
arcs2 = {p[4]: (round((p[3] - p[2]) % 360, 1)) for p in prims(1, 1) if p[0] == 'angle'}
eq('算8-1 図の円弧：図(1)の40°・ア・イ・60°・30°', arcs1, {'40°': 40.0, 'ア': float(AN(1, 1)[0]), 'イ': float(AN(1, 2)[0]), '60°': 60.0, '30°': 30.0})
eq('算8-1 図の円弧：図(2)の30°・ウ・エ', arcs2, {'30°': 30.0, 'ウ': float(AN(1, 3)[0]), 'エ': float(AN(1, 4)[0])})

# ============================================================ 第02セット：円形の遊歩道（1秒きざみで、位置をそろえる）
lead2 = lead(2)
L2 = int(re.search(r'1周(\d+)m', lead2).group(1))
va, vb = [int(x) for x in re.findall(r'分速(\d+)m', lead2)]
eq('算8-2 図の1周の長さ＝問題文', [p['lap'] for p in figargs(2)['panels']], [f'{L2}m'] * 2)


def first_meet(rate):
    """2人の位置のずれが、毎秒 rate/60 m ずつ変わるとき、はじめて、周の長さの整数倍になる秒。"""
    for t in range(1, 10 ** 6):
        if (rate * t) % (60 * L2) == 0:
            return t


lap_a = first_meet(va)                                     # Aが、スタート地点にもどる
opp = first_meet(va + vb)                                  # 反対向き：位置の和が周の整数倍
same = first_meet(vb - va)                                 # 同じ向き：位置の差が周の整数倍
span2 = int(rx(r'(\d+)分間に、2人は', Q(2, 4)))
cnt = sum(1 for t in range(1, span2 * 60 + 1) if ((va + vb) * t) % (60 * L2) == 0)
eq('算8-2(1) Aが1周する時間', A(2, 1), f'{Fr(lap_a, 60):g}分')
eq('算8-2(2) 反対向きに、はじめて出会う', A(2, 2), mmss(opp) + '後')
eq('算8-2(3) 同じ向きに、追いつくまでにBが歩く道のり', A(2, 3), f'{Fr(vb * same, 60):g}m')
eq('算8-2(4) 反対向きに歩いて、問題文の分間に出会う回数（1秒きざみ）', A(2, 4), f'{cnt}回')

# ============================================================ 第03セット：平行線の間の台形と平行四辺形（座標・ショーレース・細かい格子）
P3 = points(prims(3))
lines3 = sorted(p[1][1] for p in prims(3) if p[0] == 'line' and p[1][1] == p[2][1])
gap = rx(r'間かくは、どこも(\d+)cm', lead(3))
eq('算8-3 平行線の間かく（問題文の4cm）', [lines3[1] - lines3[0], lines3[2] - lines3[1]], [gap, gap])


def shoelace(pts):
    return abs(sum(Fr(pts[k][0]) * Fr(pts[(k + 1) % len(pts)][1]) - Fr(pts[(k + 1) % len(pts)][0]) * Fr(pts[k][1]) for k in range(len(pts)))) / 2


def inside(poly, x, y):
    c = False
    for k in range(len(poly)):
        (x1, y1), (x2, y2) = poly[k], poly[(k + 1) % len(poly)]
        if (y1 > y) != (y2 > y) and x < x1 + (y - y1) * (x2 - x1) / (y2 - y1):
            c = not c
    return c


def grid_area(poly, step=0.05):
    """格子（step cm四方）の中心が、多角形の中に入るものを数える。"""
    xs, ys = [p[0] for p in poly], [p[1] for p in poly]
    n = 0
    y = min(ys) + step / 2
    while y < max(ys):
        x = min(xs) + step / 2
        while x < max(xs):
            if inside(poly, x, y):
                n += 1
            x += step
        y += step
    return n * step * step


para = [P3['F'], P3['G'], P3['H'], P3['E']]
trap = [P3['B'], P3['C'], P3['D'], P3['A']]
tri_acd = [P3['A'], P3['C'], P3['D']]
tri_abc = [P3['A'], P3['B'], P3['C']]
fg = rx(r'FG＝(\d+)cm', Q(3, 1))
bc = rx(r'BC＝(\d+)cm', Q(3, 2))
eq('算8-3 図：EH・FGは平行線の上、FG＝6（問題文）、EF∥HG', (P3['E'][1] == P3['H'][1] == lines3[2], P3['F'][1] == P3['G'][1] == lines3[0], P3['G'][0] - P3['F'][0], P3['H'][0] - P3['G'][0] == P3['E'][0] - P3['F'][0]),
   (True, True, fg, True))
eq('算8-3 図：AD・BCの位置、BC＝14（問題文）', (P3['A'][1] == P3['D'][1] == lines3[1], P3['B'][1] == P3['C'][1] == lines3[0], P3['C'][0] - P3['B'][0]), (True, True, bc))
a_para, a_trap = shoelace(para), shoelace(trap)
eq('算8-3(1) 平行四辺形EFGHの面積（ショーレース）', A(3, 1), f'{a_para:g}cm²')
eq('算8-3(1) 格子の数え上げ', round(grid_area(para)), round(float(a_para)))
eq('算8-3(2) 台形＝平行四辺形となるADを、座標の図で確かめる', (A(3, 2), a_trap == a_para), (f'{P3["D"][0] - P3["A"][0]:g}cm', True))
ad_try = [ad for ad in range(1, 40) if Fr((ad + int(bc)) * int(gap), 2) == a_para]            # ADを総あたり
eq('算8-3(2) ADの総あたり', A(3, 2), f'{ad_try[0]:g}cm' if len(ad_try) == 1 else None)
eq('算8-3(2) 格子の数え上げ（台形）', round(grid_area(trap)), round(float(a_trap)))
eq('算8-3(3) 三角形ACDの面積', A(3, 3), f'{shoelace(tri_acd):g}cm²')
eq('算8-3(3) 格子の数え上げ', round(grid_area(tri_acd)), round(float(shoelace(tri_acd))))
r34 = shoelace(tri_abc) / a_para
eq('算8-3(4) 三角形ABC÷平行四辺形', A(3, 4), f'<{r34.numerator}/{r34.denominator}>倍')
eq('算8-3(4) 格子の数え上げ', round(grid_area(tri_abc) / grid_area(para), 2), round(float(r34), 2))
eq('算8-3(4) 三角形ABC＋ACD＝台形', shoelace(tri_abc) + shoelace(tri_acd), a_trap)
eq('算8-3 図の文字（6cm・14cm・4cm）', sorted(p[2] for p in prims(3) if p[0] == 'text' and 'cm' in p[2]), sorted([f'{fg:g}cm', f'{bc:g}cm', f'{gap:g}cm', f'{gap:g}cm']))

# ============================================================ 第04セット：水そうとグラフ（区分ごとの式・1秒きざみ）
g4 = figargs(4)['series'][0]['pts']
v0 = rx(r'(\d+)Lの水が入っています', lead(4))
eq('算8-4 図のグラフの、はじめの水の量＝問題文の40L', g4[0], (0, int(v0)))
rate_b, rate_a = int(AN(4, 1)[0]), int(AN(4, 2)[0])
t_close = g4[1][0] * 60                                    # A管を閉じる秒（グラフのとがった点）


def tank_trace(open_both=True, until=20 * 60):
    """1秒きざみの水の量（Fraction）。open_both=False なら、閉じない。"""
    v, tr = Fr(int(v0)), [Fr(int(v0))]
    for t in range(until):
        inflow = rate_a if (open_both is False or t < t_close) else 0
        v += Fr(inflow - rate_b, 60)
        tr.append(v)
    return tr


tr = tank_trace()
eq('算8-4 グラフと一致：5分後80L・10分後0L', (tr[300], tr[600]), (Fr(g4[1][1]), Fr(g4[2][1])))
eq('算8-4(1) B管（A管を閉じたあとの、1分間の減る量）', A(4, 1), f'{(tr[300] - tr[360]):g}L')
eq('算8-4(2) A管（2本とも開いている間のふえる量に、B管の量をたす）', A(4, 2), f'{(tr[60] - tr[0]) + rate_b:g}L')
want64 = int(rx(r'(\d+)Lになる', Q(4, 3)))
hits = [t for t in range(len(tr)) if tr[t] == want64]
eq('算8-4(3) 64Lになる時刻（1秒きざみ）', [f'{Fr(t, 60):g}分後' for t in hits], S[3]['qs'][2]['ans'])
want104 = int(rx(r'(\d+)Lになる', Q(4, 4)))
tr_open = tank_trace(open_both=False, until=20 * 60)
eq('算8-4(4) 閉じないとき、104Lになる時刻', A(4, 4), f'{Fr([t for t in range(len(tr_open)) if tr_open[t] == want104][0], 60):g}分後')

# ============================================================ 第05セット：速さのグラフ（兄と妹、本屋）
g5 = figargs(5)['series'][0]['pts']
D5 = int(rx(r'家から(\d+)mはなれた', lead(5)))


def pos_at(pts, t):
    """折れ線 pts（(時間, 値)）の、時間 t（Fraction）での値。"""
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return Fr(v1) + Fr(v2 - v1, t2 - t1) * (t - t1)
    raise ValueError(t)


speeds5 = sorted({Fr(v2 - v1, t2 - t1) for (t1, v1), (t2, v2) in zip(g5, g5[1:]) if v1 != v2}, key=abs)
eq('算8-5 グラフ：歩いている間の速さは、行きも帰りも同じ', [abs(x) for x in speeds5], [Fr(60), Fr(60)] if len(speeds5) == 2 else None)
eq('算8-5 グラフの本屋＝問題文の1500m', max(v for _, v in g5), D5)
eq('算8-5(1) 歩く速さ', A(5, 1), f'分速{abs(speeds5[0]):g}m')
rest = [(t1, v1) for (t1, v1), (t2, v2) in zip(g5, g5[1:]) if v1 == v2 and 0 < v1 < D5]          # 休けい：道のりが変わらず、本屋でもない
eq('算8-5(2) 休けいした場所から、本屋まで', A(5, 2), f'{D5 - rest[0][1]}m')
q53 = Q(5, 3)
sis_start = int(re.search(r'(\d+)分後に', q53).group(1))
sis_v = int(re.search(r'分速(\d+)m', q53).group(1))
sis_shop = int(re.search(r'(\d+)分間買い物', q53).group(1))


def sister_trace():
    """妹の位置（m）を、1秒きざみに。家を出る→本屋まで→買い物→帰る。"""
    t, p, phase, tr, shop_left, home = 0, Fr(0), 'wait', {}, None, None
    while home is None:
        if t == sis_start * 60:
            phase = 'go'
        if phase == 'go':
            p += Fr(sis_v, 60)
            if p >= D5:
                phase, shop_left = 'shop', sis_shop * 60
        elif phase == 'shop':
            shop_left -= 1
            if shop_left == 0:
                phase = 'back'
        elif phase == 'back':
            p -= Fr(sis_v, 60)
            if p <= 0:
                home = t + 1
        t += 1
    return home


sis_home = sister_trace()
bro_home = g5[-1][0] * 60
eq('算8-5(3) 先に着いたのは、妹で、何分早い（1秒きざみ）', S[4]['qs'][2]['ans'], ['妹' if sis_home < bro_home else '兄', f'{Fr(abs(bro_home - sis_home), 60):g}分'])
want5 = int(rx(r'家から(\d+)mの地点', Q(5, 4)))
t_pass = [t for t in range(40 * 60, 65 * 60 + 1) if pos_at(g5, Fr(t, 60)) <= want5][0]
eq('算8-5(4) 帰り道で、家から600mを通る時刻（1秒きざみ）', A(5, 4), f'{Fr(t_pass, 60):g}分後')

# ============================================================ 第06セット：速さのグラフ（姉は図書館へ、兄が追いかける）
g6 = figargs(6)['series'][0]['pts']
D6 = int(rx(r'家から([\d.]+)kmはなれた', lead(6)) * 1000)
eq('算8-6 グラフの図書館＝問題文の4.8km', Fr(str(g6[1][1])) * 1000, D6)
sis6 = [(t, Fr(str(v)) * 1000) for t, v in g6]                    # (分, m)
eq('算8-6(1) 姉の速さ（グラフの、行きの区間から）', A(6, 1), f'分速{(sis6[1][1] - sis6[0][1]) / (sis6[1][0] - sis6[0][0]):g}m')
eq('算8-6(1) 帰りも同じ速さ（問題文）', (sis6[1][1] - sis6[0][1]) / (sis6[1][0] - sis6[0][0]), (sis6[2][1] - sis6[3][1]) / (sis6[3][0] - sis6[2][0]))
eq('算8-6(2) 図書館にいた時間', A(6, 2), f'{sis6[2][0] - sis6[1][0]}分間')
q63 = Q(6, 3)
start6 = int(re.search(r'(\d+)分後に', q63).group(1))
t_leave = sis6[2][0]
vb6 = [v for v in range(1, 2000) if v * (t_leave - start6) == D6 / 2][0]                   # 姉が図書館を出るとき、兄が真ん中
eq('算8-6(3) 兄の速さ（姉が出るときに、兄が真ん中という条件を満たす速さ）', A(6, 3), f'分速{vb6}m')
sec = [s for s in range(start6 * 60, 82 * 60) if Fr(vb6 * (s - start6 * 60), 60) >= pos_at(sis6, Fr(s, 60)) and s > t_leave * 60][0]
eq('算8-6(4) 出会う時刻で、2人の位置が一致（1秒きざみ）', Fr(vb6 * (sec - start6 * 60), 60), pos_at(sis6, Fr(sec, 60)))
eq('算8-6(4) 兄が家を出てから、出会うまで', A(6, 4), mmss(sec - start6 * 60) + '後')

# ============================================================ 第07セット：立体（細かい和・立方体の数え上げ）
(_, h7), (_, s7) = figargs(7)['specs']
d7, Lc = h7['d'], h7['L']
N = 200000                                                  # 半円の面積を、細い短冊の和で（本物のπ）
r7 = d7 / 2
area_pi = sum(math.sqrt(max(0.0, r7 * r7 - (r7 - (k + .5) * d7 / N) ** 2)) * d7 / N for k in range(N))
arc_pi = sum(math.hypot(d7 / N, math.sqrt(max(0, r7 * r7 - (r7 - (k + 1) * d7 / N) ** 2)) - math.sqrt(max(0, r7 * r7 - (r7 - k * d7 / N) ** 2))) for k in range(N))
vol_pi = area_pi * Lc
surf_pi = 2 * area_pi + arc_pi * Lc + d7 * Lc
pi314 = Fr('3.14')
eq('算8-7(1) 半円柱の体積（3.14で）', A(7, 1), f'{pi314 * Fr(d7, 2) ** 2 / 2 * Lc:g}cm³')
eq('算8-7(1) 本物のπとの差が0.1%以内（細かい和）', abs(vol_pi - float(AN(7, 1)[0])) / vol_pi < 0.001, True)
eq('算8-7(2) 半円柱の表面積（3.14で）', A(7, 2), f'{pi314 * Fr(d7, 2) ** 2 + pi314 * d7 * Lc / 2 + d7 * Lc:g}cm²')
eq('算8-7(2) 本物のπとの差が0.1%以内（細かい和）', abs(surf_pi - float(AN(7, 2)[0])) / surf_pi < 0.001, True)
ws, hs, dep = s7['w'], s7['h'], s7['depth']
vox = set()
x0 = 0
for w_, h_ in zip(ws, hs):
    for x in range(x0, x0 + w_):
        for y in range(dep):
            for z in range(h_):
                vox.add((x, y, z))
    x0 += w_
faces = sum(1 for (x, y, z) in vox for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)) if (x + dx, y + dy, z + dz) not in vox)
eq('算8-7(3) 階段状の柱の体積（1cmの立方体の数）', A(7, 3), f'{len(vox)}cm³')
eq('算8-7(4) 階段状の柱の表面積（外にむいた面の数）', A(7, 4), f'{faces}cm²')
eq('算8-7 図の高さ：左の全体の高さ＝段の高さの和＋右の高さ', hs[0], sum(hs[k] - hs[k + 1] for k in range(len(hs) - 1)) + hs[-1])
eq('算8-7 階段が、左から右へ低くなる', all(hs[k] > hs[k + 1] for k in range(len(hs) - 1)), True)

# ============================================================ 第08セット：ろうそく（1分きざみ→細かく）
g8a, g8b = figargs(8)['series'][0]['pts'], figargs(8)['series'][1]['pts']
l8 = lead(8)
a0 = int(rx(r'ろうそくアの火をつける前の長さは(\d+)cm', l8))
rate_b8 = rx(r'1分間に([\d.]+)cmずつ短くなり', l8)
burn_b = int(rx(r'(\d+)分後に燃えつきます', l8))
t_eq = int(re.search(r'(\d+)分後に、2本', Q(8, 2)).group(1))
eq('算8-8 グラフの目もり：ア30cm・イは80分で0cm', (g8a[0], g8b[1][0]), ((0, a0), burn_b))
eq('算8-8 グラフのイ：1分間に0.25cmの傾き', Fr(g8b[0][1] - g8b[1][1], g8b[1][0] - g8b[0][0]), rate_b8)
b0 = rate_b8 * burn_b
eq('算8-8(1) イの、はじめの長さ', A(8, 1), f'{b0:g}cm')
eq('算8-8(1) グラフにかいたイの出発点と一致', g8b[0][1], b0)
ks = [Fr(k, 100) for k in range(1, 300) if a0 - Fr(k, 100) * t_eq == b0 - rate_b8 * t_eq]      # アの、1分間に短くなる長さ（総あたり）
eq('算8-8(2) アの、1分間に短くなる長さ', A(8, 2), f'{ks[0]:g}cm' if len(ks) == 1 else None)
ka = ks[0]
t_end_a = a0 / ka
eq('算8-8 グラフにかいたアの終点（燃えつきる時刻）', g8a[1][0], t_end_a)
eq('算8-8(3) アが燃えつきたときのイの長さ', A(8, 3), f'{b0 - rate_b8 * t_end_a:g}cm')
diff = int(rx(r'差が(\d+)cmになる', Q(8, 4)))
ts = [Fr(k, 4) for k in range(0, int(t_end_a) * 4 + 1) if abs((a0 - ka * Fr(k, 4)) - (b0 - rate_b8 * Fr(k, 4))) == diff]
eq('算8-8(4) 長さの差が9cmになる時刻（15秒きざみ）', [f'{t:g}分後' for t in ts], S[7]['qs'][3]['ans'])

# ============================================================ 第09セット：割合と比（総あたり）
l9 = lead(9)
tot9 = int(rx(r'あわせて(\d+)人', l9))
rm, rf_ = [int(x) for x in re.search(r'(\d+)：(\d+)', l9).groups()]
cand = [(m, tot9 - m) for m in range(tot9 + 1) if m * rf_ == (tot9 - m) * rm]
eq('算8-9(1) 男子の人数（男子：女子＝4：3、合計168の総あたり）', A(9, 1), f'{cand[0][0]}人' if len(cand) == 1 else None)
men, women = cand[0]
fm = Fr(int(rx(r'男子の<(\d+)/(\d+)>', Q(9, 2), 1)), int(rx(r'男子の<(\d+)/(\d+)>', Q(9, 2), 2)))
ff = Fr(int(rx(r'女子の<(\d+)/(\d+)>', Q(9, 2), 1)), int(rx(r'女子の<(\d+)/(\d+)>', Q(9, 2), 2)))
absent_m, absent_f = men * fm, women * ff
eq('算8-9(2) 欠席した人数（整数になる）', (A(9, 2), absent_m.denominator, absent_f.denominator), (f'{absent_m + absent_f:g}人', 1, 1))
present_m, present_f = men - absent_m, women - absent_f
eq('算8-9(3) 出席した男子は、全体の何%', A(9, 3), f'{Fr(present_m, tot9) * 100:g}%')
rg = math.gcd(int(present_m), int(present_f))
eq('算8-9(4) 出席した男子：女子（もっとも簡単な整数の比）', A(9, 4), f'{int(present_m) // rg}：{int(present_f) // rg}')
r1, r2 = [int(x) for x in re.search(r'比が(\d+)：(\d+)に', Q(9, 5)).groups()]
xs = [x for x in range(0, 1000) if (men + x) * r2 == women * r1]
eq('算8-9(5) 転入した男子の人数（比が3：2になるxの総あたり）', A(9, 5), f'{xs[0]}人' if len(xs) == 1 else None)
eq('算8-9(5) 問題文の比と、(4)の比がちがう（答えが同じにならない）', (r1, r2) != (int(present_m) // rg, int(present_f) // rg), True)

# ============================================================ 第10セット：弟と兄のグラフ（1秒きざみ）と玉の割合（総あたり）
l10 = lead(10)
v_ot = int(re.search(r'分速(\d+)m', l10).group(1))
t_ot = int(re.search(r'10時(\d+)分に駅に着きました', l10).group(1))
t_br = int(re.search(r'10時(\d+)分に家に着きました', l10).group(1))
g10a, g10b = figargs(10)['series'][0]['pts'], figargs(10)['series'][1]['pts']
D10 = v_ot * t_ot
eq('算8-10(1) 家から駅まで', A(10, 1), f'{D10}m')
eq('算8-10 グラフ：弟は(40, 2400)、兄は駅(0, 2400)から(24, 0)', (g10a[1], g10b[0], g10b[1]), ((t_ot, D10), (0, D10), (t_br, 0)))
eq('算8-10 グラフの縦の最大＝駅の位置', figargs(10)['ymax'], D10)
vbr = [v for v in range(1, 1000) if v * t_br == D10][0]
eq('算8-10(2) 兄の速さ', A(10, 2), f'分速{vbr}m')
sec10 = [s for s in range(0, 40 * 60) if Fr(v_ot * s, 60) >= D10 - Fr(vbr * s, 60)][0]
eq('算8-10(3) 出会う時刻（1秒きざみ）', A(10, 3), f'10時{Fr(sec10, 60):g}分')
q104 = S[9]['qs'][3]
tot_u = int(rx(r'合わせて(\d+)個入っていて', q104['head']))
pct_w = int(rx(r'そのうち(\d+)%が白玉', q104['head']))
white_u = Fr(tot_u * pct_w, 100)
red_u = tot_u - white_u
eq('算8-10(4) ウの赤玉', A(10, 4), f'{red_u:g}個')
red_i = int(rx(r'赤玉だけが(\d+)個', q104['head']))
eq('算8-10(5) イとウを混ぜたときの、赤玉の割合', A(10, 5), f'{Fr(red_i + red_u, red_i + tot_u) * 100:g}%')
ra, wa = [int(x) for x in re.search(r'比は、(\d+)：(\d+)', q104['head']).groups()]
r_mix, w_mix = [int(x) for x in re.search(r'比が(\d+)：(\d+)に', Q(10, 6)).groups()]
cands = [w for w in range(1, 3000) if (w * ra) % wa == 0 and (w * ra // wa + red_i) * w_mix == w * r_mix]
eq('算8-10(6) アの白玉の個数（赤玉と白玉の比が3：1になる個数の総あたり）', A(10, 6), f'{cands[0]}個' if len(cands) == 1 else None)

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
