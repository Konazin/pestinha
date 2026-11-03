#!/usr/bin/env bash
# Introspecção SOMENTE LEITURA do KWin e do portal de atalhos (investigação 7 e 10/atalho).
# NÃO chama loadScript/start/unloadScript, NÃO instala nada no KWin, NÃO altera configuração.
# Uso: ./verificar_kwin_dbus.sh [PASTA_SAIDA]
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
OUT="${1:-$AQUI/out/$(date +%Y%m%d-%H%M%S)-kwin-dbus}"; mkdir -p "$OUT"; R="$OUT/kwin-dbus.txt"; : >"$R"
if ! command -v busctl >/dev/null 2>&1; then echo "busctl ausente" | tee "$R"; exit 0; fi
run() { { printf '$ %s\n' "$*"; timeout 15 "$@" 2>&1 || printf '[rc=%s]\n' "$?"; } >>"$R"; }
printf '===== Objetos de org.kde.KWin =====\n' >>"$R"
run busctl --user tree org.kde.KWin --no-pager
printf '\n===== /Scripting: métodos e propriedades (introspecção) =====\n' >>"$R"
run busctl --user introspect org.kde.KWin /Scripting --no-pager
printf '\n===== /KWin: métodos (introspecção; procure sobre janelas/posição) =====\n' >>"$R"
run busctl --user introspect org.kde.KWin /KWin --no-pager
printf '\n===== Portal XDG: interfaces e versão de GlobalShortcuts =====\n' >>"$R"
{ echo '$ busctl --user introspect org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop | grep GlobalShortcuts'
  busctl --user introspect org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop --no-pager 2>&1 | grep -i -E "GlobalShortcuts|\.version" || echo "(GlobalShortcuts não listado)"; } >>"$R"
run busctl --user get-property org.freedesktop.portal.Desktop /org/freedesktop/portal/desktop org.freedesktop.portal.GlobalShortcuts version
printf '\n===== Scripts KWin já carregados? (somente leitura de config) =====\n' >>"$R"
{ echo '$ grep -i "Enabled" ~/.config/kwinrc (apenas seção [Plugins])'
  awk '/^\[Plugins\]/{f=1;next}/^\[/{f=0}f' "$HOME/.config/kwinrc" 2>/dev/null || echo "(sem kwinrc)"; } >>"$R"
echo "Concluído: $R"
