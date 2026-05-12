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
        if data.get("tipo") is not None and data.get("alvo_id") is not None:
            return data
        if data.get("anuncio_id") is not None:
            data["tipo"] = TipoDenuncia.anuncio
            data["alvo_id"] = data["anuncio_id"]
            return data
        if data.get("usuario_denunciado_id") is not None:
            data["tipo"] = TipoDenuncia.usuario
            data["alvo_id"] = data["usuario_denunciado_id"]
        return data


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
