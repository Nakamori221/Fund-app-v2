# 【統合版】投資委員会資料AI自動化_完全実装ガイド

**作成日**: 2025-10-15
**バージョン**: v1.0
**対象**: 投資委員会資料作成の半自動化を一人で実装する完全ガイド
**実装者**: 1名（兼務）
**作業時間**: 1日30-60分 × 週5日

---

## 📑 目次

1. [エグゼクティブサマリー](#エグゼクティブサマリー)
2. [プロジェクト概要](#プロジェクト概要)
3. [投資対効果（ROI）分析](#投資対効果roi分析)
4. [全体ロードマップ](#全体ロードマップ)
5. [詳細コスト内訳](#詳細コスト内訳)
6. [Phase別実装ガイド](#phase別実装ガイド)
7. [コスト最適化戦略](#コスト最適化戦略)
8. [リスクとリスク管理](#リスクとリスク管理)
9. [投資判断の推奨](#投資判断の推奨)
10. [FAQ・トラブルシューティング](#faqトラブルシューティング)

---

## 📊 エグゼクティブサマリー

### プロジェクト概要

**目的**: VC投資委員会資料作成を手動43-65時間/案件 → 10-15時間/案件に削減（**70%削減**）

**期間**: 36週（約9ヶ月）

**総作業時間**: 90-180時間（1日30-60分 × 週5日）

**総コスト**: ¥242,500（実費のみ）

### 投資対効果

| 項目 | 金額（9ヶ月） |
|------|-------------|
| **投資額（実費）** | ¥242,500 |
| **削減効果**（5案件/月想定） | ¥8,550,000 |
| **ROI** | 3,427% |
| **投資回収期間** | 約1週間（Phase 1完成後） |

### 本ドキュメントの使い方

このドキュメントは以下の3つの視点を統合しています：

1. **AIワークフロー構築プロフェッショナル視点**: 技術的実現可能性と実装順序
2. **ファンド実務者視点**: 実際に必要な機能の優先順位
3. **プロダクトプロデューサー視点**: スモールスタートと段階的拡大

**読み方**:
- **経営陣・意思決定者**: セクション1-4と9を重点的に
- **実装担当者**: セクション6（Phase別実装ガイド）を日次で参照
- **財務担当者**: セクション3と5を重点的に

---

## 🎯 プロジェクト概要

### 現状の課題

| 課題 | 現状 | 目標 |
|------|------|------|
| **作業時間** | 43-65時間/案件 | 10-15時間/案件 |
| **品質** | 手作業による見落とし・矛盾 | 自動矛盾検出 |
| **属人化** | 担当者によるばらつき | 標準化されたプロセス |
| **スケール** | 案件増加に対応困難 | 2-3倍の案件処理可能 |

### ソリューション概要

```
┌─────────────────────────────────────────────┐
│ Phase 1: PUB自動収集                         │
│ 公開情報を自動収集                           │
│ 20-30時間 → 3-5時間（85%削減）              │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ Phase 2: データ統合・正規化                   │
│ 複数ソースのデータを統合、矛盾を自動検出      │
│ 10-15時間 → 2-3時間（80%削減）              │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ Phase 3: CONF半自動処理                      │
│ Term Sheet、Cap Tableから自動抽出           │
│ 8-12時間 → 2-3時間（75%削減）               │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ Phase 4: 分析自動化                          │
│ ユニットエコノミクス、市場規模を自動計算      │
│ 5-8時間 → 1-2時間（75%削減）                │
└────────────┬────────────────────────────────┘
             ▼
┌─────────────────────────────────────────────┐
│ Phase 5: レポート自動生成                    │
│ IC資料・LP版を自動生成                       │
│ 8-12時間 → 2-3時間（75%削減）               │
└─────────────────────────────────────────────┘
```

### 技術スタック

| レイヤー | 技術 | コスト |
|---------|------|--------|
| **LLM** | OpenAI API (gpt-4o, gpt-4o-mini) | ¥15,000-¥30,000/月 |
| **補助LLM** | Google Gemini Pro 1.5 | ¥5,000-¥8,000/月 |
| **開発ツール** | Claude Code Pro, Cursor Pro, GitHub Copilot | ¥5,000/月 |
| **Web収集** | Playwright, BeautifulSoup | 無料 |
| **データベース** | SQLite（ローカル） | 無料 |
| **外部API** | Crunchbase, Similarweb（トライアル） | 無料 |

---

## 💰 投資対効果（ROI）分析

### 標準シナリオ（5案件/月）

#### 削減効果の詳細
```
【現状】
作業時間: 50時間/案件
月間合計: 50時間 × 5案件 = 250時間
人件費: 250時間 × ¥5,000 = ¥1,250,000/月

【自動化後】
作業時間: 12時間/案件
月間合計: 12時間 × 5案件 = 60時間
人件費: 60時間 × ¥5,000 = ¥300,000/月

【削減効果】
削減時間: 190時間/月（76%削減）
削減コスト: ¥950,000/月
```

#### 投資回収シミュレーション

```
┌────────────────────────────────────────────┐
│ Week 1-4 (Phase 0)                         │
│ 投資: -¥8,000                              │
│ 累計: -¥8,000                              │
├────────────────────────────────────────────┤
│ Week 5-12 (Phase 1)                        │
│ 投資: -¥50,000                             │
│ 効果: ¥0（開発中）                         │
│ 累計: -¥58,000                             │
├────────────────────────────────────────────┤
│ Week 13 (Phase 1完成・実運用開始)           │
│ 投資: -¥242,500（総額）                    │
│ 効果: ¥0（準備期間）                       │
│ 累計: -¥242,500                            │
├────────────────────────────────────────────┤
│ Week 14 (実運用1週目)                      │
│ 効果: +¥190,000                            │
│ 累計: -¥52,500                             │
├────────────────────────────────────────────┤
│ Week 15 (実運用2週目) ★投資回収完了        │
│ 効果: +¥190,000                            │
│ 累計: +¥137,500                            │
└────────────────────────────────────────────┘

投資回収期間: Phase 1完了後 約2週間
```

### 感度分析（4シナリオ）

| シナリオ | 案件数/月 | 削減時間/案件 | 月間削減額 | 9ヶ月累積 | ROI | 投資回収期間 |
|---------|----------|-------------|-----------|----------|-----|------------|
| **楽観的** | 10案件 | 38時間 | ¥1,900,000 | ¥17,100,000 | 6,951% | 4日 |
| **標準** | 5案件 | 38時間 | ¥950,000 | ¥8,550,000 | 3,427% | 1週間 |
| **保守的** | 3案件 | 30時間 | ¥450,000 | ¥4,050,000 | 1,570% | 2週間 |
| **悲観的** | 2案件 | 20時間 | ¥200,000 | ¥1,800,000 | 642% | 5週間 |

**結論**: 最悪のシナリオでも**ROI 642%**を達成

---

## 📅 全体ロードマップ

### タイムライン概要（36週・9ヶ月）

```
┌──────────────┬────────┬───────────┬──────────┐
│ Phase        │ 期間   │ 作業時間  │ コスト   │
├──────────────┼────────┼───────────┼──────────┤
│ Phase 0      │ W1-4   │ 10-20h    │ ¥8,000   │
│ 準備・検証    │ 4週    │           │          │
├──────────────┼────────┼───────────┼──────────┤
│ Phase 1      │ W5-12  │ 20-40h    │ ¥50,000  │
│ PUB自動収集  │ 8週    │           │          │
├──────────────┼────────┼───────────┼──────────┤
│ Phase 2      │ W13-18 │ 15-30h    │ ¥45,000  │
│ データ統合    │ 6週    │           │          │
├──────────────┼────────┼───────────┼──────────┤
│ Phase 3      │ W19-24 │ 15-30h    │ ¥57,000  │
│ CONF処理     │ 6週    │           │          │
├──────────────┼────────┼───────────┼──────────┤
│ Phase 4      │ W25-30 │ 15-30h    │ ¥37,500  │
│ 分析自動化    │ 6週    │           │          │
├──────────────┼────────┼───────────┼──────────┤
│ Phase 5      │ W31-36 │ 15-30h    │ ¥45,000  │
│ レポート生成  │ 6週    │           │          │
├──────────────┼────────┼───────────┼──────────┤
│ **合計**     │ 36週   │ 90-180h   │ ¥242,500 │
└──────────────┴────────┴───────────┴──────────┘
```

### マイルストーン

| 時期 | マイルストーン | 検証内容 |
|------|--------------|---------|
| **Week 4** | Phase 0完了 | 技術的実現可能性の確認 |
| **Week 12** | Phase 1完了 | PUB収集精度90%達成 |
| **Week 18** | Phase 2完了 | データ統合80%達成 |
| **Week 24** | Phase 3完了 | CONF抽出精度95%達成 |
| **Week 30** | Phase 4完了 | 分析の70%自動化 |
| **Week 36** | Phase 5完了 | 全フロー動作確認 |

---

## 💵 詳細コスト内訳

### 月別コスト推移

| 月 | Phase | LLM API | 開発ツール | 外部API | 月額合計 |
|----|-------|---------|-----------|---------|---------|
| **M1** | Phase 0 | ¥3,000 | ¥5,000 | ¥0 | **¥8,000** |
| **M2** | Phase 1 | ¥22,500 | ¥5,000 | ¥0 | **¥27,500** |
| **M3** | Phase 1 | ¥22,500 | ¥5,000 | ¥0 | **¥27,500** |
| **M4** | Phase 2 | ¥25,000 | ¥5,000 | ¥0 | **¥30,000** |
| **M5** | Phase 3 | ¥33,000 | ¥5,000 | ¥0 | **¥38,000** |
| **M6** | Phase 4 | ¥20,000 | ¥5,000 | ¥0 | **¥25,000** |
| **M7** | Phase 5 | ¥25,000 | ¥5,000 | ¥0 | **¥30,000** |
| **M8** | Phase 5 | ¥25,000 | ¥5,000 | ¥0 | **¥30,000** |
| **M9** | 運用開始 | ¥20,000 | ¥5,000 | ¥0 | **¥25,000** |
| | | | | **総額** | **¥242,500** |

### Phase別詳細コスト

#### Phase 0: 準備・技術検証（Week 1-4）

| 項目 | 詳細 | 金額 |
|------|------|------|
| OpenAI API | gpt-4o-mini（検証用） | ¥3,000 |
| Claude Code Pro | 初月無料利用 | ¥2,000 |
| Cursor Pro | 2週間トライアル | ¥2,000 |
| GitHub Copilot | 個人プラン | ¥1,000 |
| **合計** | | **¥8,000** |

**成果物**:
- 開発環境構築完了
- LLM API動作確認
- 簡単なプロトタイプ動作

---

#### Phase 1: PUB自動収集（Week 5-12）

| 項目 | 詳細 | 月額 | 2ヶ月 |
|------|------|------|-------|
| OpenAI API | gpt-4o（構造化抽出） | ¥15,000 | ¥30,000 |
| Gemini Pro | 長文処理補助 | ¥5,000 | ¥10,000 |
| Claude Code Pro | コード生成・デバッグ | ¥2,000 | ¥4,000 |
| Cursor Pro | 実装支援 | ¥2,000 | ¥4,000 |
| GitHub Copilot | 定型処理 | ¥1,000 | ¥2,000 |
| **合計** | | | **¥50,000** |

**成果物**:
- 企業サイトから基本情報を90%以上抽出
- プレスリリース自動収集
- 10社同時処理可能
- CLIツール完成

**削減効果**: PUB収集 20-30時間 → 3-5時間（85%削減）

---

#### Phase 2: データ統合・正規化（Week 13-18）

| 項目 | 詳細 | 月額 | 1.5ヶ月 |
|------|------|------|---------|
| OpenAI API | 正規化・矛盾検出 | ¥20,000 | ¥30,000 |
| Gemini Pro | データ比較 | ¥5,000 | ¥7,500 |
| Crunchbase | 30日トライアル | ¥0 | ¥0 |
| Similarweb | 7日トライアル | ¥0 | ¥0 |
| 開発ツール | 3種 | ¥5,000 | ¥7,500 |
| **合計** | | | **¥45,000** |

**成果物**:
- Crunchbase連携完了
- 正規化エンジン実装
- 矛盾検出機能（Yellow/Red Flag）
- ギャップ検出機能

**削減効果**: データ整合性チェック 10-15時間 → 2-3時間（80%削減）

---

#### Phase 3: CONF半自動処理（Week 19-24）

| 項目 | 詳細 | 月額 | 1.5ヶ月 |
|------|------|------|---------|
| OpenAI API | Term Sheet抽出 | ¥25,000 | ¥37,500 |
| Gemini Pro 1.5 | 長文PDF処理 | ¥8,000 | ¥12,000 |
| 開発ツール | 3種 | ¥5,000 | ¥7,500 |
| **合計** | | | **¥57,000** |

**成果物**:
- PDF/Excel読み込み機能
- Term Sheet自動抽出（95%精度）
- Cap Table解析
- 承認フロー実装

**削減効果**: CONF情報整理 8-12時間 → 2-3時間（75%削減）

---

#### Phase 4: 分析自動化（Week 25-30）

| 項目 | 詳細 | 月額 | 1.5ヶ月 |
|------|------|------|---------|
| OpenAI API | 分析・計算補助 | ¥15,000 | ¥22,500 |
| Gemini Pro | 業界レポート分析 | ¥5,000 | ¥7,500 |
| 開発ツール | 3種 | ¥5,000 | ¥7,500 |
| **合計** | | | **¥37,500** |

**成果物**:
- LTV/CAC自動計算
- TAM/SAM/SOM推定
- Comparables分析
- センシティビティ分析

**削減効果**: 財務分析 5-8時間 → 1-2時間（75%削減）

---

#### Phase 5: レポート自動生成（Week 31-36）

| 項目 | 詳細 | 月額 | 1.5ヶ月 |
|------|------|------|---------|
| OpenAI API | レポート生成 | ¥20,000 | ¥30,000 |
| Gemini Pro | 長文生成補助 | ¥5,000 | ¥7,500 |
| 開発ツール | 3種 | ¥5,000 | ¥7,500 |
| **合計** | | | **¥45,000** |

**成果物**:
- IC版Markdownテンプレート
- LP版自動マスキング
- PDF/Google Docs出力
- 差分サマリー自動生成

**削減効果**: レポート作成 8-12時間 → 2-3時間（75%削減）

---

## 🚀 Phase別実装ガイド

### Phase 0: 準備・技術検証（Week 1-4）

#### Week 1: 環境準備

**Day 1: プロジェクト構造の作成（30分）**

```bash
# ディレクトリ構造を作成
cd C:\Users\81801\Documents\obsidian_toto\70_Projects\Fund
mkdir fund-ic-automation
cd fund-ic-automation
git init

mkdir -p {src,tests,docs,data,output}/{collectors,models,services,agents,utils}
touch README.md .gitignore requirements.txt
```

**タスク**:
- [ ] プロジェクトディレクトリ作成
- [ ] Git初期化
- [ ] README.mdに目的記載

**AIツール活用**:
```
Claude Code: "Python製のVC資料自動化ツールのディレクトリ構造を作成して"
→ ディレクトリ構成、.gitignore、requirements.txtを自動生成
```

**コスト**: ¥0

---

**Day 2: API キーの取得と設定（30分）**

**タスク**:
- [ ] OpenAI API キー取得（https://platform.openai.com/）
- [ ] Google Gemini API キー取得（https://ai.google.dev/）
- [ ] .env ファイル作成

```bash
# .env ファイル
OPENAI_API_KEY=sk-...
GOOGLE_API_KEY=AIza...
```

**実装例**:
```python
# config.py
import os
from dotenv import load_dotenv

load_dotenv()

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GOOGLE_API_KEY = os.getenv("GOOGLE_API_KEY")
```

**AIツール活用**:
```
ChatGPT: "Pythonで.envファイルから環境変数を読み込むサンプルコードを教えて"
```

**コスト**: ¥0

---

**Day 3: LLM API動作確認（30分）**

**実装例**:
```python
# test_llm.py
import os
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# gpt-4o-mini でコスト節約
response = client.chat.completions.create(
    model="gpt-4o-mini",
    messages=[
        {"role": "user", "content": "こんにちは！VC資料自動化ツールのテストです。"}
    ]
)

print(response.choices[0].message.content)
print(f"トークン使用量: {response.usage.total_tokens}")
```

**AIツール活用**:
```
Cursor: 上記コードをコピー → "このコードを実行して動作確認"
```

**コスト**: ¥50（テスト実行）

---

**Day 4: 簡単なWeb情報収集テスト（30分）**

**実装例**:
```python
# test_web_scraping.py
import requests
from bs4 import BeautifulSoup

url = "https://www.example-startup.com"
response = requests.get(url)
soup = BeautifulSoup(response.content, 'html.parser')

# タイトルタグから会社名を抽出
title = soup.find('title').text
print(f"会社名（推定）: {title}")

# h1タグから事業内容を推定
h1_tags = soup.find_all('h1')
for h1 in h1_tags:
    print(f"見出し: {h1.text}")
```

**AIツール活用**:
```
Claude Code: "企業サイトから会社名、設立年、事業内容を抽出するPythonコードを書いて"
```

**コスト**: ¥0

---

**Day 5: プロトタイプ統合テスト（30分）**

**実装例**:
```python
# prototype.py
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import json

def collect_company_info(url):
    # 1. Webページを取得
    response = requests.get(url)
    soup = BeautifulSoup(response.content, 'html.parser')

    # 不要なタグを削除
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()

    text_content = soup.get_text(separator='\n', strip=True)

    # 2. LLMで情報抽出
    client = OpenAI()
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "企業サイトから会社名、設立年、事業内容を抽出してJSON形式で返してください。"},
            {"role": "user", "content": f"URL: {url}\n\n{text_content[:2000]}"}
        ],
        response_format={"type": "json_object"}
    )

    return json.loads(response.choices[0].message.content)

# テスト実行
result = collect_company_info("https://www.example.com")
print(json.dumps(result, indent=2, ensure_ascii=False))

# 結果を保存
with open('data/test_output.json', 'w', encoding='utf-8') as f:
    json.dump(result, f, indent=2, ensure_ascii=False)
```

**AIツール活用**:
```
Cursor Composer: "Day 3とDay 4のコードを統合して、企業情報を自動抽出するスクリプトを作成"
```

**コスト**: ¥100（LLM API呼び出し）

---

#### Week 2: データモデル設計（Day 6-10）

**Day 6: 観測テーブルの設計（30分）**

**実装例**:
```python
# src/models/observation.py
from pydantic import BaseModel, Field
from datetime import date
from typing import Optional
from enum import Enum

class SourceTag(str, Enum):
    PUB = "PUB"      # 公開情報
    EXT = "EXT"      # 外部推定データ
    CONF = "CONF"    # 機密資料
    INT = "INT"      # インタビュー
    ANL = "ANL"      # 分析結果

class DisclosureLevel(str, Enum):
    IC = "IC"                # IC版のみ
    LP = "LP"                # LP版も開示可能
    LP_NDA = "LP+NDA"        # NDA付きLP版
    PRIVATE = "Private"      # 非開示

class Observation(BaseModel):
    """観測データの最小単位"""
    entity_id: str = Field(..., description="企業ID")
    section: str = Field(..., description="business|market|team|deal|kpi")
    field: str = Field(..., description="arr|arpu|employee_count等")
    value: float | str = Field(..., description="値")
    unit: Optional[str] = Field(None, description="単位（USD_millions等）")
    source_tag: SourceTag = Field(..., description="情報ソース")
    evidence: str = Field(..., description="出典URL or ファイルID")
    as_of: date = Field(..., description="取得日")
    disclosure: DisclosureLevel = Field(..., description="開示レベル")
    confidence: float = Field(1.0, ge=0.0, le=1.0, description="信頼度")
    notes: Optional[str] = Field(None, description="備考")

    class Config:
        json_schema_extra = {
            "example": {
                "entity_id": "company:acme",
                "section": "business",
                "field": "arr",
                "value": 5000000,
                "unit": "USD",
                "source_tag": "CONF",
                "evidence": "file:term_sheet_2025.pdf",
                "as_of": "2025-10-01",
                "disclosure": "IC",
                "confidence": 1.0
            }
        }
```

**AIツール活用**:
```
ChatGPT: "VC資料作成用の観測テーブルのPydanticスキーマを設計して。
SourceTag（PUB/EXT/CONF/INT/ANL）とDisclosureLevelも含めて"
```

**コスト**: ¥0

---

**Day 7-10: データベースセットアップ（各30分）**

**Day 7: SQLiteデータベースのセットアップ**

```python
# src/database/db.py
import sqlite3
from pathlib import Path

DATABASE_PATH = Path("data/fund_ic_automation.db")

def init_database():
    """データベース初期化"""
    conn = sqlite3.connect(DATABASE_PATH)
    cursor = conn.cursor()

    # observationsテーブル
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS observations (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            entity_id TEXT NOT NULL,
            section TEXT NOT NULL,
            field TEXT NOT NULL,
            value TEXT NOT NULL,
            unit TEXT,
            source_tag TEXT NOT NULL,
            evidence TEXT NOT NULL,
            as_of DATE NOT NULL,
            disclosure TEXT NOT NULL,
            confidence REAL NOT NULL,
            notes TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)

    # インデックス作成
    cursor.execute("""
        CREATE INDEX IF NOT EXISTS idx_entity_field
        ON observations(entity_id, field)
    """)

    conn.commit()
    conn.close()
    print("Database initialized successfully")

if __name__ == "__main__":
    init_database()
```

**Day 8-9: CRUD操作の実装**

```python
# src/database/crud.py
from typing import List, Optional
from datetime import date
from .db import get_connection
from ..models.observation import Observation

class ObservationCRUD:
    """観測データのCRUD操作"""

    def create(self, obs: Observation) -> int:
        """観測データを作成"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            INSERT INTO observations
            (entity_id, section, field, value, unit, source_tag,
             evidence, as_of, disclosure, confidence, notes)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            obs.entity_id, obs.section, obs.field, str(obs.value),
            obs.unit, obs.source_tag.value, obs.evidence,
            obs.as_of, obs.disclosure.value, obs.confidence, obs.notes
        ))

        obs_id = cursor.lastrowid
        conn.commit()
        conn.close()
        return obs_id

    def get_by_entity_field(self, entity_id: str, field: str) -> List[Observation]:
        """企業IDとフィールドで取得"""
        conn = get_connection()
        cursor = conn.cursor()

        cursor.execute("""
            SELECT * FROM observations
            WHERE entity_id = ? AND field = ?
            ORDER BY as_of DESC
        """, (entity_id, field))

        rows = cursor.fetchall()
        conn.close()

        return [self._row_to_observation(row) for row in rows]
```

**Day 10: テストデータの投入**

```python
# tests/test_crud.py
from src.database.crud import ObservationCRUD
from src.models.observation import Observation, SourceTag, DisclosureLevel
from datetime import date

def test_create_and_retrieve():
    """CRUD操作のテスト"""
    crud = ObservationCRUD()

    # テストデータ作成
    obs = Observation(
        entity_id="company:test_startup",
        section="business",
        field="employee_count",
        value=50,
        unit="人",
        source_tag=SourceTag.PUB,
        evidence="https://example.com/about",
        as_of=date.today(),
        disclosure=DisclosureLevel.LP,
        confidence=0.95
    )

    # 作成
    obs_id = crud.create(obs)
    print(f"Created observation with ID: {obs_id}")

    # 取得
    results = crud.get_by_entity_field("company:test_startup", "employee_count")
    print(f"Retrieved {len(results)} observations")

    assert len(results) > 0
    print("✓ Test passed!")

if __name__ == "__main__":
    test_create_and_retrieve()
```

**AIツール活用**:
```
Claude Code: "観測テーブル用のSQLiteデータベースとCRUD操作を実装して。
Pydanticモデルと連携させて"
```

**コスト**: ¥0

---

#### Week 3-4: PUB収集プロトタイプ（Day 11-20）

**Day 11-15: 情報抽出エンジンの実装（各30分）**

**Day 11: プロンプト設計**

```python
# src/prompts/pub_extractor.py

PUB_EXTRACTOR_SYSTEM_PROMPT = """
あなたは、ベンチャーキャピタルのリサーチアナリストです。
企業の公開情報から、投資判断に必要な事実のみを正確に抽出することが役割です。

【重要な制約】
1. 事実のみを抽出し、推測・解釈は行わない
2. 数値には必ず単位・期間・定義を付ける
3. 全ての情報に出典URLを付与する
4. 不明な項目は null とし、憶測で埋めない
5. 曖昧な表現（"約", "程度", "予定"）はそのまま記録する

【出力形式】
必ず以下のJSON形式で出力してください：
{
  "observations": [
    {
      "field": "company_name",
      "value": "株式会社サンプル",
      "unit": null,
      "confidence": 1.0,
      "notes": null
    },
    {
      "field": "founded_date",
      "value": "2020-04-01",
      "unit": null,
      "confidence": 1.0,
      "notes": "会社概要ページに明記"
    },
    {
      "field": "employee_count",
      "value": 45,
      "unit": "人",
      "confidence": 1.0,
      "notes": "採用ページに「メンバー45名」と明記"
    }
  ]
}
"""

PUB_EXTRACTOR_USER_PROMPT_TEMPLATE = """
以下のHTMLコンテンツから企業情報を抽出してください。

【URL】{url}
【取得日時】{fetch_time}

【HTMLコンテンツ】
{html_content}

【抽出対象】
- company_name（会社名）
- location（所在地: 都道府県・市区まで）
- founded_date（設立年月日）
- employee_count（従業員数）
- business_description（事業内容: 100文字以内の要約）
- management_team（経営陣: 名前と役職のリスト）
- recent_news（最近のニュース: 見出しと日付、最大3件）

【重要】
- 上記の情報が見つからない場合は、該当フィールドを null としてください
- 推測は禁止です
- 複数の値がある場合（例: 複数の拠点）は配列で返してください
"""

# Few-Shot Examples
FEW_SHOT_EXAMPLES = """
【良い例】
{
  "field": "employee_count",
  "value": 45,
  "unit": "人",
  "confidence": 1.0,
  "notes": "採用ページに「メンバー45名」と明記"
}

【悪い例（推測している）】
{
  "field": "employee_count",
  "value": 50,
  "notes": "LinkedInのフォロワー数から推定"
}
→ 推定は禁止。確実な情報のみ。

【悪い例（出典がない）】
{
  "field": "founded_date",
  "value": "2020-04-01"
}
→ notes に出典を明記する必要がある。

【悪い例（単位がない）】
{
  "field": "revenue",
  "value": 500
}
→ 単位（万円/百万円/億円）と期間（年次/月次）を明記。
"""
```

**Day 12-13: 情報抽出エンジン実装**

```python
# src/collectors/pub_collector.py
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
from datetime import datetime
import json
from typing import List, Dict
from ..prompts.pub_extractor import (
    PUB_EXTRACTOR_SYSTEM_PROMPT,
    PUB_EXTRACTOR_USER_PROMPT_TEMPLATE
)
from ..models.observation import Observation, SourceTag, DisclosureLevel

class PUBCollector:
    """公開情報収集エンジン"""

    def __init__(self):
        self.client = OpenAI()

    def collect(self, url: str, entity_id: str) -> List[Observation]:
        """企業サイトから公開情報を収集"""
        # 1. Webページを取得
        html_content = self._fetch_webpage(url)

        # 2. HTMLをクリーニング
        cleaned_content = self._clean_html(html_content)

        # 3. LLMで情報抽出
        extracted_data = self._extract_with_llm(url, cleaned_content)

        # 4. 観測データに変換
        observations = self._to_observations(
            extracted_data,
            entity_id,
            url
        )

        return observations

    def _fetch_webpage(self, url: str) -> str:
        """Webページを取得"""
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.text

    def _clean_html(self, html: str) -> str:
        """HTMLをクリーニング"""
        soup = BeautifulSoup(html, 'html.parser')

        # 不要なタグを削除
        for tag in soup(['script', 'style', 'nav', 'footer', 'header']):
            tag.decompose()

        # テキストを抽出
        text = soup.get_text(separator='\n', strip=True)

        # 連続する空行を削除
        lines = [line for line in text.split('\n') if line.strip()]

        return '\n'.join(lines)

    def _extract_with_llm(self, url: str, content: str) -> Dict:
        """LLMで情報を抽出"""
        # トークン制限対策: 最初の4000文字のみ
        content_truncated = content[:4000]

        user_prompt = PUB_EXTRACTOR_USER_PROMPT_TEMPLATE.format(
            url=url,
            fetch_time=datetime.now().isoformat(),
            html_content=content_truncated
        )

        response = self.client.chat.completions.create(
            model="gpt-4o-mini",  # コスト節約
            messages=[
                {"role": "system", "content": PUB_EXTRACTOR_SYSTEM_PROMPT},
                {"role": "user", "content": user_prompt}
            ],
            response_format={"type": "json_object"}
        )

        return json.loads(response.choices[0].message.content)

    def _to_observations(
        self,
        data: Dict,
        entity_id: str,
        url: str
    ) -> List[Observation]:
        """抽出データを観測テーブル形式に変換"""
        observations = []

        for obs_data in data.get("observations", []):
            obs = Observation(
                entity_id=entity_id,
                section=self._infer_section(obs_data["field"]),
                field=obs_data["field"],
                value=obs_data["value"],
                unit=obs_data.get("unit"),
                source_tag=SourceTag.PUB,
                evidence=url,
                as_of=datetime.now().date(),
                disclosure=DisclosureLevel.LP,  # 公開情報はLP版も可
                confidence=obs_data.get("confidence", 0.9),
                notes=obs_data.get("notes")
            )
            observations.append(obs)

        return observations

    def _infer_section(self, field: str) -> str:
        """フィールド名からセクションを推定"""
        field_to_section = {
            "company_name": "business",
            "location": "business",
            "founded_date": "business",
            "employee_count": "team",
            "business_description": "business",
            "management_team": "team",
            "recent_news": "business"
        }
        return field_to_section.get(field, "business")
```

**Day 14-15: テストと検証**

```python
# tests/test_pub_collector.py
from src.collectors.pub_collector import PUBCollector
from src.database.crud import ObservationCRUD
import json

def test_pub_collection():
    """PUB収集のテスト"""
    collector = PUBCollector()
    crud = ObservationCRUD()

    # テスト対象のURL
    test_url = "https://www.example-startup.com"
    entity_id = "company:example_startup"

    # 情報収集
    print(f"Collecting information from {test_url}...")
    observations = collector.collect(test_url, entity_id)

    print(f"Collected {len(observations)} observations")

    # データベースに保存
    for obs in observations:
        obs_id = crud.create(obs)
        print(f"  - {obs.field}: {obs.value} (ID: {obs_id})")

    # 結果をJSONで出力
    result = {
        "entity_id": entity_id,
        "source_url": test_url,
        "observations": [
            {
                "field": obs.field,
                "value": obs.value,
                "unit": obs.unit,
                "confidence": obs.confidence
            }
            for obs in observations
        ]
    }

    with open('data/pub_collection_result.json', 'w', encoding='utf-8') as f:
        json.dump(result, f, indent=2, ensure_ascii=False)

    print("✓ Test completed!")
    print(f"  Result saved to data/pub_collection_result.json")

if __name__ == "__main__":
    test_pub_collection()
```

**AIツール活用**:
```
Claude Code Composer:
"企業サイトから情報を抽出し、観測テーブルに保存するPythonコードを書いて。
- BeautifulSoupでHTML解析
- OpenAI APIで情報抽出
- Pydanticモデルでバリデーション
- SQLiteに保存"
```

**コスト**: ¥200-¥500（LLM API呼び出し × 5-10回）

---

**Week 3-4の成果物**:
- ✅ PUB情報抽出エンジン完成
- ✅ 1社の情報を90%以上抽出可能
- ✅ データベースに保存完了

---

### Phase 1: PUB自動収集の本格実装（Week 5-12）

※ 以降のPhaseも同様の詳細度で記載されていますが、
  紙面の都合上、概要のみ記載します。

**Week 5-6: 情報源の拡張**
- プレスリリース収集
- 採用ページ解析
- 複数ページの統合

**Week 7-8: バッチ処理とキャッシング**
- asyncioによる並列処理
- Redis/ファイルキャッシュ
- 進捗表示（tqdm）

**Week 9-10: 品質向上**
- Few-Shot Examples追加
- 信頼度スコアリング
- 異常値検出

**Week 11-12: UI統合**
- CLIツール実装（Click）
- 案件管理コマンド
- レポート出力

**Phase 1の成果**:
- PUB収集時間 20-30時間 → 3-5時間（85%削減）
- 10社同時処理可能
- 精度90%以上

---

### Phase 2-5の概要

**Phase 2: データ統合・正規化（Week 13-18）**
- 外部API統合（Crunchbase, Similarweb）
- 正規化エンジン（優先度マージ）
- 矛盾検出（Yellow/Red Flag）

**Phase 3: CONF半自動処理（Week 19-24）**
- PDF/Excel読み込み
- Term Sheet抽出
- 承認フロー実装

**Phase 4: 分析自動化（Week 25-30）**
- ユニットエコノミクス計算
- TAM/SAM/SOM推定
- Comparables分析

**Phase 5: レポート自動生成（Week 31-36）**
- Jinja2テンプレート
- LP版マスキング
- PDF/Google Docs出力

---

## 💡 コスト最適化戦略

### 1. LLM API コスト削減（月¥10,000-¥15,000削減）

#### モデル選択の最適化

```python
# src/utils/model_selector.py

def select_model(task_type: str, complexity: str) -> str:
    """タスクに応じて最適なモデルを選択"""

    if task_type == "structured_extraction" and complexity == "low":
        # 簡単な情報抽出
        return "gpt-4o-mini"  # $0.150/1M input tokens

    elif task_type == "structured_extraction" and complexity == "medium":
        # 複雑な情報抽出
        return "gpt-4o"  # $2.50/1M input tokens

    elif task_type == "reasoning" and complexity == "high":
        # 推論が必要なタスク
        return "gpt-4o"

    elif task_type == "long_document":
        # 長文処理
        return "gemini-1.5-pro"  # $1.25/1M input tokens

    else:
        # デフォルト
        return "gpt-4o-mini"

# 使用例
model = select_model("structured_extraction", "low")
# → "gpt-4o-mini" を返す（コスト1/15）
```

**削減効果**: 月¥15,000 → ¥8,000（47%削減）

---

#### キャッシング戦略

```python
# src/utils/cache.py
import hashlib
import json
from functools import wraps
from pathlib import Path

CACHE_DIR = Path("data/cache")
CACHE_DIR.mkdir(exist_ok=True)

def cache_llm_response(ttl: int = 86400):
    """LLMレスポンスをキャッシュ（24時間）"""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            # キャッシュキーを生成
            cache_key = hashlib.md5(
                json.dumps({"args": args, "kwargs": kwargs}).encode()
            ).hexdigest()

            cache_file = CACHE_DIR / f"{cache_key}.json"

            # キャッシュが存在し、有効期限内なら返す
            if cache_file.exists():
                cache_age = time.time() - cache_file.stat().st_mtime
                if cache_age < ttl:
                    with open(cache_file, 'r') as f:
                        return json.load(f)

            # キャッシュがない場合は実行
            result = func(*args, **kwargs)

            # キャッシュに保存
            with open(cache_file, 'w') as f:
                json.dump(result, f)

            return result
        return wrapper
    return decorator

# 使用例
@cache_llm_response(ttl=86400)  # 24時間キャッシュ
def extract_pub_info(url: str):
    return call_llm(url)
```

**削減効果**: 再処理分の50-70%削減

---

#### プロンプト最適化（トークン削減）

```python
# src/utils/prompt_optimizer.py
from bs4 import BeautifulSoup

def optimize_html_for_llm(html: str, max_tokens: int = 2000) -> str:
    """HTMLを最適化してトークン数を削減"""
    soup = BeautifulSoup(html, 'html.parser')

    # 1. 不要なタグを完全削除
    for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'aside']):
        tag.decompose()

    # 2. 関連セクションのみ抽出
    relevant_tags = ['h1', 'h2', 'h3', 'p', 'li', 'table']
    relevant_content = []

    for tag_name in relevant_tags:
        for tag in soup.find_all(tag_name):
            text = tag.get_text(strip=True)
            if len(text) > 10:  # 短すぎるテキストは除外
                relevant_content.append(text)

    # 3. トークン制限まで切り詰め
    # 簡易的に文字数で制限（1トークン ≈ 4文字）
    char_limit = max_tokens * 4
    result = '\n'.join(relevant_content)

    return result[:char_limit]
```

**削減効果**: トークン使用量50-70%削減

---

### 2. 開発ツール コスト削減（月¥2,000-¥3,000削減）

#### 無料枠の最大活用

| ツール | 無料枠 | 活用方法 |
|--------|--------|---------|
| **Claude Code** | 最初の月無料 | Phase 0-1で集中利用 |
| **Cursor** | 2週間トライアル | Phase 2-3で利用 |
| **GitHub Copilot** | 学生/OSS貢献者無料 | 条件に該当すれば利用 |

#### 交互利用戦略

```
Phase 0-1（コード生成中心）
├ Claude Code Pro: ¥2,000/月
└ Cursor: 無料トライアル

Phase 2-3（デバッグ中心）
├ Cursor Pro: ¥2,000/月
└ Claude Code: 無料枠に戻る

Phase 4-5（定型処理中心）
├ GitHub Copilot: ¥1,000/月
└ Claude Code: 無料枠

削減効果: ¥5,000/月 → ¥2,000/月（60%削減）
```

---

### 3. 外部API コスト削減（月¥30,000 → ¥0）

#### 無料代替手段の活用

| 有料API | 月額 | 無料代替 | 制約 |
|---------|------|---------|------|
| **Crunchbase Pro** | $29-$99 | 30日トライアル | 期間限定 |
| **Similarweb** | $125+ | 7日トライアル + 無料枠 | 月100クエリ |
| **PitchBook** | $12,000/年 | AngelList（無料） | データの網羅性 |

#### スクレイピングによる代替

```python
# src/collectors/alternative_data.py

def get_funding_data_free(company_name: str) -> dict:
    """無料ソースから資金調達情報を取得"""

    # 1. 企業公式サイトのプレスリリース
    press_releases = scrape_press_releases(company_name)

    # 2. TechCrunchなどのニュースサイト
    news_articles = search_news(f"{company_name} funding")

    # 3. LLMで情報を統合
    funding_info = extract_funding_info_with_llm(
        press_releases + news_articles
    )

    return funding_info
```

**削減効果**: 月¥30,000 → ¥0（100%削減）

---

### 4. 総合コスト削減効果

| 項目 | 最適化前 | 最適化後 | 削減額 |
|------|---------|---------|--------|
| LLM API | ¥30,000/月 | ¥15,000/月 | ¥15,000 |
| 開発ツール | ¥5,000/月 | ¥2,000/月 | ¥3,000 |
| 外部API | ¥30,000/月 | ¥0/月 | ¥30,000 |
| **合計** | **¥65,000/月** | **¥17,000/月** | **¥48,000** |

**9ヶ月での削減効果**: ¥432,000

**最適化後の総コスト**: ¥242,500 → ¥153,000（37%削減）

---

## ⚠️ リスクとリスク管理

### 技術リスク

| リスク | 確率 | 影響 | 対策 | 対策コスト |
|--------|------|------|------|-----------|
| **LLM精度不足** | 中 | 中 | プロンプト改善、人間レビュー | ¥0 |
| **API障害** | 低 | 高 | フォールバック実装（Gemini） | ¥5,000 |
| **データ破損** | 低 | 高 | 自動バックアップ | ¥0 |
| **スクレイピング失敗** | 中 | 低 | リトライ処理、複数ソース | ¥0 |

### ビジネスリスク

| リスク | 確率 | 影響 | 対策 | 対策コスト |
|--------|------|------|------|-----------|
| **仕様変更** | 中 | 中 | アジャイル開発 | ¥0 |
| **開発遅延** | 中 | 低 | スコープ調整 | ¥0 |
| **採用率低下** | 中 | 中 | トレーニング強化 | ¥0 |
| **効果不足** | 低 | 高 | Phase 1で早期検証 | ¥0 |

### リスク管理戦略

#### 1. 段階的検証（Go/No-Go判断）

```
Week 4（Phase 0完了）
├ 検証: 技術的実現可能性
├ 判断: 精度80%以上 → Go
└ 対応: 不足の場合はプロンプト改善

Week 12（Phase 1完了）
├ 検証: 削減効果の測定
├ 判断: 30時間 → 5時間以下 → Go
└ 対応: 効果不足の場合は一時停止

Week 24（Phase 3完了）
├ 検証: CONF処理の精度
├ 判断: 95%以上 → 本格導入
└ 対応: 精度不足の場合は人間チェック強化
```

#### 2. ロールバック計画

```python
# 旧プロセスへの切り戻し手順
1. データベースのバックアップから復元
2. 手動プロセスのドキュメント参照
3. 問題の根本原因分析
4. 修正後に再度自動化を試行
```

#### 3. 総リスク管理コスト

**合計**: ¥5,000（API障害対策のみ）

---

## 🎯 投資判断の推奨

### Go判断の条件（すべて満たす必要）

✅ **案件数**: 月3案件以上
✅ **予算**: ¥30,000/月を確保可能
✅ **工数**: 週2.5-5時間を確保可能
✅ **期間**: 9ヶ月の投資期間を許容

### 判断フロー

```
Step 1: 案件数の確認
├ 月3案件以上?
│ ├ Yes → Step 2へ
│ └ No  → ROIが低い、見送り推奨

Step 2: 予算の確保
├ 月¥30,000確保可能?
│ ├ Yes → Step 3へ
│ └ No  → Phase 1のみ実施（月¥8,000）

Step 3: 工数の確保
├ 週2.5-5時間確保可能?
│ ├ Yes → Step 4へ
│ └ No  → 外部委託検討

Step 4: 期間の許容
├ 9ヶ月待てる?
│ ├ Yes → Go推奨
│ └ No  → 既製ツール検討
```

### 投資プラン（3オプション）

#### Option A: 超ミニマム（月¥5,000-¥8,000）

**対象**: Phase 0のみ先行実施

**期間**: 4週間

**効果**:
- PUB収集の70%自動化
- 1案件あたり15時間削減
- 月3案件で¥225,000削減

**判断**: 効果確認後にPhase 1へ進むか判断

---

#### Option B: スタンダード（月¥20,000-¥30,000）★推奨

**対象**: Phase 0-2を計画通り実施

**期間**: 18週間（4.5ヶ月）

**効果**:
- PUB収集 + データ統合の自動化
- 1案件あたり30時間削減
- 月3案件で¥450,000削減

**判断**: 最もバランスが良いプラン

---

#### Option C: フル実装（月¥30,000-¥40,000）

**対象**: 全Phase実施（最速）

**期間**: 36週間（9ヶ月）

**効果**:
- 全プロセスの70%自動化
- 1案件あたり38時間削減
- 月3案件で¥570,000削減

**判断**: 予算とリソースに余裕がある場合

---

### 投資回収シミュレーション（Option B）

```
【投資額】
Phase 0: ¥8,000
Phase 1: ¥50,000
Phase 2: ¥45,000
合計: ¥103,000

【効果（月3案件想定）】
削減時間: 30時間/案件 × 3案件 = 90時間/月
削減コスト: 90時間 × ¥5,000 = ¥450,000/月

【投資回収期間】
¥103,000 ÷ ¥450,000/月 = 0.23ヶ月
→ 約1週間で投資回収完了

【18週間での累積効果】
¥450,000/月 × 4.5ヶ月 = ¥2,025,000
ROI: (¥2,025,000 - ¥103,000) / ¥103,000 = 1,866%
```

---

## ❓ FAQ・トラブルシューティング

### よくある質問

#### Q1: 本当に1日30-60分で進められますか？

**A**: はい、可能です。以下の工夫により実現します：

1. **AIツールの最大活用**
   - コード生成: Claude Code / Cursor
   - デバッグ: ChatGPT / Claude
   - 定型処理: GitHub Copilot

2. **タスクの細分化**
   - 1日1タスクに限定
   - 完璧を求めず「動くもの」を優先

3. **テンプレートの活用**
   - プロンプトテンプレート
   - コードスニペット
   - チェックリスト

---

#### Q2: 技術的なスキルはどの程度必要ですか？

**A**: 以下のスキルがあれば十分です：

**必須**:
- Python基礎（変数、関数、クラス）
- Git基本操作（clone, commit, push）
- コマンドライン基本操作

**推奨**（なくても可）:
- Web API の使用経験
- データベース（SQL）の基礎
- HTML/CSSの基礎知識

**不要**:
- 高度なアルゴリズム知識
- 機械学習の専門知識
- インフラ構築の経験

AIツールが大部分を補完してくれます。

---

#### Q3: APIコストが予想より高くなったらどうしますか？

**A**: 以下の対策があります：

1. **即座に実施可能**:
   - gpt-4o → gpt-4o-miniに切り替え（コスト1/15）
   - キャッシング強化
   - バッチ処理の最適化

2. **中期的対策**:
   - Geminiへの部分移行（コスト50%削減）
   - ローカルLLMの検討（Llama 3等）
   - プロンプト最適化

3. **最悪の場合**:
   - 一時停止し、コスト分析
   - Phase 1のみ継続（月¥8,000に抑制）

**経験則**: 実際のコストは計画の70-80%程度に収まることが多い

---

#### Q4: 9ヶ月も待てません。もっと早くできませんか？

**A**: 以下の方法で短縮可能です：

**方法1: 作業時間を増やす**
```
30分/日 → 60分/日: 4.5ヶ月に短縮
60分/日 → 90分/日: 3ヶ月に短縮
```

**方法2: Phase を絞る**
```
Phase 0-1のみ実施: 3ヶ月で70%の効果
→ 投資回収後に残りを実施
```

**方法3: 外部リソースの活用**
```
- フリーランスエンジニアを部分的に活用
- コスト: +¥100,000-¥200,000
- 期間: 6ヶ月に短縮可能
```

---

#### Q5: 既製ツール（Notion AI等）との比較は？

| 項目 | 内製システム | 既製ツール |
|------|------------|-----------|
| **初期コスト** | ¥242,500（9ヶ月） | ¥0 |
| **月額コスト** | ¥25,000（運用後） | ¥50,000-¥100,000 |
| **カスタマイズ** | ◎ 完全自由 | △ 限定的 |
| **セキュリティ** | ◎ 完全管理 | △ ベンダー依存 |
| **データ所有** | ◎ 自社 | △ ベンダー |
| **差別化** | ◎ 独自ノウハウ | × 汎用 |

**推奨**:
- 短期（1年以内）: 既製ツール
- 中長期（2年以上）: 内製システム

---

### トラブルシューティング

#### 問題1: API レート制限に達した

**症状**:
```
Error: Rate limit exceeded. Please try again later.
```

**原因**:
- OpenAI API: 3 requests/min（無料枠）
- 短時間に大量リクエスト

**解決策**:
```python
# リトライ処理の実装
import time
import random

def call_with_retry(func, max_retries=3, base_delay=1):
    for attempt in range(max_retries):
        try:
            return func()
        except RateLimitError:
            if attempt == max_retries - 1:
                raise
            delay = base_delay * (2 ** attempt) + random.uniform(0, 1)
            print(f"Rate limit hit, retrying in {delay}s...")
            time.sleep(delay)
```

**予防策**:
- バッチサイズを小さくする（10社 → 3社）
- リクエスト間隔を空ける（sleep(1)）
- 有料プランにアップグレード（制限緩和）

---

#### 問題2: LLM抽出精度が低い（50-70%）

**症状**:
- 会社名が正しく抽出されない
- 数値の単位が抜けている
- 推測で情報を埋めている

**原因**:
- プロンプトが不明確
- Few-Shot Examplesが不足
- 入力データが汚い（HTMLタグ混入）

**解決策**:

**Step 1: プロンプト改善**
```python
# Before（曖昧）
"企業情報を抽出してください"

# After（明確）
"""
以下の情報を**事実のみ**抽出してください：
1. company_name: 正式な会社名（株式会社等を含む）
2. founded_date: YYYY-MM-DD形式
3. employee_count: 数値のみ、単位は"人"

【重要】
- 推測は禁止
- 不明な場合はnull
- 必ず出典を明記
"""
```

**Step 2: Few-Shot Examples追加**
```python
# 良い例・悪い例を5-10個追加
EXAMPLES = """
【良い例】
{"field": "employee_count", "value": 45, "unit": "人", "notes": "採用ページに明記"}

【悪い例】
{"field": "employee_count", "value": 50, "notes": "推定"}
→ 推定は禁止
"""
```

**Step 3: 入力データのクリーニング**
```python
def clean_html(html: str) -> str:
    soup = BeautifulSoup(html, 'html.parser')

    # 不要なタグを完全削除
    for tag in soup(['script', 'style', 'nav', 'footer']):
        tag.decompose()

    return soup.get_text(strip=True)
```

**期待結果**: 精度 50% → 90%に改善

---

#### 問題3: 30分で終わらない

**症状**:
- Day 1のタスクが1時間かかった
- コードのデバッグに時間を取られる
- AIツールの使い方がわからない

**原因**:
- タスクが細分化されていない
- AIツールへの指示が曖昧
- エラーに慣れていない

**解決策**:

**Step 1: タスクをさらに細分化**
```
Before（大きい）:
"PUB収集エンジンを実装"（60分）

After（小さい）:
Day 1: プロンプト設計のみ（20分）
Day 2: HTML取得のみ（20分）
Day 3: LLM呼び出しのみ（20分）
Day 4: データ変換のみ（20分）
Day 5: 統合テスト（30分）
```

**Step 2: AIツールへの明確な指示**
```
悪い例:
"PUB収集のコードを書いて"

良い例:
"以下の仕様で企業サイトから情報を抽出するPythonコードを書いて：
1. requestsでHTML取得
2. BeautifulSoupで解析
3. OpenAI APIで情報抽出
4. Pydanticでバリデーション
5. エラーハンドリング付き"
```

**Step 3: エラーはAIに解決させる**
```
Cursor / Claude Code に以下を入力:
"以下のエラーが発生しています。修正してください。

[エラーメッセージを貼り付け]

[関連コードを貼り付け]
"
```

**期待結果**: 作業時間 60分 → 30分に短縮

---

#### 問題4: ユーザー（チーム）が使わない

**症状**:
- システムは完成したが誰も使わない
- 「手動の方が早い」と言われる
- 旧プロセスに戻ってしまう

**原因**:
- 使い方がわからない
- メリットが実感できない
- 旧プロセスに慣れている

**解決策**:

**Step 1: 個別トレーニング**
```
1. 30分のハンズオントレーニング
2. 実案件1件を一緒に処理
3. Q&Aセッション
```

**Step 2: 成功事例の共有**
```
【Before】
PUB収集: 25時間
データ整理: 12時間
レポート作成: 10時間
合計: 47時間

【After】
PUB収集: 3時間（AI自動）
データ整理: 2時間（AI自動）
レポート作成: 3時間（AI自動）
合計: 8時間

削減効果: 39時間（83%削減）
```

**Step 3: チェンジエージェントの活用**
```
- 影響力のあるメンバーに先行利用してもらう
- その人に他のメンバーを説得してもらう
- 成功体験を共有
```

**期待結果**: 利用率 20% → 80%に改善

---

## 📌 まとめと次のアクション

### このプロジェクトの価値

**投資額**: ¥242,500（9ヶ月）

**効果**: ¥8,550,000（9ヶ月、月5案件想定）

**ROI**: 3,427%

**投資回収期間**: 1週間（Phase 1完成後）

**無形の価値**:
- データ品質の向上
- 属人化の解消
- スケーラビリティの獲得
- ノウハウの蓄積

---

### 今日から始められること

**Day 1のタスク（30分）**:

```bash
# 1. プロジェクトディレクトリ作成
cd C:\Users\81801\Documents\obsidian_toto\70_Projects\Fund
mkdir fund-ic-automation
cd fund-ic-automation
git init

# 2. Claude Codeで初期構造生成
# Claude Code を開いて以下を入力:
# "Python製のVC資料自動化ツールの初期構造を作成して"

# 3. OpenAI APIキー取得
# https://platform.openai.com/ にアクセス
```

---

### 予算申請資料（経営陣向け）

**提案**: 投資委員会資料作成の半自動化システム構築

**目的**: 作業時間70%削減、品質向上、スケーラビリティ獲得

**投資額**:
- 初月: ¥8,000（Phase 0のみ）
- 2-9ヶ月目: ¥25,000-¥38,000/月
- 総額: ¥242,500

**効果**（保守的シナリオ・月3案件）:
- 月間削減: ¥450,000
- 9ヶ月累積: ¥4,050,000
- ROI: 1,570%
- 投資回収期間: 2週間

**リスク**:
- 技術リスク: 低（Phase 0で検証）
- ビジネスリスク: 低（段階的実装）
- 最悪シナリオでもROI 642%

**判断ポイント**:
- Phase 0完了時（Week 4）: 技術的実現可能性
- Phase 1完了時（Week 12）: 削減効果の検証
- Phase 3完了時（Week 24）: 本格導入判断

**推奨**: Go

---

### 実装担当者向けチェックリスト

**Phase 0開始前**:
- [ ] 予算承認（¥8,000）
- [ ] OpenAI APIキー取得
- [ ] Google Gemini APIキー取得
- [ ] Claude Code Pro契約
- [ ] プロジェクトディレクトリ作成
- [ ] このドキュメントを読み込む

**Week 1開始時**:
- [ ] Day 1-5のタスクを確認
- [ ] AIツールの起動確認
- [ ] 30分タイマーをセット
- [ ] README.mdに進捗を記録

**毎週金曜日**:
- [ ] 今週の成果を振り返り
- [ ] 次週のタスクを確認
- [ ] ブロッカーを洗い出し
- [ ] 必要に応じてスコープ調整

---

### 連絡先・サポート

**技術的な質問**:
- Claude Code ドキュメント: https://docs.claude.com/
- OpenAI API ドキュメント: https://platform.openai.com/docs
- このプロジェクトのREADME.md参照

**コスト関連の質問**:
- このドキュメントのセクション5参照
- 月次レポートを作成して共有

**進捗報告**:
- 週次: README.mdに記録
- 月次: 経営陣向けレポート作成

---

**次のアクション**: 今日からDay 1を開始しましょう！

**保存先**: `C:\Users\81801\Documents\obsidian_toto\70_Projects\Fund\【統合版】投資委員会資料AI自動化_完全実装ガイド.md`
