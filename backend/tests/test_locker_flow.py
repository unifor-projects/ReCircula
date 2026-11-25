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
    assert concluir.json()["doado_via_locker"] is True

    # Depois de doado, o dono ainda pode abrir o locker e o anúncio continua em "Meus anúncios"
    reabrir = client.post(f"/anuncios/{anuncio.id}/locker/abrir", headers={"Authorization": "Bearer " + token})
    assert reabrir.status_code == 200
    perfil = client.get(f"/usuarios/{user.id}?incluir_concluidos=true").json()
    assert [(a["id"], a["doado_via_locker"]) for a in perfil["anuncios_publicados"]] == [(anuncio.id, True)]
    listagem = client.get("/anuncios/").json()
    assert [(a["id"], a["doado_via_locker"]) for a in listagem] == [(anuncio.id, True)]
    assert [a["id"] for a in client.get("/anuncios/?status=doado_no_locker").json()] == [anuncio.id]


def test_listagem_oculta_concluido_fora_do_locker(client, db_session):
    token = _register_and_get_token(client, "locker-manual@example.com")
    user = db_session.query(Usuario).filter(Usuario.email == "locker-manual@example.com").first()
    anuncio = _make_anuncio(db_session, user.id, _make_locker(db_session, code="UNI04").id)
    client.patch(f"/anuncios/{anuncio.id}/status", json={"status": "doado_trocado"}, headers={"Authorization": "Bearer " + token})
    assert client.get("/anuncios/").json() == []
    assert client.get("/anuncios/?status=doado_no_locker").json() == []


def test_outro_usuario_abre_locker_mas_nao_conclui(client, db_session):
    _register_and_get_token(client, "locker-dono@example.com")
    dono = db_session.query(Usuario).filter(Usuario.email == "locker-dono@example.com").first()
    anuncio = _make_anuncio(db_session, dono.id, _make_locker(db_session, code="UNI05").id)
    outro = {"Authorization": "Bearer " + _register_and_get_token(client, "locker-outro@example.com")}

    assert client.post(f"/anuncios/{anuncio.id}/locker/abrir", headers=outro).status_code == 200
    assert client.post(f"/anuncios/{anuncio.id}/locker/fechar", headers=outro).status_code == 200
    assert client.post(f"/anuncios/{anuncio.id}/locker/concluir", headers=outro).status_code == 403
    assert client.post(f"/anuncios/{anuncio.id}/locker/abrir").status_code == 401


def test_esp32_busca_comando_pelo_wifi(client, db_session, monkeypatch):
    from app.config import settings

    monkeypatch.setattr(settings, "LOCKER_DEVICE_TOKEN", "segredo-do-locker")
    token = _register_and_get_token(client, "locker-wifi@example.com")
    user = db_session.query(Usuario).filter(Usuario.email == "locker-wifi@example.com").first()
    anuncio = _make_anuncio(db_session, user.id, _make_locker(db_session, code="UNI06").id)
    esp32 = {"X-Locker-Token": "segredo-do-locker"}

    assert client.get("/lockers/UNI06/comando", headers=esp32).text == ""
    client.post(f"/anuncios/{anuncio.id}/locker/abrir", headers={"Authorization": "Bearer " + token})
    assert client.get("/lockers/UNI06/comando", headers=esp32).text == "ABRIR"
    # entregue uma vez só
    assert client.get("/lockers/UNI06/comando", headers=esp32).text == ""
    assert client.get("/lockers/UNI06/comando", headers={"X-Locker-Token": "errado"}).status_code == 401


def test_comando_antigo_expira(monkeypatch):
    from app.services import locker_control

    locker = Locker(codigo_unidade="UNI07")
    locker_control.enviar_comando_fechamento(locker, 1)
    agora = locker_control.time.monotonic()
    monkeypatch.setattr(locker_control.time, "monotonic", lambda: agora + locker_control.VALIDADE_COMANDO_S + 1)
    assert locker_control.retirar_comando("UNI07") == ""
