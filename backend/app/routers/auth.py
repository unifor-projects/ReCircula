import secrets

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, status
from fastapi.security import OAuth2PasswordRequestForm
from sqlalchemy.orm import Session

from app.database import get_db
from app.models.usuario import Usuario
from app.schemas.usuario import (
    EmailVerificationRequest,
    LoginRequest,
    RegisterResponse,
    RefreshRequest,
    Token,
    TokenPair,
    UsuarioCreate,
    UsuarioResponse,
)
from app.core.security import (
    create_access_token,
    create_refresh_token,
    decode_token,
    hash_password,
    verify_password,
)
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


@router.post("/verificar-email", summary="Verificar e-mail")
def verificar_email(
    payload: EmailVerificationRequest,
    db: Session = Depends(get_db),
):
    """Marca o e-mail como verificado a partir de um token válido."""
    usuarios_pendentes = (
        db.query(Usuario)
        .filter(
            Usuario.email_verificado.is_(False),
            Usuario.token_verificacao.is_not(None),
        )
        .all()
    )

    usuario_encontrado = None
    for usuario in usuarios_pendentes:
        try:
            if verify_password(payload.token, usuario.token_verificacao):
                usuario_encontrado = usuario
                break
        except ValueError:
            # Ignora valores legados em formato não BCrypt.
            continue

    if not usuario_encontrado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Token de verificação inválido",
        )

    usuario_encontrado.email_verificado = True
    usuario_encontrado.token_verificacao = None
    db.commit()

    return {"detail": "E-mail verificado com sucesso"}


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
    if not usuario.email_verificado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="E-mail ainda não verificado",
        )
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )
    token = create_access_token({"sub": str(usuario.id)})
    return {"access_token": token, "token_type": "bearer"}


def _authenticate_user(email: str, senha: str, db: Session) -> Usuario:
    usuario = db.query(Usuario).filter(Usuario.email == email).first()
    if not usuario or not verify_password(senha, usuario.senha_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="E-mail ou senha incorretos",
            headers={"WWW-Authenticate": "Bearer"},
        )
    if not usuario.email_verificado:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="E-mail ainda não verificado",
        )
    if not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Conta desativada",
        )
    return usuario


def _build_token_pair(usuario: Usuario) -> TokenPair:
    access_token = create_access_token({"sub": str(usuario.id)})
    refresh_token = create_refresh_token(
        {"sub": str(usuario.id), "token_version": usuario.refresh_token_version}
    )
    return TokenPair(
        access_token=access_token,
        refresh_token=refresh_token,
        token_type="bearer",
    )


@router.post("/login", response_model=TokenPair, summary="Login com e-mail e senha")
def login_json(payload: LoginRequest, db: Session = Depends(get_db)):
    usuario = _authenticate_user(payload.email, payload.senha, db)
    return _build_token_pair(usuario)


@router.post("/refresh", response_model=Token, summary="Renovar access token")
def refresh(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_payload = decode_token(payload.refresh_token)
    if not token_payload or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    user_id = token_payload.get("sub")
    token_version = token_payload.get("token_version")
    if user_id is None or token_version is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    usuario = db.get(Usuario, int(user_id))
    if not usuario or not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )
    if token_version != usuario.refresh_token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    access_token = create_access_token({"sub": str(usuario.id)})
    return Token(access_token=access_token, token_type="bearer")


@router.post("/logout", summary="Logout do usuário")
def logout(payload: RefreshRequest, db: Session = Depends(get_db)):
    token_payload = decode_token(payload.refresh_token)
    if not token_payload or token_payload.get("type") != "refresh":
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    user_id = token_payload.get("sub")
    token_version = token_payload.get("token_version")
    if user_id is None or token_version is None:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    usuario = db.get(Usuario, int(user_id))
    if not usuario or not usuario.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )
    if token_version != usuario.refresh_token_version:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Refresh token inválido",
        )

    usuario.refresh_token_version += 1
    db.commit()
    return {"detail": "Logout realizado com sucesso"}
