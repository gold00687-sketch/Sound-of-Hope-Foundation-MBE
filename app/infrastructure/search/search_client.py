"""Full-text search integration boundary.

Currently implemented as PostgreSQL full-text search via tsvector columns.
If a dedicated search service (e.g. Meilisearch, OpenSearch) is introduced
later, only this module needs updating.
"""

from sqlalchemy import func, text
from sqlalchemy.ext.asyncio import AsyncSession


async def pg_search(
    session: AsyncSession,
    table: str,
    columns: list[str],
    query: str,
    limit: int = 20,
    offset: int = 0,
) -> list[dict]:
    """Execute a simple PostgreSQL websearch_to_tsquery full-text search."""
    col_expression = " || ' ' || ".join(f"coalesce({c}::text, '')" for c in columns)
    sql = text(f"""
        SELECT *
        FROM {table}
        WHERE to_tsvector('english', {col_expression})
              @@ websearch_to_tsquery('english', :query)
        ORDER BY ts_rank(
            to_tsvector('english', {col_expression}),
            websearch_to_tsquery('english', :query)
        ) DESC
        LIMIT :limit OFFSET :offset
    """)
    result = await session.execute(sql, {"query": query, "limit": limit, "offset": offset})
    return [dict(row._mapping) for row in result]
