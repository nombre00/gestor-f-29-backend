from dataclasses import dataclass
from typing import Dict, List

@dataclass
class LibroRemuneraciones:
    encabezado: Dict
    empleados_remuneraciones: List[Dict]
    empleados_aportes: List[Dict]
    totales: Dict