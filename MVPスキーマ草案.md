---
title: MVPデータスキーマ草案（観測テーブル／ギャップテーブル／レポートテンプレ）
作成日: 2025-10-28
作成者: Codex（GPT-5）
---

## 1. 前提整理
- 参照資料：`MVPを設計する前の仕様の再確認.md`、`Step 1：指標定義辞書.md`、`Step 4（ダミー案件で一巡テスト）.md`、`セクション別「何をWEBで先行埋めできるか」マトリクス.md`、`投資委員会資料フォーマット_完全版.md` 等。
- レコードの最小単位は「案件（case）×セクション×フィールド×As-of×ソースタグ」。
- 欠損値は `status: pending` または `value_status = 'pending'` で保持し、プレビューではブランク＋注記表示とする。
- SourceTag は `PUB / EXT / INT / CONF / ANL` の5種に `calc` 等の派生を追加できる前提で設計。

## 2. 観測テーブル（observations）詳細スキーマ

### 2.1 レコード粒度
- 1レコード = 特定案件の特定フィールド（例：`kpi.revenue_arr`）の**単一As-of値**。
- 派生値（ANL計算）も同じテーブルに格納し `source_tag = 'ANL'` とする。
- エンティティ軸は `entity_type`（company / team_member / market / competitor / deal / doc など）＋`entity_id`で拡張。

### 2.2 カラム定義
| カラム名 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `observation_id` | UUID | ✓ | 主キー。 |
| `case_id` | UUID | ✓ | `cases.id` へのFK。 |
| `entity_type` | TEXT | ✓ | `company` / `team_member` / `market_segment` / `competitor` / `deal` / `document` 等。 |
| `entity_id` | TEXT | ✓ | `company:nimbusflow`, `competitor:asana` など命名規約に沿ったID。 |
| `section` | TEXT | ✓ | `exec_summary` / `business` / `product` / `market` / `competition` / `kpi` / `financials` / `team` / `deal_terms` / `valuation` / `risk` / `value_creation` / `appendix` 等。 |
| `field_id` | TEXT | ✓ | 指標辞書IDまたは narrative 用フィールドID（例：`revenue_arr`, `thesis.statement`）。 |
| `field_display_name` | TEXT |  | 表示名（日本語）。辞書から自動補填。 |
| `value_type` | TEXT | ✓ | `number` / `string` / `date` / `boolean` / `json` / `range`。 |
| `value_number` | NUMERIC |  | `value_type='number'` の実数値。 |
| `value_string` | TEXT |  | 概要や説明文。 |
| `value_date` | DATE |  | 日付値。 |
| `value_boolean` | BOOLEAN |  | 真偽値。 |
| `value_json` | JSONB |  | レンジ・リスト・表形式など構造化データ。 |
| `unit` | TEXT |  | `USD` / `%` / `count` / `months` など。 |
| `currency` | TEXT |  | 通貨変換時に使用（例：`USD`, `JPY`）。 |
| `period` | TEXT |  | `monthly` / `quarterly` / `annual` / `snapshot` / `lifetime` 等。 |
| `as_of` | DATE | ✓ | データ取得時点。 |
| `value_status` | TEXT | ✓ | `confirmed` / `derived` / `pending` / `deprecated`。 |
| `source_tag` | TEXT | ✓ | `PUB` / `EXT` / `INT` / `CONF` / `ANL` / `CALC`。 |
| `source_priority` | SMALLINT |  | 同一フィールドでの優先順位（小さいほど優先）。`CONF=1, INT=2, PUB=3, EXT=4, ANL=5` 等。 |
| `evidence_uri` | TEXT | ✓ | URL / ファイルパス / `calc:...`。 |
| `evidence_excerpt` | TEXT |  | 証憑の要旨（スクショIDや抜粋）。 |
| `as_of_timezone` | TEXT |  | タイムゾーン（UTC, JST 等）。 |
| `confidence` | NUMERIC(3,2) |  | 0.00–1.00。 |
| `disclosure_level` | TEXT | ✓ | `IC` / `LP` / `LP_NDA` / `PRIVATE`。 |
| `requires_approval` | BOOLEAN |  | CONF/INT起点で承認必須なら true。 |
| `approval_status` | TEXT |  | `pending` / `approved` / `rejected`。 |
| `approved_by` | UUID |  | 承認者。 |
| `approved_at` | TIMESTAMPTZ |  | 承認日時。 |
| `derived_from` | UUID[] |  | 依存観測値（ANL時に使用）。 |
| `calculation_note` | TEXT |  | 計算式・仮定の説明。 |
| `quality_flags` | TEXT[] |  | `["stale","low_confidence"]` 等のフラグ。 |
| `created_by` | UUID |  | 登録ユーザー。 |
| `created_at` | TIMESTAMPTZ | ✓ | 作成日時。 |
| `updated_at` | TIMESTAMPTZ | ✓ | 更新日時。 |
| `version` | INTEGER | ✓ | 悪用防止のためのバージョン番号。 |

