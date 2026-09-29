import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI
from pydantic import ValidationError

from clasificador import clasificar_ticket

import argparse
import openai
from errores import explicar_error_api


BASE_DIR = Path(__file__).resolve().parent
#CASOS_PATH = BASE_DIR / "evaluacion" / "casos.json"
PROMPT_PATH = BASE_DIR / "prompts" / "clasificador_v1.txt"


def evaluar(client: OpenAI, instrucciones: str, casos: list[dict]) -> None:
    aciertos = 0
    fallos = 0
    errores = 0

    for caso in casos:
        print(f"\n{caso['id']}: {caso['ticket']}")

        try:
            resultado = clasificar_ticket(
                ticket=caso["ticket"],
                client=client,
                instrucciones=instrucciones,
            )

        except (ValidationError, RuntimeError) as error:
            errores += 1
            print("ERROR: no se obtuvo una clasificación válida.")
            print(error)
            continue
        except openai.APIError as error:
            print("Evaluación interrumpida:")
            print(explicar_error_api(error))
            print(
                f"Casos terminados antes de la interrupción: "
                f"{aciertos + fallos + errores}/{len(casos)}"
            )
            return

        obtenido = {
            "estado": resultado.estado,
            "categoria": resultado.categoria,
        }

        esperado = caso["esperado"]

        if obtenido == esperado:
            aciertos += 1
            print("ACIERTO")
        else:
            fallos += 1
            print("FALLO")

        print("Esperado:", esperado)
        print("Obtenido:", obtenido)
        print("Motivo:", resultado.motivo)

    total = len(casos)

    print("\nRESUMEN")
    print(f"Total: {total}")
    print(f"Aciertos: {aciertos}")
    print(f"Fallos de clasificación: {fallos}")
    print(f"Errores de procesamiento: {errores}")

    if total > 0:
        porcentaje = aciertos / total * 100
        print(f"Porcentaje de aciertos sobre el total: {porcentaje:.1f}%")


if __name__ == "__main__":
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta configurar OPENAI_API_KEY en .env")

    instrucciones = PROMPT_PATH.read_text(encoding="utf-8")
    
    parser = argparse.ArgumentParser(
        description="Evalúa el clasificador con un archivo de casos."
    )

    parser.add_argument(
        "--casos",
        default="evaluacion/casos.json",
        help="Ruta del archivo JSON de evaluación.",
    )

    args = parser.parse_args()
    casos_path = BASE_DIR / args.casos
    
    casos = json.loads(casos_path.read_text(encoding="utf-8"))

    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )

    evaluar(
        client=client,
        instrucciones=instrucciones,
        casos=casos,
    )