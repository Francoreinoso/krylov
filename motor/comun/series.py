"""El andamio de los motores de series: NPE jerárquica con amortización factorizada (`WORKPLAN.md`, 11.1 y 11.6).

Un dataset es un conjunto de unidades (sectores, líneas, camiones) y cada unidad una serie
irregular de lecturas. El modelo de cada motor tiene tres niveles: el **diseño** del dataset
(cuántas unidades, cuántas lecturas por unidad, a qué tiempos), los parámetros globales η de
la faena y los locales λ_j de cada unidad. La red aproxima

    p(η, λ_1..J | D)  ≈  q(η | s(D)) · Π_j q(λ_j | η, s_j, s(D))

con un codificador por unidad (convoluciones 1D con máscara → s_j), una agregación invariante
al orden de las unidades (atención con máscara → s(D)), un flujo de acoplamiento para η y otro,
compartido entre unidades, para λ_j. El tamaño del dataset varía en cada simulación: los tensores
llevan relleno y máscara, y el número de unidades y de lecturas entra además como dato explícito
(`tam`, `cov`), porque un promedio con máscara no ve cuántos elementos promedió.

Cada motor aporta una **especificación** (su módulo `motor/<id>/simular.py`):

    MOTOR_ID, NOMBRES_ETA, NOMBRES_LAM         nombres de los parámetros, en espacio sin restricciones
    CANALES, DIM_COV, DIM_TAM                  tamaños de la entrada (los fija `nucleo/<id>.preparar`)
    DISENO                                     el a priori de tamaño, {"unidades": (mín, máx), "lecturas": (mín, máx), ...}
    simular(gen, lote) -> dict                 un lote de NumPy con un tamaño común: x (B, U, K, CANALES), mascara (B, U, K),
                                               cov (B, U, DIM_COV), tam (B, DIM_TAM), eta (B, d), lam (B, U, d_local),
                                               cantidad (B, U): lo que se decide, exacto con los parámetros verdaderos,
                                               y extra: lo que `cantidad_de` necesita
    cantidad_de(eta, lam, extra) -> (L, B, U)  lo que se decide, para muestras del posterior (L, B, d) y (L, B, U, d_local)
    CON_CLASE (opcional)                       True si cada unidad tiene además un estado discreto z_j ∈ {0, 1} (en `deformacion`:
                                               estable o acelerando). Entonces `lam` trae z_j como última columna, una cabeza
                                               da P(z_j = 1 | η, s_j, s(D)) y el flujo local se condiciona también en z_j

`nucleo/series.py` es la otra mitad: lo mismo en NumPy y onnxruntime, para responder.
"""

from __future__ import annotations

import json
import time
from pathlib import Path
from types import ModuleType

import numpy as np
import torch
from torch import Tensor, nn

from motor.comun import validacion
from motor.comun.codificador import MUY_NEGATIVO, PoolingAtencion, comparar_con_onnxruntime, exportar_onnx
from motor.comun.flujo import FlujoCondicional

DIM_UNIDAD, DIM_DATASET = 64, 128


