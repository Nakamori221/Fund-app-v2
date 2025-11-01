"""監査ログAPIエンドポイントの統合テスト"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient
from sqlalchemy.ext.asyncio import AsyncSession

from app.main import app
from app.models.database import User, AuditLog
from app.services.audit_log_service import AuditLogService
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
        email="admin@example.com",
        full_name="Admin User",
        hashed_password=AuthService.hash_password("password123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def analyst_user(db: AsyncSession):
    """分析者ユーザー"""
    user = User(
        id=uuid4(),
        email="analyst@example.com",
        full_name="Analyst User",
        hashed_password=AuthService.hash_password("password123"),
        role=UserRole.ANALYST,
        is_active=True,
    )
    db.add(user)
    await db.commit()
    await db.refresh(user)
    return user


@pytest.fixture
async def ic_user(db: AsyncSession):
    """IC メンバーユーザー"""
    user = User(
        id=uuid4(),
        email="ic@example.com",
        full_name="IC Member User",
        hashed_password=AuthService.hash_password("password123"),
        role=UserRole.IC_MEMBER,
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


class TestAuditLogAPI:
    """監査ログAPIエンドポイントのテスト"""

    @pytest.mark.asyncio
    async def test_get_audit_logs_as_admin(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """管理者が全監査ログを取得"""
        # ログを作成
        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        token = get_token(admin_user)
        response = client.get(
            "/api/v1/audit-logs",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "logs" in data
        assert "total" in data
        assert data["skip"] == 0
        assert data["limit"] == 20

    @pytest.mark.asyncio
    async def test_get_audit_logs_as_analyst_own_only(
        self, client: TestClient, db: AsyncSession, analyst_user: User
    ):
        """分析者が自分のログのみを取得"""
        # 分析者のログ
        await AuditLogService.log_action(
            db=db,
            user_id=analyst_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        token = get_token(analyst_user)
        response = client.get(
            "/api/v1/audit-logs",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # すべてのログが分析者のもの
        assert all(log["user_id"] == str(analyst_user.id) for log in data["logs"])

    @pytest.mark.asyncio
    async def test_get_audit_logs_filter_by_action(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """アクション別フィルタ"""
        # Create と Update ログを作成
        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )
        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="update",
            resource_type="user",
            resource_id=uuid4(),
        )

        token = get_token(admin_user)
        response = client.get(
            "/api/v1/audit-logs?action=create",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(log["action"] == "create" for log in data["logs"])

    @pytest.mark.asyncio
    async def test_get_audit_logs_filter_by_resource_type(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """リソース種別別フィルタ"""
        # user と case ログを作成
        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )
        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="case",
            resource_id=uuid4(),
        )

        token = get_token(admin_user)
        response = client.get(
            "/api/v1/audit-logs?resource_type=user",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(log["resource_type"] == "user" for log in data["logs"])

    @pytest.mark.asyncio
    async def test_get_audit_logs_pagination(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """ページネーション"""
        # 5つのログを作成
        for i in range(5):
            await AuditLogService.log_action(
                db=db,
                user_id=admin_user.id,
                action="create",
                resource_type="user",
                resource_id=uuid4(),
            )

        token = get_token(admin_user)
        # 最初のページ（2件）
        response1 = client.get(
            "/api/v1/audit-logs?skip=0&limit=2",
            headers={"Authorization": f"Bearer {token}"},
        )
        # 2番目のページ（2件）
        response2 = client.get(
            "/api/v1/audit-logs?skip=2&limit=2",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response1.status_code == 200
        assert response2.status_code == 200
        data1 = response1.json()
        data2 = response2.json()
        assert len(data1["logs"]) == 2
        assert len(data2["logs"]) == 2

    @pytest.mark.asyncio
    async def test_get_user_audit_logs(
        self, client: TestClient, db: AsyncSession, admin_user: User, analyst_user: User
    ):
        """特定ユーザーのログを取得"""
        await AuditLogService.log_action(
            db=db,
            user_id=analyst_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        token = get_token(admin_user)
        response = client.get(
            f"/api/v1/audit-logs/user/{analyst_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(log["user_id"] == str(analyst_user.id) for log in data["logs"])

    @pytest.mark.asyncio
    async def test_analyst_cannot_view_other_user_logs(
        self, client: TestClient, db: AsyncSession, analyst_user: User, admin_user: User
    ):
        """分析者は他ユーザーのログを閲覧できない"""
        token = get_token(analyst_user)
        response = client.get(
            f"/api/v1/audit-logs/user/{admin_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_resource_audit_logs(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """特定リソースのログを取得"""
        resource_id = uuid4()

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

        token = get_token(admin_user)
        response = client.get(
            f"/api/v1/audit-logs/resource/{resource_id}?resource_type=user",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert all(log["resource_id"] == str(resource_id) for log in data["logs"])

    @pytest.mark.asyncio
    async def test_get_audit_log_statistics_as_admin(
        self, client: TestClient, db: AsyncSession, admin_user: User
    ):
        """管理者が統計情報を取得"""
        await AuditLogService.log_action(
            db=db,
            user_id=admin_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        token = get_token(admin_user)
        response = client.get(
            "/api/v1/audit-logs/statistics",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "statistics" in data
        assert "total_logs" in data["statistics"]
        assert "by_action" in data["statistics"]
        assert "by_resource_type" in data["statistics"]

    @pytest.mark.asyncio
    async def test_get_audit_log_statistics_as_analyst_forbidden(
        self, client: TestClient, analyst_user: User
    ):
        """分析者は統計情報を取得できない"""
        token = get_token(analyst_user)
        response = client.get(
            "/api/v1/audit-logs/statistics",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    @pytest.mark.asyncio
    async def test_get_audit_log_statistics_as_ic_member(
        self, client: TestClient, db: AsyncSession, ic_user: User
    ):
        """IC メンバーが統計情報を取得"""
        await AuditLogService.log_action(
            db=db,
            user_id=ic_user.id,
            action="create",
            resource_type="user",
            resource_id=uuid4(),
        )

        token = get_token(ic_user)
        response = client.get(
            "/api/v1/audit-logs/statistics",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert "statistics" in data
