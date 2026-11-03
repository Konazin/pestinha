# Ferramentas de diagnóstico M1 (isoladas)

Scripts **somente de diagnóstico** para a validação do Pestinha em Debian 13 + KDE Plasma 6 + Wayland.
Não fazem parte do app: não importam `pestinha/`, não entram em testes nem no empacotamento. Guia completo:
[`docs/m1/RUNBOOK-M1.md`](../../docs/m1/RUNBOOK-M1.md).

| Script | Faz |
|---|---|
| `coletar_ambiente.sh` | Versões, sessão, monitores, protocolos, pacotes, fatos da wheel (somente leitura) |
| `sondar_qt.py` | Compatibilidade PySide6×Qt por plataforma (processo-filho por plataforma) |
| `sonda_janela.py` | Janela de teste: posicionamento, transparência, região de entrada, superfície grande |
| `sonda_ciclo.py` | Registra foco, fullscreen, bloqueio, hotplug e congelamentos |
| `rodar_pestinha_original.sh` | S1: roda o app original, sem modificá-lo, numa cópia temporária |
| `verificar_kwin_dbus.sh` | Introspecção D-Bus do KWin e do portal (**sem carregar scripts**) |
| `verificar_layershell.sh` | Fatos sobre LayerShellQt / layer-shell (somente leitura) |
| `extrair_input_region.sh` | Filtra de um log `WAYLAND_DEBUG` as requisições `set_input_region`/`wl_region` (somente leitura) |
| `empacotar_resultados.sh` | Empacota `out/` (journal só com `--com-journal`) |

Garantias: nada é instalado, nenhuma configuração do desktop é alterada, nenhum script é carregado no KWin,
sem entrada sintética, sem controle do cursor, sem captura de tela, sem leitura de títulos. Saídas em `out/` (git-ignorado).
Requisitos: Python ≥ 3.11 com `PySide6==6.11.3` (venv do usuário); `psutil numpy pynput` só para `rodar_pestinha_original.sh`.

## Códigos de saída (0 NÃO é PASS)
Sondas Python: `0` concluído · `1` erro · `2` argumentos inválidos · `3` vigia forçou saída (travamento) · `4` interrompido
(Ctrl+C/SIGTERM). `resumo.json` (gravação atômica) traz `status` e `codigo_saida`. O vigia é uma thread *daemon*, cancelada no
encerramento normal. `rodar_pestinha_original.sh` devolve o código do app (0, 124, 130/143, 134…). `empacotar_resultados.sh`:
0 pacote criado · 1 nada em `out/` · 2 falha. Pacotes `m1-resultados-*.tar.gz` e `out/` são ignorados pelo git.
Semântica de máscara/região de entrada: [`docs/m1/SEMANTICA-REGIAO-ENTRADA.md`](../../docs/m1/SEMANTICA-REGIAO-ENTRADA.md).
