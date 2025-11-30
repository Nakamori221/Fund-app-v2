# フロントエンド構築前 - 準備チェックリスト

**作成日**: 2025-11-01
**対象**: Fund IC Automation System フロントエンド構築
**ステータス**: 準備段階

---

## 📋 概要

フロントエンド（UI/UX）の実装を開始する前に、バックエンド・インフラ・設計面で確認・準備すべき事項を整理しました。

現在、バックエンドコードは「実装サンプル」段階であり、本番環境での運用を想定した準備が必要です。

---

## 🔴 **P0: 必須（これなしではフロントエンド開発が困難）**

### 1. **データベーススキーマの確定と実装**
- **現状**: 【10】実装サンプルコード集.py に SQLAlchemy モデルがあるが、未検証
- **必要なこと**:
  ```
  □ PostgreSQL 本番環境構築（開発・ステージング）
  □ 観測テーブル（observations）、案件テーブル（cases）の初期設計確定
  □ インデックス・制約の定義（パフォーマンス考慮）
  □ マイグレーションスクリプト整備（alembic）
  □ ダミーデータ（テスト用3案件）の準備
  ```
- **確認項目**:
  - ObservationData の `value_type`（number/string/date/boolean/json）の選択肢確定
  - `source_tag`（PUB/EXT/INT/CONF/ANL）の定義確定
  - `disclosure_level`（IC/LP/Internal）のアクセス制御との対応
  - `as_of` 日付の精度（日/時間/分）確定

**推奨順序**: Phase 1 スキーマ設計の詳細化 → DB実装 → マイグレーション整備

---

### 2. **APIエンドポイント仕様の完全化**
- **現状**: FastAPI のサンプルコードが【10】に含まれているが、CRUD 全体がない
- **必要なこと**:
  ```
  □ 観測データ CRUD エンドポイント完成
    - POST /api/v1/observations           (新規作成)
    - GET  /api/v1/cases/{id}/observations (一覧・フィルタリング)
    - PUT  /api/v1/observations/{id}      (更新)
    - DELETE /api/v1/observations/{id}    (削除)

  □ 案件管理エンドポイント完成
    - POST /api/v1/cases                  (新規案件)
    - GET  /api/v1/cases/{id}             (詳細取得)
    - PUT  /api/v1/cases/{id}             (ステータス更新)
    - GET  /api/v1/cases                  (一覧・フィルタリング)

  □ 矛盾検出・解決エンドポイント
    - POST /api/v1/cases/{id}/detect-conflicts (矛盾検出実行)
    - POST /api/v1/conflicts/{id}/resolve      (矛盾解決)

  □ レポート生成エンドポイント
    - POST /api/v1/cases/{id}/generate-report (レポート生成)
    - GET  /api/v1/cases/{id}/report          (レポート取得)

  □ ファイルアップロード対応
    - POST /api/v1/cases/{id}/upload-documents (ドキュメント添付)
  ```
- **検討事項**:
  - ページネーション・ソート仕様（フロントで必須）
  - フィルタリング条件（source_tag, confidence, as_of 日付範囲等）
  - 並列リクエスト時の同時実行制御（PUB収集は バックグラウンドタスク化）

**推奨順序**: OpenAPI/Swagger 仕様書作成 → エンドポイント実装 → 統合テスト

---

### 3. **認証・認可の設計と実装**
- **現状**: サンプルコード内の `HTTPBearer` は未実装状態
- **必要なこと**:
  ```
  □ JWT トークンベース認証の実装
    - ユーザーテーブル設計（id, email, role, password_hash）
    - ロール定義（analyst, lead_partner, ic_member, admin）
    - トークン有効期限設定（access: 1時間, refresh: 7日）

  □ ロールベースアクセス制御（RBAC）
    - CONF 情報へのアクセス権限（lead_partner, ic_member のみ）
    - INT 情報へのアクセス権限（担当analyst のみ）
    - レポート承認権限（ic_member）
    - ユーザー管理権限（admin）

  □ 監査ログ整備
    - API 呼び出し元・操作内容・結果を記録
    - 機密情報（CONF/INT）へのアクセスログ必須
  ```
