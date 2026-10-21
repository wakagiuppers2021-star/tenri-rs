"""国語の漢字の検算に使う、熟語の読みの分解（音読み・訓読み）。

小学校で習う漢字（tools/kanji_grade.py の READ）だけでできた熟語について、読み（pykakasi）を、
漢字ごとの読みに分け、それぞれが音読みか訓読みかを調べる。連濁（かわ→がわ）と、促音（がく→がっ）に対応している。
"""
from __future__ import annotations

import pykakasi

import kanji_grade as KG

_K = pykakasi.kakasi()
_VOICE = dict(zip('かきくけこさしすせそたちつてとはひふへほ', 'がぎぐげござじずぜぞだぢづでどばびぶべぼ'))
_SEMI = dict(zip('はひふへほ', 'ぱぴぷぺぽ'))


FIX = {'五分': 'ごふん', '作物': 'さくもつ'}                       # pykakasi の読みの誤り（JMdict で確認した正しい読み）


def hira(s):
    return FIX.get(s) or ''.join(x['hira'] for x in _K.convert(s))


def readings(ch):
    """漢字1字の、(読み, 音か訓か) の集まり。訓読みは、語幹と、語幹＋送りがなの両方。"""
    on, kun = KG.READ[ch]
    out = {(r, 'on') for r in on}
    for k in kun:
        stem, _, okuri = k.partition('.')
        out.add((stem, 'kun'))
        out.add((stem + okuri, 'kun'))
    return out


def _variants(r, kind, first):
    """読み r が、熟語の中で、実際にとりうる形（連濁・促音）。"""
    out = {(r, kind)}
    if not first and r[0] in _VOICE:
        out.add((_VOICE[r[0]] + r[1:], kind))
        if r[0] in _SEMI:
            out.add((_SEMI[r[0]] + r[1:], kind))
    if first and len(r) >= 2 and r[-1] in 'つくきち':
        out.add((r[:-1] + 'っ', kind))
    return out


def split_types(word):
    """二字の熟語の、読みの分け方。{('on', 'kun'), ...}（ありうる、音訓の組み合わせの集まり）。"""
    assert len(word) == 2, word
    full = hira(word)
    a, b = word
    out = set()
    for r1, k1 in readings(a):
        for v1, kk1 in _variants(r1, k1, True):
            if not full.startswith(v1):
                continue
            rest = full[len(v1):]
            for r2, k2 in readings(b):
                for v2, kk2 in _variants(r2, k2, False):
                    if rest == v2:
                        out.add((kk1, kk2))
    return out


_NAME = {('on', 'on'): '音音', ('kun', 'kun'): '訓訓', ('on', 'kun'): '音訓', ('kun', 'on'): '訓音'}


def pair_type(word):
    """二字の熟語の、読みの組み合わせ（音音・訓訓・音訓・訓音）。決まらないときは None。"""
    t = split_types(word)
    return _NAME[next(iter(t))] if len(t) == 1 else None


def reads_as(word, ch, reading):
    """熟語 word の中で、漢字 ch が、読み reading（ひらがな）で読まれているか。"""
    full = hira(word)
    i = word.index(ch)
    for r, _ in readings(ch):
        for v, _k in _variants(r, 'x', i == 0):
            if v != reading:
                continue
            if i == 0 and full.startswith(v):
                return True
            if i == len(word) - 1 and full.endswith(v):
                return True
    return False
