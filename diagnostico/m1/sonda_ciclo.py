#!/usr/bin/env python3
"""Sonda de ciclo de sessão (investigação 10): foco, fullscreen, bloqueio de tela, suspensão, telas.

Mostra uma janelinha de teste (flags do overlay do Pestinha) e REGISTRA, sem agir:
mudanças de estado do aplicativo, exposição/ocultação da janela, hotplug de telas e um batimento (1 s)
cujos atrasos (>2,5 s) denunciam congelamento (bloqueio/suspensão). Você executa as ações manuais.
Não gera entrada, não captura tela, não lê títulos de janelas.

Uso: python3 sonda_ciclo.py [--plataforma xcb|wayland|auto] [--tempo 240] [--saida PASTA]
"""
import argparse
import json
import os
import signal
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import Registro, ambiente_basico, pasta_saida, perguntar  # noqa: E402

ap = argparse.ArgumentParser()
ap.add_argument("--plataforma", choices=["auto", "xcb", "wayland"], default="auto")
ap.add_argument("--tempo", type=float, default=240.0)
ap.add_argument("--saida")
A = ap.parse_args()
if A.plataforma != "auto":
    os.environ["QT_QPA_PLATFORM"] = A.plataforma

from PySide6.QtCore import QEvent, QObject, Qt, QTimer  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

LOG = Registro(pasta_saida(f"ciclo-{A.plataforma}", A.saida) / "eventos.jsonl")
NOMES = {QEvent.Show: "Show", QEvent.Hide: "Hide", QEvent.Expose: "Expose", QEvent.WindowStateChange: "WindowStateChange",
         QEvent.WindowActivate: "WindowActivate", QEvent.WindowDeactivate: "WindowDeactivate", QEvent.ScreenChangeInternal: "ScreenChange"}


class Filtro(QObject):
    def eventFilter(self, obj, ev):
        nome = NOMES.get(ev.type())
        if nome and isinstance(obj, QWidget):
            LOG.evento("evento_janela", nome=nome, visivel=obj.isVisible())
        return False


class Janela(QWidget):
    def __init__(self):
        super().__init__(None, Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.resize(200, 200)

    def paintEvent(self, _):
        p = QPainter(self)
        p.fillRect(self.rect().adjusted(40, 40, -40, -40), QColor(230, 40, 60))
        p.end()


def main():
    app = QApplication(sys.argv[:1])
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    pulso = QTimer()
    pulso.start(200)
    pulso.timeout.connect(lambda: None)
    threading.Timer(A.tempo + 10, lambda: os._exit(3)).start()
    filtro = Filtro()
    app.installEventFilter(filtro)
    LOG.evento("inicio", ambiente=ambiente_basico(), plataforma=QGuiApplication.platformName(),
               telas=[t.name() for t in QGuiApplication.screens()])
    app.applicationStateChanged.connect(lambda s: LOG.evento("estado_app", estado=str(s)))
    app.screenAdded.connect(lambda t: LOG.evento("tela_adicionada", nome=t.name()))
    app.screenRemoved.connect(lambda t: LOG.evento("tela_removida", nome=t.name()))
    app.primaryScreenChanged.connect(lambda t: LOG.evento("tela_primaria", nome=t.name()))
    w = Janela()
    w.move(120, 120)
    w.show()
    ultimo = {"t": time.monotonic()}
    atrasos = []

    def batimento():
        agora = time.monotonic()
        delta = agora - ultimo["t"]
        ultimo["t"] = agora
        if delta > 2.5:
            atrasos.append(round(delta, 2))
            LOG.evento("ATRASO_NO_BATIMENTO", segundos=round(delta, 2), visivel=w.isVisible())

    bt = QTimer()
    bt.timeout.connect(batimento)
    bt.start(1000)
    QTimer.singleShot(int(A.tempo * 1000), app.quit)
    print("\nAções manuais sugeridas (anote a hora de cada uma): abrir app/vídeo em tela cheia; Meta+L (bloquear) e desbloquear;"
          " alternar janelas; (opcional) suspender e retomar. Ctrl+C encerra.\n")
    app.exec()
    obs = {
        "aparece_sobre_fullscreen": perguntar("A sonda apareceu SOBRE um app/vídeo em tela cheia?"),
        "aparece_sobre_tela_de_bloqueio": perguntar("A sonda apareceu sobre a TELA DE BLOQUEIO? (esperado: NÃO)"),
        "voltou_apos_desbloqueio": perguntar("A sonda voltou a aparecer normalmente após desbloquear?"),
        "roubou_foco": perguntar("A sonda roubou o foco do teclado de algum programa?"),
    }
    (LOG.caminho.parent / "resumo.json").write_text(json.dumps({"atrasos_batimento": atrasos, "observacao_do_operador": obs},
                                                              indent=2, ensure_ascii=False), encoding="utf-8")
    LOG.fechar()
    return 0


if __name__ == "__main__":
    sys.exit(main())
