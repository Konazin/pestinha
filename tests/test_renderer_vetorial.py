"""
Etapa 1 do renderer (docs/ANIME-RENDERER-EXTENSAO.md): o desenho do pet saiu do PetWindow.paintEvent
para body/renderer.py (QuadroPet + VetorialLegado), sem mudar nenhum pixel.

A referência é uma CÓPIA LITERAL do paintEvent anterior (`paint_event_original`). Aleatoriedade e relógio são
substituídos por falsos determinísticos nos dois lados. Os testes rodam em `offscreen`: provam o desenho e o
recorte, NÃO a execução gráfica em XWayland/KDE (isso é do M1-X).
"""
import math
import random
import sys
import time
from dataclasses import FrozenInstanceError
from pathlib import Path
from types import MappingProxyType

import pytest

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT))

from PySide6.QtCore import QRect, QRectF, Qt  # noqa: E402
from PySide6.QtGui import QFont, QImage, QPainter  # noqa: E402
from PySide6.QtWidgets import QApplication  # noqa: E402

from pestinha import config  # noqa: E402
from pestinha.body import pet as pet_mod  # noqa: E402
from pestinha.body import pet_state as pet_state_mod  # noqa: E402
from pestinha.body.desenho_rosto import aparencia_de, draw_face, draw_zzz  # noqa: E402
from pestinha.body.pet import CX, CY, WIN, PetWindow  # noqa: E402
from pestinha.body.pet_state import PetState  # noqa: E402
from pestinha.body.renderer import QuadroPet, VetorialLegado  # noqa: E402
from pestinha.config import EMOTION_NAMES  # noqa: E402
from pestinha.core.emotion import EYE_SHAPES  # noqa: E402
from pestinha.paths import Paths  # noqa: E402

AGORA = 1234.5
PAINT_EVENT_NOVO = PetWindow.paintEvent                              # guardado antes de qualquer patch
PETS = sorted(p.stem for p in (ROOT / "pets").glob("*.json"))


class Falso:
    """Relógio e sorteio determinísticos: o mesmo roteiro de valores a cada instância."""
    def __init__(self):
        self.n = 0

    def monotonic(self):
        return AGORA

    def uniform(self, a, b):
        self.n += 1
        return a + (b - a) * ((self.n * 0.37) % 1.0)


def paint_event_original(self, _event):
    """Cópia literal de PetWindow.paintEvent antes da extração (usa `time`/`random` do módulo de teste)."""
    p = QPainter(self)
    p.setRenderHint(QPainter.Antialiasing)
    st = self.state
    if st.desk_top is not None:
        corte = int(st.desk_top - self.y())
        p.setClipRect(QRect(0, 0, self.width(), max(0, min(self.height(), corte))))
    shake = st.shake
    jitter_x = random.uniform(-shake, shake) if shake else 0.0
    jitter_y = random.uniform(-shake, shake) if shake else 0.0

    sway = 0.0
    if self.body.grounded and st.emotion != "dormindo":
        sway = st.tone.sway() * math.sin(time.monotonic() * 2.2)
    if st.emotion == "dormindo":
        jitter_y += 1.5 * math.sin(time.monotonic() * 1.6)

    p.save()
    p.translate(CX + jitter_x, CY + jitter_y)
    p.rotate(self.body.angle + sway)
    blink = 0.08 if time.monotonic() < st.blink_until else 1.0
    draw_face(p, st.shape, st.gaze, blink, st.emotion, carinho=st.feliz_fechado(), aparencia=self.aparencia)
    p.restore()

    if st.emotion == "dormindo":
        draw_zzz(p, CX + jitter_x, CY + jitter_y, time.monotonic(), self.aparencia.olho)

    if st.show_label:
        p.setPen(self.aparencia.olho)
        p.setFont(QFont("Consolas", 9, QFont.Bold))
        p.drawText(QRectF(0, WIN - 22, WIN, 20), Qt.AlignCenter, EMOTION_NAMES.get(st.emotion, st.emotion))
    p.end()