- **セキュリティ考慮**:
  - パスワードハッシュ化（bcrypt）
  - CORS 設定（フロントエンドドメイン指定）
  - Rate limiting（API 乱用防止）

**推奨順序**: 認証設計書 → ユーザー管理エンドポイント → RBAC ポリシー実装

---

### 4. **エラーハンドリング・レスポンス形式の統一**
- **現状**: リトライロジック は実装済みだが、クライアント向けエラーレスポンスは未定義
- **必要なこと**:
  ```
  □ 統一されたエラーレスポンス形式の定義
    {
      "error_code": "VALIDATION_ERROR",
      "message": "User-friendly error message",
      "details": { "field": "company_name", "reason": "too_long" },
      "timestamp": "2025-11-01T10:30:00Z",
      "request_id": "req_abc123"
    }

  □ HTTP ステータスコード の明確な割り当て
    - 200: 成功
    - 400: バリデーションエラー
    - 401: 認証失敗
    - 403: 権限不足
    - 409: データ矛盾（conflict）
    - 429: レート制限超過
    - 500: サーバーエラー
    - 503: 外部サービス（OpenAI）不可用

  □ バリデーション エラーの詳細化
    - フロントで再入力ガイダンス可能な情報含める
  ```

---

## 🟡 **P1: 高優先度（フロントエンド開発と並行実装可）**

### 5. **ファイルアップロード・ドキュメント管理の設計**
- **現状**: ファイル保存先・形式が未定義
- **必要なこと**:
  ```
  □ ファイルストレージ選択
    - ローカル (開発用)
    - AWS S3 (本番推奨)
    - Azure Blob Storage

  □ ドキュメント管理テーブル設計
    - id, case_id, file_name, file_type, upload_date, uploader_id
    - is_confidential (CONF vs IC/public)

  □ 対応ファイル形式の定義
    - PDF, Word, Excel, 画像, テキスト
    - ファイルサイズ制限（例: 50MB）

  □ スキャン・検証機能
    - ウイルススキャン（ClamAV 等）
    - メタデータの安全性確認
  ```

**推奨順序**: P0 の 1-4 完了後に着手

---

### 6. **外部 API 統合の詳細設計**
- **現状**: PUBCollector は Playwright + OpenAI を使用するが、本番での Cost・Speed を未検討
- **必要なこと**:
  ```
  □ Web スクレイピング戦略の決定
    - Playwright vs Selenium vs API？
    - キャッシュ機構（再訪問時のコスト削減）
    - 失敗時のフォールバック

  □ OpenAI API の Cost 管理
    - 月予算の設定
    - モデル選択（gpt-4o vs gpt-4 vs gpt-3.5）
    - トークン制限の再検討

  □ レート制限対応
    - Queue 管理（複数案件の同時処理）
    - リトライ戦略の実装済み確認

  □ キャッシング戦略
    - Redis の導入検討
    - TTL 設定
  ```

---

### 7. **テスト戦略の確立**
- **現状**: ユニットテスト、統合テスト未整備
- **必要なこと**:
  ```
  □ ユニットテスト フレームワーク
    - pytest で LLMService, ConflictDetector, RetryHandler をテスト
    - Mock で外部 API（OpenAI, Playwright）をシミュレート

  □ 統合テスト
    - DBマイグレーション → API 呼び出し → 結果確認
    - テストデータベース分離

  □ E2E テスト（フロント実装後）
    - Selenium / Cypress / Playwright で UI フロー検証
    - 3 ダミー案件での完全フロー検証

  □ パフォーマンステスト
    - 複数案件同時処理時の応答時間
    - データベース クエリ最適化
  ```

---

### 8. **ログ・監視・アラート設定**
- **現状**: logger は実装済みだが、本番運用の設定なし
- **必要なこと**:
  ```
  □ ログ集約サービス選定
    - ELK Stack (Elasticsearch, Logstash, Kibana)
    - Datadog / New Relic / CloudWatch

  □ モニタリング項目
    - API 応答時間（p50, p95, p99）
    - エラー率（リトライ失敗）
    - データベース接続数
    - OpenAI API コスト・トークン使用量

  □ アラート設定
    - エラー率が 5% 超過時
    - API レスポンス時間が 5秒以上時
    - ディスク容量不足時

  □ Slack / PagerDuty 連携
    - 本番エラーの即座通知
  ```

