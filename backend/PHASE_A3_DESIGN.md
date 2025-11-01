# Phase A3: パフォーマンス最適化・データベース設計

**目的**: User API のパフォーマンスを大幅に改善し、本番環境での高速処理を実現

**実装期間**: Week 6 (推定 3-4日)

---

## 📋 概要

Phase A2 で実装した監査ログシステムにより、全操作が記録されるようになった。
Phase A3 では、以下のパフォーマンス改善施策を実装する:

1. **インデックス最適化** - ホットなクエリに効果的なインデックスを追加
2. **クエリ最適化** - N+1 問題の排除、Eager Loading の導入
3. **ページネーション最適化** - Cursor-based pagination の実装
4. **キャッシング戦略** - Redis を活用した応答キャッシング

---

## 🎯 実装目標

| 項目 | 目標 | 優先度 | 推定時間 |
|------|------|--------|---------|
| User テーブルインデックス | 5つのインデックス追加 | 🔴 高 | 4h |
| AuditLog テーブルインデックス | 4つのインデックス追加 | 🔴 高 | 3h |
| Eager Loading 導入 | Service 層での最適化 | 🟡 中 | 3h |
| Cursor-based Pagination | 新しいページネーション実装 | 🟡 中 | 4h |
| Redis キャッシング | 頻繁にアクセスされるデータのキャッシング | 🟠 低 | 4h |
| パフォーマンステスト | 8つのテストケース実装 | 🔴 高 | 3h |
| ドキュメント・最適化報告書 | パフォーマンス改善記録 | 🟡 中 | 2h |

---

## 🗄️ インデックス設計

### 1. User テーブルのインデックス

```sql
-- 既存インデックス確認
-- PRIMARY KEY: id
-- UNIQUE: email

-- 新規追加インデックス
CREATE INDEX idx_users_role ON users(role);
CREATE INDEX idx_users_created_at ON users(created_at DESC);
CREATE INDEX idx_users_is_active ON users(is_active);
-- 複合インデックス: 一般的なクエリの最適化
CREATE INDEX idx_users_role_active ON users(role, is_active);
CREATE INDEX idx_users_created_active ON users(created_at DESC, is_active);
```

**インデックス選択理由**:
- `role` - ロール別ユーザー一覧フィルタリングで頻出
- `created_at DESC` - 最新ユーザー取得で頻出
- `is_active` - 有効ユーザーフィルタで頻出
- 複合インデックス - `WHERE role = ? AND is_active = ?` のような複合条件クエリの最適化

### 2. AuditLog テーブルのインデックス

```sql
-- 既存インデックス確認
-- PRIMARY KEY: id

-- 新規追加インデックス
CREATE INDEX idx_audit_logs_user_id ON audit_logs(user_id);
CREATE INDEX idx_audit_logs_resource_id ON audit_logs(resource_id);
CREATE INDEX idx_audit_logs_timestamp ON audit_logs(timestamp DESC);
CREATE INDEX idx_audit_logs_action ON audit_logs(action);
-- 複合インデックス: リソース別操作履歴取得の最適化
CREATE INDEX idx_audit_logs_resource_timestamp ON audit_logs(resource_type, resource_id, timestamp DESC);
```

**インデックス選択理由**:
- `user_id` - ユーザー別操作履歴取得
- `resource_id` - リソース別操作履歴取得
- `timestamp DESC` - 最新ログ取得（ソート効率化）
- `action` - アクション別集計で頻出
- 複合インデックス - `WHERE resource_type = ? AND resource_id = ? ORDER BY timestamp DESC` の最適化

### 3. SQLAlchemy での インデックス定義

