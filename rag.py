import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from buscar_articulos import buscar
from schemas import RespuestaSoporte
from pydantic import ValidationError


BASE_DIR = Path(__file__).resolve().parent
INDICE_PATH = BASE_DIR / "datos" / "indice_articulos.json"
PROMPT_PATH = BASE_DIR / "prompts" / "respuesta_soporte_v1.txt"


def responder_ticket(
    consulta: str,
    client: OpenAI,
    indice: dict,
    instrucciones: str,
    top_k: int = 3,
) -> RespuestaSoporte:
    recuperados = buscar(
        consulta=consulta,
        client=client,
        indice=indice,
        top_k=top_k,
        min_similitud=0.40,
    )

    if not recuperados:
        return RespuestaSoporte(
            estado="sin_informacion",
            respuesta=(
                "No se recuperó documentación suficiente "
                "para responder a esta consulta."
            ),
            fuentes=[],
        )

    # articulos_contexto = [
    #     {
    #         "id": articulo["id"],
    #         "titulo": articulo["titulo"],
    #         "contenido": articulo["contenido"],
    #     }
    #     for articulo in recuperados
    # ]
    articulos_contexto = []

    for documento in recuperados:
        if "chunk_id" in documento:
            fuente = {
                "id": documento["chunk_id"],
                "titulo": (
                    f"{documento['titulo_documento']} — "
                    f"{documento['seccion']}"
                ),
                "contenido": documento["contenido"],
            }
        else:
            fuente = {
                "id": documento["id"],
                "titulo": documento["titulo"],
                "contenido": documento["contenido"],
            }

        articulos_contexto.append(fuente)

    entrada = {
        "consulta": consulta,
        "articulos": articulos_contexto,
    }

    respuesta_api = client.responses.parse(
        model="gpt-4.1-mini",
        instructions=instrucciones,
        input=json.dumps(entrada, ensure_ascii=False),
        text_format=RespuestaSoporte,
    )

    if respuesta_api.status != "completed":
        raise RuntimeError(
            f"La generación no se completó: {respuesta_api.status}"
        )

    resultado = respuesta_api.output_parsed

    if resultado is None:
        raise RuntimeError("No se recibió una respuesta estructurada.")

    # ids_recuperados = {
    #     articulo["id"]
    #     for articulo in recuperados
    # }
    ids_recuperados = {
        fuente["id"]
        for fuente in articulos_contexto
    }

    fuentes_desconocidas = set(resultado.fuentes) - ids_recuperados

    if fuentes_desconocidas:
        raise ValueError(
            "La respuesta cita fuentes no recuperadas: "
            f"{sorted(fuentes_desconocidas)}"
        )

    return resultado


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Responde consultas usando los artículos de soporte."
    )
    parser.add_argument("consulta")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--indice",
        type=Path,
        default=INDICE_PATH,
    )
    args = parser.parse_args()
    indice_path = args.indice

    if not indice_path.is_absolute():
        indice_path = BASE_DIR / indice_path

    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta configurar OPENAI_API_KEY en .env")

    indice = json.loads(
        indice_path.read_text(encoding="utf-8")
    )
    instrucciones = PROMPT_PATH.read_text(encoding="utf-8")

    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )
    try:
        resultado = responder_ticket(
            consulta=args.consulta,
            client=client,
            indice=indice,
            instrucciones=instrucciones,
            top_k=args.top_k,
        )
    except ValidationError as error:
        print("El modelo devolvió datos que incumplen nuestro contrato:")
        print(error)
    else:
        print(resultado.model_dump_json(indent=2))