"""Ventana de RHEED en PySide6. El cálculo está en fisica.py y las figuras en figuras.py."""

from __future__ import annotations

import base64
import sys
import tempfile
from pathlib import Path

import numpy as np
import plotly
import plotly.graph_objects as go
from plotly.offline import get_plotlyjs
from PySide6.QtCore import Qt, QTimer, QUrl
from PySide6.QtGui import QColor
from PySide6.QtWebEngineWidgets import QWebEngineView
from PySide6.QtWidgets import (
    QApplication,
    QButtonGroup,
    QCheckBox,
    QDoubleSpinBox,
    QFrame,
    QHBoxLayout,
    QLabel,
    QMainWindow,
    QPushButton,
    QRadioButton,
    QScrollArea,
    QSizePolicy,
    QSlider,
    QSpinBox,
    QSplitter,
    QStackedWidget,
    QTabWidget,
    QToolButton,
    QVBoxLayout,
    QWidget,
)

try:
    from . import figuras as rr
except ImportError:
    import figuras as rr


QApplication.setAttribute(Qt.ApplicationAttribute.AA_ShareOpenGLContexts)

_SHELL = Path(tempfile.gettempdir()) / "rheed-plotly-shell.html"


def _shell_plotly() -> Path:
    """Página local con plotly.js. Cargarla por archivo evita el límite de setHtml."""
    marca = f"<!-- plotly {plotly.__version__} -->"
    if _SHELL.exists():
        with _SHELL.open(encoding="utf-8") as archivo:
            if marca in archivo.read(240):
                return _SHELL
    pagina = f"""<!DOCTYPE html>
<html>
<head>
<meta charset="utf-8">
{marca}
<style>
  html, body {{ margin: 0; height: 100%; background: #0f1419; overflow: hidden; }}
  #gd {{ width: 100%; height: 100%; }}
</style>
<script>{get_plotlyjs()}</script>
</head>
<body><div id="gd"></div></body>
</html>
"""
    _SHELL.write_text(pagina, encoding="utf-8")
    return _SHELL


class LienzoPlotly(QWebEngineView):
    """Muestra una figura de Plotly y la reemplaza sin recargar la página."""

    def __init__(self, camara_3d: bool = False) -> None:
        super().__init__()
        self._camara_3d = camara_3d
        self._listo = False
        self._pendiente: str | None = None
        self.page().setBackgroundColor(QColor("#0f1419"))
        self.loadFinished.connect(self._al_cargar)
        self.load(QUrl.fromLocalFile(str(_shell_plotly())))

    def _al_cargar(self, ok: bool) -> None:
        self._listo = bool(ok)
        if self._listo and self._pendiente is not None:
            self._empujar(self._pendiente)
            self._pendiente = None

    def mostrar(self, figura: go.Figure) -> None:
        carga = figura.to_json()
        if not self._listo:
            self._pendiente = carga
            return
        self._empujar(carga)

    def _empujar(self, carga: str) -> None:
        codificado = base64.b64encode(carga.encode("utf-8")).decode("ascii")
        extra = "modeBarButtonsToAdd: ['resetCameraDefault3d']," if self._camara_3d else ""
        self.page().runJavaScript(
            f"""
            (function () {{
                const fig = JSON.parse(new TextDecoder().decode(
                    Uint8Array.from(atob("{codificado}"), c => c.charCodeAt(0))
                ));
                const config = {{
                    responsive: true,
                    displaylogo: false,
                    scrollZoom: true,
                    {extra}
                }};
                const gd = document.getElementById("gd");
                if (gd && gd.data) {{
                    Plotly.react(gd, fig.data, fig.layout, config);
                }} else {{
                    Plotly.newPlot(gd, fig.data, fig.layout, config);
                }}
            }})();
            """
        )


