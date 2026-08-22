# temcomo — Design do plugin (v1)

- **Data:** 2026-08-19
- **Status:** em revisão pelo Lucas
- **Decisões de origem:** `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/decisoes.md`
- **Pesquisas de suporte:** `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/pesquisas/` (wayfinder, inventário local, insights da frota)

---

## 1. Resumo em linguagem leiga

O **temcomo** é um plugin público que transforma a pergunta "tem como fazer X?" num processo de qualidade: como num sistema de gestão da qualidade (SGQ), cada etapa do trabalho é um **procedimento** (skill), cada procedimento tem **formulários** (contratos) que os agentes de IA são obrigados a preencher, e um **motor** confere os formulários e transforma cada decisão num relatório HTML bonito e leigo que o usuário abre no navegador, responde e devolve. Nada avança de etapa sem o formulário anterior validado; nada é construído sem o usuário escolher uma direção.

A primeira versão cobre as etapas 1–4 do fluxo: **entender o objetivo → pesquisar o que já existe → propor direções → grill de descoberta**. As etapas 5–9 (prototipagem, spec, issues, issue-closer, PR) ficam no roadmap.

Instalável no **Hermes**, no **Claude Code** e no **Codex** a partir de um único repositório na org QualiApps/QualiObra (push somente com aprovação explícita do Lucas).

## 2. Princípios (as "cláusulas do manual da qualidade")

1. **Procedimento + formulário.** Skill descreve *como* fazer; contrato JSON registra *o que* foi feito. O gate entre etapas é a validação do formulário pelo motor — nunca a boa vontade do agente.
2. **Orquestrador nunca avalia nem executa.** Ele roteia, acompanha, exige handoffs e devolve feedback a quem produziu. Avaliação é sempre delegada a um agente independente (precedente: `agent-team-orchestration`, luna-qualigestao).
3. **Gates bloqueiam, não avisam.** "Aviso sem bloqueio" já foi rejeitado por decisão de arquitetura do Lucas (ADR 0002 da frota): aviso vira soft-block com bypass grátis na segunda tentativa.
4. **Self-report não é verificação.** `passado: true` escrito pelo próprio produtor da etapa não vale; o motor revalida, e revisões usam agente "fresh" sem o contexto do produtor.
5. **Autoridade é o objetivo, não a solução sugerida.** O usuário é leigo: a forma técnica que ele sugere é hipótese, possivelmente errada. Primeiro o resultado desejado, depois o mecanismo.
6. **O HTML só coleta decisão.** Nenhum botão chama rede, terminal, agente ou API. Quem executa é o fluxo agêntico, depois do gate humano.
7. **Tudo versionado e com proveniência.** Schemas nomeados com `-vN`; artefatos gerados carregam cabeçalho com versão do motor e SHA-256 do contrato de entrada; mudanças de skill/contrato passam por ledger append-only.
8. **Rastreabilidade em todo o fluxo (inspiração declarada: ISO 9001).** Qualquer saída — HTML, contrato, resposta importada, documento de contexto — permite reconstituir a cadeia completa: tarefa → etapa → contrato → agente (sessão + JSONL) → versão do motor/skill. Problema encontrado no uso vira **ação corretiva na fonte** (corrige onde nasceu + registra aprendizado), nunca remendo local. *(Regra ditada pelo Lucas na aprovação do design, 2026-08-19.)*

## 3. Escopo

**v1 (este design):**
- 4 skills (mestre, pesquisa, direções, grill) + prompts de agentes por fase
- Motor Python stdlib (validação + renderização + status + importação de resposta + autoteste)
- 2 templates HTML (relatório de direções; rodada de grill) no visual QualiApps
- Pasta de tarefa como registro
- RUNBOOK, LEARNINGS com gate de evolução, ROADMAP, LEDGER
- Instalação nos 3 harnesses, README PT-BR

**Fora do v1 (ROADMAP.md):** etapas 5–9 do fluxo (prototipagem de features, spec/planejamento, issues épicas, integração issue-closer, PR merge); servidor MCP (resposta do HTML voltando direto ao agente); verificador Playwright opcional; documentação EN; hooks de enforcement por harness.

## 4. Estrutura do repositório

