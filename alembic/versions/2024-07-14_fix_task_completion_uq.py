"""fix_task_completion_uq

Revision ID: 5a6b6db4dc8c
Revises: fe2470cc90d3
Create Date: 2024-07-14 18:59:39.958637

"""


from alembic import op

# revision identifiers, used by Alembic.
revision = "5a6b6db4dc8c"
down_revision = "fe2470cc90d3"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.drop_constraint("task_completion_user_tg_id_key", "task_completion", type_="unique")


def downgrade() -> None:
    op.create_unique_constraint("task_completion_user_tg_id_key", "task_completion", ["user_tg_id"])
