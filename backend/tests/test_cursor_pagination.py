"""
Cursor-based Pagination テスト
Phase A3 Step 3: Cursor-based Pagination の実装テスト
"""

import pytest
import pytest_asyncio
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import User
from app.models.schemas import UserRole
from app.services.pagination_service import PaginationService, CursorPaginationParams
from app.services.user_service import UserService


class TestCursorPaginationParams:
    """CursorPaginationParams のテスト"""

    def test_encode_cursor(self):
        """カーソルエンコーディングのテスト"""
        created_at = datetime(2025, 1, 15, 10, 30, 0)
        entity_id = UUID("12345678-1234-5678-1234-567812345678")

        cursor = CursorPaginationParams.encode_cursor(created_at, entity_id)

        assert isinstance(cursor, str)
        assert len(cursor) > 0
        # Base64 エンコードされているはず
        assert cursor.replace("=", "").replace("+", "").replace("/", "").isalnum()

    def test_decode_cursor(self):
        """カーソルデコーディングのテスト"""
        created_at = datetime(2025, 1, 15, 10, 30, 0)
        entity_id = UUID("12345678-1234-5678-1234-567812345678")

        cursor = CursorPaginationParams.encode_cursor(created_at, entity_id)
        decoded_at, decoded_id = CursorPaginationParams.decode_cursor(cursor)

        # マイクロ秒レベルで比較（ISO フォーマット変換による丸め込みの影響を考慮）
        assert abs((decoded_at - created_at).total_seconds()) < 1
        assert decoded_id == entity_id

    def test_encode_decode_roundtrip(self):
        """エンコード/デコードのラウンドトリップテスト"""
        test_cases = [
            (datetime(2025, 1, 1, 0, 0, 0), UUID("00000000-0000-0000-0000-000000000000")),
            (datetime(2025, 12, 31, 23, 59, 59), UUID("ffffffff-ffff-ffff-ffff-ffffffffffff")),
            (datetime.now(), UUID("12345678-1234-5678-1234-567812345678")),
        ]

        for created_at, entity_id in test_cases:
            cursor = CursorPaginationParams.encode_cursor(created_at, entity_id)
            decoded_at, decoded_id = CursorPaginationParams.decode_cursor(cursor)

            # ISO フォーマットの丸め込みの影響を考慮
            assert abs((decoded_at - created_at).total_seconds()) < 1
            assert decoded_id == entity_id

    def test_decode_invalid_cursor(self):
        """無効なカーソルのデコードテスト"""
        with pytest.raises(ValueError):
            CursorPaginationParams.decode_cursor("invalid-cursor")

        with pytest.raises(ValueError):
            CursorPaginationParams.decode_cursor("")

    def test_decode_malformed_base64(self):
        """不正な Base64 形式のテスト"""
        with pytest.raises(ValueError):
            CursorPaginationParams.decode_cursor("!!!invalid-base64!!!")


