#!/usr/bin/env bash
# Coleta SOMENTE LEITURA do ambiente (investigações 6, 8, 9, 10). Não instala, não altera configuração,
# não carrega scripts no KWin, não lê títulos de janelas. Uso: ./coletar_ambiente.sh [PASTA_SAIDA]
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$AQUI/out/$(date +%Y%m%d-%H%M%S)-ambiente}"
mkdir -p "$OUT"
R="$OUT/ambiente.txt"
sec() { printf '\n===== %s =====\n' "$*" >>"$R"; }
run() { { printf '$ %s\n' "$*"; timeout 15 "$@" 2>&1 || printf '[rc=%s]\n' "$?"; } >>"$R"; }
tem() { command -v "$1" >/dev/null 2>&1; }

: >"$R"
sec "Identidade da sessão (variáveis permitidas)"
for v in XDG_SESSION_TYPE XDG_CURRENT_DESKTOP XDG_SESSION_DESKTOP WAYLAND_DISPLAY DISPLAY QT_QPA_PLATFORM QT_SCALE_FACTOR; do
  printf '%s=%s\n' "$v" "${!v-<não definida>}" >>"$R"; done
sec "Sistema"
run cat /etc/os-release
run uname -srmo
run python3 --version
sec "Plasma / KWin (versões)"
for c in plasmashell kwin_wayland kwin_x11; do if tem $c; then run $c --version; else echo "$c: ausente" >>"$R"; fi; done
for c in qtpaths6 qtpaths; do if tem $c; then run $c --qt-version; break; fi; done
sec "Processo do compositor (confirma KWin Wayland real)"
run pgrep -a kwin_wayland
sec "Pacotes relevantes (versões instaladas)"
if tem dpkg-query; then
  run dpkg-query -W -f='${Package} ${Version}\n' 'libqt6core6*' 'libqt6gui6*' 'qt6-wayland*' 'libqt6waylandclient6*' \
      'kwin-wayland*' 'kwin-common*' 'plasma-desktop*' 'xdg-desktop-portal*' 'libkf6windowsystem6*' \
      'liblayershellqtinterface*' 'layer-shell-qt*' 'python3-pyside6*' 'wayland-utils' 'xwayland' 'libwayland-client0'
else echo "dpkg-query ausente" >>"$R"; fi
sec "Candidatos de pacote (apt-cache policy, sem instalar)"
if tem apt-cache; then run apt-cache policy python3-pyside6.qtwidgets liblayershellqtinterface6 qt6-wayland wayland-utils xwayland; fi
sec "PySide6 em pip (se houver)"
run python3 -m pip show PySide6
sec "Monitores e escalas (kscreen-doctor, somente leitura)"
if tem kscreen-doctor; then run kscreen-doctor -o; else echo "kscreen-doctor ausente" >>"$R"; fi
if tem wlr-randr; then run wlr-randr; fi
sec "Protocolos Wayland anunciados (wayland-info, se instalado)"
if tem wayland-info; then
  timeout 15 wayland-info >"$OUT/wayland-info.txt" 2>&1
  grep -E "interface: '(xdg_wm_base|zwlr_layer_shell_v1|wp_fractional_scale_manager_v1|wp_viewporter|zxdg_output_manager_v1|zxdg_decoration_manager_v1|org_kde_plasma_shell|org_kde_kwin_[a-z_]+|wl_compositor|ext_session_lock_manager_v1)'" "$OUT/wayland-info.txt" >>"$R" || echo "(nenhum dos protocolos de interesse encontrado)" >>"$R"
else echo "wayland-info ausente (opcional: pacote wayland-utils; instalação é decisão do proprietário)" >>"$R"; fi
sec "XWayland"
run pgrep -a Xwayland
sec "Barramento de sessão: serviços de interesse (nomes apenas)"
if tem busctl; then
  { echo '$ busctl --user list | grep -Ei "kwin|portal|kglobalaccel|plasmashell"'; busctl --user list --no-pager 2>&1 | grep -Ei "kwin|portal|kglobalaccel|plasmashell" || echo "(nenhum)"; } >>"$R"
fi
sec "Wheel do PySide6: plugins (fatos de empacotamento)"
python3 - >>"$R" 2>&1 <<'PY'
try:
    import PySide6, os
    from PySide6.QtCore import QLibraryInfo, qVersion
    p = QLibraryInfo.path(QLibraryInfo.PluginsPath)
    print("PySide6", PySide6.__version__, "Qt", qVersion(), "plugins:", p)
    for d in ("platforms", "wayland-shell-integration", "wayland-decoration-client"):
        q = os.path.join(p, d)
        print(d, sorted(os.listdir(q)) if os.path.isdir(q) else "ausente")
    try:
        import PySide6.QtWaylandClient  # noqa
        print("PySide6.QtWaylandClient: presente")
    except Exception as e:
        print("PySide6.QtWaylandClient: ausente (", e, ")")
except Exception as e:
    print("PySide6 indisponível:", e)
PY
printf 'Concluído. Revise %s antes de compartilhar.\n' "$R"
