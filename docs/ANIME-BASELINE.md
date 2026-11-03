# Pestinha Anime — Baseline M0 (auditoria)

> Documento de auditoria. Nenhum código de execução foi alterado. Fatos = observados no repositório ou em
> comandos executados nesta auditoria. Hipóteses estão marcadas como **[HIPÓTESE]**.

## 1. Ambiente e versões

| Item | Valor | Fonte |
|---|---|---|
| Repositório auditado | `Konazin/pestinha` (remoto `origin`) | `git remote -v` |
| Upstream (fork de origem) | `mille-okws/pestinha`, branch `main` | `git ls-remote https://github.com/mille-okws/pestinha HEAD refs/heads/main` |
| SHA do upstream | `4898787cb5128bea81a57894c30607477d2f9818` (HEAD e `refs/heads/main`), **idêntico** ao `main` de `Konazin/pestinha` e à base deste PR | `git ls-remote` do upstream e do fork, 2026-11-03 |
| Branch | `claude/pestinha-anime-m0-audit-35whxi` | `git status -sb` |
| SHA base (HEAD) | `4898787cb5128bea81a57894c30607477d2f9818` — "Merge pull request #6 from tiosoaress/isaac-contribuicao" | `git rev-parse HEAD` |
| Versão do projeto | `0.7.0`, `requires-python >=3.11`, GPL-3.0-or-later | `pyproject.toml` |
| Sistema da auditoria | Linux 6.18 (contêiner cloud), userland Ubuntu 24.04 — **não é Debian 13 nem KDE** | `uname -a`, saída do `apt` |
| Python | 3.13.18 (CI do projeto usa 3.11) | `python3 --version` |
| PySide6 / shiboken6 / Qt | 6.11.3 / 6.11.3 / Qt 6.11.3 (Qt embarcado na wheel) | venv temporário |
| numpy / psutil / pytest / pyflakes | 2.5.4 / 7.2.2 / 8.4.2 / 4.1.0 | `pip list` (venv) |
| Sessão gráfica | nenhuma (`WAYLAND_DISPLAY`/`DISPLAY` vazios) | `env` |
| Ferramentas presentes | `ruff`, `flake8`, `mypy` (não usados: o projeto só configura pyflakes); `dbus-send` | `which` |
| Ferramentas ausentes | `kwin_wayland`, `qdbus` | `which` |
| Plano normativo `PLANO-PESTINHA-ANIME-v1.1.md` | **ausente** do workspace, do repositório, das duas branches e do restante do sistema de arquivos (busca repetida na revisão) | `find / -iname '*PLANO-PESTINHA*'` — ver lacuna L1 |

Ambiente temporário: venv fora do repo (`<scratchpad>/venv`) com `PySide6==6.11.3 psutil numpy pytest==8.4.2
pyflakes==4.1.0` (as mesmas versões fixadas pelo CI/`requirements.txt`) e, no contêiner, pacotes apt
`libegl1 libgl1 libxkbcommon0 libfontconfig1 libdbus-1-3`. Nenhum manifest/lock foi alterado.

## 2. Comandos e resultados

| Comando | Resultado | Duração |
|---|---|---|
| `python -m pyflakes pestinha tests main.py ferramentas conftest.py` | sem saída (limpo) | 0,35 s |
| `QT_QPA_PLATFORM=offscreen python -m pytest -q` (1ª tentativa, sem libEGL) | **19 erros de coleta**: `ImportError: libEGL.so.1` — falha de ambiente, não do código | 1,0 s |
| mesmo comando após `apt install libegl1 …` | **352 passed, 7 skipped, 0 failed** | 77,6 s |

Skips (`-rs`): 2 em `tests/test_auditoria_30.py` (caminho específico do Windows), 5 em
`tests/test_plataforma.py` (requer backend macOS). `git status` ficou limpo após os testes; nenhuma pasta
`memory/` foi criada.

