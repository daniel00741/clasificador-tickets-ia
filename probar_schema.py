from pydantic import ValidationError

from schemas import ClasificacionTicket


casos = [
    {
        "estado": "clasificado",
        "categoria": "acceso",
        "motivo": "El usuario necesita restablecer su contraseña.",
    },
    {
        "estado": "clasificado",
        "categoria": "cocina",
        "motivo": "El usuario necesita ayuda.",
    },
    {
        "estado": "requiere_revision",
        "categoria": "tecnico",
        "motivo": "No hay información suficiente.",
    },
]

for numero, datos in enumerate(casos, start=1):
    print(f"\nCaso {numero}")

    try:
        clasificacion = ClasificacionTicket.model_validate(datos)
    except ValidationError as error:
        print("RECHAZADO")
        print(error)
    else:
        print("ACEPTADO")
        print(clasificacion.model_dump())