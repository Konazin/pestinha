# M1 — Preparação técnica (Prova de conceito Wayland real)

> **Status: PREPARAÇÃO. O M1 NÃO está aprovado nem executado.** Nada aqui foi rodado numa sessão KDE Wayland
> real; o ambiente remoto do Claude não tem KDE. Tudo foi preparado para execução posterior na máquina do
> proprietário (Debian 13 + KDE Plasma 6 + Wayland). ADR 001 e ADR 002 seguem **Proposed**; nenhuma solução
> (LayerShellQt ou outra) foi escolhida.

## Conteúdo

| Arquivo | Para quê |
|---|---|
| [`RUNBOOK-M1.md`](RUNBOOK-M1.md) | Passo a passo para executar as 10 investigações, comandos, coleta de logs e relatório |
| [`MATRIZ-M1.md`](MATRIZ-M1.md) | Testes T01–T40 com critério objetivo e resultado `NOT TESTED` |
| [`ALTERNATIVAS-SE-MOVE-FALHAR.md`](ALTERNATIVAS-SE-MOVE-FALHAR.md) | Opções se `QWidget.move()` não posicionar a janela (sem escolher nenhuma) |
| [`CRITERIOS-APROVACAO.md`](CRITERIOS-APROVACAO.md) | Gates para seguir ao M2 (propostos; o proprietário aprova) |
| [`../../diagnostico/m1/`](../../diagnostico/m1/) | Ferramentas isoladas de diagnóstico (scripts) |

## Regras que valem para tudo

- Nenhum código de produção (`pestinha/`, `tests/`, `main.py`, dependências, schemas) foi modificado.
- As ferramentas **não** instalam scripts no KWin, **não** alteram configuração do desktop, **não** geram
  entrada sintética, **não** movem o cursor, **não** capturam tela e **não** leem títulos de janelas.
- Resultados de `offscreen`, Xvfb, CI ou de qualquer ambiente sem KDE real **não valem** para a matriz.
  Execuções de fumaça feitas no contêiner remoto servem só para provar que os scripts rodam.
- Qualquer passo que altere o desktop do proprietário (carregar script no KWin, regras de janela, instalar
  pacotes) está marcado **REQUER AUTORIZAÇÃO** e não é executado por padrão.

## Fatos de empacotamento observados no contêiner remoto (NÃO substituem o teste na máquina-alvo)

Observados em Linux x86_64 com a wheel `PySide6==6.11.3` (a mesma fixada em `requirements.txt`):

| Fato | Observação |
|---|---|
| Plugin de plataforma Wayland | `plugins/platforms/libqwayland.so` presente na wheel |
| Plugins de shell Wayland da wheel | `libxdg-shell.so`, `libwl-shell-plugin.so`, `libivi-shell.so`, `libfullscreen-shell-v1.so`, `libqt-shell.so` |
| Plugin de layer-shell na wheel | **ausente** |
| Biblioteca LayerShellQt na wheel | **ausente** |
| Módulo Python `PySide6.QtWaylandClient` | **ausente** |
| Plataforma `wayland` sem compositor | o processo aborta (código −6), como esperado — por isso `sondar_qt.py` testa cada plataforma em processo-filho |

Implicações **ainda hipóteses** a confirmar em KDE real: usar layer-shell a partir de PySide6 exigiria
LayerShellQt do sistema e/ou um *binding*/caminho próprio, que a wheel não traz (teste T36–T38).