**Leitura correta:** o resultado cobre lógica, rede e UI em Qt `offscreen`. **Não prova nada sobre Wayland,
KDE, KWin, input regions, multi-monitor real ou DPI real.** O CI do projeto (`.github/workflows/testes.yml`)
também usa `QT_QPA_PLATFORM=offscreen`.

Fato relevante de versão: `requirements.txt` fixa `PySide6==6.11.3` no Linux com o comentário "6.12.0 provoca
abort nativo none_dealloc" e o CI confere `6.11.3` exato.

## 3. Mapa de módulos (caminhos e símbolos reais)

Camadas (`docs/ARQUITETURA.md`, verificadas por `tests/test_arquitetura.py`):
`core < sense < body < world < mind < ui < controle < app.py`; `plataforma/` é compartilhada.

| Caminho | Símbolos principais | Papel | Qt? |
|---|---|---|:-:|
| `main.py` | `main()`, `apagar_memoria()` | Entrada: `QApplication`, `Paths`, `SettingsStore`, onboarding, `PestinhaApp(store, paths)` | sim |
| `pestinha/app.py` | `PestinhaApp(SessaoMixin, InteracaoMixin, QObject)`: `frame`, `think`, `sense`, `scan_windows`, `screen_bounds`, `screen_geometries`, `bounds`, `_timer` | Composição e ciclos | sim |
| `pestinha/core/nervous_system.py` | `LIFBrain`, `Brain`, `SENSORY_SPEC`, `INTER_SPEC`, `MOTOR_SPEC`, `CONNECTIONS`, `DECISION_MOTORS`, `LATERAL_INHIBITION`, `MotorDecoder` | SNN LIF (881 linhas) | não |
| `pestinha/core/{emotion,motor,physics,homeostasis,conditioning,episodic,protesto}.py` | `EmotionState`, `MotorTone`, `Body`, `Drives`, `Conditioning`, `EpisodicMemory`, `Protesto` | Emoção, física, aprendizado | não |
| `pestinha/plataforma/{__init__,linux,windows,macos,_comum}.py` | `ocioso_segundos`, `processo_ativo`, `retangulo_ativo`, `tela_cheia`, `janelas_visiveis`, `sem_foco_nativo`, `iniciar_atalho` | Única camada que conhece o SO; backend escolhido por `sys.platform` | não |
| `pestinha/sense/senses.py`, `timeline.py` | `get_idle_seconds`, `get_active_app`, `detect_activity`, `is_fullscreen`, `list_windows`, `foreground_rect`, `SenseState`, `TimelineRecorder` | Significado das leituras | não |
| `pestinha/body/pet.py` | `PetWindow`, `overlay_flags()`, `set_no_activate()`, `cursor_pos()`, `CX/CY` | **Janela, desenho e mouse do pet** | sim |
| `pestinha/body/{pet_state,behavior,desenho_rosto,bolinha,toy,brincadeira}.py` | `PetState`, `Behavior`, `draw_face`, `draw_zzz`, `lerp_shape`, `aparencia_de`, `Ball` | Estado exibido, comportamento, rosto vetorial | sim |
| `pestinha/world/*.py` | `FloatingWidget` (`arrastavel.py`), `MischiefEngine`, `fireworks.py`, `cartazes.py`, `notebook.py`, `objetos.py` | Objetos-janela na tela | sim |
| `pestinha/mind/*.py` | `CastigoController`, `ProtestController`, `MischiefController`, `RevolucaoController`, `SleepController`, `MesaController`, `FestaController` | Ligam decisões da rede à cena | sim |
| `pestinha/ui/*.py` | `Tray`, `PanicHotkey`, `SettingsDialog`, `FloatManager`, `NeuralMonitor`, `StrikePanel` | Telas e bandeja | sim |
| `pestinha/controle/{sessao,interacao}.py` | `SessaoMixin` (`save`, pausa, pânico), `InteracaoMixin` | Política de sessão e interação | sim |
| `pestinha/{paths,store,config,ajustes,settings_store,migracao}.py` | `Paths`, `PetPaths`, `ConteudoPaths`, `store.py`, `migracao.py` | Persistência atômica em `memory/pets/<id>/` | não |
| `tests/` | 29 arquivos `test_*.py`; `conftest.py` raiz força `QT_QPA_PLATFORM=offscreen` | Suíte | — |
| `.github/workflows/{testes,executaveis}.yml` | matriz Win/mac/Ubuntu; só offscreen | CI | — |

