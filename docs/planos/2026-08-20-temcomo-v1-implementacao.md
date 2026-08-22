# temcomo v1 — Plano de Implementação

> **For agentic workers:** REQUIRED SUB-SKILL: Use superpowers:subagent-driven-development (recommended) or superpowers:executing-plans to implement this plan task-by-task. Steps use checkbox (`- [ ]`) syntax for tracking.

**Goal:** Construir o plugin público temcomo v1 (etapas 1–4 do fluxo: objetivo → pesquisa → direções → grill) com motor Python, contratos versionados, templates HTML derivados dos protótipos aprovados, skills, agentes e empacotamento para Hermes/Claude Code/Codex.

**Architecture:** Motor único `engine/temcomo.py` (Python stdlib, determinístico, fail-closed) que valida contratos JSON contra schemas `-v1` e renderiza HTMLs standalone a partir de templates extraídos das sementes dos protótipos aprovados. Skills são procedimentos em texto que só avançam etapa via gates do motor; agentes de orquestração têm prompts próprios em `agents/`; estado por tarefa vive em `.temcomo/tarefas/<slug>-<data>/`.

**Tech Stack:** Python ≥3.9 (stdlib pura — `json`, `argparse`, `hashlib`, `pathlib`, `re`, `datetime`, `unittest`), HTML/CSS/JS vanilla standalone, git.

**Spec:** `docs/especificacoes/2026-08-19-temcomo-design.md` (aprovado 15/15 em 2026-08-19; §8 refinado pelo conselho visual e pelas decisões nº 10–11). Decisões e rastreabilidade: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/decisoes.md`. Sementes obrigatórias: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/seeds/` (build.py + template.html dos dois protótipos, verificadores). Contrato visual: `Prototypes/01-relatorio-direcoes.html` (sha `c7256205…5f61`) e `Prototypes/02-rodada-grill.html` (sha `580c20e2…8b8e`).

## Global Constraints

- Python ≥3.9, **stdlib pura** — nenhum `pip install`, nenhum import fora da biblioteca padrão.
- Todo conteúdo em **PT-BR** (código pode ter identificadores em inglês; strings visíveis e docs em PT-BR). **Exceção formal (decisão 15 do Lucas, 2026-08-20):** o rastro técnico de falha do `autoteste` (texto do interpretador Python e identificadores de `builtins`) permanece no formato original, sempre precedido da linha-rótulo em PT-BR "Detalhe técnico no formato original do Python:".
- **Determinismo do render**: mesmo contrato → mesmos bytes; nenhum `datetime.now()`/aleatório no caminho de render; `gerado_em` vem do contrato ou da ação do usuário no navegador.
- HTMLs **standalone/offline**: zero requests de rede; fontes/logo embutidos; nenhum botão executa nada.
- **Identidade QualiApps byte-preservada**: bloco `:root`, os 8 `@font-face` e o logo base64 dos templates devem ser byte-idênticos aos dos protótipos aprovados.
- Schemas nomeados `-v1`; `anotacoes` obrigatório (aceita `[]`) em `decisao-direcoes-v1` e `grill-respostas-v1`; envelope comum com `produzido_por: {agente, modelo, sessao_id, transcript_jsonl}` (spec §5).
- **Gates bloqueiam**: qualquer falha de validação = exit code ≠ 0 + mensagem acionável nomeando campo e motivo; nunca aviso-e-segue.
- Artefatos gerados carregam **cabeçalho de proveniência** (versão do motor + SHA-256 do contrato de entrada).
- `SKILL.md` com `version:` semver no frontmatter; mudanças registradas no `LEDGER.md` (append-only).
- O motor trata `inicio/fim/prefixo` de âncora de anotação como **dica**; `trecho` é a autoridade (decisões.md, aprendizado 2026-08-20).
- Commits locais livres; **push/publicação só com aprovação explícita do Lucas**.

## Estrutura de arquivos (alvo)

Conforme spec §4, mais os derivados deste plano:

