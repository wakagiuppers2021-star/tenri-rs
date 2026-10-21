"""天理中 理科・社会・算数・国語 類題の答えを、データとは別の計算・事実表から確かめる。

使い方: python -X utf8 tools/check_tenri_rs.py
"""
from __future__ import annotations

import importlib
import itertools
import math
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tenri_rs_rika1 as R1
import tenri_rs_rika2 as R2
import tenri_rs_rika3 as R3
import tenri_rs_rika4 as R4
import tenri_rs_rika5 as R5
import tenri_rs_rika6 as R6
import tenri_rs_rika7 as R7
import tenri_rs_rika8 as R8
import tenri_rs_rika9 as R9
import tenri_rs_shakai1 as S1
import tenri_rs_shakai2 as S2
import tenri_rs_shakai3 as S3
import tenri_rs_shakai4 as S4
import tenri_rs_shakai5 as S5
import tenri_rs_sansu4 as M4
import tenri_rs_kokugo1 as K1
import tenri_rs_kokugo2 as K2
import tenri_rs_kokugo3 as K3
import tenri_rs_kokugo4 as K4
import ja_grammar
import world_outline
from build_tenri_rs import SANKEN_ARROWS, SHAPES

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


# ---------------- 理科・大問1 ----------------
V = 340
eq('理1-1(6) かみなり', ans(R1, 1, 6), f'{V * 5}m')
eq('理1-1(7) こだま', ans(R1, 1, 7), f'{V * 2 // 2}m')

# 回路：豆電球の抵抗を1、電池1個の電圧を1として電流を計算
bulb = {'ア': 1 / 1, 'イ': 1 / 2, 'ウ': 1 / 1, 'エ': 2 / 1}          # 豆電球1個に流れる電流
cell = {'ア': 1, 'イ': 1 / 2, 'ウ': 2, 'エ': 2}                    # 電池1個から出る電流
eq('理1-3(3) 明るい・暗い', ans(R1, 3, 3), [k for k in 'イウエ' if bulb[k] > bulb['ア']] + [k for k in 'イウエ' if bulb[k] < bulb['ア']])
eq('理1-3(6) 長もち', ans(R1, 3, 6), min(cell, key=cell.get))

eq('理1-4(7) 1時間の角度', ans(R1, 4, 7), f'{360 // 24}度')
eq('理1-5(6) 倍率', ans(R1, 5, 6), f'{10 * 40}倍')
eq('理1-6(5) 分銅', ans(R1, 6, 5), f'{20 + 10 + 5 + 2 + 1}g')

weights = [50, 20, 10, 10, 5, 2, 2, 1]
best = None
for r in range(1, len(weights) + 1):
    combos = {tuple(sorted(c, reverse=True)) for c in itertools.combinations(weights, r) if sum(c) == 63}
    if combos:
        best = combos
        break
assert best and len(best) == 1, best
eq('理1-6(6) 63gの最少個数', ans(R1, 6, 6), join(f'{w}g' for w in next(iter(best))))

# 重さ比べ：重い方→軽い方の関係からならべる
rel = [('A', 'B'), ('C', 'A'), ('B', 'D')]
order = [p for p in itertools.permutations('ABCD') if all(p.index(a) < p.index(b) for a, b in rel)]
assert len(order) == 1
eq('理1-6(8) 重い順', ans(R1, 6, 8), '→'.join(order[0]))

# 電磁石：1つの条件だけがちがう組
tab = {'ア': (50, 1), 'イ': (100, 1), 'ウ': (50, 2), 'エ': (100, 2)}
pairs_turn = [f'{a}と{b}' for a, b in itertools.combinations('アイウエ', 2) if tab[a][1] == tab[b][1] and tab[a][0] != tab[b][0]]
pairs_cell = [f'{a}と{b}' for a, b in itertools.combinations('アイウエ', 2) if tab[a][0] == tab[b][0] and tab[a][1] != tab[b][1]]
eq('理1-7(2) 巻き数の比較', ans(R1, 7, 2), f'{pairs_turn[0]}（{pairs_turn[1]}）')
eq('理1-7(3) 電池の比較', ans(R1, 7, 3), f'{pairs_cell[0]}（{pairs_cell[1]}）')

# 月：位置A〜Hは太陽の方向から反時計回りに45度ずつ
pos = {lab: k * 45 for k, lab in enumerate('ABCDEFGH')}
eq('理1-8(2) 満月', ans(R1, 8, 2), [k for k, a in pos.items() if a == 180][0])
eq('理1-8(3) 新月', ans(R1, 8, 3), [k for k, a in pos.items() if a == 0][0])
eq('理1-8(4) 上弦', ans(R1, 8, 4)[0], [k for k, a in pos.items() if a == 90][0])
eq('理1-8(6) 日食・月食', ans(R1, 8, 6), [[k for k, a in pos.items() if a == 0][0], [k for k, a in pos.items() if a == 180][0]])

eq('理1-9(7) 氷の体積', ans(R1, 9, 7), f'{round(200 * 1.1)}cm³')

avg = (20.3 + 19.8 + 20.0) / 3
eq('理1-10(5) 平均', ans(R1, 10, 5), f'{math.floor(avg * 10 + .5) / 10:.1f}秒')
table = {25: 1.0, 50: 1.4, 100: 2.0}
for L, t in table.items():
    th = 2 * math.pi * math.sqrt(L / 100 / 9.8)
    eq(f'理1-10 表の時間 {L}cm', round(th, 1), t)
eq('理1-10(7) 400cm', ans(R1, 10, 7), f'{2.0 * math.sqrt(400 / 100):.1f}秒')
cond = {'ア': (25, 20, 10), 'イ': (50, 20, 10), 'ウ': (100, 20, 10), 'エ': (100, 40, 10), 'オ': (100, 20, 20)}
only = lambda i: [f'{a}と{b}' for a, b in itertools.combinations(cond, 2)
                  if all((cond[a][k] == cond[b][k]) != (k == i) for k in range(3))]
eq('理1-10(1) 重さ', ans(R1, 10, 1), only(1)[0])
eq('理1-10(2) ふれはば', ans(R1, 10, 2), only(2)[0])

# ---------------- 理科・大問2 ----------------
# 1 熱の量（1gの水を1℃上げる熱＝1カロリー）
eq('理2-1(4) 熱の量', ans(R2, 1, 4), f'{100 * (50 - 20)}カロリー')
eq('理2-1(5) 上がる温度', ans(R2, 1, 5), f'{4500 // 300}℃')
mix = (60 * 200 + 15 * 100) / (200 + 100)
eq('理2-1(6) 混ぜた温度', ans(R2, 1, 6), f'{num(mix)}℃')
eq('理2-1(7) 氷→水', ans(R2, 1, 7), f'{num(330 / 1.1)}cm³')

# 2 地層：下から順の層、つぶの大きさ、断層がずらした層
column = [('E', 'れき'), ('D', '砂'), ('C', 'どろ'), ('B', '火山灰'), ('A', '砂')]
grain = {'れき': 3, '砂': 2, 'どろ': 1}
cut = {'E', 'D', 'C', 'B'}
eq('理2-2(1) 最も古い層', ans(R2, 2, 1), column[0][0])
sizes = [grain[m] for _, m in column[:3]]
trend = '深く' if all(a > b for a, b in zip(sizes, sizes[1:])) else '浅く' if all(a < b for a, b in zip(sizes, sizes[1:])) else '変わら'
eq('理2-2(4) 海の深さ', ans(R2, 2, 4), [k for k, v in choices(q_text(R2, 2, 4)).items() if trend in v][0])
idx = {lab: i for i, (lab, _) in enumerate(column)}
t_fault = max(idx[l] for l in cut) + .5
assert all(idx[l] > t_fault for l in idx if l not in cut)
when = {'ア': t_fault, 'イ': idx['A'], 'ウ': idx['B']}
eq('理2-2(8) できごとの順', ans(R2, 2, 8), '→'.join(sorted(when, key=when.get)))

# 3 磁石：ふれている極の反対の極がくぎの頭にでき、先は同じ極。ちがう極どうしが引き合う
opp = {'N': 'S', 'S': 'N'}
material = {'鉄のくぎ': '鉄', '銅のはり金': '銅', 'ガラスのびん': 'ガラス', '鉄のゼムクリップ': '鉄'}
eq('理2-3(1) 引きつけられる', ans(R2, 3, 1), join(k for k, v in choices(q_text(R2, 3, 1)).items() if material[v] == '鉄'))
tip = 'N'                       # N極にふれた頭はS極、先はN極
eq('理2-3(2) くぎの先', ans(R2, 3, 2), f'{tip}極')
eq('理2-3(3) 引きよせられる極', ans(R2, 3, 3), f'{opp[tip]}極')
eq('理2-3(4) 北極', ans(R2, 3, 4), f'{opp["N"]}極')
Y = opp['N']                    # 方位磁針のN極を引きつけた
eq('理2-3(5) Yのはし', ans(R2, 3, 5), f'{Y}極')
eq('理2-3(6) 電池を逆に', ans(R2, 3, 6), f'{opp[opp[Y]]}極')
E, r, R = 1.5, 1, 1             # 電池1個の電圧、コイル・豆電球の抵抗
cur = {'ア': 2 * E / r, 'イ': E / r, 'ウ': E / (r + R)}
eq('理2-3(7) 強い・弱い', ans(R2, 3, 7), [max(cur, key=cur.get), min(cur, key=cur.get)])

# 4 水蒸気：1m³の空気がふくむことのできる最大の量(g)
sat = {0: 4.8, 5: 6.8, 10: 9.4, 15: 12.8, 20: 17.3, 25: 23.1, 30: 30.4}
eq('理2-4 表の値', [float(v) for v in R2.SETS[3]['table']['rows'][1][1:]], [sat[t] for t in sorted(sat)])
kind = {'草の葉に水てきがつく': '結ろ', '洗たく物がかわく': '蒸発', 'ペットボトルの表面がぬれる': '結ろ', 'やかんの水がへる': '蒸発'}
same = [k for k, v in choices(q_text(R2, 4, 3)).items() if any(kind[p] == '結ろ' for p in kind if p in v)]
eq('理2-4(3) 同じしくみ', ans(R2, 4, 3), join(same))
eq('理2-4(5) 20℃の最大量', ans(R2, 4, 5), f'{num(sat[20])}g')
eq('理2-4(6) 水てきができ始める', ans(R2, 4, 6), f'{[t for t, v in sat.items() if v == 12.8][0]}℃')
assert 17.3 <= sat[30]
eq('理2-4(7) できる水てき', ans(R2, 4, 7), f'{num(17.3 - sat[10])}g')

# 5 水よう液：(名前, 性質, とけているもの, においの有無)
sol = {'塩酸': ('酸性', '気体', True), '水酸化ナトリウム水よう液': ('アルカリ性', '固体', False),
       '食塩水': ('中性', '固体', False), '炭酸水': ('酸性', '気体', False), 'アンモニア水': ('アルカリ性', '気体', True),
       '石灰水': ('アルカリ性', '固体', False), '砂糖水': ('中性', '固体', False)}
lead5 = choices(R2.SETS[4]['lead'])
assert set(lead5.values()) == set(sol), lead5
pick = lambda f: join(k for k, v in lead5.items() if f(sol[v]))
eq('理2-5(1) 酸性', ans(R2, 5, 1), pick(lambda p: p[0] == '酸性'))
eq('理2-5(2) アルカリ性', ans(R2, 5, 2), pick(lambda p: p[0] == 'アルカリ性'))
eq('理2-5(3) 中性', ans(R2, 5, 3), ['中性', pick(lambda p: p[0] == '中性')])
eq('理2-5(4) 何も残らない', ans(R2, 5, 4), pick(lambda p: p[1] == '気体'))
eq('理2-5(5) におい', ans(R2, 5, 5), pick(lambda p: p[2]))
eq('理2-5(6) 石灰水と気体', ans(R2, 5, 6), [[k for k, v in lead5.items() if v == '石灰水'][0], '二酸化炭素'])
al = {'塩酸', '水酸化ナトリウム水よう液'}          # アルミニウムがとける
eq('理2-5(7) アルミニウム', ans(R2, 5, 7), join(k for k, v in lead5.items() if v in al))

# 6 とけ方：水100gにとける最大の量(g)
salt, alum = {20: 35.8, 40: 36.3, 60: 37.1}, {20: 11.4, 40: 23.8, 60: 57.4}
rows6 = R2.SETS[5]['table']['rows']
eq('理2-6 表の値', [[float(v[:-1]) for v in rows6[i][1:]] for i in (1, 2)], [list(salt.values()), list(alum.values())])
eq('理2-6(1) 食塩水の重さ', ans(R2, 6, 1), f'{80 + 20}g')
eq('理2-6(2) こさ', ans(R2, 6, 2), f'{num(20 / (80 + 20) * 100)}%')
eq('理2-6(3) 40℃の水50g', ans(R2, 6, 3), f'{num(alum[40] * 50 / 100)}g')
assert 30 <= alum[60]
eq('理2-6(4) 出てくる量', ans(R2, 6, 4), f'{num(30 - alum[20])}g')
eq('理2-6(7) 冷やして取り出しやすい', ans(R2, 6, 7), 'ミョウバン' if alum[60] - alum[20] > salt[60] - salt[20] else '食塩')

# 7 てこ：左右の（重さ×位置）が等しいとつり合う
eq('理2-7(2) おもりの数', ans(R2, 7, 2), f'{30 * 4 // 6 // 10}個')
eq('理2-7(3) 右の重さ', ans(R2, 7, 3), f'{num(40 * 2 / 5)}g')
pos = (60 * 3 - 30 * 2) / 20
assert pos <= 6
eq('理2-7(4) 位置', ans(R2, 7, 4), f'{num(pos)}の位置')
eq('理2-7(5) 右の重さ', ans(R2, 7, 5), f'{num((20 * 6 + 40 * 1) / 4)}g')
middle = {'ピンセット': '力点', 'トング': '力点', 'くぎぬき': '支点', 'せんぬき': '作用点', '和ばさみ（糸切りばさみ）': '力点'}
eq('理2-7(7) ピンセットと同じ', ans(R2, 7, 7), join(k for k, v in choices(q_text(R2, 7, 7)).items() if middle[v] == middle['ピンセット']))

# 8 呼吸：吸う空気とはく息の割合(%)
inhale, exhale = {'ちっ素': 78, '酸素': 21, '二酸化炭素': .04}, {'ちっ素': 78, '酸素': 17, '二酸化炭素': 4}
eq('理2-8(3) ふえた気体', ans(R2, 8, 3), [g for g in inhale if exhale[g] > inhale[g]][0])
o2 = 500 * (inhale['酸素'] - exhale['酸素']) / 100
eq('理2-8(4) 1回の酸素', ans(R2, 8, 4), f'{num(o2)}mL')
eq('理2-8(5) 1分間の酸素', ans(R2, 8, 5), f'{num(o2 * 15)}mL')

# 9 気体：(ものを燃やす, 石灰水を白くにごらせる)
gas = {'酸素': (True, False), '二酸化炭素': (False, True), 'ちっ素': (False, False)}
rows9 = R2.SETS[8]['table']['rows']
seen = {lab: ('燃えた' in rows9[1][k], 'にごった' in rows9[2][k]) for k, lab in enumerate(rows9[0]) if lab}
eq('理2-9(1) 気体の名前', ans(R2, 9, 1), [[g for g, p in gas.items() if p == seen[lab]][0] for lab in 'ABC'])
make = {'酸素': ('二酸化マンガン', '過酸化水素水'), '二酸化炭素': ('石灰石', '塩酸')}
o9 = choices(q_text(R2, 9, 3))
eq('理2-9(3) 発生させるもの', ans(R2, 9, 3), [[k for k, v in o9.items() if all(m in v for m in make[g])][0] for g in ('酸素', '二酸化炭素')])
eq('理2-9(6) 酸素の量', ans(R2, 9, 6), f'{num(100 * inhale["酸素"] / 100)}L')
eq('理2-9(7) 何倍', ans(R2, 9, 7), f'{num(exhale["二酸化炭素"] / inhale["二酸化炭素"])}倍')

# 10 生き物の1年
season = {'サクラの花がさき': '春', 'たまごを産んで': '秋', 'ヘチマのつる': '夏', '葉はすべて落ち': '冬',
          'おたまじゃくし': '春', 'イチョウの葉が黄色': '秋', 'カブトムシの成虫': '夏', 'タンポポが': '冬'}
items10 = dict(R2.SETS[9]['items'])
by_season = {s: join(lab for lab, body in items10.items() if any(k in body and v == s for k, v in season.items()))
             for s in '春夏秋冬'}
eq('理2-10(1) 季節', ans(R2, 10, 1), [by_season[s] for s in '春夏秋冬'])
winter = {'オオカマキリ': 'たまご', 'アゲハ': 'さなぎ', 'ナナホシテントウ': '成虫', 'カブトムシ': '幼虫'}
o10 = {v: k for k, v in choices(q_text(R2, 10, 3)).items()}
eq('理2-10(3) 冬ごし', ans(R2, 10, 3), [o10[winter[n]] for n in R2.SETS[9]['qs'][2]['labels']])
pupa = {'モンシロチョウ': True, 'カブトムシ': True, 'トンボ': False, 'バッタ': False}
eq('理2-10(7) さなぎにならない', ans(R2, 10, 7), join(k for k, v in choices(q_text(R2, 10, 7)).items() if not pupa[v]))

# ---------------- 理科・大問3 ----------------
# 1 外来種・食物連鎖：在来種の表、「食べる→食べられる」の関係、数のふえ方
native = {'ニホンアマガエル', 'ニホンザリガニ'}
o31 = choices(q_text(R3, 1, 2))
eq('理3-1(2) 外来種', ans(R3, 1, 2), join(k for k, v in o31.items() if v not in native))
eats = {'ブルーギル': 'メダカ', 'メダカ': 'ミジンコ', 'ミジンコ': '植物プランクトン'}   # 食べるもの: 食べられるもの
chain = ['植物プランクトン']
while any(eats[k] == chain[-1] for k in eats):
    chain.append([k for k in eats if eats[k] == chain[-1]][0])
o33 = {v: k for k, v in choices(q_text(R3, 1, 3)).items()}
eq('理3-1(3) 食物連鎖の順', ans(R3, 1, 3), '→'.join(o33[n] for n in chain))
count = 10
for _ in range(4):
    count *= 2
eq('理3-1(6) 4年後の数', ans(R3, 1, 6), f'{count}ひき')
SDGS_GOALS, SDGS_YEAR = 17, 2030
eq('理3-1(8) SDGs', ans(R3, 1, 8), [f'{SDGS_GOALS}個', f'{SDGS_YEAR}年'])

# 2 水よう液：表の結果から、性質の組み合わせが一致する水よう液を探す
sol3 = {'塩酸': (True, False, False, True), 'アンモニア水': (False, True, False, True), '食塩水': (False, False, True, False),
        '炭酸水': (True, False, False, False), '石灰水': (False, True, True, False)}   # 酸性・アルカリ性・蒸発後に固体・におい
rows = R3.SETS[1]['table']['rows']
seen3 = {lab: ('赤色に変化' in rows[1][k], '青色に変化' in rows[2][k], '白い固体' in rows[3][k], 'つんと' in rows[4][k])
         for k, lab in enumerate(rows[0]) if lab}
name3 = {}
for lab, pr in seen3.items():
    hit = [n for n, v in sol3.items() if v == pr]
    assert len(hit) == 1, (lab, hit)
    name3[lab] = hit[0]
eq('理3-2(1) 水よう液', ans(R3, 2, 1), [name3[l] for l in 'ABCDE'])
eq('理3-2(2) BTBで黄色', ans(R3, 2, 2), join(l for l in 'ABCDE' if sol3[name3[l]][0]))
eq('理3-2(3) 気体がとけている', ans(R3, 2, 3), join(l for l in 'ABCDE' if not sol3[name3[l]][2]))
eq('理3-2(4) 石灰水に息', ans(R3, 2, 4), {'石灰水': '白くにごる'}[name3['E']])
eq('理3-2(5) 炭酸水のあわ', ans(R3, 2, 5), {'炭酸水': '二酸化炭素'}[name3['D']])
salt3 = 200 * 10 / 100
eq('理3-2(6) 食塩の重さ', ans(R3, 2, 6), f'{num(salt3)}g')
eq('理3-2(7) 加える水', ans(R3, 2, 7), f'{num(salt3 / 0.05 - 200)}g')

# 3 アサガオ：図の記号、さいた最短の暗さ、時刻
parts = {'ア': 'がく', 'イ': '花びら', 'ウ': 'おしべ', 'エ': 'めしべ', 'オ': '子房'}
eq('理3-3(1) 図の部分', ans(R3, 3, 1), [parts[k] for k in R3.SETS[2]['qs'][0]['labels']])
rows = R3.SETS[2]['table']['rows']
dark = min(int(h[:-2]) for h, f in zip(rows[0][1:], rows[1][1:]) if f == 'さいた')
assert all(f == 'さかない' for h, f in zip(rows[0][1:], rows[1][1:]) if int(h[:-2]) < dark)
eq('理3-3(4) さく最短の暗さ', ans(R3, 3, 4), f'{dark}時間')
eq('理3-3(5) ひらく時刻', ans(R3, 3, 5), f'午前{(19 + dark) % 24}時')
both = {'ヘチマ': False, 'アブラナ': True, 'カボチャ': False, 'ツツジ': True}
eq('理3-3(8) 両性花', ans(R3, 3, 8), join(k for k, v in choices(q_text(R3, 3, 8)).items() if both[v]))

# 4 空気
eq('理3-4(3) ちぢんだ体積', ans(R3, 4, 3), f'{100 - 60}mL')
squeeze = {'自転車のタイヤ': True, 'ねん土': False, 'バスケットボール': True, '食塩水': False}
eq('理3-4(5) おしちぢめる性質', ans(R3, 4, 5), join(k for k, v in choices(q_text(R3, 4, 5)).items() if squeeze[v]))
eq('理3-4(6) ピンポン玉', ans(R3, 4, 6), [k for k, v in choices(q_text(R3, 4, 6)).items() if '体積が大きくなった' in v][0])
eq('理3-4(7) 空気の重さ', ans(R3, 4, 7), f'{num(1.2 * 20)}g')
oil = {'油圧ショベル': True, '風船': False, 'ビーチボール': False}
eq('理3-4(8) 液体を利用', ans(R3, 4, 8), [k for k, v in choices(q_text(R3, 4, 8)).items() if oil[v]][0])

# 5 月：表の時刻、1日にずれる時間
rows = R3.SETS[4]['table']['rows']
moon = {r[0]: r[1:] for r in rows[1:]}              # 月の形: [月の出, 南中, 月の入り]
eq('理3-5(1) 満月の南中', ans(R3, 5, 1), moon['満月'][1])
o35 = choices(q_text(R3, 5, 2))
eq('理3-5(2) 午後6時に東', ans(R3, 5, 2), [k for k, v in o35.items() if moon[v][0] == '午後6時'][0])
eq('理3-5(3) 明け方に南', ans(R3, 5, 3), [m for m, t in moon.items() if t[1] == '午前6時'][0])
lit = {'上弦の月': '右側', '下弦の月': '左側'}      # 北半球で南の空に見るとき光っている側
eq('理3-5(4) 上弦の月', ans(R3, 5, 4), lit[[m for m, t in moon.items() if t[1] == '午後6時' and m in lit][0]])
eq('理3-5(6) 2回後の満月', ans(R3, 5, 6), f'{num(29.5 * 2)}日後')
mins = 18 * 60 + 50 * 3
eq('理3-5(7) 3日後の月の出', ans(R3, 5, 7), f'午後{mins // 60 - 12}時{mins % 60}分')
fact5 = {'地球のまわりを回っている': True, '自分で光を出している': False, '表面にクレーターがある': True, '海があり、水がたまっている': False}
eq('理3-5(9) 月の正しい説明', ans(R3, 5, 9), join(k for k, v in choices(q_text(R3, 5, 9)).items() if fact5[v]))

# 6 気温グラフ：図のデータ（build の args）から読む
pts = R3.SETS[5]['fig']['args']['pts']
tmax, tmin = max(v for t, v in pts), min(v for t, v in pts)
eq('理3-6(1) 最高気温と時刻', ans(R3, 6, 1), [f'{tmax}℃', f'{[t for t, v in pts if v == tmax][0]}時'])
eq('理3-6(2) 気温の差', ans(R3, 6, 2), f'{tmax - tmin}℃')
day_name = {35: '猛暑日', 30: '真夏日', 25: '夏日'}
eq('理3-6(3) 用語', ans(R3, 6, 3), [day_name[35], '熱帯夜'])
eq('理3-6(4) あてはまるか', ans(R3, 6, 4), ['あてはまる' if tmax >= 35 else 'あてはまらない', 'あてはまる' if tmin >= 25 else 'あてはまらない'])
eq('理3-6(5) 国内最高気温', ans(R3, 6, 5), '41.8℃')
eq('理3-6(6) アメダス', ans(R3, 6, 6), [k for k, v in choices(q_text(R3, 6, 6)).items() if '1300' in v][0])