```python
# app/models/database.py

from sqlalchemy import Index, Column, String, DateTime, Boolean, Integer

class User(Base):
    __tablename__ = "users"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    email: Mapped[str] = mapped_column(unique=True, index=True)
    full_name: Mapped[str]
    hashed_password: Mapped[str]
    role: Mapped[UserRole] = mapped_column(default=UserRole.ANALYST)
    is_active: Mapped[bool] = mapped_column(default=True, index=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow)

    # テーブルレベルのインデックス定義
    __table_args__ = (
        Index('idx_users_role', 'role'),
        Index('idx_users_created_at', 'created_at', postgresql_using='DESC'),
        Index('idx_users_role_active', 'role', 'is_active'),
        Index('idx_users_created_active', 'created_at', 'is_active', postgresql_using='DESC'),
    )

class AuditLog(Base):
    __tablename__ = "audit_logs"

    id: Mapped[UUID] = mapped_column(primary_key=True, default=uuid4)
    user_id: Mapped[UUID] = mapped_column(ForeignKey("users.id"))
    action: Mapped[str] = mapped_column(index=True)
    resource_type: Mapped[str]
    resource_id: Mapped[UUID]
    old_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    new_values: Mapped[Optional[dict]] = mapped_column(JSON, nullable=True)
    timestamp: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    ip_address: Mapped[Optional[str]]
    user_agent: Mapped[Optional[str]]
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=datetime.utcnow)
    is_deleted: Mapped[bool] = mapped_column(default=False)
    extra_data: Mapped[Optional[dict]] = mapped_column(JSON, default=dict)

    # テーブルレベルのインデックス定義
    __table_args__ = (
        Index('idx_audit_logs_user_id', 'user_id'),
        Index('idx_audit_logs_resource_id', 'resource_id'),
        Index('idx_audit_logs_timestamp', 'timestamp', postgresql_using='DESC'),
        Index('idx_audit_logs_resource_timestamp', 'resource_type', 'resource_id', 'timestamp', postgresql_using='DESC'),
    )
```

---

## ⚡ Eager Loading と N+1 問題の解決

### 現在のコード（N+1 問題あり）

```python
# Service 層
async def get_all_users(db: AsyncSession) -> List[User]:
    """ユーザー一覧を取得"""
    query = select(User).where(User.is_active == True)
    result = await db.execute(query)
    return result.scalars().all()

# API 層
@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    users = await UserService.get_all_users(db)

    # ここで user.audit_logs にアクセス → N+1 問題発生！
    response = [
        {
            "id": user.id,
            "email": user.email,
            "audit_logs": user.audit_logs  # 各ユーザーで追加クエリ発生
        }
        for user in users
    ]
    return response
```

### 改善後（Eager Loading）

```python
# Service 層で Eager Loading を導入
async def get_all_users(db: AsyncSession) -> List[User]:
    """ユーザー一覧を取得（relationships を eager load）"""
    from sqlalchemy.orm import selectinload

    query = (
        select(User)
        .where(User.is_active == True)
        .options(selectinload(User.audit_logs))  # 関連データを先読み
        .order_by(User.created_at.desc())
    )
    result = await db.execute(query)
    # unique() は selectinload 使用時に必須（重複除外）
    return result.scalars().unique().all()

# API 層
@app.get("/users")
async def list_users(db: AsyncSession = Depends(get_db)):
    users = await UserService.get_all_users(db)

    # ここで user.audit_logs にアクセス → 追加クエリなし！
    response = [
        {
            "id": user.id,
            "email": user.email,
            "audit_logs": user.audit_logs
        }
        for user in users
    ]
    return response
```

### 最適化結果

- **改善前**: N ユーザーで N+1 クエリ（1 + N）
- **改善後**: 2 クエリ（1 for users + 1 for audit_logs）
- **改善率**: 約 50% のクエリ削減（N=100 の場合）

---

## 📄 Cursor-based Pagination の実装

### 現在のコード（Offset-based Pagination）

```python
# Service 層
async def get_users_paginated(
    db: AsyncSession,
    skip: int = 0,
    limit: int = 20,
) -> Tuple[List[User], int]:
    """Offset-based pagination"""
    query = select(User).where(User.is_active == True)
    total = await db.scalar(select(func.count()).select_from(User))

    result = await db.execute(
        query.order_by(User.created_at.desc()).offset(skip).limit(limit + 1)
    )
    return result.scalars().all(), total

# API 層
@app.get("/users")
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
):
    users, total = await UserService.get_users_paginated(db, skip, limit)
    return {"users": users, "total": total, "skip": skip, "limit": limit}
```

