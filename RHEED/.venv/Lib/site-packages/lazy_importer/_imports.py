"""Implements deferred imports using documented Python protocols."""

from __future__ import annotations

import builtins
import contextlib
import importlib.util
import operator
import threading
import types

# Type checkers recognize this flag without importing typing at runtime.
TYPE_CHECKING = False
if TYPE_CHECKING:
    from collections.abc import Callable, Generator, Mapping, Sequence
    from typing import Any, Final


class _Request:
    __slots__ = ("name", "namespace", "fromlist", "attribute", "path")

    name: str
    namespace: dict[str, Any]
    fromlist: tuple[str, ...]
    attribute: str | None
    path: tuple[str, ...]

    def __init__(
        self,
        name: str,
        namespace: dict[str, Any],
        fromlist: tuple[str, ...],
        attribute: str | None = None,
        path: tuple[str, ...] = (),
    ) -> None:
        object.__setattr__(self, "name", name)
        object.__setattr__(self, "namespace", namespace)
        object.__setattr__(self, "fromlist", fromlist)
        object.__setattr__(self, "attribute", attribute)
        object.__setattr__(self, "path", path)

    def __setattr__(self, name: str, value: Any) -> None:
        raise AttributeError("request is immutable")

    def __delattr__(self, name: str) -> None:
        raise AttributeError("request is immutable")

    def load(self) -> Any:
        with _HOOK.suspended():
            module = builtins.__import__(
                self.name, self.namespace, self.namespace, self.fromlist, 0
            )
            if self.attribute is not None:
                try:
                    return getattr(module, self.attribute)
                except AttributeError as exc:
                    raise ImportError(
                        f"cannot import name {self.attribute!r} "
                        f"from {module.__name__!r}"
                    ) from exc
            for component in self.path:
                module = getattr(module, component)
            return module


class _Proxy:
    def __init__(self, request: _Request) -> None:
        object.__setattr__(self, "_request", request)
        object.__setattr__(self, "_children", {})
        object.__setattr__(self, "_namespaces", [request.namespace])
        object.__setattr__(self, "_lock", threading.RLock())
        object.__setattr__(self, "_resolved", ())
        object.__setattr__(self, "_resolving", threading.local())

    def _resolve(self) -> Any:
        resolved = object.__getattribute__(self, "_resolved")
        if resolved:
            return resolved[0]
        resolving = object.__getattribute__(self, "_resolving")
        request = object.__getattribute__(self, "_request")
        if getattr(resolving, "active", False):
            raise ImportError(f"circular lazy import of {request.name!r}")
        resolving.active = True
        try:
            value = request.load()
        finally:
            resolving.active = False
        # Never hold a proxy lock while running import hooks or module code:
        # another thread importing that module may need this same proxy.
        with object.__getattribute__(self, "_lock"):
            resolved = object.__getattribute__(self, "_resolved")
            if resolved:
                return resolved[0]
            object.__setattr__(self, "_resolved", (value,))
            if isinstance(value, types.ModuleType):
                for name, child in object.__getattribute__(self, "_children").items():
                    if name not in vars(value):
                        vars(value)[name] = child
                        object.__getattribute__(child, "_namespaces").append(
                            vars(value)
                        )
            for namespace in object.__getattribute__(self, "_namespaces"):
                for name, binding in tuple(namespace.items()):
                    if binding is self and namespace.get(name) is self:
                        namespace[name] = value
        return value

    def __getattribute__(self, name: str) -> Any:
        if name == "__mro_entries__":
            return object.__getattribute__(self, name)
        resolved = object.__getattribute__(self, "_resolved")
        if resolved:
            return getattr(resolved[0], name)
        children = object.__getattribute__(self, "_children")
        if name in children:
            return children[name]
        return getattr(_Proxy._resolve(self), name)

    def __setattr__(self, name: str, value: Any) -> None:
        setattr(_Proxy._resolve(self), name, value)

    def __delattr__(self, name: str) -> None:
        delattr(_Proxy._resolve(self), name)

    def __call__(self, *args: Any, **kwargs: Any) -> Any:
        target = _Proxy._resolve(self)
        args = tuple(resolve(arg) for arg in args)
        kwargs = {name: resolve(value) for name, value in kwargs.items()}
        return target(*args, **kwargs)

    def __mro_entries__(self, bases: tuple[type, ...]) -> tuple[type, ...]:
        return (_Proxy._resolve(self),)


