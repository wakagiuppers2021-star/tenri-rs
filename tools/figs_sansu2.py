"""算数・大問2 専用の図（名前は s2_ で始める）。

's2_tabnets'：表（周が一定の長方形）と、しるしをつけた立方体の見取図・4つの展開図を、1つの図にならべる。
    args=dict(
        table=dict(cap='(7)', rows=[[...], ...], colw=[...]),            # 省略可
        cube=dict(cap='(8)', top='○', front='×', right='●'),             # 見える3つの面のしるし
        nets=[dict(label='ア', cells=[(行, 列), ...6つ], marks=[(行, 列, 'しるし'), ...]), ...])
    しるしは、4回転しても同じに見える記号（○・×・●）にする（文字の向きを考えなくてよい）。
    検算（tools/check_sansu2.py）は、cells・marks を読んで、3次元で折りたたんで調べる。
"""
from __future__ import annotations


def register(B):
    colors, text, setline, _poly = B.colors, B.text, B.setline, B._poly
    INK, MUTED, LINE, PALE = B.INK, B.MUTED, B.LINE, B.PALE

    def draw_cube(c, x0, y0, s, dx, dy, top, front, right):
        """見取図。(x0, y0) は、前の面の左下。"""
        faces = [([(x0, y0), (x0 + s, y0), (x0 + s, y0 + s), (x0, y0 + s)], colors.white, front, (x0 + s / 2, y0 + s / 2), 12),
                 ([(x0, y0 + s), (x0 + s, y0 + s), (x0 + s + dx, y0 + s + dy), (x0 + dx, y0 + s + dy)], colors.white, top, (x0 + s / 2 + dx / 2, y0 + s + dy / 2), 10),
                 ([(x0 + s, y0), (x0 + s + dx, y0 + dy), (x0 + s + dx, y0 + s + dy), (x0 + s, y0 + s)], colors.white, right, (x0 + s + dx / 2, y0 + s / 2 + dy / 2), 10)]
        setline(c, 1.1)
        for pts, col, sym, (cx, cy), size in faces:
            c.setFillColor(col)
            c.drawPath(_poly(c, pts), stroke=1, fill=1)
            text(c, cx, cy - size * .3, sym, size, center=True)

    def draw_net(c, x0, y_top, cell, cells, marks):
        """(x0, y_top) は、展開図の左上。行は下へ、列は右へ。"""
        mk = {(r, k): s for r, k, s in marks}
        setline(c, 1.0)
        for r, k in cells:
            c.setFillColor(colors.white)
            c.rect(x0 + k * cell, y_top - (r + 1) * cell, cell, cell, stroke=1, fill=1)
            if (r, k) in mk:
                text(c, x0 + (k + .5) * cell, y_top - (r + .5) * cell - 3.2, mk[(r, k)], 10.5, center=True)

    def fig_tabnets(c, x, top, w, h, table=None, cube=None, nets=()):
        y = top
        if table:
            text(c, x + 4, y - 11, table['cap'], 10, bold=True)
            colw = table['colw']
            B.draw_table(c, x + 36, y - 3, table['rows'], colw, 9.5, True, False)
            y -= 3 + len(table['rows']) * 9.5 * 1.9 + 12
        if cube or nets:
            if cube:
                text(c, x + 4, y - 11, cube['cap'], 10, bold=True)
                draw_cube(c, x + 40, y - 14 - 30 - 12, 30, 13, 12, cube['top'], cube['front'], cube['right'])
            cell = 14
            gap = 22
            tot = len(nets) * 4 * cell + (len(nets) - 1) * gap
            nx = x + 120 + (w - 120 - tot) / 2
            for k, nt in enumerate(nets):
                x0 = nx + k * (4 * cell + gap)
                draw_net(c, x0, y - 10, cell, nt['cells'], nt['marks'])
                text(c, x0 + 2 * cell, y - 10 - 3 * cell - 12, nt['label'], 10, bold=True, center=True)

    B.FIGS['s2_tabnets'] = fig_tabnets
