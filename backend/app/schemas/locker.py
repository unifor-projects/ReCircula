from datetime import datetime

from pydantic import BaseModel


class LockerResponse(BaseModel):
    id: int
    unidade: str
    codigo_unidade: str
    numero: str
    logradouro: str
    complemento: str | None
    bairro: str | None
    cidade: str
    estado: str | None
    pais: str
    cep: str
    ativo: bool
    criado_em: datetime
    atualizado_em: datetime

    model_config = {"from_attributes": True}


class LockerAcaoResponse(BaseModel):
    evento_id: int
    acao: str
    sucesso: bool
    detalhe: str
    gateway: dict