class CodificadorSeries(nn.Module):
    """Lecturas de cada unidad → s_j; unidades → s(D). El relleno no cambia ninguna de las dos salidas."""

    def __init__(self, canales: int, dim_cov: int, dim_tam: int, ancho: int = 64):
        super().__init__()
        self.entrada = nn.Sequential(nn.Linear(canales, ancho), nn.ReLU())
        self.conv1 = nn.Conv1d(ancho, ancho, kernel_size=3, padding=1)
        self.conv2 = nn.Conv1d(ancho, ancho, kernel_size=3, padding=1)
        self.unidad = nn.Sequential(nn.Linear(2 * ancho + dim_cov, 128), nn.ReLU(), nn.Linear(128, DIM_UNIDAD))
        self.phi = nn.Sequential(nn.Linear(DIM_UNIDAD, 128), nn.ReLU())
        self.atencion = PoolingAtencion(128, cabezas=4)
        self.rho = nn.Sequential(nn.Linear(self.atencion.dim_salida + dim_tam, 256), nn.ReLU(), nn.Linear(256, DIM_DATASET))

    def forward(self, x: Tensor, mascara: Tensor, cov: Tensor, tam: Tensor) -> tuple[Tensor, Tensor]:
        """x (B, U, K, c), mascara (B, U, K), cov (B, U, c_cov), tam (B, c_tam) → s(D) (B, 128), s_j (B, U, 64)."""
        B, U, K, c = x.shape
        m = mascara.reshape(B * U, K, 1)
        h = self.entrada(x.reshape(B * U, K, c)) * m
        # Convolución con máscara: el relleno entra como ceros, igual que el borde, y la salida vuelve a enmascararse.
        h = torch.relu(self.conv1(h.transpose(1, 2))).transpose(1, 2) * m
        h = torch.relu(self.conv2(h.transpose(1, 2))).transpose(1, 2) * m
        cuenta = m.sum(dim=1)                                         # (B·U, 1): lecturas reales de la unidad
        promedio = h.sum(dim=1) / cuenta.clamp(min=1.0)
        maximo = (h - (1.0 - m) * MUY_NEGATIVO).amax(dim=1) * (cuenta > 0)
        hay = (cuenta > 0).to(x.dtype).reshape(B, U, 1)               # 1 = unidad real, 0 = unidad de relleno
        s_j = self.unidad(torch.cat([promedio, maximo, cov.reshape(B * U, -1)], dim=-1)).reshape(B, U, -1) * hay
        s_d = self.rho(torch.cat([self.atencion(self.phi(s_j), hay.squeeze(-1)), tam], dim=-1))
        return s_d, s_j


class RedSeries(nn.Module):
    """Codificador + flujo global q(η | s(D)) + flujo local q(λ_j | η, s_j, s(D))."""

    def __init__(self, canales: int, dim_cov: int, dim_tam: int, dim_eta: int, dim_lam: int = 2, con_clase: bool = False):
        super().__init__()
        self.con_clase = con_clase
        dim_contexto = dim_eta + DIM_UNIDAD + DIM_DATASET
        self.codificador = CodificadorSeries(canales, dim_cov, dim_tam)
        self.flujo = FlujoCondicional(dim_eta, DIM_DATASET, capas=8, ocultas=(128, 128))
        self.local = FlujoCondicional(dim_lam, dim_contexto + int(con_clase), capas=6, ocultas=(128, 128))
        if con_clase:        # P(z_j = 1 | η, s_j, s(D)): el estado discreto de la unidad
            self.clase = nn.Sequential(nn.Linear(dim_contexto, 128), nn.ReLU(), nn.Linear(128, 128), nn.ReLU(), nn.Linear(128, 1))

    def contexto_local(self, eta: Tensor, s_j: Tensor, s_d: Tensor) -> Tensor:
        """[η estandarizado, s_j, s(D)] por unidad. eta (..., B, d), s_j (B, U, c), s_d (B, c) → (..., B, U, c_total)."""
        eta_z = (eta - self.flujo.media_theta) / self.flujo.escala_theta
        forma = eta.shape[:-1] + (s_j.shape[1],)
        partes = [eta_z.unsqueeze(-2), s_j, s_d.unsqueeze(-2)]
        return torch.cat([p.expand(forma + (p.shape[-1],)) for p in partes], dim=-1)

    def perdida(self, lote: dict[str, Tensor]) -> tuple[Tensor, dict[str, float]]:
        """−log q(η | s(D)) − promedio_j log q(λ_j | η, s_j, s(D)), con el η verdadero como condición del flujo local.

        Con estado discreto: q(λ_j, z_j | ·) = q(z_j | η, s_j, s(D)) · q(λ_j | z_j, η, s_j, s(D)); se suma la entropía cruzada de z_j.
        """
        s_d, s_j = self.codificador(lote["x"], lote["mascara"], lote["cov"], lote["tam"])
        global_ = -self.flujo.log_prob(lote["eta"], s_d).mean()
        hay = lote["mascara"].sum(-1) > 0                                              # (B, U)
        contexto, lam = self.contexto_local(lote["eta"], s_j, s_d)[hay], lote["lam"][hay]
        partes = {}
        clase = torch.zeros((), device=global_.device)
        if self.con_clase:
            z, lam = lam[:, -1:], lam[:, :-1]
            clase = nn.functional.binary_cross_entropy_with_logits(self.clase(contexto), z)
            contexto = torch.cat([contexto, z], dim=-1)
            partes["clase"] = float(clase.detach())
        local = -self.local.log_prob(lam, contexto).mean()
        return global_ + local + clase, {"global": float(global_.detach()), "local": float(local.detach()), **partes}

    def muestrear_locales(self, contexto: Tensor, ruido: Tensor, uniforme: Tensor | None = None) -> Tensor:
        """λ_j dado el contexto y el ruido. Con estado discreto, z_j = 1 si `uniforme` < P(z_j = 1), y va como última columna."""
        if not self.con_clase:
            return self.local.muestrear_con_ruido(contexto, ruido)
        z = (uniforme < torch.sigmoid(self.clase(contexto)[..., 0])).to(contexto.dtype).unsqueeze(-1)
        return torch.cat([self.local.muestrear_con_ruido(torch.cat([contexto, z], dim=-1), ruido), z], dim=-1)

    @torch.no_grad()
    def muestrear(self, lote: dict[str, Tensor], muestras: int) -> tuple[Tensor, Tensor]:
        """`muestras` de η y, por cada una, una de cada λ_j: (L, B, d) y (L, B, U, d_local [+ 1 con estado discreto])."""
        s_d, s_j = self.codificador(lote["x"], lote["mascara"], lote["cov"], lote["tam"])
        eta = self.flujo.muestrear(s_d, muestras)
        contexto = self.contexto_local(eta, s_j, s_d)
        forma = contexto.shape[:-1]
        lam = self.muestrear_locales(contexto, torch.randn(*forma, self.local.dim_theta, device=contexto.device), torch.rand(*forma, device=contexto.device))
        return eta, lam


