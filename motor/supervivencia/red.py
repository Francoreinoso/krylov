"""Red de `supervivencia`: codificador jerárquico del dataset y flujo normalizador condicional (NPE).

El modelo generativo (WORKPLAN.md, 11.2) es jerárquico: personas dentro de cargos dentro de una
empresa. El codificador sigue esa estructura, filas → cargo → dataset, y entrega el resumen s(D);
el flujo de acoplamiento afín de `motor/comun/flujo.py` entrega q(θ | s(D)) sobre los 32 parámetros
globales en espacio sin restricciones. La pérdida es NPE: −log q(θ | s(D)) sobre datasets simulados.
"""
from __future__ import annotations

import numpy as np
import torch
from torch import Tensor, nn

from motor.comun.codificador import PoolingAtencion
from motor.comun.flujo import FlujoCondicional
from motor.supervivencia import simular
from nucleo import supervivencia as nucleo_sv

ARQUITECTURA = {"dim_oculta": 128, "dim_resumen": 128, "capas_flujo": 8, "cargos_max": simular.CARGOS_MAX}


ESCALA_COVARIANZA = 4.0     # las covarianzas entre columnas son del orden de 0,1: se llevan a orden 1
ESCALA_ENTRE_CARGOS = 8.0   # las covarianzas entre promedios de cargo son del orden de 0,01 a 0,1 (el sueldo, hasta 1)

# Columnas de la fila de `nucleo.supervivencia.armar_filas`.
COL_SUELDO, COL_ENCUESTAS, COL_ANOS, COL_RENUNCIO, COL_POR_DECIDIR = 3, slice(4, 8), 8, 9, 10
CENTRO_ANOS = 1.8           # lo que `armar_filas` le resta a log(1 + años)
# Nudos de los resúmenes por tramos. Los años vienen en enteros: hasta 10, cada año tiene su tramo.
NIVELES_ENCUESTA = (1.0, 2.0, 3.0, 4.0)
NUDOS_ANOS = tuple(float(np.log1p(a)) for a in (0, 1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 12, 15, 20, 25, 30, 40, 60))
NUDOS_SUELDO = (-3.0, -2.0, -1.0, 0.0, 1.0, 2.0, 3.0)
CAPA_AMPLIADA = "codificador.rho.0.weight"   # la capa que recibe los resúmenes: la única que cambia de forma entre versiones
ESCALAS_DE_ATAJOS = ("codificador.media_atajos", "codificador.escala_atajos")
TOPE_ATAJO = 4.0            # los atajos nuevos entran estandarizados y recortados a ±4 desviaciones (varios tienen colas largas)
DECAIMIENTO_PROMEDIO = 0.9998   # promedio móvil de los pesos: horizonte de unos 5.000 pasos


def _mlp(entrada: int, oculta: int, salida: int) -> nn.Sequential:
    return nn.Sequential(nn.Linear(entrada, oculta), nn.ReLU(), nn.Linear(oculta, salida), nn.ReLU())


def sombreros(u: Tensor, nudos: Tensor) -> Tensor:
    """Funciones sombrero (interpolación lineal) sobre `nudos`: u (...) → (..., K), y cada fila suma 1.

    En un nudo vale 1 la función de ese nudo y 0 las demás: con valores enteros (el nivel de una encuesta, los años
    hasta 10) es el indicador de cada valor, y su promedio sobre las personas, la frecuencia. Fuera de los nudos
    extremos se queda en el extremo.
    """
    u = torch.maximum(torch.minimum(u, nudos[-1]), nudos[0]).unsqueeze(-1)
    sube = ((u - nudos[:-1]) / (nudos[1:] - nudos[:-1])).clamp(0.0, 1.0)       # (..., K−1): 0 antes de cada tramo, 1 después
    return torch.cat([torch.ones_like(u), sube], dim=-1) - torch.cat([sube, torch.zeros_like(u)], dim=-1)


