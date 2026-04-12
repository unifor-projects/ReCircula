"""Basic tests for POST /auth/registrar and POST /auth/login."""
from datetime import datetime, timedelta, timezone
from unittest.mock import patch

from app.core.security import hash_password, verify_password
from app.models.usuario import Usuario


REGISTER_URL = "/auth/registrar"
LOGIN_URL = "/auth/login"
LOGOUT_URL = "/auth/logout"
REFRESH_URL = "/auth/refresh"
VERIFY_EMAIL_URL = "/auth/verificar-email"
FORGOT_PASSWORD_URL = "/auth/forgot-password"
RESET_PASSWORD_URL = "/auth/reset-password"

VALID_PAYLOAD = {
    "nome": "João Silva",
    "email": "joao@example.com",
    "senha": "senha123",
}


# ---------------------------------------------------------------------------
# POST /auth/registrar
# ---------------------------------------------------------------------------

class TestRegistrar:
    def test_registro_bem_sucedido_retorna_201(self, client):
        """Deve criar o usuário e retornar HTTP 201."""
        with patch("app.routers.auth.send_verification_email"):
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        assert resp.status_code == 201

    def test_registro_retorna_token_jwt(self, client):
        """A resposta deve conter access_token e token_type."""
        with patch("app.routers.auth.send_verification_email"):
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_registro_retorna_dados_usuario(self, client):
        """A resposta deve conter o objeto usuario com id, nome e email."""
        with patch("app.routers.auth.send_verification_email"):
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        data = resp.json()
        usuario = data["usuario"]
        assert usuario["nome"] == VALID_PAYLOAD["nome"]
        assert usuario["email"] == VALID_PAYLOAD["email"]
        assert "id" in usuario

    def test_senha_nao_retornada_na_resposta(self, client):
        """A senha (hash) nunca deve aparecer na resposta."""
        with patch("app.routers.auth.send_verification_email"):
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        body = resp.text
        assert "senha" not in body
        assert VALID_PAYLOAD["senha"] not in body

    def test_email_duplicado_retorna_409(self, client):
        """Tentar registrar com e-mail já cadastrado deve retornar 409."""
        with patch("app.routers.auth.send_verification_email"):
            client.post(REGISTER_URL, json=VALID_PAYLOAD)
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        assert resp.status_code == 409
        assert "já cadastrado" in resp.json()["detail"]

    def test_campo_nome_obrigatorio(self, client):
        """Sem nome deve retornar 422."""
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "nome"}
        resp = client.post(REGISTER_URL, json=payload)
        assert resp.status_code == 422

    def test_campo_email_obrigatorio(self, client):
        """Sem e-mail deve retornar 422."""
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "email"}
        resp = client.post(REGISTER_URL, json=payload)
        assert resp.status_code == 422

    def test_campo_senha_obrigatorio(self, client):
        """Sem senha deve retornar 422."""
        payload = {k: v for k, v in VALID_PAYLOAD.items() if k != "senha"}
        resp = client.post(REGISTER_URL, json=payload)
        assert resp.status_code == 422

    def test_email_invalido_retorna_422(self, client):
        """E-mail com formato inválido deve retornar 422."""
        payload = {**VALID_PAYLOAD, "email": "nao-e-um-email"}
        resp = client.post(REGISTER_URL, json=payload)
        assert resp.status_code == 422

    def test_nome_muito_curto_retorna_422(self, client):
        """Nome com menos de 2 caracteres deve retornar 422."""
        payload = {**VALID_PAYLOAD, "nome": "A"}
        resp = client.post(REGISTER_URL, json=payload)
        assert resp.status_code == 422

    def test_senha_muito_curta_retorna_422(self, client):
        """Senha com menos de 6 caracteres deve retornar 422."""
        payload = {**VALID_PAYLOAD, "senha": "123"}
        resp = client.post(REGISTER_URL, json=payload)
        assert resp.status_code == 422

    def test_email_verificado_false_apos_cadastro(self, client):
        """Recém-cadastrado não deve ter e-mail verificado."""
        with patch("app.routers.auth.send_verification_email"):
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        assert resp.json()["usuario"]["email_verificado"] is False

    def test_verificacao_email_agendada(self, client):
        """O envio do e-mail de verificação deve ser chamado como background task."""
        with patch("app.routers.auth.send_verification_email") as mock_send:
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        assert resp.status_code == 201
        mock_send.assert_called_once()
        call_kwargs = mock_send.call_args
        assert call_kwargs.kwargs["destinatario"] == VALID_PAYLOAD["email"]
        assert call_kwargs.kwargs["nome"] == VALID_PAYLOAD["nome"]
        assert call_kwargs.kwargs["token"]  # token must be a non-empty string

    def test_token_de_verificacao_salvo_como_hash(self, client, db_session):
        """O token de verificação persistido deve estar hasheado no banco."""
        with patch("app.routers.auth.send_verification_email") as mock_send:
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)

        assert resp.status_code == 201
        token_plain = mock_send.call_args.kwargs["token"]

        usuario = db_session.query(Usuario).filter(Usuario.email == VALID_PAYLOAD["email"]).first()
        assert usuario is not None
        assert usuario.token_verificacao is not None
        assert usuario.token_verificacao != token_plain
        assert verify_password(token_plain, usuario.token_verificacao)


