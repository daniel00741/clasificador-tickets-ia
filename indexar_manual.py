import json
import os
from pathlib import Path

from dotenv import load_dotenv
from openai import OpenAI


BASE_DIR = Path(__file__).resolve().parent
FRAGMENTOS_PATH = BASE_DIR / "datos" / "fragmentos_manual.json"
INDICE_PATH = BASE_DIR / "datos" / "indice_manual.json"

MODELO = "text-embedding-3-small"
DIMENSIONES = 1536


def construir_texto_embedding(fragmento: dict[str, str]) -> str:
    return (
        f"{fragmento['titulo_documento']}\n"
        f"{fragmento['seccion']}\n\n"
        f"{fragmento['contenido']}"
    )


if __name__ == "__main__":
    load_dotenv(BASE_DIR / ".env")

    api_key = os.getenv("OPENAI_API_KEY")
    if not api_key:
        raise RuntimeError("Falta configurar OPENAI_API_KEY.")

    fragmentos = json.loads(
        FRAGMENTOS_PATH.read_text(encoding="utf-8")
    )

    if not fragmentos:
        raise ValueError("No hay fragmentos para indexar.")

    identificadores = [f["chunk_id"] for f in fragmentos]
    if len(identificadores) != len(set(identificadores)):
        raise ValueError("Hay identificadores de fragmentos repetidos.")

    textos = [
        construir_texto_embedding(fragmento)
        for fragmento in fragmentos
    ]

    embeddings_guardados = {}

    if INDICE_PATH.exists():
        indice_anterior = json.loads(
            INDICE_PATH.read_text(encoding="utf-8")
        )

        configuracion_compatible = (
            indice_anterior["modelo"] == MODELO
            and indice_anterior["dimensiones"] == DIMENSIONES
        )

        if configuracion_compatible:
            for documento in indice_anterior["documentos"]:
                vector = documento["embedding"]

                if len(vector) == DIMENSIONES:
                    embeddings_guardados[
                        documento["texto_indexado"]
                    ] = vector

    # dict.fromkeys elimina textos repetidos conservando su orden.
    textos_pendientes = list(
        dict.fromkeys(
            texto
            for texto in textos
            if texto not in embeddings_guardados
        )
    )

    reutilizados = sum(
        texto in embeddings_guardados
        for texto in textos
    )

    print(f"Fragmentos con embedding reutilizable: {reutilizados}")
    print(f"Textos nuevos o modificados: {len(textos_pendientes)}")

    tokens_procesados = 0

    if textos_pendientes:
        client = OpenAI(
            api_key=api_key,
            timeout=30.0,
            max_retries=0,
        )

        respuesta = client.embeddings.create(
            model=MODELO,
            input=textos_pendientes,
            dimensions=DIMENSIONES,
            encoding_format="float",
        )

        resultados = sorted(
            respuesta.data,
            key=lambda item: item.index,
        )

        if [item.index for item in resultados] != list(
            range(len(textos_pendientes))
        ):
            raise RuntimeError(
                "Los embeddings no corresponden a las entradas."
            )

        for texto, resultado in zip(textos_pendientes, resultados):
            if len(resultado.embedding) != DIMENSIONES:
                raise RuntimeError(
                    "Dimensiones del embedding inesperadas."
                )

            embeddings_guardados[texto] = resultado.embedding

        tokens_procesados = respuesta.usage.total_tokens

    documentos = [
        {
            **fragmento,
            "texto_indexado": texto,
            "embedding": embeddings_guardados[texto],
        }
        for fragmento, texto in zip(fragmentos, textos)
    ]

    indice = {
        "modelo": MODELO,
        "dimensiones": DIMENSIONES,
        "documentos": documentos,
    }

    INDICE_PATH.write_text(
        json.dumps(indice, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Fragmentos indexados: {len(documentos)}")
    print(f"Tokens procesados: {tokens_procesados}")
    print(f"Índice guardado en: {INDICE_PATH}")