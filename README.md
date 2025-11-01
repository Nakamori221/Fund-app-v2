# Fund IC Automation System

投資ファンドの投資委員会資料自動化プロジェクト（28週 Phase 1-6 実装計画）

## 🎯 プロジェクト概要

Fund IC Automation System は、投資委員会向け資料の **AI自動生成・管理システム** です。

### 目標
- **従来の作業時間を 70% 削減** （手動調査・資料作成 → AI + UI 自動化）
- **案件収集 → 観測データ採用 → 報告書生成** の完全デジタル化
- **ロールベースアクセス制御（RBAC）** による機密情報の安全な分離

### 機能概要
1. **公開情報収集（PUB）** - Web スクレイピング + AI 抽出
2. **観測データ管理** - 数値・文字列・日付・JSON など多形式対応
3. **矛盾検出・解決** - AI が自動検出、人間が選択肢から選択
4. **レポート生成** - IC / LP / 内部向け異なるフォーマット自動出力
5. **リアルタイム承認フロー** - WebSocket + SLA 監視

## 📂 プロジェクト構成

```
fund/
├── backend/                              # FastAPI バックエンド（Phase 1 Week 1-8）
│   ├── app/
│   │   ├── api/v1/                      # REST API エンドポイント
│   │   │   ├── cases.py                 # 案件 CRUD
│   │   │   ├── observations.py          # 観測データ CRUD
│   │   │   ├── conflicts.py             # 矛盾検出・解決
│   │   │   ├── reports.py               # レポート生成
│   │   │   └── auth.py                  # JWT 認証
│   │   ├── models/
│   │   │   └── schemas.py               # Pydantic スキーマ
│   │   ├── services/                    # ビジネスロジック
│   │   │   ├── llm_service.py           # LLM 統一呼び出し
│   │   │   ├── conflict_service.py      # ConflictDetector
│   │   │   └── report_service.py        # ReportGenerator
│   │   ├── core/
│   │   │   ├── security.py              # JWT、RBAC
│   │   │   └── errors.py                # カスタムエラー
│   │   ├── database.py                  # SQLAlchemy + PostgreSQL
│   │   └── main.py                      # FastAPI アプリケーション
│   ├── requirements.txt
│   ├── Dockerfile
│   ├── docker-compose.yml
│   ├── .env.example
│   └── tests/
├── frontend/                             # React + TypeScript フロントエンド（Phase 1 Week 1-8）
│   ├── src/
│   │   ├── components/                  # React コンポーネント
│   │   │   ├── CaseDetail.tsx           # 3ペインレイアウト
│   │   │   ├── ObservationTable.tsx     # 仮想スクロール表示
│   │   │   └── ApprovalPanel.tsx        # 右ペイン承認
│   │   ├── pages/                       # ページコンポーネント
│   │   │   ├── Dashboard.tsx            # KPI ダッシュボード
│   │   │   ├── CaseList.tsx             # 案件一覧
│   │   │   └── Settings.tsx             # RBAC 設定
│   │   ├── hooks/                       # TanStack Query カスタムフック
│   │   ├── stores/                      # Zustand UI 状態管理
│   │   ├── services/                    # API クライアント
│   │   ├── types/                       # TypeScript 型定義（OpenAPI 生成）
│   │   └── utils/                       # ユーティリティ
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   ├── .env.example
│   └── tests/
├── config/                               # 共有設定ファイル
│   ├── field_dictionary_v0_1.json       # 68 フィールド定義（Phase 3 用）
│   └── report_templates_v0_1.json       # IC/LP テンプレート（Phase 2 用）
├── data/                                 # サンプルデータ
│   ├── input/                            # 入力サンプル
│   └── output/                           # 出力サンプル
├── docs/                                 # ドキュメント
│   ├── PHASE1_*.md                       # Phase 1 詳細ガイド
│   ├── ARCHITECTURE.md                   # 全体アーキテクチャ
│   ├── QUERY_KEY_DESIGN.md              # TanStack Query 設計ルール
│   └── RBAC_SPECIFICATION.md            # ロールベース制御
├── 【10】実装サンプルコード集.py       # バックエンド サンプル実装（参考用）
├── .gitignore
├── README.md                             # このファイル
└── LICENSE

```

## 🔧 セットアップ

### 前提条件
- Python 3.11+
- Node.js 18+
- Docker + Docker Compose
- PostgreSQL 15+（Docker で起動可）

### バックエンド セットアップ

```bash
cd backend

# 1. 環境変数設定
cp .env.example .env
# .env を編集してデータベース接続情報を設定

# 2. 依存パッケージインストール
pip install -r requirements.txt

# 3. PostgreSQL 起動（Docker）
docker-compose up -d

# 4. データベース マイグレーション（Phase 1 Week 2）
alembic upgrade head

# 5. サーバー起動
uvicorn app.main:app --reload
# → http://localhost:8000 にアクセス
# → Swagger UI: http://localhost:8000/docs
```

### フロントエンド セットアップ

```bash
cd frontend

# 1. 環境変数設定
cp .env.example .env
# .env を編集してバックエンド URL を設定

# 2. 依存パッケージインストール
npm install

# 3. 開発サーバー起動
npm run dev
# → http://localhost:5173 にアクセス
```

