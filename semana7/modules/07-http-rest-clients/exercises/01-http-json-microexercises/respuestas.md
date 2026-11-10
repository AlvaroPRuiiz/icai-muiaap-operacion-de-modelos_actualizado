# Respuestas

## 1. Tres formas de pedir una predicción

| Caso | ¿Sale del proceso Python? | ¿Usa HTTP? | ¿La ruta nombra una acción o un recurso? |
| --- | --- | --- | --- |
| A: `infer_measurements(payload)` | No | No | No hay ruta; es una llamada local. |
| B: `POST /runPumpModel` | Sí | Sí | Acción. |
| C: `POST /v1/predictions` | Sí | Sí | Recurso. |

## 2. URL, path y query

`http://127.0.0.1:8000/v1/predictions/pred-42?include=explanation&limit=1`

| Componente | Valor |
| --- | --- |
| Scheme | `http` |
| Host | `127.0.0.1` |
| Port | `8000` |
| Path | `/v1/predictions/pred-42` |
| Query: `include` | `explanation` |
| Query: `limit` | `1` |

El identificador `pred-42` va en el path; el límite, en la query (`limit=1`); las cuatro medidas de una bomba, en el body JSON de la petición de creación, fuera de la URL.

## 3. JSON y Python

```json
{"machine_id": "pump-017", "ready": true, "comment": null, "axes": [1, 2]}
```

`True` pasa a `true`, `None` a `null` y la tupla `(1, 2)` al array `[1, 2]`. Validado con `json.loads()`: devuelve un diccionario con `ready` igual a `True`, `comment` igual a `None` y `axes` igual a `[1, 2]`.

## 4. Cuatro estados HTTP esenciales

| Caso | Código | Razón |
| --- | --- | --- |
| Predicción correcta y devuelta | `200` | La petición se ha procesado correctamente y devuelve la predicción. |
| Texto truncado o que no es JSON | `400` | El cuerpo no tiene una sintaxis JSON válida. |
| JSON válido, pero `vibration_mm_s` es la cadena `"alta"` | `422` | El JSON es válido, pero el valor no cumple el tipo numérico requerido. |
| Petición correcta, pero el modelo no está disponible temporalmente | `503` | El servicio no puede atender la petición por una indisponibilidad temporal del modelo. |

## 5. Crear y consultar una predicción

```text
Crear una predicción:    POST /v1/predictions
Consultar la predicción: GET /v1/predictions/pred-42
```

Las mediciones van en el body JSON de `POST`; `pred-42` va en el path de `GET`.

| Operación | ¿Segura? | ¿Idempotente? |
| --- | --- | --- |
| Crear (`POST`) | No: crea un recurso y cambia el estado. | No se garantiza: repetirla puede crear dos predicciones distintas. |
| Consultar (`GET`) | Sí: solo lee la predicción. | Sí: repetirla tiene el mismo efecto esperado, sin cambiar el estado del servidor. |
