# Phase A3: パフォーマンス最適化 実装ガイド

**ステータス**: 🚀 実装開始
**開始日**: 2025年 Week 6
**目標完了日**: 3-4日

---

## 📋 実装概要

Phase A3 では、以下の4つのパフォーマンス改善を段階的に実装します:

1. **✅ Step 1**: インデックス追加（完了）
2. **⏳ Step 2**: Eager Loading 実装
3. **📋 Step 3**: Cursor-based Pagination 実装
4. **📋 Step 4**: Redis キャッシング実装
5. **📋 Step 5**: パフォーマンステスト実装

---

## ✅ Step 1: インデックス追加（完了）

### 実施内容
- ファイル: `migrations/versions/002_phase_a3_performance_indexes.py`
- User テーブル: 4つの新規インデックス追加
- AuditLog テーブル: 4つの新規インデックス追加

### 追加されたインデックス

**User テーブル**:
```
- idx_users_role                    (単一列)
- idx_users_created_at_desc         (単一列、DESC順)
- idx_users_role_is_active          (複合)
- idx_users_created_at_is_active    (複合、DESC順)
```

**AuditLog テーブル**:
```
- idx_audit_logs_resource_id                    (単一列)
- idx_audit_logs_action                         (単一列)
- idx_audit_logs_resource_type_timestamp        (複合、DESC順)
- idx_audit_logs_is_deleted_timestamp           (複合)
```

### マイグレーション実行方法
```bash
# Alembic を使用してマイグレーション実行
alembic upgrade head

# または、直接 Python で実行
python -m app.database
```

---

## ⏳ Step 2: Eager Loading 実装

### 目的
N+1 クエリ問題を排除し、関連データを効率的に取得

### 実装対象ファイル
- `app/services/user_service.py` - User Service の最適化

### 実装方法

#### 2.1 UserService の最適化

```python
# app/services/user_service.py

from sqlalchemy.orm import selectinload

class UserService:

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: UUID,
        include_audit_logs: bool = False
    ) -> Optional[User]:
        """ユーザーを ID で取得（Eager Loading 対応）"""
        query = select(User).where(User.id == user_id)

        # オプション: 監査ログも一緒に取得
        if include_audit_logs:
            query = query.options(selectinload(User.audit_logs))

        result = await db.execute(query)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_all_users(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        include_audit_logs: bool = False
    ) -> Tuple[List[User], int]:
        """全ユーザーを取得（Eager Loading 対応）"""
        query = select(User).where(User.is_active == True)

        # 監査ログも eager load
        if include_audit_logs:
            query = query.options(selectinload(User.audit_logs))

        # 総件数を取得
        count_query = select(func.count()).select_from(User).where(User.is_active == True)
        total = await db.scalar(count_query)

        # ページネーション + ソート
        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        # unique() は selectinload 使用時に必須
        users = result.scalars().unique().all()

        return users, total

    @staticmethod
    async def get_users_by_role(
        db: AsyncSession,
        role: UserRole,
        skip: int = 0,
        limit: int = 20
    ) -> Tuple[List[User], int]:
        """ロール別にユーザーを取得"""
        query = select(User).where(
            (User.role == role) & (User.is_active == True)
        )

        count_query = select(func.count()).select_from(User).where(
            (User.role == role) & (User.is_active == True)
        )
        total = await db.scalar(count_query)

        query = query.order_by(User.created_at.desc()).offset(skip).limit(limit)

        result = await db.execute(query)
        users = result.scalars().all()

        return users, total
```

#### 2.2 API 層での使用例

```python
# app/api/v1/users.py

@router.get(
    "/",
    response_model=UserListResponse,
    summary="ユーザー一覧を取得",
    tags=["ユーザー管理"],
)
async def list_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: Optional[UserRole] = Query(None),
    include_logs: bool = Query(False),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserListResponse:
    """ユーザー一覧を取得

    - `include_logs=true` を指定すると、各ユーザーの監査ログも取得
    - Eager Loading により N+1 問題を回避
    """
    if role:
        users, total = await UserService.get_users_by_role(
            db=db,
            role=role,
            skip=skip,
            limit=limit
        )
    else:
        users, total = await UserService.get_all_users(
            db=db,
            skip=skip,
            limit=limit,
            include_audit_logs=include_logs
        )

    return UserListResponse(
        users=[UserResponse.model_validate(user) for user in users],
        total=total,
        skip=skip,
        limit=limit,
    )
```

