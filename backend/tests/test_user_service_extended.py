"""ユーザー管理サービス拡張テスト"""

import pytest
from uuid import uuid4

from app.models.database import User
from app.models.schemas import UserRole, UserCreate, UserUpdate
from app.services.user_service import UserService
from app.core.errors import (
    NotFoundException,
    AuthorizationException,
    ConflictException,
)


@pytest.mark.asyncio
class TestUserListUsers:
    """list_users メソッドのテスト"""

    async def test_list_users_analyst_self_only(self, test_db):
        """ANALYST は自分自身のみ表示される"""
        # ユーザーを作成
        analyst_id = uuid4()
        analyst = User(
            id=analyst_id,
            email="analyst@test.com",
            full_name="テスト分析者",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(analyst)

        lead = User(
            id=uuid4(),
            email="lead@test.com",
            full_name="テストリード",
            hashed_password="hash",
            role=UserRole.LEAD_PARTNER,
            is_active=True,
        )
        test_db.add(lead)
        await test_db.commit()

        # ANALYST として一覧取得
        users, total = await UserService.list_users(
            db=test_db,
            requester_id=analyst_id,
            requester_role=UserRole.ANALYST,
        )

        # 自分のみ表示されるはず
        assert len(users) == 1
        assert users[0].id == analyst_id

    async def test_list_users_lead_sees_analysts(self, test_db):
        """LEAD_PARTNER は ANALYST 以下を表示"""
        # ユーザーを作成
        lead_id = uuid4()
        lead = User(
            id=lead_id,
            email="lead@test.com",
            full_name="テストリード",
            hashed_password="hash",
            role=UserRole.LEAD_PARTNER,
            is_active=True,
        )
        test_db.add(lead)

        analyst = User(
            id=uuid4(),
            email="analyst@test.com",
            full_name="テスト分析者",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(analyst)

        admin = User(
            id=uuid4(),
            email="admin@test.com",
            full_name="テスト管理者",
            hashed_password="hash",
            role=UserRole.ADMIN,
            is_active=True,
        )
        test_db.add(admin)
        await test_db.commit()

        # LEAD として一覧取得
        users, total = await UserService.list_users(
            db=test_db,
            requester_id=lead_id,
            requester_role=UserRole.LEAD_PARTNER,
        )

        # リード自身と ANALYST が表示されるはず（ADMIN は表示されない）
        assert len(users) == 2
        roles = [u.role for u in users]
        assert UserRole.ANALYST in roles
        assert UserRole.LEAD_PARTNER in roles
        assert UserRole.ADMIN not in roles

    async def test_list_users_admin_sees_all(self, test_db):
        """ADMIN はすべてのユーザーを表示"""
        # 4人のユーザーを作成
        admin_id = uuid4()
        for role in [UserRole.ANALYST, UserRole.LEAD_PARTNER, UserRole.IC_MEMBER, UserRole.ADMIN]:
            user = User(
                id=uuid4() if role != UserRole.ADMIN else admin_id,
                email=f"{role.value}@test.com",
                full_name=f"テスト {role.value}",
                hashed_password="hash",
                role=role,
                is_active=True,
            )
            test_db.add(user)
        await test_db.commit()

        # ADMIN として一覧取得
        users, total = await UserService.list_users(
            db=test_db,
            requester_id=admin_id,
            requester_role=UserRole.ADMIN,
        )

        # すべてのユーザーが表示されるはず
        assert len(users) == 4
        assert total == 4


@pytest.mark.asyncio
class TestUserDelete:
    """delete_user メソッドのテスト"""

    async def test_delete_user_admin_only(self, test_db):
        """ADMIN のみがユーザーを削除できる"""
        admin = User(
            id=uuid4(),
            email="admin@test.com",
            full_name="管理者",
            hashed_password="hash",
            role=UserRole.ADMIN,
            is_active=True,
        )
        test_db.add(admin)

        target = User(
            id=uuid4(),
            email="target@test.com",
            full_name="削除対象",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(target)
        await test_db.commit()

        # ADMIN が削除
        deleted = await UserService.delete_user(
            db=test_db,
            user_id=target.id,
            requester_role=UserRole.ADMIN,
        )

        assert deleted.is_active is False

    async def test_delete_user_analyst_forbidden(self, test_db):
        """ANALYST は削除できない"""
        analyst = User(
            id=uuid4(),
            email="analyst@test.com",
            full_name="分析者",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(analyst)

        target = User(
            id=uuid4(),
            email="target@test.com",
            full_name="削除対象",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(target)
        await test_db.commit()

        # ANALYST が削除を試行
        with pytest.raises(AuthorizationException):
            await UserService.delete_user(
                db=test_db,
                user_id=target.id,
                requester_role=UserRole.ANALYST,
            )

    async def test_delete_user_not_found(self, test_db):
        """存在しないユーザーは削除できない"""
        with pytest.raises(NotFoundException):
            await UserService.delete_user(
                db=test_db,
                user_id=uuid4(),
                requester_role=UserRole.ADMIN,
            )


@pytest.mark.asyncio
class TestUserUpdate:
    """update_user_by_admin メソッドのテスト"""

    async def test_update_user_self(self, test_db):
        """ユーザーは自分の情報を更新できる"""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="user@test.com",
            full_name="元の名前",
            department="元の部門",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()

        # 自分の情報を更新
        update_data = UserUpdate(
            full_name="新しい名前",
            department="新しい部門",
        )
        updated = await UserService.update_user_by_admin(
            db=test_db,
            user_id=user_id,
            requester_id=user_id,
            requester_role=UserRole.ANALYST,
            update_data=update_data,
        )

        assert updated.full_name == "新しい名前"
        assert updated.department == "新しい部門"

    async def test_update_user_analyst_cannot_change_role(self, test_db):
        """ANALYST はロールを変更できない"""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="user@test.com",
            full_name="テストユーザー",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()

        # ロール変更を試行
        update_data = UserUpdate(role=UserRole.LEAD_PARTNER)
        with pytest.raises(AuthorizationException):
            await UserService.update_user_by_admin(
                db=test_db,
                user_id=user_id,
                requester_id=user_id,
                requester_role=UserRole.ANALYST,
                update_data=update_data,
            )

    async def test_update_user_admin_can_change_role(self, test_db):
        """ADMIN はロールを変更できる"""
        admin_id = uuid4()
        admin = User(
            id=admin_id,
            email="admin@test.com",
            full_name="管理者",
            hashed_password="hash",
            role=UserRole.ADMIN,
            is_active=True,
        )
        test_db.add(admin)

        user_id = uuid4()
        user = User(
            id=user_id,
            email="user@test.com",
            full_name="テストユーザー",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()

        # ADMIN がロール変更
        update_data = UserUpdate(role=UserRole.LEAD_PARTNER)
        updated = await UserService.update_user_by_admin(
            db=test_db,
            user_id=user_id,
            requester_id=admin_id,
            requester_role=UserRole.ADMIN,
            update_data=update_data,
        )

        assert updated.role == UserRole.LEAD_PARTNER


@pytest.mark.asyncio
class TestChangeUserRole:
    """change_user_role メソッドのテスト"""

    async def test_change_role_admin_only(self, test_db):
        """ADMIN のみロール変更できる"""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="user@test.com",
            full_name="テストユーザー",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()

        # ADMIN がロール変更
        updated = await UserService.change_user_role(
            db=test_db,
            user_id=user_id,
            new_role=UserRole.LEAD_PARTNER,
            requester_role=UserRole.ADMIN,
        )

        assert updated.role == UserRole.LEAD_PARTNER

    async def test_change_role_analyst_forbidden(self, test_db):
        """ANALYST は変更できない"""
        user_id = uuid4()
        user = User(
            id=user_id,
            email="user@test.com",
            full_name="テストユーザー",
            hashed_password="hash",
            role=UserRole.ANALYST,
            is_active=True,
        )
        test_db.add(user)
        await test_db.commit()

        # ANALYST がロール変更を試行
        with pytest.raises(AuthorizationException):
            await UserService.change_user_role(
                db=test_db,
                user_id=user_id,
                new_role=UserRole.LEAD_PARTNER,
                requester_role=UserRole.ANALYST,
            )
