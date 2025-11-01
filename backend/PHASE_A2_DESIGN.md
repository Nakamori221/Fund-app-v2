# Phase A2: 監査ログ・パフォーマンス最適化 設計ドキュメント

**目的**: ユーザー管理 API の監査・追跡機能とパフォーマンス最適化を実装し、本番環境対応を強化

**実装期間**: Week 5 (推定 3-4日)

## 📋 概要

Phase A1 で実装した User CRUD API に対して、以下の機能を追加:

1. **監査ログシステム** - すべてのユーザー操作を自動記録
2. **パフォーマンス最適化** - インデックス、キャッシング、クエリ最適化
3. **セキュリティ強化** - ログイン試行記録、異常検知

---

## 🎯 実装目標

| 項目 | 目標 | 優先度 |
|------|------|--------|
| AuditLog テーブル | 作成・実装 | 🔴 高 |
| 自動監査記録 | すべての CRUD 操作を記録 | 🔴 高 |
| パフォーマンスインデックス | email, role, created_at など | 🟡 中 |
| クエリ最適化 | N+1 問題排除 | 🟡 中 |
| 監査ログ API | 一覧取得・フィルタリング | 🟠 低 |
| テストカバレッジ | 100% | 🔴 高 |

---

## 🗄️ データベーススキーマ

### AuditLog テーブル設計

```sql
CREATE TABLE audit_logs (
    -- 主キー
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),

    -- 操作情報
    user_id UUID NOT NULL REFERENCES users(id),
    action VARCHAR(50) NOT NULL,  -- create, read, update, delete, approve
    resource_type VARCHAR(50) NOT NULL,  -- user, case, observation
    resource_id UUID NOT NULL,

    -- 変更値
    old_values JSONB,  -- 更新前の値
    new_values JSONB,  -- 更新後の値

    -- メタデータ
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    ip_address VARCHAR(45),  -- IPv4 or IPv6
    user_agent VARCHAR(1000),

    -- インデックス用
    created_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP,
    is_deleted BOOLEAN DEFAULT FALSE,

    -- その他
    extra_data JSONB DEFAULT '{}'::jsonb
);

-- インデックス定義
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
CREATE INDEX idx_audit_logs_composite
    ON audit_logs(resource_type, resource_id, timestamp DESC);
```

### User テーブル拡張

```python
# 既存の User モデルに以下を追加
class User(Base):
    # ... 既存フィールド ...

    # 監査用フィールド
    last_login_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
    failed_login_attempts: int = Column(Integer, default=0)
    last_failed_login_at: Optional[datetime] = Column(DateTime(timezone=True), nullable=True)
```

---

## 📝 AuditLog スキーマ

### Pydantic スキーマ

```python
# app/models/schemas.py に追加

class AuditLogBase(BaseModel):
    """監査ログベース"""
    action: str = Field(..., description="操作: create, read, update, delete, approve")
    resource_type: str = Field(..., description="リソース種別: user, case, observation")
    resource_id: str = Field(..., description="リソースID")

    model_config = ConfigDict(from_attributes=True)


class AuditLogCreate(AuditLogBase):
    """監査ログ作成"""
    user_id: str = Field(..., description="操作ユーザーID")
    old_values: Optional[Dict[str, Any]] = Field(None, description="変更前の値")
    new_values: Optional[Dict[str, Any]] = Field(None, description="変更後の値")
    ip_address: Optional[str] = Field(None, description="IPアドレス")
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント")
    extra_data: Optional[Dict[str, Any]] = Field(None, description="追加データ")


class AuditLogResponse(AuditLogBase):
    """監査ログレスポンス"""
    id: str = Field(..., description="監査ログID")
    user_id: str = Field(..., description="操作ユーザーID")
    old_values: Optional[Dict[str, Any]] = Field(None, description="変更前の値")
    new_values: Optional[Dict[str, Any]] = Field(None, description="変更後の値")
    timestamp: datetime = Field(..., description="操作日時")
    ip_address: Optional[str] = Field(None, description="IPアドレス")
    user_agent: Optional[str] = Field(None, description="ユーザーエージェント")
    created_at: datetime = Field(..., description="作成日時")


class AuditLogListResponse(BaseModel):
    """監査ログ一覧レスポンス"""
    logs: List[AuditLogResponse] = Field(..., description="監査ログリスト")
    total: int = Field(..., description="総件数")
    skip: int = Field(..., description="スキップ数")
    limit: int = Field(..., description="取得数")
```

---

## 🔧 実装詳細

### 1. 監査ログサービス

**ファイル**: `app/services/audit_log_service.py`

