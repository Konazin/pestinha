#!/usr/bin/env bash
# Empacota out/ para envio. PRIVACIDADE: por padrão NÃO inclui o journal do sistema. Revise o conteúdo antes de enviar.
# Uso: ./empacotar_resultados.sh [--com-journal]   (journal: só linhas de kwin/plasma/Qt/wayland dos últimos 30 min)
# O pacote (m1-resultados-*.tar.gz) é ignorado pelo git. Saída: 0 pacote criado · 1 nada para empacotar · 2 falha ao empacotar.
set -u
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; OUT="$AQUI/out"
[ -d "$OUT" ] && [ -n "$(ls -A "$OUT" 2>/dev/null)" ] || { echo "nada em out/"; exit 1; }
if [ "${1-}" = "--com-journal" ] && command -v journalctl >/dev/null 2>&1; then
  J="$OUT/journal-filtrado-$(date +%H%M%S).txt"
  journalctl --user -b --since "-30min" --no-pager 2>/dev/null | grep -i -E "kwin|plasmashell|qt\.|wayland|xwayland|portal" | tail -n 1500 >"$J"
  echo "Journal filtrado salvo em $J — REVISE: pode conter nomes de arquivos/aplicativos."
fi
ARQ="$AQUI/m1-resultados-$(date +%Y%m%d-%H%M%S).tar.gz"
if tar -C "$AQUI" -czf "$ARQ.tmp" out && mv "$ARQ.tmp" "$ARQ"; then echo "Gerado: $ARQ (ignorado pelo git; revise antes de enviar)"
else rm -f "$ARQ.tmp"; echo "falha ao empacotar" >&2; exit 2; fi
