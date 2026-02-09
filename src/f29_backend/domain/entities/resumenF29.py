from dataclasses import dataclass, field
from typing import Dict, List 

@dataclass
class ResumenF29:
    encabezado:      Dict          = field(default_factory=dict)
    ventas_detalle:  List[Dict]    = field(default_factory=list)
    ventas_total:    Dict          = field(default_factory=dict)
    compras_detalle: List[Dict]    = field(default_factory=list)
    IVAPP:           int           = 0
    remanente:       int           = 0
    remanenteMesAnterior: int      = 0
    compras_total:   Dict          = field(default_factory=dict)
    remuneraciones:  Dict          = field(default_factory=dict)
    honorarios:      Dict          = field(default_factory=dict)
    ppm:             Dict          = field(default_factory=dict)
    TT:              int           = 0

    # Métodos.
    # Calcular total ventas.

    # Calcular total compras.

    # Calcular iva por pagar y remanente.

    # Calcular PPMs.

    # Calcular total total (TT).