# ------------------------------------------------------------------------------ construir, simular en tensores

def construir(esp: ModuleType) -> RedSeries:
    return RedSeries(esp.CANALES, esp.DIM_COV, esp.DIM_TAM, len(esp.NOMBRES_ETA), len(esp.NOMBRES_LAM), bool(getattr(esp, "CON_CLASE", False)))


_TENSORES = ("x", "mascara", "cov", "tam", "eta", "lam")


def a_tensores(lote: dict, dispositivo: torch.device | str = "cpu") -> dict[str, Tensor]:
    return {k: torch.as_tensor(np.asarray(lote[k]), dtype=torch.float32, device=dispositivo) for k in _TENSORES}


def fijar_escalas(red: RedSeries, esp: ModuleType, semilla: int = 0, lotes: int = 40, lote: int = 256) -> None:
    """La estandarización de η y de λ, con muestras del prior (incluido el a priori de tamaño). Una vez, antes de entrenar."""
    gen = np.random.default_rng(semilla)
    etas, lams = [], []
    for _ in range(lotes):
        sim = esp.simular(gen, lote)
        etas.append(sim["eta"]); lams.append(sim["lam"][sim["mascara"].sum(-1) > 0])
    red.flujo.fijar_escala(torch.as_tensor(np.concatenate(etas), dtype=torch.float32))
    red.local.fijar_escala(torch.as_tensor(np.concatenate(lams)[:, : red.local.dim_theta], dtype=torch.float32))


def configuracion(esp: ModuleType, **extra) -> dict:
    """Lo que el servicio necesita saber de la red: formas fijas del ONNX, nombres de los parámetros y el diseño de tamaños."""
    return {"motor_id": esp.MOTOR_ID, "nombres_eta": list(esp.NOMBRES_ETA), "nombres_lam": list(esp.NOMBRES_LAM),
            "canales": esp.CANALES, "dim_cov": esp.DIM_COV, "dim_tam": esp.DIM_TAM, "con_clase": bool(getattr(esp, "CON_CLASE", False)),
            "max_unidades": int(esp.DISENO["unidades"][1]), "max_lecturas": int(esp.DISENO["lecturas"][1]),
            "diseno": {k: list(v) for k, v in esp.DISENO.items()}, "prior": dict(getattr(esp, "PRIOR", {})),
            "arquitectura": "codificador por unidad (convoluciones 1D con máscara) + atención sobre unidades + "
                            "flujo de acoplamiento afín global (8 capas) y local compartido (6 capas); NPE factorizada",
            **extra}


# ------------------------------------------------------------------------------ entrenar

