from typing import Literal, Self

from pydantic import BaseModel, ConfigDict, Field, model_validator


class ClasificacionTicket(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    estado: Literal["clasificado", "requiere_revision"]

    categoria: Literal["acceso", "facturacion", "tecnico"] | None

    motivo: str = Field(min_length=1)

    @model_validator(mode="after")
    def validar_coherencia(self) -> Self:
        if self.estado == "clasificado" and self.categoria is None:
            raise ValueError(
                "Un ticket clasificado debe tener una categoría."
            )

        if self.estado == "requiere_revision" and self.categoria is not None:
            raise ValueError(
                "Un ticket que requiere revisión debe tener categoria=None."
            )

        return self
    
class RespuestaSoporte(BaseModel):
    model_config = ConfigDict(
        extra="forbid",
        strict=True,
        str_strip_whitespace=True,
    )

    estado: Literal["respondido", "sin_informacion"]
    respuesta: str = Field(min_length=1)
    fuentes: list[str]

    @model_validator(mode="after")
    def validar_fuentes(self) -> Self:
        if self.estado == "respondido" and not self.fuentes:
            raise ValueError(
                "Una respuesta de soporte debe indicar sus fuentes."
            )

        if self.estado == "sin_informacion" and self.fuentes:
            raise ValueError(
                "Una respuesta sin información debe tener fuentes vacías."
            )

        if len(self.fuentes) != len(set(self.fuentes)):
            raise ValueError("No deben repetirse las fuentes.")

        return self
    
class ResultadoTicket(BaseModel):
    model_config = ConfigDict(extra="forbid", strict=True)

    clasificacion: ClasificacionTicket
    soporte: RespuestaSoporte
