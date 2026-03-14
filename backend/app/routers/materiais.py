from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

from app.models.material import MaterialCreate, MaterialResponse, MaterialUpdate

router = APIRouter(prefix="/materiais", tags=["Materiais"])

# In-memory store (replace with database in production)
_db: dict[int, dict] = {}
_next_id = 1


@router.get("/", response_model=List[MaterialResponse], summary="Listar materiais")
def listar_materiais():
    """Retorna a lista de todos os materiais recicláveis cadastrados."""
    return list(_db.values())


@router.get("/{material_id}", response_model=MaterialResponse, summary="Buscar material por ID")
def buscar_material(material_id: int):
    """Retorna os dados de um material específico pelo seu ID."""
    if material_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")
    return _db[material_id]


@router.post("/", response_model=MaterialResponse, status_code=status.HTTP_201_CREATED, summary="Criar material")
def criar_material(material: MaterialCreate):
    """Cadastra um novo tipo de material reciclável."""
    global _next_id
    novo = {
        "id": _next_id,
        "nome": material.nome,
        "tipo": material.tipo,
        "descricao": material.descricao,
        "instrucoes_descarte": material.instrucoes_descarte,
        "criado_em": datetime.utcnow(),
    }
    _db[_next_id] = novo
    _next_id += 1
    return novo


@router.put("/{material_id}", response_model=MaterialResponse, summary="Atualizar material")
def atualizar_material(material_id: int, dados: MaterialUpdate):
    """Atualiza os dados de um material existente."""
    if material_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")
    material = _db[material_id]
    for field, value in dados.model_dump(exclude_none=True).items():
        material[field] = value
    return material


@router.delete("/{material_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir material")
def excluir_material(material_id: int):
    """Remove um material do sistema."""
    if material_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Material não encontrado")
    del _db[material_id]
