---
name: temcomo-grill
description: "Etapa 4 do temcomo — grill de descoberta: transformar a direção escolhida em decisões concretas, uma rodada de perguntas por vez, em páginas HTML que o usuário responde. Use depois da etapa `direcao-escolhida`. Quem decide se o grill acabou é um avaliador independente, nunca o orquestrador. Use também quando um orquestrador, juiz, conselheiro ou revisor suspeitar de drift na implementação: o grill fechado, guardado no projeto em `.temcomo/tarefas/`, é a referência das decisões do usuário."
version: 0.2.0
---

# temcomo-grill — etapa 4

## Quando entra

A tarefa está em `direcao-escolhida`. O caminho já foi escolhido pelo usuário; falta descobrir **como ele quer que funcione** — cada pergunta é uma decisão que muda alguma coisa na prática.

Confira antes, a partir da raiz do projeto (os caminhos `.temcomo/tarefas/<tarefa>` desta skill são relativos a ela): `python3 <raiz-do-plugin>/engine/temcomo.py status .temcomo/tarefas/<tarefa>`.

## Regras invioláveis

- **Orquestrador nunca avalia nem executa**: suficiência é do `agents/avaliador-de-cobertura.md`; reconciliação é de quem redigiu as perguntas; construir vem depois do gate humano.
- **Quem lança o verificador é o orquestrador**, jamais o produtor das perguntas.
- **O HTML só coleta decisão** — nenhum botão executa nada.
- **Sem decisão fantasma:** a opção recomendada aparece destacada, **nunca pré-gravada**; `pendente` é estado legítimo até o usuário clicar.
- **Rastreabilidade** (sessão + transcript JSONL) em todo handoff e no envelope `produzido_por`.
- **O grill mora no projeto, nunca em pasta temporária** — ver a seção abaixo.

## Onde o grill mora

O grill é o registro das decisões do usuário e a referência de tudo o que vem depois — por isso fica **dentro do projeto**, na pasta da tarefa: `<raiz-do-projeto>/.temcomo/tarefas/<tarefa>/`, onde `<raiz-do-projeto>` é a raiz do repositório em que a conversa acontece. **Nunca** em `/tmp`, scratchpad do harness ou `Downloads`: o que está lá some com a sessão, e depois ninguém consegue conferir o que foi decidido. A orientação de harness de "usar o scratchpad para arquivo temporário" vale para rascunho descartável — artefato do grill não é descartável.

- **Antes da rodada 1**, confira pelo `status` que a pasta da tarefa está dentro do projeto. Está em pasta temporária? **Pare e reporte ao usuário**: trazer a tarefa para o projeto é decisão dele, e move-se a pasta inteira, nunca arquivo a arquivo.
- **Na mesma hora**, confira que o git não ignora a tarefa: `git check-ignore -v .temcomo/tarefas/<tarefa>/tarefa.json`, na raiz do projeto. Saiu uma linha (exit 0)? Alguma regra do `.gitignore` — `.temcomo/`, `.*/` — esconde o grill do versionamento: **pare e reporte** a regra ao usuário; abrir exceção é decisão dele.
- Todo subagente recebe o **caminho absoluto** da pasta da tarefa e grava ali; caminho fora dela no handoff volta a quem produziu. Exceção: subagente em worktree isolado (`RUNBOOK.md` §4) entrega no worktree, e o orquestrador copia o arquivo, byte a byte, para a pasta da tarefa antes de qualquer gate — o que fica só no worktree não conta como grill.

| O quê | Onde (dentro da pasta da tarefa) | Quem grava |
|---|---|---|
| Rodada N | `contratos/04-grill-rodada-N.json` | `entrevistador` |
| Página da rodada | `html/NN-grill-rodada-N.html` | motor (`renderizar`) |
| Resposta como chegou (colada no chat ou baixada) | `respostas/recebidas/grill-rodada-N.json` — sem sobrescrever: reenvio ganha sufixo (`grill-rodada-N-reenvio-2.json`) | quem conduz a etapa, antes de importar |
| Resposta importada (a que vale) | `respostas/grill-rodada-N.json` | motor (`importar-resposta`), nunca à mão |
| Consolidado candidato da rodada N | `contratos/04-grill-consolidado-candidato-rodada-N.json` | `entrevistador` |
| Avaliação da rodada N | `pesquisas/avaliacao-rodada-N.md` | `avaliador-de-cobertura` |
| Consolidado final | `contratos/04-grill-consolidado.json` | `entrevistador` |

Nada disso é apagado, movido ou reescrito depois do fechamento. A pasta `.temcomo/` é parte do projeto: não entra no `.gitignore` (a conferência acima pega regra que já exista) e vai junto quando o trabalho do projeto for versionado.

## Procedimento

1. **Lance o `agents/orquestrador-grill.md`.** Ele conduz o ciclo; você não redige nem avalia por fora.
2. **Ciclo por rodada N:**
   - `agents/entrevistador.md` redige `contratos/04-grill-rodada-N.json` a partir do objetivo, do brief de pesquisa e da direção escolhida.
   - `validar` → `renderizar` → entregar o HTML ao usuário → ele responde e devolve → guardar como chegou em `respostas/recebidas/` (crie a subpasta na primeira vez) → `importar-resposta` do arquivo gravado.
   - As **dúvidas voltam ao entrevistador** (quem perguntou reconcilia), junto com as **anotações ancoradas** — inclusive as órfãs, que são preservadas e respondidas.
   - O entrevistador entrega o **consolidado candidato**; o `avaliador-de-cobertura` recebe rodada + respostas + candidato e devolve `VEREDITO: SUFICIENTE` ou `VEREDITO: NOVA RODADA` com as decisões que faltam.