### 2.3 補助テーブル案
- `observation_history`: 変更履歴（旧値・新値・変更理由・操作ユーザー）。
- `observation_attachments`: 原本ファイルへのリンク（ファイルID・ページ番号・ハイライト座標）。
- `observation_links`: `observation_id` 同士の依存関係（ANL計算やシナリオ比較用）。

### 2.4 バリデーション & ビジネスルール
- 同一 `(case_id, entity_id, field_id, as_of, source_tag)` の重複禁止。
- `value_status='pending'` の場合、`value_*` は NULL、`expected_source_tag` を `value_json.expected_source` に格納。
- `disclosure_level='LP'` 以下は LP資料へそのまま露出可。`LP_NDA` 以上はマスキング定義に従い変換。
- `confidence < 0.7` の `EXT` 値は自動で注意書きを付与し、ギャップ検出対象とする。
- `requires_approval=true` かつ `approval_status!='approved'` の値はレポート反映時に脚注で「承認待ち」と明記。

### 2.5 観測レコード例（JSONイメージ）
```json
{
  "observation_id": "0d7d5f8c-2c34-4f0c-b538-9a6c2b75c111",
  "case_id": "a4e1b11a-524c-4c7b-912f-9c52ee457100",
  "entity_type": "company",
  "entity_id": "company:nimbusflow",
  "section": "kpi",
  "field_id": "revenue_arr",
  "value_type": "number",
  "value_number": 8500000,
  "unit": "USD",
  "period": "annual",
  "as_of": "2025-09-30",
  "value_status": "confirmed",
  "source_tag": "PUB",
  "source_priority": 3,
  "evidence_uri": "https://example.com/press-release",
  "confidence": 0.7,
  "disclosure_level": "LP",
  "quality_flags": ["stale_warning"],
  "created_by": "user:analyst_01",
  "created_at": "2025-10-10T02:15:00Z",
  "updated_at": "2025-10-12T05:20:00Z",
  "version": 3
}
```

---

## 3. ギャップテーブル（gaps）詳細スキーマ

### 3.1 レコード粒度
- 1レコード = 特定案件・フィールドに対する未充足／低確度／矛盾の解消タスク。
- 自動検出（Bot）と手動登録（アナリスト）の双方を許容。

