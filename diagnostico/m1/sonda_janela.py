#!/usr/bin/env python3
"""Sonda de janela (investigações 1–5, 9): posicionamento, transparência e região de entrada.

Janela de teste ISOLADA (não usa código do Pestinha). Replica as flags de `overlay_flags()` de
`pestinha/body/pet.py` (Frameless | Tool | StaysOnTop | DoesNotAcceptFocus + fundo translúcido).
NÃO gera entrada sintética, NÃO move o cursor, NÃO captura tela, NÃO lê títulos de janelas.

Atenção: em Wayland o Qt devolve a posição que PEDIMOS, não a que o compositor aplicou. Por isso o
autorrelato nunca é prova de posicionamento: a prova é a observação do operador (e, opcionalmente,
a corroboração externa descrita no runbook).

Modos (--modo):
  mover    anda por um caminho com move()/setGeometry()/janela.setPosition() e registra pedido × leitura
  regiao   testa transparência × região de entrada (veja --regiao)
  nada     só mostra a janela (flags/transparência) e registra eventos

Regiões (--regiao, modo regiao):
  nenhuma | mask-central | mask-vazia | transparente-input | dinamica

Segurança: a janela fecha sozinha em --tempo segundos (e um vigia força a saída). Use também
`timeout --signal=INT N python3 ...`. Superfícies grandes (--grande) podem bloquear cliques até fechar.
"""
import argparse
import json
import os
import signal
import statistics
import sys
import threading
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import Registro, ambiente_basico, libs_qt_carregadas, pasta_saida, perguntar  # noqa: E402


def argumentos():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plataforma", choices=["auto", "xcb", "wayland"], default="auto")
    ap.add_argument("--modo", choices=["mover", "regiao", "nada"], default="mover")
    ap.add_argument("--api", choices=["move", "setGeometry", "janela"], default="move",
                    help="como pedir a posição (QWidget.move, QWidget.setGeometry, QWindow.setPosition)")
    ap.add_argument("--caminho", choices=["retangulo", "telas"], default="retangulo")
    ap.add_argument("--passos", type=int, default=12)
    ap.add_argument("--regiao", choices=["nenhuma", "mask-central", "mask-vazia", "transparente-input", "dinamica"],
                    default="nenhuma")
    ap.add_argument("--flags", choices=["pestinha", "normal"], default="pestinha",
                    help="'normal' = janela comum, para isolar o efeito das flags")
    ap.add_argument("--tinta", type=int, default=24, help="alfa (0–255) do véu que mostra a extensão da superfície")
    ap.add_argument("--tamanho", default="600x400")
    ap.add_argument("--grande", action="store_true", help="cobre a área disponível da tela --tela")
    ap.add_argument("--tela", type=int, default=0)
    ap.add_argument("--tempo", type=float, default=30.0)
    ap.add_argument("--saida")
    return ap.parse_args()


A = argumentos()
if A.plataforma != "auto":
    os.environ["QT_QPA_PLATFORM"] = A.plataforma

from PySide6.QtCore import QPoint, QRect, Qt, QTimer  # noqa: E402
from PySide6.QtGui import QColor, QGuiApplication, QPainter, QRegion  # noqa: E402
from PySide6.QtWidgets import QApplication, QWidget  # noqa: E402

PASTA = pasta_saida(f"janela-{A.modo}-{A.regiao if A.modo == 'regiao' else A.api}-{A.plataforma}", A.saida)
LOG = Registro(PASTA / "eventos.jsonl")
LADO_PET = 160


