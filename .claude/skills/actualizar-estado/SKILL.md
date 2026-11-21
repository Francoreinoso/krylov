---
name: actualizar-estado
description: Actualiza el archivo de estado de este computador (estado/<rol>.md) con lo hecho, lo que está en curso, bloqueos, pedidos a otros y números medidos, con el identificador de la tarea al inicio de cada línea, y lo sube a los dos repositorios. Úsala al terminar una tarea, al bloquearte más de 20 minutos, antes de cada hito y antes de dejar al agente trabajando solo.
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Actualizar el estado

Rol: todos. Un minuto. Es la única forma en que los otros dos computadores saben cómo vas, lo que PC 3 lee en cada ronda y lo que muestra el tablero en vivo.

## Pasos

1. Lee tu rol en `CLAUDE.local.md`. Tu archivo es `estado/<rol>.md`. No edites el de otro rol, ni `estado/TABLERO.md`, ni lo que quedó en `estado/historia/` (es lo anterior al pivote).
2. `date "+%a %H:%M"` para la hora de Santiago.
3. Actualiza las secciones, una línea por cosa. **El identificador de la tarea va al inicio de la línea**, después de la hora si la lleva: «sáb 13:05 · A-23 terminada: …». Así lo lee el tablero en vivo; un identificador en medio de la frase no se cuenta. Después del pivote las tareas parten en 21 (P-21, A-21, S-21 en adelante).
   - **Hecho:** «<id> terminada: qué quedó» y el comando para verlo.
   - **En curso:** «<id>: qué estás haciendo» y a qué hora debería estar.
   - **Bloqueos:** qué te frena, desde cuándo, qué probaste.
   - **Pedidos a otros:** a quién, qué y para cuándo.
   - **Números medidos:** valor, cómo se midió, hora.
4. Si un número se va a mostrar al jurado, pídele a `seguimiento` que lo registre (skill `registrar-cifra`).
5. Sube: `git add estado/<rol>.md && git commit -m "estado <rol> HH:MM" && git pull --rebase && git push`. El push va a los dos repositorios; si uno falla, repite `git push`.

## Reglas

- Si algo no va a caber antes de las 18:00, dilo aquí apenas lo sepas. Cortar temprano es mejor que estirar.
- «Terminado» significa las cinco condiciones de `AGENTS.md`. Si falta una, va en «En curso».
- No borres líneas viejas de Hecho; sirven para el hito.

## Terminado cuando

El archivo está en `main` con la hora de ahora.
