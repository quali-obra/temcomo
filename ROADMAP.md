# ROADMAP — o que fica para depois do v1

O v1 cobre as etapas 1–4 (objetivo → pesquisa → direções → grill). O que está aqui **não** está implementado; cada item diz onde encaixa quando chegar a vez. Nada entra sem passar pelo mesmo processo: procedimento (skill) + formulário (contrato `-vN`) + gate do motor.

## Etapas 5–9 do fluxo

### 5. Prototipagem de features
Antes de qualquer implementação com interface, um protótipo HTML estático validado visualmente pelo usuário — o padrão que este próprio plugin seguiu. **Encaixe:** nova skill `temcomo-prototipo`, contrato `prototipo-v1` (o que o protótipo cobre, com quais dados de exemplo) e gate = aprovação visual explícita registrada, com os protótipos virando contrato visual da implementação.

### 6. Especificação e planejamento
Transformar grill + pesquisas em contexto de produto e spec executável. **Encaixe:** `orquestrador-especificacao` em `agents/` (já previsto na corrente da spec §6), consumindo `04-grill-consolidado.json` e os documentos de contexto; contrato `spec-v1` + plano por tasks pequenas com critério de aceite objetivo por task.

### 7. Issues épicas
Quebrar a spec em issues rastreáveis no tracker do projeto, cada uma amarrada à decisão do grill que a originou. **Encaixe:** contrato `issues-v1` com o mapa decisão → issue; o motor gera o corpo das issues, mas **abrir issue é ação externa** e exige aprovação explícita do usuário.

### 8. Integração com o issue-closer
Entregar cada issue ao fluxo agêntico que a implementa, revisa e leva ao PR. **Encaixe:** ponte entre `issues-v1` e o plugin `issue-closer` já existente, preservando o handoff de 6 campos e a rastreabilidade de sessão entre os dois mundos.

### 9. PR e merge
Fechar o ciclo com o PR revisado e o registro do que foi entregue. **Encaixe:** contrato `entrega-v1` com o estado final de cada decisão (`aplicada` / `verificada` / `parcial` / `nao-verificavel`) e entrada no `LEDGER.md`; push e merge continuam exigindo aprovação explícita.

## Evoluções de plataforma

### Servidor MCP (resposta do HTML voltando direto ao agente)
Hoje o usuário baixa o JSON e devolve na conversa. Com um MCP local, o relatório poderia entregar a decisão direto ao agente. **Encaixe:** casca fina sobre o mesmo motor — o MCP chama `validar`/`importar-resposta`, sem lógica nova. **Regra que não muda:** o HTML continua não executando nada; quem executa é o fluxo agêntico depois do gate humano.

### Verificador Playwright opcional (`tools/`)
Renderizar os HTMLs em 1440px e 390px e checar zero erro de console, zero request externo, alvos ≥44px, contraste AA e persistência do rascunho após reload. **Encaixe:** fora do caminho crítico e fora do `autoteste` (que é stdlib pura, sem dependência instalada); entra como **quarta camada** de verificação (depois de autoteste, revisão fresh e protótipos como contrato visual), nunca substituta da revisão fresh.

### Documentação em inglês
README e skills em EN para quem não fala português. **Encaixe:** o conteúdo visível ao usuário é dado dos contratos, então a tradução é da documentação e das skills, com PT-BR permanecendo a língua canônica do projeto; contratos e schemas não mudam.

### Hooks de enforcement por harness
Bloqueio no nível do harness para o que hoje é regra escrita (não pular etapa, não escrever antes da escolha). **Encaixe:** hook `pre_tool_call` que bloqueia — nunca só avisa — consultando `tarefa.json`. **Sem bypass:** o hook é uma camada a mais sobre os gates, não uma alternativa a eles; não existe "pular etapa com justificativa", nem escrever antes da escolha validada do usuário. O único escape previsto é a **falha do próprio hook** (harness sem suporte, hook quebrado): nesse caso valem os gates do motor como sempre valeram, o incidente é reportado ao usuário e registrado — e nada avança de estado por causa disso.

## Dívida técnica conhecida

Medida, com receita e sem bloquear o v1 — cada item diz o que ficou devendo e onde encaixa.

### Infraestrutura comum dos dois templates num módulo único
Os scripts de `engine/templates/direcoes.html.tpl` e `engine/templates/grill.html.tpl` repetem a mesma mecânica — 1.117 e 1.170 linhas, 27 nomes de função compartilhados e 62 linhas em blocos clonados na medição da auditoria cega — e já divergiram na prática: a normalização de IDs restaurados existe num e falta no outro. **Encaixe:** extrair rascunho/`localStorage`, export e anotações para um módulo único embutido nos dois, com **render byte-preservado** como prova (mesmo SHA antes e depois) e o `autoteste` como gate. Na v1 fica como está. Fonte: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/reviews/auditoria-cega-renderizadores.md` (P3, R1/R2).

### Reconciliação `prototipo` × `exemplo` na faixa de dados de exemplo
Ficou em aberto a escolha de **um nome só**: os schemas de direções e de rodada de grill declaram `exemplo` e `prototipo`, o motor acende a tarja com qualquer um dos dois, e a decisão que a Task 3 delegou à Task 5 foi adiada sem registro. **Encaixe:** eleger o canônico (o exemplo publicado já usa `exemplo: true`), unificar motor e templates nele, apertar os schemas num bump de contrato e registrar a escolha no `LEDGER.md`. Fontes: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/checkpoints/motor-task-03.md` (pendência 3) e `motor-task-05.md` (mesma pasta, "Faixa de exemplo condicionada").

### Regeneração do exemplo byte-idêntica
`bash exemplos/gerar-tarefa-stay.sh` devolve `exemplos/tarefa-stay/` byte a byte igual **exceto** os instantes de `tarefa.json` (`gerado_em` e os quatro instantes de conclusão), porque o gerador usa o relógio nas transições — o `LEIA-ME.md` do exemplo já avisa. **Encaixe:** dar ao `importar-resposta` uma opção determinística de instante para a transição automática e chamar `nova-tarefa`, os três `concluir-etapa` e a importação da direção com horários ISO fixos no gerador; aí o `tarefa.json` também fica byte-idêntico, sem edição manual depois do motor. Fonte: `contexto-de-tarefas/criar-plugin-temcomo-2026-08-19/reviews/task-12-codex-r3.md` (achado 2, P2).

## Fora de escopo por ora

- **Outras identidades visuais além da QualiApps**: o motor tem uma cor de marca com dono; submarca é decisão deliberada, não parâmetro solto.
- **Edição de tarefa por interface gráfica**: a pasta de tarefa é feita para ser legível e versionável em git; interface própria só se houver demanda real.
- **Multiusuário/estado compartilhado**: exigiria prova de escritor único (break-before-make) antes de qualquer troca de dono de recurso compartilhado.