# 7 動物：(何類, 体温が一定, 乳で育てる, 一生えらで呼吸, 子のころえら→おとなは肺, 陸上に卵を産む)
zoo = {'スズメ': ('鳥類', True, False, False, False, True), 'ウサギ': ('ほ乳類', True, True, False, False, False),
       'フナ': ('魚類', False, False, True, False, False), 'カメ': ('は虫類', False, False, False, False, True),
       'イモリ': ('両生類', False, False, False, True, False), 'クジラ': ('ほ乳類', True, True, False, False, False)}
letter = {v: k for k, v in choices(R3.SETS[6]['lead']).items()}
pick7 = lambda i: join(letter[n] for n, f in zoo.items() if f[i])
eq('理3-7(1) 体温一定', ans(R3, 7, 1), pick7(1))
eq('理3-7(2) 乳で育てる', ans(R3, 7, 2), pick7(2))
eq('理3-7(3) 一生えら', ans(R3, 7, 3), pick7(3))
eq('理3-7(4) えら→肺', ans(R3, 7, 4), pick7(4))
eq('理3-7(5) 陸上に卵', ans(R3, 7, 5), pick7(5))
klass = {'ペンギン': '鳥類', 'イルカ': 'ほ乳類', 'サンショウウオ': '両生類', 'ウミガメ': 'は虫類'}
eq('理3-7(6) 何類', ans(R3, 7, 6), [klass[n] for n in R3.SETS[6]['qs'][5]['labels']])
eq('理3-7(8) 大人になる割合', ans(R3, 7, 8), f'{num(10 / 10000 * 100)}%')

# 8 台風：風の向きの足し算、雲量、言い伝え
import math as _m
def wind(theta_deg, travel=(0, 1)):
    t = _m.radians(theta_deg)
    tx, ty = -_m.sin(t), _m.cos(t)                       # 反時計回りの向き
    return _m.hypot(tx + travel[0], ty + travel[1])
side = {'A': wind(0), 'B': wind(180)}                    # Aは進行方向の右（東）、Bは左（西）
eq('理3-8(4) 風が強い側', ans(R3, 8, 4), max(side, key=side.get))
eq('理3-8(5) 着くまでの時間', ans(R3, 8, 5), f'{600 // 30}時間後')
cloud = lambda n: '快晴' if n <= 1 else '晴れ' if n <= 8 else 'くもり'
eq('理3-8(7) 雲量9割以上', ans(R3, 8, 7), cloud(9))
eq('理3-8(1) 台風の発生', ans(R3, 8, 1), [k for k, v in choices(q_text(R3, 8, 1)).items() if v == '水温の高い海'][0])
omen = {'ツバメが低く飛ぶ': '悪化', '夕焼けがきれいに見える': '好転', '朝に虹が見える': '悪化', '月にぼんやりしたかさがかかる': '悪化'}
o38 = choices(q_text(R3, 8, 8))
eq('理3-8(8) 悪くなる前ぶれ', ans(R3, 8, 8)[1], join(k for k, v in o38.items() if omen[v] == '悪化'))

# 9 給食：食べる部分、食物連鎖
part = {'ジャガイモ': 'くき', 'ニンジン': '根'}
eq('理3-9(1) ジャガイモ', ans(R3, 9, 1), [k for k, v in choices(q_text(R3, 9, 1)).items() if v == part['ジャガイモ']][0])
eq('理3-9(2) ニンジン', ans(R3, 9, 2), part['ニンジン'])
eq('理3-9(7) デンプンの重さ', ans(R3, 9, 7), f'{num(80 * 0.75)}g')
food = ['イネ', 'バッタ', 'カエル', 'ヘビ']
i = food.index('バッタ')
eq('理3-9(8) バッタがふえると', ans(R3, 9, 8), [food[i - 1], food[i + 1]])

# 10 蒸散：A=くきだけ、B=表をふさぐ（裏＋くき）、C=裏をふさぐ（表＋くき）、D=ふさがない（表＋裏＋くき）
rows = R3.SETS[9]['table']['rows']
water = {t: float(v) for t, v in zip(rows[0][1:], rows[2][1:])}
stem, top10, bottom10 = water['A'], water['D'] - water['B'], water['D'] - water['C']
assert abs(stem + top10 + bottom10 - water['D']) < 1e-9          # 3つの部分の合計がDになる
eq('理3-10(4) 葉の裏', ans(R3, 10, 4), f'{bottom10:.1f}mL')
eq('理3-10(5) 葉の表', ans(R3, 10, 5), f'{top10:.1f}mL')
eq('理3-10(6) くき', ans(R3, 10, 6), f'{stem:.1f}mL')
eq('理3-10(7) 蒸散がさかんな面', ans(R3, 10, 7), '裏' if bottom10 > top10 else '表')

# ---------------- 理科・大問4 ----------------
# 1 発芽：表から、1つの条件だけがちがう組を探す
rows = R4.SETS[0]['table']['rows']
cols = rows[0][1:]
cond41 = {lab: {rows[r][0]: rows[r][k + 1] for r in range(1, 5)} for k, lab in enumerate(cols)}
germ = {lab: int(rows[5][k + 1][:-1]) for k, lab in enumerate(cols)}
only41 = lambda name: [f'{a}と{b}' for a, b in itertools.combinations(cols, 2)
                       if all((cond41[a][n] == cond41[b][n]) != (n == name) for n in cond41[a])]
for q, name in ((1, '水'), (2, '空気'), (3, '温度')):
    assert len(only41(name)) == 1
    eq(f'理4-1({q}) {name}を比べる組', ans(R4, 1, q), only41(name)[0])
assert only41('光') == ['AとE'] and germ['A'] == germ['E']
eq('理4-1(4) 光', ans(R4, 1, 4), '発芽に光は必要ない')
eq('理4-1(5) 発芽の割合', ans(R4, 1, 5), f'{germ["A"] * 100 // 10}%')

# 2 雲：西にあるものから東へ動く
bl = R4.SETS[1]['fig']['args']['blobs']
eq('理4-2(1) 時間の順', ans(R4, 2, 1), '→'.join('アイウエ'[i] for i in sorted(range(len(bl)), key=lambda i: bl[i][0])))
eq('理4-2(2) 雲の動く向き', ans(R4, 2, 2), [k for k, v in choices(q_text(R4, 2, 2)).items() if v == '西から東へ'][0])
eq('理4-2(6) 着くまでの時間', ans(R4, 2, 6), f'{600 // 50}時間後')

# 3 燃え方
o43 = choices(q_text(R4, 3, 1))
eq('理4-3(1) 火が消える理由', ans(R4, 3, 1), [k for k, v in o43.items() if v == '酸素が少なくなったから'][0])
steps = ['検知管の両はしを折る', '検知管をポンプにつなぎ', 'ハンドルを引いて', '色が変わった目盛りを読む']
o44 = choices(q_text(R4, 3, 4))
eq('理4-3(4) 検知管の順', ans(R4, 3, 4), '→'.join([k for k, v in o44.items() if st in v][0] for st in steps))
eq('理4-3(5) 使われた酸素', ans(R4, 3, 5), f'{num(1200 * (21 - 16) / 100)}mL')
eq('理4-3(6) スチールウール', ans(R4, 3, 6), [f'{num(6.5 - 5.0)}g', '酸素'])

# 4 種子のつくり
seed = {'ア': '種皮', 'イ': '子葉', 'ウ': 'はい'}
eq('理4-4(1) 図の名前', ans(R4, 4, 1), [seed[k] for k in 'アイウ'])
eq('理4-4(2) 根・くき・葉になる', ans(R4, 4, 2), [k for k, v in seed.items() if v == 'はい'][0])
eq('理4-4(3) 養分をたくわえる', ans(R4, 4, 3), [k for k, v in seed.items() if v == '子葉'][0])
need = {'日光': True, '水': True, '二酸化炭素': True, '酸素': False, '土': False}
eq('理4-4(8) 光合成に必要なもの', ans(R4, 4, 8), join(k for k, v in choices(q_text(R4, 4, 8)).items() if need[v]))

# 5 さおばかり：（重さ）×（支点からのきょり）が左右で等しい
fa = R4.SETS[4]['fig']['args']
plate, pos, wt = fa['plate'], fa['pos'], 60
eq('理4-5(1) さらの物', ans(R4, 5, 1), f'{num(wt * pos / plate)}g')
eq('理4-5(2) おもりの位置', ans(R4, 5, 2), f'{num(150 * plate / wt)}cm')
eq('理4-5(3) 最大の重さ', ans(R4, 5, 3), f'{num(wt * 50 / plate)}g')
maxw = lambda weight, d: weight * 50 / d
eq('理4-5(4) おもりを重く', ans(R4, 5, 4), '大きくなる' if maxw(100, plate) > maxw(wt, plate) else '小さくなる')
at = lambda w_: w_ * plate / wt
eq('理4-5(5) 物を重く', ans(R4, 5, 5), '遠くなる' if at(300) > at(150) else '近くなる')
eq('理4-5(6) 支点を近づける', ans(R4, 5, 6), '大きくなる' if wt * pos / (plate / 2) > wt * pos / plate else '小さくなる')
arm = {'ひじの関節': '支点', '筋肉がつく所': '力点', '物を持つ手': '作用点'}
eq('理4-5(7) うでのてこ', ans(R4, 5, 7), [arm[k] for k in R4.SETS[4]['qs'][6]['labels']])
mid5 = {'一輪車': '作用点', 'ピンセット': '力点', 'せんぬき': '作用点', 'ペンチ': '支点'}      # 3つの点の真ん中にあるもの
eq('理4-5(8) 作用点が真ん中', ans(R4, 5, 8), join(k for k, v in choices(q_text(R4, 5, 8)).items() if mid5[v] == '作用点'))

# 6 ふりこ：1往復の時間は、長さの平方根に比例する
rows = R4.SETS[5]['table']['rows']
Ls = [int(v) for v in rows[0][1:]]
T = {L: float(v) / 10 for L, v in zip(Ls, rows[1][1:])}                  # 1往復の時間
k6 = T[20] / math.sqrt(20)
for L in Ls:
    assert abs(T[L] - k6 * math.sqrt(L)) < .06, (L, T[L])               # 表が平方根の関係になっている
eq('理4-6(1) ふりこの長さ', ans(R4, 6, 1), f'{28 + 4 // 2}cm')
eq('理4-6(2) 20cmの1往復', ans(R4, 6, 2), f'{T[20]}秒')
eq('理4-6(3) 4倍の長さ', ans(R4, 6, 3), f'{round(T[80] / T[20])}倍')
eq('理4-6(4) 320cm', ans(R4, 6, 4), f'{num(T[20] * math.sqrt(320 / 20))}秒')
eq('理4-6(5) 180cm', ans(R4, 6, 5), f'{num(T[20] * math.sqrt(180 / 20))}秒')
eq('理4-6(6) 1分間の往復', ans(R4, 6, 6), f'{num(60 / 1.2)}往復')
eq('理4-6(7) 1.8秒の長さ', ans(R4, 6, 7), f'{[L for L in Ls if T[L] == 1.8][0]}cm')
o46 = choices(q_text(R4, 6, 8))
eq('理4-6(8) 時計のおくれ', ans(R4, 6, 8), [k for k, v in o46.items() if v == 'ふりこを短くする'][0])

# 7 茎：Aは管が輪のようにならぶ（ホウセンカなど）、Bは散らばる（トウモロコシなど）
kind7 = {'A': 'ring', 'B': 'scatter'}
plant7 = {'ホウセンカ': 'ring', 'トウモロコシ': 'scatter'}
eq('理4-7(2) ホウセンカの茎', ans(R4, 7, 2), [k for k, v in kind7.items() if v == plant7['ホウセンカ']][0])
eq('理4-7(6) 葉から出た水', ans(R4, 7, 6), f'{(50 - 38) - (50 - 46)}mL')

# 8 回路：電池の電圧=1×個数（直列）、豆電球の抵抗=1。明るさは、豆電球を流れる電流で決まる
specs = R4.SETS[7]['fig']['args']['specs']
def circuit(cell, bulb):
    V = 2 if cell == 'series' else 1
    R = {'one': 1, 'series': 2, 'parallel': .5, 'none': 0}[bulb]
    if R == 0:
        return None
    I = V / R
    i_bulb = I / 2 if bulb == 'parallel' else I
    i_cell = I / 2 if cell == 'parallel' else I
    return round(i_bulb, 6), round(i_cell, 6)
res8 = {lab: circuit(*sp) for lab, sp in zip('アイウエオカ', specs)}
base8 = res8['ア'][0]
eq('理4-8(1) ショート', ans(R4, 8, 1), join(k for k, v in res8.items() if v is None))
eq('理4-8(2) 明るい', ans(R4, 8, 2), join(k for k, v in res8.items() if v and v[0] > base8))
eq('理4-8(3) 同じ明るさ', ans(R4, 8, 3), join(k for k, v in res8.items() if v and k != 'ア' and v[0] == base8))
eq('理4-8(4) 暗い', ans(R4, 8, 4), join(k for k, v in res8.items() if v and v[0] < base8))
low8 = min(v[1] for v in res8.values() if v)
eq('理4-8(5) 長もち', ans(R4, 8, 5), join(k for k, v in res8.items() if v and v[1] == low8))
eq('理4-8(9) 電池のつなぎ方', ans(R4, 8, 9), [{'series': '直列つなぎ', 'parallel': '並列つなぎ'}[specs['アイウエオカ'.index(k)][0]] for k in 'イウ'])

# 9 気温：晴れは1日の変化が大きく、雨は小さい
ln = dict(R4.SETS[8]['fig']['args']['lines'])
span = {k: max(v for _, v in pts) - min(v for _, v in pts) for k, pts in ln.items()}
eq('理4-9(1) 晴れの日', ans(R4, 9, 1), max(span, key=span.get))
eq('理4-9(2) 雨の日', ans(R4, 9, 2), min(span, key=span.get))
eq('理4-9(3) 気温の差', ans(R4, 9, 3), f'{num(span["ア"])}℃')
at_ = lambda k, h: [v for t, v in ln[k] if t == h][0]
eq('理4-9(8) 平均', ans(R4, 9, 8), f'{(at_("ウ", 9) + at_("ウ", 12) + at_("ウ", 15)) / 3:.1f}℃')

# 10 アルミニウムと塩酸：とけた量に比例して水素が出る。塩酸50mLでとける量には上限がある
rows = R4.SETS[9]['table']['rows']
mass = [float(v) for v in rows[0][1:]]
gas10 = [float(v) for v in rows[1][1:]]
rate10 = gas10[0] / mass[0]
assert all(abs(g - rate10 * m) < 1e-6 for m, g, r in zip(mass, gas10, rows[2][1:]) if r == 'なし')
cap10 = max(g for g in gas10) / rate10                                    # 50mLの塩酸にとける最大のアルミニウム
eq('理4-10(3) 0.25g', ans(R4, 10, 3), f'{num(rate10 * 0.25)}mL')
assert 810 / rate10 <= cap10 * 2
eq('理4-10(4) 810mL', ans(R4, 10, 4), f'{num(810 / rate10)}g')
eq('理4-10(5) とけ残り', ans(R4, 10, 5), f'{num(0.5 - cap10)}g')
eq('理4-10(6) 最大', ans(R4, 10, 6), f'{num(cap10)}g')
dissolves = {'鉄': True, '銅': False, 'マグネシウム': True, '亜鉛': True}
eq('理4-10(8) 塩酸にとけない', ans(R4, 10, 8), [k for k, v in choices(q_text(R4, 10, 8)).items() if not dissolves[v]][0])

# ---------------- 理科・大問5 ----------------
# 1 ゴムの車：走る距離はのばした長さに比例する
rows = R5.SETS[0]['table']['rows']
ln51 = [float(v) for v in rows[0][1:]]
d1 = [float(v) for v in rows[1][1:]]
d2 = [float(v) for v in rows[2][1:]]
k1, k2 = d1[0] / ln51[0], d2[0] / ln51[0]
assert all(abs(d - k1 * l) < 1e-9 for d, l in zip(d1, ln51)) and all(abs(d - k2 * l) < 1e-9 for d, l in zip(d2, ln51))
eq('理5-1(1) 15cm', ans(R5, 1, 1), f'{num(d1[ln51.index(15)])}m')
eq('理5-1(2) 25cm', ans(R5, 1, 2), f'{k1 * 25:.1f}m')
eq('理5-1(3) ゴム2本', ans(R5, 1, 3), f'{k2 * 25:.1f}m')
eq('理5-1(4) 関係', ans(R5, 1, 4), '比例')
use51 = {'ヨット': '風', '模型飛行機': 'ゴム', 'こいのぼり': '風', 'おもちゃ': 'ゴム'}
lab51 = dict(zip('アイウエ', ['ヨット', '模型飛行機', 'こいのぼり', 'おもちゃ']))
eq('理5-1(5) 風とゴム', ans(R5, 1, 5), [join(k for k, v in lab51.items() if use51[v] == e) for e in ('風', 'ゴム')])
source = {'風力': '風', '水力': '流れ落ちる水', '火力': '石油や天然ガスを燃やした熱', '太陽光': '太陽の光'}
o51 = choices(q_text(R5, 1, 7))
eq('理5-1(7) 発電', ans(R5, 1, 7), [[k for k, v in o51.items() if v == source[n]][0] for n in R5.SETS[0]['qs'][6]['labels']])

# 2 電流計：5Aの端子の読みを、500mA（×100）、50mA（×10）に直す。クリップの数は電流に比例
fa2 = R5.SETS[1]['fig']['args']
eq('理5-2(1) 5A端子', ans(R5, 2, 1), f'{fa2["value"]}A')
eq('理5-2(2) 500mA端子', ans(R5, 2, 2), f'{num(fa2["value"] * 100)}mA')
eq('理5-2(3) 50mA端子', ans(R5, 2, 3), f'{num(fa2["value"] * 10)}mA')
rows = R5.SETS[1]['table']['rows']
amp = [float(v) for v in rows[0][1:]]
clip = [float(v) for v in rows[1][1:]]
kc = clip[0] / amp[0]
assert all(abs(cl - kc * a_) < 1e-9 for cl, a_ in zip(clip, amp))
eq('理5-2(5) 2.0A', ans(R5, 2, 5), f'{num(kc * 2.0)}個')
eq('理5-2(6) 6個', ans(R5, 2, 6), f'{6 / kc:g}A')
em = {'電磁石クレーン': True, '方位磁針': False, 'モーター': True, '豆電球': False, 'スピーカー': True}
eq('理5-2(8) 電磁石を利用', ans(R5, 2, 8), join(k for k, v in choices(q_text(R5, 2, 8)).items() if em[v]))

# 3 血液の循環：矢印の向きから血管の名前、酸素の多い血液を決める
edges = {'ア': ('心臓', '肺'), 'イ': ('肺', '心臓'), 'ウ': ('心臓', '全身'), 'エ': ('全身', '心臓')}
def vessel(src, dst):
    return ('肺' if '肺' in (src, dst) else '大') + ('動脈' if src == '心臓' else '静脈')
eq('理5-3(1) 血管の名前', ans(R5, 3, 1), [vessel(*edges[k]) for k in 'アイウエ'])
flow = {('肺', '心臓'): True, ('心臓', '全身'): True, ('全身', '心臓'): False, ('心臓', '肺'): False}   # 酸素が多いか
eq('理5-3(2) 酸素が多い', ans(R5, 3, 2), join(k for k in 'アイウエ' if flow[edges[k]]))
eq('理5-3(4) 1分間', ans(R5, 3, 4), f'{64 * 75 / 1000:.1f}L')
eq('理5-3(5) 1時間', ans(R5, 3, 5), f'{num(64 * 75 / 1000 * 60)}L')
eq('理5-3(6) 体重', ans(R5, 3, 6), f'{num(4.8 / 0.08)}kg')

# 4 かんの燃え方：空気の出入り（上にふた・底に穴）
cs = R5.SETS[3]['fig']['args']['specs']
score = {(False, True): 3, (False, False): 2, (True, True): 1, (True, False): 0}      # 新しい空気の入りやすさ
s54 = {k: score[sp] for k, sp in zip('アイウエ', cs)}
eq('理5-4(1) よく燃える・消える', ans(R5, 4, 1), [max(s54, key=s54.get), min(s54, key=s54.get)])
eq('理5-4(5) 使われた酸素', ans(R5, 4, 5), f'{25 * (21 - 16) / 100:.2f}L')
burn = {'ろうそく': True, '木': True, 'スチールウール': False, 'アルコール': True}          # 二酸化炭素が出るか
eq('理5-4(8) 二酸化炭素が出ない', ans(R5, 4, 8), [k for k, v in choices(q_text(R5, 4, 8)).items() if not burn[v]][0])

# 5 鏡：入射角＝反射角。鏡1枚ごとに同じだけ温度が上がる
eq('理5-5(2) 反射角', ans(R5, 5, 2), f'{R5.SETS[4]["fig"]["args"]["angle"]}度')
rows = R5.SETS[4]['table']['rows']
mir = [int(v) for v in rows[0][1:]]
tmp = [int(v) for v in rows[1][1:]]
step = (tmp[-1] - tmp[0]) // (mir[-1] - mir[0])
assert all(tmp[i] == tmp[0] + step * mir[i] for i in range(len(mir)))
eq('理5-5(3) 5枚', ans(R5, 5, 3), f'{tmp[0] + step * 5}℃')
eq('理5-5(4) 53℃', ans(R5, 5, 4), f'{(53 - tmp[0]) // step}枚')
eq('理5-5(5) 1枚あたり', ans(R5, 5, 5), f'{step}℃')

# 6 消化：図の記号と食べ物の通る順
org6 = {'ア': '口', 'イ': '肝臓', 'ウ': '食道', 'エ': '胃', 'オ': '小腸', 'カ': '大腸'}
eq('理5-6(1) 図の名前', ans(R5, 6, 1), [org6[k] for k in 'アイウエオカ'])
tube = ['口', '食道', '胃', '小腸', '大腸']
eq('理5-6(2) 通る順', ans(R5, 6, 2), '→'.join([k for k, v in org6.items() if v == n][0] for n in tube))
eq('理5-6(4) 養分を吸収', ans(R5, 6, 4), [k for k, v in org6.items() if v == '小腸'][0])
eq('理5-6(6) 水分を吸収', ans(R5, 6, 6), [k for k, v in org6.items() if v == '大腸'][0])
eq('理5-6(7) 肝臓', ans(R5, 6, 7), [k for k, v in org6.items() if v == '肝臓'][0])
eq('理5-6(8) 小腸の割合', ans(R5, 6, 8), f'約{round(6 / 9 * 100)}%')

# 7 水：地球の水、水質の指標生物、水の量
eq('理5-7(2) 海水の割合', ans(R5, 7, 2), [k for k, v in choices(q_text(R5, 7, 2)).items() if '97' in v][0])
clean = {'サワガニ': True, 'カワゲラ': True, 'サカマキガイ': False, 'ヒラタカゲロウ': True}
eq('理5-7(4) きれいな水の生物', ans(R5, 7, 4), join(k for k, v in choices(q_text(R5, 7, 4)).items() if clean[v]))
eq('理5-7(6) 1週間の水', ans(R5, 7, 6), f'{200 * 4 * 7}L')

# 8 滑車と輪じく：荷物を支えるひもの数だけ、力が小さくなり、引く長さが長くなる
hold = {'ア': 1, 'イ': 2, 'ウ': 2}
eq('理5-8(1) 定滑車', ans(R5, 8, 1), f'{60 // hold["ア"]}kg')
eq('理5-8(2) 動滑車', ans(R5, 8, 2), f'{60 // hold["イ"]}kg')
eq('理5-8(3) 引く長さ', ans(R5, 8, 3), f'{1 * hold["イ"]}m')
eq('理5-8(4) 組み合わせ', ans(R5, 8, 4), f'{60 // hold["ウ"]}kg')
eq('理5-8(6) 輪じく', ans(R5, 8, 6), f'{num(80 * 5 / 20)}g')
eq('理5-8(7) 輪じく', ans(R5, 8, 7), f'{num(30 * 20 / 5)}g')
wheel = {'ドアノブ': True, 'ピンセット': False, '水道のじゃ口のハンドル': True, 'はさみ': False}
eq('理5-8(8) 輪じくを利用', ans(R5, 8, 8), join(k for k, v in choices(q_text(R5, 8, 8)).items() if wheel[v]))