class Seccion(QWidget):
    """Bloque con título que se abre y se cierra."""

    def __init__(self, titulo: str, abierto: bool = False) -> None:
        super().__init__()
        columna = QVBoxLayout(self)
        columna.setContentsMargins(0, 0, 0, 8)
        columna.setSpacing(0)

        self._boton = QToolButton()
        self._boton.setObjectName("seccion")
        self._boton.setText(titulo)
        self._boton.setCheckable(True)
        self._boton.setChecked(abierto)
        self._boton.setToolButtonStyle(Qt.ToolButtonStyle.ToolButtonTextBesideIcon)
        self._boton.setArrowType(Qt.ArrowType.DownArrow if abierto else Qt.ArrowType.RightArrow)
        self._boton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
        self._boton.toggled.connect(self._alternar)

        self.cuerpo = QWidget()
        self.caja = QVBoxLayout(self.cuerpo)
        self.caja.setContentsMargins(2, 6, 2, 8)
        self.caja.setSpacing(8)
        self.cuerpo.setVisible(abierto)

        columna.addWidget(self._boton)
        columna.addWidget(self.cuerpo)

    def _alternar(self, abierto: bool) -> None:
        self.cuerpo.setVisible(abierto)
        self._boton.setArrowType(
            Qt.ArrowType.DownArrow if abierto else Qt.ArrowType.RightArrow
        )


def _doble(valor: float, paso: float, minimo: float, maximo: float, decimales: int = 2) -> QDoubleSpinBox:
    caja = QDoubleSpinBox()
    caja.setRange(minimo, maximo)
    caja.setDecimals(decimales)
    caja.setSingleStep(paso)
    caja.setValue(valor)
    caja.setKeyboardTracking(False)
    return caja


def _entero(valor: int, paso: int, minimo: int, maximo: int) -> QSpinBox:
    caja = QSpinBox()
    caja.setRange(minimo, maximo)
    caja.setSingleStep(paso)
    caja.setValue(valor)
    caja.setKeyboardTracking(False)
    return caja


def _etiqueta(texto: str) -> QLabel:
    rotulo = QLabel(texto)
    rotulo.setObjectName("campo")
    return rotulo


def texto_vectores(simetria: str, a: float, b: float) -> str:
    """Fórmulas de la red, en HTML que Qt sabe pintar."""

    def titulo(texto: str) -> str:
        return f"<p style='margin:10px 0 4px;color:#2a9d8f;font-weight:700'>{texto}</p>"

    def fila(texto: str) -> str:
        return f"<p style='margin:4px 0'>{texto}</p>"

    if simetria == "RECT":
        con_a = 2 * np.pi / a
        con_b = 2 * np.pi / b
        return (
            titulo("Espacio real")
            + fila(f"Red rectangular (a = {a:.3f} Å, b = {b:.3f} Å)")
            + fila(f"a₁ = a [1, 0, 0] = [{a:.3f}, 0, 0] Å")
            + fila(f"a₂ = b [0, 1, 0] = [0, {b:.3f}, 0] Å")
            + fila("γ = 90°")
            + titulo("Espacio recíproco")
            + fila(f"b₁ = (2π/a) [1, 0, 0] = [{con_a:.3f}, 0, 0] Å⁻¹")
            + fila(f"b₂ = (2π/b) [0, 1, 0] = [0, {con_b:.3f}, 0] Å⁻¹")
            + fila("γ* = 90°")
        )
    if simetria == "HEX":
        con_a = 2 * np.pi / a
        bmod = 2 * con_a / np.sqrt(3)
        return (
            titulo("Espacio real")
            + fila(f"Red hexagonal, tres vectores de superficie (a = {a:.3f} Å)")
            + fila(f"a₁ = a [1, 0, 0] = [{a:.3f}, 0, 0] Å")
            + fila(
                f"a₂ = a [−1/2, √3/2, 0] = [{-0.5 * a:.3f}, {a * np.sqrt(3) / 2:.3f}, 0] Å"
            )
            + fila(
                f"a₃ = a [−1/2, −√3/2, 0] = [{-0.5 * a:.3f}, {-a * np.sqrt(3) / 2:.3f}, 0] Å"
            )
            + fila("a₁ + a₂ + a₃ = 0, γ = 120°")
            + titulo("Espacio recíproco")
            + fila(
                f"b₁ = (2π/a) [1, 1/√3, 0] = [{con_a:.3f}, {con_a / np.sqrt(3):.3f}, 0] Å⁻¹"
            )
            + fila(
                f"b₂ = (2π/a) [−1, 1/√3, 0] = [{-con_a:.3f}, {con_a / np.sqrt(3):.3f}, 0] Å⁻¹"
            )
            + fila(f"b₃ = (2π/a) [0, −2/√3, 0] = [0, {-bmod:.3f}, 0] Å⁻¹")
            + fila(f"b₁ + b₂ + b₃ = 0, |b| = {bmod:.3f} Å⁻¹, 120°")
        )
    if simetria == "CENT":
        con_a = 2 * np.pi / a
        medio = a / 2
        return (
            titulo("Espacio real")
            + fila(f"Red cuadrada centrada (a = {a:.3f} Å)")
            + fila(f"a₁ = (a/2)(ŷ − ẑ) = [0, {medio:.3f}, {-medio:.3f}] Å")
            + fila(f"a₂ = (a/2)(ŷ + ẑ) = [0, {medio:.3f}, {medio:.3f}] Å")
            + fila("γ = 90°. El plano recíproco es yz y la normal es x̂.")
            + titulo("Espacio recíproco")
            + fila(f"b₁ = (2π/a)(ŷ − ẑ) = [0, {con_a:.3f}, {-con_a:.3f}] Å⁻¹")
            + fila(f"b₂ = (2π/a)(ŷ + ẑ) = [0, {con_a:.3f}, {con_a:.3f}] Å⁻¹")
            + fila("γ* = 90°")
        )
    return "<p>Selecciona una estructura.</p>"


