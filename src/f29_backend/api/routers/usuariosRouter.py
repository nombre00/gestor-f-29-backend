# Router para gestión de usuarios (CRUD completo)


# Bibliotecas.
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from typing import List, Optional
# Módulos.
from f29_backend.core.database import get_db  # Conección a la base de datos.
from f29_backend.core.security import get_current_user, require_role, hash_password, verify_password  # Funcionalidad de seguridad.
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario  # modelos de entidad del usuario.
from f29_backend.api.schemas.usuarioSchema import (UsuarioResponse,UsuarioListResponse,UsuarioUpdate,CambiarPasswordRequest) # schemas de REST.
from f29_backend.infrastructure.persistence.repository.usuarioRepository import UsuarioRepository as ur


# Prefijo de las rutas de este archivo.
router = APIRouter(prefix="/api/usuarios", tags=["usuarios"])


# Listar todos los usuarios de una empresa.
@router.get("", response_model=UsuarioListResponse)  # UsuarioListResponse: schema de la respuesta esperada.
def listar_usuarios(db: Session = Depends(get_db), current_user: Usuario = Depends(require_role([RolUsuario.SUPER, RolUsuario.ADMIN]))):
    repo = ur(db)
    # Filtramos los usuarios.
    usuarios = repo.find_by_empresa(current_user.empresa_id)
    # Retornamos los usuarios filtrados y el total.
    return {"usuarios": usuarios, "total": len(usuarios)}


# Obtener información del usuario autenticado (cualquier usuario).
@router.get("/me", response_model=UsuarioResponse)
def obtener_perfil_actual(current_user: Usuario = Depends(get_current_user)):
    return current_user  # Retornamos el usuario.


# El usuario cambia su contraseña.
@router.put("/me/password", status_code=status.HTTP_200_OK)
def cambiar_password(password_data: CambiarPasswordRequest, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # 1. Primero nos conectamos a la base de datos.
    repo = ur(db)
    # Verificar contraseña actual
    if not verify_password(password_data.password_actual, current_user.password_hash):
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Contraseña actual incorrecta")
    # Validar nueva contraseña
    if len(password_data.password_nueva) < 8:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="La contraseña debe tener al menos 8 caracteres")
    if password_data.password_nueva == password_data.password_actual:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="La nueva contraseña debe ser diferente a la actual")
    # Hashamos la nueva contraseña.
    new_hash = hash_password(password_data.password_nueva)
    # Actualizar contraseña
    repo.update_password(current_user.id, new_hash)
    return {"message": "Contraseña actualizada exitosamente"}


# Busca por id sujeto a permisos.
@router.get("/{usuario_id}", response_model=UsuarioResponse)  # Schema de respuesta del usuario.
def obtener_usuario_por_id(usuario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # 1. Primero nos conectamos a la base de datos.
    repo = ur(db)
    # 2. Segundo determinamos qué tipo de consulta podemos hacer según el rol
    if current_user.rol == RolUsuario.SUPER:  # SUPER: sin restricciones de empresa
        usuarioEncontrado = repo.find_by_id(usuario_id)  # Buscamos.
    elif current_user.rol == RolUsuario.ADMIN:  # Si es admin: consulamos por id Y id de la empresa.
        usuarioEncontrado = repo.find_by_id_and_empresa(usuario_id,current_user.empresa_id)  # Buscamos.
    else:  # Si no no se puede consultar, retornamos el usuario actual.
        if usuario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Solo puedes ver tu propio perfil")
        usuarioEncontrado = current_user  # Buscamos.
    # Revisamos que encontramos un usuario.
    if not usuarioEncontrado:  # Si no nos retorna un usuario levantamos un error.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuario no encontrado")
    return usuarioEncontrado  # Si todo sale bien retornamos el usuario encontrado.


# Actualizar un usuario.
@router.put("/{usuario_id}", response_model=UsuarioResponse)  # Schema de respuesta del usuario.
def actualizar_usuario(usuario_id: int,usuario_data: UsuarioUpdate,db: Session = Depends(get_db), current_user: Usuario = Depends(get_current_user)):
    # 1. Primero nos conectamos a la base de datos.
    repo = ur(db)
    # 2. Luego determinamos si el usuario actual tiene permiso para modificar este ID
    if current_user.rol == RolUsuario.SUPER:  # SUPER: sin restricciones
        usuarioEncontrado = repo.find_by_id(usuario_id)  # Buscamos.
    elif current_user.rol == RolUsuario.ADMIN: # Si es admin buscamos por id de la empresa de quien consulta y id del usuario_data.
        usuarioEncontrado = repo.find_by_id_and_empresa(usuario_id,current_user.empresa_id)  # Buscamos.
    else:  # sino solo puede modificar algunos de sus propios datos.
        if usuario_id != current_user.id:  # revisamos que el usuario está modificando sus datos.
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN,detail="Solo puedes modificar tu propio perfil")  # sino levantamos un error.
        usuarioEncontrado = current_user  # Buscamos.
    # Revisamos que encontramos un usuario.
    if not usuarioEncontrado:  # Si no nos retorna un usuario levantamos un error.
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuario no encontrado o no tienes permiso para modificarlo")
    # 3. Actualizamos campos permitidos.
    if usuario_data.nombre is not None:
        usuarioEncontrado.nombre = usuario_data.nombre
    if usuario_data.apellido is not None:
        usuarioEncontrado.apellido = usuario_data.apellido
    if usuario_data.email is not None and usuario_data.email != usuarioEncontrado.email: # Validamos que el mail no esté vacío y sea distinto al mail del usuario encontrado.
        if repo.email_exists(usuario_data.email, exclude_id=usuarioEncontrado.id):  # Revisamos que otros usuarios no tengan ese mail.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Este email ya está en uso por otro usuario")
        usuarioEncontrado.email = usuario_data.email
    # Solo si es ADMIN o SUPER → aplicar cambio de rol
    if (current_user.rol == RolUsuario.SUPER  or  current_user.rol == RolUsuario.ADMIN)  and  usuario_data.rol is not None:
        usuarioEncontrado.rol = usuario_data.rol
    # 4. Guardar cambios
    repo.update(usuarioEncontrado)
    return usuarioEncontrado


