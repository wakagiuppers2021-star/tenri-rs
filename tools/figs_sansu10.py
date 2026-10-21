"""算数・大問10の図（図の名前は s10_ で始める）。`register(B)` から、builder（build_tenri_rs.py）の部品を使って B.FIGS に登録する。

    s10_graph  折れ線・曲線のグラフ（方眼・目もり・点線のガイドつき）。速さのグラフ（第03・第10セット）
    s10_move   動く三角形と長方形の図＋重なりの面積のグラフ（第01セット）
    s10_dist3  直線上の2点の図＋2点の間の距離のグラフ3つ（第02セット）
    s10_tank   水そうとブロック（見取図）＋水面の高さのグラフ（第04セット）

モジュールの最上部の関数（move_curve）は、図にも検算にも使える、部品のない純粋な計算。
"""
from __future__ import annotations


def move_curve(leg, gap, rw, v, n=60):
    """三角形が動くときの、重なりの面積 y を、時刻 x の関数として返す（折れ線の点の列）。
    三角形：直角をはさむ2辺が leg。先たんの点R は、はじめ長方形の左はしから gap 手前。長方形：横 rw・たて leg。秒速 v。"""
    t0, t1, t2, t3 = gap / v, (gap + leg) / v, (gap + rw) / v, (gap + rw + leg) / v

    def y(t):
        d = v * t - gap                       # 点Rが、長方形の左はしから進んだ道のり
        if d <= 0 or d >= rw + leg:
            return 0.0
        if d <= leg:
            return d * d / 2
        if d <= rw:
            return leg * leg / 2
        return leg * leg / 2 - (d - rw) ** 2 / 2
    pts = [(0.0, 0.0)]
    for a, b in ((t0, t1), (t1, t2), (t2, t3)):
        k = n if b > a else 1
        for i in range(0, k + 1):
            t = a + (b - a) * i / k
            pts.append((t, y(t)))
    return pts


def move_ticks(leg, gap, rw, v):
    """第01セットのグラフの、x軸の目もり（重なり始め・平らな部分の終わり・重なりがなくなる）。"""
    return gap / v, (gap + rw) / v, (gap + rw + leg) / v


