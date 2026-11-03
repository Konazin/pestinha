"""
RENDERER - desenha o pet a partir de um QuadroPet, sem estado, sem sorteio e sem relógio.

QuadroPet é a fotografia imutável do que o pet mostra num instante (ver PetWindow.quadro): quem o monta resolve o
tremor, o balanço e a hora; quem desenha só pinta. Qualquer renderer precisa de `desenhar(painter, quadro)` e
`tamanho()`; o VetorialLegado é o desenho original do rosto, e um renderer de sprites poderá ocupar o mesmo lugar.
"""

from dataclasses import dataclass
from types import MappingProxyType
from typing import Optional

from PySide6.QtCore import QRect, QRectF, Qt
from PySide6.QtGui import QFont

from ..ajustes import LADO_JANELA_PET as WIN
from .desenho_rosto import Aparencia, draw_face, draw_zzz

CX, CY = WIN / 2, WIN / 2 - 6   # centro do corpo dentro da janela


@dataclass(frozen=True)
class QuadroPet:
    """O que desenhar agora: tudo já resolvido (ângulo com balanço, tremor, piscada, recorte e rótulo)."""
    shape: MappingProxyType          # forma dos olhos (só leitura)
    gaze: tuple                      # olhar (x, y)
    blink: float                     # 1.0 aberto, 0.08 piscando
    emocao: str
    carinho: bool                    # olhinhos fechados de felicidade
    aparencia: Aparencia
    angulo: float                    # graus, já somado ao balanço
    jitter: tuple                    # (x, y) de deslocamento do corpo (tremor e respiração)
    agora: float                     # relógio monotônico, para a animação dos Zzz
    corte_y: Optional[int]           # altura do recorte (sentado atrás do notebook); None = sem recorte
    rotulo: Optional[str]            # nome da emoção, quando o rótulo está ligado


class VetorialLegado:
    """O desenho vetorial original (moldura, tela, olhos, acessórios, Zzz e rótulo), com a mesma saída de antes."""

    def tamanho(self):
        """Lado da janela transparente que contém o corpo girado."""
        return WIN, WIN

    def desenhar(self, p, quadro):
        """Pinta o quadro no painter (já com antialiasing), na janela de tamanho `tamanho()`."""
        if quadro.corte_y is not None:
            p.setClipRect(QRect(0, 0, WIN, quadro.corte_y))
        jx, jy = quadro.jitter
        p.save()
        p.translate(CX + jx, CY + jy)
        p.rotate(quadro.angulo)
        draw_face(p, quadro.shape, quadro.gaze, quadro.blink, quadro.emocao, carinho=quadro.carinho,
                  aparencia=quadro.aparencia)
        p.restore()

        if quadro.emocao == "dormindo":
            draw_zzz(p, CX + jx, CY + jy, quadro.agora, quadro.aparencia.olho)

        if quadro.rotulo is not None:
            p.setPen(quadro.aparencia.olho)
            p.setFont(QFont("Consolas", 9, QFont.Bold))
            p.drawText(QRectF(0, WIN - 22, WIN, 20), Qt.AlignCenter, quadro.rotulo)
