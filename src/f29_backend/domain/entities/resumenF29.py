from dataclasses import dataclass, field
from typing import Dict, List, Any
from dataclasses import asdict

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

    # Método to_dict (para serializar en comunicaciones REST).
    def to_dict(self):
        data = asdict(self)
        for key, value in data.items():
            if isinstance(value, (int, float)):
                data[key] = int(value)  # o float si necesitas decimales
            elif isinstance(value, list):
                # Si las listas tienen sub-dicts que necesitan serialización
                data[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]
            elif isinstance(value, dict):
                # Si los dicts internos necesitan limpieza (opcional)
                data[key] = {k: v for k, v in value.items()}
        
        return data
    
    # Método from_dict (para desserializar en comunicaciones REST).
    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ResumenF29':
        # Crea la instancia directamente pasando los campos del dict
        return cls(
            encabezado=data.get('encabezado', {}),
            ventas_detalle=data.get('ventas_detalle', []),
            ventas_total=data.get('ventas_total', {}),
            compras_detalle=data.get('compras_detalle', []),
            IVAPP=data.get('IVAPP', 0),
            remanente=data.get('remanente', 0),
            remanenteMesAnterior=data.get('remanenteMesAnterior', 0),
            compras_total=data.get('compras_total', {}),
            remuneraciones=data.get('remuneraciones', {}),
            honorarios=data.get('honorarios', {}),
            ppm=data.get('ppm', {}),
            TT=data.get('TT', 0),
        )