"""tg_user

Revision ID: f77a28ed03b1
Revises: 2b777c614532
Create Date: 2024-06-20 01:09:23.497707

"""

import sqlalchemy as sa

from alembic import op

# revision identifiers, used by Alembic.
revision = "f77a28ed03b1"
down_revision = "2b777c614532"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "tg_user",
        sa.Column("id", sa.Integer(), sa.Identity(always=True, start=1, increment=1), nullable=False),
        sa.Column("telegram_id", sa.String(), nullable=False),
        sa.Column("chat_id", sa.String(), nullable=False),
        sa.Column("username", sa.String(), nullable=True),
        sa.Column("first_name", sa.String(), nullable=True),
        sa.Column("last_name", sa.String(), nullable=True),
        sa.Column("created_at", sa.DateTime(), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(), nullable=True),
        sa.PrimaryKeyConstraint("id", name=op.f("tg_user_pkey")),
        sa.UniqueConstraint("chat_id", "telegram_id", name="tg_user_telegram_id_chat_id_key"),
    )

    op.execute(
        """
        INSERT INTO tg_user (telegram_id, chat_id)
        SELECT tg_invite_code.referrer_telegram_id, tg_invite_code.referrer_telegram_id
        FROM tg_invite_code
        """
    )


def downgrade() -> None:
    op.drop_table("tg_user")