```
engine/temcomo.py             engine/templates/{direcoes,grill}.html.tpl
engine/assets/                contracts/*.schema.json
contracts/exemplos/{validos,invalidos}/*.json
skills/{temcomo,temcomo-pesquisa,temcomo-direcoes,temcomo-grill}/SKILL.md
agents/*.md                   exemplos/tarefa-stay/ (tour)
RUNBOOK.md LEARNINGS.md LEDGER.md ROADMAP.md README.md
.claude-plugin/ .codex-plugin/ .hermes-plugin/
tests → embutidos no autoteste (engine/temcomo.py autoteste + engine/autoteste_dados/)
```

---

### Task 1: Fundação — esqueleto do CLI + harness de autoteste

**Files:**
- Create: `engine/temcomo.py`
- Create: `engine/autoteste_dados/.gitkeep`

**Interfaces:**
- Produces: CLI `python3 engine/temcomo.py <subcomando>` com subcomandos `nova-tarefa|validar|renderizar|importar-resposta|status|autoteste`; constante `ENGINE_VERSION = "0.1.0"`; função `fail(msg) -> SystemExit(1)`; runner `autoteste` baseado em `unittest` que descobre classes `Test*` no próprio arquivo.

- [ ] **Step 1: Escrever o esqueleto com um teste que falha**

```python
#!/usr/bin/env python3
"""temcomo — motor de contratos e relatórios. Python >=3.9, stdlib pura."""
import argparse, sys, unittest

ENGINE_VERSION = "0.1.0"

def fail(msg: str):
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(1)

def cmd_autoteste(_args):
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    res = unittest.TextTestRunner(verbosity=1).run(suite)
    raise SystemExit(0 if res.wasSuccessful() else 1)

def cmd_nao_implementado(_args):
    fail("subcomando ainda não implementado")

class TestFundacao(unittest.TestCase):
    def test_versao_semver(self):
        partes = ENGINE_VERSION.split(".")
        self.assertEqual(len(partes), 3)
        self.assertTrue(all(p.isdigit() for p in partes))
    def test_validar_existe(self):
        self.assertTrue(callable(cmd_validar))  # falha até a Task 3

def main():
    p = argparse.ArgumentParser(prog="temcomo")
    sub = p.add_subparsers(dest="cmd", required=True)
    for nome in ("nova-tarefa", "validar", "renderizar", "importar-resposta", "status", "autoteste"):
        sp = sub.add_parser(nome)
        sp.add_argument("alvo", nargs="?")
        sp.set_defaults(func=cmd_autoteste if nome == "autoteste" else cmd_nao_implementado)
    args = p.parse_args()
    args.func(args)

if __name__ == "__main__":
    main()
```

- [ ] **Step 2: Rodar e confirmar que falha** — `python3 engine/temcomo.py autoteste` → esperado: FAIL (`cmd_validar` não definido).
- [ ] **Step 3: Fazer passar minimamente** — adicionar `def cmd_validar(args): fail("não implementado")` acima da classe de teste.
- [ ] **Step 4: Rodar e confirmar PASS** — `python3 engine/temcomo.py autoteste` → OK (2 testes).
- [ ] **Step 5: Commit** — `git add engine && git commit -m "feat(motor): esqueleto do CLI + harness de autoteste"`

### Task 2: Validador de contratos (subset JSON Schema, stdlib)

**Files:**
- Modify: `engine/temcomo.py`

**Interfaces:**
- Produces: `validar_contra_schema(dado: dict, schema: dict, caminho="$") -> list[str]` (lista de erros "caminho: motivo", vazia = válido). Suporta: `type` (object/array/string/number/integer/boolean/null), `required`, `properties`, `additionalProperties: false`, `items`, `enum`, `minLength`/`maxLength`, `minimum`/`maximum`, `minItems`/`maxItems`, `pattern` (via `re`), `const`.

- [ ] **Step 1: Escrever testes que falham** (adicionar à seção de testes)