VARIANTES = {
    "base": {},
    "tremor": {"shake": 3.0},
    "piscando": {"blink": True},
    "carinho": {"carinho": True},
    "sentado": {"desk": 100},
    "rotulo": {"label": True},
    "girado": {"angle": 37.0, "grounded": True, "gaze": (4.0, -3.0)},
    "tombado": {"angle": -90.0, "gaze": (-6.0, 5.0), "shake": 1.5},
}


def montar(pet, emocao, variante):
    QApplication.instance() or QApplication([])
    dados = config.load_pet(Paths(root=ROOT), pet)
    st = PetState()
    st.emotion = emocao
    st.shape = dict(EYE_SHAPES[emocao])
    v = VARIANTES[variante]
    st.shake = v.get("shake", 0.0)
    st.blink_until = AGORA + 1 if v.get("blink") else 0.0
    st.feliz_ate = AGORA + 1 if v.get("carinho") else 0.0
    st.show_label = v.get("label", False)
    st.gaze = v.get("gaze", (0.0, 0.0))
    janela = PetWindow(300, 300, st)
    janela.aparencia = aparencia_de(dados.get("aparencia"))
    janela.body.angle = v.get("angle", 0.0)
    janela.body.grounded = v.get("grounded", False)
    if "desk" in v:
        st.desk_top = janela.y() + v["desk"]
    return janela


def renderizar(janela, monkeypatch, metodo):
    falso = Falso()
    for mod in (pet_mod, pet_state_mod):
        monkeypatch.setattr(mod, "time", falso)
    monkeypatch.setattr(pet_mod, "random", falso)
    monkeypatch.setattr(sys.modules[__name__], "time", falso)
    monkeypatch.setattr(sys.modules[__name__], "random", falso)
    monkeypatch.setattr(PetWindow, "paintEvent", metodo)
    img = QImage(WIN, WIN, QImage.Format_ARGB32_Premultiplied)
    img.fill(0)
    janela.render(img)
    return img


@pytest.mark.parametrize("variante", VARIANTES)
@pytest.mark.parametrize("emocao", sorted(EYE_SHAPES))
@pytest.mark.parametrize("pet", PETS)
def test_pixels_identicos_ao_paint_event_original(pet, emocao, variante, monkeypatch):
    antes = renderizar(montar(pet, emocao, variante), monkeypatch, paint_event_original)
    depois = renderizar(montar(pet, emocao, variante), monkeypatch, PAINT_EVENT_NOVO)
    assert antes.size() == depois.size() == QImage(WIN, WIN, QImage.Format_ARGB32).size()
    assert antes.constBits().tobytes() == depois.constBits().tobytes()
    assert antes.pixelColor(0, 0).alpha() == 0                    # canto continua transparente
    assert any(antes.pixelColor(x, y).alpha() for x in range(0, WIN, 4) for y in range(0, WIN, 4))


def test_quadro_e_imutavel():
    q = QuadroPet(shape=MappingProxyType({"dy": 0.0}), gaze=(0.0, 0.0), blink=1.0, emocao="feliz", carinho=False,
                  aparencia=aparencia_de(None), angulo=0.0, jitter=(0.0, 0.0), agora=0.0, corte_y=None, rotulo=None)
    with pytest.raises(FrozenInstanceError):
        q.angulo = 5.0
    with pytest.raises(TypeError):
        q.shape["dy"] = 1.0


def test_renderer_nao_consome_sorteio_nem_relogio(monkeypatch):
    """Todo o acaso e o tempo entram pelo QuadroPet: o mesmo quadro desenha sempre os mesmos pixels."""
    QApplication.instance() or QApplication([])
    janela = montar(PETS[0], "dormindo", "tremor")
    janela.state.shake = 0.0
    quadro = janela.quadro(AGORA)
    imgs = []
    for _ in range(2):
        img = QImage(WIN, WIN, QImage.Format_ARGB32_Premultiplied)
        img.fill(0)
        p = QPainter(img)
        VetorialLegado().desenhar(p, quadro)
        p.end()
        imgs.append(img.constBits().tobytes())
    assert imgs[0] == imgs[1]


def test_tamanho_do_renderer_e_o_da_janela():
    assert VetorialLegado().tamanho() == (WIN, WIN)
