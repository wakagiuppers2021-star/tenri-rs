"""大問ごとのPDFを、教科・種類ごとに1つにまとめる（しおり付き）。

使い方:
  python -X utf8 tools/bundle_pdfs.py                    理科大問2〜9・社会大問2〜5をまとめる
  python -X utf8 tools/bundle_pdfs.py --all              大問1もふくめて、できている大問をすべてまとめる（算数もふくむ）

出力: output/まとめ/天理中学校_<理科|社会>_大問<最初>〜<最後>_<問題|解答解説|出題分析>まとめ.pdf
output/ の大問ごとのPDFは、読むだけで、変えない。
"""
from __future__ import annotations

import importlib
import sys
from pathlib import Path

import fitz

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'tools'))

OUT = ROOT / 'output' / 'まとめ'
DEFAULT = {'rika': range(2, 10), 'shakai': range(2, 6)}
SUBJ = {'rika': '理科', 'shakai': '社会', 'sansu': '算数'}
KINDS = [('問題', '*_問題.pdf'), ('解答解説', '*_解答解説.pdf'), ('出題分析', '*_出題分析と使い方.pdf')]


def find_pdf(subj, dai, pattern):
    hits = sorted((ROOT / 'output' / f'天理中学校_{SUBJ[subj]}大問{dai}対策').glob(pattern))
    return hits[0] if hits else None


def bundle(subj, dais):
    OUT.mkdir(parents=True, exist_ok=True)
    made = []
    for kind, pattern in KINDS:
        doc = fitz.open()
        toc = []
        used = []
        for dai in dais:
            src = find_pdf(subj, dai, pattern)
            if src is None:
                continue
            mod = importlib.import_module(f'tenri_rs_{subj}{dai}')
            start = doc.page_count + 1
            with fitz.open(src) as part:
                doc.insert_pdf(part)
            toc.append([1, f'大問{dai}', start])
            if kind != '出題分析':
                for i, st in enumerate(mod.SETS, 1):
                    toc.append([2, f'第{i:02d}セット　{st["title"]}', start + i - 1])
            used.append(dai)
        if not used:
            continue
        doc.set_toc(toc)
        span = f'{used[0]}' if used[0] == used[-1] else f'{used[0]}〜{used[-1]}'
        name = f'天理中学校_{SUBJ[subj]}_大問{span}_{kind}まとめ.pdf'
        doc.set_metadata({'title': name[:-4], 'author': '', 'subject': '天理中学校 入試対策 類題プリント'})
        doc.save(OUT / name, garbage=3, deflate=True)
        made.append((name, doc.page_count))
        doc.close()
    return made


def main():
    every = '--all' in sys.argv
    for subj, default in (DEFAULT if not every else {**DEFAULT, 'sansu': None}).items():
        dais = range(1, 10) if every else default
        for name, pages in bundle(subj, dais):
            print(f'{name}  {pages}ページ')


if __name__ == '__main__':
    main()
