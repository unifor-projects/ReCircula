from typing import List, Optional
from uuid import uuid4
import math
import json

from fastapi import APIRouter, Depends, File, Form, HTTPException, Query, UploadFile, status
from sqlalchemy import or_
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models.usuario import Usuario
from app.models.anuncio import Anuncio, AnuncioImagem, StatusHistorico, StatusAnuncio, TipoAnuncio, CondicaoItem
from app.models.locker import Locker, LockerEvento, LockerEventoAcao
from app.schemas.anuncio import (
    AnuncioResponse,
    AnuncioListResponse,
    AnuncioStatusUpdate,
    StatusHistoricoResponse,
)
from app.schemas.locker import LockerAcaoResponse
from app.services.geocode import geocode_cep, haversine_km
from app.services.locker_control import enviar_comando_abertura, enviar_comando_fechamento
from app.services.uploads import ANUNCIO_IMAGES_DIR, delete_image_files

router = APIRouter(prefix="/anuncios", tags=["Anúncios"])

_ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif"}
_MAX_IMAGE_BYTES = 10 * 1024 * 1024  # 10 MB
_MAX_IMAGES = 3

# Geo constants
_KM_PER_DEGREE_LAT = 111.0  # approximate km per degree of latitude at the equator
_COS_ZERO_GUARD = 1e-6  # prevents division by zero near the poles

_load_options = [
    selectinload(Anuncio.imagens),
    selectinload(Anuncio.categoria),
    selectinload(Anuncio.usuario),
    selectinload(Anuncio.locker),
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


def _get_locker_or_400(locker_id: int, db: Session) -> Locker:
    locker = db.query(Locker).filter(Locker.id == locker_id, Locker.ativo.is_(True)).first()
    if locker is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Locker inválido ou inativo.")
    return locker


def _validar_autorizacao_fluxo_locker(anuncio: Anuncio, current_user: Usuario) -> None:
    if anuncio.usuario_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")
    if anuncio.tipo not in (TipoAnuncio.doacao, TipoAnuncio.ambos):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Fluxo de locker disponível apenas para anúncios de doação.",
        )
    if anuncio.locker is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Anúncio não está associado a locker.",
        )


def _mock_resposta_gateway_locker(acao: LockerEventoAcao, locker: Locker, anuncio_id: int) -> dict:
    return {
        "mock": True,
        "command_id": f"{acao.value}-{anuncio_id}-{locker.id}",
        "locker_id": locker.id,
        "codigo_unidade": locker.codigo_unidade,
        "state": "accepted",
    }


def _registrar_evento_locker(
    *,
    db: Session,
    anuncio: Anuncio,
    acao: LockerEventoAcao,
    sucesso: bool,
    detalhe: str,
) -> LockerEvento:
    if anuncio.locker_id is None:
        raise ValueError("Anúncio sem locker associado para registrar evento.")
    evento = LockerEvento(
        anuncio_id=anuncio.id,
        locker_id=anuncio.locker_id,
        acao=acao,
        sucesso=sucesso,
        detalhe=detalhe,
    )
    db.add(evento)
    db.flush()
    return evento


def _save_image(file: UploadFile) -> tuple[str, str]:
    """Valida, salva e retorna (url_relativa, content_type)."""
    if file.content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Formato não suportado: '{file.content_type}'. Use JPEG, PNG ou GIF.",
        )
    data = file.file.read()
    if not data:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de imagem vazio.",
        )
    if len(data) > _MAX_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE,
            detail="Arquivo excede o limite de 10 MB.",
        )
    ext_map = {"image/jpeg": ".jpg", "image/png": ".png", "image/gif": ".gif"}
    filename = f"{uuid4().hex}{ext_map[file.content_type]}"
    (ANUNCIO_IMAGES_DIR / filename).write_bytes(data)
    return f"/uploads/anuncios/{filename}", file.content_type


