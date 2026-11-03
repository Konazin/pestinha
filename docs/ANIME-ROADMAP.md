# Pestinha Anime — Roadmap M0–M7

> **STATUS DA RECONCILIAÇÃO: PENDENTE.** O `PLANO-PESTINHA-ANIME-v1.1.md` (roadmap normativo M0–M7) **não está
> no workspace**; esta tabela foi montada a partir do texto do pedido do M0 e é **proposta provisória, não o
> roadmap aprovado**. Nenhuma linha abaixo deve ser lida como decisão. Quando o plano chegar, o roadmap normativo
> prevalece; divergências de objetivo ou sequência ficam registradas aqui como proposta.
>
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

## Marcos do plano que devem ser preservados (a posicionar na reconciliação)

O proprietário determinou que os dois marcos abaixo sejam preservados explicitamente. Sua numeração e sua
posição na sequência M0–M7 só podem ser fixadas contra o plano normativo (**pendente**); a tabela provisória
acima **não os contém** e, portanto, provavelmente diverge do plano.

| Marco (nome conforme a instrução) | Preservação | Restrições já aprovadas |
|---|---|---|
| **Interações contextuais** | Marco próprio; não pode ser diluído nos marcos de plataforma/renderer. Escopo a copiar do plano. | Sem keylogger, leitura de título/conteúdo de janela, screenshots, entrada sintética, telemetria ou controle do cursor (restrições do M0) |
| **Cognição experimental** | Marco próprio; inclui a **possibilidade de expansão da SNN após medições**. | D4 vale até haver autorização: nenhuma alteração de topologia, pesos, schemas ou regras de aprendizado. Qualquer expansão exige (i) medições prévias documentadas, (ii) aprovação explícita do proprietário, (iii) ADR próprio. Não é autorizada, nem implementada, nem estimada no M0 |

## Divergências conhecidas desta tabela provisória (propostas, não decisões)

- Subdivisões técnicas (spikes S1–S5 em M1, `Platform Capability Layer` em M2, contrato de renderer em M3) são
  **proposta** de detalhamento técnico.
- A ausência dos dois marcos acima na tabela é uma **lacuna a corrigir**, não uma proposta de remoção.
- Qualquer mudança de objetivo ou de ordem em relação ao plano será listada aqui como `PROPOSTA` com justificativa.

## Princípios transversais

- Prova antes de decisão: nenhuma solução de overlay/IPC é escolhida sem PASS em KDE real.
- CI `offscreen`/Xvfb não conta como evidência de Wayland.
- Sem keylogger, sem leitura de título/conteúdo de janela, sem screenshots, sem entrada sintética, sem telemetria,
  sem controle do cursor (reforça `docs/ARQUITETURA.md` § Regras do projeto).
- Sem migração nem recriação de `memory/`.
- PRs pequenos; ADRs só viram "Accepted" por decisão do proprietário.