def register(B):
    colors, text, setline, tw, arrow = B.colors, B.text, B.setline, B.tw, B.arrow
    INK, MUTED, LINE, ACCENT, PALE, SHADE = B.INK, B.MUTED, B.LINE, B.ACCENT, B.PALE, B.SHADE

    # ---------- グラフの部品 ----------
    def draw_graph(c, gx, gy, gw, gh, xmax, ymax, lines=(), xticks=(), yticks=(), xgrid=(), ygrid=(), guides=(),
                   dots=(), xlab='', ylab='', ylab_dx=0, size=8, origin=True, minor_x=()):
        """gx, gy＝原点の位置（pt）、gw・gh＝軸の長さ（pt）。lines＝[dict(pts=[(x, y), ...], w=, dash=)]。
        xticks・yticks＝[(値, 文字)]（目もりの文字）。xgrid・ygrid＝方眼の線を引く値。guides＝[(x, y)]（点から軸への点線）。"""
        X = lambda t: gx + gw * t / xmax
        Y = lambda u: gy + gh * u / ymax
        for t in minor_x:
            setline(c, .25, LINE)
            c.line(X(t), gy, X(t), gy + gh)
        for t in xgrid:
            setline(c, .4, LINE)
            c.line(X(t), gy, X(t), gy + gh)
        for u in ygrid:
            setline(c, .4, LINE)
            c.line(gx, Y(u), gx + gw, Y(u))
        for t, u in guides:
            setline(c, .7, MUTED, (2, 2))
            c.line(X(t), gy, X(t), Y(u))
            c.line(gx, Y(u), X(t), Y(u))
        c.setDash()
        arrow(c, gx, gy, gx + gw + 9, gy, 5, 1, INK)
        arrow(c, gx, gy, gx, gy + gh + 9, 5, 1, INK)
        for t, lab in xticks:
            setline(c, .8, INK)
            c.line(X(t), gy, X(t), gy - 2.5)
            text(c, X(t), gy - 11, lab, size, color=INK, center=True)
        for u, lab in yticks:
            setline(c, .8, INK)
            c.line(gx, Y(u), gx - 2.5, Y(u))
            text(c, gx - 5 - tw(lab, size), Y(u) - size * .33, lab, size, color=INK)
        if origin:
            text(c, gx - 4 - tw('0', size), gy - 11, '0', size, color=INK)
        for ln in lines:
            setline(c, ln.get('w', 1.7), ln.get('color', ACCENT), ln.get('dash'))
            pts = ln['pts']
            for (t1, u1), (t2, u2) in zip(pts, pts[1:]):
                c.line(X(t1), Y(u1), X(t2), Y(u2))
            c.setDash()
        for t, u in dots:
            c.setFillColor(INK)
            c.circle(X(t), Y(u), 2.1, stroke=0, fill=1)
        if xlab:
            text(c, gx + gw + 13, gy - 3, xlab, size + .5)
        if ylab:
            text(c, gx - 4 + ylab_dx, gy + gh + 14, ylab, size + .5)

    # ---------- 速さのグラフなど（そのまま使うグラフ）----------
    def fig_graph(c, x, top, w, h, xmax=20, ymax=2400, pts=(), xticks=(), yticks=(), xgrid=(), ygrid=(), guides=(),
                  dots=(), xlab='', ylab='', gw=None, ylab_dx=0, left=64, minor_x=()):
        gx, gy = x + left, top - h + 26
        draw_graph(c, gx, gy, gw or (w - left - 50), h - 26 - 24, xmax, ymax, [dict(pts=list(pts))], xticks, yticks,
                   xgrid, ygrid, guides, dots, xlab, ylab, ylab_dx, minor_x=minor_x)

    # ---------- 第01セット：動く三角形と重なりの面積 ----------
    def fig_move(c, x, top, w, h, leg=10, gap=4, rw=20, v=2, unit='秒速'):
        # 左：図
        pw = 262
        sc = (pw - 50) / (gap + rw + leg)
        ox = x + 36 + 0                               # 三角形の左はし（点Q）の位置
        base = top - h + 62                           # 直線の高さ
        qx, rx_, rectx = ox, ox + leg * sc, ox + (leg + gap) * sc
        # 直線
        setline(c, 1)
        c.line(ox - 12, base, rectx + rw * sc + 10, base)
        # 長方形
        c.setFillColor(PALE)
        setline(c, 1.1)
        c.rect(rectx, base, rw * sc, leg * sc, fill=1, stroke=1)
        # 三角形
        p = c.beginPath()
        p.moveTo(qx, base)
        p.lineTo(rx_, base)
        p.lineTo(qx, base + leg * sc)
        p.close()
        c.setFillColor(colors.HexColor('#C2C9CE'))
        setline(c, 1.3)
        c.drawPath(p, fill=1, stroke=1)
        setline(c, .8)
        c.lines([(qx, base + 6, qx + 6, base + 6), (qx + 6, base, qx + 6, base + 6)])          # 直角の印
        # 記号
        text(c, qx, base + leg * sc + 5, 'P', 9.5, bold=True, center=True)
        text(c, qx - 8, base - 11, 'Q', 9.5, bold=True, center=True)
        text(c, rx_, base - 11, 'R', 9.5, bold=True, center=True)
        # 長さ：たての辺
        arrow(c, qx - 12, base + 1, qx - 12, base + leg * sc - 1, 4, .7, MUTED)
        arrow(c, qx - 12, base + leg * sc - 1, qx - 12, base + 1, 4, .7, MUTED)
        text(c, qx - 16 - tw(f'{leg}cm', 8.5), base + leg * sc / 2 - 3, f'{leg}cm', 8.5)
        # はなれている長さ
        yy = base - 24
        arrow(c, rx_ + 1, yy, rectx - 1, yy, 4, .7, MUTED)
        arrow(c, rectx - 1, yy, rx_ + 1, yy, 4, .7, MUTED)
        setline(c, .5, MUTED)
        c.line(rx_, base - 14, rx_, yy - 3)
        c.line(rectx, base - 14, rectx, yy - 3)
        text(c, (rx_ + rectx) / 2, yy - 12, f'{gap}cm', 8.5, center=True)
        # 動く向き
        arrow(c, qx + 14, base + leg * sc + 12, qx + 50, base + leg * sc + 12, 5, 1.2, ACCENT)
        text(c, qx + 14, base + leg * sc + 17, f'{unit}{v}cm', 8.5, color=ACCENT)
        text(c, rectx + rw * sc / 2, base + leg * sc / 2 - 3, '長方形', 9, color=MUTED, center=True)
        # 右：グラフ
        pts = move_curve(leg, gap, rw, v)
        t0, t2, t3 = move_ticks(leg, gap, rw, v)
        ymax = leg * leg / 2
        gx, gy = x + pw + 40, top - h + 28
        gwid = w - pw - 40 - 52
        draw_graph(c, gx, gy, gwid, h - 28 - 26, t3 + 2.5, ymax * 1.2, [dict(pts=pts)],
                   xticks=[(t0, f'{t0:g}'), (t2, f'{t2:g}'), (t3, 'イ')], yticks=[(ymax, 'ア')],
                   guides=[(t2, ymax)], xlab='x（秒）', ylab='y（cm²）', ylab_dx=-6, origin=True)

    # ---------- 第02セット：往復する2点と、距離のグラフ ----------
    def fig_dist3(c, x, top, w, h, L=12, p=3, q=1, graphs=()):
        xa, xb = x + 70, x + w - 70
        y0 = top - 22
        setline(c, 1.1)
        c.line(xa - 14, y0, xb + 14, y0)
        for xx, lab in ((xa, 'A'), (xb, 'B')):
            setline(c, 1)
            c.line(xx, y0 - 4, xx, y0 + 4)
            text(c, xx, y0 - 15, lab, 9.5, bold=True, center=True)
        # 点P・Q（出発のとき：Pは点A、Qは点B）
        c.setFillColor(INK)
        c.circle(xa, y0, 2.8, stroke=0, fill=1)
        c.circle(xb, y0, 2.8, stroke=0, fill=1)
        arrow(c, xa + 6, y0 + 9, xa + 40, y0 + 9, 5, 1.2, ACCENT)
        arrow(c, xb - 6, y0 + 9, xb - 40, y0 + 9, 5, 1.2, ACCENT)
        text(c, xa, y0 + 13, 'P', 9.5, bold=True, center=True)
        text(c, xb, y0 + 13, 'Q', 9.5, bold=True, center=True)
        text(c, xa + 44, y0 + 6, f'毎秒{p}cm', 8, color=ACCENT)
        text(c, xb - 44 - tw(f'毎秒{q}cm', 8), y0 + 6, f'毎秒{q}cm', 8, color=ACCENT)
        yy = y0 - 27
        arrow(c, xa, yy, xb, yy, 4, .7, MUTED)
        arrow(c, xb, yy, xa, yy, 4, .7, MUTED)
        text(c, (xa + xb) / 2, yy + 3, f'{L}cm', 8.5, center=True)
        # グラフ3つ
        n = len(graphs)
        pw = w / n
        gtop = yy - 20
        for k, (lab, pts) in enumerate(graphs):
            px = x + k * pw
            gx = px + 34
            gy = top - h + 24
            gwid = pw - 34 - 44
            ghgt = gtop - gy - 18
            text(c, px + 6, gtop - 8, lab, 11, bold=True, color=ACCENT)
            draw_graph(c, gx, gy, gwid, ghgt, 12, L, [dict(pts=[tuple(pt) for pt in pts])],
                       xticks=[(3, '3'), (6, '6'), (9, '9'), (12, '12')], yticks=[(4, '4'), (8, '8'), (12, '12')],
                       xgrid=[3, 6, 9, 12], ygrid=[4, 8, 12], minor_x=[1, 2, 4, 5, 7, 8, 10, 11], size=7.5,
                       xlab='時間(秒)', ylab='きょり(cm)', ylab_dx=-6)

    # ---------- 第04セット：水そうとブロックの見取図＋グラフ ----------
    def oblique_box(c, x, y, wf, hf, ox, oy):
        """前の面が (x, y)〜(x+wf, y+hf)、うしろの面が (ox, oy) だけずれた、ふたのない箱（見えない辺は点線）。"""
        setline(c, .8, MUTED, (3, 2))
        c.line(x, y, x + ox, y + oy)
        c.line(x + ox, y + oy, x + wf + ox, y + oy)
        c.line(x + ox, y + oy, x + ox, y + hf + oy)
        c.setDash()
        setline(c, 1.2, INK)
        c.rect(x, y, wf, hf, fill=0, stroke=1)
        c.line(x, y + hf, x + ox, y + hf + oy)
        c.line(x + ox, y + hf + oy, x + wf + ox, y + hf + oy)
        c.line(x + wf, y + hf, x + wf + ox, y + hf + oy)
        c.line(x + wf, y, x + wf + ox, y + oy)
        c.line(x + wf + ox, y + oy, x + wf + ox, y + hf + oy)

    def cube_stack(c, x, y, cs, cols, ox, oy):
        """1辺 cs（pt）の立方体の、たかさ cols[i] の柱を左から順にならべたブロック。"""
        light, mid = colors.white, colors.HexColor('#C2C9CE')
        for i, hgt in enumerate(cols):
            for l in range(hgt):
                bx, by = x + i * cs, y + l * cs
                setline(c, 1.1, INK)
                c.setFillColor(light)
                c.rect(bx, by, cs, cs, fill=1, stroke=1)
                if l == hgt - 1:                                                  # 上の面
                    c.setFillColor(PALE)
                    c.drawPath(B._poly(c, [(bx, by + cs), (bx + ox, by + cs + oy), (bx + cs + ox, by + cs + oy), (bx + cs, by + cs)]), fill=1, stroke=1)
                if i == len(cols) - 1 or cols[i + 1] <= l:                       # 右の面
                    c.setFillColor(mid)
                    c.drawPath(B._poly(c, [(bx + cs, by), (bx + cs + ox, by + oy), (bx + cs + ox, by + cs + oy), (bx + cs, by + cs)]), fill=1, stroke=1)

    def fig_tank(c, x, top, w, h, tank_h=40, cube=10, cols=(3, 2, 1), pts=(), xticks=(), yticks=(), guides=(), xmax=56, ymax=44,
                 tank_w=40, tank_d=20):
        k = 2.0                                                                   # 1cm＝2pt
        base = top - h + 40
        tx = x + 28
        ox, oy = tank_d * k * .42, tank_d * k * .3
        oblique_box(c, tx, base, tank_w * k, tank_h * k, ox, oy)
        # たかさ
        arrow(c, tx - 7, base + 1, tx - 7, base + tank_h * k - 1, 4, .7, MUTED)
        arrow(c, tx - 7, base + tank_h * k - 1, tx - 7, base + 1, 4, .7, MUTED)
        text(c, tx - 11 - tw(f'{tank_h}cm', 8.5), base + tank_h * k / 2 - 3, f'{tank_h}cm', 8.5)
        text(c, tx + tank_w * k / 2 + ox / 2, base - 13, '水そう（ア）', 9.5, bold=True, center=True)
        # ブロック
        cs = cube * k
        bx = tx + tank_w * k + ox + 30
        cube_stack(c, bx, base, cs, cols, cs * .42, cs * .3)
        yy = base - 9
        arrow(c, bx, yy, bx + cs, yy, 4, .7, MUTED)
        arrow(c, bx + cs, yy, bx, yy, 4, .7, MUTED)
        text(c, bx + cs / 2, yy - 11, f'{cube}cm', 8.5, center=True)
        text(c, bx + len(cols) * cs / 2, base - 33, 'ブロック（イ）', 9.5, bold=True, center=True)
        # グラフ
        gx = x + 268 + 22
        gy = top - h + 34
        draw_graph(c, gx, gy, w - 268 - 22 - 58, h - 34 - 26, xmax, ymax, [dict(pts=[tuple(p) for p in pts])],
                   xticks=xticks, yticks=yticks, guides=guides, xlab='時間(分)', ylab='水面の高さ(cm)', ylab_dx=-20)
        # (最後の点の高さまでの点線)
        top_y = max(v for _, v in pts)
        setline(c, .7, MUTED, (2, 2))
        c.line(gx, gy + (h - 34 - 26) * top_y / ymax, gx + (w - 268 - 22 - 58) * pts[-1][0] / xmax, gy + (h - 34 - 26) * top_y / ymax)
        c.setDash()

    B.FIGS['s10_graph'] = fig_graph
    B.FIGS['s10_move'] = fig_move
    B.FIGS['s10_dist3'] = fig_dist3
    B.FIGS['s10_tank'] = fig_tank