@router.get("/", response_model=List[AnuncioListResponse], summary="Buscar e listar anúncios")
async def listar_anuncios(
    q: Optional[str] = Query(None, description="Busca por título ou descrição"),
    categoria_id: Optional[int] = Query(None),
    tipo: Optional[str] = Query(None, description="doacao | troca"),
    cep: Optional[str] = Query(None, description="Filtrar por CEP"),
    raio_km: Optional[float] = Query(None, ge=0.1, le=500, description="Raio de busca em km (requer cep com coordenadas)"),
    status: Optional[str] = Query(None, description="disponivel | reservado | doado_trocado"),
    ordenar: Optional[str] = Query("recente", description="recente | antigo | proximo"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db),
):
    """
    Lista anúncios com suporte a busca por palavra-chave, filtragem por categoria,
    tipo, CEP e status. Anúncios concluídos são ocultados por padrão (RF04, RF06.2).

    Parâmetros de geolocalização (RF04.3, RF04.4, RNF03):
    - ``cep``: CEP de referência para filtro por proximidade (com ou sem hífen).
    - ``raio_km``: Raio máximo em km. O CEP de busca é geocodificado diretamente,
      e todos os anúncios com coordenadas dentro do raio são retornados.
    - ``ordenar=proximo``: Ordena os resultados pela distância ao CEP fornecido.
    """
    query = db.query(Anuncio).options(*_load_options)

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

    # ── Geolocalização (RF04.3, RF04.4) ──────────────────────────────────────
    ref_lat: Optional[float] = None
    ref_lon: Optional[float] = None

    if cep:
        cep_digits = cep.replace("-", "").strip()
        # Geocodificar se há raio ou ordenação por proximidade
        if raio_km is not None or ordenar == "proximo":
            ref_lat, ref_lon = await geocode_cep(cep_digits)
        
        if raio_km is not None:
            if ref_lat is not None and ref_lon is not None:
                # Bounding-box pre-filter: ±delta graus ao redor do ponto de referência.
                # 1 grau de latitude ≈ 111 km; longitude varia com cosseno da latitude.
                delta_lat = raio_km / _KM_PER_DEGREE_LAT
                delta_lon = raio_km / (
                    _KM_PER_DEGREE_LAT * max(math.cos(math.radians(ref_lat)), _COS_ZERO_GUARD)
                )
                query = query.filter(
                    Anuncio.latitude.isnot(None),
                    Anuncio.longitude.isnot(None),
                    Anuncio.latitude.between(ref_lat - delta_lat, ref_lat + delta_lat),
                    Anuncio.longitude.between(ref_lon - delta_lon, ref_lon + delta_lon),
                )
            else:
                # Se não conseguir geocodificar o CEP, fallback: filtrar por prefixo de CEP
                query = query.filter(Anuncio.cep.ilike(f"{cep_digits[:5]}%"))
        else:
            # Sem raio_km: apenas filtro por prefixo de CEP
            query = query.filter(Anuncio.cep.ilike(f"{cep_digits[:5]}%"))

    if ordenar == "antigo":
        query = query.order_by(Anuncio.criado_em.asc())
    elif ordenar == "proximo" and ref_lat is not None and ref_lon is not None:
        # Ordenação por proximidade: busca todos os candidatos e ordena em memória
        candidates = query.all()
        candidates.sort(
            key=lambda a: haversine_km(ref_lat, ref_lon, a.latitude, a.longitude)
            if a.latitude is not None and a.longitude is not None
            else float("inf")
        )
        return candidates[offset: offset + limit]
    else:
        query = query.order_by(Anuncio.criado_em.desc())

    return query.offset(offset).limit(limit).all()


@router.get("/{anuncio_id}", response_model=AnuncioResponse, summary="Detalhe do anúncio")
def buscar_anuncio(anuncio_id: int, db: Session = Depends(get_db)):
    """Retorna todos os detalhes de um anúncio pelo ID."""
    return _get_anuncio_or_404(anuncio_id, db)


