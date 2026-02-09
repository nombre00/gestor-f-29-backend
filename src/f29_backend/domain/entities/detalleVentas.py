from dataclasses import dataclass
from typing import Dict, List, Optional

# Incompleto por ahora, cuando empieze a exportar los detalles lo termino.
@dataclass
class DetalleVentas:
    facturas: List[Dict] # Código 33. 
    boletas: List[Dict] # Código 39.
    comprobantesPago: List[Dict] # Código 48.
    notasDebito: List[Dict] # Código 56.
    notasCredito: List[Dict] # Código 61.

    resumen: Optional[Dict] = None  