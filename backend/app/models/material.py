from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class TipoMaterial(str, Enum):
    plastico = "plastico"
    papel = "papel"
    vidro = "vidro"
    metal = "metal"
    organico = "organico"
    eletronico = "eletronico"
    outro = "outro"


class MaterialBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, examples=["Garrafa PET"])
    tipo: TipoMaterial = Field(..., examples=[TipoMaterial.plastico])
    descricao: Optional[str] = Field(None, examples=["Garrafas plásticas tipo PET"])
    instrucoes_descarte: Optional[str] = Field(
        None, examples=["Limpar e amassar antes de descartar"]
    )


class MaterialCreate(MaterialBase):
    pass


class MaterialUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    tipo: Optional[TipoMaterial] = None
    descricao: Optional[str] = None
    instrucoes_descarte: Optional[str] = None


class MaterialResponse(MaterialBase):
    id: int
    criado_em: datetime

    model_config = {"from_attributes": True}