```
temcomo/
├── .claude-plugin/plugin.json        # manifesto Claude Code
├── .codex-plugin/plugin.json         # manifesto Codex (skills: ./skills/)
├── plugin.json                       # manifesto portátil raiz (Agent Plugins v1 — Hermes)
├── .hermes-plugin/                   # documentação Hermes (INSTALACAO.md)
├── skills/
│   ├── temcomo/SKILL.md              # mestre: etapa 1 + condução da jornada
│   ├── temcomo-pesquisa/SKILL.md     # etapa 2
│   ├── temcomo-direcoes/SKILL.md     # etapa 3
│   └── temcomo-grill/SKILL.md        # etapa 4
├── agents/                           # prompts de TODOS os subagentes do workflow
│   ├── orquestrador-pesquisa.md
│   ├── pesquisador-interno.md
│   ├── pesquisador-externo.md
│   ├── redator-do-brief.md
│   ├── orquestrador-grill.md
│   ├── entrevistador.md
│   ├── avaliador-de-cobertura.md
│   └── revisor-adversarial.md
├── contracts/                        # schemas dos formulários (JSON, sufixo -vN)
│   ├── tarefa-v1.schema.json
│   ├── objetivo-v1.schema.json
│   ├── pesquisa-v1.schema.json
│   ├── direcoes-v1.schema.json
│   ├── decisao-direcoes-v1.schema.json    # export do HTML de direções
│   ├── grill-rodada-v1.schema.json
│   ├── grill-respostas-v1.schema.json     # export do HTML do grill
│   └── grill-consolidado-v1.schema.json
├── engine/
│   ├── temcomo.py                    # motor único, Python ≥3.9, stdlib pura
│   ├── templates/
│   │   ├── direcoes.html.tpl
│   │   └── grill.html.tpl
│   └── assets/                       # tokens QualiApps, logo base64, fontes (opcionais)
├── exemplos/                         # 1 tarefa de exemplo completa (dados marcados como exemplo)
├── Prototypes/                       # protótipos estáticos validados pelo Lucas (mantidos como referência visual)
├── RUNBOOK.md                        # manual da qualidade: jornada, quem preenche o quê, gates, papéis de modelo
├── LEARNINGS.md                      # diário operacional com gate de promoção (ver §11)
├── LEDGER.md                         # registro append-only de mudanças em skills/contratos/motor
├── ROADMAP.md                        # etapas 5–9 e evoluções (MCP etc.)
└── README.md                         # PT-BR: o que é, instalação nos 3 harnesses, tour de 5 minutos
```

## 5. A jornada e os contratos

Máquina de estados da tarefa (`tarefa.json`, schema `tarefa-v1`):

```
criada → objetivo-confirmado → pesquisa-concluida → direcao-escolhida → grill-concluido → [v2: prototipo → spec → ...]
```

Cada transição exige o contrato da etapa validado pelo motor (`temcomo.py validar`). O motor recusa transição com formulário ausente, incompleto ou com schema errado.

| Etapa | Skill | Contrato produzido | Gate de saída |
|---|---|---|---|
| 1. Entender o objetivo | `temcomo` (mestre) | `01-objetivo.json` (`objetivo-v1`) | Frase descreve o **resultado** (não o mecanismo) em ≤1500 caracteres leigos; usuário confirmou |
| 2. Pesquisar o que existe | `temcomo-pesquisa` | `02-pesquisa.json` (`pesquisa-v1`) | Nativo/upstream/GitHub/frota pesquisados; cada achado com fonte primária, manutenção e limite |
| 3. Propor direções | `temcomo-direcoes` | `03-direcoes.json` (`direcoes-v1`) → HTML → `respostas/decisao-direcoes.json` | **Usuário escolheu uma direção no HTML.** Nada é instalado/escrito antes |
| 4. Grill de descoberta | `temcomo-grill` | `04-grill-rodada-N.json` + `respostas/grill-rodada-N.json` → `04-grill-consolidado.json` | Avaliador independente declara cobertura suficiente e zero dúvidas pendentes |

Campos essenciais por contrato (detalhe fino nos schemas):

