from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.routers import usuarios, pontos_coleta, materiais

app = FastAPI(
    title="Recicula API",
    description=(
        "API do sistema **Recicula** – plataforma de reciclagem da Unifor.\n\n"
        "Gerencie usuários, pontos de coleta e materiais recicláveis através dos endpoints abaixo.\n\n"
        "A documentação interativa (Swagger UI) está disponível em `/docs` e a documentação "
        "alternativa (ReDoc) em `/redoc`."
    ),
    version="1.0.0",
    contact={
        "name": "Unifor Projects",
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
    allow_origins=["*"],  # Restrict to specific domains in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(usuarios.router)
app.include_router(pontos_coleta.router)
app.include_router(materiais.router)


@app.get("/", tags=["Health"], summary="Health check")
def health_check():
    """Verifica se a API está online."""
    return {"status": "ok", "message": "Recicula API está funcionando!"}
