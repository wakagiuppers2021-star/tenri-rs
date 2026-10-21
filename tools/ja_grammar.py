"""国語の文法の検算に使う、形態素解析（janome。IPA辞書）と、学校文法への読みかえ。

tools/check_tenri_rs.py が、tools/tenri_rs_kokugo3.py の答え（品詞・活用形・活用の種類・文節）を、
データとは別に調べ直すために使う。janome の品詞名・活用形名を、学校で習う呼び名にそろえる。
"""
from __future__ import annotations

from janome.tokenizer import Tokenizer

import pykakasi

_T = Tokenizer()
_K = pykakasi.kakasi()


class Tok:
    __slots__ = ('surface', 'pos', 'pos1', 'pos2', 'infl_type', 'infl_form', 'base', 'start', 'end')

    def __init__(self, t, start):
        p = t.part_of_speech.split(',')
        self.surface, self.pos, self.pos1, self.pos2 = t.surface, p[0], p[1], p[2]
        self.infl_type, self.infl_form, self.base = t.infl_type, t.infl_form, t.base_form
        self.start, self.end = start, start + len(t.surface)

    def __repr__(self):
        return f'{self.surface}/{self.pos},{self.pos1}/{self.infl_type}/{self.infl_form}'


def tokens(s):
    out, i = [], 0
    for t in _T.tokenize(s):
        out.append(Tok(t, i))
        i += len(t.surface)
    assert i == len(s), (s, i)
    return out


def span(toks, a, b):
    """文字の範囲 [a, b) に、ちょうどおさまる単語の列。区切りが合わなければ、None。"""
    got = [t for t in toks if t.start >= a and t.end <= b]
    if not got or got[0].start != a or got[-1].end != b:
        return None
    return got


# ---- 品詞（ア 名詞 イ 動詞 ウ 形容詞 エ 形容動詞 オ 副詞 カ 連体詞 キ 接続詞 ク 助詞 ケ 助動詞） ----
_POS = {'名詞': 'ア', '動詞': 'イ', '形容詞': 'ウ', '副詞': 'オ', '連体詞': 'カ', '接続詞': 'キ', '助詞': 'ク', '助動詞': 'ケ'}


def pos_letter(ts):
    """単語の列（1語、または、形容動詞の語幹＋だ・な・に）の、学校文法での品詞を、記号で返す。"""
    first = ts[0]
    if first.pos == '名詞' and first.pos1 == '形容動詞語幹':
        return 'エ'
    return _POS.get(first.pos)


# ---- 活用形（ア 未然形 イ 連用形 ウ 終止形 エ 連体形 オ 仮定形 カ 命令形） ----
def form_letter(toks, i):
    """toks[i]（動詞・形容詞）の活用形を、記号で返す。終止形か連体形かは、次の語で決める（決められないときは、None）。"""
    t = toks[i]
    f = t.infl_form
    if f.startswith('未然'):
        return 'ア'
    if f.startswith('連用'):
        return 'イ'
    if f.startswith('仮定'):
        return 'オ'
    if f.startswith('命令'):
        return 'カ'
    if f == '基本形':
        nxt = toks[i + 1] if i + 1 < len(toks) else None
        if nxt is None or nxt.pos == '記号':
            return 'ウ'
        if nxt.pos == '名詞' and nxt.pos1 not in ('接尾',):
            return 'エ'
    return None


# ---- 活用の種類（ア 五段 イ 上一段 ウ 下一段 エ カ行変格 オ サ行変格） ----
_ROW = {}
for _row, _chars in {'ア': 'あかさたなはまやらわがざだばぱ', 'イ': 'いきしちにひみりぎじぢびぴ', 'ウ': 'うくすつぬふむゆるぐずづぶぷ',
                     'エ': 'えけせてねへめれげぜでべぺ', 'オ': 'おこそとのほもよろをごぞどぼぽ'}.items():
    for _c in _chars:
        _ROW[_c] = _row


def hira(s):
    return ''.join(x['hira'] for x in _K.convert(s))


def kind_letter(ts):
    """動詞（またはその語尾をふくむ列）の、活用の種類を、記号で返す。"""
    t = ts[-1]
    if t.infl_type.startswith('五段'):
        return 'ア'
    if t.infl_type.startswith('カ変'):
        return 'エ'
    if t.infl_type.startswith('サ変'):
        return 'オ'
    if t.infl_type == '一段':
        stem = hira(t.base)[:-1]                       # 「食べる」→「たべ」。語幹の最後の音で、上一段・下一段を分ける
        row = _ROW[stem[-1]]
        return {'イ': 'イ', 'エ': 'ウ'}.get(row)
    return None


