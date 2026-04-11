"""ajusta token_verificacao para armazenar hash BCrypt

Revision ID: 0003
Revises: 0002
Create Date: 2026-04-11 16:45:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0003"
down_revision: Union[str, Sequence[str], None] = "0002"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.alter_column(
        "usuarios",
        "token_verificacao",
        existing_type=sa.String(length=64),
        type_=sa.String(length=255),
        existing_nullable=True,
    )

    # Sem compatibilidade legada: invalida tokens em texto puro já persistidos.
    op.execute(
        """
        UPDATE usuarios
        SET token_verificacao = NULL
        WHERE token_verificacao IS NOT NULL
          AND token_verificacao NOT LIKE '$2%'
        """
    )


def downgrade() -> None:
    op.alter_column(
        "usuarios",
        "token_verificacao",
        existing_type=sa.String(length=255),
        type_=sa.String(length=64),
        existing_nullable=True,
    )
