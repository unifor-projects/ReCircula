"""índices GIN trigram em titulo e descricao de anuncios (RNF06)

Revision ID: 0008
Revises: 0007
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union

from alembic import op

revision: str = "0008"
down_revision: Union[str, Sequence[str], None] = "0007"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # Habilita a extensão pg_trgm (necessária para GIN com gin_trgm_ops)
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    # GIN trigram em titulo acelera buscas ILIKE '%palavra%'
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_anuncios_titulo_trgm "
        "ON anuncios USING GIN (titulo gin_trgm_ops)"
    )

    # GIN trigram em descricao (campo Text) para busca full-text ILIKE
    op.execute(
        "CREATE INDEX IF NOT EXISTS ix_anuncios_descricao_trgm "
        "ON anuncios USING GIN (descricao gin_trgm_ops)"
    )
    # ix_anuncios_categoria_id já existe (criado em 0001)


def downgrade() -> None:
    op.execute("DROP INDEX IF EXISTS ix_anuncios_titulo_trgm")
    op.execute("DROP INDEX IF EXISTS ix_anuncios_descricao_trgm")
