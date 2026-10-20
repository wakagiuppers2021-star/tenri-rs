"""天理中学校 理科・社会 大問別の類題プリントを作る。

使い方: python -X utf8 tools/build_tenri_rs.py rika 1
        python -X utf8 tools/build_tenri_rs.py shakai 1
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

SUBJECTS = {'rika': '理科', 'shakai': '社会'}
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


def wrap(s, width, size=10, bold=False):
    out = []
    for part in s.split('\n'):
        line = ''
        for ch in part:
            if line and tw(line + ch, size, bold) > width:
                if ch in '、。）」』】・,.' and len(line) > 1:
                    out.append(line[:-1])
                    line = line[-1] + ch
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


def fig_lever(c, x, top, w, h):
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
            text(c, hx, by + 10, str(k), 9, center=True)
    text(c, cx - half - 16, by - 4, '左', 10, bold=True)
    text(c, cx + half + 5, by - 4, '右', 10, bold=True)


FIGS = {'monochord': fig_monochord, 'circuits': fig_circuits, 'moon': fig_moon,
        'ice_graph': fig_ice_graph, 'pendulum': fig_pendulum,
        'strata': fig_strata, 'magnet': fig_magnet, 'lever': fig_lever}


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


def draw_question(c, y, n, q, qs):
    kind = q['kind']
    lead = qs * 1.55
    text(c, LM, y, f'({n})', qs, bold=True)
    tx = LM + 26
    if kind == 'short':
        width = 318
    else:
        width = RM - tx
    lines = wrap(q['q'], width, qs)
    for i, ln in enumerate(lines):
        text(c, tx, y - i * lead, ln, qs)
    last = y - (len(lines) - 1) * lead
    if kind == 'short':
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


def render_problem(c, subj, dai, i, st, total, qs):
    page_header(c, subj, dai, f'第{i:02d}セット　{st["title"]}', '問題', i, total,
                f'{st["year"]}年度 大問{dai}の出題形式を参考にした独自教材（過去問の転載ではありません）')
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
    if fig and tab:          # 図を左、表を右
        fh = fig['h']
        if not DRY:
            FIGS[fig['name']](c, LM, y, 150, fh)
        colw = tab['colw']
        draw_table(c, RM - sum(colw), y - (fh - len(tab['rows']) * tab.get('size', 9.5) * 1.9) / 2,
                   tab['rows'], colw, tab.get('size', 9.5))
        y -= fh + 8
    elif fig:
        if not DRY:
            FIGS[fig['name']](c, LM, y, RM - LM, fig['h'])
        y -= fig['h'] + 14
    elif tab:
        colw = tab['colw']
        y = draw_table(c, LM + (RM - LM - sum(colw)) / 2, y, tab['rows'], colw,
                       tab.get('size', 9.5), tab.get('head_col', True), tab.get('head_row', True),
                       tab.get('left_cols', ())) - 14
    y -= qs + 2
    for n, q in enumerate(st['qs'], 1):
        y = draw_question(c, y, n, q, qs)
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
    page_header(c, subj, dai, f'解答・解説　第{i:02d}セット　{st["title"]}', '解答', i, total,
                f'{st["year"]}年度 大問{dai}の出題形式を参考にした独自教材')
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
                '2014〜2024年度の過去問をもとにした分析（設問は独自に作成）')
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
            key = (q['q'] if kind == 'q' else q['ex']).replace('\n', '').replace(' ', '')[:14]
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