class CodificadorSupervivencia(nn.Module):
    """Codificador de conjuntos jerárquico: filas → cargo → dataset. Invariante al orden de las filas
    y al nombre de los cargos, con n y número de cargos variables.

    Parte aprendida:
    - phi resume cada persona (fila de 11 números de `nucleo.supervivencia.armar_filas`).
    - Por cargo: promedio de sus filas y su tamaño, pasados por psi.
    - Dos poolings de atención hacia el dataset: uno sobre las filas y otro sobre los cargos.

    Atajos: estadísticos escritos a mano que entran directo a rho, junto a lo aprendido. Cada uno existe porque la
    validación mostró que la parte aprendida no lo extraía sola (`estado/amortizacion.md`, sáb 03:53 y sáb 11:00):
    - Segundo orden: promedio y covarianza de las 11 columnas. Los efectos β y λ y las cargas de las encuestas se
      identifican por covarianzas entre columnas (horas extra × renuncia, encuesta × encuesta).
    - Entre cargos: covarianza, ponderada por tamaño, de los promedios por cargo de las 11 columnas, su diagonal en
      logaritmo y la dispersión entre cargos (también en logaritmo) de lo que psi resume. Es de donde sale σ_u (la dispersión entre cargos):
      un pooling que promedia cargos no ve cuánto difieren. Contra el MCMC, la red anterior devolvía casi el prior.
    - Por tramos: cuántas personas hay, cuántas renunciaron, cuántas están por decidir y cuántos años llevan, por
      nivel de cada encuesta, por año en la empresa y por tramo de sueldo. Las frecuencias por nivel son el
      estadístico de los cortes (promedio y varianza dejan libre un grado de libertad de tres); el histograma de
      años por estado, el de la censura (μ_c, s_c) y de la forma k; los tramos de sueldo, el del spline γ.
    - Pares de encuestas: la tabla de 4 × 4 de cada par de ítems (las cargas a_j).
    - Años por estado: promedio y dispersión de log(1 + años) entre quienes renunciaron, siguen o están por decidir.

    Los atajos de la segunda tanda (entre cargos, por tramos, pares, años por estado) entran estandarizados con su
    media y su desviación bajo el prior (`fijar_escala_atajos`), para que la capa que los recibe aprenda a usarlos
    al mismo ritmo aunque sus unidades sean distintas.

    rho junta todo, con log(n) y el número de cargos, en el resumen s(D).
    """

    def __init__(self, dim_oculta: int = 128, dim_resumen: int = 128, cargos_max: int = simular.CARGOS_MAX):
        super().__init__()
        self.cargos_max = cargos_max
        self.phi = _mlp(nucleo_sv.DIM_FILA, dim_oculta, dim_oculta)
        self.psi = _mlp(dim_oculta + 1, dim_oculta, dim_oculta)
        self.pooling_filas = PoolingAtencion(dim_oculta)
        self.pooling_cargos = PoolingAtencion(dim_oculta)
        # Constantes de los atajos: no son pesos ni van al punto de guardado.
        for nombre, nudos in (("niveles", NIVELES_ENCUESTA), ("nudos_anos", NUDOS_ANOS), ("nudos_sueldo", NUDOS_SUELDO)):
            self.register_buffer(nombre, torch.tensor(nudos, dtype=torch.float32), persistent=False)
        niveles, encuestas = len(NIVELES_ENCUESTA), nucleo_sv.N_ENCUESTAS
        pares = [(j * niveles + a) * encuestas * niveles + (k * niveles + b)
                 for j in range(encuestas) for k in range(j + 1, encuestas) for a in range(niveles) for b in range(niveles)]
        self.register_buffer("indice_pares", torch.tensor(pares, dtype=torch.long), persistent=False)

        momentos = nucleo_sv.DIM_FILA + nucleo_sv.DIM_FILA**2
        # Los atajos de la primera versión van primero y en el mismo orden: un punto de guardado anterior se carga
        # ampliando la primera capa de rho con columnas en cero a la derecha (`cargar_estado`).
        self.entrada_anterior = self.pooling_filas.dim_salida + self.pooling_cargos.dim_salida + momentos + 2
        tramos = encuestas * niveles + len(NUDOS_ANOS) + len(NUDOS_SUELDO)
        entre_cargos = nucleo_sv.DIM_FILA**2 + nucleo_sv.DIM_FILA + dim_oculta + 1
        self.entrada_nueva = entre_cargos + 4 * tramos + len(pares) + 6
        entrada_rho = self.entrada_anterior + self.entrada_nueva
        self.register_buffer("media_atajos", torch.zeros(self.entrada_nueva))
        self.register_buffer("escala_atajos", torch.ones(self.entrada_nueva))
        self.rho = nn.Sequential(nn.Linear(entrada_rho, 2 * dim_oculta), nn.ReLU(), nn.Linear(2 * dim_oculta, dim_resumen))

    def forward(self, filas: Tensor, grupo: Tensor) -> Tensor:
        """filas: (B, n, 11) float32; grupo: (B, n) enteros en 0..cargos_max−1 → s(D): (B, dim_resumen)."""
        anteriores, nuevos = self._entradas_de_rho(filas, grupo)
        nuevos = ((nuevos - self.media_atajos) / self.escala_atajos).clamp(-TOPE_ATAJO, TOPE_ATAJO)
        return self.rho(torch.cat([anteriores, nuevos], dim=-1))

    def _entradas_de_rho(self, filas: Tensor, grupo: Tensor) -> tuple[Tensor, Tensor]:
        """Lo que recibe rho, en dos partes: (lo aprendido y los atajos de la primera tanda, los atajos nuevos sin estandarizar)."""
        h = self.phi(filas)                                                        # (B, n, d)
        cargos = torch.arange(self.cargos_max, device=grupo.device)
        pertenece = (grupo.unsqueeze(-1) == cargos).to(h.dtype)                    # (B, n, G)
        tamano = pertenece.sum(dim=1)                                              # (B, G)
        por_cargo = pertenece.transpose(1, 2) / tamano.clamp(min=1.0).unsqueeze(-1)   # (B, G, n): promedia las filas de cada cargo
        h_cargo = self.psi(torch.cat([por_cargo @ h, torch.log1p(tamano).unsqueeze(-1) / 7.0], dim=-1))
        hay_cargo = (tamano > 0).to(h.dtype)
        todas = pertenece.sum(dim=-1)              # (B, n): 1 en cada fila con cargo válido
        n = tamano.sum(dim=1, keepdim=True)
        promedio_columnas = filas.mean(dim=1, keepdim=True)                        # (B, 1, 11)
        centradas = filas - promedio_columnas
        covarianza = (centradas.transpose(1, 2) @ centradas) / n.unsqueeze(-1)     # (B, 11, 11)
        anteriores = torch.cat(
            [
                promedio_columnas.squeeze(1),
                ESCALA_COVARIANZA * covarianza.flatten(start_dim=1),
                self.pooling_filas(h, todas),
                self.pooling_cargos(h_cargo, hay_cargo),
                torch.log(n) - 6.5,
                hay_cargo.sum(dim=1, keepdim=True) / self.cargos_max,
            ],
            dim=-1,
        )
        nuevos = torch.cat([*self._entre_cargos(filas, promedio_columnas, por_cargo, h_cargo, tamano / n), *self._por_tramos(filas, n)], dim=-1)
        return anteriores, nuevos

    @torch.no_grad()
    def fijar_escala_atajos(self, lotes) -> None:
        """Media y desviación de los atajos nuevos sobre empresas simuladas con el prior: `lotes` son pares (filas, grupo).

        Se fija una vez, antes de entrenar la capa que los recibe; queda en el punto de guardado y en el ONNX.
        """
        valores = torch.cat([self._entradas_de_rho(filas, grupo)[1] for filas, grupo in lotes])
        self.media_atajos.copy_(valores.mean(dim=0))
        self.escala_atajos.copy_(valores.std(dim=0).clamp_min(0.02))

    @staticmethod
    def _entre_cargos(filas: Tensor, promedio_columnas: Tensor, por_cargo: Tensor, h_cargo: Tensor, peso: Tensor) -> list[Tensor]:
        """Cuánto difieren los cargos entre sí. `peso` (B, G) es la fracción de la empresa en cada cargo (0 si está vacío)."""
        desvio = (por_cargo @ filas - promedio_columnas) * (peso > 0).to(filas.dtype).unsqueeze(-1)     # (B, G, 11)
        entre = (desvio * peso.unsqueeze(-1)).transpose(1, 2) @ desvio                                  # (B, 11, 11)
        dispersion = 0.5 * torch.log(torch.diagonal(entre, dim1=1, dim2=2).clamp(min=1e-5)) + 2.5       # log de la desviación, llevado a orden 1
        promedio_h = (h_cargo * peso.unsqueeze(-1)).sum(dim=1, keepdim=True)
        varianza_h = (((h_cargo - promedio_h) ** 2) * peso.unsqueeze(-1)).sum(dim=1)                    # (B, d)
        dispersion_h = 0.25 * torch.log(varianza_h.clamp(min=1e-8)) + 2.25                              # ídem: va de 1e-6 a 1e-2
        return [ESCALA_ENTRE_CARGOS * entre.flatten(start_dim=1), dispersion, dispersion_h, (peso**2).sum(dim=1, keepdim=True)]

    def _por_tramos(self, filas: Tensor, n: Tensor) -> list[Tensor]:
        """Frecuencias y resultados por nivel de cada encuesta, por año y por tramo de sueldo; pares de encuestas; años por estado."""
        anos, renuncio, por_decidir = filas[..., COL_ANOS], filas[..., COL_RENUNCIO], filas[..., COL_POR_DECIDIR]
        nivel = sombreros(1.5 * filas[..., COL_ENCUESTAS] + 2.5, self.niveles).flatten(start_dim=2)      # (B, n, 16): indicador de cada nivel
        tramos = torch.cat([nivel, sombreros(anos + CENTRO_ANOS, self.nudos_anos), sombreros(filas[..., COL_SUELDO], self.nudos_sueldo)], dim=-1)
        resultado = torch.stack([torch.ones_like(anos), renuncio, por_decidir, anos], dim=-1)           # (B, n, 4)
        cruzados = (tramos.transpose(1, 2) @ resultado) / n.unsqueeze(-1)                                # (B, tramos, 4)
        pares = ((nivel.transpose(1, 2) @ nivel) / n.unsqueeze(-1)).flatten(start_dim=1)[:, self.indice_pares]
        estado = torch.stack([renuncio, 1.0 - renuncio - por_decidir, por_decidir], dim=-1)             # (B, n, 3): renunció, sigue, por decidir
        potencias = torch.stack([torch.ones_like(anos), anos, anos**2], dim=-1)
        m = (estado.transpose(1, 2) @ potencias) / n.unsqueeze(-1)                                       # (B, 3, 3)
        fraccion = m[..., 0].clamp(min=1e-3)
        promedio = m[..., 1] / fraccion
        dispersion = 0.5 * torch.log((m[..., 2] / fraccion - promedio**2).clamp(min=1e-4)) + 1.0
        return [ESCALA_COVARIANZA * cruzados.flatten(start_dim=1), ESCALA_COVARIANZA * pares, promedio, dispersion]


