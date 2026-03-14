from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class CategoriaCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, examples=["Eletrônicos"])
    descricao: Optional[str] = Field(None, examples=["Aparelhos eletrônicos em geral"])


class CategoriaUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    descricao: Optional[str] = None


class CategoriaResponse(BaseModel):
    id: int
    nome: str
    descricao: Optional[str]
    criado_em: datetime

    model_config = {"from_attributes": True}
