了解です。**Step 2：セクター別マルチプルの“構造と収集ルール”**を、MVPでそのまま実装できる粒度で提示します。  
（前提：利用するのは _Gemini / GPT（OpenAI API） / MCP 連携のみ_。外部SaaSはAPIが利用可能な範囲に限定）

---

## 0) ゴールとスコープ（再確認）

- **ゴール**：投資委員会資料の「時価総額の妥当性／バリュエーション根拠」において、**セクター別の市場マルチプル**（取引・M&A・ラウンド）を**自動で収集→正規化→適用**し、  
    _対象企業のKPI（ARR/売上/粗利/EBITDA 等）×該当マルチプル_ から **妥当な評価レンジ（P25–P75 & 中央値）** を即時算出する。
    
- **スコープ**：
    
    - **Trading Comps（上場企業の取引マルチプル）**
        
    - **Transaction Comps（M&Aディールのマルチプル）**
        
    - **Round Comps（未上場ラウンドの参考倍率）**
        
    - 対象メトリクス：**EV/Revenue（TTM/NTM）**, **EV/ARR（SaaS）**, **EV/Gross Profit**, **EV/EBITDA**, **P/E** ほか、業態固有（例：Fintech=EV/TPV×Take Rate、Marketplace=EV/Net Revenue 等）
        

---

## 1) データモデル（スキーマ）

### 1-1. 「マルチプル・ストア」レコード構造（共通）

```json
{
  "id": "mult_2025Q3_saas_trading_us_evrevenue_ttm",
  "type": "trading|transaction|round",
  "sector": "SaaS|Marketplace|Fintech|Consumer|Healthcare IT|…",
  "subsector": "B2B SaaS|DevTools|Payments|Lending|…",
  "business_model": "subscription|transaction|ad|hardware+sw|services",
  "stage": "public|seed|series_a|series_b|growth|late",
  "geography": "global|NA|EMEA|APAC|JP",
  "metric": "EV/Revenue|EV/ARR|EV/GrossProfit|EV/EBITDA|P/E|…",
  "window": "TTM|NTM|LTM|CY|FY+1",
  "value_stat": {
    "p25": 0.0,
    "median": 0.0,
    "p75": 0.0
  },
  "n": 0,
  "filters": {
    "revenue_scale": "sub_5m|5_20m|20_50m|50_200m|200m_plus",
    "growth_bucket_yoy": "lt0|0_20|20_50|50_100|gt100",
    "ebitda_margin_bucket": "neg|0_10|10_20|20_plus"
  },
  "currency": "USD",
  "fx_to_usd": 1.0,
  "as_of": "2025-10-13",
  "source": "provider/tool_name",
  "evidence": ["url_or_file_id_1", "url_or_file_id_2"],
  "confidence": 0.0,
  "notes": "methodology|winsorization|exclusions"
}
```

> **ポイント**
> 
> - **統計はP25/Median/P75**（MVPは十分）。のちに加重中央値/分位を拡張可。
>     
> - **フィルタ**で規模・成長・収益性をバケット化し**近似“同質サンプル”**を作る。
>     
> - **currency/fx_to_usd** を必須化し**通貨正規化**。
>     
> - **n（サンプル数）** と **notes（除外ルール）** を必ず保持。
>     

### 1-2. 「原票」スキーマ（集計前の銘柄・ディール単位）

```json
{
  "id": "raw_XXXX",
  "type": "trading|transaction|round",
  "ticker_or_deal_id": "AAPL|deal_abc123|round_xyz",
  "company_name": "Acme Inc.",
  "sector": "SaaS",
  "subsector": "DevTools",
  "business_model": "subscription",
  "geography": "NA",
  "stage": "public|series_b|…",
  "period": "2025Q2",
  "metrics": {
    "ev": 1234567890.0,
    "revenue_ttm": 100000000.0,
    "revenue_ntm": 130000000.0,
    "arr": 85000000.0,
    "gross_profit_ttm": 70000000.0,
    "ebitda_ttm": -5000000.0,
    "pe_ntm": null
  },
  "multiples": {
    "ev_revenue_ttm": 12.3,
    "ev_revenue_ntm": 9.8,
    "ev_arr": 14.1,
    "ev_gross_profit_ttm": 17.5,
    "ev_ebitda_ttm": null,
    "p_e_ntm": null
  },
  "kpis": {
    "yoy_revenue_growth_pct": 55.0,
    "ebitda_margin_pct": -5.0
  },
  "currency": "USD",
  "fx_to_usd": 1.0,
  "as_of": "2025-10-13",
  "source": "provider/tool_name",
  "evidence": ["url_or_file_id"],
  "confidence": 0.0
}
```

