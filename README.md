# ReCircula

> **Uma alternativa digital para o fomento da economia circular e sustentabilidade**

ReCircula é uma plataforma digital de doação e troca projetada para promover a sustentabilidade urbana e mitigar o descarte inadequado de bens funcionais. A plataforma conecta doadores a indivíduos em situação de vulnerabilidade social, atuando como um vetor de **logística reversa social** e instrumento ativo de inclusão socioambiental.

Trabalho de Conclusão de Curso — Ciência da Computação, Universidade de Fortaleza (UNIFOR), 2026.  
**Autores:** João Guilherme Sales Epifânio · Mariana Vieira  
**Orientadores:** Dra. Juliana Martins de Oliveira · Me. Ronnison Reges Vidal

---

## Motivação

O descarte prematuro de itens ainda funcionais é um desafio ambiental crítico. A cultura do *fast fashion* produz cerca de 92 milhões de toneladas de resíduos anualmente, e a má gestão de resíduos sólidos urbanos já é responsável por mais de 1,6 bilhão de toneladas de gases de efeito estufa por ano — com projeção de chegar a 2,6 bilhões até 2050. Em paralelo, o contexto brasileiro exibe profundas desigualdades socioeconômicas que excluem parte significativa da população do acesso a bens básicos.

O ReCircula surge como resposta direta a esse cenário: uma infraestrutura tecnológica que aplica os princípios da **Economia Circular**, estendendo o ciclo de vida dos produtos, reduzindo o impacto ambiental e promovendo a democratização do acesso a bens de consumo.

---

## Funcionalidades

### Plataforma Web / Mobile (PWA)

| Módulo | Descrição |
|--------|-----------|
| **Gestão de Usuários** | Cadastro, login, logout, recuperação e redefinição de senha, verificação de e-mail |
| **Perfil** | Foto, descrição pessoal, localização aproximada e histórico de anúncios publicados |
| **Anúncios** | Criação de ofertas de doação ou troca com título, descrição, categoria, condição do item, localização e até 3 fotos |
| **Busca e Filtragem** | Pesquisa por palavra-chave, filtro por categoria, filtragem geográfica por CEP/proximidade e ordenação por data ou distância |
| **Chat Interno** | Mensageria em tempo real (Socket.IO) entre doadores e interessados, com histórico de conversas e notificações |
| **Gestão de Status** | Ciclo de vida do anúncio: `Disponível` → `Reservado` → `Doado/Trocado`; itens concluídos são ocultados automaticamente das buscas |
| **Moderação** | Usuários podem denunciar anúncios ou comportamentos inadequados; administradores analisam denúncias, removem conteúdos e suspendem contas |
| **Painel Admin** | Interface dedicada para gestão de usuários, anúncios e denúncias |
| **PWA** | Instalável como app nativo em dispositivos móveis e desktop, com suporte offline |

### Smart Locker (Protótipo Físico)

O ReCircula integra um sistema de **smart locker** — um armário inteligente físico que serve como ponto de retirada autônomo para doações, eliminando a necessidade de encontro presencial entre doador e receptor.

**Estado atual do protótipo:**
- Um único locker físico, construído em caixa de papelão para apresentação como prova de conceito
- Controlado remotamente pelo app: o doador ou receptor abre e fecha o locker diretamente pela plataforma
- A API já possui a estrutura completa para gerenciar múltiplos lockers e registrar todos os eventos de abertura, fechamento e conclusão de doação
- A integração física (envio do comando real ao hardware) está preparada como stub — pronta para ser conectada ao firmware do dispositivo

**Como funciona o fluxo (planejado):**
1. Doador seleciona um locker disponível ao criar o anúncio
2. Ao confirmar a doação via chat, o doador deposita o item e aciona o fechamento pelo app
3. O receptor recebe notificação e pode abrir o locker remotamente pelo app para retirada
4. O sistema registra o evento de `concluir_doacao`, atualizando o status do anúncio

**Limitações atuais do protótipo:**
- Apenas um locker físico disponível
- Sem gerenciamento de múltiplos lockers (a modelagem de dados suporta, mas não há interface de administração para cadastrar novos lockers — atualmente feito via banco de dados diretamente)
- A integração de hardware (`locker_control.py`) é um stub que retorna uma resposta mock; o fluxo completo funciona para testes mas aguarda conexão real com o firmware
- Abertura e fechamento são as únicas ações acessíveis pelo app; a conclusão de doação via locker (`concluir_doacao`) segue um wizard de 3 etapas na tela do anúncio

---

## Arquitetura

O sistema adota a arquitetura de **4+1 visões** (Kruchten) com separação clara de camadas:

