from datetime import datetime, timezone
from sqlalchemy import Boolean, DateTime, String, Text, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


def _utcnow() -> datetime:
    return datetime.now(timezone.utc)


class Usuario(Base):
    __tablename__ = "usuarios"

    id: Mapped[int] = mapped_column(primary_key=True, index=True)
    nome: Mapped[str] = mapped_column(String(150), nullable=False)
    email: Mapped[str] = mapped_column(String(255), unique=True, index=True, nullable=False)
    senha_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    foto_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    descricao: Mapped[str | None] = mapped_column(Text, nullable=True)
    localizacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    cep: Mapped[str | None] = mapped_column(String(9), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_admin: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    email_verificado: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    token_verificacao: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_reset_senha: Mapped[str | None] = mapped_column(String(255), nullable=True)
    token_reset_expira_em: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True, index=True
    )
    refresh_token_version: Mapped[int] = mapped_column(
        default=0, server_default=text("0"), nullable=False
    )
    criado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, nullable=False
    )
    atualizado_em: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), default=_utcnow, onupdate=_utcnow, nullable=False
    )

    anuncios: Mapped[list["Anuncio"]] = relationship(  # noqa: F821
        "Anuncio", back_populates="usuario", cascade="all, delete-orphan"
    )
    mensagens_enviadas: Mapped[list["Mensagem"]] = relationship(  # noqa: F821
        "Mensagem", back_populates="autor", foreign_keys="Mensagem.autor_id"
    )
    denuncias_feitas: Mapped[list["Denuncia"]] = relationship(  # noqa: F821
        "Denuncia", back_populates="denunciante", foreign_keys="Denuncia.denunciante_id"
    )
