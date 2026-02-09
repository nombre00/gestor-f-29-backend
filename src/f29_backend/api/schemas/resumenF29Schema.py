from pydantic import BaseModel, Field
from typing import Dict, List, Optional


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