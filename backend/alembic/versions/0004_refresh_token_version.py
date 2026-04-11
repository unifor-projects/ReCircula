"""adiciona versionamento para refresh token

Revision ID: 0004
Revises: 0003
Create Date: 2026-04-11 21:30:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0004"
down_revision: Union[str, Sequence[str], None] = "0003"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("refresh_token_version", sa.Integer(), nullable=False, server_default="0"),
    )
    op.alter_column("usuarios", "refresh_token_version", server_default=None)


def downgrade() -> None:
    op.drop_column("usuarios", "refresh_token_version")
