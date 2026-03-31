from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import settings
from app.routers import auth, usuarios, anuncios, categorias, mensagens, denuncias

app = FastAPI(
    title="Plataforma de Doação e Troca – API",
    description=(
        "API da **Plataforma de Doação e Troca** – sistema para conectar doadores a pessoas "
        "que necessitam de bens, promovendo sustentabilidade e impacto social.\n\n"
        "### Recursos disponíveis\n"
        "- **Autenticação** – cadastro, login JWT e sessão segura\n"
        "- **Usuários** – perfil, foto, localização e histórico de anúncios\n"
        "- **Anúncios** – criação, edição, busca por palavra-chave, categoria e CEP\n"
        "- **Categorias** – classificação dos itens\n"
        "- **Mensagens** – conversas internas entre doador e interessado\n"
        "- **Denúncias** – moderação de conteúdo inadequado\n\n"
        "A documentação interativa (Swagger UI) está disponível em `/docs` e a "
        "alternativa (ReDoc) em `/redoc`."
    ),
    version="1.0.0",
    contact={
        "name": "Unifor Projects – João Guilherme & Mariana Vieira",
        "url": "https://github.com/unifor-projects/Recicula",
    },
    license_info={
        "name": "MIT",
        "url": "https://opensource.org/licenses/MIT",
    },
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(usuarios.router)
app.include_router(anuncios.router)
app.include_router(categorias.router)
app.include_router(mensagens.router)
app.include_router(denuncias.router)


@app.get("/", tags=["Health"], summary="Health check")
def health_check():
    """Verifica se a API está online."""
    return {"status": "ok", "message": "Plataforma de Doação e Troca – API funcionando!"}

