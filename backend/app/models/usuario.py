from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UsuarioBase(BaseModel):
    nome: str = Field(..., min_length=2, max_length=100, examples=["João Silva"])
    email: EmailStr = Field(..., examples=["joao@email.com"])


class UsuarioCreate(UsuarioBase):
    senha: str = Field(..., min_length=6, examples=["senha123"])


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=100)
    email: Optional[EmailStr] = None


class UsuarioResponse(UsuarioBase):
    id: int
    criado_em: datetime

    model_config = {"from_attributes": True}
