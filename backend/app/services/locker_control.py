"""Fila de comandos para os lockers físicos.

O app enfileira ABRIR/FECHAR aqui; o ESP32 do locker consulta
GET /lockers/{codigo}/comando pelo Wi-Fi a cada ~1s e executa o que encontrar.
"""

import time
import uuid

from app.models.locker import Locker

# Comando mais velho que isso é descartado: um locker que volta a ficar online
# não deve abrir sozinho por causa de um clique antigo.
VALIDADE_COMANDO_S = 30

# ponytail: fila em memória (um comando por locker, some se o backend reiniciar);
# vira tabela no banco se houver mais de um processo do backend.
_pendentes: dict[str, tuple[str, float]] = {}


def _enfileirar(locker: Locker, comando: str) -> dict:
    command_id = uuid.uuid4().hex
    _pendentes[locker.codigo_unidade] = (comando, time.monotonic())
    return {
        "command_id": command_id,
        "codigo_unidade": locker.codigo_unidade,
        "comando": comando,
        "state": "pendente",
    }


def enviar_comando_abertura(locker: Locker, anuncio_id: int) -> dict:
    return _enfileirar(locker, "ABRIR")


def enviar_comando_fechamento(locker: Locker, anuncio_id: int) -> dict:
    return _enfileirar(locker, "FECHAR")


def retirar_comando(codigo_unidade: str) -> str:
    """Entrega o comando pendente ao ESP32 (uma vez só) ou "" se não houver."""
    pendente = _pendentes.pop(codigo_unidade, None)
    if pendente is None:
        return ""
    comando, criado_em = pendente
    return comando if time.monotonic() - criado_em <= VALIDADE_COMANDO_S else ""
