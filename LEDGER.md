# LEDGER — registro append-only de mudanças

Uma entrada por mudança aplicada em **skill, contrato, motor, prompt de agente ou processo**. Validação que não muda estado vivo não entra aqui — fica no checkpoint da tarefa.

**Append-only:** correção é **entrada nova** citando a anterior; nunca se reescreve uma entrada existente.

**Schema obrigatório de cada entrada:**

`ID (T-AAAAMMDD-NNN)` · `Escopo` · `Estado anterior` · `Mudança aplicada` · `Aprovação` · `Evidência` · `Rollback` · `Resultado`

Entradas de **não conformidade** (algo saiu do processo) usam o mesmo schema, marcadas `NÃO CONFORMIDADE`, e carregam um campo extra: `Ação corretiva (na fonte)`.

---

## T-20260820-001 · Criação do plugin temcomo v0.1.0

- **Escopo:** repositório inteiro do plugin público `temcomo` — spec, protótipos aprovados, motor, contratos, skills, prompts de agentes e empacotamento para Claude Code, Codex e Hermes.
- **Estado anterior:** não existia. A arte prévia era a skill `/temcomo` compartilhada da frota Hermes (`~/.hermes/shared/skills/workflows/temcomo/`), cobrindo só as etapas 1–3, sem contratos, sem motor e sem registro de tarefa — colisão de nome conhecida, a resolver na adoção (fora do escopo deste repo).
- **Mudança aplicada:** criado o plugin como sistema de gestão da qualidade: skills = procedimentos, contratos JSON versionados `-v1` = formulários, motor Python stdlib determinístico = gate, HTMLs autocontidos = superfície de decisão do usuário, pasta de tarefa = registro. Escopo v1: etapas 1–4 (objetivo → pesquisa → direções → grill); etapas 5–9 no `ROADMAP.md`.
- **Aprovação:** Lucas, por decisões registradas em `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/decisoes.md`:
  - **nº 8** (2026-08-19) — design doc **aprovado 15/15** via HTML de decisões, com o comentário sobre ISO 9001 incorporado (rastreabilidade ponta a ponta + ação corretiva na fonte);
  - **nº 9** (2026-08-19) — exceção pontual e autorizada: Opus assume a lente técnica do conselho visual, com o incidente de crédito do Codex documentado;
  - **nº 10** (2026-08-20) — protótipos v2 validados: direções aprovado; grill aprovado com o ajuste de destaque para decisões difíceis de reverter;
  - **nº 11** (2026-08-20) — **protótipos aprovados em definitivo** ("APROVADO, amei") e promovidos a **contrato visual** dos templates do motor.
- **Evidência:** `docs/especificacoes/2026-08-19-temcomo-design.md` (aprovado 15/15; respostas em `contexto-de-tarefas/.../respostas/review-decisions-v1__*.json`) · protótipos canônicos `Prototypes/01-relatorio-direcoes.html` (sha256 `c7256205…5f61`) e `Prototypes/02-rodada-grill.html` (sha256 `580c20e2…8b8e`) · plano `docs/planos/2026-08-20-temcomo-v1-implementacao.md` (13 tasks) · rastreabilidade de agentes (sessão + JSONL) na tabela do `decisoes.md`.
- **Rollback:** remover o diretório do plugin e desinstalá-lo dos harnesses. Nenhum sistema em produção depende dele; o `/temcomo` antigo da frota continua íntegro e independente. As tarefas já criadas em `.temcomo/tarefas/` são arquivos JSON legíveis sem o plugin.
- **Resultado:** v0.1.0 em construção pelas 13 tasks do plano, em duas lanes paralelas com revisão adversarial task a task. Sem push: publicação depende de aprovação explícita do Lucas (decisão nº 7).

## T-20260820-002 · NÃO CONFORMIDADE — `git add -A` varreu trabalho em voo de outra lane

