from app.models.locker import Locker


def enviar_comando_abertura(locker: Locker, anuncio_id: int) -> None:
    raise NotImplementedError("Integração real de abertura de locker ainda não implementada.")


def enviar_comando_fechamento(locker: Locker, anuncio_id: int) -> None:
    raise NotImplementedError("Integração real de fechamento de locker ainda não implementada.")