# 9 こん虫：あしが6本のものがこん虫
rows = R5.SETS[8]['table']['rows']
legs = {lab: int(v[:-1]) for lab, v in zip(rows[0][1:], rows[2][1:])}
name9 = dict(zip(rows[0][1:], rows[1][1:]))
eq('理5-9(1) こん虫', ans(R5, 9, 1), join(k for k, v in legs.items() if v == 6))
complete = {'モンシロチョウ': True, 'トンボ': False, 'バッタ': False}
eq('理5-9(3) さなぎ', ans(R5, 9, 3), join(k for k, v in name9.items() if complete.get(v)))
leg_of = {name9[k]: v for k, v in legs.items()}
eq('理5-9(4) あしの数', ans(R5, 9, 4), f'{2 * leg_of["モンシロチョウ"] + leg_of["クモ"] + 3 * leg_of["ダンゴムシ"]}本')

# 10 かげ：図の向き（北を90度として反時計回りに測る）
ang10 = {'ア': 150, 'イ': 90, 'ウ': 30}
eq('理5-10(1) 正午のかげ', ans(R5, 10, 1), [k for k, v in ang10.items() if v == 90][0])
eq('理5-10(2) 午前9時のかげ', ans(R5, 10, 2), [k for k, v in ang10.items() if v > 90][0])
seq = [ang10[k] for k in 'アイウ']                                             # 午前9時→正午→午後3時
eq('理5-10(3) かげの回る向き', ans(R5, 10, 3), '時計回り' if seq == sorted(seq, reverse=True) else '反時計回り')
eq('理5-10(5) 太陽の動き', ans(R5, 10, 5), f'{(14 - 10) * 15}度')
eq('理5-10(6) 星座の動き', ans(R5, 10, 6), f'{30 * 3}度')
west = (30 * 3)                                                                # 真南から西へ90度ずれた方角
eq('理5-10(7) 3か月後の方角', ans(R5, 10, 7), {0: '南の空', 90: '西の空'}[west])

# ---------------- 理科・大問6 ----------------
from fractions import Fraction

# 1 水溶液：表の観察から、5種類の水溶液を決める
props61 = {'塩酸': (True, False, False, '酸'), '重そう水': (False, False, True, 'アルカリ'), '食塩水': (False, False, True, '中'),
           '炭酸水': (False, True, False, '酸'), 'アンモニア水': (True, False, False, 'アルカリ')}      # におい・あわ・固体が残る・性質
tb61 = {r[0]: r[1:] for r in R6.SETS[0]['table']['rows'][1:]}
def obs61(k):
    blue, red = tb61['青リトマス紙'][k], tb61['赤リトマス紙'][k]
    return (tb61['におい'][k] != 'なし', tb61['あわ'][k] == 'あり', tb61['じょう発させる'][k] == '白い固体',
            '酸' if blue == '赤くなる' else 'アルカリ' if red == '青くなる' else '中')
name61 = []
for k in range(5):
    hit = [n for n, v in props61.items() if v == obs61(k)]
    assert len(hit) == 1, (k, hit)
    name61.append(hit[0])
eq('理6-1(3) 水溶液の名前', ans(R6, 1, 3), name61)
eq('理6-1(1) つんとする', ans(R6, 1, 1), join('ABCDE'[k] for k in range(5) if obs61(k)[0]))
eq('理6-1(2) 固体が残る', ans(R6, 1, 2), join('ABCDE'[k] for k in range(5) if obs61(k)[2]))
eq('理6-1(4) アルカリ性', ans(R6, 1, 4), join('ABCDE'[k] for k in range(5) if obs61(k)[3] == 'アルカリ'))
eq('理6-1(6) 食塩水の重さ', ans(R6, 1, 6), f'{150 + 15}g')
eq('理6-1(7) 10%の食塩水', ans(R6, 1, 7), [f'{200 * Fraction(10, 100):g}g', f'{200 - 200 * Fraction(10, 100):g}g'])
eq('理6-1(8) 20%の食塩水', ans(R6, 1, 8), f'{Fraction(20, 100) * 100 / (1 - Fraction(20, 100)):g}g')

# 2 てこ：棒の上の点の位置から、モーメントのつり合いを計算する
pos62 = dict(R6.SETS[1]['fig']['args']['pts'])
AB, BC = pos62['B'] - pos62['A'], pos62['C'] - pos62['B']
eq('理6-2(2) Cを押す力', ans(R6, 2, 2), f'{num(45 * AB / BC)}kg')
eq('理6-2(3) 荷物の重さ', ans(R6, 2, 3), f'{num(12 * BC / AB)}kg')
bc4 = int(re.search(r'BC間が(\d+)cm', q_text(R6, 2, 4)).group(1))
eq('理6-2(4) BCを近づける', ans(R6, 2, 4), f'{num(45 * AB / bc4)}kg')
ab5, bc5 = [int(x) for x in re.search(r'AB間を(\d+)cm、BC間を(\d+)cm', q_text(R6, 2, 5)).groups()]
assert ab5 + bc5 == AB + BC
eq('理6-2(5) 台を動かす', ans(R6, 2, 5), f'{num(45 * ab5 / bc5)}kg')
lever62 = {'くぎぬき': True, 'ペンチ': True, 'カッターナイフ': False, 'つめきり': True, 'スポイト': False}
eq('理6-2(7) てこを利用しない', ans(R6, 2, 7), join(k for k, v in choices(q_text(R6, 2, 7)).items() if not lever62[v]))
mid62 = {'くぎぬき': '支点', 'ピンセット': '力点', '手押し車': '作用点', 'せんぬき': '作用点'}                 # 3つの点の真ん中にあるもの
eq('理6-2(8) 力点が真ん中', ans(R6, 2, 8), [k for k, v in choices(q_text(R6, 2, 8)).items() if mid62[v] == '力点'][0])

# 3 メスシリンダー：図の液面の高さから読む
lv63 = R6.SETS[2]['fig']['args']['levels']
eq('理6-3(2) 石を入れる前', ans(R6, 3, 2), f'{lv63[0]:.1f}mL')
eq('理6-3(3) 石を入れたあと', ans(R6, 3, 3), f'{lv63[1]:.1f}mL')
vol63 = lv63[1] - lv63[0]
eq('理6-3(4) 石の体積', ans(R6, 3, 4), f'{vol63:.1f}cm³')
eq('理6-3(5) 1cm³の重さ', ans(R6, 3, 5), f'{27 / vol63:.1f}g')
rows = R6.SETS[2]['table']['rows']
w63 = [float(v) for v in rows[0][1:]]
s63 = [float(v) for v in rows[1][1:]]
k63 = s63[0] / w63[0]
assert all(abs(s - k63 * w) < 1e-9 for s, w in zip(s63, w63))
eq('理6-3(6) 水200mL', ans(R6, 3, 6), f'{num(k63 * 200)}g')
eq('理6-3(7) 食塩45g', ans(R6, 3, 7), f'{num(45 / k63)}mL')

# 4 上皿てんびん
eq('理6-4(1) かたむき', ans(R6, 4, 1), {'right': '右', 'left': '左'}[R6.SETS[3]['fig']['args']['tilt']])
w64 = [float(x) for x in re.findall(r'([\d.]+)g', q_text(R6, 4, 5).split('分銅')[0])]
eq('理6-4(5) 分銅の合計', ans(R6, 4, 5), f'{num(sum(w64))}g')
best = min((cmb for r in range(1, 5) for cmb in itertools.combinations([5, 2, 1, 0.5], r) if sum(cmb) == 8), key=len)
eq('理6-4(6) 8gの分銅', ans(R6, 4, 6), '・'.join(f'{num(v)}g' for v in best))
eq('理6-4(7) シーソー', ans(R6, 4, 7), f'{num(40 * 3 / 30)}m')

# 5 気温と地面の温度：グラフの2本の線から
lines65 = dict(R6.SETS[4]['fig']['args']['lines'])
rng65 = {k: max(v for _, v in pts) - min(v for _, v in pts) for k, pts in lines65.items()}
ground65 = max(rng65, key=rng65.get)                                    # 地面のほうが、1日の変化が大きい
air65 = [k for k in lines65 if k != ground65][0]
eq('理6-5(3) 地面の温度', ans(R6, 5, 3), ground65)
eq('理6-5(4) アの温度差', ans(R6, 5, 4), f'{rng65["ア"]}℃')
peak = lambda pts: max(pts, key=lambda p: p[1])[0]
eq('理6-5(5) 最高の時刻', ans(R6, 5, 5), [f'{peak(lines65[ground65])}時', f'{peak(lines65[air65])}時'])
assert peak(lines65[ground65]) < peak(lines65[air65])

# 6 回路：電圧・抵抗から、豆電球の明るさ（電流の2乗）と電池の持ちを計算する
def circuit(cell, bulb):
    V = 2 if cell == 'series' else 1
    R = {'one': Fraction(1), 'series': Fraction(2), 'parallel': Fraction(1, 2)}[bulb]
    I = Fraction(V) / R
    per_bulb = I / 2 if bulb == 'parallel' else I
    per_cell = I / 2 if cell == 'parallel' else I
    return per_bulb ** 2, per_cell                                    # 明るさ、電池1個が出す電流（小さいほど長持ち）
sp66 = dict(zip('アイウエオカ', R6.SETS[5]['fig']['args']['specs']))
b66 = {k: circuit(*v) for k, v in sp66.items()}
eq('理6-6(3) 最も明るい', ans(R6, 6, 3), max(b66, key=lambda k: b66[k][0]))
eq('理6-6(4) 最も暗い', ans(R6, 6, 4), min(b66, key=lambda k: b66[k][0]))
eq('理6-6(5) カと同じ明るさ', ans(R6, 6, 5), join(k for k in 'アイウエオ' if b66[k][0] == b66['カ'][0]))
eq('理6-6(6) 長持ち', ans(R6, 6, 6), min('カイエオ', key=lambda k: b66[k][1]))
eq('理6-6(7) 1つはずしても光る', ans(R6, 6, 7), join(k for k in 'アイウエオカ' if sp66[k][1] == 'parallel'))
cond66 = {'どう線': True, '10円玉': True, 'ガラスのコップ': False, '消しゴム': False, '鉄くぎ': True, 'わりばし': False}
eq('理6-6(1) 電気を通す', ans(R6, 6, 1), join(k for k, v in choices(q_text(R6, 6, 1)).items() if cond66[v]))

# 7 太陽・月・星
eq('理6-7(1) 光が届く時間', ans(R6, 7, 1), f'約{150000000 // 300000}秒（約{150000000 // 300000 // 60}分{150000000 // 300000 % 60}秒）')
temp7 = {'赤っぽい': 1, '黄色': 2, '白い': 3, '青白い': 4}
star7 = {r[0]: r[2] for r in R6.SETS[6]['table']['rows'][1:]}
eq('理6-7(6) 表面温度の高い順', ans(R6, 7, 6), '→'.join(sorted(['ベテルギウス', 'リゲル', 'ベガ'], key=lambda n: -temp7[star7[n]])))
tri7 = {'こと座': 'ベガ', 'わし座': 'アルタイル', 'はくちょう座': 'デネブ'}
eq('理6-7(5) 夏の大三角', ans(R6, 7, 5), [tri7[k] for k in R6.SETS[6]['qs'][4]['labels']])

# 8 水の状態変化：グラフの点から
pts68 = R6.SETS[7]['fig']['args']['pts']
eq('理6-8(2) ふっとう中の温度', ans(R6, 8, 2), f'{max(v for _, v in pts68)}℃')
def interp(pts, t):
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        if t1 <= t <= t2:
            return v1 + (v2 - v1) * (t - t1) / (t2 - t1)
eq('理6-8(3) 7分後', ans(R6, 8, 3), f'{num(interp(pts68, 7))}℃')
eq('理6-8(6) 水蒸気の体積', ans(R6, 8, 6), f'{10 * 1700 / 1000:g}L')
eq('理6-8(7) 氷の体積', ans(R6, 8, 7), f'{num(500 * 1.1)}cm³')

# 9 熱の伝わり方：表の距離と時間から
rows = R6.SETS[8]['table']['rows']
dist69 = [float(v) for v in rows[1][1:]]
time69 = [float(v) for v in rows[2][1:]]
sec_per_cm = time69[0] / dist69[0]
assert all(abs(t - sec_per_cm * d) < 1e-9 for t, d in zip(time69, dist69))
assert [d for _, d in R6.SETS[8]['fig']['args']['pts']] == dist69
eq('理6-9(1) 最初にとける', ans(R6, 9, 1), 'ABCDE'[dist69.index(min(dist69))])
eq('理6-9(2) 30cm', ans(R6, 9, 2), f'{num(sec_per_cm * 30)}秒')
eq('理6-9(3) 105秒', ans(R6, 9, 3), f'{num(105 / sec_per_cm)}cm')

# 10 食物連鎖：食べる・食べられるの関係から、並べる
eat10 = {'アオミドロ': None, 'ミジンコ': 'アオミドロ', 'メダカ': 'ミジンコ', 'ブラックバス': 'メダカ', 'サギ': 'ブラックバス'}
def depth10(n):
    return 0 if eat10[n] is None else 1 + depth10(eat10[n])
nm10 = {k: v.split('（')[0] for k, v in R6.SETS[9]['items']}
eq('理6-10(7) 食物連鎖', ans(R6, 10, 7), '→'.join(sorted(nm10, key=lambda k: depth10(nm10[k]))))
eq('理6-10(9) 数が最も少ない', ans(R6, 10, 9), max(nm10, key=lambda k: depth10(nm10[k])))
fossil10 = {'こはくの中の昆虫': True, '先月とれた貝がら': False, '石になった木の幹': True, '地層の中の恐竜の足あと': True}
eq('理6-10(4) 化石でない', ans(R6, 10, 4), [k for k, v in choices(q_text(R6, 10, 4)).items() if not fossil10[v]][0])

# ---------------- 理科・大問7 ----------------
compass = ['北', '北東', '東', '南東', '南', '南西', '西', '北西']
# 1 満月：かげは光の反対がわ。満月は真夜中に南中する。月齢から月の形を決める
dir71 = max((d for d in compass if d in q_text(R7, 1, 1)), key=len)
eq('理7-1(1) かげの方角', ans(R7, 1, 1), compass[(compass.index(dir71) + 4) % 8])
hour71 = 22
eq('理7-1(2) 満月の動き', ans(R7, 1, 2), [k for k, v in choices(q_text(R7, 1, 2)).items() if v.startswith('南の空へ') and hour71 < 24][0])
eq('理7-1(3) 満月の並び', ans(R7, 1, 3), [k for k, v in choices(q_text(R7, 1, 3)).items() if v == '太陽・地球・月'][0])
age71 = 29.5 / 2 + 7                                             # 満月の約7日後の月齢
phase71 = {0: '新月', 7.4: '上弦の月', 14.8: '満月', 22.1: '下弦の月'}
eq('理7-1(5) 満月の7日後', ans(R7, 1, 5), phase71[min(phase71, key=lambda a: abs(a - age71))])
mag71 = {'ベガ': 0.03, 'アルタイル': 0.77, 'デネブ': 1.25}                 # 明るさ（小さいほど明るい）
eq('理7-1(6) いちばん明るい', ans(R7, 1, 6), min(mag71, key=mag71.get))
eq('理7-1(7) 星の動き', ans(R7, 1, 7), [f'{360 // 24 * h}度' for h in (1, 4)])
eq('理7-1(8) デネブ', ans(R7, 1, 8), {'ベガ': 'こと座', 'アルタイル': 'わし座', 'デネブ': 'はくちょう座'}['デネブ'])

# 2 ふ入りの葉：緑色で日光が当たった部分にだけ、でんぷんができる
reg72 = {'A': (True, True), 'B': (False, True), 'C': (True, False)}       # (緑色か, 日光が当たったか)
eq('理7-2(2) 青むらさき色', ans(R7, 2, 2), join(k for k, (g_, l_) in reg72.items() if g_ and l_))
diff72 = lambda a_, b_: ['緑色の部分' if reg72[a_][0] != reg72[b_][0] else '', '日光' if reg72[a_][1] != reg72[b_][1] else '']
eq('理7-2(4) AとC', ans(R7, 2, 4), [x for x in diff72('A', 'C') if x][0])
eq('理7-2(5) AとB', ans(R7, 2, 5), [x for x in diff72('A', 'B') if x][0])

# 3 ボーリング：標高−深さ。3点から傾きを求める
rows = R7.SETS[2]['table']['rows']
sf73 = {r[0]: int(r[1]) for r in zip(rows[0][1:], rows[1][1:], rows[2][1:])}
dp73 = {r[0]: int(r[2]) for r in zip(rows[0][1:], rows[1][1:], rows[2][1:])}
z73 = {k: sf73[k] - dp73[k] for k in 'ABC'}
eq('理7-3(2) 標高', ans(R7, 3, 2), [f'{z73[k]}m' for k in 'ABC'])
dx73, dy73 = -(z73['B'] - z73['A']), -(z73['C'] - z73['A'])                 # 低くなる向き（東・北）
low73 = ('東' if dx73 > 0 else '西') if dy73 == 0 else ('北' if dy73 > 0 else '南') + ('' if dx73 == 0 else '東' if dx73 > 0 else '西')
eq('理7-3(3) 低くなる方角', ans(R7, 3, 3), low73)
cover73 = lambda n: '快晴' if n <= 1 else '晴れ' if n <= 8 else 'くもり'
eq('理7-3(6) 雲量6', ans(R7, 3, 6), [k for k, v in choices(q_text(R7, 3, 6)).items() if v == cover73(6)][0])
eq('理7-3(8) 上弦の月', ans(R7, 3, 8), f'約{round(7.4)}日後')

# 4 ふりこ：条件を1つだけ変えて比べる。周期＝10往復の時間÷10
rows = R7.SETS[3]['table']['rows']
cond74 = {r[0]: [int(v) for v in r[1:]] for r in rows[1:4]}
t74 = [float(v) for v in rows[4][1:]]
names74 = rows[0][1:]
fac = {'おもりの重さ': 'おもりの重さ(g)', 'ふれはば': 'ふれはば(度)', '糸の長さ': '糸の長さ(cm)'}
def only_diff(f):
    hits = [names74[j] for j in range(1, 4) if all((cond74[g_][j] != cond74[g_][0]) == (g_ == f) for g_ in cond74)]
    assert len(hits) == 1, (f, hits)
    return hits[0]
eq('理7-4(1) 条件を比べる', ans(R7, 4, 1), [only_diff(f) for f in fac.values()])
period = [t / 10 for t in t74]
eq('理7-4(3) 1往復', ans(R7, 4, 3), [f'{period[0]:.1f}秒', f'{period[3]:.1f}秒'])
assert abs(period[0] - period[3] * math.sqrt(cond74['糸の長さ(cm)'][0] / cond74['糸の長さ(cm)'][3])) < 1e-9
eq('理7-4(4) 225cm', ans(R7, 4, 4), f'{10 * t74[3] / 10 * math.sqrt(225 / cond74["糸の長さ(cm)"][3]):.1f}秒')
eq('理7-4(5) アの往復数', ans(R7, 4, 5), f'{num(12 / period[0])}往復')
meet74 = sum(1 for k in range(1, 13) if (Fraction(k) % Fraction(str(period[0])) == 0) and (Fraction(k) % Fraction(str(period[3])) == 0))
eq('理7-4(6) いっしょにもどる', ans(R7, 4, 6), f'{meet74}回')

# 5 ヒトのたんじょう
eq('理7-5(6) 38週', ans(R7, 5, 6), f'約{38 * 7}日')

# 6 こん虫
meta76 = {'カマキリ': '不完全', 'モンシロチョウ': '完全', 'セミ': '不完全', 'カブトムシ': '完全', 'トンボ': '不完全'}
eq('理7-6(8) 完全変態', ans(R7, 6, 8), join(k for k, v in choices(q_text(R7, 6, 8)).items() if meta76[v] == '完全'))
song76 = {'カナカナ': 'ヒグラシ', 'ミーンミーン': 'ミンミンゼミ', 'ジリジリ': 'アブラゼミ'}
eq('理7-6(4) セミの鳴き声', ans(R7, 6, 4), [song76[k.replace('と鳴く', '')] for k in R7.SETS[5]['qs'][3]['labels']])

# 7 燃える条件と気体：表の割合から
rows = R7.SETS[6]['table']['rows']
tb77 = {r[0]: {g_: float(v.rstrip('%')) for g_, v in zip(rows[0][1:], r[1:])} for r in rows[1:]}
eq('理7-7(3) 二酸化炭素', ans(R7, 7, 3), f'{num(tb77["はいた息"]["二酸化炭素"] / tb77["空気"]["二酸化炭素"])}倍')
eq('理7-7(4) 酸素の量', ans(R7, 7, 4), f'{50 * tb77["空気"]["酸素"] / 100:g}L')
eq('理7-7(5) 変わらない気体', ans(R7, 7, 5), [g_ for g_ in tb77['空気'] if tb77['空気'][g_] == tb77['はいた息'][g_]][0])
lack77 = {'びんをかぶせた': '②', '水をかけた': '③', 'ガスを止めた': '①', 'ふたをした': '②'}
eq('理7-7(2) 消えた理由', ans(R7, 7, 2), [[v for k, v in lack77.items() if k in lab][0] for lab in R7.SETS[6]['qs'][1]['labels']])

# 8 ヘチマ：実ができるのは、めばなに花粉がついたとき
rows = R7.SETS[7]['table']['rows'][1:]
for r in rows:
    pollen = '花粉をつけた' in r[2] or 'かけなかった' in r[2]
    assert (r[1] == 'めばな' and pollen) == (r[3] == 'できた'), r

# 9 川：図の上から下へ、上流・中流・下流。曲がりの外側がけずられる
v_mark = {'ア': 0.90, 'イ': 0.45, 'ウ': 0.28}
order9 = {k: ['上流', '中流', '下流'][i] for i, k in enumerate(sorted(v_mark, key=lambda k: -v_mark[k]))}
eq('理7-9(1) 上流・中流・下流', ans(R7, 9, 1), [order9[k] for k in 'アイウ'])
eq('理7-9(2) 川はばが広い', ans(R7, 9, 2), [k for k, v in order9.items() if v == '下流'][0])
curv = lambda u: 0.13 * math.sin(2 * math.pi * (u - 0.30) / 0.42)
uc9 = 0.30 + 0.42 / 4
d2 = curv(uc9 + 1e-3) + curv(uc9 - 1e-3) - 2 * curv(uc9)                      # 山（上に出っぱる）なら負
side9 = {'A': 1, 'B': -1}                                                  # 川の線の上がわ・下がわ
eq('理7-9(5) 外側（けずられる）', ans(R7, 9, 5), [k for k, s in side9.items() if s * d2 < 0][0])
eq('理7-9(6) 内側（たい積）', ans(R7, 9, 6), [k for k, s in side9.items() if s * d2 > 0][0])

# 10 顕微鏡：図の高さの順で、部分の名前を決める
h10 = {'ア': 122, 'イ': 54, 'ウ': 36, 'エ': 18, 'オ': 70, 'カ': 41}
part10 = {122: '接眼レンズ', 70: '調節ねじ', 54: '対物レンズ', 41: 'クリップ', 36: 'ステージ', 18: '反射鏡'}
eq('理7-10(1) 顕微鏡の部分', ans(R7, 10, 1), [part10[h10[k]] for k in 'アイウエオカ'])
eq('理7-10(2) 倍率', ans(R7, 10, 2), f'{10 * 40}倍')

# ---------------- 理科・大問8 ----------------
# 1 地震の波：到達時刻の差から速さを求める
rows = R8.SETS[0]['table']['rows'][1:]
sec = lambda t: int(re.search(r'(\d+)分(\d+)秒', t).group(1)) * 60 + int(re.search(r'(\d+)分(\d+)秒', t).group(2))
dist81 = {r[0]: int(r[1]) for r in rows}
tp81 = {r[0]: sec(r[2]) for r in rows}
ts81 = {r[0]: sec(r[3]) for r in rows}
vp81 = (dist81['B'] - dist81['A']) / (tp81['B'] - tp81['A'])
vs81 = (dist81['B'] - dist81['A']) / (ts81['B'] - ts81['A'])
assert all(abs(dist81[k] / vp81 - (tp81[k] - tp81['A'] + dist81['A'] / vp81)) < 1e-9 for k in 'ABC')
eq('理8-1(2) P波の速さ', ans(R8, 1, 2), f'{num(vp81)}km/s')
eq('理8-1(3) S波の速さ', ans(R8, 1, 3), f'{num(vs81)}km/s')
t0 = tp81['A'] - dist81['A'] / vp81
eq('理8-1(4) 発生時刻', ans(R8, 1, 4), f'{int(t0) // 3600 + 8:d}時{int(t0) % 3600 // 60:02d}分{int(t0) % 60:02d}秒')
eq('理8-1(5) Cの初期微動継続時間', ans(R8, 1, 5), f'{ts81["C"] - tp81["C"]}秒')
eq('理8-1(6) 15秒', ans(R8, 1, 6), f'{round(15 / (1 / vs81 - 1 / vp81))}km')

