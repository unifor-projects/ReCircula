from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from app.database import get_db
from app.deps import get_current_user, get_current_admin
from app.models.usuario import Usuario
from app.models.anuncio import Anuncio
from app.models.denuncia import Denuncia, StatusDenuncia
from app.schemas.denuncia import DenunciaCreate, DenunciaResolucao, DenunciaResponse, TipoDenuncia

router = APIRouter(prefix="/denuncias", tags=["Denúncias e Moderação"])


@router.post("/", response_model=DenunciaResponse, status_code=status.HTTP_201_CREATED, summary="Denunciar anúncio ou usuário")
def criar_denuncia(
    dados: DenunciaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Registra uma denúncia contra um anúncio ou usuário (RF07.1)."""
    anuncio_id = None
    usuario_denunciado_id = None

    if dados.tipo == TipoDenuncia.anuncio:
        anuncio = db.get(Anuncio, dados.alvo_id)
        if not anuncio:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anúncio não encontrado")
        anuncio_id = dados.alvo_id
    else:
        usuario = db.get(Usuario, dados.alvo_id)
        if not usuario:
            raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
        usuario_denunciado_id = dados.alvo_id

    denuncia = Denuncia(
        denunciante_id=current_user.id,
        anuncio_id=anuncio_id,
        usuario_denunciado_id=usuario_denunciado_id,
        motivo=dados.motivo,
        descricao=dados.descricao,
    )
    db.add(denuncia)
    db.commit()
    db.refresh(denuncia)
    return denuncia


@router.get("/", response_model=List[DenunciaResponse], summary="Listar denúncias (admin)")
def listar_denuncias(
    db: Session = Depends(get_db),
    _: Usuario = Depends(get_current_admin),
):
    """Lista todas as denúncias pendentes (RF07.2)."""
    return (
        db.query(Denuncia)
        .filter(Denuncia.status == StatusDenuncia.pendente)
        .order_by(Denuncia.criado_em.desc())
        .all()
    )


@router.patch("/{denuncia_id}/resolver", response_model=DenunciaResponse, summary="Resolver denúncia (admin)")
def resolver_denuncia(
    denuncia_id: int,
    dados: DenunciaResolucao,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_admin),
):
    """Analisa e resolve uma denúncia, com opção de remover o anúncio ou suspender o usuário (RF07.3)."""
    denuncia = db.get(Denuncia, denuncia_id)
    if not denuncia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Denúncia não encontrada")

    denuncia.status = dados.status
    denuncia.admin_id = admin.id
    denuncia.resolvido_em = datetime.now(timezone.utc)

    if dados.remover_anuncio and denuncia.anuncio_id:
        anuncio = db.get(Anuncio, denuncia.anuncio_id)
        if anuncio:
            db.delete(anuncio)

    if dados.suspender_usuario and denuncia.usuario_denunciado_id:
        usuario = db.get(Usuario, denuncia.usuario_denunciado_id)
        if usuario:
            usuario.is_active = False

    db.commit()
    db.refresh(denuncia)
    return denuncia
