from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class TipoAnuncio(str, PyEnum):
    doacao = "doacao"
    troca = "troca"
    ambos = "ambos"


class CondicaoItem(str, PyEnum):
    novo = "novo"
    seminovo = "seminovo"
    usado = "usado"
    para_reparo = "para_reparo"


class StatusAnuncio(str, PyEnum):
    disponivel = "disponivel"
    reservado = "reservado"
    doado_trocado = "doado_trocado"


class Anuncio(Base):
    __tablename__ = "anuncios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    titulo: Mapped[str] = mapped_column(String(200), nullable=False, index=True)
    descricao: Mapped[str] = mapped_column(Text, nullable=False)
    tipo: Mapped[TipoAnuncio] = mapped_column(
        Enum(TipoAnuncio, name="tipo_anuncio"), nullable=False
    )
    condicao: Mapped[CondicaoItem] = mapped_column(
        Enum(CondicaoItem, name="condicao_item"), nullable=False
    )
    status: Mapped[StatusAnuncio] = mapped_column(
        Enum(StatusAnuncio, name="status_anuncio"),
        default=StatusAnuncio.disponivel,
        nullable=False,
        index=True,
    )
    localizacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(9), nullable=True, index=True)
    usuario_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    categoria_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("categorias.id", ondelete="SET NULL"), nullable=True, index=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False, index=True
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    usuario: Mapped["Usuario"] = relationship(  # noqa: F821
        "Usuario", back_populates="anuncios"
    )
    categoria: Mapped["Categoria"] = relationship(  # noqa: F821
        "Categoria", back_populates="anuncios"
    )
    imagens: Mapped[list["AnuncioImagem"]] = relationship(
        "AnuncioImagem", back_populates="anuncio", cascade="all, delete-orphan"
    )
    status_historico: Mapped[list["StatusHistorico"]] = relationship(
        "StatusHistorico", back_populates="anuncio", cascade="all, delete-orphan"
    )
    conversas: Mapped[list["Conversa"]] = relationship(  # noqa: F821
        "Conversa", back_populates="anuncio", cascade="all, delete-orphan"
    )
    denuncias: Mapped[list["Denuncia"]] = relationship(  # noqa: F821
        "Denuncia", back_populates="anuncio"
    )


class AnuncioImagem(Base):
    __tablename__ = "anuncio_imagens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    anuncio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("anuncios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    url: Mapped[str] = mapped_column(String(500), nullable=False)
    ordem: Mapped[int] = mapped_column(Integer, default=0, nullable=False)

    anuncio: Mapped["Anuncio"] = relationship("Anuncio", back_populates="imagens")


class StatusHistorico(Base):
    __tablename__ = "status_historico"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    anuncio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("anuncios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    status_anterior: Mapped[StatusAnuncio | None] = mapped_column(
        Enum(StatusAnuncio, name="status_anuncio"), nullable=True
    )
    status_novo: Mapped[StatusAnuncio] = mapped_column(
        Enum(StatusAnuncio, name="status_anuncio"), nullable=False
    )
    alterado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    anuncio: Mapped["Anuncio"] = relationship("Anuncio", back_populates="status_historico")
