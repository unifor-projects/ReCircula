from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.schemas.usuario import UsuarioPublico


class MensagemCreate(BaseModel):
    conteudo: str = Field(..., min_length=1, max_length=5000, examples=["Olá, ainda está disponível?"])


class MensagemResponse(BaseModel):
    id: int
    conversa_id: int
    autor_id: int
    conteudo: str
    lida: bool
    criado_em: datetime
    autor: UsuarioPublico

    model_config = {"from_attributes": True}


class ConversaCreate(BaseModel):
    anuncio_id: int = Field(..., description="ID do anúncio sobre o qual iniciar conversa")
    mensagem_inicial: str = Field(
        ..., min_length=1, max_length=5000, examples=["Olá, tenho interesse no item!"]
    )


class ConversaResponse(BaseModel):
    id: int
    anuncio_id: int
    iniciador_id: int
    anunciante_id: int
    criado_em: datetime
    iniciador: UsuarioPublico
    anunciante: UsuarioPublico
    mensagens: list[MensagemResponse]

    model_config = {"from_attributes": True}


class ConversaListResponse(BaseModel):
    id: int
    anuncio_id: int
    iniciador_id: int
    anunciante_id: int
    criado_em: datetime
    iniciador: UsuarioPublico
    anunciante: UsuarioPublico
    total_nao_lidas: Optional[int] = 0

    model_config = {"from_attributes": True}
