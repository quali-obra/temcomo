---
name: temcomo-direcoes
description: "Etapa 3 do temcomo — transformar a pesquisa em até 4 caminhos reais (mais no máximo 1 fora da caixa), renderizar o relatório HTML de direções e parar no gate de escolha. Use depois da etapa `pesquisa-concluida`. Nada é instalado, configurado ou escrito antes de o usuário escolher."
version: 0.1.0
---

# temcomo-direcoes — etapa 3

## Quando entra

A tarefa está em `pesquisa-concluida` e o insumo é o `02-pesquisa.json` aprovado. Agora o usuário precisa **escolher um caminho** — com informação suficiente para decidir sozinho, em linguagem leiga.

**Confira antes, e pare se não bater:**

```bash
python3 <raiz-do-plugin>/engine/temcomo.py status .temcomo/tarefas/<tarefa>
```

Etapa diferente de `pesquisa-concluida` = **não comece**: sem pesquisa aprovada não há direção honesta a propor. Reporte o que falta e volte para a etapa anterior; não crie `03-direcoes.json` fora de ordem.

## Dois papéis, duas pessoas (independência da revisão)

Esta etapa tem **um produtor e um lançador**, e eles não podem ser o mesmo agente:

- **Redator das direções** (subagente que você lança): lê o `02-pesquisa.json`, monta o `03-direcoes.json` e devolve handoff de 6 campos com a rastreabilidade da sessão dele.
- **Você, conduzindo a etapa** (skill mestre / orquestrador): não escreve as direções. Você recorta o insumo, lança o redator, **lança o `agents/revisor-adversarial.md`** sobre o que ele produziu, roteia o feedback de volta e opera os gates do motor.

Regra que vem de `agents/revisor-adversarial.md`: **quem produz nunca lança o próprio revisor**. Se você mesmo redigir as direções, não há revisão independente possível nesta etapa — delegue a redação.

## Regra que define esta etapa: o gate de escolha

**Não instale, não configure, não escreva código, não abra PR, não aplique nada antes de o usuário escolher uma direção no HTML.** Esta etapa termina pedindo a escolha — e só. "Tem como...?" e `/temcomo` não são autorização.

## Como montar as direções (`03-direcoes.json`, `direcoes-v1`)

- **Até 4 direções reais + no máximo 1 fora da caixa** (`fora_da_caixa: true`, marcada visualmente). **Nunca invente opção para preencher cota**: se só existem duas saídas honestas, apresente duas.
- **Solução pronta e configuração vêm antes** de skill, plugin ou código novo — a ordem reflete o que a pesquisa achou, não o gosto de quem escreve.
- Cada direção com: `origem` (reuso ou construir), custo, complexidade, **aderência 0–100**, **limite principal** e **explicação leiga de até 1500 caracteres** (o que é, como funciona, o que muda no dia a dia).
- **Critérios de ranking explícitos**, e **integração agêntica sempre entre eles**: depois de pronto, a IA consegue operar isso no dia a dia? Pesa mais em funcionalidade nova, menos em correção.
- **Recomendação com justificativa** apontando uma direção — na página ela aparece **destacada, nunca pré-gravada**: aceitar a recomendação custa 1 clique, e o export distingue "não interagiu" de "escolheu a recomendação".
- Na página, **a lista É a tabela comparativa** (custo, aderência e limite lado a lado); o cartão de cada direção é o aprofundamento.
- Envelope: `schema_version`, `tarefa_id`, `gerado_em`, `produzido_por {agente, modelo, sessao_id, transcript_jsonl}`.

## Procedimento

```bash
# 1. o REDATOR (subagente que você lança) escreve contratos/03-direcoes.json a partir do 02-pesquisa.json
#    e devolve handoff de 6 campos
# 2. VOCÊ opera o gate de forma:
python3 <raiz-do-plugin>/engine/temcomo.py validar .temcomo/tarefas/<tarefa>/contratos/03-direcoes.json
# 3. VOCÊ lança a revisão independente ANTES de mostrar ao usuário — molde agents/revisor-adversarial.md,
#    entregando caminho + SHA-256 do 03-direcoes.json e do 02-pesquisa.json. Critério: as opções são reais?
#    alguma foi inventada para preencher cota? aderência e limite se sustentam na pesquisa? a explicação
#    leiga é entendível por quem não é da área? REQUEST CHANGES volta ao redator — nunca a você.
# 4. só com VEREDITO: APPROVED
python3 <raiz-do-plugin>/engine/temcomo.py renderizar .temcomo/tarefas/<tarefa>/contratos/03-direcoes.json
# 5. entregue o caminho do HTML ao usuário e ESPERE a escolha dele
python3 <raiz-do-plugin>/engine/temcomo.py importar-resposta <arquivo-baixado.json> --tarefa .temcomo/tarefas/<tarefa>
python3 <raiz-do-plugin>/engine/temcomo.py status .temcomo/tarefas/<tarefa>
```

