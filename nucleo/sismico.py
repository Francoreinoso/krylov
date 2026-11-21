"""Motor `sismico` (caso `sismicidad`): proceso de Hawkes temporal con magnitudes, jerárquico entre sectores.

El modelo generativo (`WORKPLAN.md`, 11.5). En cada sector s, t horas después de la tronadura:

    λ_s(t) = μ_s + A_s·ω·e^(−ω·t) + Σ_{t_i < t} κ(m_i)·ω·e^(−ω·(t − t_i)),      κ(m) = n·e^(α·(m − m_0)) / E[e^(α·(m − m_0))]
    m_i − m_0 ~ Exponencial(b·ln 10)                                           (Gutenberg-Richter), con α < b·ln 10

μ_s es la tasa de fondo, A_s los sismos que gatilla directamente la tronadura, n la razón de ramificación (cuántos
sismos gatilla, en promedio, cada sismo) y ω qué tan rápido se apaga el efecto. Se decide sobre
p_s = P(al menos un sismo de magnitud ≥ M_c en las próximas H horas | historia).

Aquí vive lo que comparten el simulador (`motor/sismico/simular.py`) y el servicio: el diseño de tamaños, el prior,
el preprocesamiento (uno solo), la forma cerrada de lo que se decide y `analizar`. Solo NumPy.

**La tronadura es la primera lectura de cada sector.** El andamio distingue un sector real de uno de relleno por tener
lecturas; un sector sin sismos es un dato válido (y dice mucho), así que cada serie parte con la tronadura en t = 0,
marcada en un canal propio. Por eso los tensores tienen hasta 301 lecturas para 300 sismos.
"""

from __future__ import annotations

import numpy as np

from nucleo import series
from nucleo.casos import ArchivoNoCalza

MOTOR_ID = "sismico"

# El nivel de diseño del modelo: con qué tamaños de archivo practica la red. El simulador sortea dentro de estos
# rangos, `config.json` y `papeles()` publican los mismos, y un archivo que se sale da `rojo_datos`.
MAX_SISMOS = 300
DISENO = {
    "unidades": (2, 16),                # sectores, uniforme
    "lecturas": (1, MAX_SISMOS + 1),    # la tronadura más los sismos del sector: los genera el proceso, de 0 a 300
    "ventana_horas": (2.0, 24.0),       # horas observadas desde la tronadura, log-uniforme
}
RANGOS = {"unidades": {"minimo": DISENO["unidades"][0], "maximo": DISENO["unidades"][1]},
          "lecturas_por_unidad": {"minimo": 0, "maximo": MAX_SISMOS},
          "ventana_horas": {"minimo": DISENO["ventana_horas"][0], "maximo": DISENO["ventana_horas"][1]},
          "frase": "Practiqué con minas de 2 a 16 sectores, observados de 2 a 24 horas después de la tronadura, con hasta 300 temblores por sector."}
PRACTICA = f"practiqué con minas de {DISENO['unidades'][0]} a {DISENO['unidades'][1]} sectores"

PRIOR = {
    "mu_mu_media": float(np.log(0.5)), "mu_mu_desv": 0.7, "sigma_mu_escala": 0.6,
    "n_a": 3.0, "n_b": 4.0,
    "alfa_media": 0.0, "alfa_desv": 0.3,
    "omega_media": float(np.log(1.5)), "omega_desv": 0.5,
    "b_media": 0.0, "b_desv": 0.15,
    "A_media": float(np.log(8.0)), "A_desv": 0.6,
}
NOMBRES_ETA = ("mu_mu", "log_sigma_mu", "logit_n", "log_alfa", "log_omega", "log_b")
NOMBRES_LAM = ("log_mu", "log_A")
CANALES, DIM_COV, DIM_TAM = 5, 3, 3
LN10 = float(np.log(10.0))
HORIZONTE_REF, MAGNITUD_REF = 6.0, 2.0      # para la cobertura de lo que se decide: 6 horas y 2 magnitudes sobre la mínima

PAPELES = [
    {"papel": "unidad", "cantidad": 1, "tipo": "texto", "texto": "El sector de la mina",
     "texto_largo": "En qué sector de la mina se registró cada temblor."},
    {"papel": "tiempo", "cantidad": 1, "tipo": "numero", "texto": "Horas desde la tronadura",
     "texto_largo": "Cuántas horas después de la tronadura se registró el temblor."},
    {"papel": "valor", "cantidad": 1, "tipo": "numero", "texto": "Magnitud del temblor",
     "texto_largo": "La magnitud del temblor, en la escala de los sensores de la mina."},
]


