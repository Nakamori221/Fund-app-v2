# フロントエンド構築前 - 即時アクションプラン

**作成日**: 2025-11-01
**優先度ベース**: 実装期間短縮・フロントエンド開発スタート可能化

---

## 📌 **今週中にやるべき 3 つのこと（2日程度で完了可能）**

### **タスク 1️⃣: PostgreSQL 開発環境セットアップ + スキーマ確定**
**所要時間**: 4-6 時間

```bash
# 環境構築
docker run -d \
  --name fund-postgres \
  -e POSTGRES_USER=fund_user \
  -e POSTGRES_PASSWORD=fund_dev_password \
  -e POSTGRES_DB=fund_ic_dev \
  -p 5432:5432 \
  postgres:15-alpine

# スキーマ確定項目
□ Case テーブル確認
  - id (UUID)
  - company_name, stage, status
  - location, founded_date, website_url
  - lead_partner_id, analyst_id
  - discovered_at, ic_date, created_at, updated_at

□ Observation テーブル確認
  - id (UUID), case_id (FK)
  - section, field
  - value_type (enum: number, string, date, boolean, json)
  - value_number, value_string, value_date, value_boolean, value_json
  - unit, source_tag (enum: PUB, EXT, INT, CONF, ANL)
  - evidence, as_of (datetime)
  - confidence (0.0-1.0), disclosure_level (enum: IC, LP, Internal)
  - requires_approval, approved_by, approved_at
  - notes, created_by, created_at, updated_at

□ Document テーブル新規作成
  - id (UUID), case_id (FK)
  - file_name, file_type, file_size
  - storage_path, is_confidential
  - uploaded_by, uploaded_at

□ User テーブル新規作成（認証用）
  - id (UUID)
  - email (unique), password_hash
  - role (enum: analyst, lead_partner, ic_member, admin)
  - is_active, created_at, last_login

□ AuditLog テーブル新規作成
  - id (UUID), user_id (FK), action, resource_type, resource_id
  - changes (JSON), timestamp, ip_address
```

**成果物**: `schema.sql` + `migrations/001_initial_schema.sql`

---

### **タスク 2️⃣: FastAPI プロジェクト骨組み + CRUD エンドポイント実装**
**所要時間**: 6-8 時間

```bash
# ディレクトリ構成
fund-backend/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI アプリ起動
│   ├── config.py               # Config クラス + 設定
│   ├── database.py             # DB 接続・セッション
│   ├── models/
│   │   ├── __init__.py
│   │   └── schemas.py          # Pydantic スキーマ（CaseCreate, CaseResponse等）
│   ├── api/
│   │   ├── __init__.py
│   │   ├── v1/
│   │   │   ├── __init__.py
│   │   │   ├── cases.py        # Cases CRUD
│   │   │   ├── observations.py # Observations CRUD
│   │   │   ├── conflicts.py    # Conflict detection/resolution
│   │   │   ├── reports.py      # Report generation
│   │   │   └── auth.py         # Authentication endpoints
│   ├── services/
│   │   ├── __init__.py
│   │   ├── llm_service.py      # LLMService（既存）
│   │   ├── conflict_service.py # ConflictDetector（既存）
│   │   └── report_service.py   # ReportGenerator（既存）
│   ├── core/
│   │   ├── __init__.py
│   │   ├── security.py         # JWT 処理
│   │   └── errors.py           # カスタムエラークラス
│   └── utils/
│       ├── __init__.py
│       └── logger.py           # ロギング設定
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
└── tests/
    ├── __init__.py
    └── test_cases.py

# 実装すべきエンドポイント
□ POST   /api/v1/auth/register           (ユーザー登録)
□ POST   /api/v1/auth/login              (ログイン)
□ POST   /api/v1/auth/refresh            (トークン更新)

□ POST   /api/v1/cases                   (新規案件作成)
□ GET    /api/v1/cases                   (案件一覧・フィルタリング)
□ GET    /api/v1/cases/{id}              (案件詳細)
□ PUT    /api/v1/cases/{id}              (案件更新)
□ DELETE /api/v1/cases/{id}              (案件削除)

□ POST   /api/v1/observations            (観測データ作成)
□ GET    /api/v1/observations            (一覧・フィルタリング)
□ GET    /api/v1/observations/{id}       (詳細)
□ PUT    /api/v1/observations/{id}       (更新)
□ DELETE /api/v1/observations/{id}       (削除)

□ GET    /api/v1/cases/{id}/observations (案件の観測データ一覧)

□ POST   /api/v1/cases/{id}/detect-conflicts (矛盾検出)
□ GET    /api/v1/conflicts               (矛盾一覧)
□ POST   /api/v1/conflicts/{id}/resolve  (矛盾解決)

□ POST   /api/v1/cases/{id}/generate-report (レポート生成)
□ GET    /api/v1/cases/{id}/report      (生成済みレポート取得)

□ POST   /api/v1/cases/{id}/upload      (ドキュメントアップロード)
□ GET    /api/v1/cases/{id}/documents   (ドキュメント一覧)
```

