from typing import Any

from sqlalchemy import and_, func, select
from sqlalchemy.dialects.postgresql import aggregate_order_by, insert
from sqlalchemy.sql.functions import coalesce

from src.bot.config import moon_config
from src.database import execute, fetch_all, fetch_one, task, task_buttons, task_completion, tg_invite, tg_invite_code


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


async def get_task_by_slug(slug: str) -> dict[str, Any] | None:
    select_query = task.select().where(task.c.slug == slug)
    return await fetch_one(select_query)


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
            func.json_agg(
                aggregate_order_by(
                    func.json_strip_nulls(
                        func.json_build_object(
                            "button_text",
                            task_buttons.c.button_text,
                            "button_callback_data",
                            task_buttons.c.button_callback_data,
                        )
                    ),
                    task_buttons.c.position_order,
                ),
            ).label("buttons"),
            coalesce(task_completion.c.points, task.c.points).label("points"),
            task_completion.c.created_at.label("completed_at"),
        )
        .select_from(
            task.outerjoin(
                task_completion,
                and_(task_completion.c.task_id == task.c.id, task_completion.c.user_tg_id == user_id),
            ).outerjoin(task_buttons)
        )
        .where(task.c.id == task_id)
        .group_by(task, task_completion)
    )

    return await fetch_one(select_query)


async def count_user_points(
    user_id: str, points_per_invite: int = moon_config.POINTS_PER_INVITE
) -> dict[str, int] | None:
    tasks_points = (
        select(func.sum(task_completion.c.points).label("points"))
        .where(task_completion.c.user_tg_id == user_id)
        .alias("tasks_points")
    )

    invites_count = (
        select(func.count(tg_invite.c.id).label("invites"))
        .select_from(tg_invite_code.outerjoin(tg_invite))
        .where(tg_invite_code.c.referrer_telegram_id == user_id)
        .alias("invites_count")
    )

    invites_points = select((invites_count.c.invites * points_per_invite).label("points"))

    total_points = select((coalesce(tasks_points.c.points, 0) + coalesce(invites_points.c.points, 0)).label("points"))

    return await fetch_one(total_points)
