"""Texto de las tres fuentes, una al lado de la otra, sin fusionar campos."""

from __future__ import annotations

from indium_model.article import (
    ARTICLE_TITLE,
    FINAL_WELL_QUALITATIVE,
    HAMILTONIAN,
    LAB_ABBREVIATION,
    SAMPLES,
    SIMS,
    TECHNIQUE_IN_CONCLUSIONS,
    TECHNIQUE_IN_GROWTH_SECTION,
    TEM_WELL_NM,
    TRIPLET_READING,
)
from indium_model.bitacora import NOTEBOOKS, by_sample
from indium_model.checks import section_5
from indium_model.plans import (
    PLAN_913_914,
    PLAN_932,
    PLAN_932_PLASMA_W,
    PLAN_932_WELL_NM,
    GrowthPlan,
)


def informe() -> str:
    parts = [
        "InGaN cúbico sobre 3C-SiC(001)/Si",
        "Muestras: MME914, MME925, MME930, MME931.",
        f"En el laboratorio el proceso se abrevia {LAB_ABBREVIATION}.",
        f"El artículo, en el crecimiento, lo llama {TECHNIQUE_IN_GROWTH_SECTION}.",
        f"En las conclusiones lo llama {TECHNIQUE_IN_CONCLUSIONS}.",
        "",
        _article_block(),
        "",
        _plan_block(PLAN_913_914),
        "",
        _plan_block(PLAN_932, plasma_W=PLAN_932_PLASMA_W, well_nm=PLAN_932_WELL_NM),
        "",
        _notebook_block(),
    ]
    return "\n".join(parts).rstrip() + "\n"


def comparar() -> str:
    lines = [
        "Artículo y bitácora, muestra por muestra.",
        TRIPLET_READING,
        "",
    ]
    for row in SAMPLES:
        book = by_sample(row.sample)
        lines.append(row.sample)
        lines.append(
            f"  Artículo: pozos {row.well_temperature}; barreras {row.barrier_GaN_C} °C; "
            f"ciclo {row.ga_cycle}; N2 {row.n2_sccm} sccm; PMBE {row.pmbe} Torr."
        )
        lines.append(f"  Bitácora ({book.pages}): flujo { _percent(book.flow_percent) }.")
        for reading in book.readings:
            lines.append(_format_reading(reading, indent="    "))
        for pressure in book.pressures:
            lines.append(f"    Presión, {pressure.context}: {pressure.value} Torr.")
        cycle = book.ga_cycle if book.ga_cycle else "Estas páginas no escriben el ciclo de Ga."
        lines.append(f"    Ciclo de Ga: {cycle}")
        lines.append("")
    lines.append(FINAL_WELL_QUALITATIVE)
    return "\n".join(lines).rstrip() + "\n"


def afirmar() -> str:
    lines = ["Qué queda afirmado con los datos separados.", ""]
    for text, ok in section_5():
        mark = "sí" if ok else "no"
        lines.append(f"[{mark}] {text}")
    return "\n".join(lines).rstrip() + "\n"


def _article_block() -> str:
    lines = [
        "1. Borrador del artículo",
        ARTICLE_TITLE,
        "",
        "Tabla del borrador:",
    ]
    for row in SAMPLES:
        lines.append(
            f"  {row.sample}: pozos {row.well_temperature}; barreras {row.barrier_GaN_C} °C; "
            f"{row.ga_cycle}; N2 {row.n2_sccm} sccm; {row.pmbe} Torr."
        )
    lines.append("")
    lines.append("SIMS, In/N de cráter, cota inferior de x, no consigna:")
    for row in SIMS:
        lines.append(f"  {row.sample}: QW1 {row.qw1} %, QW2 {row.qw2} %, QW3 {row.qw3} %.")
    lines.append("")
    lines.append("Hamiltoniano, promedio de capa, no pico de cráter:")
    for row in HAMILTONIAN:
        joined = ", ".join(f"{value} %" for value in row.percent)
        lines.append(f"  {row.sample}: {joined}.")
    lines.append("")
    lines.append("TEM:")
    for sample, width in TEM_WELL_NM.items():
        lines.append(f"  {sample}: pozos {width}.")
    lines.append("  MME930: sin ancho TEM.")
    lines.append(FINAL_WELL_QUALITATIVE)
    return "\n".join(lines)


