"""Puntos de extensión del taller de serialización."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

import joblib
from pydantic import BaseModel, ConfigDict, Field, field_validator

from model_packaging.contracts import (
    QualityBand,
    WineQualityPrediction,
    WineQualityRequest,
)
from model_packaging.preprocess import (
    FEATURE_NAMES,
    PREPROCESSING_VERSION,
    preprocess_wine_request,
)

ARTIFACT_SCHEMA_VERSION = "wine-quality-bundle-v1"
DEFAULT_BUNDLE_PATH = Path("models/wine_quality_bundle")
MANIFEST_FILENAME = "manifest.json"
MODEL_FILENAME = "model.joblib"
OUTPUT_LABELS: tuple[QualityBand, ...] = (
    "needs_review",
    "acceptable",
    "excellent",
)


class WineQualityEstimator(Protocol):
    """Interfaz mínima que debe cumplir el estimador cargado."""

    def predict(self, features: list[list[float]]) -> Sequence[str]:
        """Devuelve una etiqueta por fila."""

    def predict_proba(self, features: list[list[float]]) -> Sequence[Sequence[float]]:
        """Devuelve probabilidades por fila."""


class ArtifactManifest(BaseModel):
    """TODO: declara y valida los metadatos del bundle."""

    model_config = ConfigDict(extra="forbid")

    schema_version: str
    model_version: str = Field(min_length=1)
    preprocessing_version: str
    feature_names: tuple[str, ...]
    output_labels: tuple[QualityBand, ...]
    estimator_type: str = Field(min_length=1)

    @field_validator("schema_version")  # toda funcion que llames despues de @
    # entonces se ejecuta esa funcion asociada antes de la otra.
    # Los decoradores son de pydantic, son funciones q no hacen falta importar
    @classmethod
    def validate_schema_version(cls, value: str) -> str:
        if value != ARTIFACT_SCHEMA_VERSION:
            raise ValueError("Versión del esquema incompatible")
        return value

    @field_validator("preprocessing_version")
    @classmethod
    def validate_preprocessing_version(cls, value: str) -> str:
        if value != PREPROCESSING_VERSION:
            raise ValueError("Versión de preprocesado incorrecto")
        return value

    @field_validator("feature_names")
    @classmethod
    def validate_feature_names(cls, value: tuple[str, ...]) -> tuple[str, ...]:

        if value != FEATURE_NAMES:
            raise ValueError("Orden de características incompatible")

        return value

    @field_validator("output_labels")
    @classmethod
    def validate_output_labels(
        cls, value: tuple[QualityBand, ...]
    ) -> tuple[QualityBand, ...]:

        if value != OUTPUT_LABELS:
            raise ValueError("Etiquetas de salida incompatibles")

        return value


@dataclass(frozen=True)
class LoadedModelBundle:
    """Bundle cargado; no modificar esta interfaz pública."""

    estimator: WineQualityEstimator
    manifest: ArtifactManifest


def create_manifest(
    estimator: WineQualityEstimator, model_version: str
) -> ArtifactManifest:
    """TODO: devuelve un manifiesto compatible con el contrato."""
    # Comprobar que el estimador tiene los métodos necesarios.
    if not callable(getattr(estimator, "predict", None)) or not callable(
        getattr(estimator, "predict_proba", None)
    ):
        raise ValueError("El estimador debe tener predict y predict_proba")

    return ArtifactManifest(
        schema_version=ARTIFACT_SCHEMA_VERSION,
        model_version=model_version,
        preprocessing_version=PREPROCESSING_VERSION,
        feature_names=FEATURE_NAMES,
        output_labels=OUTPUT_LABELS,
        estimator_type=type(estimator).__name__,
    )


def save_model_bundle(
    bundle_path: Path,
    estimator: WineQualityEstimator,
    manifest: ArtifactManifest | None = None,
) -> ArtifactManifest:

    # Comprobar que el estimador tiene los métodos necesarios.
    if not callable(getattr(estimator, "predict", None)):
        raise ValueError("El estimador no tiene predict()")

    if not callable(getattr(estimator, "predict_proba", None)):
        raise ValueError("El estimador no tiene predict_proba()")

    # Crear un manifiesto si no se ha proporcionado.
    if manifest is None:
        manifest = create_manifest(estimator, "unknown")

    # Comprobar que el orden de características es correcto.
    if tuple(manifest.feature_names) != FEATURE_NAMES:
        raise ValueError("Las características del manifiesto no coinciden")

    # Crear el directorio de destino.
    bundle_path.mkdir(parents=True, exist_ok=True)

    # Construir las rutas.
    manifest_path = bundle_path / MANIFEST_FILENAME
    model_path = bundle_path / MODEL_FILENAME

    # Guardar el modelo entrenado.
    joblib.dump({"estimator": estimator}, model_path)

    # Guardar el manifiesto como JSON.
    manifest_path.write_text(
        manifest.model_dump_json(indent=4),
        encoding="utf-8",
    )

    return manifest


def load_model_bundle(bundle_path: Path) -> LoadedModelBundle:
    """TODO: valida el manifiesto antes de cargar el estimador."""

    manifest_path = bundle_path / MANIFEST_FILENAME

    if not manifest_path.is_file():
        raise FileNotFoundError("No existe manifest.json")

    model_path = bundle_path / MODEL_FILENAME

    manifest = ArtifactManifest.model_validate_json(
        manifest_path.read_text(encoding="utf-8")
    )
    if not model_path.is_file():
        raise FileNotFoundError("No existe model.joblib")

    data = joblib.load(model_path)

    if not isinstance(data, dict) or "estimator" not in data:
        raise ValueError("El archivo no contiene un estimador válido")

    estimator = data["estimator"]

    if not callable(getattr(estimator, "predict", None)) or not callable(
        getattr(estimator, "predict_proba", None)
    ):
        raise ValueError("El estimador debe tener predict y predict_proba")

    return LoadedModelBundle(
        estimator=estimator,
        manifest=manifest,
    )


def infer_wine_quality(
    bundle: LoadedModelBundle,
    request: WineQualityRequest,
) -> WineQualityPrediction:
    """TODO: preprocesa, invoca el estimador y valida la respuesta."""

    features = preprocess_wine_request(request)

    X = [features.as_vector()]

    labels = bundle.estimator.predict(X)
    probabilities = bundle.estimator.predict_proba(X)

    if len(labels) != 1 or len(probabilities) != 1:
        raise ValueError("El estimador debe devolver una predicción")

    if len(probabilities[0]) == 0:
        raise ValueError("El estimador no ha devuelto probabilidades")

    quality_band = labels[0]
    confidence = max(probabilities[0])

    return WineQualityPrediction(
        quality_band=quality_band,
        confidence=confidence,
        model_version=bundle.manifest.model_version,
        preprocessing_version=bundle.manifest.preprocessing_version,
    )
