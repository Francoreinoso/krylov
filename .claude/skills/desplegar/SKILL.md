---
name: desplegar
description: Despliega Krylov - la web con las respuestas precalculadas en Vercel y la API en Render, las dos desde el repositorio espejo - y verifica desde un teléfono que responde. Úsala en PC 1 para cada redespliegue después del pivote (P-22, P-28), agrupados en los hitos H4, H5 y H6, y hasta las 20:30 cada vez que un motor pase a responder con su red (P-30).
---

> **Hackathon:** proyecto chico; el producto se termina el **sábado a las 18:00** y después solo se itera el demo y el pitch. Lo más simple que se vea bien, y que la simulación se vea en pantalla.

# Desplegar

Rol: `producto` (PC 1), cuando su humano lo pide. Tope: 30 minutos por intento. Lee antes `STACK.md`, sección 2.6.

## Cómo está armado

- **Vercel** sirve la web y los archivos de `web/public/estatico/`. Con eso basta para que el recorrido completo funcione en la URL pública, sin servidor.
- **Render** corre la API del cálculo en vivo. La URL pública no depende de ella: todo el recorrido está en modo estático. Subir un archivo propio sí la exige; si no responde, el chat lo dice.
- Los dos despliegan desde **`Silent-math/krylov`**, el repositorio espejo, porque no pueden conectarse al de la organización. Cada `git push` actualiza los dos repositorios y dispara los despliegues.
- La conexión inicial de Vercel y Render la hace **el dueño de la cuenta `Silent-math`**, una sola vez, tenga el rol que tenga.

## Configuración (Vercel quedó conectado antes del pivote; sirve de referencia y para Render)

1. **Espejo público.** En el plan gratuito, Vercel no despliega commits de otros autores en un repositorio privado. El espejo `Silent-math/krylov` ya es público (D-27); si un commit no despliega, es lo primero que se revisa.
2. **Vercel:** proyecto sobre `Silent-math/krylov`, «Root Directory» `web`, framework Vite. Variable `VITE_API_URL` con la URL de Render (puede quedar vacía: la web usa el modo estático).
3. **Render:** servicio web desde el mismo repositorio. Lenguaje «Python 3». Construcción `pip install -r requirements.txt`. Inicio `uvicorn servicio.app:app --host 0.0.0.0 --port $PORT`. Variables: `PYTHON_VERSION` con una versión 3.12 completa, una `KRYLOV_MOTOR_<ID>` por motor (`ESPACIAL`, `DEFORMACION`, `CINETICA`, `DESGASTE`, `SISMICO`) con el valor que fije PC 2, y `ANTHROPIC_API_KEY`. **La clave nunca va en el repositorio.**
4. `requirements.txt` sale de `uv export --no-dev --no-hashes -o requirements.txt`. No debe traer `torch`.

## Cada vez

**Vercel tiene un límite diario de despliegues en el plan gratuito, y ya se alcanzó una vez.** Solo se despliega cuando cambia `web/`, y los redespliegues se agrupan en H4, H5 y H6 (`WORKPLAN.md`, 6.8).

1. `git pull --rebase`. Corre `uv run python -m servicio.exportar_estatico` y sube los archivos generados.
2. `git push` y comprueba que llegó a los dos repositorios (`git ls-remote` da el mismo identificador en ambos).
3. **Verifica desde un teléfono con datos móviles:** abre la URL con `?estatico=1`, entra a `leyes`, llega al mapa y a «¿Dónde perforo?»; después, cada tarjeta que esté en el inicio. Luego sin el parámetro. Mide el tiempo.
4. **Mira el rótulo de cada tarjeta:** dice que respondió la red solo si su motor pasó `validar-motor`; si no, «precalculado» (o «ejemplo» mientras se maqueta).
5. Anota en `estado/producto.md`: las dos URL, la hora y los tiempos.

## Si algo falla

- **Vercel no despliega un commit:** mira el autor del commit, la visibilidad del espejo y si se llegó al límite diario.
- **Render tarda o está dormido:** es lo esperado en el plan gratuito. La web no depende de él. La web llama a `/api/salud` al cargar, para ir despertándolo.
- **Render no levanta:** revisa que `PYTHON_VERSION` sea 3.12 y que `requirements.txt` no traiga `torch`. Si no sale en 30 minutos, la API se queda solo en local y subir un archivo propio se muestra desde el computador del escenario.

**En el escenario el demo corre en local.** La URL pública es para la entrega, el QR y la página de votación.

## Terminado cuando

La URL pública muestra el recorrido desde un teléfono, en modo estático, con el rótulo correcto en cada tarjeta, y está anotada en el estado.
