"""算数・大問5 専用の図（図の名前は s5_ で始める）。tools/build_tenri_rs.py が、起動時に register(B) を呼ぶ。

s5_plane  : 平面の図を、パネル（(1)(2)…）にならべる。座標はすべて cm（x=右, y=上）。パネルの大きさに合わせて、縦横の比を変えずに拡大・縮小する。
            fig=dict(name='s5_plane', h=140, args=dict(panels=[dict(cap='(1)', wt=1, sub='…', prims=[...]), ...]))
            パネルの書き方：cap=見出し、wt=横幅の重み、rect=(x0, y0, x1, y1)（図全体に対する割合。y は上から）で置き場所を決めてもよい、
            sub=図の下の説明、padx・pady=まわりの余白(pt)、maxsc=1cmあたりの最大の長さ(pt)。
            部品（prims）。opts は最後に dict で。
              ('poly',   [(x, y), ...], opts)          多角形。opts: fill='hatch'|'white'|'gray'|'black', w, dash=(3, 2), nostroke=True
              ('circle', (cx, cy), r, opts)            円
              ('sector', (cx, cy), r, a0, a1, opts)    おうぎ形（a0→a1度、左まわり）。a1-a0=180なら半円
              ('and',    [形1, 形2], opts)             2つの形（poly・circle・sector）の重なり。opts: fill='hatch'
              ('seg',    p, q, opts)                   線分。opts: w, dash
              ('arc',    (cx, cy), r, a0, a1, opts)    円弧（線だけ）
              ('dim',    p, q, 'ラベル', opts)         寸法の線とラベル。opts: side=1|-1（p→q の左がわが1）, off=線のはなれ(pt), size
              ('lbl',    (x, y), 'ラベル', opts)       文字。opts: dx, dy(pt), size, anchor='c'|'l'|'r', bold, bg=True（白い下地）
              ('pt',     (x, y), 'A', opts)            点の名前（太字）。opts: dx, dy(pt), dot=True
              ('dot',    (x, y), opts)                 小さな点
              ('rt',     (vx, vy), (dx1, dy1), (dx2, dy2))   直角の印
              ('ang',    (vx, vy), a0, a1, 'ラベル', opts)   角の印（小さな円弧とラベル）。opts: r(pt), dx, dy
              ('grid',   (x0, y0), (x1, y1), step, opts)     方眼。opts: dots=True（格子点だけ）
              ('arrow',  p, q, opts)                   矢印（直線）
              ('carrow', (cx, cy), r, a0, a1, opts)    弧の矢印（a1がわに矢じり）
            検算（tools/check_sansu5.py）は、この座標から、斜線部分の面積などを、公式とは別に数え上げて確かめる。
s5_solids : 立体の見取図を、(1)(2)(3)とならべる（同じ縮尺）。args=dict(solids=[dict(kind='prism'|'pipe', ...), ...])
            prism : 正面の多角形 pts（(x, z)、左まわり）を、おくゆき d にのばした柱。dims=[(点1, 点2, 'ラベル', dx, dy), ...]（点は (x, y, z)）、
                    dash=[((x, z), (x, z)), ...]（正面の面にかく点線）。
            pipe  : 円柱（半径 R、高さ h）から、同じ軸の円柱（半径 r）をくりぬいた立体。
            cap   : 図の下の説明（文字列のリスト）。
"""
from __future__ import annotations

import math


