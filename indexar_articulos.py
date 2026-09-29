import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
ARTICULOS_PATH = BASE_DIR / "datos" / "articulos.json"
INDICE_PATH = BASE_DIR / "datos" / "indice_articulos.json"

MODELO_EMBEDDINGS = "text-embedding-3-small"
DIMENSIONES = 1536


if __name__ == "__main__":
    load_dotenv(BASE_DIR / ".env")
    api_key = os.getenv("OPENAI_API_KEY")

    if not api_key:
        raise RuntimeError("Falta configurar OPENAI_API_KEY en .env")

    articulos = json.loads(
        ARTICULOS_PATH.read_text(encoding="utf-8")
    )

    if not articulos:
        raise ValueError("No hay artículos para indexar.")

    ids = [articulo["id"] for articulo in articulos]

    if len(ids) != len(set(ids)):
        raise ValueError("Los identificadores de los artículos deben ser únicos.")

    textos = [
        f"{articulo['titulo']}\n{articulo['contenido']}"
        for articulo in articulos
    ]

    client = OpenAI(
        api_key=api_key,
        timeout=30.0,
        max_retries=0,
    )

    print(f"Generando embeddings para {len(articulos)} artículos...")

    respuesta = client.embeddings.create(
        model=MODELO_EMBEDDINGS,
        input=textos,
        dimensions=DIMENSIONES,
        encoding_format="float",
    )

    elementos = sorted(
        respuesta.data,
        key=lambda elemento: elemento.index,
    )

    indices = [elemento.index for elemento in elementos]

    if indices != list(range(len(articulos))):
        raise RuntimeError("La respuesta no contiene un vector por artículo.")

    documentos = []

    for articulo, texto, elemento in zip(articulos, textos, elementos):
        vector = elemento.embedding

        if len(vector) != DIMENSIONES:
            raise RuntimeError("Se recibió un vector con dimensión inesperada.")

        documentos.append(
            {
                **articulo,
                "texto_indexado": texto,
                "embedding": vector,
            }
        )

    indice = {
        "modelo": MODELO_EMBEDDINGS,
        "dimensiones": DIMENSIONES,
        "documentos": documentos,
    }

    INDICE_PATH.write_text(
        json.dumps(indice, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Artículos indexados: {len(documentos)}")
    print(f"Dimensiones por vector: {DIMENSIONES}")
    print(f"Tokens procesados: {respuesta.usage.total_tokens}")
    print(f"Índice guardado en: {INDICE_PATH}")