# 2 蒸散：試験管の水の減った量から
rows = R8.SETS[1]['table']['rows']
v82 = dict(zip(rows[0][1:], [float(x) for x in rows[2][1:]]))
eq('理8-2(3) 葉つきの枝', ans(R8, 2, 3), f'{v82["C"] - v82["A"]:.1f}mL')
eq('理8-2(4) くき', ans(R8, 2, 4), f'{v82["B"] - v82["A"]:.1f}mL')
front, back = v82['C'] - v82['D'], v82['C'] - v82['E']
eq('理8-2(5) 葉の表', ans(R8, 2, 5), f'{front:.1f}mL')
eq('理8-2(6) 葉の裏', ans(R8, 2, 6), f'{back:.1f}mL')
assert abs(front + back + (v82['B'] - v82['A']) - (v82['C'] - v82['A'])) < 1e-9

# 3 浮き沈み：1cm³あたりの重さが、水（1g）より軽いか重いか
rows = R8.SETS[2]['table']['rows']
vol83 = dict(zip(rows[0][1:], [int(x) for x in rows[1][1:]]))
wt83 = dict(zip(rows[0][1:], [int(x) for x in rows[2][1:]]))
den83 = {k: wt83[k] / vol83[k] for k in vol83}
eq('理8-3(1) 1cm³あたりの重さ', ans(R8, 3, 1), [f'{den83[k]:g}g' if den83[k] != 1 else '1.0g' for k in 'アイウエ'] if False else
   [{0.8: '0.8g', 3.0: '3.0g', 0.92: '0.92g', 1.0: '1.0g'}[round(den83[k], 2)] for k in 'アイウエ'])
eq('理8-3(2) しずむ', ans(R8, 3, 2), join(k for k in 'アイウエ' if den83[k] > 1))
eq('理8-3(3) うく', ans(R8, 3, 3), join(k for k in 'アイウエ' if den83[k] < 1))
eq('理8-3(4) アの水中の体積', ans(R8, 3, 4), f'{wt83["ア"]}cm³')
eq('理8-3(5) ウの水面上の体積', ans(R8, 3, 5), f'{vol83["ウ"] - wt83["ウ"]}cm³')
eq('理8-3(6) 水中のばねばかり', ans(R8, 3, 6), f'{wt83["イ"] - vol83["イ"]}g')

# 4 凸レンズ：1/f＝1/a＋1/b
rows = R8.SETS[3]['table']['rows']
a84 = [int(x) for x in rows[0][1:]]
b84 = [int(x) for x in rows[1][1:]]
fl84 = {Fraction(1, 1) / (Fraction(1, a_) + Fraction(1, b_)) for a_, b_ in zip(a84, b84)}
assert len(fl84) == 1
f84 = float(fl84.pop())
eq('理8-4(1) 焦点距離', ans(R8, 4, 1), f'{num(f84)}cm')
eq('理8-4(3) 30cmのとき', ans(R8, 4, 3), f'{num(b84[a84.index(30)] / 30)}倍')
eq('理8-4(4) 15cmのとき', ans(R8, 4, 4), f'{num(b84[a84.index(15)] / 15)}倍')
assert b84 == sorted(b84, reverse=True) and a84 == sorted(a84)
eq('理8-4(8) 焦点の位置', ans(R8, 4, 8), f'{num(f84)}cm')

# 5 太陽の南中高度
lat85 = int(re.search(r'北緯(\d+)度', R8.SETS[4]['lead']).group(1))
tilt85 = float(re.search(r'約([\d.]+)度', R8.SETS[4]['lead']).group(1))
eq('理8-5(1) 夏至', ans(R8, 5, 1), f'{num(90 - lat85 + tilt85)}度')
eq('理8-5(2) 冬至', ans(R8, 5, 2), f'{num(90 - lat85 - tilt85)}度')
eq('理8-5(3) 春分', ans(R8, 5, 3), f'{num(90 - lat85)}度')

# 6 月の形：図の並びと、月齢
ph86 = dict(zip('アイウエオカキク', R8.SETS[5]['fig']['args']['phases']))
name86 = {0: '新月', 1: '三日月', 2: '上弦の月', 4: '満月', 6: '下弦の月'}
lab86 = {v: k for k, v in ph86.items()}
eq('理8-6(2) 月の名前', ans(R8, 6, 2), [lab86[[p for p, n in name86.items() if n == nm][0]] for nm in R8.SETS[5]['qs'][1]['labels']])
eq('理8-6(3) 満月', ans(R8, 6, 3), lab86[4])
eq('理8-6(4) 新月から', ans(R8, 6, 4), '→'.join(lab86[p] for p in range(8)))
eq('理8-6(5) 夕方の西空', ans(R8, 6, 5), lab86[1])
eq('理8-6(6) 明け方の東空', ans(R8, 6, 6), lab86[7])
age86 = 7.4
transit86 = (12 + 24 * age86 / 29.5) % 24
eq('理8-6(7) 上弦の月の南中', ans(R8, 6, 7), [k for k, v in choices(q_text(R8, 6, 7)).items() if v == ('夕方' if 15 <= transit86 <= 21 else '')][0])
eq('理8-6(8) 満月', ans(R8, 6, 8), f'約{round(29.5 / 2)}日後')

# 7 水溶液：BTB液・残るもの・二酸化炭素・アルミニウムから決める
props87 = {'塩酸': ('黄色', '何も残らない', '変化なし', 'あわが出てとける'), '水酸化ナトリウム水溶液': ('青色', '白い固体', '変化なし', 'あわが出てとける'),
           '石灰水': ('青色', '白い固体', '白くにごる', '変化なし'), '食塩水': ('緑色', '白い固体', '変化なし', '変化なし'),
           '炭酸水': ('黄色', '何も残らない', '変化なし', '変化なし')}
rows = R8.SETS[6]['table']['rows']
col87 = [tuple(rows[r][c] for r in range(1, 5)) for c in range(1, 6)]
name87 = []
for ob in col87:
    hit = [n for n, v in props87.items() if v == ob]
    assert len(hit) == 1, (ob, hit)
    name87.append(hit[0])
eq('理8-7(1) 水溶液の名前', ans(R8, 7, 1), name87)
eq('理8-7(2) アルカリ性', ans(R8, 7, 2), join('ABCDE'[k] for k in range(5) if col87[k][0] == '青色'))
eq('理8-7(3) 酸性', ans(R8, 7, 3), join('ABCDE'[k] for k in range(5) if col87[k][0] == '黄色'))

# 8 栄養：表の値とエネルギー（炭水化物・たんぱく質4kcal、脂質9kcal）
rows = R8.SETS[7]['table']['rows']
nut88 = {r[0]: [int(x) for x in r[1:]] for r in rows[1:]}
kcal88 = [4, 4, 9]
eq('理8-8(3) 炭水化物が最も多い', ans(R8, 8, 3), max(nut88, key=lambda k: nut88[k][0]))
eq('理8-8(4) ごはん200g', ans(R8, 8, 4), f'{nut88["ごはん"][0] * 2}g')
eq('理8-8(5) 牛乳のエネルギー', ans(R8, 8, 5), f'{sum(a_ * b_ for a_, b_ in zip(nut88["牛乳"], kcal88))}kcal')
eq('理8-8(6) 卵のエネルギー', ans(R8, 8, 6), f'{sum(a_ * b_ for a_, b_ in zip(nut88["卵"], kcal88))}kcal')

# 9 てこ：穴の記号（左から）→ 支点からの距離と向き。つり合い＝距離×重さの和が左右で等しい
nm89 = 'アイウエオカキクケコサシ'
dist89 = {ch: abs(6 - i) if i < 6 else i - 5 for i, ch in enumerate(nm89)}
side89 = {ch: ('左' if i < 6 else '右') for i, ch in enumerate(nm89)}
assert R8.SETS[8]['fig']['args']['names'] == nm89
def solve89(i):
    q = q_text(R8, 9, i)
    known = [(h_, int(w_)) for h_, w_ in re.findall(r'([ア-シ])に(\d+)g', q)]
    tgt = re.search(r'([ア-シ])に何g', q).group(1)
    assert all(side89[h_] != side89[tgt] for h_, _ in known)
    return sum(dist89[h_] * w_ for h_, w_ in known) / dist89[tgt]
for qi, label in [(1, 'ウ30gでケ'), (2, 'エ・オでサ'), (3, 'クでア'), (6, 'ケ・サでオ')]:
    eq(f'理8-9({qi}) {label}', ans(R8, 9, qi), f'{num(solve89(qi))}g')
q95 = q_text(R8, 9, 5)                                                   # 「コとシに、10gずつ」：2つの穴に同じ重さ
w95 = int(re.search(r'(\d+)gずつ', q95).group(1))
tgt95 = re.search(r'([ア-シ])に何g', q95).group(1)
eq('理8-9(5) コ・シでウ', ans(R8, 9, 5), f'{num((dist89["コ"] * w95 + dist89["シ"] * w95) / dist89[tgt95])}g')
q97 = q_text(R8, 9, 7)
h97, w97 = re.search(r'([ア-シ])に(\d+)gのおもりをつるしました。左に(\d+)g', q97).group(1), int(re.search(r'(\d+)gのおもりをつるしました。左', q97).group(1))
w97b = int(re.search(r'左に(\d+)g', q97).group(1))
need97 = dist89[h97] * w97 / w97b
eq('理8-9(7) 左の穴', ans(R8, 9, 7), [ch for ch in nm89 if side89[ch] == '左' and dist89[ch] == need97][0])
lever89 = {'ピンセット': '力点', '手押し車': '作用点', 'くぎぬき': '支点', '和ばさみ': '力点'}
eq('理8-9(8) 作用点が真ん中', ans(R8, 9, 8), [k for k, v in choices(q_text(R8, 9, 8)).items() if lever89[v] == '作用点'][0])

# 10 種子・根・葉
move810 = {'タンポポ': '風', 'オナモミ': '動物', 'ヤシ': '水', 'ホウセンカ': '自分ではじける'}
eq('理8-10(1) 種子の運ばれ方', ans(R8, 10, 1), [move810[k] for k in R8.SETS[9]['qs'][0]['labels']])
root810 = {'アサガオ': '主根と側根', 'ススキ': 'ひげ根'}
eq('理8-10(4) 根のつくり', ans(R8, 10, 4), [root810[k] for k in R8.SETS[9]['qs'][3]['labels']])

# ---------------- 理科・大問9 ----------------
# 1 電熱線：発熱 ∝ 電圧²÷抵抗（抵抗 ∝ 長さ÷太さ²）×時間
rows = R9.SETS[0]['table']['rows']
nm91 = rows[0][1:]
dia91 = [float(x) for x in rows[1][1:]]
len91 = [float(x) for x in rows[2][1:]]
volt91 = [2 if '直列' in x else 1 for x in rows[3][1:]]
rise91 = [float(x) for x in rows[4][1:]]
heat91 = [v ** 2 / (l_ / d ** 2) for v, l_, d in zip(volt91, len91, dia91)]
assert all(abs(rise91[k] - rise91[0] * heat91[k] / heat91[0]) < 1e-9 for k in range(5))
def only91(f):
    base = (dia91[0], len91[0], volt91[0])
    idx = {'太さ': 0, '長さ': 1, '電池': 2}[f]
    hit = [nm91[k] for k in range(1, 5) if all(((dia91[k], len91[k], volt91[k])[j] != base[j]) == (j == idx) for j in range(3))]
    assert len(hit) == 1, (f, hit)
    return hit[0]
eq('理9-1(1) 条件を比べる', ans(R9, 1, 1), [only91(f) for f in ('太さ', '長さ', '電池')])
eq('理9-1(3) 長さ2倍', ans(R9, 1, 3), f'{num(rise91[2] / rise91[0])}倍')
eq('理9-1(4) 電池2個直列', ans(R9, 1, 4), f'{num(rise91[3] / rise91[0])}倍')
eq('理9-1(5) 長さ5cm', ans(R9, 1, 5), f'{rise91[0] * len91[0] / 5:.1f}℃')
eq('理9-1(6) 10分間', ans(R9, 1, 6), f'{rise91[0] * 10 / 5:.1f}℃')

# 2 だ液：ヨウ素液の色が変わらない＝でんぷんがなくなった
rows = R9.SETS[1]['table']['rows']
tube92 = {r_: (rows[1][i], int(rows[2][i]), rows[3][i]) for i, r_ in enumerate(rows[0]) if i > 0}
eq('理9-2(4) でんぷんが分解された', ans(R9, 2, 4), [k for k, v in tube92.items() if v[2] == '変化なし'][0])
best92 = [v[1] for k, v in tube92.items() if v[0] == 'だ液' and v[2] == '変化なし'][0]
assert best92 == 37 and '37' in ans(R9, 2, 6)
organ92 = {'最初に消化が始まる': '口', 'たんじゅうをつくる': '肝臓', '養分を吸収する': '小腸', '水分を吸収する': '大腸', '胃液を出す': '胃'}
fig92 = {'ア': '口', 'イ': '肝臓', 'ウ': '食道', 'エ': '胃', 'オ': '小腸', 'カ': '大腸'}                 # 図の説明文のとおり
eq('理9-2(1) 消化器官', ans(R9, 2, 1), [[k for k, v in fig92.items() if v == organ92[lab]][0] for lab in R9.SETS[1]['qs'][0]['labels']])

# 3 ばね：のびは重さに比例
rows = R9.SETS[2]['table']['rows']
w93 = [float(x) for x in rows[0][1:]]
l93 = [float(x) for x in rows[1][1:]]
k93 = (l93[1] - l93[0]) / (w93[1] - w93[0])
assert all(abs(l_ - (l93[0] + k93 * w_)) < 1e-9 for l_, w_ in zip(l93, w93))
eq('理9-3(3) 50g', ans(R9, 3, 3), f'{num(l93[0] + k93 * 50)}cm')
eq('理9-3(4) 21cm', ans(R9, 3, 4), f'{num((21 - l93[0]) / k93)}g')
eq('理9-3(5) 縦につなぐ', ans(R9, 3, 5), f'{num(2 * (l93[0] + k93 * 60))}cm')
eq('理9-3(6) 横にならべる', ans(R9, 3, 6), f'{num(l93[0] + k93 * 60 / 2)}cm')
eq('理9-3(7) 月面', ans(R9, 3, 7), f'{6}分の1')

# 4 気体：性質から名前を決める
prop94 = {'ものが燃えるのを助ける': '酸素', '石灰水を白くにごらせる': '二酸化炭素', '火を近づけると、音を立てて燃える': '水素'}
rows = R9.SETS[3]['table']['rows'][1:]
name94 = {r[0]: prop94[r[2]] for r in rows}
eq('理9-4(1) 気体の名前', ans(R9, 4, 1), [name94[k] for k in 'ABC'])
dens94 = {'酸素': 1.43, '二酸化炭素': 1.98, '水素': 0.09}                  # 0℃・1気圧のg/L。空気は1.29
eq('理9-4(4) 空気より軽い', ans(R9, 4, 4), [k for k, n in name94.items() if dens94[n] < 1.29][0])

# 5 目：光が通る順に、図の場所を前から後ろへ並べる
tx95 = {'ア': -43, 'イ': -36, 'ウ': -22, 'エ': 32, 'オ': 52}                  # 図で、引き出し線がさす場所の横の位置
order95 = ['角膜', '虹彩', '水晶体', '網膜', '視神経']
eq('理9-5(1) 目の部分', ans(R9, 5, 1), [order95[sorted(tx95, key=tx95.get).index(k)] for k in 'アイウエオ'])

# 6 光電池とコンデンサー：回した回数に比例して、光る時間がのびる
rows = R9.SETS[5]['table']['rows']
n96 = [float(x) for x in rows[0][1:]]
led96 = [float(x) for x in rows[1][1:]]
bulb96 = [float(x) for x in rows[2][1:]]
assert all(abs(t / n - led96[0] / n96[0]) < 1e-9 for t, n in zip(led96, n96))
eq('理9-6(3) 60回', ans(R9, 6, 3), f'{num(led96[0] / n96[0] * 60)}秒')
eq('理9-6(4) 60秒', ans(R9, 6, 4), f'{num(60 / (led96[0] / n96[0]))}回')
eq('理9-6(5) 豆電球とLED', ans(R9, 6, 5), f'{round(bulb96[0] / led96[0] ** 1 * 2)}分の1' if False else f'{round(led96[0] / bulb96[0])}分の1')

# 7 食塩水のこさ
eq('理9-7(2) 20%', ans(R9, 7, 2), f'{num(20 / (80 + 20) * 100)}%')
eq('理9-7(3) 5%の300g', ans(R9, 7, 3), f'{num(300 * 0.05)}g')
eq('理9-7(4) 水を加える', ans(R9, 7, 4), f'{num(200 * 0.1 / (200 + 200) * 100)}%')
eq('理9-7(5) 水をじょう発', ans(R9, 7, 5), f'{num(200 * 0.1 / (200 - 100) * 100)}%')
x97 = Fraction(2, 10) * 150 - Fraction(8, 100) * 150
x97 = x97 / (1 - Fraction(2, 10))
eq('理9-7(6) 食塩を加える', ans(R9, 7, 6), f'{float(x97):g}g')
eq('理9-7(7) 混ぜる', ans(R9, 7, 7), f'{num((200 * 0.1 + 100 * 0.25) / 300 * 100)}%')
eq('理9-7(8) とけ残り', ans(R9, 7, 8), f'{50 - 36}g')

# 8 惑星：表の距離と公転周期
rows = R9.SETS[7]['table']['rows']
pl98 = rows[0][1:]
d98 = [float(x) for x in rows[1][1:]]
t98 = [float(x) for x in rows[2][1:]]
assert d98 == sorted(d98) and t98 == sorted(t98)
assert all(abs(t ** 2 - d ** 3) / d ** 3 < .05 for d, t in zip(d98, t98))        # 周期の2乗＝距離の3乗（ケプラーの第3法則）
eq('理9-8(1) 太陽に近い4つ', ans(R9, 8, 1), '→'.join(pl98[:4]))
eq('理9-8(4) 木星', ans(R9, 8, 4), f'約{round(t98[pl98.index("木星")] / t98[pl98.index("地球")])}周')
eq('理9-8(5) 火星', ans(R9, 8, 5), f'{num(19 / t98[pl98.index("火星")])}周')

# 9 エネルギーの変換
rows = R9.SETS[8]['table']['rows'][1:]
conv99 = {r[0]: re.search(r'(.+)を、(.+)に変える', r[2]).groups() for r in rows if re.search(r'(.+)を、(.+)に変える', r[2])}
eq('理9-9(1) 電気を運動に', ans(R9, 9, 1), [k for k, (a_, b_) in conv99.items() if (a_, b_) == ('電気', '運動')][0])
eq('理9-9(2) 電気を熱に', ans(R9, 9, 2), [k for k, (a_, b_) in conv99.items() if (a_, b_) == ('電気', '熱')][0])
eq('理9-9(3) 電気をつくる', ans(R9, 9, 3), join(r[0] for r in rows if r[2].endswith('電気に変える')))
eq('理9-9(6) 電力量', ans(R9, 9, 6), f'{40 * 5}Wh')
eq('理9-9(7) 白熱電球とLED', ans(R9, 9, 7), f'{60 // 10}倍')

# 10 浄水：作業の順
key910 = {'取り入れる': 0, 'ちんでん池': 1, 'ろ過池': 2, '塩素': 3}
eq('理9-10(1) 水道水の順', ans(R9, 10, 1), '→'.join(k for k, t in sorted(R9.SETS[9]['items'], key=lambda it: [v for kw, v in key910.items() if kw in it[1]][0])))

# ---------------- 社会・大問1 ----------------
capital = {'青森県': '青森市', '静岡県': '静岡市', '京都府': '京都市', '香川県': '高松市', '新潟県': '新潟市',
           '鹿児島県': '鹿児島市', '沖縄県': '那覇市', '北海道': '札幌市', '宮城県': '仙台市', '千葉県': '千葉市',
           '愛知県': '名古屋市', '大阪府': '大阪市', '兵庫県': '神戸市', '広島県': '広島市', '福岡県': '福岡市'}
def differs(names):
    return [lab for lab, n in names if capital[n][:-1] != n[:-1]]

s1 = list(zip('ABCDEFG', S1.SETS[0]['qs'][1]['ans']))
eq('社1-1(3) 県名と所在地がちがう', ans(S1, 1, 3), join(differs(s1)))
chubu = {'新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県'}
eq('社1-1(6) 中部地方', ans(S1, 1, 6), join(lab for lab, n in s1 if n in chubu))

lat = {'A': 38.9, 'B': 39.9, 'C': 51.5, 'D': 48.9, 'E': -35.3, 'F': -15.8, 'G': 28.6, 'H': -25.7}
eq('社1-3(1) 首都が南半球', ans(S1, 3, 1), join(k for k, v in lat.items() if v < 0))

year = {'A': 1575, 'B': 604, 'C': 1868, 'D': 1192, 'E': 1635, 'F': 752, 'G': 1397, 'H': 1945}
eq('社1-4(7) 5番目', ans(S1, 4, 7), sorted(year, key=year.get)[4])

nara_next = {'京都府', '大阪府', '三重県', '和歌山県'}
opts = dict(zip('アイウエオ', ['京都府', '大阪府', '兵庫県', '三重県', '和歌山県']))
eq('社1-6(2) となりでない', ans(S1, 6, 2), join(k for k, v in opts.items() if v not in nara_next))
inland = {'栃木県', '群馬県', '埼玉県', '山梨県', '長野県', '岐阜県', '滋賀県', '奈良県'}
opts = dict(zip('アイウエオ', ['滋賀県', '岐阜県', '静岡県', '長野県', '京都府']))
eq('社1-6(3) 海に面していない', ans(S1, 6, 3), join(k for k, v in opts.items() if v in inland))

yr7 = {'①': 1635, '②': 604, '③': 1868, '④': 1018, '⑤': 1232}
eq('社1-7(4) 古い順', ans(S1, 7, 4), '→'.join(sorted(yr7, key=yr7.get)))
era = dict(zip('アイウエオ', ['飛鳥', '平安', '鎌倉', '江戸', '明治']))
era_of = {'①': '江戸', '②': '飛鳥', '③': '明治', '④': '平安', '⑤': '鎌倉'}
eq('社1-7(1) 時代', ans(S1, 7, 1), [[k for k, v in era.items() if v == era_of[n]][0] for n in '①②③④⑤'])
person = dict(zip('アイウエオ', ['徳川家光', '北条泰時', '聖徳太子', '明治天皇', '藤原道長']))
person_of = {'①': '徳川家光', '②': '聖徳太子', '③': '明治天皇', '④': '藤原道長', '⑤': '北条泰時'}
eq('社1-7(2) 人物', ans(S1, 7, 2), [[k for k, v in person.items() if v == person_of[n]][0] for n in '①②③④⑤'])

eq('社1-8(4) 時差', ans(S1, 8, 4), f'{135 // 15}時間')
eq('社1-8(5) ロンドンの時刻', ans(S1, 8, 5), f'1月10日の午前{18 - 135 // 15}時')
equator = {'ブラジル', 'インドネシア', 'ケニア'}
opts = dict(zip('アイウエオ', ['ブラジル', 'エジプト', 'インドネシア', 'ケニア', 'メキシコ']))
eq('社1-8(6) 赤道', ans(S1, 8, 6), join(k for k, v in opts.items() if v in equator))

s10 = list(zip('ABCDEFGH', ['北海道', '宮城県', '千葉県', '愛知県', '大阪府', '兵庫県', '広島県', '福岡県']))
eq('社1-10(1) 名前がちがう', ans(S1, 10, 1), join(differs(s10)))

# ---------------- 社会・大問2 ----------------
# 都道府県（北から順の番号＝都道府県コード）、地方（大問2第04セットの(ア)〜(カ)）、県庁所在地
PREF = ['北海道', '青森県', '岩手県', '宮城県', '秋田県', '山形県', '福島県', '茨城県', '栃木県', '群馬県', '埼玉県', '千葉県',
        '東京都', '神奈川県', '新潟県', '富山県', '石川県', '福井県', '山梨県', '長野県', '岐阜県', '静岡県', '愛知県', '三重県',
        '滋賀県', '京都府', '大阪府', '兵庫県', '奈良県', '和歌山県', '鳥取県', '島根県', '岡山県', '広島県', '山口県', '徳島県',
        '香川県', '愛媛県', '高知県', '福岡県', '佐賀県', '長崎県', '熊本県', '大分県', '宮崎県', '鹿児島県', '沖縄県']
CODE = {p: i for i, p in enumerate(PREF, 1)}
REGION = {p: 'ア' if i <= 7 else 'イ' if i <= 14 else 'ウ' if i <= 23 else 'エ' if i <= 30 else 'オ' if i <= 39 else 'カ'
          for p, i in CODE.items()}