```
┌─────────────────────────────────────────────┐
│           Camada de Apresentação            │
│        Next.js 15 + React 18 (PWA)         │
│   TailwindCSS · Framer Motion · Zustand    │
└────────────────────┬────────────────────────┘
                     │ HTTP/REST + Socket.IO
┌────────────────────▼────────────────────────┐
│          Camada de Controladores            │
│           FastAPI + Socket.IO               │
│        Pydantic · JWT (python-jose)         │
└────────────────────┬────────────────────────┘
                     │
┌────────────────────▼────────────────────────┐
│            Camada de Negócio                │
│  Autenticação · Anúncios · Geocodificação  │
│    Mensageria · Moderação · Locker         │
└────────────────────┬────────────────────────┘
                     │ SQLAlchemy ORM
┌────────────────────▼────────────────────────┐
│           Camada de Persistência            │
│             PostgreSQL 15                   │
│          Migrações com Alembic              │
└─────────────────────────────────────────────┘
```

**Comunicação em tempo real:** Socket.IO para o chat e presença de usuários.  
**Geocodificação:** integração com ViaCEP e Nominatim; distância calculada via fórmula de Haversine.  
**Uploads:** imagens redimensionadas e comprimidas com Pillow, servidas diretamente pelo backend.

---

## Stack Tecnológica

### Frontend
| Tecnologia | Versão | Papel |
|------------|--------|-------|
| Next.js | 15 | Framework React com App Router |
| React | 18 | UI |
| TypeScript | 5 | Tipagem estática |
| TailwindCSS | 3 | Estilização |
| Framer Motion | 12 | Animações |
| Zustand | 5 | Gerenciamento de estado |
| Socket.IO Client | 4 | Chat em tempo real |
| Axios | 1.14 | Requisições HTTP |
| Sonner | 2 | Notificações toast |
| Lucide React | — | Ícones |

### Backend
| Tecnologia | Versão | Papel |
|------------|--------|-------|
| Python | 3.12+ | Linguagem principal |
| FastAPI | ≥0.115 | API REST + ASGI |
| Socket.IO (python-socketio) | — | Comunicação em tempo real |
| SQLAlchemy | ≥2.0 | ORM |
| Alembic | ≥1.13 | Migrações de banco |
| PostgreSQL | 15 | Banco de dados relacional |
| Pydantic | ≥2.7 | Validação de dados |
| python-jose | ≥3.4 | JWT |
| passlib + bcrypt | — | Hash de senhas |
| Pillow | ≥12 | Processamento de imagens |
| httpx | ≥0.27 | Geocodificação (ViaCEP/Nominatim) |
| bleach | — | Sanitização de conteúdo do chat (proteção XSS) |

### Infraestrutura
| Ferramenta | Uso |
|------------|-----|
| Docker + Docker Compose | Orquestração de containers (dev e prod) |
| uv | Gerenciador de pacotes Python (backend) |

---

## Estrutura do Repositório

```
ReCircula/
├── backend/
│   ├── app/
│   │   ├── routers/          # Endpoints REST (auth, anúncios, chat, admin...)
│   │   ├── models/           # Modelos SQLAlchemy (usuário, anúncio, locker...)
│   │   ├── schemas/          # Schemas Pydantic
│   │   ├── services/         # Geocodificação, uploads, e-mail, locker, moderação
│   │   ├── chat/             # Socket.IO server, eventos e presença
│   │   └── core/             # Configurações, segurança, JWT
│   ├── alembic/              # Migrações do banco de dados
│   ├── tests/                # Testes automatizados
│   └── Dockerfile
├── frontend/
│   ├── app/                  # Páginas (App Router do Next.js)
│   │   ├── anuncios/         # Listagem, detalhe, cadastro e meus anúncios
│   │   ├── chat/             # Interface de mensagens
│   │   ├── perfil/           # Perfil do usuário
│   │   ├── admin/            # Painel administrativo
│   │   └── login|register/   # Autenticação
│   ├── components/           # Componentes reutilizáveis (Navbar, chat, modais)
│   ├── services/             # Camada de acesso à API
│   ├── store/                # Zustand stores
│   ├── hooks/                # Custom hooks
│   └── Dockerfile
├── docs/                     # Documentação (arquitetura, sprints, TCC)
├── docker-compose.yml        # Produção
└── docker-compose.override.yml  # Desenvolvimento
```

---

## Pré-requisitos

