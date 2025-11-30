了解しました。  
ここでは**「一歩ずつ」**を徹底するために、まずは **Step 1：指標定義辞書（ARR/ARPU/Churn/NDR/LTV/CAC…）** を“実務でそのまま使える形”で提示します。  
これがMVPの土台です。承認後に Step 2（セクター別マルチプルの枠組み）、Step 3（LP向けマスキング規則）、Step 4（ダミー案件で一巡テスト）へ進みます。

---

## 全体工程（再掲・確認用）

1. **Step 1**：用語・指標の定義辞書を確定（本回答で提示）
    
2. **Step 2**：セクター別マルチプルの“データ構造と収集ルール”を設計（値は後からPUB/EXTで充填）
    
3. **Step 3**：LP開示版の**マスキング規則**（匿名化/レンジ化/条項の標準語彙）を決定
    
4. **Step 4**：ダミー案件で **PUB/EXT→ANL→ドキュ生成** を一巡（差分サマリ/品質ゲート検証）
    

> 以降は、MCP＋Gemini/GPTに組み込むだけで自動運転に載せられます。

---

# Step 1：指標定義辞書（実務版 v0.1）

### 1-1. 目的

- **定義ブレをゼロ**にし、抽出・計算・文書化を同じ辞書で駆動（Single Source of Truth）。
    
- MCP経由で収集した **PUB/EXT/CONF/INT** をこの辞書に沿って正規化。
    
- ANL（分析計算）は辞書の**式・前提**を直接参照して再現可能に。
    

---

### 1-2. 辞書のスキーマ（共通）

各メトリクスは次のフィールドを持ちます。

```
id                一意キー（英字スネークケース）
display_name      表示名（日本語）
definition        定義（日本語で厳密に）
formula           数式（擬似式も可／必要に応じて注記）
inputs[]          参照入力（id参照・必須/任意・単位/期間の前提）
period            基準期間（monthly / quarterly / annual / cohort）
unit              単位（USD, %, count など）
rules             検証ルール（分母定義・除外項目・境界値等）
notes             実務上の注意（よくある落とし穴）
synonyms[]        同義語（NRR=Net Dollar Retention 等）
examples[]        算定例（任意／将来テストで拡充）
```

---

### 1-3. コア指標（SaaS/一般スタートアップ共通）

> ※数式は **月次基準**を基本に表記。年次が必要な場合は「×12」等で変換。  
> ※「分母」「期間」を常に明記する運用をルール化。

#### (A) 収益系

- **ARR（Annual Recurring Revenue）**
    
    - `id`: `revenue_arr`
        
    - `definition`: リカーリング売上の年額換算。ワンタイム/プロフェッショナルサービスは除外。
        
    - `formula`: `ARR = MRR × 12`
        
    - `inputs`: `mrr (monthly, USD)`
        
    - `unit`: `USD`
        
    - `rules`: 使用量課金は**直近3ヶ月平均MRR**で近似可（注意書き必須）。
        
    - `notes`: 前払い年契の認識は**月割り**でMRRに反映してから計算。
        
- **MRR（Monthly Recurring Revenue）**
    
    - `id`: `revenue_mrr`
        
    - `definition`: 月次リカーリング売上。ワンタイムは除外。
        
    - `formula`: `Σ(各契約の月額リカーリング)`
        
    - `unit`: `USD`
        
    - `rules`: 通貨は統一、複数通貨は当月平均レート換算。
        
- **ARPA（Average Revenue per Account, monthly）**
    
    - `id`: `arpa_monthly`
        
    - `definition`: 有料アカウント平均月次売上。
        
    - `formula`: `ARPA = MRR / 有料アカウント数`
        
    - `unit`: `USD`
        
    - `rules`: 有料基準（トライアル/無料枠は分母に含めない）。
        
- **ARPU（Average Revenue per User, monthly）**
    
    - `id`: `arpu_monthly`
        
    - `definition`: 有料ユーザー平均月次売上（B2C中心）。
        
    - `formula`: `ARPU = MRR / 有料ユーザー数`
        
- **粗利率（Gross Margin %）**
    
    - `id`: `gross_margin_pct`
        
    - `definition`: 売上総利益率。`(売上−売上原価)/売上`。
        
    - `unit`: `%`
        
    - `rules`: 原価の内訳（ホスティング/サポート外注等）を固定ルール化。
        

