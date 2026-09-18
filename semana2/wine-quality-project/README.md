# Wine Quality

Proyecto reproducible para entrenar y validar el modelo de calidad del vino.

Desde la ra?z del fork:

```powershell
cd semana2/wine-quality-project
uv sync --locked
uv run --frozen python -m wine_quality.train
uv run --frozen pytest
uv run --frozen ruff check .
```

El dataset se encuentra en `data/raw`, el paquete en `src/wine_quality` y las
pruebas en `tests`.