class TestVerificarEmail:
    def _register_and_get_token(self, client):
        with patch("app.routers.auth.send_verification_email") as mock_send:
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        assert resp.status_code == 201
        return mock_send.call_args.kwargs["token"]

    def test_verificar_email_token_valido(self, client):
        """Token válido deve marcar o e-mail como verificado."""
        token = self._register_and_get_token(client)

        resp = client.post(VERIFY_EMAIL_URL, json={"token": token})

        assert resp.status_code == 200
        assert "sucesso" in resp.json()["detail"].lower()

    def test_verificar_email_token_invalido(self, client):
        """Token inválido deve retornar erro 400."""
        self._register_and_get_token(client)

        resp = client.post(VERIFY_EMAIL_URL, json={"token": "token-invalido"})

        assert resp.status_code == 400
        assert "inválido" in resp.json()["detail"].lower()

    def test_token_nao_pode_ser_reutilizado(self, client):
        """Após verificação com sucesso, o mesmo token não deve funcionar novamente."""
        token = self._register_and_get_token(client)

        primeira = client.post(VERIFY_EMAIL_URL, json={"token": token})
        segunda = client.post(VERIFY_EMAIL_URL, json={"token": token})

        assert primeira.status_code == 200
        assert segunda.status_code == 400


# ---------------------------------------------------------------------------
# POST /auth/login
# ---------------------------------------------------------------------------

class TestLogin:
    def _register_and_verify(self, client):
        with patch("app.routers.auth.send_verification_email") as mock_send:
            client.post(REGISTER_URL, json=VALID_PAYLOAD)
        token = mock_send.call_args.kwargs["token"]
        client.post(VERIFY_EMAIL_URL, json={"token": token})

    def test_login_bem_sucedido(self, client):
        """Login com credenciais corretas deve retornar token."""
        self._register_and_verify(client)
        resp = client.post(
            LOGIN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["senha"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert "refresh_token" in data
        assert data["token_type"] == "bearer"

    def test_login_senha_errada_retorna_401(self, client):
        """Login com senha errada deve retornar 401."""
        self._register_and_verify(client)
        resp = client.post(
            LOGIN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": "errada"},
        )
        assert resp.status_code == 401

    def test_login_email_nao_verificado_retorna_403(self, client):
        """Login deve falhar enquanto o e-mail não for verificado."""
        with patch("app.routers.auth.send_verification_email"):
            client.post(REGISTER_URL, json=VALID_PAYLOAD)

        resp = client.post(
            LOGIN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["senha"]},
        )

        assert resp.status_code == 403
        assert "não verificado" in resp.json()["detail"].lower()

    def test_login_email_inexistente_retorna_401(self, client):
        """Login com e-mail não cadastrado deve retornar 401."""
        resp = client.post(
            LOGIN_URL,
            data={"username": "naoexiste@example.com", "password": "qualquer"},
        )
        assert resp.status_code == 401

    def test_refresh_retorna_novo_access_token(self, client):
        """POST /auth/refresh deve renovar o access token usando refresh válido."""
        self._register_and_verify(client)
        login_resp = client.post(
            LOGIN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["senha"]},
        )
        refresh_token = login_resp.json()["refresh_token"]

        resp = client.post(REFRESH_URL, json={"refresh_token": refresh_token})
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_logout_invalida_refresh_token(self, client):
        """Após logout, refresh token anterior não deve mais funcionar."""
        self._register_and_verify(client)
        login_resp = client.post(
            LOGIN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["senha"]},
        )
        refresh_token = login_resp.json()["refresh_token"]

        logout_resp = client.post(LOGOUT_URL, json={"refresh_token": refresh_token})
        assert logout_resp.status_code == 200

        refresh_resp = client.post(REFRESH_URL, json={"refresh_token": refresh_token})
        assert refresh_resp.status_code == 401


