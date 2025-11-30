了解です。**Step 4：ダミー案件で一巡テスト**を、実務でそのまま回せる形で提示します。  
（前提：_Gemini / GPT（OpenAI API） / MCP_ のみ使用。実データ接続はせず、ダミー値でパイプラインを検証します。）

---

## 0) 目的（この一巡テストで確認したいこと）

- PUB/EXT → **観測テーブル**作成 → **ギャップ検出** → CONF（半自動） → **ANL計算** → **IC/LPドキュ出力** の流れが**自動で通る**こと
    
- `pending`の穴が残っても**壊れない**こと（INTで後充填できる）
    
- LPマスキング（Step 3）の**規則が意図通り**に効くこと
    

---

## 1) ダミー案件の定義

**案件名**：NimbusFlow, Inc.（B2B SaaS：ワークフロー自動化）  
**地域**：NA（US）／**モデル**：subscription／**セクター**：SaaS（DevTools系）  
**As-of**：2025-09-30

---

## 2) ダミー観測データ（PUB/EXT, CONF, INT, ANL）

> 形式は Step 1 の**観測テーブル**スキーマ準拠。Evidence はダミーURIで記載。

```json
[
  {
    "entity_id": "company:nimbusflow",
    "section": "business",
    "field": "product_overview",
    "value": "中堅〜大企業向けワークフロー自動化SaaS。主要ユースケース：承認フロー、監査ログ、SaaS間連携。",
    "unit": "text",
    "source_tag": "PUB",
    "evidence": "dummy://pub/website",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 0.9
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "revenue_arr",
    "value": 8000000,
    "unit": "USD",
    "source_tag": "PUB",
    "evidence": "dummy://pub/pr-2025-07",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 0.7
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "revenue_mrr",
    "value": 666666.67,
    "unit": "USD",
    "source_tag": "ANL",
    "evidence": "calc: arr/12",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 1.0
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "paid_accounts",
    "value": 1200,
    "unit": "count",
    "source_tag": "EXT",
    "evidence": "dummy://ext/g2-linkedin-mix",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 0.6
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "arpa_monthly",
    "value": 555.56,
    "unit": "USD",
    "source_tag": "ANL",
    "evidence": "calc: mrr/paid_accounts",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 1.0
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "gross_margin_pct",
    "value": 78.0,
    "unit": "%",
    "source_tag": "INT",
    "evidence": "dummy://int/cfo-2025-10-01",
    "as_of": "2025-09-30",
    "disclosure": "LP+NDA",
    "confidence": 0.8
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "logo_churn_rate_monthly",
    "value": 1.5,
    "unit": "%",
    "source_tag": "INT",
    "evidence": "dummy://int/cfo-2025-10-01",
    "as_of": "2025-09-30",
    "disclosure": "LP+NDA",
    "confidence": 0.7
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "net_dollar_retention_annual",
    "value": 120.0,
    "unit": "%",
    "source_tag": "INT",
    "evidence": "dummy://int/cro-2025-10-01",
    "as_of": "2025-09-30",
    "disclosure": "LP+NDA",
    "confidence": 0.6
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "s_and_m_expense_monthly",
    "value": 1000000,
    "unit": "USD",
    "source_tag": "CONF",
    "evidence": "dummy://conf/pnl-2025-09",
    "as_of": "2025-09-30",
    "disclosure": "IC",
    "confidence": 0.9,
    "sensitivity": "Pricing"
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "kpi",
    "field": "new_paid_accounts_monthly",
    "value": 200,
    "unit": "count",
    "source_tag": "INT",
    "evidence": "dummy://int/cro-2025-10-01",
    "as_of": "2025-09-30",
    "disclosure": "LP+NDA",
    "confidence": 0.8
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "unit_economics",
    "field": "cac_blended",
    "value": 5000,
    "unit": "USD",
    "source_tag": "ANL",
    "evidence": "calc: s&m/new_paid",
    "as_of": "2025-09-30",
    "disclosure": "LP+NDA",
    "confidence": 1.0
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "unit_economics",
    "field": "ltv_gross_profit_simple",
    "value": 28888.89,
    "unit": "USD",
    "source_tag": "ANL",
    "evidence": "calc: arpa*gm*(1/churn)",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 1.0
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "unit_economics",
    "field": "ltv_cac_ratio",
    "value": 5.78,
    "unit": "ratio",
    "source_tag": "ANL",
    "evidence": "calc: ltv/cac",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 1.0
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "unit_economics",
    "field": "payback_period_months",
    "value": 11.54,
    "unit": "months",
    "source_tag": "ANL",
    "evidence": "calc: cac/(arpa*gm)",
    "as_of": "2025-09-30",
    "disclosure": "LP",
    "confidence": 1.0
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "deal",
    "field": "pre_money_equity_value",
    "value": 86400000,
    "unit": "USD",
    "source_tag": "ANL",
    "evidence": "EV/ARR_median*ARR",
    "as_of": "2025-09-30",
    "disclosure": "IC",
    "confidence": 0.7,
    "notes": "ネットデット≈0仮定"
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "deal",
    "field": "round_size",
    "value": 10000000,
    "unit": "USD",
    "source_tag": "CONF",
    "evidence": "dummy://conf/term-sheet",
    "as_of": "2025-10-05",
    "disclosure": "IC",
    "confidence": 0.9,
    "sensitivity": "Valuation_Precise"
  },
  {
    "entity_id": "company:nimbusflow",
    "section": "deal",
    "field": "fund_investment_amount",
    "value": 5000000,
    "unit": "USD",
    "source_tag": "CONF",
    "evidence": "dummy://conf/ssa",
    "as_of": "2025-10-05",
    "disclosure": "IC",
    "confidence": 0.9
  }
]
```