### 3.2 カラム定義
| カラム名 | 型 | 必須 | 説明 |
| --- | --- | --- | --- |
| `gap_id` | UUID | ✓ | 主キー。 |
| `case_id` | UUID | ✓ | 案件ID。 |
| `entity_id` | TEXT | ✓ | 観測テーブルと同じ命名。 |
| `section` | TEXT | ✓ | 観測テーブルと同じ分類。 |
| `field_id` | TEXT | ✓ | 欠損対象フィールド。 |
| `gap_type` | TEXT | ✓ | `missing` / `low_confidence` / `conflict` / `stale` / `policy_masking_review`。 |
| `detected_by` | TEXT | ✓ | `auto` / `manual`。 |
| `detected_at` | TIMESTAMPTZ | ✓ | 検出日時。 |
| `owner_role` | TEXT | ✓ | `CEO` / `CFO` / `CRO` / `Legal` / `Analyst` 等。 |
| `owner_user_id` | UUID |  | 担当者ID（未アサイン時はNULL）。 |
| `required_source_tag` | TEXT |  | 期待する取得元（`CONF` / `INT` / `PUB` 等）。 |
| `question_prompt` | TEXT | ✓ | 相手に投げる質問文（INT向け）または資料要求文（CONF向け）。 |
| `expected_format` | TEXT |  | `csv:gross_margin_breakdown` / `md:interview_notes` 等。 |
| `priority_score` | SMALLINT | ✓ | 1〜5。2=通常,5=ICブロッカー。 |
| `impact_area` | TEXT |  | `valuation` / `risk` / `deal_terms` 等。 |
| `due_date` | DATE |  | 期日。 |
| `status` | TEXT | ✓ | `open` / `in_progress` / `awaiting_review` / `resolved` / `deferred`。 |
| `status_reason` | TEXT |  | ステータスに付随する備考。 |
| `resolution_observation_ids` | UUID[] |  | 解消に使用した観測レコードID。 |
| `resolution_notes` | TEXT |  | 結果メモ（「CFOより2025-10-20に受領」等）。 |
| `resolved_by` | UUID |  | 担当者。 |
| `resolved_at` | TIMESTAMPTZ |  | 解消日時。 |
| `follow_up_gap_id` | UUID |  | 継続フォロー用に次のギャップを紐付け。 |
| `created_by` | UUID | ✓ | レコード作成者（Botは `system:auto_gap_detector` 等）。 |
| `created_at` | TIMESTAMPTZ | ✓ | 作成日時。 |
| `updated_at` | TIMESTAMPTZ | ✓ | 更新日時。 |

### 3.3 ステータス遷移
1. `open`（自動検出or手動登録）
2. `in_progress`（担当割当済み）
3. `awaiting_review`（資料／回答取得済、承認待ち）
4. `resolved`（観測テーブルに登録済・承認済）
5. `deferred`（当フェーズ対象外／次ラウンドへ持ち越し）  
※ `resolved` 時に観測値へリンクし、ギャップ一覧から除外。

### 3.4 ギャップレコード例
```json
{
  "gap_id": "7f1e9431-8f3c-49a6-8ad2-0f45ab201122",
  "case_id": "a4e1b11a-524c-4c7b-912f-9c52ee457100",
  "entity_id": "company:nimbusflow",
  "section": "kpi",
  "field_id": "gross_margin_breakdown",
  "gap_type": "missing",
  "detected_by": "auto",
  "detected_at": "2025-10-10T04:15:00Z",
  "owner_role": "CFO",
  "required_source_tag": "CONF",
  "question_prompt": "直近12ヶ月の粗利率をコスト項目別に提示してください（ホスティング、外注、決済手数料等）。As-ofと通貨単位を明記願います。",
  "expected_format": "csv:gross_margin_breakdown_v1",
  "priority_score": 4,
  "impact_area": "unit_economics",
  "due_date": "2025-10-18",
  "status": "in_progress",
  "resolution_notes": null,
  "created_by": "system:auto_gap_detector",
  "created_at": "2025-10-10T04:15:00Z",
  "updated_at": "2025-10-11T08:00:00Z"
}
```

---

## 4. レポートテンプレ（report_templates）構造

### 4.1 基本方針
- テンプレは `report_templates`（ヘッダー）と `report_sections`（子要素）で管理。
- `report_template_id` に `IC`, `LP` を想定。LP版は同じセクション構造だがマスキング・丸め・表示有無が異なる。
- 各セクションは表示順・必須度・データ依存をJSONで定義し、生成エンジンが観測値を埋め込む。

### 4.2 テーブル案

#### `report_templates`
| カラム | 型 | 説明 |
| --- | --- | --- |
| `template_id` | TEXT | `ic_default`, `lp_default` 等。 |
| `name` | TEXT | 表示名。 |
| `description` | TEXT | テンプレの狙い。 |
| `version` | INTEGER | テンプレ版管理。 |
| `effective_from` | DATE | 適用開始日。 |
| `effective_to` | DATE | 終了予定（NULL可）。 |
| `masking_policy_id` | TEXT | `/config/lp_masking_policy_v0_1.json` 等。 |

