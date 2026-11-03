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
| B2 | App atual em `xcb` (XWayland) | `QT_QPA_PLATFORM=xcb python main.py --direto` | Pet aparece, anda (`move()`), fica por cima | NOT TESTED (indício informal do proprietário em C1; sem evidência arquivada) |
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

### B.1 Transparência visual × região de entrada (superfícies grandes)

Transparência visual (alfa dos pixels) **não** implica passagem de cliques. Estes testes separam as duas
coisas e cobrem o caso de uma superfície grande (ex.: uma por monitor, em tela cheia) sobre a área de trabalho.
Usar um retângulo/silhueta de teste descartável fora de `pestinha/`.

| ID | Teste | Passos | Critério PASS | Resultado |
|---|---|---|---|---|
| B21 | Superfície grande 100% transparente, **sem** região de entrada definida | Cobrir um monitor inteiro; clicar em ícones/janelas abaixo | Registrar se os cliques passam. (Hipótese: não passam só por serem transparentes) | NOT TESTED |
| B22 | Superfície grande com região de entrada **vazia** | Idem, com `input region` vazia | Todos os cliques chegam às janelas abaixo; arrastar, rolar e clicar com o botão direito também | NOT TESTED |
| B23 | Superfície grande com região = silhueta do pet | Clicar na silhueta e fora, nos quatro cantos e nas bordas | Dentro: pet recebe; fora: abaixo recebe; sem faixa morta nas bordas anti-aliased | NOT TESTED |
| B24 | Região de entrada acompanhando o pet em movimento | Pet andando e sendo arrastado; clicar fora do rastro | Sem atraso que deixe o clique "no lugar antigo"; custo por quadro medido | NOT TESTED |
| B25 | Superfície grande em 2 monitores / escalas mistas | Uma superfície por saída | Região correta em cada saída; sem bloquear o monitor vizinho | NOT TESTED |
| B26 | Rolagem, hover e foco sob a superfície grande | Rolar página, passar o mouse em botões, digitar | Nada é interceptado; foco intacto (B8) | NOT TESTED |
| B27 | Comparação com X11/XWayland | Repetir B21-B22 com `xcb` | Registrar diferença de comportamento | NOT TESTED |

Cada execução deve anexar: data, versões, comando, log/vídeo curto e veredito.

## C. Evidências declaradas pelo proprietário (informais — não são PASS)

Registradas em 2026-11-03 para a decisão D9 (ADR 003). Não têm log nem critério objetivo, portanto **não alteram** o
resultado de nenhuma linha acima. A validação formal está em `docs/m1/M1X-RELATORIO.md`.

| ID | Declarado | Linhas relacionadas | Situação |
|---|---|---|---|
| C1 | App original em `xcb` (XWayland) por 90 s, `rc=0`; movimentação e funcionamento aparentemente normais | B2 (T06/T07/T10) | Indício; **sem evidência arquivada** |
| C2 | App original em Wayland nativo: objetos concentrados no centro, sem seguir a física esperada | B3 (T09/T11) | Indício; **causa não provada** |
| C3 | Posicionamento por região, região de entrada, foco e monitores em XWayland | B5–B14, B21–B27 | **Nunca testados** |
