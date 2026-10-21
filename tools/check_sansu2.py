"""算数 大問2（小問集合）の検算。

データ（tenri_rs_sansu2.py）の答えを、問題文から数を取り出して、解説とは別の方法（総あたり・しらみつぶし・シミュレーション・
座標・ボクセルの数え上げ・3次元で折りたたむ）で計算しなおした値と比べる。
import しただけで検算が走る（tools/check_tenri_rs.py が、check_sansu*.py をすべて import する）。
単独では、`cd tools && python -X utf8 check_sansu2.py`。
"""
import itertools
import math
import re
from fractions import Fraction as Fr

from check_common import FAIL, eq, ans, q_text, val
import tenri_rs_sansu2 as M2

N = len(M2.SETS)


# ---------------- 部品 ----------------
NUM = re.compile(r'<(?:(\d+) )?(\d+)/(\d+)>|\d+\.\d+|\d+')


def nums(s):
    """文の中の数（整数・小数・<分数>・<帯分数>）を、出てきた順に、Fraction で返す。"""
    out = []
    for m in NUM.finditer(s):
        t = m.group(0)
        if t.startswith('<'):
            out.append(Fr(int(m.group(1) or 0)) + Fr(int(m.group(2)), int(m.group(3))))
        else:
            out.append(Fr(t))
    return out


def Q(s, q):
    return nums(q_text(M2, s, q))


def A(s, q):
    """答え（文字列）の中の数を、出てきた順に。"""
    a = ans(M2, s, q)
    return nums(' '.join(a) if isinstance(a, list) else a)


def A1(s, q):
    return A(s, q)[0]


def qs_(s, q):
    return M2.SETS[s - 1]['qs'][q - 1]