# Special methods are looked up on the type, bypassing __getattribute__.
# Keep the supported protocol surface explicit, including reflected operators.
_PROTOCOLS: Final = (
    "repr",
    "str",
    "bytes",
    "format",
    "bool",
    "hash",
    "len",
    "iter",
    "next",
    "reversed",
    "contains",
    "getitem",
    "setitem",
    "delitem",
    "enter",
    "exit",
    "await",
    "aiter",
    "anext",
    "aenter",
    "aexit",
    "int",
    "float",
    "complex",
    "index",
    "round",
    "trunc",
    "floor",
    "ceil",
    "neg",
    "pos",
    "abs",
    "invert",
    "lt",
    "le",
    "eq",
    "ne",
    "gt",
    "ge",
    "add",
    "sub",
    "mul",
    "matmul",
    "truediv",
    "floordiv",
    "mod",
    "divmod",
    "pow",
    "lshift",
    "rshift",
    "and",
    "xor",
    "or",
    "radd",
    "rsub",
    "rmul",
    "rmatmul",
    "rtruediv",
    "rfloordiv",
    "rmod",
    "rdivmod",
    "rpow",
    "rlshift",
    "rrshift",
    "rand",
    "rxor",
    "ror",
    "iadd",
    "isub",
    "imul",
    "imatmul",
    "itruediv",
    "ifloordiv",
    "imod",
    "ipow",
    "ilshift",
    "irshift",
    "iand",
    "ixor",
    "ior",
)


_OPERATIONS: Final[Mapping[str, Callable[..., Any]]] = {
    "__bool__": bool,
    "__str__": str,
    "__repr__": repr,
    "__bytes__": bytes,
    "__format__": format,
    "__hash__": hash,
    "__len__": len,
    "__iter__": iter,
    "__next__": next,
    "__reversed__": reversed,
    "__int__": int,
    "__float__": float,
    "__complex__": complex,
    "__round__": round,
    "__abs__": abs,
    "__contains__": operator.contains,
    "__pow__": pow,
    "__divmod__": divmod,
}


_REFLECTED: Final[Mapping[str, str]] = {
    f"__r{name}__": f"__{name}__"
    for name in (
        "add",
        "sub",
        "mul",
        "matmul",
        "truediv",
        "floordiv",
        "mod",
        "divmod",
        "pow",
        "lshift",
        "rshift",
        "and",
        "xor",
        "or",
    )
}


def _forward(method: str) -> Callable[..., Any]:
    def operation(self: _Proxy, *args: Any, **kwargs: Any) -> Any:
        value = _Proxy._resolve(self)
        args = tuple(resolve(arg) for arg in args)
        operation = _OPERATIONS.get(method)
        if operation is not None:
            return operation(value, *args, **kwargs)
        operation = getattr(operator, method, None)
        if operation is not None:
            return operation(value, *args, **kwargs)
        if method in _REFLECTED:
            operation = _OPERATIONS.get(_REFLECTED[method])
            if operation is None:
                operation = getattr(operator, _REFLECTED[method])
            return operation(args[0], value, *args[1:], **kwargs)
        return getattr(type(value), method)(value, *args, **kwargs)

    return operation


for _protocol in _PROTOCOLS:
    setattr(_Proxy, f"__{_protocol}__", _forward(f"__{_protocol}__"))


