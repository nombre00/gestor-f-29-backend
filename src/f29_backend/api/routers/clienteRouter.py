from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from f29_backend.core.database import get_db
from f29_backend.core.security import get_current_user, require_role
from f29_backend.infrastructure.persistence.models.usuario import Usuario, RolUsuario
from f29_backend.infrastructure.persistence.repository.clienteRepository import ClienteRepository
from f29_backend.api.schemas.clienteSchema import (
    ClienteCreate, ClienteUpdate, ClienteResponse, ClienteListResponse
)

router = APIRouter(prefix="/api/clientes", tags=["clientes"])


@router.get("", response_model=ClienteListResponse)
def listar_clientes(
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Lista clientes según el rol:
    - Admin: todos los clientes de la empresa
    - Contador: solo sus clientes asignados
    """
    repo = ClienteRepository(db)

    if current_user.rol in [RolUsuario.ADMIN, RolUsuario.SUPER]:
        clientes = repo.find_by_empresa(current_user.empresa_id)
    else:
        clientes = repo.find_by_usuario(current_user.id)

    return {"clientes": clientes, "total": len(clientes)}


@router.get("/{cliente_id}", response_model=ClienteResponse)
def obtener_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Obtiene un cliente por ID.
    - Admin: cualquier cliente de su empresa
    - Contador: solo sus clientes asignados
    """
    repo = ClienteRepository(db)
    cliente = repo.find_by_id(cliente_id)

    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    # Verificar que el cliente pertenece a la empresa del usuario
    if cliente.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    # Contador solo puede ver sus propios clientes
    if current_user.rol == RolUsuario.CONTADOR:
        if cliente.asignado_a_usuario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    return cliente


@router.post("", response_model=ClienteResponse, status_code=status.HTTP_201_CREATED)
def crear_cliente(
    cliente_data: ClienteCreate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Crea un nuevo cliente.
    - Admin: puede asignar a cualquier usuario de la empresa
    - Contador: se asigna automáticamente a sí mismo
    """
    repo = ClienteRepository(db)

    # Verificar RUT duplicado en la empresa
    if repo.find_by_rut(current_user.empresa_id, cliente_data.rut):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=f"Ya existe un cliente con el RUT {cliente_data.rut} en esta empresa"
        )

    # Determinar asignación
    if current_user.rol in [RolUsuario.ADMIN, RolUsuario.SUPER]:
        asignado_a = cliente_data.asignado_a_usuario_id or current_user.id
    else:
        asignado_a = current_user.id  # Contador siempre se asigna a sí mismo

    # Extraer campos opcionales
    campos_opcionales = cliente_data.model_dump(
        exclude={'rut', 'razon_social', 'asignado_a_usuario_id'}
    )

    return repo.create(
        empresa_id=current_user.empresa_id,
        asignado_a_usuario_id=asignado_a,
        rut=cliente_data.rut,
        razon_social=cliente_data.razon_social,
        **{k: v for k, v in campos_opcionales.items() if v is not None}
    )


@router.put("/{cliente_id}", response_model=ClienteResponse)
def actualizar_cliente(
    cliente_id: int,
    cliente_data: ClienteUpdate,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Actualiza datos de un cliente.
    - Admin: cualquier cliente de su empresa
    - Contador: solo sus clientes asignados
    """
    repo = ClienteRepository(db)
    cliente = repo.find_by_id(cliente_id)

    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    if cliente.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    if current_user.rol == RolUsuario.CONTADOR:
        if cliente.asignado_a_usuario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    campos = {k: v for k, v in cliente_data.model_dump().items() if v is not None}
    actualizado = repo.update(cliente_id, **campos)

    return actualizado


@router.put("/{cliente_id}/desactivar", status_code=status.HTTP_200_OK)
def desactivar_cliente(
    cliente_id: int,
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(get_current_user)
):
    """
    Desactiva un cliente (soft delete).
    - Admin: cualquier cliente de su empresa
    - Contador: solo sus clientes asignados
    """
    repo = ClienteRepository(db)
    cliente = repo.find_by_id(cliente_id)

    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    if cliente.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    if current_user.rol == RolUsuario.CONTADOR:
        if cliente.asignado_a_usuario_id != current_user.id:
            raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    if not cliente.activo:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="El cliente ya está inactivo"
        )

    repo.delete(cliente_id)
    return {"message": "Cliente desactivado exitosamente"}



# Reasignar cliente.
@router.put("/{cliente_id}/reasignar", response_model=ClienteResponse)
def reasignar_cliente(
    cliente_id: int,
    nuevo_usuario_id: int,  # Query param: /api/clientes/5/reasignar?nuevo_usuario_id=3
    db: Session = Depends(get_db),
    current_user: Usuario = Depends(require_role([RolUsuario.ADMIN, RolUsuario.SUPER]))
):
    """
    Reasigna un cliente a otro contador de la misma empresa.
    Solo admins pueden reasignar.
    """
    repo = ClienteRepository(db)
    cliente = repo.find_by_id(cliente_id)

    if not cliente:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Cliente no encontrado")

    if cliente.empresa_id != current_user.empresa_id:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Acceso denegado")

    # Verificar que el nuevo usuario existe, pertenece a la empresa y es contador.
    nuevo_usuario = db.query(Usuario).filter(
        Usuario.id == nuevo_usuario_id,
        Usuario.empresa_id == current_user.empresa_id,
        Usuario.activo == True
    ).first()

    if not nuevo_usuario:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="El usuario destino no existe o no pertenece a esta empresa"
        )

    if nuevo_usuario.rol != RolUsuario.CONTADOR:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Solo se puede reasignar a un usuario con rol contador"
        )

    return repo.reasignar(cliente_id, nuevo_usuario_id)