## 📊 実装ロードマップ

| Phase | 期間 | 主要成果物 | 完了条件 |
|-------|------|----------|--------|
| **Phase 1** | Week 1-8 | 基本 CRUD、認証、ダッシュボード、観測表示 | Happy Path E2E テスト通過 |
| **Phase 2** | Week 9-14 | 矛盾検出 UI、IC 報告書出力、WebSocket | Advanced CRUD 機能 |
| **Phase 3** | Week 15-18 | テンプレートエディタ、マスキング、LP 出力 | 複雑なデータバインディング |
| **Phase 4** | Week 19-22 | PDF インポート、高度なフィルタリング | パフォーマンス最適化 |
| **Phase 5** | Week 23-26 | モバイル PWA、オフライン対応 | デバイステスト完了 |
| **Phase 6** | Week 27-28 | 本番デプロイ、監視・運用ツール | SLA 監視稼働 |

詳細は `FE_IMPLEMENTATION_ROADMAP.md` を参照。

## 🏗️ アーキテクチャ原則

### Server State vs UI State の明確分離
- **Server State（TanStack Query）**
  - Cases, Observations, Conflicts, Approvals（APIから取得）
  - Query cache が Single Source of Truth
  - 自動 refetch + invalidation

- **UI State（Zustand）**
  - Modal open/close, selected rows, filter, pane width など
  - Zustand は record を持たない（query cache と重複を避ける）

### Query Key Design ルール
```javascript
// Format: ['cases', caseId, 'observations', {section, sourceTag}]

// Invalidation strategy:
// - Case 更新 → ['cases', caseId] invalidate のみ
// - Observation 更新 → ['cases', caseId, 'observations'] invalidate のみ

// ❌ 間違い: Zustand に observation list キャッシュ
// ✅ 正し: query cache で管理、Zustand に UI 状態だけ
```

詳細は `docs/QUERY_KEY_DESIGN.md` を参照。

## 🔐 RBAC（ロールベースアクセス制御）

4 つのロール定義：

| ロール | 権限 | 見える情報 |
|-------|------|----------|
| **analyst** | 案件作成、観測入力 | PUB, EXT, INT, (ANL の自分のもの) |
| **lead_partner** | 承認、レポート生成 | PUB, EXT, INT, ANL（全件） |
| **ic_member** | 最終承認、LP 開示判断 | CONF, INT, ANL（全件） |
| **admin** | ユーザー管理、設定変更 | 全て |

データ disclosure_level:
- `IC` - 投資委員会のみ
- `LP` - LP向けに開示可
- `LP_NDA` - NDA 付きで LP 向け
- `PRIVATE` - 内部のみ、非開示

詳細は `docs/RBAC_SPECIFICATION.md` を参照。

## 📚 重要なドキュメント

### 設計・仕様
- `FE_IMPLEMENTATION_ROADMAP.md` - Phase 1-6 完全ロードマップ
- `FRONTEND_READINESS_ASSESSMENT.md` - 準備状況チェックリスト
- `IMMEDIATE_ACTION_PLAN.md` - 今週の 3 つのアクション

### バックエンド
- `IMMEDIATE_ACTION_PLAN.md` - PostgreSQL + FastAPI セットアップ
- `【10】実装サンプルコード集.py` - リファクタリング済み参考コード

### 設定データ
- `config/field_dictionary_v0_1.json` - 68 個の投資指標定義
- `config/report_templates_v0_1.json` - IC/LP レポートテンプレート

## 🧪 テスト戦略

### Phase 1 で必須
- ユニットテスト: CRUD エンドポイント、認証
- E2E テスト: Happy Path（案件作成 → 観測入力 → 表示）

### Phase 2+ で拡大
- 矛盾検出アルゴリズム テスト
- マスキング・disclosure_level テスト
- WebSocket リアルタイム テスト

```bash
# ユニットテスト実行
pytest backend/tests/ -v

# E2E テスト（Cypress / Selenium）
npm run test:e2e
```

## 📈 成功メトリクス

### Happy Path E2E テスト
案件作成 → PUB 収集 → 観測採用 → 承認 → IC/LP 報告書生成

### KPI（フロントエンド）
- Dashboard: 「1 週間の操作回数」「次のアクション」表示
- Observation: Diff %, source_tag badge, 採用理由を 1 クリック
- Approval: 右ペインで 10 件一括承認、SLA 超過は赤バナー

## 🚀 デプロイ

### 開発環境
```bash
docker-compose up
# Backend: http://localhost:8000
# Frontend: http://localhost:5173
```

### ステージング環境（Week 3+ で構築）
- AWS ECS（バックエンド）
- Vercel / Netlify（フロントエンド）
- GitHub Actions CI/CD

## 📞 サポート

質問・問題報告は GitHub Issues にお願いします。

## 📜 ライセンス

Private / Internal Use Only

---

**最終更新**: 2025-11-01
**次のマイルストーン**: Phase 1 Week 1 - PostgreSQL セットアップ + FastAPI 初期実装
