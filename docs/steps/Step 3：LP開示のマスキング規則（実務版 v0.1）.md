了解しました。  
**Step 3：LP開示のマスキング規則（実務版 v0.1）**を、MVP実装にそのまま使える形で提示します。  
（前提：エンジンは _Gemini / GPT（OpenAI API） / MCP 連携のみ_。Step 1の指標辞書・Step 2のマルチプル構造を参照）

---

## 0) ゴールと基本方針

- **ゴール**：LP向け資料で **機微情報を自動マスキング**しつつ、**「なぜ投資したか」をロジカルに再現**できる状態を保つ。
    
- **前提概念**：各データ点（観測テーブルの1行）には、既に  
    `source_tag（PUB/EXT/INT/CONF/ANL） / evidence / as_of / disclosure（IC|LP|LP+NDA|Private）` が付与されています（Step 1）。
    
- **基本原則**：
    
    1. **最小公開**：必要な結論を支える_最低限_の情報のみ表示。
        
    2. **匿名化・一般化**：固有名詞/数値は、**カテゴリ/範囲/丸め**に変換。
        
    3. **可逆ログ**：変換前後と理由を**監査ログ**に残す（IC版に追跡可能）。
        

---

## 1) 開示レベルと機微カテゴリ

### 1-1. 開示レベル（disclosure）

- `IC`：社内専用（マスクなし）
    
- `LP+NDA`：NDA前提でLPに開示可（軽度マスク）
    
- `LP`：NDAなしでLP開示（強マスク）
    
- `Private`：一切表示不可（集計・脚注にも出さない）
    

### 1-2. 機微カテゴリ（sensitivity）— 自動分類＋手動上書き可

```
- PII（個人特定）：氏名・メール・直通電話 等
- Customer_ID（顧客特定）：顧客社名・部署・個別契約番号 等
- Pricing（単価/割引/最低保証）
- Deal_Terms（優先条項の詳細：ラチェット式、特別権利 等）
- Valuation_Precise（プレ/ポストの生数値）
- Ownership_Precise（保有％の生数値）
- Pipeline（パイプライン/勝率/具体社名）
- Security_Secrets（鍵・エンドポイント・脆弱性）
- Legal_Doc_Detail（契約条文の逐語）
```

> LLMでの**初期タグ付け** → アナリストが手動上書き可能（MVPはこの二段構え）。

---

## 2) 変換（マスキング）メソッド定義

|メソッド|説明|例（Before → After）|
|---|---|---|
|`redact_full`|完全マスク|「顧客名：ABC社」→「顧客名：［非開示］」|
|`anonymize_entity`|カテゴリに置換|「ABC社（年商300億）」→「上場・製造業（年商200–500億）」|
|`bucket_numeric`|階級化（バケット）|8.3% → 5–10% ／ 7.6M → 5–10M|
|`range_numeric`|範囲化（中央値±幅）|86.4M → 80–90M|
|`round_currency`|丸め（規模別）|76,240,000 → 76.0M（<10Mは0.1M刻み、10–100Mは1M刻み 等）|
|`generalize_date`|時間の一般化|2025-07-14 → 2025-Q3 ／ 2025年7月|
|`generalize_geo`|地理の一般化|東京都千代田区 → 首都圏／日本|
|`rights_canonicalize`|条項を標準語彙へ|「フルラチェット」→「反希薄化：フルラチェット（有）」|
|`bool_flag`|有無だけ表示|「最低保証 1.2M/年」→「最低保証：有」|
|`topk_list`|上位のみ・件数のみ|顧客名リスト → 「エンタープライズ上位10社、合計XX%」|
|`text_sanitize`|文中機微を置換|「顧客A・料金X円」→「顧客［非開示］・料金［レンジ］」|

**丸め規則（推奨）**

- < 1M：**50k**刻み
    
- 1–10M：**0.1M**刻み
    
- 10–100M：**1M**刻み
    
- 100M+：**5M**刻み
    

---

## 3) セクション別・既定マスキングポリシー（MVP）

> 右列は LP（NDAなし）既定。`LP+NDA` は1段ゆるく、`IC`はフル表示。

