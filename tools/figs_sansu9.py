"""算数・大問9 専用の図（名前は s9_ で始める）。tools/build_tenri_rs.py が register(B) を呼んで、B.FIGS にふやす。

図（セットの fig に name で書く）:
    s9_graph   折れ線グラフ（時間と、水面の高さ・道のり）。目もり・ガイドの点線・凡例・水そうの略図
    s9_solids  見取図（斜投影）。kind='cubehole'（立方体から円柱をくりぬく）・'steps'（階段の形の立体）
    s9_rows    数を段にならべた表
    s9_stones  白石○と黒石●のならび
    s9_roads   格子状の道（通れない道つき）
どれも、検算（tools/check_sansu9.py）が、args の数値から計算しなおす。
"""
from __future__ import annotations

import math


def register(B):
    colors, text, setline, tw, arrow = B.colors, B.text, B.setline, B.tw, B.arrow
    INK, MUTED, LINE, PALE, ACCENT = B.INK, B.MUTED, B.LINE, B.PALE, B.ACCENT
    SHADE = colors.HexColor('#DCE2E6')
    _poly, _obl = B._poly, B._obl

    def fmt(v):
        return f'{v:g}'

    # ---------- 折れ線グラフ ----------
    def fig_graph(c, x, top, w, h, series=(), xmax=60, ymax=24, xticks=(), yticks=(), xlab='時間（分）', ylab='',
                  guides=(), xgrid=None, ygrid=None, ylabels=None, legend=True, tank=False, left=64, right=18,
                  dots=True, xlabels=None):
        """series=[dict(pts=[(時間, 値), ...], dash=None|(4,2.5)|(1,2.5), label='凡例の文字')]。
        xticks・yticks の数だけ、目もりの数字を出す（ylabels={値: '文字'} で、数字を文字にかえられる）。
        guides=[(時間, 値), ...] は、点から、軸までの点線。tank=True のときは、左に水そうの略図（A・B管、C管）をつける。"""
        ylabels = ylabels or {}
        xlabels = xlabels or {}
        gx0 = x + left + (150 if tank else 0)
        gx1 = x + w - right
        has_leg = legend and any(s.get('label') for s in series)
        gy1 = top - (30 if has_leg else 22)
        gy0 = top - h + 30
        X = lambda t: gx0 + (gx1 - gx0) * t / xmax
        Y = lambda v: gy0 + (gy1 - gy0) * v / ymax
        if xgrid:
            k = 0
            while k <= xmax + 1e-9:
                setline(c, .3, LINE)
                c.line(X(k), gy0, X(k), gy1)
                k += xgrid
        if ygrid:
            k = 0
            while k <= ymax + 1e-9:
                setline(c, .3, LINE)
                c.line(gx0, Y(k), gx1, Y(k))
                k += ygrid
        for (t, v) in guides:
            setline(c, .6, MUTED, (1.5, 2.2))
            c.line(X(t), gy0, X(t), Y(v))
            c.line(gx0, Y(v), X(t), Y(v))
        c.setDash()
        setline(c, 1.1, INK)
        c.line(gx0, gy0, gx1 + 4, gy0)
        c.line(gx0, gy0, gx0, gy1 + 4)
        arrow(c, gx1 - 2, gy0, gx1 + 8, gy0, 5, 1.1)
        arrow(c, gx0, gy1 - 2, gx0, gy1 + 8, 5, 1.1)
        for t in xticks:
            setline(c, .8, INK)
            c.line(X(t), gy0 - 2.5, X(t), gy0 + 2.5)
            lab = xlabels.get(t, fmt(t))
            text(c, X(t), gy0 - 12, lab, 8.5, color=INK, center=True)
        for v in yticks:
            setline(c, .8, INK)
            c.line(gx0 - 2.5, Y(v), gx0 + 2.5, Y(v))
            lab = ylabels.get(v, fmt(v))
            text(c, gx0 - 6 - tw(lab, 8.5), Y(v) - 3, lab, 8.5, color=INK)
        text(c, gx0 + 3, gy1 + 9, ylab, 8.5, bold=True)
        text(c, gx1 + 9 - tw(xlab, 8.5), gy0 - 25, xlab, 8.5, bold=True)
        for k, s in enumerate(series):
            col = s.get('color', INK)
            dash = s.get('dash')
            setline(c, s.get('w', 1.7), col, dash)
            pts = s['pts']
            for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
                c.line(X(t1), Y(v1), X(t2), Y(v2))
            c.setDash()
            if dots:
                c.setFillColor(col)
                for t, v in pts[1:-1] if s.get('inner_dots') else []:
                    c.circle(X(t), Y(v), 2.0, stroke=0, fill=1)
        if has_leg:
            lx = gx0 + 4
            for k, s in enumerate(series):
                if not s.get('label'):
                    continue
                setline(c, s.get('w', 1.7), s.get('color', INK), s.get('dash'))
                c.line(lx, gy1 + 19, lx + 26, gy1 + 19)
                c.setDash()
                text(c, lx + 31, gy1 + 16, s['label'], 9, bold=True)
                lx += 31 + tw(s['label'], 9, True) + 22
        if tank:
            _tank(c, x + 6, gy0, gy1)

    def _tank(c, x0, gy0, gy1):
        """水そうの略図（正面）。A管・B管は上から水を入れ、C管は右下から水を出す。"""
        tw_, th = 92, (gy1 - gy0) - 40
        bx, by = x0 + 22, gy0 + 6
        setline(c, 1.3, INK)
        c.setFillColor(colors.white)
        c.rect(bx, by, tw_, th, stroke=1, fill=1)
        c.setFillColor(PALE)
        c.rect(bx + .6, by + .6, tw_ - 1.2, th * .45, stroke=0, fill=1)
        setline(c, .7, MUTED, (3, 2))
        c.line(bx + 3, by + th * .45, bx + tw_ - 3, by + th * .45)
        c.setDash()
        for k, nm in enumerate(('A', 'B')):                    # 入れる管
            px = bx + 16 + k * 40
            setline(c, 1.3, INK)
            c.setFillColor(colors.white)
            c.rect(px - 5, by + th + 3, 10, 14, stroke=1, fill=1)
            arrow(c, px, by + th + 3, px, by + th - 12, 5, 1.0)
            text(c, px, by + th + 21, nm + '管', 9, bold=True, center=True)
        setline(c, 1.3, INK)                                   # 出す管
        c.setFillColor(colors.white)
        c.rect(bx + tw_, by + 6, 14, 9, stroke=1, fill=1)
        arrow(c, bx + tw_ + 14, by + 10.5, bx + tw_ + 30, by + 10.5, 5, 1.0)
        text(c, bx + tw_ + 22, by + 20, 'C管', 9, bold=True, center=True)

    # ---------- 見取図 ----------
    def _ell(P, cx, cy, r, z, n=72):
        return [P(cx + r * math.cos(2 * math.pi * k / n), cy + r * math.sin(2 * math.pi * k / n), z) for k in range(n)]

    def _path(c, pts, close=True):
        p = c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        if close:
            p.close()
        return p

    def _solid_cubehole(c, px, pw, top, h, a):
        """立方体から、上の面から下の面までまっすぐに、円柱をくりぬいた立体。a: side（立方体の1辺）, d（円柱の直径）"""
        s, d = a['side'], a['d']
        kx, ky = .42, .3
        sc = min((pw - 40) / (s + kx * s), (h - 52) / (s + ky * s))
        ox = px + 20 + (pw - 40 - (s + kx * s) * sc) / 2
        oy = top - 22 - (s + ky * s) * sc
        P = _obl(ox, oy, sc, kx, ky)
        # 見えない辺（点線）
        setline(c, .7, MUTED, (3, 2))
        for p1, p2 in (((0, 0, 0), (0, s, 0)), ((0, s, 0), (s, s, 0)), ((0, s, 0), (0, s, s))):
            c.line(*P(*p1), *P(*p2))
        # 穴の下の円（見えないので点線）と、横の線
        cx, cy, r = s / 2, s / 2, d / 2
        bot = _ell(P, cx, cy, r, 0)
        c.setDash(3, 2)
        c.drawPath(_path(c, bot), stroke=1, fill=0)
        xs = [q[0] for q in bot]
        lo, hi = min(bot, key=lambda q: q[0]), max(bot, key=lambda q: q[0])
        topl = _ell(P, cx, cy, r, s)
        tl, tr = min(topl, key=lambda q: q[0]), max(topl, key=lambda q: q[0])
        c.line(*tl, *lo)
        c.line(*tr, *hi)
        c.setDash()
        # 見える面
        faces = [
            ([(0, 0, 0), (s, 0, 0), (s, 0, s), (0, 0, s)], colors.white),
            ([(s, 0, 0), (s, s, 0), (s, s, s), (s, 0, s)], SHADE),
            ([(0, 0, s), (s, 0, s), (s, s, s), (0, s, s)], colors.white),
        ]
        setline(c, 1.1, INK)
        for pts, col in faces:
            c.setFillColor(col)
            c.drawPath(_poly(c, [P(*q) for q in pts]), stroke=1, fill=1)
        c.setFillColor(PALE)                                   # 穴
        setline(c, 1.1, INK)
        c.drawPath(_path(c, topl), stroke=1, fill=1)
        # 直径
        setline(c, .7, INK, (2.5, 2))
        c.line(*P(cx - r, cy, s), *P(cx + r, cy, s))
        c.setDash()
        text(c, P(cx, cy, s)[0], P(cx, cy, s)[1] + 3, f'{fmt(d)}cm', 8.5, center=True)
        # 長さ
        text(c, P(s / 2, 0, 0)[0], P(0, 0, 0)[1] - 12, f'{fmt(s)}cm', 9, center=True)
        text(c, P(s, s / 2, 0)[0] + 5, P(s, s / 2, 0)[1] - 8, f'{fmt(s)}cm', 9)
        text(c, P(0, 0, s / 2)[0] - 15, P(0, 0, s / 2)[1] - 3, f'{fmt(s)}cm', 9, center=True)

    def _solid_steps(c, px, pw, top, h, a):
        """階段の形の立体。steps=[(はば, 高さ), ...]（左から右へ、高さは、左がいちばん高い）, depth=おくゆき"""
        steps, dep = a['steps'], a['depth']
        W = sum(wd for wd, _ in steps)
        H = steps[0][1]
        kx, ky = .42, .3
        sc = min((pw - 70) / (W + kx * dep), (h - 56) / (H + ky * dep))
        ox = px + 40 + (pw - 70 - (W + kx * dep) * sc) / 2
        oy = top - 22 - (H + ky * dep) * sc
        P = _obl(ox, oy, sc, kx, ky)
        xs = [0]
        for wd, _ in steps:
            xs.append(xs[-1] + wd)
        prof = [(0, 0)]                                         # 正面の形（左下から、右まわり）
        prof.append((W, 0))
        for k in range(len(steps) - 1, -1, -1):
            prof.append((xs[k + 1], steps[k][1]))
            prof.append((xs[k], steps[k][1]))
        # prof: (0,0),(W,0),(W,h_last),(x_last,h_last),(x_last,h_{last-1}),... ,(0,h_0)
        setline(c, 1.1, INK)
        # 右の側面（見える面）
        c.setFillColor(SHADE)
        c.drawPath(_poly(c, [P(W, 0, 0), P(W, dep, 0), P(W, dep, steps[-1][1]), P(W, 0, steps[-1][1])]), stroke=1, fill=1)
        # 上の面と、右がわの段差の面
        for k, (wd, hh) in enumerate(steps):
            c.setFillColor(colors.white)
            c.drawPath(_poly(c, [P(xs[k], 0, hh), P(xs[k + 1], 0, hh), P(xs[k + 1], dep, hh), P(xs[k], dep, hh)]), stroke=1, fill=1)
            if k + 1 < len(steps):                             # 右に向いた段差の面
                h2 = steps[k + 1][1]
                c.setFillColor(SHADE)
                c.drawPath(_poly(c, [P(xs[k + 1], 0, h2), P(xs[k + 1], dep, h2), P(xs[k + 1], dep, hh), P(xs[k + 1], 0, hh)]), stroke=1, fill=1)
        # 正面
        c.setFillColor(colors.white)
        c.drawPath(_poly(c, [P(q[0], 0, q[1]) for q in prof]), stroke=1, fill=1)
        # 長さ
        for k, (wd, hh) in enumerate(steps):
            mx = (xs[k] + xs[k + 1]) / 2
            text(c, P(mx, 0, 0)[0], P(0, 0, 0)[1] - 12, f'{fmt(wd)}cm', 9, center=True)
        text(c, P(0, 0, H / 2)[0] - 16, P(0, 0, H / 2)[1] - 3, f'{fmt(H)}cm', 9, center=True)
        for k in range(len(steps) - 1):                         # 段差の高さ
            drop = steps[k][1] - steps[k + 1][1]
            zx, zz = xs[k + 1], steps[k + 1][1] + drop / 2
            text(c, P(zx, 0, zz)[0] - 14, P(zx, 0, zz)[1] - 3, f'{fmt(drop)}cm', 9, center=True)
        hl = steps[-1][1]
        text(c, P(W, 0, hl / 2)[0] - 14, P(W, 0, hl / 2)[1] - 3, f'{fmt(hl)}cm', 9, center=True)
        text(c, P(W, dep / 2, 0)[0] + 5, P(W, dep / 2, 0)[1] - 8, f'{fmt(dep)}cm', 9)

    SOLIDS = {'cubehole': _solid_cubehole, 'steps': _solid_steps}

    def fig_solids(c, x, top, w, h, panels=()):
        """panels=[dict(kind='cubehole'|'steps', wt=1, **数値), ...]。(1)(2)…と、横にならべる。"""
        tot = sum(p.get('wt', 1) for p in panels)
        cum = 0
        for k, pn in enumerate(panels):
            pw = w * pn.get('wt', 1) / tot
            px = x + w * cum / tot
            cum += pn.get('wt', 1)
            text(c, px + 4, top - 11, f'({k + 1})', 10, bold=True)
            SOLIDS[pn['kind']](c, px, pw, top, h, pn)

    # ---------- 数を段にならべた表 ----------
    def fig_rows(c, x, top, w, h, rows=(), cw=34, rh=19):
        """rows は、各段の数のリスト。1段目・2段目…と、左そろえで書く。さいごに「・・・」の行をつける。"""
        lab_w = 46
        total_w = lab_w + max(len(r) for r in rows) * cw
        x0 = x + (w - total_w) / 2
        y = top - 6
        for n, r in enumerate(rows, 1):
            yb = y - rh
            text(c, x0 + 2, yb + 5.5, f'{n}段目', 9.5, bold=True)
            for k, v in enumerate(r):
                setline(c, .6, MUTED)
                c.setFillColor(colors.white)
                c.rect(x0 + lab_w + k * cw, yb, cw, rh, stroke=1, fill=1)
                text(c, x0 + lab_w + k * cw + cw / 2, yb + 5.5, str(v), 9.5, center=True)
            y = yb
        for k in range(3):
            text(c, x0 + lab_w + cw / 2, y - 8 - k * 5.5, '・', 9, center=True)

    # ---------- 白石と黒石 ----------
    def fig_stones(c, x, top, w, h, pattern='○●○○●●○○●', reps=3, per_row=None):
        """pattern（○＝白、●＝黒）を reps 回くり返して、石をならべ、さいごに「……」をつける。"""
        seq = pattern * reps
        n = len(seq)
        per = per_row or n
        rows = math.ceil(n / per)
        step = min(19.0, (w - 50) / per)
        r = step * .39
        x0 = x + (w - (per * step + 26)) / 2
        for i, ch in enumerate(seq):
            rr, cc = divmod(i, per)
            cx, cy = x0 + step * (cc + .5), top - 22 - rr * (step + 8)
            setline(c, 1.1, INK)
            c.setFillColor(INK if ch == '●' else colors.white)
            c.circle(cx, cy, r, stroke=1, fill=1)
        lastr = rows - 1
        text(c, x0 + step * ((n - 1) % per + 1) + 3, top - 22 - lastr * (step + 8) - 3, '……', 11, bold=True)

    # ---------- 格子状の道 ----------
    def fig_roads(c, x, top, w, h, nx=5, ny=3, labels=(), blocked=(), cap=''):
        """nx×ny の格子の道。labels=[(i, j, '名前'), ...]、blocked=[((i1, j1), (i2, j2)), ...] は、通れない道（×）。"""
        gw, gh = min(w - 120, 40 * nx), min(h - 52, 34 * ny)
        dx, dy = gw / nx, gh / ny
        ox, oy = x + (w - gw) / 2, top - h + 24
        P = lambda i, j: (ox + i * dx, oy + j * dy)
        bl = {frozenset(b) for b in blocked}
        setline(c, 1.8, INK)
        for j in range(ny + 1):
            for i in range(nx):
                if frozenset(((i, j), (i + 1, j))) not in bl:
                    c.line(*P(i, j), *P(i + 1, j))
        for i in range(nx + 1):
            for j in range(ny):
                if frozenset(((i, j), (i, j + 1))) not in bl:
                    c.line(*P(i, j), *P(i, j + 1))
        for (a, b) in blocked:                                  # 通れない道：うすい点線と、×
            (x1, y1), (x2, y2) = P(*a), P(*b)
            setline(c, .7, MUTED, (2, 2))
            c.line(x1, y1, x2, y2)
            c.setDash()
            mx, my = (x1 + x2) / 2, (y1 + y2) / 2
            setline(c, 1.8, INK)
            c.line(mx - 5, my - 5, mx + 5, my + 5)
            c.line(mx - 5, my + 5, mx + 5, my - 5)
        for (i, j, nm) in labels:
            px_, py_ = P(i, j)
            c.setFillColor(colors.white)
            setline(c, .9, INK)
            c.circle(px_, py_, 8, stroke=1, fill=1)
            text(c, px_, py_ - 3.3, nm, 9.5, bold=True, center=True)
        if cap:
            text(c, x + 4, top - 11, cap, 10, bold=True)

    B.FIGS['s9_graph'] = fig_graph
    B.FIGS['s9_solids'] = fig_solids
    B.FIGS['s9_rows'] = fig_rows
    B.FIGS['s9_stones'] = fig_stones
    B.FIGS['s9_roads'] = fig_roads
