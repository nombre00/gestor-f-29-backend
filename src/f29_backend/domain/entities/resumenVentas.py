from dataclasses import dataclass
from typing import Dict

@dataclass
class ResumenVentas:
    # Partimos con el DetalleVentas, códigos relevantes: 110, 34, 46, 33, 39, 48, 56, 61, 45, 43.
    # EStructura de cada diccionario: 
        # { 'codigo': valor, 'total documentos': valor, 'monto neto': valor, 'monto iva': valor, 'monto total': valor }
    cod110 : Dict  # Exportaciones. (falta ver como definir eso)
    cod34 : Dict  # Ventas y/o servicios exentos o no grabados.
    cod46 : Dict  # facturas de compra recibidas con ret.total.
    cod33 : Dict  # facturas emitidas.
    cod39 : Dict  # cantidad de documentos boletas.
    cod48 : Dict  # comprobante o recibo de transacciones medios.
    cod56 : Dict  # notas de débito emitidas. 
    cod61 : Dict  # notas de crédito emitidas.
    cod45 : Dict  # facturas de compras recibidas.
    cod43 : Dict  # liquidacion y liquidacion factura.