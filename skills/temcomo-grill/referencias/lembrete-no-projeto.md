# Lembrete no projeto

Referência da skill `temcomo-grill`: lida **no fechamento**, com a etapa já em `grill-concluido`. Serve para o projeto "lembrar" onde estão as decisões do usuário, mesmo para o agente que trabalha nele sem o plugin temcomo instalado.

## 1. Em que projeto o lembrete entra

No projeto onde a implementação vai acontecer — por padrão, este, onde está o grill. Se o usuário disser que a implementação é em outro repositório (ex.: issues num repositório, grill em outro), o lembrete entra **naquele**, apontando para o repositório e o caminho do grill. Os dois arquivos abaixo vão sempre para o mesmo projeto: o trecho aponta para o `LEIA-ME.md` que mora ao lado dele.

## 2. `.temcomo/LEIA-ME.md` — as regras, dentro do projeto

Grave o modelo abaixo em `.temcomo/LEIA-ME.md` do projeto escolhido, trocando:

- `<versão>` pelo `version:` do `SKILL.md` desta skill;
- `<pasta-das-tarefas>` por `` `.temcomo/tarefas/` `` (grill neste projeto) ou por `` `<caminho>/.temcomo/tarefas/` do repositório `<dono>/<repo>` `` (grill em outro repositório).

Quando gravar:

- **Projeto do grill:** grave no fechamento — `.temcomo/` é a pasta da skill.
- **Outro repositório:** é escrita fora do projeto do grill; entra só com a aprovação do usuário, junto com o trecho do passo 3.
- **Já existe:** igual ao modelo desta versão → nada a fazer; diferente → mostre a diferença e só substitua com o aval do usuário.
- **Depois de gravar:** `git check-ignore -v .temcomo/LEIA-ME.md` não pode imprimir nada; imprimiu → pare e reporte a regra do `.gitignore`.

~~~markdown
# Decisões do usuário (temcomo)

> Cópia curta de `skills/temcomo-grill/referencias/drift.md`, do plugin temcomo (https://github.com/quali-obra/temcomo), skill `temcomo-grill` <versão>. A fonte é aquele arquivo: este não se edita à mão.

Leia antes de revisar ou julgar uma implementação, e sempre que suspeitar que ela se afastou do que o usuário decidiu (drift).

1. **Ache a tarefa:** cada pasta em <pasta-das-tarefas> é uma tarefa (`<assunto>-<aaaa-mm-dd>`). Procure o assunto com `grep -ril "<termo>"` nessa pasta.
2. **Leia na ordem de autoridade:** `contratos/01-objetivo.json` (o objetivo manda) → `respostas/*.json` (a palavra do usuário, como foi importada; `respostas/recebidas/` guarda o que chegou, inclusive o recusado) → `contratos/04-grill-rodada-*.json` (o que foi perguntado e quais opções existiam) → `contratos/04-grill-consolidado.json` (a leitura consolidada, que também pode ter derivado).
3. **Só resposta `aprovada` com opção escolhida (`escolha_id`) decide o que fazer.** `rejeitada` recusa o que foi oferecido e não escolhe nada no lugar; `duvida`, `adiada` e `pendente` não decidem nada — é pergunta para o usuário, mesmo que o consolidado diga outra coisa. Na direção, vale a `direcao_escolhida` de `respostas/decisao-direcoes.json` (`estado: decidida`).
4. **Cite a evidência:** arquivo + `pergunta_id`. Parecer de drift sem essa citação é opinião.
5. **Divergência confirmada volta ao usuário.** Não edite o grill para caber no que foi feito nem reinterprete a resposta dele; se o usuário quiser mudar uma decisão, pare e reporte.
6. **Grill em silêncio não é autorização:** o que o grill não cobriu é pergunta para o usuário, não decisão de quem implementa.
~~~

## 3. Trecho para o `CLAUDE.md` e/ou `AGENTS.md` — proposta, nunca escrita direta

Mostre ao usuário o trecho e o arquivo onde ele entraria. **Só escreva depois da aprovação explícita dele.** Recusou? Nada entra, e diga que o `.temcomo/LEIA-ME.md` continua lá para quem procurar.

- **Os dois arquivos existem:** proponha nos dois — o Claude Code lê o `CLAUDE.md`; Codex, Cursor e outros, o `AGENTS.md`. Se um importa o outro (ex.: `@AGENTS.md` no `CLAUDE.md`), basta no importado.
- **Nenhum existe:** pergunte em qual criar.
- **Já há um trecho do temcomo, de tarefa anterior:** proponha acrescentar a tarefa nova nele, não um segundo bloco.

~~~markdown
## Decisões do usuário (temcomo)

As decisões do usuário para este projeto estão em `.temcomo/tarefas/<tarefa>/`. Antes de revisar ou julgar uma implementação, e sempre que suspeitar que ela se afastou do que foi decidido, leia `.temcomo/LEIA-ME.md`.
~~~

Grill em outro repositório: a primeira frase vira "As decisões do usuário para este projeto estão no repositório `<dono>/<repo>`, em `<caminho>/.temcomo/tarefas/<tarefa>/`."

O trecho não copia regra: as regras moram no `LEIA-ME.md`, e o trecho só diz onde está e quando ler.
