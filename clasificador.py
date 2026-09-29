from openai import OpenAI

from schemas import ClasificacionTicket


def clasificar_ticket(
    ticket: str,
    client: OpenAI,
    instrucciones: str,
) -> ClasificacionTicket:
    respuesta = client.responses.parse(
        model="gpt-4.1-mini",
        instructions=instrucciones,
        input=ticket,
        text_format=ClasificacionTicket,
    )

    if respuesta.status != "completed":
        raise RuntimeError(
            f"La respuesta no se completó: {respuesta.status}"
        )

    clasificacion = respuesta.output_parsed

    if clasificacion is None:
        raise RuntimeError(
            "No se recibió una clasificación estructurada."
        )

    return clasificacion