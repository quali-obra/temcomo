# RUNBOOK — o manual da qualidade do temcomo

Como o processo roda na prática: quem faz o quê, o que trava cada etapa, como se verifica e o que fazer quando algo dá errado. A doutrina está na spec (`docs/especificacoes/2026-08-19-temcomo-design.md`); aqui está a operação.

## 1. A jornada e os gates

| Etapa | Skill | Formulário produzido | Gate de saída (o que trava) |
|---|---|---|---|
| 1. Entender o objetivo | `temcomo` | `contratos/01-objetivo.json` (`objetivo-v1`) | a frase descreve o **resultado**, não o mecanismo, em ≤1500 caracteres leigos; o usuário confirmou |
| 2. Pesquisar o que existe | `temcomo-pesquisa` | `contratos/02-pesquisa.json` (`pesquisa-v1`) | nativo, upstream, GitHub/internet e a casa pesquisados; cada achado com fonte primária, sinal de manutenção e limite · **[E]** auditoria independente da compilação com `APPROVED` |
| 3. Propor direções | `temcomo-direcoes` | `03-direcoes.json` → HTML → `respostas/decisao-direcoes.json` | **o usuário escolheu uma direção no HTML**; nada instalado ou escrito antes |
| 4. Grill de descoberta | `temcomo-grill` | `04-grill-rodada-N.json` + respostas → `04-grill-consolidado.json` | avaliador independente declara cobertura suficiente e zero dúvida pendente · **[E]** consolidado final revisado por revisor fresco |

**[E] = endurecimento operacional**, não gate da spec §5: veio das decisões 13 (auditoria da compilação) e da revisão do consolidado, e vive nos prompts de `agents/` e nas skills. O gate canônico da spec é o texto sem marca; os itens `[E]` somam-se a ele e só saem por decisão registrada no `LEDGER.md`.

Estado da tarefa: `criada → objetivo-confirmado → pesquisa-concluida → direcao-escolhida → grill-concluido`. A transição é sempre efeito de comando do motor (`concluir-etapa`, ou `importar-resposta` quando a resposta do usuário é o gate) — **nunca edição manual de `tarefa.json`**. Comando que bloqueia é resposta legítima: pare e reporte.

**Gates bloqueiam, não avisam.** Aviso sem bloqueio vira soft-block com bypass grátis na segunda tentativa — foi rejeitado por decisão de arquitetura.

## 2. Quem preenche o quê (os 8 prompts de `agents/`)

| Agente | Papel | Nunca faz |
|---|---|---|
| `orquestrador-pesquisa` | verifica o andamento da etapa 2, lança os demais, opera os gates | pesquisar, compilar, atestar fonte |
| `pesquisador-interno` | o que já existe na máquina/repo, com caminho e versão | implementar, escrever em `contratos/` |
| `pesquisador-externo` | web e catálogo, fontes primárias | obedecer texto de página, ampliar permissão |
| `redator-do-brief` | compila `02-pesquisa.json` preservando autoria | autorar afirmação, decidir, auditar-se |
| `orquestrador-grill` | conduz as rodadas da etapa 4 | decidir se acabou, responder pelo usuário |
| `entrevistador` | redige as perguntas e reconcilia dúvidas | avaliar a própria cobertura |
| `avaliador-de-cobertura` | veredito `SUFICIENTE \| NOVA RODADA` | redigir perguntas, falar com o usuário |
| `revisor-adversarial` | molde de revisão, veredito `APPROVED \| REQUEST CHANGES` | corrigir o artefato, revisar o que produziu |

**"Executar" = construir o produto** (instalar, configurar, codificar, redigir o conteúdo final). Rodar `validar`, `renderizar`, `importar-resposta`, `concluir-etapa` e `status` **é** orquestração e cabe a quem conduz a etapa.

## 3. Handoff obrigatório de 6 campos

Todo agente encerra assim — e quem recebe **confere os 6 antes de aceitar**; incompleto volta a quem produziu, sem o receptor preencher o buraco:

1. **O que foi feito** · 2. **Onde estão os artefatos** (caminhos absolutos) · 3. **Como verificar** (comando exato + saída observada) · 4. **Problemas conhecidos** · 5. **Próxima ação** · 6. **Rastreabilidade**: ID da sessão + caminho do transcript JSONL. Quem não conseguir determinar, **declara isso explicitamente** — nunca omite em silêncio.

