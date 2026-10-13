"""Open SPEX DataMax .SPC spectra and write them as text.

Edit the three lines below, then run:

    python open_spc.py

SOURCE_DIR is the folder that contains the .SPC files.
FILE_NAMES is the list of files, separated by spaces. The .SPC extension is optional.
OUTPUT_DIR is the folder where the .txt files are written. It is created if needed.

Paths can be relative to the folder where you run the script, or full paths such as
r"C:\\Users\\Edgar\\Documents\\spc".
"""

import re
import struct
import sys
from pathlib import Path

# Folder that contains the .SPC files.
SOURCE_DIR = r"C:\Users\edgau\OneDrive - CINVESTAV\Documentos\Fernando\739"

# Names of the files to open, separated by spaces.
FILE_NAMES = "739ALNC 739ALNCF 739ALNL 739ALNLF 739ALNLS"

# Folder where the .txt files are written.
OUTPUT_DIR = r"C:\Users\edgau\OneDrive - CINVESTAV\Documentos\Fernando\739"


def field(text, key):
    match = re.search(re.escape(key) + r"=([^\r\n]+)", text)
    return match.group(1).strip() if match else ""


def read_spectrum(path):
    data = path.read_bytes()
    if len(data) < 544:
        raise ValueError(f"{path.name} is too small to be a Galactic SPC spectrum")
    flags, version, _experiment, exponent = struct.unpack_from("<BBBb", data, 0)
    n_points, = struct.unpack_from("<I", data, 4)
    first_x, last_x = struct.unpack_from("<dd", data, 8)
    if version != 0x4B:
        raise ValueError(f"{path.name}: unsupported SPC version {version:#x}")
    if flags & 0x01 or flags & 0x80 or exponent == -128:
        raise ValueError(f"{path.name}: expected evenly spaced integer Y data")
    end = 544 + n_points * 4
    if end > len(data):
        raise ValueError(f"{path.name}: file ends before the {n_points} intensity points")
    raw = struct.unpack_from(f"<{n_points}i", data, 544)
    scale = 2 ** (exponent - 32)
    intensity = [int(round(value * scale)) for value in raw]
    step = (last_x - first_x) / (n_points - 1)
    wavelength = [first_x + i * step for i in range(n_points)]
    text = data.decode("latin1", errors="replace")
    return wavelength, intensity, text


def find_file(folder, name):
    given = Path(name)
    if given.suffix:
        path = folder / given.name
        return path if path.is_file() else None
    for extension in (".SPC", ".spc"):
        path = folder / f"{name}{extension}"
        if path.is_file():
            return path
    return None


def write_text(destination, name, wavelength, intensity, text):
    header = [
        f"# {name}",
        "# Emission spectrum from SPEX / Horiba DataMax, converted from Thermo Galactic SPC.",
        "# X axis: wavelength (nm)",
        "# Y axis: intensity (cps)",
        f"# Excitation position: {field(text, 'Position1')} nm",
        f"# Integration time: {field(text, 'Integration Time')} s",
        (
            f"# Scan: {field(text, 'Start')} to {field(text, 'End')} nm, "
            f"increment {field(text, 'Increment')} nm, {len(wavelength)} points"
        ),
        "Wavelength_nm\tIntensity_cps",
    ]
    rows = [f"{int(x)}\t{y}" for x, y in zip(wavelength, intensity)]
    output = destination / f"{name}.txt"
    output.write_text("\n".join(header + rows) + "\n", encoding="utf-8")
    return output


def main():
    source = Path(SOURCE_DIR)
    destination = Path(OUTPUT_DIR)
    names = [name for name in FILE_NAMES.replace(",", " ").split() if name]
    if not names:
        print("FILE_NAMES is empty. Write the file names on that line.", file=sys.stderr)
        return 1
    if not source.is_dir():
        print(f"SOURCE_DIR does not exist: {source}", file=sys.stderr)
        return 1

    missing = [name for name in names if find_file(source, name) is None]
    if missing:
        print(f"These files were not found in {source}:", file=sys.stderr)
        for name in missing:
            print(f"  {name}", file=sys.stderr)
        return 1

    destination.mkdir(parents=True, exist_ok=True)
    for name in names:
        path = find_file(source, name)
        wavelength, intensity, text = read_spectrum(path)
        stem = Path(name).stem
        output = write_text(destination, stem, wavelength, intensity, text)
        peak = max(intensity)
        peak_nm = int(wavelength[intensity.index(peak)])
        print(f"{path.name} -> {output}  ({len(wavelength)} points, peak {peak} cps at {peak_nm} nm)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
