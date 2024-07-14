from typing import Any

from sqlalchemy import and_, select
from sqlalchemy.dialects.postgresql import insert
from sqlalchemy.sql.functions import coalesce

from src.database import execute, fetch_all, fetch_one, task, task_completion


async def complete_task(user_id: str, task_id: int, points: int) -> None:
    insert_query = (
        insert(task_completion)
        .values(
            user_tg_id=user_id,
            task_id=task_id,
            points=points,
        )
        .on_conflict_do_nothing(index_elements=["user_tg_id", "task_id"])
    )

    await execute(insert_query, commit_after=True)


async def get_user_tasks(user_id: str) -> list[dict[str, Any]]:
    select_query = (
        select(
            task.c.id,
            task.c.name,
            task.c.description,
            task.c.callback_data,
            task.c.slug,
            coalesce(task_completion.c.points, task.c.points).label("points"),
            task_completion.c.created_at.label("completed_at"),
        )
        .select_from(
            task.outerjoin(
                task_completion,
                and_(task_completion.c.task_id == task.c.id, task_completion.c.user_tg_id == user_id),
            )
        )
        .order_by(task.c.position_order)
    )

    return await fetch_all(select_query)


async def get_user_task(user_id: str, task_id: int) -> dict[str, Any] | None:
    select_query = (
        select(
            task.c.id,
            task.c.name,
            task.c.description,
            task.c.callback_data,
            task.c.slug,
            coalesce(task_completion.c.points, task.c.points).label("points"),
            task_completion.c.created_at.label("completed_at"),
        )
        .select_from(
            task.outerjoin(
                task_completion,
                and_(task_completion.c.task_id == task.c.id, task_completion.c.user_tg_id == user_id),
            )
        )
        .where(task.c.id == task_id)
    )

    return await fetch_one(select_query)
