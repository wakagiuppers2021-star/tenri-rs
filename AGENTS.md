# 天理中学校 理科・社会 大問別類題プリント

## 目的

天理中学校の入試（理科・社会・算数・国語）の大問ごとに、出題形式をまねた独自の類題を10セットずつ作る。順番は大問1 → 大問2 → …（算数は、依頼のあった大問から。国語は、長文読解を除き、1 漢字／2 語句・熟語／3 文法／4 作文の4大問）。手順・形式・作問ルールは `README.md` を正本とする。

## 正本

- レイアウト・図・検査：`tools/build_tenri_rs.py`
- 大問ごとのデータ：`tools/tenri_rs_<rika|shakai|sansu|kokugo><番号>.py`
- 検算：`tools/check_tenri_rs.py`（算数は、大問ごとの `tools/check_sansu<番号>.py` と共通部品 `tools/check_common.py`。起動時に自動で読み込まれる）
- 過去問の読み取り：`docs/過去問_読み取りメモ.md`（理科・社会）・`docs/過去問_読み取りメモ_算数.md`（算数。2014〜2024年度）。過去問のスキャンはリポジトリにない。これらのメモだけを根拠にする。
- 算数のデータは `tools/tenri_rs_sansu<番号>.py`（`build_tenri_rs.py sansu <番号>`）。国語は `tools/tenri_rs_kokugo<番号>.py`（`build_tenri_rs.py kokugo <番号>`）。国語の過去問の読み取りは `docs/過去問_読み取りメモ_国語.md`。漢字の学年配当・部首・画数は `tools/kanji_grade.py`。
- `output/` のPDFは生成物。直接編集しない。

## 検証ループ

1. 新しい環境では最初に `pip install -r requirements.txt`。
2. `python -X utf8 tools/build_tenri_rs.py <rika|shakai|sansu|kokugo> <番号>` で生成する。レイアウト不具合0・抽出もれ0になるまで直す。
3. `python -X utf8 tools/check_tenri_rs.py` で不一致0にする。新しい大問の検算を足してから通す。
4. PDFを画像にして目で確かめる。
5. `現況.md` を更新し、`tools/`・`output/`・`現況.md` をコミットする。

## 守ること

- 過去問の本文・図・表を転載しない。時事・統計には基準日を付ける。
- 完成済みの大問のPDFの名前・番号・内容を、指示なく変えない。
- 外部フォント・CDNを足さない。フォントは `fonts/` のOFL版だけを使う。
- 未確定のことは `現況.md` に●●と書き、推測で埋めない。

## Codex・Claude 共通の運用

- このフォルダはCodexとClaude（Claude Code・クラウドセッション）で共用する。Claudeは `CLAUDE.md` からこのファイルを読み込む。共通ルールはこのファイルにだけ書く。
- 作業を始める前に `現況.md` を読み、区切りで更新する（いまの段階／確定していること／次の一手／未確定・要確認）。