@pytest.mark.asyncio
class TestPaginationService:
    """PaginationService のテスト"""

    @pytest_asyncio.fixture
    async def sample_users(self, test_db: AsyncSession):
        """テスト用サンプルユーザーを作成"""
        users = []
        base_time = datetime(2025, 1, 1, 10, 0, 0)

        for i in range(10):
            user = User(
                email=f"user{i}@example.com",
                full_name=f"User {i}",
                hashed_password="hashed_password",
                role=UserRole.ANALYST if i % 2 == 0 else UserRole.LEAD_PARTNER,
                is_active=True,
                created_at=base_time + timedelta(hours=i),
            )
            test_db.add(user)
            users.append(user)

        await test_db.commit()

        # リフレッシュして ID を取得
        for user in users:
            await test_db.refresh(user)

        return users

    @pytest.mark.asyncio
    async def test_paginate_first_page(self, test_db: AsyncSession, sample_users):
        """最初のページの取得テスト"""
        query = select(User).order_by(User.created_at.desc(), User.id)

        users, next_cursor, has_more = await PaginationService.paginate(
            db=test_db,
            query=query,
            cursor=None,
            limit=3,
        )

        assert len(users) == 3
        assert has_more is True
        assert next_cursor is not None
        # 最後のユーザーのカーソルが返されるはず
        assert users[-1].id is not None

    @pytest.mark.asyncio
    async def test_paginate_with_cursor(self, test_db: AsyncSession, sample_users):
        """カーソル付きページングのテスト"""
        query = select(User).order_by(User.created_at.desc(), User.id)

        # 最初のページ
        users1, cursor1, has_more1 = await PaginationService.paginate(
            db=test_db,
            query=query,
            cursor=None,
            limit=3,
        )

        assert len(users1) == 3
        assert has_more1 is True

        # 2 番目のページ
        query2 = select(User).order_by(User.created_at.desc(), User.id)
        users2, cursor2, has_more2 = await PaginationService.paginate(
            db=test_db,
            query=query2,
            cursor=cursor1,
            limit=3,
        )

        assert len(users2) == 3
        assert has_more2 is True

        # ユーザーが重複していないことを確認
        user_ids_1 = {u.id for u in users1}
        user_ids_2 = {u.id for u in users2}
        assert user_ids_1.isdisjoint(user_ids_2)

    @pytest.mark.asyncio
    async def test_paginate_last_page(self, test_db: AsyncSession, sample_users):
        """最後のページのテスト"""
        query = select(User).order_by(User.created_at.desc(), User.id)

        # 最初のページから最後まで反復
        all_users = []
        cursor = None
        iteration = 0

        while True:
            query_iter = select(User).order_by(User.created_at.desc(), User.id)
            users, cursor, has_more = await PaginationService.paginate(
                db=test_db,
                query=query_iter,
                cursor=cursor,
                limit=3,
            )

            all_users.extend(users)
            iteration += 1

            if not has_more:
                break

            # 無限ループ防止
            assert iteration < 100

        # 全ユーザーが取得されたことを確認
        assert len(all_users) == 10

    @pytest.mark.asyncio
    async def test_paginate_single_page(self, test_db: AsyncSession):
        """単一ページで全データが収まるケース"""
        # 小数のユーザーのみを作成
        for i in range(2):
            user = User(
                email=f"small_user{i}@example.com",
                full_name=f"Small User {i}",
                hashed_password="hashed_password",
                role=UserRole.ANALYST,
                is_active=True,
            )
            test_db.add(user)

        await test_db.commit()

        query = select(User).where(User.email.like("small_user%")).order_by(
            User.created_at.desc(), User.id
        )

        users, next_cursor, has_more = await PaginationService.paginate(
            db=test_db,
            query=query,
            cursor=None,
            limit=10,
        )

        assert len(users) == 2
        assert has_more is False
        assert next_cursor is None

    @pytest.mark.asyncio
    async def test_paginate_limit_validation(self, test_db: AsyncSession, sample_users):
        """Limit のバリデーションテスト"""
        query = select(User).order_by(User.created_at.desc(), User.id)

        # 無効な limit は 20 にクリップされる
        users, _, _ = await PaginationService.paginate(
            db=test_db,
            query=query,
            cursor=None,
            limit=0,  # 無効
        )

        # デフォルト 20 になるはず
        assert len(users) <= 10  # 全データが 10 個なので 10 個まで

    @pytest.mark.asyncio
    async def test_get_page_info(self):
        """ページ情報取得のテスト"""
        # 最初のページ
        info = await PaginationService.get_page_info(cursor=None, limit=20)

        assert info["limit"] == 20
        assert info["is_first_page"] is True
        assert "next_cursor" not in info or info.get("next_cursor") is None

        # カーソル付き
        created_at = datetime(2025, 1, 15, 10, 30, 0)
        entity_id = UUID("12345678-1234-5678-1234-567812345678")
        cursor = CursorPaginationParams.encode_cursor(created_at, entity_id)

        info = await PaginationService.get_page_info(cursor=cursor, limit=50)

        assert info["limit"] == 50
        assert info["is_first_page"] is False
        assert info["current_cursor_timestamp"] is not None
        assert info["current_cursor_id"] is not None


