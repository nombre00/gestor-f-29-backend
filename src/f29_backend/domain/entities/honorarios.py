from dataclasses import dataclass
from typing import Dict, List 


@dataclass
class RegistroHonorariosMensual:
    contribuyente: str
    rut: str
    fecha: str
    honorarios: List[Dict]
    totales: Dict