3. **Limite de rodadas:** mesma lacuna repetida ou 3ª rodada sem suficiência → **bloqueio explícito** devolvido a esta skill, sem abrir N+1 automaticamente.
4. **Fechamento:** consolidado final revisado por `agents/revisor-adversarial.md` (fresco, recebendo caminhos e hashes do consolidado, de todas as respostas importadas, das rodadas e da avaliação), e só então:

```bash
python3 <raiz-do-plugin>/engine/temcomo.py validar .temcomo/tarefas/<tarefa>/contratos/04-grill-consolidado.json
python3 <raiz-do-plugin>/engine/temcomo.py concluir-etapa .temcomo/tarefas/<tarefa> grill-concluido
```

**Barreira de compatibilidade:** confira antes com `python3 <raiz-do-plugin>/engine/temcomo.py --ajuda` se a lista traz `concluir-etapa` e `importar-resposta <arquivo> [--tarefa <pasta>]`. Faltou, ou bloqueou? **Pare e reporte**: não improvise substituto, não edite `tarefa.json`, não mova arquivo à mão para `respostas/` e não declare o grill concluído. **Quem opera o motor** é quem conduz a etapa — acionar gate é orquestração, não "executar" no sentido proibido (que é construir o produto). Rode a transição **uma vez só**, conferindo o `status` antes: as rodadas são registradas pelo `importar-resposta`, e só o fechamento usa `concluir-etapa`.

## Forma das perguntas (o que esta skill exige do contrato)

- `id` estável e descritivo (nunca posicional), `pergunta` de até 90 caracteres, `impacto_curto` (o que muda na prática), `contexto` leigo, `origem` (de onde a pergunta veio).
- `reversivel` booleano; quando `false`, `irreversivel_aviso` em linguagem direta — a página destaca essas decisões para dar para ver de longe que é difícil voltar atrás.
- `botoes`: os tokens do contrato são **`aprovar`, `rejeitar`, `duvida`**. O rótulo que o usuário vê para `duvida` é "fiquei com dúvida", com campo ao lado para descrever (pode ficar em branco). **`adiar` só existe se esta skill habilitar** — habilite quando a tarefa tiver decisões que dependem de informação externa com prazo; caso contrário, não ofereça a saída fácil.
- `opcoes`: até 4 reais + no máximo 1 `fora_da_caixa`, com exatamente uma `recomendada`, cada uma dizendo o que se ganha e o que se abre mão.

## Consolidado (`grill-consolidado-v1`)

Cada decisão com estado explícito — `proposta → aprovada → aplicada → verificada`, mais `parcial` e `nao-verificavel` — **nunca um booleano solto**; cada uma rastreando a pergunta e a resposta que a originaram. Mais: as dúvidas reconciliadas (pergunta original → dúvida → reformulação → resposta final) e os **documentos de contexto** que alimentam a próxima etapa.

## Saída da etapa

Rodadas em `contratos/` e `html/`, respostas em `respostas/`, consolidado validado e revisado — tudo na pasta da tarefa, dentro do projeto —, tarefa em `grill-concluido`, handoff de 6 campos. Daqui saem os documentos de contexto para prototipagem e especificação (etapas do `ROADMAP.md`).

## Depois do fechamento: o grill como referência contra drift

Fechado, o grill é a **fonte de verdade das decisões do usuário** para as etapas seguintes (protótipo, spec, issues, implementação, revisão). Todo orquestrador, juiz, conselheiro ou revisor que **suspeitar de drift** — o que está sendo construído diverge do que o usuário decidiu, o escopo cresceu, uma opção rejeitada voltou, uma decisão irreversível foi tratada como reversível — **pesquisa o grill antes de dar parecer**, em vez de confiar na memória da conversa ou no resumo de outro agente:

1. **Ache a tarefa:** `ls <raiz-do-projeto>/.temcomo/tarefas/` e o `status` dela; procure o assunto com `grep -ril "<termo>" <raiz-do-projeto>/.temcomo/tarefas/<tarefa>/`.
2. **Leia na ordem de autoridade:** `contratos/01-objetivo.json` (o objetivo manda) → `respostas/` (a palavra do usuário: a direção escolhida e cada rodada importada) → `contratos/04-grill-rodada-*.json` (o que foi perguntado e quais opções existiam) → `contratos/04-grill-consolidado.json` e documentos de contexto (a leitura consolidada, que também pode ter derivado).
3. **Cite a evidência:** arquivo + `pergunta_id` + estado e escolha. Parecer de drift sem citação do grill é opinião.
4. **Divergência confirmada volta ao usuário.** Não se edita o grill para caber no que foi feito, nem se reinterpreta a resposta dele. Se ele quiser mudar a decisão, **pare e reporte**: o motor não aceita outra resposta para rodada já importada e ainda não existe registro de emenda depois do fechamento (lacuna conhecida, a definir junto das etapas seguintes do `ROADMAP.md`). Até lá vale a decisão registrada, e nada é construído sobre a decisão nova.
5. **Grill em silêncio não é autorização:** ponto que o grill não cobriu é lacuna a levar ao usuário, não licença para quem implementa decidir.

## Armadilhas

1. **Perguntar o que ferramenta ou pesquisa já responde.** Ferramentas antes de perguntas factuais.
2. **Pergunta que não muda nada** — se nenhuma resposta altera o resultado, ela não entra.
3. **Jargão sem tradução** ou textão antes do resumo curto.
4. **Responder pelo usuário** quando ele demora, ou tratar "fiquei com dúvida" em branco como aprovação.
5. **Descartar anotação órfã** porque a âncora não bate — o `trecho` é a autoridade.
6. **Deixar o orquestrador declarar que acabou.** Só o avaliador independente fecha.