class Sonda(QWidget):
    def __init__(self):
        flags = Qt.Window if A.flags == "normal" else (
            Qt.FramelessWindowHint | Qt.Tool | Qt.WindowStaysOnTopHint | Qt.WindowDoesNotAcceptFocus)
        if A.modo == "regiao" and A.regiao == "transparente-input":
            flags |= Qt.WindowTransparentForInput
        super().__init__(None, flags)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setAttribute(Qt.WA_ShowWithoutActivating)
        self.setMouseTracking(True)
        self.cliques_dentro = self.cliques_fora = self.moves = 0
        self.alvo = QRect(0, 0, LADO_PET, LADO_PET)
        self.tempos_mask = []

    def recentrar_alvo(self, cx=None, cy=None):
        cx = self.width() // 2 if cx is None else cx
        cy = self.height() // 2 if cy is None else cy
        self.alvo = QRect(int(cx - LADO_PET / 2), int(cy - LADO_PET / 2), LADO_PET, LADO_PET)

    def paintEvent(self, _):
        p = QPainter(self)
        p.setCompositionMode(QPainter.CompositionMode_Source)
        p.fillRect(self.rect(), QColor(255, 255, 255, 0))
        p.setCompositionMode(QPainter.CompositionMode_SourceOver)
        if A.tinta > 0:
            p.fillRect(self.rect(), QColor(40, 90, 255, A.tinta))
        p.setPen(QColor(40, 90, 255, 200))
        p.drawRect(self.rect().adjusted(0, 0, -1, -1))
        p.fillRect(self.alvo, QColor(230, 40, 60))
        p.setPen(Qt.white)
        p.drawText(self.alvo.adjusted(6, 6, -6, -6), Qt.TextWordWrap,
                   f"{A.modo}/{A.regiao}\n{QGuiApplication.platformName()}\ndentro {self.cliques_dentro}\nfora {self.cliques_fora}")
        p.end()

    def mousePressEvent(self, e):
        pos = e.position().toPoint()
        dentro = self.alvo.contains(pos)
        if dentro:
            self.cliques_dentro += 1
        else:
            self.cliques_fora += 1
        LOG.evento("clique_recebido", local=(pos.x(), pos.y()), global_=(int(e.globalPosition().x()), int(e.globalPosition().y())),
                   dentro_do_alvo=dentro, botao=int(e.button().value))
        self.update()

    def mouseMoveEvent(self, e):
        self.moves += 1
        if self.moves in (1, 50, 200):
            LOG.evento("mouse_move_recebido", n=self.moves)

    def enterEvent(self, e):
        LOG.evento("enter")

    def leaveEvent(self, e):
        LOG.evento("leave")

    def focusInEvent(self, e):
        LOG.evento("FOCO_GANHO")

    def focusOutEvent(self, e):
        LOG.evento("foco_perdido")

    def showEvent(self, e):
        LOG.evento("show", plataforma=QGuiApplication.platformName(), tamanho=(self.width(), self.height()))
        super().showEvent(e)

    def moveEvent(self, e):
        LOG.evento("moveEvent", pos=(e.pos().x(), e.pos().y()))

    def resizeEvent(self, e):
        LOG.evento("resizeEvent", tamanho=(e.size().width(), e.size().height()))
        self.recentrar_alvo()


def telas():
    return QGuiApplication.screens()


