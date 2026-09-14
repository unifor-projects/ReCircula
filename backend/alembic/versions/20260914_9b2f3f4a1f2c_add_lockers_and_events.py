"""add lockers and events

Revision ID: 9b2f3f4a1f2c
Revises: d0d64199b086
Create Date: 2026-09-14 01:20:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = "9b2f3f4a1f2c"
down_revision: Union[str, Sequence[str], None] = "d0d64199b086"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.create_table(
        "lockers",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("unidade", sa.String(length=120), nullable=False),
        sa.Column("codigo_unidade", sa.String(length=20), nullable=False),
        sa.Column("numero", sa.String(length=20), nullable=False),
        sa.Column("logradouro", sa.String(length=255), nullable=False),
        sa.Column("complemento", sa.String(length=120), nullable=True),
        sa.Column("bairro", sa.String(length=120), nullable=True),
        sa.Column("cidade", sa.String(length=120), nullable=False),
        sa.Column("estado", sa.String(length=120), nullable=True),
        sa.Column("pais", sa.String(length=120), nullable=False),
        sa.Column("cep", sa.String(length=9), nullable=False),
        sa.Column("ativo", sa.Boolean(), nullable=False),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.Column("atualizado_em", sa.DateTime(timezone=True), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_lockers_id"), "lockers", ["id"], unique=False)
    op.create_index(op.f("ix_lockers_codigo_unidade"), "lockers", ["codigo_unidade"], unique=True)
    op.create_index(op.f("ix_lockers_cep"), "lockers", ["cep"], unique=False)

    op.add_column("anuncios", sa.Column("locker_id", sa.Integer(), nullable=True))
    op.create_index(op.f("ix_anuncios_locker_id"), "anuncios", ["locker_id"], unique=False)
    op.create_foreign_key(
        "anuncios_locker_id_fkey",
        "anuncios",
        "lockers",
        ["locker_id"],
        ["id"],
        ondelete="SET NULL",
    )

    op.create_table(
        "locker_eventos",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anuncio_id", sa.Integer(), nullable=False),
        sa.Column("locker_id", sa.Integer(), nullable=False),
        sa.Column(
            "acao",
            sa.Enum("abrir", "fechar", "concluir_doacao", name="locker_evento_acao"),
            nullable=False,
        ),
        sa.Column("sucesso", sa.Boolean(), nullable=False),
        sa.Column("detalhe", sa.Text(), nullable=True),
        sa.Column("criado_em", sa.DateTime(timezone=True), nullable=False),
        sa.ForeignKeyConstraint(["anuncio_id"], ["anuncios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["locker_id"], ["lockers.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index(op.f("ix_locker_eventos_id"), "locker_eventos", ["id"], unique=False)
    op.create_index(op.f("ix_locker_eventos_anuncio_id"), "locker_eventos", ["anuncio_id"], unique=False)
    op.create_index(op.f("ix_locker_eventos_locker_id"), "locker_eventos", ["locker_id"], unique=False)
    op.create_index(op.f("ix_locker_eventos_acao"), "locker_eventos", ["acao"], unique=False)
    op.create_index(op.f("ix_locker_eventos_criado_em"), "locker_eventos", ["criado_em"], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index(op.f("ix_locker_eventos_criado_em"), table_name="locker_eventos")
    op.drop_index(op.f("ix_locker_eventos_acao"), table_name="locker_eventos")
    op.drop_index(op.f("ix_locker_eventos_locker_id"), table_name="locker_eventos")
    op.drop_index(op.f("ix_locker_eventos_anuncio_id"), table_name="locker_eventos")
    op.drop_index(op.f("ix_locker_eventos_id"), table_name="locker_eventos")
    op.drop_table("locker_eventos")

    op.drop_constraint("anuncios_locker_id_fkey", "anuncios", type_="foreignkey")
    op.drop_index(op.f("ix_anuncios_locker_id"), table_name="anuncios")
    op.drop_column("anuncios", "locker_id")

    op.drop_index(op.f("ix_lockers_cep"), table_name="lockers")
    op.drop_index(op.f("ix_lockers_codigo_unidade"), table_name="lockers")
    op.drop_index(op.f("ix_lockers_id"), table_name="lockers")
    op.drop_table("lockers")

    op.execute("DROP TYPE IF EXISTS locker_evento_acao")
