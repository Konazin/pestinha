#!/usr/bin/env python3
"""Sonda de janela (investigações 1–5, 9): posicionamento, transparência e região de entrada.

Janela de teste ISOLADA (não usa código do Pestinha). Replica as flags de `overlay_flags()` de
`pestinha/body/pet.py` (Frameless | Tool | StaysOnTop | DoesNotAcceptFocus + fundo translúcido).
NÃO gera entrada sintética, NÃO move o cursor, NÃO captura tela, NÃO lê títulos de janelas.

Atenção: em Wayland o Qt devolve a posição que PEDIMOS, não a que o compositor aplicou. Por isso o
autorrelato nunca é prova de posicionamento: a prova é a observação do operador.

Modos (--modo): mover | regiao | nada

Regiões (--regiao, modo regiao). SEMÂNTICA — leia docs/m1/SEMANTICA-REGIAO-ENTRADA.md:
  nenhuma             sem máscara (entrada = superfície inteira, se nada mais mudar)
  mask-central        setMask(QRegion(quadrado))            máscara NÃO vazia (região de entrada "positiva")
  mask-minima         setMask(QRegion(1x1 no canto))        máscara não vazia e quase "nada": controle confiável
  mask-vazia-qt       setMask(QRegion())                    região Qt VAZIA. Resultado indeterminado: o Qt pode
                      tratá-la como "sem máscara". NÃO equivale a input region Wayland vazia.
  mask-removida       setMask(quadrado) e, na metade do tempo, clearMask()   controle "máscara removida"
  transparente-input  Qt.WindowTransparentForInput          candidata a "entrada vazia" (a confirmar)
  dinamica            setMask(quadrado em movimento) a ~60 Hz, mede o custo

Ciclo de vida e códigos de saída (0 NÃO significa PASS do teste):
  0 concluído · 1 erro (resumo.json com traceback) · 2 argumentos inválidos · 3 vigia forçou a saída
  (travamento) · 4 interrompido (Ctrl+C/SIGTERM; resumo.json parcial gravado).

Segurança: a janela fecha sozinha em --tempo segundos; o vigia (thread daemon) só dispara se o processo
travar e é cancelado no encerramento normal. Superfícies grandes (--grande) podem bloquear cliques até fechar.
"""
import argparse
import os
import signal
import statistics
import sys
import time
import traceback
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from _comum import (CODIGOS, Registro, Vigia, ambiente_basico, escrever_json_atomico,  # noqa: E402
                    libs_qt_carregadas, pasta_saida, perguntar)

REGIOES = ["nenhuma", "mask-central", "mask-minima", "mask-vazia-qt", "mask-removida", "transparente-input", "dinamica"]


def argumentos():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("--plataforma", choices=["auto", "xcb", "wayland"], default="auto")
    ap.add_argument("--modo", choices=["mover", "regiao", "nada"], default="mover")
    ap.add_argument("--api", choices=["move", "setGeometry", "janela"], default="move",
                    help="como pedir a posição (QWidget.move, QWidget.setGeometry, QWindow.setPosition)")
    ap.add_argument("--caminho", choices=["retangulo", "telas"], default="retangulo")
    ap.add_argument("--passos", type=int, default=12)
    ap.add_argument("--regiao", choices=REGIOES, default="nenhuma")
    ap.add_argument("--flags", choices=["pestinha", "normal"], default="pestinha",
                    help="'normal' = janela comum, para isolar o efeito das flags")
    ap.add_argument("--tinta", type=int, default=24, help="alfa (0–255) do véu que mostra a extensão da superfície")
    ap.add_argument("--tamanho", default="600x400")
    ap.add_argument("--grande", action="store_true", help="cobre a área disponível da tela --tela")
    ap.add_argument("--tela", type=int, default=0)
    ap.add_argument("--tempo", type=float, default=30.0)
    ap.add_argument("--saida")
    ap.add_argument("--autoteste-travar", action="store_true",
                    help="SOMENTE para validar o vigia: bloqueia o laço de eventos de propósito")
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
INICIO = time.monotonic()
RESUMO = {"argumentos": vars(A), "status": "em_andamento", "codigo_saida": None, "passos": [],
          "cliques_por_fase": {}, "observacao_do_operador": {}}