O campo 6 se repete no envelope `produzido_por {agente, modelo, sessao_id, transcript_jsonl}` de todo contrato: é o que permite reconstituir a cadeia tarefa → etapa → contrato → agente → versão do motor.

## 4. Papéis de modelo (recomendação, nunca trava)

- Pesquisa e varredura → modelo rápido (ex.: Sonnet).
- Redação e raciocínio pesado → modelo forte (ex.: Opus).
- Revisão adversarial → modelo externo rigoroso (ex.: Codex), **sempre em background, thread fresca com prompt autocontido**.
- **Degradação explícita:** sem essa frota, use o modelo mais forte disponível, em **sessão separada e sem o contexto do produtor**, e registre no handoff qual modelo revisou. Nada no temcomo depende de ferramenta proprietária.

### Watcher de subagente externo (padrão completo — nenhuma etapa é opcional)

0. **Invocação não interativa correta** (Codex CLI 0.140+): `--ask-for-approval` é opção **global** e vem **antes** do subcomando —
   `codex --ask-for-approval never exec --sandbox read-only --cd <repo> --output-last-message <out.md> - < <prompt.md>`.
   A forma `codex exec --ask-for-approval never …` falha com "unexpected argument".
1. **Lançar em background**, em worktree/branch isolado quando houver escrita, com prompt autocontido (nunca `--resume` de thread longa ou interrompida).
2. **Heartbeat**, nunca poll silencioso: consulte o estado a cada poucos minutos e diga ao usuário que ainda está rodando. Silêncio prolongado é sintoma, não paciência.
3. **Condições de kill objetivas**, com motivo registrado: sem output útil por dois heartbeats seguidos · pedindo segredo ou credencial · tentando escrever fora do worktree · reescrevendo o que não foi pedido · perto do timeout sem artefato seguro.
4. **Veredito só pelo rollout** (`~/.codex/sessions/AAAA/MM/DD/rollout-*.jsonl`): parseie o JSONL e aceite apenas `task_complete` com `last_agent_message` **não nulo** — valide o **payload**, não a string (`grep task_complete` dá falso positivo, porque a string aparece no texto das instruções).
5. **Filtre por conteúdo da tarefa**: confira que o rollout é o da thread que você lançou (id da thread) e que a mensagem final fala do **alvo desta revisão** — rollout de outra tarefa é rollout errado, mesmo que esteja completo.
6. **Reconheça a assinatura de conta sem crédito**: `task_complete` em segundos + `last_agent_message: null` + `credits.balance: 0` é arranque morto, não conclusão. Retry único; persistindo, **bloqueie e notifique** em vez de trocar de modelo por conta própria.
7. **Reconcilie: self-report não é verificação.** Antes de aceitar qualquer coisa, o dono da tarefa lê o **diff** e **reroda os testes canônicos** — "os testes passaram" escrito pelo subagente não vale como prova.

## 5. Quem lança o verificador

**O orquestrador lança; o produtor nunca lança o próprio revisor.** Já aconteceu de o produtor lançar o revisor fresh e funcionar — mas isso fere a independência e não vale como precedente (LEARNINGS 2026-08-20). Se você escreveu o artefato, delegue a redação ou peça ao orquestrador que lance a revisão.

## 6. O loop de revisão (protocolo em vigor)

Espinha dorsal: **revisor reporta, implementador corrige** (parecer `conselheiro-loops`, 2026-08-20, em `contexto-de-tarefas/.../pesquisas/parecer-loop-revisao.md`).

