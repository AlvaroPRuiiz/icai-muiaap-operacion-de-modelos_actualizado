"""Adaptador del bundle de S4 para la interfaz Wine."""

from __future__ import annotations

import importlib.util
import sys
from collections.abc import Callable, Mapping
from pathlib import Path
from typing import Any, Protocol

from pydantic import ValidationError

from model_ui.contracts import PredictionPayload
from model_ui.errors import ArtifactUnavailableError, InputContractError

FEATURE_NAMES = (
    "fixed_acidity",
    "volatile_acidity",
    "citric_acid",
    "residual_sugar",
    "chlorides",
    "free_sulfur_dioxide",
    "total_sulfur_dioxide",
    "density",
    "ph",
    "sulphates",
    "alcohol",
)


class InferenceGateway(Protocol):
    """Frontera que usa la UI sin conocer el modelo."""

    def predict(self, values: Mapping[str, object]) -> PredictionPayload:
        """Valida una muestra y devuelve una predicción."""


def _validate_feature_names(values: Mapping[str, object]) -> None:
    """Rechaza campos ausentes o desconocidos antes de delegar en S4."""

    missing = [name for name in FEATURE_NAMES if name not in values]
    unknown = [name for name in values if name not in FEATURE_NAMES]
    if missing or unknown:
        details = []
        if missing:
            details.append(f"faltan: {', '.join(missing)}")
        if unknown:
            details.append(f"no permitidos: {', '.join(unknown)}")
        raise InputContractError(
            "La muestra no cumple el contrato: " + "; ".join(details)
        )


class PackagedBundleGateway:
    """Adaptador del contrato de S4 a la interfaz de S5."""

    def __init__(
        self,
        bundle: Any,
        request_model: Any,
        infer_function: Callable[[Any, Any], Any],
    ) -> None:
        self._bundle = bundle
        self._request_model = request_model
        self._infer_function = infer_function

    @classmethod
    def from_bundle_path(cls, bundle_path: Path) -> PackagedBundleGateway:
        """Carga S4 sin repetir ``joblib.load`` ni el preprocesado."""

        request_model = _load_wine_quality_request()
        try:
            from model_packaging.artifact import infer_wine_quality, load_model_bundle
        except ModuleNotFoundError:
            _add_s4_source_to_sys_path()
            from model_packaging.artifact import infer_wine_quality, load_model_bundle

        bundle = load_model_bundle(bundle_path)
        return cls(bundle, request_model, infer_wine_quality)

    def predict(self, values: Mapping[str, object]) -> PredictionPayload:
        """Construye el request de S4 y valida la respuesta."""

        _validate_feature_names(values)
        request = _validate_request(self._request_model, values)

        prediction = self._infer_function(self._bundle, request)
        return PredictionPayload.model_validate(prediction.model_dump())


def _validate_request(request_model: Any, values: Mapping[str, object]) -> Any:
    """Aplica el contrato de S4 y traduce su error al vocabulario de la UI."""

    try:
        return request_model.model_validate(dict(values))
    except ValidationError as error:
        raise InputContractError(
            "La muestra no cumple el contrato de entrada."
        ) from error


def _load_wine_quality_request() -> Any:
    """Importa el contrato único de S4."""

    module_name = "_model_ui_s4_contracts"
    module = sys.modules.get(module_name)
    if module is None:
        contract_path = _s4_source_path() / "model_packaging/contracts.py"
        spec = importlib.util.spec_from_file_location(module_name, contract_path)
        if spec is None or spec.loader is None:
            raise ArtifactUnavailableError("No se pudo importar el contrato de S4.")
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        spec.loader.exec_module(module)
    return module.WineQualityRequest


def _add_s4_source_to_sys_path() -> None:
    """Expone el código docente de S4 cuando no está instalado como paquete."""

    source = _s4_source_path()
    if str(source) not in sys.path:
        sys.path.insert(0, str(source))


def _s4_source_path() -> Path:
    """Devuelve la raíz importable de la solución contractual de S4."""

    repository_root = _find_repository_root(Path(__file__))
    return repository_root / (
        "semana4/modules/04-model-packaging/solutions/"
        "01.02-serializable-inference-module/src"
    )


def _find_repository_root(start: Path) -> Path:
    """Localiza el checkout para importar el módulo docente de S4."""

    for parent in (start, *start.parents):
        if (parent / "semana4/modules/04-model-packaging").is_dir():
            return parent
    raise ArtifactUnavailableError("No se encontró el repositorio de la asignatura.")
