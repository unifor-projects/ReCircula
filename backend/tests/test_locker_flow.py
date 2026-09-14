from unittest.mock import patch

from app.models.anuncio import Anuncio, CondicaoItem, StatusAnuncio, TipoAnuncio
from app.models.locker import Locker, LockerEvento, LockerEventoAcao
from app.models.usuario import Usuario


def _register_and_get_token(client, email: str) -> str:
    with patch("app.routers.auth.send_verification_email") as mock_send:
        resp = client.post(
            "/auth/registrar",
            json={
                "nome": "Locker User",
                "email": email,
                "senha": "senha123",
            },
        )
    assert resp.status_code == 201
    token_plain = mock_send.call_args.kwargs["token"]
    client.post("/auth/verify-email", json={"token": token_plain})
    login = client.post("/auth/login", data={"username": email, "password": "senha123"})
    assert login.status_code == 200
    return login.json()["access_token"]


def _make_locker(db_session, code: str = "UNI01") -> Locker:
    locker = Locker(
        unidade="Unifor 01",
        codigo_unidade=code,
        numero="1321",
        logradouro="Av. Washington Soares",
        cidade="Fortaleza",
        estado="CE",
        pais="Brasil",
        cep="60811-905",
        ativo=True,
    )
    db_session.add(locker)
    db_session.commit()
    db_session.refresh(locker)
    return locker


def _make_anuncio(db_session, usuario_id: int, locker_id: int) -> Anuncio:
    anuncio = Anuncio(
        titulo="Cadeira",
        descricao="Descrição suficientemente longa para o anúncio.",
        tipo=TipoAnuncio.doacao,
        condicao=CondicaoItem.usado,
        status=StatusAnuncio.disponivel,
        usuario_id=usuario_id,
        locker_id=locker_id,
    )
    db_session.add(anuncio)
    db_session.commit()
    db_session.refresh(anuncio)
    return anuncio


def test_criar_anuncio_com_locker_retorna_locker_associado(client, db_session):
    token = _register_and_get_token(client, "locker-create@example.com")
    locker = _make_locker(db_session)

    resp = client.post(
        "/anuncios/",
        data={
            "titulo": "Notebook para doação",
            "descricao": "Notebook funcionando, com marcas de uso.",
            "tipo": "doacao",
            "condicao": "usado",
            "locker_id": str(locker.id),
        },
        headers={"Authorization": "Bearer " + token},
    )

    assert resp.status_code == 201
    payload = resp.json()
    assert payload["locker_id"] == locker.id
    assert payload["locker"]["codigo_unidade"] == "UNI01"


def test_abrir_e_fechar_locker_registra_eventos(client, db_session):
    token = _register_and_get_token(client, "locker-flow@example.com")
    user = db_session.query(Usuario).filter(Usuario.email == "locker-flow@example.com").first()
    assert user is not None

    locker = _make_locker(db_session, code="UNI02")
    anuncio = _make_anuncio(db_session, user.id, locker.id)

    abrir = client.post(
        f"/anuncios/{anuncio.id}/locker/abrir",
        headers={"Authorization": "Bearer " + token},
    )
    fechar = client.post(
        f"/anuncios/{anuncio.id}/locker/fechar",
        headers={"Authorization": "Bearer " + token},
    )

    assert abrir.status_code == 200
    assert fechar.status_code == 200
    assert abrir.json()["sucesso"] is True
    assert fechar.json()["sucesso"] is True

    eventos = db_session.query(LockerEvento).filter(LockerEvento.anuncio_id == anuncio.id).all()
    acoes = {evento.acao for evento in eventos}
    assert LockerEventoAcao.abrir in acoes
    assert LockerEventoAcao.fechar in acoes


def test_concluir_doacao_exige_fechamento_antes(client, db_session):
    token = _register_and_get_token(client, "locker-conclude@example.com")
    user = db_session.query(Usuario).filter(Usuario.email == "locker-conclude@example.com").first()
    assert user is not None

    locker = _make_locker(db_session, code="UNI03")
    anuncio = _make_anuncio(db_session, user.id, locker.id)

    sem_fechar = client.post(
        f"/anuncios/{anuncio.id}/locker/concluir",
        headers={"Authorization": "Bearer " + token},
    )
    assert sem_fechar.status_code == 409

    client.post(f"/anuncios/{anuncio.id}/locker/fechar", headers={"Authorization": "Bearer " + token})
    concluir = client.post(
        f"/anuncios/{anuncio.id}/locker/concluir",
        headers={"Authorization": "Bearer " + token},
    )
    assert concluir.status_code == 200
    assert concluir.json()["status"] == "doado_trocado"