def register(B):
    colors, text, setline, _hatch, _poly, tw = B.colors, B.text, B.setline, B._hatch, B._poly, B.tw
    INK, MUTED, LINE, PALE = B.INK, B.MUTED, B.LINE, B.PALE
    LIGHT = colors.HexColor('#DCE2E6')
    FILLS = {'white': colors.white, 'gray': colors.HexColor('#C2C9CE'), 'black': INK}

    # ---------- 平面の図 ----------
    def hatch(c, clip, box, gap=5.6):
        """clip の内がわに、右上がりの斜線を引く。線の位置はページ全体でそろえる（形をならべても、斜線がつながる）。"""
        x0, y0, x1, y1 = box
        c.saveState()
        c.clipPath(clip, stroke=0, fill=0)
        setline(c, .45, MUTED)
        m = math.floor((x0 - y1) / gap)
        while m * gap <= x1 - y0:
            k = m * gap
            c.line(x0, x0 - k, x1, x1 - k)
            m += 1
        c.restoreState()

    def arc_points(cx, cy, r, a0, a1):
        lo, hi = min(a0, a1), max(a0, a1)
        angs = [lo, hi] + [t for t in range(-720, 721, 90) if lo < t < hi]
        return [(cx + r * math.cos(math.radians(a)), cy + r * math.sin(math.radians(a))) for a in angs]

    def bbox(prims):
        pts = []
        for pr in prims:
            k = pr[0]
            if k == 'poly':
                pts += list(pr[1])
            elif k == 'circle':
                (cx, cy), r = pr[1], pr[2]
                pts += [(cx - r, cy - r), (cx + r, cy + r)]
            elif k == 'sector':
                pts += arc_points(pr[1][0], pr[1][1], pr[2], pr[3], pr[4]) + [pr[1]]
            elif k in ('arc', 'carrow'):
                pts += arc_points(pr[1][0], pr[1][1], pr[2], pr[3], pr[4])
            elif k in ('seg', 'arrow', 'dim'):
                pts += [pr[1], pr[2]]
            elif k == 'and':
                b = bbox(pr[1])
                pts += [(b[0], b[1]), (b[2], b[3])]
            elif k in ('pt', 'lbl', 'dot', 'rt', 'ang'):
                pts.append(pr[1])
            elif k == 'grid':
                pts += [pr[1], pr[2]]
        xs, ys = [p[0] for p in pts], [p[1] for p in pts]
        return min(xs), min(ys), max(xs), max(ys)

    def ahead(c, tip, ux, uy, size=4.2):
        """tip に、向き (ux, uy) の小さな矢じりをかく。"""
        p = c.beginPath()
        p.moveTo(*tip)
        for s in (1, -1):
            a = math.atan2(uy, ux) + math.pi + s * .38
            p.lineTo(tip[0] + size * 1.9 * math.cos(a), tip[1] + size * 1.9 * math.sin(a))
        p.close()
        c.setFillColor(INK)
        c.drawPath(p, stroke=0, fill=1)

    def dimline(c, a, b, label, side=1, off=11, size=9):
        dx, dy = b[0] - a[0], b[1] - a[1]
        L = math.hypot(dx, dy)
        if L < 1e-6:
            return
        ux, uy = dx / L, dy / L
        nx, ny = -uy * side, ux * side
        a2, b2 = (a[0] + nx * off, a[1] + ny * off), (b[0] + nx * off, b[1] + ny * off)
        ww = tw(label, size)
        setline(c, .4, MUTED)
        c.line(a[0] + nx * 2, a[1] + ny * 2, a2[0] + nx * 3, a2[1] + ny * 3)
        c.line(b[0] + nx * 2, b[1] + ny * 2, b2[0] + nx * 3, b2[1] + ny * 3)
        mid = ((a2[0] + b2[0]) / 2, (a2[1] + b2[1]) / 2)
        if L > ww + 18:
            setline(c, .7, INK)
            c.line(*a2, *b2)
            ahead(c, a2, -ux, -uy)
            ahead(c, b2, ux, uy)
            c.setFillColor(colors.white)
            c.rect(mid[0] - ww / 2 - 2, mid[1] - size * .55, ww + 4, size * 1.1, stroke=0, fill=1)
            text(c, mid[0], mid[1] - size * .32, label, size, center=True)
        else:                                                        # 短い辺：線は引かず、外がわに文字だけ
            setline(c, .7, INK)
            c.line(*a2, *b2)
            ex = nx * (size * .75 + 2)
            ey = ny * (size * .75 + 2)
            text(c, mid[0] + ex, mid[1] + ey - size * .32, label, size, center=True)

    def fig_plane(c, x, top, w, h, panels=()):
        if any('rect' in p for p in panels):
            boxes = [(x + w * p['rect'][0], top - h * p['rect'][1], w * (p['rect'][2] - p['rect'][0]), h * (p['rect'][3] - p['rect'][1])) for p in panels]
        else:
            tws = sum(p.get('wt', 1) for p in panels)
            cum, boxes = 0, []
            for p in panels:
                boxes.append((x + w * cum / tws, top, w * p.get('wt', 1) / tws, h))
                cum += p.get('wt', 1)
        for pn, (bx, btop, bw, bh) in zip(panels, boxes):
            capoff = 22 if pn.get('cap') else 4
            suboff = 13 if pn.get('sub') else 0
            if pn.get('cap'):
                text(c, bx + 4, btop - 11, pn['cap'], 10, bold=True)
            if pn.get('sub'):
                text(c, bx + bw / 2, btop - bh + 3, pn['sub'], 8.5, center=True)
            gtop, gh = btop - capoff, bh - capoff - suboff - 2
            prims = pn['prims']
            x0, y0, x1, y1 = bbox(prims)
            padx, pady = pn.get('padx', 20), pn.get('pady', 16)
            W_, H_ = max(x1 - x0, 1e-6), max(y1 - y0, 1e-6)
            sc = min((bw - 2 * padx) / W_, (gh - 2 * pady) / H_, pn.get('maxsc', 1e9))
            ox = bx + (bw - W_ * sc) / 2 - x0 * sc
            oy = gtop - gh + suboff + (gh - H_ * sc) / 2 - y0 * sc
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
                    r, a0, a1 = sh[2] * sc, sh[3], sh[4]
                    p.moveTo(cx, cy)
                    p.lineTo(cx + r * math.cos(math.radians(a0)), cy + r * math.sin(math.radians(a0)))
                    p.arcTo(cx - r, cy - r, cx + r, cy + r, a0, a1 - a0)
                    p.close()
                return p

            def box_of(sh):
                b = bbox([sh])
                (u0, v0), (u1, v1) = T((b[0], b[1])), T((b[2], b[3]))
                return u0, v0, u1, v1

            for pr in prims:
                k = pr[0]
                o = pr[-1] if isinstance(pr[-1], dict) else {}
                col = o.get('color', INK)
                if k in ('poly', 'circle', 'sector'):
                    path = path_of(pr)
                    fill = o.get('fill')
                    if fill == 'hatch':
                        hatch(c, path, box_of(pr), o.get('gap', 5.6))
                    elif fill in FILLS:
                        c.setFillColor(FILLS[fill])
                        c.drawPath(path, stroke=0, fill=1)
                    if not o.get('nostroke'):
                        setline(c, o.get('w', 1.1), col, o.get('dash'))
                        c.drawPath(path, stroke=1, fill=0)
                elif k == 'and':
                    a, b = pr[1]
                    c.saveState()
                    c.clipPath(path_of(a), stroke=0, fill=0)
                    hatch(c, path_of(b), box_of(b), o.get('gap', 5.6))
                    c.restoreState()
                    if o.get('outline'):
                        setline(c, o.get('w', .8), col)
                        c.saveState()
                        c.clipPath(path_of(a), stroke=0, fill=0)
                        c.drawPath(path_of(b), stroke=1, fill=0)
                        c.restoreState()
                elif k == 'seg':
                    setline(c, o.get('w', 1.1), col, o.get('dash'))
                    c.line(*T(pr[1]), *T(pr[2]))
                elif k == 'arc':
                    cx, cy = T(pr[1])
                    r = pr[2] * sc
                    setline(c, o.get('w', 1.1), col, o.get('dash'))
                    c.arc(cx - r, cy - r, cx + r, cy + r, pr[3], pr[4] - pr[3])
                elif k == 'arrow':
                    B.arrow(c, *T(pr[1]), *T(pr[2]), o.get('head', 6), o.get('w', 1), col)
                elif k == 'carrow':
                    cx, cy = T(pr[1])
                    r, a0, a1 = pr[2] * sc, pr[3], pr[4]
                    setline(c, o.get('w', 1), col)
                    c.arc(cx - r, cy - r, cx + r, cy + r, a0, a1 - a0)
                    sgn = 1 if a1 > a0 else -1
                    ex, ey = cx + r * math.cos(math.radians(a1)), cy + r * math.sin(math.radians(a1))
                    ta = math.radians(a1) + sgn * math.pi / 2
                    ahead(c, (ex, ey), math.cos(ta), math.sin(ta), 3.6)
                elif k == 'dim':
                    dimline(c, T(pr[1]), T(pr[2]), pr[3], o.get('side', 1), o.get('off', 11), o.get('size', 9))
                elif k == 'lbl':
                    tx, ty = T(pr[1])
                    size = o.get('size', 9)
                    ww = tw(pr[2], size, o.get('bold', False))
                    an = o.get('anchor', 'c')
                    xx = tx + o.get('dx', 0) - (ww / 2 if an == 'c' else ww if an == 'r' else 0)
                    if o.get('bg'):
                        c.setFillColor(colors.white)
                        c.rect(xx - 1.5, ty + o.get('dy', 0) - size * .55, ww + 3, size * 1.1, stroke=0, fill=1)
                    text(c, xx, ty + o.get('dy', 0) - size * .3, pr[2], size, o.get('bold', False))
                elif k == 'pt':
                    tx, ty = T(pr[1])
                    if o.get('dot'):
                        c.setFillColor(INK)
                        c.circle(tx, ty, 1.8, stroke=0, fill=1)
                    text(c, tx + o.get('dx', 6) - tw(pr[2], 9.5, True) / 2, ty + o.get('dy', 6) - 3, pr[2], 9.5, True)
                elif k == 'dot':
                    tx, ty = T(pr[1])
                    c.setFillColor(INK)
                    c.circle(tx, ty, o.get('r', 1.7), stroke=0, fill=1)
                elif k == 'rt':
                    vx, vy = T(pr[1])
                    d1, d2 = pr[2], pr[3]
                    n1, n2 = math.hypot(*d1), math.hypot(*d2)
                    u1, u2 = (d1[0] / n1 * 6, d1[1] / n1 * 6), (d2[0] / n2 * 6, d2[1] / n2 * 6)
                    setline(c, .8)
                    c.lines([(vx + u1[0], vy + u1[1], vx + u1[0] + u2[0], vy + u1[1] + u2[1]),
                             (vx + u2[0], vy + u2[1], vx + u1[0] + u2[0], vy + u1[1] + u2[1])])
                elif k == 'ang':
                    vx, vy = T(pr[1])
                    a0, a1, lab = pr[2], pr[3], pr[4]
                    r = o.get('r', 13)
                    setline(c, .8)
                    c.arc(vx - r, vy - r, vx + r, vy + r, a0, a1 - a0)
                    am = math.radians((a0 + a1) / 2)
                    text(c, vx + (r + 8) * math.cos(am) + o.get('dx', 0), vy + (r + 8) * math.sin(am) + o.get('dy', 0) - 3, lab, 8.5, center=True)
                elif k == 'grid':
                    (gx0, gy0), (gx1, gy1), st = pr[1], pr[2], pr[3]
                    nx_, ny_ = int(round((gx1 - gx0) / st)), int(round((gy1 - gy0) / st))
                    if o.get('dots'):
                        c.setFillColor(INK)
                        for i in range(nx_ + 1):
                            for j in range(ny_ + 1):
                                u, v = T((gx0 + i * st, gy0 + j * st))
                                c.circle(u, v, 1.1, stroke=0, fill=1)
                    else:
                        setline(c, .4, LINE)
                        for i in range(nx_ + 1):
                            c.line(*T((gx0 + i * st, gy0)), *T((gx0 + i * st, gy1)))
                        for j in range(ny_ + 1):
                            c.line(*T((gx0, gy0 + j * st)), *T((gx1, gy0 + j * st)))
            setline(c, .8)

    # ---------- 立体の見取図 ----------
    KX, KY = .42, .3

    def extents(s):
        """(横の長さcm, たての長さcm, 上に足す余白pt)"""
        if s['kind'] == 'prism':
            xs, zs = [p[0] for p in s['pts']], [p[1] for p in s['pts']]
            return max(xs) + KX * s['d'], max(zs) + KY * s['d'], 12
        return 2 * s['R'], s['h'] + 2 * .32 * s['R'], 26

    def draw_prism(c, ox, oy, sc, s):
        P = lambda x, y, z: (ox + (x + KX * y) * sc, oy + (z + KY * y) * sc)
        pts, d = list(s['pts']), s['d']
        area2 = sum(pts[i][0] * pts[(i + 1) % len(pts)][1] - pts[(i + 1) % len(pts)][0] * pts[i][1] for i in range(len(pts)))
        if area2 < 0:
            pts.reverse()
        n = len(pts)
        setline(c, 1.1)
        for i in range(n):                                          # 見える側面（上・右がわ）
            (x1, z1), (x2, z2) = pts[i], pts[(i + 1) % n]
            nrm = (z2 - z1, -(x2 - x1))                           # 外むきの法線
            if nrm[0] * KX + nrm[1] * KY > 1e-9:
                face = [P(x1, 0, z1), P(x2, 0, z2), P(x2, d, z2), P(x1, d, z1)]
                c.setFillColor(LIGHT if abs(nrm[0]) > abs(nrm[1]) * .5 and nrm[0] > 0 else PALE)
                c.drawPath(_poly(c, face), stroke=1, fill=1)
        c.setFillColor(colors.white)
        c.drawPath(_poly(c, [P(x, 0, z) for x, z in pts]), stroke=1, fill=1)
        for (p1, p2) in s.get('dash', []):
            setline(c, .8, INK, (3, 2))
            c.line(*P(p1[0], 0, p1[1]), *P(p2[0], 0, p2[1]))
        setline(c, .8)
        for (q1, q2, lab, dx, dy) in s.get('dims', []):
            a, b = P(*q1), P(*q2)
            text(c, (a[0] + b[0]) / 2 + dx, (a[1] + b[1]) / 2 + dy - 3, lab, 9, center=True)

    def draw_pipe(c, cx, ybot, sc, s):
        R, r, hh = s['R'], s['r'], s['h']
        rx, ry = R * sc, R * sc * .32
        irx, iry = r * sc, r * sc * .32
        ytop = ybot + hh * sc
        setline(c, 1.1)
        c.setFillColor(colors.white)
        c.ellipse(cx - rx, ybot - ry, cx + rx, ybot + ry, stroke=1, fill=1)
        c.rect(cx - rx, ybot, 2 * rx, ytop - ybot, stroke=0, fill=1)
        c.line(cx - rx, ybot, cx - rx, ytop)
        c.line(cx + rx, ybot, cx + rx, ytop)
        c.setFillColor(PALE)
        c.ellipse(cx - rx, ytop - ry, cx + rx, ytop + ry, stroke=1, fill=1)
        c.setFillColor(colors.white)
        c.ellipse(cx - irx, ytop - iry, cx + irx, ytop + iry, stroke=1, fill=1)
        setline(c, .8, INK, (2.5, 2))                              # 見えない、穴のかべ
        c.line(cx - irx, ytop, cx - irx, ybot)
        c.line(cx + irx, ytop, cx + irx, ybot)
        c.arc(cx - irx, ybot - iry, cx + irx, ybot + iry, 180, 180)
        setline(c, .7, INK, (2, 2))
        c.line(cx - irx, ytop, cx + irx, ytop)
        c.setDash()
        c.setFillColor(colors.white)
        iw = tw(s['dlabel'], 8.5)
        c.rect(cx - iw / 2 - 1, ytop - 5, iw + 2, 10, stroke=0, fill=1)
        text(c, cx, ytop - 3, s['dlabel'], 8.5, center=True)
        dimline(c, (cx - rx, ytop + ry), (cx + rx, ytop + ry), s['Dlabel'], 1, 9, 9)
        dimline(c, (cx + rx, ybot), (cx + rx, ytop), s['hlabel'], -1, 10, 9)

    def fig_solids(c, x, top, w, h, solids=()):
        n = len(solids)
        cw = w / n
        capn = max(len(s.get('cap', [])) for s in solids)
        base = top - h + 12 * capn + 4 + 16                       # 立体の底（正面の、下の辺）の高さ
        avail = (top - 24) - base
        sc = 1e9
        for s in solids:
            ew, eh, tp = extents(s)
            sc = min(sc, (cw - 44) / ew, (avail - tp) / eh)
        for k, s in enumerate(solids):
            px = x + k * cw
            text(c, px + 4, top - 11, f'({k + 1})', 10, bold=True)
            ew, eh, tp = extents(s)
            if s['kind'] == 'prism':
                draw_prism(c, px + (cw - ew * sc) / 2, base, sc, s)
            else:
                draw_pipe(c, px + cw / 2 - 8, base + .32 * s['R'] * sc, sc, s)
            for j, ln in enumerate(s.get('cap', [])):
                text(c, px + cw / 2, top - h + 6 + 12 * (len(s['cap']) - 1 - j), ln, 8.5, center=True)

    B.FIGS['s5_plane'] = fig_plane
    B.FIGS['s5_solids'] = fig_solids
