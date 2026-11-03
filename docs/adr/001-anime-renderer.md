# ADR 001 — Renderer do pet anime

- **Status:** Proposed (não aprovado; sem decisão final)
- **Data:** 2026-11-03
- **Escopo:** apenas a proposta; nenhuma implementação em M0

## Contexto (fatos)

O pet é desenhado por `PetWindow.paintEvent` (`pestinha/body/pet.py`) com `QPainter` e
`draw_face(...)` (`pestinha/body/desenho_rosto.py`), lendo `PetState` e `Body`. Render, posição
(`move()`) e entrada de mouse vivem no mesmo `QWidget`. A SNN (`pestinha/core/`) não conhece Qt e deve
permanecer intocada. Decisões aprovadas: identidade "anime SD premium"; primeiro renderer por sprites;
Inochi2D só como possível evolução.

## Opções

**A. Sprites 2D (atlas + máquina de estados) em `QPainter`/`QImage`** — recomendada para spike.
- Prós: sem dependência nova; encaixa no `paintEvent`; fácil de testar por contrato.
- Contras/riscos: custo de produção de arte (muitos estados × direções); transições entre emoções podem ficar
  rígidas; DPI fracionário exige variantes ou escala com suavização.

**B. Sprites em `QML`/Qt Quick (`AnimatedSprite`/`SpriteSequence`)**
- Prós: animação declarativa, GPU.
- Contras: troca de pilha (Widgets → Quick) em uma janela translúcida; interação com `WA_TranslucentBackground`,
  input region e `offscreen` nos testes **[HIPÓTESE, não testada]**; mais superfície para o risco PySide6×Qt.

**C. Rig 2D (Inochi2D)** — evolução, não primeiro passo.
- Prós: expressividade contínua.
- Contras: runtime não é Python/PySide6 nativo; empacotamento e integração com o ciclo de 16 ms **não
  investigados**; risco alto para Debian 13.

## Decisão proposta

Avaliar **A** como renderer inicial atrás de um contrato `Renderer` (entrada: `PetState`, `Body`, `dpr`;
saída: quadro + região opaca). O renderer legado vira implementação de referência. B e C permanecem
como alternativas. **Nada é aceito sem os spikes de M1 e aprovação do proprietário.**

## Consequências / pontos em aberto

- O contrato de renderer precisa expor a **região opaca** (para input region — ver ADR 002).
- Mapeamento `emotion` (`EYE_SHAPES`, `EMOTION_NAMES`) → estado de sprite a definir em M3.
- Arte final somente em M5, após validação em KDE real.
