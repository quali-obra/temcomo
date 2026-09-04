# temcomo

**Do "tem como fazer X?" até uma decisão que você tomou de olhos abertos.**

O temcomo trata o seu pedido como um **sistema de gestão da qualidade**: cada etapa do trabalho é um **procedimento** (uma skill), cada procedimento preenche um **formulário** (um contrato em JSON), e um **motor** confere o formulário antes de deixar a etapa avançar. As decisões chegam até você como **páginas HTML em português claro**, que você abre no navegador com dois cliques, responde e devolve. Nada avança sem o formulário anterior conferido, e **nada é construído antes de você escolher um caminho**.

Feito para quem não é da área técnica. A forma técnica que você sugere é tratada como **hipótese possivelmente errada** — o que manda é o resultado que você quer.

## A jornada, em quatro etapas

| Etapa | O que acontece | O que trava a passagem |
|---|---|---|
| **1. Entender o objetivo** | perguntas curtas até a frase descrever o **resultado**, não o mecanismo | você confirmar que é isso mesmo |
| **2. Pesquisar o que existe** | varre o que já existe — o que a ferramenta já faz de fábrica, o que o projeto original publicou, o que há no GitHub e o que você já tem em casa — antes de propor construir | todo achado com fonte primária, sinal de manutenção e limite |
| **3. Propor direções** | até 4 caminhos reais + no máximo 1 fora da caixa, com custo, complexidade e limite lado a lado | **você escolher uma direção na página** |
| **4. Grill de descoberta** | perguntas de decisão, uma página por rodada, em linguagem leiga | um avaliador independente declarar a cobertura suficiente |

No fim, você tem uma pasta de tarefa que qualquer pessoa (ou agente) consegue reconstituir: o objetivo, o que já existia, os caminhos, a sua escolha e as decisões — cada um com quem produziu e quando.

## As quatro skills

| Skill | Etapa | Quando dispara |
|---|---|---|
| `temcomo` | 1 + condução da jornada | "tem como fazer X?", `/temcomo`, ou um pedido sem especificação fechada |
| `temcomo-pesquisa` | 2 | depois do objetivo confirmado |
| `temcomo-direcoes` | 3 | depois da pesquisa aprovada |
| `temcomo-grill` | 4 | depois de você escolher a direção |

O fluxo não trabalha sozinho: ele aciona **oito ajudantes especializados** (pesquisar aqui dentro, pesquisar na internet, redigir, revisar de forma independente...). As instruções de cada um ficam em [`agents/`](agents/) e não precisam ser instaladas — são entregues ao ajudante no momento em que ele é acionado.

## Instalação

O plugin é o próprio repositório. **Clone e aponte** — não há build nem dependência para instalar (o motor é Python ≥3.9, biblioteca padrão pura).

```bash
git clone https://github.com/quali-obra/temcomo.git
```

Nas receitas abaixo, `/caminho/para/temcomo` é a pasta desse clone.

### Hermes  ✅ testado

Carrega no formato portátil que o Hermes entende (um `plugin.json` na raiz do repositório). Receita completa, incluindo o caso de quem usa vários perfis (*profiles*), e como conferir: [`.hermes-plugin/INSTALACAO.md`](.hermes-plugin/INSTALACAO.md). Resumo:

```bash
export HERMES_HOME=~/.hermes/profiles/<profile>          # ou ~/.hermes, se você não usa profiles
hermes plugins doctor /caminho/para/temcomo --ci          # confere antes de instalar
ln -s /caminho/para/temcomo "${HERMES_HOME:?defina HERMES_HOME}/plugins/temcomo"
HERMES_HOME="${HERMES_HOME:?defina HERMES_HOME}" hermes plugins enable temcomo
```

Instalado e habilitado de verdade num perfil real em 2026-08-20, com as quatro skills sendo carregadas pelo próprio Hermes.

### Claude Code  ✅ testado em ambiente isolado

```bash
claude plugin marketplace add /caminho/para/temcomo
claude plugin install temcomo@temcomo-dev
```