#### (B) リテンション/解約

- **ロゴチャーン率（月次）**
    
    - `id`: `logo_churn_rate_monthly`
        
    - `definition`: 月間で解約した**顧客数**の率。
        
    - `formula`: `解約顧客数 / 期首顧客数`
        
    - `unit`: `%`
        
    - `rules`: ダウングレードは含めない（解約=契約終了）。
        
- **グロス収益チャーン（月次）**
    
    - `id`: `gross_revenue_churn_rate_monthly`
        
    - `definition`: 期中の**減収（解約+縮小）**が期首MRRに占める割合。
        
    - `formula`: `(Churned_MRR + Contraction_MRR) / 期首MRR`
        
- **ネット・ダラー・リテンション（年率, NDR/NRR）**
    
    - `id`: `net_dollar_retention_annual`
        
    - `definition`: 既存顧客の**1年後のMRR維持・拡大率**。
        
    - `formula`: `((期首MRR + Expansion − Contraction − Churn) / 期首MRR) × 100（%）`, 期間=12ヶ月
        
    - `synonyms`: `["NRR","Net Revenue Retention","Net Dollar Retention"]`
        
    - `rules`: 新規獲得は含めない。
        

#### (C) ユニットエコノミクス

- **LTV（粗利ベース・単純式, 月次→年換算可）**
    
    - `id`: `ltv_gross_profit_simple`
        
    - `definition`: 顧客1社あたりの生涯粗利益（単純式）。
        
    - `formula`: `LTV = ARPA × 粗利率 × 平均継続月数`, `平均継続月数 ≒ 1 / ロゴチャーン（月次）`
        
    - `unit`: `USD`
        
    - `rules`: チャーンが0に近い場合は**上限月数キャップ**を設ける（例：60ヶ月）。
        
- **CAC（顧客獲得コスト, Blended）**
    
    - `id`: `cac_blended`
        
    - `definition`: 新規顧客1社あたりの獲得コスト（同期間のS&M費/新規有料顧客数）。
        
    - `formula`: `CAC = 当月(または四半期)のS&M費 / 新規有料顧客数`
        
    - `unit`: `USD`
        
    - `rules`: 期間整合（支出と成果の計上ズレに注意／四半期で見る場合は移動平均推奨）。
        
- **LTV/CAC 比**
    
    - `id`: `ltv_cac_ratio`
        
    - `formula`: `LTV / CAC`
        
    - `rules`: 目安は**3以上**を良好の基準とするが業態で変動。
        
- **回収期間（月）**
    
    - `id`: `payback_period_months`
        
    - `formula`: `CAC / (ARPA × 粗利率)`
        
    - `rules`: 12ヶ月以内を良好の目安（SaaS標準目線）。
        

#### (D) 効率性（任意だが有用）

- **Magic Number（SaaS成長効率）**
    
    - `id`: `magic_number`
        
    - `definition`: 前期→当期のARR増分がS&M費に対してどれだけ効いたか。
        
    - `formula`: `((当期MRR−前期MRR) × 12) / 前期S&M費`
        
    - `rules`: 0.75〜1.0以上が目安（解釈は業態差あり）。
        
- **Rule of 40**
    
    - `id`: `rule_of_40`
        
    - `definition`: 成長率（%）＋粗利率（%）の合計。40%以上が優秀の目安。
        
    - `formula`: `YoY売上成長率(%) + 粗利率(%)`
        

---

### 1-4. 依存入力（共通ID）

- `mrr`, `starting_mrr`, `new_mrr`, `expansion_mrr`, `contraction_mrr`, `churned_mrr`
    
- `paid_accounts`, `paid_users`, `s_and_m_expense`, `customers_start_period`, `customers_churned_period`
    
- `gross_margin_pct`, `yoy_revenue_growth_pct`
    

> これらは**観測テーブル**に `section:"kpi"` として格納。期間・分母・通貨を必須メタにします。

---

### 1-5. バリデーション・運用ルール（QC）

- **必須メタ**：各観測値に `as_of`（日付）・`unit`・`period`・`evidence`（URL/ファイル）が必須。
    
