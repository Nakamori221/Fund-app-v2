"""Conflicts API endpoints"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel

from app.database import get_db
from app.core.security import get_current_user
from app.core.errors import NotFoundException, ValidationException, AuthorizationException
from app.models.schemas import ConflictResponse, PaginatedResponse
from app.services.conflict_service import ConflictService


router = APIRouter()


class ResolveConflictRequest(BaseModel):
    """Request for resolving a conflict"""

    resolution_notes: Optional[str] = None


@router.post(
    "/detect",
    response_model=PaginatedResponse,
    summary="Detect conflicts",
)
async def detect_conflicts(
    case_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Detect conflicts in a case.

    **Query Parameters**:
    - **case_id**: Case ID (UUID)

    **Returns**:
    - List of detected conflicts

    **Access Control**:
    - Only Lead Partner+ can detect conflicts

    **Errors**:
    - 400: Invalid case ID format
    - 404: Case not found
    - 403: Not authorized (requires lead partner+)
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        conflicts = await ConflictService.detect_conflicts(
            db,
            case_uuid,
            user_id,
            user_role,
        )

        conflict_responses = [
            ConflictResponse(
                id=str(conflict.id),
                case_id=str(conflict.case_id),
                observation_id_1=str(conflict.observation_id_1),
                observation_id_2=str(conflict.observation_id_2),
                conflict_type=conflict.conflict_type,
                severity=conflict.severity,
                description=conflict.description,
                detected_at=conflict.detected_at,
                is_resolved=conflict.is_resolved,
            )
            for conflict in conflicts
        ]

        return PaginatedResponse(
            data=conflict_responses,
            total=len(conflict_responses),
            skip=0,
            limit=len(conflict_responses),
            has_more=False,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid case ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List conflicts",
)
async def list_conflicts(
    case_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    resolved: Optional[bool] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List conflicts for a case.

    **Query Parameters**:
    - **case_id**: Case ID (UUID)
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Number of items to return (default: 20, max: 100)
    - **resolved**: Filter by resolved status (True/False/None for all)

    **Returns**:
    - Paginated list of conflicts

    **Access Control**:
    - Analyst: Can see conflicts in own cases only
    - Lead Partner+: Can see all conflicts

    **Errors**:
    - 400: Invalid case ID format
    - 404: Case not found
    - 403: Not authorized
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        conflicts, total = await ConflictService.get_conflicts(
            db,
            case_uuid,
            user_id,
            user_role,
            skip=skip,
            limit=limit,
            resolved_filter=resolved,
        )

        conflict_responses = [
            ConflictResponse(
                id=str(conflict.id),
                case_id=str(conflict.case_id),
                observation_id_1=str(conflict.observation_id_1),
                observation_id_2=str(conflict.observation_id_2),
                conflict_type=conflict.conflict_type,
                severity=conflict.severity,
                description=conflict.description,
                detected_at=conflict.detected_at,
                is_resolved=conflict.is_resolved,
            )
            for conflict in conflicts
        ]

        has_more = (skip + limit) < total

        return PaginatedResponse(
            data=conflict_responses,
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid case ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/{conflict_id}",
    response_model=ConflictResponse,
    summary="Get conflict",
)
async def get_conflict(
    conflict_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get conflict details.

    **Path Parameters**:
    - **conflict_id**: Conflict ID (UUID)

    **Returns**:
    - Conflict details

    **Errors**:
    - 400: Invalid conflict ID format
    - 404: Conflict not found
    - 500: Internal server error
    """
    try:
        conflict_uuid = UUID(conflict_id)

        conflict = await ConflictService.get_conflict_by_id(db, conflict_uuid)

        if not conflict:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Conflict not found",
            )

        return ConflictResponse(
            id=str(conflict.id),
            case_id=str(conflict.case_id),
            observation_id_1=str(conflict.observation_id_1),
            observation_id_2=str(conflict.observation_id_2),
            conflict_type=conflict.conflict_type,
            severity=conflict.severity,
            description=conflict.description,
            detected_at=conflict.detected_at,
            is_resolved=conflict.is_resolved,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conflict ID format",
        )


@router.post(
    "/{conflict_id}/resolve",
    response_model=ConflictResponse,
    summary="Resolve conflict",
)
async def resolve_conflict(
    conflict_id: str,
    request: ResolveConflictRequest,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Resolve a conflict.

    **Path Parameters**:
    - **conflict_id**: Conflict ID (UUID)

    **Request Body**:
    - **resolution_notes**: Notes on the resolution (optional)

    **Returns**:
    - Resolved conflict

    **Access Control**:
    - Only Lead Partner+ can resolve conflicts

    **Errors**:
    - 400: Invalid conflict ID format
    - 404: Conflict not found
    - 403: Not authorized (requires lead partner+)
    - 500: Internal server error
    """
    try:
        conflict_uuid = UUID(conflict_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        conflict = await ConflictService.resolve_conflict(
            db,
            conflict_uuid,
            user_id,
            user_role,
            resolution_notes=request.resolution_notes,
        )

        return ConflictResponse(
            id=str(conflict.id),
            case_id=str(conflict.case_id),
            observation_id_1=str(conflict.observation_id_1),
            observation_id_2=str(conflict.observation_id_2),
            conflict_type=conflict.conflict_type,
            severity=conflict.severity,
            description=conflict.description,
            detected_at=conflict.detected_at,
            is_resolved=conflict.is_resolved,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid conflict ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.get(
    "/{case_id}/high-severity",
    response_model=PaginatedResponse,
    summary="Get high-severity conflicts",
)
async def get_high_severity_conflicts(
    case_id: str,
    severity_threshold: float = Query(0.7, ge=0, le=1),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get high-severity conflicts for a case.

    **Query Parameters**:
    - **case_id**: Case ID (UUID)
    - **severity_threshold**: Severity threshold (0-1, default: 0.7)

    **Returns**:
    - List of high-severity unresolved conflicts

    **Access Control**:
    - Analyst: Can see conflicts in own cases only
    - Lead Partner+: Can see all conflicts

    **Errors**:
    - 400: Invalid case ID format
    - 404: Case not found
    - 403: Not authorized
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        conflicts = await ConflictService.get_high_severity_conflicts(
            db,
            case_uuid,
            user_id,
            user_role,
            severity_threshold=severity_threshold,
        )

        conflict_responses = [
            ConflictResponse(
                id=str(conflict.id),
                case_id=str(conflict.case_id),
                observation_id_1=str(conflict.observation_id_1),
                observation_id_2=str(conflict.observation_id_2),
                conflict_type=conflict.conflict_type,
                severity=conflict.severity,
                description=conflict.description,
                detected_at=conflict.detected_at,
                is_resolved=conflict.is_resolved,
            )
            for conflict in conflicts
        ]

        return PaginatedResponse(
            data=conflict_responses,
            total=len(conflict_responses),
            skip=0,
            limit=len(conflict_responses),
            has_more=False,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid case ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
