---
name: temcomo-grill
description: "Etapa 4 do temcomo — grill de descoberta: transformar a direção escolhida em decisões concretas, uma rodada de perguntas por vez, em páginas HTML que o usuário responde. Use depois da etapa `direcao-escolhida`. Quem decide se o grill acabou é um avaliador independente, nunca o orquestrador."
version: 0.1.0
---

# temcomo-grill — etapa 4

## Quando entra

A tarefa está em `direcao-escolhida`. O caminho já foi escolhido pelo usuário; falta descobrir **como ele quer que funcione** — cada pergunta é uma decisão que muda alguma coisa na prática.

Confira antes: `python3 <raiz-do-plugin>/engine/temcomo.py status .temcomo/tarefas/<tarefa>`.

## Regras invioláveis

- **Orquestrador nunca avalia nem executa**: suficiência é do `agents/avaliador-de-cobertura.md`; reconciliação é de quem redigiu as perguntas; construir vem depois do gate humano.
- **Quem lança o verificador é o orquestrador**, jamais o produtor das perguntas.
- **O HTML só coleta decisão** — nenhum botão executa nada.
- **Sem decisão fantasma:** a opção recomendada aparece destacada, **nunca pré-gravada**; `pendente` é estado legítimo até o usuário clicar.
- **Rastreabilidade** (sessão + transcript JSONL) em todo handoff e no envelope `produzido_por`.

## Procedimento

1. **Lance o `agents/orquestrador-grill.md`.** Ele conduz o ciclo; você não redige nem avalia por fora.
2. **Ciclo por rodada N:**
   - `agents/entrevistador.md` redige `contratos/04-grill-rodada-N.json` a partir do objetivo, do brief de pesquisa e da direção escolhida.
   - `validar` → `renderizar` → entregar o HTML ao usuário → ele responde e devolve → `importar-resposta`.
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

Rodadas em `contratos/` e `html/`, respostas em `respostas/`, consolidado validado e revisado, tarefa em `grill-concluido`, handoff de 6 campos. Daqui saem os documentos de contexto para prototipagem e especificação (etapas do `ROADMAP.md`).

## Armadilhas

1. **Perguntar o que ferramenta ou pesquisa já responde.** Ferramentas antes de perguntas factuais.
2. **Pergunta que não muda nada** — se nenhuma resposta altera o resultado, ela não entra.
3. **Jargão sem tradução** ou textão antes do resumo curto.
4. **Responder pelo usuário** quando ele demora, ou tratar "fiquei com dúvida" em branco como aprovação.
5. **Descartar anotação órfã** porque a âncora não bate — o `trecho` é a autoridade.
6. **Deixar o orquestrador declarar que acabou.** Só o avaliador independente fecha.
