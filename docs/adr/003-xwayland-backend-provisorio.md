# ADR 003 — XWayland como backend gráfico provisório do MVP

- **Status:** Accepted (provisório) — decisão do proprietário, 2026-11-03. **Evidência parcial**: ver *Evidências*.
- **Escopo:** qual plataforma Qt o Pestinha usa em Debian 13 + KDE Plasma 6 (sessão Wayland) até haver prova de outra.
- **Relação com outros ADRs:** **não** substitui o ADR 002 (backend KDE/Wayland nativo), que continua `Proposed` e **não implementado**.
  O ADR 001 (renderer) é independente e continua `Proposed`.

## Decisão

1. A sessão KDE continua em **Wayland**. Não se altera a configuração da sessão nem o ambiente global do usuário.
2. O Pestinha roda como cliente **XWayland** (`QT_QPA_PLATFORM=xcb`), iniciado por um **launcher próprio**
   (`lancadores/pestinha_xwayland.py`) que define a variável só para o processo filho.
3. `main.py`, Windows e macOS não mudam. O suporte legado a X11 é preservado (em X11 o `xcb` já é o padrão).
4. Wayland nativo (layer-shell, superfície por monitor, KWin Bridge) é **evolução futura**, sem prazo, com autorização própria.

## Evidências (e o que elas não provam)

| Fonte | Observado | Não prova |
|---|---|---|
| Máquina real do proprietário | App original em XWayland por 90 s, `rc=0` | Que não houve falha silenciosa; `rc=0` **não é PASS** |
| Mesma execução, observação visual do proprietário (informal, sem registro na matriz) | Movimentação e funcionamento aparentemente normais | Posição exata, bordas, múltiplos monitores, escala, foco, click-through |
| Mesma máquina, Wayland nativo | Objetos concentrados no centro; não acompanharam a física esperada | Causa (consistente com `move()` ignorado em xdg-toplevel; **hipótese** do ADR 002, não provada) |

**Ainda faltam** testes controlados de posicionamento, região de entrada, foco e monitores. Eles estão em
[`../m1/M1X-RELATORIO.md`](../m1/M1X-RELATORIO.md), todos `NOT TESTED`. Se algum falhar de forma que impeça o produto, esta ADR deve ser revista.

## Limitações conhecidas (hipóteses até o M1-X)

- Ferramentas X11 (`xdotool`, `wmctrl`) não enxergam necessariamente janelas Wayland nativas: os sentidos de janela
  do pet cobrem só clientes XWayland (o `plataforma/linux.py` já depende dessas ferramentas).
- Escala mista entre monitores (ex.: 100%/150%, fracionária) precisa de validação; XWayland costuma tratar escala de forma própria.
- Atalho global de pânico (`pynput`) e ocioso (`xprintidle`) não têm garantia sob Wayland; exigem alternativas
  (a bandeja já oferece o pânico; portal XDG GlobalShortcuts e fonte de ociosidade a avaliar). Não há alternativa implementada.
- Sensores de janelas de apps Wayland nativos continuarão exigindo integração com o KWin (KWin Bridge), **fora desta etapa**.
- Foco, "sempre por cima", fullscreen e bloqueio de tela dependem de como o KWin trata janelas X11 (T28–T31 do M1).
- O launcher exige `DISPLAY` (XWayland ativo) e, para o plugin `xcb` do Qt, possivelmente `libxcb-cursor0` e `xwayland` (confirmar pelo log do Qt).

## Consequências

- O núcleo (física, emoções, memória, SNN, renderização vetorial) permanece intacto; `PetWindow.animate` segue usando `move()`.
- O launcher é opcional e removível; nada em `pestinha/` o conhece.
- O contrato de renderer do próximo marco gráfico ([`../ANIME-RENDERER-EXTENSAO.md`](../ANIME-RENDERER-EXTENSAO.md))
  não depende do backend e deve expor a região opaca, necessária se o Wayland nativo voltar.