**成果物**: `app/api/v1/cases.py`, `app/api/v1/observations.py`, `app/core/security.py`

---

### **タスク 3️⃣: OpenAPI / Swagger ドキュメント + 統合テスト開始**
**所要時間**: 3-4 時間

```python
# FastAPI は自動で Swagger を生成
# http://localhost:8000/docs でアクセス可能

# ただし、明示的に以下を確認・整備
□ エンドポイントごとの説明文（docstring）
□ リクエスト/レスポンスの例（examples）
□ エラーレスポンス例（422, 404, 403 など）

# 統合テスト
□ Database 接続テスト
□ CRUD エンドポイント テスト（pytest）
□ 認証フロー テスト
□ 矛盾検出ロジック テスト（既存の ConflictDetector）
```

**成果物**: `tests/test_cases.py`, `tests/test_observations.py`, `tests/test_auth.py`

---

## 🎯 **来週の 2 番目優先タスク（これらが完了したらフロントエンド開始可能）**

### **タスク 4️⃣: エラーハンドリング・バリデーション統一**
**所要時間**: 3-4 時間

```python
# app/core/errors.py に以下を定義
class APIError(Exception):
    def __init__(self, error_code: str, message: str, details: dict = None):
        self.error_code = error_code
        self.message = message
        self.details = details or {}

# エラーレスポンス形式の統一（前述チェックリストを参照）
# 例: ValidationError, ConflictError, AuthenticationError, AuthorizationError

# FastAPI の exception_handler で統一されたレスポンスに変換
```

**成果物**: `app/core/errors.py`, 統一エラーレスポンス ハンドラー

---

### **タスク 5️⃣: 認証・認可実装完了**
**所要時間**: 4-6 時間

```python
# JWT トークン生成・検証
# ロールベースアクセス制御（RBAC）の実装
# CONF / INT データへのアクセス権限チェック

□ Depends() で認証チェック
□ ロール検証デコレーター実装
□ Audit log 記録（CONF/INT アクセス時は必須）
```

**成果物**: `app/core/security.py`, `app/api/v1/auth.py`

---

### **タスク 6️⃣: CI/CD パイプライン準備（GitHub Actions）**
**所要時間**: 2-3 時間

```yaml
# .github/workflows/test.yml
name: Test
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/
      - name: Run linter
        run: flake8 app/ --max-line-length=100
```

**成果物**: `.github/workflows/test.yml`, `requirements-dev.txt`

---

## 📋 **フロントエンド開始チェックリスト**

以下がすべて ✅ になったら、フロントエンド開発を開始可能です：

- [ ] PostgreSQL 開発環境稼働
- [ ] スキーマ実装・マイグレーション確認
- [ ] FastAPI プロジェクト起動可能
- [ ] 主要 CRUD エンドポイント動作
- [ ] 認証エンドポイント実装
- [ ] Swagger ドキュメント生成
- [ ] ユニットテスト 70% 以上カバレッジ
- [ ] エラーハンドリング統一
- [ ] CI/CD パイプライン稼働

---

## 🛠️ **使用技術スタック（推奨）**

**バックエンド**:
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic v2
- PostgreSQL 15+

**認証**:
- PyJWT
- python-jose
- passlib + bcrypt

**テスト**:
- pytest
- pytest-asyncio
- httpx (async HTTP client)

**DevOps**:
- Docker + Docker Compose
- GitHub Actions
- Alembic (DB migrations)

---

## ⏱️ **推定総工数**

| タスク | 時間 | 週 |
|--------|------|-----|
| タスク 1: DB 環境構築 | 4-6h | 今週 |
| タスク 2: FastAPI CRUD | 6-8h | 今週 |
| タスク 3: Swagger + テスト | 3-4h | 今週 |
| タスク 4: エラーハンドリング | 3-4h | 来週 |
| タスク 5: 認証・認可 | 4-6h | 来週 |
| タスク 6: CI/CD | 2-3h | 来週 |
| **合計** | **22-31h** | **2週** |

---

## 💡 **フロントエンド開発時の API 利用想定**

フロントエンドチームは以下の API を活用：

```javascript
// React/Vue 側の例
await api.post('/api/v1/cases', {
  company_name: 'Startup Inc',
  stage: 'early',
  website_url: 'https://startup.com'
});

await api.get('/api/v1/cases/case_id_123');

await api.post('/api/v1/cases/case_id_123/detect-conflicts');

await api.post('/api/v1/cases/case_id_123/generate-report');
```

Swagger ドキュメント (`http://localhost:8000/docs`) で全エンドポイントが試行可能。

---

## 🚀 **開始するには**

```bash
# 1. リポジトリクローン
git clone <repo-url>
cd Fund

# 2. 環境設定
cp .env.example .env

# 3. 依存パッケージインストール
pip install -r requirements.txt

# 4. PostgreSQL 起動（Docker）
docker-compose up -d

# 5. マイグレーション実行
alembic upgrade head

# 6. サーバー起動
uvicorn app.main:app --reload

# 7. Swagger 確認
# ブラウザで http://localhost:8000/docs を開く
```

---

**作成者**: Claude Code
**最終更新**: 2025-11-01