- **`objetivo-v1`**: pergunta original ("tem como...?"), objetivo confirmado (resultado, leigo), anti-metas, restrições, perguntas feitas/respostas, hipóteses descartadas.
- **`pesquisa-v1`**: brief de contexto local (o que já existe no repo/frota/ferramentas), trilhas externas (máx. 3), achados `[{afirmação, url, tipo de fonte, sinal de manutenção, confiança, limite}]`, lacunas remanescentes, conflitos de evidência.
- **`direcoes-v1`**: até **4 direções reais** + no máximo **1 fora da caixa** (`fora_da_caixa: true`, nunca inventada para preencher cota), cada uma com {reuso/build, custo, complexidade, aderência 0–100, limite principal, explicação leiga ≤1500 chars}; critérios de ranking explícitos (integração agêntica sempre presente); recomendação com justificativa.
- **`grill-rodada-v1`**: rodada N com **todas as perguntas da rodada** `[{id, pergunta, contexto leigo, opções (≤4 reais + ≤1 fora da caixa, recomendada pré-marcada), botões habilitados}]`.
- **`grill-respostas-v1`** (export do HTML): por pergunta `{pergunta_id, estado: aprovada|rejeitada|duvida|adiada, escolha_id, comentario, duvida_texto}` + envelope `{schema_version, tarefa_id, rodada, gerado_em}`.
- **`grill-consolidado-v1`**: decisões finais com máquina de estados por decisão (`proposta → aprovada → aplicada → verificada`, mais `parcial` e `nao-verificavel` — nunca booleano solto), dúvidas reconciliadas (pergunta original → dúvida → reformulação → resposta final), e os **documentos de contexto** gerados a partir do grill (insumo da futura etapa de spec).

**Envelope comum a todo contrato:** `schema_version` · `tarefa_id` · `gerado_em` · `produzido_por: {agente, modelo, sessao_id, transcript_jsonl}` — o campo `produzido_por` materializa a regra de rastreabilidade do §6: quem preencheu o formulário deixa dito onde está o JSONL da sua sessão.

## 6. Agentes (`agents/`) — a corrente de orquestração

Cada fase tem um **agente de orquestração** com prompt próprio e autocontido. Orquestradores nunca avaliam nem produzem conteúdo final — lançam trabalhadores, exigem handoffs (6 campos: o que foi feito, onde estão os artefatos, como verificar, problemas conhecidos, próxima ação, **rastreabilidade da sessão**) e devolvem feedback a quem produziu.

**Rastreabilidade obrigatória:** todo agente que trabalhar numa tarefa temcomo declara, no handoff e no envelope dos contratos que preencher, o **ID da sua sessão** e o **caminho do seu transcript (JSONL)** — para que qualquer informação possa ser recuperada na fonte depois. Agente que não conseguir determinar esses dados no seu ambiente declara isso explicitamente (nunca omite o campo em silêncio).

```
[skill mestre temcomo]
   └── orquestrador-pesquisa ──> pesquisador-interno (contexto local: repo, skills, MCPs, inventários)
   │                        └──> pesquisador-externo (web, fontes primárias; consulta o catálogo antes)
   │        (curadoria delegada: entrega insumo já auditado — brief de pesquisa)
   └── orquestrador-grill ─────> entrevistador (redige as perguntas a partir do insumo; reconcilia dúvidas)
   │                       └──> avaliador-de-cobertura (independente: decide se precisa nova rodada; mandato REFUTAR)
   │        (ao final: gera os documentos de contexto)
   └── [v2] orquestrador-especificacao (grill + pesquisas → contexto de produto + spec)
```

