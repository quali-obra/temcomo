#!/usr/bin/env bash
# Gera exemplos/tarefa-stay/ rodando o motor de verdade.
#
# Por que existe: a pasta de exemplo precisa ser reprodutível e auditável — nenhum JSON
# dela é escrito à mão. O script parte dos contratos de contracts/exemplos/validos/,
# aplica um saneamento explícito (abaixo) e deixa o motor produzir a jornada.
#
# Saneamento aplicado aos contratos antes de entrarem no exemplo:
#   1. produzido_por → rastreabilidade FICTÍCIA e rotulada. Os arquivos de origem
#      carregam a sessão e o transcript reais de quem os escreveu; este repositório é
#      público, então sessão, caminho e nome de usuário não podem viajar junto.
#   2. gerado_em → linha do tempo fictícia coerente: cada contrato nasce ANTES da etapa
#      que ele libera, e uma etapa nunca termina antes da anterior.
#   3. duas correções de coerência interna herdadas da origem: a justificativa da
#      recomendação citava caminhos "C" e "D" que não existem no contrato, e o
#      consolidado apontava para um documento de contexto que não existia.
#   4. contrato_sha256 das respostas → RECALCULADO. O carimbo é o SHA da forma
#      canônica do contrato respondido, e o saneamento (1 e 2) muda essa forma — o
#      carimbo herdado da origem apontaria para um contrato que não existe mais aqui,
#      e o `importar-resposta` recusaria, com razão. O recálculo usa a mesma função do
#      motor (`sha_do_contrato`), nunca uma reimplementação.
#
# Uso:  bash exemplos/gerar-tarefa-stay.sh
set -euo pipefail

REPO="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
MOTOR="$REPO/engine/temcomo.py"
DESTINO="$REPO/exemplos/tarefa-stay"
TRABALHO="$(mktemp -d)"
trap 'rm -rf "$TRABALHO"' EXIT

SESSAO="exemplo-ficticio-0001"
TRANSCRIPT="/caminho/de/exemplo/sessoes/exemplo-ficticio-0001.jsonl"
AGENTE="temcomo-exemplo (documentação do plugin)"

# ── 1. contratos saneados ────────────────────────────────────────────────────
python3 - "$REPO" "$TRABALHO" "$SESSAO" "$TRANSCRIPT" <<'PY'
import importlib.util, json, pathlib, sys
repo, trabalho, sessao, transcript = (pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2]),
                                      sys.argv[3], sys.argv[4])
origem = repo / "contracts" / "exemplos" / "validos"

# o carimbo das respostas é recalculado com a MESMA função do motor — nunca com uma
# reimplementação, que sairia do ar no dia em que a forma canônica mudasse
spec = importlib.util.spec_from_file_location("temcomo", repo / "engine" / "temcomo.py")
motor = importlib.util.module_from_spec(spec); spec.loader.exec_module(motor)

# resposta → contrato que ela responde (o carimbo aponta para este)
CARIMBO = {
    "decisao-direcoes.json": "03-direcoes.json",
    "grill-rodada-1.json":   "04-grill-rodada-1.json",
}

# nome de destino → (arquivo de origem, gerado_em fictício)
plano = {
    "01-objetivo.json":           ("objetivo.json",          "2026-08-19T10:00:00-04:00"),
    "02-pesquisa.json":           ("pesquisa.json",          "2026-08-20T09:00:00-04:00"),
    "03-direcoes.json":           ("direcoes.json",          "2026-08-20T15:00:00-04:00"),
    "04-grill-rodada-1.json":     ("grill-rodada.json",      "2026-08-21T10:00:00-04:00"),
    "04-grill-consolidado.json":  ("grill-consolidado.json", "2026-08-21T14:00:00-04:00"),
    "decisao-direcoes.json":      ("decisao-direcoes.json",  "2026-08-21T09:00:00-04:00"),
    "grill-rodada-1.json":        ("grill-respostas.json",   "2026-08-21T11:30:00-04:00"),
}

