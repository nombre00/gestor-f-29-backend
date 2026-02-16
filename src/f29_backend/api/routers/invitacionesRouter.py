from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List

from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user, require_role, hash_password
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario
from f29_backend.infrastructure.persistence.models.Invitacion import Invitacion
from f29_backend.api.schemas.invitacionSchema import (
    InvitacionCreate,
    InvitacionResponse,
    InvitacionListResponse,
    CompletarRegistro
)
from f29_backend.application.services.emailService import enviar_email_invitacion
from datetime import datetime

router = APIRouter(prefix="/api/invitaciones", tags=["invitaciones"])


@router.post("", response_model=InvitacionResponse, status_code=status.HTTP_201_CREATED)
async def crear_invitacion(
    invitacion_data: InvitacionCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN]))
):
    """
    Crear una nueva invitación (solo admins).
    Envía un email al usuario invitado con un link de registro.
    """
    
    # Verificar que el email no esté ya registrado
    usuario_existente = db.query(Usuario).filter(Usuario.email == invitacion_data.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )
    
    # Verificar que no haya una invitación pendiente para este email
    invitacion_existente = db.query(Invitacion).filter(
        Invitacion.email == invitacion_data.email,
        Invitacion.usado == False,
        Invitacion.expires_at > datetime.utcnow()
    ).first()
    
    if invitacion_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe una invitación pendiente para este email"
        )
    
    # Crear la invitación
    nueva_invitacion = Invitacion(
        email=invitacion_data.email,
        nombre=invitacion_data.nombre,
        apellido=invitacion_data.apellido,
        rol=invitacion_data.rol,
        token=Invitacion.generar_token(),
        expires_at=Invitacion.calcular_expiracion(),
        empresa_id=current_user.empresa_id,
        invitado_por_usuario_id=current_user.id
    )
    
    db.add(nueva_invitacion)
    db.commit()
    db.refresh(nueva_invitacion)
    
    # Enviar email de invitación
    try:
        await enviar_email_invitacion(
            email=nueva_invitacion.email,
            nombre=nueva_invitacion.nombre,
            token=nueva_invitacion.token,
            invitado_por=f"{current_user.nombre} {current_user.apellido or ''}".strip()
        )
    except Exception as e:
        # Si falla el envío del email, eliminamos la invitación
        db.delete(nueva_invitacion)
        db.commit()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al enviar el email de invitación: {str(e)}"
        )
    
    return nueva_invitacion


@router.get("/pendientes", response_model=InvitacionListResponse)
def listar_invitaciones_pendientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN]))
):
    """
    Listar todas las invitaciones pendientes de la empresa (solo admins)
    """
    invitaciones = db.query(Invitacion).filter(
        Invitacion.empresa_id == current_user.empresa_id,
        Invitacion.usado == False
    ).order_by(Invitacion.created_at.desc()).all()
    
    return {
        "invitaciones": invitaciones,
        "total": len(invitaciones)
    }


@router.post("/{invitacion_id}/reenviar", status_code=status.HTTP_200_OK)
async def reenviar_invitacion(
    invitacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN]))
):
    """
    Reenviar email de invitación y extender fecha de expiración
    """
    invitacion = db.query(Invitacion).filter(
        Invitacion.id == invitacion_id,
        Invitacion.empresa_id == current_user.empresa_id
    ).first()
    
    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada"
        )
    
    if invitacion.usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta invitación ya fue utilizada"
        )
    
    # Extender fecha de expiración
    invitacion.expires_at = Invitacion.calcular_expiracion()
    db.commit()
    
    # Reenviar email
    try:
        await enviar_email_invitacion(
            email=invitacion.email,
            nombre=invitacion.nombre,
            token=invitacion.token,
            invitado_por=f"{current_user.nombre} {current_user.apellido or ''}".strip()
        )
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Error al reenviar el email: {str(e)}"
        )
    
    return {"message": "Invitación reenviada exitosamente"}


@router.delete("/{invitacion_id}", status_code=status.HTTP_200_OK)
def cancelar_invitacion(
    invitacion_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN]))
):
    """
    Cancelar una invitación pendiente
    """
    invitacion = db.query(Invitacion).filter(
        Invitacion.id == invitacion_id,
        Invitacion.empresa_id == current_user.empresa_id
    ).first()
    
    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Invitación no encontrada"
        )
    
    if invitacion.usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No se puede cancelar una invitación ya utilizada"
        )
    
    db.delete(invitacion)
    db.commit()
    
    return {"message": "Invitación cancelada exitosamente"}


@router.post("/completar-registro", response_model=dict)
def completar_registro(
    registro_data: CompletarRegistro,
    db: Session = Depends(get_db)
):
    """
    Completar registro usando el token de invitación (endpoint público)
    """
    # Buscar invitación por token
    invitacion = db.query(Invitacion).filter(
        Invitacion.token == registro_data.token
    ).first()
    
    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de invitación inválido"
        )
    
    if invitacion.usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta invitación ya fue utilizada"
        )
    
    if invitacion.esta_expirada():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta invitación ha expirado"
        )
    
    # Verificar que el email no esté ya registrado (por si acaso)
    usuario_existente = db.query(Usuario).filter(Usuario.email == invitacion.email).first()
    if usuario_existente:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Ya existe un usuario con este email"
        )
    
    # Crear el nuevo usuario
    nuevo_usuario = Usuario(
        email=invitacion.email,
        nombre=registro_data.nombre or invitacion.nombre,
        apellido=registro_data.apellido or invitacion.apellido,
        rol=invitacion.rol,
        password_hash=hash_password(registro_data.password),
        empresa_id=invitacion.empresa_id,
        activo=True
    )
    
    db.add(nuevo_usuario)
    
    # Marcar invitación como usada
    invitacion.usado = True
    
    db.commit()
    db.refresh(nuevo_usuario)
    
    return {
        "message": "Registro completado exitosamente",
        "usuario_id": nuevo_usuario.id
    }


@router.get("/validar-token/{token}", response_model=dict)
def validar_token_invitacion(
    token: str,
    db: Session = Depends(get_db)
):
    """
    Validar si un token de invitación es válido (endpoint público)
    Usado para mostrar el formulario de registro
    """
    invitacion = db.query(Invitacion).filter(
        Invitacion.token == token
    ).first()
    
    if not invitacion:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Token de invitación inválido"
        )
    
    if invitacion.usado:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta invitación ya fue utilizada"
        )
    
    if invitacion.esta_expirada():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Esta invitación ha expirado"
        )
    
    return {
        "valido": True,
        "email": invitacion.email,
        "nombre": invitacion.nombre,
        "apellido": invitacion.apellido,
        "rol": invitacion.rol
    }