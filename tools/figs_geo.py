"""算数の、汎用の図形図（fig 名 'geo'）。データの中に、図形の部品（prims）を、センチメートル単位の座標で書く。

使い方（セットの fig に書く）:
    fig=dict(name='geo', h=130, args=dict(panels=[
        dict(cap='(1)', wt=1, prims=[('poly', [(0, 0), (10, 0), (10, 6), (4, 6)], dict(fill='hatch')), ('text', (5, -1.2), '10cm', {})]),
        dict(cap='(2)', prims=[...]),
    ]))

部品（prims）：
    ('poly',   [(x, y), ...], opts)                 多角形（閉じる）。opts: fill='hatch'|'black'|'gray'|'white', w=線の太さ, dash=(3, 2), open=True（閉じない）
    ('line',   (x1, y1), (x2, y2), opts)            線分
    ('circle', (cx, cy), r, opts)                   円
    ('sector', (cx, cy), r, a0, a1, opts)           おうぎ形（a0〜a1度、左まわり）
    ('arc',    (cx, cy), r, a0, a1, opts)           円弧
    ('and',    [形1, 形2], opts)                    2つの形の、重なった部分（fill='hatch' など）。形は ('poly'|'circle'|'sector', ...) の組
    ('text',   (x, y), 'ラベル', opts)              文字。opts: size, anchor='c'|'l'|'r', dx, dy（pt）, bold
    ('pt',     (x, y), 'A', opts)                   点と記号。opts: dx, dy（pt）, dot=True
    ('rt',     (vx, vy), (dx1, dy1), (dx2, dy2))    直角の印（頂点と、2辺の向き）
    ('angle',  (vx, vy), a0, a1, 'ラベル', opts)    角の印（小さな円弧と、ラベル）。opts: r（pt）, dx, dy
    ('grid',   (x0, y0), (x1, y1), step, opts)      方眼。opts: dots=True（格子点だけ）
大きさは、パネルの大きさに合わせて、縦横の比を変えずに、自動で拡大・縮小する。
"""
from __future__ import annotations

import math


