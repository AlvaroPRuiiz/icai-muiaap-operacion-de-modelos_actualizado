"""Cliente HTTP que adapta la API Wine al contrato de inferencia de la UI."""

from __future__ import annotations

from collections.abc import Mapping
from threading import local
from typing import Any

import requests
from pydantic import ValidationError  # noqa: F401 - pista para el TODO S7.4

from model_ui.contracts import PredictionPayload
from model_ui.errors import (  # noqa: F401 - pistas para el TODO S7.2
    ArtifactUnavailableError,
    BackendInferenceError,
    InferenceTimeoutError,
    InputContractError,
)


class HttpInferenceGateway:
    """Implementa la frontera de inferencia mediante una llamada HTTP REST."""

    def __init__(
        self,
        base_url: str,
        *,
        timeout: float = 5.0,
        session: Any | None = None,
    ) -> None:
        normalized = base_url.strip().rstrip("/")
        if not normalized:
            raise ValueError("base_url no puede estar vacia")
        if timeout <= 0:
            raise ValueError("timeout debe ser positivo")

        self._prediction_url = f"{normalized}/v1/predictions"
        self._timeout = float(timeout)
        self._session = session if session is not None else requests.Session()
        self._request_context = local()
        self.last_request_id: str | None = None

    @property
    def last_request_id(self) -> str | None:
        """Devuelve el identificador de la ultima llamada en el contexto actual."""

        return getattr(self._request_context, "request_id", None)

    @last_request_id.setter
    def last_request_id(self, value: str | None) -> None:
        self._request_context.request_id = value

    def predict(self, values: Mapping[str, object]) -> PredictionPayload:
        """Envia la muestra por HTTP y devuelve el contrato interno de S6."""

        # TODO S7.1: envia POST a self._prediction_url con json={"features": ...},
        # Accept application/json y self._timeout. Compruebalo con el test de llamada.
        self.last_request_id = None

        # TODO S7.2: traduce Timeout, ConnectionError y RequestException a los
        # errores de dominio que ya entiende PredictionController.

        try:
            response = self._session.post(
                self._prediction_url,
                json={"features": dict(values)},
                headers={"Accept": "application/json"},
                timeout=self._timeout,
            )
        except requests.Timeout:
            raise InferenceTimeoutError("Se ha superado el tiempo de espera") from None
        except requests.ConnectionError:
            raise ArtifactUnavailableError("No se pudo conectar con la API") from None
        except requests.RequestException:
            raise BackendInferenceError("Error al realizar la petición HTTP") from None

        # TODO S7.3: lee un objeto JSON, conserva request_id y diferencia 422/503
        # del resto de errores HTTP.

        status = response.status_code

        if not 200 <= status < 300:
            self.last_request_id = self._header_request_id(response)

            if status == 422:
                raise InputContractError("La API ha rechazado los datos de entrada")

            if status == 503:
                raise ArtifactUnavailableError("La API no está disponible")

            raise BackendInferenceError(f"Error HTTP {status}")

        body = self._read_object(response)
        self.last_request_id = self._request_id(response, body)

        # TODO S7.4: valida body["prediction"] como PredictionPayload; un dict sin
        # validar no satisface el contrato de salida.
        try:
            return PredictionPayload.model_validate(body["prediction"])
        except (KeyError, TypeError, ValidationError):
            raise BackendInferenceError(
                "La respuesta de la API no cumple el contrato"
            ) from None

    @staticmethod
    def _read_object(response: Any) -> dict[str, Any]:
        """Lee una respuesta JSON que debe representar un objeto."""

        try:
            body = response.json()
        except ValueError:
            raise BackendInferenceError("Respuesta JSON no válida") from None

        if not isinstance(body, dict):
            raise BackendInferenceError("La respuesta no es un objeto JSON")

        return body

    @staticmethod
    def _request_id(response: Any, body: dict[str, Any]) -> str | None:
        """Obtiene el identificador remoto de la petición."""

        request_id = body.get("request_id")

        if isinstance(request_id, str) and request_id:
            return request_id

        return HttpInferenceGateway._header_request_id(response)

    @staticmethod
    def _header_request_id(response: Any) -> str | None:
        headers = getattr(response, "headers", {})
        return headers.get("X-Request-Id")
