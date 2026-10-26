"""Punto de extensión del CLI de inferencia sobre un bundle."""

from __future__ import annotations

import argparse
import csv
from pathlib import Path

from pydantic import ValidationError

from model_packaging.artifact import (
    DEFAULT_BUNDLE_PATH,
    infer_wine_quality,
    load_model_bundle,
)
from model_packaging.contracts import WineQualityRequest
from model_packaging.preprocess import FEATURE_NAMES


def predict_file(
    input_path: Path,
    output_path: Path,
    bundle_path: Path,
) -> int:
    """Valida todas las filas y escribe el CSV solo al final."""

    # Cargar el modelo
    bundle = load_model_bundle(bundle_path)
    predicciones = []

    # Leer el CSV
    with input_path.open("r", newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        expected_columns = ("sample_id", *FEATURE_NAMES)

        if not reader.fieldnames:
            raise ValueError("El CSV está vacío")

        if sorted(reader.fieldnames) != sorted(expected_columns):
            raise ValueError("El CSV tiene columnas inesperadas")

        # Validar y predecir todas las filas
        for fila in reader:
            if None in fila:
                raise ValueError("El CSV contiene valores adicionales")

            sample_id = fila.pop("sample_id", None)

            if not sample_id or not sample_id.strip():
                raise ValueError("El sample_id está vacío")

            try:
                request = WineQualityRequest(**fila)
                prediccion = infer_wine_quality(bundle, request)

                predicciones.append(
                    {
                        "sample_id": sample_id.strip(),
                        **prediccion.model_dump(),
                    }
                )

            except ValidationError as e:
                raise ValueError(
                    f"Error de validación en el ID {sample_id}: {e}"
                ) from e

    # Crear la carpeta de salida
    output_path.parent.mkdir(parents=True, exist_ok=True)

    # Escribir el CSV después de validar todas las filas
    with output_path.open("w", newline="", encoding="utf-8") as out_file:
        writer = csv.DictWriter(
            out_file,
            fieldnames=[
                "sample_id",
                "quality_band",
                "confidence",
                "model_version",
                "preprocessing_version",
            ],
        )

        writer.writeheader()
        writer.writerows(predicciones)

    return len(predicciones)


def parse_args() -> argparse.Namespace:
    """Declara la interfaz del comando público."""

    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--bundle", default=DEFAULT_BUNDLE_PATH, type=Path)
    return parser.parse_args()


if __name__ == "__main__":
    arguments = parse_args()
    raise SystemExit(
        predict_file(
            input_path=arguments.input,
            output_path=arguments.output,
            bundle_path=arguments.bundle,
        )
    )
