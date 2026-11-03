#!/usr/bin/env python3
"""Sonda de ciclo de sessão (investigação 10): foco, fullscreen, bloqueio de tela, suspensão, telas.

Mostra uma janelinha de teste (flags do overlay do Pestinha) e REGISTRA, sem agir:
mudanças de estado do aplicativo, exposição/ocultação da janela, hotplug de telas e um batimento (1 s)
cujos atrasos (>2,5 s) denunciam congelamento (bloqueio/suspensão). Você executa as ações manuais.
Não gera entrada, não captura tela, não lê títulos de janelas.

Códigos de saída (0 NÃO significa PASS do teste):
  0 concluído · 1 erro · 2 argumentos inválidos · 3 vigia forçou a saída · 4 interrompido (Ctrl+C/SIGTERM).
O vigia é uma thread daemon cancelada no encerramento normal; só age se o processo travar.

Uso: python3 sonda_ciclo.py [--plataforma xcb|wayland|auto] [--tempo 240] [--saida PASTA]
"""
import argparse
import os
import signal
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import (CODIGOS, Registro, Vigia, ambiente_basico, escrever_json_atomico,  # noqa: E402
                    pasta_saida, perguntar)

ap = argparse.ArgumentParser()
ap.add_argument("--plataforma", choices=["auto", "xcb", "wayland"], default="auto")
ap.add_argument("--tempo", type=float, default=240.0)
ap.add_argument("--saida")
ap.add_argument("--autoteste-travar", action="store_true",
                help="SOMENTE para validar o vigia: bloqueia o laço de eventos de propósito")
A = ap.parse_args()
if A.plataforma != "auto":
    os.environ["QT_QPA_PLATFORM"] = A.plataforma

from PySide6.QtCore import QEvent, QObject, Qt, QTimer  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

PASTA = pasta_saida(f"ciclo-{A.plataforma}", A.saida)
LOG = Registro(PASTA / "eventos.jsonl")
INICIO = time.monotonic()
RESUMO = {"argumentos": vars(A), "status": "em_andamento", "codigo_saida": None,
          "atrasos_batimento": [], "observacao_do_operador": {}}
NOMES = {QEvent.Show: "Show", QEvent.Hide: "Hide", QEvent.Expose: "Expose", QEvent.WindowStateChange: "WindowStateChange",
         QEvent.WindowActivate: "WindowActivate", QEvent.WindowDeactivate: "WindowDeactivate", QEvent.ScreenChangeInternal: "ScreenChange"}
VIGIA = Vigia()


def gravar_resumo(status, observacao=None):
    RESUMO["status"] = status
    RESUMO["codigo_saida"] = CODIGOS[status]
    RESUMO["duracao_s"] = round(time.monotonic() - INICIO, 2)
    RESUMO["finalizado_em"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if observacao:
        RESUMO["observacao"] = observacao
    escrever_json_atomico(PASTA / "resumo.json", RESUMO)


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


def executar():
    app = QApplication(sys.argv[:1])
    estado = {"sinal": None}

    def ao_sinal(num, _frame):
        estado["sinal"] = num
        app.quit()

    signal.signal(signal.SIGINT, ao_sinal)
    signal.signal(signal.SIGTERM, ao_sinal)
    respiro = QTimer()
    respiro.start(200)
    respiro.timeout.connect(lambda: None)
    filtro = Filtro()
    app.installEventFilter(filtro)
    LOG.evento("inicio", ambiente=ambiente_basico(), plataforma=QGuiApplication.platformName(),
               telas=[t.name() for t in QGuiApplication.screens()])
    RESUMO["plataforma"] = QGuiApplication.platformName()
    app.applicationStateChanged.connect(lambda s: LOG.evento("estado_app", estado=str(s)))
    app.screenAdded.connect(lambda t: LOG.evento("tela_adicionada", nome=t.name()))
    app.screenRemoved.connect(lambda t: LOG.evento("tela_removida", nome=t.name()))
    app.primaryScreenChanged.connect(lambda t: LOG.evento("tela_primaria", nome=t.name()))
    w = Janela()
    w.move(120, 120)
    w.show()
    ultimo = {"t": time.monotonic()}

    def batimento():
        agora = time.monotonic()
        delta = agora - ultimo["t"]
        ultimo["t"] = agora
        if delta > 2.5:
            RESUMO["atrasos_batimento"].append(round(delta, 2))
            LOG.evento("ATRASO_NO_BATIMENTO", segundos=round(delta, 2), visivel=w.isVisible())

    bt = QTimer()
    bt.timeout.connect(batimento)
    bt.start(1000)
    if A.autoteste_travar:
        QTimer.singleShot(500, lambda: time.sleep(10 ** 6))
    QTimer.singleShot(int(A.tempo * 1000), app.quit)
    print("\nAções manuais sugeridas (anote a hora de cada uma): abrir app/vídeo em tela cheia; Meta+L (bloquear) e desbloquear;"
          " alternar janelas; (opcional) suspender e retomar. Ctrl+C encerra.\n")
    app.exec()
    VIGIA.cancelar()
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))
    LOG.evento("fim", sinal=estado["sinal"], atrasos=len(RESUMO["atrasos_batimento"]))
    if estado["sinal"] is not None:
        return "interrompido"
    RESUMO["observacao_do_operador"] = {
        "aparece_sobre_fullscreen": perguntar("A sonda apareceu SOBRE um app/vídeo em tela cheia?"),
        "aparece_sobre_tela_de_bloqueio": perguntar("A sonda apareceu sobre a TELA DE BLOQUEIO? (esperado: NÃO)"),
        "voltou_apos_desbloqueio": perguntar("A sonda voltou a aparecer normalmente após desbloquear?"),
        "roubou_foco": perguntar("A sonda roubou o foco do teclado de algum programa?"),
    }
    return "concluido"


def main():
    VIGIA.armar(A.tempo + 10, ao_disparar=lambda: (
        LOG.evento("VIGIA_FORCOU_SAIDA", motivo="processo não encerrou em tempo + 10 s"),
        gravar_resumo("vigia_forcou_saida", "laço de eventos travado ou encerramento pendente")))
    status = "erro"
    try:
        status = executar()
        gravar_resumo(status)
    except KeyboardInterrupt:
        status = "interrompido"
        gravar_resumo(status, "interrompido durante as perguntas")
    except Exception:
        status = "erro"
        LOG.evento("ERRO", traceback=traceback.format_exc())
        gravar_resumo(status, traceback.format_exc())
        print(traceback.format_exc(), file=sys.stderr)
    finally:
        VIGIA.cancelar()
        LOG.evento("saida", status=status, codigo=CODIGOS[status])
        LOG.fechar()
    print(f"\nResumo em {PASTA / 'resumo.json'} (status={status}, código de saída={CODIGOS[status]}; 0 NÃO é PASS)")
    return CODIGOS[status]


if __name__ == "__main__":
    sys.exit(main())
