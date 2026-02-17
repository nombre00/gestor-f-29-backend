# Router para gestión de usuarios (CRUD completo)

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional

from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user, require_role, hash_password, verify_password
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario
from f29_backend.api.schemas.usuarioSchema import (
    UsuarioResponse,
    UsuarioListResponse,
    UsuarioUpdate,
    CambiarPasswordRequest
)


router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


@router.get("", response_model=UsuarioListResponse)
def listar_usuarios(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.SUPER, RolUsuario.ADMIN]))
):
    """
    Listar todos los usuarios de la empresa (solo admins)
    """
    usuarios = db.query(Usuario).filter(
        Usuario.empresa_id == current_user.empresa_id
    ).order_by(Usuario.activo.desc(), Usuario.nombre).all()
    return {
        "usuarios": usuarios,
        "total": len(usuarios)
    }



@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil_actual(
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener información del usuario autenticado (cualquier usuario)
    """
    return current_user



# Falta dar permiso a super ususario.
@router.get("/{usuario_id}", response_model=UsuarioResponse)
def obtener_usuario_por_id(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtener información de un usuario específico
    - Super puede ver cualquier usuario de cualquier empresa.
    - Admins pueden ver cualquier usuario de su empresa
    - Otros usuarios solo pueden ver su propio perfil
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    # Verificar permisos
    if current_user.rol != RolUsuario.ADMIN:
        if usuario.id != current_user.id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este usuario"
            )
    else:
        # Admin solo puede ver usuarios de su empresa
        if usuario.empresa_id != current_user.empresa_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="No tienes permiso para ver este usuario"
            )
    return usuario



# Falta dar permiso a super usuario.
@router.put("/{usuario_id}", response_model=UsuarioResponse)
def actualizar_usuario(
    usuario_id: int,
    usuario_data: UsuarioUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualizar información de un usuario
    - Admins pueden actualizar cualquier usuario de su empresa
    - Otros usuarios solo pueden actualizar su propio perfil (excepto rol)
    """
    usuario = db.query(Usuario).filter(Usuario.id == usuario_id).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    # Verificar permisos
    es_admin = current_user.rol == RolUsuario.ADMIN
    es_mismo_usuario = usuario.id == current_user.id
    if not es_admin and not es_mismo_usuario:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    if es_admin and usuario.empresa_id != current_user.empresa_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para actualizar este usuario"
        )
    # Solo admins pueden cambiar el rol
    if usuario_data.rol and not es_admin:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para cambiar el rol"
        )
    # Actualizar campos
    if usuario_data.nombre is not None:
        usuario.nombre = usuario_data.nombre
    if usuario_data.apellido is not None:
        usuario.apellido = usuario_data.apellido
    if usuario_data.email is not None:
        # Verificar que el email no esté en uso por otro usuario
        email_existente = db.query(Usuario).filter(
            Usuario.email == usuario_data.email,
            Usuario.id != usuario_id
        ).first()
        if email_existente:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Este email ya está en uso"
            )
        usuario.email = usuario_data.email
    if usuario_data.rol is not None and es_admin:
        usuario.rol = usuario_data.rol
    db.commit()
    db.refresh(usuario)
    return usuario



# Falta dar permiso al super usuario.
@router.put("/{usuario_id}/desactivar", status_code=status.HTTP_200_OK)
def desactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN]))
):
    """
    Desactivar un usuario (solo admins)
    """
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.empresa_id == current_user.empresa_id
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes desactivar tu propia cuenta"
        )
    if not usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está inactivo"
        )
    usuario.activo = False
    db.commit()
    return {"message": "Usuario desactivado exitosamente"}



# Falta dar permiso al super usuario.
@router.put("/{usuario_id}/reactivar", status_code=status.HTTP_200_OK)
def reactivar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN]))
):
    """
    Reactivar un usuario (solo admins)
    """
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.empresa_id == current_user.empresa_id
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    if usuario.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El usuario ya está activo"
        )
    usuario.activo = True
    db.commit()
    return {"message": "Usuario reactivado exitosamente"}



# Falta dar permiso al super ususario.
@router.put("/me/password", status_code=status.HTTP_200_OK)
def cambiar_password(
    password_data: CambiarPasswordRequest,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Cambiar la contraseña del usuario autenticado
    """
    # Verificar contraseña actual
    if not verify_password(password_data.password_actual, current_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Contraseña actual incorrecta"
        )
    # Validar nueva contraseña
    if len(password_data.password_nueva) < 8:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La contraseña debe tener al menos 8 caracteres"
        )
    if password_data.password_nueva == password_data.password_actual:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="La nueva contraseña debe ser diferente a la actual"
        )
    # Actualizar contraseña
    current_user.password_hash = hash_password(password_data.password_nueva)
    db.commit()
    return {"message": "Contraseña actualizada exitosamente"}



# Falta dar permiso al super usuario.
@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(
    usuario_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN]))
):
    """
    Eliminar un usuario permanentemente (solo admins)
    NOTA: Por seguridad, es mejor usar desactivar en vez de eliminar
    """
    usuario = db.query(Usuario).filter(
        Usuario.id == usuario_id,
        Usuario.empresa_id == current_user.empresa_id
    ).first()
    if not usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Usuario no encontrado"
        )
    if usuario.id == current_user.id:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="No puedes eliminar tu propia cuenta"
        )
    # Verificar si tiene clientes asignados
    if usuario.clientes_asignados and len(usuario.clientes_asignados) > 0:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el usuario porque tiene {len(usuario.clientes_asignados)} cliente(s) asignado(s). Reasigna los clientes primero."
        )
    db.delete(usuario)
    db.commit()
    return {"message": "Usuario eliminado exitosamente"}