# O grill como referência contra drift

Referência da skill `temcomo-grill`: lida por quem **suspeitar de drift** depois do fechamento do grill.

Fechado, o grill é a **fonte de verdade das decisões do usuário** para as etapas seguintes (protótipo, spec, issues, implementação, revisão). Todo orquestrador, juiz, conselheiro ou revisor que **suspeitar de drift** — o que está sendo construído diverge do que o usuário decidiu, o escopo cresceu, uma opção rejeitada voltou, uma decisão irreversível foi tratada como reversível — **pesquisa o grill antes de dar parecer**, em vez de confiar na memória da conversa ou no resumo de outro agente:

1. **Ache a tarefa:** `ls <raiz-do-projeto>/.temcomo/tarefas/` e o `status` dela; procure o assunto com `grep -ril "<termo>" <raiz-do-projeto>/.temcomo/tarefas/<tarefa>/`.
2. **Leia na ordem de autoridade:** `contratos/01-objetivo.json` (o objetivo manda) → `respostas/*.json` (a palavra do usuário, como foi importada: a direção escolhida e cada rodada; `respostas/recebidas/` guarda o que chegou, inclusive o recusado) → `contratos/04-grill-rodada-*.json` (o que foi perguntado e quais opções existiam) → `contratos/04-grill-consolidado.json` e documentos de contexto (a leitura consolidada, que também pode ter derivado).
3. **Cite a evidência:** arquivo + `pergunta_id` + estado e escolha. Parecer de drift sem citação do grill é opinião.
4. **Divergência confirmada volta ao usuário.** Não se edita o grill para caber no que foi feito, nem se reinterpreta a resposta dele. Se ele quiser mudar a decisão, **pare e reporte**: o motor não aceita outra resposta para rodada já importada e ainda não existe registro de emenda depois do fechamento (lacuna conhecida, a definir junto das etapas seguintes do `ROADMAP.md`). Até lá vale a decisão registrada, e nada é construído sobre a decisão nova.
5. **Grill em silêncio não é autorização:** ponto que o grill não cobriu é lacuna a levar ao usuário, não licença para quem implementa decidir.

Mudou esta lista? Atualize junto o modelo do `.temcomo/LEIA-ME.md` em `lembrete-no-projeto.md`, que é cópia curta dela.
