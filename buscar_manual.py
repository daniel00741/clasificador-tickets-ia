import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from buscar_articulos import buscar


BASE_DIR = Path(__file__).resolve().parent
INDICE_PATH = BASE_DIR / "datos" / "indice_manual.json"


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Busca secciones del manual de soporte."
    )
    parser.add_argument("consulta")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument("--min-similitud", type=float, default=None)
    args = parser.parse_args()

    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta configurar OPENAI_API_KEY.")

    indice = json.loads(
        INDICE_PATH.read_text(encoding="utf-8")
    )

    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )

    resultados = buscar(
        consulta=args.consulta,
        client=client,
        indice=indice,
        top_k=args.top_k,
        min_similitud=args.min_similitud,
    )

    print(f"\nConsulta: {args.consulta}")

    if not resultados:
        print("No se encontraron fragmentos con los criterios indicados.")

    for posicion, resultado in enumerate(resultados, start=1):
        print(
            f"\n{posicion}. {resultado['chunk_id']} — "
            f"{resultado['seccion']}"
        )
        print(f"Documento: {resultado['titulo_documento']}")
        print(f"Similitud: {resultado['similitud']:.4f}")
        print(f"Contenido:\n{resultado['contenido']}")