# Plano de Testes com Usuários — ReCircula

**Disciplina:** Engenharia de Software — PFI  
**Plataforma:** ReCircula — Plataforma Digital de Doação e Troca  
**Versão avaliada:** MVP (v1.0)  
**Período de execução:** _____/______/2026 a _____/______/2026  
**Responsáveis pela avaliação:** João Guilherme Sales Epifânio · Mariana Vieira

---

## 1. Objetivo dos Testes

Avaliar se a plataforma ReCircula permite que usuários com diferentes perfis tecnológicos consigam, de forma autônoma:

- Cadastrar-se e autenticar-se na plataforma
- Publicar e gerenciar anúncios de doação ou troca
- Encontrar itens disponíveis próximos à sua localização
- Interagir com outros usuários via chat interno
- Denunciar conteúdo inadequado

> **Pergunta central:** O usuário consegue realizar as principais ações da plataforma sem auxílio e com satisfação?

---

## 2. Perfil dos Participantes

### 2.1 Critérios de Seleção

O usuário representativo do ReCircula deve refletir o público-alvo real da plataforma: pessoas que querem doar bens funcionais ou que buscam itens sem custo. Os critérios de seleção são:

| Critério | Descrição |
|----------|-----------|
| Faixa etária | Preferencialmente 18–55 anos |
| Experiência tecnológica | Mínima a moderada (usuário casual de smartphone) |
| Familiaridade com apps de anúncio | Não obrigatório (ex.: nunca usou OLX ou Enjoei) |
| Contexto social | Variado — doadores potenciais e receptores potenciais |
| Acesso à internet | Deve possuir acesso regular via smartphone |

### 2.2 Número de Participantes

**Mínimo recomendado:** 5 participantes  
**Ideal:** 8–10 participantes

> Justificativa: estudos de usabilidade indicam que 5 usuários identificam ~85% dos problemas de interface. Com 8–10 participantes é possível calcular métricas quantitativas com maior confiabilidade e contemplar variações de perfil tecnológico.

### 2.3 Identificação dos Participantes

Os participantes serão identificados por códigos (U01, U02, U03…) em todos os registros, em conformidade com a LGPD. Nenhum nome real será utilizado em relatórios ou publicações.

---

## 3. Critérios de Aceitação

Os critérios abaixo devem ser atendidos para que a plataforma seja considerada validada:

| Métrica | Critério de Aceitação |
|---------|----------------------|
| Taxa de sucesso por tarefa | ≥ 80% dos participantes concluem sem ajuda significativa |
| Tempo médio por tarefa | ≤ 3 minutos por tarefa individual |
| Necessidade de ajuda | ≤ 20% dos participantes precisam de ajuda para concluir |
| Satisfação geral (SUS) | Pontuação ≥ 70 (classificação "Bom") |
| Satisfação média (Likert 1–5) | Média ≥ 4,0 em cada dimensão avaliada |
| Falhas críticas | 0 falhas críticas que impeçam a conclusão de um fluxo principal |

---

## 4. Metodologia de Condução

### 4.1 Formato

- **Presencial** ou **remoto** (via compartilhamento de tela)
- Sessão individual por participante, com duração estimada de **30–45 minutos**
- Um avaliador observa e registra; o participante executa sozinho

### 4.2 Instruções ao Participante

> "Você vai usar a plataforma ReCircula como se fosse seu primeiro acesso. Vou pedir que realize algumas tarefas do dia a dia. Não existe resposta certa ou errada — o que estamos avaliando é o sistema, não você. Por favor, pense em voz alta enquanto navega: diga o que está tentando fazer, o que esperava encontrar e o que está sentindo. Não vou poder te ajudar durante as tarefas, mas anote mentalmente qualquer dificuldade."

### 4.3 Comportamento do Avaliador

- Observar sem interferir durante a execução
- Registrar: erros cometidos, hesitações, cliques errados, caminhos inesperados, pedidos de ajuda e comentários espontâneos
- Intervir **apenas** se o participante ficar completamente bloqueado por mais de 3 minutos, registrando o ocorrido como "necessitou de ajuda significativa"
- Cronometrar cada tarefa

---

## 5. Tarefas de Teste

> As tarefas representam situações reais de uso. Não indique o caminho a seguir — observe se o usuário consegue encontrar sozinho.

---

### T01 — Criar uma conta na plataforma
**Requisito relacionado:** RF01  
**Objetivo:** Verificar se o fluxo de cadastro é compreensível e executável de forma autônoma.

