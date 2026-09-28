from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent
PROMPT_PATH = BASE_DIR / "prompts" / "clasificador_v1.txt"


def cargar_instrucciones() -> str:
    return PROMPT_PATH.read_text(encoding="utf-8")


if __name__ == "__main__":
    instrucciones = cargar_instrucciones()

    print("INSTRUCCIONES DEL CLASIFICADOR")
    print(instrucciones)
