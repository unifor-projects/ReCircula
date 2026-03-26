# 📋 Planejamento de Sprints – ReCircula

> Plataforma de Doação e Troca | 4 Sprints × 2 Semanas

---

## Visão Geral

| Sprint | Semanas | Requisitos | Foco |
|--------|---------|------------|------|
| **Sprint 1** | 1–2 | RF01, RF02 | Setup + Autenticação + Perfil |
| **Sprint 2** | 3–4 | RF03, RF04 | Anúncios + Busca e Filtragem |
| **Sprint 3** | 5–6 | RF05, RF06 | Mensagens + Gestão de Status |
| **Sprint 4** | 7–8 | RF07 + Deploy + Artigo | Moderação + Publicação (leve) |

**Stack:** Next.js + TypeScript (Frontend) · FastAPI + PostgreSQL (Backend) · Docker + AWS EC2 (Deploy)

---

## 🏃 Sprint 1 – Semanas 1 e 2
**Tema: Fundação + RF01 (Auth) + RF02 (Perfil)**

### Setup / Infraestrutura
- `[SETUP]` Configurar projeto Next.js com TypeScript *(frontend)*
- `[SETUP]` Configurar Docker Compose (backend + frontend + db) *(devops)*
- `[SETUP]` Configurar GitHub Actions CI/CD básico *(devops)*

### RF01 – Gestão de Usuários
- `[RF01 - BE]` Finalizar e testar endpoint de cadastro (POST /auth/register) *(backend)*
- `[RF01 - BE]` Implementar endpoint de login com JWT (POST /auth/login) *(backend)*
- `[RF01 - BE]` Implementar recuperação de senha por e-mail *(backend)*
- `[RF01 - FE]` Criar páginas de Cadastro e Login *(frontend)*
- `[RF01 - FE]` Implementar contexto de autenticação (JWT no cliente) *(frontend)*

### RF02 – Gestão de Perfil
- `[RF02 - BE]` Implementar endpoints de perfil (GET e PATCH /usuarios/{id}) *(backend)*
- `[RF02 - FE]` Criar página de Perfil e formulário de Edição *(frontend)*

**Total: ~10 issues**

---

## 🏃 Sprint 2 – Semanas 3 e 4
**Tema: RF03 (Anúncios) + RF04 (Busca e Filtragem)**

### RF03 – Criação e Gestão de Anúncios
- `[RF03 - BE]` Implementar CRUD de anúncios (POST, GET, PATCH, DELETE) *(backend)*
- `[RF03 - BE]` Implementar upload de imagens do anúncio (RF03.3 + RNF02) *(backend)*
- `[RF03 - BE]` Gerenciar categorias (Labels) dos anúncios *(backend)*
- `[RF03 - FE]` Criar formulário de criação e edição de anúncio *(frontend)*
- `[RF03 - FE]` Criar página de detalhes do anúncio *(frontend)*

### RF04 – Sistema de Busca e Filtragem
- `[RF04 - BE]` Implementar busca por palavra-chave e filtros de categoria *(backend)*
- `[RF04 - BE]` Integrar geolocalização para filtro por proximidade (RNF03) *(backend)*
- `[RF04 - FE]` Criar página de busca e listagem de anúncios *(frontend)*

**Total: ~8 issues**

---

## 🏃 Sprint 3 – Semanas 5 e 6
**Tema: RF05 (Mensagens) + RF06 (Status dos Itens)**

### RF05 – Sistema de Mensagens Internas
- `[RF05 - BE]` Implementar endpoints do sistema de mensagens *(backend)*
- `[RF05 - BE]` Implementar sistema de notificações de novas mensagens (RF05.3) *(backend)*
- `[RF05 - FE]` Criar interface de chat e listagem de conversas *(frontend)*

### RF06 – Gestão de Status dos Itens
- `[RF06 - BE]` Implementar alteração de status e histórico do anúncio *(backend)*
- `[RF06 - FE]` Criar componente de status e timeline no anúncio *(frontend)*

**Total: ~5 issues**

---

## 🏃 Sprint 4 – Semanas 7 e 8 *(leve)*
**Tema: RF07 (Moderação) + Deploy + Artigo Científico**

### RF07 – Moderação e Denúncia
- `[RF07 - BE]` Implementar endpoint de denúncia de anúncio/usuário *(backend)*
- `[RF07 - BE]` Implementar painel administrativo de moderação *(backend)*
- `[RF07 - FE]` Adicionar botão de denúncia e criar painel admin *(frontend)*

### Deploy
- `[DEPLOY]` Preparar ambiente de produção com Docker Compose *(devops)*
- `[DEPLOY]` Fazer deploy da aplicação na AWS EC2 *(devops)*

### Artigo Científico
- `[ARTIGO]` Escrever introdução, metodologia e resultados do artigo científico *(docs)*

**Total: ~6 issues**

---

## 🏷️ Labels Utilizadas

| Label | Cor | Descrição |
|-------|-----|-----------|
| `sprint-1` | 🔵 | Sprint 1 – Auth & Perfil |
| `sprint-2` | 🟡 | Sprint 2 – Anúncios & Busca |
| `sprint-3` | 🔴 | Sprint 3 – Mensagens & Status |
| `sprint-4` | 🟢 | Sprint 4 – Moderação & Deploy |
| `backend` | 🩷 | Tarefa de Backend (FastAPI) |
| `frontend` | 🩵 | Tarefa de Frontend (Next.js) |
| `devops` | 🔷 | Infraestrutura / CI-CD / Deploy |
| `docs` | ⬜ | Documentação / Artigo |
| `RF01`–`RF07` | 🟨 | Requisito Funcional correspondente |
| `setup` | 🔵 | Configuração inicial |

---

## 🚀 Como criar as issues automaticamente

1. Acesse a aba **Actions** no repositório GitHub
2. Selecione o workflow **"🚀 Criar Issues das Sprints"**
3. Clique em **"Run workflow"**
4. No campo de confirmação, digite `sim` e clique em **"Run workflow"**
5. Aguarde a execução (~2 min) — todas as issues serão criadas automaticamente com labels
6. Acesse **Projects** e adicione as issues ao board como **Todo**

> **Nota:** O workflow cria as issues em ordem sequencial (Sprint 1 → 2 → 3 → 4) para facilitar a organização.