```python
class TestValidador(unittest.TestCase):
    S = {"type": "object", "required": ["nome"], "additionalProperties": False,
         "properties": {"nome": {"type": "string", "minLength": 1},
                        "nivel": {"enum": ["a", "b"]},
                        "itens": {"type": "array", "minItems": 1,
                                   "items": {"type": "integer", "minimum": 0}}}}
    def test_valido(self):
        self.assertEqual(validar_contra_schema({"nome": "x", "nivel": "a", "itens": [1]}, self.S), [])
    def test_required(self):
        self.assertIn("$.nome", ";".join(validar_contra_schema({}, self.S)))
    def test_enum_e_extra(self):
        erros = ";".join(validar_contra_schema({"nome": "x", "nivel": "z", "foo": 1}, self.S))
        self.assertIn("$.nivel", erros); self.assertIn("$.foo", erros)
    def test_item_invalido(self):
        self.assertIn("$.itens[0]", ";".join(
            validar_contra_schema({"nome": "x", "itens": [-1]}, self.S)))
```

- [ ] **Step 2: Rodar → FAIL** (`validar_contra_schema` indefinida).
- [ ] **Step 3: Implementar** — função recursiva única (~60 linhas), acumulando erros com caminho JSONPath-like; `type` mapeado para tipos Python (`bool` checado antes de `int`); nunca lançar exceção para dado inválido — sempre lista de erros.
- [ ] **Step 4: Rodar → PASS.**
- [ ] **Step 5: Commit** — `git commit -am "feat(motor): validador de contratos (subset JSON Schema em stdlib)"`

### Task 3: Schemas `-v1` + exemplos + subcomando `validar`

**Files:**
- Create: `contracts/{tarefa,objetivo,pesquisa,direcoes,decisao-direcoes,grill-rodada,grill-respostas,grill-consolidado}-v1.schema.json`
- Create: `contracts/exemplos/validos/*.json` e `contracts/exemplos/invalidos/*.json` (≥1 por schema; os do grill/direções derivam das fixtures aprovadas em `Prototypes/*.fixture.json`)
- Modify: `engine/temcomo.py` (cmd_validar real + registro de schemas)

**Interfaces:**
- Produces: `SCHEMAS: dict[str, Path]` mapeando `schema_version` → arquivo; `carregar_e_validar(caminho) -> dict` (lê JSON, resolve schema por `schema_version`, valida envelope comum + corpo, `fail` com todos os erros); envelope comum obrigatório: `schema_version`, `tarefa_id`, `gerado_em`, `produzido_por{agente,modelo,sessao_id,transcript_jsonl}` (spec §5 — nos exports de navegador `produzido_por` admite `{"agente":"usuario"}`).
- Campos-chave por schema (transcrever da spec §5 e das fixtures aprovadas): `direcoes-v1` limita `direcoes` a `maxItems: 5` com no máximo 1 `fora_da_caixa: true` (checagem extra em código, não no schema); `grill-rodada-v1` exige por pergunta `id`, `pergunta` (`maxLength: 90`), `impacto_curto`, `reversivel`, `botoes`, `opcoes` (1–5, uma `recomendada`), `irreversivel_aviso` quando `reversivel=false`; `grill-respostas-v1` exige `estado ∈ {pendente,aprovada,rejeitada,duvida,adiada}` e `anotacoes` (array, aceita vazio, itens com `id`, `trecho`, `comentario`, `bloco_id`, `ancora_status`).

- [ ] **Step 1: Testes que falham** — `TestSchemas`: para cada arquivo em `contracts/exemplos/validos/`, `carregar_e_validar` retorna dict; para cada um em `invalidos/`, `SystemExit`. Incluir caso: `direcoes` com 2 `fora_da_caixa` → inválido; resposta de grill sem `anotacoes` → inválido.
- [ ] **Step 2: Rodar → FAIL.**
- [ ] **Step 3: Escrever os 8 schemas + exemplos** — derivar os campos do grill/direções por engenharia direta das fixtures aprovadas (`Prototypes/01-relatorio-direcoes.fixture.json`, `Prototypes/02-rodada-grill.fixture.json` — são a autoridade de forma); implementar `cmd_validar`.
- [ ] **Step 4: Rodar → PASS** e conferir na mão: `python3 engine/temcomo.py validar Prototypes/02-rodada-grill.fixture.json` → OK.
- [ ] **Step 5: Commit** — `git commit -am "feat(contratos): schemas -v1 + exemplos + validar"`

