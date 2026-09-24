# Onde o grill mora

Referência da skill `temcomo-grill`: lida **antes da rodada 1** e **no fechamento**.

O grill é o registro das decisões do usuário e a referência de tudo o que vem depois — por isso fica **dentro do projeto**, na pasta da tarefa: `<raiz-do-projeto>/.temcomo/tarefas/<tarefa>/`, onde `<raiz-do-projeto>` é a raiz do repositório em que a conversa acontece. **Nunca** em `/tmp`, scratchpad do harness ou `Downloads`: o que está lá some com a sessão, e depois ninguém consegue conferir o que foi decidido. A orientação de harness de "usar o scratchpad para arquivo temporário" vale para rascunho descartável — artefato do grill não é descartável.

- **Antes da rodada 1**, confira pelo `status` que a pasta da tarefa está dentro do projeto. Está em pasta temporária? **Pare e reporte ao usuário**: trazer a tarefa para o projeto é decisão dele, e move-se a pasta inteira, nunca arquivo a arquivo.
- **Na mesma hora**, confira que o git não ignora nenhum tipo de arquivo do grill — um caminho de amostra para cada tipo da tabela abaixo, rodado na raiz do projeto (o arquivo ainda não precisa existir):

  ```bash
  T=.temcomo/tarefas/<tarefa>
  git check-ignore -v "$T/tarefa.json" "$T/contratos/04-grill-rodada-1.json" "$T/html/01-grill-rodada-1.html" \
    "$T/respostas/grill-rodada-1.json" "$T/respostas/recebidas/grill-rodada-1.json" "$T/pesquisas/avaliacao-rodada-1.md"
  ```

  Saiu alguma linha (exit 0)? Uma regra do `.gitignore` — `.temcomo/`, `.*/`, `*.html`, `respostas/`… — esconde parte do grill do versionamento: **pare e reporte** a regra ao usuário; abrir exceção é decisão dele. No fechamento, a conferência é sobre o que foi de fato gravado (seção abaixo).
- Todo subagente recebe o **caminho absoluto** da pasta da tarefa e grava ali; caminho fora dela no handoff volta a quem produziu. Exceção: subagente em worktree isolado (`RUNBOOK.md` §4) recebe antes uma cópia da pasta da tarefa no mesmo caminho relativo do worktree (o que não foi commitado não aparece lá), entrega no worktree, e o orquestrador traz de volta, byte a byte, só o que ele produziu, antes de qualquer gate — o que fica só no worktree não conta como grill. Isso vale para os subagentes que o orquestrador lança; o próprio orquestrador nunca roda em worktree isolado, porque opera o motor e o `tarefa.json` da pasta da tarefa.

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

## No fechamento, antes do `concluir-etapa`

Confira, na raiz do projeto, que o git não ignora nada do que foi de fato gravado — o comando tem de sair vazio:

```bash
git ls-files --others --ignored --exclude-standard .temcomo/tarefas/<tarefa>/
```

Listou algum arquivo? Ele está sendo ignorado pelo git: **pare e reporte** a regra ao usuário antes do `concluir-etapa`.
