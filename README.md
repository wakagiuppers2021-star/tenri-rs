# 天理中学校 理科・社会・算数・国語 大問別類題プリント

天理中学校の入試（理科・社会・算数・国語）の大問ごとに、出題形式をまねた類題を10セットずつ作る。
「大問1を10セット → 大問2を10セット → …」の順に進める。大問1は理科・社会とも完成済み。

## フォルダ構成

| パス | 中身 |
|---|---|
| `tools/build_tenri_rs.py` | PDFを作るスクリプト（レイアウト・図・検査） |
| `tools/tenri_rs_<rika\|shakai\|sansu\|kokugo><番号>.py` | 大問ごとのデータ（`SETS` と `ANALYSIS`） |
| `tools/check_tenri_rs.py` | 答えをデータとは別の計算・事実表で検算する |
| `tools/ja_read.py` | 国語の漢字の検算に使う、熟語の読みの分解（音読み・訓読み。連濁・促音に対応） |
| `tools/ja_grammar.py` | 国語の文法の検算に使う、形態素解析（janome）と、学校文法への読みかえ・表 |
| `tools/kanji_grade.py` | 漢字の学年配当（教育漢字1026字ほか）・部首番号・画数（KANJIDIC2、CC BY-SA 4.0）。国語の漢字の検算に使う |
| `tools/world_outline.py` | 世界地図の海岸線・国境のデータ（Natural Earth 1:110m。パブリックドメイン）。`fig_world` が使う |
| `tools/bundle_pdfs.py` | 大問ごとのPDFを、教科・種類（問題／解答解説／出題分析）ごとに1つにまとめる（しおり付き）。出力は `output/まとめ/` |
| `docs/過去問_読み取りメモ.md` | 2014〜2024年度の理科・社会の全大問の読み取りメモと出題分析 |
| `docs/過去問_読み取りメモ_算数.md` | 2014〜2024年度の算数の全大問の読み取りメモ（大問4の年度別一覧つき） |
| `docs/過去問_読み取りメモ_国語.md` | 国語の過去問の読み取りメモ（2014〜2024年度。2014年度は解答・解説ページだけ） |
| `fonts/` | BIZ UDゴシック（OFL版）とライセンス文 `OFL.txt` |
| `output/天理中学校_<理科\|社会>大問<番号>対策/` | 生成したPDF（git管理する） |

過去問のスキャン画像はこのリポジトリに入れていない。作問の根拠は `docs/過去問_読み取りメモ.md` だけにする。

## 準備

Python 3.10 以上。

```bash
pip install -r requirements.txt
```

## 生成・検算

```bash
python -X utf8 tools/build_tenri_rs.py rika 1
python -X utf8 tools/build_tenri_rs.py shakai 1
python -X utf8 tools/build_tenri_rs.py kokugo 1
python -X utf8 tools/check_tenri_rs.py
```

- `build_tenri_rs.py <rika|shakai|sansu|kokugo> <番号>` は、問題・解答解説・出題分析の3つのPDFを作り、続けてレイアウト（はみ出し・重なり）と本文の抽出もれを調べる。不具合があれば終了コード1。
- `check_tenri_rs.py` は、計算問題や事実問題の答えを独立に計算し直して照合する。あわせて `tools/tenri_rs_*.py` のすべてについて、10セットあるか・解答と解説が欠けていないかを調べる。不一致があれば終了コード1。

## 形式

- A4縦・1セット1ページ。各大問10セット。
- 1つの大問から3つのPDFを作る。
  - `天理中学校_<教科>大問<番号>_類題10セット_問題.pdf`（10ページ）
  - `天理中学校_<教科>大問<番号>_類題10セット_解答解説.pdf`（10ページ）
  - `天理中学校_<教科>大問<番号>_出題分析と使い方.pdf`（1ページ）
- 第01〜10セットは、過去問の各年度のその大問の形に1年ずつ対応させる（大問1では2024→2015年度）。

## 大問の追加手順

例：理科の大問2を作る場合。

