"""Provides a context manager for opt-in lazy imports."""

import builtins

if hasattr(builtins, "__lazy_import__"):
    from ._native import lazy_importer as lazy_importer
    from ._native import resolve as resolve
else:
    from ._imports import lazy_importer as lazy_importer
    from ._imports import resolve as resolve
