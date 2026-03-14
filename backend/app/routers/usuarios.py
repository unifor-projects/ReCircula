from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_user
from app.models.usuario import Usuario
from app.schemas.usuario import UsuarioResponse, UsuarioUpdate

router = APIRouter(prefix="/usuarios", tags=["Usuários"])


@router.get("/me", response_model=UsuarioResponse, summary="Meu perfil")
def meu_perfil(current_user: Usuario = Depends(get_current_user)):
    """Retorna os dados do usuário autenticado."""
    return current_user


@router.put("/me", response_model=UsuarioResponse, summary="Atualizar meu perfil")
def atualizar_perfil(
    dados: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Atualiza os dados do perfil do usuário autenticado."""
    for field, value in dados.model_dump(exclude_none=True).items():
        setattr(current_user, field, value)
    db.commit()
    db.refresh(current_user)
    return current_user


@router.get("/{usuario_id}", response_model=UsuarioResponse, summary="Perfil público de usuário")
def perfil_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Retorna o perfil público de um usuário pelo ID."""
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    return usuario
