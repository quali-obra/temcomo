# Instalar o temcomo no Hermes

O Hermes carrega este repositório como **Agent Plugin v1 portátil**: o manifesto é o `plugin.json` **da raiz do repositório** (não deste diretório — o runtime só procura na raiz do plugin), e as skills são descobertas em `skills/<nome>/SKILL.md`, com o `name` do frontmatter igual ao nome da pasta.

Esta pasta `.hermes-plugin/` guarda **só esta documentação**. Não há manifesto aqui: um `plugin.yaml` neste subdiretório seria ignorado pelo runtime instalado, que exige `plugin.yaml` + `__init__.py` com `register(ctx)` na raiz do plugin (plugin nativo) **ou** `plugin.json` na raiz (portátil). O temcomo usa o formato portátil, porque não registra ferramentas Python — ele entrega skills.

> Receita verificada por instalação real em **Hermes Agent v0.20.2**, profile `arquiteto`, em 2026-08-20 (relatório: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/instalacao-hermes.md`).

## Antes de tudo: em qual profile você está instalando?

**Numa instalação com profiles, o CLI opera no profile sticky ativo** (`~/.hermes/active_profile`), e o diretório de plugins dele é `~/.hermes/profiles/<profile>/plugins/`. O `~/.hermes/plugins/` é o home do profile **default**: um plugin colocado ali **não aparece** para o profile ativo — `hermes plugins show temcomo` responde `Plugin 'temcomo' not found.`

Descubra o alvo e fixe-o numa variável:

```bash
cat ~/.hermes/active_profile          # profile sticky ativo
export HERMES_PROFILE=arquiteto       # ou o profile onde o temcomo deve viver
export HERMES_HOME=~/.hermes/profiles/$HERMES_PROFILE
```

Se a sua instalação **não** usa profiles, o home é o próprio `~/.hermes` — mas **exporte a variável mesmo assim**, porque todos os comandos abaixo a usam dentro de caminhos:

```bash
export HERMES_HOME="$HOME/.hermes"
```

**Nunca deixe `HERMES_HOME` vazia.** Com a variável vazia, um caminho montado a partir dela apontaria para a **raiz do sistema de arquivos** — por isso todos os comandos deste documento usam a forma que **falha fechado**, `${HERMES_HOME:?defina HERMES_HOME}`: se a variável não estiver definida, a shell aborta com `HERMES_HOME: defina HERMES_HOME` e sai com código diferente de zero, sem criar nem apagar nada. Se preferir não usar variável, escreva o caminho completo em cada comando.

## Caminho 1 (recomendado): plugin portátil

```bash
# 1. conferir que o pacote é válido, ANTES de instalar (não muda nada na máquina)
hermes plugins doctor /caminho/para/temcomo --ci

# 2a. a partir do Git (URL, owner/repo ou nome do índice) — `install` NÃO aceita caminho local
hermes plugins install <owner>/temcomo

# 2b. localmente, sem publicar: symlink no diretório de plugins DO PROFILE ALVO
ln -s /caminho/para/temcomo "${HERMES_HOME:?defina HERMES_HOME}/plugins/temcomo"

# 3. pacotes portáteis instalam DESABILITADOS — habilite explicitamente
HERMES_HOME="${HERMES_HOME:?defina HERMES_HOME}" hermes plugins enable temcomo
#    ele pergunta sobre `allow_tool_override` — responda NÃO (o temcomo não registra tools)
#    e avisa "Takes effect on next session": o efeito vale a partir da próxima sessão do profile
```

## Verificação (o que funciona de verdade)

```bash
HERMES_HOME="${HERMES_HOME:?defina HERMES_HOME}" hermes plugins list --plain | grep temcomo
#   antes do enable:  not enabled  git  0.1.0  temcomo
#   depois do enable: enabled      git  0.1.0  temcomo

HERMES_HOME="${HERMES_HOME:?defina HERMES_HOME}" hermes plugins show temcomo
#   temcomo v0.1.0 · Status: enabled · Source: git · Key: temcomo

HERMES_HOME="${HERMES_HOME:?defina HERMES_HOME}" hermes plugins doctor temcomo --ci
#   OK: runtime discovery, manifest parsing, import, and registration passed   (exit 0)
```

**Para ver as 4 skills**, use o mesmo carregador que o runtime usa na sessão:

```bash
# onde o hermes-agent está instalado na sua máquina (ajuste se o seu for outro)
export HERMES_AGENT="${HERMES_AGENT:-$HOME/.hermes/hermes-agent}"

"$HERMES_AGENT/.venv/bin/python3" -c "
import os, sys, pathlib
hermes_agent = os.environ.get('HERMES_AGENT')
hermes_home = os.environ.get('HERMES_HOME')
if not hermes_agent or not hermes_home:
    raise SystemExit('defina HERMES_AGENT e HERMES_HOME antes de rodar')
sys.path.insert(0, hermes_agent)
from hermes_cli.agent_plugins import load_agent_plugin
plugin = pathlib.Path(hermes_home) / 'plugins' / 'temcomo'
dados = pathlib.Path(os.environ.get('TMPDIR', '/tmp')) / 'temcomo-data'
p = load_agent_plugin(plugin, dados)
print([s.name for s in p.skills], '| diagnósticos:', [d.message for d in p.diagnostics])"
# esperado: ['temcomo', 'temcomo-direcoes', 'temcomo-grill', 'temcomo-pesquisa'] | diagnósticos: []
```

⚠️ **Não use `hermes skills list` para conferir este plugin.** Skills de Agent Plugin v1 são registradas em runtime sob namespace próprio (`agent-plugin-temcomo-<hash>:<skill>`) e, por design do runtime (docstring de `register_skill`), **não entram na árvore plana `~/.hermes/skills/` nem no índice `<available_skills>`** — são carregamentos explícitos, opt-in. Nenhuma opção de `--source {all,hub,builtin,local}` as mostra. Ausência ali **não** é sinal de falha.

## Caminho 2 (só as skills): `skills.external_dirs`

Serve quando você quer os procedimentos como skills comuns, no índice plano, sem instalar plugin. É o padrão da frota (ADR 0001 — skills operacionais vivem em diretório git compartilhado, nunca em cópias por perfil).

```yaml
skills:
  external_dirs:
    - ~/.hermes/shared/skills               # o que já existia
    - /caminho/para/temcomo/skills          # esta linha
```

Reinicie a sessão e confirme com `hermes skills list`. Neste caminho o Hermes não conhece o plugin — só as 4 skills, e aí sim elas aparecem na listagem.

## O resto do repositório

- **`agents/`** não é instalado: os 8 prompts são **entregues como prompt** quando o fluxo lança cada subagente (`agents/orquestrador-pesquisa.md`, `agents/redator-do-brief.md`, e assim por diante).
- **O motor** não precisa de instalação: `python3 <clone>/engine/temcomo.py --ajuda`, Python ≥3.9, stdlib pura.

## Convivência com o `/temcomo` legado — depende do **mecanismo**, não do harness

Existe uma skill `/temcomo` antiga na frota (`~/.hermes/shared/skills/workflows/temcomo/`, e possivelmente uma cópia dentro do profile), cobrindo só as etapas 1–3, sem contratos nem motor. O que acontece com ela depende de **como** o temcomo novo foi instalado:

**a) Instalado como plugin — nos três harnesses, sem disputa de nome.** As skills do plugin ficam **sob o nome do plugin**, não soltas na árvore plana:

| Harness | Como a skill do plugin é exposta | Fonte |
|---|---|---|
| Hermes (Caminho 1) | `agent-plugin-temcomo-<hash>:<skill>`, fora da árvore plana e do índice `<available_skills>` | `hermes_cli/plugins.py` — `_portable_skill_namespace` e a docstring de `register_skill` ("opt-in explicit loads only") |
| Claude Code | `<plugin>:<skill>` — aqui, `temcomo:temcomo` | README do marketplace oficial: "Each skill is registered as `<plugin-name>:<skill-name>` in Claude Code" |
| Codex | prefixadas pelo plugin | binário do `codex-cli` 0.144.5: "Skills from this plugin are prefixed with …" |

Ou seja: **o legado não é atropelado e não atropela o plugin**. O efeito prático é o **inverso** do que se costuma temer — quem responde ao nome plano `temcomo` continua sendo o legado, e as skills novas precisam ser chamadas pelo nome qualificado. **Aposentar ou renomear o legado é decisão do dono; isso libera/remove o nome plano, mas não renomeia nem cria alias para a skill do plugin, que continua sendo chamada pelo nome qualificado.**

**b) Instalado direto na árvore plana de skills** — Hermes pelo Caminho 2 (`skills.external_dirs`), `~/.codex/skills`, `npx skills add`, ou qualquer cópia manual para o diretório de skills do host. Aí **as duas ocupam o mesmo nome** e a disputa é real: escolha uma antes de instalar (aposentar, renomear ou não usar esse caminho).

Como saber em qual caso você está — **pelo método de instalação, não por listagem**: se instalou pelo Caminho 1 do Hermes, confira com `plugins list` / `plugins show` / `doctor` e o loader (a skill não aparece em `skills list`, por design); se usou `skills.external_dirs`, `~/.codex/skills`, `npx skills add` ou cópia manual, é árvore plana **por construção**; no Claude Code e no Codex via plugin, o catálogo do host costuma exibir o prefixo do plugin.

A decisão sobre o legado é do dono da frota, registrada no ledger dela (fora do escopo deste repositório público).

## Se o plugin sumir da listagem

Symlink apontando para uma **worktree git** quebra quando a worktree é removida (por exemplo, depois de a branch ser mesclada). Nesse caso o plugin desaparece da descoberta: refaça o symlink para o clone definitivo, ou instale pelo Git quando o repositório estiver publicado.
