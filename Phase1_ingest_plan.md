---
title: Phase 1 インジェスト設計案（P1-B）
作成日: 2025-10-28
作成者: Codex（GPT-5）
---

## 1. ゴール
- `observations_fund_phase1.csv` などの入力ファイルを観測テーブル形式（JSON/DB）に変換する。
- 手動インジェスト手順（承認・ログ記録）を明確化し、Phase 2 のCONF自動化へつながる下地を作る。

## 2. インジェストフロー案
1. **入力取得**: CSV/フォームからエクスポートしたファイルを `data/input/` に保存  
2. **検証**: 
   - `field_id` が `field_dictionary_v0_1.json` に存在するかチェック  
   - `value_type` と値（number/string/json）が整合しているかチェック  
   - `as_of`, `source_tag`, `disclosure_level` の必須項目が入力されているか確認  
3. **正規化**: 各行を観測レコードに変換し、`value_status` や `notes` を付与  
4. **出力**: JSONファイル（例: `data/output/observations_phase1.json`）に書き出し、`scripts/lp_masking.py` 系で読み込めるようにする  
5. **ログ記録**: 実行日時、件数、エラーを `logs/import_runs.log` に保存。承認者がいる場合は手動確認後に反映。

## 3. スクリプト骨子（案）
- ファイル: `scripts/import_observations_template.py`
- 機能:
  ```python
  from pathlib import Path
  import csv, json
  from lp_masking import load_configs

  def validate_row(row, field_dict):
      # field_id/ value_type/ required columns check
      # return (True, normalized_row) or (False, error_message)

  def import_csv(csv_path: Path, output_path: Path):
      configs = load_configs()
      errors = []
      records = []
      with csv_path.open(encoding="utf-8") as f:
          reader = csv.DictReader(f)
          for line_no, row in enumerate(reader, start=2):
              ok, result = validate_row(row, configs["field_dict"])
              if ok:
                  records.append(result)
              else:
                  errors.append({"line": line_no, "message": result})
      output_path.write_text(json.dumps(records, ensure_ascii=False, indent=2), encoding="utf-8")
      return errors
  ```
- 出力に `value_status` を付与 (`pending` if `notes` に pending を含むなど)
- エラー行はログへ書き出して手修正→再実行する運用。

## 4. 手動手順（初期運用）
1. CSV を `data/input/observations_YYYYMMDD.csv` に配置  
2. コマンド例:  
   ```powershell
   python scripts/import_observations_template.py `
       --input data/input/observations_20251029.csv `
       --output data/output/observations_phase1.json `
       --log logs/import_runs.log
   ```  
3. ログにエラーが出た場合は CSV を修正して再実行  
4. 出力JSONを `render_report_markdown.py` に渡してプレビュー確認  
5. 承認済みであれば（CONF/INTを含む場合）、観測テーブルDBへ挿入 ※Phase 1ではファイル保存まで

## 5. 今後の拡張（Phase 2/3 への布石）
- CONFファイルをアップロードした際、部分抽出→CSVへ変換する半自動UIを用意（P2-2/P2-3）
- INTフォームの提出を自動CSV化し、このインジェストスクリプトで統合（P3-2）