def _figura_error(mensaje: str) -> go.Figure:
    figura = go.Figure()
    figura.update_layout(
        template="plotly_dark",
        paper_bgcolor="#0f1419",
        plot_bgcolor="#0f1419",
        font=dict(color="#e8eaed"),
        margin=dict(l=20, r=20, t=40, b=20),
        annotations=[dict(
            text=mensaje, x=0.5, y=0.5, xref="paper", yref="paper",
            showarrow=False, font=dict(color="#e8eaed", size=14),
        )],
    )
    return figura


ESTILO = """
QWidget { background: #0f1419; color: #e8eaed; font-size: 13px; }
QMainWindow { background: #0f1419; }
QFrame#panel {
    background: #1a1f26;
    border: 1px solid #2d3640;
    border-radius: 10px;
}
QScrollArea, QScrollArea > QWidget > QWidget { background: transparent; border: none; }
QLabel#titulo { font-size: 22px; font-weight: 700; background: transparent; }
QLabel#campo { color: #9aa0a6; background: transparent; }
QLabel#angulo { color: #2a9d8f; font-weight: 700; font-size: 16px; background: transparent; }
QLabel#info {
    background: #222831;
    border: 1px solid #2d3640;
    border-radius: 8px;
    padding: 8px;
}
QToolButton#seccion {
    background: transparent;
    color: #e8eaed;
    font-weight: 700;
    font-size: 15px;
    border: none;
    border-bottom: 1px solid #2d3640;
    padding: 8px 2px;
    text-align: left;
}
QDoubleSpinBox, QSpinBox {
    background: #ffffff;
    color: #111827;
    border: 1px solid #cbd5e1;
    border-radius: 6px;
    padding: 6px 8px;
    min-height: 22px;
}
QDoubleSpinBox:disabled, QSpinBox:disabled {
    background: #e5e7eb;
    color: #6b7280;
}
QRadioButton, QCheckBox {
    background: #ffffff;
    color: #111827;
    spacing: 10px;
    padding: 8px 10px;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
}
QRadioButton::indicator, QCheckBox::indicator {
    width: 18px;
    height: 18px;
    border: 2px solid #64748b;
    background: #ffffff;
}
QRadioButton::indicator {
    border-radius: 10px;
}
QCheckBox::indicator {
    border-radius: 4px;
}
QRadioButton::indicator:checked {
    background: #2a9d8f;
    border-color: #2a9d8f;
}
QCheckBox::indicator:checked {
    background: #2a9d8f;
    border-color: #2a9d8f;
}
QPushButton, QPushButton#segmento {
    background: #ffffff;
    color: #111827;
    border: 1px solid #cbd5e1;
    border-radius: 8px;
    padding: 8px 10px;
}
QPushButton:hover, QPushButton#segmento:hover {
    background: #f8fafc;
}
QPushButton#segmento:checked {
    background: #e6f4f1;
    color: #0f766e;
    border: 1px solid #2a9d8f;
    border-top: 2px solid #2a9d8f;
}
QTabWidget::pane { border: 1px solid #2d3640; background: #1a1f26; border-radius: 8px; }
QTabBar::tab {
    background: #222831;
    color: #9aa0a6;
    padding: 8px 18px;
    border: 1px solid #2d3640;
    margin-right: 2px;
}
QTabBar::tab:selected { background: #1a1f26; color: #2a9d8f; border-top: 2px solid #2a9d8f; }
QSlider::groove:horizontal { height: 4px; background: #2d3640; border-radius: 2px; }
QSlider::sub-page:horizontal { background: #2a9d8f; border-radius: 2px; }
QSlider::handle:horizontal {
    width: 16px; height: 16px; margin: -6px 0;
    background: #e8eaed; border: 2px solid #2a9d8f; border-radius: 8px;
}
QSplitter::handle { background: #0f1419; }
"""


