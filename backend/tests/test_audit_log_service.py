"""監査ログサービスのテストスイート"""

import pytest
from datetime import datetime, timedelta
from uuid import uuid4, UUID
from sqlalchemy.ext.asyncio import AsyncSession

from app.models.database import User, AuditLog
from app.services.audit_log_service import AuditLogService
from app.models.schemas import UserRole


@pytest.fixture
async def test_user(db: AsyncSession):
    """テスト用ユーザーを作成"""
    from app.core.security import AuthService

    user = User(
        id=uuid4(),
        email="test@example.com",
        full_name="Test User",
        hashed_password=AuthService.hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def another_user(db: AsyncSession):
    """別のテスト用ユーザーを作成"""
    from app.core.security import AuthService

    user = User(
        id=uuid4(),
        email="another@example.com",
        full_name="Another User",
        hashed_password=AuthService.hash_password("password123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


class TestAuditLogAction:
    """AuditLogService.log_action のテスト"""

    @pytest.mark.asyncio
    async def test_log_action_create(self, db: AsyncSession, test_user: User):
        """Create操作の監査ログ記録"""
        resource_id = uuid4()
        new_values = {"email": "new@example.com", "full_name": "New User"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=resource_id,
            new_values=new_values,
        )

        assert log is not None
        assert log.user_id == test_user.id
        assert log.action == "create"
        assert log.resource_type == "user"
        assert log.resource_id == resource_id
        assert log.new_values == new_values
        assert log.old_values is None

    @pytest.mark.asyncio
    async def test_log_action_update(self, db: AsyncSession, test_user: User):
        """Update操作の監査ログ記録"""
        resource_id = uuid4()
        old_values = {"email": "old@example.com"}
        new_values = {"email": "new@example.com"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
        )

        assert log.action == "update"
        assert log.old_values == old_values
        assert log.new_values == new_values

    @pytest.mark.asyncio
    async def test_log_action_delete(self, db: AsyncSession, test_user: User):
        """Delete操作の監査ログ記録"""
        resource_id = uuid4()
        old_values = {"email": "delete@example.com"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="delete",
            resource_type="user",
            resource_id=resource_id,
            old_values=old_values,
        )

        assert log.action == "delete"
        assert log.old_values == old_values
        assert log.new_values is None

    @pytest.mark.asyncio
    async def test_log_action_with_extra_data(self, db: AsyncSession, test_user: User):
        """Extra data を含む監査ログ記録"""
        resource_id = uuid4()
        extra_data = {"change_type": "role_change", "new_role": "lead_partner"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
            extra_data=extra_data,
        )

        assert log.extra_data == extra_data


class TestAuditLogRetrieval:
    """AuditLogService.get_logs のテスト"""

    @pytest.mark.asyncio
    async def test_get_logs_all(self, db: AsyncSession, test_user: User):
        """全監査ログを取得"""
        # 3つの監査ログを作成
        for i in range(3):
            await AuditLogService.log_action(
                db=db,
                user_id=test_user.id,
                action="create",
                resource_type="user",
                resource_id=uuid4(),
                new_values={"index": i},
            )

        logs, total = await AuditLogService.get_logs(db=db, limit=100)

        assert len(logs) >= 3
        assert total >= 3

    @pytest.mark.asyncio
    async def test_get_logs_filter_by_user(self, db: AsyncSession, test_user: User, another_user: User):
        """ユーザーIDでフィルタリング"""
        # test_user のログ
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )
        # another_user のログ
        await AuditLogService.log_action(
            db=db,
            user_id=another_user.id,
            action="update",
            resource_type="user",
            resource_id=uuid4(),
        )

        logs, total = await AuditLogService.get_logs(
            db=db,
            user_id=test_user.id,
            limit=100,
        )

        # test_user のログだけ取得
        assert all(log.user_id == test_user.id for log in logs)

    @pytest.mark.asyncio
    async def test_get_logs_filter_by_action(self, db: AsyncSession, test_user: User):
        """操作タイプでフィルタリング"""
        # Create と Update の操作を記録
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="update",
            resource_type="user",
            resource_id=uuid4(),
        )

        logs, total = await AuditLogService.get_logs(
            db=db,
            action="create",
            limit=100,
        )

        assert all(log.action == "create" for log in logs)

    @pytest.mark.asyncio
    async def test_get_logs_filter_by_resource_type(self, db: AsyncSession, test_user: User):
        """リソース種別でフィルタリング"""
        # user と case の操作を記録
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="case",
            resource_id=uuid4(),
        )

        logs, total = await AuditLogService.get_logs(
            db=db,
            resource_type="user",
            limit=100,
        )

        assert all(log.resource_type == "user" for log in logs)

    @pytest.mark.asyncio
    async def test_get_logs_filter_by_date_range(self, db: AsyncSession, test_user: User):
        """日付範囲でフィルタリング"""
        # 古いログを作成
        old_log = await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        # 日付フィルタ
        now = datetime.utcnow()
        future = now + timedelta(hours=1)
        past = now - timedelta(hours=1)

        logs, total = await AuditLogService.get_logs(
            db=db,
            start_date=past,
            end_date=future,
            limit=100,
        )

        assert len(logs) > 0

    @pytest.mark.asyncio
    async def test_get_logs_pagination(self, db: AsyncSession, test_user: User):
        """ページネーション"""
        # 5つのログを作成
        for i in range(5):
            await AuditLogService.log_action(
                db=db,
                user_id=test_user.id,
                action="create",
                resource_type="user",
                resource_id=uuid4(),
            )

        # 最初のページ（2件）
        logs_page1, total1 = await AuditLogService.get_logs(db=db, skip=0, limit=2)
        # 2番目のページ（2件）
        logs_page2, total2 = await AuditLogService.get_logs(db=db, skip=2, limit=2)

        assert len(logs_page1) == 2
        assert len(logs_page2) == 2
        # ページが異なる
        assert logs_page1[0].id != logs_page2[0].id

    @pytest.mark.asyncio
    async def test_get_user_logs(self, db: AsyncSession, test_user: User):
        """特定ユーザーのログを取得"""
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        logs, total = await AuditLogService.get_user_logs(
            db=db,
            user_id=test_user.id,
            limit=100,
        )

        assert all(log.user_id == test_user.id for log in logs)

    @pytest.mark.asyncio
    async def test_get_resource_logs(self, db: AsyncSession, test_user: User):
        """特定リソースのログを取得"""
        resource_id = uuid4()

        # 同じリソースで複数の操作をログ
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=resource_id,
        )
        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
        )

        logs, total = await AuditLogService.get_resource_logs(
            db=db,
            resource_id=resource_id,
            resource_type="user",
            limit=100,
        )

        assert len(logs) >= 2
        assert all(log.resource_id == resource_id for log in logs)


