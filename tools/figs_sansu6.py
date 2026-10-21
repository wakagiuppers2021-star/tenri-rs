"""算数・大問6 専用の図（名前は s6_ で始まる）。tools/build_tenri_rs.py の _load_figs が register(B) を呼ぶ。

    s6_dgraph   速さのグラフ（時間と道のり）。軸・目盛り・点線・折れ線。第01・09セット
    s6_solids   見取図を、(ア)(イ)(ウ) とならべる。kind は SOLIDS の名前（cutbox・cutcyl・cubes・trapprism・revolve・pitbox・triprism・fnotch・cylhole）
    s6_checkers 白黒の正方形をならべた規則性の図。第03セット
    s6_cards    数字のカード。第05セット
    s6_net      直方体の展開図（点と面に記号つき）。第07セット
    s6_trees    木を同じ間かくでならべた図。第10セット
立体は、前の面を実際の形で描き、おくゆきを右上にずらす見取図（builder の _obl）。円柱は、うえから少し見おろした、ふつうの形。
長さはすべて cm。図の数値は、データ（tools/tenri_rs_sansu6.py）の args にあり、検算（tools/check_sansu6.py）でも使う。
"""
from __future__ import annotations

import math

from reportlab.pdfgen.canvas import FILL_EVEN_ODD