def gravar_resumo(status, observacao=None):
    """Grava resumo.json de forma atômica com status e código de saída coerentes."""
    RESUMO["status"] = status
    RESUMO["codigo_saida"] = CODIGOS[status]
    RESUMO["duracao_s"] = round(time.monotonic() - INICIO, 2)
    RESUMO["finalizado_em"] = time.strftime("%Y-%m-%dT%H:%M:%S")
    if observacao:
        RESUMO["observacao"] = observacao
    escrever_json_atomico(PASTA / "resumo.json", RESUMO)


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
        self.fase = "unica"
        self.cont = {}
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
                   f"{A.modo}/{A.regiao}\n{QGuiApplication.platformName()}\nfase {self.fase}\n"
                   f"dentro {self.cliques_dentro}\nfora {self.cliques_fora}")
        p.end()

    def mousePressEvent(self, e):
        pos = e.position().toPoint()
        dentro = self.alvo.contains(pos)
        if dentro:
            self.cliques_dentro += 1
        else:
            self.cliques_fora += 1
        c = self.cont.setdefault(self.fase, {"dentro": 0, "fora": 0})
        c["dentro" if dentro else "fora"] += 1
        RESUMO["cliques_por_fase"] = self.cont
        LOG.evento("clique_recebido", fase=self.fase, local=(pos.x(), pos.y()),
                   global_=(int(e.globalPosition().x()), int(e.globalPosition().y())),
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
        return pontos
    g = QGuiApplication.primaryScreen().availableGeometry()
    m = 80
    cantos = [QPoint(g.x() + m, g.y() + m), QPoint(g.right() - w.width() - m, g.y() + m),
              QPoint(g.right() - w.width() - m, g.bottom() - w.height() - m), QPoint(g.x() + m, g.bottom() - w.height() - m)]
    return [cantos[i % 4] for i in range(A.passos)]


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


def log_regiao(w, tipo, **extra):
    """Registra o que o lado Qt sabe. NÃO é a input region do compositor (o cliente não consegue lê-la)."""
    m = w.mask()
    LOG.evento("regiao_aplicada", variante=tipo, fase=w.fase, qt_mask_isEmpty=m.isEmpty(),
               qt_mask_box=m.boundingRect().getRect(), observavel="apenas o lado Qt", **extra)


def configurar_regiao(app, w, estado):
    r = A.regiao

    def aplicar():
        if r in ("nenhuma", "transparente-input", "dinamica"):
            LOG.evento("regiao_nao_aplicada", variante=r, motivo="este modo não chama setMask no início")
            return
        if r == "mask-central":
            w.fase = "com_mascara"
            w.setMask(QRegion(w.alvo))
        elif r == "mask-minima":
            w.fase = "com_mascara"
            w.setMask(QRegion(QRect(0, 0, 1, 1)))
        elif r == "mask-vazia-qt":
            w.fase = "mascara_vazia_qt"
            w.setMask(QRegion())
        elif r == "mask-removida":
            w.fase = "com_mascara"
            w.setMask(QRegion(w.alvo))
        log_regiao(w, r)
        w.update()

    QTimer.singleShot(400, aplicar)
    if r == "mask-removida":
        def remover():
            w.clearMask()
            w.fase = "sem_mascara"
            log_regiao(w, "mask-removida:clearMask")
            w.update()
        QTimer.singleShot(int(A.tempo * 500), remover)
    if r == "transparente-input":
        w.fase = "transparente_input"
    if r == "dinamica":
        w.fase = "dinamica"

        def mover_alvo():
            import math
            estado["i"] += 1
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


def configurar_movimento(w, estado, app):
    pontos = caminho_pontos(w)
    tm = QTimer()

    def registrar(i, alvo):
        lido = ler_posicao(w)
        erro = (lido["pos"][0] - alvo.x(), lido["pos"][1] - alvo.y())
        RESUMO["passos"].append({"i": i, "pedido": (alvo.x(), alvo.y()), **lido, "erro_autorrelato": erro})
        LOG.evento("passo", i=i, pedido=(alvo.x(), alvo.y()), lido=lido["pos"], erro_autorrelato=erro, tela=lido["tela"])

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

    tm.timeout.connect(passo)
    QTimer.singleShot(1200, lambda: tm.start(900))
    w._tm = tm


def perguntas(w):
    obs = {}
    if A.modo == "mover":
        obs["janela_mudou_visivelmente_de_lugar"] = perguntar("A janela mudou VISIVELMENTE de posição ao longo do caminho?")
        obs["posicoes_visuais_acompanharam_o_caminho"] = perguntar("As posições visuais acompanharam o caminho pedido (cantos/telas)?")
    if A.modo == "regiao":
        r = A.regiao
        if r == "mask-removida":
            obs["fora_passou_com_mascara"] = perguntar("1ª metade (COM máscara): cliques FORA do quadrado vermelho chegaram à janela de baixo?")
            obs["fora_passou_sem_mascara"] = perguntar("2ª metade (máscara REMOVIDA): cliques FORA do quadrado chegaram à janela de baixo?")
        else:
            obs["clique_fora_do_alvo_chegou_embaixo"] = perguntar("Cliques FORA do quadrado vermelho chegaram à janela/ícone de baixo?")
        if r in ("nenhuma", "mask-central", "dinamica"):
            obs["clique_no_alvo_nao_vazou"] = perguntar("Cliques DENTRO do quadrado vermelho NÃO chegaram embaixo (foram capturados)?")
    obs["fundo_transparente_sem_retangulo_opaco"] = perguntar("O fundo apareceu transparente (sem retângulo preto/branco)?")
    obs["foco_do_teclado_permaneceu_no_outro_programa"] = perguntar("O foco do teclado permaneceu no seu outro programa?")
    return obs


def leitura_descritiva(w):
    """Leitura DESCRITIVA do experimento de máscara vazia. Não é PASS/FAIL nem prova de input region."""
    if A.regiao != "mask-vazia-qt":
        return None
    fora = w.cliques_fora
    passou = RESUMO["observacao_do_operador"].get("clique_fora_do_alvo_chegou_embaixo")
    if fora > 0:
        return ("A sonda RECEBEU cliques com a máscara Qt vazia: consistente com o Qt tratar a região vazia como "
                "'sem máscara' (entrada na superfície inteira). Não prova o que foi enviado ao compositor.")
    if passou == "s":
        return ("Nenhum clique chegou à sonda e os cliques passaram: consistente com entrada efetivamente vazia. "
                "Confirmar com WAYLAND_DEBUG (set_input_region) antes de concluir.")
    return "Indeterminado (sem cliques registrados ou sem resposta do operador)."


def executar():
    """Corpo da sonda. Devolve o status final."""
    app = QApplication(sys.argv[:1])
    estado = {"sinal": None, "i": 0}

    def ao_sinal(num, _frame):
        estado["sinal"] = num
        app.quit()

    signal.signal(signal.SIGINT, ao_sinal)
    signal.signal(signal.SIGTERM, ao_sinal)
    respiro = QTimer()                      # deixa o Python tratar sinais enquanto o Qt roda
    respiro.start(200)
    respiro.timeout.connect(lambda: None)

    LOG.evento("inicio", argumentos=vars(A), ambiente=ambiente_basico(), plataforma=QGuiApplication.platformName(),
               telas=[{"nome": t.name(), "geo": t.geometry().getRect(), "dpr": t.devicePixelRatio()} for t in telas()])
    RESUMO["plataforma"] = QGuiApplication.platformName()
    RESUMO["ambiente"] = ambiente_basico()

    w = Sonda()
    if A.grande:
        t = telas()[min(A.tela, len(telas()) - 1)]
        w.setGeometry(t.availableGeometry())
    else:
        largura, altura = (int(x) for x in A.tamanho.lower().split("x"))
        g = QGuiApplication.primaryScreen().availableGeometry()
        w.resize(largura, altura)
        w.move(g.x() + 100, g.y() + 100)
    w.show()

    if A.modo == "regiao":
        configurar_regiao(app, w, estado)
    if A.modo == "mover":
        configurar_movimento(w, estado, app)
    if A.autoteste_travar:
        QTimer.singleShot(500, lambda: time.sleep(10 ** 6))
    QTimer.singleShot(int(A.tempo * 1000), app.quit)

    app.exec()
    VIGIA.cancelar()                        # encerramento do laço: o vigia não pode mais agir
    # a partir daqui Ctrl+C/SIGTERM interrompem as perguntas com KeyboardInterrupt
    signal.signal(signal.SIGINT, signal.default_int_handler)
    signal.signal(signal.SIGTERM, lambda *_: (_ for _ in ()).throw(KeyboardInterrupt()))

    LOG.evento("fim", cliques_dentro=w.cliques_dentro, cliques_fora=w.cliques_fora, moves=w.moves, sinal=estado["sinal"])
    RESUMO.update(bibliotecas=libs_qt_carregadas(), cliques_dentro=w.cliques_dentro, cliques_fora=w.cliques_fora,
                  mouse_moves_recebidos=w.moves)
    if w.tempos_mask:
        o = sorted(w.tempos_mask)
        RESUMO["setMask_ms"] = {"n": len(o), "media": round(statistics.mean(o), 3),
                                "p95": round(o[max(0, int(len(o) * 0.95) - 1)], 3), "max": round(o[-1], 3)}
    if estado["sinal"] is not None:
        return "interrompido"
    RESUMO["observacao_do_operador"] = perguntas(w)
    RESUMO["leitura_descritiva_mask_vazia"] = leitura_descritiva(w)
    return "concluido"


VIGIA = Vigia()


def main():
    VIGIA.armar(A.tempo + 8, ao_disparar=lambda: (
        LOG.evento("VIGIA_FORCOU_SAIDA", motivo="processo não encerrou em tempo + 8 s"),
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