class RedSupervivencia(nn.Module):
    """Estimador neuronal del posterior: q(θ | D) = flujo(θ | codificador(D)).

    Lleva además un promedio móvil exponencial de sus pesos (`promedio`). El último paso de un entrenamiento con
    lotes de 32 empresas deja cada peso un poco corrido por el ruido del gradiente; en parámetros con posterior
    muy angosto (los cortes de las encuestas, la censura) ese corrimiento es un sesgo visible en el SBC. El promedio
    de los últimos miles de pasos lo quita. Se valida y se exporta con el promedio (`usar_promedio`).
    """

    def __init__(self, dim_oculta: int = 128, dim_resumen: int = 128, capas_flujo: int = 8,
                 cargos_max: int = simular.CARGOS_MAX):
        super().__init__()
        self.codificador = CodificadorSupervivencia(dim_oculta, dim_resumen, cargos_max)
        self.flujo = FlujoCondicional(nucleo_sv.DIM_THETA, dim_resumen, capas=capas_flujo)
        self.promedio = nn.Module()
        for nombre, pesos in self._pesos():
            self.promedio.register_buffer(nombre, pesos.detach().clone())

    def _pesos(self):
        """Los pesos entrenables, con el nombre que llevan en `promedio` (un buffer no admite puntos en su nombre)."""
        return [(nombre.replace(".", "__"), pesos) for parte in ("codificador", "flujo")
                for nombre, pesos in getattr(self, parte).named_parameters(prefix=parte)]

    @torch.no_grad()
    def actualizar_promedio(self, decaimiento: float = DECAIMIENTO_PROMEDIO) -> None:
        """Un paso del promedio móvil: promedio ← decaimiento · promedio + (1 − decaimiento) · pesos."""
        for nombre, pesos in self._pesos():
            getattr(self.promedio, nombre).mul_(decaimiento).add_(pesos, alpha=1.0 - decaimiento)

    @torch.no_grad()
    def usar_promedio(self) -> "RedSupervivencia":
        """Pone el promedio móvil en los pesos (para validar y exportar; no para seguir entrenando)."""
        for nombre, pesos in self._pesos():
            pesos.copy_(getattr(self.promedio, nombre))
        return self

    def perdida(self, filas: Tensor, grupo: Tensor, theta: Tensor) -> Tensor:
        """Pérdida NPE: −log q(θ | s(D)), promediada sobre los datasets del lote."""
        return -self.flujo.log_prob(theta, self.codificador(filas, grupo)).mean()

    @torch.no_grad()
    def muestrear(self, filas: Tensor, grupo: Tensor, m: int) -> Tensor:
        """m muestras de q(θ | D) por dataset, en espacio sin restricciones: (m, B, 32)."""
        return self.flujo.muestrear(self.codificador(filas, grupo), m)


