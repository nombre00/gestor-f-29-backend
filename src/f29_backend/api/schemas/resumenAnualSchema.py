from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum


class EstadoResumenAnual(str, Enum):
    BORRADOR = "borrador"
    REVISADO = "revisado"


class ResumenAnualContenido(BaseModel):
    encabezado: Dict = Field(default_factory=dict)
    ventas_detalle: List[Dict] = Field(default_factory=list)
    ventas_total: Dict = Field(default_factory=dict)
    compras_detalle: List[Dict] = Field(default_factory=list)
    compras_total: Dict = Field(default_factory=dict)
    remuneraciones: Dict = Field(default_factory=dict)
    honorarios: Dict = Field(default_factory=dict)
    ppm: Dict = Field(default_factory=dict)
    IVAPP: int = 0
    remanente: int = 0
    remanenteMesAnterior: int = 0
    TT: int = 0
    arriendos_pagados: int = 0
    gastos_generales_boletas: int = 0

    class Config:
        from_attributes = True


class ResumenAnualResponse(BaseModel):
    id: int
    cliente_id: int
    año: str
    estado: EstadoResumenAnual
    creado_por_usuario_id: int
    created_at: datetime
    updated_at: datetime

    periodos_incluidos: List[str] = Field(default_factory=list)  # ← era ..., ahora tiene default
    contenido: ResumenAnualContenido = Field(default_factory=ResumenAnualContenido)  # ← default vacío

    meses_incluidos_count: int = Field(default=0)          # ← era ...
    meses_totales_posibles: int = Field(default=12)
    rango_texto: str = Field(default="")                   # ← era ...

    class Config:
        from_attributes = True


class ResumenAnualRecalcularRequest(BaseModel):
    pass


class ResumenAnualListItem(BaseModel):
    id: int
    cliente_id: int
    año: str
    estado: EstadoResumenAnual
    meses_incluidos_count: int
    rango_texto: str
    created_at: datetime
    updated_at: datetime