1. `docs/過去問_読み取りメモ.md` で、各年度の理科の大問2の分野と問い方を読む。年度によって大問の数が違うので、対応させ方を決めて `ANALYSIS` に書く。
2. `tools/tenri_rs_rika1.py` を手本に `tools/tenri_rs_rika2.py` を作る。
   - `SETS`：10セットのリスト。各セットは `year`・`title`・`lead`・`qs`。必要なら `fig`（図）・`table`（表）・`items`（説明文の箇条）。図と表の両方があるときは、図を左・表を右にならべる。図が横に長いときは、セットに `stack=True` を書くと、図を上・表を下にならべる。
   - `qs` の各問は `kind`（`short`＝右の解答らん／`long`＝記述らん／`grid`＝複数の解答らん。`grid` は `labels` と `ans` の数をそろえる）・`q`・`ans`・`ex`、必要なら `unit`。
   - `ANALYSIS`：出題分析ページの中身。キーは `summary`・`years`・`points`・`usage`（大問1のファイルと同じ）。
3. 新しい図が要るときは、`tools/build_tenri_rs.py` に `fig_<名前>` 関数を足し、`FIGS` に登録する。
4. `tools/check_tenri_rs.py` に `import tenri_rs_rika2 as R2` と、その大問の検算（`eq(...)`）を足す。
5. 生成して検算する。

   ```bash
   python -X utf8 tools/build_tenri_rs.py rika 2
   python -X utf8 tools/check_tenri_rs.py
   ```

6. PDFを1ページずつ画像にして目で確かめる（図と文のずれ、解答らんの大きさ）。
7. `現況.md` を更新し、`tools/`・`output/`・`現況.md` をコミットする。

## 作問ルール

- 設問・図・表はすべて独自に作る。過去問の本文・図・表を転載しない（ページ下に「過去問の転載ではありません」と入る）。
- まねるのは、分野・問い方・設問数・難しさの形まで。
- 時事・統計・制度など変わりうる内容は、基準日を付ける（例：「2026年10月現在」）。分析ページか前書きにも基準日を書く。
- 計算問題・事実問題の答えは、`check_tenri_rs.py` でデータとは別に計算し直して照合する。データの `ans` を写しただけの検算にしない。
- 小学6年生が読める言葉と漢字にする（大問1のデータに合わせる）。

## クラウドセッションの始め方

Claude Code のクラウドセッションは、GitHub のこのリポジトリを clone して動く。成果は push しないと手元に戻らない。

1. このリポジトリを GitHub の private リポジトリに push しておく（初回のみ）。
2. https://claude.ai/code を開く（またはデスクトップアプリの Code タブでクラウドを選ぶ）。
3. GitHub と連携し、Claude の GitHub アプリにこのリポジトリへのアクセスを許可する。
4. リポジトリにこのリポジトリを選ぶ。ネットワークは PyPI から `pip install` できる設定にする。
5. 最初の指示の例：

   > AGENTS.md と README.md を読んでから、理科の大問2の類題10セットを作ってください。`docs/過去問_読み取りメモ.md` の各年度の理科・大問2を読み、`tools/tenri_rs_rika2.py` と検算を足し、build と check を通して、output/ ごとコミットして push してください。

6. 終わったら、クラウドセッションが push したブランチを GitHub でマージし、手元で取り込む。

   ```bash
   git pull
   ```

1回のセッションで1教科・1大問ずつ進めると、確認しやすい。

## フォントとライセンス

`fonts/` の BIZ UDゴシック（`BIZUDGothic-Regular.ttf`・`BIZUDGothic-Bold.ttf`）は、Google Fonts（https://github.com/google/fonts の `ofl/bizudgothic`）の SIL Open Font License 1.1 版。ライセンス文は `fonts/OFL.txt`。

Windows に入っている `C:\Windows\Fonts\BIZ-UDGothic*.ttc` は Microsoft 提供版で、再配布できないのでリポジトリに入れない。`build_tenri_rs.py` は `fonts/` を先に使い、無いときだけ Windows 版を使う。