Os arquivos de identificação do plugin ficam em `.claude-plugin/`. Instalado de verdade em 2026-08-22 no CLI real (2.1.239), apontando o programa para uma pasta de configuração temporária (`CLAUDE_CONFIG_DIR`): os comandos acima rodaram como estão escritos, o plugin ficou habilitado e o próprio CLI reconheceu as 4 skills e os 8 ajudantes. Isso prova a receita, **não** a convivência com a configuração que você já tem.

### Codex  ✅ testado em ambiente isolado

O Codex instala plugins a partir de um **marketplace**, que pode ser uma pasta local:

```bash
codex plugin marketplace add /caminho/para/temcomo
codex plugin add temcomo@temcomo-dev
codex plugin list                            # confere que apareceu
```

O arquivo de identificação fica em `.codex-plugin/plugin.json`, apontando a pasta `skills/`. Instalado de verdade em 2026-08-22 no CLI real (0.144.5), apontando o programa para uma pasta de configuração temporária (`CODEX_HOME`): os comandos acima rodaram como estão escritos e o plugin apareceu como "installed, enabled". Mesma ressalva do Claude Code — prova a receita, não a convivência com a sua configuração.

Instalado assim, as skills ficam **sob o nome do plugin** — pelo desenho, elas não devem disputar o nome com um `temcomo` que você já tenha (verificado no Hermes; ainda não testado aqui). Copiar as skills à mão para `~/.codex/skills` é outro caminho — aí elas entram soltas, disputando o nome; veja a nota logo abaixo.

### Cursor  ⏳ formato adicionado (instalação local / team marketplace)

O Cursor reconhece dois formatos de plugin. Este repositório entrega **os dois**:

- **Agent Plugins** (padrão aberto): o `plugin.json` na raiz + a pasta `skills/`
- **Cursor Plugins**: o manifesto em [`.cursor-plugin/plugin.json`](.cursor-plugin/plugin.json), apontando as 4 skills e os 8 prompts em `agents/`

**Team marketplace (recomendado para times):** em *Dashboard → Plugins → Team Marketplaces*, use *Import from Repo* com `https://github.com/quali-obra/temcomo`, revise e adicione o plugin ao marketplace do time.

**Instalação local a partir do clone:**

```bash
# /caminho/para/temcomo é a pasta deste clone
mkdir -p ~/.cursor/plugins/local
ln -s /caminho/para/temcomo ~/.cursor/plugins/local/temcomo
```

Reinicie o Cursor (ou recarregue a janela) e confira em *Customize / Plugins* se `temcomo` apareceu com as 4 skills.