# desactivar un usuario.
@router.put("/{usuario_id}/desactivar", status_code=status.HTTP_200_OK)
def desactivar_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(require_role([RolUsuario.SUPER, RolUsuario.ADMIN]))):
    # 1. Primero nos conectamos a la base de datos.
    repo = ur(db)
    # 2. Segundo determinamos si el usuario actual tiene permiso para desactivar un usuario.
    if current_user.rol == RolUsuario.SUPER:  # SUPER: sin restricciones
        usuarioEncontrado = repo.find_by_id(usuario_id)  # Buscamos.
    elif current_user.rol == RolUsuario.ADMIN: # Si es admin buscamos por id de la empresa de quien consulta y id del usuario_data.
        usuarioEncontrado = repo.find_by_id_and_empresa(usuario_id,current_user.empresa_id)  # Buscamos.
    # Revisamos que encontramos un usuario.
    if usuarioEncontrado is not None:
        if usuarioEncontrado.id != current_user.id:  # Revisamos que el usuario no intente desactivar su propia cuenta.
            if not usuarioEncontrado.activo:  # Revisamos que el usuario esté activo.
                raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Este usuario ya está desactivado.")
            else:  # Si todo bien hacemos el cambio.
                repo.deactivate(usuarioEncontrado.id)
                return {"message": "Usuario desactivado exitosamente"}
        else: 
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No puedes desactivar tu propia cuenta.")
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se ha encontrado al usuario.")


# Activar un usuario.
@router.put("/{usuario_id}/reactivar", status_code=status.HTTP_200_OK)
def reactivar_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(require_role([RolUsuario.SUPER, RolUsuario.ADMIN]))):
    # 1. Primero nos conectamos a la base de datos.
    repo = ur(db)
    # 2. Segundo determinamos si el usuario actual tiene permiso para desactivar un usuario.
    if current_user.rol == RolUsuario.SUPER:  # SUPER: sin restricciones
        usuarioEncontrado = repo.find_by_id(usuario_id)  # Buscamos.
    elif current_user.rol == RolUsuario.ADMIN: # Si es admin buscamos por id de la empresa de quien consulta y id del usuario_data.
        usuarioEncontrado = repo.find_by_id_and_empresa(usuario_id,current_user.empresa_id)  # Buscamos.
    # Revisamos que encontramos un usuario.
    if usuarioEncontrado is not None:
        if usuarioEncontrado.activo:  # Revisamos que el usuario esté activo.
            raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="Este usuario ya está activo.")
        else:  # Si todo bien hacemos el cambio.
            repo.reactivate(usuarioEncontrado.id)
            return {"message": "Usuario activado exitosamente"}
    else:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="No se ha encontrado al usuario.")


# Elimina permanentemente al usuario, solo yo tengo acceso.
@router.delete("/{usuario_id}", status_code=status.HTTP_200_OK)
def eliminar_usuario(usuario_id: int, db: Session = Depends(get_db), current_user: Usuario = Depends(require_role([RolUsuario.SUPER]))):
    # 1. Primero nos conectamos a la base de datos.
    repo = ur(db)
    usuarioencontrado = repo.find_by_id(usuario_id)
    if not usuarioencontrado:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND,detail="Usuario no encontrado")
    if usuarioencontrado.id == current_user.id:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,detail="No puedes eliminar tu propia cuenta")
    # Verificar si tiene clientes asignados
    if usuarioencontrado.clientes_asignados and len(usuarioencontrado.clientes_asignados) > 0:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"No se puede eliminar el usuario porque tiene {len(usuarioencontrado.clientes_asignados)} cliente(s) asignado(s). Reasigna los clientes primero.")
    repo.delete(usuarioencontrado.id)
    return {"message": "Usuario eliminado exitosamente"}