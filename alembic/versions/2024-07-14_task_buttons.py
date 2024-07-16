"""task_buttons

Revision ID: fe2470cc90d3
Revises: a0ab0aec5813
Create Date: 2024-07-14 17:33:34.769788

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "fe2470cc90d3"
down_revision = "a0ab0aec5813"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task_buttons",
        sa.Column("id", sa.Integer(), sa.Identity(always=True, start=1, increment=1), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("button_text", sa.String(), nullable=False),
        sa.Column("button_callback_data", sa.String(), nullable=False),
        sa.Column("position_order", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], name=op.f("task_buttons_task_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("task_buttons_pkey")),
    )


def downgrade() -> None:
    op.drop_table("task_buttons")
