# Incorporación de In en pozos cúbicos InGaN

Modelo cinético, monocapa a monocapa, de la incorporación de indio en pozos
InGaN/GaN de zincblenda crecidos en [001]. Contrasta las tres regiones de
temperatura vistas en MME914, MME925, MME930 y MME931.

```bash
python main.py
python -m unittest tests/test_growth.py
```

Salidas:

- `figures/tres_regiones.png` — un pozo de cada región, alineado en el borde inferior
- `figures/perfiles_sims.png` — los tres pozos, con un desenfoque SIMS ilustrativo y el In/N de cráter
- `figures/balance_indio.png` — fracción del In que queda en el pozo, en la cola o se desorbe
- `figures/tendencia_temperatura.png` — x máximo y longitud de segregación
- `data/processed/resumen.csv`, `data/processed/perfiles.csv`

La lectura de los resultados está en `drafts/regiones_de_crecimiento.md`.
Las condiciones de crecimiento y las reservas sobre las fuentes están en `agents.md`.