---

## 3) ギャップ検出（自動）→ INT/CONF To-Do

```json
[
  {
    "field": "kpi.gross_margin_pct_breakdown",
    "why": "INT必要（コスト内訳：ホスティング/サポート/決済手数料）",
    "suggested_ask": "粗利率78%の構成明細（%と金額）を提示ください。",
    "owner": "CFO",
    "priority": "high"
  },
  {
    "field": "kpi.cohort_retention_monthly",
    "why": "INT必要（LTVの裏取り）",
    "suggested_ask": "過去12ヶ月のコホート残存率（分母定義と表）を提示ください。",
    "owner": "CFO",
    "priority": "high"
  },
  {
    "field": "deal.key_terms",
    "why": "CONF必要（条項整備）",
    "suggested_ask": "清算優先・反希薄化・情報権・ボードの条項要約を提出ください（テンプレに記入）。",
    "owner": "Legal/BD",
    "priority": "high"
  }
]
```

> これらが `pending` のままでも、ANLとドキュ生成は**実行可**（不足セルは注記付きで穴のまま）。

---

## 4) ANL計算（検証用の手計算も併記）

- **MRR**：8,000,000 ÷ 12 ＝ **666,666.67**
    
- **ARPA**：666,666.67 ÷ 1,200 ＝ **555.56**
    
- **平均継続月数**：1 ÷ 0.015 ＝ **66.6667** ヶ月
    
- **LTV（粗利基準）**：  
    555.56 × 0.78 ＝ **433.33**（月次粗利）  
    433.33 × 66.6667 ＝ **28,888.9 USD**
    
- **CAC**：1,000,000 ÷ 200 ＝ **5,000 USD**
    
- **LTV/CAC**：28,888.9 ÷ 5,000 ＝ **5.78**
    
- **回収期間**：5,000 ÷ 433.33 ＝ **11.54 ヶ月**
    

**バリュエーション（Step 2のダミー・マルチプル）**

- EV/ARR：P25=8.5×／Median=10.8×／P75=13.2×（n=24）
    
- **EVレンジ**：
    
    - P25：8.5 × 8.0M ＝ **68.0M**
        
    - Median：10.8 × 8.0M ＝ **86.4M**
        
    - P75：13.2 × 8.0M ＝ **105.6M**
        
- **ディール整合**：Pre=86.4M（仮）／Round=10M → **Post=96.4M**
    
- **当ファンド出資**：5.0M → **持分 = 5.0 ÷ 96.4 = 0.051865… ≒ 5.19%**
    

---

## 5) ドキュメント生成（サンプル出力）

### 5-1. **IC版（要旨1ページ）**

**投資推奨（結論）**

- 当ファンドは **5.0M USD** の出資で **5.19%** の取得を実行。
    
- 前提EVは **EV/ARR=10.8×** の**中央値**に基づく **86.4M USD**（ARR=8.0M, as-of 2025-09-30）。
    

**なぜ投資か（Thesis）**

- 問題：大企業の承認・監査フローの非効率。
    
- 解決：ノーコード連携＋監査証跡の一体化（導入阻害が小さい）。
    
- タイミング：生成AI普及で自動化需要増、コンプラ要請強化。
    
- 経済性：**LTV/CAC=5.78**、**回収11.5ヶ月**。**NDR=120%**。
    
- チーム：大手SaaS出身の創業陣、セールス/CS採用の目処あり。
    

**主要KPI（as-of 2025-09-30）**

- ARR **8.0M**、YoY **+55%**（EXT/PUBの推定、CONFで検証中）
    
- 有料アカウント **1,200**、ARPA **$556**、粗利 **78%**
    
- 月次ロゴチャーン **1.5%**、NDR **120%**
    

**ディール要点**

- 前提評価（Pre）：**86.4M USD**（EV=Equity仮定）
    
- **Round：10.0M USD**（Post：96.4M）
    
- 条項（要約）：清算優先 **1x 非参加型**、反希薄化 **加重平均**、情報権/ボード **有**（CONF要約添付）
    

**リスク & 対策**

- ① チャーン上振れ → コホート施策強化、CS採用（Q4）
    
- ② 競合の同質化 → 監査ログ/API連携でMoat強化
    