def half_up(x, unit):
    """x（0以上）を、unit の倍数に四捨五入する。"""
    if isinstance(x, int) and unit % 2 == 0:
        return (x + unit // 2) // unit * unit
    return int(math.floor(Fr(x) / unit + Fr(1, 2))) * unit


def lcm_brute(a, b):
    n = 1
    while n % a or n % b:
        n += 1
    return n


def gcd_brute(a, b):
    return max(d for d in range(1, min(a, b) + 1) if a % d == 0 and b % d == 0)


KANJI_NUM = {'三': 3, '四': 4, '五': 5, '六': 6, '七': 7, '八': 8, '九': 9, '十': 10}


# ---------------- 形式 ----------------
eq('算2 セットの数・年度', ([st['year'] for st in M2.SETS], len(M2.SETS)),
   ([2024, 2023, 2022, 2021, 2020, 2019, 2018, 2017, 2016, 2015], 10))
eq('算2 各セットの小問の数（2024…2016と、第10セット）', [len(st['qs']) for st in M2.SETS], [4, 6, 6, 6, 8, 5, 5, 6, 7, 7])

bad = []
seen_q = set()
for i, st in enumerate(M2.SETS, 1):
    for j, q in enumerate(st['qs'], 1):
        if q['q'] in seen_q:
            bad.append((i, j, '問題文がほかと同じ'))
        seen_q.add(q['q'])
        # 答えに単位があるとき、解答らんの unit と合っているか
        if q.get('unit') and not q['ans'].endswith(q['unit']):
            bad.append((i, j, 'unit と答えの単位がちがう', q['unit'], q['ans']))
        # 分数の書き方：<…> が、すべて <a/b> か <w a/b> の形
        for part in (q['q'], q['ex']):
            if part.count('<') != len(re.findall(r'<(?:\d+ )?\d+/\d+>', part)) or part.count('>') != part.count('<'):
                bad.append((i, j, '分数の書き方', part[:20]))
        # 答えの数が、解説にも出てくる
        ans_list = q['ans'] if q['kind'] == 'grid' else [q['ans']]
        for a_ in ans_list:
            for n_ in re.findall(r'\d+(?:\.\d+)?', a_):
                if n_ not in q['ex'].replace(',', ''):
                    bad.append((i, j, '答えの数が解説にない', n_))
        # 解説の中の「A＝B＝C」の等式を、数だけの式は、値で確かめる（式のまとまり＝数・かっこ・＋－×÷・＜分数＞の続き）
        for m in re.finditer(r'[\d.＋－×÷()<>/ ＝]*＝[\d.＋－×÷()<>/ ＝]*', q['ex']):
            if q['ex'][m.end():m.end() + 1] == '…' or q['ex'][m.end():m.end() + 3] == 'あまり':
                continue
            vs = []
            for side in m.group(0).split('＝'):
                try:
                    vs.append(val(side.strip()))
                except Exception:
                    pass
            if len(set(vs)) > 1:
                bad.append((i, j, '解説の等式が成り立たない', m.group(0), [str(v) for v in vs]))
eq(f'算2 全{sum(len(s["qs"]) for s in M2.SETS)}問：問題文の重複なし・unit・分数の書き方・答えの数が解説にある・解説の等式', bad, [])

# ---------------- 第01セット（2024） ----------------
a, b = Q(1, 1)
eq('算2-1(1) 最小公倍数45と60', A1(1, 1), lcm_brute(int(a), int(b)))
m_, p_ = Q(1, 2)
eq('算2-1(2) 2.5mの36%をcmで', A1(1, 2), m_ * 100 * p_ / 100)
km, v = Q(1, 3)
eq('算2-1(3) 6.3kmを分速90m', A1(1, 3), km * 1000 / v)
lo, hi, d1, d2 = [int(x) for x in Q(1, 4)]
eq('算2-1(4) 1〜150の、6の倍数で8の倍数でない数', A1(1, 4), sum(1 for n in range(lo, hi + 1) if n % d1 == 0 and n % d2 != 0))

# ---------------- 第02セット（2023） ----------------
km, h, mn = Q(2, 1)
eq('算2-2(1) 21kmを3時間30分の時速', A1(2, 1), km / (h + mn / 60))
f_, m_ = Q(2, 2)
eq('算2-2(2) <17/4>mは4mより何cm', A1(2, 2), (f_ - m_) * 100)
t_ = int(Q(2, 3)[0])
eq('算2-2(3) 十の位を四捨五入して2300になる最大の整数',
   A1(2, 3), max(n for n in range(0, 10000) if half_up(n, 100) == t_))
a, b = [int(x) for x in Q(2, 4)]
eq('算2-2(4) 最大公約数84と126', A1(2, 4), gcd_brute(a, b))
rows = M2.SETS[1]['table']['rows']
dens = {r[0]: Fr(r[1]) / Fr(r[2]) for r in rows[1:]}
top_ = max(dens, key=dens.get)
fr_ = dens[top_] % 100
eq('算2-2(5) 人口密度がいちばん高い市町村の、百の位までのがい数', A1(2, 5), half_up(dens[top_], 100))
eq('算2-2(5) 四捨五入の境目に近くない（十の位以下が50±1にならない）', abs(fr_ - 50) > 1, True)
eq('算2-2(5) 人口密度が、いちばん高いのは人口がいちばん多い所ではない（まちがいやすい形）', top_ != max(rows[1:], key=lambda r: Fr(r[1]))[0], True)
q26 = q_text(M2, 2, 6)
f1, f2, f3 = [nums(t)[0] for t in re.findall(r'<\d+/\d+>', q26)]
pg = int(re.search(r'(\d+)ページ読', q26).group(1))
sol = [T for T in range(1, 2000)
       if (T - T * f1) - (T - T * f1) * f2 - pg == T * f3 and all(Fr(x).denominator == 1 for x in (T * f1, (T - T * f1) * f2))]
eq('算2-2(6) 本のページ数（全体を総あたり）', [A1(2, 6)], sol)

# ---------------- 第03セット（2022） ----------------
a, b = [int(x) for x in Q(3, 1)]
eq('算2-3(1) 最大公約数54と90', A1(3, 1), gcd_brute(a, b))
base, pct = Q(3, 2)
eq('算2-3(2) 450Lの24%', A1(3, 2), base * pct / 100)
sp_, h, mn = Q(3, 3)
eq('算2-3(3) 時速5kmで1時間36分', A1(3, 3), sp_ * (h + Fr(mn, 60)))
ra, rb, tot = [int(x) for x in Q(3, 4)]
eq('算2-3(4) 比3：4で合計98個のとき後ろの数',
   A1(3, 4), [(x, tot - x) for x in range(tot + 1) if x * rb == (tot - x) * ra][0][1])
q35 = q_text(M2, 3, 5)
tot = int(re.search(r'長さ(\d+)cm', q35).group(1))
mult = int(re.search(r'(\d+)倍', q35).group(1))
diff = int(re.search(r'より(\d+)cm長い', q35).group(1))
sols = [(s, 3 * s - diff, 3 * s) for s in range(1, tot) if mult * s - diff > s and s + (mult * s - diff) + mult * s == tot]
eq('算2-3(5) 3本のロープ：1通りに決まり、もっとも長いロープ', (len(sols), sols[0][2] if sols else None), (1, A1(3, 5)))
teams = int(Q(3, 6)[0])
eq('算2-3(6) 総当たり戦', A1(3, 6), len(list(itertools.combinations(range(teams), 2))))

# ---------------- 第04セット（2021） ----------------
sq_area, rect_area = [int(x) for x in re.findall(r'面積が(\d+)cm', q_text(M2, 4, 1))]
side = math.isqrt(sq_area)
eq('算2-4(1) 正方形の面積が平方数', side * side, sq_area)
perim = 4 * side
pairs = [(Fr(k, 4), Fr(rect_area) / Fr(k, 4)) for k in range(1, 4 * perim)
         if 2 * (Fr(k, 4) + Fr(rect_area) / Fr(k, 4)) == perim and Fr(k, 4) < Fr(rect_area) / Fr(k, 4)]
eq('算2-4(1) 周が等しい長方形のたてとよこ（1通りだけ）', ([str(x) for x in A(4, 1)], len(pairs)), ([str(pairs[0][0]), str(pairs[0][1])], 1))
total, pct = Q(4, 2)
eq('算2-4(2) 1800人の42%が女性→男性', A1(4, 2), total - total * pct / 100)
km, v = Q(4, 3)
mins = km / v * 60
eq('算2-4(3) 18kmを時速8km（何時間何分）', A(4, 3), [Fr(int(mins // 60)), mins % 60])
base, area = Q(4, 4)
eq('算2-4(4) 底辺6cm・面積45cm²の三角形の高さ', A1(4, 4), [Fr(hh) for hh in range(1, 200) if base * hh / 2 == area][0])
runners = int(Q(4, 5)[0])
third = int(Q(4, 5)[1])
eq('算2-4(5) 5人のリレーで、Aが第3走者', A1(4, 5),
   sum(1 for p in itertools.permutations('ABCDE', runners) if p[third - 1] == 'A'))
q46 = q_text(M2, 4, 6)
pa, pb = [int(x) for x in re.findall(r'1本(\d+)円', q46)]
cnt = int(re.search(r'合わせて(\d+)本', q46).group(1))
cost = int(re.search(r'代金は(\d+)円', q46).group(1))
eq('算2-4(6) つるかめ算（えんぴつとボールペン）', A1(4, 6), [b_ for b_ in range(cnt + 1) if pa * (cnt - b_) + pb * b_ == cost][0])

# ---------------- 第05セット（2020） ----------------
sec = Q(5, 1)[0]
eq('算2-5(1) 秒針が35秒間に動く角度', A1(5, 1), Fr(360) * sec / 60)
pop, keep = int(Q(5, 2)[0]), int(Q(5, 2)[1])
digits = len(str(pop))
eq('算2-5(2) 上から3けたのがい数', A1(5, 2), half_up(pop, 10 ** (digits - keep)))
price, pct = Q(5, 3)
eq('算2-5(3) 1800円の15%', A1(5, 3), price * pct / 100)
ra, rb = [int(x) for x in Q(5, 4)]
simple = [(x, y) for x in range(1, ra + 1) for y in range(1, rb + 1) if x * rb == y * ra][0]
eq('算2-5(4) 比72：108を簡単にする', ans(M2, 5, 4), f'{simple[0]}：{simple[1]}')
ca, cb = [int(x) for x in Q(5, 5)[:2]]
s_ = [s for s in range(1, 1000) if s % ca == 0 and s % cb == 0][0]
eq('算2-5(5) 正方形をつくるカードの枚数', A1(5, 5), (s_ // ca) * (s_ // cb))
q56 = q_text(M2, 5, 6)
vol = int(re.search(r'体積が(\d+)cm', q56).group(1))
k_ = int(re.search(r'(\d+)倍', q56).group(1))
side = [x for x in range(1, 50) if x ** 3 == vol][0]
eq('算2-5(6) 立方体の1辺を3倍にした体積', A1(5, 6), (side * k_) ** 3)
fig5 = M2.SETS[4]['fig']['args']
tab = fig5['table']['rows']
perim = int(Q(5, 7)[0])
cols = []
for j in range(1, len(tab[0])):
    cols.append((tab[0][j], tab[1][j]))
unknown = {}
ok_cols = []
for xv, yv in cols:
    if xv.isdigit() and yv.isdigit():
        ok_cols.append(2 * (int(xv) + int(yv)) == perim)
    elif xv.isdigit() and yv in 'アイ':
        unknown[yv] = [y for y in range(1, perim) if 2 * (int(xv) + y) == perim][0]
    elif yv.isdigit() and xv in 'アイ':
        unknown[xv] = [x for x in range(1, perim) if 2 * (x + int(yv)) == perim][0]
eq('算2-5(7) 表の、数の入っている列は、周が30cmの長方形になっている', all(ok_cols) and len(ok_cols) >= 1, True)
eq('算2-5(7) 表のア・イ（周が一定の長方形）', [str(x) for x in A(5, 7)], [str(unknown['ア']), str(unknown['イ'])])


# --- 第05セット(8)：立方体の展開図を、3次元で折りたたんで調べる ---
def cross(u, w):
    return (u[1] * w[2] - u[2] * w[1], u[2] * w[0] - u[0] * w[2], u[0] * w[1] - u[1] * w[0])


def dot(u, w):
    return sum(x * y for x, y in zip(u, w))


def mv(M, v):
    return tuple(sum(M[i][j] * v[j] for j in range(3)) for i in range(3))


def mm(P, R):
    return tuple(tuple(sum(P[i][k] * R[k][j] for k in range(3)) for j in range(3)) for i in range(3))


def rot90(axis):
    cols = []
    for e in ((1, 0, 0), (0, 1, 0), (0, 0, 1)):
        c_, d_ = cross(axis, e), dot(axis, e)
        cols.append(tuple(c_[i] + axis[i] * d_ for i in range(3)))
    return tuple(tuple(cols[j][i] for j in range(3)) for i in range(3))


I3 = ((1, 0, 0), (0, 1, 0), (0, 0, 1))


def fold(cells):
    """展開図（(行, 列) のならび）の各面が、折りたたんだ立方体の、どの向き（外向きの法線）の面になるか。
    先頭の面を床（印刷面が上）に置き、となりの面を、辺のまわりに90度ずつ、下へ折る。"""
    cells = list(cells)
    T = {cells[0]: (I3, (Fr(0),) * 3)}
    queue = [cells[0]]
    while queue:
        u = queue.pop(0)
        Ru, tu = T[u]
        for dr, dc in ((0, 1), (0, -1), (1, 0), (-1, 0)):
            w = (u[0] + dr, u[1] + dc)
            if w in cells and w not in T:
                d = (dc, -dr, 0)
                Rot = rot90(cross(d, (0, 0, -1)))
                P0 = (Fr(u[1]) + Fr(1, 2) + Fr(dc, 2), -(Fr(u[0]) + Fr(1, 2)) - Fr(dr, 2), Fr(0))
                RP0 = mv(Rot, P0)
                tw_ = tuple(x + y for x, y in zip(mv(Ru, tuple(P0[i] - RP0[i] for i in range(3))), tu))
                T[w] = (mm(Ru, Rot), tw_)
                queue.append(w)
    return {cell: mv(T[cell][0], (0, 0, 1)) for cell in T}


ROTS = []
for perm in itertools.permutations(range(3)):
    for sg in itertools.product((1, -1), repeat=3):
        R_ = tuple(tuple(sg[i] if perm[i] == j else 0 for j in range(3)) for i in range(3))
        det = (R_[0][0] * (R_[1][1] * R_[2][2] - R_[1][2] * R_[2][1]) - R_[0][1] * (R_[1][0] * R_[2][2] - R_[1][2] * R_[2][0])
               + R_[0][2] * (R_[1][0] * R_[2][1] - R_[1][1] * R_[2][0]))
        if det == 1:
            ROTS.append(R_)

cube = fig5['cube']
VIEW = {cube['top']: (0, 0, 1), cube['front']: (0, -1, 0), cube['right']: (1, 0, 0)}      # 見える3つの面（上・手前・右）
verdict = {}
bad = []
for nt in fig5['nets']:
    cells = [tuple(c_) for c_ in nt['cells']]
    nrm = fold(cells)
    if len(cells) != 6 or len(set(nrm.values())) != 6:
        bad.append((nt['label'], '展開図になっていない'))
        continue
    mk = {(r_, k_): s_ for r_, k_, s_ in nt['marks']}
    if sorted(mk.values()) != sorted(VIEW) or any(c_ not in cells for c_ in mk):
        bad.append((nt['label'], 'しるしが、立方体と同じ3つでない'))
        continue
    ns = {s_: nrm[c_] for c_, s_ in mk.items()}
    opposite = any(ns[s1] == tuple(-x for x in ns[s2]) for s1, s2 in itertools.combinations(ns, 2))
    same = any(all(mv(R_, ns[s_]) == VIEW[s_] for s_ in ns) for R_ in ROTS)
    verdict[nt['label']] = 'ok' if same else ('opposite' if opposite else 'mirror')
eq('算2-5(8) 4つとも、立方体の展開図で、しるしが3つ', bad, [])
eq('算2-5(8) 見取図と同じ立方体になる展開図（折りたたんで回して、しるしが重なる）', ans(M2, 5, 8), '・'.join(k for k, v in verdict.items() if v == 'ok'))
eq('算2-5(8) 解説の、ちがう理由（ア・エ＝向きがぎゃく、イ＝向かい合う面）', [verdict['ア'], verdict['イ'], verdict['エ']], ['mirror', 'opposite', 'mirror'])
eq('算2-5(8) 問題文の○・×・●が、図のしるしと同じ', sorted(re.findall(r'[○×●]', q_text(M2, 5, 8).split('（')[0])), sorted(VIEW))

# ---------------- 第06セット（2019） ----------------
km, v = Q(6, 1)
eq('算2-6(1) 5.4kmを分速60m', A1(6, 1), km * 1000 / v)
nside = KANJI_NUM[re.search(r'正(.)角形', q_text(M2, 6, 2)).group(1)]
pts = [(math.cos(2 * math.pi * k / nside), math.sin(2 * math.pi * k / nside)) for k in range(nside)]
v0, v1, v2 = pts[0], pts[1], pts[-1]
u1, u2 = (v1[0] - v0[0], v1[1] - v0[1]), (v2[0] - v0[0], v2[1] - v0[1])
ang = math.degrees(math.acos(dot(u1 + (0,), u2 + (0,)) / math.hypot(*u1) / math.hypot(*u2)))
eq('算2-6(2) 正八角形の1つの角（頂点の座標から）', A1(6, 2), round(ang))
eq('算2-6(2) 座標から求めた角が整数', abs(ang - round(ang)) < 1e-9, True)
fig6 = M2.SETS[5]['fig']['args']['panels']
P3 = {pr[2]: pr[1] for pr in fig6[0]['prims'] if pr[0] == 'pt'}
Pa, Pb, Pc, Pd, Pe = (P3[k] for k in 'ABCDE')


def dist(p1, p2):
    return math.hypot(p1[0] - p2[0], p1[1] - p2[1])


def angle_at(vx, p1, p2):
    u_, w_ = (p1[0] - vx[0], p1[1] - vx[1]), (p2[0] - vx[0], p2[1] - vx[1])
    return math.degrees(math.acos((u_[0] * w_[0] + u_[1] * w_[1]) / math.hypot(*u_) / math.hypot(*w_)))


eq('算2-6(3) 図：ABCDは正方形、CDEは正三角形（座標）',
   (round(dist(Pa, Pb), 3) == round(dist(Pb, Pc), 3) == round(dist(Pc, Pd), 3) == round(dist(Pd, Pa), 3) and abs(angle_at(Pb, Pa, Pc) - 90) < 1e-6 and
    round(dist(Pc, Pd), 2) == round(dist(Pd, Pe), 2) == round(dist(Pc, Pe), 2)), True)
eq('算2-6(3) 角ア＝角AEC（図の座標から）', A1(6, 3), round(angle_at(Pe, Pa, Pc), 6))
ang_prim = [pr for pr in fig6[0]['prims'] if pr[0] == 'angle'][0]
dirs = sorted(math.degrees(math.atan2(p[1] - Pe[1], p[0] - Pe[0])) % 360 for p in (Pa, Pc))
eq('算2-6(3) 図の角アの印が、EAとECの間', (round(ang_prim[2], 0), round(ang_prim[3], 0)), (round(dirs[0], 0), round(dirs[1], 0)))
q64 = q_text(M2, 6, 4)
edge = int(re.search(r'1辺が(\d+)cm', q64).group(1))
ra_, rb_ = [int(x) for x in re.search(r'体積の比が(\d+)：(\d+)の', q64).groups()]
cut = Fr(edge * ra_, ra_ + rb_)


def exposed(vox):
    n = 0
    for (x, y, z) in vox:
        for dx, dy, dz in ((1, 0, 0), (-1, 0, 0), (0, 1, 0), (0, -1, 0), (0, 0, 1), (0, 0, -1)):
            if (x + dx, y + dy, z + dz) not in vox:
                n += 1
    return n


A_ = {(x, y, z) for x in range(edge) for y in range(edge) for z in range(edge) if x < cut}
B_ = {(x, y, z) for x in range(edge) for y in range(edge) for z in range(edge) if x >= cut}
sa, sb = exposed(A_), exposed(B_)
g_ = math.gcd(sa, sb)
eq('算2-6(4) 立方体を3：5に切った2つの直方体の、表面積の比（ボクセルの面を数える）', ans(M2, 6, 4), f'{sa // g_}：{sb // g_}')
eq('算2-6(4) 体積の比が問題文のとおり', len(A_) * rb_ == len(B_) * ra_, True)
cutline = [pr for pr in fig6[1]['prims'] if pr[0] == 'line' and pr[-1].get('w') == 1.3][0]
front = [pr for pr in fig6[1]['prims'] if pr[0] == 'poly'][0][1]
eq('算2-6(4) 図：立方体の1辺8cm・切り口が、左から3cm', (max(p[0] for p in front), cutline[1][0], cutline[2][0], f'{edge}cm' in [pr[2] for pr in fig6[1]['prims'] if pr[0] == 'text']), (edge, cut, cut, True))
n60, last, n54 = [int(x) for x in Q(6, 5)]
marbles = [N_ for N_ in range(1, 5000)
           if N_ % n54 == 0 and (N_ - last) % n60 == 0 and N_ // n54 == (N_ - last) // n60 + 1]
eq('算2-6(5) ビー玉の過不足（総あたり）', [A1(6, 5)], marbles)

# ---------------- 第07セット（2018） ----------------
a, b = [int(x) for x in Q(7, 1)]
eq('算2-7(1) 最大公約数63と105', A1(7, 1), gcd_brute(a, b))
base, pct = Q(7, 2)
eq('算2-7(2) 40Lの35%', A1(7, 2), base * pct / 100)
nside = KANJI_NUM[re.search(r'正(.)角形', q_text(M2, 7, 3)).group(1)]
pts = [(math.cos(2 * math.pi * k / nside), math.sin(2 * math.pi * k / nside)) for k in range(nside)]


def axis_count(pts):
    cnt = 0
    for deg in range(0, 180):
        th = math.radians(deg)
        c2, s2 = math.cos(2 * th), math.sin(2 * th)
        refl = [(c2 * x + s2 * y, s2 * x - c2 * y) for x, y in pts]
        if all(any(abs(rx - px) < 1e-9 and abs(ry - py) < 1e-9 for px, py in pts) for rx, ry in refl):
            cnt += 1
    return cnt


eq('算2-7(3) 正六角形の対称の軸（頂点を折りかえして重なる線を調べる）', A1(7, 3), axis_count(pts))
km, v = Q(7, 4)
eq('算2-7(4) 5kmを時速12km（分）', A1(7, 4), km / v * 60)
q75 = q_text(M2, 7, 5)
sec_per_day = int(re.search(r'(\d+)秒ずつ', q75).group(1))
minutes = int(re.search(r'(\d+)分おくれる', q75).group(1))
late, day = 0, 0
while late < minutes * 60:
    late += sec_per_day
    day += 1
eq('算2-7(5) 1日8秒おくれる時計が6分おくれる日数（1日ずつ数える）', A1(7, 5), day)

# ---------------- 第08セット（2017） ----------------
sp_, mn = Q(8, 1)
eq('算2-8(1) 時速5kmで18分間', A1(8, 1), sp_ * 1000 * mn / 60)
lo, hi, d_ = [int(x) for x in Q(8, 2)]
eq('算2-8(2) 30〜120の、7の倍数', A1(8, 2), sum(1 for n in range(lo, hi + 1) if n % d_ == 0))
t_ = int(Q(8, 3)[0])
cand = [n for n in range(0, 1000000) if half_up(n, 10000) == t_]
eq('算2-8(3) 千の位を四捨五入して350000になる範囲（以上・未満）', [int(x) for x in A(8, 3)], [min(cand), max(cand) + 1])
fr_, cnt = Q(8, 4)[1], Q(8, 4)[0]
eq('算2-8(4) 全体の<2/7>が8人', A1(8, 4), [T for T in range(1, 1000) if T * fr_ == cnt][0])
r1, r2 = Q(8, 5)[0], Q(8, 5)[1]
pi_ = nums(M2.SETS[7]['lead'])[0]
eq('算2-8(5) 半径8cmと5cmの円の面積の差', A1(8, 5), pi_ * r1 * r1 - pi_ * r2 * r2)
q86 = q_text(M2, 8, 6)
side_ = int(re.search(r'長さが(\d+)cm', q86).group(1))
count_ = int(re.search(r'正方形(\d+)個', q86).group(1))
around = int(re.search(r'周りの長さが(\d+)cm', q86).group(1))
shorts = [min(a_, count_ // a_) * side_ for a_ in range(1, count_ + 1) if count_ % a_ == 0 and 2 * (a_ + count_ // a_) * side_ == around]
eq('算2-8(6) 正方形18個の長方形（周が54cmになるのは1通りで、短い辺）', [A1(8, 6)], list(set(shorts)))

# ---------------- 第09セット（2016） ----------------
a, b = Q(9, 1)
eq('算2-9(1) 9mは25mの何%', A1(9, 1), a / b * 100)
hrs = Q(9, 2)[0]
eq('算2-9(2) <8/3>時間は何時間何分', A(9, 2), [Fr(int(hrs)), (hrs - int(hrs)) * 60])
add1, mul1, add2, mul2, res = [int(x) for x in Q(9, 3)]
wrong = [x for x in range(0, 1000) if (x + add2) * mul2 == res]
eq('算2-9(3) 逆算（まちがえた式から、ある数を求め、正しい式で計算）', A1(9, 3), [(x + add1) * mul1 for x in wrong][0])
cards = [int(x) for x in re.findall(r'「(\d)」', q_text(M2, 9, 4))]
ev = {a_ * 10 + b_ for a_, b_ in itertools.permutations(cards, 2) if a_ != 0 and (a_ * 10 + b_) % 2 == 0}
eq('算2-9(4) 0〜4のカードで2けたの偶数', A1(9, 4), len(ev))
num_, den_ = [int(x) for x in re.findall(r'<(\d+)/(\d+)>', q_text(M2, 9, 5))[0]]
pos_ = int(re.search(r'第(\d+)位', q_text(M2, 9, 5)).group(1))
r_ = num_
dg = []
for _ in range(pos_):
    r_ *= 10
    dg.append(r_ // den_)
    r_ %= den_
eq('算2-9(5) <3/7>の小数第20位（わり算を20けたまで）', A1(9, 5), dg[-1])
base, area = Q(9, 6)
eq('算2-9(6) 底辺8cm・面積36cm²の三角形の高さ', A1(9, 6), [Fr(hh) for hh in range(1, 200) if base * hh / 2 == area][0])
dx, dy, dz = Q(9, 7)
eq('算2-9(7) 6×9×5の直方体の体積（1cm³の立方体を数える）', A1(9, 7), sum(1 for _ in itertools.product(range(int(dx)), range(int(dy)), range(int(dz)))))

# ---------------- 第10セット（2015・2014） ----------------
base, pct = Q(10, 1)
eq('算2-10(1) 280人の15%', A1(10, 1), base * pct / 100)
a, b = [int(x) for x in Q(10, 2)]
eq('算2-10(2) 最小公倍数16と40', A1(10, 2), lcm_brute(a, b))
price, wari = Q(10, 3)
eq('算2-10(3) 定価1500円の3割引き', A1(10, 3), price * (10 - wari) / 10)
sc = [int(x) for x in re.findall(r'(\d+)点', q_text(M2, 10, 4))]
known, avg = sc[:-1], sc[-1]
n_people = int(re.search(r'(\d+)人のテスト', q_text(M2, 10, 4)).group(1))
eq('算2-10(4) 平均点から□点（人数が、点数の数と合う）', (A1(10, 4), n_people), ([x for x in range(0, 101) if (sum(known) + x) == avg * n_people][0], len(known) + 1))
kcnt, total = [int(x) for x in Q(10, 5)]
eq('算2-10(5) 連続する3つの奇数の和が117', A1(10, 5), [a_ for a_ in range(1, 200, 2) if sum(a_ + 2 * k for k in range(kcnt)) == total][0])
p1, e1, p2, e2 = [int(x) for x in re.search(r'1人に(\d+)個ずつ配ると(\d+)個あまり、(\d+)個ずつ配ると(\d+)個たりません', q_text(M2, 10, 6)).groups()]
eq('算2-10(6) あめ玉（1人4個で7個あまり・6個で3個たりない）の子どもの数', A1(10, 6), [n for n in range(1, 200) if p1 * n + e1 == p2 * n - e2][0])
seq = [None if t == '□' else int(t) for t in re.split(r'、', q_text(M2, 10, 7).split('\n')[1])]
gap = seq.index(None)
cands = []
for x in range(1, 200):
    s_ = seq[:gap] + [x] + seq[gap + 1:]
    d_ = [s_[k + 1] - s_[k] for k in range(len(s_) - 1)]
    if len({d_[k + 1] - d_[k] for k in range(len(d_) - 1)}) == 1:
        cands.append(x)
eq('算2-10(7) 規則性（となり合う数の差が、同じだけふえる□は、1つだけ）', ([A1(10, 7)], len(cands)), (cands, 1))

if __name__ == '__main__':
    print('不一致:', len(FAIL), FAIL)
