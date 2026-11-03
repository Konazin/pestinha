"""
LAUNCHER XWAYLAND - inicia o Pestinha com o Qt em modo X11 (QT_QPA_PLATFORM=xcb).

Rodar (Linux, dentro de uma sessão KDE Wayland ou X11):
    python lancadores/pestinha_xwayland.py [opções do main.py]
    python lancadores/pestinha_xwayland.py --simular      mostra o que faria, sem abrir o app

Só o processo filho recebe a variável: a sessão KDE, o ambiente do usuário e o main.py não mudam.
Em Windows e macOS não faz nada (devolve 2): lá o main.py continua sendo o ponto de entrada.
Em sessão X11, xcb já é o padrão do Qt, então o resultado é o mesmo do main.py.
Sem DISPLAY (XWayland indisponível) recusa em vez de cair em outra plataforma sem avisar.
"""

import os
import sys
from pathlib import Path

MAIN = Path(__file__).resolve().parent.parent / "main.py"
PLATAFORMA_QT = "xcb"


def avaliar(env, plataforma):
    """Devolve (erro, avisos): erro é um texto quando o launcher não deve executar, senão None."""
    if not plataforma.startswith("linux"):
        return "o launcher XWayland é só para Linux; use `python main.py` neste sistema.", []
    if not env.get("DISPLAY"):
        return ("DISPLAY vazio: não há servidor X11/XWayland acessível nesta sessão. "
                "Nada foi iniciado (o Qt cairia em outra plataforma sem avisar)."), []
    avisos = []
    atual = env.get("QT_QPA_PLATFORM")
    if atual and atual != PLATAFORMA_QT:
        avisos.append(f"QT_QPA_PLATFORM={atual} no ambiente foi trocado por {PLATAFORMA_QT} neste processo.")
    return None, avisos


def montar_ambiente(env):
    """Cópia do ambiente com a plataforma do Qt fixada em xcb; o original não é alterado."""
    novo = dict(env)
    novo["QT_QPA_PLATFORM"] = PLATAFORMA_QT
    return novo


def main(argv=None, env=None, plataforma=None, executar=os.execve):
    """Valida a sessão e troca o processo pelo main.py; devolve o código de saída quando não executa."""
    argv = list(sys.argv[1:] if argv is None else argv)
    env = os.environ if env is None else env
    plataforma = sys.platform if plataforma is None else plataforma
    simular = "--simular" in argv
    repassar = [a for a in argv if a != "--simular"]

    erro, avisos = avaliar(env, plataforma)
    for aviso in avisos:
        print(f"aviso: {aviso}", file=sys.stderr)
    if erro:
        print(f"erro: {erro}", file=sys.stderr)
        return 2
    comando = [sys.executable, str(MAIN), *repassar]
    if simular:
        print(f"QT_QPA_PLATFORM={PLATAFORMA_QT} " + " ".join(comando))
        return 0
    executar(sys.executable, comando, montar_ambiente(env))
    return 0


if __name__ == "__main__":
    sys.exit(main())