class Ventana(QMainWindow):
    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("RHEED · Red recíproca")
        self.resize(1360, 860)
        self.setStyleSheet(ESTILO)

        self._temporizador = QTimer(self)
        self._temporizador.setSingleShot(True)
        self._temporizador.setInterval(70)
        self._temporizador.timeout.connect(self._dibujar)

        raiz = QWidget()
        self.setCentralWidget(raiz)
        marco = QHBoxLayout(raiz)
        marco.setContentsMargins(16, 16, 16, 16)
        marco.setSpacing(12)

        divisor = QSplitter(Qt.Orientation.Horizontal)
        divisor.setChildrenCollapsible(False)
        marco.addWidget(divisor)
        divisor.addWidget(self._panel_controles())
        divisor.addWidget(self._panel_vistas())
        divisor.setStretchFactor(0, 1)
        divisor.setStretchFactor(1, 2)
        divisor.setSizes([400, 920])

        self._aplicar_simetria("CENT")
        self._dibujar()

    def _panel_controles(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        panel.setMinimumWidth(320)
        panel.setMaximumWidth(460)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        contenido = QWidget()
        columna = QVBoxLayout(contenido)
        columna.setContentsMargins(16, 16, 16, 16)
        columna.setSpacing(2)

        titulo = QLabel("RHEED · Red recíproca")
        titulo.setObjectName("titulo")
        columna.addWidget(titulo)

        columna.addWidget(self._seccion_cristal())
        columna.addWidget(self._seccion_haz())
        columna.addWidget(self._seccion_pantalla())
        columna.addWidget(self._seccion_reconstruccion())
        columna.addWidget(self._seccion_configuracion())
        columna.addWidget(self._seccion_datos())
        columna.addStretch(1)

        scroll.setWidget(contenido)
        capa = QVBoxLayout(panel)
        capa.setContentsMargins(0, 0, 0, 0)
        capa.addWidget(scroll)
        return panel

    def _seccion_cristal(self) -> Seccion:
        seccion = Seccion("Cristal")
        seccion.caja.addWidget(_etiqueta("Estructura cristalina"))

        self._radios: dict[str, QRadioButton] = {}
        grupo = QButtonGroup(self)
        for clave, texto in (
            ("HEX", "Hexagonal"),
            ("RECT", "Rectangular / cuadrada"),
            ("CENT", "Centrada en caras"),
        ):
            boton = QRadioButton(texto)
            boton.setChecked(clave == "CENT")
            grupo.addButton(boton)
            self._radios[clave] = boton
            boton.toggled.connect(lambda activo, c=clave: self._al_cambiar_simetria(c, activo))
            seccion.caja.addWidget(boton)

        self.lbl_a = _etiqueta("Parámetro base a (Å)")
        self.a = _doble(3.0, 0.01, 0.01, 500.0, 3)
        self.lbl_b = _etiqueta("Parámetro b (no requerido en FCS)")
        self.b = _doble(3.0, 0.01, 0.01, 500.0, 3)
        self.b.setEnabled(False)
        for widget in (self.lbl_a, self.a, self.lbl_b, self.b):
            seccion.caja.addWidget(widget)
        self.a.valueChanged.connect(self._al_cambiar_red)
        self.b.valueChanged.connect(self._al_cambiar_red)
        return seccion

    def _seccion_haz(self) -> Seccion:
        seccion = Seccion("E-beam")
        seccion.caja.addWidget(_etiqueta("Energía del haz de electrones (keV)"))
        self.kev = _doble(0.1, 0.1, 0.0, 100.0, 3)
        seccion.caja.addWidget(self.kev)
        seccion.caja.addWidget(_etiqueta("Ángulo rasante θ (°)"))
        self.theta = _doble(2.0, 0.1, -10.0, 45.0, 2)
        seccion.caja.addWidget(self.theta)
        self.esfera = QCheckBox("Graficar esfera de Ewald")
        self.esfera.setChecked(False)
        self.esfera.toggled.connect(self._pedir_dibujo)
        seccion.caja.addWidget(self.esfera)

        fila = QHBoxLayout()
        fila.setSpacing(0)
        self.btn_azimut = QPushButton("Ángulo azimutal")
        self.btn_miller = QPushButton("Notación de Miller")
        for boton in (self.btn_azimut, self.btn_miller):
            boton.setObjectName("segmento")
            boton.setCheckable(True)
            boton.setSizePolicy(QSizePolicy.Policy.Expanding, QSizePolicy.Policy.Fixed)
            fila.addWidget(boton)
        self.btn_azimut.setChecked(True)
        grupo = QButtonGroup(self)
        grupo.setExclusive(True)
        grupo.addButton(self.btn_azimut)
        grupo.addButton(self.btn_miller)
        seccion.caja.addLayout(fila)

        self.pila_haz = QStackedWidget()
        azimut = QWidget()
        caja_az = QVBoxLayout(azimut)
        caja_az.setContentsMargins(0, 8, 0, 0)
        caja_az.addWidget(_etiqueta("Azimut φ respecto a a₁ (°)"))
        self.phi = _entero(0, 1, -180, 180)
        caja_az.addWidget(self.phi)

        miller = QWidget()
        caja_mi = QVBoxLayout(miller)
        caja_mi.setContentsMargins(0, 8, 0, 0)
        caja_mi.addWidget(_etiqueta("Dirección [u v] = u a₁ + v a₂"))
        pareja = QHBoxLayout()
        self.miller_u = _entero(1, 1, -50, 50)
        self.miller_v = _entero(0, 1, -50, 50)
        pareja.addWidget(self.miller_u)
        pareja.addWidget(self.miller_v)
        caja_mi.addLayout(pareja)

        self.pila_haz.addWidget(azimut)
        self.pila_haz.addWidget(miller)
        seccion.caja.addWidget(self.pila_haz)

        self.btn_miller.toggled.connect(self._al_cambiar_modo)
        self.phi.valueChanged.connect(self._al_editar_phi)
        self.kev.valueChanged.connect(self._pedir_dibujo)
        self.theta.valueChanged.connect(self._pedir_dibujo)
        self.miller_u.valueChanged.connect(self._pedir_dibujo)
        self.miller_v.valueChanged.connect(self._pedir_dibujo)
        return seccion

    def _seccion_pantalla(self) -> Seccion:
        seccion = Seccion("Pantalla de fósforo")
        seccion.caja.addWidget(_etiqueta("Distancia muestra–pantalla (cm)"))
        self.distancia = _doble(15.0, 0.1, 0.0, 500.0, 2)
        seccion.caja.addWidget(self.distancia)
        seccion.caja.addWidget(_etiqueta("Radio de la pantalla (cm)"))
        self.radio = _doble(10.0, 0.1, 0.0, 500.0, 2)
        seccion.caja.addWidget(self.radio)
        self.distancia.valueChanged.connect(self._pedir_dibujo)
        self.radio.valueChanged.connect(self._pedir_dibujo)
        return seccion

    def _seccion_reconstruccion(self) -> Seccion:
        seccion = Seccion("Reconstrucción")
        self.recon = QCheckBox("Agregar reconstrucción A1 × A2")
        self.recon.setChecked(True)
        seccion.caja.addWidget(self.recon)
        self.panel_recon = QWidget()
        caja = QVBoxLayout(self.panel_recon)
        caja.setContentsMargins(0, 0, 0, 0)
        caja.addWidget(_etiqueta("Órdenes A1, A2 (celda A1×A2)"))
        pareja = QHBoxLayout()
        self.orden_a1 = _entero(2, 1, 1, 30)
        self.orden_a2 = _entero(4, 1, 1, 30)
        pareja.addWidget(self.orden_a1)
        pareja.addWidget(self.orden_a2)
        caja.addLayout(pareja)
        seccion.caja.addWidget(self.panel_recon)
        self.recon.toggled.connect(self._al_cambiar_reconstruccion)
        self.orden_a1.valueChanged.connect(self._pedir_dibujo)
        self.orden_a2.valueChanged.connect(self._pedir_dibujo)
        return seccion

    def _seccion_configuracion(self) -> Seccion:
        seccion = Seccion("Configuración")
        seccion.caja.addWidget(_etiqueta("b₁ — rango"))
        self.rango_b1 = _entero(1, 1, 1, 12)
        seccion.caja.addWidget(self.rango_b1)
        seccion.caja.addWidget(_etiqueta("b₂ — rango"))
        self.rango_b2 = _entero(1, 1, 1, 12)
        seccion.caja.addWidget(self.rango_b2)
        seccion.caja.addWidget(_etiqueta("Visualización"))
        self.checks: dict[str, QCheckBox] = {}
        for clave, texto, activo in (
            ("varillas", "Varillas", True),
            ("separacion", "Separación 2π/a al origen", True),
            ("ejes", "Ejes x, y, z", True),
            ("b1", "b₁", True),
            ("b2", "b₂", True),
            ("b3", "b₃ (hexagonal)", True),
            ("bz", "b_z", True),
            ("recon", "Vectores de reconstrucción", True),
            ("k_ewald", "Vector k de Ewald", False),
            ("leyenda", "Mostrar leyenda", True),
        ):
            casilla = QCheckBox(texto)
            casilla.setChecked(activo)
            casilla.toggled.connect(self._pedir_dibujo)
            self.checks[clave] = casilla
            seccion.caja.addWidget(casilla)
        self.rango_b1.valueChanged.connect(self._pedir_dibujo)
        self.rango_b2.valueChanged.connect(self._pedir_dibujo)
        return seccion

    def _seccion_datos(self) -> Seccion:
        seccion = Seccion("Datos")
        self.info = QLabel()
        self.info.setObjectName("info")
        self.info.setWordWrap(True)
        self.info.setTextFormat(Qt.TextFormat.RichText)
        seccion.caja.addWidget(self.info)
        return seccion

    def _panel_vistas(self) -> QFrame:
        panel = QFrame()
        panel.setObjectName("panel")
        capa = QVBoxLayout(panel)
        capa.setContentsMargins(8, 8, 8, 8)

        self.pestanas = QTabWidget()
        self.vista_red = LienzoPlotly(camara_3d=True)
        self.vista_pantalla = LienzoPlotly(camara_3d=False)

        pagina_red = QWidget()
        caja_red = QVBoxLayout(pagina_red)
        caja_red.setContentsMargins(0, 8, 0, 0)
        caja_red.addWidget(self.vista_red)

        pagina_pan = QWidget()
        caja_pan = QVBoxLayout(pagina_pan)
        caja_pan.setContentsMargins(8, 8, 8, 4)
        cabecera = QHBoxLayout()
        rotulo = QLabel("Rotación de la muestra")
        rotulo.setObjectName("campo")
        self.lbl_angulo = QLabel("φ = 0°")
        self.lbl_angulo.setObjectName("angulo")
        cabecera.addWidget(rotulo)
        cabecera.addStretch(1)
        cabecera.addWidget(self.lbl_angulo)
        caja_pan.addLayout(cabecera)

        self.slider = QSlider(Qt.Orientation.Horizontal)
        self.slider.setRange(-180, 180)
        self.slider.setValue(0)
        self.slider.setSingleStep(1)
        self.slider.setPageStep(15)
        caja_pan.addWidget(self.slider)
        marcas = QHBoxLayout()
        for texto in ("−180°", "−90°", "0°", "90°", "180°"):
            marca = QLabel(texto)
            marca.setObjectName("campo")
            if texto != "−180°":
                marca.setAlignment(
                    Qt.AlignmentFlag.AlignHCenter if texto not in ("180°",) else Qt.AlignmentFlag.AlignRight
                )
            marcas.addWidget(marca)
        caja_pan.addLayout(marcas)
        caja_pan.addWidget(self.vista_pantalla, 1)

        self.pestanas.addTab(pagina_red, "Espacio recíproco")
        self.pestanas.addTab(pagina_pan, "Pantalla de fósforo")
        capa.addWidget(self.pestanas)

        self.slider.valueChanged.connect(self._al_mover_slider)
        return panel

    def _simetria(self) -> str:
        for clave, boton in self._radios.items():
            if boton.isChecked():
                return clave
        return "CENT"

    def _modo(self) -> str:
        return "miller" if self.btn_miller.isChecked() else "azimut"

    def _angulo(self) -> float:
        return float(self.slider.value())

    def _aplicar_simetria(self, simetria: str) -> None:
        if simetria == "HEX":
            self.b.setEnabled(False)
            self.lbl_a.setText("Parámetro de red a (Å)")
            self.lbl_b.setText("Parámetro b (no requerido en hexagonal)")
        elif simetria == "RECT":
            self.b.blockSignals(True)
            self.b.setEnabled(True)
            self.b.setValue(3.0)
            self.b.blockSignals(False)
            self.lbl_a.setText("Parámetro de red a (Å)")
            self.lbl_b.setText("Parámetro de red b (Å)")
        else:
            self.b.setEnabled(False)
            self.lbl_a.setText("Parámetro base a (Å)")
            self.lbl_b.setText("Parámetro b (no requerido en FCS)")

    def _al_cambiar_simetria(self, simetria: str, activo: bool) -> None:
        if not activo:
            return
        self._aplicar_simetria(simetria)
        self._pedir_dibujo()

    def _al_cambiar_red(self) -> None:
        self._pedir_dibujo()

    def _al_cambiar_modo(self, miller: bool) -> None:
        self.pila_haz.setCurrentIndex(1 if miller else 0)
        self._pedir_dibujo()

    def _al_cambiar_reconstruccion(self, activa: bool) -> None:
        self.panel_recon.setVisible(activa)
        self._pedir_dibujo()

    def _fijar_phi(self, valor: int) -> None:
        if self.phi.value() == valor:
            return
        self.phi.blockSignals(True)
        self.phi.setValue(valor)
        self.phi.blockSignals(False)

    def _al_editar_phi(self, valor: int) -> None:
        if self.slider.value() != valor:
            self.slider.blockSignals(True)
            self.slider.setValue(valor)
            self.slider.blockSignals(False)
        self.lbl_angulo.setText(f"φ = {valor:.0f}°")
        self._pedir_dibujo()

    def _al_mover_slider(self, valor: int) -> None:
        self._fijar_phi(valor)
        self.lbl_angulo.setText(f"φ = {valor:.0f}°")
        self._pedir_dibujo()

    def _pedir_dibujo(self, *_args) -> None:
        self._temporizador.start()

    def _b_efectivo(self) -> float:
        if self._simetria() == "RECT":
            return float(self.b.value())
        return float(self.a.value())

    def figuras(self):
        """Las dos figuras y el ángulo, a partir de los controles actuales."""
        simetria = self._simetria()
        a = float(self.a.value())
        b = self._b_efectivo()
        modo = self._modo()
        angulo = self._angulo()
        reconstruir = self.recon.isChecked()
        flags = {clave: casilla.isChecked() for clave, casilla in self.checks.items()}
        flags["ewald"] = self.esfera.isChecked()
        try:
            red = rr.calculadora(
                simetria, a, b, int(self.rango_b1.value()), int(self.rango_b2.value()),
                modo, angulo, int(self.miller_u.value()), int(self.miller_v.value()),
                float(self.kev.value()), float(self.theta.value()),
                reconstruir, int(self.orden_a1.value()), int(self.orden_a2.value()),
                flags, float(self.distancia.value()), float(self.radio.value()), angulo,
            )
        except Exception as exc:
            red = _figura_error(str(exc))
        try:
            pantalla = rr.figura_pantalla(
                simetria, a, b,
                modo, angulo, int(self.miller_u.value()), int(self.miller_v.value()),
                float(self.kev.value()), float(self.theta.value()),
                reconstruir, int(self.orden_a1.value()), int(self.orden_a2.value()),
                float(self.distancia.value()), float(self.radio.value()), angulo,
            )
        except Exception as exc:
            pantalla = _figura_error(str(exc))
        return red, pantalla, angulo

    def _dibujar(self) -> None:
        red, pantalla, angulo = self.figuras()
        self.vista_red.mostrar(red)
        self.vista_pantalla.mostrar(pantalla)
        self.lbl_angulo.setText(f"φ = {angulo:.0f}°")
        self.info.setText(texto_vectores(self._simetria(), float(self.a.value()), self._b_efectivo()))


def main() -> int:
    app = QApplication(sys.argv)
    app.setStyle("Fusion")
    ventana = Ventana()
    ventana.show()
    return app.exec()


if __name__ == "__main__":
    raise SystemExit(main())