def resolve(value: Any, /) -> Any:
    """Returns the imported object, or the argument if it isn't a lazy proxy.

    Resolves fallback proxies explicitly for identity checks, type checks and
    APIs that require concrete objects. Failed imports can be retried.
    """
    if type(value) is _Proxy:
        return _Proxy._resolve(value)
    return value


class _FromImport:
    def __init__(self, request: _Request) -> None:
        self._request = request

    def __getattribute__(self, name: str) -> _Proxy:
        request = object.__getattribute__(self, "_request")
        return _Proxy(
            _Request(
                request.name,
                request.namespace,
                (name,),
                attribute=name,
                path=request.path,
            )
        )


class _ThreadState(threading.local):
    def __init__(self) -> None:
        self.depth = 0
        self.suspensions = 0


class _ImportHook:
    def __init__(self) -> None:
        self._lock = threading.RLock()
        self._state = _ThreadState()
        self._users = 0
        self._previous: Callable[..., Any] = builtins.__import__
        # Store the bound method so installation and restoration use identity.
        self._callback = self._import

    @contextlib.contextmanager
    def suspended(self) -> Generator[None, None, None]:
        self._state.suspensions += 1
        try:
            yield
        finally:
            self._state.suspensions -= 1

    @contextlib.contextmanager
    def activate(self) -> Generator[None, None, None]:
        with self._lock:
            if self._users == 0:
                self._previous = builtins.__import__
                vars(builtins)["__import__"] = self._callback
            self._users += 1
        self._state.depth += 1
        try:
            yield
        finally:
            self._state.depth -= 1
            with self._lock:
                self._users -= 1
                if self._users == 0 and builtins.__import__ is self._callback:
                    builtins.__import__ = self._previous

    def _import(
        self,
        name: str,
        globals: dict[str, Any] | None = None,
        locals: Mapping[str, Any] | None = None,
        fromlist: Sequence[str] | None = (),
        level: int = 0,
    ) -> Any:
        state = self._state
        if (
            state.depth
            and not state.suspensions
            and globals is not None
            and "*" not in (fromlist or ())
            and name != "__future__"
        ):
            absolute = name
            if level:
                package = globals.get("__package__")
                if package is None:
                    spec = globals.get("__spec__")
                    if spec is not None:
                        package = spec.parent
                    else:
                        package = globals.get("__name__", "")
                        if "__path__" not in globals:
                            package = package.rpartition(".")[0]
                absolute = importlib.util.resolve_name("." * level + name, package)
            # Membership may run user code that imports its own dependencies.
            with self.suspended():
                selected = absolute in globals.get("__lazy_modules__", ())
            if selected:
                request = _Request(absolute, globals, tuple(fromlist or ()))
                if fromlist:
                    return _FromImport(request)
                existing = globals.get(name.partition(".")[0])
                root = _Proxy(request)
                if type(existing) is _Proxy:
                    object.__getattribute__(root, "_children").update(
                        object.__getattribute__(existing, "_children")
                    )
                parent = root
                components = name.split(".")
                for index, component in enumerate(components[1:], 1):
                    children = object.__getattribute__(parent, "_children")
                    child = _Proxy(
                        _Request(
                            request.name,
                            request.namespace,
                            request.fromlist,
                            attribute=request.attribute,
                            path=tuple(components[1 : index + 1]),
                        )
                    )
                    if component in children:
                        object.__getattribute__(child, "_children").update(
                            object.__getattribute__(children[component], "_children")
                        )
                    object.__getattribute__(parent, "_children")[component] = child
                    parent = child
                return root
        with self.suspended():
            return self._previous(name, globals, locals, fromlist, level)


_HOOK: Final = _ImportHook()


def lazy_importer() -> contextlib.AbstractContextManager[None]:
    """Returns a context that enables the importing module's __lazy_modules__.

    Each import checks membership in its module's current declaration. The
    fallback context is single-use and applies to imports on the current thread.
    Module-level blocks containing only imports avoid differences from native
    lazy imports described in the README.
    """
    return _HOOK.activate()
