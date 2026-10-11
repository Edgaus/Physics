"""Registro de las cuatro muestras de InGaN cúbico.

Las fuentes no se mezclan. ``tabla`` escribe el Word solo con el borrador.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

from generate_tabla import DEFAULT_OUTPUT, write_docx
from indium_model.checks import section_5
from indium_model.report import afirmar, comparar, informe


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Condiciones de crecimiento de InGaN cúbico, con las tres fuentes separadas."
    )
    sub = parser.add_subparsers(dest="command")
    sub.add_parser("informe", help="Muestra el borrador, los dos planes y la bitácora.")
    sub.add_parser("comparar", help="Pone el artículo junto a la bitácora, sin fusionarlos.")
    sub.add_parser("afirmar", help="Evalúa las afirmaciones que el registro sí sostiene.")
    tabla = sub.add_parser("tabla", help="Regenera el Word solo con el borrador.")
    tabla.add_argument("-o", "--output", type=Path, default=DEFAULT_OUTPUT)
    args = parser.parse_args(argv)
    command = args.command or "informe"

    if command == "informe":
        print(informe(), end="")
        return 0
    if command == "comparar":
        print(comparar(), end="")
        return 0
    if command == "afirmar":
        print(afirmar(), end="")
        return 0 if all(ok for _, ok in section_5()) else 1
    if command == "tabla":
        path = write_docx(args.output)
        print(path)
        return 0
    return 2


if __name__ == "__main__":
    sys.exit(main())
