"""Cases API endpoints"""

from uuid import UUID
from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.ext.asyncio import AsyncSession

from app.database import get_db
from app.core.security import get_current_user
from app.core.errors import NotFoundException, ValidationException, AuthorizationException
from app.models.schemas import (
    CaseResponse,
    CaseCreate,
    CaseUpdate,
    PaginatedResponse,
    CaseStatus,
)
from app.services.case_service import CaseService


router = APIRouter()


@router.get(
    "",
    response_model=PaginatedResponse,
    summary="List all cases",
)
async def list_cases(
    skip: int = Query(0, ge=0, description="Number of items to skip"),
    limit: int = Query(20, ge=1, le=100, description="Number of items to return"),
    status_filter: CaseStatus = Query(None, description="Filter by case status"),
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    List all cases with pagination and filtering.

    **Query Parameters:**
    - **skip**: Number of items to skip (default: 0)
    - **limit**: Number of items to return (default: 20, max: 100)
    - **status_filter**: Filter by case status (optional)

    **Returns:**
    - Paginated list of cases

    **Access Control:**
    - Analyst: Can see only their own cases
    - Lead Partner+: Can see all cases

    **Errors:**
    - 401: Not authenticated
    - 500: Internal server error
    """
    try:
        # Get cases from service with RBAC filtering
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        cases, total = await CaseService.get_cases(
            db,
            user_id,
            user_role,
            skip=skip,
            limit=limit,
            status_filter=status_filter,
        )

        # Convert to response models
        case_responses = [
            CaseResponse(
                id=str(case.id),
                title=case.title,
                description=case.description,
                company_name=case.company_name,
                sector=case.sector,
                status=case.status,
                created_by=str(case.created_by),
                created_at=case.created_at,
                updated_at=case.updated_at,
                observation_count=len(case.observations),
                metadata=case.metadata,
            )
            for case in cases
        ]

        has_more = (skip + limit) < total

        return PaginatedResponse(
            data=case_responses,
            total=total,
            skip=skip,
            limit=limit,
            has_more=has_more,
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.post(
    "",
    response_model=CaseResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Create new case",
)
async def create_case(
    case_data: CaseCreate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Create a new case.

    **Request Body:**
    - **title**: Case title (5-255 characters)
    - **description**: Case description (optional, max 2000 chars)
    - **company_name**: Target company name
    - **sector**: Industry sector (optional)
    - **status**: Initial case status (default: draft)
    - **metadata**: Additional metadata (optional)

    **Returns:**
    - Created case with ID and metadata

    **Access Control:**
    - All authenticated users can create cases

    **Errors:**
    - 400: Validation error
    - 401: Not authenticated
    - 500: Internal server error
    """
    try:
        user_id = UUID(current_user.get("user_id"))

        case = await CaseService.create_case(db, user_id, case_data)

        return CaseResponse(
            id=str(case.id),
            title=case.title,
            description=case.description,
            company_name=case.company_name,
            sector=case.sector,
            status=case.status,
            created_by=str(case.created_by),
            created_at=case.created_at,
            updated_at=case.updated_at,
            observation_count=0,
            metadata=case.metadata,
        )

    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.get(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Get case details",
)
async def get_case(
    case_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Get detailed information about a specific case.

    **Path Parameters:**
    - **case_id**: The case ID

    **Returns:**
    - Case details with all metadata

    **Access Control:**
    - Analyst: Can view only their own cases
    - Lead Partner+: Can view all cases

    **Errors:**
    - 401: Not authenticated
    - 404: Case not found
    - 403: Not authorized to view this case
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        case = await CaseService.get_case_by_id(db, case_uuid)

        if not case:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Case not found",
            )

        # Check RBAC
        from app.models.schemas import UserRole
        if user_role == UserRole.ANALYST and case.created_by != user_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Not authorized to view this case",
            )

        return CaseResponse(
            id=str(case.id),
            title=case.title,
            description=case.description,
            company_name=case.company_name,
            sector=case.sector,
            status=case.status,
            created_by=str(case.created_by),
            created_at=case.created_at,
            updated_at=case.updated_at,
            observation_count=len(case.observations),
            metadata=case.metadata,
        )

    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid case ID format",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.put(
    "/{case_id}",
    response_model=CaseResponse,
    summary="Update case",
)
async def update_case(
    case_id: str,
    case_data: CaseUpdate,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Update a case.

    **Path Parameters:**
    - **case_id**: The case ID

    **Request Body:**
    - **title**: New case title (optional)
    - **description**: New case description (optional)
    - **status**: New case status (optional)
    - **metadata**: Updated metadata (optional)

    **Returns:**
    - Updated case details

    **Access Control:**
    - Creator (analyst): Can update their own cases in DRAFT status
    - Lead Partner+: Can update case status
    - Admin: Can update any case

    **Errors:**
    - 400: Validation error
    - 401: Not authenticated
    - 403: Not authorized to update this case
    - 404: Case not found
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        case = await CaseService.update_case(db, case_uuid, user_id, user_role, case_data)

        return CaseResponse(
            id=str(case.id),
            title=case.title,
            description=case.description,
            company_name=case.company_name,
            sector=case.sector,
            status=case.status,
            created_by=str(case.created_by),
            created_at=case.created_at,
            updated_at=case.updated_at,
            observation_count=len(case.observations),
            metadata=case.metadata,
        )

    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValidationException as e:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=str(e))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid case ID format",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )


@router.delete(
    "/{case_id}",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="Delete case",
)
async def delete_case(
    case_id: str,
    current_user: dict = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    """
    Delete a case (soft delete).

    **Path Parameters:**
    - **case_id**: The case ID

    **Access Control:**
    - Creator (analyst): Can delete only their own draft cases
    - Admin: Can delete any case

    **Errors:**
    - 401: Not authenticated
    - 403: Not authorized to delete this case
    - 404: Case not found
    - 500: Internal server error
    """
    try:
        case_uuid = UUID(case_id)
        user_id = UUID(current_user.get("user_id"))
        user_role = current_user.get("role")

        await CaseService.delete_case(db, case_uuid, user_id, user_role)

        return None

    except NotFoundException as e:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail=str(e))
    except AuthorizationException as e:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail=str(e))
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid case ID format",
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e),
        )
