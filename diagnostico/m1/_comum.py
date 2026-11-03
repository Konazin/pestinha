"""Utilitários comuns das sondas M1. Isolado: NÃO importa nada de `pestinha/`."""
import json
import os
import platform
import sys
import time
from pathlib import Path

AQUI = Path(__file__).resolve().parent
# Somente estas variáveis de ambiente são registradas (nada de segredos, hostname ou usuário).
VARS_PERMITIDAS = (
    "XDG_SESSION_TYPE", "XDG_CURRENT_DESKTOP", "XDG_SESSION_DESKTOP", "WAYLAND_DISPLAY", "DISPLAY",
    "QT_QPA_PLATFORM", "QT_QPA_PLATFORM_PLUGIN_PATH", "QT_PLUGIN_PATH", "QT_SCALE_FACTOR",
    "QT_AUTO_SCREEN_SCALE_FACTOR", "QT_ENABLE_HIGHDPI_SCALING", "QT_SCREEN_SCALE_FACTORS",
    "QT_WAYLAND_DISABLE_WINDOWDECORATION", "QT_WAYLAND_SHELL_INTEGRATION", "LANG",
)


def pasta_saida(nome, base=None):
    """Cria `out/<data>-<nome>/` (ignorada pelo git) e devolve o caminho."""
    raiz = Path(base) if base else AQUI / "out"
    destino = raiz / f"{time.strftime('%Y%m%d-%H%M%S')}-{nome}"
    destino.mkdir(parents=True, exist_ok=True)
    return destino


def ambiente_basico():
    """Dados mínimos e não sensíveis do ambiente."""
    return {
        "python": sys.version.split()[0],
        "sistema": platform.platform(),
        "variaveis": {k: os.environ.get(k) for k in VARS_PERMITIDAS if os.environ.get(k) is not None},
    }


class Registro:
    """Escreve eventos JSON Lines (um por linha) e espelha no terminal."""

    def __init__(self, caminho, eco=True):
        self.caminho = Path(caminho)
        self.eco = eco
        self.t0 = time.monotonic()
        self.arq = open(self.caminho, "a", encoding="utf-8", buffering=1)

    def evento(self, tipo, **campos):
        linha = {"t": round(time.monotonic() - self.t0, 4), "wall": time.strftime("%H:%M:%S"), "tipo": tipo, **campos}
        self.arq.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")
        if self.eco:
            print(f"[{linha['t']:8.3f}] {tipo} " + " ".join(f"{k}={v}" for k, v in campos.items()), flush=True)

    def fechar(self):
        self.arq.close()


def perguntar(texto, opcoes=("s", "n", "nt")):
    """Pergunta ao operador (stdin). `nt` = não testado. Sem terminal interativo devolve 'nt'."""
    if not sys.stdin or not sys.stdin.isatty():
        return "nt"
    while True:
        r = input(f"{texto} [{'/'.join(opcoes)}] ").strip().lower()
        if r in opcoes:
            return r


def libs_qt_carregadas():
    """Caminhos únicos de bibliotecas Qt/Wayland/EGL mapeadas no processo (Linux)."""
    achados = set()
    try:
        with open("/proc/self/maps", encoding="utf-8") as f:
            for linha in f:
                partes = linha.split()
                if len(partes) >= 6 and any(s in partes[5] for s in ("libQt6", "libwayland", "libEGL", "libxcb.so", "qwayland", "libqxcb")):
                    achados.add(partes[5])
    except OSError:
        pass
    return sorted(achados)
