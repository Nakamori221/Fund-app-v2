---
title: Phase 1 テスト実行計画（ダミー/実データ投入）
作成日: 2025-10-28
作成者: Codex（GPT-5）
---

## 1. 目的
- 観測テーブルへの手動インジェスト → マスキング → レポート生成 → ギャップ検出までの一連フローをダミーデータで検証。
- Phase 1 完了条件（欠損可視化・`pending` 表示・ギャップ管理）が満たされるか確認。

## 2. テスト環境
- スクリプト：`scripts/lp_masking.py`, `scripts/render_report_markdown.py`, `scripts/gap_sync.py`
- テンプレ：`tests/fixtures/observations_lp_sample.json`（拡張予定）
- 期待値：`tests/fixtures/expected_lp_output.json`
- コマンド例：`python scripts/render_report_markdown.py` / `python scripts/gap_sync.py`

## 3. テストケース（ダミーデータ）
| Case | 項目 | 観測値入力 | 期待結果 | 備考 |
| --- | --- | --- | --- | --- |
| T1 | LPレポート生成 | `render_report_markdown.py`（デフォルト） | `lp_report_preview.md` でマスク値が表示され、欠損は `[pending]` | 既存 `observations_lp_sample.json` を使用 |
| T2 | LPギャップ検出 | `gap_sync.py` | `gap_sync_output.json` に必須フィールドの欠損が列挙される | `detect_gaps(lp_default)` |
| T3 | ICレポート生成（生値） | `render_report_markdown.py --template-id ic_default` | `ic_report_preview.md` に生値（マスクなし）が表示され `[pending]` で不足可視化 | 生値フォーマット確認 |
| T4 | ICレポート生成（マスク） | `render_report_markdown.py --template-id ic_default --use-masked` | IC版でもLPと同じマスク表示になる | LP向け共有時の比較用 |
| T5 | ICギャップ検出 | `gap_sync.py --template-id ic_default` | `gap_sync_ic.json` にIC必須フィールドの欠損が列挙される | 生値ベースでのギャップ確認 |

## 4. 実データ投入試験（予定）
- Step 1 で定義した指標辞書を基に、匿名化実データを `observations_fund_phase1.csv` に作成し、スクリプトでJSONへ変換→上記コマンドで検証。
- 検証対象：ARR/MRR、ユニットエコノミクス、ディール条項、マルチプルなど主要指標。
- 結果記録：`tests/artifacts/phase1_run_log.md`（新規作成予定）

## 5. 判定基準
- レポート：欠損時には `[pending]` 表示、必須フィールドが埋まれば自動更新されること。
- マスキング：`expected_lp_output.json` と `pytest` の結果が一致。
- ギャップ：必須項目がギャップJSONに記録され、テンプレIDごとの欠損が把握できる。

## 6. 次アクション
1. 実データインジェスト用CSVの草稿を作成（Phase 1 データ投入テンプレ案を参照）。
2. CSV→JSON変換スクリプト（例：`scripts/import_observations.py`）を実装して本番移行に備える。
3. 実データを用いた`pytest`拡張（専用期待値ファイル）を追加し、回帰テストに組み込む。
