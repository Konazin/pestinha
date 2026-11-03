"""
Launcher XWayland (lancadores/pestinha_xwayland.py): só monta o ambiente do processo filho.

Não abre janela, não usa Qt e nunca mexe em os.environ do processo de teste.
"""
import ast
import os
from pathlib import Path

from lancadores import pestinha_xwayland as lx

RAIZ = Path(__file__).resolve().parent.parent
WAYLAND = {"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0", "DISPLAY": ":1"}


class Execucao:
    """Substitui os.execve: guarda o que seria executado."""
    def __init__(self):
        self.chamadas = []

    def __call__(self, programa, argv, env):
        self.chamadas.append((programa, argv, env))


def rodar(argv=(), env=None, plataforma="linux"):
    exe = Execucao()
    codigo = lx.main(list(argv), env=dict(WAYLAND if env is None else env), plataforma=plataforma, executar=exe)
    return codigo, exe


def test_define_xcb_e_executa_o_main_original():
    codigo, exe = rodar(["--direto", "--sair-em", "5"])
    assert codigo == 0 and len(exe.chamadas) == 1
    programa, argv, env = exe.chamadas[0]
    assert env["QT_QPA_PLATFORM"] == "xcb"
    assert argv[1:] == [str(RAIZ / "main.py"), "--direto", "--sair-em", "5"]
    assert programa == argv[0]


def test_preserva_o_resto_do_ambiente_e_nao_toca_em_os_environ():
    antes = dict(os.environ)
    _, exe = rodar(env={**WAYLAND, "FOO": "bar", "WAYLAND_DISPLAY": "wayland-9"})
    env = exe.chamadas[0][2]
    assert env["FOO"] == "bar" and env["WAYLAND_DISPLAY"] == "wayland-9" and env["XDG_SESSION_TYPE"] == "wayland"
    assert dict(os.environ) == antes


def test_sobrescreve_plataforma_diferente_e_avisa(capsys):
    _, exe = rodar(env={**WAYLAND, "QT_QPA_PLATFORM": "wayland"})
    assert exe.chamadas[0][2]["QT_QPA_PLATFORM"] == "xcb"
    assert "wayland" in capsys.readouterr().err


def test_sem_display_recusa_sem_executar(capsys):
    codigo, exe = rodar(env={"XDG_SESSION_TYPE": "wayland", "WAYLAND_DISPLAY": "wayland-0"})
    assert codigo == 2 and exe.chamadas == []
    assert "DISPLAY" in capsys.readouterr().err


def test_sessao_x11_continua_funcionando():
    codigo, exe = rodar(env={"XDG_SESSION_TYPE": "x11", "DISPLAY": ":0"})
    assert codigo == 0 and exe.chamadas[0][2]["QT_QPA_PLATFORM"] == "xcb"


def test_windows_e_macos_nao_sao_afetados(capsys):
    for plataforma in ("win32", "darwin"):
        codigo, exe = rodar(plataforma=plataforma)
        assert codigo == 2 and exe.chamadas == []
        assert "Linux" in capsys.readouterr().err


def test_simular_nao_executa_e_mostra_o_comando(capsys):
    codigo, exe = rodar(["--simular", "--direto"])
    saida = capsys.readouterr().out
    assert codigo == 0 and exe.chamadas == []
    assert "QT_QPA_PLATFORM=xcb" in saida and "--direto" in saida and "--simular" not in saida.split("main.py")[1]


def test_nao_importa_qt_nem_o_pacote_pestinha():
    arvore = ast.parse(Path(lx.__file__).read_text(encoding="utf-8"))
    nomes = set()
    for no in ast.walk(arvore):
        if isinstance(no, ast.Import):
            nomes |= {a.name.split(".")[0] for a in no.names}
        elif isinstance(no, ast.ImportFrom) and no.module:
            nomes.add(no.module.split(".")[0])
    assert not nomes & {"PySide6", "pestinha"}


def test_main_py_continua_sem_conhecer_a_plataforma_grafica():
    assert "QT_QPA_PLATFORM" not in (RAIZ / "main.py").read_text(encoding="utf-8")
