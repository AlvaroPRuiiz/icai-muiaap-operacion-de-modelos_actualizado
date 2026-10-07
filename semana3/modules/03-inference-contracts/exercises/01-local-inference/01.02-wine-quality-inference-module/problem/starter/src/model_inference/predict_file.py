"""TODO: script CLI que encadena contratos, preprocesado e inferencia."""

# Implementa el comando:
# python -m model_inference.predict_file --input <csv> --output <csv>
# No dejes un archivo de salida parcial si alguna fila es inválida.
"""Inferencia sobre un fichero CSV."""

import argparse
import csv
from pathlib import Path

from pydantic import ValidationError

from model_inference.contracts import WineQualityPrediction, WineQualityRequest
from model_inference.inference import (
    DEFAULT_MODEL_PATH,
    infer_wine_quality,
    load_wine_quality_model,
)
from model_inference.preprocess import (
    PREPROCESSING_VERSION,
    preprocess_wine_request,
)


OUTPUT_FIELDS = (
    "sample_id",
    "quality_band",
    "confidence",
    "model_version",
    "preprocessing_version",
)


def predict_file(
    input_path: Path,
    output_path: Path,
    model_path: Path,
) -> int:

    model = load_wine_quality_model(model_path)
    predictions = []

    with input_path.open(newline="", encoding="utf-8") as source:
        rows = csv.DictReader(source)

        if not rows.fieldnames or "sample_id" not in rows.fieldnames:
            raise ValueError("El CSV debe incluir sample_id")

        for row in rows:
            sample_id = row.pop("sample_id")

            if not sample_id or not sample_id.strip():
                raise ValueError("sample_id vacío")

            try:
                request = WineQualityRequest.model_validate(row)
            except ValidationError as error:
                raise ValueError(
                    f"Muestra {sample_id} inválida: {error}"
                ) from error

            features = preprocess_wine_request(request)

            quality_band, confidence = infer_wine_quality(
                model,
                features,
            )

            prediction = WineQualityPrediction(
                quality_band=quality_band,
                confidence=confidence,
                model_version=model.model_version,
                preprocessing_version=PREPROCESSING_VERSION,
            )

            predictions.append(
                {
                    "sample_id": sample_id,
                    **prediction.model_dump(),
                }
            )

    output_path.parent.mkdir(parents=True, exist_ok=True)

    with output_path.open("w", newline="", encoding="utf-8") as target:
        writer = csv.DictWriter(
            target,
            fieldnames=OUTPUT_FIELDS,
        )
        writer.writeheader()
        writer.writerows(predictions)

    return len(predictions)


def main() -> int:

    parser = argparse.ArgumentParser()

    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--model", default=DEFAULT_MODEL_PATH, type=Path)

    args = parser.parse_args()

    try:
        count = predict_file(
            input_path=args.input,
            output_path=args.output,
            model_path=args.model,
        )
    except (FileNotFoundError, ValueError) as error:
        parser.error(str(error))

    print(f"Predicciones escritas: {count}")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())