**問題点**:
- `OFFSET n` は n 行をスキップする必要があるため、大きな n では遅い
- データ追加・削除時に順序がズレる可能性

### 改善後（Cursor-based Pagination）

```python
import base64
from typing import Optional, Tuple

class CursorPaginationParams:
    """Cursor-based pagination パラメータ"""

    @staticmethod
    def encode_cursor(user_id: UUID) -> str:
        """UUID を Base64 エンコード"""
        return base64.b64encode(str(user_id).encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> UUID:
        """Base64 デコード → UUID"""
        return UUID(base64.b64decode(cursor).decode())

# Service 層
async def get_users_with_cursor(
    db: AsyncSession,
    cursor: Optional[str] = None,
    limit: int = 20,
) -> Tuple[List[User], Optional[str]]:
    """Cursor-based pagination"""
    query = select(User).where(User.is_active == True).order_by(User.created_at.desc(), User.id)

    if cursor:
        cursor_created_at, cursor_id = CursorPaginationParams.decode_cursor(cursor)
        # 前回の最後のレコードより後ろを取得
        query = query.filter(
            (User.created_at < cursor_created_at) |
            ((User.created_at == cursor_created_at) & (User.id > cursor_id))
        )

    # limit + 1 個取得（次カーソルがあるかを確認）
    query = query.limit(limit + 1)
    result = await db.execute(query)
    users = result.scalars().all()

    # 次のカーソルを計算
    next_cursor = None
    if len(users) > limit:
        last_user = users[limit - 1]
        next_cursor = CursorPaginationParams.encode_cursor(
            (last_user.created_at, last_user.id)
        )
        users = users[:limit]

    return users, next_cursor

# API 層
@app.get("/users")
async def list_users(
    cursor: Optional[str] = Query(None),
    limit: int = Query(20, ge=1, le=100),
):
    users, next_cursor = await UserService.get_users_with_cursor(db, cursor, limit)
    return {
        "users": users,
        "next_cursor": next_cursor,
        "limit": limit,
    }
```

**改善効果**:
- **クエリ性能**: `OFFSET` なし → 常に O(n) instead of O(n + offset)
- **データ一貫性**: Cursor は不変 → データ追加時も順序が保証される
- **API シンプルさ**: `?limit=20&cursor=abc...` の2パラメータで十分

---

## 💾 Redis キャッシング戦略

### 実装対象

キャッシング対象：
1. **ユーザープロファイル** - TTL: 300秒（頻繁にアクセスされる）
2. **ユーザー一覧（最新100件）** - TTL: 60秒（変更頻度が高い）
3. **監査ログ統計情報** - TTL: 3600秒（変更頻度が低い）

### Redis キャッシング実装

```python
# app/services/cache_service.py

import redis.asyncio as redis
import json
from typing import Optional, Any

class CacheService:
    """Redis キャッシングサービス"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Any]:
        """キャッシュから取得"""
        value = await self.redis.get(key)
        if value:
            return json.loads(value)
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """キャッシュに設定"""
        await self.redis.setex(
            key,
            ttl,
            json.dumps(value, default=str)  # UUID などの シリアライザー対応
        )
        return True

    async def delete(self, key: str) -> int:
        """キャッシュを削除"""
        return await self.redis.delete(key)

    async def invalidate_pattern(self, pattern: str) -> int:
        """パターンマッチするキャッシュを全削除"""
        keys = await self.redis.keys(pattern)
        if keys:
            return await self.redis.delete(*keys)
        return 0

# app/services/user_service.py に統合

class UserService:

    @staticmethod
    async def get_user_by_id(db: AsyncSession, user_id: UUID, cache_service: CacheService = None) -> Optional[User]:
        """ユーザーを ID で取得（キャッシュ付き）"""
        cache_key = f"user:{user_id}"

        # キャッシュから試す
        if cache_service:
            cached_user = await cache_service.get(cache_key)
            if cached_user:
                return User(**cached_user)

        # DB から取得
        query = select(User).where(User.id == user_id)
        result = await db.execute(query)
        user = result.scalar_one_or_none()

        # キャッシュに保存
        if user and cache_service:
            await cache_service.set(
                cache_key,
                user.__dict__,
                ttl=300
            )

        return user

    @staticmethod
    async def update_user_by_admin(
        db: AsyncSession,
        user_id: UUID,
        user_data: UserUpdate,
        cache_service: CacheService = None,
    ) -> Optional[User]:
        """ユーザーを更新（キャッシュ無効化付き）"""
        user = await UserService.get_user_by_id(db, user_id, cache_service)
        if not user:
            return None

        # ユーザーを更新
        for field, value in user_data.model_dump(exclude_unset=True).items():
            setattr(user, field, value)

        db.add(user)
        await db.commit()
        await db.refresh(user)

        # キャッシュを無効化
        if cache_service:
            cache_key = f"user:{user_id}"
            await cache_service.delete(cache_key)
            # 一覧キャッシュも無効化
            await cache_service.invalidate_pattern("users:list:*")

        return user
```

