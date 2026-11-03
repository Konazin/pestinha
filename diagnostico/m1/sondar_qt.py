#!/usr/bin/env python3
"""Sondagem de compatibilidade PySide6 × Qt (investigação 6). Não abre janelas visíveis.

Para cada plugin de plataforma pedido, roda um processo-filho que cria um QApplication e relata
platformName, telas (geometria, DPR, DPI) e de onde as bibliotecas Qt foram carregadas
(wheel do PySide6 ou sistema). Um abort nativo num filho não derruba a sondagem.

Códigos de saída (0 = coleta concluída e qt.json gravado; NÃO significa que as plataformas funcionam —
leia `plataformas.<nome>.codigo_saida` em qt.json): 0 concluído · 1 PySide6 indisponível · 2 argumentos inválidos.
Um filho que aborta (ex.: código −6 sem compositor) é registrado, não derruba a sondagem.

Uso:  python3 sondar_qt.py [--plataformas xcb wayland] [--saida PASTA]
"""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import ambiente_basico, escrever_json_atomico, libs_qt_carregadas, pasta_saida  # noqa: E402


def filho(plataforma):
    os.environ["QT_QPA_PLATFORM"] = plataforma
    import PySide6
    from PySide6.QtCore import QLibraryInfo, qVersion
    from PySide6.QtWidgets import QApplication
    app = QApplication(sys.argv[:1])
    from PySide6.QtGui import QGuiApplication
    telas = []
    for t in QGuiApplication.screens():
        g, a = t.geometry(), t.availableGeometry()
        telas.append({
            "nome": t.name(), "geometria": [g.x(), g.y(), g.width(), g.height()],
            "disponivel": [a.x(), a.y(), a.width(), a.height()], "dpr": t.devicePixelRatio(),
            "dpi_logico": round(t.logicalDotsPerInch(), 2), "dpi_fisico": round(t.physicalDotsPerInch(), 2),
            "taxa_hz": t.refreshRate(), "primaria": t is QGuiApplication.primaryScreen(),
        })
    print(json.dumps({
        "pyside6": PySide6.__version__, "qt": qVersion(), "platformName": QGuiApplication.platformName(),
        "plugins_qt": QLibraryInfo.path(QLibraryInfo.PluginsPath), "libs_qt": QLibraryInfo.path(QLibraryInfo.LibrariesPath),
        "telas": telas, "bibliotecas_carregadas": libs_qt_carregadas(),
    }))
    app.quit()
    return 0


def listar(dirpath):
    p = Path(dirpath)
    return sorted(x.name for x in p.iterdir()) if p.is_dir() else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--plataformas", nargs="+", default=["xcb", "wayland"])
    ap.add_argument("--saida")
    ap.add_argument("--filho")
    a = ap.parse_args()
    if a.filho:
        return filho(a.filho)

    pasta = pasta_saida("qt", a.saida)
    resultado = {"ambiente": ambiente_basico(), "plataformas": {}}
    try:
        import PySide6
        from PySide6.QtCore import QLibraryInfo, qVersion
        plug = QLibraryInfo.path(QLibraryInfo.PluginsPath)
        resultado["pyside6"] = PySide6.__version__
        resultado["qt_da_wheel"] = qVersion()
        resultado["plugins_dir"] = plug
        resultado["plugins_platforms"] = listar(Path(plug) / "platforms")
        resultado["plugins_wayland_shell"] = listar(Path(plug) / "wayland-shell-integration")
    except Exception as erro:  # PySide6 ausente
        resultado["erro_pyside6"] = repr(erro)
    for sistema in ("/usr/lib/x86_64-linux-gnu/qt6/plugins", "/usr/lib/qt6/plugins"):
        if Path(sistema).is_dir():
            resultado.setdefault("plugins_do_sistema", {})[sistema] = {
                "platforms": listar(Path(sistema) / "platforms"),
                "wayland-shell-integration": listar(Path(sistema) / "wayland-shell-integration"),
            }
    for plat in a.plataformas:
        env = dict(os.environ, QT_DEBUG_PLUGINS="1")
        try:
            r = subprocess.run([sys.executable, __file__, "--filho", plat], capture_output=True, text=True, timeout=30, env=env)
            ultima = r.stdout.strip().splitlines()[-1] if r.stdout.strip() else ""
            try:
                dados = json.loads(ultima)
            except ValueError:
                dados = None
            (pasta / f"qt_debug_plugins_{plat}.log").write_text(r.stderr[-20000:], encoding="utf-8")  # fecha ao sair do with implícito
            resultado["plataformas"][plat] = {"codigo_saida": r.returncode, "dados": dados,
                                               "stderr_final": r.stderr.strip().splitlines()[-5:]}
        except subprocess.TimeoutExpired:
            resultado["plataformas"][plat] = {"codigo_saida": "timeout"}
    codigo = 1 if "erro_pyside6" in resultado else 0
    resultado["status"] = "pyside6_indisponivel" if codigo else "concluido"
    resultado["codigo_saida"] = codigo
    escrever_json_atomico(pasta / "qt.json", resultado)
    print(json.dumps(resultado, indent=2, ensure_ascii=False))
    print(f"\nSalvo em {pasta / 'qt.json'} (código de saída={codigo}; 0 NÃO é PASS)")
    return codigo


if __name__ == "__main__":
    sys.exit(main())