|セクション|対象フィールド|LP既定|
|---|---|---|
|概要|会社住所・担当者名|住所は市区まで／担当は役職のみ（PIIはredact）|
|ファイナンス（今回）|投資額・プレ/ポスト・保有％・ラウンド総額・実行日|**range_numeric/round_currency/generalize_date**（例：投資額=5–7M、保有=8–12%、実行=2025-Q3）|
|次回ラウンド目安|枠・時期・KPI目標|**range_numeric/generalize_date**（KPIは範囲／月は四半期化）|
|投資テーマ|テキスト|**text_sanitize**（顧客名・契約名は匿名化）|
|課題/既存代替/非効率|テキスト|公開可（特定社名は匿名化）|
|解決策（製品・優位性）|ロードマップ|**近6ヶ月のみ**要点／機微技術は抽象化|
|なぜ今|技術/政策/需要|公開可（出典はPUB/EXT）|
|ビジネス|事業ライン|公開可（価格は**レンジ**）|
|KPI収益分析|ARR/MRR/ARPA/Churn 等|**bucket_numeric/range_numeric**。顧客別・チャネル別の生値や分母定義は**非表示**（定義は脚注で一般化）|
|目標（次回/IPO）|数値目標|**range_numeric/generalize_date**|
|収益ドライバー施策|予算・CPA|施策は概略のみ／**予算・CPAはレンジ**|
|トラクション|顧客数・提携|顧客名は**anonymize_entity**（カテゴリ+規模）。総数は表示可|
|GTM|チャネル・パートナー|社名は公開済のみ記載。未公表は**topk_list/カテゴリ化**|
|ユニットエコノミクス|LTV/CAC/回収期間|**比率・期間はレンジ**、前提の機微（粗利率やCPA生値）は非表示|
|財務計画|予実・モデル|**年/四半期レベルの高粒度**のみ。月次・契約別は非表示|
|チーム|経歴/人数|氏名は公開済のみ。従業員数は**バケット**（50–100名等）|
|Cap Table|主要株主・比率|**カテゴリ別・レンジ**（創業者合計 30–40%、投資家合計 45–55%…）。個別比率は**LP+NDA以上**|
|市場規模|TAM/SAM/SOM|公開可（出典必須）|
|競合分析|競合名・比較|公開可（未公表の相手はカテゴリ化）|
|ディール条件|優先権/反希薄化/情報権/ボード|**rights_canonicalize + bool_flag**（例：清算優先：1x 非参加型、反希薄化：加重平均（有）、ボード：オブザーバー）※細目はLP+NDA以上|
|資金使途|項目別%|**10%刻みレンジ**（例：R&D 30–40%、S&M 40–50%）|
|シンジケート|投資家名|公開済のみ実名。未公表は「海外機関投資家」「国内CVC」等へ変換|
|エグジット戦略|買収候補・比較事例|事例は出典付きで公開可。買収候補は**カテゴリ化**|
|バリュエーション|方法・マルチプル|**EVレンジ（P25–P75）と中央値**のみ。原票詳細は脚注。|
|リターン分析|MOIC/IRR|**レンジ（シナリオ別）**。確率重みは**LP+NDA以上**|
|DDサマリー|主要発見・懸念|**要点のみ**（固有名詞・条文は非表示）。対応状況はカテゴリで表示|
|リスクと対策|トップ3–5|公開可（特定社名は匿名化）|
|バリューアップ|施策|概要のみ。**個社紹介・具体名**は非表示|
|付録|Q&A/モデル/契約要旨|LP版は**Q&A要約のみ**。モデル/契約は**LP+NDA以上**|

---

## 4) ルール設定ファイル（MVP用 JSON 例）

`/config/lp_masking_policy_v0_1.json`

```json
{
  "version": "0.1",
  "defaults": {
    "IC": "pass",
    "LP+NDA": "transform",
    "LP": "transform_strict",
    "Private": "hide"
  },
  "transformers": {
    "valuation": ["range_numeric", "round_currency"],
    "ownership": ["range_numeric"],
    "dates": ["generalize_date"],
    "customer": ["anonymize_entity"],
    "pii": ["redact_full"],
    "pricing": ["range_numeric", "bucket_numeric"],
    "rights": ["rights_canonicalize", "bool_flag"],
    "pipeline": ["topk_list", "anonymize_entity"],
    "kpi": ["bucket_numeric", "range_numeric"]
  },
  "section_rules": [
    {
      "section": "finance_round",
      "fields": ["investment_amount","pre_money","post_money","ownership_pct","round_size","execution_date"],
      "lp_policy": ["valuation","ownership","dates"]
    },
    {
      "section": "traction",
      "fields": ["customers","partners"],
      "lp_policy": ["customer"]
    },
    {
      "section": "unit_economics",
      "fields": ["ltv","cac","payback_months"],
      "lp_policy": ["kpi"]
    },
    {
      "section": "deal_terms",
      "fields": ["liquidation_pref","anti_dilution","board_rights","info_rights","veto_rights"],
      "lp_policy": ["rights"]
    },
    {
      "section": "cap_table",
      "fields": ["founders_pct","investors_pct","esop_pct","top_holder_list"],
      "lp_policy": ["ownership","customer"]
    }
  ],
  "rounding": {
    "lt_1m": 50000,
    "1_10m": 100000,
    "10_100m": 1000000,
    "100m_plus": 5000000
  },
  "date_generalization": "quarter", 
  "percent_buckets": [5,10,15,20,30,40,50,60,70,80,90]
}
```

---

## 5) 適用アルゴリズム（疑似コード）