- **Escopo:** processo de execução em lanes paralelas (árvore principal + worktree `lane-conteudo`) e integridade do histórico do repositório.
- **Estado anterior:** duas lanes escrevendo em paralelo, **sem regra escrita** sobre o que cada uma pode adicionar ao índice. A worktree da Lane Conteúdo não estava no `.gitignore`.
- **Mudança aplicada (o que aconteceu):** em 2026-08-20 o orquestrador rodou `git add -A` na árvore principal para commitar o disparo das lanes. O comando levou junto **arquivos em voo da Lane Motor** (`engine/temcomo.py`, `engine/autoteste_dados/.gitkeep`) e registrou `.claude/worktrees/lane-conteudo` no índice como gitlink. Efeitos: `a7c17ed` ("execução: 2 lanes disparadas…") carrega o esqueleto do CLI que não era dele, e `e230521` ("feat(motor): esqueleto do CLI + harness de autoteste") ficou **só com o checkpoint, sem o CLI** — a mensagem do commit deixou de descrever o conteúdo, quebrando a rastreabilidade que a spec §2.7 exige.
- **Aprovação:** não se aplica — incidente, não mudança planejada. A correção foi conduzida pelo dono do repositório no mesmo dia.
- **Evidência:** `git show --stat a7c17ed` (mostra `engine/temcomo.py`, `.gitkeep` e o gitlink `.claude/worktrees/lane-conteudo`) · `git show --stat e230521` (só `checkpoints/motor-task-01.md`) · `f4fd6f1` ("fix: ignorar worktrees no índice").
- **Ação corretiva (na fonte):**
  1. `.gitignore` passou a conter `.claude/worktrees/`, e o gitlink foi removido do índice (`f4fd6f1`);
  2. regra escrita no `RUNBOOK.md` §8 — **cada lane commita só os seus caminhos** (`git add <caminhos>`), nunca `git add -A` em árvore compartilhada; e a mensagem do commit tem de descrever o que ele realmente contém;
  3. aprendizado registrado no `LEARNINGS.md` (2026-08-20), com destino nomeado.
- **Rollback:** nenhum — histórico é append-only e os commits envolvidos **não** foram reescritos. A rastreabilidade fica reconstituível por esta entrada, que é o registro oficial de onde o código da Task 1 realmente aterrissou.
- **Resultado:** verificável por `git check-ignore .claude/worktrees/lane-conteudo` (ignorado) e `git ls-files .claude/worktrees` (vazio). Nenhuma perda de trabalho; o custo foi de rastreabilidade, agora coberto por este registro e pela regra do RUNBOOK.

## T-20260820-003 · Campo `[SEVERIDADE]` nos prompts de revisão

- **Escopo:** `agents/revisor-adversarial.md` e `agents/avaliador-de-cobertura.md` (contrato de saída dos pareceres) + `RUNBOOK.md` §6 (taxonomia e critério de parada).
- **Estado anterior:** os dois prompts classificavam cada item **só por confiança** (`BAIXA` não reporta · `MÉDIA` → SUGESTÃO · `ALTA` → ACHADO), e o ACHADO de confiança ALTA bloqueava por definição. O RUNBOOK repetia isso como `ACHADO ALTA ≡ P0/P1`.
- **Mudança aplicada:** separados os dois eixos. Cada item passa a trazer `[CONFIANÇA]` **e** `[SEVERIDADE: P0|P1|P2|P3]`: confiança decide se o item é **reportado**, severidade decide se **bloqueia**. A regra de bloqueio passou a ser **"achado de severidade `P0` ou `P1`"** — nos dois prompts (`REQUEST CHANGES` / `NOVA RODADA`) e no critério (b) da parada do RUNBOOK. Motivo: a equivalência anterior fazia nitpick certo bloquear e falha grave de confiança média passar.
- **Aprovação:** **pendente de ratificação do Lucas.** A mudança nasceu de achado de revisão adversarial (parecer da Task 11, rodada 2) e foi aplicada dentro do escopo da Task 11 a pedido do orquestrador da execução — **não há decisão do dono registrada** até aqui. Pela regra do `RUNBOOK.md` §10 (mudança de comportamento em prompt de agente exige aprovação explícita + ledger), esta entrada é o registro provisório: se o Lucas não ratificar, a reversão vira **entrada nova**, nunca reescrita desta.
- **Evidência:** `agents/revisor-adversarial.md` (marcadores do método e formato do veredito) · `agents/avaliador-de-cobertura.md` (idem) · `RUNBOOK.md` §6 "Taxonomia: dois eixos independentes", com a tabela dos eixos, as definições de `P0`–`P3` e a regra de leitura dos pareceres anteriores (ACHADO antigo = `P1`, salvo quando o texto descrever quebra de regra inviolável, segurança ou perda de dado).
- **Rollback:** restaurar os três trechos para a forma de um eixo só (commit `c847e24` e anteriores). Nenhum contrato JSON, schema ou código depende do campo: ele existe no texto do parecer, não no motor — por isso o rollback é textual e sem migração.
- **Resultado:** vereditos históricos permanecem válidos sob a regra de leitura; os prompts seguem em 8 arquivos abaixo do teto de 120 linhas. Sem efeito no motor, nos contratos ou nos HTMLs.

## T-20260820-004 · Ratificação da T-20260820-003 e rollback completo

