import httpx
import openai

from errores import explicar_error_api


def crear_error_http(clase_error, status_code: int, code: str):
    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses",
    )

    response = httpx.Response(
        status_code=status_code,
        request=request,
    )

    return clase_error(
        "Error simulado para una prueba local.",
        response=response,
        body={"code": code},
    )


if __name__ == "__main__":
    request = httpx.Request(
        "POST",
        "https://api.openai.com/v1/responses",
    )

    casos = [
        (
            "Credencial inválida",
            crear_error_http(
                openai.AuthenticationError,
                401,
                "invalid_api_key",
            ),
            "La API rechazó la credencial. Revisa que esté activa.",
        ),
        (
            "Permisos insuficientes",
            crear_error_http(
                openai.PermissionDeniedError,
                403,
                "insufficient_permissions",
            ),
            "La clave no tiene permisos para esta operación.",
        ),
        (
            "Saldo agotado",
            crear_error_http(
                openai.RateLimitError,
                429,
                "credit_balance_exhausted",
            ),
            "No hay cuota o saldo disponible. Revisa Billing.",
        ),
        (
            "Límite temporal",
            crear_error_http(
                openai.RateLimitError,
                429,
                "rate_limit_exceeded",
            ),
            (
                "La API devolvió un límite de uso (429). "
                "Revisa su código antes de reintentar: rate_limit_exceeded"
            ),
        ),
        (
            "Tiempo de espera agotado",
            openai.APITimeoutError(request=request),
            "Se agotó el tiempo de espera de la solicitud.",
        ),
        (
            "Error de conexión",
            openai.APIConnectionError(request=request),
            "No se pudo establecer o mantener la conexión con la API.",
        ),
    ]

    aciertos = 0

    for nombre, error, esperado in casos:
        obtenido = explicar_error_api(error)

        if obtenido == esperado:
            aciertos += 1
            print(f"OK: {nombre}")
        else:
            print(f"FALLO: {nombre}")
            print("Esperado:", esperado)
            print("Obtenido:", obtenido)

    print(f"\nPruebas correctas: {aciertos}/{len(casos)}")