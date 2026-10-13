# LEARNINGS — diário operacional do temcomo

Diário, não arquivo morto. Cada entrada nasce de algo que **aconteceu de verdade** e diz **o quê** e **por quê**.

## Como usar

- **Formato:** `### AAAA-MM-DD — título curto` + 1–5 linhas objetivas + `**Status:**`.
- **Status:** `pendente` (observado, ainda não virou regra) · `promovida (→ destino)` (virou regra em skill, RUNBOOK, motor ou prompt de agente) · `[SUPERADA AAAA-MM-DD]` (envelheceu ou foi contrariada).
- **Escreva quando:** um fluxo terminou com aprendizado reutilizável, uma suposição quebrou, um gate falhou, uma ferramenta se comportou diferente do documentado, ou o usuário deu instrução nova.
- **Regra de poda:** entrada `promovida` fica aqui **até a próxima limpeza**, com o destino nomeado — depois sai (a regra vive no destino, não no diário). Entrada superada é marcada, não apagada em silêncio. Se o arquivo passar de ~2 telas, consolide.
- **Gate de evolução:** aprendizado **não** vira mudança sozinho. Registre `pendente` → proponha o diff → **aprovação explícita do usuário** → aplique com bump semver + entrada no `LEDGER.md`.

---
