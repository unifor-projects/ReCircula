import secrets

from fastapi import APIRouter, Header, HTTPException, status
from fastapi.responses import PlainTextResponse

from app.config import settings
from app.services.locker_control import retirar_comando

router = APIRouter(prefix="/lockers", tags=["Lockers (dispositivo)"])


@router.get(
    "/{codigo_unidade}/comando",
    response_class=PlainTextResponse,
    summary="ESP32 busca o próximo comando (ABRIR, FECHAR ou vazio)",
)
def proximo_comando(codigo_unidade: str, x_locker_token: str = Header(default="")) -> str:
    # Texto puro para o ESP32 não precisar de biblioteca de JSON
    if not settings.LOCKER_DEVICE_TOKEN:
        raise HTTPException(status_code=status.HTTP_503_SERVICE_UNAVAILABLE, detail="LOCKER_DEVICE_TOKEN não configurado.")
    if not secrets.compare_digest(x_locker_token, settings.LOCKER_DEVICE_TOKEN):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Token do locker inválido.")
    return retirar_comando(codigo_unidade)
