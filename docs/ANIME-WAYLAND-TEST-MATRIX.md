# Pestinha Anime — Matriz de testes Wayland/KDE

Legenda: **PASS** = observado e registrado; **FAIL** = observado e falhou; **NOT TESTED** = nunca executado.
Regra: CI, `QT_QPA_PLATFORM=offscreen`, Xvfb ou leitura de documentação **não** contam como PASS de
KDE Wayland real. Todas as linhas de KDE real abaixo estão **NOT TESTED** no fim do M0.

## A. Resultados já observados (não são Wayland)

| ID | Teste | Ambiente | Resultado | Observação |
|---|---|---|---|---|
| A1 | `pyflakes` do projeto | contêiner Ubuntu 24.04, sem GUI | PASS | 0 avisos |
| A2 | `pytest -q` (352 passed, 7 skipped) | `offscreen`, PySide6 6.11.3 | PASS | Só lógica/UI offscreen; **não** evidencia Wayland |
| A3 | `pytest` sem libEGL | mesmo | FAIL (ambiente) | `libEGL.so.1` ausente; resolvido com `apt install libegl1` |

## B. Roteiro KDE real (Debian 13, Plasma 6, Wayland)

Pré-requisitos a registrar: `cat /etc/os-release`, `plasmashell --version`, `kwin_wayland --version`,
`qtpaths6 --qt-version`, versão PySide6, `echo $XDG_SESSION_TYPE`, monitores e escalas
(`kscreen-doctor -o`). Executar como usuário comum, sem alterar a configuração do desktop do proprietário.

| ID | Teste | Passos | Critério PASS | Resultado |
|---|---|---|---|---|
| B1 | Ambiente | Registrar pré-requisitos | Todos os campos preenchidos | NOT TESTED |
| B2 | App atual em `xcb` (XWayland) | `QT_QPA_PLATFORM=xcb python main.py --direto` | Pet aparece, anda (`move()`), fica por cima | NOT TESTED |
| B3 | App atual em `wayland` | `QT_QPA_PLATFORM=wayland python main.py --direto` | Registrar se `move()` posiciona a janela | NOT TESTED |
| B4 | PySide6 wheel × Qt do sistema | Verificar plugin `wayland` carregado, `QT_DEBUG_PLUGINS=1` | Sem abort; plugin correto | NOT TESTED |
| B5 | Transparência | Pet sobre janela com fundo claro/escuro | Sem retângulo preto/branco | NOT TESTED |
| B6 | Click-through | Clicar ao lado do pet (região transparente) | Clique chega à janela de baixo | NOT TESTED |
| B7 | Input region dinâmica | Pet em movimento; clicar na silhueta e fora | Silhueta captura, fora passa; sem atraso perceptível | NOT TESTED |
| B8 | Sem roubo de foco | Digitar em editor; pet aparece/clicado | Foco permanece no editor | NOT TESTED |
| B9 | Sempre por cima | Janela normal, maximizada, painel Plasma | Registrar ordem em cada caso | NOT TESTED |
| B10 | Fullscreen | Vídeo/jogo em tela cheia | Pet some ou obedece política documentada | NOT TESTED |
| B11 | Bloqueio de tela / suspensão | Bloquear e retomar | Pet não aparece sobre o lock; retoma sem travar | NOT TESTED |
| B12 | Dois monitores, mesma escala | Atravessar a borda | Passa sem salto/duplicação | NOT TESTED |
| B13 | Escalas mistas (100%/150%) | Atravessar e soltar | Tamanho e física coerentes | NOT TESTED |
| B14 | Escala fracionária (125%/175%) | Observar nitidez e posição | Sem deslocamento de clique | NOT TESTED |
| B15 | Arrastar/arremessar | Arrastar e soltar com velocidade | Gestos funcionam em Wayland nativo | NOT TESTED |
| B16 | Atalho de pânico | Ctrl+Alt+Shift+B (via portal GlobalShortcuts ou alternativa) | Pet desliga; sem keylogger | NOT TESTED |
| B17 | IPC KWin↔Python | Script KWin envia geometria ao serviço Python | Round-trip estável; latência e perda medidas | NOT TESTED |
| B18 | Privacidade do IPC | Inspecionar payload | Só retângulos; sem título/conteúdo | NOT TESTED |
| B19 | Persistência | Fechar e reabrir | `memory/pets/<id>/` íntegro; SNN inalterada | NOT TESTED |
| B20 | Estabilidade | 1 h rodando | Sem vazamento/queda de FPS relevante | NOT TESTED |

Cada execução deve anexar: data, versões, comando, log/vídeo curto e veredito.