### Task 4: `nova-tarefa` + `status` (máquina de estados)

**Files:**
- Modify: `engine/temcomo.py`

**Interfaces:**
- Produces: `cmd_nova_tarefa` cria `.temcomo/tarefas/<slug>-<AAAA-MM-DD>/{tarefa.json,contratos/,html/,respostas/,pesquisas/}` (data via `--data` opcional para teste determinístico; sem `--data`, usa data local — único uso de relógio fora de render); `tarefa.json` schema `tarefa-v1` com `etapa ∈ {criada, objetivo-confirmado, pesquisa-concluida, direcao-escolhida, grill-concluido}` e `historico[]`; `avancar_etapa(pasta, nova_etapa)` interno que **exige** o contrato da etapa validado (ex.: `objetivo-confirmado` exige `contratos/01-objetivo.json` válido) senão `fail`; **`cmd_concluir_etapa(tarefa, etapa)` (decisão 14 do Lucas, 2026-08-20)** — subcomando explícito e auditável `concluir-etapa <tarefa> <etapa>` que valida o contrato exigido e chama `avancar_etapa` (adicionar o subparser em `construir_parser` com gabarito PT-BR); transições fora de ordem ou sem contrato = `fail`; `importar-resposta` (Task 7) continua avançando sozinho quando a resposta do usuário é o gate; `cmd_status` imprime etapa, gates passados, pendências e próxima ação. Teste extra no Step 1: `concluir-etapa` avança com contrato válido, bloqueia sem contrato e bloqueia pulo de etapa.

- [ ] **Step 1: Testes que falham** — `TestTarefa` usando `tempfile.TemporaryDirectory`: criar tarefa; status = "criada"; `avancar_etapa` sem contrato → `SystemExit`; gravar `01-objetivo.json` válido → avanço OK; avanço pulando etapa → `SystemExit`.
- [ ] **Step 2: Rodar → FAIL.** — [ ] **Step 3: Implementar.** — [ ] **Step 4: Rodar → PASS.**
- [ ] **Step 5: Commit** — `git commit -am "feat(motor): nova-tarefa e status com gates por contrato"`

### Task 5: Renderizador de direções (template extraído da semente)

**Files:**
- Create: `engine/templates/direcoes.html.tpl` (derivado de `seeds/direcoes/template.html`)
- Create: `engine/assets/` (tokens/fontes/logo extraídos byte a byte do protótipo aprovado, com cabeçalho de proveniência + SHA no README do diretório)
- Modify: `engine/temcomo.py` (portar a lógica de `seeds/direcoes/build.py` para `render_direcoes(contrato: dict) -> str`)

**Interfaces:**
- Consumes: contrato `direcoes-v1` validado (Task 3).
- Produces: `cmd_renderizar` que infere o tipo pelo `schema_version`, escreve `html/NN-direcoes.html` (numeração sequencial, nunca sobrescreve) com comentário de proveniência `<!-- temcomo engine vX · contrato sha256 <hash> -->`; a faixa "PROTÓTIPO — dados de exemplo" só é emitida quando o contrato tem `exemplo: true`.