### キャッシュキーの戦略

```
user:{user_id}                              # 単一ユーザー（TTL: 300s）
users:list:{page}                           # ユーザー一覧（TTL: 60s）
audit:stats:by_action                       # 統計情報（TTL: 3600s）
audit:logs:{resource_type}:{resource_id}    # リソース別操作履歴（TTL: 600s）
```

---

## 🧪 パフォーマンステスト

### テストファイル: `tests/test_performance.py`

```python
import pytest
import time
from unittest.mock import AsyncMock, patch

class TestDatabasePerformance:
    """データベースパフォーマンステスト"""

    @pytest.mark.asyncio
    async def test_index_user_role_performance(self, test_db):
        """User テーブルの role インデックスがクエリを高速化"""
        # テストデータ作成（100ユーザー）
        for i in range(100):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                full_name=f"User {i}",
                hashed_password="hash",
                role=UserRole.ANALYST if i % 2 == 0 else UserRole.ADMIN,
            )
            test_db.add(user)
        await test_db.commit()

        # インデックスを活用したクエリ
        start = time.time()
        query = select(User).where(User.role == UserRole.ANALYST)
        result = await test_db.execute(query)
        users = result.scalars().all()
        elapsed = time.time() - start

        assert len(users) == 50
        assert elapsed < 0.1  # 100ms 以下

    @pytest.mark.asyncio
    async def test_eager_loading_reduces_queries(self, test_db):
        """Eager Loading により N+1 問題を排除"""
        # テストユーザーと監査ログを作成
        user = User(id=uuid4(), email="test@example.com", ...)
        test_db.add(user)
        await test_db.commit()

        for i in range(10):
            log = AuditLog(
                id=uuid4(),
                user_id=user.id,
                action="create",
                resource_type="user",
                resource_id=uuid4(),
            )
            test_db.add(log)
        await test_db.commit()

        # クエリカウント
        query_count = 0
        original_execute = test_db.execute

        async def counted_execute(*args, **kwargs):
            nonlocal query_count
            query_count += 1
            return await original_execute(*args, **kwargs)

        with patch.object(test_db, 'execute', counted_execute):
            # Eager Loading なし
            query = select(User).where(User.id == user.id)
            result = await test_db.execute(query)
            u = result.scalar_one()
            _ = u.audit_logs  # N+1 問題

            # Eager Loading あり
            query = select(User).where(User.id == user.id).options(selectinload(User.audit_logs))
            result = await test_db.execute(query)
            u = result.scalar_one()
            _ = u.audit_logs  # キャッシュから取得

    @pytest.mark.asyncio
    async def test_cursor_pagination_consistency(self, test_db):
        """Cursor-based pagination がデータ追加時に一貫性を保つ"""
        # 初期データ作成
        for i in range(30):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                full_name=f"User {i}",
            )
            test_db.add(user)
        await test_db.commit()

        # ページ1を取得
        users_page1, cursor1 = await UserService.get_users_with_cursor(test_db, limit=10)
        assert len(users_page1) == 10

        # 新規ユーザーを追加
        new_user = User(
            id=uuid4(),
            email="newuser@example.com",
            full_name="New User",
        )
        test_db.add(new_user)
        await test_db.commit()

        # ページ2を取得（新規ユーザー追加後）
        users_page2, cursor2 = await UserService.get_users_with_cursor(test_db, cursor=cursor1, limit=10)
        assert len(users_page2) == 10

        # ページ1 と ページ2 に重複がないことを確認
        page1_ids = {u.id for u in users_page1}
        page2_ids = {u.id for u in users_page2}
        assert len(page1_ids & page2_ids) == 0

    @pytest.mark.asyncio
    async def test_redis_cache_hit_rate(self, test_db, cache_service):
        """Redis キャッシュが効果的に機能"""
        user = User(
            id=uuid4(),
            email="cache@example.com",
            full_name="Cache Test User",
        )
        test_db.add(user)
        await test_db.commit()

        # 1回目：DB から取得
        start1 = time.time()
        user1 = await UserService.get_user_by_id(test_db, user.id, cache_service)
        time1 = time.time() - start1

        # 2回目：キャッシュから取得
        start2 = time.time()
        user2 = await UserService.get_user_by_id(test_db, user.id, cache_service)
        time2 = time.time() - start2

        # キャッシュ取得の方が圧倒的に高速
        assert time2 < time1 * 0.5  # キャッシュは 50% 以上高速
        assert user1.id == user2.id
```