- [Docker](https://www.docker.com/) e Docker Compose v2+
- Git

Para desenvolvimento local sem Docker:
- Node.js 20+
- Python 3.12+
- PostgreSQL 15+
- [uv](https://github.com/astral-sh/uv)

---

## Como Rodar

### Com Docker (recomendado)

```bash
# Clone o repositório
git clone https://github.com/unifor-projects/ReCircula.git
cd ReCircula
```

```bash
# Configure as variáveis de ambiente
cp backend/.env.example backend/.env
cp frontend/.env.example frontend/.env
# Edite os arquivos .env conforme necessário
```

```bash
# Suba todos os serviços (banco, backend, frontend)
docker compose up --build
```

A plataforma estará disponível em:
- **Frontend:** http://localhost:3000
- **API (docs):** http://localhost:8000/docs
- **Socket.IO:** http://localhost:8000/socket.io

Para desenvolvimento, o `docker-compose.override.yml` já expõe as portas corretas e popula usuários de teste automaticamente (`alice@recircula.dev` / `bruno@recircula.dev`, senha: `senha123`).

### Backend (sem Docker)

```bash
cd backend
uv sync
uv run alembic upgrade head
uv run uvicorn app.asgi:app --reload --port 8000
```

### Frontend (sem Docker)

```bash
cd frontend
npm install
npm run dev
```

---

## Variáveis de Ambiente

### Backend (`backend/.env`)

```env
# Banco de dados
POSTGRES_USER=recircula
POSTGRES_PASSWORD=senha_segura
POSTGRES_DB=recircula
DATABASE_URL=postgresql://recircula:senha_segura@db:5432/recircula

# Segurança
SECRET_KEY=sua_chave_secreta_aqui
ACCESS_TOKEN_EXPIRE_MINUTES=60

# E-mail (para verificação de conta e recuperação de senha)
SMTP_HOST=smtp.example.com
SMTP_PORT=587
SMTP_USER=seu@email.com
SMTP_PASSWORD=senha_do_email
EMAILS_FROM_EMAIL=noreply@recircula.dev

# Seed de desenvolvimento (opcional)
SEED_DEV_USERS=false
SEED_DEV_PASSWORD=senha123
```

### Frontend (`frontend/.env`)

```env
NEXT_PUBLIC_API_URL=http://localhost:8000
NEXT_PUBLIC_SOCKET_URL=http://localhost:8000
```

---

## Testes

```bash
# Backend
cd backend
uv run pytest

# Frontend (lint)
cd frontend
npm run lint
```

---

## Modelo de Dados (Entidades Principais)

| Entidade | Descrição |
|----------|-----------|
| `Usuario` | Conta, perfil, localização e credenciais |
| `Anuncio` | Item disponível para doação ou troca |
| `AnuncioImagem` | Imagens associadas a um anúncio (1–3 por anúncio) |
| `Categoria` | Taxonomia dos itens (eletrônicos, roupas, móveis etc.) |
| `Mensagem` | Mensagem entre dois usuários em um chat |
| `Denuncia` | Relato de comportamento inadequado |
| `DecisaoAdministrativa` | Resolução de uma denúncia pelo admin |
| `StatusHistorico` | Histórico de mudanças de status de um anúncio |
| **`Locker`** | Armário inteligente físico (unidade, localização, status) |
| **`LockerEvento`** | Log de ações sobre um locker: `abrir`, `fechar`, `concluir_doacao` |

---

## Smart Locker — Roadmap

O protótipo atual demonstra a viabilidade do conceito. O roadmap para versões futuras inclui:

- [ ] **Integração de hardware real:** conectar `locker_control.py` ao firmware do dispositivo (ESP32/Raspberry Pi) via MQTT ou HTTP
- [ ] **Gerenciamento de múltiplos lockers:** UI de administração para cadastrar, monitorar e desativar lockers
- [ ] **Mapa de lockers:** exibir lockers disponíveis próximos ao usuário na tela de criação de anúncio
- [ ] **Fila de uso:** controle de qual anúncio está usando qual locker em determinado momento
- [ ] **Notificações push:** alertar receptor quando o item for depositado e o locker estiver pronto para retirada
- [ ] **QR Code:** autenticação física via QR Code para abertura sem app aberto
- [ ] **Monitoramento de saúde:** dashboard com status em tempo real de cada locker

---

## Requisitos Não Funcionais

| Código | Requisito |
|--------|-----------|
| RNF01 | Autenticação via JWT (access + refresh token com rotação); login exige e-mail verificado — conta sem verificação recebe 403 |
| RNF02 | Upload de imagens em JPG/PNG com compressão automática (max 10 MB por imagem, 3 por anúncio) |
| RNF03 | Geolocalização precisa via CEP (ViaCEP) e Nominatim para filtragem por proximidade |
| RNF04 | Interface responsiva (*mobile-first*), acessível em smartphones de entrada e desktops |
| RNF05 | Dados de contato pessoal protegidos; endereço exato só revelado se o usuário optar |
| RNF06 | Busca retorna resultados em < 2 segundos com índices otimizados |

---

## Escopo do Projeto

**O que está incluído:**
- Sistema completo de anúncios de doação e troca
- Chat interno entre doadores e interessados
- Filtragem geográfica por proximidade
- Painel de moderação e denúncias
- Integração com smart locker (protótipo)
- PWA instalável

**O que está fora do escopo:**
- Pagamentos ou transações financeiras
- Intermediação logística (transporte e entrega são combinados pelos usuários)
- Avaliação financeira ou precificação de produtos
- Garantia sobre o estado físico dos itens

---

## Licença

Este projeto está licenciado sob os termos da [LICENSE](LICENSE).

---

## Equipe

| Nome | Matrícula |
|------|-----------|
| João Guilherme Sales Epifânio | 2220309 |
| Mariana Vieira | 2220289 |

**Instituição:** Universidade de Fortaleza — UNIFOR  
**Curso:** Ciência da Computação  
**Período:** 2026
