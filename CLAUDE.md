# CLAUDE.md — temcomo

Instruções para quem edita este repositório.

## Skill enxuta: contexto só na hora em que é preciso

- O `SKILL.md` carrega só o que **toda** execução da skill precisa: quando entra, regras invioláveis, procedimento, saída e armadilhas.
- O que serve só em parte das execuções — caso especial, conferência de um momento específico, consulta de quem vem depois — vai para `skills/<skill>/referencias/<tema>.md`.
- A skill aponta a referência numa linha que diz **quando** ler: "Suspeitou de drift? Leia `referencias/drift.md` antes de dar parecer." Sem o gatilho, a referência não é lida; copiada na skill, é lida sempre.
- Três níveis, cada um aberto só quando o anterior manda: a `description` do frontmatter diz quando carregar a skill; a skill diz quando abrir a referência; a referência não repete a skill.
- Mudança que acrescenta mais que umas poucas linhas a um `SKILL.md` quase sempre é referência. Antes de escrever na skill, pergunte: toda execução precisa disto?
