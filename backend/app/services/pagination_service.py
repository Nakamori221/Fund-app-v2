"""Pagination service - cursor-based pagination for large datasets"""

import base64
import json
from datetime import datetime
from typing import Optional, Tuple, List, Any, TypeVar, Generic
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

T = TypeVar('T')


class CursorPaginationParams:
    """Cursor encoding/decoding for pagination"""

    @staticmethod
    def encode_cursor(created_at: datetime, entity_id: UUID) -> str:
        """
        Encode cursor parameters to base64.

        **Parameters**:
        - created_at: Timestamp for ordering
        - entity_id: Entity ID for pagination

        **Returns**:
        - Base64-encoded cursor string
        """
        data = {
            "created_at": created_at.isoformat(),
            "id": str(entity_id)
        }
        json_str = json.dumps(data)
        return base64.b64encode(json_str.encode()).decode()

    @staticmethod
    def decode_cursor(cursor: str) -> Tuple[datetime, UUID]:
        """
        Decode cursor from base64.

        **Parameters**:
        - cursor: Base64-encoded cursor string

        **Returns**:
        - Tuple of (created_at datetime, entity_id UUID)

        **Errors**:
        - ValueError: Invalid cursor format
        """
        try:
            json_str = base64.b64decode(cursor).decode()
            data = json.loads(json_str)
            return (
                datetime.fromisoformat(data["created_at"]),
                UUID(data["id"])
            )
        except (ValueError, KeyError, json.JSONDecodeError) as e:
            raise ValueError(f"Invalid cursor format: {str(e)}")


class PaginationService:
    """
    Cursor-based pagination service for efficient large dataset handling.

    **Key Features**:
    - O(limit) time complexity regardless of dataset size
    - Consistent ordering even with data modifications
    - No offset-based scanning overhead
    """

    @staticmethod
    async def paginate(
        db: AsyncSession,
        query,
        cursor: Optional[str] = None,
        limit: int = 20,
        order_by_created_at: bool = True,
    ) -> Tuple[List[T], Optional[str], bool]:
        """
        Execute cursor-based pagination.

        **Parameters**:
        - db: Database session
        - query: SQLAlchemy select query (must order by created_at DESC, then id)
        - cursor: Cursor from previous page (None for first page)
        - limit: Number of records to return (1-100)
        - order_by_created_at: Whether query is ordered by created_at DESC, id (default: True)

        **Returns**:
        - Tuple of (results list, next_cursor, has_more)
        - next_cursor: Cursor for next page (None if no more pages)
        - has_more: Boolean indicating whether there are more pages

        **Example**:
        ```python
        query = select(User).where(User.is_active == True).order_by(User.created_at.desc(), User.id)
        users, next_cursor, has_more = await PaginationService.paginate(
            db=db,
            query=query,
            cursor=cursor,
            limit=20
        )
        ```
        """
        # Validate limit
        if limit < 1 or limit > 100:
            limit = 20

        # Apply cursor filter if provided
        if cursor:
            try:
                created_at, user_id = CursorPaginationParams.decode_cursor(cursor)

                # Filter: created_at < previous OR (created_at == previous AND id > previous)
                # This handles the case where multiple records have the same created_at
                from sqlalchemy import or_
                from app.models.database import User

                query = query.where(
                    or_(
                        User.created_at < created_at,
                        (User.created_at == created_at) & (User.id > user_id)
                    )
                )
            except ValueError as e:
                raise ValueError(f"Invalid cursor: {str(e)}")

        # Fetch limit + 1 to determine if there are more pages
        query = query.limit(limit + 1)
        result = await db.execute(query)
        items = result.scalars().all()

        # Determine if there are more pages
        has_more = len(items) > limit
        if has_more:
            items = items[:limit]

        # Calculate next cursor
        next_cursor = None
        if has_more and len(items) > 0:
            last_item = items[-1]
            next_cursor = CursorPaginationParams.encode_cursor(
                created_at=last_item.created_at,
                entity_id=last_item.id
            )

        return items, next_cursor, has_more

    @staticmethod
    async def get_page_info(
        cursor: Optional[str] = None,
        limit: int = 20,
    ) -> dict:
        """
        Get pagination information from cursor.

        **Parameters**:
        - cursor: Cursor string (None for first page)
        - limit: Page size

        **Returns**:
        - Dictionary with pagination info
        """
        pagination_info = {
            "limit": limit,
            "is_first_page": cursor is None,
            "next_cursor": None,
        }

        if cursor:
            try:
                created_at, entity_id = CursorPaginationParams.decode_cursor(cursor)
                pagination_info["current_cursor_timestamp"] = created_at.isoformat()
                pagination_info["current_cursor_id"] = str(entity_id)
            except ValueError:
                pass

        return pagination_info
