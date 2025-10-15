# 【改訂版】実務責任者向け_3ヶ月MVP実装計画

**作成日**: 2025-10-15
**対象**: プロジェクト責任者、実務担当マネージャー
**前提**: AI知識あり、Python経験なし（プロンプト活用・GAS使用可能）
**作業時間**: 平日毎日1時間程度

---

## 📋 目次

1. [方針転換：なぜ3ヶ月MVPなのか](#方針転換なぜ3ヶ月mvpなのか)
2. [MVP の全体像](#mvpの全体像)
3. [3ヶ月で作るもの](#3ヶ月で作るもの)
4. [実装アプローチ（段階的ブラッシュアップ）](#実装アプローチ段階的ブラッシュアップ)
5. [3ヶ月スケジュール](#3ヶ月スケジュール)
6. [Month 1: 情報把握＆PUB収集](#month-1-情報把握pub収集)
7. [Month 2: GASダッシュボード＆自動化プロンプト](#month-2-gasダッシュボード自動化プロンプト)
8. [Month 3: ブラッシュアップ＆実運用化](#month-3-ブラッシュアップ実運用化)
9. [Phase 2: アプリ化（3ヶ月後〜）](#phase-2-アプリ化3ヶ月後)
10. [コストと効果](#コストと効果)

---

## 🎯 方針転換：なぜ3ヶ月MVPなのか

### 従来の計画（9ヶ月）の問題点

```
❌ 9ヶ月後にようやく完成
❌ 途中で使えない（効果を実感できない）
❌ 作り込みすぎて方向修正が困難
❌ モチベーション維持が困難
```

### 新しいアプローチ（3ヶ月MVP）の利点

```
✅ 3ヶ月で実用可能な状態に
✅ 毎週効果を実感しながら進められる
✅ 実際に使いながら改善できる
✅ 小さく始めて段階的に拡張
✅ アプリ化は効果確認後に判断
```

### 基本方針

```
┌────────────────────────────────────────────────┐
│ Phase 1: 3ヶ月MVP（今すぐ開始）                │
├────────────────────────────────────────────────┤
│ ① プロンプト + Spreadsheet + GAS              │
│ ② すぐに使える、段階的に改善                   │
│ ③ 実用性を確認しながら進める                   │
└────────────────────────────────────────────────┘
                    ↓
            【効果を実感】
                    ↓
┌────────────────────────────────────────────────┐
│ Phase 2: アプリ化（3ヶ月後〜、任意）           │
├────────────────────────────────────────────────┤
│ ① Python + データベース + CLI                 │
│ ② さらに自動化、大規模化                       │
│ ③ MVPで効果確認後に着手                        │
└────────────────────────────────────────────────┘
```

---

## 🏗️ MVP の全体像

### 何を作るのか

**「9つのステップの情報を効率的に埋めるための半自動化ツール」**

```
┌─────────────────────────────────────────────────┐
│             投資委員会資料作成フロー              │
├─────────────────────────────────────────────────┤
│ Step 1: 案件登録                                 │
│ Step 2: 公開情報収集（PUB）                      │
│ Step 3: 外部データ統合（EXT）                    │
│ Step 4: 機密資料処理（CONF）                     │
│ Step 5: データ正規化                             │
│ Step 6: ギャップ検出                             │
│ Step 7: 分析実行                                 │
│ Step 8: レポート生成（IC版）                     │
│ Step 9: レポート生成（LP版）                     │
└─────────────────────────────────────────────────┘
```

### MVP で実装する範囲

```
┌──────────────────────────────────────────┐
│ 【3ヶ月MVPで作るもの】                    │
├──────────────────────────────────────────┤
│ ✅ Google Spreadsheet                    │
│   → 9つのステップの情報を管理             │
│   → どこが埋まってるか一目瞭然             │
│                                          │
│ ✅ PUB収集プロンプト（Claude/ChatGPT）   │
│   → 企業サイトから情報を抽出              │
│   → コピペで使える                        │
│                                          │
│ ✅ GASダッシュボード                      │
│   → 不足情報を入力するフォーム             │
│   → 自動でSpreadsheetに反映               │
│                                          │
│ ✅ レポート生成プロンプト                 │
│   → Spreadsheetの情報からIC版を生成       │
│   → LP版マスキングも自動                  │
└──────────────────────────────────────────┘
```

### MVP を使った1案件の処理フロー

```
┌─────────────────────────────────────────────┐
│ Step 1: Spreadsheetに案件登録（1分）        │
├─────────────────────────────────────────────┤
│ あなた: 企業名とURLを入力                   │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 2: PUB収集プロンプトを使用（10分）     │
├─────────────────────────────────────────────┤
│ あなた: 企業サイトを開く                    │
│ → プロンプトをClaude/ChatGPTに貼り付け     │
│ → 企業サイトのURLを渡す                    │
│                                            │
│ AI: 会社名、設立年、従業員数、事業内容を抽出│
│ → JSON形式で返す                           │
│                                            │
│ あなた: 結果をSpreadsheetにコピペ          │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 3: ギャップ確認（1分）                 │
├─────────────────────────────────────────────┤
│ Spreadsheet: 自動で完成度を表示            │
│ → 「78% 完成」                             │
│ → 不足項目を赤字でハイライト               │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 4: GASダッシュボードで入力（30分）     │
├─────────────────────────────────────────────┤
│ あなた: GASで作った入力フォームを開く       │
│ → Term Sheetの情報を手入力                │
│ → 保存すると自動でSpreadsheetに反映       │
└─────────────────────────────────────────────┘
                    ↓
┌─────────────────────────────────────────────┐
│ Step 5: レポート生成（5分）                 │
├─────────────────────────────────────────────┤
│ あなた: レポート生成プロンプトを使用        │
│ → Spreadsheetのデータをコピペ              │
│ → Claude/ChatGPTがIC版Markdownを生成       │
│                                            │
│ LP版の生成:                                │
│ → 「LP版に変換して」と指示                 │
│ → 社名・数値を自動マスキング               │
└─────────────────────────────────────────────┘

合計時間: 約1時間（現状の43-65時間から98%削減）
```

---

## 🛠️ 3ヶ月で作るもの

### 1. Google Spreadsheet（データ管理）

**シート構成**:

```
┌─────────────────────────────────────────┐
│ シート1: 案件一覧                        │
├─────────────────────────────────────────┤
│ 企業ID | 企業名 | URL | ステータス | 完成度 │
│ ─────────────────────────────────────────│
│ C001   | Acme  | ... | 進行中     | 78%    │
│ C002   | Beta  | ... | 完了       | 100%   │
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ シート2: Step2_公開情報（PUB）           │
├─────────────────────────────────────────┤
│ 企業ID | 項目名    | 値      | 出典    │
│ ─────────────────────────────────────────│
│ C001   | 会社名    | Acme Inc | 公式サイト│
│ C001   | 設立年    | 2020     | 公式サイト│
│ C001   | 従業員数  | 45       | 採用ページ│
└─────────────────────────────────────────┘

┌─────────────────────────────────────────┐
│ シート3: Step4_機密情報（CONF）          │
├─────────────────────────────────────────┤
│ 企業ID | 項目名         | 値        │
│ ─────────────────────────────────────────│
│ C001   | プレマネー評価額 | 50M USD   │
│ C001   | 投資額         | 5M USD    │
│ C001   | 取得持分       | 9.1%      │
└─────────────────────────────────────────┘

... 他のステップも同様
```

**自動計算機能**:
```javascript
// Apps Script で完成度を自動計算
function calculateCompleteness(entityId) {
  // 必須項目リスト
  const required = [
    'company_name', 'founded_date', 'employee_count',
    'arr', 'pre_money_valuation', ...
  ];

  // 埋まっている項目数をカウント
  const filled = countFilledFields(entityId, required);

  // 完成度を計算
  return (filled / required.length) * 100;
}
```

---

### 2. PUB収集プロンプト（コピペで使える）

**プロンプトファイル: `prompt_pub_collection.md`**

```markdown
# PUB収集プロンプト v1.0

## 使い方
1. 企業の公式サイトを開く
2. 以下のプロンプトをClaude/ChatGPTにコピペ
3. 企業サイトのURLを渡す
4. 返ってきたJSONをSpreadsheetにコピペ

---

## プロンプト本文

あなたはベンチャーキャピタルのリサーチアナリストです。
以下の企業サイトから投資判断に必要な情報を抽出してください。

【重要な制約】
1. 事実のみを抽出（推測禁止）
2. 数値には単位を付ける
3. 不明な項目はnull
4. 出典箇所を明記

【抽出項目】
- company_name: 会社名（正式名称）
- location: 所在地（都道府県・市区まで）
- founded_date: 設立年月日（YYYY-MM-DD形式）
- employee_count: 従業員数（数値のみ）
- business_description: 事業内容（100文字以内）
- management_team: 経営陣（役職・氏名・経歴のリスト）
- funding_history: 資金調達履歴（日付・ラウンド・金額）
- recent_news: 最近のニュース（見出しと日付、最大3件）

【出力形式】
以下のJSON形式で出力してください：
```json
{
  "company_name": "株式会社サンプル",
  "location": "東京都渋谷区",
  "founded_date": "2020-04-01",
  "employee_count": 45,
  "business_description": "...",
  "management_team": [
    {
      "role": "代表取締役CEO",
      "name": "山田太郎",
      "background": "..."
    }
  ],
  "funding_history": [
    {
      "date": "2021-06-01",
      "round": "シードラウンド",
      "amount": 50000000,
      "currency": "JPY"
    }
  ],
  "recent_news": [
    {
      "date": "2025-09-01",
      "title": "新サービスをリリース"
    }
  ]
}
```

【企業サイトURL】
{ここに企業URLを入力}

---

## 使用例

### 入力
```
【企業サイトURL】
https://www.example-startup.com
```

### 出力（例）
```json
{
  "company_name": "株式会社Example",
  "location": "東京都渋谷区",
  "founded_date": "2020-04-01",
  "employee_count": 45,
  "business_description": "SaaS型のプロジェクト管理ツールを提供",
  ...
}
```

### Spreadsheetへの転記
1. JSONをコピー
2. Spreadsheetの「Step2_公開情報」シートを開く
3. 各項目を該当セルに貼り付け
```

**改善版プロンプト（Week 2-3で追加）**:
- Few-Shot Examples付き
- プレスリリースからの抽出
- 採用ページからの技術スタック抽出

---

### 3. GASダッシュボード（入力フォーム）

**構成**:

```
┌──────────────────────────────────────────┐
│         投資委員会資料 入力フォーム        │
├──────────────────────────────────────────┤
│ 【基本情報】                              │
│ 企業名: [Acme Inc        ]              │
│ 企業ID: [C001           ]              │
│                                          │
│ 【Step 4: 機密情報（CONF）】              │
│ プレマネー評価額: [50        ] M USD    │
│ 投資額:           [5         ] M USD    │
│ 取得持分:         [9.1       ] %        │
│                                          │
│ 【Step 7: 分析情報】                      │
│ ARR:              [5.2       ] M USD    │
│ ARPU:             [500       ] USD/月   │
│ CAC:              [1500      ] USD      │
│ 月次チャーン:      [5         ] %        │
│                                          │
│ [保存]                                   │
└──────────────────────────────────────────┘
```

**GASコード（サンプル）**:

```javascript
// Code.gs

function doGet() {
  return HtmlService.createHtmlOutputFromFile('index')
    .setTitle('投資委員会資料 入力フォーム');
}

function saveData(formData) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Step4_機密情報');

  // データを追加
  sheet.appendRow([
    formData.entityId,
    'pre_money_valuation',
    formData.preMoneyValuation,
    'M USD'
  ]);

  sheet.appendRow([
    formData.entityId,
    'investment_amount',
    formData.investmentAmount,
    'M USD'
  ]);

  // ... 他の項目も同様

  return '保存完了';
}
```

**HTML（サンプル）**:

```html
<!-- index.html -->
<!DOCTYPE html>
<html>
  <head>
    <base target="_top">
    <style>
      body { font-family: Arial, sans-serif; padding: 20px; }
      .form-group { margin-bottom: 15px; }
      label { display: block; font-weight: bold; }
      input { width: 200px; padding: 5px; }
      button { padding: 10px 20px; background: #4285f4; color: white; border: none; cursor: pointer; }
    </style>
  </head>
  <body>
    <h2>投資委員会資料 入力フォーム</h2>

    <form id="inputForm">
      <div class="form-group">
        <label>企業ID:</label>
        <input type="text" name="entityId" required>
      </div>

      <div class="form-group">
        <label>プレマネー評価額 (M USD):</label>
        <input type="number" name="preMoneyValuation" required>
      </div>

      <div class="form-group">
        <label>投資額 (M USD):</label>
        <input type="number" name="investmentAmount" required>
      </div>

      <button type="submit">保存</button>
    </form>

    <script>
      document.getElementById('inputForm').addEventListener('submit', function(e) {
        e.preventDefault();
        const formData = {
          entityId: e.target.entityId.value,
          preMoneyValuation: e.target.preMoneyValuation.value,
          investmentAmount: e.target.investmentAmount.value
        };

        google.script.run.withSuccessHandler(function(result) {
          alert(result);
          e.target.reset();
        }).saveData(formData);
      });
    </script>
  </body>
</html>
```

---

### 4. レポート生成プロンプト

**プロンプトファイル: `prompt_report_generation.md`**

```markdown
# レポート生成プロンプト v1.0

## 使い方
1. Spreadsheetの全データをコピー（TSV形式）
2. 以下のプロンプトをClaude/ChatGPTにコピペ
3. データを貼り付け
4. IC版Markdownが生成される

---

## プロンプト本文

あなたはベンチャーキャピタルの投資委員会資料を作成する専門家です。
以下のSpreadsheetデータから投資委員会資料（IC版）をMarkdown形式で生成してください。

【テンプレート】
```markdown
# 投資委員会資料

**企業名**: {company_name}
**作成日**: {今日の日付}
**投資推奨**: {自動判定または空欄}

---

## 1. 概要

**会社名**: {company_name}
**所在地**: {location}
**設立年月**: {founded_date}
**代表者**: {management_team[0].name}

**事業内容**:
{business_description}

**出典**: {evidence}（取得日: {as_of}）

---

## 2. 事業内容

{business_description の詳細展開}

---

## 3. 市場環境

**市場規模（TAM）**: {market_size_tam}
**成長率**: {market_growth_rate}

---

## 4. 経営陣

{management_team をリスト形式で展開}

---

## 5. 主要KPI

| 指標 | 値 | 定義 | 出典 |
|------|----|----|------|
| ARR | {arr} | 年間経常収益 | {evidence} |
| ARPU | {arpu} | 顧客単価 | {evidence} |
| CAC | {cac} | 顧客獲得コスト | {evidence} |
| 月次チャーン | {monthly_churn} | 解約率 | {evidence} |

---

## 6. ユニットエコノミクス

- **LTV**: {ltv 計算}
- **CAC**: {cac}
- **LTV/CAC比率**: {ltv/cac 計算}（{評価}）
- **ペイバック期間**: {payback_months}ヶ月

---

## 7. 投資条件

- **プレマネー評価額**: {pre_money_valuation}
- **投資額**: {investment_amount}
- **取得持分**: {ownership_percentage}%
- **清算優先権**: {liquidation_preference}

**出典**: Term Sheet（{as_of}）

---

## 8. リスク分析

{リスクを自動抽出またはテンプレート}

---

**本資料は機密情報を含みます。IC委員以外への開示を禁じます。**
```

【Spreadsheetデータ】
{ここにSpreadsheetのTSVデータを貼り付け}

---

## LP版への変換

上記で生成されたIC版レポートに対して、以下のプロンプトを追加してください：

```
上記のIC版レポートをLP版に変換してください。

【マスキングルール】
1. 社名 → 「[{industry}] [{stage}ステージ企業]」
2. ARR等の具体的数値 → レンジ化（例: $5.2M → $5-10M）
3. プレマネー評価額 → レンジ化
4. 投資条件の詳細 → 削除
```

---

## 使用例

### 入力（Spreadsheetデータ）
```
企業ID  company_name  location    founded_date  ...
C001    Acme Inc      東京都渋谷区  2020-04-01    ...
...
```

### 出力（IC版）
```markdown
# 投資委員会資料

**企業名**: Acme Inc
**作成日**: 2025-10-15
...
```

### 出力（LP版）
```markdown
# LP向けレポート

**企業**: [SaaS] [シリーズAステージ企業]
**ARR**: $5-10M
...
```
```

---

## 📅 3ヶ月スケジュール

### 全体スケジュール

```
┌──────────┬────────────────────────────────────────┐
│ Week 1-4 │ Month 1: 情報把握 ＆ PUB収集            │
│          │ ・Spreadsheet作成                      │
│          │ ・PUB収集プロンプト作成                 │
│          │ ・実案件1件でテスト                     │
├──────────┼────────────────────────────────────────┤
│ Week 5-8 │ Month 2: GASダッシュボード ＆ 自動化    │
│          │ ・入力フォーム作成                      │
│          │ ・完成度自動計算                        │
│          │ ・レポート生成プロンプト                │
├──────────┼────────────────────────────────────────┤
│ Week 9-12│ Month 3: ブラッシュアップ ＆ 実運用化   │
│          │ ・3-5案件で実運用                       │
│          │ ・プロンプト改善                        │
│          │ ・ワークフロー最適化                    │
└──────────┴────────────────────────────────────────┘

合計: 12週（3ヶ月） / 60時間 / ¥30,000
```

### 週次作業時間

```
平日毎日1時間 × 週5日 = 5時間/週
3ヶ月（12週） = 60時間
```

---

## 📖 Month 1: 情報把握＆PUB収集

### 目標
**「1案件について、どこが埋まっていて、どこが足りないかを可視化する」**

---

### Week 1: Spreadsheet構築（5時間）

#### Day 1-2: テンプレート設計（各1時間）

**やること**:
1. 投資委員会資料のテンプレートを確認
2. 9つのステップに必要な項目をリストアップ
3. Spreadsheetのシート構成を設計

**成果物**:
```
必須項目リスト（例）:
┌────────────────────────────────────┐
│ Step 2: 公開情報（PUB）             │
├────────────────────────────────────┤
│ ✓ company_name（会社名）            │
│ ✓ founded_date（設立年月日）        │
│ ✓ employee_count（従業員数）        │
│ ✓ business_description（事業内容）  │
│ ✓ management_team（経営陣）         │
│ ... 他15項目                        │
└────────────────────────────────────┘

┌────────────────────────────────────┐
│ Step 4: 機密情報（CONF）            │
├────────────────────────────────────┤
│ ✓ pre_money_valuation（プレマネー） │
│ ✓ investment_amount（投資額）       │
│ ✓ ownership_percentage（持分）      │
│ ... 他8項目                         │
└────────────────────────────────────┘

... Step 3, 5, 6, 7, 8, 9も同様
```

#### Day 3-4: Spreadsheet作成（各1時間）

**やること**:
1. Google Spreadsheetを新規作成
2. 各ステップのシートを作成
3. 基本フォーマットを設定

**Spreadsheet構成**:
```
シート1: 案件一覧
シート2: Step2_公開情報（PUB）
シート3: Step3_外部データ（EXT）
シート4: Step4_機密情報（CONF）
シート5: Step5_正規化済みデータ
シート6: Step6_ギャップリスト
シート7: Step7_分析結果
シート8: テンプレート定義
```

**Apps Scriptで自動計算を追加**:
```javascript
// 完成度を自動計算
function updateCompleteness() {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const listSheet = ss.getSheetByName('案件一覧');

  // 各案件の完成度を計算
  const entities = listSheet.getRange('A2:A').getValues();

  entities.forEach((row, index) => {
    if (row[0]) {
      const completeness = calculateCompleteness(row[0]);
      listSheet.getRange(index + 2, 5).setValue(completeness + '%');
    }
  });
}
```

#### Day 5: 実案件でテスト（1時間）

**やること**:
1. 既存の案件資料を1件選ぶ
2. Spreadsheetに手入力してみる
3. どこが埋まっていて、どこが空欄かを確認

**成果**:
```
案件: Acme Inc
完成度: 45%

✅ 埋まっている情報（12項目）:
- 会社名、設立年、所在地、事業内容、...

❌ 不足している情報（15項目）:
- プレマネー評価額、ARR、CAC、...
```

**Week 1の成果物**:
- ✅ Spreadsheet完成
- ✅ 1案件の現状把握完了
- ✅ ギャップが可視化された

---

### Week 2: PUB収集プロンプト作成（5時間）

#### Day 1-2: プロンプト設計（各1時間）

**やること**:
1. Claude/ChatGPTで企業サイトから情報を抽出するプロンプトを作成
2. 実際の企業サイトで試す
3. 精度を確認して改善

**プロンプト作成の流れ**:
```
【試行1】基本プロンプト
→ Claude/ChatGPTに企業URL渡して抽出依頼
→ 精度60%（推測が多い）

【試行2】制約を追加
→ 「推測禁止、事実のみ」と明記
→ 精度75%（改善）

【試行3】Few-Shot Examples追加
→ 良い例・悪い例を3つずつ追加
→ 精度85%（実用レベル）
```

#### Day 3-4: 複数サイトでテスト（各1時間）

**やること**:
1. 3-5社の企業サイトでプロンプトをテスト
2. 結果をSpreadsheetに転記
3. 精度と使いやすさを確認

**検証結果（例）**:
```
企業A: 18/20項目抽出（90%）
企業B: 15/20項目抽出（75%）
企業C: 17/20項目抽出（85%）

平均精度: 83%
作業時間: 10分/社（現状の20-30時間から99%削減）
```

#### Day 5: プロンプトを文書化（1時間）

**やること**:
1. プロンプトをMarkdownファイルにまとめる
2. 使い方マニュアルを追加
3. チーム共有用に整備

**Week 2の成果物**:
- ✅ PUB収集プロンプト完成
- ✅ 使い方マニュアル完成
- ✅ 5社でテスト済み（精度85%）

---

### Week 3: プレスリリース・採用ページ対応（5時間）

#### Day 1-3: プロンプト拡張（各1時間）

**やること**:
1. プレスリリースから資金調達情報を抽出するプロンプト作成
2. 採用ページから技術スタック・組織規模を推定するプロンプト作成
3. 既存プロンプトと統合

**プレスリリース抽出プロンプト（サンプル）**:
```markdown
以下のプレスリリースから資金調達情報を抽出してください。

【抽出項目】
- date: 発表日（YYYY-MM-DD）
- round: ラウンド名（シード/シリーズA/B/C等）
- amount: 調達額（数値のみ）
- currency: 通貨（JPY/USD等）
- investors: 投資家リスト

【プレスリリースURL】
{URL}
```

#### Day 4-5: 実案件でテスト（各1時間）

**やること**:
1. Week 1で使った案件に適用
2. 追加情報をSpreadsheetに反映
3. 完成度の向上を確認

**結果**:
```
案件: Acme Inc
完成度: 45% → 68%（+23%向上）

新たに取得できた情報:
✅ 資金調達履歴（3回分）
✅ 技術スタック（React, AWS, Python）
✅ 従業員規模の推定（40-50名）
```

**Week 3の成果物**:
- ✅ プレスリリース対応プロンプト
- ✅ 採用ページ対応プロンプト
- ✅ 完成度 45% → 68% に向上

---

### Week 4: レポート生成プロンプト（5時間）

#### Day 1-3: レポート生成プロンプト作成（各1時間）

**やること**:
1. SpreadsheetデータからIC版レポートを生成するプロンプト作成
2. テンプレートに沿ったMarkdown出力
3. 出典の自動付与

**プロンプト作成**:
```markdown
Spreadsheetの全データから投資委員会資料（Markdown形式）を生成してください。

【テンプレート構造】
1. 概要
2. 事業内容
3. 市場環境
4. 経営陣
5. 主要KPI
6. ユニットエコノミクス
7. 投資条件
8. リスク分析

【Spreadsheetデータ】
{TSVデータを貼り付け}
```

#### Day 4: LP版マスキングプロンプト（1時間）

**やること**:
1. IC版からLP版への変換プロンプト作成
2. 自動マスキングルールを定義

**マスキングプロンプト**:
```markdown
上記のIC版レポートをLP版に変換してください。

【マスキングルール】
1. 社名 → [業種][ステージ]
2. 数値 → レンジ化
3. 投資条件詳細 → 削除
```

#### Day 5: 実案件でテスト（1時間）

**やること**:
1. Week 1-3で作成したSpreadsheetデータを使用
2. IC版レポートを生成
3. LP版に変換

**結果**:
```
IC版レポート: 8ページのMarkdown
LP版レポート: 5ページのMarkdown（マスキング済み）

生成時間: 5分（現状の8-12時間から99%削減）
```

**Month 1の総成果物**:
- ✅ Spreadsheet完成（データ管理基盤）
- ✅ PUB収集プロンプト完成（精度85%）
- ✅ レポート生成プロンプト完成
- ✅ 1案件で実証済み（完成度68%）

**効果**:
- 情報収集時間: 20-30時間 → 30分（98%削減）
- レポート生成: 8-12時間 → 5分（99%削減）

---

## 📊 Month 2: GASダッシュボード＆自動化

### 目標
**「不足情報を簡単に入力できる仕組みを作る」**

---

### Week 5: GAS入力フォーム作成（5時間）

#### Day 1-2: HTMLフォーム作成（各1時間）

**やること**:
1. Google Apps Scriptプロジェクトを作成
2. 入力フォームのHTMLを作成
3. スタイルを調整

**HTML構造**:
```html
<form>
  <h2>Step 4: 機密情報入力</h2>

  <label>企業ID</label>
  <input type="text" name="entityId">

  <label>プレマネー評価額 (M USD)</label>
  <input type="number" name="preMoneyValuation">

  <label>投資額 (M USD)</label>
  <input type="number" name="investmentAmount">

  <button type="submit">保存</button>
</form>
```

#### Day 3-4: GASバックエンド実装（各1時間）

**やること**:
1. フォームデータを受け取る関数を作成
2. Spreadsheetに保存する処理を実装
3. エラーハンドリング追加

**GASコード**:
```javascript
function saveData(formData) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const sheet = ss.getSheetByName('Step4_機密情報');

  // データを追加
  sheet.appendRow([
    formData.entityId,
    'pre_money_valuation',
    formData.preMoneyValuation,
    'M USD',
    new Date()
  ]);

  return '保存完了';
}
```

#### Day 5: テストとデプロイ（1時間）

**やること**:
1. フォームからの保存をテスト
2. Spreadsheetへの反映を確認
3. Webアプリとして公開

**Week 5の成果物**:
- ✅ GAS入力フォーム完成
- ✅ Spreadsheetと連携済み
- ✅ Webブラウザからアクセス可能

---

### Week 6: 完成度自動計算（5時間）

#### Day 1-3: 完成度計算ロジック実装（各1時間）

**やること**:
1. 必須項目リストをテンプレートシートに定義
2. 完成度を自動計算するGAS関数を作成
3. 案件一覧シートに自動反映

**GASコード**:
```javascript
function calculateCompleteness(entityId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const templateSheet = ss.getSheetByName('テンプレート定義');
  const requiredFields = templateSheet.getRange('A2:A').getValues().flat();

  let filledCount = 0;

  // 各ステップのシートをチェック
  ['Step2_公開情報', 'Step4_機密情報', 'Step7_分析結果'].forEach(sheetName => {
    const sheet = ss.getSheetByName(sheetName);
    const data = sheet.getRange('A2:B').getValues();

    data.forEach(row => {
      if (row[0] === entityId && row[1] && requiredFields.includes(row[1])) {
        filledCount++;
      }
    });
  });

  return Math.round((filledCount / requiredFields.length) * 100);
}
```

#### Day 4-5: 不足項目のハイライト（各1時間）

**やること**:
1. 不足項目を赤字でハイライトする機能を追加
2. ギャップリストシートに自動出力
3. 優先度を自動付与

**GASコード**:
```javascript
function highlightGaps(entityId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const gapSheet = ss.getSheetByName('Step6_ギャップリスト');

  // 不足項目を検出
  const gaps = detectGaps(entityId);

  // ギャップリストに書き込み
  gaps.forEach((gap, index) => {
    gapSheet.getRange(index + 2, 1, 1, 3).setValues([[
      gap.field,
      gap.priority,
      gap.suggested_source
    ]]);

    // 優先度に応じて色付け
    if (gap.priority === 'Critical') {
      gapSheet.getRange(index + 2, 1, 1, 3).setBackground('#ff0000');
    } else if (gap.priority === 'High') {
      gapSheet.getRange(index + 2, 1, 1, 3).setBackground('#ff9900');
    }
  });
}
```

**Week 6の成果物**:
- ✅ 完成度自動計算機能
- ✅ 不足項目の自動ハイライト
- ✅ ギャップリスト自動生成

---

### Week 7: 分析計算の自動化（5時間）

#### Day 1-3: ユニットエコノミクス計算（各1時間）

**やること**:
1. LTV/CAC計算式をGASに実装
2. Spreadsheetの数値から自動計算
3. 結果をStep7シートに出力

**GASコード**:
```javascript
function calculateUnitEconomics(entityId) {
  const ss = SpreadsheetApp.getActiveSpreadsheet();
  const dataSheet = ss.getSheetByName('Step7_分析結果');

  // データ取得
  const arpu = getValue(entityId, 'arpu');
  const cac = getValue(entityId, 'cac');
  const grossMargin = getValue(entityId, 'gross_margin');
  const churn = getValue(entityId, 'monthly_churn');

  // LTV計算
  const ltv = (arpu * grossMargin) / churn;
  const ltvCacRatio = ltv / cac;
  const paybackMonths = cac / (arpu * grossMargin);

  // 評価
  let assessment;
  if (ltvCacRatio >= 3.0) {
    assessment = '優良';
  } else if (ltvCacRatio >= 1.0) {
    assessment = '要改善';
  } else {
    assessment = '危険';
  }

  // 結果を保存
  saveResult(entityId, 'ltv', ltv);
  saveResult(entityId, 'ltv_cac_ratio', ltvCacRatio);
  saveResult(entityId, 'payback_months', paybackMonths);
  saveResult(entityId, 'ue_assessment', assessment);

  return { ltv, ltvCacRatio, paybackMonths, assessment };
}
```

#### Day 4-5: トリガー設定（各1時間）

**やること**:
1. データ更新時に自動計算するトリガーを設定
2. 完成度も自動更新
3. エラーハンドリング

**Week 7の成果物**:
- ✅ ユニットエコノミクス自動計算
- ✅ データ更新時の自動再計算
- ✅ 計算結果の自動保存

---

### Week 8: ワークフロー統合（5時間）

#### Day 1-3: 全体フローの最適化（各1時間）

**やること**:
1. Step 1 → Step 9 の流れをドキュメント化
2. 各ステップの所要時間を計測
3. ボトルネックを特定

**ワークフロードキュメント**:
```markdown
# 1案件の処理フロー（改善版）

## Step 1: 案件登録（1分）
- Spreadsheet「案件一覧」に企業名とURLを入力

## Step 2: PUB収集（10分）
- プロンプトをClaude/ChatGPTで実行
- 結果をSpreadsheetにコピペ

## Step 3: 外部データ統合（5分）
- Crunchbaseで検索
- 結果をSpreadsheetにコピペ

## Step 4: CONF入力（30分）
- GASフォームから入力

## Step 5: 自動正規化（自動）
- GASが自動で優先順位マージ

## Step 6: ギャップ確認（1分）
- Spreadsheetで完成度確認

## Step 7: 分析実行（自動）
- GASが自動で計算

## Step 8: IC版生成（5分）
- レポート生成プロンプトで実行

## Step 9: LP版生成（2分）
- マスキングプロンプトで変換

合計: 約1時間
```

#### Day 4-5: マニュアル作成（各1時間）

**やること**:
1. 使い方マニュアルを作成
2. スクリーンショット付きで説明
3. よくあるエラーと対処法を記載

**Month 2の総成果物**:
- ✅ GASダッシュボード完成
- ✅ 完成度自動計算
- ✅ ユニットエコノミクス自動計算
- ✅ ワークフロー最適化済み

**効果**:
- 1案件の処理時間: 43-65時間 → 1時間（98%削減）

---

## 🚀 Month 3: ブラッシュアップ＆実運用化

### 目標
**「3-5案件で実運用し、精度とスピードを改善する」**

---

### Week 9-10: 実案件での運用（各5時間）

#### やること

**Week 9: 3案件を処理**
- 実際の新規案件3件をシステムで処理
- 各ステップの所要時間を記録
- エラーや改善点を記録

**処理結果（例）**:
```
案件1: Startup A
├ 完成度: 82%
├ 所要時間: 1.2時間
└ 課題: プレスリリースが見つからない

案件2: Startup B
├ 完成度: 91%
├ 所要時間: 0.8時間
└ 課題: ARRの定義が曖昧

案件3: Startup C
├ 完成度: 76%
├ 所要時間: 1.5時間
└ 課題: 経営陣の経歴が不足
```

**Week 10: 改善実施**
- プロンプトの改善（Few-Shot Examples追加）
- GASフォームに項目追加
- エラーハンドリング強化

**改善後の結果**:
```
平均完成度: 83%
平均所要時間: 1.1時間
精度: 90%以上
```

---

### Week 11: プロンプトライブラリ整備（5時間）

#### Day 1-3: プロンプト集の作成（各1時間）

**やること**:
1. すべてのプロンプトを1つのドキュメントに集約
2. バージョン管理
3. チーム共有用に整備

**プロンプトライブラリ構成**:
```markdown
# プロンプトライブラリ v1.0

## 1. PUB収集プロンプト
### 1-1. 企業サイト基本情報
### 1-2. プレスリリース
### 1-3. 採用ページ

## 2. EXT統合プロンプト
### 2-1. Crunchbaseデータ変換
### 2-2. Similarwebデータ変換

## 3. レポート生成プロンプト
### 3-1. IC版生成
### 3-2. LP版マスキング

## 4. トラブルシューティング
### 4-1. 情報が抽出できない場合
### 4-2. JSON形式エラーの対処法
```

#### Day 4-5: ベストプラクティス文書化（各1時間）

**やること**:
1. 効率的な使い方をまとめる
2. 時短テクニックを記載
3. よくある失敗と対策

**Week 11の成果物**:
- ✅ プロンプトライブラリ完成
- ✅ ベストプラクティス文書化
- ✅ チーム共有準備完了

---

### Week 12: 最終調整と引き継ぎ（5時間）

#### Day 1-2: 最終テスト（各1時間）

**やること**:
1. 5件目の案件を最初から最後まで処理
2. 全ステップの動作確認
3. 最終的な所要時間を計測

**最終結果**:
```
案件5: Startup E
完成度: 88%
所要時間: 55分

【内訳】
Step 1: 案件登録（1分）
Step 2: PUB収集（8分）
Step 3: 外部データ（3分）
Step 4: CONF入力（25分）
Step 5-7: 自動処理（自動）
Step 8: IC版生成（4分）
Step 9: LP版生成（2分）
Step 0: 最終確認（12分）

合計: 55分（現状の43-65時間から98%削減）
```

#### Day 3-5: ドキュメント整備（各1時間）

**やること**:
1. システム全体のドキュメントを整備
2. 運用マニュアルを作成
3. チームトレーニング用資料作成

**最終成果物一覧**:
```
✅ Google Spreadsheet（データ管理）
✅ GASダッシュボード（入力フォーム）
✅ プロンプトライブラリ（v1.0）
✅ 運用マニュアル
✅ ベストプラクティス集
✅ トラブルシューティングガイド
```

**Month 3の総成果物**:
- ✅ 5案件で実運用完了
- ✅ 平均所要時間: 1時間/案件
- ✅ 平均完成度: 85%以上
- ✅ 全ドキュメント整備完了

---

## 🎯 Phase 2: アプリ化（3ヶ月後〜、任意）

### MVPで効果を確認後、さらなる自動化を検討

#### アプリ化のメリット

```
┌─────────────────────────────────────────┐
│ MVP（Spreadsheet + GAS + プロンプト）     │
├─────────────────────────────────────────┤
│ ✓ 3ヶ月で完成                            │
│ ✓ すぐに使える                           │
│ ✓ 98%の効果を実現                        │
│                                         │
│ × プロンプトのコピペが必要                │
│ × Spreadsheetへの転記が手動               │
└─────────────────────────────────────────┘
                    ↓
            【アプリ化で解決】
                    ↓
┌─────────────────────────────────────────┐
│ アプリ版（Python + DB + CLI）            │
├─────────────────────────────────────────┤
│ ✓ コマンド1つで自動実行                   │
│ ✓ 転記不要（自動保存）                   │
│ ✓ バッチ処理（10社同時）                 │
│ ✓ さらなる自動化                         │
│                                         │
│ × 開発に3-6ヶ月必要                      │
│ × 技術的な保守が必要                     │
└─────────────────────────────────────────┘
```

#### アプリ化の判断基準

**Go判断（アプリ化を推奨）**:
- ✅ MVPで月10案件以上処理している
- ✅ プロンプトのコピペが面倒に感じる
- ✅ さらに3-6ヶ月の開発期間を確保できる
- ✅ 予算を追加で¥200,000確保できる

**No-Go判断（MVPのまま運用継続）**:
- ❌ 月3-5案件程度しか処理しない
- ❌ MVPで十分満足している
- ❌ 開発期間を確保できない

#### アプリ化のスケジュール（参考）

```
Month 4-6: Phase 1実装（PUB自動収集）
Month 7-9: Phase 2-3実装（統合・CONF処理）
Month 10-12: Phase 4-5実装（分析・レポート）

合計: 9ヶ月、¥200,000
```

---

## 💰 コストと効果

### 3ヶ月MVP のコスト

| 項目 | 月額 | 3ヶ月 |
|------|------|-------|
| **LLM API**（Claude/ChatGPT） | ¥8,000 | ¥24,000 |
| **Google Workspace**（既存利用） | ¥0 | ¥0 |
| **開発ツール**（Claude Code等） | ¥2,000 | ¥6,000 |
| **合計** | **¥10,000** | **¥30,000** |

### 削減効果（3ヶ月）

**前提**:
- 案件数: 3案件/月
- 削減時間: 40時間/案件
- 時給換算: ¥5,000

**計算**:
```
月間削減: 40時間 × 3案件 = 120時間
月間効果: 120時間 × ¥5,000 = ¥600,000

3ヶ月累積: ¥600,000 × 3 = ¥1,800,000
```

### ROI

```
投資額: ¥30,000
効果: ¥1,800,000
ROI: (¥1,800,000 - ¥30,000) / ¥30,000 × 100 = 5,900%
投資回収期間: 約2日
```

### アプリ化した場合の追加コスト（参考）

```
Phase 2（アプリ化）追加コスト: ¥200,000（9ヶ月）
総コスト: ¥230,000（12ヶ月）

削減効果: ¥7,200,000（12ヶ月、月3案件）
ROI: 3,030%
```

---

## 📝 まとめ

### 3ヶ月MVPの価値

```
┌───────────────────────────────────────────┐
│ ✅ 3ヶ月で実用可能                         │
│ ✅ 投資額わずか¥30,000                     │
│ ✅ ROI 5,900%                             │
│ ✅ 投資回収2日                             │
│ ✅ すぐに効果を実感                        │
│ ✅ 段階的に改善可能                        │
└───────────────────────────────────────────┘
```

### 実装アプローチ

```
Month 1: 情報把握 ＆ PUB収集
→ Spreadsheet + プロンプト

Month 2: GASダッシュボード ＆ 自動化
→ 入力フォーム + 自動計算

Month 3: ブラッシュアップ ＆ 実運用
→ 5案件で実証、精度向上

その後: アプリ化は任意
→ 効果確認後に判断
```

### 推奨

✅ **3ヶ月MVPから開始することを強く推奨**

理由:
1. 投資額が小さい（¥30,000）
2. すぐに効果を実感できる
3. 段階的に改善できる
4. アプリ化は後から判断できる
5. リスクが極めて低い

---

**次のアクション**: Week 1 Day 1から開始しましょう！

**保存先**: `C:\Users\81801\Documents\obsidian_toto\70_Projects\Fund\【改訂版】実務責任者向け_3ヶ月MVP実装計画.md`
