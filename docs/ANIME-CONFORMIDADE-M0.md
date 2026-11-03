# Pestinha Anime — Matriz de conformidade do M0

Compara os requisitos de reconciliação (instrução do proprietário) com os documentos de auditoria.
**Limitação central:** o arquivo `docs/plans/PLANO-PESTINHA-ANIME-v1.1.md` não foi disponibilizado ao workspace
(busca em árvore, `main`, refs do PR #1 e disco). Conformidade com o **texto do plano** não pôde ser verificada;
as linhas abaixo avaliam conformidade com os requisitos **informados na mensagem do proprietário**.

Legenda: **Conforme** · **Parcial** · **Não conforme** · **Não verificável**.

## 1. Reconciliação com o plano

| # | Requisito | Documento | Status | Observação |
|---|---|---|---|---|
| C1 | Incorporar o plano em `docs/plans/PLANO-PESTINHA-ANIME-v1.1.md` sem alterar o conteúdo | — | **Não conforme** | Arquivo ausente; criar um substituto seria fabricar conteúdo normativo |
| C2 | Comparar o plano com `ANIME-ROADMAP.md` | `ANIME-ROADMAP.md` | **Parcial** | Comparado com a lista M0–M7 da mensagem do proprietário; não com o texto do plano |
| C3 | M0 Auditoria e baseline | Roadmap, Baseline | Conforme | |
| C4 | M1 Prova de conceito Wayland real | Roadmap, ADR 002, Matriz | Conforme | Spikes S1–S5 como subdivisão |
| C5 | M2 Backend KDE | Roadmap, ADR 002 | Conforme | Capability Layer como subdivisão |
| C6 | M3 Renderizador com sprites provisórios | Roadmap, ADR 001 | Conforme | |
| C7 | M4 Produção artística anime SD premium | Roadmap, ADR 001, Riscos R10 | Conforme | Arte final só após D5 |
| C8 | M5 Interações contextuais | Roadmap | Conforme | Restrições de privacidade mantidas |
| C9 | M6 Cognição experimental + avaliação de expansão da SNN | Roadmap | Conforme | Avaliação não autoriza implementação |
| C10 | M7 Release e distribuição | Roadmap | Conforme | |
| C11 | Subdivisões técnicas não substituem objetivos | Roadmap | Conforme | Rotuladas como PROPOSTA |
| C12 | Confirmação do SHA do upstream | Baseline §1 | Conforme | `4898787cb5128bea81a57894c30607477d2f9818`, ver §3 |
| C13 | ADR 001 e ADR 002 em `Proposed` | ADRs | Conforme | |
| C14 | Sem alteração de código, dependências, testes ou rede neural | PR #1 | Conforme | Ver §4 |
| C15 | M1 não iniciado | PR #1 | Conforme | |

## 2. Decisões aprovadas e restrições × documentos

| Item | Onde está registrado | Status |
|---|---|---|
| D1 Debian 13 / KDE Plasma 6 / Wayland | Baseline §5.1, Roadmap, ADR 002 | Conforme |
| D2 anime SD premium, arte final não agora | Baseline §5.1, Roadmap (M4), ADR 001 | Conforme |
| D3 sprites primeiro, Inochi2D só evolução | Baseline §5.1, ADR 001 (opção C) | Conforme |
| D4 SNN preservada | Baseline §5 e §5.1, Roadmap (M6) | Conforme |
| D5 Wayland em KDE real antes dos assets finais | Roadmap (M1/M2 antes de M4), Matriz | Conforme |
| D6 autorização termina em M0 | Roadmap | Conforme |
| Riscos P0 (PySide6×Qt, input region, IPC, DPI, fullscreen/lockscreen, posicionamento nativo) | Riscos R1–R6 | Conforme (R6 reclassificado P0) |
| Transparência visual ≠ região de entrada; teste em superfície grande | Riscos R2, Matriz B21–B27, ADR 002 | Conforme |
| Referências oficiais separadas de comportamento não testado | ADR 002 § Referências | Parcial — URLs **não consultadas** (rede) |
| Nenhuma validação KDE Wayland real | Matriz (tudo NOT TESTED) | Conforme |

## 3. Confirmação do SHA do upstream

Registrada em 2026-11-03 por `git ls-remote`:

| Repositório | `HEAD` | `refs/heads/main` |
|---|---|---|
| `https://github.com/mille-okws/pestinha` (upstream) | `4898787cb5128bea81a57894c30607477d2f9818` | `4898787cb5128bea81a57894c30607477d2f9818` |
| `https://github.com/Konazin/pestinha` (fork) | `4898787cb5128bea81a57894c30607477d2f9818` | `4898787cb5128bea81a57894c30607477d2f9818` |

Base do PR #1 = `4898787cb5128bea81a57894c30607477d2f9818`. Observação: o plano normativo pode citar outro SHA de
referência; isso **não foi verificável**.

## 4. Verificação de escopo

`git diff --name-only origin/main HEAD` deve listar apenas `docs/` (conferido ao fechar este PR).

## 5. Pendências para encerrar a reconciliação

1. Disponibilizar `docs/plans/PLANO-PESTINHA-ANIME-v1.1.md` no workspace (C1).
2. Reexecutar C2–C12 contra o texto do plano e registrar qualquer divergência como `PROPOSTA`.
3. Conferir as referências oficiais do ADR 002 (rede liberada ou verificação manual).
