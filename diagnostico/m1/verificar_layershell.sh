#!/usr/bin/env bash
# Viabilidade de LayerShellQt (investigação 8): SOMENTE LEITURA. Não escolhe solução; apenas coleta fatos.
# Uso: ./verificar_layershell.sh [PASTA_SAIDA]
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$AQUI/out/$(date +%Y%m%d-%H%M%S)-layershell}"; mkdir -p "$OUT"; R="$OUT/layershell.txt"; : >"$R"
sec() { printf '\n===== %s =====\n' "$*" >>"$R"; }
sec "Bibliotecas/pacotes LayerShellQt no sistema"
{ ldconfig -p 2>/dev/null | grep -i -E "layershell" || echo "(nenhuma lib LayerShellQt em ldconfig)"; } >>"$R"
{ dpkg -l 2>/dev/null | grep -i -E "layer-?shell" || echo "(nenhum pacote dpkg com layer-shell)"; } >>"$R"
{ apt-cache policy liblayershellqtinterface6 liblayershellqtinterface-dev layer-shell-qt 2>&1 | head -30; } >>"$R"
sec "Plugins Qt de integração de shell Wayland (sistema)"
for d in /usr/lib/x86_64-linux-gnu/qt6/plugins/wayland-shell-integration /usr/lib/qt6/plugins/wayland-shell-integration; do
  [ -d "$d" ] && { echo "$d:"; ls "$d"; } >>"$R"; done
sec "Plugins Qt de shell Wayland (wheel do PySide6)"
python3 - >>"$R" 2>&1 <<'PY'
import os
try:
    from PySide6.QtCore import QLibraryInfo
    d = os.path.join(QLibraryInfo.path(QLibraryInfo.PluginsPath), "wayland-shell-integration")
    print(d, sorted(os.listdir(d)) if os.path.isdir(d) else "ausente")
except Exception as e:
    print("PySide6 indisponível:", e)
PY
sec "Binding Python para LayerShellQt?"
python3 - >>"$R" 2>&1 <<'PY'
for nome in ("LayerShellQt", "layershellqt", "PySide6.QtWaylandClient", "gi"):
    try:
        __import__(nome); print(nome, ": importável")
    except Exception as e:
        print(nome, ": NÃO importável (", type(e).__name__, ")")
PY
sec "O compositor anuncia layer-shell? (wayland-info, se instalado)"
if command -v wayland-info >/dev/null 2>&1; then
  { timeout 15 wayland-info 2>&1 | grep -E "zwlr_layer_shell_v1|xdg_wm_base|ext_session_lock" || echo "(layer-shell NÃO listado)"; } >>"$R"
else echo "wayland-info ausente (pacote wayland-utils, opcional)" >>"$R"; fi
echo "Concluído: $R"
