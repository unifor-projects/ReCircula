from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime

from app.models.anuncio import TipoAnuncio, CondicaoItem, StatusAnuncio
from app.schemas.categoria import CategoriaResponse
from app.schemas.usuario import UsuarioPublico


class AnuncioImagemResponse(BaseModel):
    id: int
    url: str
    ordem: int

    model_config = {"from_attributes": True}


class AnuncioCreate(BaseModel):
    titulo: str = Field(..., min_length=3, max_length=200, examples=["Sofá 3 lugares"])
    descricao: str = Field(..., min_length=10, examples=["Sofá em bom estado, retirar no local"])
    tipo: TipoAnuncio = Field(..., examples=[TipoAnuncio.doacao])
    condicao: CondicaoItem = Field(..., examples=[CondicaoItem.usado])
    categoria_id: Optional[int] = None
    localizacao: Optional[str] = Field(None, max_length=255)
    cep: Optional[str] = Field(None, max_length=9, pattern=r"^\d{5}-?\d{3}$")
    imagens: list[str] = Field(default_factory=list, description="Lista de URLs de imagens")


class AnuncioUpdate(BaseModel):
    titulo: Optional[str] = Field(None, min_length=3, max_length=200)
    tipo: Optional[TipoAnuncio] = None
    descricao: Optional[str] = Field(None, min_length=10)
    condicao: Optional[CondicaoItem] = None
    categoria_id: Optional[int] = None
    localizacao: Optional[str] = Field(None, max_length=255)
    cep: Optional[str] = Field(None, max_length=9, pattern=r"^\d{5}-?\d{3}$")
    imagens: Optional[list[str]] = None


class AnuncioStatusUpdate(BaseModel):
    status: StatusAnuncio


class StatusHistoricoResponse(BaseModel):
    id: int
    status_anterior: Optional[StatusAnuncio]
    status_novo: StatusAnuncio
    alterado_em: datetime

    model_config = {"from_attributes": True}


class AnuncioResponse(BaseModel):
    id: int
    titulo: str
    descricao: str
    tipo: TipoAnuncio
    condicao: CondicaoItem
    status: StatusAnuncio
    localizacao: Optional[str]
    cep: Optional[str]
    usuario_id: int
    categoria_id: Optional[int]
    criado_em: datetime
    atualizado_em: datetime
    imagens: list[AnuncioImagemResponse]
    categoria: Optional[CategoriaResponse]
    usuario: UsuarioPublico

    model_config = {"from_attributes": True}


class AnuncioListResponse(BaseModel):
    id: int
    titulo: str
    tipo: TipoAnuncio
    condicao: CondicaoItem
    status: StatusAnuncio
    localizacao: Optional[str]
    cep: Optional[str]
    criado_em: datetime
    imagens: list[AnuncioImagemResponse]
    categoria: Optional[CategoriaResponse]
    usuario: UsuarioPublico

    model_config = {"from_attributes": True}
