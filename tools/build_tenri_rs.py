"""天理中学校 理科・社会・算数・国語 大問別の類題プリントを作る。

使い方: python -X utf8 tools/build_tenri_rs.py rika 1
        python -X utf8 tools/build_tenri_rs.py shakai 1
        python -X utf8 tools/build_tenri_rs.py kokugo 1
データは tools/tenri_rs_<教科><大問番号>.py に置く（SETS と ANALYSIS）。
"""
from __future__ import annotations

import importlib
import math
import sys
from pathlib import Path

import fitz
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas

sys.path.insert(0, str(Path(__file__).resolve().parent))
ROOT = Path(__file__).resolve().parents[1]
W, H = A4
LM, RM = 42, W - 42
INK = colors.HexColor('#182331')
ACCENT = colors.HexColor('#264C65')
MUTED = colors.HexColor('#56616C')
LINE = colors.HexColor('#C2C9CE')
PALE = colors.HexColor('#F0F3F5')
SHADE = colors.HexColor('#8C979F')


def find_font(*paths):
    """リポジトリの fonts/（OFL版）を先に、なければ Windows 同梱版を使う。"""
    for f in paths:
        if f.exists():
            return str(f)
    sys.exit('フォントがありません: fonts/BIZUDGothic-Regular.ttf と BIZUDGothic-Bold.ttf を置いてください')


pdfmetrics.registerFont(TTFont('JP', find_font(ROOT / 'fonts/BIZUDGothic-Regular.ttf',
                                               Path('C:/Windows/Fonts/BIZ-UDGothicR.ttc')), subfontIndex=0))
pdfmetrics.registerFont(TTFont('JPB', find_font(ROOT / 'fonts/BIZUDGothic-Bold.ttf',
                                                Path('C:/Windows/Fonts/BIZ-UDGothicB.ttc')), subfontIndex=0))

SUBJECTS = {'rika': '理科', 'shakai': '社会', 'sansu': '算数', 'kokugo': '国語'}
DRY = False          # True のときは描かずに高さだけ測る
LAYOUT = []          # (ファイル, ページ, x0, x1, y0, y1, 文字列)
BOTTOM = 52          # 本文がこれより下に来たらはみ出し


# ---------- 文字 ----------
def tw(s, size, bold=False):
    return pdfmetrics.stringWidth(s, 'JPB' if bold else 'JP', size)


def text(c, x, y, s, size=10, bold=False, color=INK, center=False):
    w = tw(s, size, bold)
    if center:
        x -= w / 2
    if not DRY:
        c.setFillColor(color)
        c.setFont('JPB' if bold else 'JP', size)
        c.drawString(x, y, s)
        LAYOUT.append((c._filename, c._pageNumber, x, x + w, y - size * .2, y + size * .85, s))
    return w


def _word(ch):
    """数字・英字・小数点・%（行の途中で切りたくない文字）。"""
    return ch.isascii() and (ch.isalnum() or ch in '.%')


def wrap(s, width, size=10, bold=False):
    out = []
    for part in s.split('\n'):
        line = ''
        for ch in part:
            if line and tw(line + ch, size, bold) > width:
                if line[-1] in '（「『【〔' and len(line) > 1:
                    out.append(line[:-1])                          # 始めのかっこは、行末に残さない
                    line = line[-1] + ch
                elif ch in '、。）」』】〕・,.' and len(line) > 1:
                    k = len(line) - 1
                    while k > 1 and ((_word(line[k]) and _word(line[k - 1])) or line[k - 1] in '（「『【〔　'):
                        k -= 1                                   # 数字や英字のかたまり、〔　〕の空らんは、まるごと次の行へ
                    out.append(line[:k])
                    line = line[k:] + ch
                elif _word(ch) and _word(line[-1]):
                    k = len(line)
                    while k > 0 and _word(line[k - 1]):
                        k -= 1
                    while k > 1 and line[k - 1] in '（「『【〔':
                        k -= 1                                   # 始めのかっこも、いっしょに次の行へ
                    if k > 0:
                        out.append(line[:k])
                        line = line[k:] + ch
                    else:
                        out.append(line)
                        line = ch
                else:
                    out.append(line)
                    line = ch
            else:
                line += ch
        out.append(line)
        # 最後の行が1〜2文字だけにならないよう、前の行から送る
        while len(out) >= 2 and 0 < len(out[-1]) <= 2 and len(out[-2]) > 4 and out[-2][-1] not in '　 ':
            out[-1] = out[-2][-1] + out[-1]
            out[-2] = out[-2][:-1]
    return out


def para(c, x, y, s, width, size=10, leading=None, color=INK, bold=False):
    leading = leading or size * 1.55
    lines = wrap(s, width, size, bold)
    for ln in lines:
        text(c, x, y, ln, size, bold, color)
        y -= leading
    return y, len(lines)


# ---------- 図形の補助 ----------
def setline(c, w=.8, color=INK, dash=None):
    c.setLineWidth(w)
    c.setStrokeColor(color)
    c.setDash(*dash) if dash else c.setDash()


def arrow(c, x1, y1, x2, y2, head=6, w=.9, color=INK):
    setline(c, w, color)
    c.line(x1, y1, x2, y2)
    a = math.atan2(y2 - y1, x2 - x1)
    p = c.beginPath()
    p.moveTo(x2, y2)
    p.lineTo(x2 - head * math.cos(a - .4), y2 - head * math.sin(a - .4))
    p.lineTo(x2 - head * math.cos(a + .4), y2 - head * math.sin(a + .4))
    p.close()
    c.setFillColor(color)
    c.drawPath(p, fill=1, stroke=0)


def fig_monochord(c, x, top, w, h):
    cx = x + w / 2
    bx0, bx1 = cx - 170, cx + 170
    by = top - h + 22
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(bx0, by, bx1 - bx0, 26, fill=1, stroke=1)
    text(c, cx, by + 9, '木の箱', 9, color=MUTED, center=True)
    # 左の固定部分と右のくい
    c.setFillColor(INK)
    c.rect(bx0 + 6, by + 26, 8, 12, fill=1, stroke=0)
    c.rect(bx1 - 14, by + 26, 8, 16, fill=1, stroke=0)
    sy = by + 38
    setline(c, 1.2)
    c.line(bx0 + 10, sy, bx1 - 10, sy)
    # ことじ
    kx = cx + 40
    p = c.beginPath()
    p.moveTo(kx - 9, by + 26); p.lineTo(kx, sy); p.lineTo(kx + 9, by + 26); p.close()
    c.setFillColor(colors.white)
    setline(c, 1)
    c.drawPath(p, fill=1, stroke=1)
    arrow(c, kx + 30, sy + 13, kx + 5, sy - 3, 5, .7, MUTED)
    text(c, kx + 33, sy + 12, 'ことじ（動かせる）', 8.5, color=MUTED)
    arrow(c, cx - 60, sy + 30, cx - 60, sy + 4, 5, .7, MUTED)
    text(c, cx - 60, sy + 34, 'げん（はじく）', 8.5, color=MUTED, center=True)
    text(c, bx1 + 2, sy + 10, 'くい', 8.5, color=MUTED)


def _battery_h(c, x, y, n=1):
    """横向きの導線上にかん電池を n 個（直列）描く。x は左はし。幅を返す。"""
    gap = 5
    for i in range(n):
        xx = x + i * 14
        setline(c, 1.1)
        c.line(xx, y - 9, xx, y + 9)          # 長い線（＋極）
        setline(c, 2.6)
        c.line(xx + gap, y - 4.5, xx + gap, y + 4.5)  # 短い線（−極）
        if i < n - 1:
            setline(c, 1)
            c.line(xx + gap, y, xx + 14, y)
    return gap + (n - 1) * 14


def _bulb(c, x, y, r=7):
    setline(c, 1)
    c.setFillColor(colors.white)
    c.circle(x, y, r, stroke=1, fill=1)
    d = r * .7
    c.line(x - d, y - d, x + d, y + d)
    c.line(x - d, y + d, x + d, y - d)


def _dot(c, x, y):
    c.setFillColor(INK)
    c.circle(x, y, 1.9, stroke=0, fill=1)


def fig_circuits(c, x, top, w, h):
    labels = ['ア', 'イ', 'ウ', 'エ']
    pw = w / 4
    for i, lab in enumerate(labels):
        px = x + i * pw
        x0, x1 = px + 18, px + pw - 18
        y0, y1 = top - h + 14, top - 26
        text(c, (x0 + x1) / 2, top - 12, lab, 11, bold=True, center=True)
        mid = (x0 + x1) / 2
        nb = 2 if lab == 'エ' else 1
        bw = 5 + (nb - 1) * 14
        bx = mid - bw / 2
        setline(c, 1)
        c.line(x0, y0, bx, y0)
        c.line(bx + bw, y0, x1, y0)
        _battery_h(c, bx, y0, nb)
        c.line(x0, y0, x0, y1)
        c.line(x1, y0, x1, y1)
        if lab == 'イ':
            xs = [x0 + (x1 - x0) * .3, x0 + (x1 - x0) * .7]
        else:
            xs = [mid]
        c.line(x0, y1, x1, y1)
        for bxx in xs:
            _bulb(c, bxx, y1)
        if lab == 'ウ':
            ym = (y0 + y1) / 2 + 6
            setline(c, 1)
            c.line(x0, ym, x1, ym)
            _bulb(c, mid, ym)
            _dot(c, x0, ym)
            _dot(c, x1, ym)
    text(c, x + w / 2, top - h - 9, '記号：長い線と短い線の組がかん電池（長い線が＋極）、丸に×が豆電球。', 8.5, color=MUTED, center=True)