- **期間整合**：分子と分母の期間が一致していなければ**警告**。例：`CAC`と`新規有料顧客`は同期間。
    
- **除外の明示**：ワンタイム収益は**MRR/ARRから除外**。使用量課金の近似は**注意書き**を自動付与。
    
- **上限・下限**：チャーン0%近傍は `平均継続月数` に**上限キャップ**（例：60ヶ月）を適用。
    
- **同義語正規化**：`NRR`/`NDR` は `net_dollar_retention_annual` に正規化。
    
- **優先度マージ**：値の衝突時は **CONF > INT > PUB > EXT** の順で採用し、棄却値は反証ログへ。
    

---

### 1-6. 同義語・取り込みマッピング例

```
"synonym_map": {
  "nrr": "net_dollar_retention_annual",
  "net revenue retention": "net_dollar_retention_annual",
  "net dollar retention": "net_dollar_retention_annual",
  "logo churn": "logo_churn_rate_monthly",
  "gross revenue churn": "gross_revenue_churn_rate_monthly",
  "arpu": "arpu_monthly",
  "arpa": "arpa_monthly"
}
```

---

### 1-7. JSON（投入用ミニ辞書・抜粋）

```json
{
  "version": "0.1",
  "metrics": [
    {
      "id": "revenue_mrr",
      "display_name": "MRR（月次リカーリング売上）",
      "definition": "月次のリカーリング売上。ワンタイム収益は除外する。",
      "formula": "Σ(各契約の月額リカーリング)",
      "inputs": [],
      "period": "monthly",
      "unit": "USD",
      "rules": ["通貨は統一", "複数通貨は平均レートで換算"],
      "synonyms": ["mrr"]
    },
    {
      "id": "revenue_arr",
      "display_name": "ARR（年換算リカーリング）",
      "definition": "リカーリング売上の年額換算（ワンタイムは除外）。",
      "formula": "ARR = MRR × 12",
      "inputs": ["revenue_mrr"],
      "period": "annualized",
      "unit": "USD",
      "rules": ["使用量課金は直近3ヶ月平均MRRを用いて可"]
    },
    {
      "id": "arpa_monthly",
      "display_name": "ARPA（月額／アカウント）",
      "definition": "有料アカウントの平均月次売上。",
      "formula": "MRR / 有料アカウント数",
      "inputs": ["revenue_mrr", "paid_accounts"],
      "period": "monthly",
      "unit": "USD",
      "rules": ["トライアル/無料は分母に含めない"]
    },
    {
      "id": "logo_churn_rate_monthly",
      "display_name": "ロゴチャーン率（月次）",
      "definition": "月内に解約した顧客数の割合（ダウングレードは含めない）。",
      "formula": "解約顧客数 / 期首顧客数",
      "inputs": ["customers_churned_period", "customers_start_period"],
      "period": "monthly",
      "unit": "%",
      "rules": ["分母は期首顧客数"]
    },
    {
      "id": "gross_revenue_churn_rate_monthly",
      "display_name": "グロス収益チャーン（月次）",
      "definition": "解約+縮小による減収が期首MRRに占める割合。",
      "formula": "(churned_mrr + contraction_mrr) / starting_mrr",
      "inputs": ["churned_mrr", "contraction_mrr", "starting_mrr"],
      "period": "monthly",
      "unit": "%"
    },
    {
      "id": "net_dollar_retention_annual",
      "display_name": "ネット・ダラー・リテンション（年率）",
      "definition": "既存顧客の1年後のMRR維持・拡大率。",
      "formula": "((starting_mrr + expansion_mrr - contraction_mrr - churned_mrr) / starting_mrr) × 100",
      "inputs": ["starting_mrr", "expansion_mrr", "contraction_mrr", "churned_mrr"],
      "period": "annual",
      "unit": "%"
    },
    {
      "id": "ltv_gross_profit_simple",
      "display_name": "LTV（粗利ベース・単純式）",
      "definition": "顧客1社当たりの生涯粗利益（単純式）。",
      "formula": "LTV = ARPA × 粗利率 × 平均継続月数",
      "inputs": ["arpa_monthly", "gross_margin_pct", "logo_churn_rate_monthly"],
      "period": "lifetime",
      "unit": "USD",
      "rules": ["平均継続月数 ≒ 1 / 月次ロゴチャーン", "チャーンが極小の場合は上限キャップ適用"]
    },
    {
      "id": "cac_blended",
      "display_name": "CAC（ブレンデッド）",
      "definition": "新規有料顧客1社を獲得するためのコスト。",
      "formula": "CAC = Sales&Marketing費 / 新規有料顧客数",
      "inputs": ["s_and_m_expense", "new_paid_accounts"],
      "period": "monthly",
      "unit": "USD",
      "rules": ["期間整合が必須（移動平均での補正可）"]
    },
    {
      "id": "ltv_cac_ratio",
      "display_name": "LTV/CAC比",
      "definition": "LTVをCACで割った比率。",
      "formula": "LTV / CAC",
      "inputs": ["ltv_gross_profit_simple", "cac_blended"],
      "period": "snapshot",
      "unit": "ratio"
    },
    {
      "id": "payback_period_months",
      "display_name": "回収期間（月）",
      "definition": "顧客獲得コストを粗利ベースで回収するまでの月数。",
      "formula": "CAC / (ARPA × 粗利率)",
      "inputs": ["cac_blended", "arpa_monthly", "gross_margin_pct"],
      "period": "snapshot",
      "unit": "months"
    }
  ],
  "synonym_map": {
    "nrr": "net_dollar_retention_annual",
    "net revenue retention": "net_dollar_retention_annual",
    "net dollar retention": "net_dollar_retention_annual",
    "logo churn": "logo_churn_rate_monthly",
    "gross revenue churn": "gross_revenue_churn_rate_monthly",
    "arpu": "arpu_monthly",
    "arpa": "arpa_monthly"
  }
}
```

