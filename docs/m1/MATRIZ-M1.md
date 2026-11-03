# Matriz de testes M1

Legenda: **PASS** (observado, com evidência) · **FAIL** (observado e falhou) · **NOT TESTED** (não executado ou
execução inválida). **Todos os testes estão `NOT TESTED`** — nenhuma sessão KDE Wayland real foi usada.
Execução fora de KDE Wayland real (ver T01) não gera PASS/FAIL. "B##" refere-se à matriz do M0
(`docs/ANIME-WAYLAND-TEST-MATRIX.md`). Comandos: ver [`RUNBOOK-M1.md`](RUNBOOK-M1.md) (pasta
`diagnostico/m1/`).

## Ambiente e compatibilidade (Inv. 6)

| ID | M0 | Teste | Critério PASS | Critério FAIL | Evidência | Resultado |
|---|---|---|---|---|---|---|
| T01 | B1 | Sessão é KDE Wayland real | `XDG_SESSION_TYPE=wayland` **e** `pgrep kwin_wayland` com PID; versões de Plasma/KWin/Qt preenchidas | (não há FAIL: se falhar, o conjunto inteiro é inválido) | `ambiente.txt` | NOT TESTED |
| T02 | B4 | Qt `wayland` inicia com a wheel PySide6 6.11.3 | `sondar_qt` plataforma `wayland`: código 0 e `platformName=="wayland"` | código ≠ 0 / abort / plugin não carrega | `qt.json`, `qt_debug_plugins_wayland.log` | NOT TESTED |
| T03 | B4 | Qt `xcb` (XWayland) inicia | código 0 e `platformName=="xcb"` | código ≠ 0 | `qt.json` | NOT TESTED |
| T04 | B4 | Sem mistura de Qt (wheel × sistema) | todas as `libQt6*` do processo sob um único prefixo | libs `libQt6*` de dois prefixos no mesmo processo, ou abort por ABI | `qt.json` (`bibliotecas_carregadas`) | NOT TESTED |

## Pestinha original — S1 (Inv. 1, 2)

| ID | M0 | Teste | Critério PASS | Critério FAIL | Evidência | Resultado |
|---|---|---|---|---|---|---|
| T06 | B2 | App original em `xcb`, 90 s | rc 0, sem `Segmentation`/`Abort`/traceback fatal no stderr, pet visível | crash ou pet não aparece | `pestinha.stderr.log`, `cabecalho.txt` | NOT TESTED |
| T07 | B2 | `xcb`: pet anda sozinho e fica por cima | movimento visível por ≥ 30 s e por cima de um editor | parado ou atrás de janelas | observação | NOT TESTED |
| T08 | B3 | App original em `wayland`, 90 s | idem T06 | idem | idem | NOT TESTED |
| T09 | B3 | `wayland`: pet anda sozinho (`move()`) | movimento visível por ≥ 30 s | pet parado/estático ou em posição fixa | observação | NOT TESTED |
| T40 | B20 | Estabilidade 30 min (plataforma que passou em T06/T08) | sem crash/travamento; sem aumento perceptível de CPU/RAM | crash, travamento, vazamento claro | `top`/log | NOT TESTED |

## Posicionamento (Inv. 3)

| ID | M0 | Teste | Critério PASS | Critério FAIL | Evidência | Resultado |
|---|---|---|---|---|---|---|
| T10 | B2 | `xcb` + `move()` | operador: janela mudou visivelmente de lugar **e** acompanhou os cantos | não se moveu | `resumo.json` (observação) | NOT TESTED |
| T11 | B3 | `wayland` + `QWidget.move()` | idem | não se moveu / posição ignorada | idem | NOT TESTED |
| T12 | B3 | `wayland` + `setGeometry()` | idem | idem | idem | NOT TESTED |
| T13 | B3 | `wayland` + `QWindow.setPosition()` | idem | idem | idem | NOT TESTED |
| T14 | — | `wayland` com `--flags normal` | informativo: registrar se as flags do overlay alteram o resultado de T11 | — | idem | NOT TESTED |

## Transparência e entrada do mouse (Inv. 4, 5)

