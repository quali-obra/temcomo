# LEDGER — registro append-only de mudanças

Uma entrada por mudança aplicada em **skill, contrato, motor, prompt de agente ou processo**. Validação que não muda estado vivo não entra aqui — fica no checkpoint da tarefa.

**Append-only:** correção é **entrada nova** citando a anterior; nunca se reescreve uma entrada existente.

**Schema obrigatório de cada entrada:**

`ID (T-AAAAMMDD-NNN)` · `Escopo` · `Estado anterior` · `Mudança aplicada` · `Aprovação` · `Evidência` · `Rollback` · `Resultado`

Entradas de **não conformidade** (algo saiu do processo) usam o mesmo schema, marcadas `NÃO CONFORMIDADE`, e carregam um campo extra: `Ação corretiva (na fonte)`.

---

## T-20261013-001 · Versão pública inicial

- **Escopo:** o repositório inteiro.
- **Estado anterior:** o temcomo era desenvolvido num repositório que passou a ser interno. As entradas `T-…` citadas no `RUNBOOK.md`, nos prompts de agente e nos documentos ficam no histórico desse repositório interno.
- **Mudança aplicada:** recorte do `main` interno em `288c925`, sem o histórico do git:
  - o nome do dono do projeto foi trocado por "dono do projeto";
  - o exemplo usa um sistema fictício, o "Portal Exemplo";
  - saíram as referências a ferramentas, caminhos, pareceres e decisões internas, o plano de implementação e as entradas do `LEARNINGS.md`;
  - os carimbos dos exemplos e o oráculo do autoteste foram recalculados pelo próprio motor;
  - o motor, os templates e os schemas são os mesmos; nos testes do motor, só saíram os literais internos das listas de resíduo.
- **Aprovação:** decisão do dono do projeto, 2026-10-13: separar a versão interna da pública, sem nada interno na pública.
- **Evidência:** `python3 engine/temcomo.py autoteste` no recorte.
- **Rollback:** não se aplica; correção é entrada nova citando esta.
- **Resultado:** versão pública do temcomo, para quem quiser usar.
