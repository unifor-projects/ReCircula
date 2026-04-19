from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload
from typing import List, Optional

from app.database import get_db
from app.deps import get_current_user
from app.models.usuario import Usuario
from app.models.anuncio import Anuncio, AnuncioImagem, StatusHistorico, StatusAnuncio, TipoAnuncio
from app.schemas.anuncio import (
    AnuncioCreate,
    AnuncioUpdate,
    AnuncioStatusUpdate,
    AnuncioResponse,
    AnuncioListResponse,
    StatusHistoricoResponse,
)

router = APIRouter(prefix="/anuncios", tags=["Anúncios"])

_load_options = [
    selectinload(Anuncio.imagens),
    selectinload(Anuncio.categoria),
    selectinload(Anuncio.usuario),
]


def _get_anuncio_or_404(anuncio_id: int, db: Session) -> Anuncio:
    anuncio = (
        db.query(Anuncio)
        .options(*_load_options)
        .filter(Anuncio.id == anuncio_id)
        .first()
    )
    if not anuncio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anúncio não encontrado")
    return anuncio


@router.get("/", response_model=List[AnuncioListResponse], summary="Buscar e listar anúncios")
def listar_anuncios(
    q: Optional[str] = Query(None, description="Busca por título ou descrição"),
    categoria_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None, description="doacao | troca"),
    cep: Optional[str] = Query(None, description="Filtrar por CEP"),
    status: Optional[str] = Query(None, description="disponivel | reservado | doado_trocado"),
    ordenar: Optional[str] = Query("recente", description="recente | antigo"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Lista anúncios com suporte a busca por palavra-chave, filtragem por categoria,
    tipo, CEP e status. Anúncios concluídos são ocultados por padrão (RF04, RF06.2).
    """
    query = db.query(Anuncio).options(*_load_options)

    # RF06.2 – hide concluded ads by default unless explicitly requested
    if status:
        query = query.filter(Anuncio.status == status)
    else:
        query = query.filter(Anuncio.status != StatusAnuncio.doado_trocado)

    if q:
        query = query.filter(
            or_(
                Anuncio.titulo.ilike(f"%{q}%"),
                Anuncio.descricao.ilike(f"%{q}%"),
            )
        )
    if categoria_id:
        query = query.filter(Anuncio.categoria_id == categoria_id)
    if tipo and tipo in (TipoAnuncio.doacao, TipoAnuncio.troca):
        query = query.filter(
            or_(Anuncio.tipo == tipo, Anuncio.tipo == TipoAnuncio.ambos)
        )
    elif tipo:
        query = query.filter(Anuncio.tipo == tipo)
    if cep:
        query = query.filter(Anuncio.cep.ilike(f"{cep[:5]}%"))

    if ordenar == "antigo":
        query = query.order_by(Anuncio.criado_em.asc())
    else:
        query = query.order_by(Anuncio.criado_em.desc())

    return query.offset(offset).limit(limit).all()


@router.get("/{anuncio_id}", response_model=AnuncioResponse, summary="Detalhe do anúncio")
def buscar_anuncio(anuncio_id: int, db: Session = Depends(get_db)):
    """Retorna todos os detalhes de um anúncio pelo ID."""
    return _get_anuncio_or_404(anuncio_id, db)


@router.post("/", response_model=AnuncioResponse, status_code=status.HTTP_201_CREATED, summary="Criar anúncio")
def criar_anuncio(
    dados: AnuncioCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Cria um novo anúncio de doação ou troca (RF03)."""
    anuncio = Anuncio(
        titulo=dados.titulo,
        descricao=dados.descricao,
        tipo=dados.tipo,
        condicao=dados.condicao,
        categoria_id=dados.categoria_id,
        localizacao=dados.localizacao,
        cep=dados.cep,
        usuario_id=current_user.id,
    )
    db.add(anuncio)
    db.flush()

    for i, url in enumerate(dados.imagens):
        db.add(AnuncioImagem(anuncio_id=anuncio.id, url=url, ordem=i))

    db.add(StatusHistorico(anuncio_id=anuncio.id, status_novo=StatusAnuncio.disponivel))
    db.commit()
    return _get_anuncio_or_404(anuncio.id, db)


@router.put("/{anuncio_id}", response_model=AnuncioResponse, summary="Editar anúncio")
def atualizar_anuncio(
    anuncio_id: int,
    dados: AnuncioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita um anúncio existente. Apenas o dono pode editar (RF03.4)."""
    anuncio = _get_anuncio_or_404(anuncio_id, db)
    if anuncio.usuario_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

    for field in ("titulo", "tipo", "descricao", "condicao", "categoria_id", "localizacao", "cep"):
        value = getattr(dados, field)
        if value is not None:
            setattr(anuncio, field, value)

    if dados.imagens is not None:
        db.query(AnuncioImagem).filter(AnuncioImagem.anuncio_id == anuncio_id).delete()
        for i, url in enumerate(dados.imagens):
            db.add(AnuncioImagem(anuncio_id=anuncio_id, url=url, ordem=i))

    db.commit()
    return _get_anuncio_or_404(anuncio_id, db)


@router.patch("/{anuncio_id}/status", response_model=AnuncioResponse, summary="Alterar status do anúncio")
def alterar_status(
    anuncio_id: int,
    dados: AnuncioStatusUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Altera o status do anúncio (disponível, reservado, doado_trocado – RF06)."""
    anuncio = _get_anuncio_or_404(anuncio_id, db)
    if anuncio.usuario_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

    historico = StatusHistorico(
        anuncio_id=anuncio_id,
        status_anterior=anuncio.status,
        status_novo=dados.status,
    )
    anuncio.status = dados.status
    db.add(historico)
    db.commit()
    return _get_anuncio_or_404(anuncio_id, db)


@router.get("/{anuncio_id}/historico-status", response_model=List[StatusHistoricoResponse], summary="Histórico de status")
def historico_status(anuncio_id: int, db: Session = Depends(get_db)):
    """Retorna o histórico completo de mudanças de status do anúncio (RF06.3)."""
    _get_anuncio_or_404(anuncio_id, db)
    return (
        db.query(StatusHistorico)
        .filter(StatusHistorico.anuncio_id == anuncio_id)
        .order_by(StatusHistorico.alterado_em.asc())
        .all()
    )


@router.delete("/{anuncio_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Excluir anúncio")
def excluir_anuncio(
    anuncio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Remove um anúncio. Apenas o dono ou admin podem excluir."""
    anuncio = _get_anuncio_or_404(anuncio_id, db)
    if anuncio.usuario_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")
    db.delete(anuncio)
    db.commit()
