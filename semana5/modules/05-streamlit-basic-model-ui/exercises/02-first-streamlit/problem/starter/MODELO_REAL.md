# Ejecuci?n con el modelo original

Desde la ra?z del repositorio, en PowerShell:

```powershell
& ./semana5/modules/05-streamlit-basic-model-ui/exercises/02-first-streamlit/problem/starter/run-local.ps1
```

El lanzador configura `MODEL_UI_BUNDLE` para la sesi?n y arranca Streamlit
con uv. Calcula la ruta desde su propia ubicaci?n; no contiene rutas personales.
Requiere acceso a las dependencias de Streamlit si todav?a no est?n instaladas.
El gateway utiliza el ejercicio de S4, no la soluci?n del profesor.

## Artefacto y procedencia

Original recuperado del profesor y confirmado como fuente de confianza por el usuario.
SHA-256 del original y de la copia:
`55423a4af32faf2f27f9899db6bb04e181e9093b2d5ffc1d4c0923784cb6ec83`.

En el starter de S4 se conserva `models/wine_quality_classifier.joblib` y se
crea `models/wine_quality_bundle/{manifest.json,model.joblib}` mediante
`create_manifest(estimator, original["model_version"])` y `save_model_bundle`.
No se reentrena ni se sustituye el estimador. Los binarios est?n ignorados por Git.

- Estimador: `RandomForestClassifier`, once entradas.
- Versi?n del original: `wine-quality-rf-v1`.
- Preprocesado declarado en S4: `wine-red-features-v1`.
- Esquema declarado en S4: `wine-quality-bundle-v1`.
- Las once caracter?sticas del original coinciden, incluido su orden, con S4 y S5.
- Las clases del estimador coinciden con las etiquetas del contrato. Su orden
  interno es el de `classes_`; la inferencia obtiene la confianza con el m?ximo
  de probabilidades, sin reasignar columnas al orden de `output_labels`.

## Verificaci?n realizada

Carga del bundle con S4 y carga/inferencia mediante `app.build_gateway()` de S5.
Con los valores predeterminados de `FIELD_SPECS`, resultado:

```json
{"quality_band":"needs_review","confidence":0.8637529232968751,"model_version":"wine-quality-rf-v1","preprocessing_version":"wine-red-features-v1"}
```

En el starter de S5: 27 tests pasan; `ruff check app.py src tests` y
`ruff format --check app.py src tests` correctos (13 archivos).
La comprobaci?n automatizada valida carga e inferencia; la navegaci?n manual
por Streamlit queda pendiente.
