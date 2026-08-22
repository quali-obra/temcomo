# LEARNINGS — diário operacional do temcomo

Diário, não arquivo morto. Cada entrada nasce de algo que **aconteceu de verdade** e diz **o quê** e **por quê**.

## Como usar

- **Formato:** `### AAAA-MM-DD — título curto` + 1–5 linhas objetivas + `**Status:**`.
- **Status:** `pendente` (observado, ainda não virou regra) · `promovida (→ destino)` (virou regra em skill, RUNBOOK, motor ou prompt de agente) · `[SUPERADA AAAA-MM-DD]` (envelheceu ou foi contrariada).
- **Escreva quando:** um fluxo terminou com aprendizado reutilizável, uma suposição quebrou, um gate falhou, uma ferramenta se comportou diferente do documentado, ou o usuário deu instrução nova.
- **Regra de poda:** entrada `promovida` fica aqui **até a próxima limpeza**, com o destino nomeado — depois sai (a regra vive no destino, não no diário). Entrada superada é marcada, não apagada em silêncio. Se o arquivo passar de ~2 telas, consolide.
- **Exceção de bootstrap (única):** este diário nasce semeado com o histórico factual da construção do v0.1.0, já acima de duas telas e com várias entradas `promovida`. Essa fotografia inicial é deliberada e vale **até a primeira limpeza após o release v0.1.0** — nela, toda entrada `promovida` cujo destino já esteja escrito sai daqui. Depois disso, a regra de poda vale sem exceção.
- **Gate de evolução:** aprendizado **não** vira mudança sozinho. Registre `pendente` → proponha o diff → **aprovação explícita do usuário** → aplique com bump semver + entrada no `LEDGER.md`.

---

### 2026-08-19 — Watcher de subagente externo: o padrão completo, não só o "está pronto?"
`grep task_complete` no JSONL deu falso positivo (a string aparece dentro do texto de instruções). O padrão que funciona tem cinco partes, e nenhuma é opcional: **background** com prompt autocontido; **heartbeat** periódico (nunca poll silencioso); **condições de kill** objetivas com motivo registrado (sem output útil por dois heartbeats, pedido de segredo, escrita fora do worktree, reescrita não solicitada, timeout à vista sem artefato seguro); **veredito só pelo rollout**, parseando o payload e aceitando apenas `task_complete` com `last_agent_message` não nulo **e** conteúdo que fale do alvo desta tarefa (rollout de outra thread não vale); e **reconciliação pelo dono** — ler o diff e rerodar os testes canônicos, porque self-report não é verificação.
**Status:** promovida (→ `RUNBOOK.md` §4, subseção "Watcher de subagente externo").

### 2026-08-19 — Conta Codex sem crédito tem assinatura reconhecível
`task_complete` em menos de 10 segundos, `last_agent_message: null` e `credits.balance: 0` **não** é tarefa concluída — é arranque morto por falta de crédito. Dois conselhos técnicos foram perdidos assim antes de alguém olhar o rollout. Retry único conforme doutrina; persistindo, bloquear e notificar em vez de trocar de modelo por conta própria.
**Status:** pendente (candidata a check automatizado do watcher).

### 2026-08-19 — Codex CLI: `--ask-for-approval` é opção global e vem **antes** do subcomando
Invocação não interativa correta (CLI 0.140+): `codex --ask-for-approval never exec --sandbox read-only --cd <repo> --output-last-message <out.md> - < <prompt.md>`. A forma intuitiva — `codex exec --ask-for-approval never …` — **falha** com "unexpected argument", porque a opção é global, não do subcomando. Registrado na varredura da frota (`contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/pesquisas/insights-frota.md` §1.3, a partir da skill `coding-agent-delegation`).
**Status:** promovida (→ `RUNBOOK.md` §4, junto do watcher).

### 2026-08-19 — Wizard sobre markup real resolve Ctrl+F, impressão e decisão fantasma de uma vez
O padrão que passou em todos os gates: renderizar o conteúdo **integral como markup real**, esconder artigos com `hidden="until-found"` e fazer o `<dialog>` único **adotar o nó** (mover, nunca clonar nem `close()+showModal()`), devolvendo no fechamento. Duas pegadinhas medidas: elemento com `display:flex` próprio ignora o atributo `hidden`; artigo com `content-visibility:hidden` ainda desenha borda e padding ("casca vazia").
**Status:** pendente (destino: templates do motor).