@router.post("/", response_model=AnuncioResponse, status_code=status.HTTP_201_CREATED, summary="Criar anúncio")
async def criar_anuncio(
    titulo: str = Form(..., min_length=3, max_length=200),
    descricao: str = Form(..., min_length=10),
    tipo: TipoAnuncio = Form(...),
    condicao: CondicaoItem = Form(...),
    categoria_id: Optional[int] = Form(None),
    localizacao: Optional[str] = Form(None, max_length=255),
    cep: Optional[str] = Form(None, max_length=9),
    locker_id: Optional[int] = Form(None),
    imagens: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Cria um novo anúncio de doação ou troca (RF03). Aceita até 3 imagens (JPEG, PNG, GIF)."""
    valid_files = [f for f in imagens if f.filename]
    if len(valid_files) > _MAX_IMAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Máximo de {_MAX_IMAGES} imagens por anúncio.",
        )

    lat, lon = await geocode_cep(cep) if cep else (None, None)
    if locker_id is not None:
        _get_locker_or_400(locker_id, db)

    anuncio = Anuncio(
        titulo=titulo,
        descricao=descricao,
        tipo=tipo,
        condicao=condicao,
        categoria_id=categoria_id,
        localizacao=localizacao,
        cep=cep,
        locker_id=locker_id,
        latitude=lat,
        longitude=lon,
        usuario_id=current_user.id,
    )
    db.add(anuncio)
    db.flush()

    for i, file in enumerate(valid_files):
        url, content_type = _save_image(file)
        db.add(AnuncioImagem(anuncio_id=anuncio.id, url=url, content_type=content_type, ordem=i))

    db.add(StatusHistorico(anuncio_id=anuncio.id, status_novo=StatusAnuncio.disponivel))
    db.commit()
    return _get_anuncio_or_404(anuncio.id, db)


@router.put("/{anuncio_id}", response_model=AnuncioResponse, summary="Editar anúncio")
async def atualizar_anuncio(
    anuncio_id: int,
    titulo: Optional[str] = Form(None, min_length=3, max_length=200),
    descricao: Optional[str] = Form(None, min_length=10),
    tipo: Optional[TipoAnuncio] = Form(None),
    condicao: Optional[CondicaoItem] = Form(None),
    categoria_id: Optional[int] = Form(None),
    localizacao: Optional[str] = Form(None, max_length=255),
    cep: Optional[str] = Form(None, max_length=9),
    locker_id: Optional[int] = Form(None),
    imagens: List[UploadFile] = File(default=[]),
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Edita um anúncio existente. Apenas o dono pode editar (RF03.4).
    Se novas imagens forem enviadas, substituem todas as anteriores."""
    anuncio = _get_anuncio_or_404(anuncio_id, db)
    if anuncio.usuario_id != current_user.id and not current_user.is_admin:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Sem permissão")

    # Captura o CEP atual antes de aplicar as alterações, para detectar mudança
    cep_anterior = (anuncio.cep or "").replace("-", "").strip()

    fields = {
        "titulo": titulo,
        "tipo": tipo,
        "descricao": descricao,
        "condicao": condicao,
        "categoria_id": categoria_id,
        "localizacao": localizacao,
        "cep": cep,
        "locker_id": locker_id,
    }
    if locker_id is not None:
        _get_locker_or_400(locker_id, db)
    for field, value in fields.items():
        if value is not None:
            setattr(anuncio, field, value)

    # Re-geocodificar se o CEP foi alterado (normaliza ambos para comparação sem hífen)
    if cep is not None:
        cep_novo = cep.replace("-", "").strip()
        if cep_novo != cep_anterior:
            lat, lon = await geocode_cep(cep)
            anuncio.latitude = lat
            anuncio.longitude = lon

    valid_files = [f for f in imagens if f.filename]
    if len(valid_files) > _MAX_IMAGES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Máximo de {_MAX_IMAGES} imagens por anúncio.",
        )

    if valid_files:
        existing = db.query(AnuncioImagem).filter(AnuncioImagem.anuncio_id == anuncio_id).all()
        delete_image_files(existing)
        db.query(AnuncioImagem).filter(AnuncioImagem.anuncio_id == anuncio_id).delete()
        for i, file in enumerate(valid_files):
            url, content_type = _save_image(file)
            db.add(AnuncioImagem(anuncio_id=anuncio_id, url=url, content_type=content_type, ordem=i))

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