def preparar(t: np.ndarray, m: np.ndarray, mascara: np.ndarray, T: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """El único preprocesamiento del motor: lo llaman el simulador (por lotes) y el servicio (un archivo).

    t, m, mascara: (..., S, K), con los sismos de cada sector ordenados por hora y el relleno al final; t en horas desde la
    tronadura y m = magnitud − magnitud mínima. T (...): horas observadas. Antepone la tronadura a cada serie y devuelve
      x (..., S, K + 1, 5) = [t / T, log(1 + t) / 3, log(tiempo desde el anterior + 0,01) / 3, m, es la tronadura];
      mascara (..., S, K + 1), con la tronadura siempre presente;
      cov (..., S, 3)      = [log(1 + sismos) / 3, tiempo sin sismos al final / T, log(1 + sismos por hora)];
      tam (..., 3)         = [log de sectores − 2, log T − 2, log(1 + sismos totales) / 5].
    """
    T_ = np.asarray(T, dtype=np.float64)[..., None, None]
    cero = np.zeros_like(t[..., :1])
    previo = np.concatenate([cero, t[..., :-1]], axis=-1)
    espera = np.log(np.maximum(t - previo, 0.0) + 0.01) / 3.0
    sismos = np.stack([t / T_, np.log1p(t) / 3.0, espera, m, np.zeros_like(t)], axis=-1) * mascara[..., None]
    tronadura = np.zeros(t.shape[:-1] + (1, 5)); tronadura[..., 4] = 1.0
    x = np.concatenate([tronadura, sismos], axis=-2)
    mascara_x = np.concatenate([np.ones_like(mascara[..., :1]), mascara], axis=-1)
    n = mascara.sum(-1)
    ultimo = (t * mascara).max(-1)
    T_s = T_[..., 0]
    cov = np.stack([np.log1p(n) / 3.0, (T_s - ultimo) / T_s, np.log1p(n / T_s)], axis=-1)
    S = np.full(n.shape[:-1], n.shape[-1], dtype=np.float64)
    tam = np.stack([np.log(S) - 2.0, np.log(T_s[..., 0]) - 2.0, np.log1p(n.sum(-1)) / 5.0], axis=-1)
    return x.astype(np.float32), mascara_x.astype(np.float32), cov.astype(np.float32), tam.astype(np.float32)


def _globales(eta: np.ndarray) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """(n, α, ω, β = b·ln 10) desde η sin restricciones."""
    return 1.0 / (1.0 + np.exp(-eta[..., 2])), np.exp(eta[..., 3]), np.exp(eta[..., 4]), np.exp(eta[..., 5]) * LN10


def excitacion(eta: np.ndarray, t: np.ndarray, m: np.ndarray, mascara: np.ndarray, T: np.ndarray) -> np.ndarray:
    """Lo que los sismos ya registrados aportan a la intensidad en T: Σ_i κ(m_i)·ω·e^(−ω·(T − t_i)), por sector.

    eta (..., d) contra t, m, mascara (..., S, K) y T (...), con difusión de NumPy → (..., S)."""
    n, alfa, omega, beta = (v[..., None, None] for v in _globales(eta))
    kappa = n * np.exp(np.minimum(alfa * m, 50.0)) * np.maximum(beta - alfa, 1e-6) / beta
    return (kappa * omega * np.exp(-omega * (np.asarray(T)[..., None, None] - t)) * mascara).sum(-1)


def esperados(eta: np.ndarray, lam: np.ndarray, de_los_sismos: np.ndarray, T: np.ndarray, horizonte) -> np.ndarray:
    """Número esperado de sismos (de cualquier magnitud registrable) entre T y T + horizonte, en forma cerrada.

    Con núcleo exponencial, E[λ(T + u)] = μ/(1 − n) + (λ(T) − μ/(1 − n))·e^(−ω(1 − n)u); aquí va su integral en [0, horizonte].
    eta (..., d), lam (..., S, 2), de_los_sismos = `excitacion(...)` difundible contra (..., S), T (...) → (..., S)."""
    n, _, omega, _ = (v[..., None] for v in _globales(eta))
    mu, A = np.exp(lam[..., 0]), np.exp(lam[..., 1])
    ahora = mu + A * omega * np.exp(-omega * np.asarray(T)[..., None]) + de_los_sismos        # λ(T)
    base, ritmo = mu / (1.0 - n), omega * (1.0 - n)
    return base * horizonte + (ahora - base) * (1.0 - np.exp(-ritmo * horizonte)) / ritmo


def sismo_fuerte(eta: np.ndarray, lam: np.ndarray, de_los_sismos: np.ndarray, T: np.ndarray, horizonte: float, sobre_la_minima: float) -> np.ndarray:
    """Lo que se decide: P(al menos un sismo de magnitud ≥ M_c en las próximas `horizonte` horas | historia), con
    `sobre_la_minima` = M_c − m_0. Aproximación de Poisson: 1 − exp(−N), N = esperados · 10^(−b·(M_c − m_0))."""
    beta = _globales(eta)[3][..., None]
    return 1.0 - np.exp(-esperados(eta, lam, de_los_sismos, T, horizonte) * np.exp(-beta * sobre_la_minima))


def analizar(caso: dict, transformaciones: list[str], costos: dict) -> dict:
    """Lo propio del motor en la respuesta de `analizar`: por sector, la probabilidad de un sismo fuerte en el horizonte y su curva."""
    col = caso["columnas"]
    plural = caso["unidad"]["plural"]
    try:
        datos = series.leer(caso)
        m0, fuerte, horizonte = float(col["magnitud_minima"]), float(col["umbral"]), float(col["horizonte"])
        if fuerte <= m0 or horizonte <= 0:
            raise ArchivoNoCalza("La magnitud fuerte tiene que ser mayor que la mínima registrada, y el horizonte mayor que cero.", "rojo_modelo")
        avisos = []
        ts, ms = [], []
        for t, y in zip(datos["t"], datos["y"]):
            sirve = np.isfinite(t) & np.isfinite(y) & (y >= m0) & (t >= 0)
            ts.append(t[sirve]); ms.append(y[sirve] - m0)
        chicos = sum(len(t) for t in datos["t"]) - sum(len(t) for t in ts)
        if chicos:
            avisos.append(f"{chicos} temblores quedaron fuera por tener magnitud bajo la mínima ({m0:g}) o no tener hora")
        ids = list(datos["ids"])
        u_min, u_max = DISENO["unidades"]
        if len(ids) < u_min:
            raise ArchivoNoCalza(f"Hay {len(ids)} {caso['unidad']['singular'] if len(ids) == 1 else plural} y {PRACTICA}.")
        if len(ids) > u_max:
            elegidos = sorted(np.random.default_rng(series.SEMILLA).choice(len(ids), size=u_max, replace=False).tolist())
            avisos.append(f"el archivo trae {len(ids)} {plural} y respondo sobre {u_max} elegidos al azar")
            ids, ts, ms = [ids[j] for j in elegidos], [ts[j] for j in elegidos], [ms[j] for j in elegidos]
        if max(len(t) for t in ts) > MAX_SISMOS:
            raise ArchivoNoCalza(f"Hay {plural} con más de {MAX_SISMOS} temblores, y practiqué con hasta {MAX_SISMOS} por sector.", "rojo_modelo")
        ventana = float(col["ventana"]) if col.get("ventana") else float(max(t.max() for t in ts if len(t)))
        v_min, v_max = DISENO["ventana_horas"]
        if not (0.9 * v_min <= ventana <= 1.1 * v_max):
            raise ArchivoNoCalza(f"El archivo cubre {ventana:.3g} {col.get('unidad_tiempo', 'horas')} desde la tronadura y practiqué con ventanas de {v_min:g} a {v_max:g} horas.")
    except ArchivoNoCalza as error:
        return series.lector.rojo(caso, error)
    except ValueError:
        return series.lector.rojo(caso, ArchivoNoCalza("El archivo no trae ningún temblor con magnitud sobre la mínima."))
    t, mascara = series.con_relleno(ts)
    m, _ = series.con_relleno(ms)
    x, mascara_x, cov, tam = preparar(t, m, mascara, np.float64(ventana))
    eta, lam, impl = series.posterior(MOTOR_ID, caso, x, mascara_x, cov, tam)        # (m, d), (m, l, U, 2)
    eta_l = eta[:, None, :]
    de_los_sismos = excitacion(eta_l, t, m, mascara, np.float64(ventana))             # (m, 1, U)
    muestras_p = sismo_fuerte(eta_l, lam, de_los_sismos, np.float64(ventana), horizonte, fuerte - m0).mean(axis=1).T     # (U, m)
    adelante = np.linspace(0.0, horizonte, series.PUNTOS_BANDA)
    curvas = []
    for j, tj in enumerate(ts):
        vienen = np.stack([esperados(eta_l, lam[..., j:j + 1, :], de_los_sismos[..., j:j + 1], np.float64(ventana), u)[..., 0] for u in adelante], axis=-1)
        t_medido, cuenta = np.append(tj, ventana), np.append(np.arange(1, len(tj) + 1), len(tj)).astype(float)
        curvas.append(series.curva(t_medido, cuenta, ventana + adelante, len(tj) + vienen.reshape(-1, len(adelante)), caso, None, decimales=2))
    p = PRIOR
    globales = {"fondo": (eta[:, 0], p["mu_mu_media"], p["mu_mu_desv"]),
                "contagio": (eta[:, 2], -0.333, 0.824),            # logit n con n ~ Beta(3, 4): media ψ(3) − ψ(4), desviación √(ψ'(3) + ψ'(4))
                "apagado": (eta[:, 4], p["omega_media"], p["omega_desv"]), "tamanos": (eta[:, 5], p["b_media"], p["b_desv"])}
    return {
        "implementacion": impl,
        "unidades": series.unidades(ids, muestras_p, costos, curvas),
        "factores": series.factores(caso, globales),
        "columnas": {"usadas": [col["unidad"], col["tiempo"], col["valor"]], "disponibles": col.get("disponibles", 3),
                     "elegidas_por": col.get("elegidas_por", "equipo"), "explicacion": ""},
        "semaforo": {"estado": "amarillo" if avisos else "verde", "motivo": ("; ".join(avisos).capitalize() + ".") if avisos else "", "propuesta": None},
        "examen": series.examen(caso, ids, muestras_p.mean(axis=1)),
        "registro": [f"{len(ids)} {plural}", f"{series.numero(int(mascara.sum()))} temblores", f"{series.MUESTRAS_ETA} versiones creíbles"],
    }
