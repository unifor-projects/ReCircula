from datetime import datetime, timezone
from enum import Enum as PyEnum

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class LockerEventoAcao(str, PyEnum):
    abrir = "abrir"
    fechar = "fechar"
    concluir_doacao = "concluir_doacao"


class Locker(Base):
    __tablename__ = "lockers"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    unidade: Mapped[str] = mapped_column(String(120), nullable=False)
    codigo_unidade: Mapped[str] = mapped_column(String(20), unique=True, nullable=False, index=True)
    numero: Mapped[str] = mapped_column(String(20), nullable=False)
    logradouro: Mapped[str] = mapped_column(String(255), nullable=False)
    complemento: Mapped[str | None] = mapped_column(String(120), nullable=True)
    bairro: Mapped[str | None] = mapped_column(String(120), nullable=True)
    cidade: Mapped[str] = mapped_column(String(120), nullable=False)
    estado: Mapped[str | None] = mapped_column(String(120), nullable=True)
    pais: Mapped[str] = mapped_column(String(120), nullable=False, default="Brasil")
    cep: Mapped[str] = mapped_column(String(9), nullable=False, index=True)
    ativo: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False)
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    anuncios: Mapped[list["Anuncio"]] = relationship("Anuncio", back_populates="locker")  # noqa: F821
    eventos: Mapped[list["LockerEvento"]] = relationship(
        "LockerEvento", back_populates="locker", cascade="all, delete-orphan"
    )


class LockerEvento(Base):
    __tablename__ = "locker_eventos"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    anuncio_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("anuncios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    locker_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("lockers.id", ondelete="CASCADE"), nullable=False, index=True
    )
    acao: Mapped[LockerEventoAcao] = mapped_column(
        Enum(LockerEventoAcao, name="locker_evento_acao"), nullable=False, index=True
    )
    sucesso: Mapped[bool] = mapped_column(Boolean, nullable=False)
    detalhe: Mapped[str | None] = mapped_column(Text, nullable=True)
    criado_em: Mapped[datetime] = mapped_column(DateTime(timezone=True), default=_utcnow, nullable=False, index=True)

    anuncio: Mapped["Anuncio"] = relationship("Anuncio", back_populates="locker_eventos")  # noqa: F821
    locker: Mapped["Locker"] = relationship("Locker", back_populates="eventos")
