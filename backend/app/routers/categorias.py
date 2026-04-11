from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin
from app.models.usuario import Usuario
from app.models.categoria import Categoria
from app.schemas.categoria import CategoriaCreate, CategoriaUpdate, CategoriaResponse
from typing import List

router = APIRouter(prefix="/categorias", tags=["Categorias"])


@router.get("/", response_model=List[CategoriaResponse], summary="Listar categorias")
def listar_categorias(db: Session = Depends(get_db)):
    """Retorna todas as categorias disponíveis."""
    return db.query(Categoria).order_by(Categoria.nome).all()


@router.get("/{categoria_id}", response_model=CategoriaResponse, summary="Buscar categoria por ID")
def buscar_categoria(categoria_id: int, db: Session = Depends(get_db)):
    cat = db.get(Categoria, categoria_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    return cat


@router.post("/", response_model=CategoriaResponse, status_code=status.HTTP_201_CREATED, summary="Criar categoria (admin)")
def criar_categoria(
    dados: CategoriaCreate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
):
    """Cria uma nova categoria. Requer privilégios de administrador."""
    existente = db.query(Categoria).filter(Categoria.nome == dados.nome).first()
    if existente:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Categoria já existe")
    cat = Categoria(**dados.model_dump())
    db.add(cat)
    db.commit()
    db.refresh(cat)
    return cat


@router.put("/{categoria_id}", response_model=CategoriaResponse, summary="Atualizar categoria (admin)")
def atualizar_categoria(
    categoria_id: int,
    dados: CategoriaUpdate,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
):
    cat = db.get(Categoria, categoria_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    for field, value in dados.model_dump(exclude_none=True).items():
        setattr(cat, field, value)
    db.commit()
    db.refresh(cat)
    return cat


@router.delete("/{categoria_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir categoria (admin)")
def excluir_categoria(
    categoria_id: int,
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
):
    cat = db.get(Categoria, categoria_id)
    if not cat:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Categoria não encontrada")
    db.delete(cat)
    db.commit()
