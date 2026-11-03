# Alternativas se `QWidget.move()` não posicionar a janela em Wayland

> Lista de opções para **estudo**. Nenhuma foi escolhida ou provada. Ordem sem significado de prioridade.
> A escolha depende dos resultados T09–T13, T18–T22 e T33–T38 e de decisão do proprietário (ADR 002 segue
> `Proposed`). Hipóteses marcadas **[H]**; conferir nas referências oficiais do ADR 002.

| # | Alternativa | Como resolve o posicionamento | Depende de | Riscos/lacunas **[H]** | Teste que a avalia | Autorização |
|---|---|---|---|---|---|---|
| A | **XWayland** (`QT_QPA_PLATFORM=xcb`) | Janelas X11 mantêm `move()` | `xwayland` no Debian 13; T06/T07/T10 PASS | Janela X11 em compositor Wayland; sem visão de janelas Wayland nativas; DPI misto; dívida técnica | T06, T07, T10, T23 | Nenhuma |
| B | **Superfície por monitor** (overlay) com o pet desenhado em coordenada interna | A "posição" vira posição de sprite dentro da superfície | Protocolo layer-shell (T35), LayerShellQt (T36–T37) **ou** outra superfície sempre-por-cima; região de entrada correta (T19–T22) | *Binding* Python inexistente na wheel (T37–T38); região de entrada dinâmica; superfície grande pode bloquear cliques; comportamento sobre fullscreen/lock (T28–T29) | T18–T22, T28–T29, T35–T38 | Nenhuma para medir; usar LayerShellQt no app exige M2 |
| C | **Uma única superfície em tela cheia por saída** com o QWidget atual desenhando dentro (variante de B sem layer-shell, via janela comum fullscreen/transparente) | Idem B, sem protocolo especial | Transparência + região de entrada em janela comum (T15, T19–T21) | Fullscreen comum pode ser tratado pelo KWin como app em tela cheia (esconder painéis, desligar composição?) **[H]** | T15, T19–T21, T28 | Nenhuma |
| D | **Janela comum + script KWin** que a move | O KWin posiciona a janela | Script carregado via `org.kde.KWin.Scripting` (T33); IPC Python↔KWin (T34) | `callDBus()` do script chama serviços mas **não** expõe um; latência a 60 Hz; privacidade (acesso a janelas); versão do KWin | T33, T34 | **REQUER AUTORIZAÇÃO** (carregar script) |
| E | **Regra de janela do KDE** que fixa posição | O KWin aplica posição fixa/inicial | Config do usuário (kwinrulesrc) | Estática; altera a configuração do desktop; não é movimento contínuo | — | **REQUER AUTORIZAÇÃO** (altera config) |
| F | **Movimento interativo do sistema** (`QWindow.startSystemMove`) | Só para o usuário arrastar o pet | xdg-toplevel `move` | Não serve para andar sozinho; útil apenas para o arraste | (novo teste, se necessário) | Nenhuma |
| G | **Modo acoplado/limitado** (produto): pet confinado a uma região/painel/borda | Evita precisar de posição global | Decisão de produto | Muda a proposta de valor (pet "livre pela tela") | — | Decisão do proprietário |

## Pontos de decisão que a execução do M1 deve informar

1. `move()` funciona em Wayland nativo? (T09, T11–T13). Se **sim**, as alternativas B–G ficam desnecessárias para posição.
2. Se não, A é suficiente como ponte? (T06–T07, T10) e a que custo (T23, T26–T27)?
3. Alguma superfície grande tem região de entrada correta e barata (T19–T22)? Sem isso, B/C ficam inviáveis.
4. Existe caminho Python viável para layer-shell (T35–T38)? Se não, B exigiria trabalho nativo fora do escopo atual.
5. O script KWin (D) é aceitável em segurança/privacidade para o proprietário? (autorização separada.)