def lotes_del_prior(config: dict, semilla: int = 0, lotes: int = 48, por_lote: int = 16) -> list[tuple[Tensor, Tensor]]:
    """Empresas simuladas con el prior (y n al azar en su rango) para fijar la escala de los atajos del codificador."""
    rng = np.random.default_rng([semilla, 7])
    reales = simular.cargar_filas_reales(config)
    return [lote_a_tensores(simular.simular(rng, por_lote, simular.muestrear_n(rng, config), config, reales))[:2] for _ in range(lotes)]


def construir(config: dict | None = None, semilla: int = 0) -> RedSupervivencia:
    """Red sin entrenar, con la estandarización de θ fijada con 20.000 muestras del prior y la de los atajos con 768 empresas simuladas."""
    config = config or simular.cargar_config()
    torch.manual_seed(semilla)
    red = RedSupervivencia(**ARQUITECTURA)
    del_prior = nucleo_sv.a_libre(simular.muestrear_prior(np.random.default_rng(semilla), 20_000, config["prior"]))
    red.flujo.fijar_escala(torch.as_tensor(del_prior, dtype=torch.float32))
    red.codificador.fijar_escala_atajos(lotes_del_prior(config, semilla))
    red.promedio.load_state_dict({nombre: pesos.detach().clone() for nombre, pesos in red._pesos()})
    return red


