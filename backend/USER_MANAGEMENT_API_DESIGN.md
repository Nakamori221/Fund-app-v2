# ユーザー管理API設計ドキュメント

**版**: 1.0
**作成日**: 2025-11-01
**ステータス**: 設計完了、実装待ち

---

## 1. 概要

ユーザー管理システムの完全なCRUD API。管理者向けのユーザー作成・編集・削除・ロール管理機能を提供。

---

## 2. データモデル

### 2.1 User スキーマ拡張

```python
class UserBase(BaseModel):
    """ユーザー基本情報"""
    email: str              # メールアドレス（一意）
    full_name: str          # フルネーム
    department: Optional[str]  # 部門（拡張フィールド）
    is_active: bool = True  # 有効フラグ

class UserCreate(UserBase):
    """ユーザー作成リクエスト"""
    password: str
    role: UserRole = UserRole.ANALYST

class UserUpdate(BaseModel):
    """ユーザー更新リクエスト"""
    email: Optional[str] = None
    full_name: Optional[str] = None
    department: Optional[str] = None
    is_active: Optional[bool] = None
    role: Optional[UserRole] = None

class UserResponse(UserBase):
    """ユーザー詳細レスポンス"""
    id: UUID
    role: UserRole
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

class UserListResponse(BaseModel):
    """ユーザー一覧レスポンス"""
    users: List[UserResponse]
    total: int
    skip: int
    limit: int

class RoleInfo(BaseModel):
    """ロール情報"""
    role: UserRole
    description: str
    permissions: List[str]
```

---

## 3. APIエンドポイント設計

### 3.1 ユーザー一覧取得

**エンドポイント**: `GET /api/v1/users`

**認証**: ✅ 必須（Lead Partner+）

**クエリパラメータ**:
```
- skip: int = 0           # スキップレコード数
- limit: int = 20         # 取得レコード数
- role_filter: UserRole   # ロール絞り込み（オプション）
- is_active: bool         # アクティブフラグ絞り込み（オプション）
- search: str             # 名前・メール検索（オプション）
```

**レスポンス**:
```json
{
  "users": [
    {
      "id": "uuid",
      "email": "user@example.com",
      "full_name": "山田太郎",
      "department": "営業部",
      "role": "ANALYST",
      "is_active": true,
      "created_at": "2025-10-15T10:30:00Z",
      "updated_at": "2025-11-01T14:20:00Z"
    }
  ],
  "total": 42,
  "skip": 0,
  "limit": 20
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 未認証
- `403`: 権限不足

---

### 3.2 ユーザー作成

**エンドポイント**: `POST /api/v1/users`

**認証**: ✅ 必須（Admin のみ）

**リクエスト**:
```json
{
  "email": "newuser@example.com",
  "full_name": "田中花子",
  "department": "企画部",
  "password": "securepassword123",
  "role": "ANALYST"
}
```

**レスポンス**:
```json
{
  "id": "uuid",
  "email": "newuser@example.com",
  "full_name": "田中花子",
  "department": "企画部",
  "role": "ANALYST",
  "is_active": true,
  "created_at": "2025-11-01T15:00:00Z",
  "updated_at": "2025-11-01T15:00:00Z"
}
```

**バリデーション**:
- email: 有効なメール形式、重複チェック
- password: 8文字以上、複雑性チェック
- full_name: 1文字以上、100文字以下
- role: ANALYST | LEAD_PARTNER | IC_MEMBER | ADMIN

**エラーレスポンス**:
```json
{
  "detail": "このメールアドレスは既に登録されています"
}
```

**ステータスコード**:
- `201`: 作成成功
- `400`: バリデーションエラー
- `401`: 未認証
- `403`: 権限不足（Adminのみ）
- `409`: メール重複

---

### 3.3 ユーザー詳細取得

**エンドポイント**: `GET /api/v1/users/{user_id}`

**認証**: ✅ 必須（自分自身、またはLead Partner+）

**パスパラメータ**:
```
- user_id: UUID
```

**レスポンス**: UserResponse (3.1と同じ)

**ステータスコード**:
- `200`: 成功
- `401`: 未認証
- `403`: 権限不足
- `404`: ユーザーが見つかりません

---

### 3.4 ユーザー情報更新

**エンドポイント**: `PUT /api/v1/users/{user_id}`

**認証**: ✅ 必須（自分自身、またはAdmin）

**リクエスト**:
```json
{
  "full_name": "田中花子 改",
  "department": "企画部・新規事業開発課",
  "is_active": true
}
```

**レスポンス**: UserResponse

**RBAC規則**:
- ANALYST: 自分の情報のみ更新可（role変更不可）
- LEAD_PARTNER: 同じロール以下のユーザーを更新可
- ADMIN: すべてのユーザーを更新可

**ステータスコード**:
- `200`: 成功
- `400`: バリデーションエラー
- `401`: 未認証
- `403`: 権限不足
- `404`: ユーザーが見つかりません

---

### 3.5 ユーザー削除

**エンドポイント**: `DELETE /api/v1/users/{user_id}`

**認証**: ✅ 必須（Admin のみ）

**リクエスト**: なし

**レスポンス**:
```json
{
  "message": "ユーザーを削除しました",
  "user_id": "uuid"
}
```

**削除方式**: ソフトデリート（is_deleted フラグ）

**ステータスコード**:
- `200`: 成功
- `401`: 未認証
- `403`: 権限不足
- `404`: ユーザーが見つかりません

---

### 3.6 ユーザーロール変更

**エンドポイント**: `POST /api/v1/users/{user_id}/role`

**認証**: ✅ 必須（Admin のみ）

**リクエスト**:
```json
{
  "role": "LEAD_PARTNER"
}
```

**レスポンス**: UserResponse

**ロール階層**:
```
ADMIN
  ↓