@router.post("/{anuncio_id}/locker/abrir", response_model=LockerAcaoResponse, summary="Solicitar abertura do locker")
def abrir_locker(
    anuncio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    anuncio = _get_anuncio_or_404(anuncio_id, db)
    _validar_autorizacao_fluxo_locker(anuncio, current_user)
    locker = anuncio.locker
    if locker is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anúncio não está associado a locker.")
    if anuncio.status == StatusAnuncio.doado_trocado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anúncio já concluído.")

    try:
        enviar_comando_abertura(locker, anuncio.id)
    except NotImplementedError:
        gateway = _mock_resposta_gateway_locker(LockerEventoAcao.abrir, locker, anuncio.id)
    except Exception:
        _registrar_evento_locker(
            db=db,
            anuncio=anuncio,
            acao=LockerEventoAcao.abrir,
            sucesso=False,
            detalhe="Falha ao solicitar abertura no gateway.",
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível solicitar abertura do locker.",
        ) from None

    if not gateway.get("command_id") or not gateway.get("state"):
        _registrar_evento_locker(
            db=db,
            anuncio=anuncio,
            acao=LockerEventoAcao.abrir,
            sucesso=False,
            detalhe="Resposta inválida do gateway.",
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resposta inválida do gateway do locker.",
        )

    evento = _registrar_evento_locker(
        db=db,
        anuncio=anuncio,
        acao=LockerEventoAcao.abrir,
        sucesso=True,
        detalhe=json.dumps(gateway, ensure_ascii=False),
    )
    db.commit()
    return LockerAcaoResponse(
        evento_id=evento.id,
        acao=LockerEventoAcao.abrir.value,
        sucesso=True,
        detalhe="Locker autorizado para abertura.",
        gateway=gateway,
    )


@router.post("/{anuncio_id}/locker/fechar", response_model=LockerAcaoResponse, summary="Solicitar fechamento do locker")
def fechar_locker(
    anuncio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    anuncio = _get_anuncio_or_404(anuncio_id, db)
    _validar_autorizacao_fluxo_locker(anuncio, current_user)
    locker = anuncio.locker
    if locker is None:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anúncio não está associado a locker.")
    if anuncio.status == StatusAnuncio.doado_trocado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anúncio já concluído.")

    try:
        enviar_comando_fechamento(locker, anuncio.id)
    except NotImplementedError:
        gateway = _mock_resposta_gateway_locker(LockerEventoAcao.fechar, locker, anuncio.id)
    except Exception:
        _registrar_evento_locker(
            db=db,
            anuncio=anuncio,
            acao=LockerEventoAcao.fechar,
            sucesso=False,
            detalhe="Falha ao solicitar fechamento no gateway.",
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Não foi possível solicitar fechamento do locker.",
        ) from None

    if not gateway.get("command_id") or not gateway.get("state"):
        _registrar_evento_locker(
            db=db,
            anuncio=anuncio,
            acao=LockerEventoAcao.fechar,
            sucesso=False,
            detalhe="Resposta inválida do gateway.",
        )
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_502_BAD_GATEWAY,
            detail="Resposta inválida do gateway do locker.",
        )

    evento = _registrar_evento_locker(
        db=db,
        anuncio=anuncio,
        acao=LockerEventoAcao.fechar,
        sucesso=True,
        detalhe=json.dumps(gateway, ensure_ascii=False),
    )
    db.commit()
    return LockerAcaoResponse(
        evento_id=evento.id,
        acao=LockerEventoAcao.fechar.value,
        sucesso=True,
        detalhe="Locker autorizado para fechamento.",
        gateway=gateway,
    )


@router.post(
    "/{anuncio_id}/locker/concluir",
    response_model=AnuncioResponse,
    summary="Concluir doação física via locker",
)
def concluir_doacao_via_locker(
    anuncio_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    anuncio = _get_anuncio_or_404(anuncio_id, db)
    _validar_autorizacao_fluxo_locker(anuncio, current_user)
    if anuncio.status == StatusAnuncio.doado_trocado:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Anúncio já concluído.")

    evento_fechamento = (
        db.query(LockerEvento)
        .filter(
            LockerEvento.anuncio_id == anuncio.id,
            LockerEvento.acao == LockerEventoAcao.fechar,
            LockerEvento.sucesso.is_(True),
        )
        .order_by(LockerEvento.criado_em.desc())
        .first()
    )
    if evento_fechamento is None:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="É necessário fechar o locker antes de concluir a doação.",
        )

    db.add(
        StatusHistorico(
            anuncio_id=anuncio_id,
            status_anterior=anuncio.status,
            status_novo=StatusAnuncio.doado_trocado,
        )
    )
    anuncio.status = StatusAnuncio.doado_trocado
    _registrar_evento_locker(
        db=db,
        anuncio=anuncio,
        acao=LockerEventoAcao.concluir_doacao,
        sucesso=True,
        detalhe="Doação concluída após confirmação de fechamento.",
    )
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
    delete_image_files(anuncio.imagens)
    db.delete(anuncio)
    db.commit()
