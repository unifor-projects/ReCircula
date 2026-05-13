from datetime import datetime, timezone
from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.database import get_db
from app.deps import get_current_admin, get_current_user
from app.models.anuncio import Anuncio
from app.models.decisao_administrativa import AcaoAdministrativa, DecisaoAdministrativa
from app.models.denuncia import Denuncia, StatusDenuncia
from app.models.usuario import Usuario
from app.routers.anuncios import _delete_image_files
from app.schemas.admin import AcaoModeracao, ResolverDenunciaAdminRequest
from app.schemas.denuncia import DenunciaResponse
from app.schemas.usuario import UsuarioResponse

router = APIRouter(
    prefix="/admin",
    tags=["Administração e Moderação"],
    dependencies=[Depends(get_current_admin)],
)


def _registrar_log(
    db: Session,
    *,
    admin_id: int,
    acao: AcaoAdministrativa,
    denuncia_id: int | None = None,
    anuncio_id: int | None = None,
    usuario_id: int | None = None,
) -> None:
    db.add(
        DecisaoAdministrativa(
            admin_id=admin_id,
            acao=acao,
            denuncia_id=denuncia_id,
            anuncio_id=anuncio_id,
            usuario_id=usuario_id,
        )
    )


@router.get("/denuncias", response_model=List[DenunciaResponse], summary="Listar denúncias pendentes (admin)")
def listar_denuncias_pendentes_admin(db: Session = Depends(get_db)):
    return (
        db.query(Denuncia)
        .filter(Denuncia.status == StatusDenuncia.pendente)
        .order_by(Denuncia.criado_em.desc())
        .all()
    )


@router.patch(
    "/denuncias/{denuncia_id}/resolver",
    response_model=DenunciaResponse,
    summary="Resolver denúncia com ação administrativa",
)
def resolver_denuncia_admin(
    denuncia_id: int,
    dados: ResolverDenunciaAdminRequest,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user),
):
    denuncia = db.get(Denuncia, denuncia_id)
    if not denuncia:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Denúncia não encontrada")

    acao = AcaoAdministrativa(dados.acao.value)
    usuario_afetado_id = denuncia.usuario_denunciado_id
    if dados.acao == AcaoModeracao.remover_anuncio:
        if not denuncia.anuncio_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Denúncia não está vinculada a anúncio",
            )
        anuncio = db.get(Anuncio, denuncia.anuncio_id)
        if anuncio:
            usuario_afetado_id = anuncio.usuario_id
            _delete_image_files(anuncio.imagens)
            db.delete(anuncio)
    elif dados.acao == AcaoModeracao.suspender_usuario:
        if not denuncia.usuario_denunciado_id:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Denúncia não está vinculada a usuário",
            )
        usuario = db.get(Usuario, denuncia.usuario_denunciado_id)
        if usuario:
            usuario.is_active = False

    denuncia.status = StatusDenuncia.resolvida
    denuncia.admin_id = admin.id
    denuncia.resolvido_em = datetime.now(timezone.utc)
    _registrar_log(
        db,
        admin_id=admin.id,
        denuncia_id=denuncia.id,
        anuncio_id=denuncia.anuncio_id,
        usuario_id=usuario_afetado_id,
        acao=acao,
    )
    db.commit()
    db.refresh(denuncia)
    return denuncia


@router.delete("/anuncios/{anuncio_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Remover anúncio (admin)")
def remover_anuncio_admin(
    anuncio_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user),
):
    anuncio = db.get(Anuncio, anuncio_id)
    if not anuncio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anúncio não encontrado")
    _delete_image_files(anuncio.imagens)
    db.delete(anuncio)
    _registrar_log(
        db,
        admin_id=admin.id,
        anuncio_id=anuncio_id,
        usuario_id=anuncio.usuario_id,
        acao=AcaoAdministrativa.remover_anuncio,
    )
    db.commit()


@router.patch(
    "/usuarios/{usuario_id}/suspender",
    response_model=UsuarioResponse,
    summary="Suspender usuário (admin)",
)
def suspender_usuario_admin(
    usuario_id: int,
    db: Session = Depends(get_db),
    admin: Usuario = Depends(get_current_user),
):
    usuario = db.get(Usuario, usuario_id)
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    usuario.is_active = False
    _registrar_log(
        db,
        admin_id=admin.id,
        usuario_id=usuario.id,
        acao=AcaoAdministrativa.suspender_usuario,
    )
    db.commit()
    db.refresh(usuario)
    return usuario