### 2026-08-19 — Estado `pendente` explícito mata a decisão fantasma; rascunho lossless ≠ export
Export precisa de estado explícito e escolha nula até ação real do usuário — nada de persistir no boot. O rascunho guarda o estado de trabalho completo (todo texto digitado, anotações, órfãs) numa chave única com o SHA-256 do contrato; o export é **função pura** do rascunho, com `gerado_em` capturado no clique. Rascunho de schema antigo nunca é descartado em silêncio: backup + migração só do que é confiável + aviso leigo visível.
**Status:** pendente (destino: templates do motor).

### 2026-08-19 — Anotação ancorada: congelar a seleção e medir contra o texto pristino
A seleção morre em qualquer transição de UI e o `Range` "mente" (parece válido e devolve vazio). Congele `{bloco, trecho, prefixo, sufixo, offsets}` no instante da seleção e aja no `pointerdown`. Offsets contra snapshot pristino de `textContent` sobrevivem a marcações — desde que badges e botões dentro do bloco não contribuam texto (conteúdo via `::after { content: attr(...) }`). `contextmenu` só é prevenido com seleção válida e fora de campos, senão mata o Colar.
**Status:** pendente (destino: templates do motor).

### 2026-08-19 — Revisão fresh pega o que o verificador determinístico não vê
Dois P1 reais escaparam de 64 checks automáticos: painel de anotações renderizado só ao abrir (a impressão saía com a caixa vazia) e uma corrida entre "próximo" e `Esc` no cross-fade de 120 ms, montando conteúdo num diálogo já fechado. Superfície derivada deve ser renderizada em **todo** sync, não sob demanda; todo `setTimeout` de troca precisa ser cancelado no fechamento.
**Status:** promovida (→ `RUNBOOK.md` §7, camada 2: PASS estrutural ≠ revisão visual).

### 2026-08-20 — Quem lança o verificador é o orquestrador, nunca o produtor
No protótipo do grill v2, o revisor fresh foi lançado pelo próprio produtor. Funcionou, mas fere a independência que dá valor à revisão — e o próprio revisor registrou a observação.
**Status:** promovida (→ `RUNBOOK.md` §5 e os 8 prompts de `agents/`).

### 2026-08-20 — Chrome headless entrega o evento `close` de `<dialog>` atrasado ou nunca
Não confie no `close` para arrumar a casa: o housekeeping de fechamento tem de ser **síncrono**, e o listener de `close` deve ignorar evento com `dlg.open === true` (evento velho chegando depois de a caixa já ter sido reaberta).
**Status:** pendente (destino: templates do motor + verificador).

### 2026-08-20 — Na âncora de anotação, o `trecho` é a autoridade; offsets são dica
O motor não pode recusar uma anotação porque `inicio/fim/prefixo` não bateram: texto muda de posição, não de conteúdo. Âncora que não re-resolve vira **anotação órfã preservada e marcada**, jamais descartada.
**Status:** promovida (→ Global Constraint do plano de implementação; `agents/entrevistador.md`).

### 2026-08-20 — Loop de revisão: reportar vence corrigir direto, fora do mecânico
Parecer da literatura (`pesquisas/parecer-loop-revisao.md`): o revisor que edita deixa de ser verificador, e correção iterativa só tem valor esperado positivo se a taxa de correção superar a de introdução de erro. Daí o desenho em vigor: revisor reporta com evidência, implementador corrige, re-revisão em thread nova valida o **diff contra o ledger de disposição**. O revisor pode **anexar patch sugerido** para achado mecânico, mas **não aplica nada**: quem decide usar o patch é o **orquestrador**, quem aplica é o implementador/fixer, e o gate determinístico revalida na hora.
**Status:** promovida (→ `RUNBOOK.md` §6).

### 2026-08-20 — "Revisor fresco não achou nada" é parada fraca sozinha
Consenso de janela 1 sobre juiz ruidoso não tem garantia nenhuma. Só se sustenta porque o gate duro é o teste determinístico e a task é pequena. Por isso a parada exige, além do veredito limpo: **zero achado de severidade `P0`/`P1`**, **evidência de verificação executada**, teto de 3 rodadas e detector de estagnação — e **`w=2`, dois pareceres frescos limpos consecutivos, em tarefa de risco alto** (gate, contrato publicado, segurança, mudança difícil de desfazer, artefato já aprovado pelo Lucas ou qualquer coisa que saia do repositório); chegando ao teto com só um parecer limpo, **escala ao dono** — o teto não se estica.
**Status:** promovida (→ `RUNBOOK.md` §6).

