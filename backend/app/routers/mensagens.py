from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, selectinload
from typing import List

from app.database import get_db
from app.deps import get_current_user
from app.models.usuario import Usuario
from app.models.anuncio import Anuncio
from app.models.mensagem import Conversa, Mensagem
from app.schemas.mensagem import (
    ConversaCreate,
    ConversaResponse,
    ConversaListResponse,
    MensagemCreate,
    MensagemResponse,
)

router = APIRouter(prefix="/mensagens", tags=["Mensagens"])

_conversa_opts = [
    selectinload(Conversa.iniciador),
    selectinload(Conversa.anunciante),
    selectinload(Conversa.mensagens).selectinload(Mensagem.autor),
]


def _get_conversa_or_404(conversa_id: int, db: Session) -> Conversa:
    conversa = (
        db.query(Conversa)
        .options(*_conversa_opts)
        .filter(Conversa.id == conversa_id)
        .first()
    )
    if not conversa:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Conversa não encontrada")
    return conversa


@router.post("/conversas", response_model=ConversaResponse, status_code=status.HTTP_201_CREATED, summary="Iniciar conversa sobre um anúncio")
def iniciar_conversa(
    dados: ConversaCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Inicia uma nova conversa com o anunciante sobre um item (RF05.1 / RF05.4)."""
    anuncio = db.get(Anuncio, dados.anuncio_id)
    if not anuncio:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Anúncio não encontrado")
    if anuncio.usuario_id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Não é possível iniciar conversa sobre o seu próprio anúncio",
        )

    # Prevent duplicate conversation
    existente = (
        db.query(Conversa)
        .filter(
            Conversa.anuncio_id == dados.anuncio_id,
            Conversa.iniciador_id == current_user.id,
        )
        .first()
    )
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Já existe uma conversa sua sobre este anúncio",
        )

    conversa = Conversa(
        anuncio_id=dados.anuncio_id,
        iniciador_id=current_user.id,
        anunciante_id=anuncio.usuario_id,
    )
    db.add(conversa)
    db.flush()

    mensagem = Mensagem(
        conversa_id=conversa.id,
        autor_id=current_user.id,
        conteudo=dados.mensagem_inicial,
    )
    db.add(mensagem)
    db.commit()
    return _get_conversa_or_404(conversa.id, db)


@router.get("/conversas", response_model=List[ConversaListResponse], summary="Minhas conversas")
def minhas_conversas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Lista todas as conversas do usuário autenticado (RF05.2)."""
    from sqlalchemy import or_

    conversas = (
        db.query(Conversa)
        .options(
            selectinload(Conversa.iniciador),
            selectinload(Conversa.anunciante),
            selectinload(Conversa.mensagens),
        )
        .filter(
            or_(
                Conversa.iniciador_id == current_user.id,
                Conversa.anunciante_id == current_user.id,
            )
        )
        .order_by(Conversa.criado_em.desc())
        .all()
    )

    result = []
    for c in conversas:
        nao_lidas = sum(
            1 for m in c.mensagens if not m.lida and m.autor_id != current_user.id
        )
        item = ConversaListResponse.model_validate(c)
        item.total_nao_lidas = nao_lidas
        result.append(item)
    return result


@router.get("/conversas/{conversa_id}", response_model=ConversaResponse, summary="Detalhes e histórico da conversa")
def detalhe_conversa(
    conversa_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna o histórico de mensagens de uma conversa (RF05.2)."""
    conversa = _get_conversa_or_404(conversa_id, db)
    if current_user.id not in (conversa.iniciador_id, conversa.anunciante_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

    # Mark messages as read for current user
    db.query(Mensagem).filter(
        Mensagem.conversa_id == conversa_id,
        Mensagem.autor_id != current_user.id,
        Mensagem.lida.is_(False),
    ).update({"lida": True})
    db.commit()
    return _get_conversa_or_404(conversa_id, db)


@router.post("/conversas/{conversa_id}/mensagens", response_model=MensagemResponse, status_code=status.HTTP_201_CREATED, summary="Enviar mensagem")
def enviar_mensagem(
    conversa_id: int,
    dados: MensagemCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Envia uma mensagem em uma conversa existente (RF05.1)."""
    conversa = _get_conversa_or_404(conversa_id, db)
    if current_user.id not in (conversa.iniciador_id, conversa.anunciante_id):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

    mensagem = Mensagem(
        conversa_id=conversa_id,
        autor_id=current_user.id,
        conteudo=dados.conteudo,
    )
    db.add(mensagem)
    db.commit()
    db.refresh(mensagem)

    from sqlalchemy.orm import joinedload
    return (
        db.query(Mensagem)
        .options(joinedload(Mensagem.autor))
        .filter(Mensagem.id == mensagem.id)
        .first()
    )


@router.get("/nao-lidas", summary="Contagem de mensagens não lidas")
def nao_lidas(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Retorna o número total de mensagens não lidas (RF05.3)."""
    from sqlalchemy import or_

    conversas_ids = (
        db.query(Conversa.id)
        .filter(
            or_(
                Conversa.iniciador_id == current_user.id,
                Conversa.anunciante_id == current_user.id,
            )
        )
        .subquery()
    )
    total = (
        db.query(Mensagem)
        .filter(
            Mensagem.conversa_id.in_(conversas_ids),
            Mensagem.autor_id != current_user.id,
            Mensagem.lida.is_(False),
        )
        .count()
    )
    return {"total_nao_lidas": total}
