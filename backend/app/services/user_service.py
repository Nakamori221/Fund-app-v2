"""User service - business logic for user management"""

from uuid import UUID
from typing import Optional, List, Tuple, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy import and_, or_, func
from sqlalchemy.orm import selectinload
from fastapi import Request

from app.models.database import User
from app.models.schemas import UserCreate, UserRole, UserUpdate, UserResponse
from app.core.security import AuthService
from app.core.errors import ValidationException, ConflictException, NotFoundException, AuthorizationException
from app.services.audit_log_service import AuditLogService
from app.services.pagination_service import PaginationService


class UserService:
    """User management service"""

    @staticmethod
    async def create_user(
        db: AsyncSession,
        user_data: UserCreate,
    ) -> User:
        """
        Create a new user account.

        **Parameters**:
        - db: Database session
        - user_data: User creation data (email, full_name, password, role)

        **Returns**:
        - Created User object

        **Errors**:
        - ValidationException: Invalid email or weak password
        - ConflictException: User already exists with this email
        """
        # Validate email format
        if not user_data.email or "@" not in user_data.email:
            raise ValidationException("Invalid email address")

        # Validate password strength
        if len(user_data.password) < 8:
            raise ValidationException("Password must be at least 8 characters")

        # Check if user already exists
        stmt = select(User).where(User.email == user_data.email)
        result = await db.execute(stmt)
        existing_user = result.scalar_one_or_none()

        if existing_user:
            raise ConflictException(f"User with email {user_data.email} already exists")

        # Hash password
        hashed_password = AuthService.hash_password(user_data.password)

        # Create user
        user = User(
            email=user_data.email,
            full_name=user_data.full_name,
            hashed_password=hashed_password,
            role=user_data.role,
            is_active=True,
        )

        db.add(user)
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def get_user_by_email(
        db: AsyncSession,
        email: str,
    ) -> Optional[User]:
        """
        Get user by email address.

        **Parameters**:
        - db: Database session
        - email: User email address

        **Returns**:
        - User object if found, None otherwise
        """
        stmt = select(User).where(User.email == email)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def get_user_by_id(
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[User]:
        """
        Get user by ID.

        **Parameters**:
        - db: Database session
        - user_id: User ID

        **Returns**:
        - User object if found, None otherwise
        """
        stmt = select(User).where(User.id == user_id)
        result = await db.execute(stmt)
        return result.scalar_one_or_none()

    @staticmethod
    async def authenticate_user(
        db: AsyncSession,
        email: str,
        password: str,
    ) -> Optional[User]:
        """
        Authenticate user with email and password.

        **Parameters**:
        - db: Database session
        - email: User email
        - password: Plain text password

        **Returns**:
        - User object if authentication successful, None otherwise
        """
        user = await UserService.get_user_by_email(db, email)

        if not user or not user.is_active:
            return None

        # Verify password
        if not AuthService.verify_password(password, user.hashed_password):
            return None

        return user

    @staticmethod
    async def update_user(
        db: AsyncSession,
        user_id: UUID,
        **kwargs,
    ) -> Optional[User]:
        """
        Update user information.

        **Parameters**:
        - db: Database session
        - user_id: User ID
        - kwargs: Fields to update (full_name, role, etc.)

        **Returns**:
        - Updated User object if found, None otherwise
        """
        user = await UserService.get_user_by_id(db, user_id)

        if not user:
            return None

        # Update fields
        for key, value in kwargs.items():
            if value is not None and hasattr(user, key):
                setattr(user, key, value)

        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def deactivate_user(
        db: AsyncSession,
        user_id: UUID,
    ) -> Optional[User]:
        """
        Deactivate user account (soft delete).

        **Parameters**:
        - db: Database session
        - user_id: User ID

        **Returns**:
        - Updated User object if found, None otherwise
        """
        return await UserService.update_user(db, user_id, is_active=False)

    @staticmethod
    async def get_users_by_role(
        db: AsyncSession,
        role: UserRole,
        skip: int = 0,
        limit: int = 100,
        include_audit_logs: bool = False,
    ) -> tuple[list[User], int]:
        """
        Get all users with a specific role.

        **Parameters**:
        - db: Database session
        - role: User role to filter by
        - skip: Number of records to skip
        - limit: Number of records to return
        - include_audit_logs: Whether to eager load audit logs (Eager Loading optimization)

        **Returns**:
        - Tuple of (users list, total count)
        """
        # Get total count
        count_stmt = select(func.count()).select_from(User).where(User.role == role)
        total = await db.scalar(count_stmt)

        # Get paginated results with Eager Loading
        stmt = (
            select(User)
            .where(User.role == role)
            .order_by(User.created_at.desc())
            .offset(skip)
            .limit(limit)
        )

        # Add Eager Loading if requested
        if include_audit_logs:
            stmt = stmt.options(selectinload(User.audit_logs))

        result = await db.execute(stmt)
        users = result.scalars().unique().all() if include_audit_logs else result.scalars().all()

        return users, total

    @staticmethod
    async def get_users_by_role_with_cursor(
        db: AsyncSession,
        role: UserRole,
        cursor: Optional[str] = None,
        limit: int = 20,
        include_audit_logs: bool = False,
    ) -> Tuple[List[User], Optional[str], bool]:
        """
        Get all users with a specific role using Cursor-based Pagination.

        **Parameters**:
        - db: Database session
        - role: User role to filter by
        - cursor: Pagination cursor (None for first page)
        - limit: Number of records to return (1-100)
        - include_audit_logs: Whether to eager load audit logs (Eager Loading optimization)

        **Returns**:
        - Tuple of (users list, next_cursor, has_more)

        **Features**:
        - O(limit) time complexity regardless of dataset size
        - Consistent ordering even with data modifications
        """
        # Build base query
        query = select(User).where(User.role == role).order_by(User.created_at.desc(), User.id)

        # Add Eager Loading if requested
        if include_audit_logs:
            query = query.options(selectinload(User.audit_logs))

        # Execute cursor-based pagination
        users, next_cursor, has_more = await PaginationService.paginate(
            db=db,
            query=query,
            cursor=cursor,
            limit=limit,
            order_by_created_at=True,
        )

        return users, next_cursor, has_more

    @staticmethod
    async def verify_user_exists(
        db: AsyncSession,
        user_id: UUID,
    ) -> bool:
        """
        Check if user exists.

        **Parameters**:
        - db: Database session
        - user_id: User ID

        **Returns**:
        - True if user exists and is active, False otherwise
        """
        user = await UserService.get_user_by_id(db, user_id)
        return user is not None and user.is_active

    @staticmethod
    async def list_users(
        db: AsyncSession,
        requester_id: UUID,
        requester_role: UserRole,
        skip: int = 0,
        limit: int = 20,
        role_filter: Optional[UserRole] = None,
        is_active_filter: Optional[bool] = None,
        search: Optional[str] = None,
        include_audit_logs: bool = False,
    ) -> Tuple[List[User], int]:
        """
        ユーザー一覧取得（RBAC対応、Eager Loading対応）

        **Parameters**:
        - db: Database session
        - requester_id: リクエスター ID
        - requester_role: リクエスターロール
        - skip: スキップ数
        - limit: 取得数
        - role_filter: ロール絞り込み
        - is_active_filter: アクティブ状態絞り込み
        - search: 名前・メール検索
        - include_audit_logs: Whether to eager load audit logs (Eager Loading optimization)

        **Returns**:
        - (ユーザーリスト, 総数)

        **RBAC規則**:
        - ANALYST: 自分自身のみ
        - LEAD_PARTNER: 同じロール以下
        - IC_MEMBER: すべてのユーザー
        - ADMIN: すべてのユーザー
        """
        filters = []

        # RBAC フィルタリング
        if requester_role == UserRole.ANALYST:
            filters.append(User.id == requester_id)
        elif requester_role == UserRole.LEAD_PARTNER:
            filters.append(
                or_(
                    User.id == requester_id,
                    User.role == UserRole.ANALYST,
                )
            )
        # IC_MEMBER, ADMIN: フィルタなし（全ユーザー表示）

        # その他フィルタ
        if role_filter:
            filters.append(User.role == role_filter)

        if is_active_filter is not None:
            filters.append(User.is_active == is_active_filter)

        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    User.full_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )

        # 総数取得
        count_stmt = select(func.count()).select_from(User)
        if filters:
            count_stmt = count_stmt.where(and_(*filters))
        total = await db.scalar(count_stmt)

        # ページネーション結果取得（Eager Loading対応）
        query = select(User)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(User.created_at.desc())

        # Add Eager Loading if requested
        if include_audit_logs:
            query = query.options(selectinload(User.audit_logs))

        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        users = result.scalars().unique().all() if include_audit_logs else result.scalars().all()

        return users, total

    @staticmethod
    async def list_users_with_cursor(
        db: AsyncSession,
        requester_id: UUID,
        requester_role: UserRole,
        cursor: Optional[str] = None,
        limit: int = 20,
        role_filter: Optional[UserRole] = None,
        is_active_filter: Optional[bool] = None,
        search: Optional[str] = None,
        include_audit_logs: bool = False,
    ) -> Tuple[List[User], Optional[str], bool]:
        """
        ユーザー一覧取得（Cursor-based Pagination対応、RBAC対応）

        **Parameters**:
        - db: Database session
        - requester_id: リクエスター ID
        - requester_role: リクエスターロール
        - cursor: ページングカーソル（Noneで最初のページ）
        - limit: 取得数（1-100）
        - role_filter: ロール絞り込み
        - is_active_filter: アクティブ状態絞り込み
        - search: 名前・メール検索
        - include_audit_logs: Eager Loading を有効化するか

        **Returns**:
        - (ユーザーリスト, 次ページカーソル, さらにページがあるか)

        **Features**:
        - O(limit) 時間複雑度（データセットサイズに無依存）
        - 一貫した順序付け（作成日時 DESC、その後ID）
        - RBAC に基づくフィルタリング

        **RBAC規則**:
        - ANALYST: 自分自身のみ
        - LEAD_PARTNER: 同じロール以下
        - IC_MEMBER: すべてのユーザー
        - ADMIN: すべてのユーザー
        """
        filters = []

        # RBAC フィルタリング
        if requester_role == UserRole.ANALYST:
            filters.append(User.id == requester_id)
        elif requester_role == UserRole.LEAD_PARTNER:
            filters.append(
                or_(
                    User.id == requester_id,
                    User.role == UserRole.ANALYST,
                )
            )
        # IC_MEMBER, ADMIN: フィルタなし（全ユーザー表示）

        # その他フィルタ
        if role_filter:
            filters.append(User.role == role_filter)

        if is_active_filter is not None:
            filters.append(User.is_active == is_active_filter)

        if search:
            search_pattern = f"%{search}%"
            filters.append(
                or_(
                    User.full_name.ilike(search_pattern),
                    User.email.ilike(search_pattern),
                )
            )

        # ベースクエリの構築
        query = select(User)
        if filters:
            query = query.where(and_(*filters))
        query = query.order_by(User.created_at.desc(), User.id)

        # Eager Loading オプション
        if include_audit_logs:
            query = query.options(selectinload(User.audit_logs))

        # Cursor-based pagination を実行
        users, next_cursor, has_more = await PaginationService.paginate(
            db=db,
            query=query,
            cursor=cursor,
            limit=limit,
            order_by_created_at=True,
        )

        return users, next_cursor, has_more

    @staticmethod
    async def delete_user(
        db: AsyncSession,
        user_id: UUID,
        requester_role: UserRole,
    ) -> User:
        """
        ユーザーを削除（ソフトデリート）

        **Parameters**:
        - db: Database session
        - user_id: 削除するユーザーID
        - requester_role: リクエスターロール

        **Returns**:
        - 削除されたUser オブジェクト

        **RBAC規則**:
        - Admin のみ削除可能

        **Errors**:
        - NotFoundException: ユーザーが見つかりません
        - AuthorizationException: 権限不足
        """
        # 認可チェック
        if requester_role != UserRole.ADMIN:
            raise AuthorizationException("このアクションを実行する権限がありません")

        # ユーザー取得
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException("ユーザーが見つかりません")

        # ソフトデリート
        user.is_active = False
        await db.commit()
        await db.refresh(user)

        return user

    @staticmethod
    async def update_user_by_admin(
        db: AsyncSession,
        user_id: UUID,
        requester_id: UUID,
        requester_role: UserRole,
        update_data: UserUpdate,
    ) -> User:
        """
        ユーザー情報を更新（RBAC対応）

        **Parameters**:
        - db: Database session
        - user_id: 更新するユーザーID
        - requester_id: リクエスターID
        - requester_role: リクエスターロール
        - update_data: 更新データ

        **Returns**:
        - 更新されたUser オブジェクト

        **RBAC規則**:
        - ANALYST: 自分自身のみ更新可（ロール変更不可）
        - LEAD_PARTNER: 同じロール以下のユーザーを更新可
        - ADMIN: すべてのユーザーを更新可

        **Errors**:
        - NotFoundException: ユーザーが見つかりません
        - AuthorizationException: 権限不足
        - ConflictException: メール重複
        """
        # ユーザー取得
        target_user = await UserService.get_user_by_id(db, user_id)
        if not target_user:
            raise NotFoundException("ユーザーが見つかりません")

        # 認可チェック
        is_self = user_id == requester_id
        is_admin = requester_role == UserRole.ADMIN
        is_lead_or_above = requester_role in [
            UserRole.LEAD_PARTNER,
            UserRole.IC_MEMBER,
            UserRole.ADMIN,
        ]

        if not is_self and not is_lead_or_above:
            raise AuthorizationException("このアクションを実行する権限がありません")

        # ANALYST は自分自身のみ、ロール変更不可
        if requester_role == UserRole.ANALYST and not is_self:
            raise AuthorizationException("他のユーザーを更新することはできません")

        if requester_role == UserRole.ANALYST and update_data.role is not None:
            raise AuthorizationException("ロールを変更する権限がありません")

        # メールアドレス更新時の重複チェック
        if update_data.email and update_data.email != target_user.email:
            existing_user = await UserService.get_user_by_email(db, update_data.email)
            if existing_user:
                raise ConflictException("このメールアドレスは既に登録されています")

        # フィールド更新
        if update_data.email is not None:
            target_user.email = update_data.email
        if update_data.full_name is not None:
            target_user.full_name = update_data.full_name
        if update_data.department is not None:
            target_user.department = update_data.department
        if update_data.is_active is not None:
            target_user.is_active = update_data.is_active
        if update_data.role is not None:
            if is_admin:
                target_user.role = update_data.role
            else:
                raise AuthorizationException("ロールを変更する権限がありません")

        await db.commit()
        await db.refresh(target_user)

        return target_user

    @staticmethod
    async def change_user_role(
        db: AsyncSession,
        user_id: UUID,
        new_role: UserRole,
        requester_role: UserRole,
    ) -> User:
        """
        ユーザーのロールを変更

        **Parameters**:
        - db: Database session
        - user_id: ユーザーID
        - new_role: 新しいロール
        - requester_role: リクエスターロール

        **Returns**:
        - 更新されたUser オブジェクト

        **RBAC規則**:
        - Admin のみロール変更可能

        **Errors**:
        - NotFoundException: ユーザーが見つかりません
        - AuthorizationException: 権限不足
        """
        # 認可チェック
        if requester_role != UserRole.ADMIN:
            raise AuthorizationException("このアクションを実行する権限がありません")

        # ユーザー取得
        user = await UserService.get_user_by_id(db, user_id)
        if not user:
            raise NotFoundException("ユーザーが見つかりません")

        # ロール変更
        user.role = new_role
        await db.commit()
        await db.refresh(user)

        return user