CAPITAL = {'北海道': '札幌市', '岩手県': '盛岡市', '宮城県': '仙台市', '茨城県': '水戸市', '栃木県': '宇都宮市', '群馬県': '前橋市',
           '埼玉県': 'さいたま市', '神奈川県': '横浜市', '石川県': '金沢市', '山梨県': '甲府市', '愛知県': '名古屋市',
           '三重県': '津市', '滋賀県': '大津市', '兵庫県': '神戸市', '島根県': '松江市', '香川県': '高松市', '愛媛県': '松山市',
           '沖縄県': '那覇市'}
same_name = lambda p: CAPITAL.get(p, p[:-1] + '市')[:-1] == p[:-1]
INLAND = {'栃木県', '群馬県', '埼玉県', '山梨県', '長野県', '岐阜県', '滋賀県', '奈良県'}


def find(features, text):
    """手がかりの言葉がすべて文中にある名前を1つ返す。"""
    hit = [k for k, ws in features.items() if all(w in text for w in ws)]
    assert len(hit) == 1, (text, hit)
    return hit[0]


# 1 国々：説明文の手がかり → 国名
feat1 = {'ベトナム': ['ハノイ', 'メコン川'], 'カナダ': ['2番目に面積', '英語とフランス語'], 'エジプト': ['ナイル川', 'スエズ運河'],
         'ドイツ': ['EU', '自動車工業'], 'タイ': ['仏教', 'バンコク'], 'チリ': ['銅の産出量', '太平洋側']}
country = {lab: find(feat1, body) for lab, body in S2.SETS[0]['items']}
eq('社2-1(1) 国名', ans(S2, 1, 1), [country[l] for l in 'ABCDEF'])
area = {'ベトナム': 331212, 'カナダ': 9984670, 'エジプト': 1001450, 'ドイツ': 357588, 'タイ': 513120, 'チリ': 756102, '日本': 377975}
row = S2.SETS[0]['table']['rows']
eq('社2-1 表の面積', row[1][1:], [str(round(area[country[l] if l != '日本' else '日本'] / 1e4)) for l in row[0][1:]])
ratio = int(row[1][2]) / int(row[1][-1])
o = {k: int(re.sub(r'\D', '', v)) for k, v in choices(q_text(S2, 1, 2)).items()}
eq('社2-1(2) 面積の倍', ans(S2, 1, 2), min(o, key=lambda k: abs(o[k] - ratio)))
eq('社2-1(3) 首都', ans(S2, 1, 3), {'カナダ': 'オタワ'}[country['B']])
city = {'ベトナム': (21.03, 105.85), 'カナダ': (45.42, -75.70), 'エジプト': (30.04, 31.24), 'ドイツ': (52.52, 13.40),
        'タイ': (13.75, 100.50), 'チリ': (-33.45, -70.67)}
def km(a, b):
    (p1, l1), (p2, l2) = [(math.radians(x), math.radians(y)) for x, y in (a, b)]
    return 6371 * math.acos(math.sin(p1) * math.sin(p2) + math.cos(p1) * math.cos(p2) * math.cos(l1 - l2))
dist = {l: km((35.68, 139.69), city[country[l]]) for l in 'ABCDEF'}
eq('社2-1(4) 最も遠い', ans(S2, 1, 4), max(dist, key=dist.get))
shu = {'ベトナム': 'アジア州', 'タイ': 'アジア州', 'カナダ': '北アメリカ州', 'エジプト': 'アフリカ州', 'ドイツ': 'ヨーロッパ州', 'チリ': '南アメリカ州'}
six = ['アジア州', 'ヨーロッパ州', 'アフリカ州', '北アメリカ州', '南アメリカ州', 'オセアニア州']
eq('社2-1(5) ない州', ans(S2, 1, 5), join(s for s in six if s not in {shu[c] for c in country.values()}))
rice_top3 = {'インド', 'タイ', 'ベトナム'}          # 米の輸出量の上位3か国
eq('社2-1(8) 米の輸出', ans(S2, 1, 8), join(l for l in 'ABCDEF' if country[l] in rice_top3))

# 2 歴史人物：手がかり → 人物 → 年
feat2 = {'足利義政': ['室町幕府の8代'], '伊能忠敬': ['測量'], '卑弥呼': ['邪馬台国'], '吉田茂': ['サンフランシスコ平和条約'],
         '菅原道真': ['894年'], '徳川吉宗': ['江戸幕府の8代'], '中大兄皇子': ['中臣鎌足'], '板垣退助': ['自由党'],
         '源頼朝': ['地頭'], '豊臣秀吉': ['刀狩']}
year2 = {'卑弥呼': 239, '中大兄皇子': 645, '菅原道真': 894, '源頼朝': 1185, '足利義政': 1467, '豊臣秀吉': 1588,
         '徳川吉宗': 1716, '伊能忠敬': 1800, '板垣退助': 1881, '吉田茂': 1951}
who = {lab: find(feat2, body) for lab, body in S2.SETS[1]['items']}
eq('社2-2(2) 人物名', ans(S2, 2, 2), [who[l] for l in 'BCDE'])
def dynasty(y):
    return next(n for n, a, b in [('隋', 581, 618), ('唐', 618, 907), ('宋', 960, 1279), ('元', 1271, 1368),
                                  ('明', 1368, 1644), ('清', 1644, 1912)] if a <= y < b)
pair = f'{dynasty(year2[who["E"]])}・{dynasty(year2[who["A"]])}'
eq('社2-2(3) 中国の王朝', ans(S2, 2, 3), [k for k, v in choices(q_text(S2, 2, 3)).items() if v == pair][0])
eq('社2-2(7) 6番目', ans(S2, 2, 7), sorted(who, key=lambda l: year2[who[l]])[5])

# 3 文化：人物の年 → 時代 → ①〜⑩
eras = [('縄文', -14000), ('弥生', -400), ('古墳', 250), ('飛鳥', 592), ('奈良', 710), ('平安', 794), ('鎌倉', 1185),
        ('室町', 1336), ('安土桃山', 1573), ('江戸', 1603), ('明治', 1868)]
era_of = lambda y: [n for n, a in eras if a <= y][-1]
num_of = {body.split('時代')[0]: lab for lab, body in S2.SETS[2]['items']}
year3 = {'清少納言': 1000, '運慶': 1203, '近松門左衛門': 1703, '行基': 745, '狩野永徳': 1576}
eq('社2-3(7) 人物の時代', ans(S2, 3, 7), [num_of[era_of(year3[n])] for n in S2.SETS[2]['qs'][6]['labels']])
site = {'三内丸山遺跡': ('青森県', '縄文', False), '吉野ヶ里遺跡': ('佐賀県', '弥生', True), '登呂遺跡': ('静岡県', '弥生', False)}
o3 = choices(q_text(S2, 3, 2))
eq('社2-3(2) 青森の縄文遺跡', ans(S2, 3, 2), [k for k, v in o3.items() if site[v][:2] == ('青森県', '縄文')][0])
eq('社2-3(3) ほりで囲んだ集落', ans(S2, 3, 3), [k for k, v in o3.items() if site[v][1] == '弥生' and site[v][2]][0])

# 4 地方区分
pick_region = lambda f: join(r for r in 'アイウエオカ' if any(f(p) for p in PREF if REGION[p] == r))
eq('社2-4(1) 「島」', ans(S2, 4, 1), pick_region(lambda p: '島' in p))
eq('社2-4(2) 「岡」', ans(S2, 4, 2), pick_region(lambda p: '岡' in p))
eq('社2-4(3) 海に面していない', ans(S2, 4, 3), pick_region(lambda p: p in INLAND))
cnt = {r: sum(REGION[p] == r for p in PREF) for r in 'アイウエオカ'}
eq('社2-4(4) 数が最も多い', ans(S2, 4, 4), join(r for r in cnt if cnt[r] == max(cnt.values())))
natural = {'知床': ['北海道'], '白神山地': ['青森県', '秋田県'], '小笠原諸島': ['東京都'], '屋久島': ['鹿児島県'],
           '奄美大島・徳之島・沖縄島北部・西表島': ['鹿児島県', '沖縄県']}
eq('社2-4(5) 自然遺産', ans(S2, 4, 5), join(sorted({REGION[p] for ps in natural.values() for p in ps}, key='アイウエオカ'.index)))
wh = {'富岡製糸場': '群馬県', '白川郷': '岐阜県', '厳島神社': '広島県', '平泉': '岩手県', '姫路城': '兵庫県'}
eq('社2-4(6) 世界遺産の地方', ans(S2, 4, 6), [REGION[wh[n]] for n in S2.SETS[3]['qs'][5]['labels']])
kii = {REGION[p] for p in ('三重県', '奈良県', '和歌山県')}
assert len(kii) == 1
eq('社2-4(9) 紀伊山地', ans(S2, 4, 9), kii.pop())

# 5 旅：見たもの → 都道府県
feat5 = {'宮城県': ['松島'], '滋賀県': ['日本最大の湖'], '広島県': ['平和記念公園'], '京都府': ['天橋立'], '長崎県': ['大浦天主堂'],
         '群馬県': ['富岡製糸場'], '石川県': ['兼六園'], '香川県': ['讃岐うどん']}
trip = {r[0]: find(feat5, r[1]) for r in S2.SETS[4]['table']['rows'][1:]}
eq('社2-5(1) 都道府県名', ans(S2, 5, 1), [trip[l] for l in 'ABCDEFGH'])
sankei = {'松島': '宮城県', '天橋立': '京都府', '宮島（厳島）': '広島県'}
eq('社2-5(2) 日本三景', ans(S2, 5, 2), ['宮島（厳島）', [l for l, p in trip.items() if p == sankei['宮島（厳島）']][0]])
eq('社2-5(3) 原爆の日', ans(S2, 5, 3), f'{2026 - 1945}回目')
eq('社2-5(7) 海に面していない', ans(S2, 5, 7), join(l for l, p in trip.items() if p in INLAND))
eq('社2-5(8) 名前がちがう', ans(S2, 5, 8), join(l for l, p in trip.items() if not same_name(p)))

# 6 三権分立：図の矢印（build の SANKEN_ARROWS）と、それぞれの関係のはたらき
power = {('国会', '内閣'): '内閣不信任', ('内閣', '国会'): '衆議院の解散', ('国会', '裁判所'): '弾劾裁判',
         ('裁判所', '国会'): '法律が憲法', ('内閣', '裁判所'): '最高裁判所長官', ('裁判所', '内閣'): '内閣の命令'}
o6 = choices(q_text(S2, 6, 1))
eq('社2-6(1) 矢印', ans(S2, 6, 1), [[k for k, v in o6.items() if power[(p, q)] in v][0] for _, p, q in SANKEN_ARROWS])
eq('社2-6(2) 国民から', ans(S2, 6, 2), [{'国会': '選挙', '内閣': '世論', '裁判所': '国民審査'}[n] for n in ('国会', '内閣', '裁判所')])
high = {'大阪': {'大阪府', '京都府', '兵庫県', '奈良県', '滋賀県', '和歌山県'}}
eq('社2-6(5) 高等裁判所', ans(S2, 6, 5).split('（')[0], [k for k, v in high.items() if '奈良県' in v][0])

# 7 都道府県番号：表が北から順になっているか、手がかり → 番号
cells = [x for r in S2.SETS[6]['table']['rows'] for x in r if x]
eq('社2-7 表の番号', cells, [f'{i} {p}' for p, i in CODE.items()])
feat7 = {'山形県': ['さくらんぼ'], '大阪府': ['天下の台所'], '島根県': ['松江市'], '福岡県': ['八幡製鉄所'], '長野県': ['レタス'], '北海道': ['知床']}
q71 = q_text(S2, 7, 1)
eq('社2-7(1) 説明文', ans(S2, 7, 1), [str(CODE[find(feat7, ln)]) for ln in q71.split('\n')[1:]])
edge = {'最北端': '北海道', '最南端': '東京都', '最東端': '東京都', '最西端': '沖縄県'}   # 択捉島・沖ノ鳥島・南鳥島・与那国島
eq('社2-7(2) 東西南北のはし', ans(S2, 7, 2), [str(CODE[edge[k]]) for k in S2.SETS[6]['qs'][1]['labels']])
eq('社2-7(3) 明石市', ans(S2, 7, 3), str(CODE['兵庫県']))
eq('社2-7(4) 冬季オリンピック', ans(S2, 7, 4), join(str(CODE[p]) for p in ('北海道', '長野県')))
top3 = {'りんご': {'青森県', '長野県', '岩手県'}, 'みかん': {'和歌山県', '愛媛県', '静岡県'}, 'ぶどう': {'山梨県', '長野県', '岡山県'}}
o7 = {k: {PREF[int(n) - 1] for n in v.split('・')} for k, v in choices(q_text(S2, 7, 5)).items()}
eq('社2-7(5) 果物', ans(S2, 7, 5), [[f for f, s in top3.items() if s == o7[k]][0] for k in 'アイウ'])
assert {REGION[PREF[i - 1]] for i in range(31, 40)} == {'オ'}
eq('社2-7(6) 31〜39', ans(S2, 7, 6), '中国・四国地方')
eq('社2-7(7) 九州で名前がちがう', ans(S2, 7, 7), join(str(i) for i in range(40, 48) if not same_name(PREF[i - 1])))

# 8 伝統的工芸品と気候
craft = {'二風谷アットゥシ': '北海道', '小千谷ちぢみ': '新潟県', '木曽漆器': '長野県', '箱根寄木細工': '神奈川県', '備前焼': '岡山県', '琉球びんがた': '沖縄県'}
made = {lab: craft[body.split('：')[0]] for lab, body in S2.SETS[7]['items']}
eq('社2-8(1) 道県', ans(S2, 8, 1), [made[l] for l in 'ABCDEF'])
climate = {'北海道': '北海道の気候', '新潟県': '日本海側', '長野県': '中央高地', '神奈川県': '太平洋側', '岡山県': '瀬戸内', '沖縄県': '南西諸島'}
o8 = choices(q_text(S2, 8, 2))
eq('社2-8(2) 気候区分', ans(S2, 8, 2), [[k for k, v in o8.items() if climate[made[l]] in v][0] for l in 'ABCDEF'])
desc = {'冬もおだやか': '瀬戸内', '台風': '南西諸島', '気温の差が大きく': '中央高地'}
lines8 = q_text(S2, 8, 3).split('\n')[1:]
eq('社2-8(3) 気候の説明', ans(S2, 8, 3), [[l for l in 'ABCDEF' if climate[made[l]] == find({v: [k] for k, v in desc.items()}, ln)][0] for ln in lines8])
eq('社2-8(4) 雪が多い', ans(S2, 8, 4), [l for l in 'ABCDEF' if climate[made[l]] == '日本海側'][0])

# 9 農産物の全国一（2025年産の米をふくむ、2026年10月現在の統計）
first = {'米': '新潟県', 'じゃがいも': '北海道', 'さとうきび': '沖縄県'}
o9 = {v: k for k, v in choices(q_text(S2, 9, 7).split('\n')[-1]).items()}
eq('社2-9(7) 全国一', ans(S2, 9, 7), [o9[first[n]] for n in ('米', 'じゃがいも', 'さとうきび')])

# 10 食料自給率（2025年度、2026年8月公表）と輸入相手国
o10 = {k: int(re.sub(r'\D', '', v)) for k, v in choices(q_text(S2, 10, 1)).items()}
eq('社2-10(1) カロリーベース', ans(S2, 10, 1), min(o10, key=lambda k: abs(o10[k] - 37)))
rate = {'米': 95, '野菜': 77, '小麦': 16, '大豆': 7}          # 重さで計算した自給率(%)のおよその値
o10b = {v: k for k, v in choices(q_text(S2, 10, 2)).items()}
eq('社2-10(2) 高い順', ans(S2, 10, 2), '→'.join(o10b[n] for n in sorted(rate, key=rate.get, reverse=True)))
partner = {'輸入額が最も大きい': '中国', '小麦を最も多く': 'アメリカ合衆国', '鉄鉱石を最も多く': 'オーストラリア'}
q104 = q_text(S2, 10, 4).split('\n')
o10c = {v: k for k, v in choices(q104[-1]).items()}
eq('社2-10(4) 輸入相手国', ans(S2, 10, 4), [o10c[find({v: [k] for k, v in partner.items()}, ln)] for ln in q104[1:4]])

# ---------------- 社会・大問3 ----------------
def ring_has(pts, x, y):
    """多角形（経度・緯度を10倍した点）の中に、点(x, y)があるか。"""
    n, inside_ = len(pts), False
    for i in range(n):
        x1, y1 = pts[i][0] / 10, pts[i][1] / 10
        x2, y2 = pts[(i + 1) % n][0] / 10, pts[(i + 1) % n][1] / 10
        if (y1 > y) != (y2 > y) and x < (x2 - x1) * (y - y1) / (y2 - y1) + x1:
            inside_ = not inside_
    return inside_


def country_at(lon, lat):
    return sorted({n for n, pts in world_outline.RINGS if ring_has(pts, lon, lat)})


blank_of = lambda text: re.search(r'〔(.)〕', text).group(1)

# 1 奈良県の史跡：〔 〕の答え、時代、市制からの年数
feat31 = {'纒向': ['桜井市'], '蘇我': ['石舞台'], '聖徳': ['法隆寺'], '平城': ['平城宮跡'], '聖武': ['東大寺'], '鑑真': ['唐招提寺']}
blank31 = {blank_of(b): find(feat31, b) for _, b in S3.SETS[0]['items']}
eq('社3-1(1) 空らん', ans(S3, 1, 1), [blank31[k] for k in 'アイウエオカ'])
year31 = {'B': 620, 'C': 607, 'D': 710, 'E': 752, 'F': 759}           # 石舞台古墳は7世紀前半
eq('社3-1(2) 時代', ans(S3, 1, 2), [join(k for k, y in year31.items() if era_of(y) == e) for e in ('飛鳥', '奈良')])
eq('社3-1(5) 市制から', ans(S3, 1, 5), f'{2026 - 1954}年目')
kuni = {'飛鳥・藤原の宮都': {'石舞台古墳'}, '古都奈良の文化財': {'平城宮跡', '東大寺', '唐招提寺', '興福寺', '薬師寺', '春日大社', '元興寺'}}
eq('社3-1(7) 飛鳥・藤原の宮都', ans(S3, 1, 7), [k for k, v in choices(q_text(S3, 1, 7)).items() if v in kuni['飛鳥・藤原の宮都']][0])

# 2 2026年のできごと
s32 = dict(S3.SETS[1]['items'])
cup_hosts = {'アメリカ合衆国', 'カナダ', 'メキシコ'}
medal = {'金': 5, '銀': 7, '銅': 12}
assert all(f'{m}{n}' in s32['A'].replace('・', '') or f'{m}{n}' in s32['A'] for m, n in medal.items())
eq('社3-2(1) 空らん', ans(S3, 2, 1), ['ミラノ', str(sum(medal.values())), join(cup_hosts - {'アメリカ合衆国', 'メキシコ'}), 'スペイン', 'エビアン', '韓国'])
eq('社3-2(2) 金メダルの割合', ans(S3, 2, 2), f'約{round(medal["金"] / sum(medal.values()) * 100)}%')
cap32 = {'スペイン': 'マドリード', 'アルゼンチン': 'ブエノスアイレス', 'メキシコ': 'メキシコシティ'}
eq('社3-2(4) メキシコの首都', ans(S3, 2, 4), cap32['メキシコ'])
eq('社3-2(5) 首都', ans(S3, 2, 5), [cap32[n] for n in S3.SETS[1]['qs'][4]['labels']])
G7 = {'日本': 'アジア州', 'アメリカ': '北アメリカ州', 'カナダ': '北アメリカ州', 'イギリス': 'ヨーロッパ州', 'フランス': 'ヨーロッパ州',
      'ドイツ': 'ヨーロッパ州', 'イタリア': 'ヨーロッパ州'}
eq('社3-2(6) G7のアジア州', ans(S3, 2, 6), join(k for k, v in G7.items() if v == 'アジア州'))

# 3 農畜産物：上位3道府県の表から品目を探す
top3 = {'米': ('新潟県', '北海道', '秋田県'), '小麦': ('北海道', '福岡県', '佐賀県'), 'キャベツ': ('群馬県', '愛知県', '千葉県'),
        'レタス': ('長野県', '茨城県', '群馬県'), 'いちご': ('栃木県', '福岡県', '熊本県'), 'りんご': ('青森県', '長野県', '岩手県'),
        'ぶどう': ('山梨県', '長野県', '岡山県'), 'もも': ('山梨県', '福島県', '長野県'), '肉用牛': ('北海道', '鹿児島県', '宮崎県')}
lead33 = {v: k for k, v in choices(S3.SETS[2]['lead']).items()}
rows33 = {r[0]: tuple(r[1:]) for r in S3.SETS[2]['table']['rows'][1:]}
item33 = {}
for k, v in rows33.items():
    hit = [n for n, t in top3.items() if t == v]
    assert len(hit) == 1, (k, hit)
    item33[k] = hit[0]
eq('社3-3(1) 品目', ans(S3, 3, 1), [lead33[item33[k]] for k in S3.SETS[2]['qs'][0]['labels']])
eq('社3-3(2) 1位が北海道', ans(S3, 3, 2), join(k for k, v in rows33.items() if v[0] == '北海道'))
eq('社3-3(5) 九州地方の県', ans(S3, 3, 5), join(p for p in rows33['D'] if REGION[p] == 'カ'))
eq('社3-3(6) 北海道の割合', ans(S3, 3, 6), f'約{round(558.5 / 2672 * 100)}%')
eq('社3-3(7) 米1位の県の川', ans(S3, 3, 7), {'新潟県': '信濃川'}[top3['米'][0]])

# 4 輸入：品目ごとの主な輸入相手国
ex4 = {'小麦': {'アメリカ合衆国', 'カナダ', 'オーストラリア'}, '大豆': {'アメリカ合衆国', 'ブラジル', 'カナダ'}, '鉄鉱石': {'オーストラリア', 'ブラジル'},
       'バナナ': {'フィリピン', 'エクアドル'}, '石炭': {'オーストラリア', 'インドネシア'}, '衣類': {'中国', 'ベトナム'}}
lead34 = {v: k for k, v in choices(S3.SETS[3]['lead']).items()}
row34 = {r[0]: set(r[1].split('・')) for r in S3.SETS[3]['table']['rows'][1:]}
item34 = {}
for k, v in row34.items():
    hit = [n for n, t in ex4.items() if t == v]
    assert len(hit) == 1, (k, hit)
    item34[k] = hit[0]
eq('社3-4(1) 品目', ans(S3, 4, 1), [lead34[item34[k]] for k in S3.SETS[3]['qs'][0]['labels']])
meaning = {'エクアドル': '赤道', 'フィリピン': '王の名'}
eq('社3-4(2) 赤道の意味', ans(S3, 4, 2), [c for c in ex4['バナナ'] if meaning[c] == '赤道'][0])
eq('社3-4(3) 共通の国', ans(S3, 4, 3), join(sorted(ex4['鉄鉱石'] & ex4['石炭'])))
eq('社3-4(5) その他の輸入量', ans(S3, 4, 5), f'{num(500 * (1 - .40 - .35))}万t')
lat34 = {'フィリピン': 14.6, 'エクアドル': -0.2}                      # 首都マニラ・キトの緯度
eq('社3-4(8) 気候帯', ans(S3, 4, 8), '熱帯' if all(abs(v) < 23.4 for v in lat34.values()) else 'ほか')

# 5 国連と国際会議
mem = {'日本', 'アメリカ', 'イギリス', 'ドイツ', 'イタリア', 'カナダ', 'フランス'}
named = {n for n in mem if n in S3.SETS[4]['items'][1][1]}                # 生徒の発言に出てくるG7の国
UN = 193
eq('社3-5(1) 空らん', ans(S3, 5, 1), [join(mem - named), 'ニューヨーク', str(UN), '安全保障', '常任', {'COP21': 'パリ'}['COP21']])
eq('社3-5(4) 過半数', ans(S3, 5, 4), f'{UN // 2 + 1}か国')
eq('社3-5(6) 北アメリカ州', ans(S3, 5, 6), '・'.join(k for k in ('アメリカ', 'カナダ') if G7[k] == '北アメリカ州'))
eq('社3-5(8) 加盟から', ans(S3, 5, 8), f'{2026 - 1956}年')

# 6・7 世界地図：印が正しい国の中にあるかを、国境のデータで確かめる
en = {'大韓民国': 'South Korea', '中華人民共和国': 'China', 'ロシア連邦': 'Russia', 'フィリピン': 'Philippines', 'ニュージーランド': 'New Zealand',
      'カナダ': 'Canada', 'アメリカ合衆国': 'United States of America', 'メキシコ': 'Mexico', 'ブラジル': 'Brazil', 'アルゼンチン': 'Argentina',
      'フランス': 'France', 'エジプト': 'Egypt', 'ナイジェリア': 'Nigeria', 'インド': 'India', 'インドネシア': 'Indonesia', 'オーストラリア': 'Australia'}
