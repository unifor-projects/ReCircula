"""adiciona log imutavel de decisoes administrativas

Revision ID: 0010
Revises: 0009
Create Date: 2026-05-12 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0010"
down_revision: Union[str, Sequence[str], None] = "0009"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute(
        "CREATE TYPE acao_administrativa AS ENUM ('ignorar', 'remover_anuncio', 'suspender_usuario')"
    )
    op.create_table(
        "decisoes_administrativas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("admin_id", sa.Integer(), nullable=False),
        sa.Column("denuncia_id", sa.Integer(), nullable=True),
        sa.Column("anuncio_id", sa.Integer(), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=True),
        sa.Column(
            "acao",
            sa.Enum(
                "ignorar",
                "remover_anuncio",
                "suspender_usuario",
                name="acao_administrativa",
                create_type=False,
            ),
            nullable=False,
        ),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["admin_id"], ["usuarios.id"], ondelete="RESTRICT"),
        sa.ForeignKeyConstraint(["anuncio_id"], ["anuncios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["denuncia_id"], ["denuncias.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(
        "ix_decisoes_administrativas_id", "decisoes_administrativas", ["id"], unique=False
    )
    op.create_index(
        "ix_decisoes_administrativas_admin_id",
        "decisoes_administrativas",
        ["admin_id"],
        unique=False,
    )
    op.create_index(
        "ix_decisoes_administrativas_denuncia_id",
        "decisoes_administrativas",
        ["denuncia_id"],
        unique=False,
    )
    op.create_index(
        "ix_decisoes_administrativas_anuncio_id",
        "decisoes_administrativas",
        ["anuncio_id"],
        unique=False,
    )
    op.create_index(
        "ix_decisoes_administrativas_usuario_id",
        "decisoes_administrativas",
        ["usuario_id"],
        unique=False,
    )
    op.create_index(
        "ix_decisoes_administrativas_acao", "decisoes_administrativas", ["acao"], unique=False
    )


def downgrade() -> None:
    op.drop_index("ix_decisoes_administrativas_acao", table_name="decisoes_administrativas")
    op.drop_index("ix_decisoes_administrativas_usuario_id", table_name="decisoes_administrativas")
    op.drop_index("ix_decisoes_administrativas_anuncio_id", table_name="decisoes_administrativas")
    op.drop_index("ix_decisoes_administrativas_denuncia_id", table_name="decisoes_administrativas")
    op.drop_index("ix_decisoes_administrativas_admin_id", table_name="decisoes_administrativas")
    op.drop_index("ix_decisoes_administrativas_id", table_name="decisoes_administrativas")
    op.drop_table("decisoes_administrativas")
    op.execute("DROP TYPE IF EXISTS acao_administrativa")
