# ADR 002 — Backend KDE/Wayland (overlay, posição, janelas, atalho)

- **Status:** Proposed (nenhuma alternativa selecionada)
- **Data:** 2026-11-03
- **Escopo:** apenas a proposta; nada foi executado em KDE real

## Contexto (fatos do repositório)

- Posição por `QWidget.move()` todo quadro (`PetWindow.animate`); cursor por `QCursor.pos()`;
  janelas de outros apps via `xdotool`/`wmctrl`; ocioso via `xprintidle`; atalho via `pynput`
  (`pestinha/plataforma/linux.py`, `_comum.py`). O README já declara que em Wayland o pet não vê janelas
  nem ocioso e o atalho não funciona.
- Alvo aprovado: Debian 13, KDE Plasma 6, Wayland. Sem alegação de outros compositores.

## O que está documentado vs. o que não está provado

Fontes: **conhecimento prévio e uma busca secundária**; os sites oficiais (develop.kde.org, wayland.app,
flatpak.github.io) estavam fora da rede permitida desta sessão. Tudo abaixo é **não verificado
contra a documentação oficial** e deve ser conferido no M1.

| Tema | Entendimento atual | Status |
|---|---|---|
| Wayland / xdg-toplevel | O cliente normalmente não define posição global de uma janela; `move()` em top-level nativo Wayland tende a não ter efeito | **[HIPÓTESE forte, a provar em KDE]** |
| XWayland (`QT_QPA_PLATFORM=xcb`) | Mantém `move()`, mas a janela é X11 dentro do KWin; `xdotool`/`wmctrl` só enxergam clientes X11 | **[HIPÓTESE]** |
| layer-shell (LayerShellQt) | Permite superfícies em camada (overlay) ancoradas por saída; posição livre exige superfície por monitor + posição interna | **[HIPÓTESE]**; binding Python para LayerShellQt (C++) **não confirmado** |
| Input regions | `wl_surface.set_input_region` permite passar cliques fora da região; no Qt, `QWindow.setMask()`/`QRegion` pode mapear para isso | **[HIPÓTESE]**; custo de atualizar a cada quadro e bordas anti-aliased não medidos |
| KWin Scripting | Scripts JS rodam no KWin com acesso a janelas (API Plasma 6 baseada em `QJSEngine`); carregáveis via `org.kde.KWin.Scripting` | fonte secundária |
| `callDBus()` | **Chama** serviços D-Bus a partir do script. **Não expõe** serviço D-Bus do script; relatos (bugs.kde.org #475847) indicam que scripts não assinam sinais nem criam serviços | fonte secundária; **IPC Python→KWin precisa de desenho próprio** (ex.: serviço D-Bus no Python que o script chama; Python carrega o script via `loadScript*`) — **não provado** |
| Segurança de scripts | Qualquer script pode chamar D-Bus arbitrário (bugs.kde.org #434808) | fonte secundária; implica revisão de privacidade |
| XDG GlobalShortcuts | Portal `org.freedesktop.portal.GlobalShortcuts` (`CreateSession`, `BindShortcuts`, sinal `Activated`) | **[HIPÓTESE]**; versão do portal no Plasma do Debian 13 e confirmação do usuário a verificar |
| Versões Debian 13 | Qt do sistema (série 6.8) e Plasma (série 6.3) **[HIPÓTESE, de memória]** | medir na máquina-alvo |

**Problemas ainda não comprovados:** (1) IPC KWin↔Python estável; (2) movimento do pet entre monitores com
escalas diferentes; (3) regiões de clique dinâmicas sem custo/flicker; (4) comportamento sob fullscreen e
tela de bloqueio; (5) PySide6 6.11.3 (wheel, Qt embarcado) × Qt/plugins do sistema Debian (platform plugin
Wayland, `libQt6WaylandClient`); (6) identificar a própria janela no KWin **sem** ler títulos
(usar `resourceClass`/`desktopFileName` próprios).

## Alternativas

**Alt 1 — XWayland como ponte (menor mudança).** Rodar o app existente com `xcb`. Mantém `move()` e
a camada `linux.py` parcialmente. Riscos: perde janelas Wayland-nativas; `pynput`/`xprintidle` não veem
input global fora do X; DPI misto ruim; é dívida técnica, mas ótima **linha de base** do spike S1.

**Alt 2 — Overlay nativo Wayland com layer-shell.** Uma superfície transparente por monitor (camada overlay)
onde o renderer desenha o pet em coordenadas internas; input region restrita à silhueta. Riscos: binding
LayerShellQt em Python; custo/latência de atualizar a região; comportamento sobre fullscreen e lockscreen;
foco/teclado (`keyboard interactivity = none`); janelas-objeto (post-its, cartazes) também precisam migrar.
Leitura de janelas continua exigindo outra fonte (Alt 3 ou nenhuma).

**Alt 3 — Janela normal + KWin Script como "motor de posição".** O pet é um toplevel comum; um script KWin
move a janela (por `resourceClass` próprio) e informa geometria de janelas via `callDBus` a um serviço D-Bus
Python. Riscos: IPC não provado; latência a 60 Hz; flicker; permissões/privacidade do script; depender de API
interna do KWin por versão. Pode ser **combinada** com Alt 2 apenas para leitura de geometrias (sem títulos).

## Ordem proposta dos spikes M1 (descartáveis, fora de `pestinha/`)

1. **S1** — baseline: app atual em KDE real com `xcb` e com `wayland` (somente observar; sem alterar código).
2. **S2** — overlay mínimo + input region (layer-shell vs. toplevel+KWin) com um retângulo opaco.
3. **S3** — IPC KWin↔Python: ida e volta com geometrias de janela; medir latência e falhas.
4. **S4** — dois monitores, escalas 100%/150%: atravessar, soltar, pousar.
5. **S5** — fullscreen, bloqueio de tela, suspensão, atalho via portal.

## Decisão

Nenhuma. Selecionar somente após evidência PASS de M1 e aprovação do proprietário.
