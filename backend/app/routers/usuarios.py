from fastapi import APIRouter, HTTPException, status
from typing import List
from datetime import datetime

from app.models.usuario import UsuarioCreate, UsuarioResponse, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuários"])

# In-memory store (replace with database in production)
_db: dict[int, dict] = {}
_next_id = 1


@router.get("/", response_model=List[UsuarioResponse], summary="Listar usuários")
def listar_usuarios():
    """Retorna a lista de todos os usuários cadastrados."""
    return list(_db.values())


@router.get("/{usuario_id}", response_model=UsuarioResponse, summary="Buscar usuário por ID")
def buscar_usuario(usuario_id: int):
    """Retorna os dados de um usuário específico pelo seu ID."""
    if usuario_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return _db[usuario_id]


@router.post("/", response_model=UsuarioResponse, status_code=status.HTTP_201_CREATED, summary="Criar usuário")
def criar_usuario(usuario: UsuarioCreate):
    """Cria um novo usuário no sistema."""
    global _next_id
    novo = {
        "id": _next_id,
        "nome": usuario.nome,
        "email": usuario.email,
        "criado_em": datetime.utcnow(),
    }
    _db[_next_id] = novo
    _next_id += 1
    return novo


@router.put("/{usuario_id}", response_model=UsuarioResponse, summary="Atualizar usuário")
def atualizar_usuario(usuario_id: int, dados: UsuarioUpdate):
    """Atualiza os dados de um usuário existente."""
    if usuario_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    usuario = _db[usuario_id]
    if dados.nome is not None:
        usuario["nome"] = dados.nome
    if dados.email is not None:
        usuario["email"] = dados.email
    return usuario


@router.delete("/{usuario_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir usuário")
def excluir_usuario(usuario_id: int):
    """Remove um usuário do sistema."""
    if usuario_id not in _db:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    del _db[usuario_id]
