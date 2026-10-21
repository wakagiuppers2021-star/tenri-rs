"""算数・大問3 専用の図（図の名前は s3_ で始める）。tools/build_tenri_rs.py が、起動時に register(B) を呼ぶ。

s3_shapes : 平面図形（頂点の座標）をならべて、ア・イ・…の記号と名前をつける。線対称・点対称を選ぶ問題（第05セット）。
            args=dict(shapes=[('二等辺三角形', [(0, 0), (4, 0), (2, 3)]), ...], per=4)
            すべての図形を、同じ縮尺で描く（座標1あたりの長さが同じ）。検算は、この座標から対称性を調べる。
s3_cells  : 正方形のマスをつないだ図形（テトロミノなど）をならべて、ア・イ・…の記号をつける（第08セット）。
            args=dict(items=[[(0, 0), (1, 0), (2, 0), (3, 0)], ...], per=4)   (列, 行) のマスの集まり。行は上に向かってふえる。
"""
from __future__ import annotations

import math

KANA = 'アイウエオカキク'


def register(B):
    colors, text, setline, _poly = B.colors, B.text, B.setline, B._poly

    def fig_s3_shapes(c, x, top, w, h, shapes=(), per=4):
        n = len(shapes)
        rows = math.ceil(n / per)
        cw, rh = w / per, h / rows
        big = max(max(max(p[0] for p in pts) - min(p[0] for p in pts), max(p[1] for p in pts) - min(p[1] for p in pts)) for _, pts in shapes)
        sc = min(cw - 34, rh - 34) / big
        for i, (name, pts) in enumerate(shapes):
            r, k = divmod(i, per)
            xs, ys = [p[0] for p in pts], [p[1] for p in pts]
            cx0 = x + k * cw + cw / 2 - (max(xs) + min(xs)) / 2 * sc
            cy0 = top - r * rh - (rh - 18) / 2 - (max(ys) + min(ys)) / 2 * sc
            c.setFillColor(colors.white)
            setline(c, 1.1)
            c.drawPath(_poly(c, [(cx0 + px * sc, cy0 + py * sc) for px, py in pts]), stroke=1, fill=1)
            text(c, x + k * cw + cw / 2, top - r * rh - rh + 6, f'{KANA[i]} {name}', 9.5, center=True)

    def fig_s3_cells(c, x, top, w, h, items=(), per=4):
        n = len(items)
        rows = math.ceil(n / per)
        cw, rh = w / per, h / rows
        big = max(max(max(p[0] for p in cells) - min(p[0] for p in cells), max(p[1] for p in cells) - min(p[1] for p in cells)) + 1 for cells in items)
        u = min(24, (cw - 30) / big, (rh - 36) / big)
        for i, cells in enumerate(items):
            r, k = divmod(i, per)
            xs, ys = [p[0] for p in cells], [p[1] for p in cells]
            wd, ht = (max(xs) - min(xs) + 1) * u, (max(ys) - min(ys) + 1) * u
            ox = x + k * cw + (cw - wd) / 2 - min(xs) * u
            oy = top - r * rh - 6 - ht - (rh - 30 - ht) / 2 - min(ys) * u
            c.setFillColor(colors.white)
            setline(c, 1.1)
            for (gx, gy) in cells:
                c.rect(ox + gx * u, oy + gy * u, u, u, stroke=1, fill=1)
            text(c, x + k * cw + cw / 2, top - r * rh - rh + 6, KANA[i], 10, bold=True, center=True)

    B.FIGS['s3_shapes'] = fig_s3_shapes
    B.FIGS['s3_cells'] = fig_s3_cells