ja = {v: k for k, v in en.items()}
marks6 = S3.SETS[5]['fig']['args']['marks']
at6 = {m[0]: country_at(m[1], m[2]) for m in marks6}
assert all(len(v) == 1 for v in at6.values()), at6
eq('社3-6(1) 地図の国名', ans(S3, 6, 1), [ja[at6[k][0]] for k in 'ABCDE'])
capital6 = {'大韓民国': 'ソウル', '中華人民共和国': 'ペキン', 'ロシア連邦': 'モスクワ', 'フィリピン': 'マニラ', 'ニュージーランド': 'ウェリントン'}
eq('社3-6(2) 首都', ans(S3, 6, 2), [capital6[ja[at6[k][0]]] for k in 'ABCDE'])
eq('社3-6(3) 面積の倍', ans(S3, 6, 3), f'約{round(960 / 38)}倍')
utc = {'日本': 9, '中華人民共和国': 8}
eq('社3-6(8) 時差', ans(S3, 6, 8), f'午前{9 - (utc["日本"] - utc["中華人民共和国"])}時')

marks7 = S3.SETS[6]['fig']['args']['marks']
at7 = {m[0]: country_at(m[1], m[2]) for m in marks7}
assert all(len(v) == 1 for v in at7.values()), at7
name7 = {k: ja[v[0]] for k, v in at7.items()}
eq('社3-7(1) 地図の国名', ans(S3, 7, 1), [name7[k] for k in S3.SETS[6]['qs'][0]['labels']])
cap7 = {'カナダ': (45.42, -75.70), 'アメリカ合衆国': (38.90, -77.04), 'メキシコ': (19.43, -99.13), 'ブラジル': (-15.79, -47.88),
        'アルゼンチン': (-34.60, -58.38), 'フランス': (48.86, 2.35), 'エジプト': (30.04, 31.24), 'ナイジェリア': (9.08, 7.40),
        'インド': (28.61, 77.21), 'インドネシア': (-6.21, 106.85), 'オーストラリア': (-35.28, 149.13)}
far = max(name7, key=lambda k: km((35.68, 139.69), cap7[name7[k]]))
eq('社3-7(2) 日本から最も遠い', ans(S3, 7, 2), far)
lat_range = {'カナダ': (41.7, 83.1), 'アメリカ合衆国': (24.5, 49.4), 'メキシコ': (14.5, 32.7), 'ブラジル': (-33.7, 5.3), 'アルゼンチン': (-55.1, -21.8),
             'フランス': (41.3, 51.1), 'エジプト': (22.0, 31.7), 'ナイジェリア': (4.3, 13.9), 'インド': (6.7, 35.5),
             'インドネシア': (-11.0, 6.1), 'オーストラリア': (-43.6, -10.7)}
eq('社3-7(3) 赤道が通る', ans(S3, 7, 3), join(k for k in sorted(name7) if lat_range[name7[k]][0] < 0 < lat_range[name7[k]][1]))
pop = {'インド': 1464, 'アメリカ合衆国': 347, 'インドネシア': 286, 'ナイジェリア': 237, 'ブラジル': 213, 'メキシコ': 131, 'エジプト': 118,
       'フランス': 66, 'アルゼンチン': 46, 'カナダ': 41, 'オーストラリア': 27}          # 2025年の人口（百万人。国連の推計）
eq('社3-7(4) 人口の順', ans(S3, 7, 4), '→'.join(sorted(name7, key=lambda k: -pop[name7[k]])[:3]))
spanish = {'メキシコ', 'アルゼンチン'}
eq('社3-7(5) スペイン語', ans(S3, 7, 5), join(k for k in sorted(name7) if name7[k] in spanish))
africa = {'エジプト', 'ナイジェリア'}
eq('社3-7(6) アフリカ州', ans(S3, 7, 6), join(k for k in sorted(name7) if name7[k] in africa))
eq('社3-7(7) 面積の倍', ans(S3, 7, 7), f'約{round(770 / 38)}倍')
eq('社3-7(8) ヒンドゥー教', ans(S3, 7, 8), [k for k in name7 if name7[k] == 'インド'][0])

# 世界遺産（2026年10月現在）：(名前, 登録年, 種類, 都道府県)。表の順に並べてある
HERITAGE = [('法隆寺地域の仏教建造物', 1993, '文化', ['奈良県']), ('姫路城', 1993, '文化', ['兵庫県']), ('屋久島', 1993, '自然', ['鹿児島県']),
            ('白神山地', 1993, '自然', ['青森県', '秋田県']), ('古都京都の文化財', 1994, '文化', ['京都府', '滋賀県']),
            ('白川郷・五箇山の合掌造り集落', 1995, '文化', ['岐阜県', '富山県']), ('原爆ドーム', 1996, '文化', ['広島県']), ('厳島神社', 1996, '文化', ['広島県']),
            ('古都奈良の文化財', 1998, '文化', ['奈良県']), ('日光の社寺', 1999, '文化', ['栃木県']), ('琉球王国のグスク及び関連遺産群', 2000, '文化', ['沖縄県']),
            ('紀伊山地の霊場と参詣道', 2004, '文化', ['三重県', '奈良県', '和歌山県']), ('知床', 2005, '自然', ['北海道']),
            ('石見銀山遺跡', 2007, '文化', ['島根県']), ('平泉', 2011, '文化', ['岩手県']), ('小笠原諸島', 2011, '自然', ['東京都']),
            ('富士山', 2013, '文化', ['山梨県', '静岡県']), ('富岡製糸場と絹産業遺産群', 2014, '文化', ['群馬県']), ('明治日本の産業革命遺産', 2015, '文化', ['福岡県', '長崎県']),
            ('国立西洋美術館', 2016, '文化', ['東京都']), ('宗像・沖ノ島と関連遺産群', 2017, '文化', ['福岡県']), ('長崎と天草の潜伏キリシタン関連遺産', 2018, '文化', ['長崎県', '熊本県']),
            ('百舌鳥・古市古墳群', 2019, '文化', ['大阪府']), ('奄美大島・徳之島・沖縄島北部及び西表島', 2021, '自然', ['鹿児島県', '沖縄県']),
            ('北海道・北東北の縄文遺跡群', 2021, '文化', ['北海道', '青森県', '岩手県', '秋田県']), ('佐渡島の金山', 2024, '文化', ['新潟県']),
            ('飛鳥・藤原の宮都', 2026, '文化', ['奈良県'])]
kind_n = lambda k: sum(1 for h in HERITAGE if h[2] == k)

# 8 日本の世界遺産
feat38 = {'日光': ['東照宮'], '銀': ['石見銀山'], '厳島': ['平清盛'], '合掌': ['白川郷'], '縄文': ['屋久島'], '3776': ['富士山'], '原子爆弾': ['原爆ドーム'], '琉球': ['琉球王国']}
blank38 = {blank_of(b): find(feat38, b) for _, b in S3.SETS[7]['items']}
eq('社3-8(1) 空らん', ans(S3, 8, 1), [blank38[k] for k in 'アイウエオカキク'])
site38 = {'A': '日光の社寺', 'B': '石見銀山遺跡', 'C': '厳島神社', 'D': '白川郷・五箇山の合掌造り集落', 'E': '屋久島', 'F': '富士山',
          'G': '原爆ドーム', 'H': '琉球王国のグスク及び関連遺産群'}
h38 = {h[0]: h for h in HERITAGE}
eq('社3-8(2) 世界自然遺産', ans(S3, 8, 2), join(k for k, n in site38.items() if h38[n][2] == '自然'))
eq('社3-8(3) またがる', ans(S3, 8, 3), join(k for k, n in site38.items() if len(h38[n][3]) > 1))
eq('社3-8(4) 都道府県', ans(S3, 8, 4), [h38[site38[k]][3][0] for k in S3.SETS[7]['qs'][3]['labels']])
eq('社3-8(5) 件数', ans(S3, 8, 5), [f'{kind_n("文化")}件', f'{kind_n("自然")}件'])
assert len(HERITAGE) == 27

# 9 戦い：年の順
war = {'①': ('元', 1274), '②': ('西郷隆盛', 1877), '③': ('百済', 663), '④': ('キリスト教徒', 1637), '⑤': ('桶狭間', 1560), '⑥': ('明智光秀', 1582), '⑦': ('鳥羽・伏見', 1868)}
items39 = dict(S3.SETS[8]['items'])
for k, (w, y) in war.items():
    assert w in items39[k] and str(y) in items39[k].replace('と1281年', ''), (k, w, y)
eq('社3-9(2) 古い順', ans(S3, 9, 2), '→'.join(sorted(war, key=lambda k: war[k][1])))
eq('社3-9(9) 年数', ans(S3, 9, 9), f'{2026 - war["①"][1]}年後')

# 10 年表：表の登録年と世界遺産の一覧を照らす
rows310 = S3.SETS[9]['table']['rows'][1:]
for yr, cell, _ in rows310:
    eq(f'社3-10 表の{yr}年', cell, '・'.join(h[0] for h in HERITAGE if h[1] == int(yr)))
eq('社3-10(2) 初登録から', ans(S3, 10, 2), f'{2026 - min(h[1] for h in HERITAGE)}年')
eq('社3-10(3) 1993年の自然遺産', ans(S3, 10, 3), '・'.join(h[0] for h in HERITAGE if h[1] == 1993 and h[2] == '自然'))
eq('社3-10(4) 奈良県の件数', ans(S3, 10, 4), f'{sum(1 for h in HERITAGE if "奈良県" in h[3])}件')
o310 = choices(q_text(S3, 10, 5))
yr10 = {'愛・地球博': 2005, '長野': 1998, '阪神': 1995, '東日本': 2011}
eq('社3-10(5) できごとの順', ans(S3, 10, 5), '→'.join(sorted(o310, key=lambda k: [y for n, y in yr10.items() if n in o310[k]][0])))
eq('社3-10(7) 古都奈良にふくまれない', ans(S3, 10, 7), [k for k, v in choices(q_text(S3, 10, 7)).items() if v not in kuni['古都奈良の文化財']][0])

# ---------------- 社会・大問4 ----------------
def blanks_of(items):
    """〔ア〕などの空らんと、その直前の文字を {記号: 直前の文} にする。"""
    out = {}
    for _, t in items:
        for m in re.finditer(r'〔(.)〕', t):
            out.setdefault(m.group(1), t[:m.start()])        # 同じ記号が2回出るときは、最初の空らん
    return out


def by_suffix(table, pre):
    hit = [v for k, v in table.items() if pre.endswith(k)]
    assert len(hit) == 1, (pre, hit)
    return hit[0]


# 1 国会・内閣・裁判所
b41 = blanks_of(S4.SETS[0]['items'])
fact41 = {'国権の': '最高', '参議院の': '二院', '国会が指名した': '内閣総理大臣', '首相は': '高市早苗', '裁判官とともに刑事裁判を行う': '裁判員'}
eq('社4-1(1) 空らん', ans(S4, 1, 1), [by_suffix(fact41, b41[k]) for k in 'アイウエオ'])
age41 = {'衆議院議員': 25, '参議院議員': 30}
eq('社4-1(2) 被選挙権', ans(S4, 1, 2), [f'満{age41[k]}歳以上' for k in S4.SETS[0]['qs'][1]['labels']])
duty41 = {'法律をつくる': '国会', '外国と条約を結ぶ': '内閣', '裁判官をやめさせるかどうか決める': '国会', '予算案をつくって国会に出す': '内閣'}
eq('社4-1(5) 内閣の仕事', ans(S4, 1, 5), join(k for k, v in choices(q_text(S4, 1, 5)).items() if duty41[v] == '内閣'))
task41 = {'国の防衛': '防衛省', '自然環境や地球温暖化の対策': '環境省', '農業・林業・水産業': '農林水産省', '道路・鉄道・空港・観光': '国土交通省'}
eq('社4-1(6) 省', ans(S4, 1, 6), [task41[v] for _, v in re.findall(r'([①②③④]) ([^　\n]+)', q_text(S4, 1, 6))])
eq('社4-1(7) 裁判員', ans(S4, 1, 7), f'{9 - 3}人')                      # 裁判官3人と裁判員6人で、合議体は9人

# 2 スーパーマーケット：消費税と期限表示
p42 = int(re.search(r'税ぬき(\d+)円', q_text(S4, 2, 1)).group(1))
r42 = int(re.search(r'税率は(\d+)%', q_text(S4, 2, 1)).group(1))
eq('社4-2(1) 税込み', ans(S4, 2, 1), f'{p42 + p42 * r42 // 100}円')
rate42 = {'飲食料品': 8, 'ふつうの商品': 10}                                # 軽減税率の対象は飲食料品
eq('社4-2(2) ふつうの税率', ans(S4, 2, 2), f'{rate42["ふつうの商品"]}%')
shelf42 = {'缶詰': 720, 'お弁当': 1}                                       # 日持ちの目安（日）。おおむね5日以内は消費期限
eq('社4-2(4) 期限表示', ans(S4, 2, 4), ['消費期限' if shelf42[k] <= 5 else '賞味期限' for k in S4.SETS[1]['qs'][3]['labels']])

# 3 工業地帯
feat43 = {'中京工業地帯': ['豊田市'], '阪神工業地帯': ['大阪湾'], '京浜工業地帯': ['東京湾'], '瀬戸内工業地域': ['瀬戸内海']}
eq('社4-3(1) 工業地帯', ans(S4, 3, 1), [find(feat43, t) for _, t in S4.SETS[2]['items']])
b43 = blanks_of(S4.SETS[2]['items'])
fact43 = {'豊田市を中心に、': '自動車', '東大阪市などに、': '中小', '石油化学': 'コンビナート'}
eq('社4-3(2) 空らん', ans(S4, 3, 2), [by_suffix(fact43, b43[k]) for k in 'アイウ'])
n43 = int(re.search(r'1日に(\d+)台', q_text(S4, 3, 4)).group(1)) * int(re.search(r'約(\d+)万個', q_text(S4, 3, 4)).group(1))
eq('社4-3(4) 部品の数', ans(S4, 3, 4), f'{n43}万個')
kind43 = {'自動車': '重化学', 'せんい': '軽', '石油化学': '重化学', '食料品': '軽'}
eq('社4-3(6) 軽工業', ans(S4, 3, 6), join(k for k, v in choices(q_text(S4, 3, 6)).items() if kind43[v] == '軽'))

# 4 修学旅行：手がかり → 県 → 地方・県庁所在地・世界遺産
spot44 = {'青森県': ['ねぶた祭'], '沖縄県': ['首里城'], '石川県': ['兼六園'], '高知県': ['桂浜'], '島根県': ['松江城']}
pref44 = {k: find(spot44, t) for k, t in S4.SETS[3]['items']}
eq('社4-4(1) 県名', ans(S4, 4, 1), [pref44[k] for k in 'ABCDE'])
region8 = lambda p: ('北海道' if CODE[p] == 1 else '東北' if CODE[p] <= 7 else '関東' if CODE[p] <= 14 else '中部' if CODE[p] <= 23
                     else '近畿' if CODE[p] <= 30 else '中国' if CODE[p] <= 35 else '四国' if CODE[p] <= 39 else '九州') + '地方'
eq('社4-4(2) 地方', ans(S4, 4, 2), [region8(pref44[k]) for k in 'ABCDE'])
eq('社4-4(3) 県名と県庁所在地名がちがう', ans(S4, 4, 3), join(k for k in 'ABCDE' if not same_name(pref44[k])))
eq('社4-4(4) 世界遺産', ans(S4, 4, 4), join(k for k in 'ABCDE' if any(pref44[k] in h[3] for h in HERITAGE)))
share44 = 70.3                                                          # 沖縄県にある米軍専用施設の割合（%）●●
opt44 = {'ア': 10, 'イ': 30, 'ウ': 70}
eq('社4-4(5) 米軍専用施設', ans(S4, 4, 5), min(opt44, key=lambda k: abs(opt44[k] - share44)))
hokuriku = ['東京', '大宮', '長野', '富山', '金沢', '小松', '加賀温泉', '芦原温泉', '福井', '越前たけふ', '敦賀']   # 2024年3月に金沢から先が開業
eq('社4-4(6) 北陸新幹線', ans(S4, 4, 6), hokuriku[-1] + '駅')
eq('社4-4(7) 出雲大社', ans(S4, 4, 7)[:4], {'出雲大社': '大国主命'}['出雲大社'])
eq('社4-4(8) 果物1位', ans(S4, 4, 8), {'青森県': 'りんご'}[pref44['A']])

# 5 日本国憲法と天皇
def after_months(y, m, d, n):
    t = y * 12 + (m - 1) + n
    return f'{t // 12}年{t % 12 + 1}月{d}日'


eq('社4-5(2) 公布と施行', ans(S4, 5, 2), ['1946年11月3日', after_months(1946, 11, 3, 6)])   # 公布から6か月後に施行
eq('社4-5(3) 施行から', ans(S4, 5, 3), f'{2026 - 1947}年')
eq('社4-5(6) 令和何年', ans(S4, 5, 6), f'令和{2026 - 2019 + 1}年')
three = ['もたず', 'つくらず', 'もちこませず']
eq('社4-5(8) 非核三原則', ans(S4, 5, 8), [w for w in three if w not in q_text(S4, 5, 8)][0])

# 6 正しい文・誤った文：文ごとの正誤から、組み合わせを決める
true46 = {
    '聖徳太子は、冠位十二階や十七条の憲法を定めた。': True, '中大兄皇子と中臣鎌足は、蘇我氏をたおして、大化の改新を始めた。': True,
    '平清盛は、武士として初めて太政大臣になった。': True, '源頼朝の死後、足利氏が代々執権となって、幕府の政治を行った。': False,   # 執権は北条氏
    '織田信長は、関ヶ原の戦いに勝って、全国をほぼ統一した。': False, '豊臣秀吉は、検地や刀狩を行って、武士と百姓の身分を区別した。': True,
    '江戸幕府は、鎖国のあいだ、長崎で、中国と朝鮮だけと貿易をした。': False, '徳川家康は、1600年に壇ノ浦の戦いに勝って、将軍になった。': False,
    '日本国憲法は、1946年11月3日に公布された。': True, '参議院議員の任期は4年で、解散がある。': 6 == 4,                 # 任期6年・解散なし
    '日清戦争のあと、日本は、ポーツマス条約を結んだ。': False, '日露戦争の講和条約で、日本は、賠償金を得られなかった。': True,
    '国会議員を選ぶ選挙で、投票できるのは、満18歳以上である。': 18 == 18, '税金を納めることは、国民の三つの義務の1つである。': True,
    '2026年10月現在、日本の世界遺産は、30件をこえている。': len(HERITAGE) > 30,
    '奈良県にある世界遺産は、2026年に登録された「飛鳥・藤原の宮都」だけである。': [h[0] for h in HERITAGE if '奈良県' in h[3]] == ['飛鳥・藤原の宮都'],
}
letter46 = {(True, True): 'ア', (True, False): 'イ', (False, True): 'ウ', (False, False): 'エ'}
for i in range(1, 9):
    a_, b_ = [l[2:] for l in q_text(S4, 6, i).split('\n') if l[:2] in ('A　', 'B　')]
    eq(f'社4-6({i}) 正誤', ans(S4, 6, i), letter46[(true46[a_], true46[b_])])
assert len([h for h in HERITAGE if '奈良県' in h[3]]) == 4

# 7 2026年のできごと
b47 = blanks_of(S4.SETS[6]['items'])
fact47 = {'第51回': '衆議院', '特別国会で、': '高市', '7月28日、': '熊本', '8月13日から14日、': '千葉', '約': '67'}
eq('社4-7(1) 空らん', ans(S4, 7, 1), [by_suffix(fact47, b47[k]) for k in 'アイウエオ'])
eq('社4-7(2) 3分の2', ans(S4, 7, 2), f'{465 * 2 // 3}人')
assert 316 > 465 * 2 // 3
eq('社4-7(4) 年数', ans(S4, 7, 4), f'{2026 - 2016}年前')
n47 = [int(x) for x in re.findall(r'約(\d+)万人', q_text(S4, 7, 7))]
eq('社4-7(7) 出生数の差', ans(S4, 7, 7), f'{n47[0] - n47[1]}万人')

# 8 地震：表から読み取る
rows48 = S4.SETS[7]['table']['rows'][1:]
name48 = {2011: '東日本', 2024: '能登'}
eq('社4-8(1) 空らん', ans(S4, 8, 1), [name48[int(r[0])] for r in rows48 if '〔' in r[1]])
eq('社4-8(2) 最大のマグニチュード', ans(S4, 8, 2), f'{max(rows48, key=lambda r: float(r[2]))[0]}年')
eq('社4-8(3) エネルギー', ans(S4, 8, 3), f'約{round(32 ** round(9.0 - 7.0), -2)}倍')
eq('社4-8(7) 自助・共助・公助', ans(S4, 8, 7), [{'自分や家族で守る': '自助', '地域の人どうしで助け合う': '共助', '国や自治体が行う': '公助'}[k] for k in S4.SETS[7]['qs'][6]['labels']])

# 9 年中行事
feat49 = {'節分': ['2月3日'], '桃': ['3月3日'], '七夕': ['7月7日'], 'ススキ': ['旧暦8月15日'], 'ゆず': ['12月22日'], '年越しそば': ['12月31日']}
b49 = {blank_of(t): find(feat49, t) for _, t in S4.SETS[8]['items']}
eq('社4-9(1) 空らん', ans(S4, 9, 1), [b49[k] for k in 'アイウエオカ'])
city49 = {'ねぶた祭': '青森市', '竿燈まつり': '秋田市', '阿波おどり': '徳島市', '博多祇園山笠': '福岡市'}
cap = lambda p: CAPITAL.get(p, p[:-1] + '市')
eq('社4-9(7) まつりの県', ans(S4, 9, 7), [[p for p in PREF if cap(p) == city49[k]][0] for k in S4.SETS[8]['qs'][6]['labels']])

# 10 元号・西暦・世紀・時代
gengo = {'明治': 1868, '大正': 1912, '昭和': 1926, '平成': 1989, '令和': 2019}
eq('社4-10(1) 元年', ans(S4, 10, 1), [f'{gengo[k]}年' for k in S4.SETS[9]['qs'][0]['labels']])
eq('社4-10(2) 平成何年', ans(S4, 10, 2), f'平成{2000 - gengo["平成"] + 1}年')
eq('社4-10(3) 昭和何年まで', ans(S4, 10, 3), f'昭和{gengo["平成"] - gengo["昭和"] + 1}年')              # 1989年1月7日が昭和64年の最後の日
century = lambda y: (y - 1) // 100 + 1
eq('社4-10(4) 世紀', ans(S4, 10, 4), [f'{century(int(k[:-1]))}世紀' for k in S4.SETS[9]['qs'][3]['labels']])
eq('社4-10(5) 時代', ans(S4, 10, 5), [era_of(int(k[:-1])) + '時代' for k in S4.SETS[9]['qs'][4]['labels']])
eq('社4-10(6) 年数', ans(S4, 10, 6), f'{2026 - gengo["明治"]}年')
eq('社4-10(8) 江戸幕府の世紀', ans(S4, 10, 8), f'{century(1603)}世紀')

# ---------------- 社会・大問5 ----------------
# 1 教育を受ける権利・税金・ユニバーサルデザイン
b61 = blanks_of(S5.SETS[0]['items'])
fact61 = {'すべて国民は、': '法律', 'ひとしく': '教育', '子どもに': '普通', '中学校をあわせた': str(6 + 3), '国民から集めた': '税金', 'デザインを、': 'ユニバーサル'}
eq('社5-1(1) 空らん', ans(S5, 1, 1), [by_suffix(fact61, b61[k]) for k in 'アイウエオカ'])
eq('社5-1(2) 三つの義務', [k in ans(S5, 1, 2) for k in ('普通教育', '勤労', '納税')], [True] * 3)
tax = {'所得税': ('国', '直接'), '住民税': ('地方', '直接'), '消費税': ('国', '間接'), '固定資産税': ('地方', '直接'), '法人税': ('国', '直接')}
eq('社5-1(4) 国税', ans(S5, 1, 4), join(k for k, v in choices(q_text(S5, 1, 4)).items() if tax[v][0] == '国'))
ud51 = {'ノンステップバス': True, '絵文字（ピクトグラム）の案内表示': True, '幅のせまい階段': False, '高い位置だけにあるボタン': False}
eq('社5-1(6) ユニバーサルデザイン', ans(S5, 1, 6), join(k for k, v in choices(q_text(S5, 1, 6)).items() if ud51[v]))
eq('社5-1(7) 教科書無償から', ans(S5, 1, 7), f'{2026 - int(re.search(r"(\d{4})年からです", q_text(S5, 1, 7)).group(1))}年')

