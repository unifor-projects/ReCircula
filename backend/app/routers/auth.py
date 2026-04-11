import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import RegisterResponse, Token, UsuarioCreate, UsuarioResponse
from app.core.security import hash_password, verify_password, create_access_token
from app.services.email import send_verification_email

router = APIRouter(prefix="/auth", tags=["Autenticação"])


@router.post(
    "/registrar",
    response_model=RegisterResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Registrar novo usuário",
)
def registrar(
    usuario: UsuarioCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
):
    """Cria uma nova conta de usuário na plataforma e retorna um token JWT."""
    existente = db.query(Usuario).filter(Usuario.email == usuario.email).first()
    if existente:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="E-mail já cadastrado",
        )
    token_verificacao = secrets.token_urlsafe(32)
    novo = Usuario(
        nome=usuario.nome,
        email=usuario.email,
        senha_hash=hash_password(usuario.senha),
        token_verificacao=hash_password(token_verificacao),
    )
    db.add(novo)
    db.commit()
    db.refresh(novo)

    background_tasks.add_task(
        send_verification_email,
        destinatario=novo.email,
        nome=novo.nome,
        token=token_verificacao,
    )

    access_token = create_access_token({"sub": str(novo.id)})
    return RegisterResponse(
        usuario=UsuarioResponse.model_validate(novo),
        access_token=access_token,
        token_type="bearer",
    )


@router.post("/token", response_model=Token, summary="Login – obter token JWT")
def login(
    form_data: OAuth2PasswordRequestForm = Depends(),
    db: Session = Depends(get_db),
):
    """Autentica o usuário com e-mail e senha, retornando um token JWT Bearer."""
    usuario = db.query(Usuario).filter(Usuario.email == form_data.username).first()
    if not usuario or not verify_password(form_data.password, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )
    token = create_access_token({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer"}