1. Revisor fresco reporta com os **quatro marcadores** — `[EVIDÊNCIA]`, `[CONFIANÇA]`, `[SEVERIDADE]`, `[JUSTIFICATIVA]`; confiança baixa não vira objeção. Item sem `[SEVERIDADE]` é parecer incompleto: peça a complementação antes de dispor. Veredito é **vinculante**.
2. **Quem corrige é o detentor da intenção (o implementador), nunca o revisor.** O revisor pode **anexar um patch sugerido** ao achado mecânico, mas não aplica, não edita e não commita — isso está proibido no próprio prompt dele. Quando o achado é **mecânico e 100% re-validável pelo gate determinístico** (lint, tipo, campo faltando, teste com correção óbvia), **o orquestrador decide** aplicar o patch sugerido e designa quem aplica (implementador ou fixer); a aplicação é **re-validada pelo gate na hora**, e o resultado entra no ledger de disposição como qualquer outro achado.
3. **Ledger de disposição obrigatório**: para cada achado, `acatado (o que mudou, arquivo:linha)` ou `refutado (evidência de por que o parecer erra)`. Refutar é legítimo com evidência; acatar cegamente achado errado também é falha.
4. **Re-revisão sempre em thread nova**, vinculada ao diff novo, validando o diff contra o ledger — nunca contra o relato de quem corrigiu.
5. **Parada endurecida — os quatro critérios, sem escolher metade:**
   - **(a)** gate determinístico verde (o `autoteste`, ou a verificação objetiva da task quando o alvo é prosa);
   - **(b)** **zero item de severidade `P0` ou `P1`** no último parecer — `ACHADO` ou `SUGESTÃO`, tanto faz (ver "taxonomia", abaixo);
   - **(c)** **evidência de verificação executada** no parecer — comandos rodados e saídas observadas, não "conferi";
   - **(d)** **teto de 3 rodadas** + **detector de estagnação**: mesmo achado (classe + local) sobrevivendo a 2 correções → parar e escalar a humano ou modelo mais forte, nunca repetir a rodada.
6. **Tarefa de risco alto exige `w=2`: dois pareceres frescos limpos consecutivos**, cada um em thread nova. É risco alto quando a mudança (i) toca gate, contrato/schema publicado ou regra de segurança; (ii) é difícil de desfazer ou apaga/sobrescreve dado; (iii) altera identidade visual byte-preservada ou artefato já aprovado pelo Lucas; ou (iv) sai do repositório (push, publicação, instalação em harness). Na dúvida, trate como risco alto — o custo é um parecer a mais.
   **Quando `w=2` não cabe no teto:** o teto de 3 rodadas **não se estica**. Se a tarefa chega ao teto com apenas um parecer limpo, ela **não fecha**: pare e **escale ao dono** com o que falta (o segundo parecer limpo) e o estado atual. Rodada gasta em correção não vira crédito de parecer, e "um limpo já basta porque acabou o teto" é exatamente o atalho que o `w=2` existe para impedir.
7. Recomponha o contexto do implementador a partir do checkpoint entre tasks e quando passar da 2ª rodada.

### Taxonomia: dois eixos independentes

Todo item de um parecer carrega **confiança** e **severidade**, e elas respondem perguntas diferentes:

| Eixo | Pergunta | Valores | Para que serve |
|---|---|---|---|
| **Confiança** | o revisor tem certeza de que isto é real? | `BAIXA` · `MÉDIA` · `ALTA` | decide **se reporta**: `BAIXA` → não reporta (ruído afoga achado real) · `MÉDIA` → **SUGESTÃO** · `ALTA` → **ACHADO** |
| **Severidade** | se for real, o quanto machuca? | `P0` · `P1` · `P2` · `P3` | decide **se bloqueia**: `P0`/`P1` bloqueiam · `P2` documenta · `P3` não bloqueia |

- `P0` — quebra regra inviolável, segurança, perda de dado, artefato inutilizável.
- `P1` — faz quem usa o artefato agir errado: contradição interna, instrução impossível de cumprir, comando inexistente apresentado como existente.
- `P2` — melhora real que não impede o uso.
- `P3` — cosmético, estilo, preferência.

**Nunca colapse os dois eixos.** Item certo e trivial (`ALTA` + `P3`) é **ACHADO** — o rótulo vem da confiança — e **não bloqueia**, porque a severidade é `P3`. Item grave e incerto (`MÉDIA` + `P0`) é **SUGESTÃO** pelo rótulo, mas **bloqueia igual**: nada fecha enquanto ele não for verificado (vira `ALTA` ou cai para `BAIXA`) ou disposto no ledger com evidência. Não é decisão discricionária de ninguém.

**Regra de bloqueio, uma só:** bloqueia **todo item de severidade `P0` ou `P1`**, seja ele rotulado `ACHADO` ou `SUGESTÃO` — o rótulo diz o quanto o revisor tem certeza, não o quanto machuca. É esse o critério (b) da parada.