def register(B):
    colors, text, setline, _hatch, _poly = B.colors, B.text, B.setline, B._hatch, B._poly
    INK, MUTED, LINE = B.INK, B.MUTED, B.LINE

    def bbox(prims):
        xs, ys = [], []

        def circ(cx, cy, r):
            xs.extend([cx - r, cx + r])
            ys.extend([cy - r, cy + r])
        for pr in prims:
            k = pr[0]
            if k == 'poly':
                xs += [p[0] for p in pr[1]]
                ys += [p[1] for p in pr[1]]
            elif k == 'line':
                xs += [pr[1][0], pr[2][0]]
                ys += [pr[1][1], pr[2][1]]
            elif k == 'circle':
                circ(pr[1][0], pr[1][1], pr[2])
            elif k in ('sector', 'arc'):
                cx, cy, r, a0, a1 = pr[1][0], pr[1][1], pr[2], pr[3], pr[4]
                xs.append(cx)
                ys.append(cy)
                for a in [a0, a1] + [t for t in range(0, 360, 90) if a0 < t < a1 or a0 < t + 360 < a1]:
                    xs.append(cx + r * math.cos(math.radians(a)))
                    ys.append(cy + r * math.sin(math.radians(a)))
            elif k == 'and':
                bb = bbox([sh for sh in pr[1]])
                xs += [bb[0], bb[2]]
                ys += [bb[1], bb[3]]
            elif k in ('text', 'pt'):
                xs.append(pr[1][0])
                ys.append(pr[1][1])
            elif k == 'grid':
                xs += [pr[1][0], pr[2][0]]
                ys += [pr[1][1], pr[2][1]]
            elif k == 'rt' or k == 'angle':
                xs.append(pr[1][0])
                ys.append(pr[1][1])
        return min(xs), min(ys), max(xs), max(ys)

    def fig_geo(c, x, top, w, h, panels=()):
        tw_ = sum(p.get('wt', 1) for p in panels)
        cum = 0
        for k, pn in enumerate(panels):
            pw = w * pn.get('wt', 1) / tw_
            px = x + w * cum / tw_
            cum += pn.get('wt', 1)
            if pn.get('cap'):
                text(c, px + 4, top - 11, pn['cap'], 10, bold=True)
            prims = pn['prims']
            x0, y0, x1, y1 = bbox(prims)
            padx, pady = pn.get('padx', 22), pn.get('pady', 20)
            ph = h - (24 if pn.get('cap') else 6)
            W, H = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
            sc = min((pw - 2 * padx) / W, (ph - 2 * pady) / H)
            sc = min(sc, pn.get('maxsc', 1e9))
            ox = px + (pw - W * sc) / 2 - x0 * sc
            oy = top - (24 if pn.get('cap') else 6) - ph + (ph - H * sc) / 2 - y0 * sc
            T = lambda p: (ox + p[0] * sc, oy + p[1] * sc)

            def path_of(sh):
                p = c.beginPath()
                if sh[0] == 'poly':
                    pts = [T(q) for q in sh[1]]
                    p.moveTo(*pts[0])
                    for q in pts[1:]:
                        p.lineTo(*q)
                    p.close()
                elif sh[0] == 'circle':
                    cx, cy = T(sh[1])
                    p.circle(cx, cy, sh[2] * sc)
                elif sh[0] == 'sector':
                    cx, cy = T(sh[1])
                    r = sh[2] * sc
                    a0, a1 = sh[3], sh[4]
                    p.moveTo(cx, cy)
                    p.lineTo(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
                    p.arcTo(cx - r, cy - r, cx + r, cy + r, a0, a1 - a0)
                    p.close()
                return p

            def box_of(sh):
                bb = bbox([sh])
                (a, b), (cc, d) = T((bb[0], bb[1])), T((bb[2], bb[3]))
                return a, b, cc, d

            def fill_style(path, sh, fill):
                if fill == 'hatch':
                    _hatch(c, path, *box_of(sh))
                elif fill in ('black', 'gray', 'white'):
                    c.setFillColor({'black': INK, 'gray': colors.HexColor('#C2C9CE'), 'white': colors.white}[fill])
                    c.drawPath(path, stroke=0, fill=1)

            for pr in prims:
                kind = pr[0]
                opts = pr[-1] if isinstance(pr[-1], dict) else {}
                setline(c, opts.get('w', 1.1), opts.get('color', INK), opts.get('dash'))
                if kind in ('poly', 'circle', 'sector'):
                    path = path_of(pr)
                    fill_style(path, pr, opts.get('fill'))
                    setline(c, opts.get('w', 1.1), opts.get('color', INK), opts.get('dash'))
                    if kind == 'poly' and opts.get('open'):
                        pts = [T(q) for q in pr[1]]
                        for a, b in zip(pts, pts[1:]):
                            c.line(*a, *b)
                    elif not opts.get('nostroke'):
                        c.drawPath(path, stroke=1, fill=0)
                elif kind == 'line':
                    c.line(*T(pr[1]), *T(pr[2]))
                elif kind == 'arc':
                    cx, cy = T(pr[1])
                    r = pr[2] * sc
                    c.arc(cx - r, cy - r, cx + r, cy + r, pr[3], pr[4] - pr[3])
                elif kind == 'and':
                    a, b = pr[1]
                    c.saveState()
                    c.clipPath(path_of(a), stroke=0, fill=0)
                    _hatch(c, path_of(b), *box_of(b)) if opts.get('fill', 'hatch') == 'hatch' else None
                    c.restoreState()
                elif kind == 'text':
                    tx, ty = T(pr[1])
                    s = pr[2]
                    size = opts.get('size', 9)
                    ww = B.tw(s, size, opts.get('bold', False))
                    an = opts.get('anchor', 'c')
                    xx = tx + opts.get('dx', 0) - (ww / 2 if an == 'c' else ww if an == 'r' else 0)
                    text(c, xx, ty + opts.get('dy', 0) - size * .3, s, size, opts.get('bold', False))
                elif kind == 'pt':
                    tx, ty = T(pr[1])
                    if opts.get('dot', True):
                        c.setFillColor(INK)
                        c.circle(tx, ty, 1.8, stroke=0, fill=1)
                    text(c, tx + opts.get('dx', 6) - B.tw(pr[2], 9.5, True) / 2, ty + opts.get('dy', 6) - 3, pr[2], 9.5, True)
                elif kind == 'rt':
                    vx, vy = T(pr[1])
                    d1, d2 = pr[2], pr[3]
                    n1, n2 = math.hypot(*d1), math.hypot(*d2)
                    u1, u2 = (d1[0] / n1 * 6, d1[1] / n1 * 6), (d2[0] / n2 * 6, d2[1] / n2 * 6)
                    setline(c, .8)
                    c.lines([(vx + u1[0], vy + u1[1], vx + u1[0] + u2[0], vy + u1[1] + u2[1]), (vx + u2[0], vy + u2[1], vx + u1[0] + u2[0], vy + u1[1] + u2[1])])
                elif kind == 'angle':
                    vx, vy = T(pr[1])
                    a0, a1, lab = pr[2], pr[3], pr[4]
                    r = opts.get('r', 13)
                    setline(c, .8)
                    c.arc(vx - r, vy - r, vx + r, vy + r, a0, a1 - a0)
                    am = math.radians((a0 + a1) / 2)
                    text(c, vx + (r + 8) * math.cos(am) + opts.get('dx', 0) - B.tw(lab, 8.5) / 2, vy + (r + 8) * math.sin(am) + opts.get('dy', 0) - 3, lab, 8.5)
                elif kind == 'grid':
                    (gx0, gy0), (gx1, gy1), st = pr[1], pr[2], pr[3]
                    nx, ny = int(round((gx1 - gx0) / st)), int(round((gy1 - gy0) / st))
                    if opts.get('dots'):
                        c.setFillColor(INK)
                        for i in range(nx + 1):
                            for j in range(ny + 1):
                                px_, py_ = T((gx0 + i * st, gy0 + j * st))
                                c.circle(px_, py_, 1.1, stroke=0, fill=1)
                    else:
                        setline(c, .4, LINE)
                        for i in range(nx + 1):
                            c.line(*T((gx0 + i * st, gy0)), *T((gx0 + i * st, gy1)))
                        for j in range(ny + 1):
                            c.line(*T((gx0, gy0 + j * st)), *T((gx1, gy0 + j * st)))
            setline(c, .8)

    B.FIGS['geo'] = fig_geo
