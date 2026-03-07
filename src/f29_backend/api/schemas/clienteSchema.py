from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class ClienteCreate(BaseModel):
    rut: str = Field(..., min_length=8, max_length=12)
    razon_social: str = Field(..., min_length=1, max_length=255)
    nombre_comercial: Optional[str] = Field(None, max_length=255)
    giro: Optional[str] = Field(None, max_length=255)
    actividad_economica: Optional[str] = Field(None, max_length=255)
    nro_cliente: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=500)
    comuna: Optional[str] = Field(None, max_length=100)
    ciudad: Optional[str] = Field(None, max_length=100)
    contacto_nombre: Optional[str] = Field(None, max_length=255)
    contacto_email: Optional[str] = Field(None, max_length=255)
    contacto_telefono: Optional[str] = Field(None, max_length=20)
    asignado_a_usuario_id: Optional[int] = None  # Solo admins pueden asignar a otro usuario

    @field_validator('rut')
    @classmethod
    def formatear_rut(cls, v: str) -> str:
        """Normaliza el RUT: elimina puntos y espacios, mantiene guión"""
        return v.replace('.', '').replace(' ', '').upper().strip()


class ClienteUpdate(BaseModel):
    razon_social: Optional[str] = Field(None, min_length=1, max_length=255)
    nombre_comercial: Optional[str] = Field(None, max_length=255)
    giro: Optional[str] = Field(None, max_length=255)
    actividad_economica: Optional[str] = Field(None, max_length=255)
    nro_cliente: Optional[str] = Field(None, max_length=50)
    direccion: Optional[str] = Field(None, max_length=500)
    comuna: Optional[str] = Field(None, max_length=100)
    ciudad: Optional[str] = Field(None, max_length=100)
    contacto_nombre: Optional[str] = Field(None, max_length=255)
    contacto_email: Optional[str] = Field(None, max_length=255)
    contacto_telefono: Optional[str] = Field(None, max_length=20)


class ClienteResponse(BaseModel):
    id: int
    rut: str
    razon_social: str
    nombre_comercial: Optional[str]
    giro: Optional[str]
    actividad_economica: Optional[str]
    nro_cliente: Optional[str]
    direccion: Optional[str]
    comuna: Optional[str]
    ciudad: Optional[str]
    contacto_nombre: Optional[str]
    contacto_email: Optional[str]
    contacto_telefono: Optional[str]
    activo: bool
    empresa_id: int
    asignado_a_usuario_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class ClienteListResponse(BaseModel):
    clientes: list[ClienteResponse]
    total: int