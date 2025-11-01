"""監査ログAPIエンドポイント"""

from datetime import datetime
from typing import Optional
from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.errors import ValidationException
from app.models.schemas import (
    AuditLogListResponse,
    AuditLogResponse,
    UserRole,
)
from app.services.audit_log_service import AuditLogService


router = APIRouter()


@router.get(
    "/audit-logs",
    response_model=AuditLogListResponse,
    summary="監査ログ一覧を取得",
    tags=["監査ログ"],
)
async def get_audit_logs(
    skip: int = Query(0, ge=0, description="スキップレコード数"),
    limit: int = Query(20, ge=1, le=100, description="取得レコード数"),
    user_id: Optional[str] = Query(None, description="ユーザーID フィルタ"),
    resource_type: Optional[str] = Query(None, description="リソース種別フィルタ"),
    action: Optional[str] = Query(None, description="操作タイプフィルタ"),
    start_date: Optional[datetime] = Query(None, description="開始日時フィルタ"),
    end_date: Optional[datetime] = Query(None, description="終了日時フィルタ"),
    resource_id: Optional[str] = Query(None, description="リソースID フィルタ"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AuditLogListResponse:
    """
    監査ログ一覧を取得します（RBAC対応）

    **認可**:
    - IC_MEMBER・ADMIN: 全監査ログ閲覧可
    - 他のロール: 自分のアクションのみ閲覧可

    **フィルタ**:
    - user_id: 操作ユーザーID
    - resource_type: リソース種別（user, case, observation）
    - action: 操作タイプ（create, read, update, delete, approve）
    - start_date: 開始日時
    - end_date: 終了日時
    - resource_id: リソースID
    """
    # RBAC チェック
    current_user_role = UserRole(current_user["role"])
    current_user_id = UUID(current_user["user_id"])

    # フィルタの初期化
    filter_user_id = None
    filter_resource_id = None

    # ロール別のアクセス制御
    if current_user_role not in [UserRole.IC_MEMBER, UserRole.ADMIN]:
        # IC_MEMBER と ADMIN 以外は自分のアクションのみ
        filter_user_id = current_user_id
    else:
        # IC_MEMBER・ADMIN は user_id フィルタを使用可能
        if user_id:
            try:
                filter_user_id = UUID(user_id)
            except ValueError:
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Invalid user_id format",
                )

    # resource_id を UUID に変換
    if resource_id:
        try:
            filter_resource_id = UUID(resource_id)
        except ValueError:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Invalid resource_id format",
            )

    try:
        logs, total = await AuditLogService.get_logs(
            db=db,
            skip=skip,
            limit=limit,
            user_id=filter_user_id,
            resource_type=resource_type,
            action=action,
            start_date=start_date,
            end_date=end_date,
            resource_id=filter_resource_id,
        )

        return AuditLogListResponse(
            logs=[AuditLogResponse.model_validate(log) for log in logs],
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit logs: {str(e)}",
        )


@router.get(
    "/audit-logs/user/{user_id}",
    response_model=AuditLogListResponse,
    summary="特定ユーザーの監査ログを取得",
    tags=["監査ログ"],
)
async def get_user_audit_logs(
    user_id: UUID,
    skip: int = Query(0, ge=0, description="スキップレコード数"),
    limit: int = Query(20, ge=1, le=100, description="取得レコード数"),
    action: Optional[str] = Query(None, description="操作タイプフィルタ"),
    resource_type: Optional[str] = Query(None, description="リソース種別フィルタ"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AuditLogListResponse:
    """
    特定ユーザーの監査ログを取得します（RBAC対応）

    **認可**:
    - IC_MEMBER・ADMIN: 全ユーザーの監査ログ閲覧可
    - 他のロール: 自分の監査ログのみ閲覧可
    """
    # RBAC チェック
    current_user_role = UserRole(current_user["role"])
    current_user_id = UUID(current_user["user_id"])

    # IC_MEMBER・ADMIN 以外は自分のログのみ
    if current_user_role not in [UserRole.IC_MEMBER, UserRole.ADMIN]:
        if user_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="他のユーザーの監査ログを閲覧する権限がありません",
            )

    try:
        logs, total = await AuditLogService.get_user_logs(
            db=db,
            user_id=user_id,
            skip=skip,
            limit=limit,
            action=action,
            resource_type=resource_type,
        )

        return AuditLogListResponse(
            logs=[AuditLogResponse.model_validate(log) for log in logs],
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch user audit logs: {str(e)}",
        )


@router.get(
    "/audit-logs/resource/{resource_id}",
    response_model=AuditLogListResponse,
    summary="特定リソースの監査ログを取得",
    tags=["監査ログ"],
)
async def get_resource_audit_logs(
    resource_id: UUID,
    resource_type: str = Query(..., description="リソース種別"),
    skip: int = Query(0, ge=0, description="スキップレコード数"),
    limit: int = Query(20, ge=1, le=100, description="取得レコード数"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
) -> AuditLogListResponse:
    """
    特定リソースに対する監査ログを取得します

    **認可**:
    - IC_MEMBER・ADMIN: すべてのリソース監査ログ閲覧可
    - 他のロール: リソース タイプが user の場合のみ、自分のユーザーレコードの監査ログ閲覧可
    """
    # RBAC チェック
    current_user_role = UserRole(current_user["role"])
    current_user_id = UUID(current_user["user_id"])

    # IC_MEMBER・ADMIN 以外は user リソース タイプで自分の ID のみ
    if current_user_role not in [UserRole.IC_MEMBER, UserRole.ADMIN]:
        if resource_type != "user" or resource_id != current_user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="このリソースの監査ログを閲覧する権限がありません",
            )

    try:
        logs, total = await AuditLogService.get_resource_logs(
            db=db,
            resource_id=resource_id,
            resource_type=resource_type,
            skip=skip,
            limit=limit,
        )

        return AuditLogListResponse(
            logs=[AuditLogResponse.model_validate(log) for log in logs],
            total=total,
            skip=skip,
            limit=limit,
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch resource audit logs: {str(e)}",
        )


@router.get(
    "/audit-logs/statistics",
    summary="監査ログ統計を取得",
    tags=["監査ログ"],
)
async def get_audit_log_statistics(
    start_date: Optional[datetime] = Query(None, description="開始日時"),
    end_date: Optional[datetime] = Query(None, description="終了日時"),
    db: AsyncSession = Depends(get_db),
    current_user: dict = Depends(get_current_user),
):
    """
    監査ログの統計情報を取得します（IC_MEMBER・ADMINのみ）

    **認可**:
    - IC_MEMBER・ADMIN: 統計情報閲覧可

    **応答**:
    ```json
    {
        "total_logs": 1500,
        "by_action": {
            "create": 500,
            "update": 700,
            "delete": 200,
            "read": 100
        },
        "by_resource_type": {
            "user": 600,
            "case": 700,
            "observation": 200
        }
    }
    ```
    """
    # RBAC チェック
    current_user_role = UserRole(current_user["role"])

    if current_user_role not in [UserRole.IC_MEMBER, UserRole.ADMIN]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="監査ログ統計を閲覧する権限がありません",
        )

    try:
        statistics = await AuditLogService.get_statistics(
            db=db,
            start_date=start_date,
            end_date=end_date,
        )

        return {
            "statistics": statistics,
            "start_date": start_date,
            "end_date": end_date,
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to fetch audit log statistics: {str(e)}",
        )
