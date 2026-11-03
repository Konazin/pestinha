# Pestinha Anime — Roadmap M0–M7

> Proposta. **Somente M0 está autorizado.** Cada marco seguinte exige aprovação explícita do proprietário
> antes de começar. Nenhum marco altera a SNN (topologia, pesos, schemas, regras de aprendizado).

Decisões já aprovadas (do pedido): alvo inicial Debian 13 + KDE Plasma 6 + Wayland (sem alegar outros
compositores); estética inicial "anime SD premium" (arte final **não** é produzida antes de M5);
primeiro renderer por sprites (Inochi2D só como evolução possível); validação em KDE real antes dos assets finais.

| Marco | Objetivo | Entregáveis | Critério de saída | Autorização |
|---|---|---|---|---|
| **M0** | Auditoria documental | 6 documentos em PR único | Docs revisados; zero mudança de código | **AUTORIZADO** (este PR) |
| M1 | Spikes descartáveis em KDE real (ordem em `ADR 002`): S1 baseline XWayland/Wayland, S2 overlay + input region, S3 IPC KWin↔Python, S4 multi-monitor/DPI, S5 fullscreen/lockscreen/atalho | Relatório com matriz preenchida (PASS/FAIL com evidência) e vídeo/log; código de spike **fora** de `pestinha/` | ADR 001/002 passam de `Proposed` a decisão do proprietário | Pendente |
| M2 | `Platform Capability Layer`: contrato de capacidades (posição, janelas, ocioso, atalho, input region) com backends X11/Windows/macOS inalterados em comportamento | Interface + testes de contrato; backend KDE/Wayland atrás de *feature flag* | Suíte atual verde; sem regressão nos outros SO | Pendente |
| M3 | Contrato de renderer (`PetState`+`Body` → quadro) e *adapter* do rosto vetorial atual | Renderer legado como implementação de referência; testes de equivalência visual | Nenhuma mudança observável no renderer legado | Pendente |
| M4 | Backend KDE/Wayland mínimo conforme decisão do M1 | Overlay, movimento, input region, atalho | Matriz Wayland (core) toda PASS em KDE real | Pendente |
| M5 | Renderer de sprites + pipeline de assets (placeholder → arte final) | Atlas, estados mapeados de `emotion`/`PetState` | Aprovação visual do proprietário; arte final só aqui | Pendente |
| M6 | Robustez: multi-monitor, DPI fracionário, fullscreen, bloqueio de tela, suspensão, perfil de desempenho | Relatório de desempenho e regressão | Matriz completa PASS ou limitações documentadas | Pendente |
| M7 | Empacotamento Debian 13 e documentação de usuário | Pacote/instruções, limitações declaradas | Instalação limpa validada em máquina real | Pendente |

## Princípios transversais

- Prova antes de decisão: nenhuma solução de overlay/IPC é escolhida sem PASS em KDE real.
- CI `offscreen`/Xvfb não conta como evidência de Wayland.
- Sem keylogger, sem leitura de título/conteúdo de janela, sem screenshots, sem entrada sintética, sem telemetria,
  sem controle do cursor (reforça `docs/ARQUITETURA.md` § Regras do projeto).
- Sem migração nem recriação de `memory/`.
- PRs pequenos; ADRs só viram "Accepted" por decisão do proprietário.