### 2026-08-20 — Confiança e severidade são eixos independentes; colapsar os dois inverte o gate
A primeira versão do RUNBOOK escreveu `ACHADO de confiança ALTA ≡ P0/P1`. Está errado: confiança responde "tenho certeza de que isto é real?" e severidade responde "se for real, o quanto machuca?". Com a equivalência, um **nitpick certo** (`ALTA` + `P3`) bloquearia a entrega e uma **falha grave incerta** (`MÉDIA` + `P0`) passaria batida. Corrigido para dois eixos: confiança decide **se reporta**, severidade decide **se bloqueia** — e a regra de bloqueio é uma só, "achado `P0` ou `P1`".
Regra final: **quem bloqueia é a severidade, nunca o rótulo** — `MÉDIA + P0` bloqueia igual, e `ALTA + P3` é ACHADO que não bloqueia.
**Status:** promovida (→ `RUNBOOK.md` §6 "Taxonomia"; campo `[SEVERIDADE]` em `agents/revisor-adversarial.md` e `agents/avaliador-de-cobertura.md`; `LEDGER.md` `T-20260820-003`, **ratificada pelo Lucas em 2026-08-20** e completada por `T-20260820-004`).

### 2026-08-20 — `git add -A` em árvore compartilhada varre o trabalho da outra lane
Com duas lanes trabalhando em paralelo, um `git add -A` na árvore principal levou junto o `engine/temcomo.py` em voo da outra lane e registrou a worktree como gitlink. Resultado: um commit de orquestração carregando código alheio e, logo depois, um commit intitulado "esqueleto do CLI" **sem** o CLI — rastreabilidade quebrada.
**Status:** promovida (→ `RUNBOOK.md` §8; não-conformidade e ação corretiva em `LEDGER.md`, `T-20260820-002`).

### 2026-08-20 — Regra de idioma tem limite: rastro técnico é rotulado, não traduzido
Traduzir o rastro de falha do interpretador quebraria a utilidade dele (não dá para procurar a mensagem original). A saída é **rotular**: linha em PT-BR anunciando "detalhe técnico no formato original", e o rastro preservado abaixo. Exceção formal registrada nas Global Constraints.
**Status:** promovida (→ plano de implementação, Global Constraints; motor).

### 2026-08-22 — Quem diz qual rodada de grill está aberta é o disco; o registro é cache
A rodada esperando resposta sai da pasta `contratos/` (os `04-grill-rodada-N.json` sem resposta guardada), não do campo `rodada_de_grill_pendente` do registro da tarefa: apontador obsoleto travaria a tarefa para sempre, e disco ambíguo — duas rodadas abertas — faz o motor bloquear em vez de deixar o cache desempatar. O campo continua **sem produtor**: `renderizar` gera a página e não marca pendência; só a importação o zera. Fonte: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/checkpoints/motor-task-07.md` (decisões da rodada 1 e fechamento da rodada 3).
**Status:** pendente — a regra vive no motor (`reconciliar_grill`), mas o campo não aparece em `RUNBOOK.md`, `skills/` nem `agents/`, e a falta de produtor segue em aberto.

### 2026-08-22 — `AVISO_IRREVERSIVEL_PADRAO`: salvaguarda que o caminho validado nunca alcança
`regras_extras` exige `irreversivel_aviso` com conteúdo sempre que a pergunta traz `reversivel: false`, então o fallback do motor (constante `AVISO_IRREVERSIVEL_PADRAO` em `engine/temcomo.py`) só age em quem chamar `render_grill()` direto — contrato validado nunca chega lá. Ficou por ser exigência literal da Task 6 e por não fabricar dado da tarefa: é leitura derivada de um campo que o contrato **declarou**, diferente do `rodada` inventado, que virou erro. Reavaliar: manter como defesa em profundidade ou remover. Fonte: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/checkpoints/motor-task-06.md`, "Observação técnica que fica registrada".
**Status:** pendente.
