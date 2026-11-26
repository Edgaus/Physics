#!/usr/bin/env python3
"""Reproduce CRECIMIENTO 966.pdf as an editable Word document."""

import os
import subprocess
import sys
from pathlib import Path

from docx import Document
from docx.enum.text import WD_ALIGN_PARAGRAPH, WD_LINE_SPACING
from docx.oxml import OxmlElement
from docx.oxml.ns import qn
from docx.shared import Pt, RGBColor, Twips

# Siempre junto a este script, sin importar desde qué carpeta se ejecute.
OUT = Path(__file__).resolve().parent / "CRECIMIENTO 966.docx"

PURPLE = "7030A0"
BLUE = "0070C0"
BLACK = "000000"
WHITE = "FFFFFF"
BORDER = "A6A6A6"
BAND = "F2F2F2"
ALN = "9353F4"
LBLUE = "59B2F6"
TEAL = "2CC09C"
NAVY = "135589"

BR = ("br",)


def rgb(hex_color):
    return RGBColor.from_string(hex_color)


def _rfonts(run, name="Arial"):
    rPr = run._element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), name)


def style_run(run, *, size=8.5, bold=False, color=BLACK, underline=False, sub=False, sup=False):
    run.font.name = "Arial"
    run.bold = bold
    run.italic = False
    run.underline = underline
    # Word already draws sub/superscript smaller. Setting a reduced size here
    # shrinks them a second time and makes 10⁻⁸ unreadable.
    run.font.size = Pt(size)
    run.font.color.rgb = rgb(color)
    run.font.subscript = bool(sub)
    run.font.superscript = bool(sup)
    _rfonts(run)


def add_runs(paragraph, parts, size=8.5):
    for part in parts:
        if part == BR or (isinstance(part, tuple) and part and part[0] == "br"):
            run = paragraph.add_run()
            style_run(run, size=size)
            run.add_break()
            continue
        if isinstance(part, str):
            text, kw = part, {}
        elif isinstance(part, tuple) and len(part) == 1:
            text, kw = part[0], {}
        else:
            text, kw = part
        run = paragraph.add_run(text)
        style_run(
            run,
            size=kw.get("size", size),
            bold=kw.get("bold", False),
            color=kw.get("color", BLACK),
            underline=kw.get("underline", False),
            sub=kw.get("sub", False),
            sup=kw.get("sup", False),
        )


def set_paragraph(paragraph, align, *, before=0, after=0, line=None, left=0, right=0):
    paragraph.alignment = {
        "center": WD_ALIGN_PARAGRAPH.CENTER,
        "left": WD_ALIGN_PARAGRAPH.LEFT,
        "right": WD_ALIGN_PARAGRAPH.RIGHT,
    }[align]
    fmt = paragraph.paragraph_format
    fmt.space_before = Pt(before)
    fmt.space_after = Pt(after)
    fmt.line_spacing = 1.0 if line is None else Pt(line)
    if line is not None:
        fmt.line_spacing_rule = WD_LINE_SPACING.EXACTLY
    if left or right:
        fmt.left_indent = Pt(left)
        fmt.right_indent = Pt(right)


def shade(cell, fill):
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag == qn("w:shd"):
            tcPr.remove(child)
    shd = OxmlElement("w:shd")
    shd.set(qn("w:val"), "clear")
    shd.set(qn("w:color"), "auto")
    shd.set(qn("w:fill"), fill)
    tcPr.append(shd)


def valign(cell, value):
    tcPr = cell._tc.get_or_add_tcPr()
    node = tcPr.find(qn("w:vAlign"))
    if node is None:
        node = OxmlElement("w:vAlign")
        tcPr.append(node)
    node.set(qn("w:val"), value)


def cell_margins(cell, top=40, bottom=20, left=80, right=80):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = tcPr.find(qn("w:tcMar"))
    if tcMar is None:
        tcMar = OxmlElement("w:tcMar")
        tcPr.append(tcMar)
    else:
        for child in list(tcMar):
            tcMar.remove(child)
    for name, val in (("top", top), ("left", left), ("bottom", bottom), ("right", right)):
        el = OxmlElement(f"w:{name}")
        el.set(qn("w:w"), str(int(val)))
        el.set(qn("w:type"), "dxa")
        tcMar.append(el)