def _plan_block(plan: GrowthPlan, plasma_W: dict[str, int] | None = None, well_nm: int | None = None) -> str:
    lines = [
        f"Plan {plan.plan_id} ({plan.date})",
        plan.filename,
        plan.scope_note,
        plan.objective,
        "Equipo: " + ", ".join(plan.crew) + ".",
        f"Apila: {plan.stack}.",
        f"Plasma: {plan.plasma}",
        plan.preparation,
        plan.buffer,
        "Celdas:",
    ]
    for moment in plan.cell_moments:
        inn = moment.in_note if moment.in_bep is None else f"{moment.in_bep} Torr, {moment.in_note}"
        lines.append(
            f"  {moment.when}: Ga {moment.ga_bep} Torr a {moment.ga_cell_C} °C; In {inn}."
        )
    lines.append("Barreras:")
    for barrier in plan.barriers:
        bits = (
            f"{barrier.name}: {barrier.thickness_nm} nm",
            barrier.temperature,
            barrier.ga_sequence,
            barrier.written_duration,
        )
        lines.append("  " + " ".join(_sentence(bit) for bit in bits))
    lines.append("Pozos:")
    for well in plan.wells:
        target = (
            f"In esperado {well.expected_in_percent} % (meta del plan, no SIMS). "
            if well.expected_in_percent is not None
            else "El plan no escribe un In %. "
        )
        power = ""
        if plasma_W is not None:
            power = f"Plasma {plasma_W[well.name]} W. "
        thickness = f"{well_nm} nm. " if well_nm is not None else ""
        computed = well.seconds_omitting_final_pause()
        minutes, seconds = divmod(computed, 60)
        lines.append(
            f"  {well.name}: Ga {well.ga_open_s} s, pausa solo N {well.pause_only_n_s} s, "
            f"In {well.in_open_s} s, pausa {well.pause_s} s, {well.pulses} pulsos. "
            f"{thickness}{power}{target}"
            f"Tiempo escrito {well.written_duration}. "
            f"Sin la pausa final da {minutes} min {seconds} s."
        )
    return "\n".join(lines)


def _notebook_block() -> str:
    lines = ["4. Bitácora"]
    for book in NOTEBOOKS:
        lines.append("")
        lines.append(f"{book.sample} ({book.pages})")
        if book.pages_note:
            lines.append(book.pages_note)
        lines.append(
            f"Plasma calibrado a {book.plasma_calibration_W} W y fijado en {book.plasma_set_W} W. "
            f"Flujo {_percent(book.flow_percent)}."
        )
        for reading in book.readings:
            lines.append(_format_reading(reading, indent="  "))
        for pressure in book.pressures:
            lines.append(f"  Presión, {pressure.context}: {pressure.value} Torr.")
        if book.ga_cycle:
            lines.append(f"  Ciclo de Ga: {book.ga_cycle}")
        else:
            lines.append("  Ciclo de Ga: estas páginas no lo escriben.")
        for note in book.notes:
            lines.append(f"  {note}")
        lines.append("  Video:")
        for mark in book.video:
            lines.append(f"    {mark}")
    return "\n".join(lines)


def _format_reading(reading, indent: str) -> str:
    temps = _reading_temps(reading)
    detail = reading.detail
    if temps and not any(mark in detail for mark in ("Tsus", "Tpiro", "Tpir")):
        body = f"{temps}. {detail}".strip()
    else:
        body = detail or temps
    return f"{indent}{reading.stage}: {reading.label}. {body}"


def _sentence(text: str) -> str:
    text = text.strip()
    if not text or text.endswith((".", "…")):
        return text
    return text + "."


def _percent(value: float) -> str:
    text = f"{value:g}"
    return f"{text} %"


def _reading_temps(reading) -> str:
    chunks = []
    if reading.tsus_C is not None:
        chunks.append(f"Tsus = {reading.tsus_C:g} °C")
    if reading.tpiro_C is not None:
        chunks.append(f"Tpiro = {reading.tpiro_C:g} °C")
    return ", ".join(chunks)
