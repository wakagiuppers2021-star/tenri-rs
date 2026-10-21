"""算数・大問7 専用の図（名前は s7_ で始める）。tools/build_tenri_rs.py が、起動時に register(B) を呼んで FIGS にふやす。

s7_gridsolid  方眼の中の斜線部分（汎用の図 geo のパネル）と、円柱を4等分した立体を、横にならべる（第01セット）
s7_gears      かみ合う歯車を、一列にならべる。歯の数だけ、実際に歯をかく。しるしの歯（●）つき（第04セット）
s7_hist       表（人数に ア・イ）と、ヒストグラムを、左右にならべる（第05セット）
s7_rect       長方形ABCDと、点P・Qの出発点と進む向き（第08セット）
s7_tank       水そう（底に金属の立方体）の見取図と、時間と水面の高さのグラフ（第09セット）
s7_numtable   数をならべた表と、縦2つ横2つの4つの数をかこむわく（第10セット）
図の中の長さ・数は、データの args で渡す（問題文の数と、検算で突き合わせる）。
"""
from __future__ import annotations

import math


def register(B):
    colors, text, setline, _poly, _obl, arrow, tw = B.colors, B.text, B.setline, B._poly, B._obl, B.arrow, B.tw
    INK, MUTED, LINE, PALE = B.INK, B.MUTED, B.LINE, B.PALE
    SHADE = colors.HexColor('#DCE2E6')

    # ---------- 円柱を4等分した立体（見取図） ----------
    def quarter_solid(c, px, pw, top, ph, R, H, kx=.5, ky=.4):
        """底面が、半径Rの四分円（おうぎ形）、高さHの立体。中心は、おくの左はし。弧が、手前の右がわ。"""
        sc = min((pw - 46) / (R * (1 + kx)), (ph - 30) / (H + ky * R))
        wd, ht = R * (1 + kx) * sc, (H + ky * R) * sc
        ox, oy = px + (pw - wd) / 2 + 6, top - ph + 18 + (ph - 30 - ht) / 2
        P = _obl(ox, oy, sc, kx, ky)
        arc = [(R * math.cos(math.radians(p)), R + R * math.sin(math.radians(p))) for p in [-90 + 90 * i / 30 for i in range(31)]]
        side = [P(x_, y_, H) for x_, y_ in arc] + [P(x_, y_, 0) for x_, y_ in reversed(arc)]
        setline(c, 1.1)
        c.setFillColor(SHADE)
        c.drawPath(_poly(c, side), stroke=1, fill=1)
        c.setFillColor(colors.white)
        c.drawPath(_poly(c, [P(0, R, H)] + [P(x_, y_, H) for x_, y_ in arc]), stroke=1, fill=1)
        setline(c, .7, INK, (3, 2))                                   # 見えない辺
        c.line(*P(0, R, H), *P(0, R, 0))
        c.line(*P(0, R, 0), *P(0, 0, 0))
        c.line(*P(0, R, 0), *P(R, R, 0))
        setline(c, .8)                                                # 直角の印（上の面の、中心）
        d = R * .13
        c.lines([(*P(0, R - d, H), *P(d, R - d, H)), (*P(d, R, H), *P(d, R - d, H))])
        text(c, P(0, R / 2, H)[0] - 21, P(0, R / 2, H)[1] + 3, f'{R:g}cm', 9)
        text(c, P(0, 0, H / 2)[0] - 25, P(0, 0, H / 2)[1] - 3, f'{H:g}cm', 9)
        text(c, px + pw / 2, top - ph + 3, '円柱を4等分した立体', 8, center=True)

    def fig_gridsolid(c, x, top, w, h, panels=(), solid=None):
        n = len(panels)
        wg = w * n / (n + 1)
        B.FIGS['geo'](c, x, top, wg, h, panels=panels)
        text(c, x + wg + 4, top - 11, solid['cap'], 10, bold=True)
        quarter_solid(c, x + wg, w - wg, top - 24, h - 24, solid['r'], solid['h'])

    # ---------- 歯車 ----------
    def fig_gears(c, x, top, w, h, teeth=(), names='ABC', unit=3.4, mark=None):
        """teeth＝歯の数。直径は歯の数に比例（unit pt／1歯）。mark＝k：k番目と、k+1番目の歯車の、ふれ合う歯に●をつける（0から数える）。"""
        d = 2.4
        rs = [n * unit / 2 for n in teeth]
        cy = top - h / 2 - 2
        x0 = x + (w - sum(2 * r for r in rs)) / 2
        cxs, px = [], x0
        for r in rs:
            cxs.append(px + r)
            px += 2 * r
        offs = []
        for k, n in enumerate(teeth):
            dl = 2 * math.pi / n
            if k == 0:
                offs.append(0.0)
            else:
                dp = 2 * math.pi / teeth[k - 1]
                prev = ((0 - offs[k - 1]) / dp) % 1
                tooth_there = prev < 1e-6 or prev > 1 - 1e-6                 # 前の歯車が、ふれ合う線の上に歯をもっているか
                offs.append(math.pi + dl / 2 if tooth_there else math.pi)
        for k, (n, r, cx) in enumerate(zip(teeth, rs, cxs)):
            dl = 2 * math.pi / n
            pts = []
            for i in range(n):
                a = offs[k] + i * dl
                for da, rad in ((-.28, -d), (-.2, d), (.2, d), (.28, -d)):
                    pts.append((cx + (r + rad) * math.cos(a + da * dl), cy + (r + rad) * math.sin(a + da * dl)))
            setline(c, .9)
            c.setFillColor(colors.white)
            c.drawPath(_poly(c, pts), stroke=1, fill=1)
            setline(c, .6, MUTED)
            c.circle(cx, cy, r - d - 3.5, stroke=1, fill=0)
            text(c, cx, cy + 1, names[k], 11, bold=True, center=True)
            text(c, cx, cy - 11, f'{n}こ', 8, center=True)
        if mark is not None:
            k = mark
            c.setFillColor(INK)
            for g, ang_dir in ((k, 0.0), (k + 1, math.pi)):
                n, r, cx = teeth[g], rs[g], cxs[g]
                dl = 2 * math.pi / n
                rel = ((ang_dir - offs[g]) / dl) % 1
                if rel < 1e-6 or rel > 1 - 1e-6:
                    a = ang_dir                                              # 線の上に歯がある
                else:
                    a = ang_dir + dl / 2 if g == k else ang_dir - dl / 2     # 線の上は、歯のあいだ。となりの歯（上がわ）
                c.circle(cx + (r + .3) * math.cos(a), cy + (r + .3) * math.sin(a), 1.9, stroke=0, fill=1)

    # ---------- 表とヒストグラム ----------
    def fig_hist(c, x, top, w, h, table=None, hist=None):
        # 左：表
        text(c, x, top - 11, table['title'], 10, bold=True)
        rows = [[table['xname']] + [str(v) for v in table['xs']], [table['yname']] + [str(v) for v in table['ys']]]
        colw = [58] + [27] * len(table['xs'])
        ty = top - 26
        B.draw_table(c, x, ty, rows, colw, 9)
        # 右：ヒストグラム
        counts, ymax = hist['counts'], hist['ymax']
        gx0, bw = x + 296, 29
        gx1 = gx0 + bw * len(counts)
        gy0, gy1 = top - h + 26, top - 30
        text(c, gx0 - 28, top - 11, hist['title'], 10, bold=True)
        text(c, gx0 - 28, gy1 + 8, hist['ylab'], 8, color=MUTED)
        for v in range(0, ymax + 1):
            yy = gy0 + (gy1 - gy0) * v / ymax
            setline(c, .35, LINE)
            c.line(gx0, yy, gx1, yy)
            text(c, gx0 - 5 - tw(str(v), 8), yy - 2.8, str(v), 8, color=MUTED)
        for i, v in enumerate(counts):
            bx = gx0 + i * bw
            c.setFillColor(colors.HexColor('#C2C9CE'))
            setline(c, .9)
            c.rect(bx, gy0, bw, (gy1 - gy0) * v / ymax, stroke=1, fill=1)
            text(c, bx + bw / 2, gy0 - 11, str(hist['xs'][i]), 8.5, center=True)
        setline(c, 1.1)
        c.line(gx0, gy0, gx1 + 6, gy0)
        c.line(gx0, gy0, gx0, gy1 + 4)
        text(c, (gx0 + gx1) / 2, gy0 - 23, hist['xlab'], 8.5, color=MUTED, center=True)

    # ---------- 長方形ABCDと、動く2点 ----------
    def fig_rect(c, x, top, w, h, W=12, H=8):
        sc = min((w - 200) / W, (h - 52) / H, 15)
        ox, oy = x + (w - W * sc) / 2, top - 24 - H * sc
        setline(c, 1.2)
        c.setFillColor(colors.white)
        c.rect(ox, oy, W * sc, H * sc, stroke=1, fill=0)
        c.setFillColor(INK)
        for px_, py_ in ((0, 0), (W, 0), (W, H), (0, H)):
            c.circle(ox + px_ * sc, oy + py_ * sc, 1.8, stroke=0, fill=1)
        text(c, ox - 9, oy + H * sc + 4, 'A', 10, bold=True, center=True)
        text(c, ox - 9, oy - 11, 'B', 10, bold=True, center=True)
        text(c, ox + W * sc + 9, oy - 11, 'C', 10, bold=True, center=True)
        text(c, ox + W * sc + 9, oy + H * sc + 4, 'D', 10, bold=True, center=True)
        text(c, ox + W * sc / 2, oy - 13, f'{W:g}cm', 9, center=True)
        text(c, ox - 22, oy + H * sc / 2 - 3, f'{H:g}cm', 9, center=True)
        arrow(c, ox + 6, oy - 5, ox + 34, oy - 5, 5, .9, INK)                    # P：Bから、Cへ
        text(c, ox + 25, oy - 16, 'P', 10, bold=True, center=True)
        arrow(c, ox + W * sc + 6, oy + H * sc - 6, ox + W * sc + 6, oy + H * sc - 34, 5, .9, INK)   # Q：Dから、Cへ
        text(c, ox + W * sc + 17, oy + H * sc - 21, 'Q', 10, bold=True, center=True)

    # ---------- 水そうと、グラフ ----------
    def fig_tank(c, x, top, w, h, a=8, pts=(), xmax=32, ymax=24, xstep=4, ystep=4, xlab='時間（分）', ylab='水面の高さ（cm）'):
        # 見取図：直方体の水そうと、底の立方体
        L, Wd, Ht = 12, 7, 8
        kx, ky = .42, .3
        sc = min(150 / (L + kx * Wd), (h - 44) / (Ht + ky * Wd))
        ox, oy = x + 8, top - h + 24
        P = _obl(ox, oy, sc, kx, ky)
        setline(c, .7, MUTED, (3, 2))
        for q1, q2 in (((0, Wd, 0), (L, Wd, 0)), ((0, Wd, 0), (0, 0, 0)), ((0, Wd, 0), (0, Wd, Ht))):
            c.line(*P(*q1), *P(*q2))
        setline(c, 1.1)
        c.setFillColor(colors.white)
        c.drawPath(_poly(c, [P(0, 0, 0), P(L, 0, 0), P(L, 0, Ht), P(0, 0, Ht)]), stroke=1, fill=0)
        c.drawPath(_poly(c, [P(0, 0, Ht), P(L, 0, Ht), P(L, Wd, Ht), P(0, Wd, Ht)]), stroke=1, fill=0)
        c.drawPath(_poly(c, [P(L, 0, 0), P(L, Wd, 0), P(L, Wd, Ht), P(L, 0, Ht)]), stroke=1, fill=0)
        s_ = 3.4 * a / 8                                                         # 立方体の大きさは、水そうの中での見た目（目安）
        cx0, cy0 = 3.6, 1.6
        faces = [([(cx0, cy0, 0), (cx0 + s_, cy0, 0), (cx0 + s_, cy0, s_), (cx0, cy0, s_)], SHADE),
                 ([(cx0, cy0, s_), (cx0 + s_, cy0, s_), (cx0 + s_, cy0 + s_, s_), (cx0, cy0 + s_, s_)], colors.white),
                 ([(cx0 + s_, cy0, 0), (cx0 + s_, cy0 + s_, 0), (cx0 + s_, cy0 + s_, s_), (cx0 + s_, cy0, s_)], SHADE)]
        for pts_, col in faces:
            c.setFillColor(col)
            c.drawPath(_poly(c, [P(*q) for q in pts_]), stroke=1, fill=1)
        text(c, P(L / 2, 0, 0)[0], oy - 13, '水そう', 9, center=True)
        text(c, P(cx0 + s_ / 2, cy0, s_ / 2)[0], P(cx0 + s_ / 2, cy0, s_ / 2)[1] - 3, '金属', 8.5, center=True)
        # グラフ
        gx0, gx1 = x + 232, x + w - 52
        gy0, gy1 = top - h + 26, top - 28
        X = lambda t: gx0 + (gx1 - gx0) * t / xmax
        Y = lambda v: gy0 + (gy1 - gy0) * v / ymax
        for v in range(0, ymax + 1, ystep):
            setline(c, .35, LINE, (1, 2) if v else None)
            c.line(gx0, Y(v), gx1, Y(v))
            text(c, gx0 - 5 - tw(str(v), 8), Y(v) - 2.8, str(v), 8, color=MUTED)
        for t in range(0, xmax + 1, xstep):
            setline(c, .35, LINE, (1, 2) if t else None)
            c.line(X(t), gy0, X(t), gy1)
            text(c, X(t), gy0 - 11, str(t), 8, color=MUTED, center=True)
        setline(c, 1.1)
        c.line(gx0, gy0, gx1 + 6, gy0)
        c.line(gx0, gy0, gx0, gy1 + 4)
        text(c, gx0 - 30, gy1 + 12, ylab, 8.5)
        text(c, gx1 + 9, gy0 - 3, xlab, 8.5)
        for t, v in pts[1:]:                                                     # 目安の点線（折れ曲がり・終わり）
            setline(c, .6, MUTED, (3, 2))
            c.line(X(t), gy0, X(t), Y(v))
            c.line(gx0, Y(v), X(t), Y(v))
        setline(c, 1.8, INK)
        for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
            c.line(X(t1), Y(v1), X(t2), Y(v2))
        c.setFillColor(INK)
        for t, v in pts[1:]:
            c.circle(X(t), Y(v), 2, stroke=0, fill=1)

    # ---------- 数表 ----------
    def fig_numtable(c, x, top, w, h, cols=8, rows=4, box=(1, 3), start=1):
        """cols個ずつ、start から順に数をならべた表（rows行）と、そのつづき（…）。box＝(上の行, 左の列)（1から数える）：縦2つ横2つをかこむ。"""
        cw, rh = 40, 20
        x0 = x + (w - cols * cw) / 2
        y0 = top - 8
        setline(c, .6, MUTED)
        for r in range(rows + 1):
            n_cells = cols if r < rows else 2
            for k in range(n_cells):
                c.setFillColor(colors.white)
                c.rect(x0 + k * cw, y0 - (r + 1) * rh, cw, rh, stroke=1, fill=1)
                num = start + r * cols + k
                text(c, x0 + k * cw + cw / 2, y0 - (r + 1) * rh + 6.5, str(num), 10, center=True)
        text(c, x0 + 2 * cw + cw / 2, y0 - (rows + 1) * rh + 6.5, '…', 10, center=True)
        br, bc = box
        setline(c, 2.0, INK)
        c.rect(x0 + (bc - 1) * cw + 2, y0 - (br + 1) * rh + 2, 2 * cw - 4, 2 * rh - 4, stroke=1, fill=0)

    B.FIGS['s7_gridsolid'] = fig_gridsolid
    B.FIGS['s7_gears'] = fig_gears
    B.FIGS['s7_hist'] = fig_hist
    B.FIGS['s7_rect'] = fig_rect
    B.FIGS['s7_tank'] = fig_tank
    B.FIGS['s7_numtable'] = fig_numtable
