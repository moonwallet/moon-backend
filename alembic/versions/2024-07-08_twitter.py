"""twitter

Revision ID: 7590f99aa731
Revises: f77a28ed03b1
Create Date: 2024-07-08 00:28:58.691454

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "7590f99aa731"
down_revision = "f77a28ed03b1"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_unique_constraint(op.f("tg_user_telegram_id_key"), "tg_user", ["telegram_id"])
    op.create_table(
        "oauth_twitter",
        sa.Column("id", sa.Integer(), sa.Identity(always=True, start=1, increment=1), nullable=False),
        sa.Column("user_tg_id", sa.String(), nullable=True),
        sa.Column("oauth_token", sa.String(), nullable=False),
        sa.Column("oauth_token_secret", sa.String(), nullable=False),
        sa.Column("access_token", sa.String(), nullable=True),
        sa.Column("access_token_secret", sa.String(), nullable=True),
        sa.Column("twitter_id", sa.String(), nullable=True),
        sa.Column("screen_name", sa.String(), nullable=True),
        sa.Column("name", sa.String(), nullable=True),
        sa.Column("description", sa.String(), nullable=True),
        sa.Column("image_url", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["user_tg_id"], ["tg_user.telegram_id"], name=op.f("oauth_twitter_user_tg_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("oauth_twitter_pkey")),
        sa.UniqueConstraint("user_tg_id", name=op.f("oauth_twitter_user_tg_id_key")),
    )


def downgrade() -> None:
    op.drop_constraint(op.f("tg_user_telegram_id_key"), "tg_user", type_="unique")
    op.drop_table("oauth_twitter")