- **Escopo:** governança da `T-20260820-003` (campo `[SEVERIDADE]` em `agents/revisor-adversarial.md` e `agents/avaliador-de-cobertura.md` + taxonomia do `RUNBOOK.md` §6). Esta entrada **não altera** a T-003 — append-only: ela a **completa e substitui** no que está dito abaixo.
- **Estado anterior:** a T-003 registrava `Aprovação: pendente de ratificação do Lucas` e um campo `Rollback` **incompleto**, que mandava restaurar apenas os trechos de `RUNBOOK.md` e dos dois prompts.
- **Mudança aplicada:** (a) a aprovação da T-003 fica **ratificada**; (b) o rollback da T-003 passa a ser o descrito nesta entrada, cobrindo também os artefatos de governança; (c) a taxonomia recebeu as correções prescritas pela revisão r3 da Task 11 — bloqueio por **item** `P0`/`P1` independentemente do rótulo `ACHADO`/`SUGESTÃO`, `MÉDIA + P0/P1` bloqueando até ser verificado ou disposto, divergência de estilo classificada como `P3` (preservando `ALTA → ACHADO`), e o quarto marcador propagado ao passo operacional do RUNBOOK e às duas seções "Saídas obrigatórias".
- **Aprovação:** **ratificada pelo Lucas em 2026-08-20** (comunicada pelo orquestrador da execução). A T-003, aplicada antes da ratificação, fica assim regularizada; o registro de que ela nasceu pendente permanece lá, como manda o append-only.
- **Evidência:** `LEDGER.md` `T-20260820-003` (entrada original) · `RUNBOOK.md` §6 "Taxonomia: dois eixos independentes" e critério (b) da parada · `agents/revisor-adversarial.md` e `agents/avaliador-de-cobertura.md` (quatro marcadores e vereditos por severidade) · parecer `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/reviews/task-11b-codex-r3.md` (achados 1, 2 e 5).
- **Rollback (substitui o campo `Rollback` da T-003, que estava incompleto):** para desfazer a mudança é preciso, na mesma passagem: (1) restaurar os trechos de `RUNBOOK.md` §6 e dos dois prompts à forma de um eixo só (`c847e24`); (2) abrir **entrada nova** no LEDGER registrando a reversão e citando T-003 e T-004 — nunca reescrevê-las; e (3) marcar a entrada "Confiança e severidade são eixos independentes" do `LEARNINGS.md` como `[SUPERADA <data>]`, para não sobrar aprendizado `promovida` apontando para regra revertida. Nenhum contrato, schema ou código depende do campo: a reversão é textual, sem migração.
- **Resultado:** taxonomia de dois eixos em vigor e ratificada; a cadeia T-003 → T-004 mostra o antes, o depois e quem aprovou. Sem efeito no motor, nos contratos ou nos HTMLs.

## T-20260820-005 · Manifests de empacotamento (Claude Code, Codex, Hermes)

- **Escopo:** `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.hermes-plugin/plugin.yaml` e `.hermes-plugin/INSTALACAO.md`.
- **Estado anterior:** o repositório não era instalável — nenhum manifesto, nenhuma declaração de onde ficam as skills. Cada harness precisaria de instrução manual.
- **Mudança aplicada:** criados os manifestos dos três harnesses, todos com `name: temcomo` e `version: 0.1.0`. Claude Code: `plugin.json` declarando as 4 skills por caminho + `marketplace.json` com `source: "./"` (instalação a partir do próprio clone). Codex: `plugin.json` com `"skills": "./skills/"` e bloco `interface`. Hermes: `plugin.yaml` (formato dos plugins reais do Hermes) declarando `skills`, `agents` e `engine`, mais `INSTALACAO.md` com o procedimento de `skills.external_dirs` (ADR 0001) e o aviso da colisão de nome com o `/temcomo` antigo da frota.
- **Aprovação:** escopo da Task 13 do plano de implementação em execução (decisão 12). **Publicação e instalação continuam exigindo aprovação explícita do Lucas** (decisão 7) — nada foi publicado, nada foi instalado.
- **Evidência:** validação determinística executada na worktree — os 3 JSON parseiam e declaram `temcomo`/`0.1.0`; o YAML parseia; **todos os caminhos declarados existem** (as 4 pastas de skill com seu `SKILL.md`, `./skills/`, `./agents/`, `./engine/temcomo.py`, e o `source: "./"`). Formatos espelhados dos exemplos reais instalados: `~/.claude/plugins/cache/claude-plugins-official/superpowers/6.2.0/.claude-plugin/` e `.codex-plugin/`, o `plugin.json` do `andrej-karpathy-skills` (precedente da chave `skills` no manifesto do Claude Code) e `~/.hermes/plugins/hermes-lcm/plugin.yaml`.
- **Estado de verificação por harness — `não verificável localmente` nos três:** o teste de instalação real muda configuração do usuário (`~/.claude`, `config.yaml` do Hermes, `~/.codex/skills`) e não pode ser feito a partir da worktree da lane. Fica para a