**Emenda (decisão 17, 2026-08-20) — restauração de rascunho com anotação incompleta:** o JavaScript do template (na restauração do rascunho, hoje `sanitizeAnnot()` na semente) NÃO preenche campos perdidos com `""` nem exporta anotação incompleta silenciosamente. Se alguma anotação restaurada perdeu `trecho`/âncora: (a) o botão de export fica desabilitado; (b) a página lista cada anotação incompleta com o comentário dela e pergunta, por anotação, "manter ou jogar fora?"; (c) mantida → sai no export com `ancora_status: "orfa"` e `trecho: "(trecho não recuperado do rascunho)"` (marcador literal, export válido no schema); (d) jogada fora → removida (descarte COM autorização do usuário; o sistema nunca descarta sozinho); (e) o export só destrava quando todas foram resolvidas. Este comportamento é delta autorizado sobre o protótipo aprovado — o protótipo em `Prototypes/` fica intocado.

- [ ] **Step 1: Teste que falha (golden estrutural)** — `TestRenderDirecoes`: renderizar `contracts/exemplos/validos/direcoes.json` e afirmar: (a) bloco `:root` byte-idêntico ao de `Prototypes/01-relatorio-direcoes.html` (extração por regex entre `:root {` e o `}` correspondente); (b) mesmos 8 `@font-face`; (c) zero `src=|href=` com `http` (fora `xmlns`); (d) comentário de proveniência presente com sha correto; (e) render 2× → bytes idênticos (determinismo).
- [ ] **Step 2: Rodar → FAIL.**
- [ ] **Step 3: Extrair template + portar build** — `seeds/direcoes/build.py` já separa template e dados; a porta é mecânica: placeholders do template viram `str.replace`/f-strings em `render_direcoes`; escapes HTML de todo dado do contrato via `html.escape`.
- [ ] **Step 4: Rodar → PASS** + inspeção visual: abrir o HTML gerado e comparar lado a lado com o protótipo aprovado.
- [ ] **Step 5: Commit** — `git commit -am "feat(motor): renderizador de direções a partir do template aprovado"`

### Task 6: Renderizador de grill

**Files:**
- Create: `engine/templates/grill.html.tpl` (derivado de `seeds/grill/template.html` — versão com linha salmão + callout de aviso)
- Modify: `engine/temcomo.py` (`render_grill(contrato) -> str`, mesma mecânica da Task 5)

**Interfaces:**
- Consumes: contrato `grill-rodada-v1` validado.
- Produces: `html/NN-grill-rodada-N.html`; mesmas garantias da Task 5 (proveniência, determinismo, identidade byte-preservada, faixa condicionada a `exemplo: true`); callout de irreversibilidade emitido quando `reversivel=false` com `irreversivel_aviso` (fallback: "Difícil voltar atrás: esta decisão não tem como ser desfeita depois — escolha com calma.").

**Emenda (decisão 17, 2026-08-20) — restauração de rascunho com anotação incompleta:** mesma regra da Task 5, repetida aqui por inteiro para leitura isolada: a restauração do rascunho no template do grill NÃO aceita anotação só com `comentario` nem exporta campos `undefined` (que o `JSON.stringify` omitiria). Se alguma anotação restaurada perdeu `trecho`/âncora: (a) export desabilitado; (b) lista das anotações incompletas com pergunta por anotação "manter ou jogar fora?"; (c) mantida → `ancora_status: "orfa"` + `trecho: "(trecho não recuperado do rascunho)"` (marcador literal, export válido no schema); (d) jogada fora → removida com autorização do usuário (o sistema nunca descarta sozinho); (e) export só destrava com todas resolvidas. Delta autorizado sobre o protótipo aprovado — `Prototypes/` fica intocado.

- [ ] **Step 1: Teste que falha** — mesmos asserts da Task 5 sobre `Prototypes/02-rodada-grill.html` + assert do callout único na pergunta irreversível e ausência nos reversíveis.
- [ ] **Step 2: FAIL.** — [ ] **Step 3: Extrair/portar.** — [ ] **Step 4: PASS + inspeção visual.**
- [ ] **Step 5: Commit** — `git commit -am "feat(motor): renderizador de grill (wizard + callout de irreversibilidade)"`

### Task 7: `importar-resposta`

**Files:**
- Modify: `engine/temcomo.py`