**Marketplace público:** listar em [cursor.com/marketplace](https://cursor.com/marketplace) exige revisão da equipe Cursor — envie o link do repositório em [cursor.com/marketplace/publish](https://cursor.com/marketplace/publish). O manifesto Cursor neste PR habilita essa submissão; **ainda não está listado no marketplace público**.

Os arquivos de identificação do Cursor ficam em `.cursor-plugin/` (além do `plugin.json` na raiz, no formato Agent Plugins).

> **Sobre conviver com uma skill `temcomo` antiga:** instalado **como plugin**, nos programas suportados a skill fica sob o nome do plugin (`temcomo:temcomo` no Claude Code, prefixada no Codex, `agent-plugin-temcomo-<hash>:<skill>` no Hermes; no Cursor, sob o namespace do plugin) — então, pelo desenho, **não deve haver disputa de nome**. Isso foi **verificado no Hermes**, na instalação real num perfil de verdade; no Claude Code, no Codex e no Cursor é o comportamento esperado, mas **ainda não testado** nesses três (o teste em ambiente isolado não exercita convivência). A disputa só existe se você copiar as skills direto para a pasta de skills soltas do programa. Detalhes em [`.hermes-plugin/INSTALACAO.md`](.hermes-plugin/INSTALACAO.md).

## Tour de 5 minutos

Roda a jornada inteira com os dados de exemplo, sem instalar nada. Copie e cole:

```bash
# 0. onde está o plugin, e uma pasta limpa para trabalhar
export TEMCOMO=/caminho/para/temcomo
mkdir -p ~/tour-temcomo && cd ~/tour-temcomo

# 1. abrir a tarefa (a --data deixa o nome da pasta previsível)
python3 "$TEMCOMO/engine/temcomo.py" nova-tarefa "lançar apartamentos Stay" --data 2026-08-19
export TAREFA="$PWD/.temcomo/tarefas/lancar-apartamentos-stay-2026-08-19"

# 2. usar os formulários de exemplo
cp "$TEMCOMO/exemplos/tarefa-stay/contratos/"* "$TAREFA/contratos/"

# 3. conferir e avançar as duas primeiras etapas
python3 "$TEMCOMO/engine/temcomo.py" validar "$TAREFA/contratos/01-objetivo.json"
python3 "$TEMCOMO/engine/temcomo.py" concluir-etapa "$TAREFA" objetivo-confirmado
python3 "$TEMCOMO/engine/temcomo.py" concluir-etapa "$TAREFA" pesquisa-concluida

# 4. gerar as páginas e abrir a de direções no navegador
python3 "$TEMCOMO/engine/temcomo.py" renderizar "$TAREFA/contratos/03-direcoes.json"
python3 "$TEMCOMO/engine/temcomo.py" renderizar "$TAREFA/contratos/04-grill-rodada-1.json"
open "$TAREFA/html/01-direcoes.html"        # no Linux: xdg-open

# 5. devolver as respostas (no uso real, os arquivos vêm da própria página)
python3 "$TEMCOMO/engine/temcomo.py" importar-resposta \
  "$TEMCOMO/exemplos/tarefa-stay/respostas/decisao-direcoes.json" --tarefa "$TAREFA"
python3 "$TEMCOMO/engine/temcomo.py" importar-resposta \
  "$TEMCOMO/exemplos/tarefa-stay/respostas/grill-rodada-1.json" --tarefa "$TAREFA"

# 6. fechar a jornada e ver o registro
python3 "$TEMCOMO/engine/temcomo.py" concluir-etapa "$TAREFA" grill-concluido
python3 "$TEMCOMO/engine/temcomo.py" status "$TAREFA"
```

No fim, o `status` mostra as cinco etapas concluídas, cada uma com o contrato que a liberou. Abra também `02-grill-rodada-1.html`: é a página que o usuário responde no grill.

**Se algum comando não existir** na sua cópia do motor, ele para com "subcomando inexistente"; **se uma opção não existir** (as que aparecem acima são `--data` e `--tarefa`), ele para com "argumentos não reconhecidos". Nos dois casos a mensagem diz o que fazer — nenhuma etapa avança em silêncio.

## O que tem no repositório

```
engine/temcomo.py      o motor: valida, renderiza, importa resposta, mostra status
contracts/             os oito formulários (schemas -v1) + exemplos válidos e inválidos
skills/                as quatro skills
agents/                os oito prompts de subagente
exemplos/tarefa-stay/  uma tarefa completa, pronta para o tour
Prototypes/            as páginas aprovadas que servem de contrato visual
```

Mais: [`RUNBOOK.md`](RUNBOOK.md) (como o processo roda na prática), [`LEARNINGS.md`](LEARNINGS.md) (o diário do que deu certo e do que quebrou), [`LEDGER.md`](LEDGER.md) (registro append-only de cada mudança) e [`ROADMAP.md`](ROADMAP.md) (o que fica para depois do v1). Os identificadores de commit citados nesses registros referem-se ao repositório de trabalho do autor, do qual este repositório público é um recorte.

## O que o temcomo garante

- **As páginas abrem sem internet.** Fontes e logo vão embutidos. A prova que vale é empírica, e leva 30 segundos: **desligue o Wi-Fi** (ou, no navegador, abra as Ferramentas do desenvolvedor → aba *Network*/*Rede* → marque **Offline**) e recarregue a página. Tudo continua no lugar: letras, logo, cores, botões.

  Para uma conferência rápida antes disso, o motor tem a varredura que ele mesmo usa nos próprios testes:

  ```bash
  python3 - "$TAREFA/html/01-direcoes.html" <<'FIM'
  import sys, pathlib, importlib.util, os
  spec = importlib.util.spec_from_file_location("t", os.environ["TEMCOMO"] + "/engine/temcomo.py")
  m = importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
  print(m.problemas_de_rede(pathlib.Path(sys.argv[1]).read_text(encoding="utf-8"), "página") or "nenhum problema de rede")
  FIM
  ```

  Ela procura endereços externos e chamadas de rede no script (`fetch`, `XMLHttpRequest`, `WebSocket`, `sendBeacon`, `EventSource`). **Uma varredura de texto nunca é prova completa** — um endereço montado por pedaços dentro do script escaparia dela. Por isso o teste offline acima é o que decide.

- **Nenhum botão executa nada.** A página coleta a sua decisão; quem executa é o fluxo agêntico, depois do seu aval.
- **Mesmo contrato, mesma página.** O render é determinístico: as datas vêm do contrato, não do relógio.
- **Os gates bloqueiam.** Formulário incompleto ou fora de ordem para a etapa, com o motivo dito em português — nunca "aviso e segue".
- **Dá para auditar.** Todo formulário preenchido por um agente diz quem o produziu — qual agente, qual modelo, e onde está o registro da conversa que o gerou. As respostas que **você** devolve pela página são identificadas como suas (`agente: "usuario"`), sem os campos de agente, porque não houve agente nenhum ali. E cada página carrega, num comentário no topo, a versão do motor e a impressão digital (SHA-256) do formulário que a originou — a resposta que você devolve leva essa mesma impressão digital de volta. O motor confere isso na importação **e em toda leitura posterior da resposta guardada** — inclusive no `status` e no `concluir-etapa`. Ou seja: se alguém mexer no formulário depois de respondido, a tarefa trava na conferência em vez de seguir com as duas versões misturadas; o aviso diz para gerar a página de novo e pedir uma resposta nova, e **nada do que já está guardado é apagado**.

Confira o motor a qualquer momento:

```bash
python3 "$TEMCOMO/engine/temcomo.py" autoteste     # de qualquer pasta, inclusive a do tour
```

## Palavras que aparecem por aqui

Se você não é da área, esta lista resolve quase tudo:

| Palavra | O que quer dizer aqui |
|---|---|
| **skill** | um procedimento escrito: o passo a passo que a IA segue numa etapa |
| **contrato** | o formulário em JSON que a etapa preenche — é o que fica de registro |
| **motor** | o programa que confere os formulários e gera as páginas (`engine/temcomo.py`) |
| **gate** | a tranca entre uma etapa e a seguinte: sem o formulário conferido, não passa |
| **renderizar** | transformar o formulário na página HTML que você abre no navegador |
| **ajudante / subagente** | uma IA acionada para uma tarefa específica dentro do fluxo (pesquisar, redigir, revisar) |
| **instruções / prompt** | o texto que diz a um desses ajudantes o que ele deve e o que ele não pode fazer |
| **perfil (*profile*)** | no Hermes, cada "personalidade" configurada separadamente, com suas próprias ferramentas |
| **marketplace** | a lista de onde o programa busca plugins para instalar — pode ser uma pasta no seu computador |
| **sob o nome do plugin** | a skill instalada fica identificada como `temcomo:temcomo`, e não como um `temcomo` solto — por isso não briga com outra de mesmo nome |
| **registro da conversa** | o arquivo que guarda a sessão da IA, para dar para voltar lá e conferir de onde veio cada coisa |
| **impressão digital (SHA-256)** | um código calculado do arquivo; se um caractere mudar, o código muda — serve para provar que a página veio daquele formulário |

## Estado do projeto

Versão **0.1.0**, cobrindo as etapas 1–4. As etapas seguintes (prototipagem, especificação, issues, PR) estão no [`ROADMAP.md`](ROADMAP.md). Este repositório é público, sem compromisso de suporte, e usa o visual QualiApps por padrão nas páginas.