def entrenar_motor(esp: ModuleType, argv: list[str] | None = None) -> None:
    """La línea de comandos de `motor/<id>/entrenar.py`: datasets simulados al vuelo, con su tamaño sorteado en cada lote."""
    import argparse
    from motor.comun.entrenar import elegir_dispositivo, entrenar
    p = argparse.ArgumentParser(description=f"Entrena la red del motor {esp.MOTOR_ID}")
    p.add_argument("--minutos", type=float, default=None)
    p.add_argument("--hasta", type=str, default=None, help="HH:MM")
    p.add_argument("--dispositivo", default="cpu", choices=("auto", "cpu", "mps"))
    p.add_argument("--lote", type=int, default=128)
    p.add_argument("--tasa", type=float, default=5e-4)
    p.add_argument("--guardar-cada-min", type=float, default=10.0)
    p.add_argument("--carpeta", type=Path, default=Path("motor/checkpoints") / esp.MOTOR_ID)
    p.add_argument("--semilla", type=int, default=0)
    p.add_argument("--nuevo", action="store_true", help="ignora el punto de guardado y parte de cero")
    a = p.parse_args(argv)

    torch.manual_seed(a.semilla)
    dispositivo = elegir_dispositivo(a.dispositivo)
    red = construir(esp)
    retomar = not a.nuevo and (a.carpeta / "ultimo.pt").exists()
    pasos_previos = 0
    if retomar:
        pasos_previos = torch.load(a.carpeta / "ultimo.pt", map_location="cpu", weights_only=False).get("pasos", 0)
    else:
        fijar_escalas(red, esp, a.semilla)
    red.to(dispositivo)
    gen = np.random.default_rng([a.semilla, pasos_previos])          # al retomar no se repiten las simulaciones

    def perdida_de_lote():
        return red.perdida(a_tensores(esp.simular(gen, a.lote), dispositivo))

    entrenar(red, perdida_de_lote, a.lote, a.carpeta, minutos=a.minutos, hasta=a.hasta, guardar_cada_min=a.guardar_cada_min,
             tasa=a.tasa, retomar=retomar, config=configuracion(esp, lote=a.lote, dispositivo=str(dispositivo), tasa=a.tasa, semilla=a.semilla))


def cargar_red(esp: ModuleType, punto: Path | None = None) -> tuple[RedSeries, dict]:
    """La red del último punto de guardado (o de `punto`) y su progreso. Sin punto de guardado: la red sin entrenar."""
    punto = punto or Path("motor/checkpoints") / esp.MOTOR_ID / "ultimo.pt"
    red = construir(esp)
    if not Path(punto).exists():
        fijar_escalas(red, esp)
        return red.eval(), {"pasos": 0, "datasets_simulados": 0, "segundos": 0.0, "entrenada": False}
    estado = torch.load(punto, map_location="cpu", weights_only=False)
    red.load_state_dict(estado["modulo"])
    return red.eval(), {k: estado.get(k, 0) for k in ("pasos", "datasets_simulados", "segundos")} | {"entrenada": True}


# ------------------------------------------------------------------------------ exportar

