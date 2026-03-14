from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

from app.models.ponto_coleta import PontoColetaCreate, PontoColetaResponse, PontoColetaUpdate

router = APIRouter(prefix="/pontos-coleta", tags=["Pontos de Coleta"])

# In-memory store (replace with database in production)
_db: dict[int, dict] = {}
_next_id = 1


@router.get("/", response_model=List[PontoColetaResponse], summary="Listar pontos de coleta")
def listar_pontos():
    """Retorna a lista de todos os pontos de coleta cadastrados."""
    return list(_db.values())


@router.get("/{ponto_id}", response_model=PontoColetaResponse, summary="Buscar ponto de coleta por ID")
def buscar_ponto(ponto_id: int):
    """Retorna os dados de um ponto de coleta específico pelo seu ID."""
    if ponto_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ponto de coleta não encontrado")
    return _db[ponto_id]


@router.post("/", response_model=PontoColetaResponse, status_code=status.HTTP_201_CREATED, summary="Criar ponto de coleta")
def criar_ponto(ponto: PontoColetaCreate):
    """Cria um novo ponto de coleta."""
    global _next_id
    novo = {
        "id": _next_id,
        "nome": ponto.nome,
        "endereco": ponto.endereco,
        "latitude": ponto.latitude,
        "longitude": ponto.longitude,
        "descricao": ponto.descricao,
        "criado_em": datetime.utcnow(),
    }
    _db[_next_id] = novo
    _next_id += 1
    return novo


@router.put("/{ponto_id}", response_model=PontoColetaResponse, summary="Atualizar ponto de coleta")
def atualizar_ponto(ponto_id: int, dados: PontoColetaUpdate):
    """Atualiza os dados de um ponto de coleta existente."""
    if ponto_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ponto de coleta não encontrado")
    ponto = _db[ponto_id]
    for field, value in dados.model_dump(exclude_none=True).items():
        ponto[field] = value
    return ponto


@router.delete("/{ponto_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir ponto de coleta")
def excluir_ponto(ponto_id: int):
    """Remove um ponto de coleta do sistema."""
    if ponto_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Ponto de coleta não encontrado")
    del _db[ponto_id]