### テスト（Step 5 で実装）
- N+1 クエリが排除されることを確認
- クエリ数が期待値以下であることを検証

---

## 📋 Step 3: Cursor-based Pagination 実装

### 目的
大規模なデータセットでのオフセットベースページネーションのパフォーマンス低下を解決

### 実装ファイル
- `app/services/pagination_service.py` (新規)
- `app/api/v1/users.py` (修正)

### 3.1 PaginationService の作成

```python
# app/services/pagination_service.py

import base64
import json
from typing import Optional, Tuple, Generic, TypeVar, List
from uuid import UUID
from datetime import datetime

T = TypeVar('T')

class CursorPaginationParams:
    """Cursor-based pagination のパラメータエンコード/デコード"""

    @staticmethod
    def encode_cursor(**kwargs) -> str:
        """複数パラメータを Base64 エンコード"""
        data = json.dumps(kwargs, default=str)
        return base64.b64encode(data.encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> dict:
        """Base64 デコード → 辞書"""
        data = base64.b64decode(cursor).decode()
        return json.loads(data)


class PaginationService:
    """Cursor-based pagination サービス"""

    @staticmethod
    def encode_cursor(created_at: datetime, user_id: UUID) -> str:
        """Cursor をエンコード（created_at + user_id）"""
        return CursorPaginationParams.encode_cursor(
            created_at=created_at.isoformat(),
            user_id=str(user_id)
        )

    @staticmethod
    def decode_cursor(cursor: str) -> Tuple[datetime, UUID]:
        """Cursor をデコード"""
        data = CursorPaginationParams.decode_cursor(cursor)
        return (
            datetime.fromisoformat(data["created_at"]),
            UUID(data["user_id"])
        )

    @staticmethod
    async def get_paginated_results(
        db: AsyncSession,
        query,
        model_class,
        cursor: Optional[str] = None,
        limit: int = 20,
        order_by = None
    ) -> Tuple[List, Optional[str]]:
        """汎用 Cursor-based pagination"""
        # Cursor から前回の位置を取得
        if cursor:
            # Cursor から値を抽出して、フィルタを適用
            # このロジックは model_class と order_by に依存
            pass

        # limit + 1 個取得（次ページの存在確認）
        query = query.limit(limit + 1)
        result = await db.execute(query)
        items = result.scalars().all()

        # 次のカーソルを計算
        next_cursor = None
        if len(items) > limit:
            last_item = items[limit - 1]
            next_cursor = PaginationService.encode_cursor(
                created_at=last_item.created_at,
                user_id=last_item.id
            )
            items = items[:limit]

        return items, next_cursor
```

### 3.2 API エンドポイントの修正

```python
# app/api/v1/users.py - 修正

from app.services.pagination_service import PaginationService

@router.get(
    "/",
    response_model=UserListResponse,
    summary="ユーザー一覧を取得（Cursor-based Pagination）",
    tags=["ユーザー管理"],
)
async def list_users(
    cursor: Optional[str] = Query(None, description="前ページの最後のカーソル"),
    limit: int = Query(20, ge=1, le=100, description="取得件数"),
    role: Optional[UserRole] = Query(None),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> Dict[str, Any]:
    """ユーザー一覧を取得（Cursor-based Pagination）

    レスポンス例:
    ```json
    {
        "users": [...],
        "next_cursor": "eyJjcmVhdGVkX2F0IjogIjIwMjUtMDEtMDFUMDA6MDA6MDAiLCAidXNlcl9pZCI6ICIxMjM0NTY3OC1hYmNkLWVmZ2gtaWprbCJ9",
        "has_more": true,
        "limit": 20
    }
    ```
    """
    # クエリを構築
    query = select(User).where(User.is_active == True)

    if role:
        query = query.where(User.role == role)

    # Cursor から前回の位置を取得
    if cursor:
        try:
            created_at, user_id = PaginationService.decode_cursor(cursor)
            # 前回の最後のレコードより後ろを取得
            query = query.filter(
                (User.created_at < created_at) |
                ((User.created_at == created_at) & (User.id > user_id))
            )
        except Exception:
            raise HTTPException(status_code=400, detail="Invalid cursor")

    # ソート順序（新しい順）
    query = query.order_by(User.created_at.desc(), User.id)

    # limit + 1 個取得
    query = query.limit(limit + 1)

    result = await db.execute(query)
    users = result.scalars().all()

    # 次のカーソルを計算
    next_cursor = None
    has_more = False
    if len(users) > limit:
        has_more = True
        last_user = users[limit - 1]
        next_cursor = PaginationService.encode_cursor(
            created_at=last_user.created_at,
            user_id=last_user.id
        )
        users = users[:limit]

    return {
        "users": [UserResponse.model_validate(user) for user in users],
        "next_cursor": next_cursor,
        "has_more": has_more,
        "limit": limit,
    }
```