**Barreira de compatibilidade:** confira com `python3 <raiz-do-plugin>/engine/temcomo.py --ajuda` (a ajuda de qualquer subcomando imprime a mesma lista) se ela traz `importar-resposta <arquivo> [--tarefa <pasta>]`. Se não tiver, ou se o comando bloquear, **pare e reporte**: não improvise substituto, não mova o arquivo à mão para `respostas/`, não edite `tarefa.json` e não declare a direção escolhida.

Ao entregar o HTML, diga em duas linhas o que ele decide e que **nenhum botão da página executa nada** — ela só coleta a decisão; ele responde e devolve por "copiar resposta" ou "baixar arquivo". O `importar-resposta` recusa export com decisão `pendente`: recusa é para ser lida ao usuário e resolvida na origem, **nunca contornada editando o JSON dele**. Quando ele é o gate, é o próprio `importar-resposta` que leva a tarefa a `direcao-escolhida` — confirme no `status` e não rode transição de novo.

## O que volta na resposta

O export (`decisao-direcoes-v1`) traz, no topo do envelope, o **carimbo `contrato_sha256`**: a impressão digital do `03-direcoes.json` que gerou a página. O `importar-resposta` confere esse carimbo contra o contrato que está na pasta e **recusa** se o formulário mudou depois de respondido. A conferência **não acontece só na importação**: toda leitura posterior da resposta guardada reconfere o vínculo — `status` e `concluir-etapa` inclusive —, então mexer no `03-direcoes.json` depois de respondido trava a tarefa até a situação ser resolvida. Em nenhum desses casos algo é apagado — nesse caso, renderize de novo, peça a resposta outra vez e importe; nada do que já está guardado é apagado. Não conserte a divergência editando o arquivo do usuário.

O `03-direcoes.json` precisa **continuar na pasta** na hora de importar: é contra ele que o motor confere o carimbo e verifica se o caminho escolhido é mesmo um dos oferecidos. Dois problemas diferentes, dois remédios diferentes: se o motor disser que a resposta veio de **uma versão diferente** do relatório, renderize de novo, peça a resposta outra vez e importe; se disser que **não encontrou** o `03-direcoes.json`, o relatório saiu da pasta — recoloque-o (ele é o registro da etapa 3, não um arquivo descartável) em vez de gerar um novo, que teria outro carimbo e invalidaria a resposta que o usuário já deu.

O export traz também `anotacoes[]` — comentários presos a trechos do relatório, obrigatórios desde o `-v1` (aceita lista vazia). **Anotação marcada como órfã é preservada e respondida, jamais descartada**; a autoridade da âncora é o `trecho`, não os offsets. Cada anotação é insumo: ou vira ajuste na direção, ou vira pergunta no grill.

## Saída da etapa

`contratos/03-direcoes.json` validado · `html/NN-direcoes.html` (imutável; render novo = arquivo novo) · `respostas/decisao-direcoes.json` importado · tarefa em `direcao-escolhida` · handoff de 6 campos com a rastreabilidade da sessão e do transcript JSONL de quem produziu.

## Armadilhas

1. **Decisão fantasma:** deixar a recomendação pré-marcada e tratar silêncio como escolha.
2. **Cota inventada:** cinco cartões porque "cinco fica melhor".
3. **Textão antes da tabela:** o comparativo curto vem primeiro; a explicação leiga depois.
4. **Direção que não veio da pesquisa:** cada caminho precisa se apoiar em achado do `02-pesquisa.json` — inclusive o fora da caixa, que é criativo, não inventado.
5. **Começar a construir "enquanto ele decide".** O gate de escolha é o ponto inteiro desta etapa.
6. **Escolher pelo usuário** quando ele responde "o que você acha melhor?": explique o trade-off, recomende, e continue esperando o clique.
