---
name: temcomo
description: "Use quando alguém perguntar 'tem como fazer X?', invocar /temcomo, ou pedir uma funcionalidade/mudança sem especificação fechada. Conduz a jornada completa — entender o objetivo, pesquisar o que já existe, propor direções e fazer o grill de descoberta — com formulários validados por um motor e decisões tomadas pelo usuário em páginas HTML. Não implementa nada antes da escolha dele."
version: 0.1.0
---

# temcomo — a skill mestre

## O que é isto

O temcomo trata o pedido do usuário como um **sistema de gestão da qualidade**: cada etapa é um procedimento (uma skill), cada procedimento preenche um formulário (um contrato JSON), e um motor confere o formulário antes de deixar a etapa avançar. As decisões chegam ao usuário como páginas HTML em linguagem leiga, que ele abre no navegador, responde e devolve. **Nada avança sem formulário validado; nada é construído sem o usuário escolher uma direção.**

O usuário é leigo em programação. A forma técnica que ele sugere é **hipótese possivelmente errada**, não especificação.

## Regras invioláveis (valem nas 4 etapas)

1. **A autoridade é o objetivo, não a solução sugerida.** Primeiro o resultado desejado, depois o mecanismo.
2. **Gates bloqueiam, não avisam.** Formulário reprovado = etapa parada, com o motivo dito em português. Nunca "aviso e segue".
3. **Orquestrador nunca avalia nem executa.** Quem orquestra lança trabalhadores, cobra handoff e devolve feedback. Avaliação é sempre de agente independente — e **quem lança o verificador é o orquestrador, jamais o produtor**.
4. **Self-report não é verificação.** "Está pronto" escrito por quem produziu não vale; o motor revalida e a revisão é feita por agente sem o contexto do produtor.
5. **O HTML só coleta decisão.** Nenhum botão chama rede, terminal, agente ou API.
6. **Rastreabilidade em todo handoff:** todo agente declara o **ID da sua sessão** e o **caminho do seu transcript JSONL**, no handoff e no envelope `produzido_por` dos contratos. Quem não conseguir determinar, declara isso — nunca omite em silêncio.
7. **"Tem como...?" não é autorização.** Pergunta exploratória e `/temcomo` não liberam instalar, configurar, escrever código ou aplicar mudança.

## Barreira de compatibilidade do motor (antes de qualquer comando)

```bash
python3 <raiz-do-plugin>/engine/temcomo.py --ajuda   # lista os subcomandos desta versão
```

A ajuda lista os subcomandos desta versão **e as opções de que as skills dependem**: `--data` em `nova-tarefa` e `--tarefa` em `importar-resposta`. Se o que as skills citam não estiver na lista, o motor falha fechado — e são dois sinais diferentes: subcomando que não existe (ex.: `concluir-etapa`) para com "subcomando inexistente"; opção que não existe (ex.: `--tarefa`) para com "argumentos não reconhecidos". Nos dois casos: **pare e reporte ao usuário**. Não improvise substituto, não edite `tarefa.json`, não marque a etapa como concluída e não simule a transição. Etapa parada com motivo dito é estado válido; etapa "concluída" sem gate, não.

**Quem opera o motor:** rodar `validar`, `renderizar`, `importar-resposta`, `concluir-etapa` e `status` **é parte da orquestração** — a regra "orquestrador nunca executa" proíbe construir o produto (instalar, configurar, codificar, redigir o conteúdo final), não proíbe acionar os gates. Cada transição é rodada **uma única vez por quem conduz a etapa**: antes de chamar `concluir-etapa`, confira o `status`; se a etapa já mudou (porque `importar-resposta` foi o gate), não rode de novo.

## Etapa 1 — Entender o objetivo (é aqui que esta skill trabalha)

1. **Diga o objetivo que você entendeu**, sem repetir a solução técnica sugerida: "Objetivo que entendi: <resultado prático>. Antes de seguir, tenho algumas perguntas."
2. **Pergunte uma de cada vez**, curto, oferecendo a hipótese mais provável para o usuário só confirmar ou corrigir.
3. **Ferramentas antes de perguntas factuais.** O que arquivo, comando, inventário ou documentação respondem, você não pergunta.
4. A etapa termina quando **a frase descreve o resultado, não o mecanismo**, e o usuário concorda em seguir. Às vezes o objetivo entendido muda tudo — inclusive revela que não precisa ser feito.
5. **Abra a tarefa** e registre o formulário:

```bash
python3 <raiz-do-plugin>/engine/temcomo.py nova-tarefa "<objetivo resumido>"
# escreva contratos/01-objetivo.json (schema objetivo-v1: pergunta original, objetivo
# confirmado em linguagem leiga ≤1500 caracteres, anti-metas, restrições, perguntas e
# respostas, hipóteses descartadas, envelope produzido_por com sessão + transcript)
python3 <raiz-do-plugin>/engine/temcomo.py validar .temcomo/tarefas/<tarefa>/contratos/01-objetivo.json
python3 <raiz-do-plugin>/engine/temcomo.py concluir-etapa .temcomo/tarefas/<tarefa> objetivo-confirmado
```

Se `concluir-etapa` bloquear, **pare e reporte** — não edite `tarefa.json` à mão.

## A jornada completa

| Etapa | Skill | Formulário | Gate de saída |
|---|---|---|---|
| 1. Entender o objetivo | `temcomo` (esta) | `01-objetivo.json` | frase descreve o resultado; usuário confirmou |
| 2. Pesquisar o que existe | `temcomo-pesquisa` | `02-pesquisa.json` | achados com fonte primária + auditoria independente aprovada |
| 3. Propor direções | `temcomo-direcoes` | `03-direcoes.json` → HTML → `respostas/decisao-direcoes.json` | **usuário escolheu uma direção no HTML** |
| 4. Grill de descoberta | `temcomo-grill` | `04-grill-rodada-N.json` → `04-grill-consolidado.json` | avaliador independente declara cobertura suficiente |

Onde tudo mora: `.temcomo/tarefas/<slug>-<aaaa-mm-dd>/` com `tarefa.json`, `contratos/`, `html/`, `respostas/`, `pesquisas/`. Em que pé está: `python3 <raiz-do-plugin>/engine/temcomo.py status .temcomo/tarefas/<tarefa>`.

### Roteamento (como você conduz, etapa a etapa)

1. Rode `status`. **A etapa atual manda**: não invoque a skill de uma etapa cujo gate anterior ainda não passou, e não pule etapa "porque está óbvio".
2. `objetivo-confirmado` → invoque **`temcomo-pesquisa`**. Ao receber o handoff de 6 campos, confira os 6 campos e a rastreabilidade; incompleto volta a quem produziu, sem você preencher o buraco.
3. `pesquisa-concluida` → invoque **`temcomo-direcoes`**. O gate dela é humano: espere a escolha do usuário, sem construir nada nesse meio-tempo.
4. `direcao-escolhida` → invoque **`temcomo-grill`**. Ela devolve o consolidado e os documentos de contexto.
5. `grill-concluido` → fim do v1. As etapas seguintes (prototipagem, spec, issues, PR) estão no `ROADMAP.md`; não as improvise aqui.
6. Em qualquer ponto: bloqueio devolvido por uma etapa (limite de rodadas, revisor indisponível, transição barrada) **para a jornada** e é reportado ao usuário com o que falta — nunca contornado.

## Os agentes (prompts em `agents/`)

`orquestrador-pesquisa.md` · `pesquisador-interno.md` · `pesquisador-externo.md` · `redator-do-brief.md` · `orquestrador-grill.md` · `entrevistador.md` · `avaliador-de-cobertura.md` · `revisor-adversarial.md`

Cada um é autocontido: ao lançar um subagente, entregue o arquivo correspondente como prompt e só o recorte de contexto que ele precisa.

**Papéis de modelo (recomendação, nunca trava):** pesquisa → modelo rápido; redação e raciocínio pesado → modelo forte; revisão adversarial → modelo externo rigoroso (ex.: Codex), sempre em background e thread fresca. **Degradação explícita:** quem não tiver essa frota usa o modelo que tem, em sessão separada e sem o contexto do produtor, e diz no handoff qual modelo revisou.

## Gate de evolução da skill

Encontrou divergência entre o que a skill manda e a realidade, ou o usuário deu instrução nova?

1. Registre em `LEARNINGS.md` como `pendente` (data + o quê + por quê).
2. Proponha a mudança concreta (diff da skill, do contrato ou do motor).
3. **Só aplique depois da aprovação explícita do usuário** — aprovação estreita autoriza só o recorte descrito, nunca o pacote por associação.
4. Aplicada: bump semver no `version:` + entrada no `LEDGER.md` (append-only).

Problema aparecido no uso é corrigido **na fonte** (skill, contrato, motor ou prompt de agente) e vira aprendizado — nunca remendo local.

## Armadilhas

1. **Responder "sim, dá" e já desenhar a solução.** Primeiro objetivo, ambiguidade e pesquisa.
2. **Pesquisar só os termos técnicos do usuário.** Pesquise também o resultado desejado e o sintoma.
3. **Confundir pergunta exploratória com autorização.**
4. **Esconder a opção simples atrás de um textão.** Tabela curta primeiro, explicação leiga depois.
5. **Perguntar o que é verificável.** Ferramentas antes de perguntas factuais.
6. **Pular a etapa porque "está óbvio".** O gate é o motor, não a sua confiança.
