"""adiciona latitude e longitude em anuncios (RNF03)

Revision ID: 0009
Revises: 0008
Create Date: 2026-04-28 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0009"
down_revision: Union[str, Sequence[str], None] = "0008"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column("anuncios", sa.Column("latitude", sa.Float(), nullable=True))
    op.add_column("anuncios", sa.Column("longitude", sa.Float(), nullable=True))


def downgrade() -> None:
    op.drop_column("anuncios", "longitude")
    op.drop_column("anuncios", "latitude")
