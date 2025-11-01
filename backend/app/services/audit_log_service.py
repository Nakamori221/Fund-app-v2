"""監査ログサービス"""

from datetime import datetime
from typing import Optional, List, Tuple, Dict, Any
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_, or_
from fastapi import Request

from app.models.database import AuditLog, User
from app.models.schemas import AuditLogResponse


class AuditLogService:
    """監査ログサービス"""

    @staticmethod
    async def log_action(
        db: AsyncSession,
        user_id: UUID,
        action: str,
        resource_type: str,
        resource_id: UUID,
        old_values: Optional[Dict[str, Any]] = None,
        new_values: Optional[Dict[str, Any]] = None,
        request: Optional[Request] = None,
        extra_data: Optional[Dict[str, Any]] = None,
    ) -> AuditLog:
        """
        操作を監査ログに記録

        Parameters:
        -----------
        db : AsyncSession
            データベースセッション
        user_id : UUID
            操作ユーザーID
        action : str
            操作: create, read, update, delete, approve
        resource_type : str
            リソース種別: user, case, observation
        resource_id : UUID
            リソースID
        old_values : Optional[Dict]
            更新前の値（update時）
        new_values : Optional[Dict]
            更新後の値
        request : Optional[Request]
            FastAPI Request オブジェクト（メタデータ抽出用）
        extra_data : Optional[Dict]
            追加データ

        Returns:
        --------
        AuditLog
            作成された監査ログレコード
        """
        # リクエストからメタデータ抽出
        ip_address = None
        user_agent = None

        if request:
            try:
                ip_address = request.client.host if request.client else None
                user_agent = request.headers.get("user-agent")
            except Exception:
                pass

        # ログ作成
        log = AuditLog(
            user_id=user_id,
            action=action,
            resource_type=resource_type,
            resource_id=resource_id,
            old_values=old_values,
            new_values=new_values,
            ip_address=ip_address,
            user_agent=user_agent,
            extra_data=extra_data or {},
        )

        db.add(log)
        await db.commit()
        await db.refresh(log)

        return log

    @staticmethod
    async def get_logs(
        db: AsyncSession,
        skip: int = 0,
        limit: int = 20,
        user_id: Optional[UUID] = None,
        resource_type: Optional[str] = None,
        action: Optional[str] = None,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        resource_id: Optional[UUID] = None,
    ) -> Tuple[List[AuditLog], int]:
        """
        監査ログを取得（フィルタリング対応）

        Parameters:
        -----------
        db : AsyncSession
            データベースセッション
        skip : int
            スキップレコード数
        limit : int
            取得レコード数
        user_id : Optional[UUID]
            ユーザーIDフィルタ
        resource_type : Optional[str]
            リソース種別フィルタ
        action : Optional[str]
            操作タイプフィルタ
        start_date : Optional[datetime]
            開始日時フィルタ
        end_date : Optional[datetime]
            終了日時フィルタ
        resource_id : Optional[UUID]
            リソースIDフィルタ

        Returns:
        --------
        Tuple[List[AuditLog], int]
            (監査ログリスト, 総件数)
        """
        # フィルタ条件構築
        filters = []

        if user_id:
            filters.append(AuditLog.user_id == user_id)

        if resource_type:
            filters.append(AuditLog.resource_type == resource_type)

        if action:
            filters.append(AuditLog.action == action)

        if resource_id:
            filters.append(AuditLog.resource_id == resource_id)

        if start_date:
            filters.append(AuditLog.timestamp >= start_date)

        if end_date:
            filters.append(AuditLog.timestamp <= end_date)

        # 総件数取得
        count_query = select(func.count()).select_from(AuditLog)
        if filters:
            count_query = count_query.where(and_(*filters))

        total = await db.scalar(count_query)

        # ログ取得
        query = select(AuditLog)
        if filters:
            query = query.where(and_(*filters))

        query = query.order_by(AuditLog.timestamp.desc())
        query = query.offset(skip).limit(limit)

        result = await db.execute(query)
        logs = result.scalars().all()

        return logs, total if total else 0

    @staticmethod
    async def get_user_logs(
        db: AsyncSession,
        user_id: UUID,
        skip: int = 0,
        limit: int = 20,
        action: Optional[str] = None,
        resource_type: Optional[str] = None,
    ) -> Tuple[List[AuditLog], int]:
        """
        特定ユーザーの監査ログを取得

        Parameters:
        -----------
        db : AsyncSession
            データベースセッション
        user_id : UUID
            対象ユーザーID
        skip : int
            スキップレコード数
        limit : int
            取得レコード数
        action : Optional[str]
            操作タイプフィルタ
        resource_type : Optional[str]
            リソース種別フィルタ

        Returns:
        --------
        Tuple[List[AuditLog], int]
            (監査ログリスト, 総件数)
        """
        return await AuditLogService.get_logs(
            db=db,
            skip=skip,
            limit=limit,
            user_id=user_id,
            action=action,
            resource_type=resource_type,
        )

    @staticmethod
    async def get_resource_logs(
        db: AsyncSession,
        resource_id: UUID,
        resource_type: str,
        skip: int = 0,
        limit: int = 20,
    ) -> Tuple[List[AuditLog], int]:
        """
        特定リソースの監査ログを取得

        Parameters:
        -----------
        db : AsyncSession
            データベースセッション
        resource_id : UUID
            リソースID
        resource_type : str
            リソース種別
        skip : int
            スキップレコード数
        limit : int
            取得レコード数

        Returns:
        --------
        Tuple[List[AuditLog], int]
            (監査ログリスト, 総件数)
        """
        return await AuditLogService.get_logs(
            db=db,
            skip=skip,
            limit=limit,
            resource_id=resource_id,
            resource_type=resource_type,
        )

    @staticmethod
    async def get_statistics(
        db: AsyncSession,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
    ) -> Dict[str, Any]:
        """
        監査ログ統計を取得

        Parameters:
        -----------
        db : AsyncSession
            データベースセッション
        start_date : Optional[datetime]
            開始日時
        end_date : Optional[datetime]
            終了日時

        Returns:
        --------
        Dict[str, Any]
            統計情報
        """
        filters = []

        if start_date:
            filters.append(AuditLog.timestamp >= start_date)

        if end_date:
            filters.append(AuditLog.timestamp <= end_date)

        # 全操作数
        count_query = select(func.count()).select_from(AuditLog)
        if filters:
            count_query = count_query.where(and_(*filters))

        total_logs = await db.scalar(count_query)

        # アクション別集計
        action_query = select(
            AuditLog.action, func.count().label("count")
        ).group_by(AuditLog.action)

        if filters:
            action_query = action_query.where(and_(*filters))

        action_result = await db.execute(action_query)
        action_stats = {row[0]: row[1] for row in action_result.all()}

        # リソース種別別集計
        resource_query = select(
            AuditLog.resource_type, func.count().label("count")
        ).group_by(AuditLog.resource_type)

        if filters:
            resource_query = resource_query.where(and_(*filters))

        resource_result = await db.execute(resource_query)
        resource_stats = {row[0]: row[1] for row in resource_result.all()}

        return {
            "total_logs": total_logs,
            "by_action": action_stats,
            "by_resource_type": resource_stats,
        }