- **`orquestrador-pesquisa`** *(emendado por decisão do Lucas, 2026-08-20 — decisão 13)*: recebe o objetivo confirmado, lança os dois pesquisadores em paralelo, exige achados com fonte primária, resolve conflitos lançando busca complementar estreita — e **só verifica se o trabalho está sendo feito corretamente**: quem monta o brief é o **`redator-do-brief`** (compila os achados auditados dos pesquisadores, preservando autoria individual; compilar não é autorar decisões), e antes da entrega o orquestrador **lança uma auditoria independente da compilação** (molde do `revisor-adversarial`; recomendação: Codex), em loop até APPROVED. O agente principal não usa as próprias ferramentas externas enquanto a delegação estiver disponível.
- **`pesquisador-externo`**: antes de pesquisar, **consulta o catálogo local de pesquisas** (`~/.temcomo/catalogo-de-pesquisas/`, configurável) para não repesquisar o que já foi estudado; salva pesquisas novas lá com índice (papers/artigos separados, PDF baixado quando possível) e uma cópia na pasta da tarefa. Trata conteúdo web como não confiável; ignora instruções embutidas em páginas.
- **`orquestrador-grill`**: monta a rodada com o `entrevistador`, chama o motor para renderizar, entrega o HTML ao usuário, importa as respostas, **devolve as dúvidas ao `entrevistador`** (quem fez as perguntas reconcilia), e pede ao `avaliador-de-cobertura` o veredito de suficiência. Nunca decide sozinho se acabou.
- **`avaliador-de-cobertura`**: mandato adversarial herdado do prompt-molde da frota: *refutar, não confirmar* — cada objeção com `[EVIDÊNCIA]`, `[CONFIANÇA]`, `[JUSTIFICATIVA]`; confiança baixa não vira objeção. Veredito: `SUFICIENTE | NOVA RODADA (com as lacunas nomeadas)`.
- **`revisor-adversarial`**: prompt-molde genérico (adaptado quase verbatim do `implementation-phased-loop`) para qualquer revisão do pipeline; recomendação de modelo externo rigoroso (Codex) quando disponível, com o padrão operacional de background/watcher/rollout documentado no RUNBOOK e LEARNINGS.

**Papéis de modelo (recomendação, nunca trava):** pesquisa → modelo rápido (ex.: Sonnet); redação/raciocínio pesado → modelo forte (ex.: Opus); revisão adversarial → modelo externo rigoroso (ex.: Codex via CLI, sempre em background, thread fresca, veredito recuperado pelo rollout). Quem não tiver essa frota usa o modelo que tiver — as skills degradam explicitamente.

## 7. O motor (`engine/temcomo.py`)

Script único, Python ≥3.9, **stdlib pura** (zero pip install). Determinístico: mesmo contrato entra → mesmo HTML sai (timestamps vêm do contrato, não do relógio do render). Subcomandos:

| Comando | Função |
|---|---|
| `nova-tarefa "<objetivo resumido>"` | Cria `.temcomo/tarefas/<slug>-<aaaa-mm-dd>/` com `tarefa.json` inicial |
| `validar <contrato.json>` | Valida contra o schema correspondente (validador próprio, subset de JSON Schema em stdlib). Erros nomeiam campo e motivo. Exit code ≠0 em falha |
| `renderizar <contrato.json>` | Gera o HTML (tipo inferido pelo `schema_version`) em `html/NN-*.html`, nunca sobrescreve; injeta cabeçalho de proveniência (versão do motor + SHA-256 do contrato) |
| `importar-resposta <arquivo.json>` | Valida o export do HTML, casa com a rodada/relatório pendente, grava em `respostas/`, atualiza `tarefa.json`. Recusa resposta incompleta ou de rodada errada |
| `status [<tarefa>]` | Em que pé está: etapa atual, gates passados, pendências, próxima ação |
| `autoteste` | Suíte fail-closed embutida (ver §12) |

Regra fail-closed: qualquer dúvida do motor (schema desconhecido, hash divergente, resposta órfã) **bloqueia com mensagem acionável**, nunca segue com aviso.

## 8. Os HTMLs (templates `direcoes` e `grill`)

Ambos derivam do padrão visual/mecânico do `011-arquiteto-relatorio-decisao.html` (que por sua vez deriva do findings-review-html v0.2.7 + mecânica grill-me-with-html v0.2.1), reescritos limpos para o temcomo:

- **Modo wizard (padrão de interação — decisão do Lucas, 2026-08-19; refinado pelo conselho de direção visual, ver pesquisas/conselho-visual/sintese.md)**: a página é uma **lista compacta** de itens, cada um com título, resumo de 1 linha, recomendação nomeada visível e **chip de estado em linguagem leiga** ("Falta responder" · "Respondido — sua escolha: X" · "Você pediu para explicarem melhor" · "Deixei para depois"). Clicar no item abre um **wizard** (`<dialog>` nativo com os remendos catalogados no parecer técnico: foco inicial, `close` assíncrono, backdrop, scroll de fundo; mobile = folha inferior). Ordem interna do cartão: pergunta → por que estou perguntando → o que muda na prática → opções → painel "ganha/abre mão" reativo → ação + comentário. **Fechar (Esc/fundo/×) sempre salva rascunho, nunca descarta**; foco volta à linha de origem. O **conteúdo real é renderizado no documento** — o wizard é aprimoramento por cima (Ctrl+F, impressão via `@media print`, leitores de tela e modo "ver como documento" continuam funcionando). Ao final, **tela de conferência** com todas as respostas em uma linha cada, antes do export.
- **Sem decisão fantasma**: a opção recomendada vem **destacada, nunca pré-gravada** — existe estado `pendente` explícito e a escolha só vale com ação do usuário (aceitar a recomendação custa 1 clique). O export distingue "sem interação" de "escolheu a recomendação". **Rascunho ≠ export**: o rascunho persiste sem perdas (texto de dúvida sobrevive a troca de estado + reload); o export é função pura do rascunho; erros de quota do localStorage são visíveis, nunca silenciados.
- **Nas direções, a lista É a tabela comparativa** (consenso 2/3 do conselho): custo, aderência e limite lado a lado na própria lista — porque escolher entre 5 caminhos é decisão comparativa; o cartão wizard é o aprofundamento de cada caminho, e escolher funciona nas duas superfícies. No grill (decisões independentes), wizard puro.
- **Irreversibilidade visível de longe (decisão do Lucas, 2026-08-20)**: pergunta/decisão com `reversivel: false` ("difícil voltar atrás") ganha, além do texto, destaque de fundo em tint de perigo **bem suave** na linha da lista — forte o bastante para saltar aos olhos, fraco o bastante para não gritar nem reprovar contraste AA.
- **Anotações ancoradas (decisão do Lucas, 2026-08-19)**: selecionar texto → **barra flutuante de seleção** (caminho primário, idêntico em mouse e toque; botão direito é atalho — nunca sequestrar o `contextmenu` do navegador) → **"Anotar"**: comentário preso ao trecho (âncora: id do bloco + trecho + offsets sobre o texto pristino, com re-ancoragem tolerante). Âncora que não re-resolve gera **anotação órfã preservada e marcada — jamais descartada**. Marcador visual em tint da marca com pontilhado (nunca amarelo), badge de contagem, painel de anotações. Campo `anotacoes: [{id, item_id|null, trecho, comentario}]` **obrigatório desde o `-v1`** de `decisao-direcoes-v1` e `grill-respostas-v1`; `gerado_em` do export = instante da ação do usuário, nas duas páginas.

- **Autocontidos e offline**: zero CDN, zero request de rede; logo QualiApps e fontes embutidos em base64 pelo renderizador; abre com clique duplo (`file://`).
- **Relatório de direções**: hero com objetivo leigo, tabela compacta das direções, um cartão por direção (explicação leiga ≤1500 chars, custo/complexidade/aderência/limite), cartão fora-da-caixa visualmente marcado, recomendação pré-selecionada, painel "o que acontece se eu escolher esta" (consequências comparadas), campo de comentário.
- **Rodada de grill**: **todas as perguntas da rodada numa página só**; cada pergunta com contexto leigo, ≤4 opções reais + ≤1 fora da caixa (recomendada pré-marcada), botões de estado **configuráveis por pergunta no contrato** — base: `aprovar | rejeitar | fiquei com dúvida`; `adiar` só aparece se a skill habilitar. O botão **"fiquei com dúvida"** abre campo ao lado para descrever a dúvida (pode ficar em branco). Barra de progresso "X de N respondidas".
- **Persistência e devolução**: rascunho salvo em `localStorage` (chave `temcomo:<tarefa>:<artefato>`); ao concluir, dois caminhos — **"copiar resposta"** (JSON compacto para colar no chat) e **"baixar arquivo"** (salvar em `respostas/`). Envelope sempre com `schema_version` + IDs estáveis (nunca posicionais).
- **Acessibilidade**: alvos ≥44px, contraste AA, foco visível, `aria-live` no painel de consequência, empilhamento mobile.
- **Nenhum botão executa nada** — o HTML coleta; o agente executa depois do gate.

## 9. A pasta de tarefa (o registro)

