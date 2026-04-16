from io import BytesIO
from pathlib import Path
from unittest.mock import patch

from PIL import Image

from app.routers.usuarios import _MAX_PROFILE_IMAGE_BYTES, PROFILE_IMAGES_DIR


REGISTER_URL = "/auth/registrar"
LOGIN_URL = "/auth/login"
VERIFY_EMAIL_URL = "/auth/verify-email"


def _registrar_verificar_e_logar(client, nome: str, email: str, senha: str) -> tuple[int, str]:
    with patch("app.routers.auth.send_verification_email") as mock_send:
        registro = client.post(REGISTER_URL, json={"nome": nome, "email": email, "senha": senha})
    assert registro.status_code == 201
    token_verificacao = mock_send.call_args.kwargs["token"]
    verificar = client.post(VERIFY_EMAIL_URL, json={"token": token_verificacao})
    assert verificar.status_code == 200
    login = client.post(LOGIN_URL, data={"username": email, "password": senha})
    assert login.status_code == 200
    return registro.json()["usuario"]["id"], login.json()["access_token"]


def _headers(token: str) -> dict[str, str]:
    return {"Authorization": f"Bearer {token}"}


def _png_bytes(color: tuple[int, int, int] = (0, 120, 255)) -> bytes:
    image = Image.new("RGB", (32, 32), color)
    output = BytesIO()
    image.save(output, format="PNG")
    return output.getvalue()


def test_get_usuario_por_id_retorna_perfil_publico_e_anuncios(client):
    usuario_id, token = _registrar_verificar_e_logar(
        client, "Usuário Perfil", "perfil@example.com", "senha123"
    )
    anuncio_payload = {
        "titulo": "Cadeira infantil",
        "descricao": "Cadeira em bom estado para doação",
        "tipo": "doacao",
        "condicao": "usado",
        "imagens": [],
    }
    criar_anuncio = client.post("/anuncios/", json=anuncio_payload, headers=_headers(token))
    assert criar_anuncio.status_code == 201
    anuncio_id = criar_anuncio.json()["id"]

    concluir_anuncio = client.patch(
        f"/anuncios/{anuncio_id}/status",
        json={"status": "doado_trocado"},
        headers=_headers(token),
    )
    assert concluir_anuncio.status_code == 200

    atualizar_perfil = client.patch(
        "/usuarios/me",
        data={"bio": "Pai de duas crianças", "localizacao": "Fortaleza"},
        headers=_headers(token),
    )
    assert atualizar_perfil.status_code == 200

    resposta = client.get(f"/usuarios/{usuario_id}")
    assert resposta.status_code == 200
    body = resposta.json()
    assert body["nome"] == "Usuário Perfil"
    assert body["bio"] == "Pai de duas crianças"
    assert body["localizacao"] == "Fortaleza"
    assert isinstance(body["anuncios_publicados"], list)
    assert body["anuncios_publicados"] == []


def test_patch_usuarios_me_atualiza_foto_bio_e_localizacao(client):
    usuario_id, token = _registrar_verificar_e_logar(
        client, "Usuário Foto", "foto@example.com", "senha123"
    )
    resposta = client.patch(
        "/usuarios/me",
        data={"bio": "Bio atualizada", "localizacao": "Aldeota"},
        files={"foto": ("perfil.png", _png_bytes(), "image/png")},
        headers=_headers(token),
    )

    assert resposta.status_code == 200
    body = resposta.json()
    assert body["bio"] == "Bio atualizada"
    assert body["localizacao"] == "Aldeota"
    assert body["foto_url"].startswith("http://testserver/uploads/perfis/")

    perfil_publico = client.get(f"/usuarios/{usuario_id}")
    assert perfil_publico.status_code == 200
    assert perfil_publico.json()["foto_url"] == body["foto_url"]


def test_patch_usuarios_me_rejeita_formato_invalido_de_foto(client):
    _, token = _registrar_verificar_e_logar(client, "Usuário GIF", "gif@example.com", "senha123")
    resposta = client.patch(
        "/usuarios/me",
        files={"foto": ("perfil.gif", b"GIF89a", "image/gif")},
        headers=_headers(token),
    )

    assert resposta.status_code == 400
    assert "JPG ou PNG" in resposta.json()["detail"]


def test_patch_usuarios_me_atualiza_apenas_usuario_autenticado(client):
    usuario1_id, token1 = _registrar_verificar_e_logar(
        client, "Usuário Um", "um@example.com", "senha123"
    )
    _, token2 = _registrar_verificar_e_logar(client, "Usuário Dois", "dois@example.com", "senha123")

    atualizar_usuario1 = client.patch(
        "/usuarios/me",
        data={"bio": "bio-um"},
        headers=_headers(token1),
    )
    assert atualizar_usuario1.status_code == 200

    atualizar_usuario2 = client.patch(
        "/usuarios/me",
        data={"bio": "bio-dois"},
        headers=_headers(token2),
    )
    assert atualizar_usuario2.status_code == 200

    perfil_usuario1 = client.get(f"/usuarios/{usuario1_id}")
    assert perfil_usuario1.status_code == 200
    assert perfil_usuario1.json()["bio"] == "bio-um"


def test_patch_usuarios_me_rejeita_formato_real_invalido(client):
    _, token = _registrar_verificar_e_logar(client, "Usuário BMP", "bmp@example.com", "senha123")
    image = Image.new("RGB", (16, 16), (255, 0, 0))
    output = BytesIO()
    image.save(output, format="BMP")
    resposta = client.patch(
        "/usuarios/me",
        files={"foto": ("perfil.png", output.getvalue(), "image/png")},
        headers=_headers(token),
    )

    assert resposta.status_code == 400
    assert "JPG ou PNG" in resposta.json()["detail"]


def test_patch_usuarios_me_rejeita_arquivo_acima_do_limite(client):
    _, token = _registrar_verificar_e_logar(client, "Usuário Grande", "grande@example.com", "senha123")
    resposta = client.patch(
        "/usuarios/me",
        files={"foto": ("perfil.png", b"0" * (_MAX_PROFILE_IMAGE_BYTES + 1), "image/png")},
        headers=_headers(token),
    )

    assert resposta.status_code == 413


def test_patch_usuarios_me_mantem_foto_antiga_se_upload_falhar(client):
    usuario_id, token = _registrar_verificar_e_logar(
        client, "Usuário Foto Antiga", "fotoantiga@example.com", "senha123"
    )
    primeiro_upload = client.patch(
        "/usuarios/me",
        files={"foto": ("perfil.png", _png_bytes(), "image/png")},
        headers=_headers(token),
    )
    assert primeiro_upload.status_code == 200
    foto_url_antiga = primeiro_upload.json()["foto_url"]

    falha_upload = client.patch(
        "/usuarios/me",
        files={"foto": ("perfil.gif", b"GIF89a", "image/gif")},
        headers=_headers(token),
    )
    assert falha_upload.status_code == 400

    perfil_publico = client.get(f"/usuarios/{usuario_id}")
    assert perfil_publico.status_code == 200
    assert perfil_publico.json()["foto_url"] == foto_url_antiga

    file_name = Path(foto_url_antiga).name
    assert (PROFILE_IMAGES_DIR / file_name).exists()
