# Critérios para seguir ao backend KDE (M2)

> **Proposta de gates, não aprovada.** Os limites numéricos são **propostos** e podem ser ajustados pelo
> proprietário. Este documento **não declara o M1 aprovado**: isso exige execução em KDE Wayland real, evidência
> arquivada e decisão explícita do proprietário. Estado atual: **nenhum gate avaliado (NOT TESTED)**.

## Regra de validade
Só contam resultados de uma sessão com `XDG_SESSION_TYPE=wayland` e `kwin_wayland` em execução (T01), com versões
registradas. `offscreen`, Xvfb, CI e VM sem KDE real **não contam**.

## Gates

| Gate | Condição para PASS | Testes | Estado |
|---|---|---|---|
| G1 — Compatibilidade Qt | PySide6 6.11.3 inicia em `wayland` e `xcb` sem abort; sem mistura de Qt | T02–T04 | NOT TESTED |
| G2 — Posicionamento | **Pelo menos um** método de posicionamento programático PASS (visual), em monitor único, em 12 passos consecutivos sem falha; o método é identificado (ex.: `move()`, XWayland, superfície interna) | T06–T13 | NOT TESTED |
| G3 — Entrada do mouse | Em superfície grande: com região = silhueta, 20/20 cliques fora passam e 20/20 dentro são capturados; região dinâmica com `setMask p95 ≤ 4 ms` e `máx ≤ 16 ms` — **ou** método equivalente documentado | T17–T22, T41–T43 | NOT TESTED |
| G4 — Foco | 0 caracteres perdidos em 20 digitados; nenhum `FOCO_GANHO` indevido | T31 | NOT TESTED |
| G5 — Sessão | **Não** aparece sobre a tela de bloqueio; volta após desbloquear; comportamento em fullscreen registrado | T28–T30 | NOT TESTED |
| G6 — Monitores/escala | Atravessa monitores em 100% e 150% e em escala fracionária com erro visual ≤ 2 px lógicos; ou limitações documentadas e aceitas | T24–T27 | NOT TESTED |
| G7 — Estabilidade | 30 min do app original (plataforma escolhida) sem crash | T40 | NOT TESTED |
| G8 — Fatos de plataforma registrados | KWin Scripting (T33), layer-shell (T35–T38) e GlobalShortcuts (T39) com versão e disponibilidade; T34 só com autorização | T33–T39 | NOT TESTED |
| G9 — Privacidade | Nenhum título de janela, captura de tela, entrada sintética ou segredo nos logs; relatório revisado | revisão | NOT TESTED |
| G10 — Decisão | Proprietário aprova por escrito a solução e o escopo do M2; ADR 001/002 passam de `Proposed` por decisão dele | — | PENDENTE |

## Resultado possível do M1 (a ser decidido depois da execução)
- **Seguir ao M2** com a solução indicada pelos dados (G1–G10 satisfeitos ou limitações aceitas).
- **Repetir spikes** (ex.: G3 ou G6 inconclusivos).
- **Reavaliar o escopo** (ex.: nenhum método de G2 viável → alternativa G de `ALTERNATIVAS-SE-MOVE-FALHAR.md`).

Nenhum desses desfechos é antecipado aqui.
