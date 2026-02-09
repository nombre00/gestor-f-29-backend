from dataclasses import dataclass
from typing import Dict

# {'tipo': tipo, 'desc': desc, 'td': td, 'exento': exento, 'neto': neto, 'iva': iva, 'total': total} 
@dataclass
class ResumenCompras:
    cod34: Dict  # Compras internas exentas o no grabadas
    cod33: Dict  # Facturas recibidas y facturas de compra
    codSupermercado: Dict  # Facturas recibidas Prom. Superm
    codActivoFijo: Dict  # Facturas activo fijo
    cod61: Dict  # Notas de crédito recibidos
    cod56: Dict  # Notas de débito recibidas
    cod914: Dict  # Form. de pago de importaciones del giro
    codActivoFijoImportacion: Dict  # Form. de pago de importaciones de activo fijo