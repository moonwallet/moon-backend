"""points

Revision ID: a0ab0aec5813
Revises: 7590f99aa731
Create Date: 2024-07-09 22:51:04.943511

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "a0ab0aec5813"
down_revision = "7590f99aa731"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "task",
        sa.Column("id", sa.Integer(), sa.Identity(always=True, start=1, increment=1), nullable=False),
        sa.Column("name", sa.String(), nullable=False),
        sa.Column("slug", sa.String(), nullable=False),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("callback_data", sa.String(), nullable=True),
        sa.Column("position_order", sa.Integer(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("task_pkey")),
        sa.UniqueConstraint("name", name=op.f("task_name_key")),
        sa.UniqueConstraint("slug", name=op.f("task_slug_key")),
    )
    op.create_table(
        "task_completion",
        sa.Column("id", sa.Integer(), sa.Identity(always=True, start=1, increment=1), nullable=False),
        sa.Column("user_tg_id", sa.String(), nullable=False),
        sa.Column("points", sa.Integer(), nullable=False),
        sa.Column("task_id", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["task_id"], ["task.id"], name=op.f("task_completion_task_id_fkey")),
        sa.ForeignKeyConstraint(["user_tg_id"], ["tg_user.telegram_id"], name=op.f("task_completion_user_tg_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("task_completion_pkey")),
        sa.UniqueConstraint("user_tg_id", "task_id", name="points_user_tg_id_task_id_key"),
        sa.UniqueConstraint("user_tg_id", name=op.f("task_completion_user_tg_id_key")),
    )

    op.execute(
        """
        INSERT INTO task(name, slug, position_order, points, description, callback_data)
        VALUES 
            ('Claim OG points', 'claim_og', 0, 250, 'Congratulations! You have claimed your OG points. 🎉\n\nThank you for being with us, we appreciate every OG member that joined our path in trenches.', null),
            ('Connect X', 'x_connect', 1, 100, 'Connect your X account and earn points.', null),
            ('Share referral on X', 'x_tweet_referral', 2, 250, 'Post a tweet with your referral and earn points just for posting!', null), 
            ('Invite friends to Moon', 'moon_invite', 3, 500, null, 'referrals_dashboard');
        """
    )


def downgrade() -> None:
    op.drop_table("task_completion")
    op.drop_table("task")
