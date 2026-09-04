
## T-20260904-001 · Manifesto Cursor (`.cursor-plugin/`) e receita de instalação

- **Escopo:** adicionar o manifesto Cursor em `.cursor-plugin/plugin.json` (skills + agents) e a seção **Cursor** no `README.md` (team marketplace, instalação local, nota sobre marketplace público). Não altera motor, contratos nem skills.
- **Estado anterior:** o repositório público já tinha `plugin.json` (Agent Plugins), `.claude-plugin/` e `.codex-plugin/`, mas não tinha manifesto Cursor nem receita de instalação no README.
- **Mudança aplicada:** criado `.cursor-plugin/plugin.json` apontando as 4 skills e `./agents/`; README ganhou seção Cursor e a nota de convivência de nomes passou a mencionar o Cursor.
- **Aprovação:** pedido explícito do dono (Lucas) para abrir PR habilitando instalação no Cursor.
- **Resultado:** o repositório fica instalável no Cursor via team marketplace / plugin local; listagem no marketplace público continua pendente de submissão em cursor.com/marketplace/publish.
