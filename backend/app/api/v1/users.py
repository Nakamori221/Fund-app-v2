"""ユーザー管理APIエンドポイント"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.errors import NotFoundException, ValidationException, AuthorizationException, ConflictException
from app.models.schemas import (
    UserCreate,
    UserUpdate,
    UserResponse,
    UserListResponse,
    UserRole,
    RoleInfo,
    RoleListResponse,
    ChangeRoleRequest,
)
from app.services.user_service import UserService


router = APIRouter()


# ロール情報定義
ROLE_DESCRIPTIONS = {
    UserRole.ANALYST: "分析者：ケース作成・観察記録を行うことができます",
    UserRole.LEAD_PARTNER: "リード・パートナー：レビューと承認を行うことができます",
    UserRole.IC_MEMBER: "IC メンバー：システム全体を監視・管理することができます",
    UserRole.ADMIN: "管理者：ユーザー管理など全権限を持ちます",
}

ROLE_PERMISSIONS = {
    UserRole.ANALYST: [
        "case:create",
        "observation:create",
        "observation:edit_own",
    ],
    UserRole.LEAD_PARTNER: [
        "case:read",
        "case:edit",
        "observation:verify",
        "conflict:resolve",
    ],
    UserRole.IC_MEMBER: [
        "case:read",
        "observation:read",
        "report:generate",
        "analytics:view",
    ],
    UserRole.ADMIN: ["*"],
}


@router.post(
    "/users",
    response_model=UserResponse,
    status_code=status.HTTP_201_CREATED,
    summary="ユーザーを作成",
    tags=["ユーザー管理"],
)
async def create_user(
    user_data: UserCreate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """
    新規ユーザーを作成します（Adminのみ）

    **要件**:
    - 管理者権限が必要です
    - メールアドレスは一意である必要があります
    - パスワードは8文字以上である必要があります
    """
    # 認可チェック
    if current_user["role"] != UserRole.ADMIN:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアクションを実行する権限がありません",
        )

    try:
        user = await UserService.create_user(db, user_data)
        return UserResponse.model_validate(user)
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.get(
    "/users",
    response_model=UserListResponse,
    summary="ユーザー一覧を取得",
    tags=["ユーザー管理"],
)
async def list_users(
    skip: int = Query(0, ge=0, description="スキップレコード数"),
    limit: int = Query(20, ge=1, le=100, description="取得レコード数"),
    role_filter: Optional[UserRole] = Query(None, description="ロール絞り込み"),
    is_active: Optional[bool] = Query(None, description="アクティブ状態絞り込み"),
    search: Optional[str] = Query(None, description="名前・メール検索"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserListResponse:
    """
    ユーザー一覧を取得します（RBAC対応）

    **RBAC規則**:
    - ANALYST: 自分自身のみ表示
    - LEAD_PARTNER: ANALYST ロール以下のユーザーを表示
    - IC_MEMBER・ADMIN: すべてのユーザーを表示
    """
    users, total = await UserService.list_users(
        db=db,
        requester_id=UUID(current_user["user_id"]),
        requester_role=UserRole(current_user["role"]),
        skip=skip,
        limit=limit,
        role_filter=role_filter,
        is_active_filter=is_active,
        search=search,
    )

    return UserListResponse(
        users=[UserResponse.model_validate(u) for u in users],
        total=total,
        skip=skip,
        limit=limit,
    )


@router.get(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="ユーザー詳細を取得",
    tags=["ユーザー管理"],
)
async def get_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """
    ユーザーの詳細情報を取得します

    **認可**:
    - 自分自身の情報は常に取得可能
    - 他のユーザーの情報はLead Partner以上で取得可能
    """
    # ユーザー取得
    user = await UserService.get_user_by_id(db, user_id)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="ユーザーが見つかりません",
        )

    # 認可チェック
    is_self = user_id == UUID(current_user["user_id"])
    is_lead_or_above = current_user["role"] in [
        UserRole.LEAD_PARTNER,
        UserRole.IC_MEMBER,
        UserRole.ADMIN,
    ]

    if not is_self and not is_lead_or_above:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="このアクションを実行する権限がありません",
        )

    return UserResponse.model_validate(user)


@router.put(
    "/users/{user_id}",
    response_model=UserResponse,
    summary="ユーザー情報を更新",
    tags=["ユーザー管理"],
)
async def update_user(
    user_id: UUID,
    update_data: UserUpdate,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """
    ユーザー情報を更新します（RBAC対応）

    **RBAC規則**:
    - ANALYST: 自分自身のみ更新可（ロール変更不可）
    - LEAD_PARTNER: ANALYST以下のユーザーを更新可
    - ADMIN: すべてのユーザーを更新可
    """
    try:
        user = await UserService.update_user_by_admin(
            db=db,
            user_id=user_id,
            requester_id=UUID(current_user["user_id"]),
            requester_role=UserRole(current_user["role"]),
            update_data=update_data,
        )
        return UserResponse.model_validate(user)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )
    except ConflictException as e:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=str(e),
        )
    except ValidationException as e:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=str(e),
        )


@router.delete(
    "/users/{user_id}",
    status_code=status.HTTP_200_OK,
    summary="ユーザーを削除",
    tags=["ユーザー管理"],
)
async def delete_user(
    user_id: UUID,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    ユーザーを削除します（Adminのみ、ソフトデリート）

    **要件**:
    - 管理者権限が必要です
    - 削除はソフトデリート（is_active フラグで無効化）です
    """
    try:
        await UserService.delete_user(
            db=db,
            user_id=user_id,
            requester_role=UserRole(current_user["role"]),
        )
        return {"message": "ユーザーを削除しました", "user_id": str(user_id)}
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.post(
    "/users/{user_id}/role",
    response_model=UserResponse,
    summary="ユーザーロールを変更",
    tags=["ユーザー管理"],
)
async def change_user_role(
    user_id: UUID,
    role_request: ChangeRoleRequest,
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> UserResponse:
    """
    ユーザーのロールを変更します（Adminのみ）

    **要件**:
    - 管理者権限が必要です
    """
    try:
        user = await UserService.change_user_role(
            db=db,
            user_id=user_id,
            new_role=role_request.role,
            requester_role=UserRole(current_user["role"]),
        )
        return UserResponse.model_validate(user)
    except NotFoundException as e:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(e),
        )
    except AuthorizationException as e:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail=str(e),
        )


@router.get(
    "/roles",
    response_model=RoleListResponse,
    summary="利用可能なロール一覧を取得",
    tags=["ユーザー管理"],
)
async def get_available_roles(
    current_user: dict = Depends(get_current_user),
) -> RoleListResponse:
    """
    システムで利用可能なロール一覧と権限情報を取得します
    """
    roles = [
        RoleInfo(
            role=role,
            description=ROLE_DESCRIPTIONS[role],
            permissions=ROLE_PERMISSIONS[role],
        )
        for role in UserRole
    ]
    return RoleListResponse(roles=roles)
