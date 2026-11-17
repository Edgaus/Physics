"""Delegates lazy imports to runtimes with native support."""

from __future__ import annotations

import contextlib
import types

TYPE_CHECKING = False
if TYPE_CHECKING:
    from typing import Any


def lazy_importer() -> contextlib.AbstractContextManager[None]:
    """Returns a context that leaves imports unchanged.

    The importing module's __lazy_modules__ declaration and interpreter policy
    determine which imports are lazy.
    """
    return contextlib.nullcontext()


def resolve(value: Any, /) -> Any:
    """Resolves a native lazy import, returning ordinary objects unchanged."""
    native_type = getattr(types, "LazyImportType", None)
    if native_type is not None and type(value) is native_type:
        return value.resolve()
    return value
