import argparse
import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI

from explorar_embeddings import similitud_coseno


BASE_DIR = Path(__file__).resolve().parent
INDICE_PATH = BASE_DIR / "datos" / "indice_articulos.json"


def buscar(
    consulta: str,
    client: OpenAI,
    indice: dict,
    top_k: int = 3,
    min_similitud: float | None = None,
) -> list[dict]:
    if not consulta.strip():
        raise ValueError("La consulta no puede estar vacía.")

    if top_k < 1:
        raise ValueError("top_k debe ser mayor o igual a 1.")
    if min_similitud is not None and not -1 <= min_similitud <= 1:
        raise ValueError("La similitud mínima debe estar entre -1 y 1.")

    documentos = indice["documentos"]

    if not documentos:
        return []

    respuesta = client.embeddings.create(
        model=indice["modelo"],
        input=consulta,
        dimensions=indice["dimensiones"],
        encoding_format="float",
    )

    vector_consulta = respuesta.data[0].embedding

    resultados = []

    for documento in documentos:
        puntuacion = similitud_coseno(
            vector_consulta,
            documento["embedding"],
        )
        if min_similitud is not None and puntuacion < min_similitud:
            continue

        # resultados.append(
        #     {
        #         "id": documento["id"],
        #         "titulo": documento["titulo"],
        #         "categoria": documento["categoria"],
        #         "contenido": documento["contenido"],
        #         "similitud": puntuacion,
        #     }
        # )
        resultado = {
            campo: valor
            for campo, valor in documento.items()
            if campo not in {"embedding", "texto_indexado"}
        }
        resultado["similitud"] = puntuacion
        resultados.append(resultado)

    resultados.sort(
        key=lambda resultado: resultado["similitud"],
        reverse=True,
    )

    return resultados[:top_k]


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Busca artículos de soporte por similitud semántica."
    )

    parser.add_argument("consulta")
    parser.add_argument("--top-k", type=int, default=3)
    parser.add_argument(
        "--min-similitud",
        type=float,
        default=None,
    )

    args = parser.parse_args()

    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta configurar OPENAI_API_KEY en .env")

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
        print("Ningún artículo supera el umbral configurado.")
        
    for posicion, resultado in enumerate(resultados, start=1):
        print(
            f"\n{posicion}. {resultado['id']} — "
            f"{resultado['titulo']}"
        )
        print(f"Similitud: {resultado['similitud']:.4f}")
        print(f"Categoría: {resultado['categoria']}")
        print(f"Contenido: {resultado['contenido']}")