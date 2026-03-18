"""initial schema

Revision ID: 0001
Revises:
Create Date: 2026-03-14 00:00:00.000000

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

revision: str = "0001"
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ── Enums ────────────────────────────────────────────────────────────────
    op.execute("CREATE TYPE tipo_anuncio AS ENUM ('doacao', 'troca')")
    op.execute("CREATE TYPE condicao_item AS ENUM ('novo', 'seminovo', 'usado', 'para_reparo')")
    op.execute(
        "CREATE TYPE status_anuncio AS ENUM ('disponivel', 'reservado', 'doado_trocado')"
    )
    op.execute(
        "CREATE TYPE status_denuncia AS ENUM ('pendente', 'analisada', 'resolvida')"
    )

    # ── usuarios ─────────────────────────────────────────────────────────────
    op.create_table(
        "usuarios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=150), nullable=False),
        sa.Column("email", sa.String(length=255), nullable=False),
        sa.Column("senha_hash", sa.String(length=255), nullable=False),
        sa.Column("foto_url", sa.String(length=500), nullable=True),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column("localizacao", sa.String(length=255), nullable=True),
        sa.Column("cep", sa.String(length=9), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default="true"),
        sa.Column("is_admin", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column("email_verificado", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_usuarios_email", "usuarios", ["email"], unique=True)
    op.create_index("ix_usuarios_id", "usuarios", ["id"], unique=False)

    # ── categorias ───────────────────────────────────────────────────────────
    op.create_table(
        "categorias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("nome", sa.String(length=100), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.PrimaryKeyConstraint("id"),
        sa.UniqueConstraint("nome"),
    )
    op.create_index("ix_categorias_id", "categorias", ["id"], unique=False)

    # ── anuncios ─────────────────────────────────────────────────────────────
    op.create_table(
        "anuncios",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("titulo", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=False),
        sa.Column("tipo", sa.Enum("doacao", "troca", name="tipo_anuncio"), nullable=False),
        sa.Column(
            "condicao",
            sa.Enum("novo", "seminovo", "usado", "para_reparo", name="condicao_item"),
            nullable=False,
        ),
        sa.Column(
            "status",
            sa.Enum("disponivel", "reservado", "doado_trocado", name="status_anuncio"),
            nullable=False,
            server_default="disponivel",
        ),
        sa.Column("localizacao", sa.String(length=255), nullable=True),
        sa.Column("cep", sa.String(length=9), nullable=True),
        sa.Column("usuario_id", sa.Integer(), nullable=False),
        sa.Column("categoria_id", sa.Integer(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column(
            "atualizado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["categoria_id"], ["categorias.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["usuario_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_anuncios_id", "anuncios", ["id"], unique=False)
    op.create_index("ix_anuncios_titulo", "anuncios", ["titulo"], unique=False)
    op.create_index("ix_anuncios_status", "anuncios", ["status"], unique=False)
    op.create_index("ix_anuncios_cep", "anuncios", ["cep"], unique=False)
    op.create_index("ix_anuncios_usuario_id", "anuncios", ["usuario_id"], unique=False)
    op.create_index("ix_anuncios_categoria_id", "anuncios", ["categoria_id"], unique=False)
    op.create_index("ix_anuncios_criado_em", "anuncios", ["criado_em"], unique=False)

    # ── anuncio_imagens ───────────────────────────────────────────────────────
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

    # ── status_historico ──────────────────────────────────────────────────────
    op.create_table(
        "status_historico",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anuncio_id", sa.Integer(), nullable=False),
        sa.Column(
            "status_anterior",
            sa.Enum("disponivel", "reservado", "doado_trocado", name="status_anuncio"),
            nullable=True,
        ),
        sa.Column(
            "status_novo",
            sa.Enum("disponivel", "reservado", "doado_trocado", name="status_anuncio"),
            nullable=False,
        ),
        sa.Column(
            "alterado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["anuncio_id"], ["anuncios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_status_historico_id", "status_historico", ["id"], unique=False)
    op.create_index(
        "ix_status_historico_anuncio_id", "status_historico", ["anuncio_id"], unique=False
    )

    # ── conversas ─────────────────────────────────────────────────────────────
    op.create_table(
        "conversas",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("anuncio_id", sa.Integer(), nullable=False),
        sa.Column("iniciador_id", sa.Integer(), nullable=False),
        sa.Column("anunciante_id", sa.Integer(), nullable=False),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["anuncio_id"], ["anuncios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["anunciante_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["iniciador_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_conversas_id", "conversas", ["id"], unique=False)
    op.create_index("ix_conversas_anuncio_id", "conversas", ["anuncio_id"], unique=False)
    op.create_index("ix_conversas_iniciador_id", "conversas", ["iniciador_id"], unique=False)
    op.create_index(
        "ix_conversas_anunciante_id", "conversas", ["anunciante_id"], unique=False
    )

    # ── mensagens ─────────────────────────────────────────────────────────────
    op.create_table(
        "mensagens",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("conversa_id", sa.Integer(), nullable=False),
        sa.Column("autor_id", sa.Integer(), nullable=False),
        sa.Column("conteudo", sa.Text(), nullable=False),
        sa.Column("lida", sa.Boolean(), nullable=False, server_default="false"),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.ForeignKeyConstraint(["autor_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(["conversa_id"], ["conversas.id"], ondelete="CASCADE"),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_mensagens_id", "mensagens", ["id"], unique=False)
    op.create_index("ix_mensagens_conversa_id", "mensagens", ["conversa_id"], unique=False)
    op.create_index("ix_mensagens_autor_id", "mensagens", ["autor_id"], unique=False)

    # ── denuncias ─────────────────────────────────────────────────────────────
    op.create_table(
        "denuncias",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("denunciante_id", sa.Integer(), nullable=False),
        sa.Column("anuncio_id", sa.Integer(), nullable=True),
        sa.Column("usuario_denunciado_id", sa.Integer(), nullable=True),
        sa.Column("motivo", sa.String(length=200), nullable=False),
        sa.Column("descricao", sa.Text(), nullable=True),
        sa.Column(
            "status",
            sa.Enum("pendente", "analisada", "resolvida", name="status_denuncia"),
            nullable=False,
            server_default="pendente",
        ),
        sa.Column("admin_id", sa.Integer(), nullable=True),
        sa.Column(
            "criado_em",
            sa.DateTime(timezone=True),
            nullable=False,
            server_default=sa.text("now()"),
        ),
        sa.Column("resolvido_em", sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(["admin_id"], ["usuarios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["anuncio_id"], ["anuncios.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["denunciante_id"], ["usuarios.id"], ondelete="CASCADE"),
        sa.ForeignKeyConstraint(
            ["usuario_denunciado_id"], ["usuarios.id"], ondelete="SET NULL"
        ),
        sa.PrimaryKeyConstraint("id"),
    )
    op.create_index("ix_denuncias_id", "denuncias", ["id"], unique=False)
    op.create_index(
        "ix_denuncias_denunciante_id", "denuncias", ["denunciante_id"], unique=False
    )
    op.create_index("ix_denuncias_anuncio_id", "denuncias", ["anuncio_id"], unique=False)
    op.create_index("ix_denuncias_status", "denuncias", ["status"], unique=False)
    op.create_index(
        "ix_denuncias_usuario_denunciado_id",
        "denuncias",
        ["usuario_denunciado_id"],
        unique=False,
    )


def downgrade() -> None:
    op.drop_table("denuncias")
    op.drop_table("mensagens")
    op.drop_table("conversas")
    op.drop_table("status_historico")
    op.drop_table("anuncio_imagens")
    op.drop_table("anuncios")
    op.drop_table("categorias")
    op.drop_table("usuarios")

    op.execute("DROP TYPE IF EXISTS status_denuncia")
    op.execute("DROP TYPE IF EXISTS status_anuncio")
    op.execute("DROP TYPE IF EXISTS condicao_item")
    op.execute("DROP TYPE IF EXISTS tipo_anuncio")