**Descrição da tarefa para o participante:**
> "Você ouviu falar do ReCircula, uma plataforma para doar e receber itens. Você nunca usou antes. Crie uma conta para começar a usar."

**Critérios de sucesso:**
- Preencheu todos os campos obrigatórios
- Concluiu o cadastro sem erros de formulário repetidos
- Chegou à tela de verificação de e-mail ou à página principal

**O que observar:** compreensão dos campos, reação às mensagens de erro, percepção do passo de verificação de e-mail.

---

### T02 — Fazer login e acessar o perfil
**Requisito relacionado:** RF01, RF02  
**Objetivo:** Avaliar facilidade de autenticação e navegação até o perfil.

**Descrição da tarefa para o participante:**
> "Agora que você tem uma conta, entre na plataforma e acesse a sua página de perfil para ver como ela está."

**Critérios de sucesso:**
- Realizou login com sucesso
- Localizou e acessou a tela de perfil

**O que observar:** confusão entre campos de login/cadastro, localização do menu de perfil.

---

### T03 — Publicar um anúncio de doação
**Requisito relacionado:** RF03  
**Objetivo:** Verificar se o usuário consegue criar um anúncio completo (com foto, categoria e localização).

**Descrição da tarefa para o participante:**
> "Você tem um casaco que não usa mais e quer doá-lo. Publique um anúncio na plataforma para que outras pessoas possam pedir esse casaco."

**Critérios de sucesso:**
- Criou um anúncio com título, descrição e categoria
- Adicionou ao menos uma foto
- Selecionou o tipo "Doação"
- Anúncio aparece publicado na plataforma

**O que observar:** localização do botão de criação, compreensão das categorias, facilidade no upload de foto, reação ao campo de localização/CEP.

---

### T04 — Buscar um item próximo à sua localização
**Requisito relacionado:** RF04  
**Objetivo:** Avaliar se o sistema de busca e filtro por proximidade é compreensível.

**Descrição da tarefa para o participante:**
> "Você está procurando um sofá ou móvel que alguém queira doar. Veja se tem alguma coisa disponível próxima a você."

**Critérios de sucesso:**
- Usou a busca ou filtros para encontrar itens
- Aplicou ao menos um filtro (categoria ou proximidade/CEP)
- Visualizou o resultado da busca

**O que observar:** descoberta do campo de busca, compreensão do filtro por CEP/raio, interpretação dos resultados.

---

### T05 — Entrar em contato com o anunciante de um item
**Requisito relacionado:** RF05  
**Objetivo:** Verificar se o usuário consegue iniciar uma conversa a partir de um anúncio.

**Descrição da tarefa para o participante:**
> "Você encontrou um anúncio de um item que te interessa. Entre em contato com quem está doando para combinar a retirada."

**Critérios de sucesso:**
- Encontrou o botão/link de contato na página do anúncio
- Enviou ao menos uma mensagem no chat
- Confirmou que a mensagem foi enviada

**O que observar:** localização do botão de contato, transição para a tela de chat, clareza da interface de mensagens.

---

### T06 — Marcar um anúncio como doado
**Requisito relacionado:** RF06  
**Objetivo:** Avaliar se o fluxo de conclusão de doação é intuitivo.

**Descrição da tarefa para o participante:**
> "A pessoa que queria o casaco veio buscá-lo e você já entregou. Atualize o status do seu anúncio para refletir que a doação foi concluída."

**Pré-condição:** participante deve ter um anúncio publicado (da T03 ou pré-existente).

**Critérios de sucesso:**
- Localizou o anúncio publicado
- Alterou o status para "Doado/Trocado"
- Anúncio desaparece da listagem principal (ou aparece como concluído)

**O que observar:** localização da opção de alterar status, compreensão dos estados disponíveis.

---

### T07 — Denunciar um anúncio inadequado
**Requisito relacionado:** RF07  
**Objetivo:** Verificar se o usuário consegue encontrar e utilizar a função de denúncia.

**Descrição da tarefa para o participante:**
> "Você encontrou um anúncio que parece ser falso ou inadequado para a plataforma. Sinalize esse conteúdo para a equipe de moderação."

**Critérios de sucesso:**
- Localizou a opção de denúncia em um anúncio
- Preencheu e enviou a denúncia

**O que observar:** visibilidade da opção de denúncia, clareza dos motivos disponíveis, feedback após o envio.

---

## 6. Ficha de Observação por Tarefa

> Preencha uma ficha por participante por tarefa.

---

**Participante:** _______ | **Data:** ___/___/2026 | **Tarefa:** T0___

