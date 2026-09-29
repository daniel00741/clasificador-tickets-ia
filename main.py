import argparse
import json
import os
from pathlib import Path

import openai
from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from errores import explicar_error_api
from procesar_ticket import procesar_ticket


BASE_DIR = Path(__file__).resolve().parent


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Clasifica un ticket y propone una respuesta con fuentes."
    )
    parser.add_argument("ticket")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--indice",
        type=Path,
        default=BASE_DIR / "datos" / "indice_manual.json",
    )
    args = parser.parse_args()

    # Validamos antes de realizar llamadas a la API.
    if not args.ticket.strip():
        parser.error("El ticket no puede estar vacío.")

    if args.top_k < 1:
        parser.error("--top-k debe ser mayor o igual a 1.")

    try:
        load_dotenv(BASE_DIR / ".env")

        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            raise RuntimeError("Falta configurar OPENAI_API_KEY.")

        indice_path = args.indice
        if not indice_path.is_absolute():
            indice_path = BASE_DIR / indice_path

        indice = json.loads(
            indice_path.read_text(encoding="utf-8")
        )

        instrucciones_clasificacion = (
            BASE_DIR / "prompts" / "clasificador_v1.txt"
        ).read_text(encoding="utf-8")

        instrucciones_soporte = (
            BASE_DIR / "prompts" / "respuesta_soporte_v1.txt"
        ).read_text(encoding="utf-8")

        with OpenAI(
            api_key=api_key,
            timeout=30.0,
            max_retries=0,
        ) as client:
            resultado = procesar_ticket(
                ticket=args.ticket,
                client=client,
                indice=indice,
                instrucciones_clasificacion=instrucciones_clasificacion,
                instrucciones_soporte=instrucciones_soporte,
                top_k=args.top_k,
            )

    except ValidationError as error:
        print(f"La respuesta incumple nuestro contrato:\n{error}")
        return 1

    except openai.APIError as error:
        print(explicar_error_api(error))
        return 1

    except (OSError, ValueError, RuntimeError) as error:
        print(f"No se pudo completar el procesamiento: {error}")
        return 1

    print(resultado.model_dump_json(indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())