# ---- 文節 ----
_START = {'名詞', '動詞', '形容詞', '副詞', '連体詞', '接続詞', '感動詞', '接頭詞'}


def bunsetsu(s):
    """文を、文節に分ける（自立語と、補助用言・形式名詞の前で区切る。接頭語・接尾語・助詞・助動詞は、前後につける）。"""
    toks = tokens(s)
    parts, cur = [], ''
    prev = None
    for t in toks:
        head = t.pos in _START and t.pos1 != '接尾' and not (prev is not None and prev.pos == '接頭詞')
        if t.pos == '動詞' and t.pos1 == '接尾':
            head = False
        if t.pos == '名詞' and t.pos1 in ('数',) and prev is not None and prev.pos == '名詞' and prev.pos1 == '数':
            head = False
        if head and cur:
            parts.append(cur)
            cur = ''
        cur += t.surface
        prev = t
    if cur:
        parts.append(cur)
    return parts


# ---------------------------------------------------------------------------------------------
# 検算：tools/tenri_rs_kokugo3.py（文法）の答えを、形態素解析と表から調べ直す
# ---------------------------------------------------------------------------------------------
CONJ_REL = {'なぜなら': '説明（理由）', 'だから': '順接', 'しかし': '逆接', 'また': '並立（つけくわえ）', 'つまり': '説明', 'ところで': '転換', 'または': '選択', 'そして': '並立（つけくわえ）'}
KEIGO = {'おっしゃる': 'ア', '拝見する': 'イ', 'ます': 'ウ', 'いらっしゃる': 'ア', '申し上げる': 'イ', 'お読みになる': 'ア', 'お持ちする': 'イ',
         'です': 'ウ', 'お帰りになる': 'ア', 'うかがう': 'イ', 'お貸しくださる': 'ア'}
KEIGO_CONV = {('食べる', '尊敬'): '召し上がる', ('来る', '尊敬'): 'いらっしゃる', ('会う', '謙譲'): 'お目にかかる', ('読む', '尊敬'): 'お読みになる',
              ('飲む', '尊敬'): '召し上がる', ('知っている', '尊敬'): 'ご存じだ', ('もらう', '謙譲'): 'いただく', ('言う', '謙譲'): '申し上げる',
              ('見る', '謙譲'): '拝見する', ('する', '尊敬'): 'なさる', ('行く', '謙譲'): 'うかがう', ('くれる', '尊敬'): 'くださる',
              ('言う', '尊敬'): 'おっしゃる'}
GITAI = {'うろうろ', 'ざあざあ', 'わくわく', 'くたくた', 'ぐんぐん', 'ぴかぴか', 'ふわふわ', 'にこにこ', 'ごろごろ', 'ひりひり', 'のろのろ'}   # 擬態語・擬音語（作問のとき JMdict で確認）
IG_RIGHT = {'道に迷って、〔　〕と歩き回った。': 'うろうろ', '雨が〔　〕と降っている。': 'ざあざあ', '合格の知らせに、胸が〔　〕した。': 'わくわく', '走りすぎて、体が〔　〕になった。': 'くたくた'}
KANA_TABLE = {'けふ': 'きょう', 'いふ': 'いう', 'かをり': 'かおり', 'こほり': 'こおり', 'ゐなか': 'いなか', 'おほきい': 'おおきい'}
KOUOU = {'決して': 'ない', 'たぶん': 'だろう', 'もし': 'たら', 'まるで': 'よう', 'どうして': 'か', 'たとえ': 'ても'}
LETTERS = {'NO': 'アイウエ', 'POS': 'アイウエオカキクケ', 'AUX': 'アイウエオ', 'KID': 'アイウ', 'RHET': 'アイウエオ', 'FORM': 'アイウエオカ', 'KIND': 'アイウエオ',
           'NAI2': 'アイウエ', 'RHS': 'アイウエ', 'IG': 'アイウエ', 'KOU2': 'アイウエ', 'PT': 'アイウエ', 'CJ': 'アイウエ', 'KOU': 'アイウエ', 'NAI': 'アイ', 'SOU': 'アイ', 'YOU': 'アイウ', 'RAS': 'アイ', 'COMP': 'アイウエオ'}


