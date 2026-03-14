# Recicula – Backend

Backend da plataforma **Recicula**, construído com [FastAPI](https://fastapi.tiangolo.com/) e documentação Swagger integrada.

## Requisitos

- Python 3.11+

## Instalação

```bash
cd backend
python -m venv .venv
source .venv/bin/activate   # Windows: .venv\Scripts\activate
pip install -r requirements.txt
```

## Executar

```bash
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```

## Documentação

Após iniciar o servidor, acesse:

| Interface | URL |
|-----------|-----|
| Swagger UI | http://localhost:8000/docs |
| ReDoc | http://localhost:8000/redoc |
| OpenAPI JSON | http://localhost:8000/openapi.json |

## Endpoints disponíveis

| Recurso | Prefixo |
|---------|---------|
| Usuários | `/usuarios` |
| Pontos de Coleta | `/pontos-coleta` |
| Materiais | `/materiais` |

Cada recurso expõe operações de **CRUD** completo (GET, POST, PUT, DELETE).