- ③ GTM費用の先行 → パイプライン精度の週次レビュー
    

**脚注**

- 出典：dummy://pub/…／dummy://conf/…（観測ID参照）
    
- EVは **ネットデット≈0** 仮定。原票n=24、Winsorize=2.5%。
    

---

### 5-2. **LP版（マスキング適用）**

**投資推奨（結論）**

- 出資額：**5–7M USD**（LP表示レンジ）
    
- 取得持分：**5–6%**
    
- 参考評価：**Pre 80–90M USD（2025年Q3時点）**
    

**なぜ投資か（要旨）**

- 非効率な承認・監査フローを**低侵襲で自動化**。
    
- **LTV/CAC ≈ 5–6倍**、**回収 ≈ 10–12ヶ月** の水準。
    
- 主要顧客：**上場・製造業、通信大手**（匿名化）
    

**主要KPI（レンジ表示）**

- ARR **7–9M**、ARPA **$500–600**、粗利 **70–80%**
    
- 月次ロゴチャーン **1–2%**、NDR **110–125%**
    

**ディール条項（標準語彙）**

- 清算優先：**1x 非参加型（有）**／反希薄化：**加重平均（有）**
    
- 情報権/ボード：**有**（詳細はNDA下）
    

**脚注**

- 本資料は**マスキングポリシー v0.1**に基づき丸め・匿名化済。As-ofと出典は脚注ID参照。
    

---

## 6) 反証ログ（例）

|主張|反証|影響|対応/期限|所有者|
|---|---|---|---|---|
|「ARR=8.5M（PR）」|CONFの月次予実では **8.0M**|-6%|PR表現の更新依頼（10/20）|広報|
|「粗利80%」|INTで **78%**|軽微|KPI定義表を更新（10/18）|CFO|

---

## 7) 品質ゲート（自動チェックの結果）

- 出典付与率：**100%**（数値・主張すべてに Evidence/As-of あり）
    
- 単位・分母・期間：**OK**（MRR/ARRの前提一致）
    
- EXT推定：注意書き自動付与（confidence<0.7）
    
- マスキング：LP版の**Valuation/Ownership/Customer/Pricing**に変換適用済
    
- `pending`：**3件**（粗利内訳、コホート残存、条項要約）
    

---

## 8) 一巡テストの実行手順（Runbook）

> すべて **MCP経由**で実行。LLMは GPT/Gemini いずれも可（構造化はGPT推奨）。

1. **設定を投入**
    
    - `metrics_dict_v0_1.json`（Step 1）
        
    - `multiples_schema_v0_1.json`, `taxonomy_v0_1.json`（Step 2）
        
    - `lp_masking_policy_v0_1.json`（Step 3）
        
2. **PUB/EXT 収集 → 観測テーブル作成**
    
    - `mcp.execute("web.search+fetch", {...})` の結果を **PUB収集Bot** に渡し、辞書IDへマップ（推測禁止）。
        
    - EXTはダミーAPI応答を**EXT収集Bot**で正規化（`confidence` 低め設定）。
        
3. **正規化 & ギャップ検出**
    
    - **正規化Bot**：同一指標の優先度マージ（`CONF > INT > PUB > EXT`）。
        
    - **ギャップ検出Bot**：テンプレ必須項目の欠落→`pending_list` 生成。
        
4. **CONFインジェスト（半自動）**
    
    - ダミーTerm Sheet/PLを投入→**CONFインジェスタ**が項目抽出→**ワンクリック承認**。
        
5. **ANL計算**
    
    - LTV/CAC/回収・TAM・EV/ARRレンジを**ANLエンジン**で算出（欠測は`pending`）。
        
6. **資料ビルダー**
    
    - **IC版**と**LP版**をMarkdownで自動生成（差分サマリ・脚注・注記を付与）。
        

---

## 9) 受け入れ基準（このテストが「合格」になる条件）

- IC/LP の両ドキュメントが**自動生成**され、**脚注・As-of**・**差分サマリ**が付く
    
- `pending` が残っていても**壊れず**に数式/文章が通る（不足は注記）
    
- **LPマスキング**が表の通り適用される（Valuation/Ownership/Customer/Terms 等）
    
- 原票ID・Winsorize・n などの**透明性メタ**が脚注に出力される
    

---

## 10) 次の一手（このテスト結果を踏まえて）

- `pending` 3件を INT/CONF で回収 → 自動再計算（LTV/条項の確度↑）
    
- マルチプル・ストアの n を増やす（SaaS以外、Marketplace/Fintechもダミー拡充）
    
- LP版の丸め幅・バケットの**社内基準**に合わせた微調整
    

---

必要であれば、上記の **観測テーブルJSON／ギャップJSON／IC/LPドラフト文面** をそのまま Notion/GDrive に置ける形で再フォーマットします。  
次は **INT質問票テンプレ（役職別）** と **CONF抽出の承認UIワイヤー** を用意し、`pending` を埋める小ループのテストに進めます。