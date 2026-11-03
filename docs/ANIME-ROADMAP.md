# Pestinha Anime — Roadmap M0–M8 (v1.2, proposta de reconciliação)

> **Fonte e limites desta versão.** Os arquivos do plano (`PLANO-PESTINHA-ANIME-v1.1.md` e qualquer v1.2) **não
> estão no repositório nem no workspace** (busca em `main`, refs e disco). Este roadmap **não é cópia nem
> reconciliação literal** de nenhum plano: registra as **diretrizes aprovadas pelo proprietário em mensagem**
> (marcos M0–M8 e decisões abaixo). Quando os arquivos do plano forem fornecidos, será feita a comparação literal
> e as diferenças entrarão aqui como `PROPOSTA`.
>
> **Estado:** M0 concluído (PR #1 mergeado). **M1 em diante não está autorizado**; cada marco exige aprovação
> explícita do proprietário. Nenhum marco altera a SNN sem autorização própria.

## Decisões aprovadas

| # | Decisão |
|---|---|
| D1 | Plataforma principal: Debian 13, KDE Plasma 6 e Wayland. Sem alegar outros compositores. |
| D2 | Personagem: garota de anime SD premium. A arte definitiva não é produzida antes da validação Wayland (D5). |
| D3 | Renderização inicial: sprites 2D. Evolução gráfica futura: Inochi2D. |
| D4 | Preservar a SNN original; expansões só serão consideradas após medições (M6), com aprovação própria. |
| D5 | Validar Wayland real (KDE) antes de produzir a arte definitiva. |
| D6 | *(histórica)* A autorização do M0 terminou ao entregar a auditoria. Marcos seguintes exigem nova aprovação. |
| D7 | Desenvolvimento incremental, com testes e aprovação por marco. |
| D8 | Funcionamento local, offline por padrão e sem interações invasivas. |

## Marcos (objetivos e numeração aprovados)

| Marco | Objetivo | Autorização |
|---|---|---|
| **M0** | Auditoria, baseline e arquitetura | **Concluído** (PR #1) |
| **M1** | Prova de conceito Wayland real | Pendente |
| **M2** | Backend KDE e adaptadores de plataforma | Pendente |
| **M3** | Renderizador de sprites com personagem provisória | Pendente |
| **M4** | Produção artística anime SD premium | Pendente |
| **M5** | Interações contextuais e personalidade | Pendente |
| **M6** | Cognição experimental e avaliação de expansão da SNN | Pendente |
| **M7** | Release, empacotamento e distribuição | Pendente |
| **M8** | Integração futura com agentes de programação (**pós-MVP, planejamento apenas**) | Pendente — **não implementar agora** |

O limite do "MVP" não foi definido na mensagem do proprietário. **PROPOSTA:** tratar M0–M7 como o MVP e M8 como
pós-MVP; a confirmar.

## Subdivisões técnicas (PROPOSTA — detalham, não substituem os objetivos)

| Marco | Subdivisão proposta | Critério de saída proposto |
|---|---|---|
| M0 | Baseline, mapa de módulos, ADRs `Proposed`, matriz de testes, riscos, conformidade | Documentos mergeados; zero mudança de código |
| M1 | Spikes descartáveis em KDE real, fora de `pestinha/`: **S1** baseline do app atual (`xcb` × `wayland`); **S2** overlay + região de entrada (incl. superfície grande); **S3** IPC KWin↔Python; **S4** multi-monitor/DPI; **S5** fullscreen, bloqueio de tela e atalho | Matriz preenchida (PASS/FAIL com evidência); ADR 001/002 prontos para decisão do proprietário |
| M2 | `Platform Capability Layer` (posição, janelas, ocioso, atalho, região de entrada) e backend KDE/Wayland conforme o M1, atrás de *feature flag*; robustez de multi-monitor, DPI, fullscreen e suspensão | Suíte atual verde; sem regressão em Windows/macOS/X11; matriz Wayland (núcleo) PASS em KDE real |
| M3 | Contrato de renderer (`PetState` + `Body` → quadro + região opaca), *adapter* do rosto vetorial atual como referência e personagem provisória em sprites 2D | Renderer legado inalterado; testes de contrato; mapeamento `emotion` → estado de sprite |
| M4 | Pipeline de assets e arte final da garota anime SD premium (só após D5) | Aprovação visual do proprietário |
| M5 | Interações contextuais e personalidade, sem keylogger, leitura de título/conteúdo de janela, screenshots, entrada sintética, telemetria remota ou controle do cursor | Escopo e permissões aprovados antes de qualquer sinal novo; `PRIVACIDADE.md` revisada |
| M6 | Medições da SNN atual e **avaliação** de expansão; qualquer mudança de topologia, pesos, schemas ou aprendizado exige medições documentadas, aprovação explícita e ADR próprio | Relatório e recomendação; a avaliação não autoriza a implementação |
| M7 | Empacotamento Debian 13, documentação de usuário, release e distribuição, limitações declaradas | Instalação limpa validada em máquina real |
| M8 | Ver `docs/ANIME-M8-AGENTES.md`: adaptadores independentes, eventos padronizados, comunicação local | Planejamento aprovado; **sem implementação** até autorização própria |

## Divergências em relação à versão anterior deste arquivo (registro)

| Antes (PR #1) | Agora | Natureza |
|---|---|---|
| M0 "Auditoria e baseline" | M0 "Auditoria, baseline e arquitetura" | Nome ampliado pela mensagem do proprietário |
| M2 "Backend KDE" | M2 "Backend KDE e adaptadores de plataforma" | Idem; Capability Layer já era subdivisão |
| M3 "sprites provisórios" | M3 "Renderizador de sprites com personagem provisória" | Idem |
| M5 "Interações contextuais" | M5 "Interações contextuais e personalidade" | Idem |
| M6 "…incluindo avaliação de expansão da SNN" | M6 "Cognição experimental e avaliação de expansão da SNN" | Redação |
| M7 "Release e distribuição" | M7 "Release, empacotamento e distribuição" | Redação |
| *(ausente)* | **M8 Integração futura com agentes** | Marco novo, pós-MVP |
| D1–D6 | D1–D8 | D7 (incremental/aprovação por marco) e D8 (local/offline/não invasivo) acrescentadas; D2 passa a dizer "garota" |

Mudança de sequência ou de objetivo além do que a mensagem do proprietário determina: **nenhuma**.

## Princípios transversais

- Prova antes de decisão: nenhuma solução de overlay/IPC é escolhida sem PASS em KDE real.
- CI `offscreen`/Xvfb não conta como evidência de Wayland.
- Sem keylogger, leitura de título/conteúdo de janela, screenshots, entrada sintética, telemetria remota ou
  controle do cursor (reforça `docs/ARQUITETURA.md` § Regras do projeto e `PRIVACIDADE.md`).
- Sem migração nem recriação de `memory/`.
- PRs pequenos; ADRs só viram "Accepted" por decisão do proprietário.
