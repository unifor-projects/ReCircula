"""Basic tests for POST /auth/registrar and POST /auth/token."""
from unittest.mock import patch


REGISTER_URL = "/auth/registrar"
TOKEN_URL = "/auth/token"

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


# ---------------------------------------------------------------------------
# POST /auth/token
# ---------------------------------------------------------------------------

class TestLogin:
    def _register(self, client):
        with patch("app.routers.auth.send_verification_email"):
            client.post(REGISTER_URL, json=VALID_PAYLOAD)

    def test_login_bem_sucedido(self, client):
        """Login com credenciais corretas deve retornar token."""
        self._register(client)
        resp = client.post(
            TOKEN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": VALID_PAYLOAD["senha"]},
        )
        assert resp.status_code == 200
        data = resp.json()
        assert "access_token" in data
        assert data["token_type"] == "bearer"

    def test_login_senha_errada_retorna_401(self, client):
        """Login com senha errada deve retornar 401."""
        self._register(client)
        resp = client.post(
            TOKEN_URL,
            data={"username": VALID_PAYLOAD["email"], "password": "errada"},
        )
        assert resp.status_code == 401

    def test_login_email_inexistente_retorna_401(self, client):
        """Login com e-mail não cadastrado deve retornar 401."""
        resp = client.post(
            TOKEN_URL,
            data={"username": "naoexiste@example.com", "password": "qualquer"},
        )
        assert resp.status_code == 401