# 2 国際連合
b62 = blanks_of(S5.SETS[1]['items'])
P5 = ['アメリカ', 'ロシア', '中国', 'イギリス', 'フランス']
said62 = [c for c in P5 if c in S5.SETS[1]['items'][2][1]]
assert len(said62) == 4
fact62 = {'世界の': '平和', 'アメリカ合衆国の': 'ニューヨーク', '加盟国は、': '193', 'イギリスと、': [c for c in P5 if c not in said62][0],
          '採択された': '持続可能な開発目標', '子どもの権利を守る': 'ユニセフ', '交流をすすめる': 'ユネスコ'}
eq('社5-2(1) 空らん', ans(S5, 2, 1), [by_suffix(fact62, b62[k]) for k in 'アイウエオカキ'])
eq('社5-2(2) 加盟から', ans(S5, 2, 2), f'{2026 - 1956}年')
eq('社5-2(3) SDGsの期間', ans(S5, 2, 3), f'{2030 - 2015}年間')
org62 = {'WHO': '健康', 'FAO': '食料・農業', 'UNESCO': '教育・科学・文化'}
eq('社5-2(5) 健康の機関', ans(S5, 2, 5), [k for k, v in choices(q_text(S5, 2, 5)).items() if org62[v] == '健康'][0])

# 3 2025年のできごと
b63 = blanks_of(S5.SETS[2]['items'])
fact63 = {'大阪・関西': '万博', '7月20日、': '参議院', '10月、': '高市', '坂口志文さんが': '生理', 'を調査期日として、': '国勢', '終わってから、': str(2025 - 1945)}
eq('社5-3(1) 空らん', ans(S5, 3, 1), [by_suffix(fact63, b63[k]) for k in 'アイウエオカ'])
eq('社5-3(2) 万博から', ans(S5, 3, 2), f'{2025 - 1970}年')
seats63 = int(re.search(r'定数は(\d+)人', q_text(S5, 3, 3)).group(1))
eq('社5-3(3) 過半数', ans(S5, 3, 3), f'{seats63 // 2 + 1}人')
eq('社5-3(4) 任期と改選', ans(S5, 3, 4), [f'{6}年', f'{6 // 2}年ごとに半数'])
nobel25 = {'文学賞': False, '化学賞': True, '物理学賞': False, '生理学・医学賞': True}                # 日本人の受賞は坂口志文さん・北川進さん
eq('社5-3(6) ノーベル賞', ans(S5, 3, 6), join(k for k, v in choices(q_text(S5, 3, 6)).items() if nobel25[v]))
assert (2025 - 1920) % 5 == 0
eq('社5-3(7) 国勢調査', ans(S5, 3, 7), ['5年ごと', f'{2025 + 5}年'])

# 4 国のお金と社会保障
b64 = blanks_of(S5.SETS[3]['items'])
fact64 = {'国の唯一の': '立法', '使い道の計画を': '予算', '担当する省は、': '財務', '足りない分を、': '国債', 'くらしを支える制度を、': '社会保障'}
eq('社5-4(1) 空らん', ans(S5, 4, 1), [by_suffix(fact64, b64[k]) for k in 'アイウエオ'])
eq('社5-4(3) 直接税・間接税', ans(S5, 4, 3), [tax[k][1] + '税' for k in S5.SETS[3]['qs'][2]['labels']])
n64 = [int(x) for x in re.findall(r'(\d+)兆円', q_text(S5, 4, 6))]
eq('社5-4(6) 割合', ans(S5, 4, 6), f'{round(n64[1] / n64[0] * 100)}%')
fund64 = {'公立学校の運営': True, '民間の映画館の入場料': False, '道路や橋の整備': True, 'コンビニの商品代金': False}
eq('社5-4(8) 税金でまかなう', ans(S5, 4, 8), join(k for k, v in choices(q_text(S5, 4, 8)).items() if fund64[v]))

# 5 歴史：手がかり → 人物・語句、年代順
feat65 = {'北条時宗': ['元が2度'], '板垣': ['自由民権運動'], '鑑真': ['唐招提寺'], '参勤交代': ['徳川家光'], '中臣鎌足': ['大化の改新'],
          '勘合': ['足利義満'], '摂関政治': ['藤原氏'], 'ペリー': ['浦賀']}
b65 = {blank_of(t): find(feat65, t) for _, t in S5.SETS[4]['items']}
eq('社5-5(1) 空らん', ans(S5, 5, 1), [b65[k] for k in 'アイウエオカキク'])
year65 = {'元が2度': 1274, '自由民権運動': 1874, '唐招提寺': 759, '徳川家光': 1635, '大化の改新': 645, '足利義満': 1404, '藤原氏': 1016, '浦賀': 1853}
yr65 = {lab: [y for k, y in year65.items() if k in t][0] for lab, t in S5.SETS[4]['items']}
eq('社5-5(2) 年代順', ans(S5, 5, 2), '→'.join(sorted(yr65, key=yr65.get)))
port65 = {'神奈川': '神奈川県', '長崎': '長崎県', '新潟': '新潟県', '兵庫': '兵庫県', '函館': '北海道'}
eq('社5-5(4) 北海道の港', ans(S5, 5, 4), [k for k, v in port65.items() if v == '北海道'][0])
temple65 = {'法隆寺': '聖徳太子', '唐招提寺': '鑑真', '薬師寺': '天武天皇', '興福寺': '藤原氏'}
eq('社5-5(3) 鑑真の寺', ans(S5, 5, 3), [k for k, v in choices(q_text(S5, 5, 3)).items() if temple65[v] == '鑑真'][0])

# 6 年表
rows66 = {int(r[0]): r[1] for r in S5.SETS[5]['table']['rows'][1:]}
fact66 = {239: '卑弥呼', 710: '平城', 1185: '壇ノ浦', 1543: '種子', 1600: '関ヶ原', 1905: 'ポーツマス', 2011: '東日本'}
eq('社5-6(1) 空らん', ans(S5, 6, 1), [fact66[y] for y, t in rows66.items() if '〔' in t])
ev66 = {'平安京への遷都': 794, '元寇（文永の役）': 1274, '江戸幕府が開かれる': 1603, '明治維新': 1868}
between = lambda y: f'{max(k for k in rows66 if k < y)}年と{min(k for k in rows66 if k > y)}年の間'
eq('社5-6(2) 年表の間', ans(S5, 6, 2), [between(ev66[k]) for k in S5.SETS[5]['qs'][1]['labels']])
oly66 = {'ロンドン': 2012, 'パリ': 2024, 'リオデジャネイロ': 2016, '東京': 2021}                       # 東京大会は1年延期され2021年開催
ch66 = choices(q_text(S5, 6, 3))
eq('社5-6(3) オリンピック順', ans(S5, 6, 3), '→'.join(sorted(ch66, key=lambda k: oly66[ch66[k]])))
eq('社5-6(4) 年数', ans(S5, 6, 4), f'{2025 - 1964}年')
assert 1853 + 1 == 1854 and '1854' in q_text(S5, 6, 6)

# 7 発電：表から読み取る
rows67 = {r[0]: r for r in S5.SETS[6]['table']['rows'][1:]}
eq('社5-7(1) 燃料を使う発電', ans(S5, 7, 1), join(k for k, r in rows67.items() if re.search('石油|石炭|天然ガス|ウラン', r[1])))
eq('社5-7(2) 二酸化炭素を多く出す', ans(S5, 7, 2), [k for k, r in rows67.items() if r[2] == '多く出る'][0])
eq('社5-7(6) 2050年まで', ans(S5, 7, 6)[1], f'{2050 - 2026}年後')

# 8 情報
feat68 = {'メディア': ['情報を伝える手段'], 'デジタル': ['アナログ放送'], '個人情報': ['個人を特定'], '著作': ['作品をつくった人'], 'マイナンバー': ['番号をつけ']}
b68 = {blank_of(t): find(feat68, t) for _, t in S5.SETS[7]['items']}
eq('社5-8(1) 空らん', ans(S5, 8, 1), [b68[k] for k in 'アイウエオ'])
eq('社5-8(2) テレビ放送から', ans(S5, 8, 2), f'{2026 - 1953}年')
eq('社5-8(3) ラジオからテレビ', ans(S5, 8, 3), f'{1953 - 1925}年後')
ok68 = {'友だちの写真を、許可なくインターネットにのせる': False, '宿題を、自分の言葉でまとめる': True, '出典を書いて、本の一部を引用する': True}
eq('社5-8(5) してはいけない', ans(S5, 8, 5), [k for k, v in choices(q_text(S5, 8, 5)).items() if not ok68[v]][0])
pw68 = {'誕生日': 1, '名前と同じ文字': 1, '長くて、ほかの人が当てにくい文字の組み合わせ': 20}            # 当てにくさの目安（字数）
eq('社5-8(8) パスワード', ans(S5, 8, 8), max(choices(q_text(S5, 8, 8)).items(), key=lambda kv: pw68[kv[1]])[0])

# 9 地方自治
b69 = blanks_of(S5.SETS[8]['items'])
fact69 = {'天理市は': '奈良', '市長と': '市議会', '市長や知事を': '首長', '任期は': '4', '定めるものを、': '条例', '税金を': '地方税', '国から': '地方交付税'}
eq('社5-9(1) 空らん', ans(S5, 9, 1), [by_suffix(fact69, b69[k]) for k in 'アイウエオカキ'])
age69 = {'市長': 25, '都道府県知事': 30, '市議会議員': 25}
eq('社5-9(2) 被選挙権', ans(S5, 9, 2), [f'満{age69[k]}歳以上' for k in S5.SETS[8]['qs'][1]['labels']])
eq('社5-9(3) 市町村の数', ans(S5, 9, 3), str(sum(int(x) for x in re.findall(r'(\d+)の', q_text(S5, 9, 3))) - 0))
q69 = q_text(S5, 9, 5)
eq('社5-9(5) 署名', ans(S5, 9, 5), f'{int(re.search(r"(\d+)万人", q69).group(1)) * 10000 // int(re.search(r"(\d+)分の1", q69).group(1))}人')
eq('社5-9(7) 県庁所在地', ans(S5, 9, 7), CAPITAL.get('奈良県', '奈良県'[:-1] + '市'))

# 10 法律ができるまでと裁判所
b610 = blanks_of(S5.SETS[9]['items'])
fact610 = {'参議院の': '委員会', '話し合われたあと、': '本会議', '法律になり、': '天皇', '内閣は、': '閣議', '最高裁判所と、': '下級', '制度を、': '三審'}
eq('社5-10(1) 空らん', ans(S5, 10, 1), [by_suffix(fact610, b610[k]) for k in 'アイウエオカ'])
duty610 = {'予算の議決': '国会', '法律が憲法に違反していないかの審査': '裁判所', '条約の承認': '国会', '内閣総理大臣の指名': '国会'}
eq('社5-10(3) 国会の仕事', ans(S5, 10, 3), join(k for k, v in choices(q_text(S5, 10, 3)).items() if duty610[v] == '国会'))
eq('社5-10(4) 過半数', ans(S5, 10, 4), f'{int(re.search(r"国務大臣が(\d+)人", q_text(S5, 10, 4)).group(1)) // 2 + 1}人')
koto610 = {'札幌': '札幌高等裁判所', '仙台': '仙台高等裁判所', '東京': '東京高等裁判所', '名古屋': '名古屋高等裁判所', '大阪': '大阪高等裁判所',
           '広島': '広島高等裁判所', '高松': '高松高等裁判所', '福岡': '福岡高等裁判所'}
eq('社5-10(5) 高等裁判所の数', ans(S5, 10, 5), ['1か所', f'{len(koto610)}か所'])
area610 = {'大阪高等裁判所': {'大阪', '京都', '兵庫', '奈良', '滋賀', '和歌山'}}
eq('社5-10(6) 奈良の高等裁判所', ans(S5, 10, 6), [k for k, v in area610.items() if '奈良' in v][0])

# ---------------- 算数・大問4 ----------------
# 1 円グラフ：合計・割合
pie = M4.SETS[0]['fig']['args']
tot41 = pie['total']
known41 = sum(v for _, v in pie['data'] if v is not None)
eq('算4-1(1) その他の人数', ans(M4, 1, 1), f'{tot41 - known41}人')
vals41 = {n: v for n, v in pie['data'] if v is not None}
pct41 = int(re.search(r'(\d+)%', q_text(M4, 1, 2)).group(1))
need41 = tot41 * pct41 // 100 - vals41['水泳部']
eq('算4-1(2) 20%になる部活動', ans(M4, 1, 2), [n for n, v in vals41.items() if v == need41 and n != '水泳部'][0])
eq('算4-1(3) バスケットボール部の割合', ans(M4, 1, 3), f'{vals41["バスケットボール部"] / tot41 * 100:g}%')
assert str(tot41) in M4.SETS[0]['lead']

# 2 図形の性質：頂点の座標から、辺・角・対称性を調べる
def sides_equal(poly):
    ls = [math.dist(poly[i], poly[(i + 1) % len(poly)]) for i in range(len(poly))]
    return max(ls) - min(ls) < 1e-9
def angles_equal(poly):
    n = len(poly)
    angs = []
    for i in range(n):
        a_, b_, c_ = poly[i - 1], poly[i], poly[(i + 1) % n]
        v1, v2 = (a_[0] - b_[0], a_[1] - b_[1]), (c_[0] - b_[0], c_[1] - b_[1])
        angs.append(math.acos((v1[0] * v2[0] + v1[1] * v2[1]) / (math.hypot(*v1) * math.hypot(*v2))))
    return max(angs) - min(angs) < 1e-9
def vset(pts):
    return {(round(x, 6), round(y, 6)) for x, y in pts}
def point_sym(poly):
    mx, my = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    return vset(poly) == vset([(2 * mx - x, 2 * my - y) for x, y in poly])
def axes_count(poly):
    mx, my = sum(p[0] for p in poly) / len(poly), sum(p[1] for p in poly) / len(poly)
    cands = [math.atan2(y - my, x - mx) % math.pi for x, y in poly]
    cands += [math.atan2(p2[0] - p1[0], -(p2[1] - p1[1])) % math.pi for p1, p2 in itertools.combinations(poly, 2)]
    good = set()
    for th in cands:
        cx_, sx_ = math.cos(2 * th), math.sin(2 * th)
        ref = [(mx + (x - mx) * cx_ + (y - my) * sx_, my + (x - mx) * sx_ - (y - my) * cx_) for x, y in poly]
        if vset(ref) == vset(poly):
            good.add(round(th, 4) % round(math.pi, 4))            # 軸の向き（0とπは同じ向き）
    return len(good)
names42 = M4.SETS[1]['fig']['args']['shapes']
lab42 = dict(zip('アイウエオカキク', names42))
sel42 = lambda f: join(k for k, nm in lab42.items() if f(SHAPES[nm]))
eq('算4-2(1) 辺がすべて等しい', ans(M4, 2, 1), sel42(sides_equal))
eq('算4-2(2) 角がすべて等しい', ans(M4, 2, 2), sel42(angles_equal))
eq('算4-2(3) 点対称', ans(M4, 2, 3), sel42(point_sym))
eq('算4-2(4) 対称の軸が2本', ans(M4, 2, 4), sel42(lambda p: axes_count(p) == 2))

# 3 仕事算：人・時間で数える
total43 = 12 * 5 * 9
assert '12人' in M4.SETS[2]['lead'] and '9日間' in M4.SETS[2]['lead']
eq('算4-3(1) 人数', ans(M4, 3, 1), f'{Fraction(total43, 6 * 5):g}人')
rest43 = total43 - 8 * 5 * 3
eq('算4-3(2) 残りの日数', ans(M4, 3, 2), f'{Fraction(rest43, 10 * 6):g}日')
first43 = 12 * 5 * 4
need43 = Fraction(total43 - first43, 6 - 4) / 5                                     # 後半の人数
eq('算4-3(3) ふやした人数', ans(M4, 3, 3), f'{need43 - 12:g}人')

# 4 文字の対称：線分の集まりを、折る・回す
def seg_set(segs, f):
    return {frozenset({(round(f(a_)[0], 6), round(f(a_)[1], 6)), (round(f(b_)[0], 6), round(f(b_)[1], 6))}) for a_, b_ in segs}
letters44 = {
    'F': [((0, 0), (0, 2)), ((0, 2), (1.5, 2)), ((0, 1), (1, 1))],
    'H': [((0, 0), (0, 2)), ((2, 0), (2, 2)), ((0, 1), (2, 1))],
    'M': [((0, 0), (0, 2)), ((0, 2), (1, .8)), ((1, .8), (2, 2)), ((2, 2), (2, 0))],
    'S': [((2, 1.9), (.5, 1.9)), ((.5, 1.9), (.5, 1)), ((.5, 1), (1.5, 1)), ((1.5, 1), (1.5, .1)), ((1.5, .1), (0, .1))],
    'T': [((0, 2), (2, 2)), ((1, 2), (1, 0))],
    'V': [((0, 2), (1, 0)), ((1, 0), (2, 2))],
    'X': [((0, 0), (2, 2)), ((0, 2), (2, 0))],
    'Z': [((0, 2), (2, 2)), ((2, 2), (0, 0)), ((0, 0), (2, 0))],
}
ident = lambda p_: p_
mirrors = [lambda p_: (2 - p_[0], p_[1]), lambda p_: (p_[0], 2 - p_[1]), lambda p_: (p_[1], p_[0]), lambda p_: (2 - p_[1], 2 - p_[0])]
line_sym = lambda segs: any(seg_set(segs, m) == seg_set(segs, ident) for m in mirrors)
pt_sym = lambda segs: seg_set(segs, lambda p_: (2 - p_[0], 2 - p_[1])) == seg_set(segs, ident)
assert M4.SETS[3]['fig']['args']['s'] == ''.join(sorted(letters44, key=lambda k: 'FHMSTVXZ'.index(k)))
pick44 = lambda f: join(k for k in M4.SETS[3]['fig']['args']['s'] if f(letters44[k]))
eq('算4-4(1) 線対称', ans(M4, 4, 1), pick44(line_sym))
eq('算4-4(2) 点対称', ans(M4, 4, 2), pick44(pt_sym))
eq('算4-4(3) どちらも', ans(M4, 4, 3), pick44(lambda sg: line_sym(sg) and pt_sym(sg)))
eq('算4-4(4) どちらでもない', ans(M4, 4, 4), pick44(lambda sg: not line_sym(sg) and not pt_sym(sg)))

# 5 斜線部分の面積：多角形はくつ下の公式、円は円周率3.14。格子点を数えた値（円周率は本物）と、近いことも確かめる
def shoelace(poly):
    return abs(sum(poly[i][0] * poly[(i + 1) % len(poly)][1] - poly[(i + 1) % len(poly)][0] * poly[i][1] for i in range(len(poly)))) / 2
def grid_area(inside, x0, x1, y0, y1, n=800):
    dx, dy = (x1 - x0) / n, (y1 - y0) / n
    cnt = sum(1 for i in range(n) for j in range(n) if inside(x0 + (i + .5) * dx, y0 + (j + .5) * dy))
    return cnt * dx * dy
sp5 = {k: v for k, v in M4.SETS[4]['fig']['args']['specs']}
a_ = sp5['trap']
area1 = shoelace([(0, 0), (a_['w'], 0), (a_['w'], a_['h']), (a_['cut'], a_['h'])])
cut_line = lambda x, y: x >= a_['cut'] * y / a_['h']
assert abs(grid_area(lambda x, y: cut_line(x, y), 0, a_['w'], 0, a_['h'], 400) - area1) < .2
s5 = sp5['lens']['s']
area2 = 2 * (3.14 * s5 * s5 / 4) - s5 * s5
assert abs(grid_area(lambda x, y: x * x + y * y <= s5 * s5 and (x - s5) ** 2 + (y - s5) ** 2 <= s5 * s5, 0, s5, 0, s5, 500) - area2) < .2
d5 = sp5['segment']['d']
r5 = d5 / 2
area3 = 3.14 * r5 * r5 / 2 - d5 * r5 / 2
assert abs(grid_area(lambda x, y: x * x + y * y <= r5 * r5 and y > r5 - abs(x), -r5, r5, 0, r5, 500) - area3) < .2   # 三角形の外がわの、半円の部分
f5 = lambda v: f'{round(v, 2):g}cm²'
eq('算4-5(1) 台形', ans(M4, 5, 1), f5(area1))
eq('算4-5(2) 葉の形', ans(M4, 5, 2), f5(area2))
eq('算4-5(3) 半円−三角形', ans(M4, 5, 3), f5(area3))

# 6 水そう：全体を1として、1分あたりの量
tA, tAB = [int(x) for x in re.findall(r'(\d+)分かかり', M4.SETS[5]['lead'])]
rA = Fraction(1, tA)
rB = Fraction(1, tAB) - rA
eq('算4-6(1) B管だけ', ans(M4, 6, 1), f'{1 / rB:g}分')
a10, b6 = [int(x) for x in re.findall(r'(\d+)分間', q_text(M4, 6, 2))]
left = 1 - a10 * rA - b6 * rB
t62 = left / (rA + rB)
eq('算4-6(2) 途中でかえる', ans(M4, 6, 2), f'{int(t62)}分{int((t62 - int(t62)) * 60)}秒後')
a5 = int(re.search(r'(\d+)分後から', q_text(M4, 6, 3)).group(1))
eq('算4-6(3) 5分後からB管も', ans(M4, 6, 3), f'{a5 + (1 - a5 * rA) / (rA + rB):g}分後')

# 7 比：所持金の比。数は問題文から読み取り、整数の範囲をしらみつぶしに調べる
ane47, imo47 = [int(x) for x in re.findall(r'(\d+)円', M4.SETS[6]['lead'])]
ratio47 = lambda a_, b_: f'{a_ // math.gcd(a_, b_)}：{b_ // math.gcd(a_, b_)}'
eq('算4-7(1) 姉：妹', ans(M4, 7, 1), ratio47(ane47, imo47))
give47 = int(re.search(r'(\d+)円を妹', q_text(M4, 7, 2)).group(1))
eq('算4-7(2) わたしたあとの比', ans(M4, 7, 2), ratio47(ane47 - give47, imo47 + give47))
mult47 = int(re.search(r'妹の(\d)倍', q_text(M4, 7, 3)).group(1))
sol473 = [x_ for x_ in range(0, imo47 + 1) if ane47 - mult47 * x_ == imo47 - x_]               # 妹がx円、姉がmult倍を出して、残りが等しい
assert len(sol473) == 1
eq('算4-7(3) プレゼントの代金', ans(M4, 7, 3), f'{(1 + mult47) * sol473[0]}円')
r1_, r2_ = [int(x) for x in re.search(r'比は(\d)：(\d)になりました', q_text(M4, 7, 4)).groups()]
sol474 = [x_ for x_ in range(0, imo47) if (ane47 - x_) * r2_ == (imo47 - x_) * r1_]            # 同じ金額x円を使ったあとの残りの比
assert len(sol474) == 1
eq('算4-7(4) おかしの代金', ans(M4, 7, 4), f'{sol474[0]}円')

# 8 斜線部分の面積（正方形・半円）
sp8 = {k: v for k, v in M4.SETS[7]['fig']['args']['specs']}
s81 = sp8['trisect']['s']
t81 = s81 / 3
rect81 = [(0, 2 * t81), (t81, s81), (s81, t81), (2 * t81, 0)]
assert angles_equal(rect81) and not sides_equal(rect81)                                       # 長方形になっている
corner81 = [[(0, 2 * t81), (0, s81), (t81, s81)], [(t81, s81), (s81, s81), (s81, t81)], [(s81, t81), (s81, 0), (2 * t81, 0)], [(2 * t81, 0), (0, 0), (0, 2 * t81)]]
assert abs(s81 * s81 - sum(shoelace(t_) for t_ in corner81) - shoelace(rect81)) < 1e-9          # 正方形＝まわりの4つの三角形＋長方形
f8 = lambda v: f'{round(v, 2):g}cm²'
eq('算4-8(1) 長方形', ans(M4, 8, 1), f8(shoelace(rect81)))
s82 = sp8['twosemi']['s']
r82 = s82 / 2
in1 = lambda x, y: x >= 0 and x * x + (y - r82) ** 2 <= r82 * r82                              # 左の辺が直径の半円
in2 = lambda x, y: y >= 0 and (x - r82) ** 2 + y * y <= r82 * r82                              # 下の辺が直径の半円
lens82 = 2 * (3.14 * r82 * r82 / 4) - r82 * r82
assert abs(grid_area(lambda x, y: in1(x, y) and in2(x, y), 0, s82, 0, s82, 500) - lens82) < .2
out82 = s82 * s82 - (2 * (3.14 * r82 * r82 / 2) - lens82)
assert abs(grid_area(lambda x, y: not in1(x, y) and not in2(x, y), 0, s82, 0, s82, 500) - out82) < .2
eq('算4-8(2) 半円の重なり', ans(M4, 8, 2), f8(lens82))
eq('算4-8(3) どちらにもふくまれない部分', ans(M4, 8, 3), f8(out82))