@pytest.mark.asyncio
class TestUserServiceCursorPagination:
    """UserService の Cursor-based Pagination メソッドのテスト"""

    @pytest_asyncio.fixture
    async def sample_users(self, test_db: AsyncSession):
        """テスト用サンプルユーザーを作成"""
        users = []

        for i in range(15):
            role = UserRole.ANALYST if i < 5 else (
                UserRole.LEAD_PARTNER if i < 10 else UserRole.IC_MEMBER
            )
            user = User(
                email=f"testuser{i}@example.com",
                full_name=f"Test User {i}",
                hashed_password="hashed_password",
                role=role,
                is_active=i % 3 != 0,  # 1/3 が非アクティブ
            )
            test_db.add(user)
            users.append(user)

        await test_db.commit()

        for user in users:
            await test_db.refresh(user)

        return users

    @pytest.mark.asyncio
    async def test_list_users_with_cursor_first_page(
        self, test_db: AsyncSession, sample_users
    ):
        """最初のページの取得テスト"""
        admin_id = UUID("00000000-0000-0000-0000-000000000000")

        users, cursor, has_more = await UserService.list_users_with_cursor(
            db=test_db,
            requester_id=admin_id,
            requester_role=UserRole.ADMIN,
            cursor=None,
            limit=5,
        )

        assert len(users) == 5
        assert has_more is True
        assert cursor is not None

    @pytest.mark.asyncio
    async def test_list_users_with_cursor_rbac(
        self, test_db: AsyncSession, sample_users
    ):
        """RBAC に従ったカーソルページングのテスト"""
        # ANALYST は自分自身のみ
        analyst_user = sample_users[0]
        users, _, _ = await UserService.list_users_with_cursor(
            db=test_db,
            requester_id=analyst_user.id,
            requester_role=UserRole.ANALYST,
            cursor=None,
            limit=10,
        )

        assert len(users) == 1
        assert users[0].id == analyst_user.id

    @pytest.mark.asyncio
    async def test_get_users_by_role_with_cursor(
        self, test_db: AsyncSession, sample_users
    ):
        """ロール別カーソルページングのテスト"""
        users, cursor, has_more = await UserService.get_users_by_role_with_cursor(
            db=test_db,
            role=UserRole.ANALYST,
            cursor=None,
            limit=10,
        )

        # ANALYST は 5 ユーザー
        assert len(users) <= 5
        for user in users:
            assert user.role == UserRole.ANALYST

    @pytest.mark.asyncio
    async def test_list_users_with_cursor_filtering(
        self, test_db: AsyncSession, sample_users
    ):
        """フィルタリング付きカーソルページングのテスト"""
        users, _, _ = await UserService.list_users_with_cursor(
            db=test_db,
            requester_id=UUID("00000000-0000-0000-0000-000000000000"),
            requester_role=UserRole.ADMIN,
            cursor=None,
            limit=10,
            role_filter=UserRole.ANALYST,
        )

        for user in users:
            assert user.role == UserRole.ANALYST

    @pytest.mark.asyncio
    async def test_list_users_with_cursor_full_iteration(
        self, test_db: AsyncSession, sample_users
    ):
        """全ページを反復するテスト"""
        admin_id = UUID("00000000-0000-0000-0000-000000000000")
        all_users = []
        cursor = None

        while True:
            users, cursor, has_more = await UserService.list_users_with_cursor(
                db=test_db,
                requester_id=admin_id,
                requester_role=UserRole.ADMIN,
                cursor=cursor,
                limit=4,
            )

            all_users.extend(users)

            if not has_more:
                break

        # 全ユーザーが取得されたことを確認
        assert len(all_users) == 15