def register(B):
    colors, text, setline, _poly, _obl, arrow, tw = B.colors, B.text, B.setline, B._poly, B._obl, B.arrow, B.tw
    INK, MUTED, LINE, PALE, SHADE = B.INK, B.MUTED, B.LINE, B.PALE, B.SHADE
    WHITE = colors.white
    KX, KY = .42, .3                                          # おくゆき1あたりの、右・上へのずれ

    def lab(c, x, y, s, size=9, anchor='c', bold=False, halo=None):
        """(x, y) を、文字のまん中の高さにして書く。anchor: 'c'＝中央、'l'＝左はしが x、'r'＝右はしが x。halo＝文字の下にしく色（線を消す）。"""
        w = tw(s, size, bold)
        xx = x - (w / 2 if anchor == 'c' else w if anchor == 'r' else 0)
        if halo is not None:
            c.setFillColor(halo)
            c.rect(xx - 1.2, y - size * .52, w + 2.4, size * 1.04, stroke=0, fill=1)
        text(c, xx, y - size * .33, s, size, bold)

    def setl(c, w, color=INK, dash=None):
        """線の太さ・色・点線（長さの並び。3つ以上でもよい）。"""
        setline(c, w, color)
        if dash:
            c.setDash(list(dash))

    def seg(c, p, q, w=1.1, dash=None, color=INK):
        setl(c, w, color, dash)
        c.line(p[0], p[1], q[0], q[1])
        c.setDash()

    def dash_path(c, pts, w=.8, dash=(3, 2), color=INK):
        """点の列を、1本の点線でつなぐ。"""
        setl(c, w, color, dash)
        p = c.beginPath()
        p.moveTo(*pts[0])
        for q in pts[1:]:
            p.lineTo(*q)
        c.drawPath(p, stroke=1, fill=0)
        c.setDash()

    def fill_poly(c, pts, fill=WHITE, w=1.1, stroke=True):
        c.setFillColor(fill)
        setline(c, w)
        c.drawPath(_poly(c, pts), stroke=1 if stroke else 0, fill=1)

    def dim_arrow(c, p, q, s, size=8.5, dx=0, dy=7):
        """細い両はしの矢じるしと、そのうえ（dx・dy だけずらした位置）に長さ。"""
        setline(c, .7, MUTED)
        c.line(p[0], p[1], q[0], q[1])
        a = math.atan2(q[1] - p[1], q[0] - p[0])
        for (x, y), sg in ((p, 1), (q, -1)):
            h = 4.2
            pa = c.beginPath()
            pa.moveTo(x, y)
            pa.lineTo(x + sg * h * math.cos(a - .4), y + sg * h * math.sin(a - .4))
            pa.lineTo(x + sg * h * math.cos(a + .4), y + sg * h * math.sin(a + .4))
            pa.close()
            c.setFillColor(MUTED)
            c.drawPath(pa, stroke=0, fill=1)
        lab(c, (p[0] + q[0]) / 2 + dx, (p[1] + q[1]) / 2 + dy, s, size)

    def rt_mark(c, v, d1, d2, size=5):
        """直角の印。v＝頂点（紙の上の点）、d1・d2＝2辺の向き。"""
        n1, n2 = math.hypot(*d1), math.hypot(*d2)
        u1, u2 = (d1[0] / n1 * size, d1[1] / n1 * size), (d2[0] / n2 * size, d2[1] / n2 * size)
        setline(c, .7)
        c.lines([(v[0] + u1[0], v[1] + u1[1], v[0] + u1[0] + u2[0], v[1] + u1[1] + u2[1]),
                 (v[0] + u2[0], v[1] + u2[1], v[0] + u1[0] + u2[0], v[1] + u1[1] + u2[1])])

    # ------------------------------------------------------------------ 速さのグラフ
    def fig_dgraph(c, x, top, w, h, xmax=30, ymax=1500, xticks=(), yticks=(), ylabels=None, lines=(), guides=(),
                   dots=(), xlab='時間（分）', ylab='', grid=None, gw=None, notes=()):
        """時間（横）と道のり（たて）のグラフ。
        xticks・yticks＝目盛りの数字を書く値。ylabels＝{値: 文字}（数字のかわりに書く）。lines＝[{pts, dash, w}]。
        guides＝[(t, v)]：点から両方の軸へ引く点線。dots＝[(t, v)]：黒い点。grid＝(横の間かく, たての間かく)：うすい方眼。
        notes＝[(t, v, 文字, dx, dy)]：グラフの中の書きこみ。gw＝グラフの幅（pt）。"""
        gw = gw or min(w - 120, 330)
        gx0 = x + (w - gw) / 2 + 24
        gx1 = gx0 + gw - 24
        gy0, gy1 = top - h + 30, top - 22

        def X(t):
            return gx0 + (gx1 - gx0) * t / xmax

        def Y(v):
            return gy0 + (gy1 - gy0) * v / ymax
        if grid:
            setline(c, .35, LINE, (1, 2))
            for t in range(0, int(xmax) + 1, grid[0]):
                c.line(X(t), gy0, X(t), gy1)
            for v in range(0, int(ymax) + 1, grid[1]):
                c.line(gx0, Y(v), gx1, Y(v))
            c.setDash()
        for (t, v) in guides:
            seg(c, (X(t), Y(v)), (X(t), gy0), .6, (1.5, 2), MUTED)
            seg(c, (X(t), Y(v)), (gx0, Y(v)), .6, (1.5, 2), MUTED)
        arrow(c, gx0, gy0, gx1 + 14, gy0, 6, 1)
        arrow(c, gx0, gy0, gx0, gy1 + 10, 6, 1)
        for t in xticks:
            lab(c, X(t), gy0 - 10, str(t), 8.5)
        if 0 in (ylabels or {}) and 0 not in xticks:
            lab(c, gx0, gy0 - 10, '0', 8.5)
        for v in yticks:
            s = (ylabels or {}).get(v, str(v))
            lab(c, gx0 - 5, Y(v), s, 8.5, 'r')
        for v, s in (ylabels or {}).items():
            if v not in yticks:
                lab(c, gx0 - 5, Y(v), s, 8.5, 'r')
        if 0 not in (ylabels or {}):
            lab(c, gx0 - 5, gy0 - 10, '0', 8.5, 'r')
        lab(c, gx1 + 15, gy0 - 4, xlab, 8.5, 'l')
        if ylab:
            lab(c, gx0 - 5, gy1 + 17, ylab, 8.5, 'l')
        for ln in lines:
            pts = ln['pts']
            setline(c, ln.get('w', 1.8), ln.get('color', INK), ln.get('dash'))
            for (t1, v1), (t2, v2) in zip(pts, pts[1:]):
                c.line(X(t1), Y(v1), X(t2), Y(v2))
            c.setDash()
        c.setFillColor(INK)
        for (t, v) in dots:
            c.circle(X(t), Y(v), 2.2, stroke=0, fill=1)
        for (t, v, s, dx, dy) in notes:
            lab(c, X(t) + dx, Y(v) + dy, s, 8.5)

    # ------------------------------------------------------------------ 立体の部品
    def fit(px, pw, rtop, rh, bw, bh, ml=0, mr=0, mt=0, mb=0, maxsc=1e9):
        """幅 bw・高さ bh の図が、(px, pw, rtop, rh) の中に、ちょうど入る倍率と、図の左下の位置。"""
        sc = min((pw - ml - mr) / bw, (rh - mt - mb) / bh, maxsc)
        ox = px + ml + (pw - ml - mr - bw * sc) / 2
        oy = rtop - mt - (rh - mt - mb - bh * sc) / 2 - bh * sc
        return sc, ox, oy

    def sh_cutbox(c, px, pw, rtop, rh, a):
        """直方体を、ななめの平面で切った立体（たての辺の高さが4本ちがう）。h＝(前左, 前右, 後ろ右, 後ろ左)。"""
        L, W = a['L'], a['W']
        hFL, hFR, hBR, hBL = a['h']
        bw = L + KX * W
        bh = max(max(hFL, hFR), max(hBR, hBL) + KY * W, hBR + KY * W)
        sc, ox, oy = fit(px, pw, rtop, rh, bw, bh, ml=30, mr=34, mt=4, mb=22)
        P = _obl(ox, oy, sc, KX, KY)
        fill_poly(c, [P(0, 0, 0), P(L, 0, 0), P(L, 0, hFR), P(0, 0, hFL)], WHITE)
        fill_poly(c, [P(L, 0, 0), P(L, W, 0), P(L, W, hBR), P(L, 0, hFR)], SHADE)
        fill_poly(c, [P(0, 0, hFL), P(L, 0, hFR), P(L, W, hBR), P(0, W, hBL)], PALE)
        for q in ((0, 0, 0), (L, W, 0), (0, W, hBL)):             # 見えない辺（点線）
            seg(c, P(0, W, 0), P(*q), .8, (3, 2))
        lab(c, P(L / 2, 0, 0)[0], P(0, 0, 0)[1] - 11, f'{L:g}cm')
        lab(c, P(L, W / 2, 0)[0] + 5, P(L, W / 2, 0)[1] - 8, f'{W:g}cm', anchor='l')
        lab(c, P(0, 0, hFL / 2)[0] - 4, P(0, 0, hFL / 2)[1], f'{hFL:g}cm', anchor='r')
        lab(c, P(L, 0, hFR / 2)[0] - 4, P(L, 0, hFR / 2)[1], f'{hFR:g}cm', anchor='r')
        lab(c, P(L, W, hBR / 2)[0] + 4, P(L, W, hBR / 2)[1], f'{hBR:g}cm', anchor='l')

    def sh_cutcyl(c, px, pw, rtop, rh, a):
        """円柱を、底面に平行でない平面で切った立体。d＝直径、h＝(左, 右) のいちばん高い・低い所の高さ。"""
        r = a['d'] / 2
        hl, hr = a['h']
        e = .3
        zc, s = (hl + hr) / 2, (hr - hl) / (2 * r)
        topmax = zc + r * math.hypot(s, e)
        sc, ox, oy = fit(px, pw, rtop, rh, 2 * r, topmax + e * r, ml=30, mr=30, mt=2, mb=20)
        cx, y0 = ox + r * sc, oy + e * r * sc               # y0＝底面の中心

        def Pt(X, Y, Z):
            return (cx + X * sc, y0 + (Z + e * Y) * sc)
        th = [i * math.pi / 60 for i in range(121)]
        top_pts = [Pt(r * math.cos(t), r * math.sin(t), zc + s * r * math.cos(t)) for t in th[:-1]]
        body = [Pt(-r, 0, 0), Pt(r, 0, 0), Pt(r, 0, hr), Pt(-r, 0, hl)]
        c.setFillColor(WHITE)
        setline(c, 1.1)
        p = c.beginPath()                                      # 側面（下の半円ふくむ）
        p.moveTo(*Pt(-r, 0, 0))
        for t in th[60:]:
            p.lineTo(*Pt(r * math.cos(t), r * math.sin(t), 0))
        p.lineTo(*Pt(r, 0, hr))
        p.lineTo(*Pt(-r, 0, hl))
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        dash_path(c, [Pt(r * math.cos(t), r * math.sin(t), 0) for t in th[:61]])      # 底面の見えない半円（点線）
        fill_poly(c, top_pts, PALE)
        lab(c, cx, y0 - e * r * sc - 10, f'直径{a["d"]:g}cm')
        lab(c, body[0][0] - 4, y0 + hl / 2 * sc, f'{hl:g}cm', anchor='r')
        lab(c, body[1][0] + 4, y0 + hr / 2 * sc, f'{hr:g}cm', anchor='l')

    def draw_boxes(c, P, boxes):
        """直方体（x0,y0,z0,x1,y1,z1）を、前・上・右の面だけ、順にぬる。後ろにあるものを先に。"""
        for (x0, y0, z0, x1, y1, z1) in boxes:
            fill_poly(c, [P(x0, y0, z0), P(x1, y0, z0), P(x1, y0, z1), P(x0, y0, z1)], WHITE)
            fill_poly(c, [P(x0, y0, z1), P(x1, y0, z1), P(x1, y1, z1), P(x0, y1, z1)], PALE)
            fill_poly(c, [P(x1, y0, z0), P(x1, y1, z0), P(x1, y1, z1), P(x1, y0, z1)], SHADE)

    def proj_bbox(boxes):
        xs, ys = [], []
        for (x0, y0, z0, x1, y1, z1) in boxes:
            for x in (x0, x1):
                for y in (y0, y1):
                    for z in (z0, z1):
                        xs.append(x + KX * y)
                        ys.append(z + KY * y)
        return min(xs), max(xs), min(ys), max(ys)

    def sh_cubes(c, px, pw, rtop, rh, a):
        """立方体（直方体）を組み合わせた立体。boxes＝後ろ・下から順。notes＝[(3Dの点, 文字, dx, dy, anchor)]。"""
        boxes = a['boxes']
        x0_, x1_, y0_, y1_ = proj_bbox(boxes)
        sc, ox, oy = fit(px, pw, rtop, rh, x1_ - x0_, y1_ - y0_, ml=18, mr=26, mt=4, mb=20)
        P0 = _obl(ox, oy, sc, KX, KY)
        P = lambda x, y, z: (P0(x, y, z)[0] - x0_ * sc, P0(x, y, z)[1] - y0_ * sc)
        draw_boxes(c, P, boxes)
        for (pt, s, dx, dy, an) in a.get('notes', ()):
            q = P(*pt)
            lab(c, q[0] + dx, q[1] + dy, s, 8.5, an)

    def sh_trapprism(c, px, pw, rtop, rh, a):
        """前の面が台形（下底 b1・上底 b2・高さ hh）の柱。おくゆき d。"""
        b1, b2, hh, d = a['b1'], a['b2'], a['hh'], a['d']
        off = (b1 - b2) / 2
        sc, ox, oy = fit(px, pw, rtop, rh, b1 + KX * d, hh + KY * d, ml=22, mr=40, mt=6, mb=22)
        P = _obl(ox, oy, sc, KX, KY)
        fill_poly(c, [P(0, 0, 0), P(b1, 0, 0), P(b1 - off, 0, hh), P(off, 0, hh)], WHITE)
        fill_poly(c, [P(off, 0, hh), P(b1 - off, 0, hh), P(b1 - off, d, hh), P(off, d, hh)], PALE)
        fill_poly(c, [P(b1, 0, 0), P(b1, d, 0), P(b1 - off, d, hh), P(b1 - off, 0, hh)], SHADE)
        for q in ((0, 0, 0), (b1, d, 0), (off, d, hh)):
            seg(c, P(0, d, 0), P(*q), .8, (3, 2))
        seg(c, P(off, 0, hh), P(off, 0, 0), .8, (3, 2))          # 高さ
        rt_mark(c, P(off, 0, 0), (1, 0), (0, 1))
        lab(c, P(b1 / 2, 0, 0)[0], P(0, 0, 0)[1] - 11, f'{b1:g}cm')
        lab(c, P(b1 / 2, d / 2, hh)[0], P(b1 / 2, d / 2, hh)[1], f'{b2:g}cm', 8.5)                      # 上底（上の面のまん中）
        lab(c, P(off, 0, hh / 2)[0] + 3, P(off, 0, hh / 2)[1], f'{hh:g}cm', 8.5, 'l', halo=WHITE)
        lab(c, P(b1, d / 2, 0)[0] + 5, P(b1, d / 2, 0)[1] - 8, f'{d:g}cm', anchor='l')

    def sh_revolve(c, px, pw, rtop, rh, a):
        """直線ABのまわりに回す平面図形。poly＝(軸からの横, 高さ) の点の列（軸は 横＝0）。labels＝長さの書きこみ。"""
        poly = a['poly']
        wmax = max(p[0] for p in poly)
        hmax = max(p[1] for p in poly)
        sc, ox, oy = fit(px, pw, rtop, rh, wmax + 1.2, hmax + 2.6, ml=18, mr=34, mt=8, mb=24)
        P = lambda u, v: (ox + (u + .6) * sc, oy + (v + 1.1) * sc)
        c.setFillColor(PALE)
        setline(c, 1.2)
        c.drawPath(_poly(c, [P(*q) for q in poly]), stroke=1, fill=1)
        seg(c, P(0, -1.1), P(0, hmax + 1.5), 1.0, (6, 2, 1, 2))     # 軸（一点さ線）
        lab(c, P(0, hmax + 1.5)[0] - 9, P(0, hmax + 1.5)[1] - 2, 'A', 10, bold=True)
        lab(c, P(0, -1.1)[0] - 9, P(0, -1.1)[1] + 2, 'B', 10, bold=True)
        for lbl in a['labels']:
            kind = lbl[0]
            if kind == 'b':                                     # 下に（横 u の位置）
                lab(c, P(lbl[1], 0)[0], P(lbl[1], 0)[1] - 11, lbl[2])
            elif kind == 'r':                                   # 右に（横 u、高さの区間 v0〜v1）
                lab(c, P(lbl[1], (lbl[2] + lbl[3]) / 2)[0] + 4, P(lbl[1], (lbl[2] + lbl[3]) / 2)[1], lbl[4], anchor='l')
            elif kind == 't':                                   # 上に（横の区間 u0〜u1、高さ v）
                lab(c, P((lbl[1] + lbl[2]) / 2, lbl[3])[0], P(lbl[1], lbl[3])[1] + 8, lbl[4])
            elif kind == 'gap':                                 # 軸から図までのすきま（横の区間 u0〜u1、高さ v）
                dim_arrow(c, P(lbl[1], lbl[3]), P(lbl[2], lbl[3]), lbl[4], dy=8)

    def sh_pitbox(c, px, pw, rtop, rh, a):
        """直方体の上の面に、四角柱の穴（深さ pit の最後）をあけた立体。奥行きの長さの文字は dlab（x など）。"""
        L, D, H = a['L'], a['D'], a['H']
        x0, x1, y0, y1, pd = a['pit']
        ky = a.get('ky', .45)
        sc, ox, oy = fit(px, pw, rtop, rh, L + KX * D, H + ky * D, ml=26, mr=40, mt=6, mb=22)
        P = _obl(ox, oy, sc, KX, ky)
        zf = H - pd
        fill_poly(c, [P(x0, y0, zf), P(x1, y0, zf), P(x1, y1, zf), P(x0, y1, zf)], WHITE)               # 穴の底
        fill_poly(c, [P(x0, y0, zf), P(x0, y1, zf), P(x0, y1, H), P(x0, y0, H)], SHADE)               # 穴の左のかべ
        fill_poly(c, [P(x0, y1, zf), P(x1, y1, zf), P(x1, y1, H), P(x0, y1, H)], PALE)                # 穴の奥のかべ
        c.setFillColor(PALE)                                                                           # 上の面（穴あき）
        setline(c, 1.1)
        pa = c.beginPath()
        for ring in ([P(0, 0, H), P(L, 0, H), P(L, D, H), P(0, D, H)], [P(x0, y0, H), P(x1, y0, H), P(x1, y1, H), P(x0, y1, H)]):
            pa.moveTo(*ring[0])
            for q in ring[1:]:
                pa.lineTo(*q)
            pa.close()
        c.drawPath(pa, stroke=1, fill=1, fillMode=FILL_EVEN_ODD)
        fill_poly(c, [P(0, 0, 0), P(L, 0, 0), P(L, 0, H), P(0, 0, H)], WHITE)
        fill_poly(c, [P(L, 0, 0), P(L, D, 0), P(L, D, H), P(L, 0, H)], SHADE)
        lab(c, P(L / 2, 0, 0)[0], P(0, 0, 0)[1] - 11, f'{L:g}cm')
        lab(c, P(L, D / 2, 0)[0] + 5, P(L, D / 2, 0)[1] - 8, a['dlab'], anchor='l')
        lab(c, P(0, 0, H / 2)[0] - 4, P(0, 0, H / 2)[1], f'{H:g}cm', anchor='r')
        if a.get('pit_labels'):
            lab(c, P(x0, y1, H)[0] - 5, P(x0, y1, H)[1] + 6, f'穴は{x1 - x0:g}cm×{y1 - y0:g}cm', 8, 'r')
            lab(c, P(x0, y0, zf + pd / 2)[0] - 4, P(x0, y0, zf + pd / 2)[1], f'深さ{pd:g}cm', 8, 'r', halo=WHITE)

    def sh_triprism(c, px, pw, rtop, rh, a):
        """前の面が直角三角形（横 b・たて hh、直角は左下）の三角柱。おくゆき d。"""
        b, hh, d = a['b'], a['hh'], a['d']
        sc, ox, oy = fit(px, pw, rtop, rh, b + KX * d, hh + KY * d, ml=24, mr=44, mt=6, mb=22)
        P = _obl(ox, oy, sc, KX, KY)
        fill_poly(c, [P(0, 0, 0), P(b, 0, 0), P(0, 0, hh)], WHITE)
        fill_poly(c, [P(b, 0, 0), P(b, d, 0), P(0, d, hh), P(0, 0, hh)], SHADE)
        for q in ((0, 0, 0), (b, d, 0), (0, d, hh)):
            seg(c, P(0, d, 0), P(*q), .8, (3, 2))
        rt_mark(c, P(0, 0, 0), (1, 0), (0, 1))
        lab(c, P(b / 2, 0, 0)[0], P(0, 0, 0)[1] - 11, f'{b:g}cm')
        lab(c, P(0, 0, hh / 2)[0] - 4, P(0, 0, hh / 2)[1], f'{hh:g}cm', anchor='r')
        if a.get('slant'):                                       # 斜辺の長さ：斜辺のすぐ上（かげの面の中）
            m = P(.75 * b, 0, .25 * hh)
            nx, ny = hh, b
            nl = math.hypot(nx, ny)
            lab(c, m[0] + nx / nl * 12, m[1] + ny / nl * 12, a['slant'], 8.5, halo=SHADE)
        lab(c, P(b, d / 2, 0)[0] + 5, P(b, d / 2, 0)[1] - 8, f'{d:g}cm', anchor='l')

    def sh_fnotch(c, px, pw, rtop, rh, a):
        """直方体の、上の面の前のまん中を、直方体（はば・高さ nh・奥行き nd）の形に切りとった立体。"""
        L, D, H = a['L'], a['D'], a['H']
        nx0, nx1, nh, nd = a['notch']
        ky = a.get('ky', .4)
        sc, ox, oy = fit(px, pw, rtop, rh, L + KX * D, H + ky * D, ml=26, mr=40, mt=6, mb=22)
        P = _obl(ox, oy, sc, KX, ky)
        zf = H - nh
        fill_poly(c, [P(0, 0, H), P(nx0, 0, H), P(nx0, nd, H), P(nx1, nd, H), P(nx1, 0, H), P(L, 0, H), P(L, D, H), P(0, D, H)], PALE)
        fill_poly(c, [P(L, 0, 0), P(L, D, 0), P(L, D, H), P(L, 0, H)], SHADE)
        fill_poly(c, [P(nx0, 0, zf), P(nx1, 0, zf), P(nx1, nd, zf), P(nx0, nd, zf)], WHITE)             # 切りとった所の底
        fill_poly(c, [P(nx0, nd, zf), P(nx1, nd, zf), P(nx1, nd, H), P(nx0, nd, H)], PALE)              # 奥のかべ
        fill_poly(c, [P(nx0, 0, zf), P(nx0, nd, zf), P(nx0, nd, H), P(nx0, 0, H)], SHADE)               # 左のかべ
        fill_poly(c, [P(0, 0, 0), P(L, 0, 0), P(L, 0, H), P(nx1, 0, H), P(nx1, 0, zf), P(nx0, 0, zf), P(nx0, 0, H), P(0, 0, H)], WHITE)
        lab(c, P(L / 2, 0, 0)[0], P(0, 0, 0)[1] - 11, f'{L:g}cm')
        lab(c, P(L, D / 2, 0)[0] + 5, P(L, D / 2, 0)[1] - 8, f'{D:g}cm', anchor='l')
        lab(c, P(0, 0, H / 2)[0] - 4, P(0, 0, H / 2)[1], f'{H:g}cm', anchor='r')
        lab(c, P((nx0 + nx1) / 2, 0, zf)[0], P(0, 0, zf)[1] + 5, f'{nx1 - nx0:g}cm', 8)                  # 切りとった所のはば
        lab(c, P(nx1, 0, zf + nh / 2)[0] + 3, P(nx1, 0, zf + nh / 2)[1], f'{nh:g}cm', 8, 'l')           # 切りとった所の高さ
        lab(c, P(nx0, nd / 2, H)[0] - 6, P(nx0, nd / 2, H)[1] + 1, f'{nd:g}cm', 8, 'r')                  # 切りとった所の奥行き

    def sh_cylhole(c, px, pw, rtop, rh, a):
        """円柱（半径 r・高さ hh）の、まん中を、底面が正方形（1辺 s）の四角柱でくりぬいた立体。"""
        r, hh, s_ = a['r'], a['hh'], a['s']
        e = .3
        sc, ox, oy = fit(px, pw, rtop, rh, 2 * r, hh + 2 * e * r, ml=40, mr=40, mt=4, mb=22)
        cx, y0 = ox + r * sc, oy + e * r * sc

        def Pt(X, Y, Z):
            return (cx + X * sc, y0 + (Z + e * Y) * sc)
        th = [i * math.pi / 60 for i in range(121)]
        c.setFillColor(WHITE)
        setline(c, 1.1)
        p = c.beginPath()
        p.moveTo(*Pt(-r, 0, 0))
        for t in th[60:]:
            p.lineTo(*Pt(r * math.cos(t), r * math.sin(t), 0))
        p.lineTo(*Pt(r, 0, hh))
        for t in th[:61]:
            p.lineTo(*Pt(r * math.cos(t), r * math.sin(t), hh))
        p.close()
        c.drawPath(p, stroke=1, fill=1)
        fill_poly(c, [Pt(r * math.cos(t), r * math.sin(t), hh) for t in th[:-1]], PALE)
        q = s_ / 2
        bot = [Pt(-q, -q, 0), Pt(q, -q, 0), Pt(q, q, 0), Pt(-q, q, 0)]
        for (X, Y) in ((-q, -q), (q, -q), (q, q), (-q, q)):                       # 穴の、見えない辺（点線）
            seg(c, Pt(X, Y, hh), Pt(X, Y, 0), .7, (2.5, 2))
        for k in range(4):
            seg(c, bot[k], bot[(k + 1) % 4], .7, (2.5, 2))
        fill_poly(c, [Pt(-q, -q, hh), Pt(q, -q, hh), Pt(q, q, hh), Pt(-q, q, hh)], WHITE, 1.1)
        lab(c, Pt(0, 0, 0)[0], y0 - e * r * sc - 10, f'半径{r:g}cm')
        lab(c, Pt(-r, 0, hh / 2)[0] - 4, Pt(-r, 0, hh / 2)[1], f'{hh:g}cm', anchor='r')
        a1 = Pt(q, q, hh)
        seg(c, a1, (a1[0] + 18, a1[1] + 9), .5, None, MUTED)
        lab(c, a1[0] + 20, a1[1] + 10, f'1辺{s_:g}cm', 8, 'l')


    SOLIDS = {'cutbox': sh_cutbox, 'cutcyl': sh_cutcyl, 'cubes': sh_cubes, 'trapprism': sh_trapprism, 'revolve': sh_revolve,
              'pitbox': sh_pitbox, 'triprism': sh_triprism, 'fnotch': sh_fnotch, 'cylhole': sh_cylhole}

    def fig_solids(c, x, top, w, h, specs=()):
        """specs＝[(kind, {cap, wt, ...})]。(ア)(イ)(ウ) の見出しをつけて、よこにならべる。"""
        wts = [a.get('wt', 1) for _, a in specs]
        cum = 0
        for k, (kind, a) in enumerate(specs):
            pw = w * wts[k] / sum(wts)
            px = x + w * cum / sum(wts)
            cum += wts[k]
            if a.get('cap'):
                text(c, px + 4, top - 11, a['cap'], 10, bold=True)
            SOLIDS[kind](c, px, pw, top - 22, h - 22, a)
        setline(c, .8)

    # ------------------------------------------------------------------ 規則性・カード・展開図・木
    def fig_checkers(c, x, top, w, h, ns=(1, 2, 3, 4), cell=13, gap=26, dots=True):
        """n番目は、たて n・よこ n+1 の長方形に、白黒の正方形を市松もようにならべた図（左上は黒）。下をそろえてならべる。"""
        total = sum((n + 1) * cell for n in ns) + gap * (len(ns) - 1) + (30 if dots else 0)
        cx = x + (w - total) / 2
        base = top - h + 22
        for n in ns:
            for r in range(n):
                for k in range(n + 1):
                    black = (r + k) % 2 == 0
                    c.setFillColor(INK if black else WHITE)
                    setline(c, .7)
                    c.rect(cx + k * cell, base + (n - 1 - r) * cell, cell, cell, stroke=1, fill=1)
            lab(c, cx + (n + 1) * cell / 2, base - 11, f'{n}番目', 9.5)
            cx += (n + 1) * cell + gap
        if dots:
            lab(c, cx - gap + 6, base + ns[-1] * cell / 2, '…', 12, 'l')

    def fig_cards(c, x, top, w, h, digits=(0, 1, 1, 2, 3)):
        """数字のカードを、よこに1列。"""
        cw, ch, gp = 34, 44, 14
        total = len(digits) * cw + (len(digits) - 1) * gp
        cx = x + (w - total) / 2
        cy = top - (h - ch) / 2 - ch
        for d in digits:
            c.setFillColor(WHITE)
            setline(c, 1.3)
            c.roundRect(cx, cy, cw, ch, 4, stroke=1, fill=1)
            lab(c, cx + cw / 2, cy + ch / 2, str(d), 24, bold=True)
            cx += cw + gp

    def fig_net(c, x, top, w, h, cols=(), rows=(), faces=(), pts=None, dims=(), unit=20):
        """直方体の展開図。cols・rows＝列のはば・行の高さ（cm）。faces＝[(列, 行, 面の名前)]。pts＝{(i, j): 点の名前}（i・j は格子の線の番号）。
        dims＝[('top'|'right'|'bottom'|'left', (列, 行), 文字)]：その面のはしの長さ。面と面のあいだ（折り目）は点線。"""
        W_, H_ = sum(cols) * unit, sum(rows) * unit
        ox, oy = x + (w - W_) / 2, top - (h - H_) / 2          # 左上の角
        xs = [ox]
        for cw_ in cols:
            xs.append(xs[-1] + cw_ * unit)
        ys = [oy]
        for rh_ in rows:
            ys.append(ys[-1] - rh_ * unit)
        have = {(cc, rr): nm for cc, rr, nm in faces}
        for (cc, rr), nm in have.items():
            c.setFillColor(WHITE)
            c.rect(xs[cc], ys[rr + 1], xs[cc + 1] - xs[cc], ys[rr] - ys[rr + 1], stroke=0, fill=1)
        for (cc, rr), nm in have.items():
            for side, (p, q, nb) in {'top': ((xs[cc], ys[rr]), (xs[cc + 1], ys[rr]), (cc, rr - 1)),
                                     'bottom': ((xs[cc], ys[rr + 1]), (xs[cc + 1], ys[rr + 1]), (cc, rr + 1)),
                                     'left': ((xs[cc], ys[rr]), (xs[cc], ys[rr + 1]), (cc - 1, rr)),
                                     'right': ((xs[cc + 1], ys[rr]), (xs[cc + 1], ys[rr + 1]), (cc + 1, rr))}.items():
                if nb in have:
                    if side in ('bottom', 'right'):               # 点線は、となりあう面の片方からだけ引く
                        seg(c, p, q, .8, (3, 2.5), MUTED)
                else:
                    seg(c, p, q, 1.5)
            lab(c, (xs[cc] + xs[cc + 1]) / 2, (ys[rr] + ys[rr + 1]) / 2, nm, 14, bold=True)
        quad = {(-1, -1): (-1, 1), (0, -1): (1, 1), (-1, 0): (-1, -1), (0, 0): (1, -1)}   # 格子の点のまわりの4つのマスと、そのむき（左上・右上・左下・右下）
        for (i, j), nm in (pts or {}).items():
            # マスのある向きの反対がわ（外がわ）に、記号を書く
            ox_ = sum(sx for (dc, dr), (sx, sy) in quad.items() if (i + dc, j + dr) in have)
            oy_ = sum(sy for (dc, dr), (sx, sy) in quad.items() if (i + dc, j + dr) in have)
            nx_, ny_ = -ox_, -oy_
            if nx_ == 0 and ny_ == 0:
                nx_, ny_ = 1, 1
            n_ = math.hypot(nx_, ny_)
            q = (xs[i], ys[j])
            c.setFillColor(INK)
            c.circle(q[0], q[1], 1.6, stroke=0, fill=1)
            lab(c, q[0] + nx_ / n_ * 9.5, q[1] + ny_ / n_ * 9.5, nm, 9.5, bold=True)
        for side, (cc, rr), s in dims:
            if side == 'top':
                lab(c, (xs[cc] + xs[cc + 1]) / 2, ys[rr] + 10, s, 8.5)
            elif side == 'bottom':
                lab(c, (xs[cc] + xs[cc + 1]) / 2, ys[rr + 1] - 10, s, 8.5)
            elif side == 'right':
                lab(c, xs[cc + 1] + 5, (ys[rr] + ys[rr + 1]) / 2, s, 8.5, 'l')
            else:
                lab(c, xs[cc] - 5, (ys[rr] + ys[rr + 1]) / 2, s, 8.5, 'r')

    def fig_trees(c, x, top, w, h, n=5, gap=44, label='', dots=True):
        """木を、同じ間かくでよこにならべた図。label＝はじめの2本の間の長さ。"""
        total = (n - 1) * gap + (40 if dots else 0)
        cx = x + (w - total) / 2
        base = top - h + 14
        for k in range(n):
            tx = cx + k * gap
            seg(c, (tx, base), (tx, base + 12), 2.4)
            for (yb, hw, yt) in ((base + 9, 11, base + 24), (base + 19, 9, base + 32), (base + 28, 7, base + 40)):
                c.setFillColor(INK)
                c.drawPath(_poly(c, [(tx - hw, yb), (tx + hw, yb), (tx, yt)]), stroke=0, fill=1)
        seg(c, (cx - 14, base), (cx + (n - 1) * gap + (30 if dots else 14), base), 1.0)
        if label:
            dim_arrow(c, (cx, base - 9), (cx + gap, base - 9), label, dy=-7)
        if dots:
            lab(c, cx + (n - 1) * gap + 18, base + 10, '…', 12, 'l')

    B.FIGS['s6_dgraph'] = fig_dgraph
    B.FIGS['s6_solids'] = fig_solids
    B.FIGS['s6_checkers'] = fig_checkers
    B.FIGS['s6_cards'] = fig_cards
    B.FIGS['s6_net'] = fig_net
    B.FIGS['s6_trees'] = fig_trees
