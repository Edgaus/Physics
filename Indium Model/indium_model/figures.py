"""Figures for the three incorporation regimes."""

from __future__ import annotations

from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np

from indium_model.growth import GrowResult
from indium_model.profiles import DepthProfile, SampleReport
COLORS = {
    "MME914": "#b91c1c",
    "MME925": "#d97706",
    "MME930": "#0369a1",
    "MME931": "#0f766e",
}


def _style() -> None:
    plt.rcParams.update(
        {
            "font.size": 11,
            "axes.labelsize": 12,
            "axes.titlesize": 12,
            "legend.fontsize": 9,
            "figure.dpi": 140,
            "savefig.dpi": 170,
            "axes.grid": True,
            "grid.alpha": 0.28,
            "grid.linestyle": "--",
            "axes.axisbelow": True,
        }
    )


def _one_well_curve(
    result: GrowResult, profile: DepthProfile
) -> tuple[np.ndarray, np.ndarray]:
    """Return growth-coordinate z and x around well 2, z = 0 at its start."""
    layers = result.layers
    origin = 0.0
    seen = False
    for layer in layers:
        if layer.well_index == 2 and layer.kind == "well":
            seen = True
            break
        origin += layer.thickness_nm
    if not seen:
        raise ValueError("stack has no well 2")
    # Keep a few nm of the lower barrier and the upper tail.
    z_rel = profile.z_nm - origin
    keep = (z_rel >= -6.0) & (z_rel <= 28.0)
    return z_rel[keep], profile.x[keep]


def plot_regions(
    results: list[tuple[GrowResult, DepthProfile, SampleReport]],
    path: Path,
) -> None:
    """One well of each region, aligned at the substrate-side edge."""
    _style()
    chosen = [item for item in results if item[0].regime.sample in {"MME914", "MME925", "MME931"}]
    fig, axes = plt.subplots(1, 3, figsize=(11.2, 4.15), sharey=True)
    for axis, (result, profile, sample) in zip(axes, chosen):
        z_nm, x = _one_well_curve(result, profile)
        color = COLORS[result.regime.sample]
        axis.plot(z_nm, 100.0 * x, color=color, lw=2.0)
        axis.axvspan(0.0, sample.wells[1].thickness_nm, color=color, alpha=0.08, lw=0)
        axis.set_xlim(-6.0, 28.0)
        axis.set_ylim(0.0, 32.0)
        axis.set_xlabel("Crecimiento desde el borde del pozo (nm)")
        axis.set_title(
            f"Región {result.regime.region}: {result.regime.sample}\n"
            f"{result.regime.temperature_c:.0f} °C,  λ = {sample.segregation_length_nm:.1f} nm"
        )
    axes[0].set_ylabel("Incorporación de In, x (%)")
    fig.suptitle(
        "Banda tenue: pozo. A la derecha, la barrera. Dirección de crecimiento →",
        y=0.02,
        fontsize=10,
        color="0.35",
    )
    fig.tight_layout(rect=(0, 0.08, 1, 1))
    fig.savefig(path)
    plt.close(fig)


def plot_stacks(
    results: list[tuple[GrowResult, DepthProfile, SampleReport]],
    path: Path,
) -> None:
    """Full active region as SIMS would see it, plus the crater peak values."""
    _style()
    fig, axes = plt.subplots(2, 2, figsize=(10.6, 7.2), sharex=True, sharey=True)
    for axis, (result, profile, sample) in zip(axes.ravel(), results):
        color = COLORS[result.regime.sample]
        axis.plot(
            profile.depth_nm,
            100.0 * profile.x,
            color=color,
            lw=1.15,
            alpha=0.45,
            label="Perfil del modelo",
        )
        axis.plot(
            profile.depth_nm,
            100.0 * profile.x_sims,
            color=color,
            lw=2.0,
            label="Modelo con resolución SIMS",
        )
        axis.scatter(
            [],
            [],
            s=28,
            color="0.15",
            label="In/N de cráter",
        )
        for well, measured in zip(sample.wells, result.regime.sims_peaks):
            axis.scatter(
                [well.sims_peak_depth_nm],
                [100.0 * measured],
                s=28,
                zorder=4,
                color="0.15",
            )
        axis.set_title(
            f"{result.regime.sample}  ·  región {result.regime.region}  ·  "
            f"{result.regime.temperature_c:.0f} °C"
        )
        axis.set_xlim(0.0, max(item[1].depth_nm[0] for item in results))
        axis.set_ylim(0.0, 34.0)
    axes[0, 0].legend(loc="upper right", frameon=False)
    axes[1, 0].set_xlabel("Profundidad desde la superficie (nm), hacia el sustrato →")
    axes[1, 1].set_xlabel("Profundidad desde la superficie (nm), hacia el sustrato →")
    axes[0, 0].set_ylabel("x de In (%)")
    axes[1, 0].set_ylabel("x de In (%)")
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_balance(
    reports: list[SampleReport],
    path: Path,
) -> None:
    """Where the supplied indium ends, as a fraction of the dose."""
    _style()
    labels = [f"{item.sample}\n{item.temperature_c:.0f} °C" for item in reports]
    wells = np.array([item.incorporated_wells / item.supplied for item in reports])
    tails = np.array([item.incorporated_barriers / item.supplied for item in reports])
    lost = np.array([item.desorbed / item.supplied for item in reports])
    x = np.arange(len(reports))
    fig, axis = plt.subplots(figsize=(8.2, 4.6))
    axis.bar(x, 100.0 * wells, 0.62, label="En los pozos", color="#1e3a5f")
    axis.bar(
        x,
        100.0 * tails,
        0.62,
        bottom=100.0 * wells,
        label="En las barreras (cola)",
        color="#d97706",
    )
    axis.bar(
        x,
        100.0 * lost,
        0.62,
        bottom=100.0 * (wells + tails),
        label="Desorbido",
        color="#b91c1c",
    )
    axis.set_xticks(x, labels)
    axis.set_ylabel("Fracción del In enviado (%)")
    axis.set_ylim(0.0, 108.0)
    axis.legend(loc="upper center", ncol=3, frameon=False, bbox_to_anchor=(0.5, 1.02))
    axis.set_title("Balance del indio enviado a los tres pozos", pad=28)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)


def plot_trends(reports: list[SampleReport], path: Path) -> None:
    _style()
    x_max = [100.0 * max(well.x_max for well in item.wells) for item in reports]
    length = [item.segregation_length_nm for item in reports]
    fig, axes = plt.subplots(1, 2, figsize=(8.8, 3.8))
    for item, x_value, length_value in zip(reports, x_max, length):
        color = COLORS[item.sample]
        axes[0].scatter(item.temperature_c, x_value, s=55, color=color, zorder=3)
        axes[0].annotate(
            item.sample,
            (item.temperature_c, x_value),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=8,
            color=color,
        )
        axes[1].scatter(item.temperature_c, length_value, s=55, color=color, zorder=3)
        axes[1].annotate(
            item.sample,
            (item.temperature_c, length_value),
            textcoords="offset points",
            xytext=(6, 6),
            fontsize=8,
            color=color,
        )
    axes[0].set_xlabel("Temperatura del pozo (°C)")
    axes[1].set_xlabel("Temperatura del pozo (°C)")
    axes[0].set_ylabel("x máximo del pozo (%)")
    axes[1].set_ylabel("Longitud de segregación λ (nm)")
    axes[0].set_ylim(0.0, 32.0)
    axes[1].set_ylim(0.0, 8.0)
    fig.tight_layout()
    fig.savefig(path)
    plt.close(fig)