**Interfaces:**
- Consumes: exports `decisao-direcoes-v1` / `grill-respostas-v1` (Task 3), pasta de tarefa (Task 4).
- Produces: `cmd_importar_resposta(arquivo, --tarefa)`: valida o export; **recusa** (a) `estado: pendente` em decisão de direções, (b) resposta de rodada ≠ rodada pendente da tarefa, (c) resposta de grill com pergunta faltante em relação ao `grill-rodada` correspondente; grava em `respostas/`, atualiza `tarefa.json` (`direcao-escolhida` ou registra rodada respondida); anotações órfãs (`ancora_status: "orfa"`) são aceitas e preservadas; `inicio/fim/prefixo` nunca são causa de recusa (dica, não autoridade).

- [ ] **Step 1: Testes que falham** — `TestImportar`: fluxo feliz de direções (avança etapa); export pendente → `SystemExit` com mensagem citando "pendente"; rodada errada → `SystemExit`; grill completo → rodada registrada; export com anotação órfã → aceito e preservado byte a byte em `respostas/`.
- [ ] **Step 2: FAIL.** — [ ] **Step 3: Implementar.** — [ ] **Step 4: PASS.**
- [ ] **Step 5: Commit** — `git commit -am "feat(motor): importar-resposta com gates e preservação de anotações"`

### Task 8: `autoteste` completo fail-closed

**Files:**
- Modify: `engine/temcomo.py`
- Create: `engine/autoteste_dados/` (contratos golden + exports de teste usados pelas tasks 3–7, consolidados)

**Interfaces:**
- Produces: `cmd_autoteste` roda TODA a suíte + as checagens estáticas herdadas do parecer técnico (§9) e dos verificadores-semente (`seeds/verify/static_checks.py`, adaptar as regras, não copiar cegamente): zero URL externa nos templates; contrato embutido == fixture quando aplicável; chave de localStorage com namespace `temcomo:`; e a **prova fail-closed**: mutar cópias temporárias dos exemplos válidos (remover campo obrigatório, duplicar fora_da_caixa) e afirmar que a validação REPROVA.

- [ ] **Step 1: Teste que falha** — `TestFailClosed` com as mutações acima (falha porque as checagens estáticas ainda não existem como funções puras chamáveis).
- [ ] **Step 2: FAIL.** — [ ] **Step 3: Implementar checagens como funções + integrar.** — [ ] **Step 4: `python3 engine/temcomo.py autoteste` → tudo PASS (≥25 testes).**
- [ ] **Step 5: Commit** — `git commit -am "feat(motor): autoteste fail-closed completo"`

### Task 9: Prompts dos agentes (`agents/`)

**Files:**
- Create: `agents/{orquestrador-pesquisa,pesquisador-interno,pesquisador-externo,redator-do-brief,orquestrador-grill,entrevistador,avaliador-de-cobertura,revisor-adversarial}.md` *(8 prompts — `redator-do-brief` adicionado por decisão 13 do Lucas, 2026-08-20: orquestrador-pesquisa só verifica; o redator compila o brief; o orquestrador lança auditoria independente da compilação — molde revisor-adversarial, recomendação Codex — em loop até APPROVED)*

**Interfaces:**
- Consumes: spec §6 (papéis, corrente, handoff de 6 campos), decisoes.md (aprendizados: orquestrador lança verificadores; rastreabilidade obrigatória).
- Produces: **8** prompts autocontidos (7 originais + `redator-do-brief`, decisão 13), cada um com: papel e mandato em 1 parágrafo; entradas esperadas (contratos/caminhos); saídas obrigatórias (contrato preenchido + handoff de 6 campos com sessão/JSONL); proibições (orquestrador nunca avalia/executa; produtor nunca lança o próprio revisor; pesquisador trata web como não confiável; ninguém implementa durante pesquisa); para `revisor-adversarial` e `avaliador-de-cobertura`, o prompt-molde "REFUTE, not confirm" com `[EVIDÊNCIA]/[CONFIANÇA]/[JUSTIFICATIVA]` e veredito fechado (`APPROVED | REQUEST CHANGES`, `SUFICIENTE | NOVA RODADA`); para `pesquisador-externo`, o protocolo do catálogo `~/.temcomo/catalogo-de-pesquisas/` (consultar antes, salvar depois, índice com papers/PDF separados).