> **原票→集計** の順で保持することで、**再集計やフィルタ条件の見直し**が容易。

---

## 2) 収集ルール（MCP経由）

> **方針**：MVPでは「_API・一次資料で取れるもの_ を優先」。取れない場合は `confidence` を下げて注記。  
> MCP 側に以下のツールを用意（命名は例）し、**LLMからは単一関数 `mcp.execute(tool, args)`** で呼ぶ。

### 2-1. Trading Comps（上場銘柄）

- **ソース候補**：財務データAPI（株価・時価総額・有利子負債・現金）、決算PDF/IR（売上・粗利・EBITDA）、コンセンサス（NTM）
    
- **MCPツール例**
    
    - `ext.finance.quotes.get({tickers, as_of})`：株価・時価総額
        
    - `ext.finance.fundamentals.get({tickers, period})`：売上TTM、粗利TTM、EBITDA等
        
    - `web.fetch({url})`：決算PDF取得→Gemini要約で数値抽出（`confidence` と**出典ページ**付与）
        
- **ルール**
    
    - **EV** = 時価総額 + 有利子負債 − 現金同等物（取得できなければ**注記**）。
        
    - **NTM** はコンセンサスがない場合、**直近期成長率で補間**（`confidence` を下げる）。
        
    - **通貨**はすべてUSDに正規化（`fx_to_usd` 必須）。
        
    - **欠損**は原票に `null` で保持し、集計時に除外。
        

### 2-2. Transaction Comps（M&A）

- **ソース候補**：プレスリリース、規制当局提出資料、ニュース（対価と直近期の売上/ARR）
    
- **MCPツール例**
    
    - `web.search({q, recency})` → `web.fetch({url})` → Gemini/GPTで**対価・対象KPI**を抽出
        
- **ルール**
    
    - **対価**は総対価（株式+現金+アーンアウト）を優先。分割不明は**最小対価で記録**し注記。
        
    - KPIが売上かARRかを**明示**（`metric` に反映）。
        
    - 期間がバラつくため、**TTM換算**または**ARR換算**のルールをノートに残す。
        

### 2-3. Round Comps（未上場ラウンド）

- **ソース候補**：Crunchbase等の融資履歴（公開情報）、プレス、企業ブログ
    
- **MCPツール例**
    
    - `ext.crunchbase.search({company})`, `web.search+fetch`（PR）
        
- **ルール**
    
    - プレ/ポストの**評価額**とラウンド種別を抽出。**売上/ARR**が不明なら**倍率計算は保留**。
        
    - 同一セクター・同ステージの**評価額分布**を参考テーブルとして保持（`type:"round"`）。
        

---

## 3) 正規化・集計ルール

### 3-1. セクター/サブセクター/ビジネスモデルのタクソノミー

```json
{
  "sector_map": {
    "SaaS": ["B2B SaaS", "DevTools", "Security", "MarTech", "HRTech"],
    "Marketplace": ["B2B marketplace", "Consumer marketplace"],
    "Fintech": ["Payments", "Lending", "Brokerage", "Infra"],
    "Consumer": ["Subscription", "Ad-supported"],
    "Healthcare IT": ["Provider IT", "Payer IT"]
  },
  "business_model_map": {
    "subscription": ["SaaS", "Consumer Subscription"],
    "transaction": ["Marketplace", "Payments"],
    "ad": ["Ad-supported"],
    "hardware+sw": ["IoT", "Devices"],
    "services": ["Professional Services"]
  }
}
```

> **分類**は**手動オーバーライド可**。自動分類（LLM）→人手確認を推奨（MVPは静的定義＋手修正OK）。

### 3-2. バケット設計（規模・成長・収益性）

- `revenue_scale`：`sub_5m`, `5_20m`, `20_50m`, `50_200m`, `200m_plus`（基準：ARRまたは売上TTM）
    
- `growth_bucket_yoy`：`lt0`, `0_20`, `20_50`, `50_100`, `gt100`
    
- `ebitda_margin_bucket`：`neg`, `0_10`, `10_20`, `20_plus`
    

