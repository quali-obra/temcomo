# engine/assets — identidade QualiApps, byte-preservada

Estes arquivos **não são editáveis à mão**. São recortes byte a byte do protótipo
aprovado em definitivo (2026-08-20), que é o **contrato visual**
dos templates do motor (spec §12.3). Trocar qualquer byte aqui muda a identidade da
marca em todo relatório gerado — é ato deliberado, que passa por decisão e registro no
LEDGER (spec §10, regra anti-fork).

## Proveniência

| arquivo | o que é | origem | SHA-256 |
|---|---|---|---|
| `tokens.css` | bloco `:root` da página de direções (cores, espaçamentos, raios, sombras) | protótipo da página de direções | `0a6191dbb42a9fca33ca62b7a7d379fdc65e7acf465381b798a0dbd7b33a6568` |
| `fontes.css` | os 8 `@font-face` (Poppins, Barlow, JetBrains Mono) embutidos em base64 | idem | `69d3174f1ca09f88ff5a17ec5e7901a804b2362bfd227b8e81745e99023aae76` |
| `logo-qualiapps.txt` | logotipo QualiApps como `data:` URI (PNG 1638×395) | idem | `7e43f1f5b8716d655d5940d87d94161522bced46189fa5c8ff33946cae7f0cff` |
| `tokens-grill.css` | bloco `:root` da página de grill — os mesmos tokens das direções **mais** a cor de dúvida (roxo) | protótipo da página de grill | `e2f799f938982fbca403b42d5151a374ff0255b4f9aa22e7564cc051ecc936ee` |

- **Arquivos de origem:** os dois protótipos aprovados, que ficam no repositório de trabalho
  do autor e não são publicados. As fontes e o logotipo são byte-idênticos nos dois; só os
  tokens diferem, porque o grill declara a cor de dúvida que a página de direções não usa.
- **Fonte canônica upstream:** o sistema de design interno da QualiApps (não publicado)
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