- [ ] **Step 1:** Escrever os **8** arquivos seguindo o mapa acima (conteúdo real, sem TBD; usar como base os prompts desta própria tarefa registrados nos JSONLs citados no decisoes.md).
- [ ] **Step 2: Verificação objetiva** — `grep -L "6 campos" agents/*.md` vazio; `grep -L "transcript" agents/*.md` vazio; cada arquivo ≤120 linhas.
- [ ] **Step 3: Commit** — `git commit -am "feat(agents): prompts de orquestração por fase"`

### Task 10: Skills (`skills/`)

**Files:**
- Create: `skills/temcomo/SKILL.md`, `skills/temcomo-pesquisa/SKILL.md`, `skills/temcomo-direcoes/SKILL.md`, `skills/temcomo-grill/SKILL.md`

**Interfaces:**
- Consumes: spec §5–§7 (jornada, gates, motor), agents/ (Task 9), CLI real (Tasks 1–8).
- Produces: 4 SKILL.md com frontmatter `name`, `description` (gatilhos claros: "tem como", `/temcomo`), `version: 0.1.0`; cada procedimento referencia comandos reais do motor (`python3 engine/temcomo.py …`) e os agentes de `agents/` pelo nome de arquivo; regras invioláveis transcritas: gate de escolha (nada de instalar/escrever antes da direção escolhida), "orquestrador nunca avalia", "objetivo é a autoridade", rastreabilidade nos handoffs, armadilhas do docx original (não confundir pergunta exploratória com autorização; tabela curta primeiro; ferramentas antes de perguntas factuais).

- [ ] **Step 1:** Escrever as 4 skills (mestre inclui a condução da jornada + gate de evolução apontando para LEARNINGS/LEDGER).
- [ ] **Step 2: Verificação objetiva** — `grep -l "version: 0.1.0" skills/*/SKILL.md` = 4; cada comando de motor citado existe no CLI (conferir com `grep add_parser engine/temcomo.py`).
- [ ] **Step 3: Commit** — `git commit -am "feat(skills): procedimentos das etapas 1-4"`

### Task 11: RUNBOOK + LEARNINGS + LEDGER + ROADMAP

**Files:**
- Create: `RUNBOOK.md`, `LEARNINGS.md`, `LEDGER.md`, `ROADMAP.md`

**Interfaces:**
- Produces: `RUNBOOK.md` = manual da qualidade (jornada com tabela de gates da spec §5; papéis de modelo com degradação explícita; handoff de 6 campos; regra "orquestrador lança verificadores"; verificação em camadas §12; nota da origem localStorage compartilhada em `file://`). `LEARNINGS.md` = formato diário datado + status (`pendente|promovida|superada`) + regra de poda, semeado com as entradas reais de `decisoes.md` (watcher valida payload; assinatura de Codex sem crédito; `close` de dialog stale em headless; âncora trecho-como-autoridade) e `seeds/direcoes/learnings-proposta.md`. `LEDGER.md` = schema `T-AAAAMMDD-NNN · Escopo · Estado anterior · Mudança · Aprovação · Evidência · Rollback · Resultado` + entrada T-…-001 registrando a criação do plugin v0.1.0 com aprovação do Lucas (decisões nº 8–11). `ROADMAP.md` = etapas 5–9 da spec §3 + MCP + verificador Playwright + i18n EN, cada uma com 2–3 linhas de encaixe.

- [ ] **Step 1:** Escrever os 4 arquivos. — [ ] **Step 2:** Conferência: LEDGER com 1 entrada completa; LEARNINGS com ≥5 entradas datadas reais. — [ ] **Step 3: Commit** — `git commit -am "docs: runbook, learnings, ledger e roadmap"`