#### `report_sections`
| カラム | 型 | 説明 |
| --- | --- | --- |
| `section_id` | TEXT | 固有ID（例：`exec_summary`）。 |
| `template_id` | TEXT | FK。 |
| `order_index` | SMALLINT | 表示順。 |
| `title` | TEXT | 表示タイトル。 |
| `purpose` | TEXT | セクションの狙い。 |
| `required` | BOOLEAN | テンプレ的に必須か。 |
| `ic_visible` | BOOLEAN | IC版で表示するか。 |
| `lp_visible` | BOOLEAN | LP版で表示するか。 |
| `data_requirements` | JSONB | 必須観測フィールドIDと優先ソース（例：`{"required":["revenue_arr","ltv_cac_ratio"],"optional":["product_milestones"]}`）。 |
| `source_priority` | JSONB | `{"revenue_arr":["CONF","ANL","PUB"]}` など。 |
| `render_type` | TEXT | `narrative` / `table` / `chart`。 |
| `narrative_template_id` | TEXT | テキスト生成用テンプレID。 |
| `pending_policy` | JSONB | 欠損時の表示ルール（例：`{"type":"inline_note","text":"情報取得中（予定：{due_date}）"}`）。 |
| `lp_masking_profile` | TEXT | LP向け丸め設定ID。 |
| `footer_notes_policy` | JSONB | 脚注生成ルール（source_tag, As-of, EvidenceID 等）。 |
| `updated_at` | TIMESTAMPTZ | 更新日時。 |

#### `narrative_templates`
| カラム | 型 | 説明 |
| --- | --- | --- |
| `narrative_template_id` | TEXT | 例：`exec_summary_v1`。 |
| `language` | TEXT | `ja-JP` 等。 |
| `body` | TEXT | 変数プレースホルダを含むテンプレ。 |
| `placeholders` | JSONB | 使用する観測値キー一覧とフォーマット定義。 |
| `fallback_policy` | JSONB | 欠損時に入れる文。 |

### 4.3 セクション定義サンプル
```json
{
  "section_id": "exec_summary",
  "order_index": 10,
  "title": "投資推奨サマリー",
  "purpose": "投資判断の結論と主要根拠を1ページで提示する。",
  "required": true,
  "ic_visible": true,
  "lp_visible": true,
  "data_requirements": {
    "required": ["thesis.statement", "deal.investment_amount", "deal.ownership_range", "valuation.pre_money_range"],
    "optional": ["kpi.revenue_arr_range", "kpi.ndr_range"]
  },
  "source_priority": {
    "deal.investment_amount": ["CONF"],
    "kpi.revenue_arr_range": ["ANL", "CONF", "PUB"]
  },
  "render_type": "narrative",
  "narrative_template_id": "exec_summary_v1",
  "pending_policy": {
    "type": "inline_note",
    "text": "情報取得中：{required_source_tag} からの更新待ち"
  },
  "lp_masking_profile": "lp_summary_range",
  "footer_notes_policy": {
    "include_source_tag": true,
    "include_as_of": true,
    "include_evidence": true
  }
}
```

### 4.4 欠損表示ポリシー案
- `value_status='pending'` → テンプレ内では空欄＋脚注「（取得中）」を自動挿入。
- `gap` が開いている場合、セクション冒頭に `前回比の変更点: 情報取得待ち項目あり（詳細: ギャップID #123）` を表示。
- IC版では `pending` をグレーアウト、LP版では該当行を丸ごと非表示＋脚注「LP開示レベル未達」。

### 4.5 レポート生成時のデータマッピング
1. `report_template` と `report_sections` をロード。
2. 各セクションの `data_requirements.required` を観測テーブルで解決。未解決はギャップ参照。
3. `narrative_template` に観測値をバインド。必要に応じて計算値（ANL）を再実行。
4. `lp_masking_profile` を適用し、LP版ではレンジ化／匿名化を自動適用。
5. `footer_notes_policy` に従い脚注を生成（Evidence URI、As-of、Disclosureを列挙）。

