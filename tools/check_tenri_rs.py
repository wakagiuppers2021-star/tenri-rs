"""天理中 理科・社会 類題の答えを、データとは別の計算・事実表から確かめる。

使い方: python -X utf8 tools/check_tenri_rs.py
"""
from __future__ import annotations

import importlib
import itertools
import math
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
import tenri_rs_rika1 as R1
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
