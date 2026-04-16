from io import BytesIO
from pathlib import Path
from typing import Annotated
from urllib.parse import urlparse
from uuid import uuid4
import warnings

from fastapi import APIRouter, Depends, File, Form, HTTPException, Request, UploadFile, status
from PIL import Image, ImageOps, UnidentifiedImageError
from sqlalchemy.orm import Session, selectinload

from app.database import get_db
from app.deps import get_current_user
from app.models.anuncio import Anuncio, StatusAnuncio
from app.models.usuario import Usuario
from app.schemas.usuario import (
    UsuarioPerfilAnuncio,
    UsuarioPerfilResponse,
    UsuarioPerfilUpdateResponse,
    UsuarioResponse,
    UsuarioUpdate,
)

router = APIRouter(prefix="/usuarios", tags=["Usuários"])
PROFILE_IMAGES_DIR = Path(__file__).resolve().parents[2] / "uploads" / "perfis"
PROFILE_IMAGES_DIR.mkdir(parents=True, exist_ok=True)
_ALLOWED_IMAGE_TYPES = {"image/jpeg": "JPEG", "image/png": "PNG"}
_ALLOWED_IMAGE_FORMATS = {"JPEG", "PNG"}
_MAX_PROFILE_IMAGE_BYTES = 5 * 1024 * 1024
_MAX_PROFILE_IMAGE_PIXELS = 20_000_000


def _serialize_usuario_perfil(usuario: Usuario, anuncios_publicados: list[Anuncio]) -> UsuarioPerfilResponse:
    return UsuarioPerfilResponse(
        id=usuario.id,
        nome=usuario.nome,
        foto_url=usuario.foto_url,
        localizacao=usuario.localizacao,
        bio=usuario.descricao,
        anuncios_publicados=[
            UsuarioPerfilAnuncio.model_validate(anuncio) for anuncio in anuncios_publicados
        ],
    )


def _delete_profile_image(foto_url: str | None) -> None:
    if not foto_url:
        return
    path = urlparse(foto_url).path
    expected_prefix = "/uploads/perfis/"
    if not path.startswith(expected_prefix):
        return
    base_dir = PROFILE_IMAGES_DIR.resolve()
    image_path = (PROFILE_IMAGES_DIR / path.removeprefix(expected_prefix)).resolve()
    try:
        image_path.relative_to(base_dir)
    except ValueError:
        return
    if image_path.is_file():
        image_path.unlink()


def _compress_and_save_profile_image(foto: UploadFile, request: Request) -> str:
    if foto.content_type not in _ALLOWED_IMAGE_TYPES:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagem inválido. Use JPG ou PNG.",
        )

    image_bytes = foto.file.read()
    if not image_bytes:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Arquivo de imagem vazio.")
    if len(image_bytes) > _MAX_PROFILE_IMAGE_BYTES:
        raise HTTPException(
            status_code=status.HTTP_413_CONTENT_TOO_LARGE,
            detail="Arquivo de imagem excede o tamanho máximo permitido.",
        )

    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            image = Image.open(BytesIO(image_bytes))
            image.load()
    except (UnidentifiedImageError, Image.DecompressionBombError, Image.DecompressionBombWarning) as exc:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Arquivo de imagem inválido.",
        ) from exc

    image_format = (image.format or "").upper()
    if image_format not in _ALLOWED_IMAGE_FORMATS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Formato de imagem inválido. Use JPG ou PNG.",
        )

    width, height = image.size
    if width * height > _MAX_PROFILE_IMAGE_PIXELS:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Dimensões da imagem excedem o limite permitido.",
        )

    image = ImageOps.exif_transpose(image)
    ext = ".jpg" if image_format == "JPEG" else ".png"
    output = BytesIO()

    if ext == ".jpg":
        image = image.convert("RGB")
        image.save(output, format="JPEG", optimize=True, quality=75)
    else:
        if image.mode not in ("RGB", "RGBA"):
            image = image.convert("RGBA")
        image.save(output, format="PNG", optimize=True, compress_level=9)

    file_name = f"{uuid4().hex}{ext}"
    file_path = PROFILE_IMAGES_DIR / file_name
    file_path.write_bytes(output.getvalue())
    return str(request.url_for("uploads", path=f"perfis/{file_name}"))


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


@router.patch("/me", response_model=UsuarioPerfilUpdateResponse, summary="Atualizar meu perfil (foto, bio e localização)")
def atualizar_meu_perfil(
    request: Request,
    foto: UploadFile | None = File(None),
    bio: Annotated[str | None, Form()] = None,
    localizacao: Annotated[str | None, Form(max_length=255)] = None,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user),
):
    """Atualiza dados de perfil do usuário autenticado (RF02.2)."""
    if foto is not None:
        foto_antiga = current_user.foto_url
        nova_foto_url = _compress_and_save_profile_image(foto, request)
        current_user.foto_url = nova_foto_url
        _delete_profile_image(foto_antiga)
    if bio is not None:
        current_user.descricao = bio
    if localizacao is not None:
        current_user.localizacao = localizacao

    db.commit()
    db.refresh(current_user)
    return UsuarioPerfilUpdateResponse(
        id=current_user.id,
        nome=current_user.nome,
        foto_url=current_user.foto_url,
        localizacao=current_user.localizacao,
        bio=current_user.descricao,
    )


@router.get("/{usuario_id}", response_model=UsuarioPerfilResponse, summary="Perfil público de usuário")
def perfil_usuario(usuario_id: int, db: Session = Depends(get_db)):
    """Retorna o perfil público de um usuário com seus anúncios publicados."""
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Usuário não encontrado")
    anuncios_publicados = (
        db.query(Anuncio)
        .options(selectinload(Anuncio.imagens))
        .filter(
            Anuncio.usuario_id == usuario_id,
            Anuncio.status != StatusAnuncio.doado_trocado,
        )
        .order_by(Anuncio.criado_em.desc())
        .all()
    )
    return _serialize_usuario_perfil(usuario, anuncios_publicados)
