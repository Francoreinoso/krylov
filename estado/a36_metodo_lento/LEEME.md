# A-36 · método lento (MCMC de referencia) de los motores de series: propuesta de PC 3

Escrito por PC 3 el sábado 21-nov a las 20:00, por encargo de la persona de PC 3, porque `motor/<id>/mcmc.py` no existía
para `cinetica`, `deformacion`, `desgaste` y `sismico`. **Vive aquí y no en `motor/` porque `motor/` es de PC 2:** es una
propuesta para que PC 2 la revise y decida si entra a `motor/<id>/mcmc.py` y a los sellos. Nada de esto está en un sello.

- `comun.py`: correr NUTS (NumPyro, 4 cadenas, 500 de calentamiento y 500 muestras), diagnósticos y guardado.
- `<motor>.py`: el modelo de cada motor, con sus aproximaciones dichas en el docstring.
- `lanzar.py`: un dataset a la vez, 10 minutos de presupuesto por dataset (`WORKPLAN.md`, 11.8).
- `comparar.py`: la red contra el método lento (diferencia de medias de η en desviaciones del método lento, como en el sello de `espacial`).
- `registro.jsonl` y `comparacion_con_la_red.jsonl`: lo que salió, tal cual.

Correr, desde la raíz: `PYTHONPATH=. uv run python estado/a36_metodo_lento/lanzar.py cinetica sismico deformacion desgaste`
(los `.npz` quedan en `estado/a36_metodo_lento/salida/`, sin versionar) y `PYTHONPATH=. uv run python estado/a36_metodo_lento/comparar.py <motor>`.

## `desgaste`, corrido el sábado de 22:41 a 23:29 (sin nada más corriendo)

- **Archivo del demo (`flota`, 40 camiones):** 255 s, r̂ máximo 1,019, sin divergencias. Convergió.
- **Los cuatro simulados:** ninguno terminó en sus 10 minutos (más 1 de gracia). «El método lento no terminó en 10 minutos», tal cual.
- **Contra la red, en `flota`:** lo propio de cada camión coincide (0,07 desviaciones en promedio, misma incertidumbre: razón 0,99). En los cinco parámetros globales la diferencia media es 0,387: tres coinciden (0,09; 0,03; 0,03) y dos no (`log_c` 0,48 y `log_sigma_eps` 1,3). Es un solo archivo.