```pseudo
function mask_for_lp(observation, policy):
  if observation.disclosure == "Private":
    return HIDE

  level = getTargetLevel()  # "LP" or "LP+NDA"
  if observation.disclosure in ["IC"] and level != "IC":
    # IC専用データは、LP向けに必ず変換または非表示
    mode = policy.defaults[level]
  else:
    mode = policy.defaults[level]

  if mode == "pass":
    return observation  # 変換なし

  # セクション・フィールドに基づきポリシーを選定
  rules = findRules(policy.section_rules, observation.section, observation.field)
  transformers = flatten(policy.transformers, rules.lp_policy)

  value = observation.value
  meta = {}

  for t in transformers:
    value, meta = apply_transform(t, value, observation, policy, meta)

  # 変換結果を返却（元値は監査ログに保持）
  return {
    ...observation,
    "masked_value": value,
    "mask_applied": transformers,
    "mask_meta": meta
  }
```

**apply_transform のイメージ**

- `range_numeric`：中央値±幅（Step 2のP25–P75や規模別丸めを参照）
    
- `round_currency`：`rounding` テーブルに従い丸め
    
- `generalize_date`：`YYYY-Qn` または `YYYY年m月`
    
- `anonymize_entity`：業種・規模レンジへ置換（辞書：_上場/非上場、売上レンジ_）
    
- `rights_canonicalize`：条項を標準語彙へマップ（例：反希薄化=加重平均/フルラチェット、清算優先=1x/参加型 等）
    

---

## 6) 文書生成時の出し分け（資料ビルダー連携）

- **IC版**：`masked_value` があっても **元値** を優先表示（監査ログは非表示）。
    
- **LP+NDA版**：`masked_value` を表示、脚注に「NDA対象」「丸め/範囲」の旨を明記。
    
- **LP版**：`masked_value` のみ。**脚注に出典（URL/ファイル）**とともに「マスキングポリシー」を自動注記。
    
- **脚注必須項目**：`as_of / source_tag / evidence（URL/ファイル） / 変換メソッド / 変換理由（カテゴリ）`
    

---

## 7) 監査ログ（自動）

**ログ1行の例**

```
timestamp: 2025-10-13T10:42Z
entity_id: company:acme
section/field: finance_round/pre_money
original: 86,400,000 USD (as_of 2025-09-30)
masked: 80–90M USD (rounding=1M, method=range_numeric+round_currency)
reason: disclosure=IC → target=LP, category=Valuation_Precise
operator: auto (policy v0.1)  # 手動上書き時は user_id を記録
```

---

## 8) サンプル（Before/After）

**Before（IC版）**

- プレマネー評価額：**86,400,000 USD**（2025-09-30 時点）
    
- 保有比率：**9.2%**
    
- 主要顧客：**ABC社・XYZ社（製造/通信）**
    
- 清算優先：**1x Non-Participating**、反希薄化：**Weighted Avg.**
    
- 次回ラウンド目安：**2026年2Q、ARR 15M**
    

**After（LP版）**

- プレマネー評価額：**80–90M USD（2025年Q3）**
    
- 保有比率：**8–12%**
    
- 主要顧客：**上場・製造業（年商200–500億）、通信大手**
    
- ディール条項：**清算優先：1x 非参加型（有）／反希薄化：加重平均（有）**
    
- 次回ラウンド目安：**2026年上期、ARR 13–17M**
    

---

## 9) 品質ガード（受け入れ基準）

- **漏えいゼロ**：`Private` と `PII` は常に `redact_full`。
    
- **一貫性**：同じフィールドは**同じ丸め・範囲化ルール**で表示。
    
- **透明性**：すべてのマスクに**脚注（出典/As-of/メソッド）**が自動付与。
    
- **再現性**：IC版に戻せるよう**監査ログ**を保持。
    
- **例外処理**：手動オーバーライド時は**差分と操作者**を記録。
    

---

## 10) このStepでの確認ポイント

1. **丸め・範囲幅**の初期値（<1M=50k、1–10M=0.1M、10–100M=1M、100M+=5M）は運用に合うか
    
2. **Cap Table開示**の粒度（LPではカテゴリ＋レンジ、LP+NDAでトップ5のレンジまで）
    
3. **ディール条項**の表現（標準語彙の粒度とLP/LP+NDAの境界）
    
4. **ユニットエコノミクス**の開示（LTV/CACはレンジ、前提は脚注の「一般化」まで）
    
5. **監査ログ**の保存場所（GDrive/S3）とアクセス権
    

---

## 11) 次アクション（Step 4 準備）

- 本ポリシーを `/config/lp_masking_policy_v0_1.json` として確定。
    
- 観測テーブルに `sensitivity` フィールド（初期は自動分類）を追加。
    
- 資料ビルダーに **IC/LP/LP+NDA** モード切り替えと **脚注生成**を実装。
    
- ダミー案件で **PUB/EXTのみ**→LP版を自動生成し、**マスキングと脚注の妥当性**を確認。
    

---

以上が **Step 3：LP開示のマスキング規則（MVP実装仕様）** です。  
この内容で進め、必要があれば丸め幅やセクション別の既定値を調整していきます。次は **Step 4（ダミー案件で一巡テスト）** に進む準備を整えます。