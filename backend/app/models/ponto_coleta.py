from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class PontoColetaBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150, examples=["Ecoponto Centro"])
    endereco: str = Field(..., examples=["Av. Washington Soares, 1321 - Fortaleza, CE"])
    latitude: Optional[float] = Field(None, examples=[-3.7172])
    longitude: Optional[float] = Field(None, examples=[-38.5433])
    descricao: Optional[str] = Field(None, examples=["Ponto de coleta de materiais recicláveis"])


class PontoColetaCreate(PontoColetaBase):
    pass


class PontoColetaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    endereco: Optional[str] = None
    latitude: Optional[float] = None
    longitude: Optional[float] = None
    descricao: Optional[str] = None


class PontoColetaResponse(PontoColetaBase):
    id: int
    criado_em: datetime

    model_config = {"from_attributes": True}
