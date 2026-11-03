"""Utilitários comuns das sondas M1. Isolado: NÃO importa nada de `pestinha/`."""
import json
import os
import platform
import sys
import threading
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
        reservados = {"t", "wall", "tipo"} & set(campos)
        if reservados:   # nunca deixar um campo sobrescrever a estrutura do evento
            raise ValueError(f"campos reservados no evento {tipo!r}: {sorted(reservados)}")
        linha = {"t": round(time.monotonic() - self.t0, 4), "wall": time.strftime("%H:%M:%S"), "tipo": tipo, **campos}
        self.arq.write(json.dumps(linha, ensure_ascii=False, default=str) + "\n")
        if self.eco:
            print(f"[{linha['t']:8.3f}] {tipo} " + " ".join(f"{k}={v}" for k, v in campos.items()), flush=True)

    def fechar(self):
        self.arq.close()


def perguntar(texto, opcoes=("s", "n", "nt")):
    """Pergunta ao operador (stdin). `nt` = não testado. Sem terminal interativo ou em EOF devolve 'nt'.

    Usa `sys.stdin.readline()` e NÃO `input()`: com PySide6 carregado, `input()` passa por um *input hook*
    que mantém o Qt processando eventos (timers disparam) e engole o KeyboardInterrupt dentro dos slots,
    deixando o Ctrl+C sem efeito. Ctrl+C propaga como KeyboardInterrupt; quem chama decide como finalizar
    (ver `CODIGOS`).
    """
    if not sys.stdin or not sys.stdin.isatty():
        return "nt"
    while True:
        print(f"{texto} [{'/'.join(opcoes)}] ", end="", flush=True)
        linha = sys.stdin.readline()
        if linha == "":          # EOF
            return "nt"
        r = linha.strip().lower()
        if r in opcoes:
            return r


# Códigos de saída das sondas Python. Atenção: código 0 significa "a sonda terminou e gravou os
# arquivos", NUNCA "o teste passou". PASS/FAIL só existe na matriz, com evidência.
CODIGOS = {
    "concluido": 0,      # execução completa; resumo.json final gravado
    "erro": 1,           # exceção inesperada (traceback em eventos.jsonl); resumo.json gravado
    # 2 = argumentos inválidos (argparse, antes de criar qualquer arquivo)
    "vigia_forcou_saida": 3,   # o vigia detectou travamento e encerrou o processo
    "interrompido": 4,   # SIGINT/SIGTERM/Ctrl+C; resumo.json gravado com o que havia
}


def escrever_json_atomico(caminho, dados):
    """Grava JSON em arquivo temporário e troca (nunca deixa resumo.json pela metade)."""
    caminho = Path(caminho)
    tmp = caminho.with_suffix(caminho.suffix + ".tmp")
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(dados, f, indent=2, ensure_ascii=False, default=str)
        f.flush()
        os.fsync(f.fileno())
    os.replace(tmp, caminho)


class Vigia:
    """Proteção contra travamento: se não for cancelado a tempo, grava o estado e força a saída (código 3).

    A thread é DAEMON e espera num `Event`: `cancelar()` a acorda e ela termina sem agir, então o
    encerramento normal nunca é adiado nem convertido em saída forçada.
    """

    def __init__(self):
        self._cancelado = threading.Event()
        self._thread = None
        self.disparou = False

    def armar(self, segundos, ao_disparar=None, codigo=CODIGOS["vigia_forcou_saida"]):
        def vigiar():
            if self._cancelado.wait(segundos):
                return                      # cancelado: saída normal, nada a fazer
            self.disparou = True
            try:
                if ao_disparar:
                    ao_disparar()
            except Exception:
                pass                        # o vigia nunca pode deixar de encerrar
            finally:
                os._exit(codigo)

        self._thread = threading.Thread(target=vigiar, name="vigia-m1", daemon=True)
        self._thread.start()

    def cancelar(self):
        self._cancelado.set()
        if self._thread is not None and self._thread is not threading.current_thread():
            self._thread.join(timeout=2)


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