def caminho_pontos(w):
    pontos = []
    if A.caminho == "telas" and len(telas()) > 1:
        for t in telas():
            g = t.availableGeometry()
            pontos += [QPoint(g.x() + 60, g.y() + 60), QPoint(g.center().x() - w.width() // 2, g.center().y() - w.height() // 2),
                       QPoint(g.right() - w.width() - 60, g.bottom() - w.height() - 60)]
    else:
        g = QGuiApplication.primaryScreen().availableGeometry()
        m = 80
        cantos = [QPoint(g.x() + m, g.y() + m), QPoint(g.right() - w.width() - m, g.y() + m),
                  QPoint(g.right() - w.width() - m, g.bottom() - w.height() - m), QPoint(g.x() + m, g.bottom() - w.height() - m)]
        pontos = [cantos[i % 4] for i in range(A.passos)]
    return pontos[: max(A.passos, len(pontos))] if A.caminho == "telas" else pontos


def pedir_posicao(w, ponto):
    if A.api == "move":
        w.move(ponto)
    elif A.api == "setGeometry":
        w.setGeometry(QRect(ponto, w.size()))
    else:
        h = w.windowHandle()
        if h is not None:
            h.setPosition(ponto)


def ler_posicao(w):
    h = w.windowHandle()
    fg = w.frameGeometry()
    return {"pos": (w.pos().x(), w.pos().y()), "frame": (fg.x(), fg.y(), fg.width(), fg.height()),
            "janela_geometry": None if h is None else (h.geometry().x(), h.geometry().y()),
            "tela": None if h is None or h.screen() is None else h.screen().name()}


def main():
    app = QApplication(sys.argv[:1])
    signal.signal(signal.SIGINT, lambda *_: app.quit())
    sinal = QTimer()
    sinal.start(200)
    sinal.timeout.connect(lambda: None)
    threading.Timer(A.tempo + 8, lambda: os._exit(3)).start()

    LOG.evento("inicio", argumentos=vars(A), ambiente=ambiente_basico(), plataforma=QGuiApplication.platformName(),
               telas=[{"nome": t.name(), "geo": t.geometry().getRect(), "dpr": t.devicePixelRatio()} for t in telas()])
    w = Sonda()
    if A.grande:
        t = telas()[min(A.tela, len(telas()) - 1)]
        g = t.availableGeometry()
        w.setGeometry(g)
    else:
        largura, altura = (int(x) for x in A.tamanho.lower().split("x"))
        g = QGuiApplication.primaryScreen().availableGeometry()
        w.resize(largura, altura)
        w.move(g.x() + 100, g.y() + 100)
    w.show()

    estado = {"i": 0}
    passos = []

    if A.modo == "regiao":
        def aplicar():
            if A.regiao == "mask-central":
                w.setMask(QRegion(w.alvo))
            elif A.regiao == "mask-vazia":
                w.setMask(QRegion())
            LOG.evento("regiao_aplicada", tipo=A.regiao, mask_vazia=w.mask().isEmpty(), mask_box=w.mask().boundingRect().getRect())
        QTimer.singleShot(400, aplicar)
        if A.regiao == "dinamica":
            def mover_alvo():
                estado["i"] += 1
                import math
                cx = w.width() / 2 + math.cos(estado["i"] / 20) * (w.width() / 3)
                cy = w.height() / 2 + math.sin(estado["i"] / 25) * (w.height() / 3)
                w.recentrar_alvo(cx, cy)
                t0 = time.perf_counter()
                w.setMask(QRegion(w.alvo))
                w.tempos_mask.append((time.perf_counter() - t0) * 1000)
                w.update()
            din = QTimer()
            din.timeout.connect(mover_alvo)
            QTimer.singleShot(600, lambda: din.start(16))
            w._din = din

    if A.modo == "mover":
        pontos = caminho_pontos(w)

        def passo():
            i = estado["i"]
            if i >= len(pontos):
                tm.stop()
                QTimer.singleShot(800, app.quit)
                return
            alvo = pontos[i]
            pedir_posicao(w, alvo)
            QTimer.singleShot(250, lambda i=i, alvo=alvo: registrar(i, alvo))
            estado["i"] += 1

        def registrar(i, alvo):
            lido = ler_posicao(w)
            erro = (lido["pos"][0] - alvo.x(), lido["pos"][1] - alvo.y())
            passos.append({"i": i, "pedido": (alvo.x(), alvo.y()), **lido, "erro_autorrelato": erro})
            LOG.evento("passo", i=i, pedido=(alvo.x(), alvo.y()), lido=lido["pos"], erro_autorrelato=erro, tela=lido["tela"])

        tm = QTimer()
        tm.timeout.connect(passo)
        QTimer.singleShot(1200, lambda: tm.start(900))
        w._tm = tm

    QTimer.singleShot(int(A.tempo * 1000), app.quit)
    app.exec()
    LOG.evento("fim", cliques_dentro=w.cliques_dentro, cliques_fora=w.cliques_fora, moves=w.moves)

    resumo = {"argumentos": vars(A), "plataforma": QGuiApplication.platformName(), "bibliotecas": libs_qt_carregadas(),
              "cliques_dentro": w.cliques_dentro, "cliques_fora": w.cliques_fora, "mouse_moves_recebidos": w.moves, "passos": passos}
    if w.tempos_mask:
        ordenado = sorted(w.tempos_mask)
        resumo["setMask_ms"] = {"n": len(ordenado), "media": round(statistics.mean(ordenado), 3),
                                "p95": round(ordenado[int(len(ordenado) * 0.95) - 1], 3), "max": round(ordenado[-1], 3)}
    obs = {}
    if A.modo == "mover":
        obs["janela_mudou_visivelmente_de_lugar"] = perguntar("A janela mudou VISIVELMENTE de posição ao longo do caminho?")
        obs["posicao_final_correta_a_olho"] = perguntar("As posições visuais acompanharam o caminho pedido (cantos/telas)?")
    if A.modo == "regiao":
        obs["clique_fora_do_alvo_chegou_embaixo"] = perguntar("Cliques FORA do quadrado vermelho chegaram à janela/ícone de baixo?")
        obs["clique_no_alvo_nao_vazou"] = perguntar("Cliques DENTRO do quadrado vermelho NÃO chegaram embaixo (foram capturados)?")
    obs["fundo_transparente_sem_retangulo_opaco"] = perguntar("O fundo apareceu transparente (sem retângulo preto/branco)?")
    obs["foco_do_teclado_permaneceu_no_outro_programa"] = perguntar("O foco do teclado permaneceu no seu outro programa?")
    resumo["observacao_do_operador"] = obs
    (PASTA / "resumo.json").write_text(json.dumps(resumo, indent=2, ensure_ascii=False, default=str), encoding="utf-8")
    LOG.fechar()
    print(f"\nResumo em {PASTA / 'resumo.json'}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