def fig_moon(c, x, top, w, h):
    cx, cy = x + w / 2 - 30, top - h / 2 - 4
    R, re, rm = 62, 15, 8.5
    setline(c, .7, MUTED, (3, 2))
    c.circle(cx, cy, R, stroke=1, fill=0)
    setline(c, .9)
    # 地球（右半分が昼）
    c.setFillColor(SHADE)
    c.circle(cx, cy, re, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.wedge(cx - re, cy - re, cx + re, cy + re, -90, 180, stroke=0, fill=1)
    c.circle(cx, cy, re, stroke=1, fill=0)
    text(c, cx, cy - re - 11, '地球', 8.5, center=True)
    for k, lab in enumerate('ABCDEFGH'):
        a = math.radians(k * 45)
        mx, my = cx + R * math.cos(a), cy + R * math.sin(a)
        c.setFillColor(SHADE)
        c.circle(mx, my, rm, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.wedge(mx - rm, my - rm, mx + rm, my + rm, -90, 180, stroke=0, fill=1)
        setline(c, .8)
        c.circle(mx, my, rm, stroke=1, fill=0)
        lx, ly = cx + (R + 19) * math.cos(a), cy + (R + 19) * math.sin(a)
        text(c, lx, ly - 4, lab, 10, bold=True, center=True)
    # 月の動く向き（北極の上から見て反時計回り）
    a1, a2 = math.radians(112), math.radians(128)
    arrow(c, cx + (R - 1) * math.cos(a1), cy + (R - 1) * math.sin(a1),
          cx + (R - 1) * math.cos(a2), cy + (R - 1) * math.sin(a2), 6, .9, ACCENT)
    text(c, cx - 104, cy + 70, '月の動く向き', 8.5, color=ACCENT)
    # 太陽の光
    sx = cx + R + 58
    for dy in (-34, 0, 34):
        arrow(c, sx + 40, cy + dy, sx, cy + dy, 6, 1, INK)
    text(c, sx + 20, cy + 46, '太陽の光', 9, center=True)


def fig_ice_graph(c, x, top, w, h):
    gx0, gx1 = x + 120, x + 390
    gy0, gy1 = top - h + 28, top - 24
    tmin, tmax = -20, 120
    def X(t): return gx0 + (gx1 - gx0) * t / 20
    def Y(v): return gy0 + (gy1 - gy0) * (v - tmin) / (tmax - tmin)
    setline(c, .35, LINE)
    for v in range(-20, 121, 20):
        c.line(gx0, Y(v), gx1, Y(v))
        text(c, gx0 - 6 - tw(str(v), 8), Y(v) - 3, str(v), 8, color=MUTED)
    for t in range(0, 21, 2):
        setline(c, .35, LINE)
        c.line(X(t), gy0, X(t), gy1)
        if t % 4 == 0:
            text(c, X(t), gy0 - 11, str(t), 8, color=MUTED, center=True)
    setline(c, 1, INK)
    c.line(gx0, Y(0), gx1, Y(0))
    c.line(gx0, gy0, gx0, gy1)
    text(c, gx0 - 30, gy1 + 13, '温度(℃)', 8.5)
    text(c, (gx0 + gx1) / 2, gy0 - 24, '時間(分)', 8.5, center=True)
    pts = [(0, -10), (2, 0), (6, 0), (14, 100), (20, 100)]
    setline(c, 1.8, ACCENT)
    for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
        c.line(X(t1), Y(v1), X(t2), Y(v2))
    for (t, v), lab in zip(pts, 'ABCDE'):
        c.setFillColor(ACCENT)
        c.circle(X(t), Y(v), 2.4, stroke=0, fill=1)
        dx, dy = {'A': (5, -12), 'B': (-4, 6), 'C': (4, 6), 'D': (-11, 5), 'E': (-4, 6)}[lab]
        text(c, X(t) + dx, Y(v) + dy, lab, 10, bold=True)


def fig_pendulum(c, x, top, w, h):
    px, py = x + w / 2 + 8, top - 14
    setline(c, 2)
    c.line(px - 50, py, px + 50, py)
    setline(c, .5)
    for i in range(-48, 50, 8):
        c.line(px + i, py, px + i + 5, py + 5)
    L = h - 50
    a = math.radians(24)
    # 静止位置（点線）
    setline(c, .7, MUTED, (3, 2))
    c.line(px, py, px, py - L)
    # ふれた位置
    bx, by = px - L * math.sin(a), py - L * math.cos(a)
    setline(c, 1)
    c.line(px, py, bx, by)
    c.setFillColor(PALE)
    c.circle(bx, by, 9, stroke=1, fill=1)
    _dot(c, px, py)
    text(c, px + 6, py - 12, '支点', 8.5)
    text(c, bx - 30, by - 22, 'おもり', 8.5)
    # ふれはば（角度）
    setline(c, .8, ACCENT)
    c.arc(px - 40, py - 40, px + 40, py + 40, 270 - 24, 24)
    text(c, px - 76, py - 47, 'ふれはば', 8.5, color=ACCENT)
    # ふりこの長さ
    setline(c, .7, MUTED)
    c.line(px + 18, py, px + 18, py - L)
    arrow(c, px + 18, py - L / 2, px + 18, py - 2, 4, .7, MUTED)
    arrow(c, px + 18, py - L / 2, px + 18, py - L + 2, 4, .7, MUTED)
    text(c, px + 22, py - L / 2 - 3, 'ふりこの長さ', 8.5, color=MUTED)


def _poly(c, pts):
    p = c.beginPath()
    p.moveTo(*pts[0])
    for pt in pts[1:]:
        p.lineTo(*pt)
    p.close()
    return p


def _pattern(c, kind, x0, y0, x1, y1):
    """地層の模様。れき=丸、砂=点、どろ=短い横線、火山灰=小さなv。"""
    if kind == 'gravel':
        setline(c, .6)
        c.setFillColor(PALE)
        for r, yy in enumerate(range(int(y0) + 4, int(y1) + 6, 8)):
            for xx in range(int(x0) + 4 + (r % 2) * 5, int(x1) + 6, 10):
                c.circle(xx, yy, 2.7, stroke=1, fill=1)
    elif kind == 'sand':
        c.setFillColor(INK)
        for r, yy in enumerate(range(int(y0) + 2, int(y1) + 4, 4)):
            for xx in range(int(x0) + 2 + (r % 2) * 2, int(x1) + 4, 5):
                c.circle(xx, yy, .55, stroke=0, fill=1)
    elif kind == 'mud':
        setline(c, .5, MUTED)
        for r, yy in enumerate(range(int(y0) + 3, int(y1) + 4, 5)):
            for xx in range(int(x0) + (r % 2) * 4, int(x1) + 6, 9):
                c.line(xx, yy, xx + 5, yy)
    elif kind == 'ash':
        setline(c, .6)
        for r, yy in enumerate(range(int(y0) + 3, int(y1) + 4, 6)):
            for xx in range(int(x0) + 2 + (r % 2) * 4, int(x1) + 6, 8):
                c.line(xx - 2, yy + 2, xx, yy - 1)
                c.line(xx, yy - 1, xx + 2, yy + 2)


def _layer(c, pts, kind):
    c.saveState()
    c.clipPath(_poly(c, pts), stroke=0, fill=0)
    xs, ys = [p[0] for p in pts], [p[1] for p in pts]
    _pattern(c, kind, min(xs), min(ys), max(xs), max(ys))
    c.restoreState()
    setline(c, .8)
    c.drawPath(_poly(c, pts), stroke=1, fill=0)


def fig_strata(c, x, top, w, h):
    """がけの地層。下からE〜Bが断層Xでずれていて、いちばん上のAはずれていない。"""
    cx = x + w / 2 - 60
    bx0, bx1 = cx - 140, cx + 140
    yb = top - h + 20
    layers = [('E', 26, 'gravel'), ('D', 26, 'sand'), ('C', 26, 'mud'), ('B', 14, 'ash')]
    ys = [yb]
    for _, t, _ in layers:
        ys.append(ys[-1] + t)
    T = ys[-1] + 26
    d = 18                                   # 断層の右側が下がった大きさ
    fx0, fx1 = cx + 24, cx - 6

    def fx(y):
        return fx0 + (fx1 - fx0) * (y - yb) / (ys[-1] - yb)

    for i, (lab, _, kind) in enumerate(layers):
        lo, hi = ys[i], ys[i + 1]
        _layer(c, [(bx0, lo), (fx(lo), lo), (fx(hi), hi), (bx0, hi)], kind)
        lo2, hi2 = max(lo - d, yb), hi - d
        _layer(c, [(fx(lo2), lo2), (bx1, lo2), (bx1, hi2), (fx(hi2), hi2)], kind)
        text(c, bx0 - 14, (lo + hi) / 2 - 3.5, lab, 10, bold=True)
    top_b = ys[-1]
    _layer(c, [(bx0, top_b), (fx(top_b), top_b), (fx(top_b - d), top_b - d), (bx1, top_b - d), (bx1, T), (bx0, T)], 'sand')
    text(c, bx0 - 14, (top_b + T) / 2 - 3.5, 'A', 10, bold=True)
    setline(c, 2.2, ACCENT)
    c.line(fx(yb), yb, fx(top_b), top_b)
    text(c, fx(yb), yb - 14, 'X', 10, bold=True, color=ACCENT, center=True)
    # 凡例（Bの層は凡例に入れない）
    lx = bx1 + 34
    for k, (name, kind) in enumerate([('れき', 'gravel'), ('砂', 'sand'), ('どろ', 'mud')]):
        yy = T - 12 - k * 24
        _layer(c, [(lx, yy - 6), (lx + 26, yy - 6), (lx + 26, yy + 8), (lx, yy + 8)], kind)
        text(c, lx + 33, yy - 2, name, 9)
    _layer(c, [(lx, T - 84), (lx + 26, T - 84), (lx + 26, T - 70), (lx, T - 70)], 'ash')
    text(c, lx + 33, T - 80, 'Bの層', 9)


def _nail_v(c, x, ytop, length):
    """頭が上、先が下の鉄くぎ。先の y を返す。"""
    setline(c, .9)
    c.setFillColor(PALE)
    c.rect(x - 8, ytop - 4, 16, 4, stroke=1, fill=1)
    c.rect(x - 2.2, ytop - 4 - length, 4.4, length, stroke=1, fill=1)
    tip = ytop - 4 - length
    c.drawPath(_poly(c, [(x - 2.2, tip), (x + 2.2, tip), (x, tip - 9)]), stroke=1, fill=1)
    return tip - 9


def fig_magnet(c, x, top, w, h):
    # 図1：棒磁石のN極に鉄くぎの頭をつける
    mx = x + 110
    text(c, x + 30, top - 14, '図1', 10, bold=True)
    my1, my0 = top - 8, top - 64
    setline(c, 1)
    c.setFillColor(colors.white)
    c.rect(mx - 13, (my0 + my1) / 2, 26, (my1 - my0) / 2, stroke=1, fill=1)
    c.setFillColor(SHADE)
    c.rect(mx - 13, my0, 26, (my1 - my0) / 2, stroke=1, fill=1)
    text(c, mx, (my0 + my1) / 2 + 9, 'S', 11, bold=True, center=True)
    text(c, mx, my0 + 9, 'N', 11, bold=True, center=True, color=colors.white)
    text(c, mx - 19 - tw('棒磁石', 8.5), (my0 + my1) / 2 - 3, '棒磁石', 8.5, color=MUTED)
    tip = _nail_v(c, mx, my0, 48)
    arrow(c, mx + 40, my0 - 6, mx + 10, my0 - 2, 5, .7, MUTED)
    text(c, mx + 43, my0 - 9, '頭', 8.5, color=MUTED)
    arrow(c, mx + 40, tip + 2, mx + 4, tip + 5, 5, .7, MUTED)
    text(c, mx + 43, tip - 1, '先', 8.5, color=MUTED)
    text(c, mx - 10 - tw('鉄くぎ', 8.5), my0 - 34, '鉄くぎ', 8.5, color=MUTED)
    # 図2：鉄くぎに巻いたコイルと方位磁針
    text(c, x + 250, top - 14, '図2', 10, bold=True)
    y = top - 46
    px0, px1 = x + 300, x + 420
    setline(c, .9)
    c.setFillColor(PALE)
    c.rect(px0 - 4, y - 8, 4, 16, stroke=1, fill=1)
    c.rect(px0, y - 3, px1 - px0, 6, stroke=1, fill=1)
    setline(c, 1.1, ACCENT)
    xs = [px0 + 14 + k * 9 for k in range(11)]
    for xx in xs:
        c.line(xx, y - 9, xx + 5, y + 9)
    yw = top - h + 22
    setline(c, 1)
    c.line(xs[0], y - 9, xs[0], yw)
    c.line(xs[-1] + 5, y - 9, xs[-1] + 5, yw)
    mid = (xs[0] + xs[-1] + 5) / 2
    c.line(xs[0], yw, mid - 26, yw)
    _battery_h(c, mid - 26, yw)
    c.line(mid - 21, yw, mid + 12, yw)
    _dot(c, mid + 12, yw)
    c.line(mid + 12, yw, mid + 32, yw + 2)          # スイッチ（入れたところ）
    _dot(c, mid + 32, yw)
    c.line(mid + 32, yw, xs[-1] + 5, yw)
    text(c, mid - 30, yw - 16, 'かん電池', 8.5, color=MUTED)
    text(c, mid + 12, yw - 16, 'スイッチ', 8.5, color=MUTED)
    text(c, px1 + 4, y + 9, 'Y', 10, bold=True, color=ACCENT)
    text(c, (px0 + px1) / 2 - 20, y + 15, 'コイル', 8.5, color=MUTED)
    # 方位磁針（黒いほうがN極。N極がYのほうを向いている）
    ox, r = px1 + 50, 15
    setline(c, .9)
    c.setFillColor(colors.white)
    c.circle(ox, y, r, stroke=1, fill=1)
    c.setFillColor(INK)
    c.drawPath(_poly(c, [(ox - r + 3, y), (ox, y + 3.5), (ox, y - 3.5)]), stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.drawPath(_poly(c, [(ox + r - 3, y), (ox, y + 3.5), (ox, y - 3.5)]), stroke=1, fill=1)
    text(c, ox, y - r - 12, '方位磁針', 8.5, color=MUTED, center=True)
    text(c, ox, y - r - 23, '（黒いほうがN極）', 8, color=MUTED, center=True)


def fig_lever(c, x, top, w, h, names=None):
    """実験用てこ。names=12文字を渡すと、穴の番号のかわりに、左から順に記号を書く。"""
    cx, u = x + w / 2, 28
    by = top - 34
    half = 6 * u + 14
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(cx - half, by - 4, 2 * half, 8, stroke=1, fill=1)
    # 支え
    c.setFillColor(colors.white)
    c.drawPath(_poly(c, [(cx, by - 4), (cx - 22, top - h + 10), (cx + 22, top - h + 10)]), stroke=1, fill=1)
    c.setFillColor(PALE)
    c.rect(cx - 40, top - h + 4, 80, 6, stroke=1, fill=1)
    _dot(c, cx, by)
    text(c, cx + 26, top - h + 20, '支点', 8.5, color=MUTED)
    for k in range(1, 7):
        for side in (-1, 1):
            hx = cx + side * k * u
            setline(c, .8)
            c.setFillColor(colors.white)
            c.circle(hx, by, 2.2, stroke=1, fill=1)
            c.line(hx, by - 4, hx, by - 11)
            c.arc(hx - 3, by - 17, hx + 3, by - 11, 180, 180)
            lab = str(k) if names is None else (names[6 - k] if side == -1 else names[5 + k])
            text(c, hx, by + 10, lab, 9, center=True)
    text(c, cx - half - 16, by - 4, '左', 10, bold=True)
    text(c, cx + half + 5, by - 4, '右', 10, bold=True)


# 三権分立の図の矢印（①〜⑥）。check_tenri_rs.py の検算もこの向きで作っている。
SANKEN_ARROWS = [('①', '国会', '内閣'), ('②', '内閣', '国会'), ('③', '国会', '裁判所'),
                 ('④', '裁判所', '国会'), ('⑤', '内閣', '裁判所'), ('⑥', '裁判所', '内閣')]


def fig_sanken(c, x, top, w, h):
    cx = x + w / 2
    bw, bh = 104, 28
    box = {'国会': (cx, top - 18), '内閣': (cx - 168, top - h + 20), '裁判所': (cx + 168, top - h + 20)}
    for name, (bx, by) in box.items():
        setline(c, 1)
        c.setFillColor(PALE)
        c.rect(bx - bw / 2, by - bh / 2, bw, bh, stroke=1, fill=1)
        text(c, bx, by - 4.5, name, 12, bold=True, center=True)

    def edge(p, q, gap=5):
        """箱pの中心から箱qの中心へ向かう線が、箱pのふちを出る点。"""
        (px, py), (qx, qy) = box[p], box[q]
        dx, dy = qx - px, qy - py
        t = min(bw / 2 / abs(dx) if dx else 9e9, bh / 2 / abs(dy) if dy else 9e9)
        L = math.hypot(dx, dy)
        return px + dx * t + dx / L * gap, py + dy * t + dy / L * gap

    def badge(x0, y0, lab, color, ring=True):
        """記号を、線の上に白い丸をしいて書く。①〜⑥は文字に丸があるので、外の丸線は引かない。"""
        c.setFillColor(colors.white)
        setline(c, .7, color)
        c.circle(x0, y0, 7.5, stroke=1 if ring else 0, fill=1)
        text(c, x0, y0 - 3.8, lab, 10, bold=True, color=color, center=True)

    for lab, p, q in SANKEN_ARROWS:
        (px, py), (qx, qy) = box[p], box[q]
        L = math.hypot(qx - px, qy - py)
        # 組（p, q）ごとに、名前順で決めた向きの法線で左右に分ける
        a, b = sorted((p, q))
        (ax, ay), (bx2, by2) = box[a], box[b]
        nx, ny = -(by2 - ay) / L, (bx2 - ax) / L
        off = 7 * (1 if p == a else -1)
        x1, y1 = edge(p, q)
        x2, y2 = edge(q, p)
        x1, y1, x2, y2 = x1 + nx * off, y1 + ny * off, x2 + nx * off, y2 + ny * off
        arrow(c, x1, y1, x2, y2, 6, 1, INK)
        # 記号は矢印の出発点寄りに置く（同じ組の2本で位置がずれる）
        badge(x1 + (x2 - x1) * .3, y1 + (y2 - y1) * .3, lab, ACCENT, ring=False)
    # 国民
    gx, gy = cx, top - h / 2 - 6
    setline(c, 1)
    c.setFillColor(colors.white)
    c.ellipse(gx - 32, gy - 13, gx + 32, gy + 13, stroke=1, fill=1)
    text(c, gx, gy - 4.5, '国民', 11, bold=True, center=True)
    for lab, name, (sx, sy) in [('X', '国会', (gx, gy + 13)), ('Y', '内閣', (gx - 24, gy - 9)),
                                ('Z', '裁判所', (gx + 24, gy - 9))]:
        bx, by = box[name]
        if bx == gx:
            ex, ey = bx, by - bh / 2 - 3
        else:
            ex, ey = bx + (bw / 2 - 14) * (1 if bx < gx else -1), by + bh / 2 + 3
        setline(c, .8, MUTED, (3, 2))
        c.line(sx, sy, ex, ey)
        c.setDash()
        arrow(c, sx + (ex - sx) * .8, sy + (ey - sy) * .8, ex, ey, 5, .8, MUTED)
        badge((sx + ex) / 2, (sy + ey) / 2, lab, MUTED)


def fig_linegraph(c, x, top, w, h, pts=(), xmax=24, xstep=3, ymin=20, ymax=40, ystep=5, xlab='', ylab='', lines=None):
    """折れ線グラフ。pts は (横, 縦) の組。目盛りの数字だけで、点の値は書かない。
    lines=[(記号, 点のリスト), ...] を渡すと、線の種類をかえて何本も描き、右上に凡例を書く。"""
    gx0, gx1 = x + 120, x + 390
    gy0, gy1 = top - h + 30, top - 24

    def X(t): return gx0 + (gx1 - gx0) * t / xmax
    def Y(v): return gy0 + (gy1 - gy0) * (v - ymin) / (ymax - ymin)
    for v in range(ymin, ymax + 1, ystep):
        setline(c, .35, LINE)
        c.line(gx0, Y(v), gx1, Y(v))
        text(c, gx0 - 6 - tw(str(v), 8), Y(v) - 3, str(v), 8, color=MUTED)
    for t in range(0, xmax + 1, xstep):
        setline(c, .35, LINE)
        c.line(X(t), gy0, X(t), gy1)
        text(c, X(t), gy0 - 11, str(t), 8, color=MUTED, center=True)
    setline(c, 1, INK)
    c.line(gx0, gy0, gx1, gy0)
    c.line(gx0, gy0, gx0, gy1)
    text(c, gx0 - 30, gy1 + 13, ylab, 8.5)
    text(c, (gx0 + gx1) / 2, gy0 - 24, xlab, 8.5, center=True)
    styles = [(ACCENT, 1.8, None), (INK, 1.4, (4, 2.5)), (MUTED, 1.7, (1, 2.5))]
    for k, (lab, line) in enumerate(lines or [('', list(pts))]):
        col, lw, dash = styles[k % 3]
        setline(c, lw, col, dash)
        for (t1, v1), (t2, v2) in zip(line, line[1:]):
            c.line(X(t1), Y(v1), X(t2), Y(v2))
        c.setDash()
        c.setFillColor(col)
        for t, v in line:
            c.circle(X(t), Y(v), 2.2, stroke=0, fill=1)
        if lines:
            ly = gy1 - 9 - k * 13
            setline(c, lw, col, dash)
            c.line(gx1 - 62, ly + 3, gx1 - 40, ly + 3)
            c.setDash()
            text(c, gx1 - 34, ly, lab, 9.5, bold=True)


def fig_flower(c, x, top, w, h):
    """アサガオの花の縦の切り口。ア〜オの記号をつける。"""
    cx = x + w / 2
    yb = top - h + 14

    def funnel(k, fill):
        p = c.beginPath()
        p.moveTo(cx - 9 * k, yb + 26)
        p.curveTo(cx - 14 * k, yb + 52, cx - 44 * k, yb + 70, cx - 46 * k, yb + 104)
        p.lineTo(cx + 46 * k, yb + 104)
        p.curveTo(cx + 44 * k, yb + 70, cx + 14 * k, yb + 52, cx + 9 * k, yb + 26)
        p.close()
        c.setFillColor(fill)
        c.drawPath(p, fill=1, stroke=1)

    setline(c, .9)
    # がく（根もとの小さな葉）
    c.setFillColor(LINE)
    for sd in (-1, 1):
        c.drawPath(_poly(c, [(cx + sd * 4, yb + 6), (cx + sd * 30, yb + 22), (cx + sd * 10, yb + 24)]), fill=1, stroke=1)
    funnel(1, PALE)
    funnel(.8, colors.white)
    # おしべ（先にやくがある）
    for xs in (-16, -8, 10, 17):
        setline(c, .9)
        c.line(cx + xs * .4, yb + 32, cx + xs, yb + 70)
        c.setFillColor(SHADE)
        c.ellipse(cx + xs - 3.4, yb + 69, cx + xs + 3.4, yb + 76, stroke=1, fill=1)
    # めしべ（子房・花柱・柱頭）
    setline(c, 1.1)
    c.line(cx, yb + 24, cx, yb + 88)
    c.setFillColor(colors.white)
    c.circle(cx, yb + 16, 9, stroke=1, fill=1)
    c.circle(cx, yb + 90, 3.6, stroke=1, fill=1)
    # 記号と引き出し線
    def mark(lab, lx, ly, tx, ty):
        setline(c, .6, MUTED)
        c.line(lx, ly + 3.5, tx, ty)
        text(c, lx, ly, lab, 10.5, bold=True, color=ACCENT, center=True)

    mark('ア', cx - 62, yb + 10, cx - 24, yb + 15)
    mark('イ', cx - 64, yb + 84, cx - 40, yb + 90)
    mark('ウ', cx + 62, yb + 60, cx + 21, yb + 72)
    mark('エ', cx + 36, yb + 118, cx + 3, yb + 92)
    mark('オ', cx + 38, yb + 6, cx + 9, yb + 14)


def fig_syringe(c, x, top, w, h):
    """空気と水を入れた注射器。ピストンは100mLの目盛りまで引いてある。"""
    base = top - h + 22
    bh = 62
    for cx, kind, lab in ((x + w / 2 - 90, 'air', '空気'), (x + w / 2 + 90, 'water', '水')):
        y0, y1 = base + 10, base + 10 + bh
        setline(c, 1)
        c.setFillColor(colors.white)
        c.rect(cx - 2.5, base, 5, 10, stroke=1, fill=1)
        c.setFillColor(PALE if kind == 'water' else colors.white)
        c.rect(cx - 20, y0, 40, bh, stroke=1, fill=1)
        if kind == 'air':
            c.setFillColor(SHADE)
            for r, yy in enumerate(range(int(y0) + 6, int(y1) - 2, 9)):
                for xx in range(int(cx) - 14 + (r % 2) * 6, int(cx) + 16, 12):
                    c.circle(xx, yy, .9, stroke=0, fill=1)
        c.setFillColor(colors.white)
        c.rect(cx - 5, y1, 10, 24, stroke=1, fill=1)
        c.rect(cx - 16, y1 + 24, 32, 5, stroke=1, fill=1)
        c.setFillColor(INK)
        c.rect(cx - 20, y1 - 3, 40, 3, stroke=0, fill=1)        # ピストンのゴム
        for k, v in enumerate(range(0, 101, 20)):
            yy = y0 + bh * v / 100
            setline(c, .6, MUTED)
            c.line(cx - 20, yy, cx - 25, yy)
            text(c, cx - 28 - tw(str(v), 8), yy - 3, str(v), 8, color=MUTED)
        text(c, cx, base - 12, lab, 10, bold=True, center=True)
        arrow(c, cx, y1 + 52, cx, y1 + 34, 5, 1, ACCENT)
        text(c, cx + 14, y1 + 40, 'おす', 8.5, color=ACCENT)
    text(c, x + w / 2, base + 12, '目盛りの単位は mL', 8.5, color=MUTED, center=True)


def fig_typhoon(c, x, top, w, h):
    """北半球の台風。風は中心に向かって反時計回りにふきこむ。A・Bは進行方向のどちら側か。"""
    cx, cy = x + w / 2 - 40, top - h / 2
    for r in (26, 46, 66):
        setline(c, .6, LINE, (3, 2))
        c.circle(cx, cy, r, stroke=1, fill=0)
    c.setDash()
    for r, off in ((56, 0), (36, 22.5)):
        for k in range(8):
            th = math.radians(off + k * 45)
            px, py = cx + r * math.cos(th), cy + r * math.sin(th)
            tx, ty = -math.sin(th), math.cos(th)          # 反時計回り
            ix, iy = -math.cos(th), -math.sin(th)         # 中心に向かう
            vx, vy = .85 * tx + .45 * ix, .85 * ty + .45 * iy
            arrow(c, px - vx * 8, py - vy * 8, px + vx * 8, py + vy * 8, 5, .9, ACCENT)
    setline(c, 1)
    c.setFillColor(colors.white)
    c.circle(cx, cy, 8, stroke=1, fill=1)
    ax = cx + 125
    arrow(c, ax, cy - 32, ax, cy + 36, 7, 1.6, INK)
    text(c, ax + 10, cy - 2, '台風の進行方向', 9)
    for lab, px in (('A', cx + 88), ('B', cx - 88)):
        setline(c, 1)
        c.setFillColor(PALE)
        c.circle(px, cy, 9, stroke=1, fill=1)
        text(c, px, cy - 3.6, lab, 10, bold=True, center=True)


def fig_world(c, x, top, w, h, marks=(), japan_label=True):
    """世界の略地図（正距円筒図法）。marks は (記号, 経度, 緯度) または (記号, 経度, 緯度, 文字の右へ, 上へ)。"""
    from world_outline import RINGS
    lat_top, lat_bot = 84, -56
    sc = min(w / 360, (h - 16) / (lat_top - lat_bot))
    x0 = x + (w - 360 * sc) / 2
    y0 = top - 4

    def X(lon): return x0 + (lon + 180) * sc
    def Y(lat): return y0 - (lat_top - lat) * sc
    # 緯線・経線
    for lat in range(-30, 91, 30):
        if lat > lat_top:
            continue
        setline(c, .35, LINE, (2, 2) if lat else None)
        c.line(X(-180), Y(lat), X(180), Y(lat))
        lab = f'{abs(lat)}' + ('N' if lat > 0 else 'S' if lat < 0 else '')
        text(c, X(-180) - 3 - tw(lab, 7), Y(lat) - 2.5, lab, 7, color=MUTED)
    for lon in range(-180, 181, 60):
        setline(c, .35, LINE, (2, 2))
        c.line(X(lon), Y(lat_top), X(lon), Y(lat_bot))
        lab = f'{abs(lon)}' + ('E' if 0 < lon < 180 else 'W' if -180 < lon < 0 else '')
        text(c, X(lon), Y(lat_bot) - 10, lab, 7, color=MUTED, center=True)
    c.setDash()
    setline(c, .9, MUTED)
    c.line(X(-180), Y(0), X(180), Y(0))
    text(c, X(180) - 28, Y(0) + 2.5, '赤道', 7.5, color=MUTED)
    # 陸地
    for name, pts in RINGS:
        p = c.beginPath()
        p.moveTo(X(pts[0][0] / 10), Y(pts[0][1] / 10))
        for lon10, lat10 in pts[1:]:
            p.lineTo(X(lon10 / 10), Y(lat10 / 10))
        p.close()
        c.setFillColor(SHADE if name == 'Japan' else PALE)
        setline(c, .3, SHADE)
        c.drawPath(p, fill=1, stroke=1)
    if japan_label:
        text(c, X(140), Y(35) - 15, '日本', 8, bold=True, color=INK)
    # 印
    for m in marks:
        lab, lon, lat = m[:3]
        px, py = X(lon) + (m[3] if len(m) > 3 else 0), Y(lat) + (m[4] if len(m) > 4 else 0)
        c.setFillColor(colors.white)
        setline(c, .9, ACCENT)
        c.circle(px, py, 6.4, stroke=1, fill=1)
        text(c, px, py - 3.5, lab, 9.5, bold=True, color=ACCENT, center=True)


def fig_cloudmaps(c, x, top, w, h, blobs=(), labels='アイウエ'):
    """日本付近の雲の画像（気象衛星の画像のかわりの略図）。blobs は (経度, 緯度, 横の半径度, 縦の半径度)。"""
    from world_outline import RINGS
    n = len(blobs)
    gap = 8
    lon0, lon1, lat0, lat1 = 118, 152, 27, 47
    slot = (w - gap * (n - 1)) / n
    sx = sy = min(slot / (lon1 - lon0), (h - 18) / (lat1 - lat0))
    fw, fh = (lon1 - lon0) * sx, (lat1 - lat0) * sy
    for k, (lon, lat, rx, ry) in enumerate(blobs):
        fx0, fy0 = x + k * (slot + gap) + (slot - fw) / 2, top - 16 - fh

        def X(l): return fx0 + (l - lon0) * sx
        def Y(a): return fy0 + (a - lat0) * sy
        c.saveState()
        clip = c.beginPath()
        clip.rect(fx0, fy0, fw, fh)
        c.clipPath(clip, stroke=0, fill=0)
        c.setFillColor(colors.HexColor('#6F7E8B'))
        c.rect(fx0, fy0, fw, fh, stroke=0, fill=1)
        for name, pts in RINGS:
            pp = c.beginPath()
            pp.moveTo(X(pts[0][0] / 10), Y(pts[0][1] / 10))
            for lon10, lat10 in pts[1:]:
                pp.lineTo(X(lon10 / 10), Y(lat10 / 10))
            pp.close()
            c.setFillColor(colors.HexColor('#B6BEB0'))
            c.drawPath(pp, stroke=0, fill=1)
        c.setFillAlpha(.93)
        c.setFillColor(colors.white)
        for dx, dy, f in ((0, 0, 1), (-rx * .55, ry * .25, .7), (rx * .6, -ry * .2, .75), (rx * .1, ry * .55, .6)):
            c.ellipse(X(lon + dx - rx * f), Y(lat + dy - ry * f), X(lon + dx + rx * f), Y(lat + dy + ry * f), stroke=0, fill=1)
        c.setFillAlpha(1)
        c.restoreState()
        setline(c, .9)
        c.rect(fx0, fy0, fw, fh, stroke=1, fill=0)
        text(c, fx0 + fw / 2, top - 11, labels[k], 11, bold=True, center=True)


def fig_seed(c, x, top, w, h):
    """インゲンマメの種子を、半分に開いたようす。ア種皮・イ子葉・ウはい。"""
    cx, cy = x + w / 2, top - h / 2 - 2
    a, b = 74, 36
    setline(c, 1.4)
    c.setFillColor(SHADE)
    c.ellipse(cx - a, cy - b, cx + a, cy + b, stroke=1, fill=1)          # 種皮
    c.setFillColor(PALE)
    setline(c, .9)
    c.ellipse(cx - a + 5, cy - b + 5, cx + a - 5, cy + b - 5, stroke=1, fill=1)   # 子葉
    setline(c, .7, MUTED, (3, 2))
    c.line(cx - a + 8, cy, cx + a - 8, cy)
    c.setDash()
    c.setFillColor(INK)
    c.ellipse(cx - a + 12, cy + 7, cx - a + 34, cy + 15, stroke=0, fill=1)     # はい
    setline(c, .6, MUTED)

    def mark(lab, lx, ly, tx, ty):
        c.line(lx, ly + 3.5, tx, ty)
        text(c, lx, ly, lab, 10.5, bold=True, color=ACCENT, center=True)

    mark('ア', cx + a + 24, cy + 14, cx + a - 2, cy + 8)
    mark('イ', cx + 28, cy - b - 18, cx + 22, cy - 18)
    mark('ウ', cx - a - 8, cy + 30, cx - a + 14, cy + 12)


def fig_sao(c, x, top, w, h, plate=5, pos=20, weight='60g', maxpos=50):
    """さおばかり。支点からさらまでplate(cm)、おもりは支点から右へpos(cm)のところにつるす。"""
    sc = 6.0
    xf = x + 52 + plate * sc
    yr = top - 56
    xl, xr = xf - plate * sc - 6, xf + maxpos * sc + 8
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(xl, yr - 3.5, xr - xl, 7, stroke=1, fill=1)
    for k in range(0, maxpos + 1, 5):
        setline(c, .7, INK)
        c.line(xf + k * sc, yr + 3.5, xf + k * sc, yr + (8 if k % 10 == 0 else 6))
        if k % 10 == 0:
            text(c, xf + k * sc, yr + 11, str(k), 8, color=MUTED, center=True)
    text(c, xr - 10, yr + 23, '(cm)', 8, color=MUTED)
    # 支点
    setline(c, 1)
    c.line(xf, yr + 3.5, xf, yr + 28)
    c.circle(xf, yr + 31, 3, stroke=1, fill=0)
    text(c, xf + 7, yr + 26, '支点', 8.5, color=MUTED)
    # さら
    px = xl + 3
    setline(c, .9)
    c.line(px, yr - 3.5, px - 14, yr - 38)
    c.line(px, yr - 3.5, px + 14, yr - 38)
    c.setFillColor(colors.white)
    c.rect(px - 20, yr - 42, 40, 4, stroke=1, fill=1)
    text(c, px - 26 - tw('さら', 8.5), yr - 42, 'さら', 8.5, color=MUTED)
    setline(c, .6, MUTED)
    c.line(xf, yr - 12, px, yr - 12)
    arrow(c, (xf + px) / 2, yr - 12, px + 1, yr - 12, 4, .6, MUTED)
    arrow(c, (xf + px) / 2, yr - 12, xf - 1, yr - 12, 4, .6, MUTED)
    text(c, (xf + px) / 2, yr - 24, f'{plate}cm', 8.5, color=MUTED, center=True)
    # おもり
    wx = xf + pos * sc
    setline(c, .9)
    c.line(wx, yr - 3.5, wx, yr - 24)
    c.setFillColor(SHADE)
    c.rect(wx - 12, yr - 44, 24, 20, stroke=1, fill=1)
    text(c, wx, yr - 38, weight, 9, bold=True, color=colors.white, center=True)


def fig_stem(c, x, top, w, h):
    """茎の横断面。Aは管が輪のようにならぶ。Bは管が全体に散らばる。"""
    r, cy = 40, top - h / 2 - 4
    scatter = [(-18, 14), (6, 20), (22, 8), (-4, 2), (14, -12), (-22, -8), (-8, -22), (26, -22), (0, 24), (-26, 22),
               (28, 24), (-14, -2), (8, -28), (20, 28), (-30, 0), (30, 0), (-2, -12), (16, 6)]
    for cx, lab, kind in ((x + w / 2 - 90, 'A', 'ring'), (x + w / 2 + 90, 'B', 'scatter')):
        setline(c, 1.1)
        c.setFillColor(PALE)
        c.circle(cx, cy, r, stroke=1, fill=1)
        c.setFillColor(SHADE)
        setline(c, .8)
        if kind == 'ring':
            for k in range(10):
                t = math.radians(k * 36)
                c.circle(cx + 26 * math.cos(t), cy + 26 * math.sin(t), 3.6, stroke=1, fill=1)
        else:
            for dx, dy in scatter:
                c.circle(cx + dx * .95, cy + dy * .95, 3.2, stroke=1, fill=1)
        text(c, cx, cy - r - 13, lab, 11, bold=True, center=True)
    text(c, x + w / 2, cy - 4, '●が管のあと', 8.5, color=MUTED, center=True)


def fig_circuitset(c, x, top, w, h, specs=(), labels='アイウエオカ'):
    """豆電球とかん電池の回路を、ならべて描く。specs は (電池, 豆電球)。
    電池 = 'one' / 'series'（2個を直列）/ 'parallel'（2個を並列）、豆電球 = 'one' / 'series' / 'parallel' / 'none'（導線だけ）。"""
    n = len(specs)
    pw = w / n
    yb, yt = top - h + 14, top - 28
    for k, (cell, bulb) in enumerate(specs):
        px = x + k * pw
        x0, x1 = px + 16, px + pw - 16
        mid = (x0 + x1) / 2
        text(c, mid, top - 12, labels[k], 11, bold=True, center=True)
        setline(c, 1)
        ybots = [yb] if cell != 'parallel' else [yb, yb + 18]
        ytops = [yt] if bulb != 'parallel' else [yt, yt - 18]
        c.line(x0, min(ybots), x0, max(ytops))
        c.line(x1, min(ybots), x1, max(ytops))
        for yy in ybots:
            setline(c, 1)
            if cell == 'series':
                bx = mid - 12
                c.line(x0, yy, bx, yy)
                _battery_h(c, bx, yy, 2)
                setline(c, 1)
                c.line(bx + 19, yy, x1, yy)
            else:
                bx = mid - 2.5
                c.line(x0, yy, bx, yy)
                _battery_h(c, bx, yy, 1)
                setline(c, 1)
                c.line(bx + 5, yy, x1, yy)
        setline(c, 1)
        for yy in ytops:
            c.line(x0, yy, x1, yy)
            if bulb == 'series':
                for bxx in (x0 + (x1 - x0) * .3, x0 + (x1 - x0) * .7):
                    _bulb(c, bxx, yy, 6.5)
            elif bulb != 'none':
                _bulb(c, mid, yy, 6.5)
        if cell == 'parallel':
            for xx in (x0, x1):
                _dot(c, xx, yb)
                _dot(c, xx, yb + 18)
        if bulb == 'parallel':
            for xx in (x0, x1):
                _dot(c, xx, yt)
                _dot(c, xx, yt - 18)
    text(c, x + w / 2, top - h - 5, '記号：長い線と短い線の組がかん電池（長い線が＋極）、丸に×が豆電球。', 8.5, color=MUTED, center=True)


def fig_ammeter(c, x, top, w, h, value=3.2, vmax=5):
    """電流計の目盛り板と針（0〜vmax）。値は図の針の位置だけで示す。"""
    R = min(w / 2 - 16, 84)
    cx, cy = x + w / 2, top - R - 12
    a0, a1 = 150, 30                                  # 目盛りの左端と右端の角度
    setline(c, 1)
    c.arc(cx - R, cy - R, cx + R, cy + R, a1, a0 - a1)
    n = int(round(vmax * 10))
    for k in range(n + 1):
        ang = math.radians(a0 - (a0 - a1) * k / n)
        ln = 10 if k % 10 == 0 else 7 if k % 5 == 0 else 4
        setline(c, .9 if k % 5 == 0 else .5)
        c.line(cx + R * math.cos(ang), cy + R * math.sin(ang), cx + (R - ln) * math.cos(ang), cy + (R - ln) * math.sin(ang))
        if k % 10 == 0:
            text(c, cx + (R + 9) * math.cos(ang), cy + (R + 9) * math.sin(ang) - 3.5, str(k // 10), 9, center=True)
    ang = math.radians(a0 - (a0 - a1) * value / vmax)
    setline(c, 1.4, ACCENT)
    c.line(cx, cy, cx + (R - 6) * math.cos(ang), cy + (R - 6) * math.sin(ang))
    c.setFillColor(INK)
    c.circle(cx, cy, 3.4, stroke=0, fill=1)
    text(c, cx, cy - 22, 'A', 12, bold=True, center=True)


def fig_circulation(c, x, top, w, h):
    """血液の流れ。肺・心臓・全身の間を、ア〜エの血管がつなぐ。"""
    cx, cy = x + w / 2, top - h / 2 - 2
    bw, bh, gap = 76, 40, 92
    boxes = {'肺': cx - bw - gap, '心臓': cx - bw / 2, '全身': cx + gap}
    for name, bx in boxes.items():
        setline(c, 1)
        c.setFillColor(PALE)
        c.rect(bx, cy - bh / 2, bw, bh, stroke=1, fill=1)
        text(c, bx + bw / 2, cy - 4.5, name if name != '全身' else '全身', 12, bold=True, center=True)

    def edge(lab, xs, xe, y):
        arrow(c, xs, y, xe, y, 7, 1.1, INK)
        mx = (xs + xe) / 2
        c.setFillColor(colors.white)
        setline(c, .7, ACCENT)
        c.circle(mx, y + (11 if y > cy else -11), 7.4, stroke=1, fill=1)
        text(c, mx, y + (11 if y > cy else -11) - 3.6, lab, 10, bold=True, color=ACCENT, center=True)

    l0, l1 = boxes['肺'] + bw, boxes['心臓']
    r0, r1 = boxes['心臓'] + bw, boxes['全身']
    edge('ア', l1 - 2, l0 + 2, cy + 10)           # 心臓→肺
    edge('イ', l0 + 2, l1 - 2, cy - 10)           # 肺→心臓
    edge('ウ', r0 + 2, r1 - 2, cy + 10)           # 心臓→全身
    edge('エ', r1 - 2, r0 + 2, cy - 10)           # 全身→心臓


def fig_cans(c, x, top, w, h, specs=(), labels='アイウエ'):
    """空きかんの中で木の棒を燃やす。specs は (上にふたがあるか, 底に穴があるか)。"""
    n = len(specs)
    pw = w / n
    cw, ch = 44, 58
    yb = top - h + 16
    for k, (lid, hole) in enumerate(specs):
        cx = x + k * pw + pw / 2
        text(c, cx, top - 11, labels[k], 11, bold=True, center=True)
        setline(c, 1.3)
        c.line(cx - cw / 2, yb + ch, cx - cw / 2, yb)
        c.line(cx + cw / 2, yb + ch, cx + cw / 2, yb)
        if hole:
            c.line(cx - cw / 2, yb, cx - 5, yb)
            c.line(cx + 5, yb, cx + cw / 2, yb)
        else:
            c.line(cx - cw / 2, yb, cx + cw / 2, yb)
        if lid:
            c.setFillColor(INK)
            c.rect(cx - cw / 2 - 2, yb + ch, cw + 4, 3.5, stroke=0, fill=1)
        setline(c, 2.2, MUTED)
        c.line(cx, yb + 3, cx, yb + 34)                                   # 木の棒
        c.setFillColor(colors.HexColor('#C9822B'))
        c.drawPath(_poly(c, [(cx - 4.5, yb + 34), (cx + 4.5, yb + 34), (cx, yb + 48)]), stroke=0, fill=1)   # 炎
    text(c, x + w / 2, top - h + 3, '黒い線はふた。底の切れ目は穴。', 8.5, color=MUTED, center=True)


def fig_mirror(c, x, top, w, h, angle=30):
    """鏡に当たる光と、はね返る光。入射角にだけ角度を書く。"""
    cx, my = x + w / 2, top - h + 26
    L = 66
    setline(c, 1.6)
    c.line(cx - 62, my, cx + 62, my)
    setline(c, .5)
    for k in range(-60, 62, 7):
        c.line(cx + k, my, cx + k - 5, my - 6)
    setline(c, .7, MUTED, (3, 2))
    c.line(cx, my, cx, my + L + 10)
    c.setDash()
    t = math.radians(angle)
    arrow(c, cx - L * math.sin(t), my + L * math.cos(t), cx - 4 * math.sin(t), my + 4 * math.cos(t), 7, 1.2, INK)
    arrow(c, cx, my, cx + L * math.sin(t), my + L * math.cos(t), 7, 1.2, INK)
    setline(c, .8, ACCENT)
    c.arc(cx - 26, my - 26, cx + 26, my + 26, 90, angle)
    text(c, cx - 30 - tw(f'{angle}°', 9) + 8, my + 28, f'{angle}°', 9, bold=True, color=ACCENT)
    c.setFillColor(colors.white)
    setline(c, .7, ACCENT)
    c.circle(cx + 33, my + 33, 8, stroke=1, fill=1)
    text(c, cx + 33, my + 33 - 3.6, '?', 10, bold=True, color=ACCENT, center=True)
    text(c, cx - L * math.sin(t) - 6, my + L * math.cos(t) + 4, '日光', 8.5, color=MUTED, center=True)


def fig_digest(c, x, top, w, h):
    """食べ物の通り道の略図。ア口・イ肝臓・ウ食道・エ胃・オ小腸・カ大腸。"""
    cx = x + w / 2
    y0 = top - 6
    setline(c, 1)
    c.setFillColor(PALE)
    c.ellipse(cx - 15, y0 - 20, cx + 15, y0 - 4, stroke=1, fill=1)             # 口
    setline(c, 1.8)
    c.line(cx, y0 - 20, cx, y0 - 52)                                             # 食道
    setline(c, 1)
    c.setFillColor(PALE)
    c.ellipse(cx + 2, y0 - 82, cx + 44, y0 - 50, stroke=1, fill=1)               # 胃
    c.setFillColor(SHADE)
    c.ellipse(cx - 62, y0 - 76, cx - 4, y0 - 52, stroke=1, fill=1)               # 肝臓
    # 大腸（小腸を囲む）
    setline(c, 5, LINE)
    c.line(cx - 40, y0 - 128, cx - 40, y0 - 86)
    c.line(cx - 40, y0 - 86, cx + 40, y0 - 86)
    c.line(cx + 40, y0 - 86, cx + 40, y0 - 128)
    setline(c, 1.2, MUTED)
    c.line(cx - 43.5, y0 - 128, cx - 43.5, y0 - 83)
    c.line(cx - 43.5, y0 - 83, cx + 43.5, y0 - 83)
    c.line(cx + 43.5, y0 - 83, cx + 43.5, y0 - 128)
    setline(c, 5, LINE)
    c.line(cx + 40, y0 - 128, cx + 12, y0 - 138)
    c.line(cx + 12, y0 - 138, cx + 12, y0 - 150)
    setline(c, 1.2, MUTED)
    c.line(cx + 43.5, y0 - 128, cx + 15, y0 - 140)
    c.line(cx + 8.5, y0 - 138, cx + 8.5, y0 - 150)
    # 小腸
    setline(c, 1.4, INK)
    pts = []
    for k in range(7):
        yy = y0 - 94 - k * 5.4
        pts += [(cx - 28, yy), (cx + 28, yy)] if k % 2 == 0 else [(cx + 28, yy), (cx - 28, yy)]
    for (xa, ya), (xb, yb) in zip(pts, pts[1:]):
        c.line(xa, ya, xb, yb)
    c.line(cx, y0 - 52, cx + 23, y0 - 82)

    def mark(lab, lx, ly, tx, ty):
        setline(c, .6, MUTED)
        c.line(lx, ly + 3.5, tx, ty)
        text(c, lx, ly, lab, 10.5, bold=True, color=ACCENT, center=True)

    mark('ア', cx + 40, y0 - 14, cx + 15, y0 - 12)
    mark('イ', cx - 84, y0 - 62, cx - 58, y0 - 64)
    mark('ウ', cx + 20, y0 - 36, cx + 2, y0 - 36)
    mark('エ', cx + 66, y0 - 70, cx + 44, y0 - 68)
    mark('オ', cx + 70, y0 - 112, cx + 28, y0 - 108)
    mark('カ', cx - 70, y0 - 112, cx - 42, y0 - 108)


def fig_watercycle(c, x, top, w, h):
    """水のじゅんかん。ア蒸発・イ雲・ウ雨・エ川・オ地下水。"""
    cx = x + w / 2
    yb = top - h + 8
    # 海
    sx0, sx1 = cx - 190, cx - 40
    c.setFillColor(colors.HexColor('#C9D6DF'))
    setline(c, .8)
    c.rect(sx0, yb, sx1 - sx0, 30, stroke=1, fill=1)
    setline(c, .6, MUTED)
    for k in range(5):
        c.line(sx0 + 14 + k * 28, yb + 20, sx0 + 26 + k * 28, yb + 20)
    text(c, (sx0 + sx1) / 2, yb + 6, '海', 9, color=MUTED, center=True)
    # 山と地面
    c.setFillColor(PALE)
    setline(c, 1)
    c.drawPath(_poly(c, [(sx1, yb + 30), (cx + 18, yb + 30), (cx + 60, yb + 84), (cx + 100, yb + 30), (cx + 190, yb + 30), (cx + 190, yb), (sx1, yb)]), stroke=1, fill=1)
    # 川
    setline(c, 2.2, colors.HexColor('#7F96A8'))
    c.line(cx + 50, yb + 70, cx + 30, yb + 44)
    c.line(cx + 30, yb + 44, cx + 10, yb + 34)
    c.line(cx + 10, yb + 34, sx1 + 2, yb + 28)
    # 雲
    c.setFillColor(colors.white)
    setline(c, 1)
    for dx, dy, r in ((-18, 0, 13), (0, 6, 16), (20, 0, 13), (4, -3, 15)):
        c.circle(cx - 20 + dx, yb + 112 + dy, r, stroke=1, fill=1)
    c.setFillColor(colors.white)
    for dx, dy, r in ((-18, 0, 12.4), (0, 6, 15.4), (20, 0, 12.4), (4, -3, 14.4)):
        c.circle(cx - 20 + dx, yb + 112 + dy, r, stroke=0, fill=1)
    # 雨
    setline(c, .9, MUTED)
    for k in range(4):
        c.line(cx - 6 + k * 12, yb + 98, cx - 12 + k * 12, yb + 80)
    # 蒸発（海から雲へ）
    for k in range(3):
        xx = sx0 + 36 + k * 40
        arrow(c, xx, yb + 32, xx + 4, yb + 74, 5, .8, MUTED)
    # 地下水
    arrow(c, cx + 60, yb + 14, cx + 4, yb + 14, 5, .9, MUTED)

    def mark(lab, mx, my):
        c.setFillColor(colors.white)
        setline(c, .7, ACCENT)
        c.circle(mx, my, 7.4, stroke=1, fill=1)
        text(c, mx, my - 3.6, lab, 10, bold=True, color=ACCENT, center=True)

    mark('ア', sx0 + 78, yb + 58)
    mark('イ', cx - 20, yb + 112)
    mark('ウ', cx + 40, yb + 90)
    mark('エ', cx + 18, yb + 48)
    mark('オ', cx + 32, yb + 14)


def fig_pulleys(c, x, top, w, h):
    """ひもと滑車。ア定滑車、イ動滑車、ウ動滑車と定滑車のくみ合わせ。荷物は60kg。"""
    pw = w / 3
    yc = top - 6                                    # 天井の下の線
    ypul = yc - 24
    ymov = top - 82
    r = 9

    def ceiling(cx):
        setline(c, 1.6)
        c.line(cx - 48, yc, cx + 48, yc)
        setline(c, .5)
        for k in range(-48, 48, 8):
            c.line(cx + k, yc, cx + k + 5, yc + 6)

    def pulley(px, py):
        setline(c, 1)
        c.setFillColor(PALE)
        c.circle(px, py, r, stroke=1, fill=1)
        c.setFillColor(INK)
        c.circle(px, py, 1.6, stroke=0, fill=1)

    def box(bx, by):
        setline(c, 1)
        c.setFillColor(SHADE)
        c.rect(bx - 14, by - 18, 28, 18, stroke=1, fill=1)
        text(c, bx, by - 13, '60kg', 8.5, bold=True, color=colors.white, center=True)

    for k, lab in enumerate('アイウ'):
        cx = x + k * pw + pw / 2
        ceiling(cx)
        text(c, cx, top - h + 4, lab, 11, bold=True, center=True)
        setline(c, 1)
        if lab == 'ア':
            px = cx
            c.line(px, yc, px, ypul + r + 3)
            pulley(px, ypul)
            c.line(px - r, ypul, px - r, ymov - 8)            # 荷物側
            box(px - r, ymov - 8)
            c.line(px + r, ypul, px + r, ymov + 14)           # 引く側
            arrow(c, px + r, ymov + 14, px + r, ymov - 8, 7, 1.3, ACCENT)
        elif lab == 'イ':
            px = cx
            c.line(px - r, yc, px - r, ymov)                  # 天井にとめたひも
            pulley(px, ymov)
            c.arc(px - r, ymov - r, px + r, ymov + r, 180, 180)
            c.line(px + r, ymov, px + r, ypul + 6)
            arrow(c, px + r, ypul + 6, px + r, ypul + 24, 7, 1.3, ACCENT)
            c.line(px, ymov - r, px, ymov - r - 4)
            box(px, ymov - r - 4)
        else:
            fx = cx + 12
            mx = fx - 2 * r
            c.line(mx - r, yc, mx - r, ymov)
            pulley(mx, ymov)
            c.arc(mx - r, ymov - r, mx + r, ymov + r, 180, 180)
            c.line(mx + r, ymov, mx + r, ypul)
            c.line(fx, yc, fx, ypul + r + 3)
            pulley(fx, ypul)
            c.line(fx + r, ypul, fx + r, ymov + 14)
            arrow(c, fx + r, ymov + 14, fx + r, ymov - 8, 7, 1.3, ACCENT)
            c.line(mx, ymov - r, mx, ymov - r - 4)
            box(mx, ymov - r - 4)


def fig_shadow(c, x, top, w, h):
    """棒のかげを上から見た図。ア・イ・ウは午前9時・正午・午後3時のかげのどれか。"""
    cx, cy = x + w / 2, top - h / 2 - 4
    R = 54
    setline(c, .7, LINE, (3, 2))
    c.circle(cx, cy, R, stroke=1, fill=0)
    c.setDash()
    for lab, dx, dy in (('北', 0, R + 10), ('南', 0, -R - 17), ('東', R + 14, -3.5), ('西', -R - 14, -3.5)):
        text(c, cx + dx, cy + dy, lab, 10, bold=True, color=MUTED, center=True)
    for lab, ang, ln in (('ア', 150, 50), ('イ', 90, 26), ('ウ', 30, 50)):
        t = math.radians(ang)
        setline(c, 2, ACCENT)
        c.line(cx, cy, cx + ln * math.cos(t), cy + ln * math.sin(t))
        text(c, cx + (ln + 9) * math.cos(t), cy + (ln + 9) * math.sin(t) - 3.6, lab, 10.5, bold=True, color=ACCENT, center=True)
    c.setFillColor(INK)
    c.circle(cx, cy, 3.6, stroke=0, fill=1)
    text(c, cx + 8, cy - 14, '棒', 8.5, color=MUTED)


def fig_leverbar(c, x, top, w, h, pts=(), fulcrum='B', dist=True):
    """棒の上の点 pts=(記号, 左はしからの長さcm) と支点。点の間の長さを下に書く。"""
    xs = [p for _, p in pts]
    lo, hi = min(xs), max(xs)
    scale = min(300, w - 160) / (hi - lo)
    x0 = x + (w - (hi - lo) * scale) / 2
    X = lambda p: x0 + (p - lo) * scale
    by = top - 44
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(X(lo) - 14, by - 4, (hi - lo) * scale + 28, 8, stroke=1, fill=1)
    fp = dict(pts)[fulcrum]
    c.setFillColor(colors.white)
    c.drawPath(_poly(c, [(X(fp), by - 4), (X(fp) - 15, by - 34), (X(fp) + 15, by - 34)]), stroke=1, fill=1)
    for lab, p in pts:
        _dot(c, X(p), by)
        text(c, X(p), by + 9, lab, 11, bold=True, center=True)
    if dist:
        ys = by - 50
        ps = sorted(p for _, p in pts)
        for a, b in zip(ps, ps[1:]):
            setline(c, .7, ACCENT)
            c.line(X(a), ys, X(b), ys)
            c.line(X(a), ys - 3, X(a), ys + 3)
            c.line(X(b), ys - 3, X(b), ys + 3)
            text(c, (X(a) + X(b)) / 2, ys - 12, f'{b - a:g}cm', 9, color=ACCENT, center=True)


def fig_balance(c, x, top, w, h, tilt='level', left='', right=''):
    """上皿てんびん。tilt は 'level'（つり合い）・'left'（左の皿が下がる）・'right'（右の皿が下がる）。"""
    cx = x + w / 2
    by = top - h + 8
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(cx - 34, by, 68, 7, stroke=1, fill=1)
    c.rect(cx - 3, by + 7, 6, 56, stroke=1, fill=1)
    py = by + 66
    half, d = 80, {'level': 0, 'left': 8, 'right': -8}[tilt]
    ly, ry = py - d, py + d
    setline(c, 2.2)
    c.line(cx - half, ly, cx + half, ry)
    c.setFillColor(INK)
    c.circle(cx, py, 3, stroke=0, fill=1)
    a = math.atan2(d, half)
    setline(c, 1.1, ACCENT)
    c.line(cx, py, cx + 20 * math.sin(a), py - 20 * math.cos(a))               # 針
    setline(c, .7, MUTED)
    c.line(cx, by + 40, cx, by + 46)
    for ex, ey, lab in ((cx - half, ly, left), (cx + half, ry, right)):
        setline(c, .8)
        c.line(ex, ey, ex - 24, ey - 20)
        c.line(ex, ey, ex + 24, ey - 20)
        c.setFillColor(PALE)
        c.drawPath(_poly(c, [(ex - 28, ey - 20), (ex + 28, ey - 20), (ex + 22, ey - 26), (ex - 22, ey - 26)]), stroke=1, fill=1)
        text(c, ex, ey - 39, lab, 9, center=True)


def fig_cylinder(c, x, top, w, h, levels=(32.0,), vmax=50, labels='アイウエ'):
    """メスシリンダー。levels は水面（へこんだ液面の底）の目盛り。"""
    n = len(levels)
    pw = min(w / n, 130)
    ch, cw = h - 36, 26
    yb = top - h + 22
    sc = ch / vmax
    for k, lv in enumerate(levels):
        cx = x + (w - n * pw) / 2 + k * pw + pw / 2 - 14
        c.setFillColor(colors.HexColor('#D8E6F0'))
        c.rect(cx - cw / 2, yb, cw, lv * sc, stroke=0, fill=1)
        setline(c, 1.2)
        c.line(cx - cw / 2, yb + ch + 4, cx - cw / 2, yb)
        c.line(cx + cw / 2, yb + ch + 4, cx + cw / 2, yb)
        c.setFillColor(PALE)
        c.rect(cx - cw / 2 - 7, yb - 5, cw + 14, 5, stroke=1, fill=1)
        for v in range(0, vmax + 1):
            ln = 12 if v % 10 == 0 else 8 if v % 5 == 0 else 5
            setline(c, .5)
            c.line(cx + cw / 2, yb + v * sc, cx + cw / 2 - ln, yb + v * sc)
            if v % 10 == 0 and v > 0:
                text(c, cx + cw / 2 + 5, yb + v * sc - 3, str(v), 8, color=MUTED)
        yl = yb + lv * sc
        setline(c, 1)
        p = c.beginPath()
        p.moveTo(cx - cw / 2, yl + 2.5)
        p.curveTo(cx - cw / 4, yl, cx + cw / 4, yl, cx + cw / 2, yl + 2.5)
        c.drawPath(p, stroke=1, fill=0)
        text(c, cx, yb - 18, labels[k], 11, bold=True, center=True)


def fig_rods(c, x, top, w, h, pts=(), length=30):
    """金属の棒。左はしを加熱する。pts は (記号, 加熱するところからの距離cm)。"""
    x0, x1 = x + 60, x + w - 40
    X = lambda d: x0 + (x1 - x0) * d / length
    by = top - 36
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(x0, by - 4, x1 - x0, 8, stroke=1, fill=1)
    c.setFillColor(colors.HexColor('#C9822B'))
    c.drawPath(_poly(c, [(x0 + 2, by - 6), (x0 + 14, by - 6), (x0 + 8, by - 24)]), stroke=0, fill=1)
    text(c, x0 + 8, by - 38, '加熱', 9, color=MUTED, center=True)
    for d in range(0, length + 1, 5):
        setline(c, .6)
        c.line(X(d), by - 4, X(d), by - 9)
        text(c, X(d), by - 21, str(d), 8, color=MUTED, center=True)
    text(c, x1 + 4, by - 21, 'cm', 8, color=MUTED)
    for lab, d in pts:
        c.setFillColor(ACCENT)
        c.circle(X(d), by + 7, 3, stroke=0, fill=1)
        text(c, X(d), by + 14, lab, 10.5, bold=True, center=True)


def _badge(c, x, y, lab, r=7.5):
    setline(c, .7, ACCENT)
    c.setFillColor(colors.white)
    c.circle(x, y, r, stroke=1, fill=1)
    text(c, x, y - 3.6, lab, 10, bold=True, color=ACCENT, center=True)


def fig_fuleaf(c, x, top, w, h):
    """ふ入りの葉。A＝緑色の部分、B＝白い部分（ふ）、C＝アルミニウムはくでおおった緑色の部分。"""
    cx, cy = x + w / 2, top - 60
    x0, x1 = cx - 112, cx + 112
    leaf = c.beginPath()
    leaf.moveTo(x0, cy)
    leaf.curveTo(x0 + 40, cy + 62, x1 - 60, cy + 54, x1, cy)
    leaf.curveTo(x1 - 60, cy - 54, x0 + 40, cy - 62, x0, cy)
    c.saveState()
    c.clipPath(leaf, stroke=0, fill=0)
    c.setFillColor(colors.HexColor('#CFE3CC'))
    c.rect(x0, cy - 70, x1 - x0, 140, stroke=0, fill=1)
    c.setFillColor(colors.white)
    c.ellipse(cx + 8, cy + 6, cx + 92, cy + 60, stroke=0, fill=1)
    c.restoreState()
    setline(c, 1.1)
    c.drawPath(leaf, stroke=1, fill=0)
    setline(c, .7, MUTED)
    c.line(x0 - 8, cy, x1 - 6, cy)
    c.setFillColor(colors.HexColor('#B9C2C9'))
    setline(c, 1)
    c.rect(cx - 66, cy - 46, 38, 92, stroke=1, fill=1)
    setline(c, .4, MUTED)
    for k in range(0, 92, 8):
        c.line(cx - 66, cy - 46 + k, cx - 28, cy - 46 + k + 8)
    _badge(c, cx + 20, cy - 24, 'A')
    _badge(c, cx + 52, cy + 28, 'B')
    _badge(c, cx - 47, cy, 'C')
    text(c, cx, top - h + 4, '灰色の部分はアルミニウムはく。白い部分は、ふ（葉緑体がない）。', 8.5, color=MUTED, center=True)


def fig_river(c, x, top, w, h):
    """山から海へ流れる川を上から見た図。ア・イ・ウは上流・中流・下流、A・Bは曲がりの両岸。"""
    X = lambda u: x + 30 + (w - 60) * u
    Y = lambda v: top - h + 8 + (h - 16) * v
    pts = [(0.14, 0.90), (0.18, 0.76), (0.23, 0.62), (0.30, 0.45)]
    for k in range(1, 26):
        u = 0.30 + 0.42 * k / 25
        pts.append((u, 0.45 + 0.13 * math.sin(2 * math.pi * (u - 0.30) / 0.42)))
    pts += [(0.77, 0.34), (0.81, 0.22), (0.83, 0.12)]
    c.setFillColor(colors.HexColor('#E3EBF0'))
    c.rect(X(0.40), Y(0.0), X(1.0) - X(0.40), Y(0.12) - Y(0.0), stroke=0, fill=1)
    text(c, X(0.96), Y(0.0) + 4, '海', 10, bold=True, color=ACCENT, center=True)
    for ux in (0.02, 0.10):
        c.setFillColor(SHADE)
        c.drawPath(_poly(c, [(X(ux), Y(0.78)), (X(ux) + 22, Y(0.78)), (X(ux) + 11, Y(0.97))]), stroke=0, fill=1)
    setline(c, 4, ACCENT)
    p = c.beginPath()
    p.moveTo(X(pts[0][0]), Y(pts[0][1]))
    for u, v in pts[1:]:
        p.lineTo(X(u), Y(v))
    c.drawPath(p, stroke=1, fill=0)
    uc = 0.30 + 0.42 / 4
    for lab, dy in (('A', 12), ('B', -20)):
        c.setFillColor(INK)
        c.circle(X(uc), Y(0.58) + dy / 2 * .45, 1.8, stroke=0, fill=1)
        text(c, X(uc), Y(0.58) + dy, lab, 11, bold=True, center=True)
    for lab, u, v, dx, dy in (('ア', 0.14, 0.90, 12, -3), ('イ', 0.30, 0.45, -16, -3), ('ウ', 0.79, 0.28, 14, -3)):
        _badge(c, X(u) + dx, Y(v) + dy, lab)


def fig_microscope(c, x, top, w, h):
    """顕微鏡。ア〜カの部分の名前を答える。"""
    cx = x + w / 2 - 20
    yb = top - h + 8
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(cx - 46, yb, 92, 9, stroke=1, fill=1)
    c.rect(cx + 22, yb + 9, 9, 104, stroke=1, fill=1)               # うで
    c.rect(cx - 8, yb + 104, 39, 9, stroke=1, fill=1)
    c.rect(cx - 8, yb + 58, 16, 54, stroke=1, fill=1)               # 鏡筒
    c.rect(cx - 5, yb + 112, 10, 16, stroke=1, fill=1)              # 接眼レンズ
    c.rect(cx - 4, yb + 50, 8, 8, stroke=1, fill=1)                 # 対物レンズ
    c.rect(cx - 32, yb + 34, 64, 5, stroke=1, fill=1)               # ステージ
    for dx in (-24, 20):
        c.rect(cx + dx, yb + 39, 5, 3, stroke=1, fill=1)            # クリップ
    c.circle(cx - 2, yb + 18, 8, stroke=1, fill=1)                  # 反射鏡
    c.line(cx - 2, yb + 10, cx - 2, yb + 9)
    c.circle(cx + 26, yb + 70, 7, stroke=1, fill=1)                 # 調節ねじ
    for lab, (px, py), (tx, ty) in (('ア', (cx + 5, yb + 122), (cx + 56, yb + 128)), ('イ', (cx - 4, yb + 54), (cx - 52, yb + 62)),
                                   ('ウ', (cx - 32, yb + 36), (cx - 62, yb + 42)), ('エ', (cx - 10, yb + 18), (cx - 56, yb + 20)),
                                   ('オ', (cx + 33, yb + 70), (cx + 62, yb + 76)), ('カ', (cx + 25, yb + 41), (cx + 62, yb + 46))):
        setline(c, .6, MUTED)
        c.line(px, py, tx, ty)
        _badge(c, tx + (6 if tx > cx else -6), ty, lab)


def fig_lens(c, x, top, w, h):
    """光学台。ろうそく・凸レンズ・スクリーンと、レンズの両側の焦点。"""
    cx, ay = x + w / 2, top - h / 2 - 2
    setline(c, .7, MUTED, (3, 2))
    c.line(cx - 190, ay, cx + 190, ay)
    c.setDash()
    setline(c, 1.2)
    c.setFillColor(colors.HexColor('#E3EBF0'))
    c.ellipse(cx - 5, ay - 30, cx + 5, ay + 30, stroke=1, fill=1)
    text(c, cx, ay - 44, '凸レンズ', 9, center=True)
    for dx in (-60, 60):
        _dot(c, cx + dx, ay)
        text(c, cx + dx, ay - 14, '焦点', 8.5, color=MUTED, center=True)
    # ろうそく
    qx = cx - 130
    setline(c, 1)
    c.setFillColor(PALE)
    c.rect(qx - 3, ay, 6, 16, stroke=1, fill=1)
    c.setFillColor(colors.HexColor('#C9822B'))
    c.drawPath(_poly(c, [(qx - 3, ay + 16), (qx + 3, ay + 16), (qx, ay + 28)]), stroke=0, fill=1)
    text(c, qx, ay - 44, 'ろうそく', 9, center=True)
    # スクリーンと、さかさまの像
    sx = cx + 130
    setline(c, 2)
    c.line(sx, ay - 34, sx, ay + 34)
    c.setFillColor(colors.HexColor('#C9822B'))
    c.drawPath(_poly(c, [(sx + 3, ay - 12), (sx + 9, ay - 12), (sx + 6, ay - 4)]), stroke=0, fill=1)
    text(c, sx, ay - 44, 'スクリーン', 9, center=True)


def fig_moonphases(c, x, top, w, h, phases=(0, 1, 2, 3, 4, 5, 6, 7), labels='アイウエオカキク'):
    """月の形を並べる。phases は 0=新月 1=三日月 2=上弦 3=右が大きい 4=満月 5=左が大きい 6=下弦 7=左の細い月。"""
    n = len(phases)
    pw = w / n
    r = 17
    cy = top - h / 2 - 4
    for k, ph in enumerate(phases):
        cx = x + k * pw + pw / 2
        circ = c.beginPath()
        circ.circle(cx, cy, r)
        c.saveState()
        c.clipPath(circ, stroke=0, fill=0)
        c.setFillColor(SHADE)
        c.rect(cx - r, cy - r, 2 * r, 2 * r, stroke=0, fill=1)
        c.setFillColor(colors.white)
        if ph == 4:
            c.rect(cx - r, cy - r, 2 * r, 2 * r, stroke=0, fill=1)
        elif ph in (1, 2, 3):
            c.rect(cx, cy - r, r, 2 * r, stroke=0, fill=1)
            ex = r * .5 if ph != 2 else 0
            c.saveState()
            half = c.beginPath()
            half.rect(cx if ph == 1 else cx - r, cy - r, r, 2 * r)
            c.clipPath(half, stroke=0, fill=0)
            c.setFillColor(SHADE if ph == 1 else colors.white)
            if ex:
                c.ellipse(cx - ex, cy - r, cx + ex, cy + r, stroke=0, fill=1)
            c.restoreState()
        elif ph in (5, 6, 7):
            c.rect(cx - r, cy - r, r, 2 * r, stroke=0, fill=1)
            ex = r * .5 if ph != 6 else 0
            c.saveState()
            half = c.beginPath()
            half.rect(cx - r if ph == 7 else cx, cy - r, r, 2 * r)
            c.clipPath(half, stroke=0, fill=0)
            c.setFillColor(SHADE if ph == 7 else colors.white)
            if ex:
                c.ellipse(cx - ex, cy - r, cx + ex, cy + r, stroke=0, fill=1)
            c.restoreState()
        c.restoreState()
        setline(c, .8)
        c.circle(cx, cy, r, stroke=1, fill=0)
        text(c, cx, cy - r - 14, labels[k], 11, bold=True, center=True)


def fig_eye(c, x, top, w, h):
    """目の断面。ア角膜・イ虹彩・ウ水晶体・エ網膜・オ視神経。"""
    cx, cy = x + w / 2, top - h / 2 - 2
    R = 44
    setline(c, 1.2)
    c.setFillColor(colors.white)
    c.circle(cx, cy, R, stroke=1, fill=1)
    setline(c, 3.2, INK)
    c.arc(cx - R, cy - R, cx + R, cy + R, 150, 60)                       # 角膜
    setline(c, 3.2, ACCENT)
    c.arc(cx - R + 4, cy - R + 4, cx + R - 4, cy + R - 4, -55, 110)      # 網膜
    setline(c, 1.2)
    c.setFillColor(colors.HexColor('#E3EBF0'))
    c.ellipse(cx - 27, cy - 14, cx - 17, cy + 14, stroke=1, fill=1)      # 水晶体
    setline(c, 3, MUTED)
    c.line(cx - 36, cy + 14, cx - 36, cy + 36)                           # 虹彩
    c.line(cx - 36, cy - 14, cx - 36, cy - 36)
    setline(c, 5, MUTED)
    ax, ay = cx + R * math.cos(math.radians(-30)), cy + R * math.sin(math.radians(-30))
    c.line(ax, ay, ax + 18, ay - 12)                                     # 視神経
    arrow(c, cx - R - 34, cy + 4, cx - R - 6, cy + 4, 6, 1, MUTED)
    text(c, cx - R - 40, cy + 12, '光', 9, color=MUTED, center=True)
    for lab, (bx, by), (tx, ty) in (('ア', (cx - 76, cy - 18), (cx - 43, cy - 8)), ('イ', (cx - 58, cy + 56), (cx - 36, cy + 30)),
                                   ('ウ', (cx - 4, cy + 60), (cx - 22, cy + 12)), ('エ', (cx + 62, cy + 40), (cx + 32, cy + 26)),
                                   ('オ', (cx + 70, cy - 48), (cx + 52, cy - 32))):
        setline(c, .6, MUTED)
        c.line(bx, by, tx, ty)
        _badge(c, bx, by, lab)


# ---------- 算数の図 ----------
def _hatch(c, clip, x0, y0, x1, y1, gap=4.2):
    """clip（パス）の内がわに、右上がりの斜線を引く。"""
    c.saveState()
    c.clipPath(clip, stroke=0, fill=0)
    setline(c, .45, MUTED)
    k = x0 - (y1 - y0)
    while k < x1:
        c.line(k, y0, k + (y1 - y0), y1)
        k += gap
    c.restoreState()


def _quarter(c, cx, cy, r, a0):
    p = c.beginPath()
    p.moveTo(cx, cy)
    p.lineTo(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
    p.arcTo(cx - r, cy - r, cx + r, cy + r, a0, 90)
    p.close()
    return p


def fig_piechart(c, x, top, w, h, data=(), total=None, unit='人'):
    """円グラフ。data は (名前, 値)。値が None のものは、全体から残りを求めるらんで、数は書かない。右まわりに、真上から。"""
    known = sum(v for _, v in data if v is not None)
    total = total or known
    cx, cy = x + w / 2, top - h / 2
    R = min(h / 2 - 24, 62)
    cum = 0
    for k, (name, v) in enumerate(data):
        val = v if v is not None else total - known
        a1 = 90 - (cum + val) * 360 / total
        span = val * 360 / total
        c.setFillColor(colors.white if v is None else (PALE if k % 2 == 0 else colors.HexColor('#DCE2E6')))
        setline(c, .9)
        c.wedge(cx - R, cy - R, cx + R, cy + R, a1, span, stroke=1, fill=1)
        mid = math.radians(90 - (cum + val / 2) * 360 / total)
        lx, ly = cx + (R + 12) * math.cos(mid), cy + (R + 12) * math.sin(mid)
        setline(c, .5, MUTED)
        c.line(cx + R * math.cos(mid), cy + R * math.sin(mid), lx, ly)
        label = name
        sub = '' if v is None else f'{v}{unit}'
        right = math.cos(mid) >= 0
        tx = lx + 2 if right else lx - 2
        if right:
            text(c, tx, ly + 1, label, 9.5)
            text(c, tx, ly - 10, sub, 9.5)
        else:
            text(c, tx - tw(label, 9.5), ly + 1, label, 9.5)
            text(c, tx - tw(sub, 9.5), ly - 10, sub, 9.5)
        cum += val


SHAPES = {                      # 平面図形の頂点（検算でも、この座標から対称性を調べる）
    '正三角形': [(0, 0), (2, 0), (1, math.sqrt(3))],
    '直角二等辺三角形': [(0, 0), (2, 0), (0, 2)],
    '正方形': [(0, 0), (2, 0), (2, 2), (0, 2)],
    '長方形': [(0, 0), (3, 0), (3, 2), (0, 2)],
    'ひし形': [(0, 1), (1.5, 0), (3, 1), (1.5, 2)],
    '平行四辺形': [(0, 0), (2.5, 0), (3.5, 2), (1, 2)],
    '等脚台形': [(0, 0), (3, 0), (2.4, 2), (0.6, 2)],
    '正六角形': [(2, 0), (1, math.sqrt(3)), (-1, math.sqrt(3)), (-2, 0), (-1, -math.sqrt(3)), (1, -math.sqrt(3))],
}


def fig_symshapes(c, x, top, w, h, shapes=(), per=4):
    """平面図形をならべて、ア・イ・…の記号と名前をつける。"""
    n = len(shapes)
    rows = math.ceil(n / per)
    cw, rh = w / per, h / rows
    for i, name in enumerate(shapes):
        r, k = divmod(i, per)
        pts = SHAPES[name]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        sc = 38 / max(max(xs) - min(xs), max(ys) - min(ys)) * (1 if max(xs) - min(xs) < 4 else 1)
        sc = min(sc, 18)
        cx0 = x + k * cw + cw / 2 - (max(xs) + min(xs)) / 2 * sc
        cy0 = top - r * rh - rh / 2 + 4 - (max(ys) + min(ys)) / 2 * sc
        c.setFillColor(colors.white)
        setline(c, 1.1)
        c.drawPath(_poly(c, [(cx0 + px * sc, cy0 + py * sc) for px, py in pts]), stroke=1, fill=1)
        text(c, x + k * cw + cw / 2, top - r * rh - rh + 10, f'{"アイウエオカキク"[i]} {name}', 9.5, center=True)


def fig_letters(c, x, top, w, h, s='BHKNSTXZ'):
    """大きなアルファベットを、わくの中にならべる。"""
    bw = min(w - 80, 46 * len(s) + 24)
    bx = x + (w - bw) / 2
    setline(c, 1)
    c.setFillColor(colors.white)
    c.rect(bx, top - h + 6, bw, h - 10, stroke=1, fill=1)
    step = (bw - 24) / len(s)
    for k, ch in enumerate(s):
        text(c, bx + 12 + step * (k + .5), top - h / 2 - 12, ch, 30, bold=True, center=True)


def fig_areas(c, x, top, w, h, specs=()):
    """斜線部分の面積の図を、(1)(2)(3)とならべる。specs は (種類, 数値のdict)。"""
    n = len(specs)
    wts = [a.get('wt', 1) for _, a in specs]                 # 図ごとの幅の重み（ふつうは同じ幅）
    cum = 0
    for k, (kind, a) in enumerate(specs):
        pw = w * wts[k] / sum(wts)
        px = x + w * cum / sum(wts)
        cum += wts[k]
        text(c, px + 4, top - 11, f'({k + 1})', 10, bold=True)
        if kind == 'trap':                                   # 長方形の中の、四角形（上の左はしを切りとる）
            W, H, cut = a['w'], a['h'], a['cut']
            sc = min((pw - 50) / W, (h - 50) / H)
            ox, oy = px + (pw - W * sc) / 2, top - 24 - H * sc
            poly = [(ox, oy), (ox + W * sc, oy), (ox + W * sc, oy + H * sc), (ox + cut * sc, oy + H * sc)]
            _hatch(c, _poly(c, poly), ox, oy, ox + W * sc, oy + H * sc)
            setline(c, 1.1)
            c.rect(ox, oy, W * sc, H * sc, stroke=1, fill=0)
            c.drawPath(_poly(c, poly), stroke=1, fill=0)
            text(c, ox + W * sc / 2, oy - 12, f'{W:g}cm', 9, center=True)
            text(c, ox + W * sc + 4, oy + H * sc / 2 - 3, f'{H:g}cm', 9)
            text(c, ox + cut * sc / 2, oy + H * sc + 4, f'{cut:g}cm', 9, center=True)
        elif kind == 'lens':                                 # 正方形と、向かい合う頂点を中心とする2つの四分円
            s_ = a['s']
            sc = min((pw - 40) / s_, (h - 46) / s_)
            ox, oy = px + (pw - s_ * sc) / 2, top - 24 - s_ * sc
            c.saveState()
            c.clipPath(_quarter(c, ox, oy, s_ * sc, 0), stroke=0, fill=0)
            _hatch(c, _quarter(c, ox + s_ * sc, oy + s_ * sc, s_ * sc, 180), ox, oy, ox + s_ * sc, oy + s_ * sc)
            c.restoreState()
            setline(c, 1.1)
            c.rect(ox, oy, s_ * sc, s_ * sc, stroke=1, fill=0)
            c.arc(ox - s_ * sc, oy - s_ * sc, ox + s_ * sc, oy + s_ * sc, 0, 90)
            c.arc(ox, oy, ox + 2 * s_ * sc, oy + 2 * s_ * sc, 180, 90)
            text(c, ox + s_ * sc / 2, oy - 12, f'{s_:g}cm', 9, center=True)
        elif kind == 'segment':                              # 半円から、直径を底辺とする三角形をひく
            d = a['d']
            sc = min((pw - 40) / d, (h - 56) / (d / 2))
            ox, oy = px + (pw - d * sc) / 2, top - 30 - d / 2 * sc
            semi = c.beginPath()
            semi.moveTo(ox + d * sc, oy)
            semi.arcTo(ox, oy - d / 2 * sc, ox + d * sc, oy + d / 2 * sc, 0, 180)
            semi.close()
            _hatch(c, semi, ox, oy, ox + d * sc, oy + d / 2 * sc)
            c.setFillColor(colors.white)
            setline(c, 1.1)
            c.drawPath(_poly(c, [(ox, oy), (ox + d * sc, oy), (ox + d * sc / 2, oy + d / 2 * sc)]), stroke=1, fill=1)
            c.arc(ox, oy - d / 2 * sc, ox + d * sc, oy + d / 2 * sc, 0, 180)
            c.line(ox, oy, ox + d * sc, oy)
            text(c, ox + d * sc / 2, oy - 12, f'{d:g}cm', 9, center=True)
        else:
            AREA_KINDS[kind](c, px, pw, top, h, a)


def _obl(ox, oy, sc, kx=.42, ky=.3):
    """見取図（斜投影）。(x=右, y=おくゆき, z=上) を、紙の上の点にうつす関数を返す。"""
    return lambda x, y, z: (ox + (x + kx * y) * sc, oy + (z + ky * y) * sc)


def _faces(c, P, faces):
    """見える面を、(頂点の列, 色) で、順にぬる。"""
    setline(c, 1.1)
    for pts, col in faces:
        c.setFillColor(col)
        c.drawPath(_poly(c, [P(*q) for q in pts]), stroke=1, fill=1)


SHADE = colors.HexColor('#DCE2E6')


def _ar_trisect(c, px, pw, top, h, a):                       # 正方形の各辺を3等分する点のうち4点を結んだ長方形
    s_ = a['s']
    sc = min((pw - 40) / s_, (h - 46) / s_)
    ox, oy = px + (pw - s_ * sc) / 2, top - 24 - s_ * sc
    t = s_ / 3
    pts = [(0, 2 * t), (t, s_), (s_, t), (2 * t, 0)]
    poly = [(ox + u * sc, oy + v * sc) for u, v in pts]
    _hatch(c, _poly(c, poly), ox, oy, ox + s_ * sc, oy + s_ * sc)
    setline(c, 1.1)
    c.rect(ox, oy, s_ * sc, s_ * sc, stroke=1, fill=0)
    c.drawPath(_poly(c, poly), stroke=1, fill=0)
    c.setFillColor(INK)
    for u in (t, 2 * t):                                     # 3等分する点
        for q in ((u, 0), (u, s_), (0, u), (s_, u)):
            c.circle(ox + q[0] * sc, oy + q[1] * sc, 1.6, stroke=0, fill=1)
    text(c, ox + s_ * sc / 2, oy - 12, f'{s_:g}cm', 9, center=True)


def _ar_twosemi(c, px, pw, top, h, a):                       # 正方形の2辺を直径とする、半円2つの重なり
    s_ = a['s']
    sc = min((pw - 40) / s_, (h - 46) / s_)
    ox, oy = px + (pw - s_ * sc) / 2, top - 24 - s_ * sc
    r = s_ / 2 * sc
    c.saveState()
    p1 = c.beginPath()
    p1.circle(ox, oy + r, r)
    c.clipPath(p1, stroke=0, fill=0)
    p2 = c.beginPath()
    p2.circle(ox + r, oy, r)
    _hatch(c, p2, ox, oy, ox + s_ * sc, oy + s_ * sc)
    c.restoreState()
    setline(c, 1.1)
    c.rect(ox, oy, s_ * sc, s_ * sc, stroke=1, fill=0)
    c.arc(ox - r, oy, ox + r, oy + 2 * r, -90, 180)          # 左の辺が直径（右がわの半円）
    c.arc(ox, oy - r, ox + 2 * r, oy + r, 0, 180)            # 下の辺が直径（上がわの半円）
    text(c, ox + s_ * sc / 2, oy - 12, f'{s_:g}cm', 9, center=True)


def _centroid(inside, x0, x1, y0, y1, n=120):
    """領域の重心（見つからない、または、領域の外のときは、領域の中でいちばん近い点）。"""
    pts = [(x0 + (i + .5) * (x1 - x0) / n, y0 + (j + .5) * (y1 - y0) / n) for i in range(n) for j in range(n)]
    pts = [q for q in pts if inside(*q)]
    gx, gy = sum(q[0] for q in pts) / len(pts), sum(q[1] for q in pts) / len(pts)
    return min(pts, key=lambda q: (q[0] - gx) ** 2 + (q[1] - gy) ** 2)


def _ar_semitri(c, px, pw, top, h, a):                       # 直径BCの半円と、直角三角形ABC（Bが直角）の重なり
    d = a['d']
    ab = 3.14 * d / 4
    sc = min((pw - 44) / d, (h - 58) / ab)
    ox, oy = px + (pw - d * sc) / 2, top - 30 - ab * sc
    semi = c.beginPath()
    semi.moveTo(ox + d * sc, oy)
    semi.arcTo(ox, oy - d / 2 * sc, ox + d * sc, oy + d / 2 * sc, 0, 180)
    semi.close()
    c.setFillColor(colors.white)
    setline(c, 1.1)
    c.drawPath(_poly(c, [(ox, oy), (ox + d * sc, oy), (ox, oy + ab * sc)]), stroke=1, fill=0)
    c.arc(ox, oy - d / 2 * sc, ox + d * sc, oy + d / 2 * sc, 0, 180)
    c.line(ox, oy, ox + d * sc, oy)
    in_semi = lambda u, v: v >= 0 and (u - d / 2) ** 2 + v ** 2 <= (d / 2) ** 2
    in_tri = lambda u, v: u >= 0 and v >= 0 and v <= ab * (1 - u / d)
    for lab, f in (('ア', lambda u, v: in_semi(u, v) and not in_tri(u, v)), ('イ', lambda u, v: in_tri(u, v) and not in_semi(u, v))):
        gx, gy = _centroid(f, 0, d, 0, ab)
        text(c, ox + gx * sc, oy + gy * sc - 3.5, lab, 10, bold=True, center=True)
    text(c, ox - 9, oy - 3, 'B', 9.5, bold=True, center=True)
    text(c, ox + d * sc + 9, oy - 3, 'C', 9.5, bold=True, center=True)
    text(c, ox - 9, oy + ab * sc - 3, 'A', 9.5, bold=True, center=True)
    text(c, ox + d * sc / 2, oy - 14, f'{d:g}cm', 9, center=True)


def _ar_trap3(c, px, pw, top, h, a):                         # 台形ABCDを、BEとEFで3つの部分に分ける
    ad, bc, ae = a['ad'], a['bc'], a['ae']
    hh = a.get('hh', 8)
    sc = min((pw - 40) / bc, (h - 58) / hh)
    ox, oy = px + (pw - bc * sc) / 2, top - 30 - hh * sc
    A, D = ((bc - ad) / 2, hh), ((bc - ad) / 2 + ad, hh)
    B, C, E, F = (0, 0), (bc, 0), ((bc - ad) / 2 + ae, hh), (ae, 0)
    P = lambda q: (ox + q[0] * sc, oy + q[1] * sc)
    setline(c, 1.1)
    c.setFillColor(colors.white)
    c.drawPath(_poly(c, [P(B), P(C), P(D), P(A)]), stroke=1, fill=0)
    c.line(*P(B), *P(E))
    c.line(*P(E), *P(F))
    for lab, region in (('ア', [A, B, E]), ('イ', [B, E, F]), ('ウ', [E, F, C, D])):
        gx, gy = sum(q[0] for q in region) / len(region), sum(q[1] for q in region) / len(region)
        text(c, ox + gx * sc, oy + gy * sc - 3.5, lab, 10, bold=True, center=True)
    for lab, q, dx, dy in (('A', A, -8, 5), ('D', D, 8, 5), ('B', B, -8, -9), ('C', C, 8, -9), ('E', E, 0, 6), ('F', F, 0, -11)):
        text(c, P(q)[0] + dx, P(q)[1] + dy, lab, 9.5, bold=True, center=True)
    text(c, ox + bc * sc / 2, oy - 22, f'BC {bc:g}cm　AD {ad:g}cm', 8.5, center=True)


def _ar_views(c, px, pw, top, h, a):                         # 円柱を、真正面と真上から見た図
    Wd, H = a['w'], a['h']
    sc = min((pw - 22) / (2 * Wd + 3), (h - 56) / H)
    x0 = px + (pw - (2 * Wd + 3) * sc) / 2
    oy = top - 24 - H * sc
    setline(c, 1.1)
    c.rect(x0, oy, Wd * sc, H * sc, stroke=1, fill=0)
    text(c, x0 + Wd * sc / 2, oy - 11, f'{Wd:g}cm', 9, center=True)
    text(c, x0 + Wd * sc + 4, oy + H * sc / 2 - 3, f'{H:g}cm', 9)
    cx, cy = x0 + (Wd + 3) * sc + Wd * sc / 2, oy + H * sc / 2
    c.circle(cx, cy, Wd * sc / 2, stroke=1, fill=0)
    setline(c, .7, INK, (3, 2))
    c.line(cx - Wd * sc / 2, cy, cx + Wd * sc / 2, cy)
    text(c, cx, cy + 3, f'{Wd:g}cm', 9, center=True)
    text(c, x0 + Wd * sc / 2, oy - 23, '真正面から見た図', 8, center=True)
    text(c, cx, oy - 23, '真上から見た図', 8, center=True)


def _ar_notchbox(c, px, pw, top, h, a):                      # 直方体の、右手前の上のかどから、立方体を切りとった立体
    L, Wd, H, n = a['l'], a['w'], a['h'], a['n']
    kx, ky = .42, .3
    sc = min((pw - 46) / (L + kx * Wd), (h - 50) / (H + ky * Wd))
    ox = px + 24 + (pw - 46 - (L + kx * Wd) * sc) / 2
    oy = top - 24 - (H + ky * Wd) * sc
    P = _obl(ox, oy, sc, kx, ky)
    _faces(c, P, [
        ([(0, 0, 0), (L, 0, 0), (L, 0, H - n), (L - n, 0, H - n), (L - n, 0, H), (0, 0, H)], colors.white),
        ([(0, 0, H), (L - n, 0, H), (L - n, n, H), (L, n, H), (L, Wd, H), (0, Wd, H)], colors.white),
        ([(L, 0, 0), (L, Wd, 0), (L, Wd, H), (L, n, H), (L, n, H - n), (L, 0, H - n)], SHADE),
        ([(L - n, 0, H - n), (L, 0, H - n), (L, n, H - n), (L - n, n, H - n)], colors.white),
        ([(L - n, n, H - n), (L, n, H - n), (L, n, H), (L - n, n, H)], PALE),
        ([(L - n, 0, H - n), (L - n, n, H - n), (L - n, n, H), (L - n, 0, H)], PALE)])
    text(c, P(L / 2, 0, 0)[0], P(0, 0, 0)[1] - 12, f'{L:g}cm', 9, center=True)
    text(c, P(L, Wd / 2, 0)[0] + 5, P(L, Wd / 2, 0)[1] - 8, f'{Wd:g}cm', 9)
    text(c, P(0, 0, H / 2)[0] - 15, P(0, 0, H / 2)[1] - 3, f'{H:g}cm', 9, center=True)
    text(c, P(L - n, 0, H - n / 2)[0] - 14, P(L - n, 0, H - n / 2)[1] - 3, f'{n:g}cm', 8.5, center=True)


def _ar_house(c, px, pw, top, h, a):                         # 家の形（五角形）の柱
    Wd, wall, roof, ln = a['w'], a['wall'], a['roof'], a['len']
    kx, ky = .42, .3
    sc = min((pw - 46) / (Wd + kx * ln), (h - 50) / (wall + roof + ky * ln))
    ox = px + 24 + (pw - 46 - (Wd + kx * ln) * sc) / 2
    oy = top - 24 - (wall + roof + ky * ln) * sc
    P = _obl(ox, oy, sc, kx, ky)
    _faces(c, P, [
        ([(Wd / 2, 0, wall + roof), (Wd, 0, wall), (Wd, ln, wall), (Wd / 2, ln, wall + roof)], PALE),
        ([(Wd, 0, 0), (Wd, ln, 0), (Wd, ln, wall), (Wd, 0, wall)], SHADE),
        ([(0, 0, 0), (Wd, 0, 0), (Wd, 0, wall), (Wd / 2, 0, wall + roof), (0, 0, wall)], colors.white)])
    setline(c, .7, INK, (3, 2))
    c.line(*P(Wd / 2, 0, wall + roof), *P(Wd / 2, 0, wall))
    c.line(*P(0, 0, wall), *P(Wd, 0, wall))
    text(c, P(Wd / 2, 0, 0)[0], P(0, 0, 0)[1] - 12, f'{Wd:g}cm', 9, center=True)
    text(c, P(Wd, ln / 2, 0)[0] + 5, P(Wd, ln / 2, 0)[1] - 8, f'{ln:g}cm', 9)
    text(c, P(0, 0, wall / 2)[0] - 15, P(0, 0, wall / 2)[1] - 3, f'{wall:g}cm', 9, center=True)
    text(c, P(Wd / 2, 0, wall + roof * .3)[0] - 12, P(Wd / 2, 0, wall + roof * .3)[1] - 3, f'{roof:g}cm', 9, center=True)


def _ar_sector(c, px, pw, top, h, a):                        # 円柱を4等分した立体を、真上から見た図（おうぎ形）
    r = a['r']
    sc = min((pw - 40) / r, (h - 62) / r)
    ox, oy = px + (pw - r * sc) / 2, top - 26 - r * sc
    sec = _quarter(c, ox, oy, r * sc, 0)
    c.setFillColor(colors.white)
    setline(c, 1.1)
    c.drawPath(sec, stroke=1, fill=0)
    if a.get('chord'):
        setline(c, .8, INK, (3, 2))
        c.line(ox + r * sc, oy, ox, oy + r * sc)
    text(c, ox + r * sc / 2, oy - 12, f'{r:g}cm', 9, center=True)
    text(c, ox + r * sc / 2, oy - 24, f'（真上から見た図　高さ{a["hh"]:g}cm）', 8, center=True)


AREA_KINDS = {'trisect': _ar_trisect, 'twosemi': _ar_twosemi, 'semitri': _ar_semitri, 'trap3': _ar_trap3,
              'views': _ar_views, 'notchbox': _ar_notchbox, 'house': _ar_house, 'sector': _ar_sector}


def fig_matchsticks(c, x, top, w, h, counts=(1, 2, 3)):
    """同じ長さの棒で、正方形を横にならべた図。counts は、ならべる正方形の個数。"""
    side = 22
    gap = 26
    total = sum(n * side + side for n in counts) + gap * (len(counts) - 1) + 30
    cx = x + (w - total) / 2
    by = top - h / 2 - side / 2
    for n in counts:
        setline(c, 2.2)
        for k in range(n + 1):
            c.line(cx + k * side, by, cx + k * side, by + side)
        for k in range(n):
            c.line(cx + k * side, by, cx + (k + 1) * side, by)
            c.line(cx + k * side, by + side, cx + (k + 1) * side, by + side)
        text(c, cx + n * side / 2, by - 15, f'{n}個', 9.5, center=True)
        cx += n * side + gap
    text(c, cx - 4, by + side / 2 - 3, '…', 12)


def fig_roadmap(c, x, top, w, h, cols=4, rows=3, labels=(), blocked=()):
    """格子状の道の地図（国語の道案内）。labels は (i, j, 名前)。blocked は、通れない道 ((i1, j1), (i2, j2))。北は上。"""
    dx, dy = (w - 70) / (cols - 1), (h - 34) / (rows - 1)
    ox, oy = x + 34, top - h + 16
    P = lambda i, j: (ox + i * dx, oy + j * dy)
    setline(c, 1.6)
    for j in range(rows):
        for i in range(cols - 1):
            c.line(*P(i, j), *P(i + 1, j))
    for i in range(cols):
        for j in range(rows - 1):
            c.line(*P(i, j), *P(i, j + 1))
    for (a, b) in blocked:                                   # 通れない道：白ぬきにして、×と「工事中」
        (x1, y1), (x2, y2) = P(*a), P(*b)
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2
        if not DRY:
            c.setFillColor(colors.white)
            c.setStrokeColor(colors.white)
            c.rect(mx - 11, my - 5, 22, 10, fill=1, stroke=0) if y1 == y2 else c.rect(mx - 5, my - 11, 10, 22, fill=1, stroke=0)
            setline(c, 1.4)
            c.line(mx - 5, my - 5, mx + 5, my + 5)
            c.line(mx - 5, my + 5, mx + 5, my - 5)
        text(c, mx, my + (8 if y1 == y2 else -3), '工事中', 8, center=True, bold=True) if y1 == y2 else text(c, mx + 24, my - 3, '工事中', 8, center=True, bold=True)
    for (i, j, name) in labels:
        px, py = P(i, j)
        wb = tw(name, 8.5) + 8
        if not DRY:
            c.setFillColor(colors.white)
            setline(c, .8)
            c.rect(px - wb / 2, py - 7, wb, 14, fill=1, stroke=1)
        text(c, px, py - 3, name, 8.5, center=True)
    arrow(c, x + 12, top - 26, x + 12, top - 5, head=5)       # 北
    text(c, x + 12, top - 38, '北', 9, bold=True, center=True)


FIGS = {'monochord': fig_monochord, 'circuits': fig_circuits, 'moon': fig_moon,
        'ice_graph': fig_ice_graph, 'pendulum': fig_pendulum,
        'strata': fig_strata, 'magnet': fig_magnet, 'lever': fig_lever, 'sanken': fig_sanken,
        'linegraph': fig_linegraph, 'flower': fig_flower, 'syringe': fig_syringe, 'typhoon': fig_typhoon,
        'world': fig_world, 'cloudmaps': fig_cloudmaps, 'seed': fig_seed, 'sao': fig_sao, 'stem': fig_stem,
        'circuitset': fig_circuitset, 'ammeter': fig_ammeter, 'circulation': fig_circulation, 'cans': fig_cans,
        'mirror': fig_mirror, 'digest': fig_digest, 'watercycle': fig_watercycle, 'pulleys': fig_pulleys, 'shadow': fig_shadow,
        'leverbar': fig_leverbar, 'balance': fig_balance, 'cylinder': fig_cylinder, 'rods': fig_rods,
        'fuleaf': fig_fuleaf, 'river': fig_river, 'microscope': fig_microscope, 'lens': fig_lens, 'moonphases': fig_moonphases, 'eye': fig_eye,
        'roadmap': fig_roadmap, 'piechart': fig_piechart, 'symshapes': fig_symshapes, 'letters': fig_letters, 'areas': fig_areas, 'matchsticks': fig_matchsticks}


# ---------- 表・本文ブロック ----------
def table_size(rows, colw, size):
    return sum(colw), len(rows) * (size * 1.9)


def draw_table(c, x, y, rows, colw, size=9.5, head_col=True, head_row=True, left_cols=()):
    rh = size * 1.9
    if not DRY:
        for r, row in enumerate(rows):
            xx = x
            for k, cell in enumerate(row):
                shade = (head_row and r == 0) or (head_col and k == 0)
                c.setFillColor(PALE if shade else colors.white)
                setline(c, .6, MUTED)
                c.rect(xx, y - (r + 1) * rh, colw[k], rh, fill=1, stroke=1)
                xx += colw[k]
    for r, row in enumerate(rows):
        xx = x
        for k, cell in enumerate(row):
            yy = y - (r + 1) * rh + rh / 2 - size * .35
            if (k in left_cols or (k == 0 and head_col and len(row) > 2 and not left_cols)) and not (head_row and r == 0):
                text(c, xx + 6, yy, cell, size)
            else:
                text(c, xx + colw[k] / 2, yy, cell, size, center=True)
            xx += colw[k]
    return y - len(rows) * rh


def draw_items(c, y, items, size=10):
    """A　説明文… を、記号を左にそろえて囲みの中に書く。"""
    lead = size * 1.5
    tot = 0
    for lab, body in items:
        tot += len(wrap(body, RM - LM - 46, size)) * lead + 3
    top = y
    if not DRY:
        setline(c, .7, LINE)
        c.setFillColor(colors.white)
        c.rect(LM, top - tot - 10, RM - LM, tot + 10, fill=0, stroke=1)
    y = top - 8 - size * .85
    for lab, body in items:
        text(c, LM + 10, y, lab, size, bold=True, color=ACCENT)
        y, _ = para(c, LM + 36, y, body, RM - LM - 46, size, lead)
        y -= 3
    return top - tot - 18


# ---------- 問題ページ ----------
def ans_box(c, x0, x1, y0, y1):
    if not DRY:
        setline(c, .7, INK)
        c.rect(x0, y0, x1 - x0, y1 - y0, fill=0, stroke=1)


def marks(s):
    """{…} でかこんだ部分に下線を引く（国語）。(かっこをとった本文, [(はじめ, おわり)]) を返す。"""
    out, spans, i = '', [], None
    for ch in s:
        if ch == '{':
            i = len(out)
        elif ch == '}':
            spans.append((i, len(out)))
        else:
            out += ch
    return out, spans


def draw_question(c, y, n, q, qs):
    kind = q['kind']
    lead = qs * 1.55
    text(c, LM, y, f'({n})', qs, bold=True)
    tx = LM + 26
    if kind == 'short':
        width = 318
    else:
        width = RM - tx
    plain, spans = marks(q['q'])
    lines = wrap(plain, width, qs)
    pos = 0
    for i, ln in enumerate(lines):
        text(c, tx, y - i * lead, ln, qs)
        at = plain.index(ln, pos)
        for a, b in spans:                              # 下線
            a2, b2 = max(a, at), min(b, at + len(ln))
            if a2 < b2 and not DRY:
                setline(c, .8)
                c.line(tx + tw(ln[:a2 - at], qs), y - i * lead - 2.4, tx + tw(ln[:b2 - at], qs), y - i * lead - 2.4)
        pos = at + len(ln)
    last = y - (len(lines) - 1) * lead
    if kind == 'short':
        if q.get('boxes'):                              # 名前つきの解答らんを、右から順にならべる
            x = RM
            for lab, w_ in reversed(q['boxes']):
                ans_box(c, x - w_, x, last - 8, last + 14)
                text(c, x - w_ - 4 - tw(lab, 8.5), last - 1, lab, 8.5, color=MUTED)
                x -= w_ + 12 + tw(lab, 8.5)
            return last - lead - 8
        if q.get('cells'):                              # 漢字・かなを1字ずつ書く、マス目
            k_, cs = q['cells'], min(22, 150 / q['cells'])
            for k in range(k_):
                ans_box(c, RM - (k_ - k) * cs, RM - (k_ - k - 1) * cs, last - 8, last - 8 + cs)
            return last - lead - 8
        ans_box(c, 404, RM, last - 7, last + qs + 3)
        if q.get('unit'):
            text(c, RM - tw(q['unit'], 9) - 4, last - 1, q['unit'], 9, color=MUTED)
        return last - lead - 6
    y = last - lead + 2
    if kind == 'long':
        ans_box(c, tx, RM, y - 40, y + 4)
        if not DRY:
            setline(c, .4, LINE, (2, 2))
            c.line(tx + 6, y - 18, RM - 6, y - 18)
            c.setDash()
        return y - 40 - lead + 2
    if kind == 'grid':
        labels = q['labels']
        per = q.get('per', min(len(labels), 4))
        cw = (RM - tx) / per
        rows = math.ceil(len(labels) / per)
        for i, lab in enumerate(labels):
            r, k = divmod(i, per)
            cx = tx + k * cw
            cy = y - r * 27
            text(c, cx, cy - 13, lab, 9.5, bold=True, color=ACCENT)
            ans_box(c, cx + tw(lab, 9.5, True) + 5, cx + cw - 6, cy - 19, cy + 3)
        return y - rows * 27 - lead + 8
    raise ValueError(kind)


def page_header(c, subj, dai, title, label, idx, total, year_note):
    text(c, LM, H - 39, f'天理中学校 入試対策  /  {subj}・大問{dai}', 9, bold=True, color=ACCENT)
    ts = 19
    while tw(title, ts, True) > RM - LM and ts > 13:
        ts -= .5
    text(c, LM, H - 74, title, ts, bold=True)
    if not DRY:
        setline(c, 1.2, ACCENT)
        c.line(LM, H - 87, RM, H - 87)
    text(c, LM, 25, year_note, 8, color=MUTED)
    right = f'{label}  {idx:02d} / {total:02d}'
    text(c, RM - tw(right, 8), 25, right, 8, color=MUTED)


# ---------- 作文（縦書き原稿用紙） ----------
GENKO_COLS, GENKO_ROWS, GENKO_CS = 10, 20, 22.5            # 縦書き200字（20字×10行）


def draw_genko(c, gx, top):
    """縦書きの原稿用紙（右上から書き始める）。まん中の太い線は、100字の目じるし。"""
    cs, cols, rows = GENKO_CS, GENKO_COLS, GENKO_ROWS
    if not DRY:
        setline(c, .4, SHADE)
        for r in range(rows + 1):
            c.line(gx, top - r * cs, gx + cols * cs, top - r * cs)
        for k in range(cols + 1):
            c.line(gx + k * cs, top, gx + k * cs, top - rows * cs)
        setline(c, 1.0, INK)
        c.rect(gx, top - rows * cs, cols * cs, rows * cs, fill=0, stroke=1)
        c.line(gx + cols * cs / 2, top, gx + cols * cs / 2, top - rows * cs)
    for r in (5, 10, 15, 20):                                # 1行の字数の目じるし
        text(c, gx - 5 - tw(str(r), 7), top - (r - .5) * cs - 2.4, str(r), 7, color=MUTED)


def render_essay_problem(c, subj, dai, i, st, total):
    ess = st['essay']
    page_header(c, subj, dai, f'第{i:02d}セット　{st["title"]}', '問題', i, total,
                st.get('note') or f'{st["year"]}年度 大問{dai}の出題形式を参考にした独自教材（過去問の転載ではありません）')
    text(c, LM, H - 109, '名前：____________________  日付：____／____  時間：____分', 9.5)
    y = H - 130
    lead_lines = wrap(st['lead'], RM - LM - 20, 10.5)
    bh = len(lead_lines) * 16 + 10
    if not DRY:
        c.setFillColor(PALE)
        c.rect(LM, y - bh + 14, RM - LM, bh, fill=1, stroke=0)
    for ln in lead_lines:
        text(c, LM + 10, y, ln, 10.5)
        y -= 16
    top = y - bh + len(lead_lines) * 16 - 12                  # 左の説明と、右の原稿用紙の、上のはし
    gw = GENKO_COLS * GENKO_CS
    gx = RM - gw
    text(c, RM - tw('原稿用紙（縦書き・200字）', 8), top + 3, '原稿用紙（縦書き・200字）', 8, color=MUTED)
    draw_genko(c, gx, top - 8)
    gbot = top - 8 - GENKO_ROWS * GENKO_CS
    pw = gx - 16 - LM
    yy = top - 12
    text(c, LM, yy, '題', 10, bold=True, color=ACCENT)
    yy, _ = para(c, LM + 22, yy, ess['topic'], pw - 22, 10.5, 16.5, INK, True)
    yy -= 6
    text(c, LM, yy, '条件', 10, bold=True, color=ACCENT)
    for k, cond in enumerate(ess['conds']):
        text(c, LM + 22, yy, '①②③④⑤⑥'[k], 10)
        yy, _ = para(c, LM + 36, yy, cond, pw - 36, 10, 15.5)
        yy -= 1
    yy -= 4
    mat = ess.get('material')
    if mat:
        text(c, LM, yy, '資料', 10, bold=True, color=ACCENT)
        if mat['kind'] == 'table':
            yy = draw_table(c, LM + 30, yy + 8, mat['rows'], mat['colw'], mat.get('size', 9), mat.get('head_col', True), mat.get('head_row', True)) - 6
        elif mat['kind'] == 'fig':
            if not DRY:
                FIGS[mat['name']](c, LM + 28, yy + 12, pw - 28, mat['h'], **mat.get('args', {}))
            yy -= mat['h'] - 6
        else:
            yy, _ = para(c, LM + 30, yy, mat['text'], pw - 30, 9.5, 15)
        if mat.get('note'):
            yy, _ = para(c, LM + 30, yy - 2, mat['note'], pw - 30, 8.5, 13, MUTED)
    assert yy >= gbot - 4, ('作文の説明が長すぎる', st['title'], yy, gbot)
    mtop, mbot = gbot - 18, 72                                 # メモらん
    text(c, LM, mtop + 2, 'メモらん（書くことを、先に書き出そう）', 9, bold=True, color=ACCENT)
    labs = ess.get('memo', ['はじめ', 'なか', 'おわり'])
    bw = (RM - LM - 12 * (len(labs) - 1)) / len(labs)
    for k, lab in enumerate(labs):
        bx = LM + k * (bw + 12)
        if not DRY:
            setline(c, .6, MUTED, (2, 2))
            c.rect(bx, mbot, bw, mtop - 8 - mbot, fill=0, stroke=1)
            c.setDash()
        text(c, bx + 6, mtop - 20, lab, 8.5, color=MUTED)
    text(c, LM, 44, '字数：______字', 9.5, bold=True)
    return mbot


def render_essay_answer(c, subj, dai, i, st, total, s1):
    ess, q = st['essay'], st['qs'][0]
    page_header(c, subj, dai, f'解答・解説　第{i:02d}セット　{st["title"]}', '解答', i, total,
                st.get('note') or f'{st["year"]}年度 大問{dai}の出題形式を参考にした独自教材')
    y = H - 120
    n = len(q['ans'].replace('\n', ''))
    text(c, LM, y, f'例文（{n}字）', 11, bold=True, color=ACCENT)
    y -= 8
    text(c, LM + 100, y + 8, '（これと同じでなくてよい。条件を守り、自分の言葉で書けていればよい）', 8.5, color=MUTED)
    y -= 12
    for para_ in q['ans'].split('\n'):
        y, _ = para(c, LM + 8, y, '　' + para_, RM - LM - 16, s1, s1 * 1.65)
        y -= 3
    y -= 8
    text(c, LM, y, 'この作文のポイント', 11, bold=True, color=ACCENT)
    y -= 18
    for line in q['ex'].split('\n'):
        text(c, LM + 4, y, '・', s1)
        y, _ = para(c, LM + 18, y, line, RM - LM - 18, s1 - .5, (s1 - .5) * 1.55)
        y -= 3
    y -= 10
    text(c, LM, y, '自己採点チェック表', 11, bold=True, color=ACCENT)
    y -= 8
    rows = ess.get('rubric') or [
        ['観点', 'チェックする内容', '配点', '自己採点'],
        ['条件', '字数・段落・指定された言葉や形式を守っている', '3点', '　　点'],
        ['内容', '題に合った内容で、理由や具体例（体験）が書けている', '3点', '　　点'],
        ['表現', '主語と述語が合い、文末（です・ます／だ・である）がそろっている', '2点', '　　点'],
        ['表記', '漢字・かなづかい・句読点・原稿用紙の使い方に、まちがいがない', '2点', '　　点'],
    ]
    y = draw_table(c, LM, y, rows, [48, 345, 42, 76], 9.2, head_col=True, left_cols=(1,))
    text(c, RM - 120, y - 16, '合計　　　　／10点', 10, bold=True)
    y -= 46
    text(c, LM, y, '原稿用紙の使い方', 11, bold=True, color=ACCENT)
    y -= 18
    for line in ['題名・名前は、書かなくてよいと指示されたときは書かない。一行目の一番上のますから書き始める。',
                 '段落のはじめは、一ますあける。',
                 '句読点（、。）も一字として、一ますに書く。行のはじめにくるときは、前の行の最後のますの中に、文字といっしょに書く。',
                 '数字は、漢数字で書く（例：十二人・五百トン）。',
                 '小さい「っ」「ゃ」「ゅ」「ょ」も、一ますに書く。',
                 '字数は、句読点もふくめて数える。指定された字数の八割（百六十字なら百三十字くらい）は書くようにする。']:
        text(c, LM + 4, y, '・', s1 - .5)
        y, _ = para(c, LM + 18, y, line, RM - LM - 18, s1 - .5, (s1 - .5) * 1.55)
        y -= 2
    return y - 4


def render_problem(c, subj, dai, i, st, total, qs):
    if st.get('essay'):
        return render_essay_problem(c, subj, dai, i, st, total)
    page_header(c, subj, dai, f'第{i:02d}セット　{st["title"]}', '問題', i, total,
                st.get('note') or f'{st["year"]}年度 大問{dai}の出題形式を参考にした独自教材（過去問の転載ではありません）')
    text(c, LM, H - 109, '名前：____________________  日付：____／____  時間：____分', 9.5)
    y = H - 130
    lead_lines = wrap(st['lead'], RM - LM - 20, 10.5)
    bh = len(lead_lines) * 16 + 10
    if not DRY:
        c.setFillColor(PALE)
        c.rect(LM, y - bh + 14, RM - LM, bh, fill=1, stroke=0)
    yy = y
    for ln in lead_lines:
        text(c, LM + 10, yy, ln, 10.5)
        yy -= 16
    y = y - bh - 2
    if st.get('items'):
        y = draw_items(c, y, st['items'], st.get('item_size', 10))
    fig, tab = st.get('fig'), st.get('table')
    if fig and tab and st.get('stack'):          # 図を上、表を下（図が横に長いとき）
        if not DRY:
            FIGS[fig['name']](c, LM, y, RM - LM, fig['h'], **fig.get('args', {}))
        y -= fig['h'] + 6
        colw = tab['colw']
        y = draw_table(c, LM + (RM - LM - sum(colw)) / 2, y, tab['rows'], colw,
                       tab.get('size', 9.5), tab.get('head_col', True), tab.get('head_row', True),
                       tab.get('left_cols', ())) - 14
    elif fig and tab:          # 図を左、表を右
        fh = fig['h']
        if not DRY:
            FIGS[fig['name']](c, LM, y, 150, fh, **fig.get('args', {}))
        colw = tab['colw']
        draw_table(c, RM - sum(colw), y - (fh - len(tab['rows']) * tab.get('size', 9.5) * 1.9) / 2,
                   tab['rows'], colw, tab.get('size', 9.5))
        y -= fh + 8
    elif fig:
        if not DRY:
            FIGS[fig['name']](c, LM, y, RM - LM, fig['h'], **fig.get('args', {}))
        y -= fig['h'] + 14
    elif tab:
        colw = tab['colw']
        y = draw_table(c, LM + (RM - LM - sum(colw)) / 2, y, tab['rows'], colw,
                       tab.get('size', 9.5), tab.get('head_col', True), tab.get('head_row', True),
                       tab.get('left_cols', ())) - 14
    y -= qs + 2
    for n, q in enumerate(st['qs'], 1):
        if q.get('head'):                               # 小問のまとまりの見出し（国語）
            y -= 2
            if not DRY:
                c.setFillColor(PALE)
                c.rect(LM, y - 6, RM - LM, 19, fill=1, stroke=0)
            text(c, LM + 6, y, q['head'], 9.5, bold=True, color=ACCENT)
            y -= 24
        y = draw_question(c, y, n, q, qs)
        sp = q.get('space', st.get('space', 0))
        if sp:                                          # 算数：式・考え方を書く、計算らん
            top_ = y + qs * 1.55 - 8
            if not DRY:
                setline(c, .5, LINE, (2, 2))
                c.rect(LM + 26, top_ - sp, RM - LM - 26, sp, stroke=1, fill=0)
                c.setDash()
                text(c, LM + 32, top_ - 10, '式・考え方', 8, color=MUTED)
            y = top_ - sp - 12
        if not DRY and n < len(st['qs']):
            setline(c, .3, LINE)
            c.line(LM, y + qs + 4, RM, y + qs + 4)
        y -= 4
    text(c, LM, 44, f'正答数：____／{len(st["qs"])}問', 9.5, bold=True)
    return y + qs


def build_problems(mod, key, dai, out):
    global DRY
    subj = SUBJECTS[key]
    fn = f'天理中学校_{subj}大問{dai}_類題{len(mod.SETS)}セット_問題.pdf'
    c = canvas.Canvas(str(out / fn), pagesize=A4, pageCompression=1)
    c.setTitle(fn[:-4]); c.setAuthor('若木塾 教材制作')
    for i, st in enumerate(mod.SETS, 1):
        for qs in (10.5, 10, 9.6, 9.2):
            DRY = True
            low = render_problem(c, subj, dai, i, st, len(mod.SETS), qs)
            if low >= BOTTOM + 10:
                break
        DRY = False
        low = render_problem(c, subj, dai, i, st, len(mod.SETS), qs)
        assert low >= BOTTOM + 10, (fn, i, low)
        st['_qsize'] = qs
        c.showPage()
    c.save()
    return out / fn


# ---------- 解答ページ ----------
def ans_text(q):
    if q['kind'] == 'grid':
        return '　'.join(f'{l} {a}' for l, a in zip(q['labels'], q['ans']))
    return q['ans']


def render_answer(c, subj, dai, i, st, total, s1, s2):
    if st.get('essay'):
        return render_essay_answer(c, subj, dai, i, st, total, s1)
    page_header(c, subj, dai, f'解答・解説　第{i:02d}セット　{st["title"]}', '解答', i, total,
                st.get('note') or f'{st["year"]}年度 大問{dai}の出題形式を参考にした独自教材')
    text(c, LM, H - 108, '（　）の中は別の答え方・正解にしてよい例です。記述は、解答例と同じ内容が書けていれば正解とします。'
         if any(q['kind'] == 'long' for q in st['qs']) else '（　）の中は別の答え方・正解にしてよい例です。', 8.5, color=MUTED)
    y = H - 132
    for n, q in enumerate(st['qs'], 1):
        text(c, LM, y, f'({n})', s1, bold=True)
        y, _ = para(c, LM + 30, y, '答　' + ans_text(q), RM - LM - 30, s1, s1 * 1.5, ACCENT, True)
        y, _ = para(c, LM + 30, y + 1, q['ex'], RM - LM - 30, s2, s2 * 1.55, INK)
        if not DRY and n < len(st['qs']):
            setline(c, .3, LINE)
            c.line(LM, y + s2 * .6, RM, y + s2 * .6)
        y -= 6
    return y


def build_answers(mod, key, dai, out):
    global DRY
    subj = SUBJECTS[key]
    fn = f'天理中学校_{subj}大問{dai}_類題{len(mod.SETS)}セット_解答解説.pdf'
    c = canvas.Canvas(str(out / fn), pagesize=A4, pageCompression=1)
    c.setTitle(fn[:-4]); c.setAuthor('若木塾 教材制作')
    for i, st in enumerate(mod.SETS, 1):
        for s1, s2 in ((11, 9.6), (10.5, 9.2), (10, 8.8)):
            DRY = True
            low = render_answer(c, subj, dai, i, st, len(mod.SETS), s1, s2)
            if low >= BOTTOM:
                break
        DRY = False
        low = render_answer(c, subj, dai, i, st, len(mod.SETS), s1, s2)
        assert low >= BOTTOM, (fn, i, low)
        c.showPage()
    c.save()
    return out / fn


# ---------- 出題分析と使い方 ----------
def build_analysis(mod, key, dai, out):
    subj = SUBJECTS[key]
    fn = f'天理中学校_{subj}大問{dai}_出題分析と使い方.pdf'
    c = canvas.Canvas(str(out / fn), pagesize=A4, pageCompression=1)
    c.setTitle(fn[:-4]); c.setAuthor('若木塾 教材制作')
    an = mod.ANALYSIS
    page_header(c, subj, dai, f'出題分析と使い方　{subj}・大問{dai}', '分析', 1, 1,
                an.get('footer', '2014〜2024年度の過去問をもとにした分析（設問は独自に作成）'))
    y = H - 118
    y, _ = para(c, LM, y, an['summary'], RM - LM, 10.5, 17)
    y -= 6
    rows = [['年度', f'大問{dai}の内容', '対応セット']] + an['years']
    y = draw_table(c, LM, y, rows, [52, 371, 88], 9.2, head_col=False)
    y -= 26
    c.setFillColor(PALE); c.rect(LM, y - 9, RM - LM, 24, fill=1, stroke=0)
    text(c, LM + 8, y, 'ねらわれる力', 11, bold=True, color=ACCENT)
    y -= 26
    for s in an['points']:
        text(c, LM + 4, y, '・', 10)
        y, _ = para(c, LM + 18, y, s, RM - LM - 18, 10, 16)
        y -= 2
    y -= 10
    c.setFillColor(PALE); c.rect(LM, y - 9, RM - LM, 24, fill=1, stroke=0)
    text(c, LM + 8, y, '使い方', 11, bold=True, color=ACCENT)
    y -= 26
    for s in an['usage']:
        text(c, LM + 4, y, '・', 10)
        y, _ = para(c, LM + 18, y, s, RM - LM - 18, 10, 16)
        y -= 2
    assert y >= BOTTOM, (fn, y)
    c.showPage()
    c.save()
    return out / fn


# ---------- 検査 ----------
def check_layout():
    bad = []
    by_page = {}
    for f, p, x0, x1, y0, y1, s in LAYOUT:
        if x0 < LM - 1 or x1 > RM + 1 or y0 < 18 or y1 > H - 20:
            bad.append(('はみ出し', f, p, s))
        by_page.setdefault((f, p), []).append((x0, x1, y0, y1, s))
    for key, boxes in by_page.items():
        for i in range(len(boxes)):
            a = boxes[i]
            for b in boxes[i + 1:]:
                if a[0] < b[1] - .5 and b[0] < a[1] - .5 and a[2] < b[3] - .8 and b[2] < a[3] - .8:
                    bad.append(('重なり', key[0], key[1], a[4] + ' / ' + b[4]))
    return bad


def check_text(pdf, mod, kind):
    doc = fitz.open(pdf)
    assert doc.page_count == len(mod.SETS), (pdf, doc.page_count)
    missing = []
    for i, st in enumerate(mod.SETS):
        page = doc[i].get_text().replace('\n', '').replace(' ', '')
        for q in st['qs']:
            key = (q['q'] if kind == 'q' else q['ex']).replace('\n', '').replace(' ', '').replace('{', '').replace('}', '')[:14]
            if key not in page:
                missing.append((i + 1, key))
    return missing


def main():
    key, dai = sys.argv[1], int(sys.argv[2])
    mod = importlib.import_module(f'tenri_rs_{key}{dai}')
    out = ROOT / f'output/天理中学校_{SUBJECTS[key]}大問{dai}対策'
    out.mkdir(parents=True, exist_ok=True)
    p = build_problems(mod, key, dai, out)
    a = build_answers(mod, key, dai, out)
    an = build_analysis(mod, key, dai, out)
    bad = check_layout()
    miss = check_text(p, mod, 'q') + check_text(a, mod, 'a')
    print('問題', p.name, '/ 解答', a.name, '/ 分析', an.name)
    print('設問の文字サイズ:', [st['_qsize'] for st in mod.SETS])
    print('レイアウト不具合:', len(bad))
    for b in bad[:20]:
        print('  ', b)
    print('本文の抽出もれ:', len(miss), miss[:10])
    if bad or miss:
        sys.exit(1)


if __name__ == '__main__':
    main()
