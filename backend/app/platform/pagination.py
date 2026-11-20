"""
Shared pagination helper for list endpoints.

Teammates can import this for their list endpoints:
    from backend.app.platform.pagination import paginate, pagination_params
"""
import math
from fastapi import Query
from sqlalchemy.orm import Query as OrmQuery


def pagination_params(
    page: int = Query(1, ge=1, description="Page number, starting from 1"),
    size: int = Query(20, ge=1, le=100, description="Items per page, maximum 100"),
):
    """
    FastAPI dependency that extracts and validates pagination query parameters.
    Use as: Depends(pagination_params)
    """
    # Return page and size as a simple dict for the route handler to pass to paginate()
    return {"page": page, "size": size}


def paginate(items_query: OrmQuery, page: int, size: int) -> dict:
    """
    Apply page/size slicing to a SQLAlchemy query and return a paginated result dict.

    Returns a dict with keys: items, total, page, size, pages.
    The pages count is ceil(total / size) so the last page number is always known.
    """
    # Count all matching rows before slicing
    total = items_query.count()

    # Calculate how many pages there are in total
    pages = math.ceil(total / size) if total > 0 else 1

    # Slice the query to return only the current page of results
    offset = (page - 1) * size
    items = items_query.offset(offset).limit(size).all()

    # Return the standard paginated response shape
    return {
        "items": items,
        "total": total,
        "page": page,
        "size": size,
        "pages": pages,
    }
