# env-demo

Proyecto reproducible con `uv` y configuración mediante `APP_ENV`.

##Instalación

```bash
uv sync --locked

##Ejecución
APP_ENV=dev uv run python -m env_demo.main
APP_ENV=pre uv run python -m env_demo.main
APP_ENV=pro uv run python -m env_demo.main

##Comprobación
uv run pytest
uv run ruff check .
