#!/usr/bin/env bash
# S1 — roda o Pestinha ORIGINAL, sem modificá-lo, numa CÓPIA TEMPORÁRIA do commit atual (git archive),
# para que `memory/` do proprietário não seja tocada. Uso:
#   ./rodar_pestinha_original.sh xcb|wayland [SEGUNDOS=90] [PASTA_SAIDA]
# (`offscreen` existe só para teste de fumaça dos scripts: o cabeçalho marca "NÃO VÁLIDO PARA A MATRIZ".)
# Requisitos: PySide6 6.11.3 + psutil + numpy no Python usado (venv do proprietário).
# Privacidade: o app original registra o atalho global via pynput no Linux e lê o NOME do programa ativo
# (nunca o título). Encerre com o menu da bandeja ou Ctrl+C.
#
# Código de saída do script = código do app (0 = o app encerrou sozinho, 124 = estourou o tempo e foi
# interrompido, 130/143 = Ctrl+C/SIGTERM, 134 = abort, 139 = falha de segmentação, outros = erro do app).
# 0 NÃO é PASS: PASS vem da observação do operador na matriz. Argumentos inválidos: 2.
set -u
PLAT="${1:-}"; SEG="${2:-90}"
case "$PLAT" in xcb|wayland|offscreen) ;; *) echo "uso: $0 xcb|wayland [SEGUNDOS] [PASTA_SAIDA]" >&2; exit 2;; esac
case "$SEG" in ''|*[!0-9]*) echo "SEGUNDOS deve ser inteiro" >&2; exit 2;; esac
AQUI="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"; REPO="$(cd "$AQUI/../.." && pwd)"
OUT="${3:-$AQUI/out/$(date +%Y%m%d-%H%M%S)-pestinha-$PLAT}"; mkdir -p "$OUT"
TMP="$(mktemp -d)"; RC=""; PID=""
parar_app() {   # encerramento escalonado do grupo do app: INT (3 s) -> TERM (2 s) -> KILL
  [ -n "$PID" ] || return 0
  kill -0 "$PID" 2>/dev/null || return 0
  kill -INT -- "-$PID" 2>/dev/null || kill -INT "$PID" 2>/dev/null
  for _ in 1 2 3 4 5 6; do sleep 0.5; kill -0 "$PID" 2>/dev/null || return 0; done
  kill -TERM -- "-$PID" 2>/dev/null || kill -TERM "$PID" 2>/dev/null
  for _ in 1 2 3 4; do sleep 0.5; kill -0 "$PID" 2>/dev/null || return 0; done
  kill -KILL -- "-$PID" 2>/dev/null || kill -KILL "$PID" 2>/dev/null
}
finalizar() {   # roda SEMPRE na saída (inclusive Ctrl+C/SIGTERM): fecha os arquivos de resultado e apaga a cópia
  trap - EXIT INT TERM
  parar_app
  [ -n "$PID" ] && wait "$PID" 2>/dev/null
  [ -z "$RC" ] && RC=1
  [ -f "$TMP/memory/logs/pestinha.log" ] && cp "$TMP/memory/logs/pestinha.log" "$OUT/app.log" 2>/dev/null
  [ -f "$OUT/pestinha.stderr.log" ] && tail -n 40 "$OUT/pestinha.stderr.log" >"$OUT/stderr_final.txt"
  { echo "rc=$RC"; echo "terminou_em=$(date +%Y-%m-%dT%H:%M:%S)"; } >>"$OUT/cabecalho.txt"
  rm -rf "$TMP"
  echo "Logs em $OUT (rc=$RC; 0 NÃO é PASS; revise antes de compartilhar)."
  exit "$RC"
}
trap 'RC=130; finalizar' INT
trap 'RC=143; finalizar' TERM
trap finalizar EXIT
git -C "$REPO" archive HEAD | tar -x -C "$TMP" || { echo "git archive falhou"; RC=1; exit 1; }
{ echo "commit: $(git -C "$REPO" rev-parse HEAD)"; echo "plataforma pedida: $PLAT"; echo "XDG_SESSION_TYPE=${XDG_SESSION_TYPE-}"
  [ "$PLAT" = offscreen ] && echo "AVISO: offscreen = teste de fumaça, NÃO VÁLIDO PARA A MATRIZ"
  echo "iniciou_em=$(date +%Y-%m-%dT%H:%M:%S)"; } >"$OUT/cabecalho.txt"
echo "Rodando por ${SEG}s com QT_QPA_PLATFORM=$PLAT. Observe e anote (matriz T06–T09). Cópia em $TMP (apagada no fim)."
# Em segundo plano + `wait`: o bash só roda o trap depois que um comando em primeiro plano termina, então
# um comando em primeiro plano tornaria Ctrl+C inútil até o fim do app. `setsid` dá ao app um grupo próprio.
SETSID=""; command -v setsid >/dev/null 2>&1 && SETSID="setsid"
( cd "$TMP" && QT_QPA_PLATFORM="$PLAT" QT_DEBUG_PLUGINS=1 QT_LOGGING_RULES="qt.qpa.*=true" \
  exec $SETSID timeout --signal=INT --kill-after=5 "$((SEG+10))" python3 main.py --direto --sair-em "$SEG" ) \
  >"$OUT/pestinha.stdout.log" 2>"$OUT/pestinha.stderr.log" &
PID=$!
wait "$PID"
RC=$?
PID=""
exit "$RC"