def set_table_width(table, width_pt, jc="center"):
    tblPr = table._tbl.tblPr
    tblW = tblPr.find(qn("w:tblW"))
    if tblW is None:
        tblW = OxmlElement("w:tblW")
        tblPr.append(tblW)
    tblW.set(qn("w:w"), str(int(round(width_pt * 20))))
    tblW.set(qn("w:type"), "dxa")
    layout = tblPr.find(qn("w:tblLayout"))
    if layout is None:
        layout = OxmlElement("w:tblLayout")
        tblPr.append(layout)
    layout.set(qn("w:type"), "fixed")
    node = tblPr.find(qn("w:jc"))
    if node is None:
        node = OxmlElement("w:jc")
        tblPr.append(node)
    node.set(qn("w:val"), jc)
    spacing = tblPr.find(qn("w:tblCellSpacing"))
    if spacing is None:
        spacing = OxmlElement("w:tblCellSpacing")
        tblPr.append(spacing)
    spacing.set(qn("w:w"), "0")
    spacing.set(qn("w:type"), "dxa")


def set_borders(table, color=BORDER, sz="4"):
    tblPr = table._tbl.tblPr
    borders = tblPr.find(qn("w:tblBorders"))
    if borders is None:
        borders = OxmlElement("w:tblBorders")
        tblPr.append(borders)
    else:
        for child in list(borders):
            borders.remove(child)
    for edge in ("top", "left", "bottom", "right", "insideH", "insideV"):
        el = OxmlElement(f"w:{edge}")
        el.set(qn("w:val"), "single" if sz != "0" else "nil")
        el.set(qn("w:sz"), sz)
        el.set(qn("w:space"), "0")
        el.set(qn("w:color"), color)
        borders.append(el)


def clear_borders(table):
    set_borders(table, color="auto", sz="0")


def set_col_widths(table, widths):
    tbl = table._tbl
    grid = tbl.find(qn("w:tblGrid"))
    for child in list(grid):
        grid.remove(child)
    for width in widths:
        gc = OxmlElement("w:gridCol")
        gc.set(qn("w:w"), str(int(round(width * 20))))
        grid.append(gc)
    for row in table.rows:
        for cell, width in zip(row.cells, widths):
            tcPr = cell._tc.get_or_add_tcPr()
            tcW = tcPr.find(qn("w:tcW"))
            if tcW is None:
                tcW = OxmlElement("w:tcW")
                tcPr.append(tcW)
            tcW.set(qn("w:w"), str(int(round(width * 20))))
            tcW.set(qn("w:type"), "dxa")


def set_row_height(row, pt):
    trPr = row._tr.get_or_add_trPr()
    for child in list(trPr):
        if child.tag == qn("w:trHeight"):
            trPr.remove(child)
    height = OxmlElement("w:trHeight")
    height.set(qn("w:val"), str(int(round(pt * 20))))
    height.set(qn("w:hRule"), "exact")
    trPr.append(height)


def B(text, **kw):
    kw.setdefault("bold", True)
    kw.setdefault("color", BLUE)
    return (text, kw)


def S(text, **kw):
    kw["sub"] = True
    return (text, kw)


def P(text, **kw):
    kw["sup"] = True
    return (text, kw)


def fill_cell(cell, paragraphs, *, align="center", valign_="top", fill=None, margins=(40, 40, 60, 60)):
    """paragraphs: list of (parts, kwargs)."""
    if fill:
        shade(cell, fill)
    valign(cell, valign_)
    top, bottom, left, right = margins
    cell_margins(cell, top, bottom, left, right)
    first = True
    for parts, kw in paragraphs:
        paragraph = cell.paragraphs[0] if first else cell.add_paragraph()
        first = False
        set_paragraph(
            paragraph,
            kw.get("align", align),
            before=kw.get("before", 0),
            after=kw.get("after", 0),
            line=kw.get("line"),
            left=kw.get("left", 0),
            right=kw.get("right", 0),
        )
        add_runs(paragraph, parts, size=kw.get("size", 8.5))
    if first:
        set_paragraph(cell.paragraphs[0], align)


def add_stack(cell, bands, fill=None):
    if fill:
        shade(cell, fill)
    valign(cell, "center")
    cell_margins(cell, 60, 40, 80, 80)
    anchor = cell.paragraphs[0]
    set_paragraph(anchor, "center", line=1)
    table = cell.add_table(rows=len(bands), cols=1)
    set_table_width(table, 84, jc="center")
    clear_borders(table)
    set_col_widths(table, [84])
    for row, (height, color, label) in zip(table.rows, bands):
        set_row_height(row, height)
        inner = row.cells[0]
        shade(inner, color)
        valign(inner, "center")
        cell_margins(inner, 0, 0, 0, 0)
        paragraph = inner.paragraphs[0]
        set_paragraph(paragraph, "center", line=max(height - 1, 4))
        if label:
            add_runs(paragraph, [label], size=8.5)
            for run in paragraph.runs:
                style_run(run, size=8.5, color=WHITE)
    return table


