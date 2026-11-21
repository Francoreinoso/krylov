"""Corre el método lento de a un dataset, con 10 minutos de presupuesto cada uno (WORKPLAN 11.8), y anota lo que salga."""
import json, subprocess, sys, time
from pathlib import Path
AQUI = Path(__file__).resolve().parent
PY = "/Users/clementeferrer/Downloads/krylov/.venv/bin/python"
CASO = {"sismico": "sismicidad", "cinetica": "flotacion", "deformacion": "taludes", "desgaste": "flota"}
PRESUPUESTO = 600
registro = AQUI / "salida" / "registro.jsonl"
for motor in sys.argv[1:]:
    for clave in [("--caso", CASO[motor])] + [("--simulado", str(i)) for i in range(4)]:
        inicio = time.time()
        try:
            r = subprocess.run([PY, str(AQUI / f"{motor}.py"), *clave], capture_output=True, text=True, timeout=PRESUPUESTO + 60, env={"PYTHONPATH": ".", "PATH": "/usr/bin:/bin"})
            lineas = [l for l in r.stdout.splitlines() if l.startswith("{")]
            fila = json.loads(lineas[-1]) if lineas else {"error": r.stderr[-400:]}
        except subprocess.TimeoutExpired:
            fila = {"no_termino_en_s": PRESUPUESTO + 60}
        fila.update(motor=motor, dataset=" ".join(clave), pared_s=round(time.time() - inicio, 1), hora=time.strftime("%H:%M"))
        with open(registro, "a") as f:
            f.write(json.dumps(fila) + "\n")