---

## 5. 今後のTODO（実装準備）
1. **フィールド辞書拡張**：観測テーブルの `field_id` を `metrics_dict_v0_1.json` + Narrative用ID（例：`thesis.statement`）として整理。
2. **ギャップテンプレの初期データ作成**：Step 4で使用した pending CSV テンプレをJSON Schema化し、`expected_format` の妥当性チェックを自動化。
3. **レポートテンプレ v0.1 作成**：`投資委員会資料フォーマット_完全版.md` をベースに、IC/LP両方の `report_sections` JSON を下書き。
4. **バリデーションロジック**：`confidence < 0.7` かつ `source_tag='EXT'` の観測値が入った際に自動でギャップ生成するルールを実装。
5. **監査ログ整備**：観測テーブル／ギャップテーブル双方で `history` テーブルの構造とAPIレスポンス形式を定義。

--- 

必要に応じて、本草案を Notion/Sheets 用のスキーマ表や JSON Schema として再フォーマットできます。修正要望があれば逐次反映します。

---

## 6. 観測フィールド辞書（ドラフト）

### 6.1 指標系フィールド（Step 1 指標辞書との突合）
| field_id | display_name | section | value_type | unit/period | 優先SourceTag | 補足 |
| --- | --- | --- | --- | --- | --- | --- |
| `revenue_mrr` | 月次リカーリング売上 (MRR) | kpi | number | USD / monthly | CONF > ANL > PUB | 指標辞書IDをそのまま使用 |
| `revenue_arr` | 年次リカーリング売上 (ARR) | kpi | number | USD / annual | CONF > ANL > PUB | ANL計算で補完 |
| `arpa_monthly` | ARPA（月次） | kpi | number | USD / monthly | ANL > CONF > EXT | `revenue_mrr`÷有料アカウント数 |
| `logo_churn_rate_monthly` | ロゴチャーン率（月次） | kpi | number | % / monthly | CONF > INT | 0%近傍はキャップ処理 |
| `gross_revenue_churn_rate_monthly` | グロスレベニューチャーン率（月次） | kpi | number | % / monthly | CONF > INT | |
| `net_dollar_retention_annual` | ネット・ダラー・リテンション（年率） | kpi | number | % / annual | CONF > INT > ANL | |
| `ltv_gross_profit_simple` | LTV（粗利ベース） | kpi | number | USD / lifetime | ANL | `value_json.assumptions` に粗利率等 |
| `cac_blended` | CAC（ブレンデッド） | kpi | number | USD / snapshot | CONF > ANL | |
| `ltv_cac_ratio` | LTV/CAC比 | kpi | number | ratio | ANL | |
| `payback_period_months` | 回収期間（月数） | kpi | number | months / snapshot | ANL | |

> ※ Step 1 の辞書に追加された指標は順次この表に追記。`unit` `period` `rules` は辞書側を参照して同期。

### 6.2 KPI補助フィールド
| field_id | 説明 | 備考 |
| --- | --- | --- |
| `paid_accounts` | 有料アカウント数 | `entity_type=company` |
| `paid_users` | 有料ユーザー数 | B2C向け想定 |
| `gross_margin_pct` | 粗利率 | CONF/INT優先 |
| `gross_margin_breakdown` | 粗利内訳 | `value_json` で項目別比率を保持 |
| `cohort_retention_monthly` | コホート残存率表 | CSVテンプレ連携 (`value_json.table`) |
| `expansion_mrr` / `churned_mrr` / `contraction_mrr` | MRR内訳 | NDR計算に使用 |
| `new_paid_accounts` | 新規有料アカウント数 | CAC計算に使用 |
| `s_and_m_expense` | Sales & Marketing費用 | 期間整合注意 |

### 6.3 ナラティブ系フィールド命名規則
- フォーマット：`{セクション}.{サブトピック}[.粒度]`
    - 例：`thesis.statement`, `market.size_tam`, `competition.landscape_summary`
