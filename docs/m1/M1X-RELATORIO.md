# M1-X — Relatório de validação do XWayland

> **Status: AGUARDANDO RESULTADOS.** Nenhum teste abaixo foi executado por quem preparou este documento.
> Preencha somente com o que for observado na máquina real (Debian 13 + KDE Plasma 6 + Wayland). Não deixe
> `PASS` sem evidência arquivada. ADR de referência: [`../adr/003-xwayland-backend-provisorio.md`](../adr/003-xwayland-backend-provisorio.md).

## 1. Revisão das ferramentas existentes (`diagnostico/m1/`)

| Ferramenta | Serve ao M1-X? | Observação |
|---|---|---|
| `coletar_ambiente.sh` | Sim, sem mudança | Confirma sessão KDE Wayland, monitores e escalas (T01, T24) |
| `sondar_qt.py --plataformas xcb` | Sim | T03, T04. Basta `xcb`; `wayland` fica para a trilha futura |
| `rodar_pestinha_original.sh xcb 90` | Sim | T06/T07/T40. Roda uma **cópia temporária** (não toca em `memory/`) e sem o launcher: equivale a `QT_QPA_PLATFORM=xcb` |
| `sonda_janela.py --plataforma xcb` | Sim | `mover` (T10), `regiao` (T16–T23, T41–T42), `--caminho telas` (T25–T27). **Lacuna:** `SEMANTICA-REGIAO-ENTRADA.md` descreve a máscara só para Wayland; em `xcb` o efeito de `setMask` na entrada (X Shape) é **hipótese** e é o que T20/T41/T42 medem |
| `sonda_ciclo.py --plataforma xcb` | Sim | T28–T31 (fullscreen, bloqueio, foco, hotplug) |
| `extrair_input_region.sh` / `WAYLAND_DEBUG` | **Não** | Só vale para clientes Wayland nativos (T43 fica fora do M1-X) |
| `verificar_kwin_dbus.sh`, `verificar_layershell.sh` | Informativos | T33–T39 são da trilha Wayland nativa/KWin; só T39 (portal de atalhos) interessa ao pânico |
| `pestinha_xwayland.py` (launcher) | Teste de uso | Rodar uma vez no fim: `python lancadores/pestinha_xwayland.py --simular` e depois sem `--simular` |

Nenhuma ferramenta nova foi necessária. Nada acima foi alterado nesta etapa.

## 2. Evidências já declaradas pelo proprietário (informais, **não validam**)

| Data | Fonte | Declarado | Registro | Situação na matriz |
|---|---|---|---|---|
| 2026-11-03 | Proprietário | App original em XWayland por 90 s, `rc=0` | Sem log anexado a este repositório | T06: **não promovido a PASS** até anexar `pestinha.stderr.log`/`cabecalho.txt` |
| 2026-11-03 | Proprietário | Movimentação e funcionamento "aparentemente normais" em XWayland | Observação visual, sem critério | T07/T10: **não promovido a PASS** |
| 2026-11-03 | Proprietário | Wayland nativo: objetos concentrados no centro, sem seguir a física | Observação visual | T09/T11: indício, **não FAIL registrado** |

### 2.1 Teste do launcher pelo proprietário (informal) e problema visual conhecido

| Data | Declarado | Situação |
|---|---|---|
| 2026-11-03 | Launcher testado em sessão real: funcionamento aparentemente correto | Indício; a linha "Launcher" da matriz continua `NOT TESTED` (sem critério nem log) |
| 2026-11-03 | **O notebook não apareceu.** Posição salva em `memory`: `[519, 1228]` | **Problema visual conhecido, não bloqueante.** Não investigado e sem alteração de código nesta etapa; causa desconhecida (nenhuma hipótese é afirmada aqui) |

**O M1-X NÃO está integralmente aprovado.** Os demais testes da seção 3 seguem pendentes.

## 3. Matriz M1-X (todos `NOT TESTED`)

Comandos a partir de `diagnostico/m1/` com o venv do M1 (ver `RUNBOOK-M1.md` §1). Critérios completos em [`MATRIZ-M1.md`](MATRIZ-M1.md).

| Grupo | IDs | Comando | Resultado | Evidência (arquivo) | Data / observador |
|---|---|---|---|---|---|
| Sessão e Qt | T01, T03, T04 | `./coletar_ambiente.sh` · `python3 sondar_qt.py --plataformas xcb` | NOT TESTED | | |
| App original | T06, T07 | `./rodar_pestinha_original.sh xcb 90` | NOT TESTED | | |
| Estabilidade | T40 | idem, 30 min (`xcb 1800`) | NOT TESTED | | |
| Posicionamento | T10 | `timeout --signal=INT 40 python3 sonda_janela.py --plataforma xcb --modo mover --api move` | NOT TESTED | | |
| Transparência | T16 | `... --plataforma xcb --modo regiao --regiao nenhuma --tempo 35` | NOT TESTED | | |
| Click-through (janela grande) | T17, T18, T23 | `... --plataforma xcb --modo regiao --regiao nenhuma --grande --tempo 20` | NOT TESTED | | |
| Máscara / região | T19 (info), T20, T21, T41, T42 | `... --regiao mask-vazia-qt\|mask-central\|transparente-input\|mask-removida\|mask-minima --grande` | NOT TESTED | | |
| Região dinâmica | T22 | `... --regiao dinamica --grande --tempo 30` | NOT TESTED | | |
| Foco | T31 | `python3 sonda_ciclo.py --plataforma xcb --tempo 240` (digitar 20 caracteres em um editor) | NOT TESTED | | |
| Fullscreen / bloqueio | T28–T30 | idem | NOT TESTED | | |
| Monitores e escalas | T24–T27 | `... --plataforma xcb --modo mover --caminho telas --passos 9 --tempo 60` em 100/100, 100/150 e fracionária | NOT TESTED | | |
| Pânico e ociosidade | (sem ID) | Observar se Ctrl+Alt+Shift+B e o ocioso respondem fora de janelas X11; anotar | NOT TESTED | | |
| Launcher | (sem ID) | `python lancadores/pestinha_xwayland.py --direto --sair-em 30` | NOT TESTED | | |

Códigos de saída das sondas e regras de PASS/FAIL: `RUNBOOK-M1.md` §3.1 e §4 (`0` **não** é PASS).

## 4. Resumo para a decisão (preencher no fim)

- Há bloqueio que impeça o XWayland como backend do MVP? _(sim/não, qual teste)_
- Limitações confirmadas (sair de "hipótese" no ADR 003): _(lista)_
- Itens que continuam sem prova: _(lista)_
- Recomendação: _(manter / revisar ADR 003)_ — decisão do proprietário.