> **理由**：**同質の近傍比較**を可能にし、倍率の歪みを抑制。

### 3-3. 外れ値処理・再サンプリング

- **外れ値**：上下2.5%を**ウィンズライジング**（Winsorize）
    
- **最小サンプル**：`n >= 8` を閾値（満たない場合は**一段広いバケット**で再抽出）
    
- **再帰的拡張**：`subsector → sector → business_model → global` の順で広げる
    
- **時点**：`as_of` は**四半期末**へ丸め可能（同期化のため）
    

---

## 4) 適用ロジック（どのマルチプルを当てるか）

### 4-1. 階層ルール（MVP）

1. **ビジネスモデル優先**：
    
    - `subscription` → **EV/ARR**, **EV/Revenue**（TTM/NTM）
        
    - `transaction`（marketplace/payments） → **EV/Net Revenue**（=取引総額×Take Rate） or **EV/Revenue**
        
    - `ad` → **EV/Revenue**（粗利率も参照）
        
    - `hardware+sw` → **EV/Gross Profit**, **EV/Revenue**
        
2. **利益赤字**：EBITDAがマイナスの場合は **EV/EBITDA を使わない**。
    
3. **NTMが有効**：コンセンサスNTMが信頼可能なら **NTM優先**、無ければ **TTM/ARR**。
    
4. **同質近傍**：`sector/subsector` 一致 + `scale/growth/margin` 近いバケットの **median** を標準採用。
    
5. **レンジ**：**P25–P75**を評価レンジ、**Median**を中心値。
    
6. **信頼度**：`n` と `confidence` により **Low/Medium/High** のタグ付け。
    

### 4-2. スコアリング（オプション）

```text
score =  w1*(sector_match) 
        + w2*(1 - |log(scale_target) - log(scale_comp)|) 
        + w3*(1 - |growth_diff|/100) 
        + w4*(1 - |margin_diff|/100) 
        + w5*(recency_score) 
        + w6*(source_quality)
```

> MVPでは**階層ルール**で十分。将来は上記スコアで**k近傍重み付け中央値**へ拡張可。

---

## 5) ANL適用フロー（疑似コード）

```pseudo
function build_multiples(target):
  # 1) ターゲットの属性を正規化
  attrs = classify(target)  # sector, subsector, business_model, geography
  buckets = bucketize(target)  # revenue_scale, growth_bucket, ebitda_margin_bucket

  # 2) マルチプル候補を抽出（厳→緩）
  pools = [
    query_store(type="trading", attrs, buckets),
    fallback(query_store, relax="buckets"),
    fallback(query_store, relax="subsector"),
    fallback(query_store, relax="sector"),
    fallback(query_store, relax="business_model"),
    fallback(query_store, relax="global")
  ]

  # 3) 外れ値処理 & 統計
  stats = compute_stats(pools, winsor=2.5, min_n=8)

  # 4) KPIを選定（business_modelに応じてARR/Revenue/GP/EBITDA）
  kpi = choose_kpi(target)  # ARR or Revenue TTM/NTM or GP etc.

  # 5) レンジ算出
  ev_p25   = stats.multiple.p25   * kpi.value
  ev_median= stats.multiple.median* kpi.value
  ev_p75   = stats.multiple.p75   * kpi.value

  return {ev_p25, ev_median, ev_p75, n: stats.n, method: stats.meta}
```

> 併せて **注記**（フィルタ条件・Nの大小・外れ値処理・NTM補間の有無）を出力。

---

## 6) 品質ガード（受け入れ基準）

- **再現性**：集計に使った**原票IDのリスト**と**フィルタ条件**をドキュメント脚注に自動出力。
    
- **サンプル閾値**：`n < 8` の場合は**警告**表示＋**上位階層への自動フォールバック**の履歴を残す。
    
- **外れ値処理**：ウィンズライジングのパラメータ（%）をメタに記録。
    
- **通貨**：`currency`/`fx_to_usd` を必須、未設定は**失敗**（適用不可）。
    
- **バリデーション**：マルチプルが**負値/ゼロ**の原票はデフォルト除外（`notes`に理由記載）。
    

---

## 7) 具体例（ダミー、説明用）

- ターゲット：**B2B SaaS（subscription） / ARR = USD 8M / YoY +55% / EBITDA Margin -10%**
    
