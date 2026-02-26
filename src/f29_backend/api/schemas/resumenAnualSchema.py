from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

from f29_backend.api.schemas.resumenF29Schema import ResumenF29Response  # ← asumiendo que ya tienes este


class EstadoResumenAnual(str, Enum):
    BORRADOR = "borrador"
    REVISADO = "revisado"


# ────────────────────────────────────────────────
# Este schema representa SOLO el contenido acumulado
# → misma estructura que ResumenF29Response para máxima reutilización
# ────────────────────────────────────────────────
class ResumenAnualContenido(BaseModel):
    encabezado: Dict = Field(default_factory=dict)
    ventas_detalle: List[Dict] = Field(default_factory=list)  # opcional, si decides incluirlo
    ventas_total: Dict = Field(default_factory=dict)
    compras_detalle: List[Dict] = Field(default_factory=list)  # opcional
    compras_total: Dict = Field(default_factory=dict)
    remuneraciones: Dict = Field(default_factory=dict)
    honorarios: Dict = Field(default_factory=dict)
    ppm: Dict = Field(default_factory=dict)
    IVAPP: int = 0
    remanente: int = 0
    remanenteMesAnterior: int = 0  # el del último mes incluido
    TT: int = 0
    arriendos_pagados: int = 0
    gastos_generales_boletas: int = 0

    class Config:
        from_attributes = True


# ────────────────────────────────────────────────
# Schema completo para respuestas de API (lo que devuelve el endpoint)
# Incluye metadatos + periodos + el contenido reutilizable
# ────────────────────────────────────────────────
class ResumenAnualResponse(BaseModel):
    id: int
    cliente_id: int
    año: str
    estado: EstadoResumenAnual
    creado_por_usuario_id: int
    created_at: datetime
    updated_at: datetime

    periodos_incluidos: List[str] = Field(
        ..., 
        description="Lista de periodos incluidos en formato 'YYYY-MM', ordenados"
    )
    # Opcional: si quieres mostrar también los IDs de F29
    # f29_ids: List[int] = Field(default_factory=list)

    # El contenido acumulado (reutilizable en previsualización y export)
    contenido: ResumenAnualContenido

    # Campos calculados para UI (no guardados en BD, generados en runtime)
    meses_incluidos_count: int = Field(..., description="Cantidad de meses incluidos")
    meses_totales_posibles: int = Field(12, description="Siempre 12 para un año completo")
    rango_texto: str = Field(..., description="Ej: 'Enero - Junio 2025'")

    class Config:
        from_attributes = True


# ────────────────────────────────────────────────
# Para request de actualización / recalcular (si necesitas body)
# ────────────────────────────────────────────────
class ResumenAnualRecalcularRequest(BaseModel):
    # Por ahora vacío, porque recalcular no necesita parámetros extras
    # Si más adelante quieres forzar algo (ej: ignorar algún mes), aquí iría
    pass


# ────────────────────────────────────────────────
# Response simple para lista (dashboard)
# ────────────────────────────────────────────────
class ResumenAnualListItem(BaseModel):
    id: int
    cliente_id: int
    año: str
    estado: EstadoResumenAnual
    meses_incluidos_count: int
    rango_texto: str
    created_at: datetime
    updated_at: datetime