### メリット
- **パフォーマンス**: `OFFSET` なし → 常に O(limit) 時間で結果取得
- **一貫性**: Cursor は不変 → データ追加/削除時も順序が保証
- **大規模データセット対応**: 数百万レコードでも高速

---

## 📋 Step 4: Redis キャッシング実装

### 目的
頻繁にアクセスされるデータ（ユーザープロファイル、統計情報）をメモリにキャッシング

### 前提条件
```bash
# Redis をインストール・起動
# Docker を使用する場合:
docker run -d -p 6379:6379 redis:latest
```

### 実装ファイル
- `app/services/cache_service.py` (新規)
- `app/services/user_service.py` (修正)

### 4.1 CacheService の実装

```python
# app/services/cache_service.py

import redis.asyncio as redis
import json
from typing import Optional, Any, Dict
import logging

logger = logging.getLogger(__name__)

class CacheService:
    """Redis キャッシングサービス"""

    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client

    async def get(self, key: str) -> Optional[Dict[str, Any]]:
        """キャッシュから取得"""
        try:
            value = await self.redis.get(key)
            if value:
                return json.loads(value)
        except Exception as e:
            logger.warning(f"Cache get error for key {key}: {e}")
        return None

    async def set(self, key: str, value: Any, ttl: int = 300) -> bool:
        """キャッシュに設定"""
        try:
            await self.redis.setex(
                key,
                ttl,
                json.dumps(value, default=str)
            )
            return True
        except Exception as e:
            logger.warning(f"Cache set error for key {key}: {e}")
            return False

    async def delete(self, key: str) -> int:
        """キャッシュを削除"""
        try:
            return await self.redis.delete(key)
        except Exception as e:
            logger.warning(f"Cache delete error for key {key}: {e}")
            return 0

    async def invalidate_pattern(self, pattern: str) -> int:
        """パターンマッチするすべてのキャッシュを削除"""
        try:
            keys = await self.redis.keys(pattern)
            if keys:
                return await self.redis.delete(*keys)
            return 0
        except Exception as e:
            logger.warning(f"Cache invalidate pattern error: {e}")
            return 0

    async def clear_all(self) -> bool:
        """すべてのキャッシュをクリア"""
        try:
            await self.redis.flushdb()
            return True
        except Exception as e:
            logger.warning(f"Cache clear error: {e}")
            return False
```

### 4.2 キャッシュキー戦略

```
キャッシュキー命名規則:
{namespace}:{entity_type}:{identifier}:{variant}

例:
- user:profile:{user_id}                          # 単一ユーザープロファイル (TTL: 300s)
- user:list:active:{role}                         # アクティブユーザー一覧 (TTL: 60s)
- audit:stats:by_action                           # 統計情報 (TTL: 3600s)
- audit:logs:{resource_type}:{resource_id}        # リソース別操作履歴 (TTL: 600s)
```

### 4.3 UserService への キャッシング統合

