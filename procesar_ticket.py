from openai import OpenAI

from clasificador import clasificar_ticket
from rag import responder_ticket
from schemas import ResultadoTicket


def procesar_ticket(
    ticket: str,
    client: OpenAI,
    indice: dict,
    instrucciones_clasificacion: str,
    instrucciones_soporte: str,
    top_k: int = 3,
) -> ResultadoTicket:
    ticket = ticket.strip()

    if not ticket:
        raise ValueError("El ticket no puede estar vacío.")

    if top_k < 1:
        raise ValueError("top_k debe ser mayor o igual a 1.")

    clasificacion = clasificar_ticket(
        ticket=ticket,
        client=client,
        instrucciones=instrucciones_clasificacion,
    )

    soporte = responder_ticket(
        consulta=ticket,
        client=client,
        indice=indice,
        instrucciones=instrucciones_soporte,
        top_k=top_k,
    )

    return ResultadoTicket(
        clasificacion=clasificacion,
        soporte=soporte,
    )