IC_MEMBER
  ↓
LEAD_PARTNER
  ↓
ANALYST
```

**ルール**:
- 上位ロールへの変更は不可
- Adminは全ロール変更可

**ステータスコード**:
- `200`: 成功
- `400`: 無効なロール
- `401`: 未認証
- `403`: 権限不足
- `404`: ユーザーが見つかりません

---

### 3.7 利用可能ロール一覧

**エンドポイント**: `GET /api/v1/roles`

**認証**: ✅ 必須

**レスポンス**:
```json
{
  "roles": [
    {
      "role": "ANALYST",
      "description": "分析者：ケース作成・観察記録",
      "permissions": [
        "case:create",
        "observation:create",
        "observation:verify"
      ]
    },
    {
      "role": "LEAD_PARTNER",
      "description": "リード・パートナー：レビュー・承認",
      "permissions": [
        "case:read",
        "observation:verify",
        "conflict:resolve"
      ]
    },
    {
      "role": "IC_MEMBER",
      "description": "IC メンバー：監視・管理",
      "permissions": [
        "case:read",
        "user:manage",
        "report:generate"
      ]
    },
    {
      "role": "ADMIN",
      "description": "管理者：全権限",
      "permissions": ["*"]
    }
  ]
}
```

**ステータスコード**:
- `200`: 成功
- `401`: 未認証

---

## 4. エラーハンドリング

### 4.1 標準エラーレスポンス

```json
{
  "detail": "エラーメッセージ",
  "error_code": "USER_NOT_FOUND",
  "status_code": 404
}
```

### 4.2 エラーコード一覧

| コード | メッセージ | HTTP |
|--------|-----------|------|
| `USER_NOT_FOUND` | ユーザーが見つかりません | 404 |
| `DUPLICATE_EMAIL` | このメールアドレスは既に登録されています | 409 |
| `INVALID_PASSWORD` | パスワードが要件を満たしていません | 400 |
| `UNAUTHORIZED` | 認証が必要です | 401 |
| `FORBIDDEN` | このアクションを実行する権限がありません | 403 |
| `INVALID_ROLE` | 無効なロールです | 400 |

---

## 5. RBAC規則

### 5.1 ユーザー作成
- **許可**: Admin のみ
- **拒否**: 他のすべてのロール

### 5.2 ユーザー一覧表示
- **ANALYST**: 自分自身のみ
- **LEAD_PARTNER**: 同じロール以下のユーザー
- **IC_MEMBER**: すべてのユーザー
- **ADMIN**: すべてのユーザー

### 5.3 ユーザー更新
- **ANALYST**: 自分自身のみ（ロール変更不可）
- **LEAD_PARTNER**: 同じロール以下のユーザー
- **ADMIN**: すべてのユーザー

### 5.4 ユーザー削除
- **許可**: Admin のみ

### 5.5 ロール変更
- **許可**: Admin のみ

---

## 6. 実装チェックリスト

- [ ] UserCreate, UserUpdate, UserResponse スキーマ作成
- [ ] app/api/v1/users.py 作成（6つのエンドポイント）
- [ ] UserService 拡張（CRUD + ロール変更）
- [ ] RBAC チェック実装
- [ ] バリデーション実装
- [ ] 25+ ユニットテスト作成
- [ ] API統合テスト
- [ ] エラーハンドリング
- [ ] ログ記録

---

## 7. テスト計画

### 7.1 ユニットテスト (UserService)

```python
✅ create_user_success
✅ create_user_duplicate_email
✅ create_user_invalid_password
✅ get_user_by_id_success
✅ get_user_by_id_not_found
✅ list_users_analyst_rbac
✅ list_users_lead_partner_rbac
✅ update_user_success
✅ update_user_forbidden
✅ delete_user_soft_delete
✅ change_role_success
✅ change_role_unauthorized
```

### 7.2 API統合テスト

```python
✅ test_create_user_endpoint_admin
✅ test_create_user_endpoint_forbidden
✅ test_list_users_pagination
✅ test_update_user_endpoint
✅ test_delete_user_endpoint
✅ test_change_role_endpoint
✅ test_get_roles_endpoint
```

---

## 8. 実装予定スケジュール

| 日程 | タスク | 予定時間 |
|-----|--------|----------|
| Day 1 | スキーマ作成 + UserService拡張 | 2h |
| Day 1 | API エンドポイント実装 | 3h |
| Day 2 | ユニットテスト作成 | 2h |
| Day 2 | 統合テスト + デバッグ | 2h |
| Day 3 | ドキュメント完成 + レビュー | 1h |

**合計**: 約 10-12 時間

---

## 9. 関連ドキュメント

- `CODE_QUALITY_REPORT.md` - Week 4 品質レビュー
- `RBAC_DESIGN.md` - 権限管理詳細設計
- API Specification v1.0

---

**次ステップ**: 実装開始