def exportar(esp: ModuleType, red: RedSeries, carpeta: Path, progreso: dict | None = None) -> dict:
    """Deja en `carpeta` lo que el servicio lee: `codificador.onnx` (formas fijas con relleno), `flujo.npz`, `flujo_local.npz`,
    `config.json` y `pesos.pt`. Devuelve la diferencia máxima entre torch y onnxruntime, y entre torch y NumPy en los dos flujos."""
    from nucleo import flujo as flujo_np, series as series_np
    carpeta = Path(carpeta)
    carpeta.mkdir(parents=True, exist_ok=True)
    red = red.eval().cpu()
    u_max, k_max = int(esp.DISENO["unidades"][1]), int(esp.DISENO["lecturas"][1])
    sim = a_tensores(esp.simular(np.random.default_rng(0), 1))
    u, k = sim["mascara"].shape[1:]
    ejemplo = (torch.zeros(1, u_max, k_max, esp.CANALES), torch.zeros(1, u_max, k_max), torch.zeros(1, u_max, esp.DIM_COV), sim["tam"])
    ejemplo[0][0, :u, :k], ejemplo[1][0, :u, :k], ejemplo[2][0, :u] = sim["x"][0], sim["mascara"][0], sim["cov"][0]
    ruta = str(carpeta / "codificador.onnx")
    exportar_onnx(red.codificador, ejemplo, ruta, ["x", "mascara", "cov", "tam"], None, nombres_salida=("resumen", "resumen_unidades"))
    dif_onnx = comparar_con_onnxruntime(red.codificador, ruta, ejemplo)
    red.flujo.exportar_npz(str(carpeta / "flujo.npz"))
    cabeza = {}
    if red.con_clase:        # la cabeza del estado discreto viaja en el mismo archivo que el flujo local
        lineales = [m for m in red.clase if isinstance(m, nn.Linear)]
        cabeza = {"clase_n": np.int64(len(lineales))}
        for j, lineal in enumerate(lineales):
            cabeza[f"clase_W{j}"], cabeza[f"clase_b{j}"] = lineal.weight.detach().numpy(), lineal.bias.detach().numpy()
    red.local.exportar_npz(str(carpeta / "flujo_local.npz"), **cabeza)
    # NumPy contra torch, con los mismos pesos y el mismo ruido, en los dos flujos (regla 3 de AGENTS.md).
    with torch.no_grad():
        s_d, s_j = red.codificador(sim["x"], sim["mascara"], sim["cov"], sim["tam"])
        ruido = torch.randn(16, 1, red.flujo.dim_theta)
        eta = red.flujo.muestrear_con_ruido(s_d, ruido)
        contexto = red.contexto_local(eta, s_j, s_d)
        ruido_l, uniforme = torch.randn(*contexto.shape[:-1], red.local.dim_theta), torch.rand(*contexto.shape[:-1])
        lam = red.muestrear_locales(contexto, ruido_l, uniforme)
    f, fl = flujo_np.cargar(str(carpeta / "flujo.npz")), flujo_np.cargar(str(carpeta / "flujo_local.npz"))
    eta_np = flujo_np.muestrear(f, s_d.numpy(), ruido.numpy())
    contexto_np = series_np.contexto_local(f, eta_np[:, :, None, :], s_j.numpy()[None], s_d.numpy()[None, :, None, :], tuple(contexto.shape[:-1]))
    lam_np = series_np.muestrear_locales(fl, contexto_np, ruido_l.numpy(), uniforme.numpy())
    diferencias = {"onnx": dif_onnx, "flujo_numpy": float(np.abs(eta_np - eta.numpy()).max()), "flujo_local_numpy": float(np.abs(lam_np - lam.numpy()).max())}
    torch.save(red.state_dict(), carpeta / "pesos.pt")
    progreso = progreso or {}
    config = configuracion(esp, entrenada=bool(progreso.get("entrenada", False)), pasos=int(progreso.get("pasos", 0)),
                           simulaciones_entrenamiento=int(progreso.get("datasets_simulados", 0)),
                           entrenamiento_min=round(float(progreso.get("segundos", 0.0)) / 60, 1), diferencias_exportacion=diferencias)
    (carpeta / "config.json").write_text(json.dumps(config, indent=1, ensure_ascii=False) + "\n", encoding="utf-8")
    return diferencias


# ------------------------------------------------------------------------------ validar sin MCMC: SBC y cobertura por tramos de tamaño

def _resumen_rangos(rangos: np.ndarray, verdad: np.ndarray, medias: np.ndarray, muestras: int) -> dict:
    """Por parámetro: χ² de uniformidad del rango (10 cajas), rango medio, cobertura del 90% y recuperación."""
    cajas = np.histogram(rangos, bins=10, range=(0, muestras + 1))[0]
    esperado = len(rangos) / 10
    r = np.corrcoef(verdad, medias)[0, 1] if np.std(verdad) > 0 and np.std(medias) > 0 else 0.0
    return {"chi2_uniformidad": round(float(((cajas - esperado) ** 2 / esperado).sum()), 2),
            "rango_medio": round(float(rangos.mean() / muestras), 4),
            "cobertura_90": round(float(validacion.dentro_del_rango(rangos, muestras).mean()), 4),
            "recuperacion": round(float(r), 3), "n": int(len(rangos))}


def tramos_de_tamano(diseno: dict) -> list[tuple[str, int, int]]:
    """Tres tramos del número de unidades, de igual ancho en log: (nombre, desde, hasta), ambos incluidos."""
    u_min, u_max = diseno["unidades"]
    cortes = np.round(np.exp(np.linspace(np.log(u_min), np.log(u_max + 1), 4))).astype(int)
    cortes[0], cortes[-1] = u_min, u_max + 1
    return [(f"{a} a {b - 1} unidades", int(a), int(b - 1)) for a, b in zip(cortes[:-1], cortes[1:])]