```
.temcomo/tarefas/<slug>-<aaaa-mm-dd>/
├── tarefa.json          # máquina de estados da jornada
├── contratos/           # 01-objetivo.json, 02-pesquisa.json, 03-direcoes.json, 04-grill-*.json
├── html/                # relatórios numerados, imutáveis (novo render = novo arquivo)
├── respostas/           # exports do usuário importados pelo motor
└── pesquisas/           # material bruto dos pesquisadores até a conclusão da tarefa
```

Criada no repositório onde a conversa acontece (versionável em git junto com o projeto). Catálogo global de pesquisas externas reutilizáveis: `~/.temcomo/catalogo-de-pesquisas/` (configurável), consultado antes de qualquer pesquisa externa nova.

## 10. Visual QualiApps

Fonte canônica dos ativos: `iris-design-system/skills/brand/qualiapps-design-system/` (tokens.css, logos, manual). O temcomo **copia** (não referencia) os ativos necessários para `engine/assets/`, com cabeçalho de proveniência (caminho fonte + SHA-256) e regra de sincronização anti-fork — bump do upstream é ato deliberado registrado no LEDGER.

- **Cor institucional**: QualiApps cyan-deep `#058FFE` como `--brand` padrão dos relatórios (regra da casa: cor de marca tem dono — se um dia o relatório for de uma submarca, usa a cor dela).
- **Tipografia**: Poppins (títulos/UI) + Barlow (corpo) + JetBrains Mono (metadados), com fallbacks de sistema; Balloon **nunca** em texto (só no logotipo, que entra como imagem). Poppins/Barlow/JetBrains Mono são OFL (embutíveis legalmente em repo público).
- **Tokens**: neutros, espaçamento 4px, radius, sombras — transcritos do `tokens.css` oficial.
- **Nunca misturar com a identidade Araújo** (institucional A4 azul `#1E4E89` + Plus Jakarta Sans) — regra documentada em 3 skills da frota.

## 11. Governança e evolução (LEARNINGS + gate)

- **`LEARNINGS.md`**: diário datado (`### AAAA-MM-DD — título` + 1–5 linhas com o quê e por quê), combinando o formato do `learnings.md` do iris-design-system com o status de promoção do self-improvement: cada entrada pode ser `pendente | promovida (→ SKILL/RUNBOOK/motor) | superada`. Regra de poda: virou regra permanente → promove e remove do diário; envelheceu → marca `[SUPERADA]`. Diário, não arquivo morto. Exemplos que já nascem lá: padrão watcher para subagente Codex (background, heartbeat, kill conditions, veredito pelo rollout, self-report nunca é prova); invocação não-interativa correta do Codex CLI (`--ask-for-approval` antes do subcomando `exec`).
- **Gate de evolução da skill**: quando o agente encontra divergência entre a skill e a realidade, ou instrução nova do usuário, ele (1) registra no LEARNINGS como `pendente`, (2) propõe a mudança concreta (diff da skill/contrato/motor), (3) **só aplica após aprovação explícita do usuário**, (4) aplica com bump semver + entrada no LEDGER. Aprovação estreita autoriza só o recorte descrito, nunca o pacote por associação.
- **`LEDGER.md`**: append-only, uma entrada por mudança aplicada em skill/contrato/motor: `ID (T-AAAAMMDD-NNN) · Escopo · Estado anterior · Mudança · Aprovação · Evidência · Rollback · Resultado`. Correção = entrada nova, nunca reescrita.
- **Versionamento**: todo `SKILL.md` com `version:` semver no frontmatter; schemas nunca mudam em silêncio — mudança incompatível cria `-v2` e o motor aceita ambos durante a transição.
- **Ação corretiva (ISO 9001)**: problema encontrado no uso é rastreado até a origem pela cadeia de rastreabilidade (§2.8) e corrigido **na fonte** (skill, contrato, motor ou prompt de agente), com entrada no LEARNINGS; se a correção muda comportamento, bump semver + entrada no LEDGER.

## 12. Verificação