---

## 🟢 **P2: 中優先度（フェーズ 1.5 以降）**

### 9. **マスキング・非表示ロジックの実装**
- **現状**: disclosure_level は定義されているがロジックなし
- **必要なこと**:
  ```
  □ IC / LP 向けフィルタリング
    - disclosure_level = "IC" のデータのみを IC 資料に表示
    - disclosure_level = "LP" のデータを LP 資料から削除
    - disclosure_level = "Internal" は内部のみ

  □ 個人情報マスキング
    - 名前の一部マスキング（例: "田中太郎" → "田中*郎"）
    - 電話番号・メール アドレスのマスキング

  □ テンプレート自動生成時のマスキング適用
    - ReportGenerator が自動でマスク適用
  ```

---

### 10. **バックアップ・災害復旧（DR）計画**
- **必要なこと**:
  ```
  □ データベース バックアップ戦略
    - 日次 バックアップ（1ヶ月分保持）
    - 即座復旧ポイント目標（RPO）: 1時間
    - 復旧時間目標（RTO）: 4時間

  □ ドキュメント / ファイル バックアップ
    - S3 バージョニング有効化
    - クロスリージョン レプリケーション

  □ 復旧テスト
    - 四半期ごとに復旧テスト実施
  ```

---

## 📅 **推奨実装順序（タイムライン）**

```
Week 1-2 (P0 準備)
├─ P0-1: DB スキーマ確定 → PostgreSQL 構築
├─ P0-2: API エンドポイント仕様書（Swagger）作成
├─ P0-3: 認証・認可設計書作成
└─ P0-4: エラーハンドリング仕様確定

Week 3 (P0 実装)
├─ DB マイグレーション整備
├─ 認証・認可実装
├─ CRUD エンドポイント実装
└─ 統合テスト開始

Week 4 (P1 + FE 開始)
├─ ファイルアップロード実装
├─ テスト戦略・ユニットテスト追加
├─ ログ・監視設定
└─ 【フロントエンド開発開始】

Week 5-6 (P1 完了 + FE 進行)
├─ 外部 API 統合検証
├─ パフォーマンステスト
└─ E2E テスト（FE との統合）

Week 7+ (P2 + 運用準備)
├─ マスキング機能
├─ DR 計画・テスト
└─ 本番環境構築
```

---

## ✅ **チェックリスト（実装確認）**

### 実装サンプルコード（【10】）の確認状況

- [x] RetryHandler - リトライロジック実装済み
- [x] LLMService - LLM API 共通化実装済み
- [x] Config - マジックナンバー設定化済み
- [x] Type Hints - TypedDict で型定義済み
- [x] ConflictDetector - Strategyパターン実装済み
- [x] PUBCollector - Web スクレイピング実装済み
- [x] ReportGenerator - Markdown 生成実装済み
- [ ] **認証エンドポイント** - 未実装
- [ ] **CRUD エンドポイント全体** - 部分実装のみ
- [ ] **データベーススキーマ実装** - 定義のみ（未稼働）
- [ ] **ファイルアップロード処理** - 未実装
- [ ] **ログ・監視設定** - Logger のみ定義
- [ ] **本番環境構成** - 未実装

---

## 🚀 **次アクション**

1. **第 1 優先**: P0-1 のデータベーススキーマを詳細化し、PostgreSQL 開発環境を構築
2. **第 2 優先**: P0-2 の API エンドポイント仕様書（Swagger）を作成
3. **第 3 優先**: P0-3 の認証・認可実装
4. **フロントエンド開始**: P0 の 1-4 が確認できた時点で開始
5. **並行作業**: P1 の テスト・監視設定を進める

---

## 📚 **関連ドキュメント**

- `【10】実装サンプルコード集.py` - バックエンドコード
- `MVP準備計画.md` - 全体フェーズプラン
- `FRONTEND_PREPARATION_CHECKLIST.md` - このファイル

---

**作成者**: Claude Code
**最終更新**: 2025-11-01
