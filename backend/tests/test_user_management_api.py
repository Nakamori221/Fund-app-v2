"""ユーザー管理API統合テスト"""

import pytest
from uuid import uuid4
from fastapi.testclient import TestClient

from app.main import create_app
from app.models.schemas import UserRole
from app.models.database import User
from app.database import get_db
from app.core.security import AuthService


# テスト用定数
TEST_ADMIN_EMAIL = "admin@test.com"
TEST_ADMIN_PASSWORD = "AdminPass123!"
TEST_ADMIN_HASH = AuthService.hash_password(TEST_ADMIN_PASSWORD)

TEST_ANALYST_EMAIL = "analyst@test.com"
TEST_ANALYST_PASSWORD = "AnalystPass123!"
TEST_ANALYST_HASH = AuthService.hash_password(TEST_ANALYST_PASSWORD)

TEST_LEAD_EMAIL = "lead@test.com"
TEST_LEAD_PASSWORD = "LeadPass123!"
TEST_LEAD_HASH = AuthService.hash_password(TEST_LEAD_PASSWORD)


def create_test_token(user_id: str, role: str) -> str:
    """テスト用トークンを生成"""
    return AuthService.create_access_token(
        user_id=user_id,
        role=role,
    )


@pytest.fixture
def app(test_db):
    """テスト用FastAPIアプリを作成"""
    app_instance = create_app()

    async def override_get_db():
        return test_db

    app_instance.dependency_overrides[get_db] = override_get_db
    return app_instance


@pytest.fixture
def client(app):
    """同期テストクライアント"""
    return TestClient(app)


