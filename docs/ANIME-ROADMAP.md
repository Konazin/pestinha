# Pestinha Anime — Roadmap M0–M7

> **Fonte dos objetivos e da numeração:** instrução do proprietário (mensagem de reconciliação do M0, que lista
> M0–M7). O arquivo `docs/plans/PLANO-PESTINHA-ANIME-v1.1.md` **ainda não foi disponibilizado** ao workspace
> (busca no repositório, nas refs do PR e no disco), portanto **esta tabela não foi conferida contra o texto do
> plano**. Quando o plano chegar, ele prevalece e qualquer diferença será registrada como `PROPOSTA`.
>
> **Somente M0 está autorizado.** Cada marco seguinte exige aprovação explícita do proprietário.
> Nenhum marco altera a SNN (topologia, pesos, schemas, regras de aprendizado) sem autorização própria.

## Decisões aprovadas (D1–D6)

D1 Debian 13 + KDE Plasma 6 + Wayland (sem alegar outros compositores) · D2 identidade "anime SD premium", arte final
não criada agora · D3 primeiro renderer por sprites, Inochi2D só como evolução · D4 SNN original preservada ·
D5 Wayland validado em KDE real antes dos assets finais · D6 autorização termina em M0. (Texto completo em
`ANIME-BASELINE.md` §5.1.)

## Marcos aprovados (objetivos e numeração)

| Marco | Objetivo aprovado | Autorização |
|---|---|---|
| **M0** | Auditoria e baseline | **AUTORIZADO** (este PR) |
| **M1** | Prova de conceito Wayland real | Pendente |
| **M2** | Backend KDE | Pendente |
| **M3** | Renderizador com sprites provisórios | Pendente |
| **M4** | Produção artística anime SD premium | Pendente |
| **M5** | Interações contextuais | Pendente |
| **M6** | Cognição experimental, incluindo avaliação de expansão da SNN | Pendente |
| **M7** | Release e distribuição | Pendente |

## Subdivisões técnicas (PROPOSTA — detalham, não substituem os objetivos)

| Marco | Subdivisão proposta | Critério de saída proposto |
|---|---|---|
| M0 | Baseline, mapa de módulos, ADRs `Proposed`, matriz de testes, riscos, conformidade | Documentos revisados; zero mudança de código |
| M1 | Spikes descartáveis em KDE real, fora de `pestinha/`: **S1** baseline do app atual (`xcb` × `wayland`); **S2** overlay + região de entrada (inclui superfície grande); **S3** IPC KWin↔Python; **S4** multi-monitor/DPI; **S5** fullscreen, bloqueio de tela e atalho | Matriz preenchida (PASS/FAIL com evidência); ADR 001/002 prontos para decisão do proprietário. **D5 começa a ser cumprida aqui** |
| M2 | `Platform Capability Layer` (contrato de capacidades: posição, janelas, ocioso, atalho, região de entrada) e backend KDE/Wayland conforme a decisão do M1, atrás de *feature flag*; robustez de multi-monitor, DPI, fullscreen e suspensão | Suíte atual verde; sem regressão nos backends Windows/macOS/X11; matriz Wayland (núcleo) PASS em KDE real |
| M3 | Contrato de renderer (`PetState` + `Body` → quadro + região opaca), *adapter* do rosto vetorial atual como referência e sprites **provisórios** (placeholders) | Renderer legado inalterado; testes de contrato; mapeamento `emotion` → estado de sprite |
| M4 | Pipeline de assets e arte final anime SD premium (somente após D5: Wayland validado em KDE real) | Aprovação visual do proprietário |
| M5 | Interações contextuais, sem keylogger, leitura de título/conteúdo de janela, screenshots, entrada sintética, telemetria remota ou controle do cursor | Escopo e permissões aprovados antes de qualquer sinal novo; privacidade revisada (`PRIVACIDADE.md`) |
| M6 | Medições da SNN atual e **avaliação** de expansão; qualquer mudança de topologia, pesos, schemas ou aprendizado exige medições documentadas, aprovação explícita e ADR próprio | Relatório de medições e recomendação; **a avaliação não autoriza a implementação** |
| M7 | Empacotamento Debian 13, documentação de usuário, release e distribuição, limitações declaradas | Instalação limpa validada em máquina real |

## Divergências corrigidas em relação à versão anterior deste arquivo (PROPOSTA/registro)

A versão anterior (commits `3f40a9e` e `6b461cb`) usava outra numeração. Foi corrigida:

| Antes (provisório, incorreto) | Agora (aprovado) | Tratamento |
|---|---|---|
| M1 Spikes em KDE real | M1 Prova de conceito Wayland real | Mantido como subdivisão (S1–S5) |
| M2 Platform Capability Layer | M2 Backend KDE | Capability Layer absorvida como subdivisão |
| M3 Contrato de renderer | M3 Renderizador com sprites provisórios | Contrato mantido como subdivisão |
| M4 Backend KDE/Wayland mínimo | M2 | Fundido em M2 |
| M5 Renderer de sprites + arte final | M3 (provisórios) + M4 (arte final) | Dividido |
| M6 Robustez | M2 (robustez) | Fundido em M2 |
| M7 Empacotamento Debian 13 | M7 Release e distribuição | Mantido |
| *(ausente)* | M5 Interações contextuais; M6 Cognição experimental | **Lacuna corrigida** |

Mudança de sequência ou de objetivo em relação ao aprovado: **nenhuma proposta** nesta versão.

## Princípios transversais

- Prova antes de decisão: nenhuma solução de overlay/IPC é escolhida sem PASS em KDE real.
- CI `offscreen`/Xvfb não conta como evidência de Wayland.
- Sem keylogger, leitura de título/conteúdo de janela, screenshots, entrada sintética, telemetria remota ou
  controle do cursor (reforça `docs/ARQUITETURA.md` § Regras do projeto).
- Sem migração nem recriação de `memory/`.
- PRs pequenos; ADRs só viram "Accepted" por decisão do proprietário.
