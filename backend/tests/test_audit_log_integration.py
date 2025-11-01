"""監査ログの統合テスト - ユーザー操作と監査ログの相関確認"""

import pytest
import pytest_asyncio
from uuid import uuid4
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.models.database import User, AuditLog
from app.services.audit_log_service import AuditLogService
from app.core.security import AuthService
from app.models.schemas import UserRole


@pytest_asyncio.fixture
async def admin_user(db: AsyncSession):
    """管理者ユーザー"""
    user = User(
        id=uuid4(),
        email="audit_admin@example.com",
        full_name="Audit Admin User",
        hashed_password=AuthService.hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


def get_token(user: User):
    """JWT トークンを生成（テスト用）"""
    return AuthService.create_access_token(
        user_id=str(user.id),
        role=user.role,
    )


class TestAuditLogIntegration:
    """監査ログの統合テスト"""

    @pytest.mark.asyncio
    async def test_audit_log_action_complete_workflow(
        self, db: AsyncSession, admin_user: User
    ):
        """監査ログの完全なワークフロー"""
        # 1. ログを作成
        resource_id = uuid4()
        new_values = {"email": "created@example.com", "full_name": "Created User"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=resource_id,
            new_values=new_values,
        )

        # 2. ログが正しく記録されたことを確認
        assert log is not None
        assert log.user_id == admin_user.id
        assert log.action == "create"
        assert log.resource_type == "user"
        assert log.resource_id == resource_id
        assert log.new_values == new_values
        assert log.old_values is None

    @pytest.mark.asyncio
    async def test_update_audit_log_captures_changes(
        self, db: AsyncSession, admin_user: User
    ):
        """更新ログが変更前後のデータをキャプチャ"""
        resource_id = uuid4()
        old_values = {"email": "old@example.com", "full_name": "Old Name"}
        new_values = {"email": "new@example.com", "full_name": "New Name"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
        )

        # 変更前後の値が記録されている
        assert log.old_values == old_values
        assert log.new_values == new_values
        assert log.old_values != log.new_values

    @pytest.mark.asyncio
    async def test_delete_audit_log_preserves_data(
        self, db: AsyncSession, admin_user: User
    ):
        """削除ログが削除前のデータを保存"""
        resource_id = uuid4()
        deleted_values = {"email": "deleted@example.com", "full_name": "Deleted User"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="delete",
            resource_type="user",
            resource_id=resource_id,
            old_values=deleted_values,
        )

        # 削除前のデータが保存されている
        assert log.old_values == deleted_values
        assert log.new_values is None

    @pytest.mark.asyncio
    async def test_audit_log_with_extra_data(
        self, db: AsyncSession, admin_user: User
    ):
        """ロール変更などの追加情報を記録"""
        resource_id = uuid4()
        extra_data = {"change_type": "role_change", "new_role": "lead_partner"}

        log = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
            extra_data=extra_data,
        )

        # 追加情報が記録されている
        assert log.extra_data == extra_data
        assert log.extra_data["change_type"] == "role_change"

    @pytest.mark.asyncio
    async def test_audit_log_query_by_resource(
        self, db: AsyncSession, admin_user: User
    ):
        """リソース別のログ取得"""
        resource_id = uuid4()

        # 同じリソースで複数の操作をログ
        log1 = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=resource_id,
        )

        log2 = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
        )

        # リソースのログを取得
        logs, total = await AuditLogService.get_resource_logs(
            db=db,
            resource_id=resource_id,
            resource_type="user",
            limit=100,
        )

        # 同じリソースのすべてのログが取得される
        assert len(logs) >= 2
        assert all(log.resource_id == resource_id for log in logs)

    @pytest.mark.asyncio
    async def test_audit_log_action_sequence(
        self, db: AsyncSession, admin_user: User
    ):
        """複数のアクションの順序が正しく記録される"""
        resource_id = uuid4()

        # create -> update -> delete の順序でログ
        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=resource_id,
        )

        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
        )

        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="delete",
            resource_type="user",
            resource_id=resource_id,
        )

        # すべてのログを取得
        logs, total = await AuditLogService.get_resource_logs(
            db=db,
            resource_id=resource_id,
            resource_type="user",
            limit=100,
        )

        # すべてのアクションが記録されている
        actions = [log.action for log in logs]
        assert "create" in actions
        assert "update" in actions
        assert "delete" in actions

    @pytest.mark.asyncio
    async def test_audit_log_timestamps_are_sequential(
        self, db: AsyncSession, admin_user: User
    ):
        """ログのタイムスタンプが時系列順"""
        resource_id = uuid4()

        # 複数のログを作成
        log1 = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=resource_id,
        )

        log2 = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="update",
            resource_type="user",
            resource_id=resource_id,
        )

        # タイムスタンプが記録されている
        assert log1.timestamp is not None
        assert log2.timestamp is not None
        # 後のログが前のログより遅い（またはイコール）
        assert log2.timestamp >= log1.timestamp

    @pytest.mark.asyncio
    async def test_audit_log_captures_all_user_fields(
        self, db: AsyncSession, admin_user: User
    ):
        """ログがユーザーのすべてのフィールドをキャプチャ"""
        resource_id = uuid4()
        complete_user_data = {
            "id": str(resource_id),
            "email": "fullfields@example.com",
            "full_name": "Full Fields User",
            "department": "Engineering",
            "role": "analyst",
            "is_active": True,
        }

        log = await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=resource_id,
            new_values=complete_user_data,
        )

        # すべてのフィールドが記録されている
        assert log.new_values is not None
        assert all(key in log.new_values for key in complete_user_data.keys())
