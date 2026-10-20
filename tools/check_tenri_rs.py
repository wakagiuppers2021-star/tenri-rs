"""天理中 理科・社会 類題の答えを、データとは別の計算・事実表から確かめる。

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
import tenri_rs_shakai1 as S1

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


def opts(s):
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
eq('理2-2(4) 海の深さ', ans(R2, 2, 4), [k for k, v in opts(q_text(R2, 2, 4)).items() if trend in v][0])
idx = {lab: i for i, (lab, _) in enumerate(column)}
t_fault = max(idx[l] for l in cut) + .5
assert all(idx[l] > t_fault for l in idx if l not in cut)
when = {'ア': t_fault, 'イ': idx['A'], 'ウ': idx['B']}
eq('理2-2(8) できごとの順', ans(R2, 2, 8), '→'.join(sorted(when, key=when.get)))

# 3 磁石：ふれている極の反対の極がくぎの頭にでき、先は同じ極。ちがう極どうしが引き合う
opp = {'N': 'S', 'S': 'N'}
material = {'鉄のくぎ': '鉄', '銅のはり金': '銅', 'ガラスのびん': 'ガラス', '鉄のゼムクリップ': '鉄'}
eq('理2-3(1) 引きつけられる', ans(R2, 3, 1), join(k for k, v in opts(q_text(R2, 3, 1)).items() if material[v] == '鉄'))
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
same = [k for k, v in opts(q_text(R2, 4, 3)).items() if any(kind[p] == '結ろ' for p in kind if p in v)]
eq('理2-4(3) 同じしくみ', ans(R2, 4, 3), join(same))
eq('理2-4(5) 20℃の最大量', ans(R2, 4, 5), f'{num(sat[20])}g')
eq('理2-4(6) 水てきができ始める', ans(R2, 4, 6), f'{[t for t, v in sat.items() if v == 12.8][0]}℃')
assert 17.3 <= sat[30]
eq('理2-4(7) できる水てき', ans(R2, 4, 7), f'{num(17.3 - sat[10])}g')

# 5 水よう液：(名前, 性質, とけているもの, においの有無)
sol = {'塩酸': ('酸性', '気体', True), '水酸化ナトリウム水よう液': ('アルカリ性', '固体', False),
       '食塩水': ('中性', '固体', False), '炭酸水': ('酸性', '気体', False), 'アンモニア水': ('アルカリ性', '気体', True),
       '石灰水': ('アルカリ性', '固体', False), '砂糖水': ('中性', '固体', False)}
lead5 = opts(R2.SETS[4]['lead'])
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
eq('理2-7(7) ピンセットと同じ', ans(R2, 7, 7), join(k for k, v in opts(q_text(R2, 7, 7)).items() if middle[v] == middle['ピンセット']))

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
o9 = opts(q_text(R2, 9, 3))
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
o10 = {v: k for k, v in opts(q_text(R2, 10, 3)).items()}
eq('理2-10(3) 冬ごし', ans(R2, 10, 3), [o10[winter[n]] for n in R2.SETS[9]['qs'][2]['labels']])
pupa = {'モンシロチョウ': True, 'カブトムシ': True, 'トンボ': False, 'バッタ': False}
eq('理2-10(7) さなぎにならない', ans(R2, 10, 7), join(k for k, v in opts(q_text(R2, 10, 7)).items() if not pupa[v]))

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