| Campo | Registro |
|-------|---------|
| Concluiu a tarefa? | ( ) Sim, sem ajuda ( ) Sim, com pequena ajuda ( ) Sim, com ajuda significativa ( ) Não concluiu |
| Tempo de execução | _____ min _____ seg |
| Número de tentativas / cliques errados | _______ |
| Pediu ajuda? | ( ) Não ( ) Sim — descrever: |
| Erros cometidos | |
| Caminhos inesperados percorridos | |
| Hesitações / momentos de confusão | |
| Comentários espontâneos do participante | |
| Observações do avaliador | |

---

## 7. Classificação dos Erros

Registre cada problema identificado com o seguinte modelo:

| ID | Tarefa | Descrição do Problema | Tipo | Frequência | Gravidade |
|----|--------|-----------------------|------|------------|-----------|
| E01 | T03 | Usuário não encontrou o botão de adicionar foto | Interface | _/10 | Alta |
| E02 | T04 | Usuário não compreendeu o campo de CEP para filtro de proximidade | Comunicação | _/10 | Média |
| E03 | T06 | Usuário não localizou a opção de alterar status do anúncio | Fluxo | _/10 | Alta |
| ... | ... | ... | ... | ... | ... |

**Tipos de erro:**
- **Interface** — clique em local errado, campo incorreto, hierarquia visual confusa
- **Fluxo** — caminho percorrido incorreto, etapas excessivas, sequência pouco intuitiva
- **Comunicação** — rótulo, ícone ou mensagem não compreendida

**Gravidade:**
- **Alta** — impede a conclusão da tarefa; exige correção imediata
- **Média** — atrapalha mas não impede; gera confusão recorrente
- **Baixa** — incômodo menor; não compromete o fluxo

---

## 8. Tabela de Resultados por Tarefa

| Tarefa | Requisito | Total de Participantes | Concluíram sem ajuda | Concluíram com ajuda | Não concluíram | Taxa de Sucesso | Tempo Médio | Principal Problema |
|--------|-----------|----------------------|---------------------|--------------------|----------------|-----------------|-------------|--------------------|
| T01 — Cadastro | RF01 | | | | | | | |
| T02 — Login e perfil | RF01/RF02 | | | | | | | |
| T03 — Publicar anúncio | RF03 | | | | | | | |
| T04 — Buscar por proximidade | RF04 | | | | | | | |
| T05 — Contato via chat | RF05 | | | | | | | |
| T06 — Marcar como doado | RF06 | | | | | | | |
| T07 — Denunciar conteúdo | RF07 | | | | | | | |

---

## 9. Análise dos Resultados

### 9.1 Modelo de Apresentação dos Resultados

Para cada tarefa, registrar:

```
[T03 — Publicar anúncio de doação]
Taxa de sucesso: X/10 (XX%)
Tempo médio: X min XX seg
Principais dificuldades: ...
Frequência do problema mais grave: X ocorrências — Gravidade: Alta/Média/Baixa
```

### 9.2 Comparativo Antes / Após Correções (se houver reteste)

| Tarefa | Taxa de Sucesso — 1ª sessão | Taxa de Sucesso — Reteste | Evolução |
|--------|-----------------------------|--------------------------|----------|
| T03 | | | |
| T04 | | | |

---

## 10. Limitações do Estudo

- Número de participantes: _______ (indicar se abaixo do ideal)
- Perfil dos participantes: _______ (indicar se houve dificuldade em encontrar o perfil representativo)
- Condições do teste: _______ (presencial / remoto; possíveis interferências)
- Funcionalidades não testadas: Smart Locker (protótipo físico único, integração de hardware ainda não finalizada)

---

## 11. Checklist de Entrega (TCC)

Para a seção de validação no trabalho acadêmico, verifique se estão presentes:

- [ ] Metodologia de teste descrita
- [ ] Perfil dos participantes documentado
- [ ] Tarefas aplicadas listadas com rastreabilidade aos requisitos
- [ ] Métricas e critérios de aceitação definidos previamente
- [ ] Questionário pós-uso aplicado e resultados tabulados
- [ ] Tabela de resultados por tarefa preenchida
- [ ] Problemas identificados com frequência e gravidade
- [ ] Alterações realizadas após os testes documentadas
- [ ] Limitações do estudo descritas
- [ ] Formulários de consentimento coletados e arquivados

---

*Referência metodológica: OLIVEIRA, Juliana Martins de. Teste e Validação de Software com Usuários Finais. UNIFOR, 2026.*