class TestRecuperacaoSenha:
    def _register_and_verify(self, client):
        with patch("app.routers.auth.send_verification_email") as mock_send:
            resp = client.post(REGISTER_URL, json=VALID_PAYLOAD)
        assert resp.status_code == 201
        token = mock_send.call_args.kwargs["token"]
        verify_resp = client.post(VERIFY_EMAIL_URL, json={"token": token})
        assert verify_resp.status_code == 200

    def test_forgot_password_gera_token_e_envia_email(self, client, db_session):
        self._register_and_verify(client)

        with patch("app.routers.auth.send_password_reset_email") as mock_send:
            resp = client.post(FORGOT_PASSWORD_URL, json={"email": VALID_PAYLOAD["email"]})

        assert resp.status_code == 200
        mock_send.assert_called_once()
        token_enviado = mock_send.call_args.kwargs["token"]
        token_plain = token_enviado.split(".", 1)[1]

        usuario = db_session.query(Usuario).filter(Usuario.email == VALID_PAYLOAD["email"]).first()
        assert usuario is not None
        assert usuario.token_reset_senha is not None
        assert usuario.token_reset_senha != token_plain
        assert verify_password(token_plain, usuario.token_reset_senha)
        assert usuario.token_reset_expira_em is not None

    def test_forgot_password_email_inexistente_retorna_200(self, client):
        with patch("app.routers.auth.send_password_reset_email") as mock_send:
            resp = client.post(FORGOT_PASSWORD_URL, json={"email": "inexistente@example.com"})

        assert resp.status_code == 200
        mock_send.assert_not_called()

    def test_reset_password_com_token_valido_altera_senha(self, client, db_session):
        self._register_and_verify(client)
        with patch("app.routers.auth.send_password_reset_email") as mock_send:
            forgot_resp = client.post(FORGOT_PASSWORD_URL, json={"email": VALID_PAYLOAD["email"]})
        assert forgot_resp.status_code == 200
        token = mock_send.call_args.kwargs["token"]

        nova_senha = "novaSenha123"
        reset_resp = client.post(
            RESET_PASSWORD_URL,
            json={"token": token, "nova_senha": nova_senha},
        )
        assert reset_resp.status_code == 200
        usuario = db_session.query(Usuario).filter(Usuario.email == VALID_PAYLOAD["email"]).first()
        assert usuario is not None
        assert usuario.senha_hash != nova_senha
        assert verify_password(nova_senha, usuario.senha_hash)
        assert usuario.token_reset_senha is None
        assert usuario.token_reset_expira_em is None

        login_antigo = client.post(
            LOGIN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["senha"]},
        )
        login_novo = client.post(
            LOGIN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": nova_senha},
        )
        assert login_antigo.status_code == 401
        assert login_novo.status_code == 200

    def test_reset_password_token_expirado_retorna_400(self, client, db_session):
        self._register_and_verify(client)

        usuario = db_session.query(Usuario).filter(Usuario.email == VALID_PAYLOAD["email"]).first()
        assert usuario is not None
        token_bruto = "token-expirado-de-redefinicao"
        token = f"{usuario.id}.{token_bruto}"
        usuario.token_reset_senha = hash_password(token_bruto)
        usuario.token_reset_expira_em = datetime.now(timezone.utc) - timedelta(minutes=1)
        db_session.commit()

        resp = client.post(
            RESET_PASSWORD_URL,
            json={"token": token, "nova_senha": "novaSenha123"},
        )
        assert resp.status_code == 400
        assert "inválido ou expirado" in resp.json()["detail"].lower()
