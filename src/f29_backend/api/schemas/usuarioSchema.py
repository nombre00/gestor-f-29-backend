# Schemas de validación para usuarios

from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
from f29_backend.infrastructure.persistence.models.usuario import RolUsuario


# Schema de respuesta de usuario
class UsuarioResponse(BaseModel):
    id: int
    email: str
    nombre: str
    apellido: Optional[str]
    rol: RolUsuario
    activo: bool
    # Datos opcionales, esto porque algunas respuestas no requieren ni dan tantos datos.
    empresa_id: Optional[int] = None          # ← hazlo Optional
    ultimo_acceso: Optional[datetime] = None  # ← ya era Optional, pero confirma
    created_at: Optional[datetime] = None     # ← hazlo Optional si no siempre lo cargas
    updated_at: Optional[datetime] = None     # ← igual
    
    class Config:
        from_attributes = True


# Schema para listar usuarios
class UsuarioListResponse(BaseModel):
    usuarios: list[UsuarioResponse]
    total: int


# Schema para actualizar usuario
class UsuarioUpdate(BaseModel):
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    apellido: Optional[str] = Field(None, max_length=255)
    email: Optional[EmailStr] = None
    rol: Optional[RolUsuario] = None


# Schema para cambiar contraseña
class CambiarPasswordRequest(BaseModel):
    password_actual: str = Field(..., min_length=1)
    password_nueva: str = Field(..., min_length=8, max_length=255)