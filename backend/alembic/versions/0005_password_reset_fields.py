"""adiciona campos de recuperação de senha

Revision ID: 0005
Revises: 0004
Create Date: 2026-04-11 23:50:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0005"
down_revision: Union[str, Sequence[str], None] = "0004"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "usuarios",
        sa.Column("token_reset_senha", sa.String(length=255), nullable=True),
    )
    op.add_column(
        "usuarios",
        sa.Column("token_reset_expira_em", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index(
        op.f("ix_usuarios_token_reset_expira_em"),
        "usuarios",
        ["token_reset_expira_em"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_index(op.f("ix_usuarios_token_reset_expira_em"), table_name="usuarios")
    op.drop_column("usuarios", "token_reset_expira_em")
    op.drop_column("usuarios", "token_reset_senha")