def ampliar(pesos: Tensor, columnas: int) -> Tensor:
    """Agrega columnas en cero a la derecha hasta llegar a `columnas`."""
    return torch.cat([pesos, pesos.new_zeros(pesos.shape[0], columnas - pesos.shape[1])], dim=1)


def cargar_estado(red: RedSupervivencia, modulo: dict, config: dict | None = None) -> bool:
    """Carga los pesos de un punto de guardado. Devuelve True si venía de la red anterior a los atajos nuevos.

    En ese caso la primera capa de rho se amplía con columnas en cero para las entradas nuevas: la red cargada da
    el mismo s(D) que la anterior, y al seguir entrenando aprende a usarlas. Así el afinado parte de todo lo que la
    red ya practicó. La escala de esas entradas se fija ahí mismo con el prior vigente, y el promedio móvil de los
    pesos, si el punto no lo trae, parte igual a los pesos.
    """
    modulo = dict(modulo)
    columnas = red.state_dict()[CAPA_AMPLIADA].shape[1]
    ampliada = modulo[CAPA_AMPLIADA].shape[1] < columnas
    if ampliada:
        modulo[CAPA_AMPLIADA] = ampliar(modulo[CAPA_AMPLIADA], columnas)
    for nombre in ESCALAS_DE_ATAJOS:
        modulo.setdefault(nombre, red.state_dict()[nombre])
    for nombre, pesos in red._pesos():
        modulo.setdefault(f"promedio.{nombre}", modulo[nombre.replace("__", ".")].clone())
    red.load_state_dict(modulo)
    if ampliada:
        red.codificador.fijar_escala_atajos(lotes_del_prior(config or simular.cargar_config()))
    return ampliada


def lote_a_tensores(lote: dict, dispositivo: str = "cpu") -> tuple[Tensor, Tensor, Tensor]:
    """Lote del simulador (NumPy) → (filas, grupo, theta) en el dispositivo de entrenamiento."""
    return (
        torch.as_tensor(lote["filas"], device=dispositivo),
        torch.as_tensor(lote["grupo"], device=dispositivo),
        torch.as_tensor(lote["theta"], device=dispositivo),
    )