@torch.no_grad()
def sbc(esp: ModuleType, red: RedSeries, datasets: int = 2000, muestras: int = 99, lote: int = 20, semilla: int = 12345) -> dict:
    """Calibración basada en simulación en datasets nuevos, sin MCMC: η (global), λ_j (local) y lo que se decide.

    Para cada dataset simulado se sacan `muestras` del posterior amortizado y se cuenta cuántas quedan bajo el valor
    verdadero (el rango). Devuelve el resumen por parámetro, la cobertura del 90% de lo que se decide y lo mismo por
    tramos del número de unidades, con el peor tramo: el sello informa ese y no solo el promedio.
    """
    red = red.eval().cpu()
    gen = np.random.default_rng(semilla)
    torch.manual_seed(semilla)
    r_eta, v_eta, m_eta, tam_eta = [], [], [], []
    r_lam, v_lam, m_lam = [], [], []
    r_dec, tam_dec, lec_dec = [], [], []
    hechos = 0
    while hechos < datasets:
        sim = esp.simular(gen, lote)
        t = a_tensores(sim)
        eta, lam = red.muestrear(t, muestras)                                     # (L, B, d), (L, B, U, 2)
        eta, lam = eta.numpy(), lam.numpy()
        hay = sim["mascara"].sum(-1) > 0                                          # (B, U)
        U = hay.shape[1]
        r_eta.append((eta < sim["eta"][None]).sum(0)); v_eta.append(sim["eta"]); m_eta.append(eta.mean(0)); tam_eta.append(np.full(lote, U))
        r_lam.append((lam < sim["lam"][None]).sum(0)[hay]); v_lam.append(sim["lam"][hay]); m_lam.append(lam.mean(0)[hay])
        cantidad = esp.cantidad_de(eta, lam, sim["extra"])                        # (L, B, U)
        r_dec.append((cantidad < sim["cantidad"][None]).sum(0)[hay]); tam_dec.append(np.full(int(hay.sum()), U))
        lec_dec.append(sim["mascara"].sum(-1)[hay])
        hechos += lote
    r_eta, v_eta, m_eta, tam_eta = map(np.concatenate, (r_eta, v_eta, m_eta, tam_eta))
    r_lam, v_lam, m_lam = map(np.concatenate, (r_lam, v_lam, m_lam))
    r_dec, tam_dec, lec_dec = map(np.concatenate, (r_dec, tam_dec, lec_dec))

    globales = {n: _resumen_rangos(r_eta[:, i], v_eta[:, i], m_eta[:, i], muestras) for i, n in enumerate(esp.NOMBRES_ETA)}
    locales = {n: _resumen_rangos(r_lam[:, i], v_lam[:, i], m_lam[:, i], muestras) for i, n in enumerate(esp.NOMBRES_LAM)}
    dentro_eta = validacion.dentro_del_rango(r_eta, muestras)
    dentro_dec = validacion.dentro_del_rango(r_dec, muestras)
    por_tramo = []
    for nombre, desde, hasta in tramos_de_tamano(esp.DISENO):
        en_eta, en_dec = (tam_eta >= desde) & (tam_eta <= hasta), (tam_dec >= desde) & (tam_dec <= hasta)
        if en_eta.sum() < 30:
            continue
        por_tramo.append({"tramo": nombre, "datasets": int(en_eta.sum()), "unidades": int(en_dec.sum()),
                          "cobertura_90_parametros": round(float(dentro_eta[en_eta].mean()), 4),
                          "cobertura_90_decision": round(float(dentro_dec[en_dec].mean()), 4)})
    # Otro corte del diseño: unidades con pocas lecturas contra unidades con muchas (la mediana parte en dos).
    mediana = float(np.median(lec_dec))
    for nombre, en in (("unidades con pocas lecturas", lec_dec <= mediana), ("unidades con muchas lecturas", lec_dec > mediana)):
        if en.sum() >= 30:
            por_tramo.append({"tramo": nombre, "datasets": None, "unidades": int(en.sum()),
                              "cobertura_90_parametros": None, "cobertura_90_decision": round(float(dentro_dec[en].mean()), 4)})
    peor = min(por_tramo, key=lambda t: t["cobertura_90_decision"]) if por_tramo else None
    pasa_g, fallan_g = validacion.sbc_sin_sesgo(globales)
    pasa_l, fallan_l = validacion.sbc_sin_sesgo(locales)
    return {"datasets": int(hechos), "muestras": muestras, "globales": globales, "locales": locales,
            "sbc_global_pasa": pasa_g, "sbc_global_fallan": fallan_g, "sbc_local_pasa": pasa_l, "sbc_local_fallan": fallan_l,
            "cobertura_90_parametros": round(float(dentro_eta.mean()), 4),
            "cobertura_90_locales": round(float(validacion.dentro_del_rango(r_lam, muestras).mean()), 4),
            "cobertura_90_decision": round(float(dentro_dec.mean()), 4),
            "por_tramo": por_tramo, "peor_grupo": peor["tramo"] if peor else None,
            "cobertura_90_peor_grupo": peor["cobertura_90_decision"] if peor else None}