```python
# app/services/user_service.py - 修正

from app.services.cache_service import CacheService

class UserService:

    @staticmethod
    async def get_user_by_id_cached(
        db: AsyncSession,
        user_id: UUID,
        cache_service: Optional[CacheService] = None
    ) -> Optional[User]:
        """ユーザーを ID で取得（キャッシュ付き）"""
        cache_key = f"user:profile:{user_id}"

        # Step 1: キャッシュから試す
        if cache_service:
            cached = await cache_service.get(cache_key)
            if cached:
                logger.info(f"Cache hit: {cache_key}")
                # キャッシュされたデータから User オブジェクト再構築
                user = User(**cached)
                return user

        # Step 2: DB から取得
        user = await UserService.get_user_by_id(db, user_id)

        # Step 3: キャッシュに保存
        if user and cache_service:
            user_dict = {
                "id": str(user.id),
                "email": user.email,
                "full_name": user.full_name,
                "role": user.role.value,
                "is_active": user.is_active,
                "created_at": user.created_at.isoformat(),
                "updated_at": user.updated_at.isoformat(),
            }
            await cache_service.set(cache_key, user_dict, ttl=300)
            logger.info(f"Cache set: {cache_key}")

        return user

    @staticmethod
    async def update_user_by_admin_cached(
        db: AsyncSession,
        user_id: UUID,
        user_data: UserUpdate,
        cache_service: Optional[CacheService] = None,
        requester_id: Optional[UUID] = None,
    ) -> Optional[User]:
        """ユーザーを更新（キャッシュ無効化付き）"""
        # ユーザーを更新
        user = await UserService.update_user_by_admin(
            db=db,
            user_id=user_id,
            user_data=user_data,
            requester_id=requester_id
        )

        # キャッシュを無効化
        if user and cache_service:
            cache_key = f"user:profile:{user_id}"
            await cache_service.delete(cache_key)
            # ユーザー一覧のキャッシュも無効化
            await cache_service.invalidate_pattern("user:list:*")
            logger.info(f"Cache invalidated: {cache_key}")

        return user

    @staticmethod
    async def delete_user_cached(
        db: AsyncSession,
        user_id: UUID,
        cache_service: Optional[CacheService] = None,
        requester_id: Optional[UUID] = None,
    ) -> Optional[User]:
        """ユーザーを削除（キャッシュ無効化付き）"""
        user = await UserService.delete_user(
            db=db,
            user_id=user_id,
            requester_id=requester_id
        )

        # キャッシュを無効化
        if user and cache_service:
            await cache_service.delete(f"user:profile:{user_id}")
            await cache_service.invalidate_pattern("user:list:*")

        return user
```

### 4.4 Dependency Injection での CacheService 提供

```python
# app/core/dependencies.py - 追加

from redis.asyncio import Redis
from app.services.cache_service import CacheService
from app.config import get_settings

# グローバル Redis クライアント
_redis_client: Optional[Redis] = None

async def get_redis_client() -> Redis:
    """Redis クライアントを取得"""
    global _redis_client

    if _redis_client is None:
        settings = get_settings()
        _redis_client = Redis.from_url(
            settings.REDIS_URL,
            decode_responses=True
        )
    return _redis_client

async def get_cache_service() -> CacheService:
    """CacheService を取得"""
    redis_client = await get_redis_client()
    return CacheService(redis_client)
```

### 4.5 API での使用例

```python
# app/api/v1/users.py - 修正

@router.get("/{user_id}", response_model=UserResponse)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    cache_service: CacheService = Depends(get_cache_service),
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """ユーザーを ID で取得（キャッシュ付き）"""
    user = await UserService.get_user_by_id_cached(
        db=db,
        user_id=user_id,
        cache_service=cache_service
    )

    if not user:
        raise HTTPException(status_code=404, detail="User not found")

    return UserResponse.model_validate(user)
```

---

## 📋 Step 5: パフォーマンステスト実装

### 目的
- Eager Loading による N+1 問題解決を検証
- Cursor-based Pagination の動作確認
- Redis キャッシングの効果測定

### テストファイル
- `tests/test_performance_optimization.py` (新規)

### テスト項目