### Task 12: README + tour de exemplo

**Files:**
- Create: `README.md`, `exemplos/tarefa-stay/` (pasta de tarefa completa, dados marcados `exemplo: true`)

**Interfaces:**
- Consumes: CLI completo (Tasks 1–8).
- Produces: `README.md` PT-BR: o que é (analogia SGQ em 1 parágrafo), instalação nos 3 harnesses (Task 13 fornece os manifests — escrever já os comandos), **tour de 5 minutos** com comandos copiáveis: criar tarefa → validar objetivo → renderizar direções do exemplo → abrir HTML → importar resposta de exemplo → status. `exemplos/tarefa-stay/` = os contratos do cenário Stay (derivados das fixtures aprovadas) + respostas de exemplo.

- [ ] **Step 1:** Montar `exemplos/tarefa-stay/` executando o próprio motor (os comandos do tour devem rodar de verdade).
- [ ] **Step 2:** Escrever o README; **rodar o tour inteiro do zero** numa pasta temporária e colar a saída real no commit message.
- [ ] **Step 3: Commit** — `git commit -am "docs: README com tour executável + tarefa de exemplo"`

### Task 13: Manifests dos 3 harnesses + teste de instalação

**Files:**
- Create: `.claude-plugin/plugin.json`, `.claude-plugin/marketplace.json`, `.codex-plugin/plugin.json`, `.hermes-plugin/` (formato conforme o exemplo instalado do superpowers: `ls ~/.claude/plugins/cache/claude-plugins-official/superpowers/*/` mostra os três padrões — copiar a estrutura, não o conteúdo)

**Interfaces:**
- Consumes: skills/ (Task 10).
- Produces: os 3 manifests apontando `skills: ./skills/`; versão 0.1.0 em todos; nomes `temcomo`.

- [ ] **Step 1:** Escrever os manifests espelhando o formato do superpowers instalado (inspecionar os arquivos reais antes).
- [ ] **Step 2: Teste de instalação local (Claude Code)** — `claude plugins install /caminho/para/temcomo` (ou o mecanismo local equivalente da versão instalada) e conferir que `/temcomo` aparece; para Hermes, adicionar o caminho a `skills.external_dirs` de um profile de teste e rodar `hermes-subagents:list`; para Codex, conferir descoberta via `~/.codex/skills` (symlink) — **nenhum push**; se algum harness não puder ser testado sem publicação, registrar no LEDGER como "não verificável localmente" (estado da máquina de estados da spec §2.5, nunca fingir PASS).
- [ ] **Step 3: Commit** — `git commit -am "feat(pacote): manifests claude/codex/hermes"`

---

## Auto-revisão do plano (executada em 2026-08-20)

1. **Cobertura da spec:** §4 estrutura → Tasks 1/9–13; §5 contratos/jornada → 3/4/7; §6 agentes → 9; §7 motor → 1–8; §8 HTMLs → 5/6 (templates vêm dos protótipos aprovados, que JÁ implementam §8 — wizard, anotações, callout); §9 pasta → 4; §10 visual → 5/6 + assets; §11 governança → 11; §12 verificação → 8 (+ inspeção visual em 5/6); §13 instalação → 13; §14–15 riscos/aceite → cobertos por 8/12/13. Sem lacunas.
2. **Placeholders:** nenhum TBD; tasks de prosa (9–12) têm conteúdo mapeado item a item + verificação objetiva por grep/execução.
3. **Consistência de tipos/nomes:** `validar_contra_schema`, `carregar_e_validar`, `render_direcoes`, `render_grill`, `avancar_etapa`, `ENGINE_VERSION` usados consistentemente; subcomandos idênticos aos da spec §7.

## Critério de "pronto" do plano

Os 5 critérios de aceite da spec §15, verificados na ordem: autoteste limpo (Task 8) → tour executável (Task 12) → HTMLs offline (Tasks 5/6) → fidelidade visual aos protótipos (Tasks 5/6 Step 4) → instalação tripla (Task 13).
