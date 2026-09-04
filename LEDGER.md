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

SEE_FULL_CONTENT_AT_/workspace/PUSH_NOW.json
