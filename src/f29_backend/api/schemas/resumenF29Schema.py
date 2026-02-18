from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import date, datetime
from decimal import Decimal
from f29_backend.infrastructure.persistence.models.resumenF29Modelo import EstadoF29


class ResumenF29Base(BaseModel):
    encabezado: Dict = Field(default_factory=dict)
    ventas_detalle: List[Dict] = Field(default_factory=list)
    ventas_total: Dict = Field(default_factory=dict)
    compras_detalle: List[Dict] = Field(default_factory=list)
    IVAPP: int = 0
    remanente: int = 0
    remanenteMesAnterior: int = 0
    compras_total: Dict = Field(default_factory=dict)
    remuneraciones: Dict = Field(default_factory=dict)
    honorarios: Dict = Field(default_factory=dict)
    ppm: Dict = Field(default_factory=dict)
    TT: int = 0


class ResumenF29Create(ResumenF29Base):
    periodo: str = Field(..., min_length=7, max_length=7, pattern=r"^\d{4}-\d{2}$")


class ResumenF29Read(ResumenF29Create):
    id: int

    class Config:
        from_attributes = True  # Permite convertir directamente desde SQLAlchemy




# Cosas nuevas.
class ResumenF29Update(BaseModel):
    debito_fiscal: Optional[Decimal] = None
    credito_fiscal: Optional[Decimal] = None
    remanente_mes_anterior: Optional[Decimal] = None
    iva_a_pagar: Optional[Decimal] = None
    total_ventas_netas: Optional[Decimal] = None
    total_compras_netas: Optional[Decimal] = None
    total_iva_ventas: Optional[Decimal] = None
    total_iva_compras: Optional[Decimal] = None
    numero_folio: Optional[str] = None
    fecha_envio_sii: Optional[date] = None


class CambiarEstadoRequest(BaseModel):
    estado: EstadoF29


# Schema reducido para listas (dashboard)
class ResumenF29ListItem(BaseModel):
    id: int
    cliente_id: int
    rut_cliente: str        # Desnormalizado para no hacer joins en frontend
    razon_social_cliente: str
    periodo: date
    estado: EstadoF29
    iva_a_pagar: Optional[Decimal]
    created_at: datetime

    class Config:
        from_attributes = True


# Schema completo para vista detalle
class ResumenF29Response(BaseModel):
    id: int
    cliente_id: int
    periodo: date
    debito_fiscal: Optional[Decimal]
    credito_fiscal: Optional[Decimal]
    remanente_mes_anterior: Optional[Decimal]
    iva_a_pagar: Optional[Decimal]
    total_ventas_netas: Optional[Decimal]
    total_compras_netas: Optional[Decimal]
    total_iva_ventas: Optional[Decimal]
    total_iva_compras: Optional[Decimal]
    estado: EstadoF29
    fecha_envio_sii: Optional[date]
    numero_folio: Optional[str]
    creado_por_usuario_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


# Schema para cliente sin resumen (dashboard)
class ClienteSinResumenItem(BaseModel):
    id: int
    rut: str
    razon_social: str
    nombre_comercial: Optional[str]

    class Config:
        from_attributes = True


# Respuesta del dashboard
class DashboardResumenResponse(BaseModel):
    mes: int
    anio: int
    resumenes_hechos: list[ResumenF29ListItem]
    clientes_pendientes: list[ClienteSinResumenItem]
    total_hechos: int
    total_pendientes: int