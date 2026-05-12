from enum import Enum
from typing import Optional

from pydantic import BaseModel, Field, model_validator
from datetime import datetime

from app.models.denuncia import StatusDenuncia


class TipoDenuncia(str, Enum):
    anuncio = "anuncio"
    usuario = "usuario"


class DenunciaCreate(BaseModel):
    tipo: TipoDenuncia = Field(..., description="Tipo do alvo denunciado")
    alvo_id: int = Field(..., gt=0, description="ID do anúncio ou usuário denunciado")
    motivo: str = Field(..., min_length=5, max_length=200, examples=["Conteúdo inapropriado"])
    descricao: Optional[str] = Field(None, max_length=2000)

    @model_validator(mode="before")
    @classmethod
    def _normalizar_payload_legado(cls, data):
        if not isinstance(data, dict):
            return data

        normalized = data.copy()
        has_tipo = normalized.get("tipo") is not None
        has_alvo_id = normalized.get("alvo_id") is not None
        has_canonical = has_tipo or has_alvo_id
        has_complete_canonical = has_tipo and has_alvo_id
        has_anuncio_legacy = normalized.get("anuncio_id") is not None
        has_usuario_legacy = normalized.get("usuario_denunciado_id") is not None
        legacy_targets = int(has_anuncio_legacy) + int(has_usuario_legacy)

        if has_canonical and legacy_targets:
            raise ValueError(
                "Envie exatamente um alvo: use 'tipo' e 'alvo_id' ou um único campo legado."
            )

        if legacy_targets > 1:
            raise ValueError(
                "Envie exatamente um alvo: 'anuncio_id' e 'usuario_denunciado_id' são mutuamente exclusivos."
            )

        if has_complete_canonical:
            return normalized

        if has_anuncio_legacy:
            normalized["tipo"] = TipoDenuncia.anuncio
            normalized["alvo_id"] = normalized["anuncio_id"]
            return normalized

        if has_usuario_legacy:
            normalized["tipo"] = TipoDenuncia.usuario
            normalized["alvo_id"] = normalized["usuario_denunciado_id"]

        return normalized


class DenunciaResolucao(BaseModel):
    status: StatusDenuncia
    remover_anuncio: bool = False
    suspender_usuario: bool = False


class DenunciaResponse(BaseModel):
    id: int
    denunciante_id: int
    anuncio_id: Optional[int]
    usuario_denunciado_id: Optional[int]
    motivo: str
    descricao: Optional[str]
    status: StatusDenuncia
    admin_id: Optional[int]
    criado_em: datetime
    resolvido_em: Optional[datetime]

    model_config = {"from_attributes": True}