# 9 立体と面積
sp9 = {k: v for k, v in M4.SETS[8]['fig']['args']['specs']}
w91, h91 = sp9['views']['w'], sp9['views']['h']
r91 = w91 / 2
base91 = 3.14 * r91 * r91
assert abs(grid_area(lambda x, y: x * x + y * y <= r91 * r91, -r91, r91, -r91, r91, 500) - base91) < .1
eq('算4-9(1) 円柱の名前と体積', ans(M4, 9, 1), ['円柱', f'{round(base91 * h91, 2):g}cm³'])
circ91 = 3600 * 2 * r91 * math.sin(math.pi / 3600)                                              # 円周を、正3600角形の周でたしかめる
assert abs(circ91 - 3.14 * w91) < .02
eq('算4-9(2) 表面積', ans(M4, 9, 2), f8(2 * base91 + 3.14 * w91 * h91))
d92 = sp9['semitri']['d']
eq('算4-9(3) AB', ans(M4, 9, 3), f'{round(3.14 * d92 / 4, 2):g}cm')                           # 半円＝三角形ABC（円周率3.14）
ab92 = float(re.search(r'([\d.]+)', ans(M4, 9, 3)).group(1))
in_semi92 = lambda x, y: y >= 0 and (x - d92 / 2) ** 2 + y * y <= (d92 / 2) ** 2
in_tri92 = lambda x, y: x >= 0 and y >= 0 and y <= ab92 * (1 - x / d92)
area_a92 = grid_area(lambda x, y: in_semi92(x, y) and not in_tri92(x, y), 0, d92, 0, ab92, 700)
area_i92 = grid_area(lambda x, y: in_tri92(x, y) and not in_semi92(x, y), 0, d92, 0, ab92, 700)
assert abs(area_a92 - area_i92) < .1 and area_a92 > 1                                           # この長さのとき、格子点の数え上げでも、ア＝イ
ad93, bc93, ae93 = sp9['trap3']['ad'], sp9['trap3']['bc'], sp9['trap3']['ae']
for hh93 in (3, 8, 11):                                                                         # 高さによらず、3つの面積が等しい
    A_, D_, B_, C_ = ((bc93 - ad93) / 2, hh93), ((bc93 - ad93) / 2 + ad93, hh93), (0, 0), (bc93, 0)
    E_, F_ = ((bc93 - ad93) / 2 + ae93, hh93), (ae93, 0)
    ar93 = [shoelace([A_, B_, E_]), shoelace([B_, E_, F_]), shoelace([E_, F_, C_, D_])]
    assert max(ar93) - min(ar93) < 1e-9 and abs(sum(ar93) - shoelace([A_, B_, C_, D_])) < 1e-9
eq('算4-9(4) FC', ans(M4, 9, 4), f'{bc93 - ae93:g}cm')

# 10 立体の体積
sp10 = {k: v for k, v in M4.SETS[9]['fig']['args']['specs']}
nb = sp10['notchbox']
cells = sum(1 for i in range(nb['l']) for j in range(nb['w']) for k in range(nb['h']) if not (i >= nb['l'] - nb['n'] and j < nb['n'] and k >= nb['h'] - nb['n']))
assert f'{nb["n"]}cm' in q_text(M4, 10, 1)
eq('算4-10(1) 直方体から立方体', ans(M4, 10, 1), f'{cells}cm³')
hs = sp10['house']
house10 = [(0, 0), (hs['w'], 0), (hs['w'], hs['wall']), (hs['w'] / 2, hs['wall'] + hs['roof']), (0, hs['wall'])]
eq('算4-10(2) 家の形の柱', ans(M4, 10, 2), f'{shoelace(house10) * hs["len"]:g}cm³')
sc10 = sp10['sector']
r10, hh10 = sc10['r'], sc10['hh']
assert f'高さは{hh10}cm' in M4.SETS[9]['lead']
quarter10 = 3.14 * r10 * r10 / 4
assert abs(grid_area(lambda x, y: x * x + y * y <= r10 * r10, 0, r10, 0, r10, 800) * hh10 - quarter10 * hh10) < .5
eq('算4-10(3) 円柱の4分の1', ans(M4, 10, 3), f'{round(quarter10 * hh10, 2):g}cm³')
seg10 = quarter10 - shoelace([(0, 0), (r10, 0), (0, r10)])
assert abs(grid_area(lambda x, y: x * x + y * y <= r10 * r10 and x + y >= r10, 0, r10, 0, r10, 800) * hh10 - seg10 * hh10) < .5
eq('算4-10(4) 三角柱を切りとった立体', ans(M4, 10, 4), f'{round(seg10 * hh10, 2):g}cm³')

# ---------------- 国語（漢字・語句の検査に使う道具） ----------------
try:
    import pykakasi
except ImportError:
    sys.exit('pykakasi がありません。pip install -r requirements.txt を実行してください')
import kanji_grade as KG

_kks = pykakasi.kakasi()
KANA_FIX = {'築く': 'きずく', '潔く': 'いさぎよく'}                       # pykakasi の読みの誤り（JMdict で確認した正しい読み）
is_kanji = lambda ch: '一' <= ch <= '龥'
kata2h = lambda t_: ''.join(chr(ord(c_) - 0x60) if 'ァ' <= c_ <= 'ヶ' else c_ for c_ in t_)
RAD_NAME = {                                                              # 康熙字典の部首番号 → 部首名（本によってちがう呼び名もふくむ）
    9: {'にんべん'}, 18: {'りっとう'}, 19: {'ちから'}, 30: {'くち'}, 31: {'くにがまえ'}, 32: {'つちへん', 'つち'}, 38: {'おんなへん', 'おんな'},
    40: {'うかんむり'}, 53: {'まだれ'}, 60: {'ぎょうにんべん'}, 61: {'りっしんべん', 'こころ', 'したごころ'}, 64: {'てへん', 'て'}, 66: {'ぼくにょう', 'のぶん'},
    72: {'ひへん', 'にちへん', 'ひ'}, 75: {'きへん', 'き'}, 85: {'さんずい', 'みず'}, 86: {'れっか', 'れんが', 'ひ'}, 96: {'おうへん', 'たまへん'},
    104: {'やまいだれ'}, 113: {'しめすへん'}, 115: {'のぎへん'}, 116: {'あなかんむり'}, 118: {'たけかんむり'}, 120: {'いとへん'},
    140: {'くさかんむり'}, 145: {'ころもへん'}, 149: {'ごんべん'}, 154: {'かいへん'}, 157: {'あしへん'}, 159: {'くるまへん'}, 162: {'しんにょう', 'しんにゅう'},
    163: {'おおざと'}, 167: {'かねへん'}, 169: {'もんがまえ'}, 170: {'こざとへん'}, 181: {'おおがい'}, 184: {'しょくへん'},
}


def reading(w_):
    return KANA_FIX.get(w_) or ''.join(x_['hira'] for x_ in _kks.convert(w_))


def check_kanji_set(mod):
    """漢字の問題の答えを、読み（pykakasi）・学年配当（KANJIDIC2）・部首と画数（KANJIDIC2）から調べ直す。(問題数, 不一致の一覧) を返す。"""
    bad, n_ = [], 0
    for i_, st_ in enumerate(mod.SETS, 1):
        seen = set()
        for j_, q_ in enumerate(st_['qs'], 1):
            n_ += 1
            tag = f'{i_}-{j_}'
            m_, a_ = q_.get('meta'), q_['ans']
            if not m_:                                                    # 書き取り・読み・送りがなの答えは、セットの中で重ならない
                if a_ in seen:
                    bad.append((tag, '同じセットに、同じ答えがある'))
                seen.add(a_)
            if m_ and m_['t'] == 'P':
                hit = [k_ for k_, o_ in zip('アイウエ', m_['opts']) if set(o_) & set(m_['word'])]
                if hit != [a_]:
                    bad.append((tag, '同じ漢字をふくむ熟語が、ちょうど1つではない', hit, a_))
                if non_elem(''.join(m_['opts']) + m_['word']):
                    bad.append((tag, '小学校で習わない漢字', non_elem(''.join(m_['opts']) + m_['word'])))
                if q_['q'].count('{') != 1 or _t_(q_) != '' and not re.fullmatch(r'[ァ-ヶー]+', _t_(q_)):
                    bad.append((tag, '下線部がカタカナでない'))
            elif m_ and m_['t'] == 'B':
                r_, ex_r = KG.INFO[m_['kanji']][0], KG.INFO[m_['example']][0]
                if (r_ != ex_r or m_['name'] not in RAD_NAME.get(r_, set()) or a_ != f'{m_["name"]}　{m_["example"]}'
                        or any(KG.INFO.get(c_, (None,))[0] != r_ for c_ in m_['all'])):         # 解説にあげた漢字も、同じ部首
                    bad.append((tag, '部首', m_['kanji'], r_, ex_r, m_['name']))
            elif m_ and m_['t'] == 'S':
                if KG.INFO[m_['kanji']][1] != m_['n'] or a_ != f'{m_["n"]}画':
                    bad.append((tag, '画数', m_['kanji'], KG.INFO[m_['kanji']][1], m_['n']))
            else:
                t_ = _t_(q_)
                if re.fullmatch(r'[ァ-ヶー]+', t_):                      # 書き取り：答えの読みが、カタカナと同じ
                    if reading(a_) != kata2h(t_) or non_elem(a_):
                        bad.append((tag, '書き取り', t_, a_, reading(a_), non_elem(a_)))
                elif re.fullmatch(r'[ぁ-ん]+', t_):                        # 送りがな：答えの読みが、ひらがなと同じ
                    if reading(a_) != t_ or non_elem(a_):
                        bad.append((tag, '送りがな', t_, a_, reading(a_), non_elem(a_)))
                else:                                                     # 読み：漢字の読みが、答えと同じ
                    if reading(t_) != a_ or non_elem(t_):
                        bad.append((tag, '読み', t_, a_, reading(t_), non_elem(t_)))
            if not q_['ex'] or q_['ex'].endswith(('と書く。', '読む。')):
                bad.append((tag, '解説に一言がない'))
    return n_, bad


def _t_(q_):
    mm_ = re.search(r'\{(.+?)\}', q_['q'])
    return mm_.group(1) if mm_ else ''


non_elem = lambda t_: [ch_ for ch_ in t_ if is_kanji(ch_) and not KG.elementary(ch_)]

# ---------------- 国語・大問1（漢字） ----------------
n1_, bad1_ = check_kanji_set(K1)
eq(f'国1 漢字{n1_}問（読み・書き取り・送りがな・熟語の選択・部首・画数）の答え', bad1_, [])
assert all(len(st_['qs']) == 15 for st_ in K1.SETS)

# ---------------- 国語・大問2（語句・熟語） ----------------
# 作問のとき、JMdict（PyPIの jamdict-data）で、言葉の実在と意味を確かめた。ここでは、その表と、データが食いちがっていないかを調べる。
JUKUGO_TYPE = {                                                           # 熟語の組み立て（ア 似た意味／イ 反対の意味／ウ 修飾／エ 目的・対象／オ 主述／カ 打ち消し）
    '増減': 'イ', '洗顔': 'エ', '地震': 'オ', '白紙': 'ウ', '森林': 'ア', '開閉': 'イ', '強風': 'ウ', '登山': 'エ', '未来': 'カ', '学習': 'ア',
    '前後': 'イ', '新年': 'ウ', '乗車': 'エ', '頭痛': 'オ', '無理': 'カ', '身体': 'ア', '出入': 'イ', '作文': 'エ', '高低': 'イ', '登校': 'エ',
}
ANTONYM = {
    '増加': '減少', '成功': '失敗', '原因': '結果', '過去': '未来', '安全': '危険', '開会': '閉会', '勝利': '敗北', '質問': '回答', '拡大': '縮小',
    '前進': '後退', '集合': '解散', '直接': '間接', '理想': '現実', '長所': '短所',
}
YOJI = {
    '一石二鳥', '十人十色', '以心伝心', '自画自賛', '起承転結', '温故知新', '晴耕雨読', '絶体絶命', '大器晩成', '大同小異', '四苦八苦', '弱肉強食',
    '不言実行', '無我夢中', '一日千秋', '心機一転', '完全無欠', '意味深長', '空前絶後', '老若男女', '千差万別', '古今東西', '自給自足', '一心不乱',
    '適材適所', '半信半疑', '公明正大',
}
IDIOMS = {
    'ねこの手も借りたい', '耳を疑う', '顔が広い', '肩の荷が下りる', '青菜に塩', '目が高い', 'すずめのなみだ', '馬の耳に念仏', '口が重い', '胸をなでおろす',
    '首を長くして待つ', '足を引っぱる', '腹を割って話す', '鼻が高い', '手が足りない', '足が出る', '頭が下がる', '肩を並べる', '目を丸くする', '気が重い',
    '歯が立たない', '首をかしげる', '肩を落とす', '腕が鳴る', '胸を打つ', '耳が痛い', '骨が折れる', '急がば回れ', '七転び八起き', '灯台もと暗し',
    '百聞は一見にしかず', '手を焼く', '目を皿にする', '足を運ぶ', '頭をかかえる', '石の上にも三年', '花よりだんご', '雨降って地固まる',
    '立つ鳥あとをにごさず', 'まかぬ種は生えぬ', '後悔先に立たず', '良薬は口に苦し', '備えあればうれいなし', '住めば都', '笑う門には福来たる',
    'ころばぬ先のつえ', '足を洗う', '手を貸す', '気が長い',
}


def check_goku_set(mod):
    """語句・熟語の問題の答えを、表と、問題文・選択肢から調べ直す。(問題数, 不一致の一覧) を返す。"""
    bad, n_ = [], 0
    for i_, st_ in enumerate(mod.SETS, 1):
        for j_, q_ in enumerate(st_['qs'], 1):
            n_ += 1
            tag = f'{i_}-{j_}'
            m_, a_, qt_ = q_['meta'], q_['ans'], q_['q']
            t_ = m_['t']
            if t_ == 'J':
                if len(a_) != 2 or a_[1] != m_['hint'] or f'［{m_["hint"]}］' not in qt_ or non_elem(a_):
                    bad.append((tag, '意味から熟語', a_, m_['hint']))
            elif t_ == 'C':
                if JUKUGO_TYPE.get(m_['word']) != a_ or f'「{m_["word"]}」' not in qt_:
                    bad.append((tag, '熟語の組み立て', m_['word'], a_, JUKUGO_TYPE.get(m_['word'])))
            elif t_ == 'A':
                if ANTONYM.get(m_['word']) != a_ or ANTONYM.get(a_) not in (None, m_['word']) or non_elem(a_):
                    bad.append((tag, '対義語', m_['word'], a_))
            elif t_ == 'Y':
                if m_['word'] not in YOJI or m_['word'][m_['idx']] != a_ or '〔　〕' not in qt_ or non_elem(m_['word']):
                    bad.append((tag, '四字熟語', m_['word'], a_))
            elif t_ == 'I':
                if (m_['idiom'] not in IDIOMS or m_['pre'] + a_ + m_['post'] != m_['idiom'] or m_['pre'] + '〔　〕' + m_['post'] not in qt_
                        or non_elem(a_)):
                    bad.append((tag, '慣用句の空らん', m_['idiom'], a_))
            elif t_ in ('K', 'L', 'M'):
                opts_ = re.findall(r'(?:^|\n|　)([アイウエ]) ([^\n　]+)', qt_)
                if [k_ for k_, _ in opts_] != list('アイウエ') or a_ not in 'アイウエ' or len({o_ for _, o_ in opts_}) != 4:
                    bad.append((tag, '選択肢', opts_, a_))
                elif t_ == 'K' and (m_['idiom'] not in IDIOMS or dict(opts_)[a_] != m_['idiom']):
                    bad.append((tag, '慣用句の選択', m_['idiom'], a_))
                elif t_ == 'L' and (m_['idiom'] not in IDIOMS or f'「{m_["idiom"]}」' not in qt_):
                    bad.append((tag, '慣用句の意味の選択', m_['idiom'], a_))
            if not q_['ex']:
                bad.append((tag, '解説がない'))
    return n_, bad


# ---------------- 国語・大問2（語句・熟語） ----------------
n2_, bad2_ = check_goku_set(K2)
eq(f'国2 語句・熟語{n2_}問（意味から熟語・組み立て・対義語・四字熟語・慣用句）の答え', bad2_, [])

# ---------------- 国語・大問3（文法） ----------------
# 品詞・活用形・活用の種類・文節・「の」の用法・「ない／そうだ／らしい」の識別などは、形態素解析（janome）で調べ直す。
# 敬語・かなづかい・呼応・接続語のつながり方は、tools/ja_grammar.py の表と照合する。
n3_, bad3_ = ja_grammar.check_bunpo(K3)
eq(f'国3 文法{n3_}問（品詞・活用・文節・助詞・助動詞・敬語・修辞法・かなづかい・呼応）の答え', bad3_, [])

# ---------------- 国語・大問4（作文） ----------------
def kan2(n_):
    """整数（999まで）の漢数字。（データ側とは別に、ここでも書いた）"""
    d_ = '〇一二三四五六七八九'
    h_, r_ = divmod(n_, 100)
    t_, u_ = divmod(r_, 10)
    return ('' if h_ == 1 else d_[h_] if h_ else '') + ('百' if h_ else '') + ('' if t_ == 1 else d_[t_] if t_ else '') + ('十' if t_ else '') + (d_[u_] if u_ else '')


POLITE = ('です', 'ます', 'ました', 'でした', 'ません', 'でしょう', 'ましょう', 'ください')
FORBID = set('「」『』（）()ー…―') | set('0123456789') | set('abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ')


def walk(route_):
    """道案内の経路をたどり、通った交差点の名前の列と、ゴールの位置を返す。通れない道・地図の外に出たら、None。"""
    w_, h_ = route_['size']
    x_, y_ = route_['start']
    blocked_ = {frozenset(b_) for b_ in route_['blocked']}
    seen_ = [route_['labels'].get((x_, y_))]
    for d_, k_ in route_['moves']:
        dx_, dy_ = {'E': (1, 0), 'W': (-1, 0), 'N': (0, 1), 'S': (0, -1)}[d_]
        for _ in range(k_):
            nx_, ny_ = x_ + dx_, y_ + dy_
            if not (0 <= nx_ < w_ and 0 <= ny_ < h_) or frozenset({(x_, y_), (nx_, ny_)}) in blocked_:
                return None, None
            x_, y_ = nx_, ny_
            seen_.append(route_['labels'].get((x_, y_)))
    return [v_ for v_ in seen_ if v_], (x_, y_)


def check_essay(mod):
    """作文の例文を調べ直す。(セット数, 不一致の一覧) を返す。"""
    bad = []
    for i_, st_ in enumerate(mod.SETS, 1):
        q_ = st_['qs'][0]
        m_, ess_ = q_['meta'], st_['essay']
        sample = q_['ans']
        body = sample.replace('\n', '')
        lo_, hi_ = m_['lo'], m_['hi']
        if ess_['topic'] != q_['q']:
            bad.append((i_, 'お題が、問題文と合わない'))
        if ess_['conds'][0] != f'{kan2(lo_)}字以上、{kan2(hi_)}字以内で書くこと。':
            bad.append((i_, '字数の条件', ess_['conds'][0]))
        if not lo_ <= len(body) <= hi_:
            bad.append((i_, '例文の字数', len(body), lo_, hi_))
        paras_ = sample.split('\n')
        if len(paras_) != m_['paras'] or not all(paras_) or ('二段落' in ' '.join(ess_['conds'])) != (m_['paras'] == 2):
            bad.append((i_, '段落の数', len(paras_), m_['paras']))
        if FORBID & set(body):
            bad.append((i_, '縦書きにしにくい文字', sorted(FORBID & set(body))))
        if non_elem(body):
            bad.append((i_, '小学校で習わない漢字', non_elem(body)))
        sents_ = [x_ for x_ in body.split('。') if x_]
        polite_ = [x_.endswith(POLITE) for x_ in sents_]
        if m_['style'] == 'です' and not all(polite_) or m_['style'] == 'だ' and any(polite_):
            bad.append((i_, '文末がそろっていない', m_['style'], [x_[-4:] for x_ in sents_]))
        if (('「です・ます」' in ' '.join(ess_['conds'])) != (m_['style'] == 'です')) or (('「だ・である」' in ' '.join(ess_['conds'])) != (m_['style'] == 'だ')):
            bad.append((i_, '文末の条件', m_['style']))
        if m_.get('must_n'):
            if sum(1 for w_ in m_['must'] if w_ in body) < m_['must_n']:
                bad.append((i_, '指定された観点が足りない', m_['must']))
        elif any(w_ not in body for w_ in m_['must']):
            bad.append((i_, '使うことになっている言葉がない', [w_ for w_ in m_['must'] if w_ not in body]))
        if m_.get('sentences') and body.count('。') != m_['sentences']:
            bad.append((i_, '文の数', body.count('。'), m_['sentences']))
        f_ = m_.get('facts')
        if f_ and f_.get('counts'):                                            # 表の人数：合計・例文の人数・割合・いちばん多い／少ない
            cnt_, mat_ = f_['counts'], ess_['material']['rows'][1:]
            if sum(cnt_.values()) != f_['total'] or {r_[0]: int(r_[1].rstrip('人')) for r_ in mat_} != cnt_:
                bad.append((i_, '表の人数', cnt_))
            for w_, v_ in f_['say']:
                if w_ not in body or w_ != kan2(v_) + '人' or v_ not in cnt_.values():
                    bad.append((i_, '例文の人数', w_, v_))
            w_, a_, b_ = f_['ratio']
            if w_ not in body or w_ != kan2(a_ * 10 // b_) + '割' or a_ * 10 % b_ or a_ not in cnt_.values():
                bad.append((i_, '割合', w_))
            top_, low_ = max(cnt_, key=cnt_.get), min(cnt_, key=cnt_.get)
            if body.find(top_) > body.find('いちばん多') or body.find(low_) > body.find('いちばん少') or 'いちばん多' not in body or 'いちばん少' not in body:
                bad.append((i_, 'いちばん多い・少ない', top_, low_))
        if f_ and f_.get('first'):                                             # 表の数字の差
            row_ = ess_['material']['rows'][1][1:]
            if (row_[0], row_[-1]) != (str(f_['first']), str(f_['last'])) or any(kan2(f_['first'] - f_['last']) != w_ or w_ not in body or v_ != f_['first'] - f_['last'] for w_, v_ in f_['say']):
                bad.append((i_, '表の数字の差', row_, f_))
        r_ = m_.get('route')
        if r_:                                                                  # 道案内：地図の上で、実際に歩いてみる
            fa_ = ess_['material']['args']
            if r_['labels'] != {(a_, b_): n_ for a_, b_, n_ in fa_['labels']} or {frozenset(b_) for b_ in r_['blocked']} != {frozenset(b_) for b_ in fa_['blocked']} or r_['size'] != (fa_['cols'], fa_['rows']):
                bad.append((i_, '地図が、経路のデータと合わない'))
            seen_, end_ = walk(r_)
            if end_ != r_['goal'] or seen_ is None or seen_[-1] != '図書館':
                bad.append((i_, '経路がゴールにつかない', seen_, end_))
            else:
                pos_ = [body.find(v_) for v_ in r_['via']]
                if any(p_ < 0 for p_ in pos_) or pos_ != sorted(pos_) or [v_ for v_ in seen_ if v_ in r_['via']] != r_['via']:
                    bad.append((i_, '目じるしの順番', r_['via'], seen_))
    return len(mod.SETS), bad


n4_, bad4_ = check_essay(K4)
eq(f'国4 作文{n4_}セット（字数・段落・文末・漢字・資料の数字・道案内の経路）の例文', bad4_, [])

# ---------------- 形式（tools/tenri_rs_*.py をすべて） ----------------
for f in sorted(Path(__file__).resolve().parent.glob('tenri_rs_*.py')):
    mod, name = importlib.import_module(f.stem), f.stem.removeprefix('tenri_rs_')
    assert len(mod.SETS) == 10, name
    for i, st in enumerate(mod.SETS, 1):
        for j, q in enumerate(st['qs'], 1):
            if q['kind'] == 'grid':
                assert len(q['labels']) == len(q['ans']), (name, i, j)
            assert q['ans'] and q['ex'], (name, i, j)
    print(f'{name}: 10セット・{sum(len(s["qs"]) for s in mod.SETS)}問、解答と解説の欠けなし')

print('不一致:', len(FAIL), FAIL)
sys.exit(1 if FAIL else 0)
