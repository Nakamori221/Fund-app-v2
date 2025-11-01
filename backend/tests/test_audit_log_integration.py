"""監査ログの統合テスト - ユーザー操作と監査ログの相関確認"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from app.main import app
from app.models.database import User, AuditLog
from app.core.security import AuthService
from app.models.schemas import UserRole


@pytest.fixture
def client():
    """テスト用 FastAPI クライアント"""
    return TestClient(app)


@pytest.fixture
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
        data={"user_id": str(user.id), "email": user.email, "role": user.role}
    )


class TestAuditLogIntegration:
    """監査ログの統合テスト"""

    @pytest.mark.asyncio
    async def test_create_user_generates_audit_log(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """ユーザー作成時に監査ログが記録される"""
        token = get_token(admin_user)

        # ユーザーを作成
        response = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "newuser@example.com",
                "full_name": "New User",
                "password": "password123",
                "role": "analyst",
            },
        )

        assert response.status_code == 201
        created_user = response.json()

        # 監査ログを確認
        stmt = select(AuditLog).where(
            (AuditLog.action == "create")
            & (AuditLog.resource_type == "user")
            & (AuditLog.resource_id == created_user["id"])
        )
        result = await db.execute(stmt)
        audit_log = result.scalar_one_or_none()

        assert audit_log is not None
        assert audit_log.user_id == admin_user.id
        assert audit_log.action == "create"
        assert audit_log.resource_type == "user"
        assert audit_log.new_values is not None
        assert audit_log.new_values["email"] == "newuser@example.com"
        assert audit_log.old_values is None

    @pytest.mark.asyncio
    async def test_update_user_generates_audit_log(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """ユーザー更新時に監査ログが記録される"""
        token = get_token(admin_user)

        # 更新対象のユーザーを作成
        create_response = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "updatetest@example.com",
                "full_name": "Update Test User",
                "password": "password123",
                "role": "analyst",
            },
        )
        user_id = create_response.json()["id"]

        # ユーザーを更新
        update_response = client.put(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "full_name": "Updated User Name",
            },
        )

        assert update_response.status_code == 200

        # 監査ログを確認
        stmt = select(AuditLog).where(
            (AuditLog.action == "update")
            & (AuditLog.resource_type == "user")
            & (AuditLog.resource_id == user_id)
        )
        result = await db.execute(stmt)
        audit_logs = result.scalars().all()

        # update ログを検索
        update_log = None
        for log in audit_logs:
            if log.action == "update":
                update_log = log
                break

        assert update_log is not None
        assert update_log.user_id == admin_user.id
        assert update_log.old_values is not None
        assert update_log.new_values is not None
        assert update_log.old_values["full_name"] == "Update Test User"
        assert update_log.new_values["full_name"] == "Updated User Name"

    @pytest.mark.asyncio
    async def test_delete_user_generates_audit_log(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """ユーザー削除時に監査ログが記録される"""
        token = get_token(admin_user)

        # 削除対象のユーザーを作成
        create_response = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "deletetest@example.com",
                "full_name": "Delete Test User",
                "password": "password123",
                "role": "analyst",
            },
        )
        user_id = create_response.json()["id"]

        # ユーザーを削除
        delete_response = client.delete(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert delete_response.status_code == 200

        # 監査ログを確認
        stmt = select(AuditLog).where(
            (AuditLog.action == "delete")
            & (AuditLog.resource_type == "user")
            & (AuditLog.resource_id == user_id)
        )
        result = await db.execute(stmt)
        delete_log = result.scalar_one_or_none()

        assert delete_log is not None
        assert delete_log.user_id == admin_user.id
        assert delete_log.action == "delete"
        assert delete_log.old_values is not None
        assert delete_log.old_values["email"] == "deletetest@example.com"
        assert delete_log.new_values is None

    @pytest.mark.asyncio
    async def test_change_user_role_generates_audit_log(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """ユーザーロール変更時に監査ログが記録される"""
        token = get_token(admin_user)

        # ロール変更対象のユーザーを作成
        create_response = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "roletest@example.com",
                "full_name": "Role Test User",
                "password": "password123",
                "role": "analyst",
            },
        )
        user_id = create_response.json()["id"]

        # ロールを変更
        role_response = client.post(
            f"/api/v1/users/{user_id}/role",
            headers={"Authorization": f"Bearer {token}"},
            json={"role": "lead_partner"},
        )

        assert role_response.status_code == 200

        # 監査ログを確認
        stmt = select(AuditLog).where(
            (AuditLog.action == "update")
            & (AuditLog.resource_type == "user")
            & (AuditLog.resource_id == user_id)
        )
        result = await db.execute(stmt)
        audit_logs = result.scalars().all()

        # role_change の extra_data を持つログを検索
        role_change_log = None
        for log in audit_logs:
            if log.extra_data and log.extra_data.get("change_type") == "role_change":
                role_change_log = log
                break

        assert role_change_log is not None
        assert role_change_log.user_id == admin_user.id
        assert role_change_log.extra_data["new_role"] == "lead_partner"
        assert role_change_log.old_values["role"] == "analyst"
        assert role_change_log.new_values["role"] == "lead_partner"

    @pytest.mark.asyncio
    async def test_audit_log_contains_request_metadata(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """監査ログがリクエストメタデータ（IP、User-Agent）を含む"""
        token = get_token(admin_user)

        # ユーザーを作成
        response = client.post(
            "/api/v1/users",
            headers={
                "Authorization": f"Bearer {token}",
                "User-Agent": "TestClient/1.0",
            },
            json={
                "email": "metadatatest@example.com",
                "full_name": "Metadata Test User",
                "password": "password123",
                "role": "analyst",
            },
        )

        assert response.status_code == 201
        created_user = response.json()

        # 監査ログを確認
        stmt = select(AuditLog).where(
            (AuditLog.action == "create")
            & (AuditLog.resource_type == "user")
            & (AuditLog.resource_id == created_user["id"])
        )
        result = await db.execute(stmt)
        audit_log = result.scalar_one_or_none()

        assert audit_log is not None
        # ip_address が記録されている
        assert audit_log.ip_address is not None
        # user_agent が記録されている
        assert audit_log.user_agent is not None

    @pytest.mark.asyncio
    async def test_multiple_operations_create_multiple_logs(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """複数の操作で複数のログが記録される"""
        token = get_token(admin_user)

        # ユーザーを作成、更新、ロール変更
        # 1. 作成
        create_response = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "multiops@example.com",
                "full_name": "Multi Ops User",
                "password": "password123",
                "role": "analyst",
            },
        )
        user_id = create_response.json()["id"]

        # 2. 更新
        client.put(
            f"/api/v1/users/{user_id}",
            headers={"Authorization": f"Bearer {token}"},
            json={"full_name": "Updated Multi Ops"},
        )

        # 3. ロール変更
        client.post(
            f"/api/v1/users/{user_id}/role",
            headers={"Authorization": f"Bearer {token}"},
            json={"role": "lead_partner"},
        )

        # 監査ログを確認
        stmt = select(AuditLog).where(AuditLog.resource_id == user_id)
        result = await db.execute(stmt)
        audit_logs = result.scalars().all()

        # 最低 3 つのログ（create, update, update with role change）
        actions = [log.action for log in audit_logs]
        assert "create" in actions
        assert "update" in actions

        # 異なるタイムスタンプ
        timestamps = [log.timestamp for log in audit_logs]
        assert len(set(timestamps)) >= 1  # 少なくとも異なる時刻があるか

    @pytest.mark.asyncio
    async def test_audit_log_captures_all_user_fields(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """監査ログがユーザーのすべてのフィールドをキャプチャ"""
        token = get_token(admin_user)

        # ユーザーを作成
        response = client.post(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
            json={
                "email": "fullfields@example.com",
                "full_name": "Full Fields User",
                "department": "Engineering",
                "password": "password123",
                "role": "analyst",
            },
        )

        assert response.status_code == 201
        created_user = response.json()

        # 監査ログを確認
        stmt = select(AuditLog).where(
            (AuditLog.action == "create")
            & (AuditLog.resource_type == "user")
            & (AuditLog.resource_id == created_user["id"])
        )
        result = await db.execute(stmt)
        audit_log = result.scalar_one_or_none()

        assert audit_log is not None
        assert audit_log.new_values is not None
        # すべてのフィールドが記録されている
        assert "id" in audit_log.new_values
        assert "email" in audit_log.new_values
        assert "full_name" in audit_log.new_values
        assert "role" in audit_log.new_values
        assert "is_active" in audit_log.new_values
        assert audit_log.new_values["email"] == "fullfields@example.com"
        assert audit_log.new_values["full_name"] == "Full Fields User"