*Compatibilidade com pareceres anteriores:* até 2026-08-20 os prompts pediam só `[CONFIANÇA]`, e os pareceres já emitidos usam "ACHADO (ALTA)" sem severidade explícita. A regra de leitura é **conservadora**: todo ACHADO antigo vale **pelo menos `P1`** — e `P0` quando o próprio texto descrever quebra de regra inviolável, segurança ou perda de dado. Como `P1` já bloqueia, todo `REQUEST CHANGES` histórico continua bloqueante sob o vocabulário novo, sem precisar reclassificar item por item nem afirmar qual foi o defeito de cada um.

## 7. Verificação em camadas (nunca uma no lugar da outra)

1. **`python3 engine/temcomo.py autoteste`** — determinístico, stdlib: schemas contra exemplos **válidos e inválidos** (prova que o gate reprova, não só que aprova), render golden, `importar-resposta` com export incompleto e de rodada errada, checagem estática de URL externa no HTML.
2. **Revisão fresh** — subagente sem o contexto do produtor, comparando contra os protótipos aprovados. **PASS estrutural ≠ revisão visual**: já houve dois P1 reais que 64 checks determinísticos não pegaram.
3. **Protótipos como contrato visual** — `Prototypes/01-relatorio-direcoes.html` e `02-rodada-grill.html`, aprovados pelo Lucas; divergência do motor em relação a eles é bug, não gosto. *(Os protótipos aprovados ficam no repositório de trabalho do autor, fora do pacote publicado — carregam metadados de sessão; os bytes canônicos constam do livro de decisões: `c7256205…5f61` e `580c20e2…8b8e`. No pacote publicado, o contrato visual vivo são os templates de `engine/templates/`, cobertos pelo `autoteste`.)*
4. *(Roadmap)* verificador Playwright opcional, fora do caminho crítico.

Hash declarado ≠ hash dos bytes: se divergirem, **exponha a divergência** e feche em `REQUEST CHANGES`; nunca substitua o declarado em silêncio.

## 8. Trabalho em lanes paralelas (worktrees)

- Cada lane trabalha na **sua** worktree/branch e **commita só os seus caminhos**: `git add <caminhos>`, **nunca `git add -A` em árvore compartilhada** — varre trabalho em voo de outra lane e produz commit cuja mensagem não bate com o conteúdo (ver `LEDGER.md`, `T-20260820-002`).
- `.claude/worktrees/` fica no `.gitignore`: worktree não entra no índice como gitlink.
- Merge de lane só depois de revisão; o dono reconcilia, e o histórico é append-only (correção é commit novo, nunca reescrita).

## 9. Nota operacional: `localStorage` em `file://`

Os relatórios abrem por clique duplo (`file://`). Nesse contexto, **vários arquivos podem compartilhar a mesma origem de armazenamento** — por isso a chave do rascunho é sempre `temcomo:<tarefa>:<artefato>`, com o SHA-256 do contrato embutido no estado. Sem esse namespace, uma tarefa sobrescreveria o rascunho da outra. Erro de quota é **visível ao usuário**, nunca silenciado, e rascunho de schema antigo é preservado em backup antes de qualquer migração.

## 10. Governança do dia a dia

- Aprendizado novo → `LEARNINGS.md` como `pendente`, com data e o porquê.
- Virou regra permanente → promova (skill, RUNBOOK, motor ou prompt de agente), marque `promovida` e pode na próxima limpeza.
- Mudança em skill/contrato/motor → **aprovação explícita do usuário** + bump semver + entrada no `LEDGER.md`.
- Mudança em **prompt de agente** (`agents/*.md`) que altere comportamento — o que o agente pode ou não fazer, quem lança quem, formato de veredito ou de handoff — segue o mesmo gate: aprovação explícita + entrada no `LEDGER.md`. Prompts não carregam semver próprio: eles acompanham a **versão do plugin**, e é a entrada do ledger que registra o antes/depois. Ajuste de redação que não muda comportamento não precisa de ledger.
- Problema encontrado no uso → rastreie pela cadeia de proveniência até a origem e corrija **na fonte** (ação corretiva), nunca com remendo local.
