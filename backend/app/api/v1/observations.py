"""Observations API endpoints"""

from uuid import UUID
from typing import Optional
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.errors import NotFoundException, ValidationException, AuthorizationException
from app.models.schemas import (
    ObservationResponse,
    ObservationCreate,
    ObservationUpdate,
    PaginatedResponse,
    SourceTag,
    DisclosureLevel,
)
from app.services.observation_service import ObservationService


router = APIRouter()


@router.post(
    "",
    response_model=ObservationResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create observation",
)
async def create_observation(
    case_id: str,
    observation_data: ObservationCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new observation for a case.

    **Query Parameters**:
    - **case_id**: Case ID (UUID)

    **Request Body**:
    - **section**: Report section name
    - **content**: Observation content (10+ characters)
    - **source_tag**: Data source (PUB, EXT, INT, CONF, ANL)
    - **disclosure_level**: Disclosure level (IC, LP, LP_NDA, PRIVATE)
    - **metadata**: Additional metadata (optional)

    **Returns**:
    - Created observation with ID and metadata

    **Access Control**:
    - All authenticated users can create observations

    **Errors**:
    - 400: Validation error
    - 404: Case not found
    - 401: Not authenticated
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))

        observation = await ObservationService.create_observation(
            db,
            case_uuid,
            user_id,
            observation_data,
        )

        return ObservationResponse(
            id=str(observation.id),
            case_id=str(observation.case_id),
            section=observation.section,
            content=observation.content,
            source_tag=observation.source_tag,
            disclosure_level=observation.disclosure_level,
            created_by=str(observation.created_by),
            created_at=observation.created_at,
            updated_at=observation.updated_at,
            is_verified=observation.is_verified,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid case ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List observations",
)
async def list_observations(
    case_id: str,
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    source_tag: Optional[SourceTag] = Query(None),
    disclosure_level: Optional[DisclosureLevel] = Query(None),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List observations for a case with filtering.

    **Query Parameters**:
    - **case_id**: Case ID (UUID)
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Number of items to return (default: 20, max: 100)
    - **source_tag**: Filter by source tag (optional)
    - **disclosure_level**: Filter by disclosure level (optional)

    **Returns**:
    - Paginated list of observations

    **Access Control**:
    - Analyst: Can see observations in own cases only
    - Lead Partner+: Can see all observations

    **Errors**:
    - 400: Invalid case ID format
    - 404: Case not found
    - 403: Not authorized to access case
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        observations, total = await ObservationService.get_observations(
            db,
            case_uuid,
            user_id,
            user_role,
            skip=skip,
            limit=limit,
            source_tag_filter=source_tag,
            disclosure_level_filter=disclosure_level,
        )

        observation_responses = [
            ObservationResponse(
                id=str(obs.id),
                case_id=str(obs.case_id),
                section=obs.section,
                content=obs.content,
                source_tag=obs.source_tag,
                disclosure_level=obs.disclosure_level,
                created_by=str(obs.created_by),
                created_at=obs.created_at,
                updated_at=obs.updated_at,
                is_verified=obs.is_verified,
            )
            for obs in observations
        ]

        has_more = (skip + limit) < total

        return PaginatedResponse(
            data=observation_responses,
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
    "/{observation_id}",
    response_model=ObservationResponse,
    summary="Get observation",
)
async def get_observation(
    observation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get observation details.

    **Path Parameters**:
    - **observation_id**: Observation ID (UUID)

    **Returns**:
    - Observation details

    **Errors**:
    - 400: Invalid observation ID format
    - 404: Observation not found
    - 500: Internal server error
    """
    try:
        observation_uuid = UUID(observation_id)

        observation = await ObservationService.get_observation_by_id(db, observation_uuid)

        if not observation:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Observation not found",
            )

        return ObservationResponse(
            id=str(observation.id),
            case_id=str(observation.case_id),
            section=observation.section,
            content=observation.content,
            source_tag=observation.source_tag,
            disclosure_level=observation.disclosure_level,
            created_by=str(observation.created_by),
            created_at=observation.created_at,
            updated_at=observation.updated_at,
            is_verified=observation.is_verified,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid observation ID format",
        )


@router.put(
    "/{observation_id}",
    response_model=ObservationResponse,
    summary="Update observation",
)
async def update_observation(
    observation_id: str,
    observation_data: ObservationUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update an observation.

    **Path Parameters**:
    - **observation_id**: Observation ID (UUID)

    **Request Body**:
    - **section**: Report section (optional)
    - **content**: Observation content (optional, 10+ chars if provided)
    - **source_tag**: Data source (optional)
    - **disclosure_level**: Disclosure level (optional)
    - **metadata**: Additional metadata (optional)

    **Returns**:
    - Updated observation

    **Access Control**:
    - Creator: Can update own observations
    - Lead Partner+: Can update any observation

    **Errors**:
    - 400: Invalid observation ID or data
    - 404: Observation not found
    - 403: Not authorized
    - 500: Internal server error
    """
    try:
        observation_uuid = UUID(observation_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        observation = await ObservationService.update_observation(
            db,
            observation_uuid,
            user_id,
            user_role,
            observation_data,
        )

        return ObservationResponse(
            id=str(observation.id),
            case_id=str(observation.case_id),
            section=observation.section,
            content=observation.content,
            source_tag=observation.source_tag,
            disclosure_level=observation.disclosure_level,
            created_by=str(observation.created_by),
            created_at=observation.created_at,
            updated_at=observation.updated_at,
            is_verified=observation.is_verified,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid observation ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))


@router.delete(
    "/{observation_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete observation",
)
async def delete_observation(
    observation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete an observation (soft delete).

    **Path Parameters**:
    - **observation_id**: Observation ID (UUID)

    **Access Control**:
    - Creator: Can delete own observations
    - Lead Partner+: Can delete any observation

    **Errors**:
    - 400: Invalid observation ID format
    - 404: Observation not found
    - 403: Not authorized
    - 500: Internal server error
    """
    try:
        observation_uuid = UUID(observation_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        await ObservationService.delete_observation(
            db,
            observation_uuid,
            user_id,
            user_role,
        )

        return None

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid observation ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))


@router.post(
    "/{observation_id}/verify",
    response_model=ObservationResponse,
    summary="Verify observation",
)
async def verify_observation(
    observation_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Verify an observation (lead partner+ only).

    **Path Parameters**:
    - **observation_id**: Observation ID (UUID)

    **Returns**:
    - Verified observation

    **Access Control**:
    - Only Lead Partner+ can verify observations

    **Errors**:
    - 400: Invalid observation ID format
    - 404: Observation not found
    - 403: Not authorized (requires lead partner+)
    - 500: Internal server error
    """
    try:
        observation_uuid = UUID(observation_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        observation = await ObservationService.verify_observation(
            db,
            observation_uuid,
            user_id,
            user_role,
        )

        return ObservationResponse(
            id=str(observation.id),
            case_id=str(observation.case_id),
            section=observation.section,
            content=observation.content,
            source_tag=observation.source_tag,
            disclosure_level=observation.disclosure_level,
            created_by=str(observation.created_by),
            created_at=observation.created_at,
            updated_at=observation.updated_at,
            is_verified=observation.is_verified,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid observation ID format",
        )
    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
