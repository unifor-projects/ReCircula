from unittest.mock import patch

from app.models.denuncia import Denuncia, StatusDenuncia
from app.models.usuario import Usuario


REGISTER_URL = "/auth/registrar"
VERIFY_EMAIL_URL = "/auth/verify-email"
LOGIN_URL = "/auth/login"
DENUNCIAS_URL = "/denuncias/"


def _registrar_verificar_e_logar(
    client,
    db_session,
    nome: str,
    email: str,
    senha: str = "senha123",
    *,
    admin: bool = False,
) -> tuple[int, str]:
    with patch("app.routers.auth.send_verification_email") as mock_send:
        registro = client.post(REGISTER_URL, json={"nome": nome, "email": email, "senha": senha})
    assert registro.status_code == 201

    token_verificacao = mock_send.call_args.kwargs["token"]
    verificar = client.post(VERIFY_EMAIL_URL, json={"token": token_verificacao})
    assert verificar.status_code == 200

    user_id = registro.json()["usuario"]["id"]
    if admin:
        usuario = db_session.get(Usuario, user_id)
        usuario.is_admin = True
        db_session.commit()

    login = client.post(LOGIN_URL, data={"username": email, "password": senha})
    assert login.status_code == 200
    return user_id, login.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def test_post_denuncias_cria_denuncia_de_anuncio(client, db_session):
    _, token = _registrar_verificar_e_logar(client, db_session, "Autor", "autor@example.com")

    anuncio = client.post(
        "/anuncios/",
        data={
            "titulo": "Mesa de madeira",
            "descricao": "Mesa para doação em bom estado",
            "tipo": "doacao",
            "condicao": "usado",
        },
        headers=_headers(token),
    )
    assert anuncio.status_code == 201
    anuncio_id = anuncio.json()["id"]

    denunciante_id, denunciante_token = _registrar_verificar_e_logar(
        client, db_session, "Denunciante", "denunciante@example.com"
    )
    resposta = client.post(
        DENUNCIAS_URL,
        json={
            "tipo": "anuncio",
            "alvo_id": anuncio_id,
            "motivo": "Conteúdo impróprio no anúncio",
            "descricao": "Detalhes da denúncia",
        },
        headers=_headers(denunciante_token),
    )

    assert resposta.status_code == 201
    body = resposta.json()
    assert body["anuncio_id"] == anuncio_id
    assert body["usuario_denunciado_id"] is None
    assert body["denunciante_id"] == denunciante_id
    assert body["status"] == "pendente"


def test_post_denuncias_cria_denuncia_de_usuario(client, db_session):
    alvo_id, _ = _registrar_verificar_e_logar(client, db_session, "Alvo", "alvo@example.com")
    _, denunciante_token = _registrar_verificar_e_logar(
        client, db_session, "Denunciante", "den2@example.com"
    )

    resposta = client.post(
        DENUNCIAS_URL,
        json={
            "tipo": "usuario",
            "alvo_id": alvo_id,
            "motivo": "Comportamento inadequado",
            "descricao": "Mensagens ofensivas",
        },
        headers=_headers(denunciante_token),
    )

    assert resposta.status_code == 201
    body = resposta.json()
    assert body["usuario_denunciado_id"] == alvo_id
    assert body["anuncio_id"] is None
    assert body["status"] == "pendente"


def test_post_denuncias_exige_autenticacao(client):
    resposta = client.post(
        DENUNCIAS_URL,
        json={
            "tipo": "usuario",
            "alvo_id": 1,
            "motivo": "Motivo válido",
            "descricao": "Descrição",
        },
    )
    assert resposta.status_code == 401


def test_get_denuncias_admin_lista_apenas_pendentes(client, db_session):
    _, admin_token = _registrar_verificar_e_logar(
        client, db_session, "Admin", "admin@example.com", admin=True
    )
    alvo_id, _ = _registrar_verificar_e_logar(client, db_session, "Alvo", "alvo2@example.com")
    _, denunciante_token = _registrar_verificar_e_logar(
        client, db_session, "Denunciante", "den3@example.com"
    )

    criar = client.post(
        DENUNCIAS_URL,
        json={
            "tipo": "usuario",
            "alvo_id": alvo_id,
            "motivo": "Perfil suspeito",
            "descricao": "Descrição inicial",
        },
        headers=_headers(denunciante_token),
    )
    assert criar.status_code == 201
    denuncia_id = criar.json()["id"]

    lista = client.get(DENUNCIAS_URL, headers=_headers(admin_token))
    assert lista.status_code == 200
    ids = [item["id"] for item in lista.json()]
    assert denuncia_id in ids

    denuncia = db_session.get(Denuncia, denuncia_id)
    denuncia.status = StatusDenuncia.resolvida
    db_session.commit()

    lista_atualizada = client.get(DENUNCIAS_URL, headers=_headers(admin_token))
    assert lista_atualizada.status_code == 200
    ids_atualizados = [item["id"] for item in lista_atualizada.json()]
    assert denuncia_id not in ids_atualizados
