import math
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent


def similitud_coseno(a: list[float], b: list[float]) -> float:
    if len(a) != len(b):
        raise ValueError("Los vectores deben tener la misma dimensión.")

    producto_punto = sum(x * y for x, y in zip(a, b))

    norma_a = math.sqrt(sum(x * x for x in a))
    norma_b = math.sqrt(sum(y * y for y in b))

    if norma_a == 0 or norma_b == 0:
        raise ValueError("No se puede comparar un vector de longitud cero.")

    return producto_punto / (norma_a * norma_b)


if __name__ == "__main__":
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta configurar OPENAI_API_KEY en .env")

    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )

    textos = [
        "Olvidé mi contraseña.",
        "No recuerdo la clave para entrar a mi cuenta.",
        "Me cobraron dos veces la suscripción.",
    ]

    respuesta = client.embeddings.create(
        model="text-embedding-3-small",
        input=textos,
        encoding_format="float",
    )

    elementos = sorted(respuesta.data, key=lambda elemento: elemento.index)
    vectores = [elemento.embedding for elemento in elementos]

    for etiqueta, texto, vector in zip("ABC", textos, vectores):
        print(f"\n{etiqueta}: {texto}")
        print("Dimensiones:", len(vector))
        print("Primeros 5 componentes:", vector[:5])

    vector_a, vector_b, vector_c = vectores

    print("\nSIMILITUDES")
    print(f"A con A: {similitud_coseno(vector_a, vector_a):.4f}")
    print(f"A con B: {similitud_coseno(vector_a, vector_b):.4f}")
    print(f"A con C: {similitud_coseno(vector_a, vector_c):.4f}")

    print("\nTokens procesados:", respuesta.usage.total_tokens)