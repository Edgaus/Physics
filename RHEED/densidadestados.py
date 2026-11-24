#!/usr/bin/env python3
"""Esquema de las cuatro densidades de estados.

Paneles: bulto 3D, pozo 2D, hilo 1D y punto 0D.
Las energías y las alturas están en unidades arbitrarias.
En 0D la altura del segmento es el peso de la delta.
"""

from pathlib import Path

import matplotlib.pyplot as plt
import numpy as np

SALIDA = Path(__file__).resolve().parent / "figuras"
E_MIN, E_MAX = -0.35, 5.4
E = np.linspace(E_MIN, E_MAX, 5000)

BORDE = "#9a3412"
CURVA = "#1e3a5f"
RELLENO = "#dbe7f3"


def marcar(ax, energia, texto, y, ha="left", va="bottom"):
    ax.axvline(energia, color=BORDE, lw=0.8, ls=(0, (3, 2)), zorder=1)
    if texto:
        ax.text(
            energia + 0.08,
            y,
            texto,
            ha=ha,
            va=va,
            color=BORDE,
            fontsize=9,
        )


def panel_3d(ax):
    ec = 0.0
    g = np.zeros_like(E)
    encima = E >= ec
    g[encima] = 1.15 * np.sqrt(E[encima] - ec)
    ax.fill_between(E, g, color=RELLENO, zorder=0)
    ax.plot(E, g, color=CURVA, lw=2)
    marcar(ax, ec, r"borde de banda $E_c$", 2.55)
    ax.set_ylim(-0.15, 3.1)
    ax.set_title("(a)  Bulto 3D")


def panel_2d(ax):
    umbrales = (0.55, 2.05, 4.15)
    xs = [E_MIN]
    ys = [0.0]
    for i, eth in enumerate(umbrales):
        xs.extend([eth, eth])
        ys.extend([i, i + 1])
    xs.append(E_MAX)
    ys.append(len(umbrales))
    ax.plot(xs, ys, color=CURVA, lw=2)
    for n, eth in enumerate(umbrales, start=1):
        marcar(ax, eth, rf"$E_{n}$", n + 0.12)
    ax.set_ylim(-0.15, 3.7)
    ax.set_title("(b)  Pozo 2D")


def panel_1d(ax):
    # (umbral, degeneración orbital de la subbanda)
    subbandas = ((0.70, 1, r"$E_{11}$"), (2.30, 2, r"$E_{12}=E_{21}$"), (4.40, 1, r"$E_{22}$"))
    g = np.zeros_like(E)
    for eth, deg, _ in subbandas:
        activo = E > eth
        g[activo] += deg / np.sqrt(E[activo] - eth)
    ax.plot(E, g, color=CURVA, lw=2)
    for eth, _, etiqueta in subbandas:
        marcar(ax, eth, etiqueta, 3.35, va="top")
    ax.set_ylim(-0.15, 3.6)
    ax.set_title("(c)  Hilo 1D")


def panel_0d(ax):
    # (energía, peso). El peso 4 es dos orbitales degenerados, cada uno con espín 2.
    niveles = ((0.85, 2), (2.15, 4), (3.45, 2), (4.75, 2))
    for energia, peso in niveles:
        ax.vlines(energia, 0, peso, color=CURVA, lw=2.4)
        ax.plot(energia, peso, "o", color=CURVA, ms=5)
        ax.annotate(
            f"peso {peso}",
            xy=(energia, peso),
            xytext=(0, 6),
            textcoords="offset points",
            ha="center",
            va="bottom",
            fontsize=8,
            color=CURVA,
        )
        marcar(ax, energia, "", 0)
    ax.set_ylim(-0.2, 5.4)
    ax.set_ylabel(r"peso de $\delta(E-E_i)$")
    ax.set_title("(d)  Punto 0D")


def main():
    plt.rcParams.update({
        "font.size": 11,
        "axes.labelsize": 12,
        "axes.titlesize": 13,
        "axes.spines.top": False,
        "axes.spines.right": False,
        "axes.linewidth": 0.8,
        "figure.facecolor": "white",
        "savefig.facecolor": "white",
    })

    fig, ejes = plt.subplots(2, 2, figsize=(9.4, 7.2), sharex=True)
    panel_3d(ejes[0, 0])
    panel_2d(ejes[0, 1])
    panel_1d(ejes[1, 0])
    panel_0d(ejes[1, 1])

    for ax in (ejes[0, 0], ejes[0, 1], ejes[1, 0]):
        ax.set_ylabel(r"$g(E)$  (u. a.)")
    for ax in ejes[1]:
        ax.set_xlabel(r"energía $E$  (u. a.)")
    for ax in ejes.ravel():
        ax.set_xlim(E_MIN, E_MAX)
        ax.axhline(0, color="#cbd5e1", lw=0.6, zorder=0)

    fig.tight_layout()
    SALIDA.mkdir(exist_ok=True)
    png = SALIDA / "dos_cuatro_paneles.png"
    pdf = SALIDA / "dos_cuatro_paneles.pdf"
    fig.savefig(png, dpi=180)
    fig.savefig(pdf)
    print(png)
    print(pdf)


if __name__ == "__main__":
    main()
