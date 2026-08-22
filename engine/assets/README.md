# engine/assets — identidade QualiApps, byte-preservada

Estes arquivos **não são editáveis à mão**. São recortes byte a byte do protótipo
aprovado em definitivo (decisão 11, 2026-08-20), que é o **contrato visual**
dos templates do motor (spec §12.3). Trocar qualquer byte aqui muda a identidade da
marca em todo relatório gerado — é ato deliberado, que passa por decisão e registro no
LEDGER (spec §10, regra anti-fork).

## Proveniência

| arquivo | o que é | origem | SHA-256 |
|---|---|---|---|
| `tokens.css` | bloco `:root` da página de direções (cores, espaçamentos, raios, sombras) | `Prototypes/01-relatorio-direcoes.html` | `0a6191dbb42a9fca33ca62b7a7d379fdc65e7acf465381b798a0dbd7b33a6568` |
| `fontes.css` | os 8 `@font-face` (Poppins, Barlow, JetBrains Mono) embutidos em base64 | idem | `69d3174f1ca09f88ff5a17ec5e7901a804b2362bfd227b8e81745e99023aae76` |
| `logo-qualiapps.txt` | logotipo QualiApps como `data:` URI (PNG 1638×395) | idem | `7e43f1f5b8716d655d5940d87d94161522bced46189fa5c8ff33946cae7f0cff` |
| `tokens-grill.css` | bloco `:root` da página de grill — os mesmos tokens das direções **mais** a cor de dúvida (roxo QualiClub) | `Prototypes/02-rodada-grill.html` | `e2f799f938982fbca403b42d5151a374ff0255b4f9aa22e7564cc051ecc936ee` |

- **Arquivos de origem:** `Prototypes/01-relatorio-direcoes.html` · SHA-256 `c72562050200a0323e1fc719cf591abb7ebf6d6b6398d7fcd2a7e1762e695f61`
  (decisão 11: `c7256205…5f61`) e `Prototypes/02-rodada-grill.html` · SHA-256 `580c20e20507f3ac9b705a16456ec50dcf8183011c3c4618a7d90d2051648b8e`
  (decisão 11: `580c20e2…8b8e`). As fontes e o logotipo são byte-idênticos nos dois; só os
  tokens diferem, porque o grill declara a cor de dúvida que a página de direções não usa.
- **Fonte canônica upstream:** `iris-design-system/skills/brand/qualiapps-design-system/`
  (tokens.css, logos, manual). O temcomo **copia** e não referencia, para que o HTML
  gerado abra offline com clique duplo.
- **Licenças:** Poppins, Barlow e JetBrains Mono são OFL — podem ser embutidas em
  repositório público. Balloon **nunca** entra em texto: só no logotipo, que é imagem.

## Como conferir

O autoteste do motor compara, a cada execução, o `:root` e os 8 `@font-face` do HTML
renderizado com estes arquivos **e** com o protótipo aprovado, quando ele está presente:

```
python3 engine/temcomo.py autoteste
```