for destino, (arquivo, gerado_em) in plano.items():
    dado = json.loads((origem / arquivo).read_text(encoding="utf-8"))
    dado["gerado_em"] = gerado_em
    pp = dado.get("produzido_por")
    if isinstance(pp, dict) and "sessao_id" in pp:      # exports do usuário só têm 'agente'
        pp["sessao_id"] = sessao
        pp["transcript_jsonl"] = transcript
    # correção 3a — a justificativa citava caminhos que não estão no contrato
    rec = dado.get("recomendacao")
    if isinstance(rec, dict) and "justificativa" in rec:
        letras = {d.get("letra") for d in dado.get("direcoes", [])}
        if "C" not in letras and "Os caminhos B e C" in rec["justificativa"]:
            rec["justificativa"] = (
                "O caminho A é o único que entrega exatamente o que foi pedido — lançar pelo "
                "chat — com nota máxima em integração agêntica e a maior aderência da lista "
                "(92 de 100), a um custo médio. O caminho E pontua quase igual em integração "
                "agêntica, mas custa mais e depende de peças externas (canal WhatsApp, "
                "corretores); funciona melhor como evolução futura do A. O caminho B é o mais "
                "barato, porém deixa o chat de fora do fluxo — melhora o processo atual sem "
                "responder à pergunta.")
    # correção 4 — carimbo recalculado sobre o contrato JÁ SANEADO
    if destino in CARIMBO:
        respondido = json.loads((trabalho / CARIMBO[destino]).read_text(encoding="utf-8"))
        dado["contrato_sha256"] = motor.sha_do_contrato(respondido)
    (trabalho / destino).write_text(
        json.dumps(dado, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

# correção 3b — o documento de contexto que o consolidado promete passa a existir
(trabalho / "contexto-regras-lancamento.md").write_text("""# Regras de lançamento de apartamento

> Documento de contexto gerado pelo grill — dados de exemplo.

O que **trava** um lançamento (sem isto, não vai ao ar):

- unidade (número e prédio)
- tipo (studio, 1 quarto, ...)
- valor da diária
- pelo menos uma foto

O que é **opcional** e pode entrar depois: descrição longa, comodidades, regras da casa,
fotos adicionais.

Quem aprova: o lançamento entra como rascunho e só publica com o aval de quem cuida do
anúncio — o agente nunca publica sozinho.
""", encoding="utf-8")
print("contratos saneados em", trabalho)
PY

# ── 2. a jornada, pelo motor ─────────────────────────────────────────────────
cd "$TRABALHO"
python3 "$MOTOR" nova-tarefa "lançar apartamentos Stay" --data 2026-08-19 --raiz "$TRABALHO" \
  --agente "$AGENTE" --modelo "claude-fable-5" --sessao "$SESSAO" --transcript "$TRANSCRIPT" >/dev/null
TAREFA="$TRABALHO/.temcomo/tarefas/lancar-apartamentos-stay-2026-08-19"

cp "$TRABALHO"/0*.json "$TAREFA/contratos/"
cp "$TRABALHO/contexto-regras-lancamento.md" "$TAREFA/contratos/"

# as etapas concluídas por contrato usam o relógio (sem --data), o que mantém a jornada
# em ordem: cada marca cai depois da anterior e depois do contrato que a liberou
python3 "$MOTOR" validar "$TAREFA/contratos/01-objetivo.json" >/dev/null
python3 "$MOTOR" concluir-etapa "$TAREFA" objetivo-confirmado --por "$AGENTE" >/dev/null
python3 "$MOTOR" validar "$TAREFA/contratos/02-pesquisa.json" >/dev/null
python3 "$MOTOR" concluir-etapa "$TAREFA" pesquisa-concluida --por "$AGENTE" >/dev/null
python3 "$MOTOR" validar "$TAREFA/contratos/03-direcoes.json" >/dev/null
python3 "$MOTOR" importar-resposta "$TRABALHO/decisao-direcoes.json" --tarefa "$TAREFA" >/dev/null
python3 "$MOTOR" validar "$TAREFA/contratos/04-grill-rodada-1.json" >/dev/null
python3 "$MOTOR" importar-resposta "$TRABALHO/grill-rodada-1.json" --tarefa "$TAREFA" >/dev/null
python3 "$MOTOR" validar "$TAREFA/contratos/04-grill-consolidado.json" >/dev/null
python3 "$MOTOR" concluir-etapa "$TAREFA" grill-concluido --por "$AGENTE" >/dev/null

# ── 3. publicar no repositório ───────────────────────────────────────────────
# o LEIA-ME é escrito à mão e sobrevive à regeneração — só o que o motor produz é trocado
LEIAME_GUARDADO=""
[ -f "$DESTINO/LEIA-ME.md" ] && LEIAME_GUARDADO="$TRABALHO/LEIA-ME.md.guardado" && cp "$DESTINO/LEIA-ME.md" "$LEIAME_GUARDADO"
rm -rf "$DESTINO"
mkdir -p "$DESTINO"
[ -n "$LEIAME_GUARDADO" ] && cp "$LEIAME_GUARDADO" "$DESTINO/LEIA-ME.md"
cp "$TAREFA/tarefa.json" "$DESTINO/"
cp -R "$TAREFA/contratos" "$DESTINO/contratos"
cp -R "$TAREFA/respostas" "$DESTINO/respostas"
# git não versiona pasta vazia: sem estes marcadores, a pasta chega incompleta num
# clone novo e o motor recusa o `status`
mkdir -p "$DESTINO/html" "$DESTINO/pesquisas"
printf '# as páginas ficam aqui — gere com: temcomo renderizar <contrato>\n' > "$DESTINO/html/.gitkeep"
printf '# o material bruto dos pesquisadores fica aqui\n' > "$DESTINO/pesquisas/.gitkeep"

python3 "$MOTOR" status "$DESTINO" | sed 's/^/  /'
echo
echo "OK — exemplo regenerado em $DESTINO"