- セクションIDはレポートテンプレの `report_sections.section_id` と揃える。
- 同一セクション内で複数段落がある場合は `order_index` を `value_json.order` で管理、またはフィールド末尾に `_{n}` を付与。
- LPマスキング対象（ディール条件等）は `deal_terms.*` にまとめ、マスキングプロファイルで一括制御。

### 6.4 ナラティブ系フィールド一覧（初稿）
| field_id | section | 想定内容 | value_type | 優先SourceTag |
| --- | --- | --- | --- | --- |
| `thesis.statement` | exec_summary | 投資の結論（1–2行） | string | ANL > INT |
| `thesis.reason_1` / `_2` / `_3` | exec_summary | 投資理由トップ3 | string | ANL |
| `thesis.key_metrics` | exec_summary | 主要KPIレンジ | json(range) | ANL |
| `business.problem_summary` | business | 課題（誰が何に困っているか） | string | PUB > INT |
| `business.solution_summary` | business | プロダクト概要と解決策 | string | PUB |
| `business.model_summary` | business | 収益モデル・価格帯 | string | ANL > PUB |
| `product.overview` | product | プロダクト機能・ユースケース | string | PUB |
| `product.roadmap_key` | product | 主要ロードマップ項目 | json(list) | INT > CONF |
| `market.size_tam` / `_sam` / `_som` | market | TAM/SAM/SOM算定結果 | json(number) | ANL |
| `market.why_now` | market | マクロ・規制・技術トレンド | string | PUB > ANL |
| `competition.landscape_summary` | competition | 競合マップ要約 | string | ANL |
| `competition.key_differentiators` | competition | 差別化ポイント | json(list) | ANL > INT |
| `team.overview` | team | 経営陣サマリー | string | PUB > CONF |
| `team.gap_and_plan` | team | チームのギャップと採用計画 | string | INT |
| `deal.investment_amount` | deal_terms | 投資額（IC向け実数） | number | CONF |
| `deal.investment_amount_range` | deal_terms | 投資額レンジ（LP向け） | range | ANL |
| `deal.ownership` / `deal.ownership_range` | deal_terms | 持分（実数/レンジ） | number/range | CONF / ANL |
| `deal.valuation_pre` / `_range` | valuation | Pre Money評価（実数/レンジ） | number/range | CONF / ANL |
| `deal.key_terms_summary` | deal_terms | 清算優先・反希薄化など要約 | string | CONF |
| `financials.summary` | financials | 直近PL/CF要約 | string | CONF |
| `financials.forecast_highlights` | financials | 予測ハイライト・前提 | string | CONF > ANL |
| `risk.top_list` | risk | リスク要約（Top3–5） | json(list) | ANL |
| `risk.mitigations` | risk | 対応策 | json(list) | ANL > INT |
| `value_creation.plan_summary` | value_creation | バリューアップ計画 | string | ANL |
| `value_creation.next_milestones` | value_creation | 今後のマイルストーン | json(list) | CONF > INT |
| `appendix.key_questions` | appendix | 想定Q&A | json(list) | ANL |

### 6.5 フィールドIDメタデータ格納案
- `/config/field_dictionary_v0_1.json` として整理し、観測テーブル投入時に参照。
- JSON構造例：
```json
{
  "revenue_arr": {
    "category": "kpi",
    "source_priority": ["CONF", "ANL", "PUB"],
    "masking_profile": "numeric_usd"
  },
  "thesis.statement": {
    "category": "exec_summary",
    "value_type": "string",
    "source_priority": ["ANL", "INT"],
    "masking_profile": "narrative_default"
  }
}
```

### 6.6 今後の拡張ポイント
- セクター固有指標（例：Fintech向け `tpv`, Marketplace向け `gmv`）を `sector_specific` として追加。
- Timeline型フィールド（例：`product.milestones_timeline`）は `value_json.timeline` 構造で統一。
- LP向けマスキングに合わせて `*_range` フィールドを生成するユーティリティを実装予定（実数フィールドと紐付け）。