```python
class AuditLogService:
    """監査ログサービス"""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        old_values: Optional[Dict] = None,
        new_values: Optional[Dict] = None,
        request: Optional[Request] = None,
    ) -> AuditLog:
        """操作を監査ログに記録"""
        # リクエストからメタデータ抽出
        ip_address = request.client.host if request else None
        user_agent = request.headers.get("user-agent") if request else None

        # ログ作成
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
        )

        db.add(log)
        await db.commit()
        await db.refresh(log)
        return log

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Tuple[List[AuditLog], int]:
        """監査ログを取得（フィルタリング対応）"""
        # クエリ構築
        query = select(AuditLog).filter(AuditLog.is_deleted == False)

        if user_id:
            query = query.filter(AuditLog.user_id == user_id)
        if resource_type:
            query = query.filter(AuditLog.resource_type == resource_type)
        if action:
            query = query.filter(AuditLog.action == action)
        if start_date:
            query = query.filter(AuditLog.timestamp >= start_date)
        if end_date:
            query = query.filter(AuditLog.timestamp <= end_date)

        # 総件数取得
        count_query = select(func.count()).select_from(AuditLog).filter(
            AuditLog.is_deleted == False
        )
        total = await db.scalar(count_query)

        # ログ取得
        query = query.order_by(AuditLog.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        logs = result.scalars().all()

        return logs, total
```

### 2. UserService への監査記録統合

**修正**: `app/services/user_service.py`

```python
# 各メソッドに監査ログを追加

async def create_user(db: AsyncSession, user_data: UserCreate, request: Optional[Request] = None) -> User:
    """ユーザー作成"""
    # ... 既存の実装 ...

    # 監査ログ記録
    await AuditLogService.log_action(
        db=db,
        user_id=current_user_id,  # システムユーザーまたはリクエストユーザー
        action="create",
        resource_type="user",
        resource_id=user.id,
        new_values=UserResponse.model_validate(user).model_dump(),
        request=request,
    )

    return user


async def update_user_by_admin(...) -> User:
    """ユーザー更新"""
    # 更新前の値を取得
    old_user = await UserService.get_user_by_id(db, user_id)
    old_values = UserResponse.model_validate(old_user).model_dump() if old_user else None

    # ... 既存の更新処理 ...

    # 監査ログ記録
    await AuditLogService.log_action(
        db=db,
        user_id=requester_id,
        action="update",
        resource_type="user",
        resource_id=user_id,
        old_values=old_values,
        new_values=UserResponse.model_validate(updated_user).model_dump(),
        request=request,
    )

    return updated_user


async def delete_user(...) -> User:
    """ユーザー削除"""
    user = await UserService.get_user_by_id(db, user_id)

    # ... 既存の削除処理 ...

    # 監査ログ記録
    await AuditLogService.log_action(
        db=db,
        user_id=requester_id,
        action="delete",
        resource_type="user",
        resource_id=user_id,
        old_values=UserResponse.model_validate(user).model_dump(),
        request=request,
    )

    return user
```

### 3. 監査ログ API エンドポイント

**ファイル**: `app/api/v1/audit_logs.py` (新規)

```python
@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="監査ログ一覧を取得",
    tags=["監査ログ"],
)
async def get_audit_logs(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    user_id: Optional[str] = Query(None),
    resource_type: Optional[str] = Query(None),
    action: Optional[str] = Query(None),
    start_date: Optional[datetime] = Query(None),
    end_date: Optional[datetime] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AuditLogListResponse:
    """監査ログを取得（ADMIN + IC_MEMBER のみ）"""
    # 認可チェック
    if current_user["role"] not in [UserRole.IC_MEMBER.value, UserRole.ADMIN.value]:
        raise HTTPException(status_code=403, detail="権限がありません")

    # ログ取得
    logs, total = await AuditLogService.get_logs(
        db=db,
        skip=skip,
        limit=limit,
        user_id=UUID(user_id) if user_id else None,
        resource_type=resource_type,
        action=action,
        start_date=start_date,
        end_date=end_date,
    )

    return AuditLogListResponse(
        logs=[AuditLogResponse.model_validate(log) for log in logs],
        total=total,
        skip=skip,
        limit=limit,
    )
```

---

## ⚡ パフォーマンス最適化

### 1. インデックス追加

```python
# 既存の User テーブルにインデックスを追加
class User(Base):
    __tablename__ = "users"

    # ... 既存カラム ...

    # インデックス定義
    __table_args__ = (
        Index('idx_users_email', 'email'),
        Index('idx_users_role', 'role'),
        Index('idx_users_created_at', 'created_at'),
        Index('idx_users_is_active', 'is_active'),
        Index('idx_users_composite', 'role', 'is_active'),
    )
```

