from datetime import datetime, timezone
from enum import Enum as PyEnum
from sqlalchemy import DateTime, Enum, ForeignKey, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class StatusDenuncia(str, PyEnum):
    pendente = "pendente"
    analisada = "analisada"
    resolvida = "resolvida"


class Denuncia(Base):
    __tablename__ = "denuncias"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    denunciante_id: Mapped[int] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="CASCADE"), nullable=False, index=True
    )
    anuncio_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("anuncios.id", ondelete="SET NULL"), nullable=True, index=True
    )
    usuario_denunciado_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True, index=True
    )
    motivo: Mapped[str] = mapped_column(String(200), nullable=False)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[StatusDenuncia] = mapped_column(
        Enum(StatusDenuncia, name="status_denuncia"),
        default=StatusDenuncia.pendente,
        nullable=False,
        index=True,
    )
    admin_id: Mapped[int | None] = mapped_column(
        Integer, ForeignKey("usuarios.id", ondelete="SET NULL"), nullable=True
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    resolvido_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    denunciante: Mapped["Usuario"] = relationship(  # noqa: F821
        "Usuario", back_populates="denuncias_feitas", foreign_keys=[denunciante_id]
    )
    anuncio: Mapped["Anuncio | None"] = relationship(  # noqa: F821
        "Anuncio", back_populates="denuncias", foreign_keys=[anuncio_id]
    )
    usuario_denunciado: Mapped["Usuario | None"] = relationship(  # noqa: F821
        "Usuario", foreign_keys=[usuario_denunciado_id]
    )
    admin: Mapped["Usuario | None"] = relationship(  # noqa: F821
        "Usuario", foreign_keys=[admin_id]
    )