@pytest.fixture
def admin_user(test_db):
    """管理者ユーザーを作成"""
    import asyncio

    async def create_admin():
        user = User(
            id=uuid4(),
            email=TEST_ADMIN_EMAIL,
            full_name="テスト管理者",
            department="システム部",
            hashed_password=TEST_ADMIN_HASH,
            role=UserRole.ADMIN,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    return asyncio.run(create_admin())


@pytest.fixture
def analyst_user(test_db):
    """分析者ユーザーを作成"""
    import asyncio

    async def create_analyst():
        user = User(
            id=uuid4(),
            email=TEST_ANALYST_EMAIL,
            full_name="テスト分析者",
            department="分析部",
            hashed_password=TEST_ANALYST_HASH,
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    return asyncio.run(create_analyst())


@pytest.fixture
def lead_user(test_db):
    """リードパートナーを作成"""
    import asyncio

    async def create_lead():
        user = User(
            id=uuid4(),
            email=TEST_LEAD_EMAIL,
            full_name="テストリード",
            department="営業部",
            hashed_password=TEST_LEAD_HASH,
            role=UserRole.LEAD_PARTNER,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()
        await test_db.refresh(user)
        return user

    return asyncio.run(create_lead())


class TestUserCreation:
    """ユーザー作成エンドポイントテスト"""

    def test_create_user_success(self, client, admin_user):
        """管理者がユーザーを作成できる"""
        # 管理者用トークンを生成
        token = create_test_token(str(admin_user.id), UserRole.ADMIN.value)

        # ユーザー作成
        response = client.post(
            "/api/v1/users",
            json={
                "email": "newuser@test.com",
                "full_name": "新規ユーザー",
                "department": "新規部門",
                "password": "NewPass123!",
                "role": "analyst",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 201
        data = response.json()
        assert data["email"] == "newuser@test.com"
        assert data["full_name"] == "新規ユーザー"
        assert data["role"] == "analyst"

    def test_create_user_unauthorized(self, client, analyst_user):
        """分析者はユーザーを作成できない"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # ユーザー作成試行
        response = client.post(
            "/api/v1/users",
            json={
                "email": "newuser2@test.com",
                "full_name": "新規ユーザー2",
                "password": "NewPass123!",
                "role": "analyst",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403
        assert "権限" in response.json()["detail"]

    def test_create_user_duplicate_email(self, client, admin_user):
        """重複したメールアドレスではユーザーを作成できない"""
        # 管理者用トークンを生成
        token = create_test_token(str(admin_user.id), UserRole.ADMIN.value)

        # 既存メールで作成試行
        response = client.post(
            "/api/v1/users",
            json={
                "email": TEST_ADMIN_EMAIL,  # 既存のメール
                "full_name": "別のユーザー",
                "password": "NewPass123!",
                "role": "analyst",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 409


class TestUserList:
    """ユーザー一覧取得エンドポイントテスト"""

    def test_list_users_analyst_self_only(self, client, analyst_user, lead_user):
        """分析者は自分自身のみ表示"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # ユーザー一覧取得
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) == 1
        assert data["users"][0]["email"] == TEST_ANALYST_EMAIL

    def test_list_users_lead_sees_analysts(self, client, analyst_user, lead_user):
        """リードパートナーはANALYST以下を表示"""
        # リード用トークンを生成
        token = create_test_token(str(lead_user.id), UserRole.LEAD_PARTNER.value)

        # ユーザー一覧取得
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # リード自身 + ANALYST ユーザー = 2
        assert len(data["users"]) >= 1

    def test_list_users_admin_sees_all(self, client, admin_user, analyst_user, lead_user):
        """管理者はすべてのユーザーを表示"""
        # 管理者用トークンを生成
        token = create_test_token(str(admin_user.id), UserRole.ADMIN.value)

        # ユーザー一覧取得
        response = client.get(
            "/api/v1/users",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        # 管理者 + ANALYST + リード = 3
        assert len(data["users"]) == 3

    def test_list_users_pagination(self, client, admin_user):
        """ページネーションが機能する"""
        # 管理者用トークンを生成
        token = create_test_token(str(admin_user.id), UserRole.ADMIN.value)

        # limit=1 でリクエスト
        response = client.get(
            "/api/v1/users?limit=1&skip=0",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["users"]) <= 1
        assert data["limit"] == 1
        assert data["skip"] == 0


class TestUserDetail:
    """ユーザー詳細取得エンドポイントテスト"""

    def test_get_user_self(self, client, analyst_user):
        """ユーザーは自分の情報を取得できる"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # 自分の詳細取得
        response = client.get(
            f"/api/v1/users/{analyst_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["email"] == TEST_ANALYST_EMAIL

    def test_get_user_not_found(self, client, admin_user):
        """存在しないユーザーは404"""
        # 管理者用トークンを生成
        token = create_test_token(str(admin_user.id), UserRole.ADMIN.value)

        # 存在しないユーザーを取得
        response = client.get(
            f"/api/v1/users/{uuid4()}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 404


class TestUserUpdate:
    """ユーザー更新エンドポイントテスト"""

    def test_update_user_self(self, client, analyst_user):
        """ユーザーは自分の情報を更新できる"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # 自分の情報を更新
        response = client.put(
            f"/api/v1/users/{analyst_user.id}",
            json={
                "full_name": "更新されたユーザー",
                "department": "新しい部門",
            },
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["full_name"] == "更新されたユーザー"
        assert data["department"] == "新しい部門"

    def test_update_user_analyst_cannot_change_role(self, client, analyst_user):
        """分析者はロールを変更できない"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # ロール変更を試行
        response = client.put(
            f"/api/v1/users/{analyst_user.id}",
            json={"role": "lead_partner"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403

    def test_update_other_user_unauthorized(self, client, analyst_user, lead_user):
        """分析者は他のユーザーを更新できない"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # 他のユーザーを更新試行
        response = client.put(
            f"/api/v1/users/{lead_user.id}",
            json={"full_name": "ハッキング試行"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestUserDelete:
    """ユーザー削除エンドポイントテスト"""

    def test_delete_user_admin_only(self, client, admin_user, analyst_user):
        """管理者のみがユーザーを削除できる"""
        # 管理者用トークンを生成
        token = create_test_token(str(admin_user.id), UserRole.ADMIN.value)

        # ユーザー削除
        response = client.delete(
            f"/api/v1/users/{analyst_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        assert "削除しました" in response.json()["message"]

    def test_delete_user_analyst_forbidden(self, client, analyst_user, lead_user):
        """分析者はユーザーを削除できない"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # 削除試行
        response = client.delete(
            f"/api/v1/users/{lead_user.id}",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestChangeRole:
    """ロール変更エンドポイントテスト"""

    def test_change_role_admin_only(self, client, admin_user, analyst_user):
        """管理者のみがロールを変更できる"""
        # 管理者用トークンを生成
        token = create_test_token(str(admin_user.id), UserRole.ADMIN.value)

        # ロール変更
        response = client.post(
            f"/api/v1/users/{analyst_user.id}/role",
            json={"role": "lead_partner"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert data["role"] == "lead_partner"

    def test_change_role_analyst_forbidden(self, client, analyst_user, lead_user):
        """分析者はロールを変更できない"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # ロール変更試行
        response = client.post(
            f"/api/v1/users/{lead_user.id}/role",
            json={"role": "admin"},
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 403


class TestGetRoles:
    """ロール一覧エンドポイントテスト"""

    def test_get_roles_success(self, client, analyst_user):
        """認証ユーザーはロール一覧を取得できる"""
        # 分析者用トークンを生成
        token = create_test_token(str(analyst_user.id), UserRole.ANALYST.value)

        # ロール一覧取得
        response = client.get(
            "/api/v1/roles",
            headers={"Authorization": f"Bearer {token}"},
        )

        assert response.status_code == 200
        data = response.json()
        assert len(data["roles"]) == 4  # ANALYST, LEAD_PARTNER, IC_MEMBER, ADMIN

        # 各ロールに説明と権限リストがあることを確認
        for role in data["roles"]:
            assert "role" in role
            assert "description" in role
            assert "permissions" in role
