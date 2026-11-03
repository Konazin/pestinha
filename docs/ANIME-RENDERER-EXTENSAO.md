# Próximo marco gráfico — pontos de extensão para o renderer de sprites (planejamento)

> **Somente planejamento.** Nada aqui foi implementado nem testado. Complementa o ADR 001 (`Proposed`) e o marco M3
> do roadmap. **Não** inclui a personagem, arte, nem mudanças em `core/` (SNN), física, emoções ou memória.
> Referências de linha são do `main` em 2026-11-03 e podem mudar.

## O que o renderer atual lê (a fronteira a preservar)

| Entrada | Origem | Campos usados em `PetWindow.paintEvent` / `draw_face` |
|---|---|---|
| `PetState` (`body/pet_state.py`) | escrito por app/behavior/pet | `emotion`, `shape` (olhos suavizados), `gaze`, `shake`, `tone.sway()`, `blink_until`, `feliz_fechado()`, `desk_top`, `show_label` |
| `Body` (`core/physics.py`) | física | `angle`, `grounded`, `held` (posição vira `move()`; o desenho usa só o ângulo) |
| `Aparencia` (`body/desenho_rosto.py`) | `pets/<id>.json` → `aparencia_de()` | cores e acessórios do pet |

`PetState`, `Body` e as interfaces com o cérebro (`app.py` → `PetState`) **não mudam**.

## Pontos de extensão (do mais barato ao mais invasivo)

1. **`paintEvent` entre `p.save()` e `p.restore()` (`pet.py:153–161`)** — hoje chama `draw_face(...)` e `draw_zzz(...)`.
   É o único ponto que sabe *como* desenhar. Substituir por `self.renderer.desenhar(p, quadro)` com o renderer vetorial
   como implementação padrão mantém o comportamento idêntico.
2. **Quadro de entrada (`QuadroPet`, novo, só leitura)** — monta, a cada `paintEvent`, os valores acima já
   resolvidos (tremor/balanço/respiração e o ângulo hoje calculados dentro de `paintEvent`; o recorte do
   notebook `desk_top`). Evita que o renderer de sprites reimplemente `random`/`sin` do `pet.py`.
3. **`animate()` (`pet.py:112`)** — suavização de `shape` e piscar ficam no `PetWindow`; o renderer de sprites os
   *consome* (mapeia `emotion` + `shape` → estado de sprite), não os recalcula.
4. **`Aparencia`/`aparencia_de`** — o JSON do pet já valida cores/acessórios; um campo opcional (ex.: `renderer`)
   escolheria `vetorial` (padrão) ou `sprites`. Pets sem o campo continuam vetoriais.
5. **Ícone da bandeja e do diálogo (`ui/ui.py:51 face_icon`)** — também chama `draw_face`; manter o vetorial até haver
   um quadro estático de sprite. Não pode importar o renderer da camada `body` na ordem errada
   (`tests/test_arquitetura.py`: `body < … < ui`; `ui` pode importar `body`).
6. **Região opaca** — hoje **não existe** (`PetWindow` não usa `setMask`; o clique atravessa por alfa em X11/Windows).
   O contrato deve devolver a região opaca ao lado do desenho, porque o M1-X e o Wayland nativo a exigem.
   Só deve ser aplicada se o M1-X mostrar necessidade (T20–T22, T41–T42).

## Contrato proposto (PROPOSTA)

```text
Renderer.desenhar(p: QPainter, quadro: QuadroPet) -> None
Renderer.regiao_opaca(quadro: QuadroPet) -> QRegion | None     # None = não informar
Renderer.tamanho() -> (w, h)                                    # hoje LADO_JANELA_PET (WIN)
```

- `QuadroPet` é imutável e contém apenas leitura de `PetState`/`Body`/`Aparencia`; o renderer **não escreve** neles.
- Implementações: `VetorialLegado` (envolve `draw_face`/`draw_zzz`, sem alterar o desenho) e, depois, `SpritesProvisorio`.
- Camada: `body/` (abaixo de `world`, `mind`, `ui`); sem importar `core/` além do que `body` já importa.

## Sequência sugerida (cada passo = um PR pequeno, com aprovação)

1. **Extração sem mudança de pixel:** `VetorialLegado` + `QuadroPet`; teste de equivalência (renderizar `QImage`
   offscreen antes/depois, comparar bytes) para as 9 emoções de `EYE_SHAPES` e os pets existentes.
2. **Teste de contrato** do `Renderer` (só leitura, tamanho, região opaca coerente com o alfa).
3. **Mapeamento `emotion` → estado de sprite** (tabela + testes de cobertura de `EYE_SHAPES`/`EMOTION_NAMES`).
4. **`SpritesProvisorio`** com atlas de teste (retângulos coloridos, **sem arte da personagem**) atrás do campo `renderer`.
5. Só então a personagem provisória (M3) e a arte final (M4).

## Riscos

- Os testes atuais rodam em `offscreen`: a equivalência de pixel é válida, mas **não** prova nada sobre XWayland/KDE.
- DPI fracionário: sprites precisam de escala com suavização; validar junto com T26–T27 do M1-X.
- `random` no `paintEvent` (tremor) torna a comparação de pixel não determinística; fixar a semente ou injetar o jitter no `QuadroPet`.
