#!/usr/bin/env bash
# Empacota out/ para envio. PRIVACIDADE: por padrão NÃO inclui o journal do sistema. Revise o conteúdo antes de enviar.
# Uso: ./empacotar_resultados.sh [--com-journal]   (journal: só linhas de kwin/plasma/Qt/wayland dos últimos 30 min)
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; OUT="$AQUI/out"; [ -d "$OUT" ] || { echo "nada em out/"; exit 1; }
if [ "${1-}" = "--com-journal" ] && command -v journalctl >/dev/null 2>&1; then
  J="$OUT/journal-filtrado-$(date +%H%M%S).txt"
  journalctl --user -b --since "-30min" --no-pager 2>/dev/null | grep -i -E "kwin|plasmashell|qt\.|wayland|xwayland|portal" | tail -n 1500 >"$J"
  echo "Journal filtrado salvo em $J — REVISE: pode conter nomes de arquivos/aplicativos."
fi
ARQ="$AQUI/m1-resultados-$(date +%Y%m%d-%H%M%S).tar.gz"
tar -C "$AQUI" -czf "$ARQ" out && echo "Gerado: $ARQ"
