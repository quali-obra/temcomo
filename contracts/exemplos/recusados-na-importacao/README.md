# Exemplos recusados na importação

Respostas que **passam** no `temcomo validar` e mesmo assim são **recusadas** pelo
`temcomo importar-resposta`. Não é contradição: `validar` confere a forma de um
documento sozinho, e estes são bem formados. O que os torna inválidos é uma relação
com outro arquivo — o contrato que os originou —, e essa relação só existe dentro de
uma pasta de tarefa.

Por isso eles não moram em `invalidos/`: lá a regra é "o validador recusa", e ela
continua valendo para todos os arquivos de lá.

| arquivo | por que é recusado |
|---|---|
| `decisao-direcoes-carimbo.json` | `contrato_sha256` não é o do relatório de direções da tarefa |
| `grill-respostas-carimbo.json` | `contrato_sha256` não é o da rodada de grill da tarefa |

Decisão 20 (2026-08-21): a resposta carrega a impressão digital do formulário que foi
respondido, e carimbo divergente bloqueia a importação.