def marks(s):
    """{…} を、(かっこをとった本文, [(はじめ, おわり)]) にする。"""
    out, spans, i = '', [], None
    for ch in s:
        if ch == '{':
            i = len(out)
        elif ch == '}':
            spans.append((i, len(out)))
        else:
            out += ch
    return out, spans


def _strip(b):
    return b.rstrip('。、')


def check_bunpo(mod):
    """文法の問題の答えを調べ直す。(問題数, 不一致の一覧) を返す。"""
    bad, n_ = [], 0
    for i_, st_ in enumerate(mod.SETS, 1):
        for j_, q_ in enumerate(st_['qs'], 1):
            n_ += 1
            tag = f'{i_}-{j_}'
            m_, a_, qt_ = q_['meta'], q_['ans'], q_['q']
            t_ = m_['t']
            if not q_['ex']:
                bad.append((tag, '解説がない'))
            if t_ in LETTERS and a_ not in LETTERS[t_]:
                bad.append((tag, '答えの記号が範囲外', t_, a_))
                continue
            sent, spans = marks(qt_.split('\n')[0])
            toks = tokens(sent)
            tg = None
            if spans:
                a, b = spans[0]
                tg = span(toks, a, b)
                if tg is None and t_ not in ('KAK', 'COMP', 'KID', 'KCV', 'KANA', 'RHET', 'AUX', 'YOU', 'SOU'):
                    bad.append((tag, '下線部が、単語の区切りと合わない', sent[a:b], toks))
                    continue
            # ----- 「の」の用法 -----
            if t_ == 'NO':
                k = next(x for x, t in enumerate(toks) if t.start == a)
                tk, nx = toks[k], toks[k + 1]
                if sent[a:b] != 'の':
                    got = None
                elif tk.pos == '名詞' and tk.pos1 == '非自立':
                    got = 'ウ'
                elif tk.pos == '助詞' and nx.pos in ('動詞', '形容詞'):
                    got = 'ア'
                elif tk.pos == '助詞' and nx.pos == '名詞' and nx.pos1 == '固有名詞':
                    got = 'エ'
                elif tk.pos == '助詞' and tk.pos1 == '連体化' and nx.pos == '名詞':
                    got = 'イ'
                else:
                    got = None
                if got != a_:
                    bad.append((tag, '「の」の用法', got, a_, toks))
            # ----- 文節の数 -----
            elif t_ == 'BUN':
                sl = m_['slash']
                parts = bunsetsu(_plain_(sl))
                if '／'.join(parts) != sl or a_ != str(len(parts)) or qt_ != f'「{_plain_(sl)}」':
                    bad.append((tag, '文節', parts, sl, a_))
            # ----- 主語・述語 -----
            elif t_ == 'SV':
                sl = m_['slash']
                parts = bunsetsu(_plain_(sl))
                if '／'.join(parts) != sl:
                    bad.append((tag, '文節の区切り', parts, sl))
                subj = next((p for p in reversed(parts) if _last_particle(p) in ('が', 'は', 'も')), None)      # 文全体の主語は、最後の「が・は・も」の文節
                pred = _strip(parts[-1])
                if (_strip(subj or ''), pred) != (m_['subj'], m_['pred']) or a_ != f'{m_["subj"]}　{m_["pred"]}':
                    bad.append((tag, '主語・述語', subj, pred, m_['subj'], m_['pred']))
            # ----- 助詞・接続語・呼応の選択 -----
            elif t_ in ('PT', 'CJ', 'KOU'):
                opts = m_['opts']
                row = qt_.split('\n')[1]
                if row != '　'.join(f'{s} {o}' for s, o in zip('アイウエ', opts)) or len(set(opts)) != 4:
                    bad.append((tag, '選択肢', row, opts))
                    continue
                right = opts['アイウエ'.index(a_)]
                filled = sent.replace('〔　〕', right)
                ft = tokens(filled)
                at = sent.index('〔　〕')
                inside = [t for t in ft if t.start >= at and t.end <= at + len(right)]
                if t_ == 'PT':
                    if not inside or ''.join(t.surface for t in inside) != right or any(t.pos != '助詞' for t in inside):
                        bad.append((tag, '助詞として解析されない', right, ft))
                elif t_ == 'CJ':
                    for o in opts:
                        ot = tokens(o)
                        if len(ot) != 1 or ot[0].pos != '接続詞':
                            bad.append((tag, '接続語でない選択肢', o, ot))
                    if CONJ_REL.get(right) != m_['rel']:
                        bad.append((tag, 'つながり方', right, m_['rel']))
                else:
                    key = next((k for k in KOUOU if k in sent), None)
                    if key is None or right != KOUOU[key] or sum(1 for o in opts if o == KOUOU[key]) != 1:
                        bad.append((tag, '呼応', key, right))
            # ----- 品詞 -----
            elif t_ == 'POS':
                if pos_letter(tg) != a_:
                    bad.append((tag, '品詞', sent[a:b], pos_letter(tg), a_, tg))
            # ----- れる・られる・せる・させる -----
            elif t_ == 'AUX':
                if tg is None or tg[-1].base not in ('れる', 'られる', 'せる', 'させる') or (a_ == 'オ') != (tg[-1].base in ('せる', 'させる')):
                    bad.append((tag, 'れる・られる・せる・させる', sent[a:b], tg))
            # ----- 敬語 -----
            elif t_ == 'KID':
                tgt = sent[a:b]
                if KEIGO.get(tgt) != a_:
                    bad.append((tag, '敬語の種類', tgt, a_))
            elif t_ == 'KCV':
                tgt = sent[a:b]
                typ = '尊敬' if '（尊敬語）' in sent else '謙譲'
                if KEIGO_CONV.get((tgt, typ)) != a_:
                    bad.append((tag, '敬語に直す', tgt, typ, a_))
            # ----- 修辞法 -----
            elif t_ == 'RHET':
                has_you = any(t.surface in ('よう', 'みたい') for t in toks)
                body = [t for t in toks if t.pos != '記号']
                taigen = body[-1].pos == '名詞' and not (len(body) >= 2 and body[-2].pos == '名詞,形容動詞語幹')
                if (a_ == 'ア') != has_you or (a_ == 'オ' and not taigen):
                    bad.append((tag, '修辞法', a_, has_you, taigen))
            # ----- 活用形 -----
            elif t_ == 'FORM':
                k = next(x for x, t in enumerate(toks) if t.start == a)
                if toks[k].pos not in ('動詞', '形容詞') or form_letter(toks, k) != a_:
                    bad.append((tag, '活用形', sent[a:b], form_letter(toks, k), a_, toks[k]))
            # ----- 活用の種類 -----
            elif t_ == 'KIND':
                if tg[-1].pos != '動詞' or kind_letter(tg) != a_:
                    bad.append((tag, '活用の種類', sent[a:b], kind_letter(tg), a_))
            # ----- かなづかい -----
            elif t_ == 'KANA':
                if KANA_TABLE.get(sent[a:b]) != a_:
                    bad.append((tag, 'かなづかい', sent[a:b], a_))
            # ----- 係り受け -----
            elif t_ == 'KAK':
                sl = m_['slash']
                plain, sp = marks(sl)
                parts = [_strip(p) for p in bunsetsu(plain.replace('／', ''))]
                if '／'.join(bunsetsu(plain.replace('／', ''))) != plain or not sp:
                    bad.append((tag, '文節の区切り', parts, plain))
                    continue
                words = plain.split('／')
                idx = None
                for x, w in enumerate(words):
                    start = len('／'.join(words[:x])) + (1 if x else 0)     # 「／」をふくむ文字位置
                    if (start, start + len(w)) == sp[0]:
                        idx = x
                if idx is None:
                    bad.append((tag, '下線部が、文節ではない', sl))
                    continue
                last = tokens(_strip(words[idx]))[-1]
                heads = [_head(w) for w in words]
                if last.pos in ('連体詞', '副詞') or (last.pos == '助詞' and last.surface == 'の') or _is_attr(words, idx):
                    want = words[idx + 1]                                           # 連体修飾（あとの名詞）・副詞（すぐあとの語）
                else:                                                               # 連用修飾：あとの、述語（連体修飾の形でない用言）
                    want = next((w for k, w in enumerate(words[idx + 1:], idx + 1) if heads[k] in ('動詞', '形容詞', 'エ') and not _is_attr(words, k)), None)
                if want is None or _strip(want) != a_ or a_ != q_['ans']:
                    bad.append((tag, '係り受け', words[idx], want, a_))
                if q_['q'] != sl.replace('／', ''):
                    bad.append((tag, '問題文'))
            # ----- 文の成分 -----
            elif t_ == 'COMP':
                parts = bunsetsu(sent)
                tgt = sent[a:b]
                idx = next((x for x, p in enumerate(parts) if _strip(p).strip('、') == tgt or _strip(p) == tgt), None)
                if idx is None:
                    bad.append((tag, '下線部が、文節ではない', tgt, parts))
                    continue
                head = _head(parts[idx])
                first_subj = next((x for x, p in enumerate(parts) if _last_particle(p) in ('が', 'は', 'も')), None)
                if head in ('接続詞',):
                    got = 'エ'
                elif head in ('感動詞',):
                    got = 'オ'
                elif idx == len(parts) - 1 or parts[idx].endswith('。') and False:
                    got = 'イ'
                elif idx == first_subj:
                    got = 'ア'
                else:
                    got = 'ウ'
                # 「雨がふった。」のように、文が2つあるときは、「ふった」も述語
                if got == 'ウ' and parts[idx].endswith('。'):
                    got = 'イ'
                if got != a_:
                    bad.append((tag, '文の成分', tgt, got, a_, parts))
            # ----- ない・そうだ・ようだ・らしい -----
            elif t_ == 'NAI':
                tk = next((t for t in toks if t.start == a), None)
                got = 'ア' if tk and tk.pos == '助動詞' else 'イ' if tk and tk.pos == '形容詞' else None
                if got != a_ or sent[a:b] != 'ない':
                    bad.append((tag, '「ない」の識別', got, a_))
            elif t_ == 'SOU':
                k = next((x for x, t in enumerate(toks) if t.start == a), None)
                if k is None or sent[a:b] != 'そうだ' or toks[k].surface != 'そう':
                    bad.append((tag, '「そうだ」', sent[a:b], toks))
                else:
                    pv = toks[k - 1]
                    got = 'イ' if pv.infl_form == '基本形' else 'ア'
                    if got != a_:
                        bad.append((tag, '「そうだ」の識別', pv, got, a_))
            elif t_ == 'YOU':
                if not any(t.surface == 'よう' for t in toks) or sent[a:b] not in ('ようだ', 'ような'):
                    bad.append((tag, '「ようだ」', sent[a:b], toks))
            elif t_ == 'RAS':                       # 用言（や「た」）につく＝推定。名詞について、あとの名詞をくわしくする＝接尾語
                k = next((x for x, t in enumerate(toks) if t.start == a), None)
                if k is None or sent[a:b] != 'らしい' or toks[k].pos != '助動詞':
                    bad.append((tag, '「らしい」', sent[a:b], toks))
                else:
                    pv, nx = toks[k - 1], toks[k + 1]
                    got = 'ア' if pv.pos in ('動詞', '形容詞', '助動詞') else 'イ' if pv.pos == '名詞' and nx.pos == '名詞' else None
                    if got != a_:
                        bad.append((tag, '「らしい」の識別', got, a_, toks))
            # ----- 現代かなづかいの誤り -----
            elif t_ == 'KM':
                if (m_['wrong'] not in m_['sent'] or hira(m_['kanji']) != m_['right'] or m_['wrong'] == m_['right'] or a_ != m_['right']
                        or hira(m_['kanji']) == m_['wrong'] or q_['q'] != f'「{m_["sent"]}」' or m_['sent'].count(m_['wrong']) != 1):
                    bad.append((tag, 'かなづかいの誤り', m_['wrong'], m_['right'], hira(m_['kanji'])))
            # ----- 「ない」の使い方（助動詞・形容詞・補助形容詞） -----
            elif t_ == 'NAI2':
                lines = qt_.split('\n')
                got = []
                for ln in [lines[0]] + [x[2:] for x in lines[1:]]:
                    pl, sp = marks(ln)
                    tk = tokens(pl)
                    k = next((x for x, t in enumerate(tk) if sp and t.start == sp[0][0]), None)
                    if k is None or tk[k].surface != 'ない':
                        got.append(None)
                        continue
                    prev = tk[k - 1]
                    if tk[k].pos == '助動詞' and prev.pos == '動詞':
                        got.append('aux')                                           # 動詞の未然形につく打ち消し
                    elif tk[k].pos == '形容詞':
                        got.append('adj')                                           # 「ある」の反対（存在しない）
                    elif tk[k].pos == '助動詞' and (prev.pos == '形容詞' or (prev.surface == 'は' and tk[k - 2].surface == 'で')):
                        got.append('hojo')                                          # 「〜くない」「〜ではない」（補助形容詞）
                    else:
                        got.append(None)
                tags = [t for _, t in m_['opts']]
                if (got != [m_['ttag']] + tags or [k for k, t in zip('アイウエ', tags) if t == m_['ttag']] != [a_] or len(m_['opts']) != 4
                        or lines[0] != m_['target']):
                    bad.append((tag, '「ない」の使い方', got, m_['ttag'], tags, a_))
            # ----- 同じ表現技法の文を選ぶ -----
            elif t_ == 'RHS':
                lines = qt_.split('\n')
                texts = [t for t, _ in m_['opts']]
                tags = [t for _, t in m_['opts']]

                def figure(sentence, tg):
                    tk = [x for x in tokens(sentence) if x.pos != '記号']
                    simile = any(x.surface in ('よう', 'みたい') for x in tk)
                    return (tg == '直喩') == simile and (tg != '体言止め' or tk[-1].pos == '名詞')
                if (lines[0] != f'「{m_["target"]}」' or lines[1:] != [f'{k} {t}' for k, t in zip('アイウエ', texts)] or len(m_['opts']) != 4
                        or [k for k, t in zip('アイウエ', tags) if t == m_['ttag']] != [a_] or not figure(m_['target'], m_['ttag'])
                        or not all(figure(t, g) for t, g in m_['opts'])):
                    bad.append((tag, '表現技法の選択', m_['ttag'], tags, a_))
            # ----- 言いかえ（空らんに入る言葉） -----
            elif t_ == 'RP':
                filled = m_['s2'].replace('〔　〕', a_)
                tk = tokens(filled)
                bases = {x.base for x in tk}
                if (len(a_) != m_['n'] or '〔　〕' not in m_['s2'] or any(b not in bases for b in m_['must'])
                        or qt_ != f'ア　{m_["s1"]}\nイ　{m_["s2"]}（{"一二三四五六七八"[m_["n"] - 1]}字）'):
                    bad.append((tag, '言いかえ', a_, m_['must'], sorted(bases)))
            # ----- 擬態語・擬音語の選択 -----
            elif t_ == 'IG':
                opts = m_['opts']
                row = qt_.split('\n')[1]
                right = opts['アイウエ'.index(a_)]
                if (row != '　'.join(f'{k} {o}' for k, o in zip('アイウエ', opts)) or len(set(opts)) != 4 or '〔　〕' not in qt_.split('\n')[0]
                        or right not in GITAI or any(o not in GITAI for o in opts) or IG_RIGHT.get(qt_.split('\n')[0]) != right):
                    bad.append((tag, '擬態語の選択', opts, a_))
            # ----- 呼応する言葉の選択（とうてい…ない・まるで…ようだ・たぶん…だろう） -----
            elif t_ == 'KOU2':
                opts = m_['opts']
                row = qt_.split('\n')[1]
                has = {'neg': lambda o: any(x.pos == '助動詞' and x.surface in ('ない', 'ず', 'ぬ') for x in tokens(o)),
                       'simile': lambda o: any(x.surface == 'よう' for x in tokens(o)),
                       'guess': lambda o: 'だろう' in o}[m_['kind']]
                key = {'neg': ('とうてい', '決して', '少しも'), 'simile': ('まるで',), 'guess': ('たぶん', 'おそらく')}[m_['kind']]
                if (row != '　'.join(f'{k} {o}' for k, o in zip('アイウエ', opts)) or [k for k, o in zip('アイウエ', opts) if has(o)] != [a_]
                        or not any(w in qt_.split('\n')[0] for w in key) or len(set(opts)) != 4):
                    bad.append((tag, '呼応', m_['kind'], opts, a_))
            else:
                bad.append((tag, '未対応の種類', t_))
    return n_, bad


def _is_attr(words, i):
    """文節 words[i] が、あとの名詞をくわしくする形（連体修飾）か。"""
    last = tokens(_strip(words[i]))[-1]
    noun_next = i + 1 < len(words) and _head(words[i + 1]) == '名詞'
    if last.pos == '連体詞':
        return True
    if noun_next and ((last.pos == '助動詞' and last.surface in ('な', 'た', 'だ')) or (last.pos in ('形容詞', '動詞') and last.infl_form == '基本形')):
        return True
    return False


def _plain_(s):
    return s.replace('／', '').replace('{', '').replace('}', '')


def _last_particle(b):
    """文節の最後の単語が助詞ならその語を、そうでなければ ''。"""
    ts = tokens(_strip(b))
    return ts[-1].surface if ts and ts[-1].pos == '助詞' else ''


def _head(b):
    """文節の最初の単語の品詞（形容動詞語幹は 'エ'）。"""
    ts = tokens(_strip(b))
    if ts[0].pos == '名詞' and ts[0].pos1 == '形容動詞語幹':
        return 'エ'
    return ts[0].pos
