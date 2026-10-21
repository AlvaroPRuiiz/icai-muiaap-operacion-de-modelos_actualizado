# Starter — Módulo local de inferencia de vino

Este es el único proyecto de código que recibe el alumnado. Implementad los
`TODO` siguiendo el orden del `../readme.md` y haced pasar las pruebas sin mirar
la solución del profesorado.

El profesor colocará `wine_quality_classifier.joblib` dentro de `models/` antes
del taller. El modelo ya está entrenado: no hay que modificarlo ni reentrenarlo.

## Nota técnica — Semana 3.2

Responsabilidad de cada módulo:

- `contracts.py`: validar las características de entrada y la categoría, confianza y versiones de salida con Pydantic.
- `preprocess.py`: transformar la petición validada en las 11 características ordenadas mediante `FEATURE_NAMES`, con una versión explícita de preprocesado.
- `inference.py`: cargar el artefacto ya entrenado, comprobar su compatibilidad y ejecutar `predict` y `predict_proba`.
- `predict_file.py`: orquestar la lectura del CSV, separar `sample_id`, validar, preprocesar, inferir y escribir las predicciones.

Dos decisiones de diseño:

1. **Validar en la frontera y fijar el orden interno.** Uso Pydantic para rechazar campos extra y valores fuera de rango; después, una `dataclass` representa las características ya validadas. `FEATURE_NAMES` fija el orden y se contrasta con el artefacto para evitar predicciones con columnas intercambiadas. `sample_id` solo acompaña la respuesta.
2. **Escribir después de procesar todas las filas.** Acumulo las predicciones en memoria y abro el fichero de salida al final. Así, una fila inválida interrumpe el proceso sin crear un CSV parcial. Para este CSV pequeño prima la sencillez; un lote grande requeriría otra estrategia de memoria y escritura.
