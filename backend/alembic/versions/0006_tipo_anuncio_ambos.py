"""adiciona valor ambos ao enum tipo_anuncio

Revision ID: 0006
Revises: 0005
Create Date: 2026-04-19 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0006"
down_revision: Union[str, Sequence[str], None] = "0005"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute("ALTER TYPE tipo_anuncio ADD VALUE IF NOT EXISTS 'ambos'")


def downgrade() -> None:
    op.execute("UPDATE anuncios SET tipo = 'doacao' WHERE tipo = 'ambos'")
    op.execute("ALTER TABLE anuncios ALTER COLUMN tipo TYPE varchar(20)")
    op.execute("DROP TYPE tipo_anuncio")
    op.execute("CREATE TYPE tipo_anuncio AS ENUM ('doacao', 'troca')")
    op.execute(
        "ALTER TABLE anuncios ALTER COLUMN tipo TYPE tipo_anuncio USING tipo::tipo_anuncio"
    )
