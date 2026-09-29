import openai


def explicar_error_api(error: openai.APIError) -> str:
    if isinstance(error, openai.AuthenticationError):
        return "La API rechazó la credencial. Revisa que esté activa."

    if isinstance(error, openai.PermissionDeniedError):
        return "La clave no tiene permisos para esta operación."

    if isinstance(error, openai.RateLimitError):
        codigos_cuota = {
            "insufficient_quota",
            "credit_balance_exhausted",
        }

        if error.code in codigos_cuota:
            return "No hay cuota o saldo disponible. Revisa Billing."

        return (
            "La API devolvió un límite de uso (429). "
            f"Revisa su código antes de reintentar: {error.code}"
        )

    if isinstance(error, openai.APITimeoutError):
        return "Se agotó el tiempo de espera de la solicitud."

    if isinstance(error, openai.APIConnectionError):
        return "No se pudo establecer o mantener la conexión con la API."

    if isinstance(error, openai.BadRequestError):
        return "La solicitud es inválida. Revisa parámetros y esquema."

    if isinstance(error, openai.APIStatusError):
        return (
            f"La API devolvió un error HTTP {error.status_code}. "
            f"Código: {error.code}"
        )

    return "Ocurrió un error del SDK al utilizar la API."