### 2. クエリ最適化

```python
# N+1 問題の排除

# 修正前
users = await db.execute(select(User).where(...))
users = users.scalars().all()
for user in users:
    # user.cases に アクセス → 追加クエリ発生！
    cases = user.cases

# 修正後
users = await db.execute(
    select(User)
    .where(...)
    .options(selectinload(User.cases))  # eager loading
)
users = users.scalars().unique().all()
```

### 3. ページネーション最適化

```python
# offset/limit の代わりに cursor-based pagination

async def get_users_with_cursor(
    db: AsyncSession,
    cursor: Optional[str] = None,
    limit: int = 20,
) -> List[User]:
    """カーソルベースのページネーション"""
    query = select(User).order_by(User.id)

    if cursor:
        # base64 デコード
        cursor_id = UUID(base64.b64decode(cursor).decode())
        query = query.filter(User.id > cursor_id)

    query = query.limit(limit + 1)

    result = await db.execute(query)
    users = result.scalars().all()

    # 次のカーソル計算
    next_cursor = None
    if len(users) > limit:
        next_cursor = base64.b64encode(str(users[limit].id).encode()).decode()
        users = users[:limit]

    return users, next_cursor
```

---

## 🧪 テスト戦略

### テストファイル構成

1. **`tests/test_audit_log_service.py`** (新規) - 15テスト
   - ログ作成機能
   - フィルタリング機能
   - データ完全性

2. **`tests/test_audit_log_api.py`** (新規) - 10テスト
   - エンドポイント機能
   - 認可チェック
   - ページネーション

3. **`tests/test_performance.py`** (新規) - 8テスト
   - インデックス有効性
   - クエリ実行時間
   - メモリ使用量

4. **`tests/test_user_service_extended.py`** 修正 - 監査ログ検証追加

### テスト例

```python
@pytest.mark.asyncio
class TestAuditLogService:

    async def test_log_action_success(self, test_db):
        """監査ログ記録成功"""
        log = await AuditLogService.log_action(
            db=test_db,
            user_id=uuid4(),
            action="create",
            resource_type="user",
            resource_id=uuid4(),
            new_values={"email": "test@example.com"},
        )

        assert log.action == "create"
        assert log.resource_type == "user"
        assert log.new_values["email"] == "test@example.com"

    async def test_get_logs_with_filters(self, test_db):
        """ログ取得（フィルタリング）"""
        # ... テスト実装 ...

    async def test_audit_trail_completeness(self, test_db):
        """監査証跡の完全性"""
        # 各操作後にログが記録されていることを検証
```

---

## 📊 実装スケジュール

| 段階 | 実装内容 | 予定日数 |
|------|---------|---------|
| 1 | DB スキーマ設計・マイグレーション | 0.5日 |
| 2 | AuditLogService 実装 | 1日 |
| 3 | UserService に監査記録統合 | 1日 |
| 4 | 監査ログ API エンドポイント | 0.5日 |
| 5 | パフォーマンス最適化 | 0.5日 |
| 6 | テスト実装 | 1.5日 |
| 7 | ドキュメント・コミット | 0.5日 |
| **合計** | | **5日** |

---

## ✅ 完了基準

- [ ] AuditLog テーブル作成
- [ ] AuditLogService 実装
- [ ] すべての CRUD 操作に監査記録を統合
- [ ] 監査ログ API 実装
- [ ] インデックス追加・最適化
- [ ] テストカバレッジ 100% (33テスト)
- [ ] ドキュメント完備
- [ ] Git コミット

---

## 🔐 セキュリティ考慮

### ログへのアクセス制御
- ✅ ADMIN・IC_MEMBER のみ監査ログ閲覧可
- ✅ 他ユーザーの操作ログは隠蔽

### ログ改ざん防止
- ✅ ログは追記のみ（削除不可）
- ✅ is_deleted フラグで論理削除
- ✅ タイムスタンプは不変

### プライバシー保護
- ✅ パスワードハッシュは記録しない
- ✅ 個人情報は最小化
- ✅ GDPR コンプライアンス対応

---

## 📚 参考資料

- PostgreSQL インデックス: https://www.postgresql.org/docs/current/indexes.html
- SQLAlchemy eager loading: https://docs.sqlalchemy.org/
- 監査ログベストプラクティス: ISO 27001

---

**次のステップ**: 実装開始前に上記設計内容を確認し、フィードバックをお願いします。
