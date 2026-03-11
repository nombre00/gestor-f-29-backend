# Clase dominio/entidad del modelo.

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
    # Datos extra (ajenos al documento). 
    arriendos_pagados: int         = 0
    gastos_generales_boletas: int  = 0



    # Métodos.
    # Método to_dict (para serializar en comunicaciones REST).
    def to_dict(self):
        data = asdict(self)  # Guardamos los datos en una variable, queda como un diccionario ya que recibe un JSON.
        for key, value in data.items():  # Por valor-llave dentro del diccionario.
            if isinstance(value, (int, float)):  # Si es int o float:
                data[key] = int(value)  # lo tratamos como int.
            elif isinstance(value, list): # Si es una lista de diccionarios:
                data[key] = [item.to_dict() if hasattr(item, 'to_dict') else item for item in value]  # Lo tratamos como lista de diccionarios.
            elif isinstance(value, dict):  # Si es diccionario:
                data[key] = {k: v for k, v in value.items()}  # Lo tratamos como diccionario.
        
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
            # Datos nuevos.
            arriendos_pagados=data.get('arriendos_pagados', 0),
            gastos_generales_boletas=data.get('gastos_generales_boletas', 0),
        )