- 適用ロジック：`subscription` → **EV/ARR** を主指標、バックアップで **EV/Revenue TTM**
    
- マルチプル・ストア（仮）：
    
    - `EV/ARR`（SaaS/B2B、5–20M ARR、YoY 50–100%、EBITDA neg） → P25=8.5× / **Median=10.8×** / P75=13.2×（n=24）
        
- **結果**：
    
    - EV（P25–P75）= **8.5××8 = 68M** 〜 **13.2××8 = 105.6M**
        
    - 中央値 = **10.8××8 = 86.4M**
        
    - **注記**：TTM/NTM未使用、ARRベース。n=24、Winsorize 2.5%、US/EU混在→USD換算。
        

> ※値はダミー。MVPではこの**計算書式と注記**まで自動生成します。

---

## 8) MCP 実装メモ（役割とプロンプト骨子）

- **MultiplesCollector（LLM）**
    
    - _IN_：`mcp.execute("ext.finance.*"|"web.fetch", args)` の結果
        
    - _OUT_：**原票**（上記スキーマ）
        
    - _ルール_：出典URL・`as_of`・`currency`・`fx_to_usd` を必須。NTM補間時は `confidence<0.5`。
        
- **MultiplesAggregator（LLM）**
    
    - _IN_：原票＋フィルタ条件
        
    - _OUT_：**マルチプル・ストア**（P25/Median/P75, n, notes）
        
    - _ルール_：外れ値Winsorize、サンプル数チェック、注記生成。
        
- **MultiplesSelector（LLM/Rules）**
    
    - _IN_：対象企業属性・KPI（Step 1の辞書IDで）
        
    - _OUT_：適用レンジ（P25–P75・中央値）＋脚注
        
    - _ルール_：階層ルール→フォールバック→注記。
        
- **CompsTableBuilder（LLM）**
    
    - _IN_：原票IDリスト
        
    - _OUT_：ドキュ用の**比較表**（上位10件など）＋脚注（出典/日付）
        

---

## 9) 運用・UIの最低要件

- **手動オーバーライド**：
    
    - セクター/サブセク/ビジネスモデル、フィルタバケット、外れ値除外の**手修正**を許可。
        
- **再集計ボタン**：オーバーライド後、**即時再集計**。
    
- **透明性**：脚注に**原票サマリ（会社名/期間/出典URL）**を標準出力。
    
- **差分管理**：四半期ごとにマルチプル・ストアを**版管理**し、ドキュメント冒頭に**前回比差分**を自動記載。
    

---

## 10) テスト観点（MVP）

- **ハッピーパス**：SaaS×EV/ARR（原票n≥20）でレンジが出る。
    
- **フォールバック**：n<8 → サブセク→セクタ→ビジネスモデル→グローバルで補完。
    
- **欠損**：NTM欠落でもTTM/ARRで評価可。
    
- **通貨**：JPY/EUR含む原票混在→すべてUSD換算で整合。
    
- **ドキュ出力**：P25–P75・中央値・n・注記・原票脚注が揃う。
    

---

### このStepでの“確認ポイント”

1. **タクソノミー**（sector/subsector/business_model）の粒度は妥当か
    
2. **バケット境界**（規模/成長/EBITDAマージン）は運用に合うか
    
3. **最小サンプル閾値**（n=8）と**外れ値処理**（2.5%）の既定値
    
4. **適用優先順**（subscription→EV/ARR、negative EBITDA→EV/EBITDA除外 等）
    
5. **脚注に出す情報の必須項目**（原票ID・出典URL・as_of・外れ値処理・補間記載）
    

---

## 11) 次アクション（Step 3への準備）

- 上記スキーマを `/config/multiples_schema_v0_1.json` として確定。
    
- **セクター/サブセク/ビジネスモデルの辞書**を `/config/taxonomy_v0_1.json` に反映（オーバーライド可）。
    
- MCP側に **`ext.finance.*` / `web.search` / `web.fetch`** を登録（鍵はMCP保管）。
    
- ダミー原票（SaaS 10件、Marketplace 10件）を流し、**マルチプル・ストア生成 → 適用計算 → ドキュ出力**を通す。
    

この内容でMVPの**“バリュエーションの型”**が固まります。  
問題なければ、次は **Step 3：LP開示のマスキング規則** に進み、IC版/LP版の自動出し分けを設計します。