```python
# tests/test_performance_optimization.py

import pytest
import time
from unittest.mock import AsyncMock, patch, MagicMock
from sqlalchemy import event
from sqlalchemy.ext.asyncio import AsyncSession

class TestEagerLoadingOptimization:
    """Eager Loading によるパフォーマンス改善テスト"""

    @pytest.mark.asyncio
    async def test_eager_loading_reduces_queries(self, test_db):
        """Eager Loading が N+1 クエリを排除"""
        # テストデータ作成
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

        def count_queries(conn, *args, **kwargs):
            nonlocal query_count
            query_count += 1

        # リスナを登録
        event.listen(AsyncSession, "before_execute", count_queries)

        try:
            # Without eager loading
            query_count = 0
            query = select(User).where(User.id == user.id)
            result = await test_db.execute(query)
            u = result.scalar_one()
            _ = u.audit_logs  # N+1 問題発生

            without_eager_count = query_count

            # With eager loading
            query_count = 0
            query = (
                select(User)
                .where(User.id == user.id)
                .options(selectinload(User.audit_logs))
            )
            result = await test_db.execute(query)
            u = result.scalars().unique().all()[0]
            _ = u.audit_logs  # キャッシュから取得

            with_eager_count = query_count

            # Eager Loading の方がクエリ数が少ないことを確認
            assert with_eager_count < without_eager_count
            assert with_eager_count <= 2  # User + audit_logs

        finally:
            event.remove(AsyncSession, "before_execute", count_queries)


class TestCursorPaginationOptimization:
    """Cursor-based Pagination のテスト"""

    @pytest.mark.asyncio
    async def test_cursor_pagination_consistency(self, test_db):
        """Cursor-based pagination が一貫性を保つ"""
        # テストデータ作成
        for i in range(30):
            user = User(
                id=uuid4(),
                email=f"user{i}@example.com",
                ...
            )
            test_db.add(user)
        await test_db.commit()

        # ページ1を取得
        users_page1, cursor1 = await get_paginated_users(test_db, limit=10)
        assert len(users_page1) == 10

        # 新規ユーザーを追加
        new_user = User(id=uuid4(), email="newuser@example.com", ...)
        test_db.add(new_user)
        await test_db.commit()

        # ページ2を取得
        users_page2, cursor2 = await get_paginated_users(test_db, cursor=cursor1, limit=10)
        assert len(users_page2) == 10

        # 重複なし
        page1_ids = {u.id for u in users_page1}
        page2_ids = {u.id for u in users_page2}
        assert len(page1_ids & page2_ids) == 0


class TestCacheOptimization:
    """Redis キャッシングのテスト"""

    @pytest.mark.asyncio
    async def test_cache_hit_reduces_latency(self, test_db, cache_service):
        """キャッシュヒットが応答時間を短縮"""
        user = User(id=uuid4(), email="cache@example.com", ...)
        test_db.add(user)
        await test_db.commit()

        # 1回目：DB から取得
        start1 = time.time()
        user1 = await UserService.get_user_by_id_cached(
            test_db, user.id, cache_service
        )
        time1 = time.time() - start1

        # 2回目：キャッシュから取得
        start2 = time.time()
        user2 = await UserService.get_user_by_id_cached(
            test_db, user.id, cache_service
        )
        time2 = time.time() - start2

        # キャッシュ取得の方が高速
        assert time2 < time1
        assert user1.id == user2.id

        # キャッシュ無効化
        await cache_service.delete(f"user:profile:{user.id}")
```

---

## 🔄 実装チェックリスト

### Phase A3 実装進捗

- [x] Step 1: インデックス追加（完了）
  - [x] User テーブルインデックス 4つ
  - [x] AuditLog テーブルインデックス 4つ
  - [x] マイグレーションファイル作成

- [ ] Step 2: Eager Loading 実装（進行中）
  - [ ] UserService の selectinload 実装
  - [ ] API エンドポイント修正
  - [ ] テスト実装

- [ ] Step 3: Cursor-based Pagination 実装
  - [ ] PaginationService 作成
  - [ ] API エンドポイント修正
  - [ ] テスト実装

- [ ] Step 4: Redis キャッシング実装
  - [ ] CacheService 作成
  - [ ] UserService 統合
  - [ ] 依存性注入設定
  - [ ] テスト実装

- [ ] Step 5: パフォーマンステスト
  - [ ] test_performance_optimization.py 作成
  - [ ] すべてのテストを実行
  - [ ] パフォーマンス測定

---

## 📊 パフォーマンス期待値

### インデックス追加後
- User 検索: 100ms → 10ms (10倍高速化)
- AuditLog 検索: 500ms → 50ms (10倍高速化)

### Eager Loading 導入後
- User + AuditLog 取得: N+1 クエリ → 2クエリ
- 100ユーザー取得: 101クエリ → 2クエリ

### Cursor-based Pagination
- 大規模データセット: OFFSET が不要
- 100万レコード取得: 常に < 100ms

### Redis キャッシング
- キャッシュヒット: 10ms → < 1ms
- メモリ使用量: 合理的な範囲内（TTL で自動削除）

---

## 🚀 次のステップ

1. **Eager Loading 実装** (Step 2)
   - UserService を修正
   - API エンドポイントをテスト

2. **Cursor-based Pagination** (Step 3)
   - PaginationService を作成
   - API エンドポイントを修正

3. **Redis キャッシング** (Step 4)
   - CacheService を実装
   - 依存性注入を設定

4. **パフォーマンステスト** (Step 5)
   - すべてのテストを作成・実行
   - パフォーマンス測定

5. **本番準備**
   - ドキュメント完備
   - Git コミット
   - 本番環境へのデプロイ

---

*Implementation Guide Created: 2025年 Week 6*
*Status: In Progress (Step 2)*