def sello(esp: ModuleType, informe_sbc: dict, progreso: dict, latencia_ms: int | None, examen: dict | None,
          limitaciones: list[str], ensayo: bool = False, mcmc: dict | None = None) -> dict:
    """El sello de un motor de series. Se escribe sin el MCMC de referencia: sus campos van en `null` y «pasa» se decide
    con el SBC, la cobertura y la latencia. La comparación con el MCMC se agrega (`mcmc`) cuando exista, tal como salga."""
    entre = lambda v: v is not None and 0.85 <= v <= 0.95          # noqa: E731
    criterios = {
        "sbc_sin_sesgo": bool(informe_sbc["sbc_global_pasa"]),
        "sbc_local_sin_sesgo": bool(informe_sbc["sbc_local_pasa"]),
        "cobertura_parametros_entre_85_y_95": entre(informe_sbc["cobertura_90_parametros"]),
        "cobertura_decision_entre_85_y_95": entre(informe_sbc["cobertura_90_decision"]),
        "peor_grupo_sobre_80": informe_sbc["cobertura_90_peor_grupo"] is not None and informe_sbc["cobertura_90_peor_grupo"] >= 0.80,
        "analisis_bajo_1_s": latencia_ms is not None and latencia_ms < 1000,
    }
    mcmc = mcmc or {}
    if mcmc.get("mcmc_diferencia_media") is not None:
        criterios["mcmc_bajo_0_3"] = mcmc["mcmc_diferencia_media"] < 0.3
    return {
        "motor_id": esp.MOTOR_ID, "implementacion": "red", "pasa": all(criterios.values()) and not ensayo, "criterios": criterios,
        "simulaciones_entrenamiento": int(progreso.get("datasets_simulados", 0)),
        "entrenamiento_min": round(float(progreso.get("segundos", 0.0)) / 60),
        "casos_validacion": informe_sbc["datasets"],
        "cobertura_90": informe_sbc["cobertura_90_decision"], "cobertura_90_parametros": informe_sbc["cobertura_90_parametros"],
        "cobertura_90_locales": informe_sbc["cobertura_90_locales"],
        "cobertura_90_peor_grupo": informe_sbc["cobertura_90_peor_grupo"], "peor_grupo": informe_sbc["peor_grupo"], "peor_grupo_de": "tamaño del archivo",
        "sbc_pasa": bool(informe_sbc["sbc_global_pasa"]), "sbc_local_pasa": bool(informe_sbc["sbc_local_pasa"]),
        "recuperacion": validacion.recuperacion(informe_sbc["globales"]),
        "rangos": {k: list(v) for k, v in esp.DISENO.items()},
        "latencia_ms": latencia_ms, "examen": examen,
        "mcmc_datasets_comparados": mcmc.get("mcmc_datasets_comparados"), "mcmc_s_por_dataset": mcmc.get("mcmc_s_por_dataset"),
        "mcmc_diferencia_media": mcmc.get("mcmc_diferencia_media"), "mcmc_r_hat_max": mcmc.get("mcmc_r_hat_max"),
        "amortizacion": mcmc.get("amortizacion"),
        "fecha": time.strftime("%Y-%m-%d"), "hora": time.strftime("%H:%M"), "ensayo": ensayo, "limitaciones": limitaciones,
    }