---

### 1-8. 実装ノート（MCP × Gemini/GPT）

- **辞書の配置**：`/config/metrics_dict_v0_1.json`（MCP側から読み取り、LLMにコンテキスト提示）
    
- **抽出プロンプト**（PUB/EXT/CONF/INT共通）
    
    - 「辞書IDにマップできない指標は**出力しない**」
        
    - 数値には必ず `unit/period/as_of/evidence` を付与
        
    - 同義語は `synonym_map` で正規化してから観測テーブルに格納
        
- **ANL計算**：辞書の `formula` を優先。依存値が欠ける場合は **`status: "pending"`** で穴を保持。
    
- **QC**：分母/期間の不整合や、MRRにワンタイムが混入していないかを自動チェック。
    

---

### 1-9. レビュー観点（このStepで確認したいこと）

- 用語・計算式が**現場の運用と一致**しているか
    
- 期間の扱い（すべて月次起点→年換算の運用で良いか）
    
- チャーン0%近傍の取り扱い（上限キャップの既定値：例 60ヶ月）
    
- 使用量課金の近似運用（直近3ヶ月平均で妥当か／業態別の別ルールが必要か）
    

> ※上記は**“確認観点”であり、現時点ではこの案で作業を進められる状態**です。  
> 追加の運用差があれば、辞書の `rules/notes` に追記します。

---

## 次の工程（予告）

**Step 2：セクター別マルチプルの“構造と収集ルール”設計**

- 値そのものは可変性が高いため、MVPでは **データ構造／収集ソース／集計ルール／適用優先** を確定します（数表はPUB/EXT接続後に自動充填）。
    
- 例：`sector → stage → metric (EV/Revenue, EV/GP, EV/EBITDA) → window (TTM/NTM) → region → source → as_of → value_range` の構造。
    

**Step 3：LPマスキング規則**

- 「社名→セグメント」「単価→レンジ」「契約条項→標準語彙（有/無/範囲）」等のルールを**自動適用**できるよう正規表現＋辞書化。
    

**Step 4：ダミー案件で一巡**

- PUB/EXTだけで走る最小ケース→不足は `pending` として穴のまま文書化→IC/LP同時生成→差分サマリ確認。
    

---

必要であれば、この**辞書JSON**を Notion/Google Drive にそのまま置ける形（MCP参照）でお渡しできます。  
このまま Step 2（マルチプル構造）へ進めますが、まずは本ステップの辞書仕様で実務上の差異があれば、こちらで即反映します。