## 4. Fluxo de execução (confirmado no código)

1. **Captura de ambiente** — `PestinhaApp.sense` (500 ms) → `senses.get_idle_seconds()` /
   `get_active_app()` / `is_fullscreen()` → `plataforma.*` → no Linux, subprocessos `xprintidle`, `xdotool`,
   `wmctrl` via `plataforma/_comum.rodar` (`plataforma/linux.py`). `scan_windows` (250 ms) →
   `senses.list_windows` → `plataforma.janelas_visiveis` → plataformas de pouso (`self.platforms`).
2. **Sense** — `SenseState.update(activity, idle, drives, caressing, mouse_moving)` devolve intensidades
   por canal (`SENSORY_SPEC`).
3. **Decisão** — `PestinhaApp.think` (100 ms): `brain.stimulate(intensities)`, `brain.step(chunk)`,
   `brain.motor_activity()`, `brain.learn(...)`; emoção (`EmotionState.update`) e controladores `mind/`.
4. **Física** — `PestinhaApp.frame` (16 ms): `body.step(dt, bounds, platforms, areas, monitores)`
   (`core/physics.Body`), `behavior.tick`, controladores.
5. **Animação** — `PetWindow.animate(now)`: interpola `st.shape` (`lerp_shape`), pisca, e
   `self.move(int(body.x - CX), int(body.y - CY))`; depois `self.update()`.
6. **Renderização** — `PetWindow.paintEvent` com `QPainter`: `draw_face(p, st.shape, st.gaze, blink,
   st.emotion, carinho=…, aparencia=…)`, `draw_zzz`, rótulo opcional. Janela quadrada `LADO_JANELA_PET`=200 px,
   `WA_TranslucentBackground`.
7. **Persistência** — timer de 30 s → `SessaoMixin.save` → `brain.save(state_file)`, `drives.save`,
   `memory.save`, `conditioning.save`, `protest_ctl.save`, `sad.save` (caminhos só via `paths.py`; escrita
   atômica via `store.py`).

Entradas do usuário: `PetWindow.mousePress/Move/ReleaseEvent`, `contextMenuEvent`, `wheelEvent` usam
`event.globalPosition()`/`globalPos()` e emitem `poked`, `drag_started`, `drag_ended`, `thrown`,
`menu_requested`. Atalho de pânico: `ui/ui.PanicHotkey` → `plataforma.iniciar_atalho` → `pynput` no Linux.

## 5. Fronteira SNN (a preservar)

A SNN está isolada em `pestinha/core/` sem Qt nem SO (garantido por `tests/test_arquitetura.py`). O renderer
atual consome apenas `PetState` (`emotion`, `shape`, `gaze`, `shake`, `tone`, `show_label`, `desk_top`,
`protest_stage`, …) e `Body` (`x`, `y`, `angle`, `grounded`, `held`). **Um novo renderer pode se encaixar
lendo `PetState`/`Body` sem tocar em `core/`.** Qualquer alteração em topologia, pesos, `MOTOR_SPEC`,
`CONNECTIONS`, schemas de `memory/` ou regras de aprendizado está fora de escopo.

## 5.1 Decisões aprovadas (registro)

Seis decisões aprovadas pelo proprietário, transcritas do pedido do M0 (a conferir contra o plano normativo quando ele estiver disponível):

