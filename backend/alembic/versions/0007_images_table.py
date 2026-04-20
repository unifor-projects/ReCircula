"""substitui anuncio_imagens por images com suporte a upload de arquivos

Revision ID: 0007
Revises: 0006
Create Date: 2026-04-20 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0007"
down_revision: Union[str, Sequence[str], None] = "0006"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.drop_table("anuncio_imagens")
    op.create_table(
        "images",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anuncio_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("content_type", sa.String(length=50), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["anuncio_id"], ["anuncios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_images_id", "images", ["id"], unique=False)
    op.create_index("ix_images_anuncio_id", "images", ["anuncio_id"], unique=False)


def downgrade() -> None:
    op.drop_table("images")
    op.create_table(
        "anuncio_imagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anuncio_id", sa.Integer(), nullable=False),
        sa.Column("url", sa.String(length=500), nullable=False),
        sa.Column("ordem", sa.Integer(), nullable=False, server_default="0"),
        sa.ForeignKeyConstraint(["anuncio_id"], ["anuncios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_anuncio_imagens_id", "anuncio_imagens", ["id"], unique=False)
    op.create_index(
        "ix_anuncio_imagens_anuncio_id", "anuncio_imagens", ["anuncio_id"], unique=False
    )
