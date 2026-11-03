#!/usr/bin/env bash
# S1 — roda o Pestinha ORIGINAL, sem modificá-lo, numa CÓPIA TEMPORÁRIA do commit atual (git archive),
# para que `memory/` do proprietário não seja tocada. Uso:
#   ./rodar_pestinha_original.sh xcb|wayland [SEGUNDOS=90] [PASTA_SAIDA]
# Requisitos: PySide6 6.11.3 + psutil + numpy no Python usado (venv do proprietário).
# Observação de privacidade: o app original registra o atalho global via pynput no Linux e lê o NOME do
# programa ativo (nunca o título). Rode apenas se concordar; encerre com o menu da bandeja ou Ctrl+C.
set -u
PLAT="${1:?use xcb ou wayland}"; SEG="${2:-90}"
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$AQUI/../.." && pwd)"
OUT="${3:-$AQUI/out/$(date +%Y%m%d-%H%M%S)-pestinha-$PLAT}"; mkdir -p "$OUT"
TMP="$(mktemp -d)"; trap 'rm -rf "$TMP"' EXIT
git -C "$REPO" archive HEAD | tar -x -C "$TMP" || { echo "git archive falhou"; exit 1; }
{ echo "commit: $(git -C "$REPO" rev-parse HEAD)"; echo "plataforma pedida: $PLAT"; echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE-}"; } >"$OUT/cabecalho.txt"
echo "Rodando por ${SEG}s com QT_QPA_PLATFORM=$PLAT. Observe e anote (matriz T01–T09). Cópia em $TMP (apagada no fim)."
( cd "$TMP" && QT_QPA_PLATFORM="$PLAT" QT_DEBUG_PLUGINS=1 QT_LOGGING_RULES="qt.qpa.*=true" \
  timeout --signal=INT "$((SEG+10))" python3 main.py --direto --sair-em "$SEG" ) >"$OUT/pestinha.stdout.log" 2>"$OUT/pestinha.stderr.log"
echo "rc=$?" >>"$OUT/cabecalho.txt"
tail -n 40 "$OUT/pestinha.stderr.log" >"$OUT/stderr_final.txt"
[ -f "$TMP/memory/logs/pestinha.log" ] && cp "$TMP/memory/logs/pestinha.log" "$OUT/app.log"
echo "Logs em $OUT (revise antes de compartilhar)."
