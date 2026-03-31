from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, ForeignKey, Integer, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Conversa(Base):
    __tablename__ = "conversas"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    anuncio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("anuncios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    iniciador_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    anunciante_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    anuncio: Mapped["Anuncio"] = relationship("Anuncio", back_populates="conversas")  # noqa: F821
    iniciador: Mapped["Usuario"] = relationship(  # noqa: F821
        "Usuario", foreign_keys=[iniciador_id]
    )
    anunciante: Mapped["Usuario"] = relationship(  # noqa: F821
        "Usuario", foreign_keys=[anunciante_id]
    )
    mensagens: Mapped[list["Mensagem"]] = relationship(
        "Mensagem", back_populates="conversa", cascade="all, delete-orphan"
    )


class Mensagem(Base):
    __tablename__ = "mensagens"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    conversa_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("conversas.id", ondelete="CASCADE"), nullable=False, index=True
    )
    autor_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    conteudo: Mapped[str] = mapped_column(Text, nullable=False)
    lida: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )

    conversa: Mapped["Conversa"] = relationship("Conversa", back_populates="mensagens")
    autor: Mapped["Usuario"] = relationship(  # noqa: F821
        "Usuario", back_populates="mensagens_enviadas", foreign_keys=[autor_id]
    )
