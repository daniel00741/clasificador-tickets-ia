# Evaluación inicial del RAG

Configuración:
- Modelo generativo: gpt-4.1-mini
- Modelo de embeddings: text-embedding-3-small
- Top-K: 3
- Similitud mínima: 0.40, experimental
- Prompt: respuesta_soporte_v1.txt

## R1: Cobro duplicado

Consulta:
Me aparecen dos cargos por la misma suscripción. ¿Cómo solicito una revisión?

Fuente necesaria:
KB-003.

Criterios:
- Distingue cargos confirmados y pendientes.
- Solicita fechas, importes y referencias de las transacciones.
- No promete un reembolso automático.
- Cita KB-003.

Resultados:
- IDs recuperados: KB-003, KB-004.
- Recall@3: 1.0.
- Estado generado: respondido.
- Fuentes citadas: KB-003.
- Afirmaciones sin respaldo: ninguna identificada.
- ¿Cumple los criterios?: sí.
- Observaciones: recuperó un artículo adicional no necesario,
  pero la respuesta utilizó únicamente la fuente pertinente.

## R2: Dos problemas distintos

Consulta:
Olvidé mi contraseña y además tengo un cobro duplicado.
¿Qué pasos debo seguir para cada problema?

Fuentes necesarias:
KB-001 y KB-003.

Criterios:
- Explica cómo restablecer la contraseña.
- Explica cómo solicitar la revisión del cobro.
- No afirma que la cuenta esté bloqueada.
- No garantiza un reembolso.
- Cita las fuentes que respaldan cada parte.

Resultados:
- IDs recuperados: KB-001, KB-003, KB-002.
- Recall@3: 1.0.
- Estado generado: respondido.
- Fuentes citadas: KB-001, KB-003.
- Afirmaciones sin respaldo: ninguna identificada.
- ¿Atiende ambos problemas?: sí.
- Observaciones: utiliza las dos fuentes necesarias y no incorpora
  el procedimiento de bloqueo del artículo adicional.

## R3: Sin documentación disponible

Consulta:
¿Puedo cambiar el idioma de la aplicación a portugués?

Fuentes necesarias:
Ninguna: el corpus no contiene ese procedimiento.

Criterios:
- Devuelve sin_informacion.
- Devuelve fuentes vacías.
- No inventa opciones de menú ni afirma que la función no existe.

Resultados:
- IDs recuperados:
- Recall@3: no aplica.
- Estado generado:
- Fuentes citadas:
- ¿Se abstiene correctamente?:
- Observaciones:

## R4: Pregunta sin respuesta dentro de un tema conocido

Consulta:
Si confirmáis que me habéis cobrado dos veces,
¿en cuántos días recibiré el reembolso?

Fuente relacionada:
KB-003, pero no especifica el plazo de reembolso.

Criterios:
- Reconoce que no dispone del plazo solicitado.
- No inventa una cantidad de días.
- Según nuestro contrato actual, devuelve sin_informacion
  y fuentes vacías si no puede responder a esa pregunta.

Resultados:
- IDs recuperados: KB-003, KB-004.
- Primer intento: error de validación; incluyó fuentes con sin_informacion.
- Cambio aplicado: aclaración y ejemplo en el prompt.
- Segundo intento: sin_informacion y fuentes vacías.
- ¿Inventó un plazo?: no.
- ¿Reconoce la información ausente?: sí.
- Observación: caso utilizado para ajustar el prompt; desde ahora
  se considera un caso de desarrollo y regresión.