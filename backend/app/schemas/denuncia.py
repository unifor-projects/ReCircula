from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.denuncia import StatusDenuncia


class DenunciaCreate(BaseModel):
    anuncio_id: Optional[int] = Field(None, description="ID do anúncio denunciado")
    usuario_denunciado_id: Optional[int] = Field(None, description="ID do usuário denunciado")
    motivo: str = Field(..., min_length=5, max_length=200, examples=["Conteúdo inapropriado"])
    descricao: Optional[str] = Field(None, max_length=2000)


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
