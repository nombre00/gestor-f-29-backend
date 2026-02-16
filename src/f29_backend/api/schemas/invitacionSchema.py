

# Bibliotecas.
from pydantic import BaseModel, EmailStr, Field
from typing import Optional
from datetime import datetime
# Módulos.
from f29_backend.infrastructure.persistence.models.usuario import RolUsuario



# Schema para crear una invitación
class InvitacionCreate(BaseModel):
    email: EmailStr
    nombre: str = Field(..., min_length=1, max_length=255)
    apellido: Optional[str] = Field(None, max_length=255)
    rol: RolUsuario = RolUsuario.CONTADOR


# Schema para respuesta de invitación
class InvitacionResponse(BaseModel):
    id: int
    email: str
    nombre: Optional[str]
    apellido: Optional[str]
    rol: str
    usado: bool
    expires_at: datetime
    created_at: datetime
    invitado_por_usuario_id: Optional[int]
    
    class Config:
        from_attributes = True


# Schema para listar invitaciones pendientes
class InvitacionListResponse(BaseModel):
    invitaciones: list[InvitacionResponse]
    total: int


# Schema para completar registro con token
class CompletarRegistro(BaseModel):
    token: str = Field(..., min_length=10)
    password: str = Field(..., min_length=8, max_length=255)
    # Nombre y apellido ya vienen en la invitación, pero el usuario puede modificarlos
    nombre: Optional[str] = Field(None, min_length=1, max_length=255)
    apellido: Optional[str] = Field(None, max_length=255)