class TestAuditLogStatistics:
    """AuditLogService.get_statistics のテスト"""

    @pytest.mark.asyncio
    async def test_get_statistics_by_action(self, db: AsyncSession, test_user: User):
        """アクション別統計"""
        # 異なるアクションをログ
        for action in ["create", "update", "delete"]:
            await AuditLogService.log_action(
                db=db,
                user_id=test_user.id,
                action=action,
                resource_type="user",
                resource_id=uuid4(),
            )

        stats = await AuditLogService.get_statistics(db=db)

        assert "by_action" in stats
        assert stats["by_action"].get("create", 0) > 0
        assert stats["by_action"].get("update", 0) > 0
        assert stats["by_action"].get("delete", 0) > 0

    @pytest.mark.asyncio
    async def test_get_statistics_by_resource_type(self, db: AsyncSession, test_user: User):
        """リソース種別別統計"""
        # 異なるリソース種別をログ
        for resource_type in ["user", "case", "observation"]:
            await AuditLogService.log_action(
                db=db,
                user_id=test_user.id,
                action="create",
                resource_type=resource_type,
                resource_id=uuid4(),
            )

        stats = await AuditLogService.get_statistics(db=db)

        assert "by_resource_type" in stats
        assert stats["by_resource_type"].get("user", 0) > 0
        assert stats["by_resource_type"].get("case", 0) > 0
        assert stats["by_resource_type"].get("observation", 0) > 0

    @pytest.mark.asyncio
    async def test_get_statistics_total_logs(self, db: AsyncSession, test_user: User):
        """総ログ数統計"""
        count_before = (await AuditLogService.get_statistics(db=db))["total_logs"]

        await AuditLogService.log_action(
            db=db,
            user_id=test_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        stats = await AuditLogService.get_statistics(db=db)
        count_after = stats["total_logs"]

        assert count_after == count_before + 1
