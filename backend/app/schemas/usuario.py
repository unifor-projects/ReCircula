from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime


class UsuarioCreate(BaseModel):
    nome: str = Field(..., min_length=2, max_length=150, examples=["João Silva"])
    email: EmailStr = Field(..., examples=["joao@email.com"])
    senha: str = Field(..., min_length=6, examples=["senha123"])


class UsuarioUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=2, max_length=150)
    foto_url: Optional[str] = Field(None, max_length=500)
    descricao: Optional[str] = None
    localizacao: Optional[str] = Field(None, max_length=255)
    cep: Optional[str] = Field(None, max_length=9, pattern=r"^\d{5}-?\d{3}$")


class UsuarioPublico(BaseModel):
    id: int
    nome: str
    foto_url: Optional[str]
    localizacao: Optional[str]
    criado_em: datetime

    model_config = {"from_attributes": True}


class UsuarioResponse(BaseModel):
    id: int
    nome: str
    email: EmailStr
    foto_url: Optional[str]
    descricao: Optional[str]
    localizacao: Optional[str]
    cep: Optional[str]
    is_active: bool
    is_admin: bool
    email_verificado: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class RegisterResponse(BaseModel):
    usuario: UsuarioResponse
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    sub: Optional[str] = None
