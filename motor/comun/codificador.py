"""Codificador de conjuntos (DeepSets) con pooling de atención y máscara de relleno.

Un dataset D es un conjunto de filas: su orden no lleva información. El codificador lo
comprime en un vector de tamaño fijo, el resumen s(D), que condiciona al estimador de la
posterior. La arquitectura es phi por fila -> pooling con máscara -> rho, que es
invariante a permutaciones de las filas por construcción.

Los conjuntos de un lote tienen tamaños distintos, así que se rellenan hasta un n común y
una máscara de relleno (1 = fila real, 0 = relleno) indica qué filas cuentan.
"""

import torch
from torch import Tensor, nn

# Se resta a los logits del relleno para que nunca sean el máximo del conjunto.
MUY_NEGATIVO = 1e9


class PoolingAtencion(nn.Module):
    """Pooling de atención con máscara sobre el penúltimo eje.

    Cada cabeza aprende un logit por fila; los pesos son un softmax con máscara sobre las
    n filas y la salida es la suma ponderada de h, una por cabeza, concatenadas.
    Acepta ejes delanteros arbitrarios, así que sirve igual para filas -> grupo que para
    grupos -> dataset en un codificador jerárquico.

    Atributo `dim_salida`: tamaño del último eje de la salida, `cabezas * dim`.
    """

    def __init__(self, dim: int, cabezas: int = 4):
        super().__init__()
        self.logits = nn.Linear(dim, cabezas)
        self.dim_salida = cabezas * dim

    def forward(self, h: Tensor, mascara: Tensor) -> Tensor:
        """h: (..., n, dim); mascara: (..., n) con 1 = fila real -> (..., cabezas * dim).

        Un conjunto vacío (máscara toda en cero) devuelve ceros, no NaN.
        """
        m = mascara.unsqueeze(-1)  # (..., n, 1)
        logits = self.logits(h)  # (..., n, cabezas)
        # Softmax con máscara, estable y sin -inf: se resta el máximo sobre las filas
        # reales; multiplicar por m antes del exp impide que el relleno desborde.
        maximo = (logits - (1.0 - m) * MUY_NEGATIVO).amax(dim=-2, keepdim=True)
        pesos = torch.exp((logits - maximo) * m) * m
        # La fila del máximo aporta exp(0) = 1, así que la suma es >= 1 salvo en el
        # conjunto vacío, donde vale 0: acotarla por 1 evita 0/0 sin sesgar los pesos.
        pesos = pesos / pesos.sum(dim=-2, keepdim=True).clamp(min=1.0)
        # (..., cabezas, n) @ (..., n, dim) -> (..., cabezas, dim)
        return (pesos.transpose(-1, -2) @ h).flatten(start_dim=-2)


class PoolingPromedio(nn.Module):
    """Promedio con máscara sobre el penúltimo eje (plan B si la atención no exporta).

    Atributo `dim_salida`: tamaño del último eje de la salida, `dim`.
    """

    def __init__(self, dim: int):
        super().__init__()
        self.dim_salida = dim

    def forward(self, h: Tensor, mascara: Tensor) -> Tensor:
        """h: (..., n, dim); mascara: (..., n) -> (..., dim). Conjunto vacío -> ceros."""
        m = mascara.unsqueeze(-1)
        # Con máscara binaria el conteo es >= 1 salvo en el conjunto vacío.
        return (h * m).sum(dim=-2) / m.sum(dim=-2).clamp(min=1.0)


class CodificadorConjunto(nn.Module):
    """Codificador de conjuntos: filas de D -> resumen s(D), invariante a permutaciones."""

    def __init__(
        self,
        dim_fila: int,
        dim_oculta: int = 128,
        dim_resumen: int = 128,
        pooling: str = "atencion",
    ):
        super().__init__()
        if pooling not in ("atencion", "promedio"):
            raise ValueError(f"pooling desconocido: {pooling!r}")
        # phi: se aplica a cada fila por separado.
        self.phi = nn.Sequential(
            nn.Linear(dim_fila, dim_oculta), nn.ReLU(), nn.Linear(dim_oculta, dim_oculta), nn.ReLU()
        )
        self.pooling = PoolingAtencion(dim_oculta) if pooling == "atencion" else PoolingPromedio(dim_oculta)
        # rho: se aplica una vez al conjunto ya agregado.
        self.rho = nn.Sequential(
            nn.Linear(self.pooling.dim_salida, dim_oculta), nn.ReLU(), nn.Linear(dim_oculta, dim_resumen)
        )

    def forward(self, x: Tensor, mascara: Tensor) -> Tensor:
        """x: (B, n, dim_fila); mascara: (B, n) -> resumen s(D): (B, dim_resumen)."""
        return self.rho(self.pooling(self.phi(x), mascara))


def exportar_onnx(
    modulo: nn.Module,
    ejemplo: tuple[Tensor, ...],
    ruta: str,
    nombres_entrada: list[str],
    ejes_dinamicos: dict,
    nombres_salida: tuple[str, ...] = ("resumen",),
) -> None:
    """Exporta `modulo` a ONNX dejando dinámicos los ejes indicados (el lote y n).

    `ejes_dinamicos` va por nombre de entrada: {"x": {0: "lote", 1: "n"}, ...}. Los
    nombres de entrada deben coincidir con los argumentos de `forward`. Conviene que el
    ejemplo tenga lote > 1 para que el exportador no fije el lote en 1.

    Ojo: el optimizador de este exportador elimina sumas con constantes muy chicas
    (`x + 1e-8` desaparece del grafo), así que un `+ eps` no protege una división en
    ONNX. Por eso los poolings acotan el denominador con `clamp(min=1.0)`.

    Deja un solo archivo: sin `external_data=False` el exportador escribe los pesos aparte,
    en `<ruta>.data`, y el servicio y git necesitarían los dos.
    """
    modulo.eval()
    torch.onnx.export(
        modulo,
        ejemplo,
        ruta,
        input_names=nombres_entrada,
        output_names=list(nombres_salida),
        dynamic_shapes=ejes_dinamicos,
        dynamo=True,
        external_data=False,   # los pesos van dentro: un solo archivo, que es lo que versiona el contrato
        verbose=False,
    )


def comparar_con_onnxruntime(modulo: nn.Module, ruta: str, entradas: tuple[Tensor, ...]) -> float:
    """Máxima diferencia absoluta entre las salidas de torch y las de onnxruntime (todas las salidas)."""
    import onnxruntime

    sesion = onnxruntime.InferenceSession(ruta, providers=["CPUExecutionProvider"])
    nombres = [entrada.name for entrada in sesion.get_inputs()]
    salidas_onnx = sesion.run(None, {n: t.numpy() for n, t in zip(nombres, entradas)})
    modulo.eval()
    with torch.no_grad():
        salidas_torch = modulo(*entradas)
    if isinstance(salidas_torch, Tensor):
        salidas_torch = (salidas_torch,)
    return max(float(abs(t.numpy() - o).max()) for t, o in zip(salidas_torch, salidas_onnx))