1. **`temcomo.py autoteste`** (determinístico, stdlib): valida os schemas contra contratos de exemplo válidos **e inválidos** (prova que os gates reprovam, não só que aprovam — fail-closed); renderiza os contratos golden e compara com saída esperada (hash de HTML normalizado); testa importar-resposta com exports válidos, incompletos e de rodada errada; verifica por inspeção estática que o HTML gerado não contém URLs externas.
2. **Revisão fresh**: procedimento no RUNBOOK — todo artefato visual novo passa por um subagente revisor **sem o contexto do produtor**, comparando contra os protótipos aprovados. PASS estrutural ≠ revisão visual (aprendizado documentado da frota).
3. **Protótipos como contrato visual**: os HTMLs de `Prototypes/` aprovados pelo Lucas ficam no repo como referência canônica do visual; divergência do motor em relação a eles é bug.
4. (Roadmap) verificador Playwright opcional em `tools/`, fora do caminho crítico.

## 13. Instalação nos 3 harnesses

| Harness | Mecanismo |
|---|---|
| **Claude Code** | `.claude-plugin/plugin.json` + marketplace.json; instalação via `claude plugin marketplace add <repo>` seguido de `claude plugin install temcomo@temcomo-dev` |
| **Codex** | `.codex-plugin/plugin.json` com `skills: "./skills/"`; alternativa `npx skills add <org>/temcomo` |
| **Hermes** | `plugin.json` na raiz (Agent Plugins v1 portátil; skills namespaced); alternativa plana: adicionar o clone a `skills.external_dirs` do profile (padrão já usado na frota, ADR 0001) |

O README traz os três caminhos + um tour de 5 minutos (criar tarefa de exemplo, abrir o HTML, responder, importar).

**Colisão de nome conhecida**: existe `/temcomo` em `~/.hermes/shared/skills/workflows/temcomo/` (só etapas 1–3). A convivência depende do mecanismo de instalação: **via plugin**, a skill nova fica namespaced nos três harnesses (Claude Code `<plugin>:<skill>`, Codex prefixada, Hermes `agent-plugin-<slug>-<hash>:<skill>`) e não disputa o nome plano com o legado — aposentar ou renomear o legado não cria alias para a skill do plugin, que continua sendo chamada pelo nome qualificado; **em instalação direta na árvore plana** (`skills.external_dirs`, `~/.codex/skills`, cópia manual), a disputa de nome é real. O destino do legado é decisão do Lucas na hora da adoção, registrada no ledger da frota (fica fora do escopo do repo público).

## 14. Riscos e mitigação

| Risco | Mitigação |
|---|---|
| Agente "esperto" pula etapa ou preenche formulário de fachada | Gate = validação do motor (exit code); campos com critérios mínimos (ex.: achado sem URL de fonte primária reprova); avaliador independente no grill |
| HTML diverge visualmente com o tempo | Protótipos aprovados como contrato visual + revisão fresh + autoteste golden |
| Fork silencioso dos ativos QualiApps | Cabeçalho de proveniência + SHA-256 + sincronização deliberada via LEDGER |
| Usuário sem a frota do Lucas (sem Codex/Hermes) | Papéis de modelo são recomendação com degradação explícita; nada depende de ferramenta proprietária |
| Schema muda e quebra tarefas antigas | Schemas versionados `-vN`; motor aceita versões antigas em transição |
| Pesquisa externa repetida a cada tarefa | Catálogo global `~/.temcomo/catalogo-de-pesquisas/` consultado antes de pesquisar |
| Problema aparece no uso real e ninguém sabe de onde veio | Rastreabilidade ponta a ponta (ISO 9001, §2.8): envelope `produzido_por`, proveniência nos HTMLs, ledger e JSONLs de sessão — localiza a origem e corrige na fonte (ação corretiva) |

## 15. Critérios de aceite do v1

1. `temcomo.py autoteste` passa limpo em Python 3.9+ sem nenhuma dependência instalada.
2. Jornada completa da tarefa de exemplo roda de ponta a ponta nos 3 harnesses: criar tarefa → objetivo → pesquisa → HTML de direções → escolha importada → rodadas de grill → consolidado.
3. Os dois HTMLs abrem offline via `file://`, sem nenhum request externo, rascunho sobrevive a reload, export valida no motor.
4. Protótipos visuais aprovados pelo Lucas antes do motor ser escrito; render final bate com eles.
5. README permite a um terceiro instalar e rodar o tour de 5 minutos sem ajuda.

---

*Próximo passo após aprovação deste documento: protótipos HTML em `Prototypes/` (relatório de direções + rodada de grill) para validação visual do Lucas; depois, plano de implementação (skill writing-plans).*
