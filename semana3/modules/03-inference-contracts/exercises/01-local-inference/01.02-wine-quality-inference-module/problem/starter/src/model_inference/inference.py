"""TODO: carga del .joblib e inferencia sobre características preparadas."""

# Declara DEFAULT_MODEL_PATH, load_wine_quality_model() e infer_wine_quality().
# Comprueba las características del artefacto antes de llamar al clasificador.

from dataclasses import dataclass
from pathlib import Path

import joblib

from model_inference.preprocess import FEATURE_NAMES, WineFeatures


DEFAULT_MODEL_PATH = Path("models/wine_quality_classifier.joblib")


@dataclass(frozen=True)
class LoadedWineModel:
    estimator: object
    model_version: str


def load_wine_quality_model(
    model_path: Path = DEFAULT_MODEL_PATH,
) -> LoadedWineModel:

    if not model_path.is_file():
        raise FileNotFoundError(
            f"No se encontró el modelo en {model_path}"
        )

    payload = joblib.load(model_path)

    if tuple(payload.get("feature_names", [])) != FEATURE_NAMES:
        raise ValueError(
            "Los feature_names del artefacto no coinciden con el contrato."
        )

    estimator = payload.get("estimator")
    model_version = payload.get("model_version")

    if not hasattr(estimator, "predict") or not hasattr(
        estimator,
        "predict_proba",
    ):
        raise ValueError(
            "El artefacto no contiene un clasificador compatible."
        )

    if not isinstance(model_version, str):
        raise ValueError(
            "El artefacto no declara una versión de modelo válida."
        )

    return LoadedWineModel(
        estimator=estimator,
        model_version=model_version,
    )


def infer_wine_quality(
    model: LoadedWineModel,
    features: WineFeatures,
) -> tuple[str, float]:

    vector = [features.as_vector()]

    quality_band = model.estimator.predict(vector)[0]

    confidence = max(
        model.estimator.predict_proba(vector)[0]
    )

    return str(quality_band), round(float(confidence), 2)