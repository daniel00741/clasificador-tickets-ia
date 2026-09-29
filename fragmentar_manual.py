import json
from pathlib import Path


BASE_DIR = Path(__file__).resolve().parent
MANUAL_PATH = BASE_DIR / "datos" / "manual_soporte.md"
SALIDA_PATH = BASE_DIR / "datos" / "fragmentos_manual.json"


def fragmentar_por_secciones(
    texto: str,
    documento_id: str,
) -> list[dict[str, str]]:
    titulo_documento = ""
    seccion_actual: str | None = None
    lineas_contenido: list[str] = []
    fragmentos: list[dict[str, str]] = []

    def guardar_seccion() -> None:
        contenido = "\n".join(lineas_contenido).strip()

        if seccion_actual is None or not contenido:
            return

        fragmentos.append(
            {
                "documento_id": documento_id,
                "chunk_id": f"{documento_id}-{len(fragmentos) + 1:02d}",
                "titulo_documento": titulo_documento,
                "seccion": seccion_actual,
                "contenido": contenido,
            }
        )

    for linea in texto.splitlines():
        if linea.startswith("# "):
            titulo_documento = linea[2:].strip()

        elif linea.startswith("## "):
            guardar_seccion()
            seccion_actual = linea[3:].strip()
            lineas_contenido = []

        elif seccion_actual is not None:
            lineas_contenido.append(linea)

    guardar_seccion()

    return fragmentos


if __name__ == "__main__":
    texto = MANUAL_PATH.read_text(encoding="utf-8")

    fragmentos = fragmentar_por_secciones(
        texto=texto,
        documento_id="MANUAL-001",
    )

    SALIDA_PATH.write_text(
        json.dumps(fragmentos, ensure_ascii=False, indent=2),
        encoding="utf-8",
    )

    print(f"Fragmentos generados: {len(fragmentos)}")

    for fragmento in fragmentos:
        print(
            f"{fragmento['chunk_id']} | "
            f"{fragmento['seccion']} | "
            f"{len(fragmento['contenido'])} caracteres"
        )

    print(f"\nArchivo guardado en: {SALIDA_PATH}")