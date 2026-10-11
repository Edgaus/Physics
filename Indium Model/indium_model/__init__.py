"""Registro de crecimiento de InGaN cúbico (MME914, MME925, MME930, MME931).

Los números salen de ``agents.md``. Hay tres fuentes y cada módulo guarda
solo una:

- ``article`` — borrador del artículo
- ``plans`` — recetas 913-914 y 932
- ``bitacora`` — fotos de la libreta

El plan 932 no es ninguna de las cuatro muestras.
"""

from indium_model.article import ARTICLE_TITLE, GROWTH_PARAGRAPH, SAMPLES
from indium_model.bitacora import NOTEBOOKS
from indium_model.plans import PLAN_913_914, PLAN_932

__all__ = [
    "ARTICLE_TITLE",
    "GROWTH_PARAGRAPH",
    "NOTEBOOKS",
    "PLAN_913_914",
    "PLAN_932",
    "SAMPLES",
]
