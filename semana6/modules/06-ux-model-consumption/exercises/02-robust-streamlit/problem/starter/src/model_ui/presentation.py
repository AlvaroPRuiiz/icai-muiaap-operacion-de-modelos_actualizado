"""TODOs de la vista UX: copy de salida y traducción de errores."""

from __future__ import annotations

from model_ui.contracts import PredictionPayload, PredictionView, UserFacingError
from model_ui.errors import (
    ArtifactUnavailableError,
    InferenceTimeoutError,
    InputContractError,
)
from model_ui.policies import (
    DEFAULT_CONFIDENCE_POLICY,
    DEFAULT_LATENCY_POLICY,
    ConfidencePolicy,
    LatencyPolicy,
    classify_confidence,
    classify_latency,
)

QUALITY_LABELS = {
    "needs_review": "Requiere revisión",
    "acceptable": "Resultado aceptable",
    "excellent": "Resultado excelente",
}

CONFIDENCE_COPY = {
    "low": (
        "Confianza baja",
        "El resultado es orientativo y requiere revisión; "
        "la confianza no es una garantía.",
    ),
    "medium": (
        "Confianza intermedia",
        "Usa el resultado como señal orientativa y revisa su contexto antes de actuar.",
    ),
    "high": (
        "Confianza alta",
        "La confianza es alta para este modelo, pero no garantiza "
        "que la decisión sea correcta.",
    ),
}

LATENCY_COPY = {
    "within_target": (
        "Dentro del objetivo",
        "La respuesta quedó dentro del objetivo de la demo.",
    ),
    "above_target": (
        "Por encima del objetivo",
        "La respuesta llegó, pero la latencia supera el objetivo técnico de la demo.",
    ),
}


def build_prediction_view(
    prediction: PredictionPayload,
    latency_ms: float,
    *,
    confidence_policy: ConfidencePolicy = DEFAULT_CONFIDENCE_POLICY,
    latency_policy: LatencyPolicy = DEFAULT_LATENCY_POLICY,
) -> PredictionView:
    """TODO: construye la vista con etiquetas, confianza, latencia y versiones."""

    quality_label = QUALITY_LABELS[prediction.quality_band]

    confidence_level = classify_confidence(
        prediction.confidence,
        confidence_policy,
    )

    confidence_label, confidence_message = CONFIDENCE_COPY[confidence_level]

    latency_status = classify_latency(
        latency_ms,
        latency_policy,
    )

    latency_label, latency_message = LATENCY_COPY[latency_status]

    return PredictionView(
        quality_band=prediction.quality_band,
        quality_label=quality_label,
        confidence=prediction.confidence,
        confidence_level=confidence_level,
        confidence_label=confidence_label,
        confidence_message=confidence_message,
        latency_ms=latency_ms,
        latency_status=latency_status,
        latency_label=latency_label,
        latency_message=latency_message,
        model_version=prediction.model_version,
        preprocessing_version=prediction.preprocessing_version,
    )


def to_user_facing_error(error: Exception, request_id: str) -> UserFacingError:
    """TODO: asigna código estable, mensaje accionable y recuperación."""

    if isinstance(error, InputContractError):
        return UserFacingError(
            code="invalid_input",
            title="Datos de entrada inválidos",
            message="Los valores introducidos no cumplen el contrato de entrada.",
            recovery="Revisa los datos y vuelve a enviar el formulario.",
            request_id=request_id,
        )

    elif isinstance(error, ArtifactUnavailableError):
        return UserFacingError(
            code="artifact_unavailable",
            title="Modelo no disponible",
            message="El modelo no está disponible en este momento.",
            recovery="Revisa la configuración del modelo o contacta con soporte.",
            request_id=request_id,
        )

    elif isinstance(error, InferenceTimeoutError):
        return UserFacingError(
            code="timeout",
            title="Tiempo de espera agotado",
            message="La inferencia no ha terminado dentro del tiempo permitido.",
            recovery="Comprueba el estado de la petición antes de reintentar.",
            request_id=request_id,
        )

    else:
        return UserFacingError(
            code="prediction_error",
            title="Error durante la predicción",
            message="No se ha podido completar la inferencia.",
            recovery="Inténtalo de nuevo más tarde o contacta con soporte.",
            request_id=request_id,
        )
