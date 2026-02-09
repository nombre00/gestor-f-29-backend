from dataclasses import dataclass
from typing import Dict, List, Optional

# Incompleto por ahora, duando empieze a exportar los detalles lo termino.

@dataclass
class DetalleCompras:
    facturas: List[Dict] # Código 33.
    notas_debito: List[Dict] # Código 56.
    notas_credito: List[Dict] # Código 61.
    factura_exenta: List[Dict] # Código 34.

    resumen: Optional [Dict] = None  