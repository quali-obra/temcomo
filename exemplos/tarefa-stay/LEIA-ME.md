# Tarefa de exemplo — "lançar apartamentos Stay"

Esta é uma **pasta de tarefa completa**, do jeito que o motor a produz: os formulários preenchidos, as duas respostas devolvidas pelo usuário e o `tarefa.json` com a jornada inteira registrada — de `criada` até `grill-concluido`.

**Tudo aqui é dado de exemplo**, inclusive a rastreabilidade: a sessão é `exemplo-ficticio-0001` e o caminho do registro da conversa é `/caminho/de/exemplo/...`. Nenhum dado real de máquina ou de pessoa viaja neste repositório público.

## O que tem aqui

```
tarefa.json                            a jornada: etapa atual + histórico de cada tranca vencida
contratos/01-objetivo.json             o resultado desejado, em linguagem leiga
contratos/02-pesquisa.json             o que já existe, com fonte e limite de cada achado
contratos/03-direcoes.json             os caminhos possíveis + a recomendação
contratos/04-grill-rodada-1.json       as perguntas da rodada 1
contratos/04-grill-consolidado.json    as decisões fechadas, com estado por decisão
contratos/contexto-regras-lancamento.md  o documento de contexto que o grill gerou
respostas/decisao-direcoes.json        a escolha do usuário, exportada da página
respostas/grill-rodada-1.json          as respostas do grill, exportadas da página
html/                                  vazio de propósito — as páginas você gera com `renderizar`
pesquisas/                             vazio de propósito — material bruto dos pesquisadores
```

`html/` e `pesquisas/` trazem um `.gitkeep` só para existirem depois de um clone (o git não versiona pasta vazia, e o motor recusa a tarefa se faltar alguma). `html/` não vem preenchido porque cada página tem ~1,6 MB — fontes e logo embutidos, para abrir sem internet — e o motor as regera idênticas a partir do contrato. Gerá-las é justamente o passo 4 do tour do `README.md`.

Cada uma das duas respostas carrega, no topo, o **carimbo `contrato_sha256`**: a impressão digital do formulário que ela responde. Como o exemplo é saneado (rastreabilidade fictícia e datas do cenário), o carimbo é **recalculado** pelo gerador sobre o contrato já saneado — se ele viesse da origem, apontaria para um formulário que não existe mais aqui e o `importar-resposta` recusaria, com razão.

## Como esta pasta foi feita

Por um script, rodando o motor de verdade — nenhum JSON foi escrito à mão:

```bash
bash exemplos/gerar-tarefa-stay.sh
```

Ele parte dos contratos de `contracts/exemplos/validos/`, aplica um saneamento explícito (rastreabilidade fictícia, datas coerentes e duas correções de coerência interna herdadas da origem) e deixa o motor conduzir a jornada: `validar` + `concluir-etapa` nas etapas de formulário, `importar-resposta` nas duas em que a resposta do usuário é a tranca. O cabeçalho do script explica cada decisão.

Uma observação sobre as datas: a tarefa é de 19/08 e os formulários trazem datas do cenário, mas as marcas de conclusão no `tarefa.json` são do momento em que o exemplo foi gerado — cada uma depois da anterior e depois do formulário que a liberou.