| # | Decisão aprovada |
|---|---|
| D1 | Alvo inicial: Debian 13, KDE Plasma 6, Wayland. Não alegar compatibilidade com todos os compositores. |
| D2 | Identidade visual inicial: anime SD premium; a arte final não é criada agora. |
| D3 | Primeiro renderer planejado: sprites; Inochi2D só como possível evolução. |
| D4 | Preservar a SNN original: sem alteração de topologia, pesos, schemas ou regras de aprendizado. |
| D5 | Wayland deve ser validado em KDE real antes da produção de assets finais. |
| D6 | A autorização termina em M0: parar ao entregar o PR documental e o relatório. |

## 6. Acoplamentos confirmados (fatos)

| # | Fato | Onde |
|---|---|---|
| F1 | Posição do pet = `QWidget.move()` de uma janela top-level, todo quadro | `body/pet.py` `PetWindow.animate` |
| F2 | Renderização e hit-testing estão no mesmo `QWidget` (`paintEvent` + eventos de mouse) | `body/pet.py` |
| F3 | Flags: `FramelessWindowHint | Tool | WindowStaysOnTopHint | WindowDoesNotAcceptFocus` + `WA_TranslucentBackground`, `WA_ShowWithoutActivating` | `overlay_flags()` |
| F4 | O docstring de `body/pet.py` afirma que "pixels transparentes deixam o clique passar"; só os fogos usam `Qt.WindowTransparentForInput`; **não há `setMask` nem região de input explícita** (grep). Essa afirmação é comportamento observado/esperado em Windows/X11 e **não deve ser assumida em Wayland** — ver `ANIME-RISK-REGISTER.md` R2 | `body/pet.py`, `world/fireworks.py` |
| F5 | Posição do cursor global por `QCursor.pos()` | `body/pet.py` `cursor_pos()` |
| F6 | Identificação de janelas por `int(widget.winId())` para excluí-las de `janelas_visiveis` | `app.py` `scan_windows`, `ui/float_manager.py` `visible_handles` |
| F7 | `scan_windows` usa o `devicePixelRatio` **só da tela primária** para converter todas as janelas | `app.py` `scan_windows` |
| F8 | Geometria multi-monitor em coordenadas lógicas Qt (`availableGeometry`/`geometry` por `QGuiApplication.screens()`) | `app.py` `screen_bounds`, `screen_geometries` |
| F9 | Backend Linux é X11-only (`xdotool`, `wmctrl`, `xprintidle`); em Wayland devolve valores padrão; README declara que o atalho global não funciona em Wayland | `plataforma/linux.py`, `README.md` |
| F10 | `sem_foco_nativo` é no-op no Linux | `plataforma/linux.py` |
| F11 | Atalho global via `pynput` (X11) | `plataforma/_comum.atalho_pynput` |
| F12 | Vários objetos-janela independentes (post-its, bolinha, cartazes, fogos, painéis) usam o mesmo `overlay_flags()` | `world/*`, `body/bolinha.py` |
| F13 | Docs oficiais do projeto dizem "macOS e Linux ainda não foram testados numa máquina real" e "pouco testado com escala >100% e vários monitores" | `README.md` § Limitações |

## 7. Lacunas

- **L1** — `docs/plans/PLANO-PESTINHA-ANIME-v1.1.md` **ainda não foi disponibilizado** ao workspace. `ANIME-ROADMAP.md` foi corrigido para os objetivos M0–M7 informados pelo proprietário em mensagem, mas não foi conferido contra o texto do plano. Ver `ANIME-CONFORMIDADE-M0.md`.
- **L2** — *(resolvida na revisão)* SHA do upstream registrado na seção 1.
- **L3** — Sem sessão KDE/Wayland real: nada sobre comportamento de janela, input, DPI ou atalhos foi observado.
- **L4** — Documentação externa (KWin, LayerShellQt, portais) inacessível por rede; ver `ANIME-RISK-REGISTER.md` e ADR 002 (fontes secundárias, não verificadas).
- **L5** — Versões de Qt/Plasma do Debian 13 não medidas aqui; qualquer número é **[HIPÓTESE]** a confirmar na máquina-alvo (`apt policy`, `kwin_wayland --version`, `qtpaths6`).
