---
title: Phase 1 データ入力テンプレ案
作成日: 2025-10-28
作成者: Codex（GPT-5）
---

## 1. CSVテンプレート案
| カラム | 必須 | 内容 | 備考 |
| --- | --- | --- | --- |
| `entity_id` | ◎ | `company:nimbusflow` など | `field_dictionary` に沿った命名 |
| `entity_type` | ◎ | `company` / `market_segment` など | 必要なら列を追加 |
| `section` | ◎ | `kpi` / `deal_terms` など | report_sections と揃える |
| `field_id` | ◎ | `revenue_arr`, `deal.investment_amount` など | `field_dictionary` の keys |
| `value_type` | ◎ | `number` / `string` / `json` / `range` | `field_dictionary` と一致 |
| `value_number` | ○ | 数値の場合のみ入力 | `value_type = number` |
| `value_string` | ○ | テキストの場合 | `value_type = string` |
| `value_json` | ○ | JSON文字列（ビルトインスキーマに合わせる） | `value_type = json` / `range` |
| `unit` | ○ | `USD`, `%`, `count` など | 必要に応じて |
| `as_of` | ◎ | `YYYY-MM-DD` | 例：`2025-09-30` |
| `source_tag` | ◎ | `PUB` / `EXT` / `CONF` / `INT` / `ANL` | タグ方針に従う |
| `evidence_uri` | ○ | URL / ファイルパス / `calc:...` | ない場合は空欄可 |
| `disclosure_level` | ◎ | `IC` / `LP` / `LP_NDA` / `PRIVATE` | マスキング処理で参照 |
| `confidence` | ○ | `0.7` など | 0.0–1.0、空欄可 |
| `notes` | ○ | 補足メモ | 任意 |

### 1.1 CSVサンプル（抜粋）
```csv
entity_id,entity_type,section,field_id,value_type,value_number,value_string,value_json,unit,as_of,source_tag,evidence_uri,disclosure_level,confidence,notes
company:nimbusflow,company,deal_terms,deal.investment_amount,number,6500000,,,"USD",2025-09-30,CONF,calc:deal_sheet,IC,0.9,
company:nimbusflow,company,deal_terms,deal.key_terms_summary,string,,Liquidation Preference: 1x Non-Participating; ...,,"",2025-09-30,CONF,GDrive:term_sheet.pdf,IC,0.7,"標準語彙に変換要"
company:nimbusflow,company,kpi,gross_margin_pct,number,78.4,,,"percent",2025-09-30,INT,int/cfo_20251001,LP_NDA,0.8,
company:nimbusflow,company,kpi,gross_margin_breakdown,json,,,"{\"cost_items\":[{\"item\":\"Hosting\",\"percent\":12}]}",,2025-09-30,CONF,GDrive:cost_breakdown.xlsx,IC,,承認済
```

## 2. フォーム入力項目（ノーコード想定）
1. `Case / Entity`（選択またはID入力）
2. `Field`（ドロップダウン：`field_dictionary` の display_name）
3. `Value Type`（自動補完）
4. `Value`（数値/文字列/JSON入力欄）
5. `Unit`（任意）
6. `As-of Date`
7. `Source Tag`（ラジオボタン）
8. `Evidence URI / File`（リンクまたは添付のメタ情報）
9. `Disclosure Level`
10. `Confidence`（任意）
11. `Notes`（任意）

※ フォームからエクスポートしたCSVが上記テンプレと整合するよう列順を合わせる。

## 3. タグ運用ルール（再掲）
- **ANL**: 設計・分析資料（既存資料の大半）
- **PUB**: 公開資料（今後追加）
- **EXT**: 推定データ（API連携後に追加）
- **CONF**: 社内機密資料（Phase 2 以降）
- **INT**: インタビュー（Phase 3 以降）

## 4. 次アクション
- 実データ投入を想定した `observations_fund_phase1.csv` のドラフトを作成し、上記テンプレと照合する。
- `field_dictionary_v0_1.json` と照らし合わせて、フォーム選択肢（display_name → field_id）をマッピング。
- CSVから観測テーブルへのインジェストスクリプトを準備する（Phase 1 後半）。_currently todo_
