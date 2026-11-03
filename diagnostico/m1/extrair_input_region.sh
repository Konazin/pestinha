#!/usr/bin/env bash
# Extrai de um log WAYLAND_DEBUG as requisições que mostram O QUE o Qt enviou ao compositor sobre a região de
# entrada (somente leitura do log). É a única evidência do lado cliente sobre a input region efetiva.
# Gerar o log (manual): WAYLAND_DEBUG=client python3 sonda_janela.py --plataforma wayland --modo regiao ... 2> wayland-debug.log
# Uso: ./extrair_input_region.sh wayland-debug.log
# Interpretação (semântica do protocolo, de memória; reconfirmar na especificação oficial):
#   set_input_region(nil)          -> região de entrada INFINITA (a superfície inteira aceita entrada)
#   set_input_region(wl_region@N)  -> região definida; o conteúdo vem de wl_region@N.add(x, y, w, h)
#   wl_region criada sem nenhum .add -> região VAZIA (nenhuma entrada)
#   as mudanças só valem após wl_surface.commit
# O formato exato das linhas depende da versão do libwayland: o script apenas filtra por palavra-chave.
set -u
LOG="${1:?uso: $0 wayland-debug.log}"
[ -r "$LOG" ] || { echo "log ilegível: $LOG" >&2; exit 2; }
echo "# set_input_region / wl_region / commit (ordem original do log)"
grep -n -E "set_input_region|wl_region@[0-9]+\.(add|subtract|destroy)|wl_compositor@[0-9]+\.create_region|wl_surface@[0-9]+\.commit" "$LOG" || { echo "(nenhuma ocorrência: o log não contém essas requisições)"; exit 1; }
