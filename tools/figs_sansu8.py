"""算数・大問8 専用の図（図の名前は s8_ で始める）。builder が、起動時に register(この module) を呼ぶ。

    s8_graph   折れ線グラフ（時間と距離・水の量・長さ）。軸の目もり・案内線・点・文字・水そうの絵（inset='tank'）
    s8_track   円形の遊歩道（反対向き・同じ向きに歩く）
    s8_solids  立体の見取図（半円柱・階だん状の柱）
"""
from __future__ import annotations

import math


def register(B):
    colors, text, setline, _poly, _obl, _faces = B.colors, B.text, B.setline, B._poly, B._obl, B._faces
    INK, MUTED, LINE, PALE, SHADE = B.INK, B.MUTED, B.LINE, B.PALE, B.SHADE
    tw, arrow = B.tw, B.arrow

    # ---------- 折れ線グラフ ----------
    def _tick(v):
        """目もりの指定は、数 または (数, '表示する文字')。"""
        return (v, f'{v:g}') if not isinstance(v, (tuple, list)) else (v[0], v[1])

    def _tank(c, x0, y0, wd, ht):
        """水そうの絵。(x0, y0) は左下。A管（上から入れる）とB管（下から出す）。"""
        water = ht * .5
        c.setFillColor(PALE)
        c.rect(x0, y0, wd, water, stroke=0, fill=1)
        setline(c, .8, MUTED)
        pts = []
        for k in range(0, 41):
            u = k / 40
            pts.append((x0 + wd * u, y0 + water + 2.2 * math.sin(u * math.pi * 6)))
        for (a, b), (a2, b2) in zip(pts, pts[1:]):
            c.line(a, b, a2, b2)
        setline(c, 1.5, INK)
        c.line(x0, y0 + ht, x0, y0)
        c.line(x0, y0, x0 + wd, y0)
        c.line(x0 + wd, y0, x0 + wd, y0 + ht)
        # A管：水そうの上、左から入れる
        py = y0 + ht + 16
        setline(c, 1.5, INK)
        c.line(x0 - 24, py, x0 + 24, py)
        c.line(x0 + 24, py, x0 + 24, py - 12)
        c.line(x0 - 24, py - 6, x0 + 18, py - 6)
        c.line(x0 + 18, py - 6, x0 + 18, py - 12)
        arrow(c, x0 + 21, py - 6, x0 + 21, y0 + water + 10, 5, .9, INK)
        text(c, x0 - 40 + 0, py - 3, 'A管', 9.5, bold=True)
        # B管：水そうの下の右はし、外へ出す
        bx = x0 + wd - 26
        setline(c, 1.5, INK)
        c.line(bx, y0, bx, y0 - 14)
        c.line(bx + 7, y0, bx + 7, y0 - 14)
        c.line(bx - 3, y0 - 14, bx + 10, y0 - 14)
        arrow(c, bx + 3.5, y0 - 15, bx + 3.5, y0 - 29, 5, .9, INK)
        text(c, bx + 16, y0 - 22, 'B管', 9.5, bold=True)

    def fig_graph(c, x, top, w, h, xmax=10, ymax=10, xticks=(), yticks=(), xgrid=(), ygrid=(), xlab='', ylab='',
                  series=(), guides=(), dots=(), texts=(), box=(.1, .88), xlab_below=False, inset=None, ylab_dx=-28):
        gx0, gx1 = x + w * box[0], x + w * box[1]
        gy0, gy1 = top - h + (32 if xlab_below else 22), top - 24

        def X(t): return gx0 + (gx1 - gx0) * t / xmax
        def Y(v): return gy0 + (gy1 - gy0) * v / ymax
        for t in xgrid:
            setline(c, .35, LINE)
            c.line(X(t), gy0, X(t), gy1)
        for v in ygrid:
            setline(c, .35, LINE)
            c.line(gx0, Y(v), gx1, Y(v))
        for v in yticks:
            v_, lab = _tick(v)
            setline(c, .5, MUTED)
            c.line(gx0 - 3, Y(v_), gx0, Y(v_))
            text(c, gx0 - 6 - tw(lab, 8), Y(v_) - 2.6, lab, 8, color=MUTED)
        for t in xticks:
            t_, lab = _tick(t)
            setline(c, .5, MUTED)
            c.line(X(t_), gy0 - 3, X(t_), gy0)
            text(c, X(t_), gy0 - 11.5, lab, 8, color=MUTED, center=True)
        arrow(c, gx0, gy0, gx1 + 10, gy0, 5, 1, INK)
        arrow(c, gx0, gy0, gx0, gy1 + 9, 5, 1, INK)
        if ylab:
            text(c, gx0 + ylab_dx, gy1 + 13, ylab, 8.5)
        if xlab:
            if xlab_below:
                text(c, (gx0 + gx1) / 2, gy0 - 25, xlab, 8.5, center=True)
            else:
                text(c, gx1 + 16, gy0 - 3, xlab, 8.5)
        for g in guides:                                    # 案内線（点線）：(横, 縦) または (横, 縦, 'h' | 'v' | 'hv')
            gxv, gyv = g[0], g[1]
            mode = g[2] if len(g) > 2 else 'hv'
            setline(c, .7, MUTED, (1.5, 2.2))
            if 'v' in mode:
                c.line(X(gxv), gy0, X(gxv), Y(gyv))
            if 'h' in mode:
                c.line(gx0, Y(gyv), X(gxv), Y(gyv))
            c.setDash()
        styles = {'solid': (INK, 1.8, None), 'dash': (INK, 1.4, (4.5, 2.6)), 'dot': (MUTED, 1.9, (1, 2.4))}
        for s in series:
            col, lw, dash = styles[s.get('style', 'solid')]
            setline(c, lw, col, dash)
            pts = s['pts']
            for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
                c.line(X(t1), Y(v1), X(t2), Y(v2))
            c.setDash()
        c.setFillColor(INK)
        for t, v in dots:
            c.circle(X(t), Y(v), 2, stroke=0, fill=1)
        for tx in texts:                                    # (横, 縦, 文字, dx, dy) 　dx, dy は pt
            t, v, s = tx[0], tx[1], tx[2]
            dx = tx[3] if len(tx) > 3 else 0
            dy = tx[4] if len(tx) > 4 else 0
            text(c, X(t) + dx, Y(v) + dy - 3, s, 9.5, bold=True, center=True)
        if inset == 'tank':
            _tank(c, x + 34, top - 118, 116, 68)

    # ---------- 円形の遊歩道 ----------
    def _arc_arrow(c, cx, cy, r, a0, a1):
        """半径 r の円の上を、角 a0 から a1（度）へ向かう矢印（a1 < a0 なら右まわり）。"""
        setline(c, 1.3, INK)
        c.arc(cx - r, cy - r, cx + r, cy + r, a0, a1 - a0)
        ex, ey = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
        sgn = 1 if a1 > a0 else -1
        tx, ty = -math.sin(math.radians(a1)) * sgn, math.cos(math.radians(a1)) * sgn      # 進む向き
        p = c.beginPath()
        p.moveTo(ex + tx * 4, ey + ty * 4)
        nx, ny = math.cos(math.radians(a1)), math.sin(math.radians(a1))
        p.lineTo(ex - tx * 3 + nx * 3.6, ey - ty * 3 + ny * 3.6)
        p.lineTo(ex - tx * 3 - nx * 3.6, ey - ty * 3 - ny * 3.6)
        p.close()
        c.setFillColor(INK)
        c.drawPath(p, stroke=0, fill=1)

    def fig_track(c, x, top, w, h, panels=()):
        n = len(panels)
        pw = w / n
        for k, pn in enumerate(panels):
            px = x + pw * k
            text(c, px + 4, top - 11, pn['cap'], 9.5, bold=True)
            r = min(pw / 2 - 52, (h - 56) / 2)
            cx, cy = px + pw / 2, top - 24 - 14 - r
            setline(c, 2.2, INK)
            c.circle(cx, cy, r, stroke=1, fill=0)
            # スタート地点（真上）
            c.setFillColor(INK)
            c.circle(cx, cy + r, 2.6, stroke=0, fill=1)
            text(c, cx, cy + r + 8, 'スタート', 8.5, center=True)
            # A：右まわり（内がわ）
            _arc_arrow(c, cx, cy, r - 10, 86, 36)
            text(c, cx + (r - 28) * math.cos(math.radians(58)), cy + (r - 28) * math.sin(math.radians(58)) - 3, 'A', 9.5, bold=True, center=True)
            if pn['mode'] == 'opp':                           # B：左まわり（外がわ）
                _arc_arrow(c, cx, cy, r + 10, 94, 144)
                text(c, cx + (r + 22) * math.cos(math.radians(122)), cy + (r + 22) * math.sin(math.radians(122)) - 3, 'B', 9.5, bold=True, center=True)
            else:                                             # B：右まわり（外がわ）
                _arc_arrow(c, cx, cy, r + 10, 86, 30)
                text(c, cx + (r + 22) * math.cos(math.radians(52)), cy + (r + 22) * math.sin(math.radians(52)) - 3, 'B', 9.5, bold=True, center=True)
            text(c, cx, cy + 2, pn['lap'], 9.5, center=True)
            text(c, cx, cy - 12, '（1周）', 8, color=MUTED, center=True)

    # ---------- 立体の見取図 ----------
    KX, KY = .42, .3

    def _s_halfcyl(c, px, pw, top, h, a):
        d, L = a['d'], a['L']
        r = d / 2
        sc = min((pw - 46) / (d + KX * L), (h - 54) / (r + KY * L))
        wid = (d + KX * L) * sc
        ox = px + 22 + (pw - 44 - wid) / 2
        oy = top - 28 - (r + KY * L) * sc
        P = _obl(ox, oy, sc, KX, KY)
        tht = math.pi - math.atan(KX / KY)                    # 曲面の輪かくの線がふれる角
        N = 48
        front = lambda t: P(r + r * math.cos(t), 0, r * math.sin(t))
        back = lambda t: P(r + r * math.cos(t), L, r * math.sin(t))
        sil = [front(tht * i / N) for i in range(N + 1)] + [back(tht * (N - i) / N) for i in range(N + 1)]
        c.setFillColor(SHADE)
        setline(c, 1.1)
        c.drawPath(_poly(c, sil), stroke=1, fill=1)
        fr = [front(math.pi * i / N) for i in range(N + 1)]
        c.setFillColor(colors.white)
        c.drawPath(_poly(c, fr), stroke=1, fill=1)
        fx, fy = front(math.pi / 2)
        text(c, P(r, 0, 0)[0], P(0, 0, 0)[1] - 12, f'{d:g}cm', 9, center=True)
        bx, by = P(d, L / 2, 0)
        text(c, bx + 6, by - 10, f'{L:g}cm', 9)

    def _s_stairs(c, px, pw, top, h, a):
        ws, hs, D = a['w'], a['h'], a['depth']
        n = len(ws)
        X = [0]
        for v in ws:
            X.append(X[-1] + v)
        W, H = X[-1], hs[0]
        sc = min((pw - 70) / (W + KX * D), (h - 56) / (H + KY * D))
        wid = (W + KX * D) * sc
        ox = px + 36 + (pw - 72 - wid) / 2
        oy = top - 28 - (H + KY * D) * sc
        P = _obl(ox, oy, sc, KX, KY)
        faces = [([(W, 0, 0), (W, D, 0), (W, D, hs[-1]), (W, 0, hs[-1])], SHADE)]
        for i in range(n - 1):                                 # 右むきの段の面
            faces.append(([(X[i + 1], 0, hs[i + 1]), (X[i + 1], D, hs[i + 1]), (X[i + 1], D, hs[i]), (X[i + 1], 0, hs[i])], SHADE))
        for i in range(n):                                     # 上の面
            faces.append(([(X[i], 0, hs[i]), (X[i + 1], 0, hs[i]), (X[i + 1], D, hs[i]), (X[i], D, hs[i])], PALE))
        prof = [(0, 0, 0), (W, 0, 0)]
        for i in range(n - 1, -1, -1):
            prof += [(X[i + 1], 0, hs[i]), (X[i], 0, hs[i])]
        faces.append((prof, colors.white))
        _faces(c, P, faces)
        # 長さ（正面の下に横の長さ、左に全体の高さ、段の高さ、おくゆき）
        for i in range(n):
            text(c, P((X[i] + X[i + 1]) / 2, 0, 0)[0], P(0, 0, 0)[1] - 12, f'{ws[i]:g}cm', 9, center=True)
        text(c, P(0, 0, H / 2)[0] - 5 - tw(f'{H:g}cm', 9), P(0, 0, H / 2)[1] - 3, f'{H:g}cm', 9)
        for i in range(n - 1):                                 # 段の高さ（正面の段の縦の辺の、右がわ）
            zc = (hs[i] + hs[i + 1]) / 2
            sx, sy = P(X[i + 1], 0, zc)
            text(c, sx + 4, sy - 3, f'{hs[i] - hs[i + 1]:g}cm', 9)
        ex, ey = P(W, 0, hs[-1] / 2)
        text(c, ex + 4, ey - 3, f'{hs[-1]:g}cm', 9)
        bx, by = P(W, D / 2, 0)
        text(c, bx + 6, by - 10, f'{D:g}cm', 9)

    SOLIDS = {'halfcyl': _s_halfcyl, 'stairs': _s_stairs}

    def fig_solids(c, x, top, w, h, specs=()):
        wts = [a.get('wt', 1) for _, a in specs]
        cum = 0
        for k, (kind, a) in enumerate(specs):
            pw = w * wts[k] / sum(wts)
            px = x + w * cum / sum(wts)
            cum += wts[k]
            text(c, px + 4, top - 11, f'({k + 1})', 10, bold=True)
            SOLIDS[kind](c, px, pw, top, h, a)

    B.FIGS['s8_graph'] = fig_graph
    B.FIGS['s8_track'] = fig_track
    B.FIGS['s8_solids'] = fig_solids
