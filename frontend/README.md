# Plataforma de Doacao e Troca - Frontend

Frontend do projeto ReCircula, construido com Next.js.

## Requisitos

- Node.js 20+
- npm

## Instalacao

```bash
cd frontend
npm install
cp .env.example .env
```

## Variaveis de Ambiente

- O frontend usa `frontend/.env`.
- O arquivo de exemplo e `frontend/.env.example`.

Variavel usada atualmente:

- `NEXT_PUBLIC_API_URL` (URL publica da API consumida no navegador)

## Executar em desenvolvimento

```bash
cd frontend
npm run dev
```

A aplicacao fica disponivel em `http://localhost:3000`.

## Executar com Docker Compose

Na raiz do repositorio:

```bash
docker compose up --build
```

Observacao:

- O serviço `frontend` no Compose carrega `frontend/.env`.
