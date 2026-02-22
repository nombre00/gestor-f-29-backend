# Schema de la clase empresa.


from pydantic import BaseModel, Field, field_validator
from typing import Optional
from datetime import datetime


class EmpresaCreate(BaseModel):
    rut: str = Field(..., min_length=8, max_length=12)
    razon_social: str = Field(..., min_length=1, max_length=255)
    nombre_comercial: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=20)

    @field_validator('rut')
    @classmethod
    def formatear_rut(cls, v: str) -> str:
        return v.replace('.', '').replace(' ', '').upper().strip()


class EmpresaUpdate(BaseModel):
    razon_social: Optional[str] = Field(None, min_length=1, max_length=255)
    nombre_comercial: Optional[str] = Field(None, max_length=255)
    email: Optional[str] = Field(None, max_length=255)
    telefono: Optional[str] = Field(None, max_length=20)


class EmpresaResponse(BaseModel):
    id: int
    rut: str
    razon_social: str
    nombre_comercial: Optional[str]
    email: Optional[str]
    telefono: Optional[str]
    activa: bool
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class EmpresaListResponse(BaseModel):
    empresas: list[EmpresaResponse]
    total: int