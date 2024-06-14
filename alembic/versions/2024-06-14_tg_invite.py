"""tg_invite

Revision ID: 2b777c614532
Revises:
Create Date: 2024-06-14 21:00:29.125272

"""

import sqlalchemy as sa

from alembic import op

revision = "2b777c614532"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tg_invite_code",
        sa.Column("id", sa.Integer(), sa.Identity(always=True, start=1, increment=1), nullable=False),
        sa.Column("referrer_telegram_id", sa.String(), nullable=False),
        sa.Column("code", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("tg_invite_code_pkey")),
        sa.UniqueConstraint("code", name=op.f("tg_invite_code_code_key")),
        sa.UniqueConstraint("referrer_telegram_id", name=op.f("tg_invite_code_referrer_telegram_id_key")),
    )
    op.create_table(
        "tg_invite",
        sa.Column("id", sa.Integer(), sa.Identity(always=True, start=1, increment=1), nullable=False),
        sa.Column("invite_id", sa.Integer(), nullable=False),
        sa.Column("referee_telegram_id", sa.String(), nullable=False),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.ForeignKeyConstraint(["invite_id"], ["tg_invite_code.id"], name=op.f("tg_invite_invite_id_fkey")),
        sa.PrimaryKeyConstraint("id", name=op.f("tg_invite_pkey")),
        sa.UniqueConstraint("referee_telegram_id", name=op.f("tg_invite_referee_telegram_id_key")),
    )


def downgrade() -> None:
    op.drop_table("tg_invite")
    op.drop_table("tg_invite_code")