---

## 📊 実装スケジュール

| 段階 | 実装内容 | 予定日数 | ステータス |
|------|---------|---------|----------|
| 1 | インデックス設計・マイグレーション | 0.5日 | 📋 計画中 |
| 2 | Eager Loading 実装 | 0.5日 | 📋 計画中 |
| 3 | Cursor-based Pagination 実装 | 1日 | 📋 計画中 |
| 4 | Redis キャッシング実装 | 1日 | 📋 計画中 |
| 5 | パフォーマンステスト実装 | 1日 | 📋 計画中 |
| 6 | 性能測定・ベンチマーク | 0.5日 | 📋 計画中 |
| 7 | ドキュメント・最適化報告書 | 0.5日 | 📋 計画中 |
| **合計** | | **5日** | |

---

## ✅ 完了基準

- [ ] 5つの User インデックスを追加
- [ ] 4つの AuditLog インデックスを追加
- [ ] UserService に Eager Loading を導入
- [ ] Cursor-based Pagination を実装
- [ ] Redis キャッシングを実装
- [ ] 8つのパフォーマンステストが全て PASS
- [ ] ベンチマーク結果を測定・報告
- [ ] ドキュメント完備
- [ ] Git コミット

---

## 🔐 セキュリティ考慮

### キャッシング時の注意点
- ✅ キャッシュキーに認証情報を含めない
- ✅ 機密情報（パスワード）はキャッシュしない
- ✅ キャッシュ有効期限を設定して古い情報を排除
- ✅ ユーザー削除時にキャッシュを無効化

### インデックス設計時の注意点
- ✅ 不要なインデックスを避ける（ストレージ・更新性能への影響）
- ✅ 複合インデックスの列順序を最適化
- ✅ 定期的なインデックス分析・メンテナンス

---

## 📚 参考資料

- PostgreSQL インデックス: https://www.postgresql.org/docs/current/indexes.html
- SQLAlchemy Eager Loading: https://docs.sqlalchemy.org/en/20/orm/loading_columns.html
- Redis キャッシング: https://redis.io/
- Cursor-based Pagination: https://slack.engineering/a-little-thing-about-pagination/

---

## 🚀 次のステップ

1. **インデックス追加**: マイグレーションファイルを作成し、必要なインデックスを追加
2. **Service 層改善**: Eager Loading と Cursor-based Pagination を実装
3. **キャッシング統合**: Redis を導入し、頻繁にアクセスされるデータをキャッシング
4. **パフォーマンステスト**: 性能測定とボトルネック分析を実施
5. **本番環境対応**: 最適化結果をドキュメント化し、本番環境へのデプロイ準備

---

*Design Document Created: 2025年 Week 6*
*Next: Phase A3 Implementation Planning*