| ID | M0 | Teste | Critério PASS | Critério FAIL | Evidência | Resultado |
|---|---|---|---|---|---|---|
| T15 | B5 | Fundo transparente em `wayland` | operador `s` (sem retângulo opaco) | retângulo preto/branco | `resumo.json` | NOT TESTED |
| T16 | B5 | Fundo transparente em `xcb` | idem | idem | idem | NOT TESTED |
| T17 | B6 | Janela pequena, sem máscara: clique em área só-transparente | **registrar** se o clique chega embaixo (informativo; separa alfa de entrada) | — | `eventos.jsonl` | NOT TESTED |
| T18 | B21 | Superfície grande, **sem** região | **registrar** (hipótese: bloqueia) | — | `eventos.jsonl` + operador | NOT TESTED |
| T19 | B22 | Superfície grande, `mask-vazia` | ≥ 20 cliques fora chegam embaixo; `cliques_fora == 0` e `cliques_dentro == 0` | algum clique capturado | `resumo.json` | NOT TESTED |
| T20 | B23 | Superfície grande, `mask-central` | ≥ 20 cliques **fora** passam (`cliques_fora==0`, operador `s`) **e** ≥ 20 **dentro** capturados (`cliques_dentro ≥ 20`, operador `s`) | clique fora capturado, ou dentro vazando | `resumo.json` | NOT TESTED |
| T21 | B26 | `transparente-input` | todos os cliques passam; foco intacto | clique capturado | idem | NOT TESTED |
| T22 | B24 | Região dinâmica a 60 Hz | `setMask_ms.p95 ≤ 4 ms` e `max ≤ 16 ms`; operador `s` (clique segue o quadrado sem atraso perceptível) | acima dos limites ou clique no lugar antigo | `resumo.json` | NOT TESTED |
| T23 | B27 | Mesmos T18/T19 em `xcb` | **registrar** diferença em relação ao `wayland` | — | idem | NOT TESTED |

## Monitores e escalas (Inv. 9)

| ID | M0 | Teste | Critério PASS | Critério FAIL | Evidência | Resultado |
|---|---|---|---|---|---|---|
| T24 | B12 | Telas e DPR coerentes entre Qt e `kscreen-doctor` | geometria/escala do Qt batem com o sistema para todos os monitores | divergência | `qt.json` × `ambiente.txt` | NOT TESTED |
| T25 | B12 | 2 monitores 100%/100%, caminho `telas` | janela atravessa e aparece em ambos, sem salto/duplicação | não atravessa / duplica | `resumo.json` + operador | NOT TESTED |
| T26 | B13 | 100%/150% | idem; tamanho visual coerente | idem | idem | NOT TESTED |
| T27 | B14 | Fracionária (125%/175%) | posição visual dentro de ±2 px lógicos do pedido; nitidez aceitável (operador) | deslocamento maior ou clique em lugar errado | idem | NOT TESTED |

## Fullscreen, foco, bloqueio (Inv. 10)

| ID | M0 | Teste | Critério PASS | Critério FAIL | Evidência | Resultado |
|---|---|---|---|---|---|---|
| T28 | B10 | Sobre app/vídeo em tela cheia | **registrar** (a política de produto é decisão posterior) | — | `resumo.json` | NOT TESTED |
| T29 | B11 | Tela de bloqueio | a sonda **não** aparece sobre a tela de bloqueio | aparece sobre o bloqueio (**FAIL grave**) | idem | NOT TESTED |
| T30 | B11 | Após desbloquear | a sonda volta normalmente; sem `ATRASO_NO_BATIMENTO` > 10 s | não volta/travou | `eventos.jsonl` | NOT TESTED |
| T31 | B8 | Foco | 20 caracteres digitados no editor sem perda; `FOCO_GANHO` ausente nos logs | caractere perdido ou `FOCO_GANHO` | idem + operador | NOT TESTED |
| T32 | B11 | Suspender/retomar (opcional) | retoma sem crash | crash/janela morta | idem | NOT TESTED |

## KWin Scripting, LayerShellQt, atalho (Inv. 7, 8)

| ID | M0 | Teste | Critério PASS | Critério FAIL | Evidência | Resultado |
|---|---|---|---|---|---|---|
| T33 | B17 | `org.kde.KWin /Scripting` existe e lista métodos | introspecção lista os métodos (ex.: carga/consulta de scripts) | serviço ausente | `kwin-dbus.txt` | NOT TESTED |
| T34 | B17 | Ida e volta KWin→Python | — **REQUER AUTORIZAÇÃO**; fora desta preparação | — | — | NOT TESTED |
| T35 | — | Compositor anuncia layer-shell | `zwlr_layer_shell_v1` listado em `wayland-info` | ausente | `layershell.txt` | NOT TESTED |
| T36 | — | LayerShellQt disponível no Debian 13 | pacote/lib com versão registrada | indisponível | `layershell.txt`, `ambiente.txt` | NOT TESTED |
| T37 | — | *Binding* Python para LayerShellQt | **registrar** se existe caminho utilizável a partir de PySide6 | — | `layershell.txt` | NOT TESTED |
| T38 | — | Plugin de layer-shell no Qt da wheel | **registrar** (observado ausente no contêiner remoto; reconfirmar) | — | `ambiente.txt` | NOT TESTED |
| T39 | B16 | Portal XDG GlobalShortcuts presente | interface listada e versão lida | ausente | `kwin-dbus.txt` | NOT TESTED |

T05 está reservado e sem uso (numeração mantida para referência cruzada futura).
