# Origem das regras

Referência única de formato: leia antes de escrever, consolidar ou revisar regras, inclusive em brief, documento de contexto, prompt e parecer.

Uma linha de origem por regra, limite, teto, proibição ou uso de **sempre**, **nunca** ou **só** tratado como decisão do dono (o usuário) ou como regra geral. Preserve a linha e o local da fonte em handoffs e resumos de compactação; esses resumos não passam a ser a fonte.

## Formato fixo

Use apenas estes quatro tipos; `dono` tem três formas de localizar a decisão:

```text
origem: dono, <arquivo> §<seção>, <AAAA-MM-DD>, lote <id>, pergunta <id>
origem: dono, grill <tarefa> rodada <N>, pergunta <id>
origem: dono, chat <registro:linha>, <AAAA-MM-DD>, "<fala literal curta>"
origem: prompt do <agente> <versão>
origem: decisão técnica, <papel responsável>, <AAAA-MM-DD>, <motivo curto>
origem: sem registro
```

Na primeira forma, lote ou pergunta inexistentes ficam como `não aplicável`, sem inventar identificador. No grill, `<tarefa>` localiza a pasta da tarefa; confira a pergunta e a resposta importada, seu estado e sua escolha. No chat, `<registro:linha>` localiza a mensagem original preservada, não um resumo dela. Em prompts sem versão própria, use a versão do plugin.

- **Dono:** abra a fonte e confira existência, sentido, força e alcance. Aprovar uma versão inteira de um documento não aprova cada regra dele; só atribua a regra ao dono com decisão específica verificável.
- **Prompt do agente:** restrição de escopo daquele agente, válida só para ele; nunca decisão do dono nem regra geral. Restrição que o agente se impôs também não vira regra geral.
- **Decisão técnica:** autoria técnica explícita, revisável por quem é técnico; não apresente como decisão do dono. Motivo curto não dispensa evidência nem justifica apertar além do objetivo.
- **Sem registro:** não pode sustentar regra do dono ou regra geral; vira achado. Prompt de outro agente, handoff ou resumo de compactação como única fonte também vira achado.

**Mais apertado que o objetivo é defeito:** compare a restrição com o objetivo e as decisões específicas do dono, mesmo que a intenção seja boa. **Caso raro ou lacuna vira problema em aberto para o dono decidir**, não regra nova nem recomendação de restrição. Isso vale também para quem revisa.

## Onde registrar sem mudar schema

Na prosa, junto da regra. Em JSON, use campo textual existente: no consolidado, `decisoes[].evidencia` recebe a linha, preservando as demais evidências e o `pergunta_id`. Se não houver campo adequado, registre em `pesquisas/origens-das-regras.md`, identificando arquivo + campo/ID da regra, e entregue esse mapa na revisão. Não invente chave nem mude schema.

Quem lança a revisão entrega também o objetivo, as fontes citadas e o mapa, quando houver. Fonte ausente ou inacessível não comprova decisão do dono: registre a limitação e peça a fonte, sem presumir aprovação.