def blue_line_growth():
    return [
        B("T"),
        S("pir", bold=True, color=BLUE),
        B("= 720 °C, BEP"),
        S("Al", bold=True, color=BLUE),
        B("=9x10"),
        P("-8", bold=True, color=BLUE),
        B(" Torr, T"),
        S("Al", bold=True, color=BLUE),
        B("=?°C"),
    ]


def build():
    doc = Document()
    normal = doc.styles["Normal"]
    normal.font.name = "Arial"
    normal.font.size = Pt(9.5)
    normal.font.color.rgb = rgb(BLACK)
    _rfonts_style(normal)
    pf = normal.paragraph_format
    pf.space_before = Pt(0)
    pf.space_after = Pt(0)
    pf.line_spacing = 1.0

    section = doc.sections[0]
    section.page_width = Twips(12240)
    section.page_height = Twips(15840)
    section.left_margin = Pt(46)
    section.right_margin = Pt(46)
    section.top_margin = Pt(71)
    section.bottom_margin = Pt(50)
    section.header_distance = Pt(28)
    section.footer_distance = Pt(28)

    title = doc.add_paragraph()
    set_paragraph(title, "center", before=0, after=2, line=13)
    add_runs(title, [("CRECIMIENTO 966", {"bold": True, "color": PURPLE, "underline": True, "size": 9.5})], size=9.5)

    objetivo = doc.add_paragraph()
    set_paragraph(objetivo, "center", before=0, after=0, line=12, left=42, right=42)
    add_runs(
        objetivo,
        [
            ("Objetivo.", {"underline": True, "size": 9.5}),
            (" Crecimiento de AlN cúbico sobre sustratos de SiC(100) para un espesor de 100 nm", {"size": 9.5}),
        ],
        size=9.5,
    )

    busca = doc.add_paragraph()
    set_paragraph(busca, "center", before=0, after=6, line=12, left=42, right=42)
    add_runs(
        busca,
        [
            (
                "Se buscarán las mejores condiciones de crecimiento de AlN cúbico fijando el flujo de Al, flujo de N y la potencia del plasma, pero variando la temperatura del sustrato",
                {"size": 9.5},
            )
        ],
        size=9.5,
    )

    widths = [22.0, 92.0, 310.0, 96.0]
    heights = [90.8, 43.7, 15.8, 45.6, 146.0, 104.9]
    shaded = {1, 3, 5}

    table = doc.add_table(rows=6, cols=4)
    table.autofit = False
    table.allow_autofit = False
    set_table_width(table, sum(widths))
    set_borders(table)
    set_col_widths(table, widths)
    for row, height in zip(table.rows, heights):
        set_row_height(row, height)

    def band(i):
        return BAND if i in shaded else "FFFFFF"

    # Row 5 — crecimiento de AlN
    i = 0
    fill_cell(table.cell(i, 0), [([("5",)], {})], fill=band(i), margins=(60, 20, 20, 20))
    fill_cell(
        table.cell(i, 1),
        [([("Crecimiento de AlN",)], {})],
        fill=band(i),
        valign_="center",
        margins=(40, 40, 40, 40),
    )
    fill_cell(
        table.cell(i, 2),
        [
            (blue_line_growth(), {}),
            ([("Abrir Al y N simultáneamente por 20 s e interrumpir por 30 s",)], {}),
            ([("Continuar los ciclos hasta completar 5 minutos de nucleación intencional", {"underline": True})], {}),
            ([("No exponer directamente a N, esto puede inducir la fase hexagonal", {"underline": True})], {}),
            (
                [("Revisar la evolución del RHEED", {"bold": True, "underline": True})],
                {"before": 6},
            ),
            ([(" ",)], {}),
            ([("Crecer 20 ML de AlN e interrumpir por 30 segundos hasta completar 100 nm.",)], {}),
            ([("Monitorear el RHEED durante cada ciclo", {"underline": True})], {}),
        ],
        fill=band(i),
        margins=(40, 20, 50, 50),
    )
    add_stack(
        table.cell(i, 3),
        [
            (26.0, ALN, "AlN"),
            (5.5, LBLUE, None),
            (4.4, TEAL, None),
            (22.0, NAVY, "3C-SiC"),
        ],
        fill=band(i),
    )

    # Row 4 — nitruración no intencional
    i = 1
    fill_cell(table.cell(i, 0), [([("4",)], {})], fill=band(i), margins=(40, 20, 20, 20))
    fill_cell(
        table.cell(i, 1),
        [
            ([("Nitruración de",)], {}),
            ([("Aluminio No",)], {}),
            ([("Intencional",)], {}),
            ([("(Nucleación)",)], {}),
        ],
        fill=band(i),
        valign_="center",
        margins=(20, 20, 30, 30),
    )
    fill_cell(
        table.cell(i, 2),
        [
            (
                [
                    ("Shutter de N cerrado y shutter de Al cerrado, durante 5 min (tiempo después",),
                    BR,
                    ("del encendido del plasma)",),
                ],
                {},
            )
        ],
        fill=band(i),
        valign_="center",
        margins=(20, 20, 50, 50),
    )
    add_stack(
        table.cell(i, 3),
        [
            (7.6, LBLUE, None),
            (4.4, TEAL, None),
            (22.1, NAVY, "3C-SiC"),
        ],
        fill=band(i),
    )

    # Row 3 — plasma
    i = 2
    fill_cell(table.cell(i, 0), [([("3",)], {})], fill=band(i), valign_="center", margins=(0, 0, 20, 20))
    fill_cell(
        table.cell(i, 1),
        [([("Encendido del plasma",)], {})],
        fill=band(i),
        valign_="center",
        margins=(0, 0, 30, 30),
    )
    fill_cell(
        table.cell(i, 2),
        [([("P=150 W y Flujo=2.6%=0.26 sccm", {"bold": True, "color": BLUE})], {})],
        fill=band(i),
        valign_="center",
        margins=(0, 0, 40, 40),
    )
    fill_cell(table.cell(i, 3), [], fill=band(i), valign_="center", margins=(0, 0, 0, 0))

    # Row 2 — capa inicial de Al
    i = 3
    fill_cell(table.cell(i, 0), [([("2",)], {})], fill=band(i), margins=(40, 20, 20, 20))
    fill_cell(
        table.cell(i, 1),
        [([("Capa inicial de Al",)], {}), ([("(1 ML)",)], {})],
        fill=band(i),
        margins=(40, 20, 30, 30),
    )
    fill_cell(
        table.cell(i, 2),
        [
            (
                [
                    B("T"),
                    S("pir", bold=True, color=BLUE),
                    B("=850°C  BEP"),
                    S("Al", bold=True, color=BLUE),
                    B(" = 1.5x10"),
                    P("-7", bold=True, color=BLUE),
                    B(" Torr , T"),
                    S("Al", bold=True, color=BLUE),
                    B("=?°C"),
                ],
                {},
            ),
            (
                [
                    ("Abrir celda de Al por ",),
                    ("30 segundos", {"bold": True, "underline": True}),
                ],
                {},
            ),
            ([("Revisar la evolución del RHEED", {"bold": True, "underline": True})], {}),
            (
                [
                    ("Iniciar rampa de Al para pasar a una BEP",),
                    S("Al"),
                    ("= 9x10",),
                    P("-8"),
                    (" Torr en 10 minutos",),
                ],
                {},
            ),
        ],
        fill=band(i),
        margins=(30, 20, 40, 40),
    )
    add_stack(
        table.cell(i, 3),
        [
            (5.5, TEAL, None),
            (22.0, NAVY, "3C-SiC"),
        ],
        fill=band(i),
    )

    # Row 1 — desorción y toques de aluminio
    i = 4
    fill_cell(table.cell(i, 0), [([("1",)], {})], fill=band(i), margins=(50, 20, 20, 20))
    fill_cell(
        table.cell(i, 1),
        [([("Desorción y",)], {}), ([("Toques de Aluminio",)], {})],
        fill=band(i),
        margins=(50, 20, 30, 30),
    )
    fill_cell(
        table.cell(i, 2),
        [
            (
                [
                    B("BEP"),
                    S("Al", bold=True, color=BLUE),
                    B("= 1.5x10"),
                    P("-7", bold=True, color=BLUE),
                    B(" Torr. , T"),
                    S("Al", bold=True, color=BLUE),
                    B("=?°C"),
                ],
                {},
            ),
            (
                [
                    ("Utilizar una rampa hasta T",),
                    S("piro"),
                    ("=850°C en 40 minutos",),
                ],
                {},
            ),
            (
                [
                    ("Observar cuidadosamente el RHEED se busca en lo posible un patrón lineal",),
                    BR,
                    ("brillante",),
                ],
                {},
            ),
            (
                [
                    ("I.    Dar 5 toques de Al de 1 segundo cada toque con T",),
                    S("pir"),
                    ("=800 °C con un tiempo",),
                    BR,
                    ("de desorción de 1 segundo entre cada toque. ",),
                    ("Observar los cambios en la", {"underline": True}),
                    BR,
                    ("intensidad del RHEED", {"underline": True}),
                ],
                {},
            ),
            (
                [
                    ("II. Subir T",),
                    S("sus"),
                    (" a T",),
                    S("pir"),
                    ("=820 °C y dar 5 toques más de Al de 1 segundo cada toque.",),
                ],
                {},
            ),
            (
                [
                    ("III. Subir T",),
                    S("sus"),
                    (" a T",),
                    S("pir"),
                    ("=840 °C y repetir 5 toques de Al.",),
                ],
                {},
            ),
            (
                [
                    ("IV. Subir T",),
                    S("sus"),
                    (" a T",),
                    S("pir"),
                    ("=850 °C y repetir 5 toques de Al.",),
                ],
                {},
            ),
            (
                [
                    ("V. Ir subiendo 10 °C y repetir toques de Al, esperar 5 min al llegar a la",),
                    BR,
                    ("temperatura",),
                ],
                {},
            ),
            (
                [
                    ("VI. Iniciar rampa para el sustrato de T",),
                    S("pir"),
                    ("=850°C a T",),
                    S("pir"),
                    ("=720°C en 10 minutos",),
                ],
                {},
            ),
        ],
        fill=band(i),
        margins=(40, 30, 40, 40),
    )
    fill_cell(table.cell(i, 3), [], fill=band(i), margins=(0, 0, 0, 0))

    # Row 0 — preparación del sustrato
    i = 5
    fill_cell(
        table.cell(i, 0),
        [([("0",)], {})],
        fill=band(i),
        valign_="center",
        margins=(20, 20, 20, 20),
    )
    fill_cell(
        table.cell(i, 1),
        [([("Preparación del",)], {}), ([("sustrato",)], {})],
        fill=band(i),
        margins=(40, 20, 30, 30),
    )
    fill_cell(
        table.cell(i, 2),
        [
            ([("Sustrato SiC (100)",)], {}),
            (
                [
                    ("1. Desengrasado con Xileno, Acetona e Isopropanol (en ese orden) con 10",),
                    BR,
                    ("minutos en cada solvente en baño ultrasónico",),
                ],
                {"align": "left"},
            ),
            (
                [
                    ("2. Enjuague con agua DI por 5 minutos en baño ultrasónico al terminar el",),
                    BR,
                    ("tratamiento con isopropanol",),
                ],
                {"align": "left"},
            ),
            (
                [
                    ("3. Ataque químico con Buffered Oxide Etchant (BOE) 10:1 en intervalos de 30",),
                    BR,
                    ("segundos examinando se alcance la condición hidrofóbica. Se tiene como",),
                    BR,
                    ("referencia 3 minutos de exposición, pero con posibilidad a tiempos mayores",),
                ],
                {"align": "left"},
            ),
            ([("4. Enjuague con agua DI por 5 minutos en baño ultrasónico",)], {"align": "left"}),
            ([("5. Secado con nitrógeno",)], {"align": "left"}),
        ],
        fill=band(i),
        margins=(30, 20, 40, 40),
    )
    fill_cell(table.cell(i, 3), [], fill=band(i), margins=(0, 0, 0, 0))

    props = doc.core_properties
    props.title = "CRECIMIENTO 966"
    props.subject = "Crecimiento de AlN cúbico sobre sustratos de SiC(100), 100 nm"
    props.category = "Receta de crecimiento"
    props.author = "Lizette Zebadua"

    doc.save(OUT)
    print()
    print("Documento Word guardado en:")
    print(OUT)
    print()
    abrir_documento(OUT)


def _rfonts_style(style):
    rPr = style.element.get_or_add_rPr()
    rFonts = rPr.find(qn("w:rFonts"))
    if rFonts is None:
        rFonts = OxmlElement("w:rFonts")
        rPr.append(rFonts)
    for attr in ("w:ascii", "w:hAnsi", "w:cs", "w:eastAsia"):
        rFonts.set(qn(attr), "Arial")


def abrir_documento(path):
    """Abre el .docx con Word o la app predeterminada, si hay escritorio."""
    try:
        if sys.platform == "win32":
            os.startfile(path)  # noqa: S606 — el usuario pidió ver el documento
            return
        if sys.platform == "darwin":
            comando = ["open", str(path)]
        else:
            if not os.environ.get("DISPLAY") and not os.environ.get("WAYLAND_DISPLAY"):
                return
            comando = ["xdg-open", str(path)]
        subprocess.Popen(comando, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    except OSError as exc:
        print(f"No pude abrirlo automáticamente ({exc}). Ábrelo desde la ruta de arriba.")


if __name__ == "__main__":
    build()
